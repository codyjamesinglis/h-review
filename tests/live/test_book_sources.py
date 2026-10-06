"""Live: Crossref and Open Library return what the book searchers parse.

The unit tests feed canned responses, so they pin our parsing, not the
services' shapes. Run with `pytest -m live tests/live/test_book_sources.py`.
Both services are free and keyless.
"""

from __future__ import annotations

import pytest
from searchers import CrossrefSearch, OpenLibrarySearch
from searchers.base import SearchContext

pytestmark = pytest.mark.live


class _Config:
    BLOCK_A_TERMS = ["Skinner", "Visions of Politics"]
    BLOCK_B_TERMS: list = []
    CROSSREF_WORK_TYPES = ("book", "monograph", "edited-book")


def _ctx() -> SearchContext:
    return SearchContext(from_year=2000, to_year=2005, issns=[])


def test_crossref_returns_books_with_isbn_and_publisher() -> None:
    rows = CrossrefSearch().run(_Config, _ctx())
    assert rows, "Crossref returned nothing for a famous book"
    assert any(r["isbn"] for r in rows)
    assert any(r["publisher"] for r in rows)
    assert all(r["type"] in {"book", "monograph", "edited-book", ""} for r in rows)


def test_openlibrary_returns_catalogue_records_without_doi() -> None:
    class Cfg:
        BLOCK_A_TERMS = ["Leviathan", "Hobbes"]
        BLOCK_B_TERMS: list = []

    ctx = SearchContext(from_year=1500, to_year=2026, issns=[])
    rows = OpenLibrarySearch().run(Cfg, ctx)
    assert rows
    assert all(r["doi"] == "" and r["type"] == "book" for r in rows)
    assert any(r["isbn"] for r in rows)
