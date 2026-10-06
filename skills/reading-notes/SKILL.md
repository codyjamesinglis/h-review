---
name: reading-notes
description: Use when reading a book, chapter or primary text for a humanities project and recording notes, quotations or concepts in Zotero. Trigger phrases "take notes on", "extract quotations", "reading note", "pull the highlights", "what did I annotate", "track this concept". Do NOT use for citing in prose — use `grounded-citations`. Do NOT use for adding editions — use `editions-and-translations`.
---

# Reading notes

> **Glossary:** **BBT**, **MCP**: see [skills/_glossary.md](../_glossary.md).

Notes are the durable consultation artifact that `grounded-citations`
relies on: a note with a **page number** in the **edition read** survives
context compaction and lets any later citation be written and checked
without re-reading the book. This skill fixes the format.

## Where notes live

As Zotero **child notes** of the edition item that was read
(`editions-and-translations`), created with
`mcp__zotero__zotero_manage_note`. One of each kind per item:

- **`Reading note`**: what the text argues and does, in your words.
- **`Quotations`**: verbatim passages with locators.

Never put notes on a different edition's item than the one read.

## Reading note format

Begin with the heading `Reading note`, then:

- **Text and edition**: BBT key, edition, language, translation used.
- **Question**: why you are reading it (the project's question).
- **Argument** in a few sentences, with locators: `(pp. 91–93)`.
- **Moves and interlocutors**: who the author is answering, and what the
  author is doing (defending, refuting, redefining a term).
- **Concepts**: terms the author uses in a technical sense, as the author
  uses them.
- **Open problems**: what you could not decide. Do not paper over.

Separate *what the text says* from *your interpretation*. Mark
interpretation with *I read this as*.

## Quotations format

Begin with the heading `Quotations`. One entry per passage:

```
"<verbatim text>" — p. 91 [lang: en; trans. Tuck]
  gloss: <one line: why it matters>
  concept: sovereignty
```

- **Verbatim, exact**, including spelling and punctuation. Mark omissions
  `[…]` and your insertions `[like this]`.
- **Locator is mandatory** and from the edition read; use the text's
  standard pagination where it exists (`A51/B75`).
- For a translation, record the translator; add the original wording
  under `orig:` when the argument turns on it.
- Check each extracted quotation against the page image or PDF. OCR
  errors in scanned books are common (`mcp__zotero__zotero_read_pdf_pages`).

## Extracting from Zotero annotations

1. `mcp__zotero__zotero_get_annotations` on the PDF attachment's parent
   item returns highlights and comments with page labels.
2. Use the **page label** (the printed page), not the PDF page index,
   as the locator when they differ. If the PDF is a scan with no
   labels, say so in the note.
3. `mcp__zotero__zotero_synthesize_annotations` helps cluster them.
   Treat its output as a draft: verify each quotation and locator, then
   write the `Quotations` note.
4. Write with `mcp__zotero__zotero_manage_note` (`action="create"`; on a
   re-read, `append=true` to the existing `Quotations` note rather than
   a second note).

## Tracking concepts and thinkers

- Tag **notes or items** with the project's namespace if it has one:
  `<TAG_PREFIX>/concept:<term>`, `<TAG_PREFIX>/thinker:<surname>`.
  Terms in the original language where the period had one
  (`concept:potestas`). Without a project prefix use `concept:` and
  `thinker:` directly. Add tags with `mcp__zotero__zotero_manage_note`'s
  `tags` or `mcp__zotero__zotero_update_item`.
- Search with `mcp__zotero__zotero_search_by_tag` to collect every
  passage on a concept across texts.
- One tag per concept, one spelling. Check existing tags with
  `mcp__zotero__zotero_get_tags` before inventing one.

## Reading in another language

Take the note in English or your working language, but quote the original
and give the original term beside your gloss. Say which translation, if
any, you consulted for the passage, and where you departed from it.

## Red flags

- A quotation with no locator, or a locator not from the edition read.
- A paraphrase presented in the `Quotations` note.
- A note on the translation item that records pages from the original.
- A quotation reproduced from memory or from an LLM, not from the page.
- Two notes of the same kind on one item.
