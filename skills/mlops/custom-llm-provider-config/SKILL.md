---
name: custom-llm-provider-config
description: "Configure and manage custom OpenAI-compatible LLM providers in Hermes Agent (NVIDIA NIM, local endpoints, third-party APIs)"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, configuration, llm, providers, nvidia, nim, custom-endpoint]
    related_skills: [hermes-agent, serving-llms-vllm, ollama-setup]
---

# Custom LLM Provider Configuration

This skill covers configuring Hermes Agent to use custom OpenAI-compatible endpoints — including NVIDIA NIM (build.nvidia.com), local vLLM/Ollama servers, and third-party API gateways.

## When to Use

- User wants to use a model not in Hermes's built-in provider list
- User has API access to NVIDIA NIM, Together AI, Fireworks, Groq, or any OpenAI-compatible endpoint
- User runs local inference servers (vLLM, Ollama, TGI) and wants Hermes to use them

## Prerequisites

- API key for the target provider (if required)
- Base URL of the OpenAI-compatible endpoint
- Exact model ID as exposed by the provider

## Configuration Steps

### 1. Set Custom Provider Config

```bash
hermes config set model.provider custom
hermes config set model.base_url <ENDPOINT_URL>
hermes config set model.api_key <API_KEY>
hermes config set model.default <MODEL_ID>
```

### 2. Common Endpoints

| Provider | Base URL |
|---|---|
| NVIDIA NIM (API Catalog) | `https://integrate.api.nvidia.com/v1` |
| Local vLLM | `http://localhost:8000/v1` |
| Local Ollama | `http://localhost:11434/v1` |
| Together AI | `https://api.together.xyz/v1` |
| Fireworks AI | `https://api.fireworks.ai/inference/v1` |
| Groq | `https://api.groq.com/openai/v1` |

### 3. Verify Configuration

```bash
hermes config check
hermes doctor
hermes chat -q "Hello, respond with just OK"
```

## NVIDIA NIM Specific Notes

### Model ID Format

NVIDIA uses `publisher/model-name` format. Examples:
- `nvidia/nemotron-3-ultra-550b-a55b`
- `deepseek-ai/deepseek-v4-pro`
- `minimaxai/minimax-m3`
- `stepfun-ai/step-3.7-flash`
- `moonshotai/kimi-k2.6`
- `mistralai/mistral-medium-3.5-128b`
- `z-ai/glm-5.1`
- `qwen/qwen3.5-397b-a17b`

### Free Tier Availability

Model availability on NVIDIA's free tier varies by region and account. **Always test before documenting as working.**

**Tested working (as of 2026-06-27):**
- `nvidia/nemotron-3-ultra-550b-a55b`
- `deepseek-ai/deepseek-v4-pro`
- `minimaxai/minimax-m3`
- `stepfun-ai/step-3.7-flash`
- `moonshotai/kimi-k2.6`
- `mistralai/mistral-medium-3.5-128b`
- `z-ai/glm-5.1`
- `qwen/qwen3.5-397b-a17b`

**Known unavailable/require paid access:**
- `nvidia/cosmos3-nano` → 404
- `google/gemma-4-31b-it` → 404
- `meta/llama-3.2-90b-vision-instruct` → 401 (requires premium)
- `meta/llama-3.3-70b-instruct` → 401 (requires premium)
- `nvidia/kimi-k2.6` (old ID) → 404 (use `moonshotai/kimi-k2.6`)
- `nvidia/glm-5.1` (old ID) → 404 (use `z-ai/glm-5.1`)

### Provider Auto-Detection Quirk

Hermes may auto-detect some model IDs as belonging to other providers (e.g., `google/gemma-*` → Gemini, `meta/llama-*` → Gemini). This causes wrong endpoint routing. If this happens, the model simply won't work — try a different model ID or report as a Hermes issue.

## Switching Models at Runtime

### Persistent (survives restart)
```bash
hermes config set model.default <NEW_MODEL_ID>
```

### Temporary (current session only, requires `/reset`)
```
/model <NEW_MODEL_ID>
/reset
```

### One-off (single query)
```bash
hermes chat -m <MODEL_ID> -q "Your question"
```

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| HTTP 404 | Model ID not found on endpoint | Verify exact model ID on provider dashboard |
| HTTP 401 | API key invalid or no access to model | Check key validity; some models require paid tier |
| HTTP 400 | Malformed request | Check model ID format; try without publisher prefix |
| Provider shows `gemini` for NVIDIA models | Hermes auto-detected wrong provider | Known quirk; model will fail. Use different model ID. |

## Pitfalls

1. **Model ID must match exactly** — case-sensitive, including publisher prefix
2. **Free tier changes** — models that work today may be restricted tomorrow
3. **Auto-detection conflicts** — Hermes's provider inference can route to wrong backend
4. **Rate limits** — Free tiers have strict RPM/TPM limits; expect 429 errors under load
5. **Context length** — Varies by model; NVIDIA NIM models typically 4k-128k context

## ⚠️ Known Incompatibility: Claude Code + Custom OpenAI Endpoints

**Claude Code does NOT work with NVIDIA NIM, Together AI, Groq, local vLLM/Ollama, or any OpenAI-compatible endpoint.**

### Why it fails
- Claude Code validates `--model` against Anthropic's model registry **client-side** before making requests
- Setting `ANTHROPIC_BASE_URL=https://integrate.api.nvidia.com/v1` and `ANTHROPIC_AUTH_TOKEN=***` fails with: `"There's an issue with the selected model (nvidia/nemotron-3-ultra-550b-a55b). It may not exist or you may not have access to it."`
- Even if model validation passed, the Anthropic API format (Messages API, tool use, streaming) is incompatible with OpenAI-compatible endpoints

### What to use instead

| Tool | Supports Custom OpenAI Endpoints? | Config |
|------|-----------------------------------|--------|
| **Hermes Agent** (this session) | ✅ Yes | `hermes config set model.provider custom` + `model.base_url` + `model.api_key` |
| **OpenCode** | ✅ Yes | `opencode config set provider.openai.base_url ...` |
| **Codex CLI** | ✅ Yes | `OPENAI_BASE_URL` + `OPENAI_API_KEY` env vars |
| **Aider** | ✅ Yes | `--model` + `--api-base` flags |
| **Claude Code** | ❌ No | Hardcoded to Anthropic models only |

**Bottom line:** If you want to code with NVIDIA NIM models (Nemotron, etc.), use Hermes, OpenCode, Codex, or Aider — not Claude Code.

## References

- `references/nvidia-nim-models.md` — Tested model matrix for NVIDIA API Catalog
- `references/custom-provider-template.md` — Template for documenting new providers
- `references/claude-code-incompatibility.md` — Why Claude Code doesn't work with NIM/OpenAI-compatible endpoints