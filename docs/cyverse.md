# Run on CyVerse

This tutorial is for ESIIL network users who want to run the lesson in a CyVerse cloud environment. You will launch a working environment, connect it to GitHub, clone the lesson repository, add your LLM API credentials safely, and run the reference example.

If you already have a working local environment and API key, you may prefer the shorter [Start Here](start-here.md) page.

## What you will do

In this tutorial, you will:

1. Launch a CyVerse analysis environment.
2. Open a terminal or notebook session.
3. Connect the environment to GitHub.
4. Clone the lesson repository.
5. Configure your LLM API key without committing it to GitHub.
6. Run the reference example.
7. Check the outputs.

## Before you begin

You need:

- Access to the ESIIL/CyVerse environment being used for this training.
- A GitHub account.
- Access to an LLM API key or an ESIIL-provided model endpoint.
- Permission to use the selected model for this lesson.

Never paste API keys into public files, notebooks that will be committed, screenshots, or GitHub issues.

## Step 1: Launch the CyVerse environment

Open the CyVerse Discovery Environment or the ESIIL-provided CyVerse launch link for this lesson.

<!-- Screenshot needed: CyVerse launch page or application tile. Suggested path: docs/assets/screenshots/cyverse-launch.png -->

Select the application or image recommended for this lesson. Use the default settings unless your instructor or project lead gives you different settings.

<!-- Screenshot needed: launch settings screen. Suggested path: docs/assets/screenshots/cyverse-settings.png -->

Start the analysis and wait for the environment to become available.

## Step 2: Open the working session

When the environment is ready, open the interactive session. Depending on the image, this may be JupyterLab, RStudio, VS Code, or a terminal-based interface.

<!-- Screenshot needed: open analysis/session button. Suggested path: docs/assets/screenshots/cyverse-open-session.png -->

Open a terminal inside the session.

<!-- Screenshot needed: terminal inside the running environment. Suggested path: docs/assets/screenshots/cyverse-terminal.png -->

## Step 3: Connect to GitHub

In the terminal, confirm that Git is available:

```bash
git --version
```

Then clone the repository:

```bash
git clone https://github.com/CU-ESIIL/LLM_lesson_exemplar.git
cd LLM_lesson_exemplar
```

If you plan to modify the lesson and push changes, fork the repository first or clone your own copy.

## Step 4: Create or activate the Python environment

Use the dependency path supported by the repository. Common options include:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If the repository includes a different maintained environment file, use that instead.

## Step 5: Add your LLM API key safely

Set your API key as an environment variable in the terminal session:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

Do not paste your key into a tracked Python file, Markdown file, notebook output, or screenshot.

If the training uses an ESIIL-provided model endpoint instead of an individual key, follow the endpoint instructions provided by the training team and document the environment variable names here.

## Step 6: Run the reference example

Run the reference workflow:

```bash
python examples/colorado_fire_risk/colorado_harmonization.py
```

The run should produce files that can be inspected, shared, or adapted.

## Step 7: Check the outputs

Look for the generated outputs in `examples/colorado_fire_risk/output/`. The expected output should include:

- a record of the data sources used,
- a harmonization plan or explanation,
- a geospatial output or visualization,
- and a short written summary of the result.

<!-- Screenshot needed: output files or rendered result. Suggested path: docs/assets/screenshots/cyverse-outputs.png -->

## Common issues

### The API key is not found

Confirm that the environment variable is set in the same terminal or session where you are running the workflow.

```bash
echo $OPENAI_API_KEY
```

If this prints nothing, set the key again. Do not print or share the full key in screenshots or support requests.

### The repository did not clone

Check that the environment has internet access and that GitHub is reachable. If you are cloning a fork or private repository, confirm that your GitHub credentials are available in the session.

### A package is missing

Confirm that you activated the environment and installed the repository dependencies. If the repo provides a preferred installation command, use that command rather than installing packages one by one.

### The workflow runs but the output looks wrong

Check the input URLs, the harmonization plan, and any warnings printed during the run. The goal of this lesson is to keep the workflow inspectable, so the first debugging step is to read the generated plan and compare it to the expected data types.

## Next steps

To change the example, prompt, model, or outputs, continue to [Modify the Lesson](modify.md).
