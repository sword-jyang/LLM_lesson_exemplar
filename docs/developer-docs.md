# Developer Documentation

This page is for maintainers and contributors who need to understand how the lesson site and repository are organized. It is not the fastest way to run the lesson. For the short path, use [Quick Start](start-here.md). For the guided cloud tutorial, use [Run on CyVerse](cyverse.md).

## Repository structure

The current repository structure is:

```text
LLM_lesson_exemplar/
├── docs/                 # MkDocs website content
├── mkdocs.yml            # MkDocs site configuration
├── src/                  # Package source code
├── examples/             # Read-only reference example material
├── workflows/            # User-created harmonization workflows
├── scripts/              # Repository helper scripts
├── tests/                # Tests
├── requirements.txt      # Python dependencies
└── README.md             # Repository overview
```

## Website structure

The website is built with MkDocs Material. The main documentation pages are:

- `docs/index.md`: public-facing homepage.
- `docs/start-here.md`: quick start page for users with an existing LLM environment.
- `docs/slides.md`: native website lesson slideshow.
- `docs/available-models.md`: guidance on model options, endpoint setup, and reproducibility notes.
- `docs/ai-infrastructure/llm-hosting-data-centers.md`: explanation of LLM hosting, data centers, and sovereignty.
- `docs/cyverse.md`: full CyVerse tutorial for ESIIL network users.
- `docs/developer-docs.md`: maintainer and developer reference.
- `docs/examples.md`: current API reference and programmatic usage page.
- `docs/examples/colorado_fire_risk.md`: reference example page.
- `docs/workflows/`: generated or maintained pages for user workflows.

## Documentation principles

Keep the documentation organized by user intent:

- The homepage explains what the lesson is and routes users to the right place.
- Quick Start minimizes friction for users who already have an environment.
- The LLM Guide section groups conceptual teaching material, model choices, hosting context, and developer notes.
- The Workflows section is populated from workflow docs and output folders by `hooks.py`.
- Developer Documentation records structure, maintenance notes, reference details, and modification guidance.

Avoid mixing all of these purposes into one long page.

## API keys and credentials

Never commit API keys, tokens, or credentials. Documentation may show environment variable names and placeholder values, but it should not include real secrets.

Use examples like:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Updating the site

When updating the website:

1. Edit Markdown files in `docs/`.
2. Update `mkdocs.yml` if navigation changes.
3. Keep screenshots in `docs/assets/screenshots/`.
4. Prefer relative links between documentation pages.
5. Run the local MkDocs preview if available:

```bash
mkdocs serve
```

## Adding screenshots

The CyVerse tutorial is the main place for screenshots. Store screenshots in:

```text
docs/assets/screenshots/
```

Use descriptive filenames such as:

```text
cyverse-launch.png
cyverse-settings.png
cyverse-terminal.png
cyverse-outputs.png
```

Do not include screenshots that show API keys, tokens, private URLs, or user credentials.

## Modifying the lesson

This section is for users who have already run the reference example and want to adapt it. The most common modifications are changing the prompt, changing the data sources, changing the model provider, changing the output format, or adding a new example.

The guiding principle is simple: keep each example self-contained, inspectable, and reproducible. A user should be able to open an example folder or page and understand what data it used, what the model was asked to do, what transformations were applied, and what output was produced.

### How to approach a modification

Before changing code, identify which part of the lesson you want to modify:

- Change the prompt if the model is being asked the wrong question.
- Change the data sources if the example should use a different place, hazard, ecosystem, or environmental variable.
- Change the model configuration if you need a different provider, endpoint, or model behavior.
- Change the output format if the result should become a map, table, report, JSON file, or notebook cell.
- Add a new example if the change is large enough that future users should be able to run it independently.

### Change the prompt

Find the prompt text used by the reference example. In this repository, the Colorado reference prompt is documented in `docs/examples/colorado_fire_risk.md` and implemented in `examples/colorado_fire_risk/colorado_harmonization.py`.

When editing a prompt, keep three things explicit:

1. What role the model is playing.
2. What inputs the model should use.
3. What output format the model should return.

A good prompt for this lesson should not simply ask the model to produce an answer. It should ask the model to produce an inspectable plan or structured output that a human can check.

### Change the data sources

When changing the data, document the source, spatial coverage, temporal coverage, format, and any access constraints. Environmental data workflows become difficult to debug when data assumptions are implicit.

For each new data source, record:

- source name,
- access URL or citation,
- data type,
- coordinate reference system if relevant,
- spatial resolution if relevant,
- temporal resolution if relevant,
- and any preprocessing needed before analysis.

The existing reference example is in `examples/colorado_fire_risk/`. User-created workflows live in `workflows/`, with the Utah workflow in `workflows/utah_fire_risk/` as the current user workflow example.

### Change the model provider or endpoint

Keep model configuration separate from the scientific logic whenever possible. API keys and endpoints should be provided through environment variables or local configuration files that are not committed to GitHub.

Do not hard-code credentials in tracked files.

If the lesson supports multiple model providers, document the required environment variables and any differences in output format or model behavior.

### Change the outputs

Outputs should be easy to inspect. Prefer outputs that make the model's reasoning and the geospatial workflow visible, such as:

- a structured harmonization plan,
- a table of data sources,
- a map or figure,
- a reproducible script or notebook cell,
- and a short written summary.

Avoid outputs that only give a final answer without showing the assumptions used to produce it.

### Add a new example

If you add a new example, keep it parallel to the reference example. The new example should include:

- a short purpose statement,
- required inputs,
- the prompt or prompt template,
- the run command,
- expected outputs,
- and a short explanation of how to inspect the result.

For a new website-facing workflow, add the script under `workflows/<project_name>/`, write outputs to `workflows/<project_name>/output/`, and add a matching page under `docs/workflows/<project_name>.md`.

### What not to change casually

Do not change shared package code, dependency files, or workflow internals unless you are intentionally doing developer work and have coordinated with the repo maintainers. For normal lesson adaptation, prefer adding a new example or editing documentation-facing files rather than changing shared infrastructure.

## Pull request checklist

Before opening a pull request for documentation changes, check that:

- the site builds locally,
- navigation links work,
- no credentials are included,
- screenshots are readable,
- quickstart commands match the current repo,
- and the CyVerse tutorial matches the current ESIIL training environment.

## API Reference

Preserve the existing API Reference setup. Do not remove API reference generation unless it is already broken and can be fixed only inside `docs/` or `mkdocs.yml`.

The current API reference is maintained at [API Reference](examples.md). It documents the harmonization module, key dataclasses, supported data types, and programmatic usage.

## Styling updates

The site uses `docs/stylesheets/extra.css` for custom ESIIL styling. Keep custom styles restrained and focused on:

- a clean link grid on the homepage,
- slide-like sections for the lesson slideshow,
- better spacing around cards or buttons,
- ESIIL color accents,
- readable screenshot presentation.

Do not make the site visually busy.
