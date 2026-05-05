# Modify the Lesson

This page is for users who have already run the reference example and want to adapt it. The most common modifications are changing the prompt, changing the data sources, changing the model provider, changing the output format, or adding a new example.

The guiding principle is simple: keep each example self-contained, inspectable, and reproducible. A user should be able to open an example folder or page and understand what data it used, what the model was asked to do, what transformations were applied, and what output was produced.

## How to approach a modification

Before changing code, identify which part of the lesson you want to modify:

- Change the prompt if the model is being asked the wrong question.
- Change the data sources if the example should use a different place, hazard, ecosystem, or environmental variable.
- Change the model configuration if you need a different provider, endpoint, or model behavior.
- Change the output format if the result should become a map, table, report, JSON file, or notebook cell.
- Add a new example if the change is large enough that future users should be able to run it independently.

## Change the prompt

Find the prompt text used by the reference example. In this repository, the Colorado reference prompt is documented in `docs/examples/colorado_fire_risk.md` and implemented in `examples/colorado_fire_risk/colorado_harmonization.py`.

For a deeper explanation of how agents operate within structured repositories, see [Agents and Systems](agents-and-systems.md).

When editing a prompt, keep three things explicit:

1. What role the model is playing.
2. What inputs the model should use.
3. What output format the model should return.

A good prompt for this lesson should not simply ask the model to produce an answer. It should ask the model to produce an inspectable plan or structured output that a human can check.

## Change the data sources

When changing the data, document the source, spatial coverage, temporal coverage, format, and any access constraints. Environmental data workflows become difficult to debug when data assumptions are implicit.

If you want more context on why these alignment decisions matter, see [What Is a Data Harmonizer?](data-harmonizer.md).

For each new data source, record:

- source name,
- access URL or citation,
- data type,
- coordinate reference system if relevant,
- spatial resolution if relevant,
- temporal resolution if relevant,
- and any preprocessing needed before analysis.

The existing reference example is in `examples/colorado_fire_risk/`. User-created workflows live in `workflows/`, with the Utah workflow in `workflows/utah_fire_risk/` as the current user workflow example.

## Change the model provider or endpoint

Keep model configuration separate from the scientific logic whenever possible. API keys and endpoints should be provided through environment variables or local configuration files that are not committed to GitHub.

If you want a deeper comparison of model options and tradeoffs, see [Available Models](available-models.md).

Do not hard-code credentials in tracked files.

If the lesson supports multiple model providers, document the required environment variables and any differences in output format or model behavior. For more context on where hosted models run and why that matters, see [LLM Hosting and Data Centers](ai-infrastructure/llm-hosting-data-centers.md).

## Change the outputs

Outputs should be easy to inspect. Prefer outputs that make the model's reasoning and the geospatial workflow visible, such as:

- a structured harmonization plan,
- a table of data sources,
- a map or figure,
- a reproducible script or notebook cell,
- and a short written summary.

Avoid outputs that only give a final answer without showing the assumptions used to produce it.

## Add a new example

If you add a new example, keep it parallel to the reference example. The new example should include:

- a short purpose statement,
- required inputs,
- the prompt or prompt template,
- the run command,
- expected outputs,
- and a short explanation of how to inspect the result.

For a new website-facing workflow, add the script under `workflows/<project_name>/`, write outputs to `workflows/<project_name>/output/`, and add a matching page under `docs/workflows/<project_name>.md`.

## What not to change casually

Do not change shared package code, dependency files, or workflow internals unless you are intentionally doing developer work and have coordinated with the repo maintainers. For normal lesson adaptation, prefer adding a new example or editing documentation-facing files rather than changing shared infrastructure.

## Next steps

If your changes are only for teaching or demonstration, document them clearly in the relevant example page.

If your changes alter package behavior, dependencies, or deployment, read [Developer Documentation](developer-docs.md) before opening a pull request.

Because of the scope constraint for this task, this page explains how to modify the repo, but this documentation update itself does not modify non-website files.
