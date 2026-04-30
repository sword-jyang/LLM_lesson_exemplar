#!/usr/bin/env python3
"""
Scrape the ESIIL Data Library for dataset download URLs and print new
entries not already present in data_catalog.yml.

Usage:
    python scripts/sync_esiil_catalog.py

Output is printed as YAML to stdout. Review the candidates and manually
add useful entries to data_catalog.yml.

Source: https://cu-esiil.github.io/data-library/
GitHub: https://github.com/CU-ESIIL/data-library
"""

import re
import sys
from pathlib import Path

import requests
import yaml

ESIIL_MKDOCS = (
    "https://raw.githubusercontent.com/CU-ESIIL/data-library/main/mkdocs.yml"
)
ESIIL_RAW_BASE = (
    "https://raw.githubusercontent.com/CU-ESIIL/data-library/main/docs"
)
CATALOG_PATH = Path(__file__).parent.parent / "data_catalog.yml"

# File extensions that indicate a direct data download
DATA_EXTENSIONS = (
    ".zip", ".tif", ".tiff", ".csv", ".nc", ".geojson",
    ".json", ".shp", ".gpkg", ".img", ".gz",
)

# Substrings that identify non-data URLs (docs, badges, package registries)
SKIP_PATTERNS = (
    "github.com", "shields.io", "badge", ".png", ".jpg", ".svg",
    "pypi.org", "anaconda.org", "readthedocs", "conda.io",
)


def get_topic_paths(mkdocs_url: str) -> list[str]:
    """Parse the ESIIL mkdocs.yml nav and return topic index .md page paths."""
    r = requests.get(mkdocs_url, timeout=15)
    r.raise_for_status()
    config = yaml.safe_load(r.text)

    paths: list[str] = []

    def walk(node):
        if isinstance(node, dict):
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for item in node:
                walk(item)
        elif isinstance(node, str) and node.endswith(".md"):
            paths.append(node)

    walk(config.get("nav", []))
    return paths


def get_dataset_paths(topic_paths: list[str]) -> list[str]:
    """Follow links inside topic index pages to find individual dataset pages."""
    dataset_paths: list[str] = []
    for topic_path in topic_paths:
        if not topic_path.startswith("topic/"):
            continue
        raw_url = f"{ESIIL_RAW_BASE}/{topic_path}"
        try:
            r = requests.get(raw_url, timeout=10)
            if r.status_code != 200:
                continue
            # Links look like: [Name](../hazards/Air_data/Air_data.md)
            for link in re.findall(r'\]\(\.\./([^)]+\.md)\)', r.text):
                dataset_paths.append(link)
        except Exception as e:
            print(f"  SKIP topic {topic_path}: {e}", file=sys.stderr)
    return dataset_paths


def extract_data_urls(md_text: str) -> set[str]:
    """Return data download URLs found inside code blocks in a markdown file."""
    code_blocks = re.findall(r"```[\s\S]*?```", md_text)
    urls: set[str] = set()
    for block in code_blocks:
        for raw_url in re.findall(r'https?://[^\s\'">\)]+', block):
            url = raw_url.rstrip(".,;)")
            if not any(url.lower().endswith(ext) for ext in DATA_EXTENSIONS):
                continue
            if any(skip in url for skip in SKIP_PATTERNS):
                continue
            urls.add(url)
    return urls


def main() -> int:
    with open(CATALOG_PATH) as f:
        catalog = yaml.safe_load(f) or {}
    # Templated entries (url_template + variants) have no top-level `url`; skip
    # them — they cover one-pattern dataset families that the ESIIL sync would
    # not propose as new candidates anyway.
    existing_urls = {d["url"] for d in catalog.get("datasets", []) if "url" in d}

    print(f"Fetching ESIIL nav from {ESIIL_MKDOCS} …", file=sys.stderr)
    try:
        topic_paths = get_topic_paths(ESIIL_MKDOCS)
    except Exception as e:
        print(f"ERROR fetching ESIIL mkdocs.yml: {e}", file=sys.stderr)
        return 1

    print(f"Found {len(topic_paths)} topic pages — discovering dataset pages …", file=sys.stderr)
    paths = get_dataset_paths(topic_paths)
    print(f"Found {len(paths)} dataset pages — scanning for data URLs …", file=sys.stderr)

    new_entries: list[dict] = []
    seen_urls: set[str] = set(existing_urls)

    for md_path in paths:
        raw_url = f"{ESIIL_RAW_BASE}/{md_path}"
        try:
            r = requests.get(raw_url, timeout=10)
            if r.status_code != 200:
                continue
            urls = extract_data_urls(r.text)
            for url in urls:
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                # Derive a readable name from the path segment
                name = Path(md_path).stem.replace("_", " ").title()
                # Category is the first path component (e.g. "hazards")
                category = md_path.split("/")[0] if "/" in md_path else "unknown"
                new_entries.append({
                    "name": name,
                    "type": "unknown",   # review and update before committing
                    "source": f"ESIIL Data Library — {category}",
                    "url": url,
                    "notes": f"Scraped from {raw_url} — verify type and add notes before committing.",
                })
        except Exception as e:
            print(f"  SKIP {md_path}: {e}", file=sys.stderr)

    if new_entries:
        print(
            f"\n# {len(new_entries)} new candidate URL(s) — review, set 'type', "
            "update 'notes', then add to data_catalog.yml:\n"
        )
        print(yaml.dump({"datasets": new_entries}, default_flow_style=False, allow_unicode=True))
    else:
        print("\nNo new URLs found — data_catalog.yml is up to date.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
