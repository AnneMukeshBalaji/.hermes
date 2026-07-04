# Ollama Model Sizes by VRAM Tier

Verified tag availability as of June 2026. Always re-verify with curl before recommending.

## 8GB VRAM sweet spot (Q4_K_M)

### General purpose (7B-9B, fit comfortably)

| Model | Available tags | Verified |
|---|---|---|
| Qwen 3 | 0.6b, 1.7b, 4b, 8b, 14b, 30b, 32b, 235b | ✅ 8b fits well |
| Qwen 3.5 | 0.8b, 2b, 4b, 9b, 27b, 35b, 122b, 397b | ✅ **9b is the sweet spot** |
| Qwen 3.6 | 27b, 35b | ❌ Too big for 8GB |
| Gemma 3 | 270m, 1b, 4b, 12b, 27b | ✅ 4b fast, 12b tight |
| Gemma 4 | e2b, e4b, 12b, 26b, 31b | ✅ e4b very fast, 12b tight |
| Llama 3.1 | 8b, 70b, 405b | ✅ 8b classic |
| Llama 3.2 | (3b, 1b) | ✅ Tiny |
| Llama 4 | 17b | ❌ Too big |
| Phi-4 | 8b, 14b | ✅ 8b good, 14b tight |
| Phi-4-mini | 3b | ✅ Fast |
| Mistral Nemo | 12b | ⚠️ Tight at Q4 |
| Mistral Small 3.2 | 24b | ❌ Too big |
| Command R7b | 7b, 8b | ✅ Fits well |
| Granite 4 | 1b, 3b, 7b, 9b | ✅ 7b/9b fit |
| Granite 4.1 | 8b, 9b, 10b | ✅ Good fit |
| Nemotron 3 | 8b, 33b | ✅ 8b fits |
| DeepSeek R1 | 7b, 8b, 14b, 32b, 70b, 671b | ✅ 7b/8b fit well, 14b tight |
| GLM-5 | 40b, 744b | ❌ Too big |

### Reasoning / thinking models

- DeepSeek R1: 7b ✅, 8b ✅, 14b ⚠️
- Phi-4-mini-reasoning: 3b ✅ (fast)
- Phi-4-reasoning: 14b ⚠️ (tight)
- Qwen 3: 4b-thinking ✅, 30b-thinking ❌

## How to verify

```bash
# Replace <model> with the model name
curl -sL "https://ollama.com/library/<model>/tags" | grep -oP 'href="/library/<model>:[^"]+"' | sed 's/.*://;s/"//' | sort -u
```
