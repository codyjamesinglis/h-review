# CLAUDE.md

Context for Claude Code and Antigravity when working on this essay,
chapter or thesis. Adapt the placeholders in angle brackets.

For manuscript-only projects in the history of ideas, political thought,
philosophy or the theory of history. Computed statistics are not expected;
use `manuscript_claude_md.md` instead if the paper has a quantitative
component.

## What this project is

<The question, the period and corpus of primary texts, the historiographical
debate it intervenes in, and the target venue.>

## Conventions that override defaults

- **Citation style:** Chicago notes-bibliography (`chicago-notes-bibliography.csl`).
  Every citation is `[@key, locator]`; `scripts/test_citations.py` enforces it.
- **Languages:** <primary-source languages, e.g. Latin, German, French>.
  Quote the original where the argument turns on wording; give the
  translation used and its translator in the footnote.
- **Editions:** <which edition of each primary text is canonical for this
  project, e.g. Leviathan: Tuck ed., Cambridge 1996, cited by that
  pagination, not the 1651 head pagination>.
- **Historiographical stance:** <e.g. contextualist; explain what the project
  declines to claim about the author's later influence>.

## Layout

- `manuscript/essay.qmd` — source.
- `manuscript/references.bib` — generate with
  `${CLAUDE_PLUGIN_ROOT}/scripts/pipelines/generate_bib.py`.
- `scripts/test_citations.py`, `scripts/test_common.py` — regression tests.

## Test command

```bash
python3 scripts/test_citations.py
```

Run before every milestone. `critic-loop` runs it as its Step 1 gate.
