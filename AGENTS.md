# AGENTS.md

## Repository Purpose

This repository is a **template for scientists** learning how AI can help harmonize environmental datasets. It ships with a Colorado fire risk example so scientists can see what kinds of data the system can process and so the agent can learn from a concrete worked example.

---

## TL;DR — Required for every workflow

When a scientist asks for a new harmonization analysis, you MUST do all of the following.
Every item links to the detailed section below; none are optional.

1. **Validate all user-provided URLs FIRST** by running `python scripts/check_urls.py <url1> <url2> ...` before writing any code. If any URL fails, stop and tell the user which URLs are broken. You MAY suggest alternatives from the data catalog (step 2) for the broken ones, but always wait for the user to confirm before proceeding. Do NOT write a script with broken URLs.
2. **Search the data catalog ONLY when needed** — run `python scripts/find_dataset.py <keyword>` when: (a) the user asks for data by topic without providing URLs, (b) a user-provided URL failed and you need to suggest an alternative, or (c) the user asks what's available. Do NOT search the catalog when the user already provided working URLs. Do NOT open or grep `data_catalog.yml` manually; the script is faster and more reliable. See [Check the catalog before searching elsewhere](#check-the-catalog-before-searching-elsewhere).
3. **Place the script in `workflows/<project_name>/`** — never in `examples/` (read-only teaching material).
4. **Start the script with the bootstrap header** (sys.path insert) — see [Required Script Header](#required-script-header). Skipping this causes `ModuleNotFoundError: No module named 'src'` when run from any working directory other than the repo root.
5. **Set `output_dir=Path(__file__).parent / "output"`** so outputs co-locate with the script.
6. **Save the static visualization as exactly `harmonized_visualization.png`** — the mkdocs build hook in [hooks.py](hooks.py) is hardcoded to that filename. Different filenames silently fail to appear on the website.
7. **Create `docs/workflows/<project_name>.md`** from the [template](#template-for-docsworkflowsproject_namemd) — `tests/test_doc_pages.py` will fail if any `<PLACEHOLDER>` text remains.
8. **Append a new entry to `PROMPT_ACTION_LOG.md`** with the user's exact prompt verbatim.
9. **Add any newly used datasets to `data_catalog.yml`** (only if their URL passes `tests/test_url_health.py`).
10. **If the user names a US state, county, or place, run `python scripts/region_extent.py <type> <name> [<state>] [--crs <target_crs>]`** to get `target_extent` — never guess from model knowledge, and pass `--crs` whenever `target_crs` ≠ EPSG:4326. **Always set `clip_boundary`** to clip outputs to the actual boundary polygon, not just the rectangular bounding box (e.g. `clip_boundary="state:<name>"`). See [Resolving named regions to a bbox and boundary clipping](#resolving-named-regions-to-a-bbox-and-boundary-clipping). For regions outside the US or outside TIGER (custom AOIs, ecoregions, international locations), see [Regions outside CONUS and international locations](#regions-outside-conus-and-international-locations).
11. **Run the script with `nohup ... &`** so it executes in the background. **Check progress with `cat workflows/<project_name>/output/.status`** — it will say `RUNNING`, `DONE`, or `FAILED`. First check after 2 minutes, then every 3 minutes. Never re-run a script that is still running.

If you skip any of these, the workflow is incomplete. Each rule is detailed in a section below.

---

## Directory Structure

```
src/                              Core harmonization library — do NOT modify
examples/
  colorado_fire_risk/             Reference example — do NOT modify
    colorado_harmonization.py
    output/                       Generated outputs for this example
workflows/
  my_project/                     Each user analysis is its own folder
    my_script.py
    output/                       Generated outputs for this project
docs/                             Website source
```

Each project — whether an example or a user workflow — is **self-contained**: the script and its outputs live in the same folder. `output/` is always a subfolder of the project, never a top-level directory.

When a scientist asks you to analyze new data:
- Create a new folder in `workflows/my_project_name/`
- Put the script inside it
- Set `output_dir=Path(__file__).parent / "output"` so outputs land next to the script
- Do NOT create files in `examples/` — that is read-only teaching material

---

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
- Preserve existing structure and historical context.
- Do not perform destructive rewrites unless explicitly requested.
- Record each harmonization run in `PROMPT_ACTION_LOG.md`.

---

## Prompt and Action Logging

- `PROMPT_ACTION_LOG.md` is required project memory for all harmonization activity.
* After every successful harmonization, append a new dated entry with:
  + the user's original prompt (verbatim or as close as possible),
  + the LLM/agent that handled the request (model name and version, e.g. "MiniMax-M2.5" or "gpt-oss-120b"); ,
  + the files and folders inspected,
  + the actions taken and key decisions made per dataset,
  + any verification performed,
  + open questions, caveats, or follow-up needs.
- Keep entries factual and chronological.
- Preserve the user's exact wording in the Prompt field — it is the reproducible record of what was requested.

---

## Documentation and Website Policy

- Treat `docs/` as project-level documentation and website source.
- Update docs whenever code, workflows, or outputs change.
- Amend existing docs when possible; do not replace whole files without need.
- Preserve navigation, readability, and consistency in website changes.
- Keep default website behavior clean and minimal unless the user asks for more expressive design.

---

## Documentation Generation Protocol for New Analyses

Every time you create a new workflow in `workflows/<project_name>/` and run it,
you MUST create `docs/workflows/<project_name>.md` before the task is complete.

The hook in `hooks.py` automatically handles:
- Copying the PNG from `workflows/<project_name>/output/` into `docs/assets/workflows/<project_name>/` at build time
- Injecting the page into the website nav under a "Workflows" section

You only need to create the Markdown file. Do NOT manually edit `mkdocs.yml`.

### Template for `docs/workflows/<project_name>.md`

Fill all placeholders from the script and conversation. Commit no placeholder text (`<...>`).

```markdown
# <Project Name>

<One-sentence description of the scientific question this workflow addresses.>

---

## Prompt

> "<Exact user prompt or request that produced this workflow, including the
> dataset URLs provided by the user.>"

---

## Datasets

| Layer | Type | URL |
|---|---|---|
<!-- One row per DatasetSpec. Include the exact download URL so the workflow is reproducible. -->

**Target grid:** <TARGET_CRS> · extent <TARGET_EXTENT> · resolution <TARGET_RESOLUTION>

---

## What Was Harmonized

<!-- 2–4 bullets: resampling choices, vector/raster decisions, notable preprocessing. -->

---

## Result

![Harmonized visualization for <project_name>](../assets/workflows/<project_name>/harmonized_visualization.png)

---

## Reproduce It

From the repo root:

\```bash
python workflows/<project_name>/<script_name>.py
\```

Outputs are saved to `workflows/<project_name>/output/`.

---

## Source

Script: `workflows/<project_name>/<script_name>.py`
```

### How the PNG gets to the website

The hook in `hooks.py` runs `on_pre_build` and copies
`workflows/<project_name>/output/harmonized_visualization.png` →
`docs/assets/workflows/<project_name>/harmonized_visualization.png` at every
`mkdocs build` or `mkdocs serve`. The file in `docs/assets/` is never committed
to git — it is always regenerated from the canonical output directory.

The image path in the Markdown file must be:
```
../assets/workflows/<project_name>/harmonized_visualization.png
```
(relative from `docs/workflows/` up one level to `docs/`, then into `assets/`).

### Verification checklist

- [ ] `docs/workflows/<project_name>.md` exists with no placeholder text
- [ ] The Prompt section contains the exact user request
- [ ] Dataset table has one row per `DatasetSpec` in the script
- [ ] Image path matches `../assets/workflows/<project_name>/harmonized_visualization.png`
- [ ] `mkdocs.yml` was NOT manually edited (hook handles the nav)

---

## Data Catalog Protocol

`data_catalog.yml` at the repo root is a library of known-good dataset URLs.
It is seeded with the Colorado fire risk example datasets and grows as new
workflows are created.

### When to search the data catalog

**If the user provided URLs:** do NOT search the catalog. Validate the URLs
with `check_urls.py` and use them directly if they pass. Only search the
catalog if a URL fails and you need to suggest an alternative.

**If the user requests data by topic, name, or region** without providing URLs
(e.g. "fire risk in Wyoming", "NLCD land cover", "building footprints for
Texas") — search the catalog first. The catalog is the canonical,
health-checked source of truth; URLs found there have already been verified
to download and harmonize correctly.

Catalog lookup workflow:

1. **Run `python scripts/find_dataset.py <keyword> [<keyword> ...]`.** This is
   the one-shot lookup: it scans every entry's name, source, notes, topics,
   and variants list (case-insensitive substring match, multiple keywords
   AND-ed) and prints each match with its concrete URL (or expanded template),
   default STAC asset, type, and topics. Examples:
   ```bash
   python scripts/find_dataset.py fire
   python scripts/find_dataset.py climate precipitation
   python scripts/find_dataset.py building wyoming
   ```
   Do NOT open or grep `data_catalog.yml` manually; the script is faster and
   more reliable.
2. If a matching entry exists, use that URL directly — do NOT search the web,
   the ESIIL Data Library, or external sources for an alternative.
3. If multiple entries match (e.g. NLCD has multiple years), surface the choices
   and ask the user which to use.
4. Only fall through to the ESIIL Data Library or web search if no entry matches.
5. If you discover a new URL through the fallback path AND it passes the health
   check after a successful workflow, add it to the catalog (see rules below).

### Templated entries (url_template + variants)

Some entries cover many variants of the same dataset under one row. These use
`url_template:` (with `{placeholder}` syntax) and `variants:` (the list of valid
substitutions) instead of a literal `url:`. To use one:

1. Read the entry's `url_template` and `variants` fields.
2. Substitute the variant the user asked for into the placeholder.
3. Pass the resulting URL to `DatasetSpec` as usual.

Examples:
- `url_template: .../usbuildings-v2/{state}.geojson.zip`, `state=Wyoming` →
  `.../usbuildings-v2/Wyoming.geojson.zip`
- `url_template: .../Annual_NLCD_LndCov_{year}_CU_C1V1.zip`, `year=2024` →
  `.../Annual_NLCD_LndCov_2024_CU_C1V1.zip`

The URL health test only checks the first variant of each templated entry,
since all variants share the same host. Add a templated entry (rather than N
separate rows) when you have ≥3 mostly-identical entries that differ only in
one substitutable token (year, state code, FIPS, tile ID, etc.).

### DatasetSpec field reference

Every workflow constructs one `DatasetSpec` per input layer. The fields below
are the complete public API — if a field you want to use isn't listed here,
**it doesn't exist**. Do not invent fields like `crs=`, `extent=`, or
`resampling=`; CRS / extent / resolution belong on `ExampleWorkflow`, not on
individual datasets. Source of truth: `src/geospatial_harmonizer.py:91`.

| Field | Type | Default | Purpose |
|---|---|---|---|
| `name` | `str` | required | Short identifier — used as the output filename stem |
| `url` | `str` | required | Direct download URL, OPeNDAP endpoint, or STAC API root |
| `data_type` | `Literal["raster", "vector"]` | required | Dispatches to raster vs vector pipeline |
| `rasterize` | `bool` | `False` | Vector→raster: rasterize to the target grid instead of keeping vector |
| `burn_value` | `int` | `1` | Value to burn into rasterized vector pixels |
| `labels_url` | `str \| None` | `None` | URL to a `VALUE,LABEL` CSV for legend labels |
| `resampling_method` | `Literal["bilinear", "nearest", "cubic"] \| None` | `None` (auto) | Override auto-detect (int dtype → nearest, float → bilinear) |
| `display_name` | `str \| None` | `None` | Human-readable label for visualization panels (falls back to formatted `name`) |
| `description` | `str \| None` | `None` | One-line subtitle shown below the panel title (e.g. "What can burn") |
| `netcdf_variable` | `str \| None` | `None` | NetCDF/OPeNDAP variable name, e.g. `"precipitation"` |
| `netcdf_months` | `list[int] \| None` | `None` | Month indices to average over, e.g. `[12,1,2,3]` for winter |
| `secondary_url` | `str \| None` | `None` | Second OPeNDAP URL for derived variables (e.g. `rhsmin` for VPD) |
| `secondary_netcdf_variable` | `str \| None` | `None` | Variable name in the secondary NetCDF |
| `is_stac` | `bool` | `False` | Set `True` to discover/download via STAC catalog |
| `stac_collection` | `str \| None` | `None` | STAC collection ID, e.g. `"sentinel-2-l2a"` |
| `stac_asset` | `str \| None` | `None` | Asset key to download, e.g. `"B08"` or `"data"` |
| `stac_datetime` | `str \| None` | `None` | ISO-8601 range, e.g. `"2023-06-01/2023-08-31"` |
| `stac_query` | `dict \| None` | `None` | Extra search filters, e.g. `{"eo:cloud_cover": {"lt": 20}}` |
| `is_wcs` / `wcs_layer` | `bool` / `str` | `False` / `None` | WCS endpoint support (rarely needed) |
| `is_wms` / `wms_layer` | `bool` / `str` | `False` / `None` | WMS endpoint support (rarely needed) |

`ExampleWorkflow` carries the workflow-level settings (CRS, extent, resolution,
output_dir, create_visualization, verbose) — not `DatasetSpec`.

### Catalog entry → DatasetSpec (worked examples)

The catalog row tells you what to pass to `DatasetSpec`. Three cases:

**Plain entry (most common).** Just use `url:` directly.

```yaml
# data_catalog.yml
- name: USDA Cropland Data Layer (CDL) 2025
  url: https://www.nass.usda.gov/Research_and_Science/Cropland/Release/datasets/2025_30m_cdls.zip
```
```python
# in your workflow
DatasetSpec(
    name="cdl_2025",
    url="https://www.nass.usda.gov/Research_and_Science/Cropland/Release/datasets/2025_30m_cdls.zip",
    resampling_method="nearest",  # categorical — see entry's notes
)
```

**Templated entry.** Substitute the chosen variant into `url_template`.

```yaml
# data_catalog.yml
- name: National Land Cover Database (NLCD) — Annual CONUS
  url_template: https://www.mrlc.gov/.../Annual_NLCD_LndCov_{year}_CU_C1V1.zip
  variants: [2024, 2023, 2022, 2021, 2020, 2016, 2011, 2006, 2001]
```
```python
url = "https://www.mrlc.gov/.../Annual_NLCD_LndCov_2024_CU_C1V1.zip"  # year=2024 from variants
DatasetSpec(name="nlcd_2024", url=url, resampling_method="nearest")
```

**STAC entry.** Set `is_stac=True`, copy `stac_collection`, pick an asset
(use `stac_asset_default` if unsure).

```yaml
# data_catalog.yml
- name: ERA5 Hourly Reanalysis (Microsoft Planetary Computer STAC)
  url: https://planetarycomputer.microsoft.com/api/stac/v1
  stac_collection: era5-pds
  stac_asset_default: air_temperature_at_2_metres
```
```python
DatasetSpec(
    name="era5_t2m",
    url="https://planetarycomputer.microsoft.com/api/stac/v1",
    is_stac=True,
    stac_collection="era5-pds",
    stac_asset="air_temperature_at_2_metres",  # from stac_asset_default
    stac_datetime="2023-06-01/2023-08-31",     # optional date filter
    resampling_method="bilinear",              # continuous — see entry's notes
)
```

### Adding new entries

Every time a workflow runs successfully (URLs download, harmonization completes,
PNG is generated), you MUST add any new datasets to `data_catalog.yml`:

```yaml
  - name: <Human-readable dataset name>
    type: raster  # or vector
    source: <Organization / service name>
    url: <direct download or OPeNDAP URL>
    labels_url: <optional — CSV with VALUE, R, G, B, label columns>
    notes: >
      <One or two sentences: format, resampling choice, gotchas.>
```

Rules:
- **Only add URLs that pass `tests/test_url_health.py`.** A URL that fails the
  health check does not belong in the catalog — remove it even if it worked in
  the past. Sources go stale and the catalog must stay clean.
- Do not add URLs that failed to download or produced corrupt outputs.
- Do not duplicate existing entries — check the file before adding.
- Include `labels_url` if a CSV was needed for correct visualization colors/labels.
- Add a `notes` line if the dataset requires special handling (e.g. OPeNDAP
  variable name, ensemble member, rasterization decision).
- No API keys: only add URLs that are freely accessible without authentication.

If an existing entry starts returning errors in the health check, **remove it**
from `data_catalog.yml`. Do not add `health_check: skip` to work around a
failure — that defeats the purpose of the catalog.

If `data_catalog.yml` does not already contain a matching dataset, fall through
to the ESIIL Data Library at https://cu-esiil.github.io/data-library/ for
relevant datasets and working code examples. If you successfully download and
harmonize a dataset found there, add the URL to `data_catalog.yml`.

To discover new candidate URLs from the ESIIL library, run:
```bash
python scripts/sync_esiil_catalog.py
```
This prints YAML candidates to stdout. Review them, verify each URL passes the
health check, set `type`, update `notes`, then add useful entries to
`data_catalog.yml`.

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

   - The harmonizer handles downloads internally; pass the URL via `DatasetSpec`
   - Raw files are written to a temporary directory during processing
   - Avoid overwriting existing harmonized outputs unless explicitly instructed

2. **Extract (if needed)**

   - Detect archive type automatically (ZIP is handled by the harmonizer)

3. **Discover + Select Data**

   - Identify valid geospatial files:

     - Raster: `.tif`, `.tiff`, `.img`
     - Vector: `.shp`, `.geojson`, `.gdb`, `.gpkg`
   - If multiple valid files exist inside an archive → ask the user which to use
   - Prefer primary or highest-quality datasets when obvious

---

### Output Organization

Each project writes outputs into its own `output/` subfolder, co-located with the script:

```
examples/colorado_fire_risk/
  colorado_harmonization.py
  output/
    harmonized_*.tif             # harmonized rasters (gitignored)
    harmonized_*.geojson         # harmonized vectors (gitignored)
    harmonized_visualization.png # static map (tracked in git)
    harmonized_visualization.html# interactive map (tracked in git)

workflows/my_project/
  my_script.py
  output/
    harmonized_*.tif             # (gitignored)
    harmonized_visualization.png # (tracked)
```

Always set `output_dir=Path(__file__).parent / "output"` in new scripts.

---

### Required Script Header

Every workflow script MUST include this bootstrap before importing from `src/`,
so the script runs correctly regardless of the user's working directory **and
regardless of how deeply the script is nested below the repo root**:

```python
import sys
from pathlib import Path

# Walk up the directory tree until we find the repo root (the dir containing src/).
# This is depth-agnostic: works for examples/<topic>/<script>.py,
# workflows/<project>/<script>.py, and arbitrarily nested subfolders.
_repo_root = next(p for p in Path(__file__).resolve().parents
                  if (p / "src" / "geospatial_harmonizer.py").exists())
sys.path.insert(0, str(_repo_root))

from src.geospatial_harmonizer import (
    DatasetSpec,
    ExampleWorkflow,
    run_harmonization_example,
)
```

Without this header, `from src.geospatial_harmonizer import ...` only works when
the user happens to run from the repo root with `src/` on `PYTHONPATH`. With it,
`python workflows/my_project/my_script.py` (or any nested path) works from anywhere.

**Why a walker instead of `.parent.parent.parent`?** The earlier template
hardcoded "three levels up", which broke as soon as a script lived at a
different depth (e.g. `workflows/<topic>/<subtopic>/script.py`). The walker
finds the repo root by *content* (the presence of `src/geospatial_harmonizer.py`)
rather than by *count*, so it can't get the depth wrong.

The Colorado reference example uses this pattern — see
`examples/colorado_fire_risk/colorado_harmonization.py`.

---

### Reproducibility Requirements

The agent MUST:

- Log all data sources (URLs)
- Preserve raw data unchanged
- Document extraction and preprocessing steps

---

### Failure Handling

If:

- Download fails → **stop and tell the user which URL failed and why**.
  You MAY suggest alternatives from `data_catalog.yml` (run `find_dataset.py`),
  but do NOT search the web for replacement URLs on your own.
  Always wait for the user to confirm before substituting any dataset.
- Archive cannot be read → report issue
- URL returns an HTML page instead of data → tell the user this is a portal
  link, not a direct download URL, and ask for a direct download URL.
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

- `target_crs` (e.g., `EPSG:4326`, `EPSG:32613`, or any CRS pyproj resolves).
  **Any valid CRS is supported** — not just EPSG:4326. When using a projected CRS
  (e.g. UTM zones), remember that `target_extent` is in the CRS's native units
  (meters, not degrees) and `target_resolution` should also be in meters.
- `target_extent` (xmin, ymin, xmax, ymax) — see [Resolving named regions to a bbox and boundary clipping](#resolving-named-regions-to-a-bbox-and-boundary-clipping) below.
  Must be in the same CRS as `target_crs`.
- `clip_boundary` (recommended) — clips outputs to an actual boundary polygon instead
  of just the rectangular bounding box. See [Boundary clipping](#boundary-clipping-not-just-bounding-box).
  For US states/counties/places, use the shorthand (e.g. `"state:<name>"`).
  For custom regions, ask the user for a boundary file.
- `input_datasets` (local paths or URLs)

If any required inputs are missing → ask the user before proceeding.

### Resolving named regions to a bbox and boundary clipping

If the user names a US state, county, or place ("crop to Colorado", "just
Larimer County", "around Boulder, CO"), **never fabricate the bounding box
from model knowledge**. Run the helper and use its output verbatim:

```bash
python scripts/region_extent.py state Colorado
python scripts/region_extent.py county Larimer Colorado
python scripts/region_extent.py place Boulder CO
```

The script downloads (and caches) the relevant Census TIGER 2025 layer,
filters to the requested feature, reprojects, and prints a ready-to-paste
`target_extent=(xmin, ymin, xmax, ymax)` line. State identifiers accept the
full name, the 2-letter postal code, or the 2-digit FIPS code.

**Match the bbox CRS to `target_crs`.** `target_extent` and `target_crs` must
agree — pass `--crs` whenever the workflow uses anything other than EPSG:4326.
Any CRS pyproj can resolve is accepted (EPSG codes, WKT, proj strings):

```bash
python scripts/region_extent.py state Colorado --crs <whatever-target_crs-is>
```

The polygon is reprojected before bounds are taken, so the output tightly
envelops the feature in the target CRS (corner-reprojection alone would miss
curvature in projected CRSs).

#### Boundary clipping (not just bounding box)

**Always set `clip_boundary` on `ExampleWorkflow`** when the user names a
geographic region. A bounding box is rectangular; most states, counties, and
places are not. Without `clip_boundary`, the output includes data outside the
actual boundary (e.g. corners of adjacent states).

`clip_boundary` accepts three formats:

| Format | Example | When to use |
|---|---|---|
| Shorthand string | `"state:<name>"`, `"county:<name>:<state>"`, `"place:<name>:<state>"` | Any US state / county / place — resolved automatically via Census TIGER |
| File path | `"data/my_boundary.geojson"` | User-provided boundary file (GeoJSON, shapefile, GeoPackage) for custom regions |
| `None` (default) | — | Rectangular bbox only (backwards compatible) |

**What it does:**
- **Rasters:** pixels outside the boundary polygon are set to nodata after
  reprojection, so the output follows the actual boundary shape.
- **Vectors:** features are clipped to the boundary polygon (not just filtered
  by bbox intersection).
- The grid is still computed from the rectangular bbox of the boundary
  (for pixel alignment), but the boundary mask removes data outside the polygon.

**Example — state boundary in EPSG:4326 (geographic CRS):**

```python
# Resolution is in degrees because EPSG:4326 is geographic.
# Substitute any state, county, or place the user requests.
workflow = ExampleWorkflow(
    name="virginia_land_cover",
    datasets=DATASETS,
    target_crs="EPSG:4326",
    target_extent=(-83.6754, 36.5408, -75.2422, 39.466),  # from region_extent.py state Virginia
    target_resolution=0.00243,
    output_dir=OUTPUT_DIR,
    clip_boundary="state:Virginia",  # clips to actual state polygon, not bbox
)
```

**Example — projected CRS (meters) with boundary clipping:**

```python
# Resolution is in meters because EPSG:5070 (Conus Albers) is projected.
# Pass --crs so target_extent is in the same units as target_crs.
workflow = ExampleWorkflow(
    name="larimer_fire_risk",
    datasets=DATASETS,
    target_crs="EPSG:5070",
    target_extent=(-876543.2, 1789012.3, -812345.6, 1856789.0),  # from region_extent.py county Larimer Colorado --crs EPSG:5070
    target_resolution=270,  # 270 meters in projected CRS
    output_dir=OUTPUT_DIR,
    clip_boundary="county:Larimer:Colorado",  # boundary auto-reprojected to target_crs
)
```

**Example — user-provided boundary file:**

```python
# For regions not in Census TIGER (watersheds, custom AOIs, etc.),
# ask the user for a GeoJSON/shapefile and pass the path directly.
workflow = ExampleWorkflow(
    name="watershed_analysis",
    datasets=DATASETS,
    target_crs="EPSG:32613",
    target_extent=(400000.0, 4400000.0, 500000.0, 4500000.0),
    target_resolution=30,
    output_dir=OUTPUT_DIR,
    clip_boundary="data/my_watershed.geojson",  # any vector file the user provides
)
```

**For anything the helper does not cover** — custom AOIs, ecoregions,
watersheds, study sites, neighborhoods, named features outside TIGER —
**ask the user** for a boundary vector file (GeoJSON/shapefile) to pass as
`clip_boundary`, or fall back to a bbox in the target CRS. Guessing is not
an acceptable fallback; an off-by-half-a-degree extent silently miscrops
every downstream layer.

### Regions outside CONUS and international locations

The harmonizer works with **any location on Earth** — it is not limited to
CONUS or the US. However, the worked examples and most catalog entries happen
to cover CONUS, so the agent must take extra care when a user requests a
region outside the contiguous United States (including Alaska, Hawaii, US
territories, and international locations).

#### Region resolution

`scripts/region_extent.py` and the `clip_boundary` shorthand strings
(`"state:X"`, `"county:X:Y"`, `"place:X:Y"`) use **US Census TIGER** data
and only resolve US states, counties, and places. **Do not attempt to use
them for non-US locations** — they will error.

For non-US regions, the agent MUST:

1. **Ask the user** for one of:
   - A bounding box (`target_extent`) in the target CRS, or
   - A boundary vector file (GeoJSON, shapefile, GeoPackage) to pass as
     `clip_boundary`.
2. **Never fabricate coordinates from model knowledge.** This rule applies
   globally, not just within the US — an off-by-a-degree extent silently
   miscrops every downstream layer.
3. If the user provides a boundary file, use it directly as `clip_boundary`
   (file-path format). The harmonizer will reproject it to `target_crs`
   automatically and derive `target_extent` from its bounding box.

**Example — international region with user-provided boundary:**

```python
workflow = ExampleWorkflow(
    name="amazon_deforestation",
    datasets=DATASETS,
    target_crs="EPSG:4326",
    target_extent=(-73.5, -18.0, -44.0, 5.3),     # user-provided bbox
    target_resolution=0.0025,
    output_dir=OUTPUT_DIR,
    clip_boundary="data/amazon_basin.geojson",      # user-provided boundary
)
```

#### Data catalog awareness

Many datasets in `data_catalog.yml` are US-specific or CONUS-only (e.g.
NLCD, CDL, LANDFIRE fuel models, MACAv2, MTBS, NClimGrid, Microsoft US
Building Footprints, Census TIGER boundaries). These datasets **will not
contain data** for regions outside their geographic scope.

When the user's region is outside CONUS, the agent MUST:

1. **Still check the catalog first** — some entries are global or
   near-global (Hansen Global Forest Change, ERA5, TerraClimate,
   NEX-GDDP-CMIP6, Daymet for North America). These work anywhere within
   their stated coverage.
2. **Read each matched entry's `notes` and `name` fields** to check for
   geographic scope keywords (e.g. "CONUS", "US", "North America",
   "global"). Do not blindly use a CONUS-only URL for a non-CONUS region.
3. **If no catalog entry covers the user's region**, fall through to:
   - STAC catalogs (Microsoft Planetary Computer, Earth Search, NASA CMR)
     for global satellite and climate data,
   - The ESIIL Data Library for curated examples,
   - Web search as a last resort.
4. **Tell the user** when a commonly used dataset (like NLCD) is not
   available for their region, and suggest global alternatives (e.g.
   ESA WorldCover or Copernicus Global Land Cover instead of NLCD).

#### CRS selection for non-CONUS regions

- **EPSG:4326** (WGS 84 geographic) works globally and is a safe default.
- For higher spatial accuracy, use a **UTM zone** appropriate for the
  region (e.g. `EPSG:32737` for UTM zone 37S in East Africa). Remember
  that `target_extent` and `target_resolution` must be in meters for
  projected CRSs.
- **Do not use CONUS-specific projected CRSs** (e.g. `EPSG:5070` Conus
  Albers) for regions outside CONUS — the distortion will be severe.

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
https://thredds.northwestknowledge.net/thredds/dodsC/
  agg_macav2metdata_{variable}_{model}_{ensemble}_{scenario}_{start}_{end}_CONUS_monthly.nc
```

Variables: `tasmax`, `tasmin`, `pr`, `rhsmax`, `rhsmin`, `huss`, `rsds`, `was`, `uas`, `vas`
Models: `CCSM4`, `CanESM2`, `HadGEM2-ES365`, `MIROC5`, `IPSL-CM5A-LR`, and 15 others
Scenarios: `historical` (1950–2005), `rcp45` (2006–2099), `rcp85` (2006–2099)

**Note — ensemble member varies by model.** Do not assume `r1i1p1`. Verify by
browsing the THREDDS catalog XML at:
```
https://thredds.northwestknowledge.net/thredds/catalog/MACAV2/catalog.xml
```
Example: CCSM4 uses `r6i1p1`, not `r1i1p1`.

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
9. Append an entry to `PROMPT_ACTION_LOG.md`

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

### Prompt Action Log

After every successful harmonization, append a new entry to `PROMPT_ACTION_LOG.md`
following the format and rules in the **Prompt and Action Logging** section above.
See `PROMPT_ACTION_LOG.md` for a worked example (the Colorado fire risk entry).

---

## Interaction Model

The agent SHOULD:

- Ask clarifying questions
- Explain decisions briefly
- Surface tradeoffs

The agent SHOULD NOT:

- Make silent assumptions
- Perform destructive operations without confirmation

### Be Patient With Long-Running Scripts

Harmonization scripts typically take **5–15 minutes** to run — downloading data,
reprojecting, and generating the final HTML/PNG outputs all take time. This is
normal, not a sign of failure.

**Do not prompt the user to re-run a script that is still executing.** If you
are unsure whether it finished, check whether the process is still running or
whether the expected output files exist before suggesting a retry.

**When running in tool environments with short command timeouts** (e.g. Roo Code,
Cline, Cursor), run the harmonization script in the background:

```bash
nohup python workflows/<project_name>/<script>.py > workflows/<project_name>/output/run.log 2>&1 &
```

The script writes a `.status` file in the output directory that tells you
exactly what is happening. **Use this to poll — not `ls` for the PNG.**

**Check status:**
```bash
cat workflows/<project_name>/output/.status
```

**The status file shows progress per dataset, for example:**
- `RUNNING: processing dataset 1/4: FBFM40 Fuel Models` — downloading/processing.
- `RUNNING: saved 2/4: harmonized_mtbs_burned_areas.geojson` — dataset 2 done, moving to 3.
- `RUNNING: saved 4/4: harmonized_vpd.tif — generating visualization next` — all datasets done, building PNG/HTML.
- `DONE: 7m 23s` — finished successfully. Proceed with follow-up tasks.
- `FAILED: URL does not work: https://... Please provide a different URL.` — something went wrong. Read the error and fix it.

**Polling rules:**
1. First poll: **2 minutes** after starting the script.
2. If status is `RUNNING`, wait **3 more minutes** before checking again.
3. If status is `FAILED`, read the error and act on it. Do NOT re-run the
   same script without fixing the problem first.
4. Do NOT re-run the script while status is `RUNNING`.

---

## Example Workflows

The agent SHOULD support real-world workflows involving:

- Remote datasets provided via URL
- Mixed raster and vector inputs
- Harmonization to a user-defined CRS and extent

See:

- `examples/colorado_fire_risk/colorado_harmonization.py`

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
- **Multi-band visualization** — `harmonize_raster` reads, reprojects, and writes all bands (multi-band GeoTIFFs round-trip cleanly), but `create_visualization` renders only band 1 in the static PNG. For multi-spectral analysis, work directly with the harmonized GeoTIFF; for single-band visualization output, use a STAC asset key to select one band upstream (e.g. Sentinel-2 `B08`, Landsat `SR_B4`).
- **Time series output** — the pipeline produces one harmonized raster per dataset; stacked temporal outputs are not yet supported.
- **Attribute-based rasterization** — vectors are rasterized with a constant burn value; to burn a field value (e.g. fire year, watershed ID) requires a custom step.
- **DEM-derived products** — slope and aspect are not computed automatically; download a DEM and derive these externally before adding to the workflow.
- **Spectral indices** — NDVI, NBR, EVI are not computed automatically; download the required bands separately and compute before harmonizing.
