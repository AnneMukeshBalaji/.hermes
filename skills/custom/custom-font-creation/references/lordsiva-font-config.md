# LordSiva Nerd Font Propo — Project Configuration

## Overview

LordSiva is a custom Nerd Font based on **JetBrainsMonoNerdFont**, converted to a
proportional (Propo) variant and with specific glyphs replaced from MapleMono.
Created for use as a terminal/UI font on Arch Linux.

## Parameters

| Parameter   | Value                           |
|-------------|---------------------------------|
| Base font   | JetBrainsMonoNerdFont            |
| Output name | LordSiva Nerd Font Propo         |
| PS prefix   | LordSivaNerdFontPropo            |
| UPM         | 1000                             |
| Target width| 600 (mono advance of JBMono)     |
| Bold weight | 600 (Semi-Bold, not 700)         |

## Variants

| Style file                              | NameID 1 (Family)              | NameID 2 (SubFamily) | NameID 6 (PS Name)                         |
|-----------------------------------------|--------------------------------|----------------------|--------------------------------------------|
| LordSivaNerdFontPropo-Regular.ttf       | LordSiva Nerd Font Propo       | Regular              | LordSivaNerdFontPropo-Regular              |
| LordSivaNerdFontPropo-Bold.ttf          | LordSiva Nerd Font Propo       | Bold                 | LordSivaNerdFontPropo-Bold                 |
| LordSivaNerdFontPropo-Italic.ttf        | LordSiva Nerd Font Propo       | Italic               | LordSivaNerdFontPropo-Italic               |
| LordSivaNerdFontPropo-BoldItalic.ttf    | LordSiva Nerd Font Propo       | Bold Italic          | LordSivaNerdFontPropo-BoldItalic           |

## Creation Approaches

### Approach A: Mono-to-Propo conversion (original)

Uses **Option C (Mono → Propo conversion)** from the umbrella `custom-font-creation` skill:

1. Copy JetBrainsMonoNerdFont-{Regular,Bold,Italic,BoldItalic}.ttf to new filenames
2. Update name table ("JetBrainsMono Nerd Font" → "LordSiva Nerd Font Propo")
3. Compute proportional advance widths from glyph ink bounds (capped at 600)
4. Clear monospace flags: `isFixedPitch=0`, `panose.bProportion=3`
5. Set Bold weight class to 600 on Bold + BoldItalic variants
6. Update `fsSelection` and `head.macStyle` per style
7. Full fontconfig purge

### Approach B: Selective glyph replacement from MapleMono (current)

Uses **Option D (Selective glyph replacement)** from the umbrella skill. Starts
from JetBrainsMonoNerdFontPropo (already proportional) and replaces 22 specific
characters with MapleMono glyphs.

**Source font:** MapleMono v7.9 TTF (https://github.com/subframe7536/maple-font)

**Replaced characters:**
```
! @ # $ % ^ & * [ ] \ , < > ? / . : ; ' " |
```
All in both Regular and Bold variants at `~/.fonts/bak/JetBrainsMonoNerdFontPropo-*.ttf`.

**Key details:**
- UPM=1000 in both fonts → no scaling needed
- All 22 chars map to the same glyph names in both fonts → direct copy from `glyf` table
- Colon (:) and semicolon (;) are compound glyphs in Regular/Bold (built from period + period, comma + period). Since period and comma are also being replaced, compounds are kept as-is — no decomposition needed. In Italic/BoldItalic, colon/semicolon are simple glyphs.
- The base font's nameID 1 uses the short form "JetBrainsMono NFP" while nameID 16 uses the long form "JetBrainsMono Nerd Font Propo". Both must be updated during rename.

**Build script pattern:**
```python
from fontTools.ttLib import TTFont
import shutil

CHARS = "!@#$%^&*[]\\,<>?/.:;'\"|"
VARIANTS = ["Regular", "Bold", "Italic", "BoldItalic"]

for variant in VARIANTS:
    shutil.copy2(f"bak/JetBrainsMonoNerdFontPropo-{variant}.ttf",
                 f"LordSivaNerdFontPropo-{variant}.ttf")

    src = TTFont(f"MapleMono-{variant}.ttf")
    dst = TTFont(f"LordSivaNerdFontPropo-{variant}.ttf")

    src_cmap = src.getBestCmap()
    dst_cmap = dst.getBestCmap()

    for c in CHARS:
        cp = ord(c)
        if cp not in src_cmap or cp not in dst_cmap:
            continue
        src_gn = src_cmap[cp]
        dst_gn = dst_cmap[cp]
        dst['glyf'][dst_gn] = src['glyf'][src_gn]
        dst['hmtx'][dst_gn] = src['hmtx'][src_gn]

    dst.save(f"LordSivaNerdFontPropo-{variant}.ttf")
    src.close()
    dst.close()
```

**Rename script pattern:**
```python
from fontTools.ttLib import TTFont

FAMILY = "LordSiva Nerd Font Propo"
STYLES = {"Regular": ("Regular", "Regular", 400),
          "Bold": ("Bold", "Bold", 600),
          "Italic": ("Italic", "Italic", 400),
          "BoldItalic": ("Bold Italic", "BoldItalic", 600)}

for variant, (subfamily, ps_sfx, weight) in STYLES.items():
    f = TTFont(f"LordSivaNerdFontPropo-{variant}.ttf")
    f['OS/2'].usWeightClass = weight

    for r in f['name'].names:
        old = r.toUnicode()
        if r.nameID == 0:
            r.string = "LordSiva is based on JetBrains Mono (Copyright ...) and MapleMono."
        elif r.nameID == 1:
            r.string = FAMILY
        elif r.nameID == 2:
            r.string = subfamily
        elif r.nameID == 4:
            r.string = f"{FAMILY} {subfamily}"
        elif r.nameID == 6:
            r.string = f"LordSivaNerdFontPropo-{ps_sfx}"
        elif r.nameID == 16:
            r.string = FAMILY
        elif r.nameID == 17:
            r.string = subfamily

    f.save(f"LordSivaNerdFontPropo-{variant}.ttf")
    f.close()
```

## Verification

```bash
# All 4 styles resolve
for style in Regular Bold Italic "Bold Italic"; do
  fc-match "LordSiva Nerd Font Propo:style=$style"
done

# Check weight class
python3 -c "
from fontTools.ttLib import TTFont
for v in ['Regular', 'Bold', 'Italic', 'BoldItalic']:
    f = TTFont(f'LordSivaNerdFontPropo-{v}.ttf')
    print(f'{v}: weight={f[\"OS/2\"].usWeightClass}')
    f.close()
"
```

## History

- 2025-04-24: Initially created via Mono-to-Propo conversion from JetBrainsMonoNerdFont
- 2026-06-30: Rebuilt from JetBrainsMonoNerdFontPropo with 22 MapleMono glyph replacements
  (chars: ! @ # $ % ^ & * [ ] \\ , < > ? / . : ; ' " |)
