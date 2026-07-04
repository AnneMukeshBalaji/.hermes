# Font File Management Strategy

Custom terminal fonts are fragile — they can stop working after fontconfig cache purges,
system updates, or accidental overwrites. A robust two-location strategy prevents
downtime and makes recovery instant.

## The Dual-Location Pattern

```
~/.fonts/                          ← Active installation (fontconfig discovery)
  LordSivaNerdFontPropo-Regular.ttf
  LordSivaNerdFontPropo-Bold.ttf
  LordSivaNerdFontPropo-Italic.ttf
  LordSivaNerdFontPropo-BoldItalic.ttf

~/.config/kitty/                   ← Persistent backup (terminal config directory)
  CustomFont.ttf                   ← Known-good fallback font
  LordSivaNerdFontPropo-Regular.ttf
  LordSivaNerdFontPropo-Bold.ttf
  LordSivaNerdFontPropo-Italic.ttf
  LordSivaNerdFontPropo-BoldItalic.ttf
```

### Active copy (`~/.fonts/`)

This is the copy that fontconfig scans. Fonts are registered here for all
applications to discover. This directory is the one that gets rebuilt on every
font iteration.

**Vulnerability:** `fc-cache -f` or `rm -rf ~/.cache/fontconfig/*` does not touch
this directory, but if you edit/replace files here and run `fc-cache`, the old
entries may still shadow new ones until a full purge.

### Backup copy (`~/.config/kitty/`)

Kitty's configuration directory is a safe storage because:
- It is never touched by fontconfig operations
- It survives `~/.fonts/` rewrites and accidental deletions
- Kitty picks up font files from its config directory by path reference
- The files serve as ground-truth originals during iterative development

**Never `rm` or overwrite this directory** without explicit user intent.

## Recovery from a broken font

1. Exit Kitty completely
2. Copy backup from `~/.config/kitty/` back to `~/.fonts/`
3. `rm -rf ~/.cache/fontconfig/*`
4. `fc-cache -fv`
5. Restart Kitty

## When to update the backup

Only update `~/.config/kitty/` after verifying the new font renders correctly
in the terminal. This way the backup always holds a known-good state.

## Build output directory

Use a separate build output directory (e.g. `~/Downloads/CustomFont/`) for
font generation. Copy proven builds to both locations:

```bash
# After verifying the font renders correctly:
cp ~/Downloads/CustomFont/LordSivaNerdFontPropo-*.ttf ~/.fonts/
cp ~/Downloads/CustomFont/LordSivaNerdFontPropo-*.ttf ~/.config/kitty/
rm -rf ~/.cache/fontconfig/* && fc-cache -fv
```
