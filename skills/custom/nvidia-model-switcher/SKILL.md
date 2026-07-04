---
name: nvidia-model-switcher
description: "Quick-switch slash commands for NVIDIA NIM models via custom provider"
version: 1.0.0
author: Hermes Agent
license: MIT
---

# NVIDIA Model Switcher Skill

Adds slash commands to instantly switch between working NVIDIA NIM models.

## Slash Commands Added

| Command | Model |
|---------|-------|
| `/model-nemotron` | `nvidia/nemotron-3-ultra-550b-a55b` |
| `/model-deepseek` | `deepseek-ai/deepseek-v4-pro` |
| `/model-minimax` | `minimaxai/minimax-m3` |
| `/model-stepfun` | `stepfun-ai/step-3.7-flash` |
| `/model-kimi` | `moonshotai/kimi-k2.6` |
| `/model-mistral` | `mistralai/mistral-medium-3.5-128b` |
| `/model-glm` | `z-ai/glm-5.1` |
| `/model-qwen` | `qwen/qwen3.5-397b-a17b` |
| `/model-list` | Show all available models |

## Usage

Type any command above in a Hermes session — it updates `model.default` in config.yaml and prompts for `/reset`.

## Requirements

- Hermes configured with `model.provider: custom` and `model.base_url: https://integrate.api.nvidia.com/v1`
- Valid NVIDIA API key in `model.api_key`