"""Open Library search: catalogue records for books and editions.

Free, no key. Open Library (Internet Archive) holds catalogue records for
books of every period and language, with ISBNs, publishers and first
publication years, and no DOIs: the complement of Crossref for the
monographs and older editions a history of ideas turns on. Records carry no
abstracts. Rows arrive with `type = "book"` and are imported as Zotero
`book` items; `import_to_zotero.py` already builds items from a search row
alone when there is no DOI.

Open Library answers one *work* with many *editions*. The search returns the
work, with the ISBNs of its editions; the row records the first ISBN and
the first-publication year, and a human picks the edition read
(`editions-and-translations`).

Year bounds are applied to the first publication year, not the edition's:
for a survey of scholarship that is the right axis, and for a primary text
set `FROM_YEAR` early enough to admit it.
"""

from __future__ import annotations

import re

import http_client

from .base import SearchContext, SearchSource, empty_row

API = "https://openlibrary.org/search.json"
PAGE_SIZE = 100
MAX_PAGES = 3
FIELDS = ("key,title,author_name,first_publish_year,publisher,isbn,"
          "language,subject,edition_count")


def _clean_isbn(values: list[str]) -> str:
    for raw in values or []:
        digits = re.sub(r"[^0-9Xx]", "", str(raw))
        if len(digits) == 13 or len(digits) == 10:
            return digits.upper()
    return ""


class OpenLibrarySearch(SearchSource):
    name = "openlibrary"
    supports_block_queries = True
    default_enabled = False   # opt in with --databases

    def run(self, config, ctx: SearchContext) -> list[dict]:
        blocks = []
        if getattr(config, "BLOCK_A_TERMS", None):
            blocks.append(("block_a", config.BLOCK_A_TERMS))
        if getattr(config, "BLOCK_B_TERMS", None):
            blocks.append(("block_b", config.BLOCK_B_TERMS))
        if not blocks:
            return []
        rows: list[dict] = []
        for label, terms in blocks:
            query = " ".join(terms)
            print(f"  Open Library {label}: ", end="", flush=True)
            docs = self._fetch(query, ctx)
            kept = [d for d in docs if self._in_window(d, ctx)]
            print(f"{len(kept)} results", flush=True)
            rows.extend(self.doc_to_row(d, label) for d in kept)
        return rows

    @staticmethod
    def _in_window(doc: dict, ctx: SearchContext) -> bool:
        year = doc.get("first_publish_year")
        return not year or ctx.from_year <= int(year) <= ctx.to_year

    def _fetch(self, query: str, ctx: SearchContext) -> list[dict]:
        session = ctx.http()
        out: list[dict] = []
        for page in range(1, MAX_PAGES + 1):
            data = http_client.get_json(
                session, API,
                params={"q": query, "fields": FIELDS,
                        "limit": PAGE_SIZE, "page": page},
            )
            if data is None:
                raise RuntimeError(f"Open Library rejected the request (page {page}).")
            docs = data.get("docs") or []
            out.extend(docs)
            if len(docs) < PAGE_SIZE:
                break
        return out

    def doc_to_row(self, doc: dict, label: str) -> dict:
        langs = doc.get("language") or []
        pubs = doc.get("publisher") or []
        row = empty_row()
        row.update({
            "db": self.name,
            "query": label,
            "title": doc.get("title", "") or "",
            "authors": "; ".join(doc.get("author_name") or []),
            "year": str(doc.get("first_publish_year") or ""),
            "type": "book",
            "isbn": _clean_isbn(doc.get("isbn") or []),
            "publisher": pubs[0] if pubs else "",
            "language": langs[0] if langs else "",
        })
        return row
