---
name: font-patching
description: Techniques for font modification, including copying glyphs between fonts using FontForge or fontTools Python scripting.
---

# Font Patching

Use this skill for programmatic modification of TTF/OTF files. Two Python approaches:
- **fontTools** (preferred, `from fontTools.ttLib import TTFont`) — direct table manipulation, more reliable output, handles compound glyphs
- **FontForge** (`import fontforge`) — higher-level API, can produce broken output with `generate()`

**Rule of thumb:** Use fontTools for precision work (glyph injection, metadata changes). Use FontForge for whole-font batch operations.

> **Note:** See `references/google_sans_code_merge.md` for the original CustomFont merge session.
> See `references/glyph_injection_fonttools.md` for the LordSiva font update workflow using fontTools.

---

## Workflow A: fontTools (Preferred)

### Core pattern — copy simple glyphs from one font to another

```python
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates
from fontTools.ttLib.tables.ttProgram import Program

src = TTFont("source.ttf")
dst = TTFont("target.ttf")

cmap_s = src.getBestCmap()
cmap_d = dst.getBestCmap()

for char in "!@#$%":
    code = ord(char)
    gn_s = cmap_s[code]
    gn_d = cmap_d[code]
    src_glyph = src['glyf'][gn_s]

    # Only works for SIMPLE glyphs (numberOfContours > 0)
    if not (hasattr(src_glyph, 'numberOfContours') and src_glyph.numberOfContours > 0):
        continue  # skip compound glyphs

    ng = Glyph()
    ng.numberOfContours = src_glyph.numberOfContours
    ng.coordinates = GlyphCoordinates(src_glyph.coordinates)
    ng.endPtsOfContours = src_glyph.endPtsOfContours[:]
    ng.flags = src_glyph.flags[:]
    ng.program = Program()
    for attr in ('xMin', 'yMin', 'xMax', 'yMax'):
        v = getattr(src_glyph, attr, None)
        if v is not None:
            setattr(ng, attr, v)

    dst['glyf'][gn_d] = ng
    dst['hmtx'][gn_d] = (TARGET_WIDTH, 0)  # set advance width

dst.save("output.ttf")
src.close(); dst.close()
```

### Handling UPM differences

When source and target fonts have different `unitsPerEm` values, scale coordinates:

```python
SCALE = TARGET_UPM / SOURCE_UPM  # e.g. 1000/2000 = 0.5
ng.coordinates = GlyphCoordinates([
    (int(x * SCALE), int(y * SCALE)) for x, y in src_glyph.coordinates
])
if src_glyph.xMin is not None:
    ng.xMin = int(src_glyph.xMin * SCALE)
    # ... same for yMin, xMax, yMax
```

Check UPM with:
```python
src['head'].unitsPerEm
dst['head'].unitsPerEm
```

### Alternative: RecordingPen + TTGlyphPen (cleaner than direct GlyphCoordinates)

For copying simple glyphs (numberOfContours > 0) with scaling, use pens to replay outline operations — avoids manually managing coordinates, flags, endPtsOfContours, and bbox:

```python
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.recordingPen import RecordingPen

def copy_and_scale_glyph(src_glyph_pen, scale):
    """Return a TTGlyphPen glyph with scaled coordinates."""
    rec = RecordingPen()
    src_glyph_pen.draw(rec)
    pen = TTGlyphPen(None)

    for operator, args in rec.value:
        if operator == 'moveTo':
            pen.moveTo((args[0][0] * scale, args[0][1] * scale))
        elif operator == 'lineTo':
            pen.lineTo((args[0][0] * scale, args[0][1] * scale))
        elif operator == 'curveTo':
            pen.curveTo(
                (args[0][0] * scale, args[0][1] * scale),
                (args[1][0] * scale, args[1][1] * scale),
                (args[2][0] * scale, args[2][1] * scale),
            )
        elif operator == 'qCurveTo':
            pen.qCurveTo(*[(p[0] * scale, p[1] * scale) for p in args])
        elif operator == 'closePath':
            pen.closePath()
        elif operator == 'endPath':
            pen.endPath()
        elif operator == 'addComponent':
            pen.addComponent(args[0], (args[1][0], args[1][1],
                                       args[1][2] * scale, args[1][3] * scale))
    return pen.glyph()

# Usage — works with both static glyph and variable-font instance:
src_glyph = src.getGlyphSet()[glyph_name]  # or getGlyphSet(location=...)
scaled = copy_and_scale_glyph(src_glyph, 0.5)

dst['glyf'][glyph_name] = scaled
# Also scale hmtx:
old_w, old_lsb = src['hmtx'][glyph_name]
dst['hmtx'][glyph_name] = (round(old_w * scale), round(old_lsb * scale))
```

**When to prefer this over direct GlyphCoordinates:** Always, unless you need extreme performance (thousands of glyphs). The pen approach automatically handles bbox computation, flag correctness, and glyph structure — no risk of forgetting to set `program`, missing `endPtsOfContours[:]`, or mismatching coordinates/flags length.

**Limitation:** Compound glyphs (numberOfContours == -1) drawn through `addComponent` keep their component references — the component glyphs themselves must also exist in the destination font. For decomposition (flattening compounds to simple outlines), use the manual approach below.

### Variable fonts — extracting glyph instances

Variable fonts (VVAR/gvar) store default outlines + delta variations per axis. To extract glyphs at a specific weight/width, use `getGlyphSet(location=...)` which applies the variations:

**1. Inspect the variable font axes:**

```python
font = TTFont("VariableFont[MONO,wght].ttf")
fvar = font['fvar']

print("=== Axes ===")
for axis in fvar.axes:
    print(f'{axis.axisTag}: min={axis.minValue}, max={axis.maxValue}, default={axis.defaultValue}')

print("=== Named Instances ===")
for inst in fvar.instances:
    coords = dict(inst.coordinates)
    subfamily = font['name'].getDebugName(inst.subfamilyNameID) or ''
    print(f'coords={coords}, subfamily={subfamily}')
```

**2. Extract glyphs at a specific weight:**

```python
# Get glyph outlines at wght=700 (Bold) with MONO=1 (monospaced variant)
glyf_set = font.getGlyphSet(location={'wght': 700, 'MONO': 1})

glyph = glyf_set['braceleft']  # returns outlines with Bold weight applied
width, lsb = font['hmtx']['braceleft']  # NOTE: hmtx is static (not affected by location)
```

**3. Combine with RecordingPen for UPM-scaled copies to a static font:**

```python
src_var = TTFont("VariableFont[MONO,wght].ttf")
src_var_upem = src_var['head'].unitsPerEm  # e.g. 2000
dst = TTFont("StaticFont.ttf")
dst_upem = dst['head'].unitsPerEm           # e.g. 1000
scale = dst_upem / src_var_upem

# Get instance at Bold weight
src_glyf = src_var.getGlyphSet(location={'wght': 700, 'MONO': 1})

for gname in ['braceleft', 'braceright']:
    scaled = copy_and_scale_glyph(src_glyf[gname], scale)
    dst['glyf'][gname] = scaled
    ow, olsb = src_var['hmtx'][gname]
    dst['hmtx'][gname] = (round(ow * scale), round(olsb * scale))
```

**4. Separate upright and italic variable fonts:**

Some variable font families provide separate files for upright and italic:

```python
var_map = {
    'Regular': ('GoogleSansCode[MONO,wght].ttf', 400),
    'Bold': ('GoogleSansCode[MONO,wght].ttf', 700),
    'Italic': ('GoogleSansCode-Italic[MONO,wght].ttf', 400),
    'BoldItalic': ('GoogleSansCode-Italic[MONO,wght].ttf', 700),
}

for style, (var_path, wght) in var_map.items():
    var = TTFont(var_path)
    instance_glyphs = var.getGlyphSet(location={'wght': wght, 'MONO': 1})
    # ... copy glyphs from instance_glyphs to dst at style
    var.close()
```

**5. Check if glyphs have variations (gvar table):**

```python
if 'gvar' in font:
    gvar = font['gvar']
    for gname in ['braceleft', 'braceright']:
        if gname in gvar.variations:
            print(f'{gname} has {len(gvar.variations[gname])} variation tuples')
```

**Key insight:** When you access a glyph via `getGlyphSet(location=...)`, the returned glyph object supports `.draw(pen)` with the variations already applied. The raw `glyf` table still contains the default (unvaried) outlines. Always use the glyph set for copying, never the raw `glyf` table directly, if you want the instance-specific shape.

### Decomposing compound glyphs

Some glyphs (semicolon `;`, accented chars like `é`) are **compound glyphs** made of multiple simple components. fontTools stores them with `numberOfContours = -1` and a `.components` list.

To copy them, decompose manually:

```python
all_coords = []
all_end_pts = []
all_flags = []
offset = 0

g_comp = glyf_s[gn_s]
for comp in g_comp.components:
    sub = glyf_s[comp.glyphName]
    coords = list(sub.coordinates)
    # Apply component offset and scale
    transformed = [(int((x + comp.x) * SCALE), int((y + comp.y) * SCALE)) for x, y in coords]
    all_coords.extend(transformed)
    all_end_pts.extend([e + offset for e in sub.endPtsOfContours])
    all_flags.extend(sub.flags)
    offset += len(coords)

# Build new simple glyph from decomposed data
ng = Glyph()
ng.numberOfContours = len(all_end_pts)
ng.coordinates = GlyphCoordinates(all_coords)
ng.endPtsOfContours = all_end_pts
ng.flags = all_flags
ng.program = Program()
xs = [p[0] for p in all_coords]
ys = [p[1] for p in all_coords]
ng.xMin, ng.xMax = min(xs), max(xs)
ng.yMin, ng.yMax = min(ys), max(ys)

glyf_d[gn_d] = ng
hmtx_d[gn_d] = (TARGET_WIDTH, 0)
```

### Modifying font metadata

**Font family names** (name table):
```python
from fontTools.ttLib.tables._n_a_m_e import NameRecord

name = font['name']
# Remove existing records for IDs we want to replace
keep_ids = {0, 5, 7, 8, 9, 10, 11, 12, 13, 14}
name.names = [r for r in name.names if r.nameID in keep_ids]

def add(plat, enc, lang, nid, val):
    r = NameRecord()
    r.platformID = plat; r.platEncID = enc; r.langID = lang
    r.nameID = nid; r.string = val
    name.names.append(r)

# Mac (plat=1) and Windows (plat=3) entries
for plat, enc, lang in [(1, 0, 0), (3, 1, 0x0409)]:
    add(plat, enc, lang, 1, "Family Name")       # Font Family
    add(plat, enc, lang, 2, "Regular")            # Subfamily
    add(plat, enc, lang, 4, "Family Name Regular") # Full name
    add(plat, enc, lang, 6, "FamilyName-Regular")  # PostScript name
```

**Weight class** (OS/2 table):
```python
font['OS/2'].usWeightClass = 600  # 400=Regular, 600=SemiBold, 700=Bold
```

**Monospace flag (for terminal fonts)**:
```python
font['post'].isFixedPitch = 1
font['OS/2'].panose.bProportion = 9  # 9=monospace
```

**Proportional flag (for Propo/UI fonts)**:
```python
font['post'].isFixedPitch = 0
font['OS/2'].panose.bFamilyType = 2    # Latin Text
font['OS/2'].panose.bSerifStyle = 11   # Sans Serif
font['OS/2'].panose.bProportion = 3    # 3=proportional (9=monospace)
```

**OS/2 fsSelection bits** (used for proper weight/style classification):
```
BIT 0 (1):     ITALIC
BIT 5 (32):    BOLD
BIT 6 (64):    REGULAR
```
Common combinations:
```python
font['OS/2'].fsSelection = 0b1000000   # 64 — Regular
font['OS/2'].fsSelection = 0b1100000   # 96 — Bold
font['OS/2'].fsSelection = 0b1000001   # 65 — Italic
font['OS/2'].fsSelection = 0b1100001   # 97 — Bold Italic
```

**head.macStyle** (parallel classification):
```python
mac = font['head'].macStyle
mac = (mac | 0x01) if is_bold else (mac & ~0x01)
mac = (mac | 0x02) if is_italic else (mac & ~0x02)
font['head'].macStyle = mac
```

### Processing multiple variants

Loop over Regular, Bold, Italic, BoldItalic:

```python
VARIANTS = [
    ("Regular", "Regular"),
    ("Bold", "Bold"),
    ("Italic", "Italic"),
    ("BoldItalic", "Bold Italic"),
]

for out_name, style_name in VARIANTS:
    path = f"FontName-{out_name}.ttf"
    font = TTFont(path)
    # ... modify ...
    font.save(path)
    font.close()
```

---

## Workflow C: Mono → Propo Conversion

Convert a monospace Nerd Font ("Mono" variant) to proportional ("Propo" variant) by computing natural glyph widths, clearing monospace flags, and updating the name table.

### When to use

- User has a Nerd Font with `Nerd Font Mono` in the name and wants a proportional (`Nerd Font Propo`) variant
- All glyphs have the same advance width (e.g. 640 for MonoLisa, 600 for JetBrainsMono)
- The font is an installed `.ttf` or `.otf` file

### Step-by-step

**1. Inspect the font** — determine if it's TrueType or CFF-based:

```python
from fontTools.ttLib import TTFont
font = TTFont("font.otf")
print("Family:", font['name'].getDebugName(1))
print("UPM:", font['head'].unitsPerEm)
print("Has glyf table:", 'glyf' in font)   # TrueType outlines
print("Has CFF table:", 'CFF ' in font)    # PostScript outlines
print("isFixedPitch:", font['post'].isFixedPitch)
hmtx = font['hmtx']
widths = set(w for w, _ in hmtx.metrics.values())
print("Unique advance widths:", sorted(widths)[:10])
```

**2. Compute proportional advance widths** — different approach per outline format:

*For TrueType (glyf table)* — use `glyph.xMin/xMax`:
```python
def prop_width_tt(font, glyph_name, mono_width):
    glyf = font['glyf']
    if glyph_name not in glyf:
        return mono_width
    g = glyf[glyph_name]
    # Skip empty glyphs (spaces)
    if g.numberOfContours == 0 and not (hasattr(g, 'components') and g.components):
        return max(mono_width // 3, 250) if 'space' in glyph_name else max(mono_width // 4, 200)
    try:
        ink = g.xMax - g.xMin
    except:
        return mono_width
    if ink <= 0:
        return max(mono_width // 4, 200)
    proportional = min(ink + 100, mono_width)
    return max(proportional, 220)
```

*For CFF (OTF, 'CFF ' table)* — use `calcBounds`:
```python
def get_cff_bounds(font, glyph_name):
    top_dict = font['CFF '].cff.topDictIndex[0]
    cs = top_dict.CharStrings
    if glyph_name not in cs:
        return None
    try:
        return cs[glyph_name].calcBounds(cs[glyph_name].program)
    except:
        return None

def prop_width_cff(font, glyph_name, mono_width):
    bounds = get_cff_bounds(font, glyph_name)
    if bounds:
        ink = bounds[2] - bounds[0]  # xMax - xMin
    else:
        ink = 0
    if ink <= 0:
        return max(mono_width // 3, 250) if 'space' in glyph_name else max(mono_width // 4, 200)
    proportional = min(ink + 100, mono_width)
    return max(proportional, 220)
```

Apply to all glyphs:
```python
for gn in list(hmtx.metrics.keys()):
    adv, lsb = hmtx[gn]
    hmtx[gn] = (prop_width_cff(font, gn, mono_width), lsb)
```

**3. Update name table** — replace "Mono" → "Propo" (but NOT in the foundry name like "MonoLisa"):

Replace only whole-word occurrences:
- `"Nerd Font Mono"` → `"Nerd Font Propo"`
- `"Complete Mono"` → `"Complete Propo"`
- For PostScript: `"CompleteMono"` → `"CompletePropo"`

```python
def fix_name(text, style_ps):
    """Replace Mono→Propo in name strings, preserving the foundry name."""
    result = text
    result = result.replace("Complete Mono", "Complete Propo")
    result = result.replace("Nerd Font Mono", "Nerd Font Propo")
    result = result.replace("CompleteMono", "CompletePropo")
    result = result.replace("-Regular", f"-{style_ps}")
    return result

name = font['name']
for rec in name.names:
    try:
        txt = rec.toUnicode()
    except:
        continue
    nid = rec.nameID
    if nid in (1, 2, 4, 6, 16, 17, 18):
        new_txt = fix_name(txt, style_ps)
        if nid in (2, 17):  # Subfamily names
            new_txt = dst_style
        if new_txt != txt:
            name.removeNames(nameID=nid, platformID=rec.platformID,
                            platEncID=rec.platEncID, langID=rec.langID)
            name.setName(new_txt, nid, rec.platformID, rec.platEncID, rec.langID)
```

**4. Clear monospace flags**:

```python
font['post'].isFixedPitch = 0
font['OS/2'].panose.bFamilyType = 2
font['OS/2'].panose.bSerifStyle = 11
font['OS/2'].panose.bProportion = 3  # Proportional

# fsSelection: weight/style bits (see "Modifying font metadata" section above)
is_bold = "Bold" in dst_style
is_italic = "Italic" in dst_style
if is_bold and is_italic:
    font['OS/2'].fsSelection = 0b1100001  # 97
elif is_bold:
    font['OS/2'].fsSelection = 0b1100000  # 96
elif is_italic:
    font['OS/2'].fsSelection = 0b1000001  # 65
else:
    font['OS/2'].fsSelection = 0b1000000  # 64

mac = font['head'].macStyle
mac = (mac | 0x01) if is_bold else (mac & ~0x01)
mac = (mac | 0x02) if is_italic else (mac & ~0x02)
font['head'].macStyle = mac
```

**5. Save with a new filename**:

```python
font.save(f"FontName Regular Nerd Font Complete Propo.otf")
```

### Full script template

See `references/mono_to_propo_conversion.md` for a complete runnable script that processes all 4 variants (Regular, Bold, Italic, BoldItalic).

### Pitfalls

- **CFF vs TrueType**: Always detect which outline format the font uses (`'glyf' in font` vs `'CFF ' in font`) before computing proportional widths. Using `glyf`-based logic on a CFF font will crash.
- **Name replacement**: `"Mono".replace(...)` will corrupt foundry names like `"MonoLisa"` → `"PropoLisa"`. Always replace whole-word occurrences (`"Nerd Font Mono"`, `"Complete Mono"`), not the bare substring.
- **Italic glyphs may cap at mono width**: Italic glyphs often have wider ink bounds due to slant, and `min(ink + 100, mono_width)` may keep them at the original mono width. This is normal — italic glyphs are inherently wider.
- **Space/blank glyphs**: Set space characters to ~1/3 of mono width (e.g. 250 for a 640-UPM font) rather than computing from bounding box, which would yield 0.
- **PostScript names**: Must not contain spaces. Build them with `replace("CompleteMono", "CompletePropo")` style replacements.
- **`name.getBestCmap()` not `getBestCMap()`**: The method has lowercase 'm' — `getBestCmap()`. Wrong case raises AttributeError.
- **Duplicate name records**: Always use `name.removeNames(nameID=..., platformID=..., platEncID=..., langID=...)` with all 4 parameters to target the exact record. Omitting parameters may remove too many or too few entries.

---

## Workflow B: FontForge

### Essential Script Template

```python
import fontforge

def copy_glyphs(src_path, dst_path, glyph_names):
    src = fontforge.open(src_path)
    dst = fontforge.open(dst_path)
    for name in glyph_names:
        if name in src:
            src.selection.select(name)
            src.copy()
            dst.selection.select(name)
            dst.paste()
    dst.generate(dst_path)
    src.close()
    dst.close()
```

### UPM Scaling after paste

FontForge copy/paste does NOT auto-scale. Apply after pasting:

```python
font.selection.select(code)
font.transform([SCALE, 0, 0, SCALE, 0, 0])
glyph = font[code]
glyph.width = int(glyph.width * SCALE)
glyph.left_side_bearing = int(glyph.left_side_bearing * SCALE)
glyph.right_side_bearing = int(glyph.right_side_bearing * SCALE)
```

### Setting font names in FontForge

```python
font.familyname = "MyFont Nerd Font Propo"
font.fontname = "MyFontNerdFontPropo-Regular"
font.fullname = "MyFont Nerd Font Propo Regular"
font.sfnt_names = (
    ('English (US)', 'Family', 'MyFont Nerd Font Propo'),
    ('English (US)', 'SubFamily', 'Regular'),
    ('English (US)', 'Fullname', 'MyFont Nerd Font Propo Regular'),
    ('English (US)', 'PostScriptName', 'MyFontNerdFontPropo-Regular'),
)
```

---

## Verification

```bash
fc-cache -f
fc-list | grep -i "FontName"
# Quick render test (requires ImageMagick)
for f in ~/.fonts/FontName-*.ttf; do
    convert -background none -fill black -font "$f" -pointsize 48 label:'AaBb{}()' "${f%.ttf}.png"
done
```

Verify glyph outlines in Python:
```python
from fontTools.ttLib import TTFont
f = TTFont("font.ttf")
g = f['glyf'][f.getBestCmap()[ord('@')]]
print(f"contours={g.numberOfContours}, pts={len(list(g.coordinates))}")
f.close()
```

## Pitfalls
- **Compound glyphs can be variant-specific** — A character may be simple in Regular but compound in Bold (e.g., 'i' and 'j' in FantasqueSansM Bold have a compound dot+body structure while Regular uses a simple outline). Always check ALL variants (`numberOfContours == -1`) before assuming a glyph is copyable as a simple glyph.
- **Compound glyphs** (semicolon `;`, accented chars) have `numberOfContours == -1` and must be decomposed — fontTools' simple copy won't work on them.
- **UPM mismatch** between source and target fonts will cause wrong glyph size if not scaled. Always check both fonts' `head.unitsPerEm`.
- **FontForge `generate()`** can produce broken TTFs. If the output looks wrong, switch to fontTools for the same operation.
- **Name table duplication**: Some tools (FontForge, ttx) leave stale name records. Always strip and rebuild the table cleanly.
- **fc-cache** must be run after any TTF modification. Restart the target app to pick up cached font changes.
- **Backup first**: Before modifying installed font files, always copy them to a backup directory outside fontconfig-scanned paths (e.g. `~/.config/kitty/`, not `~/.fonts/bak/`).
- **Variable font hmtx is static** — The `hmtx` table in a variable font holds the default instance's advance widths (typically Regular weight). Varying the weight does NOT change hmtx values. When extracting glyphs at a different weight, hmtx stays the same; scale it proportionally with the outlines.
- **Variable font `getGlyphSet(location=...)` is pen-friendly** — The returned glyph objects support `.draw(pen)` with variations applied. You cannot index them into `glyf_table[name]` directly and get varied outlines — always use `.draw()` for instance-specific output.
- **Check `gvar` to know if glyphs vary with weight** — Some glyphs in a variable font may not have variation data (e.g. the `.notdef` glyph). Those stay at default regardless of location.
- **Backup first**: Before modifying installed font files, always copy them to a backup directory.
- **Check `isFixedPitch`**: For terminal use, set `post.isFixedPitch = 1` and `OS/2.panose.bProportion = 9`.
