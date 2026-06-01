---
name: stack-ai
description: 'Apply AI *integration* expertise — LLM provider SDKs (OpenAI, Anthropic). Use when implementing API calls; for RAG, routing, or pipelines use @ai-architecture instead.'
paths:
  - "src/ai/**"
  - "src/llm/**"
  - "src/openai/**"
---

Do:
- validate structured outputs (schema/JSON mode + parse before use)
- redact PII before sending prompts; never log full prompt/response bodies with user data
- handle provider errors: timeouts, retries with backoff, rate-limit responses

Avoid:
- client-side API keys or provider SDK calls from the browser
- parsing free-form model text when structured output is available