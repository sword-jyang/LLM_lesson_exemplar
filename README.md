# Geospatial Harmonization with LLMs

This repository demonstrates how large language models (LLMs) can be used to harmonize geospatial datasets from user-provided URLs.

Instead of writing custom scripts for each dataset, the workflow is:

1. A user provides dataset URLs
2. The LLM inspects the datasets
3. The LLM decides how to harmonize them (CRS, extent, resolution)
4. Shared Python functions perform the harmonization
5. Outputs and maps are generated

---

## What This Repository Does

The harmonization workflow supports:

* downloading datasets from URLs (direct download, ZIP extraction, OPeNDAP streaming)
* extracting archives (e.g., ZIP files)
* identifying raster and vector inputs
* reprojecting to a common CRS
* clipping to a shared extent
* aligning raster resolution
* optionally rasterizing vector data
* saving harmonized outputs
* generating a static PNG visualization and an interactive HTML map

---

## Quick Start

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the example:

```bash
python examples/colorado_fire_risk/colorado_harmonization.py
```

---

## Example: Colorado Fire Risk

This repository includes a worked example that harmonizes:

* **FBFM40 Fire Behavior Fuel Models** (raster) — Landfire 2024 Scott and Burgan 40-class model
* **MACAv2 Winter Precipitation** (raster) — CCSM4 RCP8.5 Dec–Mar mean 2006–2099, streamed via OPeNDAP
* **MTBS Burned Area Boundaries** (vector) — USGS fire perimeters, kept as vector
* **Microsoft Building Footprints** (vector, rasterized) — Colorado buildings at ~270 m

All datasets are harmonized to:

* CRS: EPSG:4326
* Extent: Colorado bounding box (`-109.05, 36.99, -102.04, 41.01`)
* Resolution: ~270 m (0.00243°)

Goal:

> Visualize fire behavior fuel models, projected winter precipitation, past burned areas, and human infrastructure together to understand fire risk patterns across Colorado.

See `examples/colorado_fire_risk/colorado_harmonization.py`.

---

## How to Use This Repository with an LLM

You can prompt an LLM with something like:

> "Download these datasets, harmonize them to EPSG:4326 over Colorado, and generate a map."

The LLM should:

* download and inspect the datasets
* determine raster vs vector inputs
* ask about resolution mismatches if needed
* reproject and clip datasets
* optionally rasterize vector data
* generate harmonized outputs and a visualization

The expected behavior is defined in `AGENTS.md`.

---

## Repository Structure

```text
src/
  geospatial_harmonizer.py        # core harmonization library — import from here

examples/
  colorado_fire_risk/             # reference example — learn from here, don't modify
    colorado_harmonization.py
    output/                       # generated outputs (data gitignored, viz tracked)

workflows/                        # your analyses go here
  my_project/                     # one folder per project
    my_script.py
    output/                       # generated outputs co-located with the script

docs/                             # website source (MkDocs)
AGENTS.md                         # LLM behavior and workflow rules
requirements.txt
```

**If you are a scientist using this as a template:**
- Read `examples/colorado_fire_risk/colorado_harmonization.py` to understand the pattern
- Create a new folder in `workflows/` for each analysis
- Outputs land in your project's own `output/` folder, next to the script

**If you are an LLM agent:**
- New analyses go in `workflows/<project_name>/`, not in `examples/`
- Set `output_dir=Path(__file__).parent / "output"` — never hardcode paths
- Core library is `src/geospatial_harmonizer.py` — read it before writing harmonization code
- Full rules are in `AGENTS.md`

---

## Python API

Run a harmonization workflow directly:

```python
from pathlib import Path
from src.geospatial_harmonizer import DatasetSpec, ExampleWorkflow, run_harmonization_example

workflow = ExampleWorkflow(
    name="my_workflow",
    datasets=[
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
        ),
    ],
    target_crs="EPSG:4326",
    target_extent=(-109.05, 36.99, -102.04, 41.01),
    target_resolution=0.00243,
    output_dir=Path("./output/my_run"),
    create_visualization=True,
    verbose=True,
)

output_files, interactive_map = run_harmonization_example(workflow)
```

---

## Design Philosophy

* The LLM handles decision-making and orchestration
* The Python code handles geospatial processing
* Examples demonstrate real workflows
* The system is reusable across datasets

---

## Documentation Website

This repository includes a documentation site built with MkDocs.

To preview locally:

```bash
pip install mkdocs mkdocs-material
mkdocs serve
```

Then open `http://127.0.0.1:8000`.

---

## Notes

This repository is designed as a teaching and demonstration tool.

It shows how LLMs can:

* reason about geospatial data
* make harmonization decisions
* orchestrate reusable processing code

rather than requiring custom scripts for each dataset.
