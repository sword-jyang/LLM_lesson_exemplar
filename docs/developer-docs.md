# Developer Documentation

This page is for maintainers and contributors who need to understand how the lesson site and repository are organized. It is not the fastest way to run the lesson. For the short path, use [Start Here](start-here.md). For the guided cloud tutorial, use [Run on CyVerse](cyverse.md).

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
- `docs/slides.md`: native website lesson slideshow.
- `docs/start-here.md`: short quickstart for users with an existing LLM environment.
- `docs/available-models.md`: guidance on model options, endpoint setup, and reproducibility notes.
- `docs/cyverse.md`: full CyVerse tutorial for ESIIL network users.
- `docs/modify.md`: practical guide for adapting the lesson.
- `docs/developer-docs.md`: maintainer and developer reference.
- `docs/examples.md`: current API reference and programmatic usage page.
- `docs/examples/colorado_fire_risk.md`: reference example page.
- `docs/workflows/`: generated or maintained pages for user workflows.

## Documentation principles

Keep the documentation organized by user intent:

- The homepage explains what the lesson is and routes users to the right place.
- Start Here minimizes friction for users who already have an environment.
- Run on CyVerse provides the full guided tutorial with screenshots.
- Modify the Lesson explains how to adapt the lesson safely.
- Developer Documentation records structure, maintenance notes, and reference details.

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
