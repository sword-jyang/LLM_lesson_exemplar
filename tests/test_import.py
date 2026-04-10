"""Smoke tests — verify the core library imports cleanly and public API is intact."""

import sys
from pathlib import Path

# Ensure repo root is on sys.path so `src` is importable
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_import_geospatial_harmonizer():
    from src.geospatial_harmonizer import (
        DatasetSpec,
        ExampleWorkflow,
        run_harmonization_example,
        harmonize_raster,
        rasterize_vector_to_grid,
        create_visualization,
        create_interactive_visualization,
        build_grid_spec,
        download_file,
    )


def test_datasetspec_defaults():
    from src.geospatial_harmonizer import DatasetSpec

    ds = DatasetSpec(name="test", url="http://example.com/data.tif", data_type="raster")
    assert ds.resampling_method is None
    assert ds.rasterize is False
    assert ds.burn_value == 1
    assert ds.data_type == "raster"


def test_datasetspec_vector():
    from src.geospatial_harmonizer import DatasetSpec

    ds = DatasetSpec(
        name="boundaries",
        url="http://example.com/bounds.zip",
        data_type="vector",
        rasterize=True,
        burn_value=5,
    )
    assert ds.data_type == "vector"
    assert ds.rasterize is True
    assert ds.burn_value == 5
