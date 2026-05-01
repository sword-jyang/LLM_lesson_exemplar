# Start Here

This page is the fast path. It is for users who already have a working Python environment and access to an LLM API. If you need a fully guided cloud setup, use the [Run on CyVerse](cyverse.md) tutorial instead.

## What this lesson does

This lesson uses a small geospatial example to show how a large language model can help organize environmental data sources, identify harmonization steps, and produce a reproducible analysis workflow. The goal is not to hide the analysis behind AI. The goal is to make the assumptions, transformations, and outputs easier to inspect.

## Clone the repository

```bash
git clone https://github.com/CU-ESIIL/LLM_lesson_exemplar.git
cd LLM_lesson_exemplar
```

## Create an environment

Use the environment approach that fits your system. For example:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If the repository includes a requirements.txt, environment.yml, or pyproject.toml, prefer the maintained dependency path already present in the repo.

## Add your API key

Set the environment variable required by the current model provider used in the lesson. For example:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

Do not commit API keys, tokens, or credentials to the repository.

## Run the reference example

Run the existing reference workflow from the repository:

```bash
python examples/colorado_fire_risk/colorado_harmonization.py
```

The example should create inspectable outputs in `examples/colorado_fire_risk/output/`.

## What to check

After the workflow runs, check three things:

1. The input sources were read correctly.
2. The harmonization plan is explicit enough for a human to inspect.
3. The final outputs include both the geospatial result and a short explanation of what the workflow did.

## Where to go next

If you need a step-by-step cloud setup, go to [Run on CyVerse](cyverse.md).

If you want to adapt this lesson to a different dataset, prompt, or model, go to [Modify the Lesson](modify.md).

If you are maintaining the package or site, go to [Developer Documentation](developer-docs.md).
