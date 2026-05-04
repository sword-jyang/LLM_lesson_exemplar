# Where LLMs Live: Data Centers, Hosting, and Sovereignty

Large language models are often described as if they live in an abstract place called "the cloud." But the cloud is not a place. It is a collection of buildings, power contracts, cooling systems, network cables, storage arrays, GPUs, software stacks, and governance decisions. Every model that answers a prompt is running somewhere specific. It may be running on a laptop, on a lab server, in a university data center, on an NSF-funded research cloud, inside a national laboratory, or in a hyperscale commercial data center owned by a major technology company.

That physical location matters. It determines who controls the model, who pays for the electricity, what data can safely move through the system, how reproducible the workflow can be, and whether the benefits of the infrastructure flow back to the community that hosts it. For science, these are not side issues. They shape whether AI becomes a shared public infrastructure or a private dependency.

This chapter explains the major ways LLMs are hosted, what resources they require, where those resources are located, and how communities evaluate whether the infrastructure is welcome, reasonable, or extractive.

## What hosting means

Hosting is the process of making a model available for use. At a minimum, hosting requires hardware that can load the model, software that can run inference, storage for model files and logs, networking so users can reach it, and some form of access control. A hosted model may be exposed through a chat interface, an API endpoint, a Jupyter notebook, a classroom tool, or a workflow system.

For small experiments, hosting can be informal. A researcher can download a model and run it locally through a tool like Ollama or llama.cpp. For shared scientific use, hosting becomes infrastructure. The model needs uptime, authentication, monitoring, versioning, storage, documentation, cost control, and governance. The difference between "I ran a model" and "we host a model" is the difference between a demonstration and a service.

The central challenge is that open models are easier to download than they are to operate. Open weights make a model legally and technically available. Hosting makes it practically usable.

## The pieces of an LLM hosting system

LLM hosting is a coupled system. The model is only one part of it.

| Component | What it does | Typical constraint |
|---|---|---|
| GPU or CPU compute | Executes inference or training | FLOPS, GPU count, accelerator type |
| GPU memory | Holds model weights, key-value cache, and context | Often the main inference bottleneck |
| System memory | Supports loading, preprocessing, and non-GPU work | Can bottleneck large models or RAG systems |
| Storage | Holds model weights, embeddings, documents, logs, and outputs | Capacity and I/O speed |
| Networking | Connects users, APIs, storage, and compute | Latency, bandwidth, firewall policy |
| Serving software | Runs the model behind an API | Throughput, batching, scheduling |
| Orchestration | Starts, stops, scales, and monitors services | Operational complexity |
| Authentication | Controls who can use the system | Identity integration |
| Governance | Controls quotas, budgets, models, data policy, and logging | Institutional maturity |
| Power and cooling | Keeps hardware online and stable | Energy, heat, water, facility limits |

Inference is usually constrained by memory. The model weights must fit into GPU memory, and long conversations require additional memory for the key-value cache. Training and large-scale fine-tuning are constrained by compute, GPU interconnect, storage throughput, and total runtime. Retrieval-augmented generation adds another layer because documents, embeddings, and vector databases must also be hosted and governed.

## Three main hosting models

Most scientific LLM hosting falls into three broad categories: self-hosting, institutional or open-science hosting, and commercial API hosting. These are not mutually exclusive. Mature systems often combine all three.

### Self-hosting

Self-hosting means running the model on hardware that an individual, lab, department, university, Tribal organization, agency, or project controls directly. This can be a laptop, a workstation, a rack-mounted GPU server, or a private cloud instance.

Self-hosting provides the most control. The user can choose the model, inspect the software stack, decide where logs are stored, restrict access, and keep sensitive data inside a trusted environment. This is especially important when the data are unpublished, regulated, proprietary, Indigenous-governed, human-subjects related, or otherwise sensitive.

The tradeoff is responsibility. The group must manage hardware, drivers, model serving, user access, security, backups, monitoring, upgrades, and costs. A single researcher can often make a local model work. A lab can often maintain a small server. A university-wide service requires a professional platform.

### Institutional and open-science hosting

Institutional hosting sits between individual self-hosting and commercial hyperscale AI. Examples include campus research clouds, ACCESS-CI resources, CyVerse services, Jetstream2, Delta, and VERDE-like platforms. These systems are designed to support many users while keeping infrastructure aligned with research and education.

This layer is especially important for open models. It gives communities somewhere to run them without asking every lab to become a data center operator. It can also provide governance: identity management, quotas, allocations, model catalogs, shared documentation, cost controls, and data policies.

CyVerse VERDE is an example of this service-layer idea. Instead of requiring every user to know which GPU is running which model, VERDE provides a more unified access point for models, APIs, and retrieval workflows. ACCESS-CI resources provide the underlying research cyberinfrastructure that can support cloud-like services, batch workloads, training, fine-tuning, and scientific AI workflows.

### Commercial API hosting

Commercial API hosting means sending requests to external providers such as OpenAI, Anthropic, Google, Microsoft, Amazon, Hugging Face, or other hosted inference providers. This is the fastest and simplest path. Users do not need to buy GPUs, operate servers, or manage model deployments.

The tradeoff is dependency. The provider controls the model, pricing, retention policies, regional hosting options, uptime, and terms of service. Commercial APIs are often excellent for rapid prototyping, low-risk tasks, and general-purpose workloads. They are less ideal when data sovereignty, auditability, reproducibility, or long-term cost stability are central requirements.

## A practical comparison

| Question | Self-hosting | Institutional / ACCESS / VERDE | Commercial APIs |
|---|---|---|---|
| Who controls the hardware? | User, lab, or institution | Institution or research cyberinfrastructure provider | Vendor |
| Who controls the model? | User or institution | Shared governance | Vendor |
| Setup burden | High | Medium | Low |
| Operating burden | High | Shared | Low for user, high dependency |
| Best for | Sensitive data, experimentation, custom systems | Shared science, teaching, governed access | Rapid prototyping, general tasks |
| Data sovereignty | Strongest | Strong if designed well | Weak to moderate, depending on provider and contract |
| Cost pattern | Capital cost plus operations | Allocation or institutional cost | Usage-based tokens |
| Reproducibility | Strong if versioned | Strong if platform logs versions | Limited by model changes and provider access |
| Scaling | Hard without staff | Designed for communities | Easy but externally controlled |
| Main risk | Underused hardware and admin burden | Governance complexity | Lock-in, cost growth, data exposure |

The important point is that no one layer solves every problem. A good scientific AI strategy usually uses commercial APIs for low-risk convenience, institutional systems for shared and governed research use, and self-hosted systems for sensitive data or specialized methods.

## How much infrastructure are we talking about?

The scale of LLM hosting ranges from a single GPU to infrastructure that affects regional power planning. A small quantized model can run on a laptop or workstation. A useful shared service for a lab or course may require one to four data-center GPUs. A campus service may require tens to hundreds of GPUs plus staff. National open-science systems may operate hundreds to tens of thousands of GPUs. Commercial frontier-model infrastructure is larger still.

A useful rule of thumb is that inference is mostly about memory and training is mostly about compute. A 7B or 8B parameter model can often run on a single consumer GPU if quantized. A 70B parameter model is already a different class. In full precision, it may require roughly 140 GB just for weights. In 8-bit form it may require roughly 70 to 85 GB. In 4-bit form it may fit in roughly 40 to 50 GB, not including all serving overheads. Exact requirements vary by architecture, quantization method, context length, batch size, and serving engine. `(source needed)`

That is why open weights do not automatically mean local usability. A model can be open and still require data-center-class hardware to serve well.

| Hosting tier | Typical hardware | What it can realistically support | Main limitation |
|---|---|---|---|
| Laptop | CPU, Apple Silicon, or small GPU | Small local models, demos, private experiments | Slow, limited concurrency |
| Workstation | 1 to 2 consumer GPUs | 7B to 14B models; larger models with quantization | Heat, noise, VRAM, uptime |
| Lab server | 1 to 4 data-center GPUs | Shared lab chatbot, RAG, coding assistant, moderate open models | Administration, security, scheduling |
| Campus service | Tens to hundreds of GPUs | Courses, research groups, shared APIs | Governance, funding, staffing |
| ACCESS or national resource | Hundreds to thousands of GPUs | Training, fine-tuning, large-scale inference, open science workflows | Allocation and service design |
| Hyperscale AI data center | Thousands to hundreds of thousands of accelerators across sites | Frontier model training and global API serving | Grid, water, land, community impact |

## Workloads are not all the same

Different AI workloads stress infrastructure in different ways. A campus chatbot, a fine-tuning job, a document-grounded RAG system, and an autonomous agent workflow may all use an LLM, but they behave very differently as infrastructure.

### Inference

Inference is the act of running a trained model to generate outputs. Chatbots, coding assistants, summarizers, classification pipelines, and most API calls are inference workloads. Inference needs enough GPU memory to load the model and enough compute to generate tokens quickly. It also needs low latency, uptime, user authentication, and monitoring.

A small model can support many users on one GPU. A large model may support only a few concurrent users at acceptable latency. Throughput depends on model size, context length, batching, quantization, serving software, GPU type, and user behavior.

### Training and fine-tuning

Training and fine-tuning are much more compute-intensive. They require repeated passes through data, high GPU utilization, fast storage, and often high-bandwidth interconnects between GPUs. These workloads are often better suited to HPC systems like Delta or leadership-class systems than to a small persistent service.

Fine-tuning small models can be realistic for a lab or campus. Training frontier-scale models is not. It belongs to national labs, large companies, or very large consortia.

### Retrieval-augmented generation

RAG systems add documents to the hosting problem. The system must store source documents, create embeddings, maintain a vector database, retrieve relevant chunks, and pass them into the model. This shifts some of the bottleneck from GPU memory to storage, indexing, permissions, and governance.

For science, RAG is often more important than fine-tuning. It allows an existing model to answer using project documents, data dictionaries, protocols, publications, or course materials without changing the model weights. But RAG also increases the sovereignty problem because private documents may be sent into prompts or embedding systems.

### Agents and workflow systems

Agent systems make many model calls as they reason, search, write code, call tools, and revise outputs. They can be bursty and difficult to budget. A single user may trigger dozens or hundreds of calls. This makes governance, quotas, logging, and cost accounting more important than in simple chat.

## Throughput and cost intuition

Exact performance numbers change quickly, but rough orders of magnitude help users understand the hosting problem.

| Model size | Typical serving hardware | Rough behavior |
|---|---|---|
| 7B to 8B | One consumer or data-center GPU | Good for teaching, demos, lightweight tools |
| 13B to 14B | One higher-memory GPU | Better quality, lower throughput |
| 30B to 34B | One large GPU or multiple GPUs | Useful but less convenient |
| 70B | One very high-memory GPU with quantization or multiple GPUs | Stronger model, much lower concurrency |
| 100B+ | Multi-GPU serving | Institutional or commercial scale |

Self-hosting becomes economically attractive when utilization is high and predictable. Commercial APIs are often cheaper and easier when usage is low, bursty, or experimental. A GPU server that sits idle most of the day has a high cost per useful token. A commercial API may seem expensive per token but avoids idle hardware, maintenance, and staffing costs.

This is one of the most important lessons for institutions: do not compare only the price of a GPU with the price of tokens. Compare the full cost of ownership, including staff time, electricity, cooling, networking, downtime, security, and replacement cycles.

## Energy and power

Modern AI hardware is power dense. A single high-end data-center GPU may draw hundreds of watts. A server with eight high-end GPUs can draw several kilowatts before facility overhead. A rack of liquid-cooled AI servers can draw tens of kilowatts. A large AI data center can draw tens to hundreds of megawatts.

| System | Approximate IT load |
|---|---|
| One GPU workstation | Hundreds of watts to around 1 kW |
| One 4-GPU server | Roughly 2 to 4 kW |
| One 8-GPU high-end server | Roughly 6 to 10+ kW |
| Dense AI rack | Tens of kW |
| Small institutional AI room | Hundreds of kW to around 1 MW |
| Large commercial AI data center | Tens to hundreds of MW |

Facility efficiency matters. Data centers are often described using PUE, or power usage effectiveness. PUE is total facility power divided by IT equipment power. A PUE of 2.0 means that for every watt used by computing equipment, another watt is used for cooling, power conversion, lighting, and facility overhead. A PUE close to 1.0 is much more efficient.

This means local hosting is not automatically greener. A GPU server in a poorly cooled room may have low total scale but poor efficiency. A professional data center may have much higher total demand but better energy use per computation because it can cool efficiently, maintain high utilization, and reuse waste heat.

The sustainability question is therefore not simply local versus data center. It is utilization, facility efficiency, grid carbon intensity, water use, heat reuse, hardware lifetime, and whether the work being done is worth the resource cost.

## Place matters: where these systems actually are

AI infrastructure is geographic. It is built in specific places with specific power grids, water systems, land-use politics, labor markets, universities, national labs, and communities. The same GPU cluster can be welcomed in one place and resisted in another.

| Facility or region | Location | Type | Approximate scale | Community reception | Why it matters |
|---|---|---|---|---|---|
| Jetstream2 | Indiana University and Texas Advanced Computing Center | ACCESS-CI open science cloud | About 360 NVIDIA A100 GPUs `(verify)` | Generally welcomed | Framed as research and education infrastructure |
| Delta | NCSA, University of Illinois Urbana-Champaign | ACCESS-CI GPU/HPC resource | Hundreds of A100, A40, H200, and related GPUs `(verify)` | Generally welcomed | Campus and national research mission |
| Frontier | Oak Ridge National Laboratory, Tennessee | DOE leadership supercomputer | Tens of thousands of GPUs `(verify)` | Welcomed as national scientific instrument | Public mission, peer-reviewed science access |
| Aurora | Argonne National Laboratory, Illinois | DOE leadership supercomputer | Tens of thousands of GPUs `(verify)` | Welcomed as national scientific instrument | Science, simulation, AI, and data-intensive research |
| NREL HPC Data Center | Golden, Colorado | Energy-optimized scientific data center | MW-scale `(verify)` | Welcomed | Known for efficiency, warm-water cooling, and waste-heat reuse |
| Northern Virginia Data Center Alley | Loudoun County and surrounding region, Virginia | Commercial hyperscale corridor | Hundreds of facilities `(verify)` | Increasingly contested | Grid constraints, land use, transmission, local saturation |
| Phoenix metro | Arizona | Commercial hyperscale growth region | Rapid expansion `(verify)` | Mixed to contested | Water scarcity, heat, energy demand |
| Georgia and Atlanta region | Georgia | Commercial hyperscale growth region | Rapid expansion `(verify)` | Increasing scrutiny | Grid planning and local benefit questions |
| Rural Pennsylvania proposals | Pennsylvania | Proposed AI/data-center campuses | Multi-site proposals `(verify)` | Often resisted | Concerns over land, utility costs, noise, and extractive development |

The pattern is not random. AI infrastructure is more likely to be welcomed when it is legible as public infrastructure: research, education, national science, workforce development, or local institutional benefit. It is more likely to be resisted when it appears extractive: local power, land, water, and noise in exchange for distant profits and few local benefits.

## Welcomed versus resisted infrastructure

Communities tend to welcome AI infrastructure when it is tied to a mission they understand and value. A university research cloud is easier to defend than an anonymous hyperscale facility. A national lab supercomputer is framed as a scientific instrument. An ACCESS-CI resource is allocated to research and education. The benefit is public, or at least institutionally accountable.

Communities tend to resist AI infrastructure when it arrives as a private industrial load on local resources. The concerns are usually concrete: electricity demand, transmission lines, water use, backup diesel generators, noise, land clearing, tax incentives, and whether local residents will see meaningful benefits.

A useful framing question is:

> Is this community hosting infrastructure for its own future, or absorbing impacts for someone else's model?

That question often determines whether AI infrastructure is seen as innovation or extraction.

## Data sovereignty

Data sovereignty is the principle that communities, institutions, nations, or rights holders should control how their data are stored, accessed, moved, interpreted, and reused. For LLM hosting, sovereignty becomes central because prompts are data, documents passed into RAG systems are data, embeddings are data, logs are data, and model outputs may reveal information about inputs.

Self-hosting or institutional hosting is especially important when data cannot leave a jurisdiction, when Indigenous data governance applies, when human-subjects or health data are involved, when research is unpublished or sensitive, when government or agency rules restrict external processing, or when communities require control over interpretation and access.

In these cases, commercial APIs may still be useful for low-risk tasks, but they should not become the default path for sensitive workflows. The safest architecture is often layered:

| Layer | Best use |
|---|---|
| Local or community-controlled hosting | Sensitive data, sovereignty, experimentation |
| Institutional hosting | Shared research, courses, governed access |
| ACCESS or national research infrastructure | Open science compute, scaling, reproducibility |
| Commercial APIs | Low-risk tasks, rapid prototyping, overflow capacity |

Sovereignty does not always require that every model run under a desk. It requires that hosting decisions match the governance needs of the data and the community.

## What makes VERDE and ACCESS important

The open-source AI world has made model weights more available, but it has not made hosting equally available. ACCESS-CI, Jetstream2, Delta, CyVerse, and VERDE help solve the next problem: where open models can run for science.

ACCESS resources provide national-scale cyberinfrastructure for research and education. Jetstream2 is especially relevant for persistent, cloud-like services and interactive environments. Delta is more appropriate for large batch workloads, training, fine-tuning, and GPU-heavy scientific computing. VERDE-like services add the user-facing layer: model catalogs, APIs, routing, retrieval, access control, and policy.

This division of labor matters. A GPU cluster alone is not an AI service. A service needs identity, quotas, model management, documentation, monitoring, storage, and governance. VERDE is valuable because it points toward an institutional control plane for AI: a layer that can connect users to models without exposing every user to the full complexity of the hardware.

## Common failure modes

Most LLM hosting failures are predictable.

VRAM exhaustion happens when the model, context window, and batch size exceed available GPU memory. This is common when users try to host larger open-weight models than their hardware can comfortably support.

Underutilization happens when expensive GPUs sit idle. This makes self-hosting look cheap on paper but expensive in practice. Utilization is one of the main reasons shared infrastructure can be more efficient than isolated lab servers.

Overload happens when too many users hit a service at once. Latency spikes, queues grow, and users lose trust. This is common when a prototype becomes a shared tool without a scaling plan.

RAG bottlenecks happen when document retrieval, vector search, storage, or permissions are not designed carefully. The model may be fast, but the system feels slow or unreliable because the retrieval layer is weak.

Governance failure happens when there are no quotas, no model policy, no logging policy, and no cost controls. This is how experimental systems become expensive, insecure, or impossible to maintain.

## A decision framework

Use a local machine when the goal is experimentation, privacy, or learning, and when small models are sufficient.

Use a lab server when a small group needs shared access, when data should stay local, and when someone can maintain the system.

Use campus, CyVerse, VERDE, or ACCESS-style infrastructure when the goal is shared scientific use, teaching, reproducibility, or governed access across many users.

Use commercial APIs when speed matters, the data are low risk, the workload is bursty, and the group does not want to operate infrastructure.

Use national HPC systems when the workload is large-scale training, fine-tuning, model evaluation, simulation, or batch scientific analysis.

Avoid pretending that one layer solves every problem. The best architecture is usually hybrid.

## The main lesson

Open models lowered the barrier to entry, but infrastructure determines participation. The next phase of open AI will depend less on whether a model can be downloaded and more on whether communities have somewhere reasonable to run it.

That means hosting is not just a technical decision. It is a decision about energy, geography, sovereignty, governance, and public value.

The question is not only which model is best.

The question is where that model lives, who controls it, who pays for it, and whether the community hosting it wants it there.
