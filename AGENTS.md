# AGENTS.md

## Core Operating Contract

- Treat this repository as the source of truth.
- Treat the website as a rendered view of repository state.
- Prefer small, additive, traceable edits.
- Keep documentation synchronized with code and project structure.
- Keep the repository minimalist by default.

---

## Default Workflow

- Inspect repository structure before editing.
- Make the smallest diff that solves the request.
- Update related docs when behavior, workflows, or outputs change.
- Update changelog, dev log, or equivalent history files for meaningful changes.
- Preserve existing structure and historical context.
- Do not perform destructive rewrites unless explicitly requested.

---

## Documentation and Website Policy

- Treat `docs/` as project-level documentation and website source.
- Update docs whenever code, workflows, or outputs change.
- Amend existing docs when possible; do not replace whole files without need.
- Preserve navigation, readability, and consistency in website changes.
- Keep default website behavior clean and minimal unless the user asks for more expressive design.

---

## Testing Policy

- Assume `tests/` may exist before a full testing framework is defined.
- Do not invent domain-specific tests when expected behavior is unclear.
- Add the smallest meaningful tests when behavior is known.
- Prefer early-stage checks such as smoke tests, import tests, CLI tests, schema checks, or example-based checks.
- If tests are deferred, document the gap; do not imply coverage that does not exist.

---

## Package and Structure Separation Policy

- Keep website structure and package structure clearly separated.
- Do not automatically repurpose `docs/` for package-native docs or build artifacts.
- For Python packaging requests, prefer standard Python layout, typically `src/`.
- For R packaging requests, follow standard R conventions (`R/`, `man/`, `DESCRIPTION`, `NAMESPACE`, optional `vignettes/`).
- For other ecosystems, follow ecosystem conventions.
- If structural conflicts arise, choose a durable long-term structure and document the decision.

---

## Data Discovery and Data Use Policy

- Prefer open and FAIR data when possible.
- Prefer streaming or lazy-access workflows over bulk downloads when feasible.
- Use standards-based discovery systems (for example STAC) when relevant.
- When relevant, consider streaming-friendly tooling such as xarray, zarr, GDAL, rasterio, pystac-client, stackstac, gdalcubes, terra, stars, cubo, or equivalent tools.
- When introducing data, document source, access method, format, license, and citation requirements.
- Do not silently ingest external data into the project.

---

## Data Acquisition and Preparation Policy

The agent MUST support workflows where users provide datasets via URLs (e.g., zipped archives, cloud-hosted files, or geodatabases).

### Supported Input Types

| Format | Extension(s) | Handler | Notes |
|---|---|---|---|
| GeoTIFF / COG | `.tif`, `.tiff` | rasterio | Primary raster format |
| ERDAS Imagine | `.img` | rasterio | Discovered automatically |
| GeoJSON | `.geojson`, `.json` | geopandas | Primary vector format |
| Shapefile | `.shp` | geopandas | Auto-discovered inside ZIP |
| GeoPackage | `.gpkg` | geopandas | |
| NetCDF | `.nc` | xarray + rasterio | Requires `netcdf_variable` — see below |
| Zarr | `.zarr` | xarray | Cloud-native array store |
| STAC catalog | (URL) | pystac-client | Set `is_stac=True` — see below |
| Compressed archive | `.zip` | zipfile | Extracted automatically |

**Formats NOT yet supported — preprocess to GeoTIFF first:**

- **HDF4 / HDF5** (`.hdf`, `.h5`, `.he4`, `.he5`) — used by MODIS, VIIRS, SRTM.
  Convert with: `gdal_translate HDF4_EOS:EOS_GRID:"file.hdf":Grid:Band output.tif`
- **GRIB / GRIB2** (`.grb`, `.grb2`) — used by ERA5, GFS, ECMWF weather models.
  Convert with: `cfgrib` + `xarray`, then write to GeoTIFF via rasterio.
- **LAS / LAZ point clouds** — LiDAR data; requires `pdal` to rasterize to a DEM first.

---

### Data Acquisition Workflow

When a dataset is provided as a URL, the agent MUST:

1. **Download**

   - Save to a structured data directory (e.g., `data/raw/`)
   - Preserve original filenames
   - Avoid overwriting existing data unless explicitly instructed

2. **Extract (if needed)**

   - Detect archive type automatically
   - Extract to:

     ```
     data/raw/<dataset_name>/
     ```

3. **Discover + Select Data**

   - Identify valid geospatial files:

     - Raster: `.tif`, `.tiff`
     - Vector: `.shp`, `.geojson`, `.gdb`
   - If multiple valid files exist → ask the user which to use
   - Prefer primary or highest-quality datasets when obvious

---

### Data Organization

The agent SHOULD organize data as:

```
data/
  raw/
  processed/
    harmonized/
```

---

### Reproducibility Requirements

The agent MUST:

- Log all data sources (URLs)
- Preserve raw data unchanged
- Document extraction and preprocessing steps

---

### Failure Handling

If:

- Download fails → retry or notify user
- Archive cannot be read → report issue
- No valid geospatial files found → stop and ask user

The agent MUST NOT proceed with incomplete or ambiguous data.

---

## Data Sovereignty and Intellectual Property Policy

- Consider licensing, copyright, privacy, Indigenous data sovereignty, and related restrictions for all data and content.
- If rights or permissions are unclear, document uncertainty and avoid assuming open reuse.

---

## Design and Usability Policy

- Keep the website simple, readable, and easy to extend by default.
- When design improvements are requested, prioritize system-level improvements (layout, spacing, typography, hierarchy, navigation, consistency).
- Do not use scattered one-off styling hacks.

---

## Decision Logging

- Reflect meaningful structural, architectural, documentation, data-source, or design decisions in changelog, dev log, roadmap, or equivalent history files when appropriate.

---

# Geospatial Harmonization Agent (LLM-Guided Workflow)

## Purpose

The Geospatial Harmonization Agent standardizes multiple geospatial datasets (raster and vector) into a common spatial support so they can be directly compared or analyzed.

---

## Supported Data Types

- Raster (GeoTIFF, COG, etc.)
- Vector (GeoJSON, Shapefile, GDB)

---

## Required User Inputs

The agent MUST ensure the following inputs are defined before execution:

- `target_crs` (e.g., EPSG:4326)
- `target_extent` (xmin, ymin, xmax, ymax)
- `input_datasets` (local paths or URLs)

If any are missing → ask the user before proceeding.

---

## Resolution Harmonization Policy

If multiple raster datasets have different resolutions:

The agent MUST:

1. Detect mismatch

2. Ask the user:

   “Do you want to:
   (a) upsample to the finest resolution
   (b) downsample to the coarsest resolution
   (c) specify a custom resolution?”

3. Apply consistently across all outputs

### Resampling Rules

| Data type | Method | Reason |
|---|---|---|
| Categorical (land cover, fuel models, soil class) | `nearest` | Interpolating between class codes produces meaningless values |
| Continuous (temperature, VPD, elevation, precipitation) | `bilinear` | Smooth interpolation preserves gradients |
| Continuous, high precision needed | `cubic` | Better edge accuracy at cost of speed |
| Unknown | Ask the user | Cannot infer safely |

Set `resampling_method` on `DatasetSpec` explicitly.  If not set, the harmonizer
auto-detects: integer dtype → `nearest`, float dtype → `bilinear`.  Always verify
for datasets where the dtype does not match the data type (e.g. float-encoded
categorical data).

---

## Vector ↔ Raster Strategy

When vector data is present:

The agent MUST ask:

“Should vector data be rasterized to match the raster grid?”

If YES:

- Rasterize using target CRS, extent, and resolution
- Ask for attribute field if needed

If NO:

- Keep vector format
- Align CRS and extent only

---

## STAC Data Sources

Use `is_stac=True` on a `DatasetSpec` to search a STAC catalog and download an
asset.  Key fields:

| Field | Description | Example |
|---|---|---|
| `url` | STAC API root URL | `"https://planetarycomputer.microsoft.com/api/stac/v1"` |
| `stac_collection` | Collection ID | `"sentinel-2-l2a"`, `"landsat-c2-l2"`, `"cop-dem-glo-30"` |
| `stac_asset` | Asset key to download | `"B08"`, `"SR_B4"`, `"visual"`, `"data"` |
| `stac_datetime` | ISO-8601 date or range | `"2023-06-01/2023-08-31"` |
| `stac_query` | Extra filter properties | `{"eo:cloud_cover": {"lt": 20}}` |

The harmonizer automatically picks the least-cloudy item within the search results.
If an asset key is wrong, the error message lists all available keys.

**Common public STAC catalogs:**
- Microsoft Planetary Computer: `https://planetarycomputer.microsoft.com/api/stac/v1`
- Earth Search (AWS): `https://earth-search.aws.element84.com/v1`
- NASA CMR STAC: `https://cmr.earthdata.nasa.gov/stac`

---

## NetCDF and OPeNDAP Sources

For datasets in NetCDF format (MACAv2, CMIP6, ERA5 subsets, etc.):

- Set `netcdf_variable` on `DatasetSpec` to the variable name inside the file
  (e.g. `"air_temperature"`, `"pr"`, `"relative_humidity"`).
- For derived quantities that require two input variables (e.g. VPD from tasmax +
  rhsmin), set `secondary_url` and `secondary_netcdf_variable` as well.
- Use OPeNDAP URLs (THREDDS `dodsC` paths) rather than full file downloads to
  subset spatially before any data is transferred.
- The harmonizer fetches both variables in parallel and subsets to the target bbox
  before triggering the download.

**MACAv2 CMIP5 OPeNDAP URL pattern:**
```
http://thredds.northwestknowledge.net:8080/thredds/dodsC/
  agg_macav2metdata_{variable}_{model}_r1i1p1_{scenario}_{start}_{end}_CONUS_monthly.nc
```

Variables: `tasmax`, `tasmin`, `pr`, `rhsmax`, `rhsmin`, `huss`, `rsds`, `was`, `uas`, `vas`
Models: `CCSM4`, `CanESM2`, `HadGEM2-ES365`, `MIROC5`, `IPSL-CM5A-LR`, and 15 others
Scenarios: `historical` (1950–2005), `rcp45` (2006–2099), `rcp85` (2006–2099)

---

## Nodata Handling

- The harmonizer preserves the source nodata value through reprojection.
- If no nodata is declared in the source file, it defaults to `0` for integer
  dtypes and `NaN` for float dtypes.
- Pixels outside the source extent are filled with the nodata value after
  reprojection — they are **not** filled with zero.
- When combining layers for analysis, mask pixels where **any** layer is nodata
  before computing statistics.
- If a dataset encodes nodata as a large sentinel value (e.g. `-9999`, `32767`),
  verify this is correctly declared in the file metadata.  If not, set it
  explicitly before passing to the harmonizer.

---

## Harmonization Workflow

The agent MUST execute:

1. Inspect datasets
2. Validate inputs
3. Reproject to target CRS
4. Clip to target extent
5. Harmonize resolution (raster only)
6. Handle vector conversion if needed
7. Save outputs
8. Generate visualization

---

## Output Requirements

### Harmonized Data

- Shared CRS
- Shared extent
- Shared resolution (if raster)
- Saved with:

  ```
  harmonized_<original_name>.tif
  ```

### Visualization

- Multi-panel or overlay map
- Saved as:

  ```
  harmonized_visualization.png
  ```

---

## Interaction Model

The agent SHOULD:

- Ask clarifying questions
- Explain decisions briefly
- Surface tradeoffs

The agent SHOULD NOT:

- Make silent assumptions
- Perform destructive operations without confirmation

---

## Example Workflows

The agent SHOULD support real-world workflows involving:

- Remote datasets provided via URL
- Mixed raster and vector inputs
- Harmonization to a user-defined CRS and extent

See:

- `examples/colorado_harmonization.py`
- `notebooks/colorado_harmonization_demo.ipynb`

---

## Implementation Notes

- Core implementation: `src/geospatial_harmonizer.py`
- Raster processing uses rasterio
- Visualization via matplotlib
- Vector support may require preprocessing

---

## Interactive Map: Large Vector Handling

When a vector layer exceeds 50 MB on disk, the harmonizer automatically simplifies
it before embedding in the HTML map:

- Geometry is simplified using a tolerance of ~0.1% of the shorter bbox dimension
  (≈100 m for a state-scale map like Colorado).
- Coordinates are snapped to a 0.0001° grid (~11 m precision).
- All non-geometry attribute columns are dropped to minimize file size.
- The simplification tolerance and resulting size are logged so the user can see
  exactly what happened.

**The agent MUST disclose this to the user whenever simplification occurs.**
Example disclosure:

> "The building footprints layer (707 MB) was too large to embed in the HTML map
> as-is. I simplified the geometry to ~100 m tolerance and reduced coordinate
> precision to 4 decimal places before embedding — the visual result at state
> scale is identical, but individual building shapes are approximated. If you
> need full-fidelity vector tiles, consider serving the original GeoJSON as
> PMTiles or via a WFS endpoint."

---

## Known Limitations

- **HDF4/HDF5 and GRIB/GRIB2 not supported** — preprocess to GeoTIFF with GDAL or cfgrib before using the harmonizer.
- **Multi-band rasters** — only band 1 is read; multi-spectral inputs (Landsat, Sentinel) must be split per band or use the STAC asset key to select a single band.
- **Time series output** — the pipeline produces one harmonized raster per dataset; stacked temporal outputs are not yet supported.
- **Attribute-based rasterization** — vectors are rasterized with a constant burn value; to burn a field value (e.g. fire year, watershed ID) requires a custom step.
- **DEM-derived products** — slope and aspect are not computed automatically; download a DEM and derive these externally before adding to the workflow.
- **Spectral indices** — NDVI, NBR, EVI are not computed automatically; download the required bands separately and compute before harmonizing.
