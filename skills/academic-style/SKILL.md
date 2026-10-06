---
name: academic-style
description: Use when drafting or editing humanities prose — intellectual history, history of political thought or philosophy, theory of history — in a .qmd / .Rmd / .md / .tex file. Covers Chicago notes-bibliography, footnote discipline, tense, quotation and translation, period terms, historiographical positioning. Do NOT use for the revision workflow — use `manuscript-revision` + `/critic-loop`. Do NOT use for citation sourcing or accuracy — use `grounded-citations` / `fact-check`.
---

# Academic style (humanities)

> **No pre-flight, no bootstrap by design.** This is a doctrine
> skill — pure prose conventions. It does not call MCPs, does not
> install project scaffolds, and does not need `/setup` to have run.

> *Adapted from the upstream `academic-style` skill in
> mronkko/claude-academic-research, which targets quantitative empirical
> writing (APA, IMRaD, causal hedging). Those rules are replaced here.*

## Core rule

Apply these conventions **during drafting**. The `critic-loop` argument
critic checks them later; writing them in first reduces what it has to fix.

This skill governs style only. Citation sourcing is
`grounded-citations`; auditing a draft's claims is `fact-check`; the
revision workflow is `manuscript-revision` + `critic-loop`.

## Citations: Chicago notes-bibliography

- Cite with a located key: `[@hobbes1651, p. 91]`. Pandoc renders it as a
  footnote under `chicago-notes-bibliography.csl`; never hand-type
  `Hobbes, Leviathan, 91` or add `^[…]` around a citation.
- **Every citation has a locator** — `p.`, `pp.`, `chap.`, `bk.`, `§`,
  line numbers, or the standard pagination of the text (Kant's `A51/B75`,
  Aristotle's Bekker numbers, Plato's Stephanus numbers). A deliberate
  whole-work reference is `[@key, passim]`. `test_citations.py` enforces this.
- Commentary and citation share a footnote:
  `^[Compare [@locke1689, bk. 2, §4].]`. Footnotes carry reference,
  qualification and dissent with other scholars; argument that the case
  depends on belongs in the text.
- Naming an author and the date of a work in prose is fine
  (*Hobbes's* Leviathan *(1651)*); the footnote carries the reference.
  Do not use the parenthetical author-date form `(Skinner 1969)`.
- Cite the **edition you read**, in the **language you read it**. A
  translation is cited as the translation; give the original date
  alongside when it matters to the argument.
- Prefer primary sources over commentary for what a text says; prefer
  scholarship for what a text meant to its first readers.

## Quotation, translation, original language

- Quote when the wording carries the argument; paraphrase otherwise. Do
  not quote a sentence to make a point you could make in half the words.
- Block quotation for roughly 100 words or more (Chicago).
- Quote the original where the argument turns on a word (*potestas*,
  *Geist*, *virtù*), with the translation in the text and the original in
  the footnote, or the reverse; be consistent within a piece.
- Say whose translation it is: `translation Tuck`, `translation mine`. A
  model-drafted translation is never `translation mine` until you have
  made it yours (`multilingual-sources`).
- Say whose translation it is. If you changed it, write
  `translation modified` in the footnote.
- Italicise foreign terms on first use and gloss them once. Do not
  translate a term silently and then use the translation as if it were the
  author's own vocabulary.

## Voice and tense

- **Argument and the text's content: present** — *"Hobbes argues that the
  covenant binds only while the sovereign protects."*
- **Historical events and reception: past** — *"The Leviathan was
  condemned by Oxford in 1683."*
- **First person** is acceptable in the humanities for the argument
  (*"I argue"*, *"I will show"*). Prefer it to *"this paper argues"*.
- Active voice where the agent matters, and in intellectual history it
  usually does: name who argued, wrote, replied.

## Hedging and interpretive claims

Match the confidence of the sentence to the kind of evidence behind it.

- **What a text says** can be stated flatly, with a locator.
- **What an author meant or intended** is an inference: use *suggests*,
  *seems to*, *I read this as* unless the author says so.
- **Influence and reception** need documentary evidence (a citation, a
  letter, a marginal note, ownership). Without it, write *resembles* or
  *anticipates*, never *influenced* or *drew on*.
- **Causal claims about ideas and events** deserve the most caution; say
  what the evidence shows and what the claim depends on.
- Do not hedge what the scholarly consensus holds firmly; do not
  assert as settled what the field disputes — name the dispute.

## Historical discipline in prose

- **Avoid anachronism.** Do not use a later category (*liberal*,
  *the state*, *the individual*, *ideology*, *the Enlightenment*) as if
  the author would have recognised it; if you use it as an analytic term,
  say so on first use.
- **Avoid teleology and "precursors".** Not *"anticipated Rawls"*, unless
  the claim is about a later reader's reconstruction.
- **Name the interlocutors.** Say who in the period the author was
  arguing with. A text is a move in a debate; a paragraph that treats it as
  a free-standing statement of doctrine is incomplete.
- **Distinguish** the author's own words, the editor's, the translator's,
  and your gloss.

## Structure

- State **the question, the interlocutors and your claim** within the first
  page. A historiographical position (what is contested, where you
  stand) belongs there, not in a free-standing "literature review".
- **Topic sentences** open paragraphs. **Signposting** at transitions.
- **Synthesis over enumeration** applies to scholarship too: do not march
  through *"A argues… B argues… C argues…"*. Group scholars by the
  position they hold, say what divides them, and say where you stand.
- Sections follow the argument, not a template; there is no mandatory
  IMRaD.

## Terms

- **Define a term on first substantive use**, not first mention, in the
  sense *your period's authors* used it, then say if you use it differently.
- **Consistent terminology**; do not drift between *sovereignty*,
  *supreme power* and *majesty* for the same concept without saying whether
  the period distinguished them.
- Expand abbreviations of editions and series on first use
  (*Cambridge Texts in the History of Political Thought*, CTHPT).

## Red flags

- A citation with no page or locator.
- `(Author 1969)` author-date citations in a notes-bibliography project.
- A quotation from a translation cited as if it were the original.
- *"X influenced Y"* with no documentary evidence.
- A modern category projected onto an earlier author with no warning.
- A chain of *"A argues… B argues…"* paragraphs.
- A foreign term used with no gloss, or silently translated.
- Hand-typed `Hobbes, Leviathan, 91` instead of a `[@key, p. 91]`.
