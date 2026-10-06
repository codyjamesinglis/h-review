"""Per-project search configuration for a historiographical survey.

The humanities counterpart of `search_config.py`. Install it as
`search_config.py`:

    python3 ${CLAUDE_PLUGIN_ROOT}/scripts/setup/install_templates.py \\
        survey_search_config.py:search_config.py

Run OpenAlex only (no Scopus/WoS subscription needed):

    uv run ${CLAUDE_PLUGIN_ROOT}/scripts/pipelines/search.py \\
        --config ./search_config.py --databases openalex

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

QUERY_DEFS: list = []     # Scopus/WoS queries: leave empty if you have no access.

# OpenAlex runs the two blocks as separate searches and merges them.
# Block A: the author, text or concept; block B: the angle.
BLOCK_A_TERMS = [
    "Hobbes",
    "Leviathan",
]
BLOCK_B_TERMS = [
    "sovereignty",
    "political obligation",
]

# Forward snowballing: every work citing these DOIs. The strongest stream for
# intellectual history, since the key studies of a thinker are cited by
# everything that follows them. Seed with the standard studies and editions.
CITATION_SEEDS: list[str] = [
    # "10.xxxx/xxxxx",   # e.g. a landmark study of your author
]
