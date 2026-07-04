# Design-Size Compensation Beyond UPM Scaling

## The Problem

Different typefaces have inherently different proportions within their UPM space.
Even after correct UPM scaling (e.g. 2048→1000 via `scale = dst_upm / src_upm`),
glyph sizes may be visibly different because font designers choose different x-heights,
cap heights, and letter proportions.

## Case Study: FantasqueSansM → LordSiva (JetBrainsMono-based)

| Font | UPM | 'A' height | 'A' width | % of UPM |
|------|-----|-----------|----------|---------|
| JetBrainsMono (LordSiva base) | 1000 | 716 | 542 | 71.6% |
| FantasqueSansM (raw) | 2048 | 1302 | 971 | 63.5% |
| FantasqueSansM (UPM-scaled to 1000) | 1000 | 635 | 474 | 63.5% |
| **Difference** | | **-11.3%** | **-12.5%** | |

**Result:** After naive UPM scaling (1000/2048 = 0.488), FantasqueSansM letters are
~10-12% smaller across the alphabet. The user reported "characters are smaller."

## The Fix — Secondary Design Scale

```
final_scale = upm_scale * design_scale
```

Where `design_scale` compensates for the inherent size difference:

```python
# Measure reference glyphs in both fonts (at native UPM)
orig_a = original_glyf['A']  # JetBrainsMono
src_a  = source_glyf['A']    # FantasqueSansM

h_orig  = orig_a.yMax - orig_a.yMin
h_src   = src_a.yMax - src_a.yMin
w_orig  = orig_a.xMax - orig_a.xMin
w_src   = src_a.xMax - src_a.xMin

design_scale_h = h_orig / (h_src * upm_scale)  # height ratio
design_scale_w = w_orig / (w_src * upm_scale)  # width ratio
design_scale   = (design_scale_h + design_scale_w) / 2  # average

final_scale = upm_scale * design_scale
```

For the FantasqueSansM → LordSiva case:
- `upm_scale = 1000/2048 = 0.48828`
- `design_scale ≈ 1.1078` (10.8% larger)
- `final_scale = 0.48828 * 1.1078 ≈ 0.5409`

## When to Apply

- **Always measure** bounding boxes of A, a, X, x in both fonts before merging
- If the size ratio deviates more than 3-5% from 1.0, apply design compensation
- Use a **uniform** `final_scale` for all copied glyphs — per-glyph scaling breaks
  the font's visual harmony
- Apply the same scale to advance widths if you're not forcing a uniform width

## Verification

After applying the adjusted scale:

```python
for c in 'AaXx':
    orig_w = original_glyf[cmap_orig[ord(c)]].xMax - original_glyf[cmap_orig[ord(c)]].xMin
    new_w  = new_glyf[cmap_new[ord(c)]].xMax - new_glyf[cmap_new[ord(c)]].xMin
    ratio  = new_w / orig_w if orig_w else 1
    print(f'{c}: new/orig width ratio = {ratio:.2f}')
    # Should be close to 1.0 (±0.05)
```

## Related Pitfalls

- **Compound glyphs need decompose before scaling** — see `font-patching` skill
  for the decomposition pattern
- **Empty hinting programs** — scaled glyphs need `Program()` not the source's
  hinting instructions
- **Uniform advance widths** — for terminal fonts, force all substituted glyphs
  to the same advance width regardless of design scale
