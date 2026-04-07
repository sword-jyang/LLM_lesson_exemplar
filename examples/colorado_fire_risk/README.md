# Colorado Fire Risk — Harmonization Example

This is a reference example showing how to harmonize four geospatial datasets over Colorado using `src/geospatial_harmonizer.py`.

## Datasets

| Layer | Type | Source |
|---|---|---|
| FBFM40 Fire Behavior Fuel Models | Raster (categorical) | Landfire 2024, direct ZIP download |
| MACAv2 Winter Precipitation | Raster (continuous) | CCSM4 RCP8.5 Dec–Mar mean 2006–2099, OPeNDAP |
| MTBS Burned Area Boundaries | Vector | USGS perimeter data |
| Microsoft Building Footprints | Vector → rasterized | Microsoft, Colorado state file |

All harmonized to EPSG:4326, Colorado extent, ~270 m resolution (0.00243°).

## Run it

From the repo root:

```bash
python examples/colorado_fire_risk/colorado_harmonization.py
```

Or from inside this folder:

```bash
python colorado_harmonization.py
```

## Output

Outputs are saved to `output/` inside this folder:

```
examples/colorado_fire_risk/
  colorado_harmonization.py
  output/
    harmonized_fbfm40_fuel_models.tif      # gitignored (regenerate with script)
    harmonized_pr_winter_rcp85_ccsm4.tif   # gitignored
    harmonized_mtbs_burned_areas.geojson   # gitignored
    harmonized_building_footprints.tif     # gitignored
    harmonized_visualization.png           # tracked in git
    harmonized_visualization.html          # tracked in git
```

## What this demonstrates

* Categorical raster resampling with `resampling_method="nearest"` to avoid interpolating between class codes
* Continuous raster resampling via OPeNDAP — only Colorado pixels are downloaded
* Mixed raster + vector inputs in one workflow
* Automatic rasterization of oversized vector layers
* Static PNG and interactive HTML map with per-layer opacity controls

## Notes

For general LLM behavior and workflow rules, see the repository-level `AGENTS.md`.
To start your own analysis, create a new folder in `workflows/` instead of modifying this one.
