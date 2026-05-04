# Run on CyVerse

![ESIIL, CyVerse, AI Infrastructure, and AI Verde hero banner.](assets/images/cyverse/cyverse-hero-banner.png){ .page-hero .cyverse-hero }

This tutorial is for ESIIL network learners who want to run the lesson in a CyVerse cloud environment rather than on their own laptop. CyVerse gives you a browser-based workspace with compute, storage, and a terminal already available, which is helpful when you do not want to install everything locally or when you want the whole group to work in the same environment.

By the end of this page, you will have launched a CyVerse analysis, opened a working session, connected the session to GitHub, cloned the lesson repository, added your LLM credentials safely, run the reference workflow, and checked the output files.

If you already have Python, Git, and an LLM API key working on your own computer, you may prefer the shorter [Quick Start](start-here.md) page.

!!! warning "Do not put secrets in screenshots"
    This page includes workshop screenshots. Before adding or updating screenshots, remove or blur usernames, tokens, API keys, private file paths, email addresses, and anything else that should not be public.

## What you will do

You will move through the workflow in four phases. First, you will launch the CyVerse environment. Second, you will open the interactive workspace and terminal. Third, you will connect the workspace to the lesson repository on GitHub. Fourth, you will configure the model access and run the example workflow.

This page is written as a click-by-click guide. The exact button names in CyVerse may change slightly over time, but the workflow should remain the same: log in, launch the correct app, open the running analysis, use a terminal, clone the repository, install dependencies, set credentials, and run the lesson.

## Before you begin

Make sure you have the following before starting:

- A CyVerse account with access to the Discovery Environment or the ESIIL-provided training environment.
- A GitHub account.
- Access to the lesson repository or your fork of it.
- An LLM API key, an ESIIL-provided model endpoint, or instructor-provided credentials for the training.
- Enough time to wait for the cloud environment to launch. The first launch can take several minutes.

For the current workshop:

- You will manually clone the repository for now. The training team may automate this later.
- During testing, the instructor may provide shared API credentials privately. At the summit, participants may use their own credentials or the credentials provided for that event.
- If something does not work, tell the training team what happened. Many issues can be fixed by updating the repository instructions or the `AGENTS.md` guidance.

!!! danger "Protect your API key"
    Never paste an API key into a public Markdown file, notebook cell that will be committed, GitHub issue, screenshot, slide, chat message, or shared document. Use environment variables, an ignored `.env` file, or the secure settings field in the training interface. When asking for help, describe the error without sharing the secret value.

## Step 1: Log in to CyVerse

1. Open [https://user.cyverse.org](https://user.cyverse.org) in your browser, or open the ESIIL-provided launch link for this training.
2. Click **Log in**.
3. Sign in with your CyVerse account.
4. Open the **Discovery Environment**.
5. Confirm that you land on the CyVerse dashboard or Discovery Environment home screen.

![Screenshot showing the CyVerse Discovery Environment launch card.](assets/images/cyverse/cyverse-01-login.png)

*CyVerse Discovery Environment launch card.*

![Screenshot showing the CyVerse Discovery Environment dashboard entry point.](assets/images/cyverse/cyverse-02-dashboard.png)

*CyVerse dashboard entry point after login.*

If you cannot log in, stop here and ask the training team to confirm that your account has access to the correct CyVerse resources.

## Step 2: Find the lesson application

The training team should provide the name of the CyVerse app, image, or launch link for this lesson. Use that exact app when possible so your environment matches the rest of the group.

For the Innovation Summit training, use:

- **App name:** `ESIIL_OASIS`
- **Version:** `Innovation_Summit_2026`

To find the app:

1. In CyVerse, open the **Apps** or **Applications** area.
2. Use the search box to search for `ESIIL_OASIS`.
3. Select the app for this lesson.
4. Read the short app description to confirm that it is the correct environment.

![Screenshot showing the ESIIL OASIS CyVerse app card selected in the app search results.](assets/images/cyverse/cyverse-03-app-search.png)

*Finding the `ESIIL_OASIS` lesson app in CyVerse.*

If your instructor gives you a direct launch link, use that link instead of searching manually.

## Step 3: Launch the analysis

After selecting the app, CyVerse will ask for launch settings. Use the default settings unless the instructor gives different values.

1. Click **Launch**, **Run**, or the equivalent button for the selected app.
2. Confirm that the version is `Innovation_Summit_2026`.
3. Give the analysis a recognizable name, such as `llm-lesson-yourname`.
4. Confirm the output folder or working directory if CyVerse asks for one.
5. Leave CPU, memory, and advanced resource settings at their defaults unless the instructor tells you otherwise.
6. Click the final **Launch Analysis** or **Run** button.

![Screenshot showing the CyVerse launch settings page for the ESIIL OASIS app.](assets/images/cyverse/cyverse-04-launch-settings.png)

*Launch settings for the CyVerse analysis.*

CyVerse will now start the environment. This can take a few minutes. You may see the analysis move through statuses such as submitted, queued, running, or ready.

![Screenshot showing the CyVerse analysis status page with a Go to Analysis button.](assets/images/cyverse/cyverse-05-analysis-status.png)

*Analysis status while the environment starts.*

## Step 4: Open the interactive session

When the analysis is ready, open the interactive workspace.

1. Go to your running analyses or notifications.
2. Find the analysis you just launched.
3. Click **Go to Analysis**, **Open**, **Launch**, **Access**, or the link provided by CyVerse.
4. For the `ESIIL_OASIS` app, launch **VS Code** from the analysis interface.
5. The session will open as a browser-based coding environment.

For this lesson, the most important tool is the terminal. In VS Code, open a terminal with **Terminal -> New Terminal**. In JupyterLab, open a terminal with **File -> New -> Terminal**, or by clicking the terminal icon in the launcher.

After VS Code opens, use **File -> Open Folder** and navigate to:

```text
/home/joyvan/work/
```

This is the working folder used in the current training image.

![Screenshot showing the VS Code launcher inside the CyVerse workspace.](assets/images/cyverse/cyverse-06-open-jupyterlab.png)

*Opening the interactive VS Code workspace.*

![Screenshot showing the New Terminal menu item inside VS Code.](assets/images/cyverse/cyverse-07-terminal.png)

*Opening a terminal inside the CyVerse workspace.*

## Step 5: Confirm Git and Python are available

In the terminal, run:

```bash
git --version
python --version
pwd
```

You should see a Git version, a Python version, and your current working directory. The exact versions do not need to match everyone else's as long as the lesson environment was launched from the correct app.

If `python` does not work, try:

```bash
python3 --version
```

If Git or Python is missing, confirm that you launched the correct CyVerse app.

## Step 6: Clone the lesson repository

Move to a working directory where you want the lesson files to live. For the current CyVerse training image, the working folder may be:

```bash
cd /home/joyvan/work/
```

If that folder does not exist, use your home directory:

```bash
cd ~
```

Clone the lesson repository:

```bash
git clone https://github.com/CU-ESIIL/LLM_lesson_exemplar.git
cd LLM_lesson_exemplar
```

Confirm that you are inside the repository:

```bash
ls
```

You should see files such as `README.md`, `docs/`, `mkdocs.yml`, `examples/`, or lesson-related folders.

If you used the VS Code file browser to open `/home/joyvan/work/`, navigate into the `LLM_lesson_exemplar` folder after cloning. This is the folder you will use for Cline and terminal commands.

![Screenshot showing the terminal command to clone the lesson repository from GitHub.](assets/images/cyverse/cyverse-08-github-clone.png)

*Cloning the lesson repository from GitHub.*

If you plan to edit the lesson and push changes back to GitHub, fork the repository first and clone your fork instead. For simply running the lesson, cloning the public repository is enough.

## Step 7: Create or activate the Python environment

Use the dependency path maintained by the repository. Start with the standard virtual environment approach unless the repository has a different documented setup.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If `python` does not work but `python3` does, use:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

When the environment is active, your terminal prompt may show `(.venv)` at the beginning of the line.

If the repository includes a Conda environment file, such as `environment.yml`, and the instructor tells you to use Conda, use the instructor-provided command instead. Do not mix Conda and virtual environment setup unless you know why you are doing it.

## Step 8: Add model credentials safely

Most LLM workflows need either an API key or a model endpoint. The safest pattern for a workshop is to store the key in an environment variable for the current terminal session or paste it into the secure model settings field in the VS Code extension.

For OpenAI-compatible workflows in a terminal, use:

```bash
export OPENAI_API_KEY="paste-your-key-here"
```

If the training uses the CyVerse-hosted model endpoint, the instructor may give you values such as:

```bash
export OPENAI_API_KEY="paste-your-key-here"
export OPENAI_BASE_URL="https://llm-api.cyverse.ai/v1"
export MODEL_NAME="nrp/qwen3-small"
```

Do not copy example key values from a slide, screenshot, or shared note unless the instructor tells you to. Replace them with the values for the training.

To check whether the key is set without printing the key itself, run:

```bash
python -c "import os; print('OPENAI_API_KEY is set' if os.getenv('OPENAI_API_KEY') else 'OPENAI_API_KEY is missing')"
```

!!! warning "Do not commit secrets"
    Do not put your API key directly in a Python script, notebook, Markdown file, or Git-tracked configuration file. Do not take screenshots that show the key. Do not run commands that print the full key into a terminal that will be screenshotted or shared.

### Optional: configure Cline in VS Code

If the workshop uses Cline inside VS Code, open Cline from the left sidebar and choose **Bring my own API key**. Use the instructor-provided credentials.

For the CyVerse-hosted endpoint, the settings may look like:

| Setting | Value |
|---|---|
| API Provider | OpenAI Compatible |
| Base URL | `https://llm-api.cyverse.ai/v1` |
| OpenAI Compatible API Key | Provided privately by the instructor |
| Model ID | One of the supported model IDs |

Supported model IDs for this training may include:

- `nrp/minimax-m2`
- `nrp/glm-4.7`
- `nrp/qwen3-small`
- `js2/gpt-oss-120b`
- `nrp/kimi`
- `nrp/qwen3`
- `js2/llama-4-scout`

Some models may be slower than others. If the model is doing poorly, ask the training team for help, record what happened, and try another model. Some models also expose a reasoning setting that can be increased in the interface.

!!! note "If Cline asks for Sonnet"
    Cline may strongly recommend a default Anthropic model such as Sonnet. For this training, ignore that recommendation and use the CyVerse/OpenAI-compatible endpoint supplied by the instructor. If Cline asks you to confirm, click **Proceed Anyway**.

If the model is doing poorly:

1. Tell the training team what happened. It is often something that can be fixed in the repository instructions or `AGENTS.md`.
2. Try increasing **Model Reasoning** in the Cline settings if the selected model exposes that option.
3. Record what happened and try another model from the list.

![Screenshot showing Cline configured with an OpenAI-compatible provider, CyVerse base URL, hidden API key, and model ID.](assets/images/cyverse/cyverse-09-env-file.png)

*Safe model credential setup with the API key hidden.*

## Step 9: Run the reference workflow

From the repository root, run the reference example. Use the command maintained by the repository. If the current repository command is still the Colorado fire risk example, use:

```bash
python examples/colorado_fire_risk/colorado_harmonization.py
```

If the repository has moved to a different workflow command, update this page to match the current working example.

As the workflow runs, watch the terminal output. You are looking for three things:

1. The script starts without import errors.
2. The model call succeeds or the lesson uses the configured model endpoint.
3. The workflow writes output files to the expected output folder.

![Screenshot showing a Cline chat interaction while the workflow runs.](assets/images/cyverse/cyverse-10-run-workflow.png)

*Running or testing the agentic workflow from the CyVerse workspace.*

You can also test the app through Cline's chat. Ask it to harmonize your data. Your request must include:

- projection,
- extent,
- resolution,
- and URLs to download the data from.

The LLM should produce:

- a new folder under `workflows/`,
- an `output/` folder inside that workflow,
- the Python script used to harmonize the data,
- processed versions of each dataset,
- a PNG image showing the datasets side-by-side,
- and an interactive HTML map.

Be patient. It can be slow to generate the outputs, and the HTML file can take up to 10 minutes.

## Step 10: Check the outputs

Look for generated outputs in the workflow output folder. For the Colorado fire risk example, start with:

```bash
ls examples/colorado_fire_risk/output/
```

The expected outputs may include:

- a record of the data sources used,
- a harmonization plan or explanation,
- a geospatial output or visualization,
- logs or intermediate files,
- and a short written summary of the result.

Open small text outputs directly in the terminal when they exist:

```bash
cat examples/colorado_fire_risk/output/summary.md
```

If the output is a map, image, notebook, or HTML file, open it from the file browser in JupyterLab or VS Code, or download it from CyVerse.

![Screenshot showing the repository folder in the VS Code file browser.](assets/images/cyverse/cyverse-11-output-files.png)

*Checking repository and output files in the workspace file browser.*

## Step 11: Save or download your results

CyVerse sessions are cloud-based. Depending on the training environment, files may persist in CyVerse storage, or they may disappear when the analysis is deleted. Before closing the session, save anything you need.

Common options include:

- Download the output files through the JupyterLab or VS Code file browser.
- Copy important outputs to the CyVerse Data Store if the app is configured for persistent storage.
- Commit non-secret code changes to your GitHub fork.
- Save a short note describing the model, prompt, data sources, and output files you produced.

![Screenshot showing the folder-opening workflow used to navigate to `/home/joyvan/work/`.](assets/images/cyverse/cyverse-12-download-results.png)

*Navigating to the working folder before saving or downloading results.*

!!! warning "Only commit files that are safe to share"
    Before committing or downloading results, check that you are not including API keys, private data, private endpoints, or credentials. If you used a `.env` file, it should stay out of Git.

## Optional: ask the agent to harmonize your own data

After the reference workflow runs, you can ask the agent to create a new workflow. Be specific. Include the projection, extent, resolution, and direct download URLs for each dataset.

Example request:

```text
Download these datasets, harmonize them to EPSG:4326 over Colorado, and generate a map:

- FBFM40 fuel models (raster, categorical, resampling_method="nearest"):
  https://www.landfire.gov/data-downloads/CONUS_LF2024/LF2024_FBFM40_CONUS.zip
  Use this CSV for both visualization colors (R, G, B columns) and legend labels:
  https://landfire.gov/sites/default/files/CSV/2024/LF2024_FBFM40.csv

- MACAv2 winter precipitation via OPeNDAP (raster, continuous, variable precipitation, months Dec-Mar):
  http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_macav2metdata_pr_CCSM4_r6i1p1_rcp85_2006_2099_CONUS_monthly.nc

- MTBS burned area boundaries (vector, do not rasterize):
  https://edcintl.cr.usgs.gov/downloads/sciweb1/shared/MTBS_Fire/data/composite_data/burned_area_extent_shapefile/mtbs_perimeter_data.zip

- Microsoft building footprints (vector, rasterize to presence/absence):
  https://minedbuildings.z5.web.core.windows.net/legacy/usbuildings-v2/Colorado.geojson.zip
```

Good URLs matter. Some download buttons hide the real file URL behind redirects or JavaScript. To get the actual file URL:

You have two good options:

1. Use the example datasets from the repository data catalog.
2. Get a direct download URL for public data of your choice from Chrome.

To get the actual file URL from Chrome:

1. Click the download button and let the file start downloading. You can cancel it after it starts.
2. Open `chrome://downloads/`, or press Cmd/Ctrl + J.
3. Right-click the file name and choose **Copy link address**.
4. Paste the URL into a new browser tab as a quick test.

The right URL usually starts downloading the file directly. It often ends in a real file extension such as `.tif`, `.zip`, or `.nc`. If it loads a viewer page or a landing page, it is probably not the direct download URL.

## Common issues

### The CyVerse app does not appear

Confirm that you are logged in with the correct CyVerse account. Some apps are only visible to specific users, teams, or workspaces. If you are using an ESIIL-provided app, ask the training team to confirm that your CyVerse username has access.

### The analysis is stuck in queued or submitted status

Cloud resources may take time to start, especially during a workshop when many people launch at once. Refresh the analyses page and check whether the status changes. If it remains stuck for a long time, ask the training team whether there is a resource limit or whether you should relaunch.

### The interactive session opens but the terminal is missing

In JupyterLab, look for **File -> New -> Terminal** or the terminal icon in the launcher. In VS Code, look for **Terminal -> New Terminal**. If the terminal option is disabled, the app image may not support terminal access. Ask the instructor which app image to use.

### GitHub asks for a username or password

Public repositories should clone without a GitHub login. If you are cloning a private fork or trying to push changes, you may need GitHub authentication. Use GitHub's current recommended authentication method, such as a browser-based flow, SSH key, or personal access token. Do not paste tokens into screenshots or commit them to files.

### The repository did not clone

Check that the terminal has internet access and that the repository URL is correct. Try:

```bash
ping github.com
```

If `ping` is blocked but the browser works, try cloning again. Some systems block `ping` even when Git works.

### A package is missing

Confirm that the virtual environment is active and dependencies were installed in that environment:

```bash
which python
python -m pip list
```

If the environment is not active, run:

```bash
source .venv/bin/activate
```

Then reinstall the dependencies:

```bash
pip install -r requirements.txt
```

### The API key is not found

Confirm that the environment variable is set in the same terminal where you are running the workflow:

```bash
python -c "import os; print('OPENAI_API_KEY is set' if os.getenv('OPENAI_API_KEY') else 'OPENAI_API_KEY is missing')"
```

If it says the key is missing, set the variable again in that same terminal session.

### The model call fails

Check whether the error is about authentication, rate limits, model name, endpoint URL, or network access. These are different problems:

- Authentication error: the key may be missing, expired, pasted incorrectly, or not authorized for that provider.
- Rate limit error: the key is valid, but the account or shared endpoint is temporarily over its limit.
- Model not found: the workflow is asking for a model name that your key or endpoint cannot access.
- Connection error: the CyVerse environment may not be able to reach the model endpoint.

Do not share your full key when asking for help. Share the error type and the command you ran.

### The workflow runs but the output looks wrong

Read the generated plan, logs, and summary before changing code. The goal of this lesson is to make the workflow inspectable. Check which input URLs were used, which model was called, what the harmonization plan says, and whether warnings appeared during the run.

## Next steps

After you can run the reference workflow, continue to the workflow pages and modify one part at a time: the study area, the input datasets, the prompt, the model, or the output format.

For model choices and endpoint context, continue to [Available Models](available-models.md). For agentic workflow design, continue to [Agents and Systems](agents-and-systems.md).

Please report what works and what goes wrong. Use the workshop feedback tab, fill out the feedback table if one is provided, or contact the training team on Slack.

If you are teaching or maintaining this page, update the screenshots when the CyVerse interface changes. Keep screenshots narrow, readable, and free of private information.

## Screenshot notes

The images in `docs/assets/images/cyverse/` come from the current workshop instructions. Update them when the training interface changes:

- `cyverse-01-login.png`
- `cyverse-02-dashboard.png`
- `cyverse-03-app-search.png`
- `cyverse-04-launch-settings.png`
- `cyverse-05-analysis-status.png`
- `cyverse-06-open-jupyterlab.png`
- `cyverse-07-terminal.png`
- `cyverse-08-github-clone.png`
- `cyverse-09-env-file.png`
- `cyverse-10-run-workflow.png`
- `cyverse-11-output-files.png`
- `cyverse-12-download-results.png`
