"""Crossref and Open Library searchers: response parsing, filters, opt-in
default, and ISBN-aware dedup. No network."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "scripts" / "pipelines", ROOT / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import import_to_zotero  # noqa: E402
import search  # noqa: E402
from searchers import (  # noqa: E402
    CrossrefSearch,
    OpenLibrarySearch,
    SearchContext,
    searchers_by_name,
)
from searchers.base import SEARCH_ROW_FIELDS  # noqa: E402

CROSSREF_BOOK = {
    "DOI": "10.1017/CBO9780511598265",
    "title": ["Visions of Politics"],
    "author": [{"family": "Skinner", "given": "Quentin"}],
    "issued": {"date-parts": [[2002]]},
    "container-title": [],
    "type": "book",
    "ISBN": ["978-0-521-58926-0", "9780511598265"],
    "publisher": "Cambridge University Press",
    "language": "en",
    "is-referenced-by-count": 12,
}


def test_crossref_row_for_a_book() -> None:
    row = CrossrefSearch().item_to_row(CROSSREF_BOOK, "block_a")
    assert set(row) == set(SEARCH_ROW_FIELDS)
    assert row["doi"] == "10.1017/cbo9780511598265"
    assert row["authors"] == "Skinner, Quentin"
    assert row["year"] == "2002"
    assert row["type"] == "book"
    assert row["isbn"] == "9780521589260"      # hyphens stripped, first valid
    assert row["publisher"] == "Cambridge University Press"


def test_crossref_unknown_type_is_blank_not_article() -> None:
    row = CrossrefSearch().item_to_row({"DOI": "10.1/x", "type": "weird"}, "q")
    assert row["type"] == ""


def test_crossref_filter_has_dates_types_and_optional_issn() -> None:
    ctx = SearchContext(from_year=1950, to_year=2026, issns=[])
    f = CrossrefSearch._filters(ctx, ("book", "book-chapter"))
    assert f == "from-pub-date:1950,until-pub-date:2026,type:book,type:book-chapter"
    ctx2 = SearchContext(from_year=1950, to_year=2026, issns=["1234-5678"])
    assert CrossrefSearch._filters(ctx2, ("book",)).endswith("issn:1234-5678")


def test_openlibrary_row() -> None:
    doc = {
        "title": "Leviathan", "author_name": ["Thomas Hobbes"],
        "first_publish_year": 1651, "publisher": ["Penguin"],
        "isbn": ["0140431950", "9780140431957"], "language": ["eng"],
    }
    row = OpenLibrarySearch().doc_to_row(doc, "block_a")
    assert row["doi"] == ""
    assert row["type"] == "book"
    assert row["isbn"] == "0140431950"
    assert row["year"] == "1651"


def test_openlibrary_year_window_uses_first_publication() -> None:
    ctx = SearchContext(from_year=1900, to_year=2026, issns=[])
    ol = OpenLibrarySearch()
    assert not ol._in_window({"first_publish_year": 1651}, ctx)
    assert ol._in_window({"first_publish_year": 1999}, ctx)
    assert ol._in_window({}, ctx)           # unknown year is kept


def test_book_sources_are_opt_in() -> None:
    reg = searchers_by_name()
    assert reg["crossref"].default_enabled is False
    assert reg["openlibrary"].default_enabled is False
    assert reg["openalex"].default_enabled is True


def test_dedup_merges_doi_less_catalogue_row_into_doi_row_by_isbn() -> None:
    doi_row = CrossrefSearch().item_to_row(CROSSREF_BOOK, "q")
    ol = OpenLibrarySearch().doc_to_row(
        {"title": "Visions of politics (3 vols)", "first_publish_year": 2002,
         "isbn": ["9780521589260"], "language": ["eng"]}, "q")
    out, merged = search._dedup([doi_row, ol])
    assert merged == 1 and len(out) == 1


def test_dedup_merges_two_doi_less_rows_with_same_isbn() -> None:
    a = OpenLibrarySearch().doc_to_row(
        {"title": "A", "isbn": ["9780140431957"]}, "q")
    b = OpenLibrarySearch().doc_to_row(
        {"title": "A reissue", "isbn": ["9780140431957"], "publisher": ["Penguin"]}, "q")
    out, merged = search._dedup([a, b])
    assert merged == 1 and len(out) == 1
    assert out[0]["publisher"] == "Penguin"     # filled from the duplicate


def test_import_maps_book_fields_and_drops_what_the_type_lacks() -> None:
    row = CrossrefSearch().item_to_row(CROSSREF_BOOK, "q")
    item = import_to_zotero._row_to_zotero_item(row, None, "book", ns="t/")
    assert item["ISBN"] == "9780521589260"
    assert item["publisher"] == "Cambridge University Press"
    cleaned, dropped = import_to_zotero._filter_valid_fields(item)
    assert cleaned["ISBN"] and cleaned["publisher"]
    art = import_to_zotero._row_to_zotero_item(row, None, "journalArticle", ns="t/")
    _, dropped = import_to_zotero._filter_valid_fields(art)
    assert "ISBN" in dropped      # a journalArticle has no ISBN
