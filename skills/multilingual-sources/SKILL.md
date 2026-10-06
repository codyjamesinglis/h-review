---
name: multilingual-sources
description: Use when searching for, reading, quoting or citing scholarship and primary texts in languages other than English — translating search terms, handling Cyrillic and Serbo-Croatian variants, quoting originals, flagging machine translations. Trigger phrases "search in German", "translate the search terms", "Hungarian sources", "quote the original", "cite a translation". Do NOT use for editions of one work — use `editions-and-translations`. Do NOT use for the search run itself — use `historiographical-survey`.
---

# Multilingual sources

> **Glossary:** **BBT**, **MCP**: see [skills/_glossary.md](../_glossary.md).

Intellectual history is done in the languages the texts and the scholarship
are in. This skill covers four things: search terms in several languages,
screening and coding of non-English work, reading and quoting originals,
and being honest about what the agent can and cannot do in each language.

## Read first: what the agent can vouch for

Treat the agent's competence as **uneven**. It is usually reliable in
English, German, French, Italian and Russian; it is weaker, and more likely
to produce fluent mistakes, in Hungarian, Slovenian, Serbo-Croatian
varieties, Slovak, Romanian and Ukrainian, and in older orthography, Latin
and Greek. So:

- **Every translation the agent drafts is a draft.** Label it
  `[machine translation]` wherever it is recorded, and have the user (or a
  reader of the language) confirm anything that goes into prose or into the
  search configuration.
- **Never present a translated quotation as the author's words.** The
  quotation is the original text. A translation beside it says whose it is
  (`translation Tuck`, `translation mine`, `[machine translation]`).
- When the agent is not sure it has read a passage correctly, it says so
  and does not paraphrase from a guess.

## 1. Translating search terms

Search terms are guesses about what the literature calls a thing. The
procedure turns the guess into something checkable.

1. **List the languages** the survey should cover (those in the project's
   CLAUDE.md), and the **concept, author and text** terms in English.
2. **Draft terms per language** with the user, not for them:
   - the term the period or the field actually uses, not a literal
     translation (Bodin's *maiestas*, German *Staatsräson*, Hungarian
     *államérdek*: the field's word may not be the dictionary word);
   - **inflected forms** for inflecting languages (Hungarian, Slovenian,
     Slovak, Czech, Polish, Russian, Ukrainian): phrase searches miss other
     cases, so list the forms the literature uses;
   - **variant spellings**: German umlauts (ä/ae), Romanian ș/ş, older
     orthography, Latin u/v and i/j;
   - **author names** as the language writes them (Cyrillic *Гоббс*;
     Serbian *Хобс*), including transliterations;
   - **Serbo-Croatian**: give each variety the scholarship may be in, as
     separate tags: `hr`, `bs`, `sr-Latn`, `sr-Cyrl`, and `sh` where
     catalogues use the umbrella. Croatian and Serbian differ in
     vocabulary as well as script.
3. **Write them into `TERMS_BY_LANGUAGE`** in `search_config.py` (the
   survey template shows the shape). Tags are listed in
   `scripts/pipelines/languages.py`. `search.py` validates the config before
   any request: an unknown tag, or Cyrillic under a Latin tag, is refused.
4. **Probe** the terms before searching:
   ```bash
   uv run "${CLAUDE_PLUGIN_ROOT:-.}/scripts/pipelines/probe_terms.py" --config ./search_config.py
   ```
   It prints OpenAlex hit counts per term. Zero hits means a spelling,
   inflection or vocabulary problem; thousands means too general. It shows a
   term is *used*, not that it is *right*, so the user still reads the
   list. OpenAlex under-indexes some languages, so a low count is not proof
   of an absent literature.
5. **Search**, as in `historiographical-survey`. Each language runs as its
   own query, labelled `block_a:de`; the label is on every record and in the
   Zotero `search:` tag, which lets you report which language's search found
   what.

Record in the survey's methods paragraph which languages were searched,
with what terms, and that translations were drafted by a model and
checked by the user.

## 2. Screening and coding non-English work

The survey templates already tell the screener to judge a work in its own
language, never to exclude for language, and to write reasons in English.
Beyond that:

- A **missing or English-only abstract** on a non-English work is still
  `borderline`, not `exclude`.
- The coded `language_and_translation` field takes the ISO tag.
- Check a sample of non-English decisions against the works yourself; model
  triage is weakest exactly where you most need it.

## 3. Quoting and citing

- **Quote the original.** The footnote or text carries the original wording
  where the argument turns on it; the translation is secondary and
  attributed. This follows `academic-style`.
- **Never quote an agent's translation as if it were a published one.** If
  the agent translates a passage for the user's reading, it is `translation
  mine` only after the user has made it theirs; otherwise it is marked as a
  machine draft and kept out of the manuscript.
- **Citing a translation**: cite the translation read, in its own Zotero
  item, with the original-date and original-title in `Extra`
  (`editions-and-translations`). Page numbers are the translation's.
- **Verification** (`verifying-citations`): a quotation in a language the
  agent cannot read with confidence is classified UNVERIFIABLE, not VERIFIED.
  It needs the user's eye on the page.

## 4. Reading notes in several languages

Take notes in the user's working language, but in the `Quotations` note
keep the original verbatim with `[lang: hu]`, add the English gloss on its
own line, and say who made it. Tag the concept under its original-language
term when the period had one (`concept:Staatsräson`). `reading-notes` has
the format.

## Scripts and encodings

- Terms are normalised to Unicode NFC before searching, because text
  copied from some sources arrives with combining characters that do not
  match precomposed ones (Hungarian ő, ű; Czech ř).
- Cyrillic and Latin Serbian records are different strings: a Latin-script
  title is not found by a Cyrillic term, or the reverse. Search both.
- Transliteration in catalogues varies (ALA-LC, ISO 9, national
  standards); a work may appear as *Gobbs*, *Hobbes* and *Гоббс*.

## Red flags

- A translated term never probed or shown to the user.
- A Serbo-Croatian search in one variety or one script only, unstated.
- A non-English work excluded for its language or for an English-only
  abstract.
- A translated quotation presented as the author's own words.
- A quotation in a language the agent cannot read well marked VERIFIED.
- Hungarian, Slovenian or other inflected terms searched only in the
  nominative.
