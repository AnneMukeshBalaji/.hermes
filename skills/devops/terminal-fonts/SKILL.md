---
name: terminal-fonts
description: "Troubleshooting font rendering, ligatures, and terminal configuration."
---

# Terminal Font Troubleshooting

Strategies for managing font rendering, ligatures, and terminal-specific visual issues (Ghostty, Alacritty, Kitty).

## Ligatures
Ligatures in terminals are fragile. If they work in editors (Neovim) but not the shell:
1. **Font Variant:** Avoid "Propo" (proportional) fonts. They break character width alignment required by terminals. Use the standard monospaced Nerd Font variant.
2. **Configuration:** Explicitly enable in `config`: `font-feature = "liga"`.
3. **Environment:** If they work in `cat`/`echo` but not the prompt, check the prompt theme (e.g., Starship/Powerlevel10k). Prompt plugins often override terminal font settings or use glyphs that don't support ligatures.
4. **Multiplexers:** In `tmux`/`zellij`, ensure passthrough is enabled: `set -g allow-passthrough on`.

## Verification
Use the shell escape test to check if the renderer is capable:
`echo -e "\xE2\x87\x92 \xE2\x89\xA0 \xE2\x89\xA4 \xE2\x89\xA5 \xE2\x86\x92"`

## References
- references/ghostty-ligatures.md: Specific session findings on shell vs editor rendering.
