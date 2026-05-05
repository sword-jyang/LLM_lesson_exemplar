![Watercolor mountain banner for the Geospatial Harmonization with LLMs home page.](assets/images/heroes/home-hero.png){ .page-hero }

# Geospatial Harmonization with LLMs

!!! info "Authorship"
    **Designed and led by Cassie Buhler (ESIIL Postdoctoral Fellow)**

    Developed in collaboration with:

    - Ty Tuff (ESIIL)
    - Aashish Mukund (ESIIL)
    - Tyson Swetnam (CyVerse)

AI is not magic. It is a new interface to scientific work.

Most environmental scientists are already using computation. We write scripts, move data, debug pipelines, and translate ideas into code.

What has changed is not the goal. It is the interface.

Large language models allow you to describe what you want in plain language and have working code, workflows, and analyses generated in response. That can sound like "vibe coding." It can feel informal, even unscientific.

But used correctly, it is neither.

This lesson is about turning that raw interaction into a structured, reproducible, and inspectable scientific workflow.

<div class="oasis-link-grid" markdown>
[Start Here](start-here.md){ .md-button .md-button--primary }
[Run on CyVerse](cyverse.md){ .md-button }
[Bring Your Own Data](provide-your-own-data-sources.md){ .md-button }
[Developer Documentation](developer-docs.md){ .md-button }
</div>

## What You Will Learn

You will go from asking a model a question to producing a complete, shareable workflow:

* Data access that anyone can reproduce
* Code that is versioned and inspectable
* Results that can be rerun, modified, and extended
* A public artifact that others can critique and build on

The goal is not to trust the model. The goal is to use the model to accelerate everything you already know how to do well.

## The Core Idea: From Conversation to Workflow

Most people use AI like a search engine or a chatbot. That is the least useful way to use it.

In this lesson, you will treat the model as a collaborator that helps you:

1. Define a problem clearly
2. Generate candidate solutions
3. Test those solutions in real compute environments
4. Capture everything in a reproducible workflow

The conversation is not the product. The workflow is the product.

## Why This Is Not "Vibe Coding"

Skepticism is healthy. You should not trust generated code blindly.

This approach is different because it builds in constraints:

* All outputs are executed in real environments, including cloud or CyVerse instances
* All code is stored in version-controlled repositories
* All data sources are explicit and traceable
* All results can be rerun by someone else

If something is wrong, you can see where it went wrong. If something works, you can prove that it works.

This is closer to reproducible science than to improvisation.

## What This Enables

When the interface becomes easier, the bottleneck shifts.

Instead of spending most of your time writing boilerplate code, you can spend more time on:

* framing better scientific questions
* comparing alternative models and assumptions
* integrating datasets that were previously too cumbersome to use
* iterating quickly across hypotheses

This is not about replacing expertise. It is about amplifying it.

## What You Will Build

By the end of this lesson, you will have:

* A working analysis pipeline
* A public repository documenting your process
* A deployable workflow that others can run
* A clear record of how AI contributed to the result

You will not just have an answer. You will have something that can be reviewed, reused, and extended.

## Start Here

If you already have access to a model and a compute environment, begin with [Quick Start](start-here.md).

If you want a full walkthrough using ESIIL infrastructure, follow [Run on CyVerse](cyverse.md).

If you are here as part of a summit team, your goal is to turn your question into a working workflow by the end of the session.

## Closing Line

We are not teaching you how to talk to AI. We are teaching you how to turn conversation into science.
