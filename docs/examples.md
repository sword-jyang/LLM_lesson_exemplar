# Examples

This page contains examples for using the geospatial harmonization tools in this repository.

---

## Geospatial Data Harmonization

The `geospatial_harmonizer` module helps harmonize multiple geospatial datasets by projecting them to a common CRS, clipping to a common extent, and creating visualizations.

### Running the Colorado Example

The main example harmonizes four datasets for Colorado fire risk analysis:

```bash
python examples/colorado_fire_risk/colorado_harmonization.py
```

This downloads and processes:

- **FBFM40 Fire Behavior Fuel Models** (raster) — Landfire 2024 Scott and Burgan 40-class model
- **MACAv2 Winter Precipitation** (raster) — CCSM4 RCP8.5 Dec–Mar mean 2006–2099, streamed via OPeNDAP
- **MTBS Burned Area Boundaries** (vector) — USGS fire perimeter data, kept as vector
- **Microsoft Building Footprints** (vector, rasterized) — Colorado buildings rasterized to presence/absence at ~270 m

Output is saved to `examples/colorado_fire_risk/output/`.

### Programmatic Usage

Import the harmonization functions and run a custom workflow:

```python
from pathlib import Path
from src.geospatial_harmonizer import (
    DatasetSpec,
    ExampleWorkflow,
    run_harmonization_example,
)

# Define your target grid
TARGET_CRS = "EPSG:4326"
TARGET_EXTENT = (-109.05, 36.99, -102.04, 41.01)  # Colorado bounding box
TARGET_RESOLUTION = 0.00243  # ~270m in degrees
OUTPUT_DIR = Path("./my_harmonized_output")

# Define datasets to harmonize
DATASETS = [
    DatasetSpec(
        name="my_raster",
        url="https://example.com/data.tif",
        data_type="raster",
    ),
    DatasetSpec(
        name="my_vector",
        url="https://example.com/data.zip",
        data_type="vector",
        rasterize=True,
        burn_value=1,
    ),
]

# Run the workflow
workflow = ExampleWorkflow(
    name="my_workflow",
    datasets=DATASETS,
    target_crs=TARGET_CRS,
    target_extent=TARGET_EXTENT,
    target_resolution=TARGET_RESOLUTION,
    output_dir=OUTPUT_DIR,
    create_visualization=True,
    verbose=True,
)

output_files, interactive_map = run_harmonization_example(workflow)
```

### Supported Data Types

- **Raster**: GeoTIFF, COG, IMG (downloaded and harmonized)
- **NetCDF / OPeNDAP**: Climate model outputs (MACAv2, ERA5 subsets) — set `netcdf_variable` and use a THREDDS `dodsC` URL to subset spatially before download
- **Vector**: GeoJSON, Shapefile (optionally rasterized to match the raster grid)
- **Archives**: ZIP files (automatically extracted)
- **STAC**: Cloud-native collections (set `is_stac=True`)

### Output Structure

After running, the output directory contains:

```
output/
└── colorado_harmonized_output/
    ├── harmonized_fbfm40_fuel_models.tif
    ├── harmonized_pr_winter_rcp85_ccsm4.tif
    ├── harmonized_mtbs_burned_areas.geojson
    ├── harmonized_building_footprints.tif
    ├── harmonized_visualization.png
    └── harmonized_visualization.html
```

All harmonized rasters share:

- Common CRS (EPSG:4326)
- Common extent (Colorado bounding box)
- Common resolution (~270 m / 0.00243°)

---

## Core Functions

### `DatasetSpec`

Dataclass describing a single dataset to harmonize. Key fields:

| Field | Description |
|---|---|
| `name` | Short identifier used in output filenames |
| `url` | Direct download URL, OPeNDAP endpoint, or STAC API root |
| `data_type` | `"raster"` or `"vector"` |
| `rasterize` | Rasterize vector to match the target grid |
| `burn_value` | Value to burn when rasterizing (default `1`) |
| `resampling_method` | `"nearest"` (categorical), `"bilinear"` (continuous), or `"cubic"`; auto-detected from dtype if not set |
| `labels_url` | URL to a CSV with `VALUE,LABEL` columns for legend labels (e.g. FBFM40 fuel model names) |
| `netcdf_variable` | Variable name inside a NetCDF file (e.g. `"pr"`, `"tasmax"`) |
| `netcdf_months` | Months to average over, e.g. `[12, 1, 2, 3]` for Dec–Mar winter mean |
| `secondary_url` | Second OPeNDAP URL for derived variables (e.g. rhsmin for VPD) |
| `secondary_netcdf_variable` | Variable name in the secondary NetCDF |
| `is_wcs` | Download from a WCS endpoint; set `wcs_layer` to the coverage name |
| `is_wms` | Download from a WMS endpoint; set `wms_layer` to the layer name |
| `is_stac` | Search a STAC catalog instead of downloading directly |
| `stac_collection` | STAC collection ID, e.g. `"sentinel-2-l2a"` |
| `stac_asset` | Asset key to download, e.g. `"B08"`, `"visual"` |
| `stac_datetime` | ISO-8601 date or range, e.g. `"2023-06-01/2023-08-31"` |
| `stac_query` | Extra STAC filter properties, e.g. `{"eo:cloud_cover": {"lt": 20}}` |

### `build_grid_spec(target_crs, target_extent, target_resolution)`

Creates a `GridSpec` defining the target coordinate system and resolution.

### `download_file(url, output_dir, verbose)`

Downloads a file from a URL to the specified directory.

### `harmonize_raster(input_path, grid, output_path, verbose)`

Reprojects and resamples a raster to match the target grid.

### `rasterize_vector_to_grid(input_path, grid, output_path, burn_value, verbose)`

Rasterizes vector geometries onto the target grid.

### `create_visualization(outputs, output_dir, verbose)`

Creates a multi-panel matplotlib visualization of harmonized outputs. Saves to
`<output_dir>/harmonized_visualization.png` — the filename is hardcoded so the
website build hook can find it.

### `create_interactive_visualization(outputs, target_extent, output_dir=None, verbose=True)`

Creates a Folium HTML map with per-layer toggle checkboxes and opacity sliders.
If `output_dir` is given, saves to `<output_dir>/harmonized_visualization.html`
(filename hardcoded). If `output_dir` is None, returns the map without saving
(useful for inline display in Jupyter).

### `run_harmonization_example(workflow)`

Main entry point that orchestrates the complete harmonization workflow.
