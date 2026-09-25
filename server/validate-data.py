#!/usr/bin/env python3
"""Validate TechFreedom static catalogue data."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "assess" / "data"
TOOLS_PATH = DATA / "tools.json"
ALTS_PATH = DATA / "alternatives.json"
ALT_PAGE = ROOT / "alternatives" / "index.html"

REQUIRED_ALT_FIELDS = {
    "id", "name", "slug", "category", "alternativeTo", "provider", "hqCountry",
    "openSource", "selfHostable", "dataHosting", "jurisdiction", "continuity",
    "surveillance", "lockIn", "costExposure", "total", "approxCost",
    "migrationDifficulty", "tradeoffs", "lastReviewed",
}
SCORE_FIELDS = ("jurisdiction", "continuity", "surveillance", "lockIn", "costExposure")
MIN_ALTERNATIVES = 60


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def main() -> int:
    tools = load_json(TOOLS_PATH)
    alternatives = load_json(ALTS_PATH)
    errors: list[str] = []

    tool_slugs = {tool["slug"] for tool in tools}
    if len(tool_slugs) != len(tools):
        fail(errors, "tools.json contains duplicate slugs")

    alt_slugs = [alt.get("slug") for alt in alternatives]
    if len(set(alt_slugs)) != len(alt_slugs):
        fail(errors, "alternatives.json contains duplicate slugs")

    alt_ids = [alt.get("id") for alt in alternatives]
    if len(set(alt_ids)) != len(alt_ids):
        fail(errors, "alternatives.json contains duplicate ids")

    if len(alternatives) < MIN_ALTERNATIVES:
        fail(errors, f"expected at least {MIN_ALTERNATIVES} alternatives, found {len(alternatives)}")

    coverage = Counter()

    for alt in alternatives:
        label = alt.get("slug") or alt.get("name") or "<unknown>"
        missing = sorted(REQUIRED_ALT_FIELDS - set(alt))
        if missing:
            fail(errors, f"{label}: missing fields: {', '.join(missing)}")

        for field in SCORE_FIELDS:
            score = alt.get(field)
            if not isinstance(score, int) or not 1 <= score <= 5:
                fail(errors, f"{label}: {field} must be an integer from 1 to 5")

        scores = [alt.get(field) for field in SCORE_FIELDS]
        if all(isinstance(score, int) for score in scores):
            expected_total = sum(scores)
            if alt.get("total") != expected_total:
                fail(errors, f"{label}: total={alt.get('total')} but lens sum={expected_total}")

        links = alt.get("alternativeTo")
        if not isinstance(links, list) or not links:
            fail(errors, f"{label}: alternativeTo must contain at least one tool slug")
            continue

        for slug in links:
            if slug not in tool_slugs:
                fail(errors, f"{label}: alternativeTo references missing tool slug '{slug}'")
            else:
                coverage[slug] += 1

    uncovered = sorted(tool_slugs - set(coverage))
    if uncovered:
        fail(errors, "tools with no alternatives: " + ", ".join(uncovered))

    # The page keeps a fallback copy for resilience. It must match the JSON source.
    page = ALT_PAGE.read_text(encoding="utf-8")
    match = re.search(
        r"var ALTERNATIVES_FALLBACK = (\[.*?\]);\s*\n\s*var TOOLS = TOOLS_FALLBACK;",
        page,
        flags=re.S,
    )
    if not match:
        fail(errors, "could not locate ALTERNATIVES_FALLBACK in alternatives/index.html")
    else:
        try:
            fallback = json.loads(match.group(1))
            if fallback != alternatives:
                fail(errors, "alternatives/index.html fallback is out of sync with alternatives.json")
        except json.JSONDecodeError as exc:
            fail(errors, f"alternatives/index.html fallback is not valid JSON: {exc}")

    if errors:
        print("Catalogue validation FAILED")
        for error in errors:
            print(f" - {error}")
        return 1

    category_counts = Counter(alt["category"] for alt in alternatives)
    print("Catalogue validation passed")
    print(f" Tools: {len(tools)}")
    print(f" Alternatives: {len(alternatives)}")
    print(f" Tools covered: {len(coverage)}/{len(tools)}")
    print(" Categories:")
    for category, count in sorted(category_counts.items()):
        print(f"   {category}: {count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
