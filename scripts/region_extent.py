#!/usr/bin/env python3
"""Look up the bounding box **or actual boundary geometry** of a US state,
county, or place in any target CRS.

Use this instead of guessing or relying on model knowledge for region extents.
Bounds come from authoritative Census TIGER 2025 data.

**CLI usage** (returns a ready-to-paste ``target_extent`` tuple)::

    python scripts/region_extent.py state <name> [--crs <EPSG:NNNN>]
    python scripts/region_extent.py county <name> <state> [--crs <EPSG:NNNN>]
    python scripts/region_extent.py place <name> <state> [--crs <EPSG:NNNN>]

Add ``--boundary <output.geojson>`` to write the actual polygon boundary to
a GeoJSON file (for use with ``ExampleWorkflow(clip_boundary=...)``).

**Programmatic usage** (returns a GeoDataFrame with the boundary polygon)::

    from scripts.region_extent import resolve_boundary
    gdf = resolve_boundary("state", "Utah")
    gdf = resolve_boundary("county", "Larimer", state="Colorado", target_crs="EPSG:32613")

Examples:
    python scripts/region_extent.py state Colorado
    python scripts/region_extent.py state "New York"
    python scripts/region_extent.py county Larimer Colorado
    python scripts/region_extent.py place Boulder CO
    python scripts/region_extent.py state Colorado --crs EPSG:32613
    python scripts/region_extent.py state Utah --boundary utah_boundary.geojson

State identifiers can be the full name ("Colorado"), the 2-letter postal
code ("CO"), or the 2-digit FIPS code ("08"). County and place names are
matched case-insensitively against the TIGER NAME field within the given
state. The ``--crs`` value can be any CRS pyproj resolves (EPSG code, WKT,
proj string) and must match whatever you plan to set ``target_crs=`` to in
the workflow — ``target_extent`` and ``target_crs`` must agree.

For regions not covered by this helper (custom AOIs, ecoregions, watersheds,
study sites, neighborhoods, named features outside TIGER), ask the user for
a bounding-box in EPSG:4326 **or a boundary vector file** to clip to. Do not
guess.
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


def resolve_boundary(
    kind: str,
    name: str,
    *,
    state: str | None = None,
    target_crs: str = "EPSG:4326",
) -> gpd.GeoDataFrame:
    """Return the actual boundary polygon for a US state, county, or place.

    This is the **programmatic API** for use inside Python scripts and the
    harmonizer.  The returned GeoDataFrame is in *target_crs* and contains the
    full polygon geometry (not just a bounding box).

    Parameters
    ----------
    kind : str
        One of ``"state"``, ``"county"``, or ``"place"``.
    name : str
        Feature name (e.g. ``"Utah"``, ``"Larimer"``, ``"Boulder"``).
    state : str, optional
        Required for ``"county"`` and ``"place"`` — the state the feature is in.
    target_crs : str
        CRS to reproject the boundary into (default ``"EPSG:4326"``).

    Returns
    -------
    gpd.GeoDataFrame
        Single-row GeoDataFrame with the boundary polygon in *target_crs*.

    Raises
    ------
    SystemExit
        If the feature cannot be found.
    """
    kind = kind.lower()
    states_gdf = gpd.read_file(_download_and_extract(STATES_URL, CACHE_DIR / "state"))

    if kind == "state":
        _full, _stusps, fips = _resolve_state(states_gdf, name)
        gdf = states_gdf[states_gdf["STATEFP"] == fips].copy()
    elif kind == "county":
        if state is None:
            sys.exit("county lookup requires a state argument")
        _full, _, fips = _resolve_state(states_gdf, state)
        counties = gpd.read_file(_download_and_extract(COUNTIES_URL, CACHE_DIR / "county"))
        sub = counties[counties["STATEFP"] == fips]
        gdf = sub[sub["NAME"].str.lower() == name.lower().strip()].copy()
        if len(gdf) == 0:
            choices = ", ".join(sorted(sub["NAME"].tolist()))
            sys.exit(f"No county {name!r} in {_full}.\nAvailable: {choices}")
    elif kind == "place":
        if state is None:
            sys.exit("place lookup requires a state argument")
        _full, _, fips = _resolve_state(states_gdf, state)
        places_url = PLACE_URL_TEMPLATE.format(fips=fips)
        places = gpd.read_file(_download_and_extract(places_url, CACHE_DIR / f"place_{fips}"))
        gdf = places[places["NAME"].str.lower() == name.lower().strip()].copy()
        if len(gdf) == 0:
            sys.exit(
                f"No place {name!r} in {_full}. "
                f"Names are matched exactly (case-insensitive) against TIGER's NAME field; "
                f"try a different spelling or a nearby city."
            )
        if len(gdf) > 1:
            kinds = gdf["NAMELSAD"].tolist()
            sys.exit(f"Multiple matches for {name!r} in {_full}: {kinds}")
    else:
        sys.exit(f"Unknown kind {kind!r} — expected state, county, or place")

    return gdf.to_crs(target_crs)


def _emit(
    label: str,
    bbox: tuple[float, float, float, float],
    target_crs: str,
    boundary_path: str | None = None,
) -> None:
    xmin, ymin, xmax, ymax = bbox
    print(f"{label}")
    print(f"{target_crs} bounds: ({xmin}, {ymin}, {xmax}, {ymax})")
    print()
    print("Copy-paste for ExampleWorkflow:")
    print(f'  target_crs="{target_crs}",')
    print(f"  target_extent=({xmin}, {ymin}, {xmax}, {ymax}),  # {label}")
    if boundary_path:
        print(f'  clip_boundary="{boundary_path}",  # actual boundary polygon')


def cmd_state(name: str, target_crs: str, boundary_path: str | None = None) -> int:
    gdf = resolve_boundary("state", name, target_crs=target_crs)
    row = gdf.iloc[0]
    full, stusps, fips = row["NAME"], row["STUSPS"], row["STATEFP"]
    bbox = _bbox_in_crs(gdf, target_crs)
    if boundary_path:
        gdf.to_file(boundary_path, driver="GeoJSON")
        print(f"Boundary written to {boundary_path}", file=sys.stderr)
    _emit(f"{full} ({stusps}, FIPS {fips})", bbox, target_crs, boundary_path)
    return 0


def cmd_county(county_name: str, state_ident: str, target_crs: str, boundary_path: str | None = None) -> int:
    gdf = resolve_boundary("county", county_name, state=state_ident, target_crs=target_crs)
    states_gdf = gpd.read_file(_download_and_extract(STATES_URL, CACHE_DIR / "state"))
    state_full, _, _ = _resolve_state(states_gdf, state_ident)
    bbox = _bbox_in_crs(gdf, target_crs)
    if boundary_path:
        gdf.to_file(boundary_path, driver="GeoJSON")
        print(f"Boundary written to {boundary_path}", file=sys.stderr)
    _emit(f"{gdf.iloc[0]['NAME']} County, {state_full}", bbox, target_crs, boundary_path)
    return 0


def cmd_place(place_name: str, state_ident: str, target_crs: str, boundary_path: str | None = None) -> int:
    gdf = resolve_boundary("place", place_name, state=state_ident, target_crs=target_crs)
    states_gdf = gpd.read_file(_download_and_extract(STATES_URL, CACHE_DIR / "state"))
    state_full, _, _ = _resolve_state(states_gdf, state_ident)
    bbox = _bbox_in_crs(gdf, target_crs)
    if boundary_path:
        gdf.to_file(boundary_path, driver="GeoJSON")
        print(f"Boundary written to {boundary_path}", file=sys.stderr)
    _emit(f"{gdf.iloc[0]['NAMELSAD']}, {state_full}", bbox, target_crs, boundary_path)
    return 0


def _extract_flags(argv: list[str]) -> tuple[list[str], str, str | None]:
    """Pull ``--crs`` and ``--boundary`` flags out of argv.

    Returns (remaining_args, target_crs, boundary_path).
    """
    target_crs = "EPSG:4326"
    boundary_path: str | None = None
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
        if a == "--boundary" and i + 1 < len(argv):
            boundary_path = argv[i + 1]
            i += 2
            continue
        if a.startswith("--boundary="):
            boundary_path = a.split("=", 1)[1]
            i += 1
            continue
        rest.append(a)
        i += 1
    return rest, target_crs, boundary_path


def main(argv: list[str]) -> int:
    argv, target_crs, boundary_path = _extract_flags(argv)
    if len(argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2
    kind = argv[0].lower()
    if kind == "state" and len(argv) == 2:
        return cmd_state(argv[1], target_crs, boundary_path)
    if kind == "county" and len(argv) == 3:
        return cmd_county(argv[1], argv[2], target_crs, boundary_path)
    if kind == "place" and len(argv) == 3:
        return cmd_place(argv[1], argv[2], target_crs, boundary_path)
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
