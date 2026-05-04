![Available Models banner with connected model nodes and cube icon.](assets/images/heroes/available-models-hero.png){ .page-hero }

# Available Models

This page is a field guide to the AI models available through your API key. It is written for people who may not already know these model families, but who need to make informed choices about scientific work, reproducibility, cost, transparency, and capability.

Think of these models as different research instruments. Some are fast and lightweight. Some are large and capable. Some can look at images. Some are better for long documents. Some publish enough information to support scientific interpretation, while others should be treated as black-box services.

## Quick Comparison

| Model endpoint | Model family | Builder | Base location | Best use | Modality | Openness | Disclosure level |
|---|---|---|---|---|---|---|---|
| `nrp/glm-4.7` | GLM | Zhipu AI / THUDM lineage | China | General chat, multilingual work | Text | Closed/API-only | Low |
| `nrp/kimi` | Kimi | Moonshot AI | China | Long documents, large-context synthesis | Text | Closed/API-only | Low |
| `nrp/gemma` | Gemma | Google DeepMind | UK / USA | Fast general tasks | Text | Open-weight | High |
| `nrp/qwen3` | Qwen | Alibaba | China | Coding, reasoning, multilingual tasks | Text | Open-weight | High |
| `nrp/qwen3-small` | Qwen small | Alibaba | China | Fast, low-cost prototyping | Text | Open-weight | High |
| `nrp/minimax-m2` | MiniMax | MiniMax | China | Fast conversational applications | Text | Closed/API-only | Low |
| `nrp/gpt-oss` | GPT-OSS | Varies by host | Mixed | General open-model experimentation | Text | Usually open-weight | Variable |
| `Meta-Llama-3.1-70B-Instruct-quantized` | Llama 3.1 | Meta | USA | High-quality writing and reasoning | Text | Open-weight, restricted license | High |
| `llama-3.3-70b-instruct-quantized` | Llama 3.3 | Meta | USA | High-quality instruction following | Text | Open-weight, restricted license | High |
| `Llama-3.3-70B-Instruct-quantized` | Llama 3.3 | Meta | USA | Same as above, alternate endpoint name | Text | Open-weight, restricted license | High |
| `phi-4` | Phi | Microsoft | USA | Efficient reasoning, math, logic | Text | Open-weight | Moderate |
| `phi-4-multimodal-instruct` | Phi multimodal | Microsoft | USA | Text + image reasoning | Text + image | Open-weight | Moderate |
| `gemma-3-12b-it` | Gemma 3 | Google DeepMind | UK / USA | Balanced chat and structured output | Text | Open-weight | High |
| `Llama-3.2-11B-Vision-Instruct` | Llama Vision | Meta | USA | Image understanding | Text + image | Open-weight, restricted license | High |
| `js2/llama-4-scout` | Llama 4 Scout | Meta ecosystem / host provider | USA / mixed | Experimental, high-capacity multimodal work | Text + multimodal depending on host | Open-weight, restricted license | Moderate to high |
| `js2/gpt-oss-120b` | GPT-OSS 120B | Varies by host | Mixed | Large open-model synthesis | Text | Usually open-weight | Variable |

## Best Starting Points

| Goal | Recommended models | Why |
|---|---|---|
| I just want a good default model | `nrp/qwen3`, Llama 3.3 70B | Strong general performance and broadly useful behavior |
| I need speed or lower cost | `nrp/qwen3-small`, `nrp/gemma`, `gemma-3-12b-it` | Smaller models respond faster and require less compute |
| I need high-quality writing or synthesis | Llama 3.3 70B, `js2/gpt-oss-120b` | Larger models generally produce better long-form reasoning and prose |
| I need coding help | `nrp/qwen3`, Llama 3.3 70B | Strong code and structured reasoning performance |
| I need to analyze images | `phi-4-multimodal-instruct`, `Llama-3.2-11B-Vision-Instruct` | These are vision-language models |
| I need to read very long documents | `nrp/kimi` | Designed around long-context use cases |
| I need transparent scientific workflows | Llama, Gemma, Qwen | These model families publish comparatively more technical information |
| I need local or institutional deployment | Llama, Gemma, Qwen, Phi | Open-weight models can often be deployed outside a vendor API |

## What the Labels Mean

| Term | Meaning | Why it matters |
|---|---|---|
| Open-weight | The model weights are available, but the full training data and training process may not be. | You can often run or inspect the model, but cannot fully reproduce it. |
| Closed/API-only | The model is only available through an API or hosted service. | Useful and convenient, but difficult to audit or reproduce. |
| High disclosure | The builder publishes technical reports, architecture details, training recipes, or model cards. | Better for scientific interpretation. |
| Low disclosure | The builder mainly publishes product descriptions, benchmark claims, or API documentation. | Treat as a black-box system. |
| RLHF | Reinforcement Learning from Human Feedback. Humans rank or evaluate model outputs, and the model is tuned toward preferred behavior. | Improves usability and safety, but introduces human and institutional preferences. |
| RLAIF | Reinforcement Learning from AI Feedback. Another model provides preference judgments. | Scales alignment cheaply, but can amplify model biases. |
| DPO | Direct Preference Optimization. A simpler preference-learning method that can replace some RLHF pipelines. | Often easier to train than full RLHF. |
| Reasoning model | A model trained or tuned to perform better on multi-step tasks. | Better for math, code, planning, and scientific explanation, but not automatically more truthful. |

## Model Profiles

### GLM-4.7

`nrp/glm-4.7`

| Category | Details |
|---|---|
| Builder | Zhipu AI, with roots in the THUDM / Tsinghua GLM research lineage |
| Based in | Beijing, China |
| Funding model | Commercial AI company with academic roots and venture / national AI ecosystem support |
| Openness | Closed/API-only for this endpoint |
| Disclosure level | Low for the deployed model, moderate for earlier GLM research lineage |
| Best for | General chat, bilingual Chinese-English work, coding support, structured outputs |
| Watch out for | Limited public disclosure about exact training data, alignment, and deployed version details |

GLM models come from a Chinese model family developed around generalized language modeling methods. Earlier GLM research has been published openly, but deployed GLM-4 style products generally do not disclose full training data, alignment methods, or reinforcement learning details. For scientific use, this means GLM can be useful as a capable black-box model, especially for multilingual work, but it is harder to document reproducibly than open-weight model families.

**Training data:** Not fully disclosed. It likely includes large Chinese-language corpora, English web data, code, and instruction data, but exact proportions are not public.

**Reasoning:** Standard transformer-based reasoning. Public documentation does not establish that this endpoint is a dedicated reasoning model in the same sense as models trained explicitly for long chain-of-thought or test-time reasoning.

**Alignment and RL:** Likely uses supervised instruction tuning and preference optimization. Human feedback is likely involved, but the exact RLHF pipeline is not public. Regulatory and safety filtering may also shape outputs.

**Useful links:**

- THUDM GLM repository: [https://github.com/THUDM/GLM](https://github.com/THUDM/GLM)
- GLM-130B paper: [https://arxiv.org/abs/2210.02414](https://arxiv.org/abs/2210.02414)
- Zhipu / BigModel platform: [https://open.bigmodel.cn/](https://open.bigmodel.cn/)

### Kimi

`nrp/kimi`

| Category | Details |
|---|---|
| Builder | Moonshot AI |
| Based in | Beijing, China |
| Funding model | Venture-backed AI startup |
| Openness | Closed/API-only |
| Disclosure level | Low |
| Best for | Long documents, large-context synthesis, report reading, literature review support |
| Watch out for | Strong product capability claims, but limited public methods disclosure |

Kimi is best known for long-context interaction. In practical terms, that means it is often useful when the user wants to place a large amount of text into the prompt and ask the model to synthesize, compare, or extract information. Long context, however, should not be confused with perfect memory or guaranteed reasoning. Models can still miss details, over-weight nearby text, or produce confident summaries that require verification.

**Training data:** Not fully disclosed. The model is likely trained or tuned on long-form documents, web text, code, and instruction data, but the underlying dataset mixture is not public.

**Reasoning:** Context-driven reasoning. Its main advantage is the ability to process long inputs, not necessarily a fundamentally different reasoning architecture.

**Alignment and RL:** Not publicly detailed. Likely uses supervised instruction tuning and some preference optimization. Human feedback may be used, but the public record does not provide enough detail to document the RL pipeline.

**Useful links:**

- Kimi product page: [https://kimi.moonshot.cn/](https://kimi.moonshot.cn/)
- Moonshot AI: [https://www.moonshot.cn/](https://www.moonshot.cn/)

### Gemma

`nrp/gemma`

| Category | Details |
|---|---|
| Builder | Google DeepMind |
| Based in | London, UK and Mountain View, USA |
| Funding model | Corporate research funded by Google / Alphabet |
| Openness | Open-weight |
| Disclosure level | High compared with most commercial models |
| Best for | Efficient general tasks, local deployment, fast inference, educational use |
| Watch out for | Open-weight does not mean fully reproducible because the complete training data is not released |

Gemma is Google DeepMind's family of lightweight open-weight models derived from the same broad research ecosystem as Gemini. Gemma models are designed to be more accessible than frontier closed models while still benefiting from high-quality training infrastructure, filtering, and safety work.

**Training data:** Public documentation describes large-scale filtered training data, including web text, code, and mathematical content, but does not release the full dataset. Like most open-weight models, Gemma is transparent about model design relative to closed APIs, but not fully reproducible from raw data.

**Reasoning:** General transformer reasoning. Instruction-tuned variants can perform multi-step tasks, but smaller Gemma models will usually have less deep reasoning capacity than 70B-scale models.

**Alignment and RL:** Google describes instruction tuning and safety tuning. Public details vary by release, and full RLHF or preference optimization data is not released.

**Human RL:** Likely mixed human and synthetic feedback. Exact annotation pipelines are not fully public.

**Useful links:**

- Gemma documentation: [https://ai.google.dev/gemma](https://ai.google.dev/gemma)
- Gemma technical report: [https://arxiv.org/abs/2403.08295](https://arxiv.org/abs/2403.08295)

### Gemma 3 12B IT

`gemma-3-12b-it`

| Category | Details |
|---|---|
| Builder | Google DeepMind |
| Based in | London, UK and Mountain View, USA |
| Funding model | Corporate research funded by Google / Alphabet |
| Openness | Open-weight |
| Disclosure level | High compared with most commercial models |
| Best for | Balanced chat, structured output, moderate reasoning, efficient deployment |
| Watch out for | Mid-sized model, so it may underperform larger models on complex synthesis |

Gemma 3 12B IT is an instruction-tuned model. The "IT" usually indicates that the base model has been tuned to follow user instructions, answer questions, and behave more like a chat assistant. It is a good choice when users need a practical, relatively efficient model rather than the largest possible model.

**Training data:** Based on the Gemma family's filtered training regime. The exact data mixture for this endpoint should be documented against the specific hosted model card when available.

**Reasoning:** Better than many small models, but still constrained by size. Good for structured answers, summaries, and routine analysis.

**Alignment and RL:** Instruction tuning and safety tuning. Full preference data and human feedback details are not fully public.

**Useful links:**

- Gemma documentation: [https://ai.google.dev/gemma](https://ai.google.dev/gemma)
- Gemma technical report: [https://arxiv.org/abs/2403.08295](https://arxiv.org/abs/2403.08295)

### Qwen 3

`nrp/qwen3`

| Category | Details |
|---|---|
| Builder | Alibaba Qwen team |
| Based in | Hangzhou, China |
| Funding model | Corporate research funded by Alibaba |
| Openness | Open-weight |
| Disclosure level | High for model reports and code, incomplete for exact training data |
| Best for | Coding, multilingual work, reasoning, technical workflows |
| Watch out for | Strong model family, but exact hosted endpoint details may differ from the public model card |

Qwen is one of the strongest open-weight model families, especially for multilingual and coding tasks. It is useful in scientific settings because it combines strong performance with comparatively good documentation and public model releases.

**Training data:** Qwen reports describe large-scale multilingual data, code, mathematical content, and instruction datasets. The full raw training dataset is not released.

**Reasoning:** Qwen models are often strong at reasoning and code because of training data composition and instruction tuning. Some Qwen variants explicitly support "thinking" or reasoning modes, but users should verify whether the specific endpoint exposes that behavior.

**Alignment and RL:** Public Qwen materials describe supervised fine-tuning and preference optimization in the model family. Exact RLHF or DPO details can vary by release.

**Human RL:** Likely hybrid human and synthetic feedback. Full human annotation details are not public.

**Useful links:**

- Qwen GitHub organization: [https://github.com/QwenLM](https://github.com/QwenLM)
- Qwen technical paper: [https://arxiv.org/abs/2309.16609](https://arxiv.org/abs/2309.16609)

### Qwen 3 Small

`nrp/qwen3-small`

| Category | Details |
|---|---|
| Builder | Alibaba Qwen team |
| Based in | Hangzhou, China |
| Funding model | Corporate research funded by Alibaba |
| Openness | Open-weight |
| Disclosure level | High for model family, endpoint-specific details may vary |
| Best for | Fast iteration, low-cost inference, simple coding or writing tasks |
| Watch out for | Less reasoning depth than larger Qwen models |

Qwen 3 Small is the faster, lighter option in the Qwen family. It is useful for teaching, prototyping, and repeated low-cost calls. It is less appropriate for complex synthesis, long reasoning chains, or high-stakes interpretation.

**Training data:** Same general family pattern as Qwen: multilingual text, code, math, and instruction data. Exact data for the small endpoint is not fully disclosed.

**Reasoning:** Efficient but more limited. Small models can appear fluent while missing deeper dependencies.

**Alignment and RL:** Likely instruction tuning and preference optimization inherited from the Qwen release pipeline.

**Useful links:**

- Qwen GitHub organization: [https://github.com/QwenLM](https://github.com/QwenLM)
- Qwen technical paper: [https://arxiv.org/abs/2309.16609](https://arxiv.org/abs/2309.16609)

### MiniMax M2

`nrp/minimax-m2`

| Category | Details |
|---|---|
| Builder | MiniMax |
| Based in | Shanghai, China |
| Funding model | Venture-backed AI startup |
| Openness | Closed/API-only |
| Disclosure level | Low |
| Best for | Fast conversational use, chat interfaces, lightweight assistants |
| Watch out for | Limited public information about data, training, and RL methods |

MiniMax models are generally positioned as fast conversational systems. They may be useful for interactive applications where responsiveness matters more than methodological transparency.

**Training data:** Not publicly disclosed.

**Reasoning:** Likely optimized for conversational quality and latency rather than deep scientific reasoning.

**Alignment and RL:** Not publicly documented in detail. It likely uses supervised instruction tuning and human or AI preference feedback, but the exact RL pipeline is not available.

**Human RL:** Possible or likely, especially for chat quality, but not documented enough for confident scientific description.

**Useful links:**

- MiniMax company site: [https://www.minimax.io/](https://www.minimax.io/)
- MiniMax API site: [https://api.minimax.chat/](https://api.minimax.chat/)

### GPT-OSS

`nrp/gpt-oss`

| Category | Details |
|---|---|
| Builder | Varies by model and host |
| Based in | Mixed; depends on the underlying model |
| Funding model | Open-source, academic, nonprofit, startup, or hosted-provider ecosystem |
| Openness | Usually open-weight, but verify the exact model |
| Disclosure level | Variable |
| Best for | Experimentation, open-model workflows, testing alternatives |
| Watch out for | The endpoint name alone does not identify the full training lineage |

"GPT-OSS" is not a single universally defined model family in the way Llama, Gemma, or Qwen are. It usually means a GPT-style open-source or open-weight model made available through a hosting provider. For scientific use, the most important step is to identify the exact underlying model, version, license, and model card.

**Training data:** Variable. Some open models use curated datasets; others use web-scale mixtures with limited disclosure.

**Reasoning:** Depends heavily on scale, training data, and whether the model received reasoning-oriented fine-tuning.

**Alignment and RL:** Variable. Some open models use DPO or preference optimization. Others may have minimal alignment.

**Human RL:** Variable and often poorly documented.

**Useful links:**

- OpenAccess AI Collective: [https://github.com/OpenAccess-AI-Collective](https://github.com/OpenAccess-AI-Collective)
- OpenChat example repository: [https://github.com/imoneoi/openchat](https://github.com/imoneoi/openchat)

### GPT-OSS 120B

`js2/gpt-oss-120b`

| Category | Details |
|---|---|
| Builder | Varies by exact hosted model |
| Based in | Mixed; depends on host and training organization |
| Funding model | Usually open-model ecosystem plus hosting infrastructure |
| Openness | Usually open-weight, but confirm the exact base model |
| Disclosure level | Variable |
| Best for | Large-model synthesis, high-quality writing, heavier reasoning tasks |
| Watch out for | Large size improves capability but not necessarily transparency |

A 120B open-weight GPT-style model can be powerful, but "120B" is not by itself a methods description. Parameter count tells you about scale, not data quality, alignment, safety, or reproducibility. This endpoint should be documented carefully in any scientific workflow: record the provider, date, exact model string, and any model card the provider supplies.

**Training data:** Depends on exact model. Often a mixture of web text, code, books, and synthetic instruction data.

**Reasoning:** Mostly scale-driven unless the model has explicit reasoning fine-tuning.

**Alignment and RL:** Variable. Could include SFT, DPO, RLHF, or minimal alignment.

**Human RL:** Unknown unless the underlying model card says otherwise.

**Useful links:**

- OpenAccess AI Collective: [https://github.com/OpenAccess-AI-Collective](https://github.com/OpenAccess-AI-Collective)
- Ask your provider for the exact model card and license for `js2/gpt-oss-120b`.

### Llama 3.1 70B Instruct Quantized

`Meta-Llama-3.1-70B-Instruct-quantized`

| Category | Details |
|---|---|
| Builder | Meta |
| Based in | Menlo Park, California, USA |
| Funding model | Corporate research funded by Meta |
| Openness | Open-weight under Meta's license, not fully open-source in the strict sense |
| Disclosure level | High compared with most model families |
| Best for | High-quality writing, coding, instruction following, scientific synthesis |
| Watch out for | Quantization improves efficiency but can slightly reduce quality |

Llama 3.1 70B is a large open-weight instruction model. "70B" refers to roughly 70 billion parameters, making it much larger than models like Gemma 12B or Llama Vision 11B. The "quantized" version reduces numerical precision so the model can run more efficiently, at some cost to exactness and sometimes quality.

**Training data:** Meta reports large-scale pretraining on filtered web data, code, and other text sources. The raw training data is not released.

**Reasoning:** Strong scale-driven reasoning. The model is not guaranteed to reason correctly, but larger Llama models tend to handle multi-step tasks better than small models.

**Alignment and RL:** Meta reports supervised fine-tuning and preference-based alignment for Llama chat/instruct models, including human feedback and safety tuning.

**Human RL:** Yes, human preference data is part of the Llama alignment lineage, augmented by synthetic data and automated filtering.

**Useful links:**

- Llama documentation: [https://ai.meta.com/llama/](https://ai.meta.com/llama/)
- Llama 3 publication page: [https://ai.meta.com/research/publications/llama-3-open-foundation-and-fine-tuned-chat-models/](https://ai.meta.com/research/publications/llama-3-open-foundation-and-fine-tuned-chat-models/)
- Llama 2 paper for earlier lineage: [https://arxiv.org/abs/2307.09288](https://arxiv.org/abs/2307.09288)

### Llama 3.3 70B Instruct Quantized

`llama-3.3-70b-instruct-quantized`

`Llama-3.3-70B-Instruct-quantized`

| Category | Details |
|---|---|
| Builder | Meta |
| Based in | Menlo Park, California, USA |
| Funding model | Corporate research funded by Meta |
| Openness | Open-weight under Meta's license |
| Disclosure level | High compared with most model families |
| Best for | General high-quality instruction following, coding, synthesis, reasoning |
| Watch out for | Large and compute-intensive, even when quantized |

These two endpoints appear to be alternate names for the same or closely related hosted Llama 3.3 70B instruct model. In documentation, it is useful to list both endpoint strings so users know either one may work in the API.

**Training data:** Meta does not release raw training data, but describes large-scale pretraining using filtered text and code, followed by instruction and preference tuning.

**Reasoning:** Strong general reasoning from scale and instruction tuning. It is a good default choice when quality matters more than speed.

**Alignment and RL:** Llama instruct models use supervised fine-tuning and preference optimization. Public reports describe human feedback as part of the alignment process, though full datasets are not released.

**Human RL:** Yes, but not fully reproducible because the human preference datasets and reward models are not completely public.

**Useful links:**

- Llama documentation: [https://ai.meta.com/llama/](https://ai.meta.com/llama/)
- Llama 3 publication page: [https://ai.meta.com/research/publications/llama-3-open-foundation-and-fine-tuned-chat-models/](https://ai.meta.com/research/publications/llama-3-open-foundation-and-fine-tuned-chat-models/)

### Llama 3.2 Vision 11B Instruct

`Llama-3.2-11B-Vision-Instruct`

| Category | Details |
|---|---|
| Builder | Meta |
| Based in | Menlo Park, California, USA |
| Funding model | Corporate research funded by Meta |
| Openness | Open-weight under Meta's license |
| Disclosure level | High compared with most multimodal systems |
| Best for | Image understanding, visual question answering, image + text workflows |
| Watch out for | Smaller than 70B text models and may be less capable at deep text-only reasoning |

Llama 3.2 Vision extends the Llama family into multimodal work. It can process both images and text, making it useful for workflows such as interpreting figures, screenshots, diagrams, or field photos. Vision-language models should still be validated carefully, especially for scientific images where small details matter.

**Training data:** Meta describes multimodal training using image-text data and instruction tuning, but does not release the full dataset.

**Reasoning:** Combines visual representation learning with language-model reasoning. Its visual ability depends heavily on the image encoder and training mixture.

**Alignment and RL:** Likely follows the Llama instruct alignment pattern, adapted for multimodal tasks.

**Human RL:** Likely includes human preference or annotation components, but full details are not public.

**Useful links:**

- Llama documentation: [https://ai.meta.com/llama/](https://ai.meta.com/llama/)
- Llama model downloads and cards: [https://www.llama.com/](https://www.llama.com/)

### Llama 4 Scout

`js2/llama-4-scout`

| Category | Details |
|---|---|
| Builder | Meta model family, hosted through JS2 / provider infrastructure |
| Based in | Meta is USA-based; host environment may vary |
| Funding model | Corporate model development plus hosted research / cyberinfrastructure access |
| Openness | Open-weight under Meta's license, depending on hosted model terms |
| Disclosure level | Moderate to high for model family; endpoint details should be verified |
| Best for | Experimental high-capacity workflows, broad multimodal exploration where supported |
| Watch out for | Confirm the exact model card, context length, modality support, and hosting configuration |

Llama 4 Scout should be treated as a hosted endpoint for a specific Llama-family model. Because hosted endpoints may differ in quantization, context length, system prompts, safety filters, and inference settings, document the exact endpoint and provider when using it for scientific work.

**Training data:** Depends on Meta's Llama 4 release documentation and the hosted variant. Full raw data is not expected to be public.

**Reasoning:** Likely scale-driven and instruction-tuned. If the model supports multimodal input, reasoning will also depend on multimodal training.

**Alignment and RL:** Expected to follow Meta's modern instruction and preference-tuning approach, but endpoint-specific details should be checked.

**Human RL:** Likely part of the broader Llama alignment lineage, but exact hosted details are not public.

**Useful links:**

- Llama documentation: [https://ai.meta.com/llama/](https://ai.meta.com/llama/)
- Llama model site: [https://www.llama.com/](https://www.llama.com/)

### Phi-4

`phi-4`

| Category | Details |
|---|---|
| Builder | Microsoft |
| Based in | Redmond, Washington, USA |
| Funding model | Corporate research funded by Microsoft |
| Openness | Open-weight for many Phi-family releases |
| Disclosure level | Moderate |
| Best for | Efficient reasoning, math, logic, structured problem solving |
| Watch out for | Smaller model size can limit general knowledge and open-ended synthesis |

Phi models are built around the idea that data quality can compensate for model size. Instead of only scaling parameters, Microsoft's Phi lineage emphasizes curated data, textbook-like examples, code, and synthetic reasoning data.

**Training data:** Microsoft publications emphasize curated high-quality data and synthetic data. Exact datasets vary by release and are not fully public.

**Reasoning:** Phi is designed for strong reasoning per parameter. This often means it performs surprisingly well on math, code, and logic relative to its size.

**Alignment and RL:** Phi models rely heavily on curated and synthetic training data. They may use instruction tuning and safety tuning, but the family is less defined by large public RLHF pipelines than some larger chat models.

**Human RL:** Lower or less central than in some large chat models. Human validation may be used, but synthetic data is a major feature of the Phi approach.

**Useful links:**

- Microsoft Phi overview: [https://aka.ms/phi](https://aka.ms/phi)
- Phi-2 paper for lineage: [https://arxiv.org/abs/2312.12148](https://arxiv.org/abs/2312.12148)

### Phi-4 Multimodal Instruct

`phi-4-multimodal-instruct`

| Category | Details |
|---|---|
| Builder | Microsoft |
| Based in | Redmond, Washington, USA |
| Funding model | Corporate research funded by Microsoft |
| Openness | Open-weight for many Phi-family releases |
| Disclosure level | Moderate |
| Best for | Efficient image + text tasks, multimodal reasoning, lightweight visual analysis |
| Watch out for | Not a replacement for domain-specific scientific image analysis pipelines |

Phi-4 Multimodal extends the Phi reasoning-efficient approach to inputs beyond text. It can be useful when a workflow requires both language and visual understanding, but like all multimodal LLMs, it should be treated as interpretive support rather than measurement infrastructure.

**Training data:** Likely combines Phi-style curated text and synthetic reasoning data with image-text training data. Exact dataset composition is not fully public.

**Reasoning:** Efficient multimodal reasoning. Strong for small-model use cases, but not necessarily as deep as much larger multimodal systems.

**Alignment and RL:** Likely instruction and safety tuning. Public details are less complete than for the core architectural idea of Phi.

**Human RL:** Unknown to moderate; likely a mix of human validation and synthetic data.

**Useful links:**

- Microsoft Phi overview: [https://aka.ms/phi](https://aka.ms/phi)
- Phi-2 paper for lineage: [https://arxiv.org/abs/2312.12148](https://arxiv.org/abs/2312.12148)

## Transparency and Disclosure

### Publicly documented model families

These model families provide technical reports, repositories, model cards, or papers that describe architecture, training strategy, evaluation, and alignment at least partially.

| Family | What is public | What remains private |
|---|---|---|
| Llama | Architecture, training recipe summaries, safety work, model cards | Exact raw datasets, full human preference data, full reward models |
| Gemma | Technical report, model cards, training overview, safety evaluation | Exact raw datasets, full alignment data |
| Qwen | Repositories, papers, model cards, benchmark reports | Exact raw datasets, full RLHF / DPO details |
| Phi | Papers and reports emphasizing synthetic data and reasoning efficiency | Exact data mixture and full alignment process |

### More opaque or API-centered model families

These models may be highly capable, but public documentation does not provide enough detail to fully evaluate training data, alignment, or reproducibility.

| Family | What is public | What remains private |
|---|---|---|
| GLM-4 style deployed models | Earlier GLM research lineage, product claims, benchmarks | Exact deployed training data, alignment process, RL details |
| Kimi | Product descriptions, long-context capability claims | Training data, alignment methods, RL details |
| MiniMax | Product and API documentation | Training data, alignment methods, RL details |
| GPT-OSS endpoints | Depends entirely on underlying model | Often unclear unless host provides exact model card |

## Scientific Tradeoffs

### Scale vs efficiency

Large models such as Llama 70B and GPT-OSS 120B usually produce better synthesis, reasoning, and writing than smaller models, but they cost more to run and respond more slowly. Smaller models such as Gemma, Qwen small, and Phi are better for repeated calls, teaching, prototyping, and lightweight workflows.

### Open-weight vs reproducible

Open-weight models give users more control because the weights can often be downloaded or hosted independently. But open-weight does not mean fully reproducible. Most open-weight models do not release the raw training data, filtering pipeline, human feedback data, or full alignment procedure.

### Human feedback vs synthetic feedback

Human feedback can improve helpfulness and safety, but it also embeds the preferences of the annotators, the labeling instructions, and the institution funding the work. Synthetic feedback scales more easily and can improve reasoning data, but it can also amplify the assumptions and errors of the models used to generate it.

### Long context vs careful reading

Long-context models can accept more text, but they do not automatically understand all of it equally. Long prompts can still lead to missed details, false synthesis, or overconfident summaries. For scientific documents, long-context output should be checked against the source.

### Reasoning vs truth

A model that is good at reasoning is not necessarily good at truth. Reasoning-tuned models may produce more structured explanations, but they can still reason from false premises, invent citations, or hide uncertainty. For science, reasoning output should be paired with source checking and reproducible workflows.

## Recommended Documentation Practice

When using any model in a scientific workflow, record:

| Field | Example |
|---|---|
| API endpoint | `nrp/qwen3` |
| Provider | NRP / hosted API provider |
| Underlying model family | Qwen 3 |
| Date used | YYYY-MM-DD |
| Prompt or system instruction | Save in a prompt log |
| Temperature and settings | Record if available |
| Whether output was verified | Yes / no, plus method |
| Source documents used | List files, URLs, or datasets |
| Human review | Who reviewed and what changed |

A simple methods sentence might read:

> Draft summaries were generated using `nrp/qwen3` through the project API on YYYY-MM-DD. Outputs were reviewed by the authors against the source documents and revised manually before inclusion.

## Final Perspective

AI models are shaped by data, compute, alignment, institutions, and incentives. Two models with similar architectures can behave very differently because they were trained on different data, tuned toward different preferences, and deployed under different constraints.

For OASIS workflows, the practical goal is not to find one perfect model. The goal is to choose models deliberately, document their use, validate their outputs, and match the model to the scientific task.
