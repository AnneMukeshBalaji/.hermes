---
name: custom-font-setup
title: Custom Font Creation and Kitty Configuration
description: Reusable workflow for building a patched font (e.g., merging GoogleSansCode glyphs into JetBrainsMono Nerd Font Propo) and configuring the Kitty terminal to use it, including remote‑control enablement and common pitfalls.
---

## Overview
This skill describes a reusable workflow for creating a custom patched font (e.g., merging glyphs from GoogleSansCode into JetBrainsMono Nerd Font Propo) and configuring the Kitty terminal to use it automatically.

## Trigger
- **When** a user requests a custom font that combines glyphs from multiple source fonts and wants Kitty to render it without manual steps.

## Steps
1. **Prepare source fonts** — ensure the original Nerd Font files exist under `~/.fonts/`.
2. **Copy desired glyphs** using a FontForge script. The script should:
   - Open the source JetBrainsMono font and the source GoogleSansCode font.
   - Copy the glyphs `A‑Z`, `a‑z`, `{`, `}`, `(`, `)` from GoogleSansCode into JetBrainsMono.
   - Set the family name to `CustomFont Nerd Font Propo` (or a user‑chosen name).
   - Generate the four style variants (`Regular`, `Bold`, `Italic`, `BoldItalic`).
3. **Fix the name table** with `fonttools/ttx` to remove any leftover family names (e.g., "JetBrainsMono Nerd Font Propo").  
   **Critical: Mac platform langID must be 0, not 0x0409.** See `custom-font-creation` skill (`references/font_rename_technique.md`) for the full name table technique.
4. **Refresh fontconfig** — a full purge is most reliable:
   ```bash
   rm -rf ~/.cache/fontconfig/*
   fc-cache -fv
   ```
5. **Update `kitty.conf`** — use the **simple format** (more reliable than `family="..." style="..."`):
   ```conf
   # BEGIN_CUSTOM_KITTY_FONTS
   font_family      LordSiva Nerd Font Propo
   bold_font        auto
   italic_font      auto
   bold_italic_font auto
   # END_CUSTOM_KITTY_FONTS
   ```
6. **Enable remote control (optional but recommended)**:
   - Add `allow_remote_control yes` and `listen_on unix:/tmp/kitty-control.sock` to `kitty.conf`.
   - Use `kitty @ --to=unix:/tmp/kitty-control.sock load-config ~/.config/kitty/kitty.conf` to reload config without restarting Kitty.
7. **If remote control is not available**, restart Kitty (or start a new instance) so it reads the updated configuration.

## Pitfalls & Tips
- **UPM scaling is THE #1 failure mode**: When source fonts have different `unitsPerEm` values (e.g. GoogleSansCode at UPM=2000 vs JetBrainsMono at UPM=1000), FontForge's copy/paste does NOT scale outlines or advance widths. Pasted glyphs land at 2x size unless you manually apply `font.transform([0.5, 0, 0, 0.5, 0, 0])` and fix `glyph.width`. Check both fonts first with `fontforge` or `fonttools`.
- **Mac langID must be 0 for Mac platform**: Platform 1 (Mac) uses Mac language codes where 0 = English. Using 0x0409 (a Windows LCID) creates an invalid font that Kitty silently refuses. Platform 3 (Windows) correctly uses 0x0409 for English US.
- **Simple Kitty config is more reliable**: Prefer `font_family Name` with `bold_font auto` over `family="Name" style="Style"` format which can cause font-matching issues.
- **Full cache purge needed**: `rm -rf ~/.cache/fontconfig/*` then `fc-cache -fv` is more reliable than `fc-cache -f` alone.
- **Name table leftovers**: Kitty picks the first family name it finds. Ensure the old JetBrainsMono family records are fully removed; otherwise Kitty will fall back to the old font.
- **Remote‑control socket missing**: `kitty @` fails with "open /dev/tty". Add `allow_remote_control yes` and `listen_on` to create a control socket.
- **Running without a DISPLAY**: Starting Kitty in a headless script may emit GLFW errors; these are harmless for config loading.
- **Font cache not refreshed**: Always run `fc-cache -f` after generating the TTFs.
- **Restart required**: If you cannot enable remote control, closing the current Kitty window and launching a new one is the simplest way to apply the new font.

## References
- `references/verification_script.md` — a minimal script that starts a temporary Kitty with a control socket, reloads the config, and verifies Fontconfig sees the custom font.

## Versioning
- Added 2026‑06‑28 based on a real‑world troubleshooting session where the custom font was built, name tables were cleaned, and Kitty remote control was enabled.

---
*Generated automatically to capture the workflow and pitfalls discovered in the session.*