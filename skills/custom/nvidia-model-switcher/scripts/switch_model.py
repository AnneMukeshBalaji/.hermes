#!/usr/bin/env python3
"""
NVIDIA Model Switcher - Slash command handlers for quick model switching.
Place this in ~/.hermes/skills/custom/nvidia-model-switcher/scripts/switch_model.py
"""

import sys
import yaml
from pathlib import Path

# Working models on NVIDIA NIM (tested)
MODELS = {
    "nemotron": "nvidia/nemotron-3-ultra-550b-a55b",
    "deepseek": "deepseek-ai/deepseek-v4-pro",
    "minimax": "minimaxai/minimax-m3",
    "stepfun": "stepfun-ai/step-3.7-flash",
    "kimi": "moonshotai/kimi-k2.6",
    "mistral": "mistralai/mistral-medium-3.5-128b",
    "glm": "z-ai/glm-5.1",
    "qwen": "qwen/qwen3.5-397b-a17b",
}

CONFIG_PATH = Path.home() / ".hermes" / "config.yaml"

def switch_model(alias: str) -> str:
    """Switch the default model in config.yaml"""
    if alias not in MODELS:
        available = ", ".join(MODELS.keys())
        return f"❌ Unknown model '{alias}'. Available: {available}"
    
    model_name = MODELS[alias]
    
    # Read current config
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
    
    # Update model.default
    if 'model' not in config:
        config['model'] = {}
    config['model']['default'] = model_name
    
    # Write back
    with open(CONFIG_PATH, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    return f"✅ Switched to **{model_name}**\n\nRun `/reset` to apply the change."

def list_models() -> str:
    """Show all available models"""
    lines = ["**Available NVIDIA NIM Models:**\n"]
    for alias, model in MODELS.items():
        lines.append(f"  `/{alias}` → `{model}`")
    lines.append("\n**Usage:** Type `/model-<alias>` then `/reset`")
    return "\n".join(lines)

def main():
    if len(sys.argv) < 2:
        print(list_models())
        return
    
    command = sys.argv[1].lstrip('/')
    if command == "model-list":
        print(list_models())
    elif command.startswith("model-"):
        alias = command.replace("model-", "")
        print(switch_model(alias))
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()