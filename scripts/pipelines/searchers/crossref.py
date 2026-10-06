"""Crossref REST API search.

Free, no key. Crossref registers DOIs for most journal articles and for the
books and chapters of the major university presses (Cambridge, Oxford,
Chicago, Princeton, ...), which makes it the first stop for DOI-bearing
humanities scholarship that the journal-centred databases miss. It holds
metadata only: no abstracts for most books and no full text.

Runs the two block queries (Block A, Block B) separately, as the OpenAlex
searcher does, via `query.bibliographic`. `OPENALEX_WORK_TYPES`-style scoping
is read from `CROSSREF_WORK_TYPES` (Crossref type names, default articles,
books, chapters and monographs). Forward citation search is not offered:
Crossref's cited-by is a members-only service.
"""

from __future__ import annotations

import re

import http_client

from .base import SearchContext, SearchSource, empty_row, term_groups

API = "https://api.crossref.org/works"
PAGE_SIZE = 100
MAX_PAGES = 5            # 500 hits per block: a survey reads the top of the ranking

DEFAULT_TYPES = ("journal-article", "book", "book-chapter", "monograph", "edited-book")

#: Crossref type -> `base.CROSSREF_TYPES`. Identity for what we request;
#: kept explicit so an unlisted type maps to "" and is looked up downstream.
_KNOWN = {
    "journal-article", "proceedings-article", "book-chapter", "book",
    "monograph", "edited-book", "reference-entry", "report",
    "dissertation", "posted-content",
}


def _first(value) -> str:
    if isinstance(value, list):
        return str(value[0]) if value else ""
    return str(value or "")


def _year(item: dict) -> str:
    for key in ("published", "published-print", "published-online", "issued"):
        parts = (item.get(key) or {}).get("date-parts") or []
        if parts and parts[0] and parts[0][0]:
            return str(parts[0][0])
    return ""


def _authors(item: dict) -> str:
    out = []
    for a in (item.get("author") or item.get("editor") or []):
        family = (a.get("family") or "").strip()
        given = (a.get("given") or "").strip()
        if family and given:
            out.append(f"{family}, {given}")
        elif family or a.get("name"):
            out.append(family or a["name"])
    return "; ".join(out)


def _isbn(item: dict) -> str:
    for raw in item.get("ISBN") or []:
        digits = re.sub(r"[^0-9Xx]", "", str(raw))
        if len(digits) in (10, 13):
            return digits.upper()
    return ""


class CrossrefSearch(SearchSource):
    name = "crossref"
    supports_journal_scope = True       # via the issn: filter
    supports_block_queries = True
    default_enabled = False   # opt in with --databases

    def run(self, config, ctx: SearchContext) -> list[dict]:
        blocks = [*term_groups(config, "a"), *term_groups(config, "b")]
        if not blocks:
            return []
        types = getattr(config, "CROSSREF_WORK_TYPES", None) or DEFAULT_TYPES
        filters = self._filters(ctx, types)

        rows: list[dict] = []
        for label, terms in blocks:
            query = " ".join(terms)
            print(f"  Crossref {label}: ", end="", flush=True)
            works = self._fetch(query, filters, ctx)
            print(f"{len(works)} results", flush=True)
            rows.extend(self.item_to_row(w, label) for w in works)
        return rows

    @staticmethod
    def _filters(ctx: SearchContext, types) -> str:
        parts = [
            f"from-pub-date:{ctx.from_year}",
            f"until-pub-date:{ctx.to_year}",
        ]
        parts.extend(f"type:{t}" for t in types)
        parts.extend(f"issn:{i}" for i in ctx.issns)
        return ",".join(parts)

    def _fetch(self, query: str, filters: str, ctx: SearchContext) -> list[dict]:
        session = ctx.http()
        out: list[dict] = []
        offset = 0
        for _ in range(MAX_PAGES):
            data = http_client.get_json(
                session, API,
                params={
                    "query.bibliographic": query,
                    "filter": filters,
                    "rows": PAGE_SIZE,
                    "offset": offset,
                    "select": "DOI,title,author,editor,issued,published,"
                              "container-title,ISSN,volume,issue,page,type,"
                              "ISBN,publisher,abstract,"
                              "is-referenced-by-count",
                },
            )
            if data is None:
                raise RuntimeError(
                    f"Crossref rejected the request at offset {offset}. "
                    f"Check the filter: {filters}"
                )
            items = (data.get("message") or {}).get("items") or []
            out.extend(items)
            if len(items) < PAGE_SIZE:
                break
            offset += PAGE_SIZE
        return out

    def item_to_row(self, item: dict, label: str) -> dict:
        ctype = str(item.get("type") or "").strip().lower()
        abstract = re.sub(r"<[^>]+>", " ", item.get("abstract") or "")
        row = empty_row()
        row.update({
            "db": self.name,
            "query": label,
            "doi": (item.get("DOI") or "").lower(),
            "title": _first(item.get("title")),
            "authors": _authors(item),
            "year": _year(item),
            "source": _first(item.get("container-title")),
            "issn": _first(item.get("ISSN")),
            "volume": str(item.get("volume") or ""),
            "issue": str(item.get("issue") or ""),
            "pages": str(item.get("page") or ""),
            "type": ctype if ctype in _KNOWN else "",
            "cited_by": item.get("is-referenced-by-count", 0) or 0,
            "abstract": re.sub(r"\s+", " ", abstract).strip(),
            "isbn": _isbn(item),
            "publisher": str(item.get("publisher") or ""),
            "language": str(item.get("language") or ""),
        })
        return row
