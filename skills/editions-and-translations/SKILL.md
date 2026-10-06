---
name: editions-and-translations
description: Use when adding or fixing a book, chapter or primary text in Zotero that exists in several editions or translations, or when a citation's page number depends on which edition was read. Trigger phrases "add the translation", "another edition of", "which edition", "link the editions", "original date". Do NOT use for general Zotero housekeeping — use `zotero-operations`. Do NOT use for note-taking on a text — use `reading-notes`.
---

# Editions and translations

> **Glossary:** **BBT**, **MCP**: see [skills/_glossary.md](../_glossary.md).

In the history of ideas the same work is read in several editions,
languages and translations, and **page numbers do not transfer between
them**. This skill fixes the Zotero model so a citation always points at
the edition that was actually read.

## The model: one Zotero item per edition, linked by Related

- **Each edition or translation is its own Zotero item**, with its own
  BBT key, its own PDF or scan, and its own notes. Never reuse one item
  for two editions.
- **Every edition is registered in the others' Related field**, using
  `mcp__zotero__zotero_add_item_relation` (bidirectional: one call links
  both items). For three editions, link all three pairs.
- A **cited edition** is the one whose pages the manuscript's locators
  refer to. Tag it `edition:cited` so it can be found with
  `mcp__zotero__zotero_search_by_tag`.

## Fields that must be filled

| Field | Where | Example |
|---|---|---|
| Original date | `Extra`: `original-date: 1651` | Hobbes, *Leviathan* |
| Original title (translations) | `Extra`: `original-title: Leviathan` | |
| Original language / this edition's language | `Language` | `la`, `de`, `en` |
| Translator, editor | creators, with the correct creator type | translator: Tuck |
| Edition | `Edition` | `Student ed., rev.` |
| Series | `Series` | `Cambridge Texts in the History of Political Thought` |

CSL reads `original-date` and `original-title` from `Extra`, so the
Chicago bibliography shows them. Set fields with
`mcp__zotero__zotero_update_item`.

## Procedure: adding an edition

1. **Search first.** `mcp__zotero__zotero_search_items` by title, author
   and year. Do not create a duplicate of an item that exists.
2. If the edition is not in the library, add it with
   `mcp__zotero__zotero_add_item` (`source_type="doi"` when there is a
   DOI, else `"url"`), then fill the fields above. Books usually have
   no DOI: identify by ISBN.
3. **Link** it to each sibling edition with
   `mcp__zotero__zotero_add_item_relation`.
4. Fetch the BBT key with `mcp__zotero__zotero_get_item_metadata`
   (`format="bibtex"`). Never hand-craft keys.
5. If the project cites this edition, tag it `edition:cited`. Remove the
   tag from a sibling the project no longer cites; a project cites **one
   edition per work** unless the argument compares them.

## Checking

- `mcp__zotero__zotero_get_item_related` lists an item's editions. Run it
  before citing to confirm which edition a key refers to.
- If two items carry the same `original-date` and title but are not
  linked, they are probably unregistered editions: link them or merge
  them if they are in fact the same edition (`zotero-operations`).
- When the manuscript changes cited edition, every locator for that
  work must be re-checked against the new edition: hand the work to
  `fact-check`.

## If the relations tools are missing

`zotero_add_item_relation` belongs to the `relations` toolset of
zotero-mcp, enabled by `ZOTERO_MCP_TOOLSETS` in the MCP registration.
`/setup` registers it for new installs. For an existing install, ask the
user to re-register the Zotero MCP server with
`libraries,search-admin,pdf-geometry,duplicates,relations,scite`. Do not
fall back to writing Related links by hand through Extra.

## Red flags

- Two editions in one Zotero item.
- A citation whose locator was read in a different edition than the item
  it points at.
- A translation item with no translator creator or no `original-date`.
- Editions linked in one direction only (use the MCP relation tool, which
  links both).
