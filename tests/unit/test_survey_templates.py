"""The humanities survey templates must load under the same loaders as the
SLR templates, so the unchanged pipeline scripts accept them."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / "templates"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, TEMPLATES / f"{name}.py")
    assert spec and spec.loader
    sys.dont_write_bytecode = True
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_survey_screening_config_has_required_names() -> None:
    m = _load("survey_screening_config")
    for name in (
        "TAG_PREFIX", "ABSTRACT_SCREENING_SYSTEM_PROMPT",
        "FULLTEXT_CODING_SYSTEM_PROMPT", "FULLTEXT_CODING_FIELDS",
        "ABSTRACT_SCREENING_MODEL", "FULLTEXT_CODING_MODEL",
    ):
        assert hasattr(m, name), name


def test_fulltext_prompt_has_the_placeholder_the_script_substitutes() -> None:
    m = _load("survey_screening_config")
    assert "{coding_fields_json_placeholder}" in m.FULLTEXT_CODING_SYSTEM_PROMPT


def test_abstract_prompt_asks_for_the_two_line_format_the_parser_reads() -> None:
    m = _load("survey_screening_config")
    assert "DECISION:" in m.ABSTRACT_SCREENING_SYSTEM_PROMPT
    assert "REASON:" in m.ABSTRACT_SCREENING_SYSTEM_PROMPT


def test_survey_fields_pass_the_scripts_own_validation() -> None:
    sys.path.insert(0, str(ROOT / "scripts" / "pipelines"))
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import fulltext_code
    finally:
        sys.path.pop(0)
        sys.path.pop(0)
    m = _load("survey_screening_config")
    names = [f["name"] for f in m.FULLTEXT_CODING_FIELDS]
    assert len(names) == len(set(names))
    for field in m.FULLTEXT_CODING_FIELDS:
        fulltext_code._validate_coding_field(field)
        if field.get("tag"):
            assert field.get("values"), f"{field['name']}: tag needs values"


def test_survey_search_config_loads_with_no_journals() -> None:
    m = _load("survey_search_config")
    assert m.JOURNALS == {}
    assert "book" in m.OPENALEX_WORK_TYPES


@pytest.mark.parametrize(
    ("issns", "types", "expected"),
    [
        (["1234-5678"], None,
         "primary_location.source.issn:1234-5678,publication_year:2000-2020,type:article"),
        ([], ("article", "book"),
         "publication_year:2000-2020,type:article|book"),
    ],
)
def test_openalex_filter(issns, types, expected) -> None:
    sys.path.insert(0, str(ROOT / "scripts" / "pipelines"))
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        from searchers import OpenAlexSearch
    finally:
        sys.path.pop(0)
        sys.path.pop(0)
    assert OpenAlexSearch()._build_filter(issns, 2000, 2020, types) == expected
