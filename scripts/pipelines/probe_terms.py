#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "requests>=2.31",
#     "urllib3>=2.0",
#     "tenacity>=8.0",
# ]
# ///
"""Count OpenAlex hits for every term in `TERMS_BY_LANGUAGE`, before searching.

A translated search term is a guess. This script gives the guess evidence:
how many works OpenAlex returns for each quoted term in the project's year
window. A term with no hits is spelled wrongly, inflected, or not what the
literature calls the thing, and is worth a second look; a term with
thousands of hits is probably too general. It cannot tell you that a
translation is *right*, only that it is *used*. Read-only; no key needed.

Usage:
    uv run probe_terms.py --config ./search_config.py
    uv run probe_terms.py --config ./search_config.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import http_client  # noqa: E402
import languages  # noqa: E402

API = "https://api.openalex.org/works"


def count_hits(term: str, from_year: int, to_year: int, session) -> int | None:
    """OpenAlex `meta.count` for the quoted term, or None if the call failed."""
    data = http_client.get_json(
        session, API,
        params={
            "search": f'"{languages.nfc(term)}"',
            "filter": f"publication_year:{from_year}-{to_year}",
            "per-page": 1,
        },
    )
    if data is None:
        return None
    return int((data.get("meta") or {}).get("count", 0))


def probe(config, session) -> list[dict]:
    problems = languages.validate_terms_by_language(
        getattr(config, "TERMS_BY_LANGUAGE", None))
    if problems:
        raise ValueError("; ".join(problems))
    out = []
    for tag, blocks in config.TERMS_BY_LANGUAGE.items():
        for key in ("a", "b"):
            for term in blocks.get(key) or []:
                out.append({
                    "language": tag, "block": key, "term": term,
                    "hits": count_hits(term, config.FROM_YEAR, config.TO_YEAR,
                                       session),
                })
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--config", default="./search_config.py")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    import screening_common
    config = screening_common.load_config_module(
        args.config, "search_config",
        required=("FROM_YEAR", "TO_YEAR", "TERMS_BY_LANGUAGE"),
    )
    session = http_client.build_session()
    try:
        results = probe(config, session)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        for r in results:
            hits = "request failed" if r["hits"] is None else f"{r['hits']:>9,}"
            flag = "  <-- no hits: check spelling or inflection" if r["hits"] == 0 else ""
            print(f"{r['language']:8} {r['block']}  {hits}  {r['term']}{flag}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
