#!/usr/bin/env python3
"""Look up the bounding box of a US state, county, or place in any target CRS.

Use this instead of guessing or relying on model knowledge for region extents.
Bounds come from authoritative Census TIGER 2025 data and are returned as a
(xmin, ymin, xmax, ymax) tuple ready to paste into `target_extent=` on
`ExampleWorkflow`. Output is in EPSG:4326 by default; pass `--crs` to get
bounds in any other CRS (the polygon is reprojected before bounds are taken,
so the result tightly envelops the feature in the target CRS).

Usage:
    python scripts/region_extent.py state <name> [--crs <EPSG:NNNN>]
    python scripts/region_extent.py county <name> <state> [--crs <EPSG:NNNN>]
    python scripts/region_extent.py place <name> <state> [--crs <EPSG:NNNN>]

Examples:
    python scripts/region_extent.py state Colorado
    python scripts/region_extent.py state "New York"
    python scripts/region_extent.py county Larimer Colorado
    python scripts/region_extent.py place Boulder CO
    python scripts/region_extent.py state Colorado --crs <target_crs>

State identifiers can be the full name ("Colorado"), the 2-letter postal
code ("CO"), or the 2-digit FIPS code ("08"). County and place names are
matched case-insensitively against the TIGER NAME field within the given
state. The `--crs` value can be any CRS pyproj resolves (EPSG code, WKT,
proj string) and must match whatever you plan to set `target_crs=` to in
the workflow — `target_extent` and `target_crs` must agree.

For regions not covered by this helper (custom AOIs, ecoregions, watersheds,
study sites, neighborhoods, named features outside TIGER), ask the user for
a bbox in EPSG:4326 or for a vector file to derive bounds from. Do not guess.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import geopandas as gpd
import requests

CACHE_DIR = Path.home() / ".cache" / "llm_lesson_exemplar" / "region_extent"

STATES_URL = "https://www2.census.gov/geo/tiger/TIGER2025/STATE/tl_2025_us_state.zip"
COUNTIES_URL = "https://www2.census.gov/geo/tiger/TIGER2025/COUNTY/tl_2025_us_county.zip"
PLACE_URL_TEMPLATE = "https://www2.census.gov/geo/tiger/TIGER2025/PLACE/tl_2025_{fips}_place.zip"


def _download_and_extract(url: str, dest_dir: Path) -> Path:
    """Download and unzip a TIGER archive into dest_dir; return the .shp path.

    Idempotent: re-runs are no-ops if the .shp already exists. Downloads to a
    .part file and renames atomically so a Ctrl-C mid-download cannot leave a
    truncated zip masquerading as cache.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    zip_path = dest_dir / Path(url).name
    extracted = dest_dir / zip_path.stem
    shp = next(extracted.glob("*.shp"), None) if extracted.exists() else None
    if shp is not None:
        return shp

    if not zip_path.exists():
        print(f"Downloading {url} ...", file=sys.stderr)
        tmp_path = zip_path.with_suffix(zip_path.suffix + ".part")
        with requests.get(url, stream=True, timeout=120) as r:
            r.raise_for_status()
            with open(tmp_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1 << 14):
                    f.write(chunk)
        tmp_path.rename(zip_path)

    extracted.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(extracted)
    shp = next(extracted.glob("*.shp"), None)
    if shp is None:
        sys.exit(f"No .shp found in {extracted}")
    return shp


def _resolve_state(states: gpd.GeoDataFrame, ident: str) -> tuple[str, str, str]:
    """Match a state by NAME, STUSPS, or 2-digit FIPS. Return (name, stusps, fips)."""
    raw = ident.strip()
    if raw.isdigit():
        match = states[states["STATEFP"] == raw.zfill(2)]
    else:
        low = raw.lower()
        match = states[
            (states["NAME"].str.lower() == low) | (states["STUSPS"].str.lower() == low)
        ]
    if len(match) == 0:
        sys.exit(f"No state matched: {ident!r}")
    if len(match) > 1:
        choices = ", ".join(match["NAME"].tolist())
        sys.exit(f"Ambiguous state {ident!r}: {choices}")
    row = match.iloc[0]
    return row["NAME"], row["STUSPS"], row["STATEFP"]


def _bbox_in_crs(gdf: gpd.GeoDataFrame, target_crs: str) -> tuple[float, float, float, float]:
    """Reproject the polygon(s) to target_crs, then take total_bounds.

    Reprojecting the polygon (rather than reprojecting four bbox corners) is
    important: a feature's bbox in EPSG:4326 reprojected corner-by-corner can
    miss curvature and yield a too-tight envelope in projected CRSs.
    """
    xmin, ymin, xmax, ymax = gdf.to_crs(target_crs).total_bounds
    # Geographic CRSs are in degrees → 4 decimals (~11 m); projected CRSs are
    # typically in meters → integer precision is sufficient for cropping.
    if gpd.GeoSeries([], crs=target_crs).crs.is_geographic:
        return round(xmin, 4), round(ymin, 4), round(xmax, 4), round(ymax, 4)
    return round(xmin, 1), round(ymin, 1), round(xmax, 1), round(ymax, 1)


def _emit(label: str, bbox: tuple[float, float, float, float], target_crs: str) -> None:
    xmin, ymin, xmax, ymax = bbox
    print(f"{label}")
    print(f"{target_crs} bounds: ({xmin}, {ymin}, {xmax}, {ymax})")
    print()
    print("Copy-paste for ExampleWorkflow:")
    print(f'  target_crs="{target_crs}",')
    print(f"  target_extent=({xmin}, {ymin}, {xmax}, {ymax}),  # {label}")


def cmd_state(name: str, target_crs: str) -> int:
    states = gpd.read_file(_download_and_extract(STATES_URL, CACHE_DIR / "state"))
    full, stusps, fips = _resolve_state(states, name)
    bbox = _bbox_in_crs(states[states["STATEFP"] == fips], target_crs)
    _emit(f"{full} ({stusps}, FIPS {fips})", bbox, target_crs)
    return 0


def cmd_county(county_name: str, state_ident: str, target_crs: str) -> int:
    states = gpd.read_file(_download_and_extract(STATES_URL, CACHE_DIR / "state"))
    state_full, _, fips = _resolve_state(states, state_ident)
    counties = gpd.read_file(_download_and_extract(COUNTIES_URL, CACHE_DIR / "county"))
    sub = counties[counties["STATEFP"] == fips]
    matches = sub[sub["NAME"].str.lower() == county_name.lower().strip()]
    if len(matches) == 0:
        choices = ", ".join(sorted(sub["NAME"].tolist()))
        sys.exit(f"No county {county_name!r} in {state_full}.\nAvailable: {choices}")
    if len(matches) > 1:
        sys.exit(f"Multiple counties matched {county_name!r} in {state_full}")
    bbox = _bbox_in_crs(matches, target_crs)
    _emit(f"{matches.iloc[0]['NAME']} County, {state_full}", bbox, target_crs)
    return 0


def cmd_place(place_name: str, state_ident: str, target_crs: str) -> int:
    states = gpd.read_file(_download_and_extract(STATES_URL, CACHE_DIR / "state"))
    state_full, _, fips = _resolve_state(states, state_ident)
    places_url = PLACE_URL_TEMPLATE.format(fips=fips)
    places = gpd.read_file(_download_and_extract(places_url, CACHE_DIR / f"place_{fips}"))
    matches = places[places["NAME"].str.lower() == place_name.lower().strip()]
    if len(matches) == 0:
        sys.exit(
            f"No place {place_name!r} in {state_full}. "
            f"Names are matched exactly (case-insensitive) against TIGER's NAME field; "
            f"try a different spelling or a nearby city."
        )
    if len(matches) > 1:
        kinds = matches["NAMELSAD"].tolist()
        sys.exit(f"Multiple matches for {place_name!r} in {state_full}: {kinds}")
    bbox = _bbox_in_crs(matches, target_crs)
    _emit(f"{matches.iloc[0]['NAMELSAD']}, {state_full}", bbox, target_crs)
    return 0


def _extract_crs_flag(argv: list[str]) -> tuple[list[str], str]:
    """Pull `--crs <value>` (or `--crs=<value>`) out of argv. Default EPSG:4326."""
    target_crs = "EPSG:4326"
    rest: list[str] = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--crs" and i + 1 < len(argv):
            target_crs = argv[i + 1]
            i += 2
            continue
        if a.startswith("--crs="):
            target_crs = a.split("=", 1)[1]
            i += 1
            continue
        rest.append(a)
        i += 1
    return rest, target_crs


def main(argv: list[str]) -> int:
    argv, target_crs = _extract_crs_flag(argv)
    if len(argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2
    kind = argv[0].lower()
    if kind == "state" and len(argv) == 2:
        return cmd_state(argv[1], target_crs)
    if kind == "county" and len(argv) == 3:
        return cmd_county(argv[1], argv[2], target_crs)
    if kind == "place" and len(argv) == 3:
        return cmd_place(argv[1], argv[2], target_crs)
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
