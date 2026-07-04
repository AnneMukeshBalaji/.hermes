---
name: custom-font-creation
category: custom
description: |
  Workflow for creating a custom Nerd Font by merging glyphs from one font into another, renaming the font family reliably, and configuring terminal emulators (e.g., Kitty) to use it.
version: "1.0"
trigger: |
  When the user wants to create a custom Nerd Font that merges glyphs from one or more source fonts into a base font.
---

## Steps

### Option A: FontForge (when UPM matches)

1. **Check UPM first** – Verify source and base fonts have the same `unitsPerEm`:
   ```bash
   python3 -c "from fontTools.ttLib import TTFont; t=TTFont('font.ttf'); print(t['head'].unitsPerEm)"
   ```
   If UPM differs, use **Option B** (fonttools) — FontForge's copy/paste does not auto-scale.

2. **Copy glyphs** – Use FontForge or `scripts/generate_custom_font.py` to open the source and destination fonts and copy the desired glyphs. **Always clear the destination glyph slot before pasting** to avoid stale-data corruption:
   ```python
   dest.selection.select(code); dest.clear(); dest.paste()
   ```

3. **Scale if needed** – When source and base UPM differ, manually scale after paste:
   ```python
   scale = base_upm / src_upm
   dest.selection.select(code)
   dest.transform([scale, 0, 0, scale, 0, 0])
   glyph = dest[code]
   glyph.width = int(glyph.width * scale)
   glyph.left_side_bearing = int(glyph.left_side_bearing * scale)
   ```

4. **Set names in FontForge** – Before generating:
   - `font.familyname` – family name
   - `font.fontname` – PostScript name, no spaces
   - `font.fullname` – full human name
   - `font.sfnt_names` – SFNT name table tuple

5. **Generate the TTF** – Call `fontforge.generate(out_path)`.

### Option B: fonttools (preferred — handles UPM scaling)

Use `scripts/build_custom_font_fonttools.py`:

```bash
python3 scripts/build_custom_font_fonttools.py \
    --base JetBrainsMonoNerdFontPropo-Regular.ttf \
    --source GoogleSansCodeProportionalNerdFontPropo-Regular.ttf \
    --output LordSivaNerdFontPropo-Regular.ttf \
    --family "LordSiva Nerd Font Propo" \
    --style "Regular"
```

This handles: UPM scaling, name table cleanup with correct Mac langID, monospace flags for terminal use, and empty hinting programs for scaled glyphs. See `scripts/build_custom_font_fonttools.py` for the full implementation.

### Pre-merge: Check design size match

Before any glyph merge, **measure bounding boxes of reference characters** at their native UPM:

```bash
python3 -c "
from fontTools.ttLib import TTFont
for name, path in [('Base', 'base_font.ttf'), ('Source', 'source_font.ttf')]:
    f = TTFont(path)
    cmap = f.getBestCmap()
    for c in 'AaXx':
        g = f['glyf'][cmap[ord(c)]]
        w = g.xMax - g.xMin; h = g.yMax - g.yMin
        print(f'{name} {c}: {w}x{h} (UPM={f[\"head\"].unitsPerEm})')
    f.close()
"
```

If the source font's letters are proportionally smaller/larger than the base's at the same UPM, you'll need a **secondary design scale** (see pitfalls below and `references/design_size_compensation.md`).

### Post-processing (both options)

6. **Set monospace flags** – Terminal emulators silently refuse fonts without these:
   ```python
   jet['post'].isFixedPitch = 1
   jet['OS/2'].panose.bProportion = 9  # Monospaced
   ```

7. **Clean the name table** – FontForge and fonttools both need this. Remove stale name records (IDs 1,2,3,4,6,16,17) and add clean ones for both Mac and Windows platforms:
   - **Windows (platform 3):** `enc=1, lang=0x0409`
   - **Mac (platform 1):** `enc=0, lang=0` ← **NOT 0x0409!**
   
   See `references/font_rename_technique.md` for the exact code.

8. **Refresh font cache** – Full purge, not just fc-cache -f:
   ```bash
   rm -rf ~/.cache/fontconfig/*
   fc-cache -fv
   ```

9. **Verify no duplicate registrations** – After cache refresh, confirm only ONE path per style variant:
   ```bash
   fc-list | grep "<family>"
   ```
   If you see multiple paths for the same style (e.g. the live font AND a backup copy), fontconfig may pick the wrong one. Move any backup directories OUTSIDE ~/.fonts/ and repeat step 8.

10. **Install & verify**:
   ```bash
   cp *.ttf ~/.fonts/
   fc-match "LordSiva Nerd Font Propo"
   ```

11. **Maintain a backup** – After verifying the font renders correctly, copy a
    known-good set to your terminal's config directory (e.g. `~/.config/kitty/`)
    as a persistent backup. See `references/font_file_management.md` for the
    dual-location strategy.

### Option C: Convert Nerd Font Mono → Propo (fonttools CFF)

Use this when you have a Nerd Font Complete Mono (e.g. MonoLisa Nerd Font Complete Mono) and want a proportional variant. This is the **reverse** of Options A/B — you're not merging glyphs, you're converting an existing monospace Nerd Font to proportional.

```bash
python3 scripts/convert_mono_to_propo.py \
    --src-prefix "MonoLisa" \
    --src-dir ~/.fonts \
    --scale 1.15
```

See `references/mono_to_propo.md` for session-specific detail and the full script.

**What the conversion does:**

1. **Computes proportional advance widths** — For each glyph with CFF outlines, measures the ink bounding box via `calcBounds()` and sets `advance = ink_width + padding` (capped at the original mono width).
2. **Scales CFF glyph outlines** — Uses `TransformPen` + `T2CharStringPen` to uniformly scale all glyph coordinates by a factor (e.g. 1.15x). This is critical because proportional fonts at the same point size feel smaller than mono — the glyphs need to be bigger to fill the proportionally-spaced line.
3. **Updates the name table** — Changes `"Nerd Font Mono"` → `"Nerd Font Propo"`, `"Complete Mono"` → `"Complete Propo"`, and corrects PostScript names.
4. **Clears monospace flags** — Sets `post.isFixedPitch = 0`, `panose.bProportion = 3` (proportional).
5. **Fixes space widths** — Empty glyphs (space, .notdef) that have no CFF outlines get a proportional width, not the original mono width.

**Critical for CFF fonts:**
- After creating a new charstring via `T2CharStringPen.getCharString()`, you **must** copy the `.private` attribute from the original charstring: `new_cs.private = cs.private`. Without this, the CFF compiler cannot find the Private dict and raises `AttributeError: 'NoneType' object has no attribute 'nominalWidthX'`.
- After scaling, **do NOT scale `head.unitsPerEm`** — that would cancel out the glyph scaling at render time.
- The `T2CharStringPen` module is `fontTools.pens.t2CharStringPen`, not `t2Pen`.

### Option D: Selective glyph replacement (same UPM, matching glyph names)

Use this when you want to replace **specific characters** in a base font with
glyphs from a source font, and both fonts share the same UPM and matching glyph
names for the target characters. No scaling or name remapping needed for the
glyph operation itself.

**When to use:** You have a working base font (e.g. JetBrainsMonoNerdFontPropo)
and want to swap in certain glyphs from another font (e.g. MapleMono) for
stylistic reasons.

**Pre-flight checks:**

```bash
# 1. Same UPM?
python3 -c "from fontTools.ttLib import TTFont; \
  s=TTFont('source.ttf'); d=TTFont('dest.ttf'); \
  print(f'src UPM={s[\"head\"].unitsPerEm} dst UPM={d[\"head\"].unitsPerEm}'); \
  s.close(); d.close()"

# 2. Matching glyph names for target chars?
python3 -c "
from fontTools.ttLib import TTFont
s=TTFont('source.ttf'); d=TTFont('dest.ttf')
sc=s.getBestCmap(); dc=d.getBestCmap()
chars='!@#\$%^&*[]\\,<>?/.:;\"|'
for c in chars:
    cp=ord(c)
    if cp in sc and cp in dc:
        ok='MATCH' if sc[cp]==dc[cp] else 'DIFF'
        print(f'U+{cp:04X} {c}: src={sc[cp]} dst={dc[cp]} [{ok}]')
s.close(); d.close()
"
```

**Process:**

1. **Backup originals** first:
   ```bash
   mkdir -p ~/.fonts/bak
   cp BaseFont-*.ttf ~/.fonts/bak/
   ```

2. **Copy base to output filenames**, then for each variant iterate over target
   characters and copy glyph outlines + advance widths directly:

   ```python
   from fontTools.ttLib import TTFont

   src = TTFont("Source-{variant}.ttf")
   dst = TTFont("Output-{variant}.ttf")
   src_cmap = src.getBestCmap()
   dst_cmap = dst.getBestCmap()

   for c in TARGET_CHARS:
       cp = ord(c)
       if cp not in src_cmap or cp not in dst_cmap:
           continue
       src_gn = src_cmap[cp]
       dst_gn = dst_cmap[cp]
       dst['glyf'][dst_gn] = src['glyf'][src_gn]       # outlines
       dst['hmtx'][dst_gn] = src['hmtx'][src_gn]        # advance width
   ```

3. **Compound glyphs: keep them as-is** when the component glyphs are ALSO in
   your replacement list. For example, colon (:) may be a compound of two
   period glyphs -- if you're replacing both period and colon, the compound
   references glyph names and will resolve correctly with the source font's
   newly-copied glyph data. **Do NOT decompose** -- doing so is unnecessary
   work and loses the component-reference structure.

4. **Rename** the font family (see Post-processing step 7 below). Pay attention
   to both nameID 1 (short form, e.g. "JetBrainsMono NFP") and nameID 16
   (long form, e.g. "JetBrainsMono Nerd Font Propo") -- both need updating.

5. **Set style-specific metadata** (weight class, fsSelection, macStyle).

6. **Full cache purge**: `rm -rf ~/.cache/fontconfig/* && fc-cache -fv`

### Option E: Create named font family from base (rename + convert)

Use this when you want to **create a new named font from scratch** — no glyph
merging needed. You take an existing Nerd Font as a base, rename it, and optionally
convert Mono → Propo if starting from a monospaced variant.

**Typical use case:** Creating a custom font family (e.g. "LordSiva") using
JetBrainsMonoNerdFont as the base, with proportional widths and custom naming.

**Steps:**

1. Copy base font files to new filenames:
   ```bash
   for v in Regular Bold Italic BoldItalic; do
     cp JetBrainsMonoNerdFont-$v.ttf CustomFontNerdFontPropo-$v.ttf
   done
   ```

2. For each variant, apply **Option C (Mono → Propo conversion)** above to compute
   proportional advance widths, clear monospace flags, and update the name table
   with your custom family name instead of "Nerd Font Mono" → "CustomFont Nerd Font Propo".

3. Set style-specific metadata:
   ```python
   from fontTools.ttLib import TTFont

   VARIANTS = [
       ("Regular", "Regular", 400, 0b1000000),
       ("Bold", "Bold", 600, 0b1100000),       # Semi-Bold weight preferred
       ("Italic", "Italic", 400, 0b1000001),
       ("BoldItalic", "Bold Italic", 600, 0b1100001),
   ]

   for out_name, style_name, weight, fs_sel in VARIANTS:
       f = TTFont(f"CustomFontNerdFontPropo-{out_name}.ttf")
       f['OS/2'].usWeightClass = weight
       f['OS/2'].fsSelection = fs_sel
       mac = f['head'].macStyle
       mac = (mac | 0x01) if "Bold" in style_name else (mac & ~0x01)
       mac = (mac | 0x02) if "Italic" in style_name else (mac & ~0x02)
       f['head'].macStyle = mac
       f.save()
       f.close()
   ```

4. Full fontconfig purge: `rm -rf ~/.cache/fontconfig/* && fc-cache -fv`

5. Verify all styles resolve:
   ```bash
   fc-list | grep "CustomFont"
   ```

**See project-specific configs in `references/`** — e.g. `references/lordsiva-font-config.md`
for the LordSiva Nerd Font Propo project (UPM=1000, width=600, Bold=600, base=JBMono).

---

## Pitfalls
- **Compound glyphs: keep them when replacing both compound AND components** — When a compound glyph (e.g. colon as two periods) references component glyphs that are ALSO in your replacement set (period, comma), do NOT decompose. The compound stores glyph-name references that already exist in the destination font; after you replace the component glyphs with source outlines, the compound renders correctly. Decomposing just bloats the file and loses the reference structure.\n- **Check glyph name matching before selective replacement** — If source and dest map the same character to different glyph names (e.g. "period" vs "periodcentered"), you need name remapping. Check early: `python3 -c "from fontTools.ttLib import TTFont; s=TTFont('src.ttf'); d=TTFont('dst.ttf'); sc=s.getBestCmap(); dc=d.getBestCmap(); [print(f'{chr(cp)}: src={sc[cp]} dst={dc[cp]}') for cp in set(sc)&set(dc) if sc[cp]!=dc[cp]]"`.\n- **Design proportion differs between typefaces even after UPM scaling** — Different fonts have inherently different proportions (x-height, cap height, ascender/descender ratios) within their UPM space. After correct UPM scaling (e.g. 2048→1000), FantasqueSansM letters are ~10.8% smaller than JetBrainsMono letters at the same UPM. **Always compare bounding boxes of a few reference characters** (A, a, X, x) between source and target before merging. If they differ, apply a **secondary design scale** on top of the UPM scale. Calculate the adjustment from the ratio of cap heights or x-heights:

   ```python
   # After UPM scaling, check if an extra design scale is needed
   scale_upm = dst_upm / src_upm
   # Compare 'A' height as proxy for cap-height ratio
   h_orig = glyph_original['A'].yMax - glyph_original['A'].yMin
   h_src_scaled = int((glyph_source['A'].yMax - glyph_source['A'].yMin) * scale_upm)
   design_scale = h_orig / h_src_scaled  # e.g. 716/635 ≈ 1.128
   final_scale = scale_upm * design_scale  # combined scale factor
   ```

   Apply `final_scale` uniformly to all copied glyph coordinates and advance widths. See `references/design_size_compensation.md` for a worked example.

- **Font backup location strategy** — Custom font files are fragile; fontconfig cache purges, font reinstalls, and system updates can leave you without a working terminal font. Maintain two copies: the **active installation** in `~/.fonts/` (registered with fontconfig) and a **persistent backup** in your terminal's configuration directory (e.g. `~/.config/kitty/`). The config-directory copy survives fontconfig resets and makes recovery trivial.
- **Backup directories inside `~/.fonts/` cause fontconfig conflicts** — Never place a backup folder INSIDE `~/.fonts/` (or any fontconfig-scanned directory). Fontconfig recursively scans `~/.fonts/` and registers every font it finds — including old copies in subdirectories. This creates duplicate entries for the same family name, and fontconfig may prefer the old backup over the updated font. After `fc-cache`, `fc-list | grep "<family>"` will show multiple paths for the same style. **Fix:** move backups to `~/backups/` or `~/.config/kitty/` — anywhere outside a fontconfig-scanned path. Then purge cache and re-run `fc-cache -fv`.
- **Force uniform advance widths for terminal fonts** — Terminal emulators silently fall back to a default font when ANY substituted glyph has a width different from the monospaced norm. When you copy glyphs from a different-UPM source, don't just scale the source width — **explicitly set all substituted glyphs to a known uniform width** matching the base font's monospace advance. For JetBrainsMonoNerdFont (UPM=1000) the mono width is 600. Use `hmtx[glyph_name] = (TARGET_WIDTH, 0)` for every replaced glyph, or pass `--force-width 600` to the build script. Without this, a single glyph with a stray width (e.g. 601 instead of 600) causes the terminal to silently fall back to a different font.
- **Build all variants in one script run** — When creating a complete terminal font, build all four variants (Regular, Bold, Italic, BoldItalic) together rather than running the tool four times. A single script that iterates over a variant list ensures consistent scaling, naming, and monospace flags across all styles. See `scripts/build_font_family.py` for an example that builds all 4 variants from a single invocation.
- **UPM scaling — THE #1 cause of "not rendering" in custom fonts.** FontForge's copy/paste does NOT auto-scale glyph outlines or advance widths when source and destination fonts have different `unitsPerEm` (UPM). For example, GoogleSansCode uses UPM=2000 while JetBrainsMono uses UPM=1000. The pasted glyphs land at 2× size — both outlines AND advance widths — unless you manually scale them:
  ```python
  SCALE = dst_upm / src_upm  # e.g. 1000/2000 = 0.5
  jet.selection.select(code)
  jet.transform([SCALE, 0, 0, SCALE, 0, 0])  # scale outlines
  glyph = jet[code]
  glyph.width = int(glyph.width * SCALE)       # fix advance width
  glyph.left_side_bearing = int(glyph.left_side_bearing * SCALE)
  ```
  **Always check `unitsPerEm` of both fonts before starting** via `python3 -c "from fontTools.ttLib import TTFont; t=TTFont('font.ttf'); print(t['head'].unitsPerEm)"`.
- **Fonttools is a more reliable alternative to FontForge** for glyph manipulation. When FontForge's `generate()` produces subtly broken fonts, use fonttools to directly manipulate `glyf`, `hmtx`, and `name` tables on a copy of the base font — this preserves the original table structure and avoids generation artifacts. See `references/fonttools_glyph_merge.md`.
- **Stale family names** – If only `fontforge.generate()` is used, Fontconfig may still pick the original family (`JetBrainsMono`). Always clean the name table with `fonttools` after generation.
- **`font.sfnt_names` string keys are case-sensitive** – `'Fullname'` works, `'FullName'` raises `ValueError`.
- **`scripts/generate_custom_font.py` uses FontForge** — for fonts with UPM mismatch, prefer the fonttools-based script `scripts/build_custom_font_fonttools.py` which avoids generation artifacts and has proper scaling.
- **IsFixedPitch flag in fonttools** – when creating a font for a terminal emulator, set `jet['post'].isFixedPitch = 1` AND `jet['OS/2'].panose.bProportion = 9` (monospaced). Omitting these causes Kitty et al. to silently fall back to a different font.
- **Propo vs Mono variant matters for terminal fonts** – "Propo" (proportional) Nerd Font variants have hundreds of different glyph widths. Terminal emulators like Kitty silently fall back to a default font when the font isn't truly monospaced. Always use the **MONO** variant as the base for terminal fonts (JetBrainsMonoNerdFont-*.ttf, not JetBrainsMonoNerdFontPropo-*.ttf). After merging, force uniform advance widths (e.g. 600) on all replaced glyphs.\n- **Empty program hinting for scaled glyphs** – when scaling glyphs from a different-UPM source font, the original hinting instructions (TrueType `program`) become invalid. Always set `new_glyph.program = Program()` (empty) rather than copying the source's program, which would contain coordinates calibrated for the original UPM.
- **PostScript name cannot contain spaces** – `font.fontname` must be a single token (e.g. `LordSivaNerdFontPropo-Regular`).
- **Always clear destination glyph slots before pasting** – `dest.clear()` prevents stale outline data.
- **`name.sort()` does NOT exist** on fontTools `TTFont['name']` — the `table__n_a_m_e` object has no sort method.
- **Both platform tables matter** – Set records for both platform 3 (Windows, `enc=1`, `lang=0x0409`) and platform 1 (Mac, `enc=0`, `lang=0`).  **Mac langID must be 0, not 0x0409** — using Windows LCIDs on the Mac platform creates an invalid font that applications silently refuse.
- **Simple Kitty config is more reliable** – Prefer `font_family Name` over `family="Name" style="Style"` syntax. Use `bold_font auto`.
- **Full cache purge needed** – `rm -rf ~/.cache/fontconfig/*` then `fc-cache -fv` is more reliable than `fc-cache -f` alone.
- **Set sfnt_names BEFORE generate** – FontForge may not apply name table changes set after `generate()`.
- **Launching a new Kitty** from inside Kitty kills the window. Use config reload instead.

## References
- `references/font_file_management.md` – dual-location font backup strategy (active `~/.fonts/` + persistent `~/.config/kitty/` backup).
- `references/font_rename_technique.md` – detailed notes on the `fonttools` name‑table cleanup performed in this session.
- `references/font_name_table_structure.md` – platform IDs, encodings, and language IDs for the name table.
- `references/fonttools_glyph_merge.md` – using fonttools directly to merge glyphs (alternative to FontForge).
- `references/font_debug_checklist.md` – step-by-step debugging guide when a custom font doesn't render in Kitty.
- `references/design_size_compensation.md` – worked example of secondary design scale when source font proportions differ from target (FantasqueSansM → JetBrainsMono case study).
- `references/mono_to_propo.md` – full session detail for converting Nerd Font Mono to Propo: CFF scaling with T2CharStringPen, proportional width computation, space width fixes, and the scale-factor rationale.
- `references/lordsiva-font-config.md` – LordSiva Nerd Font Propo project config: UPM=1000, width=600, Bold=600, base=JetBrainsMonoNerdFont. Blueprint for creating a named font from scratch.

## Scripts
- `scripts/generate_custom_font.py` – FontForge-based glyph copy + rename (works when UPM matches).
- `scripts/build_custom_font_fonttools.py` – **Preferred.** fonttools-based build with proper UPM scaling, monospace flags, and name table cleanup. No FontForge required.
- `scripts/verify_mono_to_propo.py` – verification script for Mono → Propo conversions: checks all 4 styles resolve, monospace flags are cleared, and widths are proportional.