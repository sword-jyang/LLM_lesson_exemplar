# Geospatial Harmonization with LLMs

A template for using large language models to harmonize environmental science datasets from user-provided URLs.

[See Example](examples.md){ .md-button .md-button--primary }
[View Repository](https://github.com/CU-ESIIL/LLM_lesson_exemplar){ .md-button }

<div class="grid cards" markdown>

- **Reference Example**

  ---

  The Colorado fire risk example shows how to harmonize raster, vector, and climate model data into a common grid and visualization.

- **Your Workflows**

  ---

  Create your own analysis in `workflows/`. Each project is self-contained — script and outputs in one folder.

- **Core Library**

  ---

  `src/geospatial_harmonizer.py` handles downloads, reprojection, resampling, rasterization, and visualization. Import it, don't modify it.

</div>

!!! note "Template usage"
    Clone or fork this repository, then add your own analysis scripts to `workflows/`. The `examples/` directory is read-only reference material.
