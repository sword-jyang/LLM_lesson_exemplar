![Watercolor mountain banner for the Geospatial Harmonization with LLMs home page.](assets/images/heroes/home-hero.png){ .page-hero }

# Geospatial Harmonization with LLMs

!!! info "Authorship"
    **Designed and led by Cassie Buhler (ESIIL Postdoctoral Fellow)**

    Developed in collaboration with:

    - Ty Tuff (ESIIL)
    - Aashish Mukund (ESIIL)
    - Tyson Swetnam (CyVerse)

    Testing and feedback:

    - Nate Hofford (Earth Lab)
    - Matt Bitters (Earth Lab)
    - Bridger Huhn (ASCEND Engine)
    - Danielle Losos (Earth Lab)

## Agentic Repositories for Environmental Data Science

Environmental data science has never been limited by ideas. It has been limited by translation. We move from questions to code, from code to workflows, from workflows to results, and at each step something is lost: time, clarity, reproducibility, or access.

Large language models introduce a new interface to that process. They allow us to express intent in natural language and generate working code in response. This has led to a common critique: that this style of work is “vibe coding”—informal, unstructured, and detached from the rigor that scientific computing requires.

That critique is valid for ad hoc use. It is not valid for what we are building here.

This project is centered on a different model: the agentic repository. In this approach, the repository—not the conversation—is the unit of scientific work. The repository contains code, data access patterns, workflows, and, critically, the rules that govern how an AI agent interacts with all of them.

At the core of this structure is a simple idea: if you want to use AI in science, you must constrain it in the same way you constrain any computational system. That means defining interfaces, expectations, and boundaries. In this repository, those constraints are made explicit through:

* Version-controlled code that can be inspected and modified
* Reproducible workflows that can be executed in real environments
* Explicit data sources and transformations
* An agent.md file that defines how the AI is allowed to operate within the system

The agent.md file is not decoration. It is the equivalent of an API contract or a methods section. It encodes rules, expectations, and structure so that interactions with the model are not free-form, but guided, testable, and repeatable.

This is why this is not “vibe coding.” The model is not being trusted. It is being constrained and integrated into a system that enforces the same principles that have always defined good computational science: clarity, versioning, reproducibility, and inspection.

In that sense, working with AI is less like abandoning programming and more like learning a new language for expressing it. The underlying fundamentals have not changed. You are still defining logic, structuring workflows, managing state, and validating outputs. What has changed is the interface through which you do that work.

Agentic repositories make that interface usable without sacrificing rigor. They allow you to move more quickly from idea to implementation while preserving a clear record of how that implementation was constructed.

This lesson will guide you through building and working within that structure. You will define a problem, use an AI model to help generate and refine code, and integrate that code into a repository that enforces rules about how it can be used, modified, and extended. The result is not a conversation. It is a system: one that others can run, inspect, and build upon.

This is the standard we are aiming for. Not informal experimentation, but structured acceleration. Not less rigor, but a different way of achieving it.

<div class="oasis-link-grid" markdown>
[Run Locally](start-here.md){ .md-button .md-button--primary }
[Run on CyVerse](cyverse.md){ .md-button }
[Bring Your Own Data](provide-your-own-data-sources.md){ .md-button }
[Developer Documentation](developer-docs.md){ .md-button }
</div>

## Choose a Run Path

If you already have access to a model and a working Python environment on your computer, begin with [Run Locally](start-here.md).

If you want a full walkthrough using ESIIL infrastructure, follow [Run on CyVerse](cyverse.md).

If you are here as part of a summit team, your goal is to move from an initial question to a working, shareable repository within the time available.

## Closing Line

We are not replacing scientific computing.
We are changing how we interface with it.
