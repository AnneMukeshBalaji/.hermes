---
name: lord-siva-font-update
description: Workflow for adding new glyphs to LordSivaNerdFont Propo from a source font.
---

# LordSiva Font Glyph Update

Add new glyphs from an external source font into all 4 LordSivaNerdFontPropo variants.

**Font location:** `~/.fonts/LordSivaNerdFontPropo-{Regular,Bold,Italic,BoldItalic}.ttf`

**UPM:** LordSiva = 1000, **Target width:** 600

## Process

1. **Download source font** to `~/.fonts/`
2. **Check glyphs** in both source and target:
   ```python
   from fontTools.ttLib import TTFont
   src = TTFont("~/path/to/source.ttf")
   dst = TTFont("~/.fonts/LordSivaNerdFontPropo-Regular.ttf")
   cmap_s, cmap_d = src.getBestCmap(), dst.getBestCmap()
   ## Process

   1. **Download source font** to `~/.fonts/`
   2. **Check glyphs** in both source and target:
   3. **Check if compound glyphs** — if `numberOfContours <= 0` or has `components`, decompose first.
   4. **Scale** if UPM differs (e.g. GSC UPM=2000 → scale 0.5×)
   5. **Write update script** copying glyphs → all 4 variants
   6. **Run** `python3 script.py`
   7. **Backup** originals first (`mkdir -p ~/.fonts/bak && cp LordSivaNerdFontPropo-*.ttf bak/`)
   8. **Check metadata** on all variants — especially `usWeightClass` on Bold/BoldItalic:
      ```python
      from fontTools.ttLib import TTFont
      for v in ['Regular', 'Bold', 'Italic', 'BoldItalic']:
          f = TTFont(f'LordSivaNerdFontPropo-{v}.ttf')
          print(f'{v}: weightClass={f["OS/2"].usWeightClass}')
          f.close()
      ```
      If you need a lighter bold, set to 600 (Semi-Bold):
      ```python
      f['OS/2'].usWeightClass = 600
      ```
   9. **Clean up** source font + temp scripts
   10. **Refresh** `fc-cache -f`

## Common source fonts used
- **MapleMono** — UPM=1000, simple glyphs, no scaling needed
- **GoogleSansCode Nerd Font Mono** — UPM=2000, some compound glyphs, 0.5× scale
- **JetBrainsMono Nerd Font** — UPM=1000, MONO variant for base

## Pitfalls
- Compound glyphs (`numberOfContours = -1`) need manual decomposition via component iteration
- GoogleSansCode's `;` is a compound of `period` + `comma` with offset
- Always check UPM difference before copying coordinates
- `hermes config/kitty/` fonts are the user's backups — never touch them
