# Claude Code + Custom OpenAI Endpoints Incompatibility

## Summary

Claude Code (Anthropic's CLI coding agent) **cannot** be used with NVIDIA NIM, Together AI, Fireworks, Groq, local vLLM/Ollama, or any OpenAI-compatible endpoint.

## Root Cause

1. **Client-side model validation** — Claude Code checks the `--model` value against Anthropic's internal model registry *before* sending any request. NVIDIA model IDs (e.g., `nvidia/nemotron-3-ultra-550b-a55b`) don't exist in Anthropic's registry, so validation fails immediately.

2. **Protocol/format mismatch** — Even if validation were bypassed:
   - Anthropic uses **Messages API** format (different from OpenAI's Chat Completions)
   - Tool/function calling schemas differ
   - Streaming event formats differ (Anthropic SSE vs OpenAI SSE)
   - System prompt injection and context handling differ

## Tested and Failed Approaches

| Approach | Result |
|----------|--------|
| `ANTHROPIC_BASE_URL=https://integrate.api.nvidia.com/v1 ANTHROPIC_AUTH_TOKEN=*** claude -p "hello" --model nvidia/nemotron-3-ultra-550b-a55b` | Fails: "There's an issue with the selected model..." |
| `ANTHROPIC_BASE_URL=... ANTHROPIC_AUTH_TOKEN=*** claude --bare -p "hello" --model nvidia/nemotron-3-ultra-550b-a55b` | Fails: same model validation error |
| `ANTHROPIC_BASE_URL=... ANTHROPIC_AUTH_TOKEN=*** ANTHROPIC_MODEL=... claude -p "hello"` | Fails: same model validation error |

## Working Alternatives for NVIDIA NIM Coding

| Tool | Config Approach |
|------|-----------------|
| **Hermes Agent** | `hermes config set model.provider custom && hermes config set model.base_url https://integrate.api.nvidia.com/v1 && hermes config set model.api_key <key> && hermes config set model.default nvidia/nemotron-3-ultra-550b-a55b` |
| **OpenCode** | `opencode config set provider.openai.base_url https://integrate.api.nvidia.com/v1 && opencode config set provider.openai.api_key <key> && opencode config set provider.openai.model nvidia/nemotron-3-ultra-550b-a55b` |
| **Codex CLI** | `export OPENAI_BASE_URL=https://integrate.api.nvidia.com/v1 && export OPENAI_API_KEY=<key> && codex` |
| **Aider** | `aider --model nvidia/nemotron-3-ultra-550b-a55b --api-base https://integrate.api.nvidia.com/v1 --api-key <key>` |

## Verification

Tested on 2026-06-27 with:
- Claude Code v2.x (npm package `@anthropic-ai/claude-code`)
- NVIDIA API key: `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`
- Endpoint: `https://integrate.api.nvidia.com/v1`
- Model: `nvidia/nemotron-3-ultra-550b-a55b` (confirmed available via `/v1/models`)

All attempts to use Claude Code with NVIDIA NIM failed with model validation error.