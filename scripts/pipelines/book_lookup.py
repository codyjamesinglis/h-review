#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "requests>=2.31",
#     "urllib3>=2.0",
#     "tenacity>=8.0",
# ]
# ///
"""Look up a book by ISBN, or by title and author, and print candidate records.

For adding books and editions to Zotero (`editions-and-translations`,
`zotero-operations`) without improvising HTTP code. Queries Crossref (DOI-
bearing books) and Open Library (catalogue records, no DOI), and prints
every candidate as JSON in the `search_results.csv` row schema, so a chosen
record can be handed to `import_to_zotero.py` or read off by the agent. It
writes nothing to Zotero.

Usage:
    uv run book_lookup.py --isbn 978-0-521-58926-0
    uv run book_lookup.py --title "Visions of Politics" --author Skinner
    uv run book_lookup.py --title Leviathan --author Hobbes --limit 10

WorldCat is not queried: its search API needs an OCLC WSKey.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import http_client  # noqa: E402
from searchers.crossref import API as CROSSREF_API  # noqa: E402
from searchers.crossref import CrossrefSearch  # noqa: E402
from searchers.openlibrary import OpenLibrarySearch  # noqa: E402

OPENLIBRARY_BOOKS = "https://openlibrary.org/api/books"
OPENLIBRARY_SEARCH = "https://openlibrary.org/search.json"


def normalize_isbn(raw: str) -> str:
    """Digits (and a final X) only; "" unless it is a valid ISBN-10 or -13."""
    s = re.sub(r"[^0-9Xx]", "", raw or "").upper()
    if len(s) == 10 and re.fullmatch(r"\d{9}[\dX]", s):
        total = sum((10 - i) * (10 if c == "X" else int(c)) for i, c in enumerate(s))
        return s if total % 11 == 0 else ""
    if len(s) == 13 and s.isdigit():
        total = sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(s))
        return s if total % 10 == 0 else ""
    return ""


def lookup_isbn(isbn: str, session) -> list[dict]:
    """Candidate rows for one ISBN from Crossref and Open Library."""
    clean = normalize_isbn(isbn)
    if not clean:
        raise ValueError(f"not a valid ISBN (bad length or check digit): {isbn!r}")
    rows: list[dict] = []

    data = http_client.get_json(
        session, CROSSREF_API,
        params={"filter": f"isbn:{clean}", "rows": 5},
    )
    cr = CrossrefSearch()
    for item in ((data or {}).get("message") or {}).get("items") or []:
        rows.append(cr.item_to_row(item, f"isbn:{clean}"))

    data = http_client.get_json(
        session, OPENLIBRARY_BOOKS,
        params={"bibkeys": f"ISBN:{clean}", "format": "json", "jscmd": "data"},
    )
    for rec in (data or {}).values():
        rows.append(_ol_record_to_row(rec, clean))
    return rows


def _ol_record_to_row(rec: dict, isbn: str) -> dict:
    from searchers.base import empty_row

    row = empty_row()
    pubs = [p.get("name", "") for p in rec.get("publishers") or []]
    date = str(rec.get("publish_date") or "")
    m = re.search(r"\b(\d{4})\b", date)
    row.update({
        "db": "openlibrary",
        "query": f"isbn:{isbn}",
        "title": " ".join(x for x in (rec.get("title"), rec.get("subtitle")) if x),
        "authors": "; ".join(a.get("name", "") for a in rec.get("authors") or []),
        "year": m.group(1) if m else "",
        "type": "book",
        "isbn": isbn,
        "publisher": pubs[0] if pubs else "",
    })
    return row


def lookup_title(title: str, author: str, session, limit: int) -> list[dict]:
    """Candidate rows for a title (and optional author) from both sources."""
    rows: list[dict] = []
    query = f"{title} {author}".strip()
    data = http_client.get_json(
        session, CROSSREF_API,
        params={
            "query.bibliographic": query,
            "filter": "type:book,type:monograph,type:edited-book,type:book-chapter",
            "rows": limit,
        },
    )
    cr = CrossrefSearch()
    for item in ((data or {}).get("message") or {}).get("items") or []:
        rows.append(cr.item_to_row(item, f"title:{title}"))

    params = {"title": title, "limit": limit,
              "fields": "key,title,author_name,first_publish_year,publisher,isbn,language"}
    if author:
        params["author"] = author
    data = http_client.get_json(session, OPENLIBRARY_SEARCH, params=params)
    ol = OpenLibrarySearch()
    for doc in (data or {}).get("docs") or []:
        rows.append(ol.doc_to_row(doc, f"title:{title}"))
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--isbn", help="ISBN-10 or ISBN-13, hyphens allowed")
    ap.add_argument("--title")
    ap.add_argument("--author", default="")
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--mailto", default="",
                    help="Contact address for Crossref's polite pool (optional)")
    args = ap.parse_args(argv)
    if bool(args.isbn) == bool(args.title):
        ap.error("give exactly one of --isbn or --title")

    session = http_client.build_session(mailto=args.mailto or None)
    try:
        rows = (lookup_isbn(args.isbn, session) if args.isbn
                else lookup_title(args.title, args.author, session, args.limit))
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(rows, indent=2, ensure_ascii=False))
    if not rows:
        print("No candidates found.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
