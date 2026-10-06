"""Per-project screening configuration for a historiographical survey.

The humanities counterpart of `screening_config.py`. Install it into your
project AS `screening_config.py` (the pipeline scripts read that name):

    python3 ${CLAUDE_PLUGIN_ROOT}/scripts/setup/install_templates.py \\
        survey_screening_config.py:screening_config.py

`abstract_screen.py` and `fulltext_code.py` read it by path (`--config`);
they are unchanged from the systematic-review pipeline. What differs is
what the prompts ask: relevance to an interpretive question, and a record of
each work's thesis, school and sources in place of sample and method.

Scope. These scripts work on articles and chapters that have an abstract or
a PDF of manageable length (the full-text cap is ~720,000 characters).
Books go through the `reading-notes` skill instead, not through
`fulltext_code.py`.

Keep this file in git. The prompts are the scope of the survey.
"""

# MANDATORY. Namespace for every Zotero tag this survey writes, e.g.
# `hobbes-reception/abstract:include`. Set it with:
#     python3 ${CLAUDE_PLUGIN_ROOT}/scripts/setup/set_tag_prefix.py --prefix <prefix>
TAG_PREFIX = ""


# =============================================================================
# Stage 1: relevance triage on title + abstract
# =============================================================================

ABSTRACT_SCREENING_MODEL = ""
ABSTRACT_SCREENING_PROMPT_VERSION = "v1-survey"

ABSTRACT_SCREENING_SYSTEM_PROMPT = """\
You are triaging scholarship for a historiographical survey in intellectual \
history and the history of philosophy. Decide whether a work bears on this \
question:

**<INSERT YOUR RESEARCH QUESTION HERE>**

Period: <e.g. 1500-1700>. Texts, authors or debates in scope: <list>. \
Languages: the title and abstract may be in any of <e.g. English, German, \
Hungarian, Slovenian, Russian, French>. Judge the work in its own language. \
Do not exclude a work because of its language, or because its abstract is \
not in English. Write the REASON in English.

A work is relevant if it does at least one of:

1. Interprets the primary texts or authors in scope (monograph, article, \
chapter, commentary, critical edition).
2. Reconstructs the context the question depends on: the debate, the \
institutions, the vocabulary, the readers.
3. Is itself a historiographical or methodological intervention on the \
question (including the theory and philosophy of history where in scope).

NOT relevant: works that only mention the author in passing; works on a \
different period or tradition with no bearing on the question; textbooks \
and encyclopedia entries (unless the question is about reception).

DECISION RULES:
- INCLUDE: title and abstract clearly meet at least one test above.
- EXCLUDE: clearly none. Use a code:
  E1-wrong period or tradition
  E2-passing mention only
  E3-not scholarship (news, review of a different book, bibliographic list)
  E4-duplicate edition or translation of an already-included work
  E5-other irrelevant domain
- BORDERLINE: when uncertain. Humanities abstracts are often missing or \
uninformative, and a title like "Reflections on Leviathan" does not decide \
anything. A missing abstract is BORDERLINE, never EXCLUDE.

BIAS: Be liberal. When uncertain between include and borderline, choose \
include; between borderline and exclude, choose borderline.

Respond with EXACTLY two lines:
DECISION: include|borderline|exclude
REASON: <one sentence naming the test or exclusion code>
"""


# =============================================================================
# Stage 2: interpretive coding on the full text (articles and chapters)
# =============================================================================

FULLTEXT_CODING_MODEL = ""
FULLTEXT_CODING_PROMPT_VERSION = "v1-survey"

# Free-text fields are quoted or paraphrased from the work, with page
# references so each claim can be checked. Categorical fields declare a
# closed `values` list; `tag: True` also writes them as Zotero tags.
FULLTEXT_CODING_FIELDS = [
    {
        "name": "thesis",
        "description": "The work's central claim about the texts, authors or "
                       "debate in scope, in one to three sentences, in your "
                       "words. Add the page where the claim is stated, e.g. "
                       "'(p. 12)'.",
    },
    {
        "name": "interlocutors",
        "description": "The scholars or schools the work argues with or "
                       "against, by name, with what the disagreement is. "
                       "Empty if it positions itself against no one.",
    },
    {
        "name": "primary_sources",
        "description": "The primary texts, archives or editions the argument "
                       "rests on, as named in the work. Note the edition or "
                       "translation if the work gives it.",
    },
    {
        "name": "context_claimed",
        "description": "The historical context the work uses to interpret the "
                       "text: period, institutions, controversy, audience. "
                       "One or two sentences.",
    },
    {
        "name": "school_or_method",
        "description": "The work's interpretive approach, judged from how it "
                       "argues, not from what it says about itself.",
        "values": [
            "contextualist",
            "history-of-concepts",
            "textual-exegesis",
            "reconstructive-philosophical",
            "social-or-material",
            "reception-history",
            "genealogical",
            "other",
        ],
        "tag": True,
    },
    {
        "name": "work_type",
        "description": "What kind of scholarship this is.",
        "values": [
            "monograph-chapter",
            "article",
            "critical-edition-introduction",
            "commentary",
            "historiographical-essay",
            "theoretical-essay",
        ],
        "tag": True,
    },
    {
        "name": "language_and_translation",
        "description": "The language of the work (give the ISO tag, e.g. 'hu') "
                       "and the languages and "
                       "translations of the primary sources it uses, e.g. "
                       "'English; Latin and French originals, own "
                       "translations'.",
    },
    {
        "name": "key_passages",
        "description": "Up to three passages worth returning to, quoted "
                       "exactly, each with its page number. Do not "
                       "paraphrase here.",
    },
    {
        "name": "limits_and_gaps",
        "description": "What the work itself says it leaves out, and any "
                       "evident gap relative to the survey's question.",
    },
]

FULLTEXT_CODING_SYSTEM_PROMPT = """\
You are coding scholarship for a historiographical survey in intellectual \
history and the history of philosophy. You read the full text of an article \
or chapter and extract a structured record.

RESEARCH QUESTION:
<INSERT YOUR RESEARCH QUESTION — same as abstract screening>

The work reached this stage because its title and abstract passed. Confirm \
from the full text whether it bears on the question (see the three tests \
below); if so, extract the fields.

Relevant if it (1) interprets the primary texts or authors in scope, (2) \
reconstructs the context the question depends on, or (3) is a \
historiographical or methodological intervention on the question.

EXCLUSION CODES (full-text stage):
  FE1-does not bear on the question once read
  FE2-passing mention only
  FE3-not scholarship (review, bibliography, reprint of a primary text)
  FE4-same work as an included edition or translation
  FE5-other

OUTPUT FORMAT: strict JSON, one object.

{{
  "decision": "include" | "exclude",
  "exclusion_code": "<code or empty if include>",
  "reason": "<one to three sentences>",
  {coding_fields_json_placeholder}
}}

Rules:
- For every field provide substantive content if include, or an empty string \
if exclude.
- Extract from the body of the work, not from the abstract.
- Report what the work says, not what you think of it. Where you infer \
(the school, the context), say so.
- Write the fields in English, but quote in the work's own language where a \
field asks for quotation, and never translate a quotation silently: if you \
add a translation, label it "[machine translation]".
- Quote exactly where a field asks for quotation, and give page numbers \
from the text's own pagination. If page numbers are not visible, say \
"page not visible"; never invent one.
- Do not attribute a claim to the work's author unless the text makes it. \
Mark a cited position as the cited author's, not the work's.
- Return ONLY the JSON object.
"""
