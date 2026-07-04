---
name: lordsiva-font-from-scratch
description: Workflow for creating the LordSiva Nerd Font Propo from JetBrainsMono base with selected MapleMono glyph replacements, and configuring Kitty to use it.
---

# LordSiva Font — From-Scratch Creation

Creates LordSiva Nerd Font Propo (4 variants) by taking JetBrainsMonoNerdFontPropo as the base and replacing specific glyphs with those from MapleMono.

**Font location:** `~/.fonts/LordSivaNerdFontPropo-{Regular,Bold,Italic,BoldItalic}.ttf`
**Backup location:** `~/.config/kitty/` (persistent backup, survives fontconfig resets)
**Base:** JetBrainsMonoNerdFontPropo (UPM=1000, TrueType)
**Source:** MapleMono TTF (UPM=1000, no scaling needed)
**Bold weight class:** 600 (Semi-Bold)
**Advance width:** 600 (matches both source and base)

## Step-by-step

### 1. Verify source materials are available

Base font: `~/.fonts/JetBrainsMonoNerdFontPropo-{Regular,Bold,Italic,BoldItalic}.ttf`

Download MapleMono TTF from GitHub:
```bash
curl -sL "https://github.com/subframe7536/maple-font/releases/download/v7.9/MapleMono-TTF.zip" -o /tmp/MapleMono-TTF.zip
unzip -qo /tmp/MapleMono-TTF.zip -d /tmp/MapleMono-TTF
```

### 2. Check UPM and glyph compatibility

Both fonts must be UPM=1000 (or apply scaling). Verify:
```bash
python3 -c "from fontTools.ttLib import TTFont; print('JBM:', TTFont('~/.fonts/JetBrainsMonoNerdFontPropo-Regular.ttf')['head'].unitsPerEm); print('MM:', TTFont('/tmp/MapleMono-TTF/MapleMono-Regular.ttf')['head'].unitsPerEm)"
```

Check glyph names match for target characters:
```python
chars = "!@#$%^&*[]\\,<>?/.:;'\"|"
jb_cmap = TTFont(jb_path).getBestCmap()
mm_cmap = TTFont(mm_path).getBestCmap()
for c in chars:
    cp = ord(c)
    print(f'{c}: JB="{jb_cmap[cp]}" MM="{mm_cmap[cp]}"')
```

### 3. Backup originals

```bash
mkdir -p ~/.fonts/bak
cp ~/.fonts/JetBrainsMonoNerdFontPropo-{Regular,Bold,Italic,BoldItalic}.ttf ~/.fonts/bak/
```

### 4. Run the build script

The build script copies specified glyphs from MapleMono into JetBrainsMono for each variant. For compound glyphs (colon, semicolon), they are kept as compounds since component glyphs (period, comma) are also being replaced.

Key points in the script:
- Iterates over `["Regular", "Bold", "Italic", "BoldItalic"]`
- Copies `glyf` entry and `hmtx` entry for each target glyph
- Compounds are copied as-is (they reference component glyphs by name, which exist in both fonts)
- Result is saved as `LordSivaNerdFontPropo-{variant}.ttf`

### 5. Rename font family

Change JetBrainsMono references to LordSiva:
- Name ID 0 (Copyright): Update to credit both JetBrains Mono and MapleMono
- Name ID 1 (Font Family): `"LordSiva Nerd Font Propo"`
- Name ID 2 (Subfamily): `Regular` / `Bold` / `Italic` / `Bold Italic`
- Name ID 4 (Full Name): `"LordSiva Nerd Font Propo {Subfamily}"`
- Name ID 6 (PostScript): `"LordSivaNerdFontPropo-{Variant}"` (no spaces!)
- Name ID 16 (Preferred Family): `"LordSiva Nerd Font Propo"`
- Name ID 17 (Preferred Subfamily): `Regular` / `Bold` / `Italic` / `Bold Italic`

Set `f['OS/2'].usWeightClass = 600` for Bold and BoldItalic.

### 6. Install and refresh cache

```bash
rm -rf ~/.cache/fontconfig/*
fc-cache -fv
fc-list | grep LordSiva
fc-match "LordSiva Nerd Font Propo"
```

### 7. Backup to Kitty config dir

```bash
cp ~/.fonts/LordSivaNerdFontPropo-*.ttf ~/.config/kitty/
```

This dual-location strategy keeps a working copy outside fontconfig-scanned paths.

### 8. Configure Kitty

Edit `~/.config/kitty/kitty.conf`:
```
font_family      LordSiva Nerd Font Propo
bold_font        auto
italic_font      auto
bold_italic_font auto
```

No `family=` wrapper needed — just the plain family name string.

### 9. Verify in Kitty

Reload Kitty config (or reopen terminal). The font should render with MapleMono-styled `! @ # $ % ^ & * [ ] \ , < > ? / . : ; ' " |` characters within an otherwise JetBrainsMono typeface.

## Characters replaced from MapleMono

All 22: `! @ # $ % ^ & * [ ] \ , < > ? / . : ; ' " |`

## Pitfalls

- **Glyph name mismatch** — If JetBrainsMono and MapleMono use different glyph names for the same codepoint, you need a name mapping step. Currently they match for all target chars.
- **Compound glyphs** — Colon and semicolon in MapleMono are compounds of period/comma. If you skip replacing period/comma, the compounds will reference JetBrainsMono's period/comma outlines and won't match MapleMono's style.
- **Copyright trimming** — The name table stores truncated strings on some platforms. Verify the full copyright text renders after renaming.
- **UPM mismatch** — If using a different source font, always check UPM and apply scale factor. MapleMono matches JetBrainsMono at UPM=1000, so no scale needed.
- **CFF vs TrueType** — This workflow assumes TrueType ('glyf' table). For CFF fonts, use a different approach (T2CharStringPen).
