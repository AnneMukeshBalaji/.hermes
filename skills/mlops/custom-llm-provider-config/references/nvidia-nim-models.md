# NVIDIA NIM Model Matrix (Tested)

Last verified: 2026-06-27  
Account tier: Free  
Endpoint: `https://integrate.api.nvidia.com/v1`

## ✅ Working Models (Free Tier)

| Model ID | Publisher | Notes |
|---|---|---|
| `nvidia/nemotron-3-ultra-550b-a55b` | NVIDIA | Nemotron 3 Ultra, 550B MoE |
| `deepseek-ai/deepseek-v4-pro` | DeepSeek | DeepSeek V4 Pro |
| `minimaxai/minimax-m3` | MiniMax | MiniMax M3 |
| `stepfun-ai/step-3.7-flash` | StepFun | Step 3.7 Flash |
| `moonshotai/kimi-k2.6` | Moonshot AI | Kimi K2.6 |
| `mistralai/mistral-medium-3.5-128b` | Mistral AI | Mistral Medium 3.5 128B |
| `z-ai/glm-5.1` | Z.ai | GLM 5.1 |
| `qwen/qwen3.5-397b-a17b` | Qwen | Qwen 3.5 397B MoE |

## ❌ Not Found (404)

| Model ID | Likely Reason |
|---|---|
| `nvidia/cosmos3-nano` | Not in free catalog |
| `google/gemma-4-31b-it` | Not in free catalog |
| `nvidia/kimi-k2.6` | Wrong publisher prefix (use `moonshotai/`) |
| `nvidia/glm-5.1` | Wrong publisher prefix (use `z-ai/`) |
| `nvidia/deepseek-v4-pro` | Wrong publisher prefix (use `deepseek-ai/`) |
| `nvidia/nemotron-3-ultra` | Wrong model ID (use `nemotron-3-ultra-550b-a55b`) |

## 🔒 Requires Paid/Premium Access (401)

| Model ID | Publisher |
|---|---|
| `meta/llama-3.2-90b-vision-instruct` | Meta |
| `meta/llama-3.3-70b-instruct` | Meta |

## Notes

- Model IDs are **case-sensitive** and must include the publisher prefix
- Free tier model availability varies by region and account age — re-test periodically
- Some models may have different rate limits or context windows
- Hermes auto-detection may misclassify `google/*` and `meta/*` models as Gemini — they will fail with 401