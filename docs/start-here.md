![Run Locally banner with a speed gauge and checklist.](assets/images/heroes/quick-start-hero.png){ .page-hero }

# Run Locally

This page is for learners who want to run the lesson on their own computer instead of launching the CyVerse cloud environment. Use this path if you already have a working terminal, Python, Git, and access to an LLM API key or OpenAI-compatible model endpoint.

If you want the fully guided workshop environment, use [Run on CyVerse](cyverse.md) instead.

## What you will run

This lesson uses a Colorado fire risk example to show how a large language model can help organize environmental data sources, identify harmonization steps, and produce a reproducible analysis workflow. The goal is not to hide the analysis behind AI. The goal is to make the assumptions, transformations, and outputs easier to inspect.

If you want more context on why harmonization is necessary before analysis, see [What Is a Data Harmonizer?](data-harmonizer.md).

The local run will:

1. Clone the lesson repository.
2. Create a local Python environment.
3. Install the required packages.
4. Add model credentials safely.
5. Run the reference Colorado example.
6. Inspect the generated outputs.

## Before you begin

Make sure you have:

- Git installed.
- Python 3 available from your terminal.
- Permission to install Python packages.
- An LLM API key or OpenAI-compatible endpoint if you plan to run model-assisted parts of the workflow.
- Enough disk space for downloaded geospatial data and generated outputs.

Check Git and Python:

```bash
git --version
python --version
```

If `python` does not work but `python3` does, use `python3` in the commands below.

## Step 1: Clone the repository

Open a terminal and move to the folder where you want the lesson repository to live. Then run:

```bash
git clone https://github.com/CU-ESIIL/LLM_lesson_exemplar.git
cd LLM_lesson_exemplar
```

For a deeper explanation of why this lesson centers the repository as the unit of AI-assisted scientific work, see [Agents and Systems](agents-and-systems.md).

Confirm that you are in the repository:

```bash
ls
```

You should see files and folders such as `README.md`, `requirements.txt`, `docs/`, `examples/`, `src/`, and `workflows/`.

## Step 2: Create a local Python environment

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell, activation usually looks like:

```powershell
.\.venv\Scripts\Activate.ps1
```

When the environment is active, your terminal prompt may show `(.venv)`.

## Step 3: Install dependencies

Install the packages used by the lesson:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

This installs the documentation tools, geospatial libraries, plotting libraries, STAC support, NetCDF/OPeNDAP tools, and testing utilities used by the example workflow.

If dependency installation fails, read the error message carefully. Geospatial Python packages sometimes depend on local system libraries, especially on older machines or managed computers.

## Step 4: Add model credentials safely

Some parts of the lesson can run as ordinary Python geospatial processing. Model-assisted workflows require an API key or endpoint.

For an OpenAI-compatible setup, set your API key in the same terminal session:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

If your provider gives you a custom endpoint and model name, set those too:

```bash
export OPENAI_BASE_URL="https://example-endpoint.invalid/v1"
export MODEL_NAME="example-model-name"
```

Replace the example values with the values from your model provider or instructor.

Do not commit API keys, tokens, or credentials to the repository.

If you want a deeper comparison of model options and tradeoffs before choosing a model, see [Available Models](available-models.md).

Check whether your key is set without printing the key itself:

```bash
python -c "import os; print('OPENAI_API_KEY is set' if os.getenv('OPENAI_API_KEY') else 'OPENAI_API_KEY is missing')"
```

## Step 5: Run the reference example

Run the Colorado fire risk example from the repository root:

```bash
python examples/colorado_fire_risk/colorado_harmonization.py
```

The script downloads and harmonizes:

- FBFM40 fire behavior fuel models,
- MACAv2 winter precipitation,
- MTBS burned area boundaries,
- and Microsoft building footprints.

All layers are harmonized to a common CRS, extent, and resolution for the Colorado example.

## Step 6: Inspect the outputs

Outputs are written to:

```text
examples/colorado_fire_risk/output/
```

List the output files:

```bash
ls examples/colorado_fire_risk/output/
```

Expected outputs may include:

- harmonized raster or vector files,
- `harmonized_visualization.png`,
- `harmonized_visualization.html`,
- intermediate files or logs,
- and a short summary if the workflow generated one.

Open the PNG to check the static visualization. Open the HTML file in a browser to inspect the interactive map.

## Step 7: Modify or create a workflow

After the reference example works locally, use the repository structure for your own workflow. User-created analyses should go under `workflows/`, not `examples/`.

If you want to use your own datasets, start with [Bring Your Own Data](provide-your-own-data-sources.md) so the workflow receives direct download URLs.

If you want to adapt the lesson prompt, model, data sources, or outputs, continue to [Modify the Lesson](modify.md).

## Common issues

### Python is not found

Try:

```bash
python3 --version
```

If `python3` works, use `python3` instead of `python` when creating the environment.

### The virtual environment is not active

Activate it again from the repository root:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### A package is missing

Confirm that you installed dependencies inside the active virtual environment:

```bash
which python
python -m pip list
```

Then reinstall:

```bash
python -m pip install -r requirements.txt
```

### The workflow cannot download data

Check your internet connection and try the command again. Some institutional networks block large downloads or streaming endpoints.

### The model key is missing

Set the key in the same terminal session where you run the workflow:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

Then check without printing the secret:

```bash
python -c "import os; print('OPENAI_API_KEY is set' if os.getenv('OPENAI_API_KEY') else 'OPENAI_API_KEY is missing')"
```

## Where to go next

If you need the full cloud setup, go to [Run on CyVerse](cyverse.md).

If you are following the workshop sequence, keep the [Lesson Slides](slides.md) open alongside these steps.

If you are maintaining the package or site, go to [Developer Documentation](developer-docs.md).
