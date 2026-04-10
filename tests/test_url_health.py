"""
URL health checks for data_catalog.yml.

Sends a lightweight request to each URL to verify reachability.
NEVER fails the test suite — collects and reports dead URLs as warnings only,
since URL staleness is outside this repo's control.

Run separately with: pytest tests/test_url_health.py -v -s
"""

import sys
from pathlib import Path

import pytest
import requests
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

CATALOG = Path(__file__).parent.parent / "data_catalog.yml"
REQUEST_TIMEOUT = 20  # seconds


def load_urls():
    """Return list of (label, url) tuples from data_catalog.yml.
    Entries with health_check: skip are excluded."""
    with open(CATALOG) as f:
        catalog = yaml.safe_load(f)
    urls = []
    for entry in catalog.get("datasets", []):
        if entry.get("health_check") == "skip":
            continue
        urls.append((entry["name"], entry["url"]))
        if entry.get("labels_url"):
            urls.append((entry["name"] + " (labels)", entry["labels_url"]))
    return urls


def check_url(url: str) -> tuple[bool, str]:
    """Return (ok, message).
    - OPeNDAP (dodsC): request .dds suffix — returns metadata without triggering a download
    - Everything else: HEAD request
    """
    if "dodsC" in url:
        # Strip any existing suffix and request .dds (dataset descriptor — lightweight metadata)
        check_url_str = url.split("?")[0].rstrip("/") + ".dds"
        method = "GET"
    else:
        check_url_str = url
        method = "HEAD"
    try:
        r = requests.request(
            method, check_url_str,
            timeout=REQUEST_TIMEOUT,
            stream=True,
            headers={"User-Agent": "Mozilla/5.0"},
            allow_redirects=True,
        )
        if r.status_code < 400:
            return True, f"HTTP {r.status_code}"
        return False, f"HTTP {r.status_code}"
    except requests.exceptions.Timeout:
        return False, "Timeout"
    except requests.exceptions.ConnectionError as e:
        return False, f"Connection error: {e}"
    except Exception as e:
        return False, str(e)


@pytest.mark.url_health
def test_all_catalog_urls_reachable():
    """Check every URL in data_catalog.yml. Report failures but always pass."""
    urls = load_urls()
    failures = []
    for name, url in urls:
        ok, message = check_url(url)
        status = "OK" if ok else "DEAD"
        print(f"  [{status}] {name}: {url}  ({message})")
        if not ok:
            failures.append(f"  {name}: {url}  ({message})")

    if failures:
        print(f"\n⚠  {len(failures)} unreachable URL(s) — update data_catalog.yml:\n")
        for f in failures:
            print(f)

    # Always pass — dead URLs are a maintenance note, not a repo error
    assert True
