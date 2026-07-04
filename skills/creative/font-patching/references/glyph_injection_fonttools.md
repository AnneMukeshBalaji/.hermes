# Glyph Injection with fontTools — LordSiva Font Update

## Context

**Font:** LordSiva Nerd Font Propo (4 variants: Regular, Bold, Italic, BoldItalic)
**Base:** JetBrainsMonoNerdFont (MONO, UPM=1000) 
**Source glyphs:** MapleMono-Regular.ttf (UPM=1000) + GoogleSansCodeNerdFontMono-Regular.ttf (UPM=2000)
**Target width:** 600 (matches JetBrainsMono MONO advance width)
**Output dir:** `~/.fonts/` (font files directly, with backup in `~/Downloads/lord_siva_bak/`)

## Characters injected

| Source | Characters | Type |
|--------|-----------|------|
| MapleMono | `! @ # $ % ^ & * ? , . \| \ / \`` | All simple glyphs |
| GoogleSansCode | `;` | Compound glyph (period + comma components) |
| GoogleSansCode | `( ) { }` | All simple glyphs |

## Key techniques used

### 1. Checking glyph structure

```python
from fontTools.ttLib import TTFont

f = TTFont("font.ttf")
cmap = f.getBestCmap()
g = f['glyf'][cmap[ord(';')]]

# numberOfContours > 0  = simple glyph (outlines directly stored)
# numberOfContours == -1 = compound glyph (made of component glyphs)
print(g.numberOfContours)

if hasattr(g, 'components'):
    for comp in g.components:
        print(f"  {comp.glyphName} offset=({comp.x},{comp.y})")
```

### 2. Compound glyph decomposition (for semicolon `;`)

The semicolon in Nerd-font-patched fonts is compound: `period` + `comma` with a Y-offset on `period`. Decompose, apply component offsets, then scale:

```python
SCALE = 1000/2000  # when source UPM=2000, target UPM=1000

all_coords = []
all_end_pts = []
all_flags = []
offset = 0

g_comp = glyf_s[gn_s]
for comp in g_comp.components:
    sub = glyf_s[comp.glyphName]
    coords = list(sub.coordinates)
    transformed = [(int((x + comp.x) * SCALE), int((y + comp.y) * SCALE)) for x, y in coords]
    all_coords.extend(transformed)
    all_end_pts.extend([e + offset for e in sub.endPtsOfContours])
    all_flags.extend(sub.flags)
    offset += len(coords)
```

### 3. Weight class modification

```python
font['OS/2'].usWeightClass = 600  # changed Bold from 700→600
```

### 4. Processing all 4 variants in a loop

Iterate over `["LordSivaNerdFontPropo-Regular.ttf", "Bold.ttf", "Italic.ttf", "BoldItalic.ttf"]`, open each with TTFont, modify `glyf` and `hmtx` tables, then `font.save()`.

## Pitfalls encountered

- **Compound glyphs break simple copy**: Copying GlyphCoordinates directly from a compound glyph (numberOfContours=-1) fails because compound glyphs store component references, not outlines. Must decompose first.
- **GSC UPM=2000 vs target UPM=1000**: All coordinates and metrics must be scaled by 0.5×. The existing `build_fonttools.py` already handles this for A-Z/a-z.
- **Backup in ~/.fonts pollutes fontconfig**: When making a backup inside `~/.fonts/`, it gets picked up by `fc-cache` and shows duplicate font entries. Better to backup outside `~/.fonts/`.
- **fc-cache -f required** after every modification to make fontconfig see the changes.
