# Mono → Propo Nerd Font Conversion

Session: 2026-06-30 — Converting MonoLisa Nerd Font Complete Mono to Propo.

## The Problem

A Nerd Font "Mono" variant has:
- Fixed advance widths (all glyphs same width, e.g. 640)
- `post.isFixedPitch = 1`
- `panose.bProportion = 9` (or 0)
- Family name containing "Mono"

A "Propo" (proportional) variant needs:
- Variable advance widths based on glyph ink bounds
- `post.isFixedPitch = 0`
- `panose.bProportion = 3` (proportional)
- Family name containing "Propo"
- Glyph outlines optionally scaled up (proportional fonts at the same point size feel smaller than mono)

## Key Techniques

### 1. Computing Proportional Widths from CFF Bounds

For CFF fonts (OTF with PostScript outlines):

```python
from fontTools.ttLib import TTFont

font = TTFont("font.otf")
top_dict = font["CFF "].cff.topDictIndex[0]
char_strings = top_dict.CharStrings
hmtx = font["hmtx"]

def get_cff_bounds(font, glyph_name):
    if glyph_name not in char_strings:
        return None
    try:
        return char_strings[glyph_name].calcBounds(
            char_strings[glyph_name].program
        )
    except:
        return None

def proportional_width(font, glyph_name, mono_width):
    bounds = get_cff_bounds(font, glyph_name)
    if bounds:
        ink_width = bounds[2] - bounds[0]
    else:
        ink_width = 0

    if ink_width <= 0:
        # Empty glyph (space, .notdef)
        if glyph_name == "space":
            return mono_width // 2  # ~50% of mono width
        return max(mono_width // 4, 200)

    # ink + side bearings, capped at mono width
    return min(ink_width + 100, mono_width)
```

### 2. Scaling CFF Glyph Outlines (fonttools)

CFF fonts use CharString programs — you cannot scale them with `glyf[].scale()`. Instead, use the fonttools pen system:

```python
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen

scale = 1.15

for name in glyph_order:
    if name not in char_strings:
        continue
    cs = char_strings[name]

    adv, lsb = hmtx[name]
    new_adv = round(adv * scale)

    # Create a new charstring via T2CharStringPen + TransformPen
    t2_pen = T2CharStringPen(new_adv, glyphSet=char_strings)
    transform = TransformPen(t2_pen, (scale, 0, 0, scale, 0, 0))
    cs.draw(transform)
    new_cs = t2_pen.getCharString()

    # *** CRITICAL *** Copy the .private reference from the original
    new_cs.private = cs.private

    char_strings[name] = new_cs
    hmtx[name] = (new_adv, round(lsb * scale))
```

**Without `new_cs.private = cs.private`**, saving the font raises:
`AttributeError: 'NoneType' object has no attribute 'nominalWidthX'`

### 3. Name Table Updates

Replace in name records:
- `"Nerd Font Mono"` → `"Nerd Font Propo"`
- `"Complete Mono"` → `"Complete Propo"`
- `"CompleteMono"` → `"CompletePropo"` (PostScript names have no spaces)

Use `name.removeNames()` + `name.setName()` for updates. Keep both platform 3 (Windows, lang=0x0409) and platform 1 (Mac, lang=0) entries.

### 4. Clearing Monospace Flags

```python
font["post"].isFixedPitch = 0
font["OS/2"].panose.bProportion = 3  # proportional
font["OS/2"].panose.bFamilyType = 2   # Latin Text
font["OS/2"].panose.bSerifStyle = 11  # Sans Serif
```

### 5. fsSelection Bits

| Style | Bits | Value |
|-------|------|-------|
| Regular | BIT 6 | 0b1000000 (64) |
| Bold | BIT 5 + BIT 6 | 0b1100000 (96) |
| Italic | BIT 0 + BIT 6 | 0b1000001 (65) |
| Bold Italic | BIT 0 + BIT 5 + BIT 6 | 0b1100001 (97) |

### 6. head.macStyle

```python
mac = font["head"].macStyle
mac = (mac | 0x01) if is_bold else (mac & ~0x01)     # bit 0 = bold
mac = (mac | 0x02) if is_italic else (mac & ~0x02)    # bit 1 = italic
font["head"].macStyle = mac
```

## The Scale Factor Question

When converting Mono → Propo, **glyph outlines should be scaled up** (e.g. 1.15x). Reason:

- In a mono font, every glyph gets the full fixed-width cell (e.g. 640 units). Narrow glyphs like `i` or `l` have lots of empty space around them.
- In a proportional font, each glyph gets only as much width as it needs. The same-size glyph outlines in narrower cells make the text feel sparse and "small."
- Scaling the outlines by ~1.15x makes the characters fill the proportional widths more naturally.

**Do NOT scale `head.unitsPerEm`** — that would cancel out the glyph scaling at render time. UPM should stay at the original value (e.g. 1000).

## Verification

```bash
# All 4 styles resolve
for style in Regular Italic Bold BoldItalic; do
  fc-list "MonoLisa Nerd Font Propo:style=$style"
done

# Sample proportional widths from Python
python3 -c "
from fontTools.ttLib import TTFont
f=TTFont('font.otf')
h=f['hmtx']
c=f.getBestCmap()
for ch in ' Hello iMW':
    g=c.get(ord(ch))
    if g: print(ch, h[g][0])
"
```
