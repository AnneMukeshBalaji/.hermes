# Ghostty Ligature Troubleshooting
- If ligatures work in editors (Neovim) but not the terminal shell prompt, the terminal's font rendering engine is working, but the shell environment is interfering.
- Use Monospaced Nerd Fonts (e.g., JetBrainsMono Nerd Font). Avoid "Propo" (proportional) variants; they break character width alignment and mangle ligatures.
- Configuration in `~/.config/ghostty/config`:
  font-family = "JetBrainsMono Nerd Font"
  font-feature = "calt=1,liga=1"
- If it still fails, the terminal buffer itself might not be supporting the ligature joiner sequence. Verify rendering with:
  `echo -e "\xE2\x87\x92 \xE2\x89\xA0 \xE2\x89\xA4 \xE2\x89\xA5 \xE2\x86\x92"`
