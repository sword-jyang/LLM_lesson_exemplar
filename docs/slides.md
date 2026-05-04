# AI Summit Lesson

![Lesson Slides banner with a presentation window and chart icon.](assets/images/heroes/lesson-slides-hero.png){ .page-hero }

<button id="presenter-mode-toggle" class="md-button md-button--primary" type="button">
  Enter presenter mode
</button>
<p class="presenter-mode-help">
Presenter mode shows one slide at a time. Use the left and right arrow keys to move between slides. Press Escape to exit.
</p>

<div class="lesson-slideshow" markdown>
<section class="lesson-slide title-slide" markdown>
# AI Summit Lesson
## ESIIL Summit 2026
### Using LLMs to Harmonize Data
</section>
<section class="lesson-slide section-slide" markdown>
# Part 1
## Introduction
</section>
<section class="lesson-slide" markdown>
# Outline
## Part 1: Intro
20–25 minutes
1. AI is not a monolith
2. What are LLMs?
3. What is an agent?
4. Your choices as a user
## Part 2: Geospatial Harmonization with an LLM Agent
90 minutes
1. Framing the problem
2. Colorado fire example
3. Auditing the output
4. Run your own workflow
</section>
<section class="lesson-slide" markdown>
# AI is not a monolith
AI is not just ChatGPT.
There is a wide spectrum of models, interfaces, hosting arrangements, and trade-offs.
The important point for this lesson is simple:
**You have choices.**
</section>
<section class="lesson-slide" markdown>
# What is an LLM?
A large language model is a stochastic generator. It predicts and produces text, code, and structured outputs from patterns in data.
LLMs are useful for:
- reasoning about structure,
- making decisions across messy inputs,
- translating between formats,
- and asking the right questions.
LLMs are weak at:
- exact computation,
- guaranteed factual recall,
- and knowing things outside their training or context.
The fix is not to trust them blindly.
**The fix is to give them tools.**
</section>
<section class="lesson-slide" markdown>
# What is an agent?
An agent is an LLM plus tools it can call on your behalf.
The key split is:
**The LLM decides. Software executes.**
This matters for scientists because you already have domain software and the expertise to know when an output is wrong.
The LLM is the orchestration layer on top of tools you already trust.
Scientists are well-positioned here because the expertise to build these tools, and the domain knowledge to verify the outputs, lives in your community.
</section>
<section class="lesson-slide" markdown>
# Your choices as a user
You have choices about the model and the environment.
## Which model?
Commercial frontier model, open-weights model, or local model.
## Where does it run?
Cloud API, institutional server, or your own machine.
## Why this matters
- **Privacy:** does your data leave your machine?
- **Environmental footprint:** energy and water use vary across providers. Some report this, some do not.
- **Reproducibility and governance:** who owns the interaction log? Can you audit what happened?
You have a choice, and you should be mindful about it.
</section>
<section class="lesson-slide section-slide" markdown>
# Part 2
## Tutorial
### Geospatial Harmonization with an LLM Agent
</section>
<section class="lesson-slide" markdown>
# The challenge
Environmental data rarely arrive ready to use together.
You may have multiple datasets with different projections, resolutions, extents, and formats.
Traditionally, this means writing a custom preprocessing script for every new dataset. That works, but it does not scale well.
We already know how to harmonize data.
The question for this lesson is:
**What if we used AI to assist with that process?**
</section>
<section class="lesson-slide" markdown>
# Example: Colorado fire risk
The reference workflow harmonizes four datasets:
- FBFM40 fuel models: raster
- MACAv2 winter precipitation through OPeNDAP: raster
- MTBS fire perimeters: vector
- Microsoft building footprints: vector, rasterized for analysis
The goal is to process these data to:
- EPSG:4326,
- the Colorado boundary,
- and a shared raster resolution of approximately 270 meters.
</section>
<section class="lesson-slide" markdown>
# Audit the output
How do you know the agent did the right thing?
Start with the outputs:
- a static PNG map,
- an interactive HTML map,
- and `PROMPT_ACTION_LOG.md`.
The action log records every run, every decision, and every dataset URL.
The agent is designed to ask before acting on ambiguous decisions. That is a feature, not a limitation.
Verify the output. If it is not what you expect, explain that clearly to the LLM.
LLMs cannot read your mind. You need to provide clear instructions.
</section>
<section class="lesson-slide" markdown>
# Bring your own data
Open the repository in CyVerse and test the workflow with datasets from your own research domain.
You provide:
- dataset names and descriptions,
- dataset download URLs,
- desired harmonization outputs such as projection, extent, and resolution,
- and specific plotting instructions, such as the color for each layer.
Dataset URLs are often the biggest point of failure. If a URL is broken, private, or points to a page rather than a downloadable data object, the workflow may fail.
You can also reference data URLs that the chatbot already has from the ESIIL data library.
</section>
<section class="lesson-slide closing-slide" markdown>
# The goal
Use the agent as an assistant, not an authority.
Let it organize the workflow, expose the assumptions, and produce outputs you can inspect.
Then use your scientific expertise to verify the result.
</section>
</div>
<div class="slide-nav-links" markdown>
[Start Here](start-here.md){ .md-button .md-button--primary }
[Run on CyVerse](cyverse.md){ .md-button }
[Modify the Lesson](modify.md){ .md-button }
</div>
