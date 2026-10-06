"""`book_lookup.py`: ISBN validation and candidate assembly, offline."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "scripts" / "pipelines", ROOT / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import book_lookup  # noqa: E402


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("978-0-521-58926-0", "9780521589260"),
        ("0-521-58926-X", ""),            # wrong check digit
        ("0140431950", "0140431950"),     # valid ISBN-10
        ("123", ""),
        ("", ""),
    ],
)
def test_normalize_isbn(raw: str, expected: str) -> None:
    assert book_lookup.normalize_isbn(raw) == expected


def test_lookup_isbn_rejects_invalid_before_any_request() -> None:
    class Boom:
        def get(self, *a, **k):
            raise AssertionError("no request expected")

    with pytest.raises(ValueError):
        book_lookup.lookup_isbn("123", Boom())


def test_lookup_isbn_collects_both_sources(monkeypatch) -> None:
    def fake_get_json(session, url, **kw):
        if "crossref" in url:
            return {"message": {"items": [{
                "DOI": "10.1017/x", "title": ["Visions of Politics"],
                "type": "book", "ISBN": ["9780521589260"],
                "issued": {"date-parts": [[2002]]},
            }]}}
        return {"ISBN:9780521589260": {
            "title": "Visions of politics", "authors": [{"name": "Quentin Skinner"}],
            "publishers": [{"name": "Cambridge University Press"}],
            "publish_date": "2002",
        }}

    monkeypatch.setattr(book_lookup.http_client, "get_json", fake_get_json)
    rows = book_lookup.lookup_isbn("978-0-521-58926-0", object())
    assert [r["db"] for r in rows] == ["crossref", "openlibrary"]
    assert rows[1]["publisher"] == "Cambridge University Press"
    assert rows[1]["year"] == "2002"
