"""Language tags used by the multilingual search config.

Stdlib-only. `TERMS_BY_LANGUAGE` in a project's `search_config.py` is keyed by
these tags; this module says which are recognised and carries the notes a
reader of the config needs. Tags are BCP 47 style: an ISO 639 language, with
a script subtag where one language is written in two (`sr-Latn`, `sr-Cyrl`).

Serbo-Croatian is the awkward case. Croatian, Serbian and Bosnian are
standardised separately, differ in vocabulary and (Serbian) in script, and
a bibliographic record may use any of them or the umbrella `sh`. Give terms
for each variety the scholarship may be in; a search in one variety does not
find titles in another reliably.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class Language:
    tag: str
    name: str
    script: str          # "Latn", "Cyrl", "Grek"
    note: str = ""


LANGUAGES: dict[str, Language] = {lang.tag: lang for lang in (
    Language("en", "English", "Latn"),
    Language("de", "German", "Latn",
             "Compounds and nouns capitalised; search the stem with and "
             "without umlauts (ä/ae). Older texts: Fraktur-era spelling."),
    Language("hu", "Hungarian", "Latn",
             "Agglutinative: a noun appears in many case forms, and a "
             "phrase search for the nominative misses them."),
    Language("hr", "Croatian", "Latn"),
    Language("sr-Latn", "Serbian (Latin)", "Latn"),
    Language("sr-Cyrl", "Serbian (Cyrillic)", "Cyrl"),
    Language("bs", "Bosnian", "Latn"),
    Language("sh", "Serbo-Croatian (umbrella)", "Latn",
             "Used by some catalogues for any of hr/sr/bs."),
    Language("sl", "Slovenian", "Latn", "Has a dual number; inflected."),
    Language("pl", "Polish", "Latn", "Inflected; diacritics (ł, ą, ę)."),
    Language("cs", "Czech", "Latn", "Inflected; diacritics (ř, ě, š)."),
    Language("sk", "Slovak", "Latn", "Inflected; diacritics (ľ, ĺ, ŕ)."),
    Language("ro", "Romanian", "Latn",
             "Diacritics ș/ț are often typed as ş/ţ (cedilla); search both."),
    Language("uk", "Ukrainian", "Cyrl",
             "Transliteration from catalogues varies (KMU vs. ALA-LC)."),
    Language("ru", "Russian", "Cyrl",
             "Pre-1918 orthography differs (ѣ, ъ at word end)."),
    Language("it", "Italian", "Latn"),
    Language("fr", "French", "Latn"),
    Language("la", "Latin", "Latn",
             "Spelling varies by period and editor (u/v, i/j, ae/e)."),
    Language("grc", "Ancient Greek", "Grek", "Polytonic; accents vary."),
)}


def validate_tag(tag: str) -> str:
    """Return `tag` if recognised, else raise ValueError naming the options."""
    if tag in LANGUAGES:
        return tag
    raise ValueError(
        f"unknown language tag {tag!r}. Known: {', '.join(sorted(LANGUAGES))}"
    )


def validate_terms_by_language(terms: dict) -> list[str]:
    """Problems with a `TERMS_BY_LANGUAGE` dict, as messages (empty if fine)."""
    problems: list[str] = []
    if not isinstance(terms, dict) or not terms:
        return ["TERMS_BY_LANGUAGE must be a non-empty dict"]
    seen_any = False
    for tag, blocks in terms.items():
        try:
            validate_tag(tag)
        except ValueError as exc:
            problems.append(str(exc))
            continue
        if not isinstance(blocks, dict) or not (set(blocks) <= {"a", "b"}):
            problems.append(f"{tag}: value must be a dict with keys 'a' and/or 'b'")
            continue
        for key in ("a", "b"):
            for term in blocks.get(key) or []:
                seen_any = True
                if not isinstance(term, str) or not term.strip():
                    problems.append(f"{tag}[{key}]: empty or non-string term")
                    continue
                script = LANGUAGES[tag].script
                if script == "Cyrl" and not re.search(r"[Ѐ-ӿ]", term):
                    problems.append(
                        f"{tag}[{key}]: {term!r} has no Cyrillic letters; "
                        f"this tag is for Cyrillic. Use a Latin tag, or "
                        f"`sr-Latn` for Serbian in Latin script.")
                if script == "Latn" and re.search(r"[Ѐ-ӿ]", term):
                    problems.append(
                        f"{tag}[{key}]: {term!r} is Cyrillic under a Latin tag.")
    if not seen_any and not problems:
        problems.append("TERMS_BY_LANGUAGE has no terms")
    return problems


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)
