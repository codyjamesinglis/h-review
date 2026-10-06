"""Per-project search configuration for a historiographical survey.

The humanities counterpart of `search_config.py`. Install it as
`search_config.py`:

    python3 ${CLAUDE_PLUGIN_ROOT}/scripts/setup/install_templates.py \\
        survey_search_config.py:search_config.py

Run the keyless sources (no Scopus/WoS subscription needed). Crossref and
Open Library are opt-in, so name them:

    uv run ${CLAUDE_PLUGIN_ROOT}/scripts/pipelines/search.py \\
        --config ./search_config.py --databases openalex,crossref,openlibrary

Differences from the SLR config: no journal list (a survey in intellectual
history is rarely journal-bound), books and chapters are searched as well as
articles, and citation snowballing from seed works is the main stream.
Coverage caveat: OpenAlex indexes works by DOI and OpenAlex ID; books and
older monographs without a DOI are under-represented. Seed with what you
know and add the rest by hand through `zotero-operations`.
"""

FROM_YEAR = 1950          # publication window of the *scholarship*, not the texts
TO_YEAR = 2026

# Empty: no journal restriction. The OpenAlex searcher omits the ISSN filter.
JOURNALS: dict = {}

# What OpenAlex should return. Default for the SLR pipeline is articles only.
OPENALEX_WORK_TYPES = ("article", "book", "book-chapter")

# What Crossref should return, in Crossref's own type names.
CROSSREF_WORK_TYPES = ("journal-article", "book", "monograph", "edited-book", "book-chapter")

QUERY_DEFS: list = []     # Scopus/WoS queries: leave empty if you have no access.

# Search terms, per language. Each language is searched as its own query,
# labelled `block_a:de`, `block_b:hu`, ..., so every record says which
# vocabulary found it and a translation that finds nothing is visible.
# Block A: the author, text or concept; block B: the angle.
#
# THESE ARE EXAMPLE DRAFTS, NOT A VERIFIED GLOSSARY. A translated term is a
# guess about what the literature calls the thing; check each one with
#     uv run ${CLAUDE_PLUGIN_ROOT}/scripts/pipelines/probe_terms.py --config ./search_config.py
# and with a reader of that language, then edit. Recognised tags:
# scripts/pipelines/languages.py (en de hu hr sr-Latn sr-Cyrl bs sh sl pl
# cs sk ro uk ru it fr la grc). Terms may be inflected forms (Hungarian,
# Slovak, Slovenian...), alternates, or transliterations: list as many as
# the literature uses. Cyrillic terms go under Cyrillic tags (`sr-Cyrl`,
# `uk`, `ru`); a Latin-script Serbian title is found only by `sr-Latn`.
TERMS_BY_LANGUAGE = {
    "en": {"a": ["Hobbes", "Leviathan"], "b": ["sovereignty", "political obligation"]},
    "de": {"a": ["Hobbes", "Leviathan"], "b": ["Souveränität"]},
    "hu": {"a": ["Hobbes", "Leviatán"], "b": ["szuverenitás"]},
    "sl": {"a": ["Hobbes", "Leviathan"], "b": ["suverenost"]},
    "ru": {"a": ["Гоббс", "Левиафан"], "b": ["суверенитет"]},
    "fr": {"a": ["Hobbes", "Léviathan"], "b": ["souveraineté"]},
    "it": {"a": ["Hobbes", "Leviatano"], "b": ["sovranità"]},
}

# `BLOCK_A_TERMS` / `BLOCK_B_TERMS` are ignored when TERMS_BY_LANGUAGE is set.


# Forward snowballing: every work citing these DOIs. The strongest stream for
# intellectual history, since the key studies of a thinker are cited by
# everything that follows them. Seed with the standard studies and editions.
CITATION_SEEDS: list[str] = [
    # "10.xxxx/xxxxx",   # e.g. a landmark study of your author
]
