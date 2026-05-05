# Agents and Systems

The use of computation in environmental science has evolved through several distinct stages. Early workflows were often built around standalone scripts, written to process a specific dataset or answer a narrowly defined question. As data grew in volume and complexity, these scripts gave way to more structured pipelines, notebooks, and workflow managers that allowed researchers to organize, document, and reproduce their analyses.

Large language models introduce a new stage in this evolution. They do not replace existing computational methods, but they change how those methods are constructed. Instead of writing code line by line, researchers can now describe analytical intent in natural language and receive executable code in response.

This shift raises an important question: does this represent a new form of scientific computing, or does it undermine the rigor that computational workflows are meant to provide?

Answering that question requires a more precise understanding of agents and systems.

---

## Historical Context: From Scripts to Systems

To understand the role of agents, it is useful to situate them within the broader history of computational practice.

| Stage of Practice | Primary Unit of Work | Strengths | Limitations |
|---|---|---|---|
| Standalone scripts | Individual files | Flexible, direct control | Difficult to scale or reproduce |
| Notebooks | Interactive documents | Combines narrative, code, and results | Often linear, hard to modularize |
| Pipelines and workflows | Structured processes | Reproducibility and automation | Require significant setup and expertise |
| Agentic systems | Repository-centered systems | Rapid development with structured integration | Require new conventions and constraints |

Each stage addresses limitations of the previous one. Agentic systems build on workflows and pipelines, but introduce a new interface for constructing them.

---

## What Is a System?

In scientific computing, a system is more than a collection of code. It is an organized set of components that work together to produce results.

A system typically includes data sources, code, computational environments, documentation, and rules for how each part interacts. The defining feature of a system is not its complexity, but its structure. A system specifies how work is done, not just what is done.

In environmental data science, systems are essential because analyses often depend on integrating heterogeneous datasets, applying multiple transformations, and ensuring that results can be reproduced and interpreted correctly. A biodiversity analysis may draw from field surveys, remote sensing products, climate data, and model output. Each component may be valid on its own, but the scientific result depends on how those components are connected.

A system is what makes those connections explicit.

---

## What Is an Agent?

Within a system, an agent is an entity that performs tasks according to defined rules and with access to specific resources.

In the context of large language models, an agent is not simply the model itself. It is the model operating within constraints. It may be given access to a repository, allowed to modify or generate code, guided by explicit instructions, and asked to work within a defined workflow.

This distinction is important. A model used without constraints produces outputs that are difficult to reproduce and verify. A model embedded as an agent within a system produces outputs that are shaped by the structure of that system.

The agent is useful because it can accelerate implementation. The system is necessary because it makes that implementation inspectable.

---

## The Repository as the Core System

In this project, the repository serves as the central system.

It is where code is written, stored, and versioned. It is where data access and harmonization are defined. It is where workflows are implemented and executed. It is where results are generated and documented. It is also where agent behavior is constrained and guided.

This structure transforms AI interaction into something durable. Instead of relying on transient conversations, the work is captured in a persistent, inspectable form.

The repository becomes the primary artifact of the scientific process.

---

## The Role of agent.md

A defining feature of this approach is the inclusion of an agent.md file.

This file specifies how the agent should behave within the repository. It may include goals and priorities for the agent, constraints on how code should be written or modified, expectations for documentation and structure, and rules for interacting with data and workflows.

In traditional programming, similar constraints are often implicit. They may exist as team norms, instructor expectations, coding conventions, or informal practices. By making them explicit, agent.md functions as a formal interface between the user and the agent.

It plays a role analogous to a methods section in a scientific paper, an API contract in software engineering, or a protocol in experimental design. It does not replace human judgment, but it makes the conditions for agent-assisted work clearer.

This explicit structure is what allows agent-assisted work to remain rigorous.

---

## Why Structure Matters: Addressing "Vibe Coding"

The term "vibe coding" is often used to describe informal, unconstrained use of AI to generate code. In such cases, outputs may appear functional but lack transparency, consistency, and reproducibility.

This critique highlights a real risk. Without structure, AI-assisted workflows can become difficult to interpret or validate. Code may run without being understandable. Results may appear plausible without being traceable. Decisions may be buried in a conversation that is not part of the scientific record.

Agentic systems address this by enforcing constraints at multiple levels.

| Concern | Unstructured Interaction | Agentic System Approach |
|---|---|---|
| Reproducibility | Conversation-dependent | Version-controlled repository |
| Transparency | Implicit reasoning and hidden assumptions | Explicit code and documented workflows |
| Consistency | Variable outputs across prompts | Rule-guided agent behavior |
| Validation | Ad hoc checking | Executable and testable pipelines |
| Collaboration | Difficult to share context | Shared repository and documented conventions |

These constraints do not eliminate uncertainty, but they make it visible and manageable. That is the core difference between vibe coding and structured agentic work.

---

## Agents in Environmental Workflows

In environmental data science, agents can assist with a range of tasks. They can help access and format heterogeneous datasets, implement data harmonization procedures, generate analysis code, document assumptions, and revise workflows as questions evolve.

These tasks are not performed in isolation. They are integrated into workflows that reflect the structure of the repository.

For example, an agent might generate code to align biodiversity observations with climate data. That code is then executed, inspected, and potentially revised. The result becomes part of a reproducible pipeline rather than a one-off solution.

The scientific value does not come from the model producing a correct answer on its own. The value comes from using the model to help construct a workflow that can be tested, modified, and shared.

---

## From Interaction to Infrastructure

The significance of agentic systems lies in their ability to support infrastructure development.

A well-structured repository with an embedded agent can function as a reusable analytical workflow, a shared resource for collaboration, a record of methodological decisions, and a platform for extending and refining analyses.

This is particularly important in environmental science, where research often depends on integrating data across scales, domains, and disciplines. The work is rarely a single calculation. It is more often a chain of decisions linking data collection, harmonization, modeling, visualization, and interpretation.

Agentic repositories help make that chain visible.

---

## Closing Perspective

Agents and systems provide a way to incorporate AI into scientific practice without abandoning the principles that make that practice reliable.

The key shift is conceptual.

The goal is not to obtain answers from a model. The goal is to build systems that produce answers in a transparent and reproducible way.

The agent accelerates the process. The system ensures that the results remain scientific.
