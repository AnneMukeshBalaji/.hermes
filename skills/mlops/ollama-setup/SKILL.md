---
name: ollama-setup
description: Install, clean up, configure Ollama on Linux (Arch) and recommend models matched to hardware specs (VRAM, RAM).
version: 1.1.0
author: nous
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [ollama, arch-linux, model-recommendation, vram, gpu, local-llm]
---

# Ollama Setup & Model Recommendation

Use this skill when the user asks to install Ollama, troubleshoot a broken Ollama install, or get a model recommendation based on their hardware.

## When to use

- User wants to install Ollama (especially on Arch Linux)
- Previous Ollama install left leftovers (orphaned user/group, stale directories)
- User asks "what model should I run?" — check their specs and recommend
- User reports corrupted models, failed pulls, or service issues

## Workflow

### 1. Check current state

```bash
# Is Ollama installed?
which ollama

# Is it running?
systemctl status ollama --no-pager -l

# Which models are loaded, and on what processor?
ollama ps
# Look at PROCESSOR column: "CPU" (100% CPU) vs "GPU" (accelerated)

# Cross-reference GPU usage
nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total --format=csv,noheader
# If VRAM is <500 MiB but a model is loaded, it's running on CPU

# Check if Ollama build includes GPU backends
ls /usr/lib/ollama/ | grep -E "cuda|vulkan|rocm"
# If none of these exist, you have the CPU-only build (Arch: ollama package)

# Any leftovers from a previous install?
getent passwd ollama   # orphaned user?
getent group ollama    # orphaned group?
ls -la /usr/share/ollama 2>/dev/null   # stale data dir?
ls -la /var/lib/ollama 2>/dev/null     # stale model storage?
```

### 2. Clean leftovers before install

If previous install was removed but left artifacts:

```bash
# Remove stale directory that blocks pacman
sudo rm -rf /usr/share/ollama

# Remove orphaned user (after removing the package)
sudo userdel ollama

# Remove orphaned group (after removing user from it)
sudo gpasswd -d luffy ollama   # if user is a member
sudo groupdel ollama
```

### 3. Install on Arch Linux

**Choose the right variant:**

| Package | Backend | When to use |
|---|---|---|
| `ollama` | CPU only | No dedicated GPU, or just testing |
| `ollama-cuda` | NVIDIA CUDA | NVIDIA GPU with 6+ GB VRAM (adds ~4.7 GB CUDA toolkit) |
| `ollama-rocm` | AMD ROCm | AMD GPU |
| `ollama-vulkan` | Vulkan | Fallback GPU support, any vendor |

```bash
# For NVIDIA GPUs (your case):
sudo pacman -S ollama-cuda

# This replaces ollama (CPU-only) with the CUDA variant.
# It pulls the full CUDA toolkit (~4.7 GB installed) as a dependency.
# Download is ~3 GB total — may take several minutes.
```

**If install was interrupted:**

```bash
# Remove stale lock
sudo rm /var/lib/pacman/db.lck

# Clean partial downloads
sudo rm -rf /var/cache/pacman/pkg/partial/*

# Retry
sudo pacman -S ollama-cuda
```

**Important note about sudo + background tasks:** `sudo` requires a TTY to read passwords. Background terminal processes (`terminal(background=true)`) cannot prompt for passwords. Always run `sudo pacman -S ...` in a foreground terminal or the user's own shell.

If it fails with "exists in filesystem", the previous clean step is needed first.

### 4. Start the service

```bash
sudo systemctl enable --now ollama
# Verify it's running
systemctl status ollama --no-pager -l
# Check it responds
curl http://localhost:11434/api/tags
```

### 5. Verify GPU acceleration

After loading a model, confirm the GPU is actually being used:

```bash
# Check processor column — should show "GPU" or "CPU/GPU" not "100% CPU"
ollama ps

# Check VRAM usage — should be well above idle (~500 MiB idle, expect GBs with model loaded)
nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv,noheader

# Check detailed GPU utilization
nvidia-smi --query-gpu=utilization.gpu,temperature.gpu --format=csv,noheader
```

### 6. Check system hardware

Collect these to match a model to the user's hardware:

```bash
# CPU
cat /proc/cpuinfo | grep "model name" | head -1
nproc

# RAM
free -h

# GPU
lspci | grep -i vga
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader

# Disk
df -h /
```

### 6. Model Recommendation by VRAM

**VRAM heuristic (Q4_K_M quantization):**

| VRAM | Max model size | Example models |
|---|---|---|
| 4-6 GB | 3B-7B | Gemma 3:4b, Phi-4-mini, Qwen 3:4b |
| 8 GB | 7B-12B | Qwen 3:8b, Qwen 3.5:9b, Gemma 4:12b(tight), Phi-4:8b |
| 12 GB | 12B-24B | Mistral Nemo:12b, Qwen 3:14b, Llama 3.1:8b(FP16) |
| 24 GB+ | 30B-70B | Llama 3.1 70B (Q4), Qwen 3 32B, DeepSeek R1 32B |

**Always verify model tags exist on the Ollama library before recommending.** Use:

```bash
# Check available tags for a model
curl -sL "https://ollama.com/library/<model>/tags" | grep -oP 'href="/library/<model>:[^"]+"' | sed 's/.*://;s/"//' | sort -u
```

Never assume a size variant exists — especially for very new models like Qwen 3.6 (which only has 27B/35B, no 9B).

### 7. Pull and test

```bash
ollama pull <model>:<tag>
ollama run <model>:<tag>
```

## Common pitfalls

- **`/usr/share/ollama exists in filesystem`** during pacman install — stale directory from a previous install. Remove it with `sudo rm -rf /usr/share/ollama`.
- **`group ollama not removed because it has other members`** — the user's own account was in the ollama group. Remove them first: `sudo gpasswd -d <user> ollama`.
- **Recommending a tag that doesn't exist** — always verify tags via curl before suggesting. HTML scraping can produce garbage numbers; parse tag links carefully.
- **Model runs on CPU despite having an NVIDIA GPU** — this is the top issue on Arch. Diagnostic checklist:
  1. `ollama ps` — check if PROCESSOR column says "100% CPU"
  2. `nvidia-smi` — if VRAM usage is <500 MiB with a model loaded, it's CPU-only
  3. `ls /usr/lib/ollama/ | grep -E "cuda|vulkan|rocm"` — if no GPU libraries exist, you have the CPU build
  4. Fix: swap to `ollama-cuda` (or `ollama-rocm` / `ollama-vulkan`) via pacman
  5. After install, verify `ls /usr/lib/ollama/libggml-cuda.so` exists
  6. Restart Ollama: `sudo systemctl restart ollama`
- **`error: failed to init transaction (unable to lock database)`** during pacman — stale lock from an interrupted install. Fix: `sudo rm /var/lib/pacman/db.lck`. Verify no other pacman process is actually running first with `ps aux | grep pacman`.
- **sudo fails in background terminal processes** — sudo needs a TTY. Backgrounded terminal processes (`background=true` in terminal tool) cannot prompt for passwords. Use foreground terminal or have the user run the command directly.
- **Previous corrupted models** — `sudo rm -rf /var/lib/ollama/*` and start fresh.

## References

- **[model-sizes.md](references/model-sizes.md)** — current Ollama model sizes by VRAM tier
- **[ollama-library-urls.md](references/ollama-library-urls.md)** — verified tag URLs for common models

## Resources

- Ollama library: https://ollama.com/library
- Ollama GitHub: https://github.com/ollama/ollama
- Arch package: https://archlinux.org/packages/extra/x86_64/ollama/
