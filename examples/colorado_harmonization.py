#!/usr/bin/env python3
"""
Colorado fire risk harmonization example.

This example demonstrates how to harmonize multiple geospatial datasets
for Colorado using shared functions from src/geospatial_harmonizer.py.

Datasets:
1. FBFM40 Fire Behavior Fuel Models (raster) - Landfire 2024
2. MTBS Burned Area Boundaries (vector, rasterized)
3. Microsoft Building Footprints (vector, rasterized)
4. MACAv2 VPD (raster) - Projected mean summer VPD 2006-2099 (CCSM4, RCP8.5)
   Derived from tasmax + rhsmin via OPeNDAP; resampled from ~4 km to match fuel model grid.

All outputs are harmonized to:
- CRS: EPSG:4326
- Extent: Colorado
- Resolution: ~270 m (in degrees, approximated for Colorado)
"""

from pathlib import Path
from src.geospatial_harmonizer import (
    DatasetSpec,
    ExampleWorkflow,
    run_harmonization_example,
)

# Colorado bounding box in EPSG:4326
COLORADO_EXTENT = (-109.05, 36.99, -102.04, 41.01)

# Common output settings
TARGET_CRS = "EPSG:4326"

# Approximate degree resolution for ~270 m at Colorado latitude
TARGET_RESOLUTION = 0.00243

OUTPUT_DIR = Path("./output/colorado_harmonized_output")

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
        url="https://www.landfire.gov/data-downloads/CONUS_LF2024/LF2024_FBFM40_CONUS.zip",
        data_type="raster",
        resampling_method="nearest",
        labels_url="https://landfire.gov/sites/default/files/CSV/2024/LF2024_FBFM40.csv",
    ),
    # MACAv2 projected VPD (kPa): JJA mean across 2006-2099, CCSM4 RCP8.5.
    # Derived from tasmax (K) + rhsmin (%) via the Buck equation.
    # Native resolution is ~4 km; harmonize_raster resamples to the ~270 m fuel model grid.
    # MACAv2 projected winter precipitation (kg m-2 day-1): Dec–Mar mean across
    # 2006-2099, CCSM4 RCP8.5. Downloaded as a single variable via OPeNDAP,
    # subsetted to Colorado before transfer. Native resolution is ~4 km;
    # harmonize_raster resamples to the ~270 m fuel model grid using bilinear
    # interpolation (continuous data).
    DatasetSpec(
        name="pr_winter_rcp85_ccsm4",
        url=f"{_THREDDS}/agg_macav2metdata_pr_CCSM4_r6i1p1_rcp85_2006_2099_CONUS_monthly.nc",
        data_type="raster",
        netcdf_variable="precipitation",
        netcdf_months=[12, 1, 2, 3],
    ),
    DatasetSpec(
        name="mtbs_burned_areas",
        url="https://edcintl.cr.usgs.gov/downloads/sciweb1/shared/MTBS_Fire/data/composite_data/burned_area_extent_shapefile/mtbs_perimeter_data.zip",
        data_type="vector",
        rasterize=False,
    ),
    # Rasterized to presence/absence at ~270 m — individual building polygons are
    # not visible at state scale and the raw vector is too large to embed in HTML.
    DatasetSpec(
        name="building_footprints",
        url="https://minedbuildings.z5.web.core.windows.net/legacy/usbuildings-v2/Colorado.geojson.zip",
        data_type="vector",
        rasterize=True,
    ),
]

def main() -> int:
    workflow = ExampleWorkflow(
        name="colorado_fire_risk",
        datasets=DATASETS,
        target_crs=TARGET_CRS,
        target_extent=COLORADO_EXTENT,
        target_resolution=TARGET_RESOLUTION,
        output_dir=OUTPUT_DIR,
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