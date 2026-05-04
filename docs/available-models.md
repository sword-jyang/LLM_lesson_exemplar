# Available Models

This lesson can work with any language model that can read a prompt, produce text or code, and be called from the environment where the harmonization workflow runs. The model is not the scientific result. It is a helper for organizing data sources, writing reproducible workflow code, and making assumptions easier for a human to inspect.

## Model options

| Option | Best for | Watch for |
|---|---|---|
| Commercial API models | Fast setup, strong general reasoning, workshops where users already have keys | Cost, changing model names, data-use policies, external hosting |
| Institutionally hosted models | Courses, shared research infrastructure, governed access, reproducible teaching environments | Availability, quotas, endpoint-specific setup |
| Local or open-weight models | Sensitive data, offline work, experimentation with model behavior | Hardware requirements, slower responses, more setup |

## What to choose for this lesson

Use the strongest available model when the task involves unfamiliar datasets, ambiguous file formats, or multi-step geospatial reasoning. Use a smaller or locally hosted model when the goal is privacy, cost control, or demonstrating that the workflow can run without a commercial provider.

For teaching, the most important requirement is consistency. Pick one model or endpoint for the room, document the required environment variables, and make sure every participant can run the same reference example before asking them to modify the workflow.

## Configuration checklist

Before running the lesson, confirm:

- the model or endpoint name,
- the API key or authentication method,
- the environment variable names users must set,
- whether prompts, data snippets, or logs leave the local environment,
- any token, quota, or rate limits,
- and whether the model is appropriate for the data governance needs of the project.

## Reproducibility note

Model availability changes over time. When you adapt this lesson, record the exact model name, provider, endpoint, and date in your notes or workflow documentation. That makes it easier to understand differences in generated code, explanations, or harmonization plans later.
