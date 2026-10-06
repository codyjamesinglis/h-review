---
name: historiographical-survey
description: Use when mapping the scholarship on a thinker, text, debate or period in intellectual history, political thought, the history of philosophy or the theory of history — scoping, searching, snowballing, triaging, coding and synthesising. Trigger phrases "survey the literature on", "historiography of", "map the scholarship", "who has written on", "state of the field". Do NOT use for a PRISMA-style quantitative review — use `systematic-review`. Do NOT use for reading one text — use `reading-notes`.
---

# Historiographical survey

> **Glossary:** **BBT**, **MCP**, **DOI**: see [skills/_glossary.md](../_glossary.md).

> *This skill adapts the upstream systematic-review pipeline
> (mronkko/claude-academic-research) to interpretive scholarship. The scripts
> are the same; the scope, prompts and report differ. A survey is not a
> systematic review: it makes no claim to completeness and reports no
> PRISMA counts.*

## What this skill is for

A survey answers *what has been argued about X, by whom, with what method,
and where does that leave my question?* Its output is a **map of positions**
that goes into the introduction or a historiographical chapter, not a count
of included studies.

## Companion skills

- **REQUIRED SUB-SKILL: systematic-review.** Load it for the command-level
  protocols this skill does not repeat: pre-flight, Zotero library
  selection, tag prefix, model choice and connection check, batch and
  cluster runs, and the "no improvised pipeline code" rule. Where it
  speaks of PRISMA counts, screening reliability or `test_systematic_review.py`,
  those do not apply here.
- `reading-notes`, `editions-and-translations`: for the primary texts and for
  books, which this pipeline does not code.
- `zotero-operations`: adding works by hand, merging duplicates.
- `grounded-citations`, `fact-check`: when the survey becomes prose.

## Procedure

1. **Scope** (before any search). Write down, with the user: the question; the
   texts, authors or debate in scope; the period of the *primary* material;
   the period and languages of the *scholarship* to survey; whether books
   count. Record it in the project's CLAUDE.md. There is no protocol to
   register, but later readers need to know what the survey covered.
2. **Install the templates**:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT:-.}/scripts/setup/install_templates.py" \
       survey_search_config.py:search_config.py \
       survey_screening_config.py:screening_config.py
   ```
   Fill the question, scope, block terms and `TAG_PREFIX`.
3. **Seed.** Ask the user for 3–10 landmark studies, editions and the
   standard handbook or companion. Add their DOIs to `CITATION_SEEDS`.
   For works without a DOI, add them to Zotero by hand
   (`zotero-operations`) and note them for the snowball by title.
4. **Search.** The keyless sources need no setup; name them with
   `--databases`, since Crossref and Open Library are opt-in:
   ```bash
   uv run "${CLAUDE_PLUGIN_ROOT:-.}/scripts/pipelines/search.py" \
       --config ./search_config.py --databases openalex,crossref,openlibrary
   ```
   - **OpenAlex**: broad, with abstracts and the citation graph;
     `OPENALEX_WORK_TYPES` admits books and chapters.
   - **Crossref**: DOI-bearing books and chapters from the university
     presses, with ISBN and publisher. It lists a book's chapters as
     separate records, so expect several hits per book.
   - **Open Library**: catalogue records for books and older editions,
     no DOI, one hit per work with its ISBNs.
   Rows for the same book from different sources are merged on DOI,
   title and author, or ISBN. Use `--streams citation` to run the
   snowball alone (OpenAlex and Semantic Scholar only).
5. **Import and enrich** (`import_to_zotero.py`, `enrich_abstracts.py`,
   `enrich_pdfs.py`), as in `systematic-review`.
6. **Triage on abstract** (`abstract_screen.py`). Expect many `borderline`:
   humanities abstracts are often missing, so a missing abstract is never an
   exclusion. The human reads the borderlines.
7. **Code the includes** (`fulltext_code.py`) for articles and chapters only.
   Books exceed the full-text cap; read them with `reading-notes`.
8. **Snowball again** from the strongest included works (add their DOIs to
   `CITATION_SEEDS`, re-run), until new hits are mostly known. That is the
   stopping rule: saturation of names, not a count.
9. **Add what the tools cannot find**: books without DOIs, scholarship in other
   languages, works the user knows. Mark them in Zotero and run them
   through `reading-notes`.
10. **Synthesise.** Export with `export_coded_includes.py`, then write the
    map (below). Do not paste the CSV into prose.

## Writing the map

- Group works by **position**, not by author or year: what each group
  claims, what divides it from the others, who started it, whose
  argument is the strongest on each side.
- Use the coded fields: `school_or_method` to separate approaches,
  `interlocutors` to draw the lines of dispute, `primary_sources` to
  show which texts carry the debate and which are neglected.
- Say where the survey stops: databases, languages and types of work
  searched, and what was added by hand. One paragraph, no flow diagram.
- Every claim about what a scholar argued goes through `grounded-citations`
  with a locator, then `fact-check`. A coded field is a lead, not evidence.

## Limits to tell the user

- **No single source covers the field.** OpenAlex under-covers books and
  non-English scholarship; Crossref covers only DOI-registered works; Open
  Library is a library catalogue and says nothing about content. Works
  with no DOI do import (from the search row alone), with thinner
  metadata. JSTOR, Project MUSE, PhilPapers and WorldCat are not
  searched (see `BACKLOG.md`); add what they hold by hand.
- To add one known book, use `book_lookup.py` (below) rather than a search.
- LLM coding of `school_or_method` is a judgement. Spot-check a sample
  against the works before relying on the distribution.
- The tools do not remove the need to know the field. Ask the user to
  review the includes against what they know is missing.

## Looking up one book

```bash
uv run "${CLAUDE_PLUGIN_ROOT:-.}/scripts/pipelines/book_lookup.py" --isbn 978-0-14-043195-7
uv run "${CLAUDE_PLUGIN_ROOT:-.}/scripts/pipelines/book_lookup.py" --title Leviathan --author Hobbes
```

It prints candidates from Crossref and Open Library as JSON and writes
nothing. An ISBN with a bad check digit is refused. Choose the record for
the edition the user read, then add it with `editions-and-translations`.

## Red flags

- A "PRISMA flow diagram" or counts of "studies identified, screened,
  included" in a humanities survey.
- Missing abstracts excluded as irrelevant.
- A book sent through `fulltext_code.py`.
- A claim about a scholar's argument written from a coded field without
  reading the work.
- Scholarship in one language only, unstated.
- Stopping at a fixed number of works rather than at saturation.
