"""Multilingual search: term groups, tag validation, probe, config checks.
No network."""

from __future__ import annotations

import sys
import types
import unicodedata
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "scripts" / "pipelines", ROOT / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import languages  # noqa: E402
import probe_terms  # noqa: E402
import search  # noqa: E402
from searchers import CrossrefSearch, SearchContext, term_groups  # noqa: E402


def _cfg(**kw):
    return types.SimpleNamespace(**kw)


def test_term_groups_single_language_is_unchanged() -> None:
    cfg = _cfg(BLOCK_A_TERMS=["Hobbes"], BLOCK_B_TERMS=[])
    assert term_groups(cfg, "a") == [("block_a", ["Hobbes"])]
    assert term_groups(cfg, "b") == []


def test_term_groups_one_group_per_language_with_labels() -> None:
    cfg = _cfg(TERMS_BY_LANGUAGE={
        "de": {"a": ["Hobbes"], "b": ["Souveränität"]},
        "hu": {"a": ["Hobbes"]},
    })
    assert term_groups(cfg, "a") == [
        ("block_a:de", ["Hobbes"]), ("block_a:hu", ["Hobbes"])]
    assert term_groups(cfg, "b") == [("block_b:de", ["Souveränität"])]


def test_term_groups_ignores_the_flat_lists_when_by_language_is_set() -> None:
    cfg = _cfg(BLOCK_A_TERMS=["ignored"], TERMS_BY_LANGUAGE={"fr": {"a": ["Léviathan"]}})
    assert term_groups(cfg, "a") == [("block_a:fr", ["Léviathan"])]


def test_terms_are_nfc_normalised() -> None:
    decomposed = unicodedata.normalize("NFD", "szuverenitás őr")
    assert decomposed != "szuverenitás őr"
    cfg = _cfg(TERMS_BY_LANGUAGE={"hu": {"a": [decomposed]}})
    (_, terms), = term_groups(cfg, "a")
    assert terms == ["szuverenitás őr"]


def test_known_tags_cover_the_users_languages() -> None:
    wanted = ["en", "de", "hu", "hr", "sr-Latn", "sr-Cyrl", "bs", "sl", "pl",
              "cs", "sk", "ro", "uk", "it", "ru", "fr", "la"]
    for tag in wanted:
        languages.validate_tag(tag)


@pytest.mark.parametrize(
    ("terms", "needle"),
    [
        ({"xx": {"a": ["x"]}}, "unknown language tag"),
        ({"ru": {"a": ["Hobbes"]}}, "no Cyrillic"),
        ({"de": {"a": ["Гоббс"]}}, "Cyrillic under a Latin tag"),
        ({"de": {"c": ["x"]}}, "keys 'a' and/or 'b'"),
        ({"de": {"a": [""]}}, "empty or non-string"),
        ({}, "non-empty dict"),
    ],
)
def test_validation_catches_mistakes(terms: dict, needle: str) -> None:
    problems = languages.validate_terms_by_language(terms)
    assert any(needle in p for p in problems), problems


def test_valid_config_has_no_problems() -> None:
    ok = {"de": {"a": ["Hobbes"]}, "ru": {"a": ["Гоббс"]}, "sr-Cyrl": {"b": ["суверенитет"]}}
    assert languages.validate_terms_by_language(ok) == []


def test_search_refuses_a_bad_multilingual_config(tmp_path: Path) -> None:
    cfg = tmp_path / "search_config.py"
    cfg.write_text(
        "FROM_YEAR=1900\nTO_YEAR=2000\nJOURNALS={}\n"
        "TERMS_BY_LANGUAGE={'ru': {'a': ['Hobbes']}}\n", encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        search._load_config(str(cfg))
    assert "no Cyrillic" in str(exc.value)


def test_crossref_runs_each_language_and_labels_the_rows(monkeypatch) -> None:
    seen: list[str] = []

    def fake_fetch(self, query, filters, ctx):
        seen.append(query)
        return [{"DOI": f"10.1/{len(seen)}", "title": [query], "type": "book"}]

    monkeypatch.setattr(CrossrefSearch, "_fetch", fake_fetch)
    cfg = _cfg(TERMS_BY_LANGUAGE={
        "de": {"a": ["Hobbes", "Leviathan"]}, "hu": {"a": ["Leviatán"]}})
    rows = CrossrefSearch().run(cfg, SearchContext(from_year=1950, to_year=2026, issns=[]))
    assert seen == ["Hobbes Leviathan", "Leviatán"]
    assert [r["query"] for r in rows] == ["block_a:de", "block_a:hu"]


def test_probe_counts_every_term(monkeypatch) -> None:
    calls: list[str] = []

    def fake_get_json(session, url, **kw):
        calls.append(kw["params"]["search"])
        return {"meta": {"count": 0 if "bogus" in kw["params"]["search"] else 42}}

    monkeypatch.setattr(probe_terms.http_client, "get_json", fake_get_json)
    cfg = _cfg(FROM_YEAR=1950, TO_YEAR=2026, TERMS_BY_LANGUAGE={
        "de": {"a": ["Hobbes"], "b": ["bogus"]}})
    out = probe_terms.probe(cfg, object())
    assert [(r["language"], r["block"], r["hits"]) for r in out] == [
        ("de", "a", 42), ("de", "b", 0)]
    assert calls == ['"Hobbes"', '"bogus"']


def test_probe_rejects_an_invalid_config() -> None:
    cfg = _cfg(FROM_YEAR=1950, TO_YEAR=2026, TERMS_BY_LANGUAGE={"xx": {"a": ["x"]}})
    with pytest.raises(ValueError):
        probe_terms.probe(cfg, object())
