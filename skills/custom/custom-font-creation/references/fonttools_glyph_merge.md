# Fonttools glyph merge (alternative to FontForge)

When FontForge's `generate()` produces fonts that don't render (e.g. corrupted `glyf` table, wrong UPM scaling, or broken name tables), use fonttools to manipulate the font in place — copying the base font file and surgically replacing only the glyph tables that need changing.

## Why fonttools instead of FontForge

| Issue | FontForge | fonttools |
|-------|-----------|-----------|
| UPM scaling | Manual transform needed after paste | Manual scaling of coordinates/widths |
| Table structure | `generate()` rebuilds tables, can corrupt | Original table structure preserved |
| Name table | Leaves stale entries, case-sensitive keys | Full control via `NameRecord` |
| Generation artifacts | Known issues with `glyf` program bytecode | No generation — direct table manipulation |

## The approach: copy base, replace glyphs

```python
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates
import shutil

shutil.copy2(base_font_path, output_path)  # start from perfect copy
base = TTFont(output_path)
src = TTFont(source_font_path)

SCALE = base['head'].unitsPerEm / src['head'].unitsPerEm

for code in [ord(c) for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz']:
    src_glyph_name = src.getBestCmap()[code]
    dst_glyph_name = base.getBestCmap()[code]
    src_glyph = src['glyf'][src_glyph_name]

    if not hasattr(src_glyph, 'coordinates') or src_glyph.numberOfContours <= 0:
        continue  # skip composite or empty glyphs

    # Scale coordinates
    new_coords = GlyphCoordinates()
    for x, y in src_glyph.coordinates:
        new_coords.append((int(x * SCALE), int(y * SCALE)))

    # Build new glyph preserving all structure
    new_glyph = Glyph()
    new_glyph.numberOfContours = src_glyph.numberOfContours
    new_glyph.coordinates = new_coords
    new_glyph.endPtsOfContours = src_glyph.endPtsOfContours[:]
    new_glyph.flags = src_glyph.flags[:]
    # CRITICAL: when scaling glyphs (SCALE != 1.0), use empty Program().
    # The source hinting is calibrated for the source UPM and will be
    # wrong at the target UPM, corrupting rendering.
    if scale == 1.0 and hasattr(src_glyph, 'program') and src_glyph.program is not None:
        new_glyph.program = src_glyph.program
    else:
        new_glyph.program = Program()

    # Scale bounding box
    if src_glyph.xMin is not None:
        new_glyph.xMin = int(src_glyph.xMin * SCALE)
        new_glyph.yMin = int(src_glyph.yMin * SCALE)
        new_glyph.xMax = int(src_glyph.xMax * SCALE)
        new_glyph.yMax = int(src_glyph.yMax * SCALE)

    base['glyf'][dst_glyph_name] = new_glyph

    # Scale advance width and side bearings
    old_width, old_lsb = src['hmtx'][src_glyph_name]
    base['hmtx'][dst_glyph_name] = (int(old_width * SCALE), int(old_lsb * SCALE))
```

## Key: the Glyph() constructor requirements

When creating a new `_g_l_y_f.Glyph()` to replace an existing glyph:

| Attribute | Required? | Source |
|-----------|-----------|--------|
| `numberOfContours` | Yes | `src_glyph.numberOfContours` |
| `coordinates` | Yes | Scaled from src |
| `endPtsOfContours` | Yes | Copy list `src_glyph.endPtsOfContours[:]` |
| `flags` | Yes | Copy list `src_glyph.flags[:]` |
| `program` | **Always set** | Use `Program()` for scaled glyphs |
| `xMin/yMin/xMax/yMax` | Recommended | Scale from src |

Omitting `program` causes `AttributeError: 'Glyph' object has no attribute 'program'` on save.

**CRITICAL: when scaling glyphs from a different-UPM source font, set `program = Program()` (empty) rather than copying the source's program.** The original hinting instructions are calibrated for the source UPM (e.g. 2000) and are invalid at the target UPM (e.g. 1000). Copying them produces corrupted glyph rendering.

```python
from fontTools.ttLib.tables.ttProgram import Program
# Always use empty program for scaled glyphs:
new_glyph.program = Program()
```

Omitting `endPtsOfContours[:]` reference (using shared list) causes corruption since fonttools mutates it in-place during compile.

## Monospace flags for terminal fonts

When the output font is intended for a terminal emulator (Kitty, etc.), set these two flags **after** glyph copying but **before** save:

```python
# Mark as monospace
jet['post'].isFixedPitch = 1

# Set OS/2 panose proportion to monospaced (9)
jet['OS/2'].panose.bProportion = 9

# Optional: also set family type
jet['OS/2'].panose.bFamilyType = 2  # Latin Text
jet['OS/2'].panose.bSerifStyle = 0  # Sans Serif
```

Without `isFixedPitch=1` and `bProportion=9`, terminal emulators may silently fall back to a different font even though fontconfig resolves correctly.
