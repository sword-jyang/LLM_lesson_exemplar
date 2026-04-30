#!/usr/bin/env python3
"""Find catalog entries matching one or more keywords.

A weak LLM following the "grep names → match → Read offset/limit → substitute
placeholder" protocol from AGENTS.md is likely to skip steps. This script
collapses the protocol into one command: every catalog entry whose name,
topics, source, or notes contains the keyword(s) is printed in a compact,
ready-to-use form (URL or expanded template, default STAC asset, key flags).

Usage:
    python scripts/find_dataset.py <keyword> [<keyword> ...]
    python scripts/find_dataset.py fire
    python scripts/find_dataset.py climate precipitation
    python scripts/find_dataset.py building Wyoming     # match across fields

Matches are case-insensitive substrings. Multiple keywords are AND-ed.
For templated entries, the script prints the template with each variant
plugged in (truncated to the first 5 if the variant list is long).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

CATALOG_PATH = Path(__file__).resolve().parent.parent / "data_catalog.yml"


def haystack(entry: dict) -> str:
    parts = [
        entry.get("name", ""),
        entry.get("source", ""),
        entry.get("notes", ""),
        " ".join(entry.get("topics", [])),
        " ".join(str(v) for v in entry.get("variants", [])),
        entry.get("stac_collection", ""),
        entry.get("url", ""),
        entry.get("url_template", ""),
    ]
    return " ".join(parts).lower()


def expand_template(entry: dict, max_variants: int = 5) -> list[str]:
    """Return concrete URLs for a templated entry (truncated)."""
    template = entry["url_template"]
    variants = entry.get("variants", [])
    placeholder_match = re.search(r"\{(\w+)\}", template)
    if not placeholder_match or not variants:
        return [template]
    placeholder = placeholder_match.group(1)
    shown = variants[:max_variants]
    expanded = [template.format(**{placeholder: v}) for v in shown]
    if len(variants) > max_variants:
        expanded.append(f"... and {len(variants) - max_variants} more variants: "
                        + ", ".join(str(v) for v in variants[max_variants:max_variants + 5])
                        + ("…" if len(variants) > max_variants + 5 else ""))
    return expanded


def format_entry(entry: dict) -> str:
    lines = [f"  name:   {entry['name']}"]
    lines.append(f"  type:   {entry.get('type', '?')}")
    if entry.get("topics"):
        lines.append(f"  topics: {', '.join(entry['topics'])}")
    if "url" in entry:
        lines.append(f"  url:    {entry['url']}")
    if "url_template" in entry:
        lines.append(f"  url_template: {entry['url_template']}")
        for u in expand_template(entry):
            lines.append(f"    → {u}")
    if "stac_collection" in entry:
        lines.append(f"  stac_collection:    {entry['stac_collection']}")
        if "stac_asset_default" in entry:
            lines.append(f"  stac_asset_default: {entry['stac_asset_default']}")
    notes = entry.get("notes", "").strip()
    if notes:
        notes_oneline = " ".join(notes.split())
        if len(notes_oneline) > 240:
            notes_oneline = notes_oneline[:240] + "…"
        lines.append(f"  notes:  {notes_oneline}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    keywords = [k.lower() for k in argv]

    with open(CATALOG_PATH) as f:
        catalog = yaml.safe_load(f) or {}
    entries = catalog.get("datasets", [])

    matches = [e for e in entries if all(k in haystack(e) for k in keywords)]

    if not matches:
        print(f"No catalog entries match: {' '.join(keywords)}", file=sys.stderr)
        print(f"(Searched {len(entries)} entries in {CATALOG_PATH.name}.)", file=sys.stderr)
        return 1

    print(f"Found {len(matches)} match(es) for: {' '.join(keywords)}\n")
    for entry in matches:
        print(format_entry(entry))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
