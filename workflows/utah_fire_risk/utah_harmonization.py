#!/usr/bin/env python3
"""
Utah fire risk harmonization example.

This example demonstrates how to harmonize multiple geospatial datasets
for Utah using shared functions from src/geospatial_harmonizer.py.

Datasets:
1. FBFM40 Fire Behavior Fuel Models (raster) — Landfire 2024 Scott and Burgan 40-class model
2. MACAv2 Winter Precipitation (raster) — CCSM4 RCP8.5 Dec–Mar mean, 2006–2099
   Downloaded via OPeNDAP from the Northwest Knowledge Network THREDDS server.
   Subsetted to Utah before transfer; resampled from ~4 km to ~270 m using bilinear interpolation.
3. MTBS Burned Area Boundaries (vector) — USGS perimeter data, kept as vector
4. Microsoft Building Footprints (vector, rasterized to presence/absence at ~270 m)

All outputs are harmonized to:
- CRS: EPSG:5070 (CONUS Albers Equal Area)
- Extent: Utah
- Resolution: 270 m
"""

import sys
from pathlib import Path

# Walk up to find the repo root (dir containing src/geospatial_harmonizer.py).
# Depth-agnostic — works regardless of how nested this script is.
_repo_root = next(p for p in Path(__file__).resolve().parents
                  if (p / "src" / "geospatial_harmonizer.py").exists())
sys.path.insert(0, str(_repo_root))

from src.geospatial_harmonizer import (
    DatasetSpec,
    ExampleWorkflow,
    run_harmonization_example,
)

# Utah bounding box in EPSG:5070 (CONUS Albers Equal Area)
# From region_extent.py state Utah --crs EPSG:5070
UTAH_EXTENT = (-1581748.3, 1629453.6, -1085516.0, 2250700.3)

# Common output settings
TARGET_CRS = "EPSG:5070"

# Resolution in meters (EPSG:5070 is a projected CRS)
TARGET_RESOLUTION = 270

# Output goes into this project's own folder, regardless of where the script is run from
OUTPUT_DIR = Path(__file__).parent / "output"

# MACAv2 CMIP5 OPeNDAP base URL (Northwest Knowledge Network THREDDS server)
_THREDDS = "http://thredds.northwestknowledge.net:8080/thredds/dodsC"

# Example datasets
# Using Landfire FBFM40 (Scott and Burgan Fire Behavior Fuel Models) - CONUS 2024
# Note: WMS returns rendered images (not raw data), so we use direct download
# The harmonizer now caches results, so subsequent runs are fast
DATASETS = [
    # Categorical raster — must use nearest-neighbour resampling to avoid
    # interpolating between integer class codes (e.g. fuel model 91 ≠ 92).
    DatasetSpec(
        name="fbfm40_fuel_models",
        display_name="Vegetation and Fuel Types",
        description="What can burn",
        url="https://www.landfire.gov/data-downloads/CONUS_LF2024/LF2024_FBFM40_CONUS.zip",
        data_type="raster",
        resampling_method="nearest",
        labels_url="https://landfire.gov/sites/default/files/CSV/2024/LF2024_FBFM40.csv",
    ),
    # MACAv2 projected winter precipitation (kg m-2 day-1): Dec–Mar mean across
    # 2006-2099, CCSM4 RCP8.5. Downloaded as a single variable via OPeNDAP,
    # subsetted to Utah before transfer. Native resolution is ~4 km;
    # harmonize_raster resamples to the 270 m fuel model grid using bilinear
    # interpolation (continuous data). Ensemble member r6i1p1 is CCSM4-specific.
    DatasetSpec(
        name="pr_winter_rcp85_ccsm4",
        display_name="Winter Precipitation",
        description="Climate moisture conditions (RCP 8.5 projection)",
        url=f"{_THREDDS}/agg_macav2metdata_pr_CCSM4_r6i1p1_rcp85_2006_2099_CONUS_monthly.nc",
        data_type="raster",
        netcdf_variable="precipitation",
        netcdf_months=[12, 1, 2, 3],
    ),
    DatasetSpec(
        name="mtbs_burned_areas",
        display_name="Recent Fire Activity",
        description="Where fires have occurred (1984\u2013present)",
        url="https://edcintl.cr.usgs.gov/downloads/sciweb1/shared/MTBS_Fire/data/composite_data/burned_area_extent_shapefile/mtbs_perimeter_data.zip",
        data_type="vector",
        rasterize=False,
    ),
    # Rasterized to presence/absence at 270 m — individual building polygons are
    # not visible at state scale and the raw vector is too large to embed in HTML.
    DatasetSpec(
        name="building_footprints",
        display_name="Building Density",
        description="Where people are located",
        url="https://minedbuildings.z5.web.core.windows.net/legacy/usbuildings-v2/Utah.geojson.zip",
        data_type="vector",
        rasterize=True,
    ),
]

def main() -> int:
    workflow = ExampleWorkflow(
        name="utah_fire_risk",
        datasets=DATASETS,
        target_crs=TARGET_CRS,
        target_extent=UTAH_EXTENT,
        target_resolution=TARGET_RESOLUTION,
        output_dir=OUTPUT_DIR,
        clip_boundary="state:Utah",  # Clip to actual state polygon, not just bbox
        create_visualization=True,
        verbose=True,
    )

    output_files, interactive_map = run_harmonization_example(workflow)

    print("\nHarmonization complete.")
    print(f"\nOutputs saved to: {OUTPUT_DIR.resolve()}")

    print("\nGenerated files:")
    for path in output_files:
        print(f" - {path.name}")

    viz_path = OUTPUT_DIR / "harmonized_visualization.png"
    composite_path = OUTPUT_DIR / "harmonized_visualization_composite.png"

    print("\nGenerated visualizations:")
    if viz_path.exists():
        print(f" - Per-layer PNG: {viz_path.name}")
    if composite_path.exists():
        print(f" - Composite PNG: {composite_path.name}")
    if interactive_map is not None:
        print(" - Interactive map available (display with `interactive_map` in a notebook)")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
