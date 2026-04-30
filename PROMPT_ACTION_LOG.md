# Prompt Action Log

---

## 2026-03-31

### Prompt
User asked: "Download these datasets, harmonize them to EPSG:4326 over Colorado, and generate a map:

- FBFM40 fuel models (raster, categorical, `resampling_method="nearest"`):
  `https://www.landfire.gov/data-downloads/CONUS_LF2024/LF2024_FBFM40_CONUS.zip`
  Use this CSV for both visualization colors (R, G, B columns) and legend labels:
  `https://landfire.gov/sites/default/files/CSV/2024/LF2024_FBFM40.csv`
- MACAv2 winter precipitation via OPeNDAP (raster, continuous, variable `precipitation`, months Dec–Mar):
  `http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_macav2metdata_pr_CCSM4_r6i1p1_rcp85_2006_2099_CONUS_monthly.nc`
- MTBS burned area boundaries (vector, do not rasterize):
  `https://edcintl.cr.usgs.gov/downloads/sciweb1/shared/MTBS_Fire/data/composite_data/burned_area_extent_shapefile/mtbs_perimeter_data.zip`
- Microsoft building footprints (vector, rasterize to presence/absence):
  `https://minedbuildings.z5.web.core.windows.net/legacy/usbuildings-v2/Colorado.geojson.zip`"

### LLM
Claude Sonnet 4.5

### Files and folders inspected
- `src/geospatial_harmonizer.py`
- `data_catalog.yml`
- `AGENTS.md`

### Actions taken
- Created `examples/colorado_fire_risk/colorado_harmonization.py` defining four `DatasetSpec` entries and an `ExampleWorkflow` targeting EPSG:4326, Colorado extent (-109.05, 36.99, -102.04, 41.01), and ~270 m resolution (0.00243°).
- FBFM40 fuel models: downloaded CONUS ZIP, extracted GeoTIFF, resampled with `nearest` to preserve integer class codes; loaded Scott & Burgan color map and labels from Landfire CSV.
- MACAv2 precipitation: streamed via OPeNDAP, subsetted to Colorado before transfer to avoid downloading the full CONUS NetCDF; averaged Dec–Mar months; resampled from ~4 km to ~270 m using bilinear interpolation.
- MTBS burned areas: downloaded perimeter shapefile ZIP, reprojected to EPSG:4326, clipped to Colorado extent, kept as vector.
- Building footprints: downloaded Colorado GeoJSON ZIP, rasterized to presence/absence at ~270 m (burn value = 1); raw vector too large to embed in HTML at state scale.
- Generated `examples/colorado_fire_risk/output/harmonized_visualization.png` (per-layer static map) and `harmonized_visualization.html` (interactive Folium map with per-layer opacity controls).

### Verification
- Re-ran `python examples/colorado_fire_risk/colorado_harmonization.py` from repo root; all four layers harmonized and written to `examples/colorado_fire_risk/output/`.
- Confirmed OPeNDAP subset transferred only Colorado pixels (~19 MB vs. ~500 MB full CONUS).
- Confirmed `nearest` resampling preserved FBFM40 class codes (no interpolated values between integer codes).
- Visualization PNG and HTML map committed to git.

### Open questions and follow-up
- MTBS perimeters are kept as vector; if a future workflow needs them as a raster mask, set `rasterize=True` in the `DatasetSpec`.
- MACAv2 ensemble member used is CCSM4 r6i1p1; other models are available on the same THREDDS server if a multi-model comparison is needed.
