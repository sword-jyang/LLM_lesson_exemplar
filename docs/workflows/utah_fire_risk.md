# Utah Fire Risk

Harmonizes fire behavior fuel models, winter precipitation projections, historical burned areas, and building footprints for Utah to assess fire risk factors.

---

## Prompt

> "recreate the colorado fire risk example but for utah in epsg:5070"

---

## Datasets

| Layer | Type | URL |
|---|---|---|
| FBFM40 Fuel Models | raster | https://www.landfire.gov/data-downloads/CONUS_LF2024/LF2024_FBFM40_CONUS.zip |
| Winter Precipitation (CCSM4 RCP8.5) | raster | http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_macav2metdata_pr_CCSM4_r6i1p1_rcp85_2006_2099_CONUS_monthly.nc |
| MTBS Burned Areas | vector | https://edcintl.cr.usgs.gov/downloads/sciweb1/shared/MTBS_Fire/data/composite_data/burned_area_extent_shapefile/mtbs_perimeter_data.zip |
| Building Footprints | vector | https://minedbuildings.z5.web.core.windows.net/legacy/usbuildings-v2/Utah.geojson.zip |

**Target grid:** EPSG:5070 · extent (-1581748.3, 1629453.6, -1085516.0, 2250700.3) · resolution 270 m

---

## What Was Harmonized

- FBFM40 fuel models resampled using nearest-neighbor (categorical data)
- MACAv2 winter precipitation averaged over Dec–Mar months, resampled using bilinear interpolation
- MTBS burned area boundaries kept as vector, clipped to Utah state boundary
- Building footprints rasterized to presence/absence at 270 m resolution
- All outputs clipped to actual Utah state polygon (not just bounding box)

---

## Result

![Harmonized visualization for utah_fire_risk](../assets/workflows/utah_fire_risk/harmonized_visualization.png)

---

## Reproduce It

From the repo root:

```bash
python workflows/utah_fire_risk/utah_harmonization.py
```

Outputs are saved to `workflows/utah_fire_risk/output/`.

---

## Source

Script: `workflows/utah_fire_risk/utah_harmonization.py`
