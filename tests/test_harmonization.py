"""
Harmonization correctness tests using small synthetic data.

No downloads required — rasters and vectors are generated in memory
using tmp_path fixtures. Tests verify that the core harmonization
functions produce outputs with the correct CRS, extent, and resolution.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.crs import CRS
from rasterio.transform import from_bounds

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.geospatial_harmonizer import build_grid_spec, harmonize_raster, rasterize_vector_to_grid

# Small Colorado test area
TARGET_CRS = "EPSG:4326"
TARGET_EXTENT = (-105.5, 39.5, -104.5, 40.5)
TARGET_RES = 0.01  # ~1 km — small enough to be fast


@pytest.fixture
def synthetic_raster(tmp_path):
    """20×20 GeoTIFF in UTM zone 13N (EPSG:32613) covering the test bbox."""
    from pyproj import Transformer

    t = Transformer.from_crs("EPSG:4326", "EPSG:32613", always_xy=True)
    xmin, ymin = t.transform(TARGET_EXTENT[0], TARGET_EXTENT[1])
    xmax, ymax = t.transform(TARGET_EXTENT[2], TARGET_EXTENT[3])
    transform = from_bounds(xmin, ymin, xmax, ymax, 20, 20)
    path = tmp_path / "synthetic.tif"
    with rasterio.open(
        path, "w", driver="GTiff", height=20, width=20,
        count=1, dtype="float32", crs=CRS.from_epsg(32613), transform=transform,
    ) as dst:
        dst.write(np.random.rand(1, 20, 20).astype("float32"))
    return path


@pytest.fixture
def synthetic_vector(tmp_path):
    """GeoJSON polygon that covers roughly half the test bbox."""
    geojson = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-105.2, 39.7], [-104.8, 39.7],
                    [-104.8, 40.2], [-105.2, 40.2],
                    [-105.2, 39.7],
                ]],
            },
            "properties": {},
        }],
    }
    path = tmp_path / "synthetic.geojson"
    path.write_text(json.dumps(geojson))
    return path


def test_harmonize_raster_output_crs(synthetic_raster, tmp_path):
    grid = build_grid_spec(TARGET_CRS, TARGET_EXTENT, TARGET_RES)
    out = tmp_path / "harmonized.tif"
    harmonize_raster(synthetic_raster, grid, out, verbose=False)
    with rasterio.open(out) as ds:
        assert ds.crs.to_epsg() == 4326, f"Expected EPSG:4326, got {ds.crs}"


def test_harmonize_raster_output_extent(synthetic_raster, tmp_path):
    grid = build_grid_spec(TARGET_CRS, TARGET_EXTENT, TARGET_RES)
    out = tmp_path / "harmonized.tif"
    harmonize_raster(synthetic_raster, grid, out, verbose=False)
    with rasterio.open(out) as ds:
        b = ds.bounds
        tolerance = TARGET_RES * 2
        assert abs(b.left - TARGET_EXTENT[0]) < tolerance, f"Left edge off: {b.left}"
        assert abs(b.bottom - TARGET_EXTENT[1]) < tolerance, f"Bottom edge off: {b.bottom}"
        assert abs(b.right - TARGET_EXTENT[2]) < tolerance, f"Right edge off: {b.right}"
        assert abs(b.top - TARGET_EXTENT[3]) < tolerance, f"Top edge off: {b.top}"


def test_harmonize_raster_output_resolution(synthetic_raster, tmp_path):
    grid = build_grid_spec(TARGET_CRS, TARGET_EXTENT, TARGET_RES)
    out = tmp_path / "harmonized.tif"
    harmonize_raster(synthetic_raster, grid, out, verbose=False)
    with rasterio.open(out) as ds:
        res_x, res_y = ds.res
        assert abs(res_x - TARGET_RES) < TARGET_RES * 0.1, f"X resolution off: {res_x}"
        assert abs(res_y - TARGET_RES) < TARGET_RES * 0.1, f"Y resolution off: {res_y}"


def test_rasterize_vector_output_crs(synthetic_vector, tmp_path):
    grid = build_grid_spec(TARGET_CRS, TARGET_EXTENT, TARGET_RES)
    out = tmp_path / "rasterized.tif"
    rasterize_vector_to_grid(synthetic_vector, grid, out, burn_value=1, verbose=False)
    with rasterio.open(out) as ds:
        assert ds.crs.to_epsg() == 4326, f"Expected EPSG:4326, got {ds.crs}"


def test_rasterize_vector_burn_value_present(synthetic_vector, tmp_path):
    grid = build_grid_spec(TARGET_CRS, TARGET_EXTENT, TARGET_RES)
    out = tmp_path / "rasterized.tif"
    rasterize_vector_to_grid(synthetic_vector, grid, out, burn_value=1, verbose=False)
    with rasterio.open(out) as ds:
        data = ds.read(1)
        assert data.max() == 1, "Burn value 1 not found in rasterized output"
        assert data.min() == 0, "Background (0) not found — unexpected"
