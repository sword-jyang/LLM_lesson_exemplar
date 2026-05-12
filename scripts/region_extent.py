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

**Programmatic usage** (returns a dict with geometry, bounds, crs, attributes)::

    from scripts.region_extent import resolve_boundary
    result = resolve_boundary("state", "Utah")
    result = resolve_boundary("county", "Larimer", state="Colorado", target_crs="EPSG:32613")
    # result["geometry"]   → Shapely geometry in target_crs
    # result["bounds"]     → (xmin, ymin, xmax, ymax) in target_crs
    # result["crs"]        → target CRS string
    # result["attributes"] → dict with NAME, STUSPS, STATEFP, etc.

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
import tempfile
import zipfile
from pathlib import Path

import fiona
import pyproj
import requests
from shapely.geometry import shape as shapely_shape
from shapely.ops import transform as shapely_transform, unary_union

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


def _find_features(shp_path: Path, match_fn) -> list[dict]:
    """Stream features from a shapefile and return those matching *match_fn*.

    Each returned dict has keys ``"geometry"`` (Shapely) and ``"properties"``.
    Uses fiona for streaming — never loads the whole file into RAM.
    """
    matches = []
    with fiona.open(str(shp_path)) as src:
        for feat in src:
            props = feat["properties"]
            if match_fn(props):
                matches.append({
                    "geometry": shapely_shape(feat["geometry"]),
                    "properties": dict(props),
                })
    return matches


def _resolve_state(shp_path: Path, ident: str) -> dict:
    """Match a state by NAME, STUSPS, or 2-digit FIPS. Return feature dict."""
    raw = ident.strip()
    low = raw.lower()

    def match(props):
        if raw.isdigit():
            return props.get("STATEFP") == raw.zfill(2)
        return (
            (props.get("NAME") or "").lower() == low
            or (props.get("STUSPS") or "").lower() == low
        )

    matches = _find_features(shp_path, match)
    if len(matches) == 0:
        sys.exit(f"No state matched: {ident!r}")
    if len(matches) > 1:
        choices = ", ".join(m["properties"]["NAME"] for m in matches)
        sys.exit(f"Ambiguous state {ident!r}: {choices}")
    return matches[0]


def _reproject_geometry(geom, src_crs: str, dst_crs: str):
    """Reproject a Shapely geometry from src_crs to dst_crs using pyproj."""
    # Use pyproj.CRS objects for proper comparison (WKT vs EPSG string won't
    # match with a plain string ==, e.g. NAD83 WKT != "EPSG:4326").
    src = pyproj.CRS(src_crs)
    dst = pyproj.CRS(dst_crs)
    if src == dst:
        return geom
    transformer = pyproj.Transformer.from_crs(
        src, dst, always_xy=True, allow_ballpark=True,
    )
    result = shapely_transform(transformer.transform, geom)
    # Validate: some PROJ configurations produce inf when datum grids are
    # missing.  Fall back to the original geometry if the CRSes are both
    # geographic (NAD83 ↔ WGS84 differs by < 2 m, safe to skip).
    bounds = result.bounds
    import math
    if any(math.isinf(v) or math.isnan(v) for v in bounds):
        if src.is_geographic and dst.is_geographic:
            print(
                f"Warning: reprojection {src.to_epsg()} → {dst.to_epsg()} "
                f"produced invalid bounds — using original coordinates "
                f"(NAD83/WGS84 offset is < 2 m)",
                file=sys.stderr,
            )
            return geom
        sys.exit(
            f"Reprojection from {src_crs} to {dst_crs} produced invalid bounds. "
            f"Check that PROJ datum grids are installed."
        )
    return result


def _round_bbox(bbox, is_geographic: bool):
    """Round bbox appropriately for the CRS."""
    xmin, ymin, xmax, ymax = bbox
    if is_geographic:
        return round(xmin, 4), round(ymin, 4), round(xmax, 4), round(ymax, 4)
    return round(xmin, 1), round(ymin, 1), round(xmax, 1), round(ymax, 1)


def resolve_boundary(
    kind: str,
    name: str,
    *,
    state: str | None = None,
    target_crs: str = "EPSG:4326",
) -> dict:
    """Return the actual boundary polygon for a US state, county, or place.

    This is the **programmatic API** for use inside Python scripts and the
    harmonizer.

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
    dict
        Keys: ``geometry`` (Shapely geometry in *target_crs*),
        ``bounds`` (xmin, ymin, xmax, ymax), ``crs`` (str),
        ``attributes`` (dict with NAME, STUSPS, STATEFP, etc.).
    """
    kind = kind.lower()
    states_shp = _download_and_extract(STATES_URL, CACHE_DIR / "state")

    # Determine the source CRS from the shapefile
    with fiona.open(str(states_shp)) as src:
        src_crs = src.crs_wkt

    if kind == "state":
        feat = _resolve_state(states_shp, name)
        geom = feat["geometry"]
        attrs = feat["properties"]

    elif kind == "county":
        if state is None:
            sys.exit("county lookup requires a state argument")
        state_feat = _resolve_state(states_shp, state)
        state_fips = state_feat["properties"]["STATEFP"]

        counties_shp = _download_and_extract(COUNTIES_URL, CACHE_DIR / "county")
        low_name = name.lower().strip()
        matches = _find_features(
            counties_shp,
            lambda p: p.get("STATEFP") == state_fips and (p.get("NAME") or "").lower() == low_name,
        )
        if len(matches) == 0:
            # List available counties for helpful error
            all_counties = _find_features(
                counties_shp, lambda p: p.get("STATEFP") == state_fips
            )
            choices = ", ".join(sorted(m["properties"]["NAME"] for m in all_counties))
            sys.exit(f"No county {name!r} in {state_feat['properties']['NAME']}.\nAvailable: {choices}")
        geom = matches[0]["geometry"]
        attrs = matches[0]["properties"]

    elif kind == "place":
        if state is None:
            sys.exit("place lookup requires a state argument")
        state_feat = _resolve_state(states_shp, state)
        state_fips = state_feat["properties"]["STATEFP"]

        places_url = PLACE_URL_TEMPLATE.format(fips=state_fips)
        places_shp = _download_and_extract(places_url, CACHE_DIR / f"place_{state_fips}")
        low_name = name.lower().strip()
        matches = _find_features(
            places_shp,
            lambda p: (p.get("NAME") or "").lower() == low_name,
        )
        if len(matches) == 0:
            sys.exit(
                f"No place {name!r} in {state_feat['properties']['NAME']}. "
                f"Names are matched exactly (case-insensitive) against TIGER's NAME field; "
                f"try a different spelling or a nearby city."
            )
        if len(matches) > 1:
            kinds = [m["properties"].get("NAMELSAD", m["properties"]["NAME"]) for m in matches]
            sys.exit(f"Multiple matches for {name!r} in {state_feat['properties']['NAME']}: {kinds}")
        geom = matches[0]["geometry"]
        attrs = matches[0]["properties"]

    else:
        sys.exit(f"Unknown kind {kind!r} — expected state, county, or place")

    # Reproject geometry to target CRS
    reprojected = _reproject_geometry(geom, src_crs, target_crs)

    # Compute bounds
    is_geographic = pyproj.CRS(target_crs).is_geographic
    bbox = _round_bbox(reprojected.bounds, is_geographic)

    return {
        "geometry": reprojected,
        "bounds": bbox,
        "crs": target_crs,
        "attributes": attrs,
    }


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


def _write_boundary(result: dict, boundary_path: str) -> None:
    """Write the boundary geometry to a GeoJSON file using ogr-free JSON."""
    import json
    from shapely.geometry import mapping
    fc = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "geometry": mapping(result["geometry"]),
            "properties": result["attributes"],
        }],
    }
    Path(boundary_path).parent.mkdir(parents=True, exist_ok=True)
    with open(boundary_path, "w") as f:
        json.dump(fc, f)
    print(f"Boundary written to {boundary_path}", file=sys.stderr)


def cmd_state(name: str, target_crs: str, boundary_path: str | None = None) -> int:
    result = resolve_boundary("state", name, target_crs=target_crs)
    attrs = result["attributes"]
    full, stusps, fips = attrs["NAME"], attrs["STUSPS"], attrs["STATEFP"]
    if boundary_path:
        _write_boundary(result, boundary_path)
    _emit(f"{full} ({stusps}, FIPS {fips})", result["bounds"], target_crs, boundary_path)
    return 0


def cmd_county(county_name: str, state_ident: str, target_crs: str, boundary_path: str | None = None) -> int:
    result = resolve_boundary("county", county_name, state=state_ident, target_crs=target_crs)
    # Get state full name
    states_shp = _download_and_extract(STATES_URL, CACHE_DIR / "state")
    state_feat = _resolve_state(states_shp, state_ident)
    state_full = state_feat["properties"]["NAME"]
    if boundary_path:
        _write_boundary(result, boundary_path)
    _emit(f"{result['attributes']['NAME']} County, {state_full}", result["bounds"], target_crs, boundary_path)
    return 0


def cmd_place(place_name: str, state_ident: str, target_crs: str, boundary_path: str | None = None) -> int:
    result = resolve_boundary("place", place_name, state=state_ident, target_crs=target_crs)
    states_shp = _download_and_extract(STATES_URL, CACHE_DIR / "state")
    state_feat = _resolve_state(states_shp, state_ident)
    state_full = state_feat["properties"]["NAME"]
    if boundary_path:
        _write_boundary(result, boundary_path)
    label = result["attributes"].get("NAMELSAD", result["attributes"]["NAME"])
    _emit(f"{label}, {state_full}", result["bounds"], target_crs, boundary_path)
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
