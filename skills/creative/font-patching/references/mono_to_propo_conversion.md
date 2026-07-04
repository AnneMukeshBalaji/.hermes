# Mono → Propo Conversion Script

Full script for converting a MonoLisa Nerd Font Complete Mono (4 OTF variants) to a proportional Propo variant. Works for CFF-based OTF fonts; adapt `compute_proportional_width` for TrueType (glyf) fonts.

## Prerequisites

```bash
pip install fonttools
```

## Script

```python
#!/usr/bin/env python3
"""Convert a Nerd Font from Mono (monospace) to Propo (proportional).

Processes all 4 variants: Regular, Italic, Bold, Bold Italic.
Handles CFF-based OTF fonts (PostScript outlines).
"""

import os
from fontTools.ttLib import TTFont

SRC_DIR = os.path.expanduser("~/.fonts")
DST_DIR = SRC_DIR

VARIANTS = [
    ("Regular", "Regular", "Regular", 400),
    ("Regular Italic", "Italic", "Italic", 400),
    ("Bold", "Bold", "Bold", 700),
    ("Bold Italic", "BoldItalic", "BoldItalic", 700),
]


def get_cff_bounds(font, glyph_name):
    """Get bounding box for a CFF glyph."""
    top_dict = font["CFF "].cff.topDictIndex[0]
    cs = top_dict.CharStrings
    if glyph_name not in cs:
        return None
    try:
        return cs[glyph_name].calcBounds(cs[glyph_name].program)
    except:
        return None


def compute_proportional_width(font, glyph_name, mono_width):
    """Compute proportional advance width for a glyph."""
    bounds = get_cff_bounds(font, glyph_name)
    if bounds:
        ink = bounds[2] - bounds[0]  # xMax - xMin
    else:
        ink = 0

    if ink <= 0:
        # Space-like glyphs: ~1/3 of mono width
        if "space" in glyph_name or "nbspace" in glyph_name:
            return max(mono_width // 3, 250)
        return max(mono_width // 4, 200)

    proportional = min(ink + 100, mono_width)
    return max(proportional, 220)


def fix_name(text, style_ps):
    """Replace Mono→Propo in name strings (preserving foundry name)."""
    result = text
    result = result.replace("Complete Mono", "Complete Propo")
    result = result.replace("Nerd Font Mono", "Nerd Font Propo")
    result = result.replace("CompleteMono", "CompletePropo")
    result = result.replace("-Regular", f"-{style_ps}")
    return result


def convert_variant(src_name, dst_style, style_ps, weight_class):
    family_part = src_name.split(" Nerd Font")[0]  # e.g. "MonoLisa Regular"
    src = os.path.join(SRC_DIR, f"MonoLisa {src_name} Nerd Font Complete Mono.otf")
    dst = os.path.join(DST_DIR, f"MonoLisa {src_name} Nerd Font Complete Propo.otf")

    if not os.path.exists(src):
        print(f"  SKIP: {src} not found")
        return

    print(f"  Loading: {os.path.basename(src)}")
    font = TTFont(src)
    name = font["name"]
    hmtx = font["hmtx"]

    # --- 1. Proportional widths ---
    mono_width = max(w for w, _ in hmtx.metrics.values())
    print(f"  Mono base: {mono_width}")
    for gn in list(hmtx.metrics.keys()):
        adv, lsb = hmtx[gn]
        hmtx[gn] = (compute_proportional_width(font, gn, mono_width), lsb)

    # --- 2. Name table ---
    for rec in name.names:
        try:
            txt = rec.toUnicode()
        except:
            continue
        nid = rec.nameID
        if nid in (1, 2, 4, 6, 16, 17, 18):
            new_txt = fix_name(txt, style_ps)
            if nid in (2, 17):
                new_txt = dst_style
            if new_txt != txt:
                name.removeNames(nameID=nid, platformID=rec.platformID,
                                platEncID=rec.platEncID, langID=rec.langID)
                name.setName(new_txt, nid, rec.platformID, rec.platEncID, rec.langID)

    print(f"  Family: {name.getDebugName(1)}")

    # --- 3. Monospace flags off ---
    font["post"].isFixedPitch = 0
    font["OS/2"].panose.bFamilyType = 2
    font["OS/2"].panose.bSerifStyle = 11
    font["OS/2"].panose.bProportion = 3

    is_bold = "Bold" in dst_style
    is_italic = "Italic" in dst_style
    if is_bold and is_italic:
        font["OS/2"].fsSelection = 0b1100001
    elif is_bold:
        font["OS/2"].fsSelection = 0b1100000
    elif is_italic:
        font["OS/2"].fsSelection = 0b1000001
    else:
        font["OS/2"].fsSelection = 0b1000000

    mac = font["head"].macStyle
    mac = (mac | 0x01) if is_bold else (mac & ~0x01)
    mac = (mac | 0x02) if is_italic else (mac & ~0x02)
    font["head"].macStyle = mac
    font["OS/2"].usWeightClass = weight_class

    print(f"  Saving: {os.path.basename(dst)}")
    font.save(dst)
    font.close()


def main():
    for src_name, dst_style, style_ps, weight in VARIANTS:
        print(f"\n=== {src_name} -> {dst_style} ===")
        convert_variant(src_name, dst_style, style_ps, weight)
    print("\nDone!")


if __name__ == "__main__":
    main()
```

## Usage

```bash
cd ~/.fonts
python3 convert_mono_to_propo.py
```

Then refresh font cache:

```bash
fc-cache -fv ~/.fonts/
fc-list | grep "Nerd Font Propo"
```

## Adapting for other fonts

- Change `SRC_DIR` if fonts are elsewhere
- Change `"MonoLisa"` in the path-building logic to match your font name
- For TrueType fonts (glyf table), replace `get_cff_bounds()` with the TrueType version using `glyf[gn].xMax - glyf[gn].xMin`
- Adjust `VARIANTS` to match your font's filename scheme (different foundries use different naming conventions)

## Verification

```python
from fontTools.ttLib import TTFont
f = TTFont("output.otf")
hmtx = f['hmtx']
cmap = f.getBestCmap()
for char in "Hello iii MMM ...":
    g = cmap.get(ord(char))
    if g:
        print(f"'{char}': width={hmtx[g][0]}")
f.close()
```
