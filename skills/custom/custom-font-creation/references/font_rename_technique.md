# Name Table Cleanup with fonttools

FontForge's native name-table handling is unreliable — it often leaves stale
family names (e.g. "JetBrainsMono Nerd Font Propo") in the font metadata even
after `font.familyname` is set.  This causes `fc-list` and terminal emulators
(Kitty, etc.) to show or pick the old name.

The reliable fix is a post-processing pass with `fonttools` that scrubs all
records for the critical name IDs and inserts clean ones.

## Critical Name IDs

| ID | Field             | Example (Regular variant)                |
|----|-------------------|------------------------------------------|
| 1  | Family            | `LordSiva Nerd Font Propo`               |
| 2  | SubFamily         | `Regular`                                |
| 3  | Unique ID         | (remove + re-add or skip)                |
| 4  | Full Name         | `LordSiva Nerd Font Propo Regular`       |
| 6  | PostScript Name   | `LordSivaNerdFontPropo-Regular`          |
| 16 | Preferred Family  | `LordSiva Nerd Font Propo`               |
| 17 | Preferred Styles  | `Regular`                                |

## Technique

```python
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._n_a_m_e import NameRecord

FAMILY = "LordSiva Nerd Font Propo"
PS_PREFIX = "LordSivaNerdFontPropo"

def clean_name_table(ttfont, out_suffix, style_name):
    name = ttfont["name"]
    target_ids = {1, 2, 3, 4, 6, 16, 17}

    # 1. Remove old records for these IDs
    name.names = [r for r in name.names if r.nameID not in target_ids]

    # 2. Add new records: platform 3 (Windows) + platform 1 (Mac)
    new_records = [
        (3, 1, 0x0409, 1, FAMILY),
        (3, 1, 0x0409, 2, style_name),
        (3, 1, 0x0409, 4, f"{FAMILY} {style_name}"),
        (3, 1, 0x0409, 6, f"{PS_PREFIX}-{out_suffix}"),
        (1, 0, 0, 1, FAMILY),
        (1, 0, 0, 2, style_name),
        (1, 0, 0, 4, f"{FAMILY} {style_name}"),
        (1, 0, 0, 6, f"{PS_PREFIX}-{out_suffix}"),
        (3, 1, 0x0409, 16, FAMILY),
        (3, 1, 0x0409, 17, style_name),
    ]

    for plat, enc, lang, nid, s in new_records:
        rec = NameRecord()
        rec.platformID = plat
        rec.platEncID = enc
        rec.langID = lang
        rec.nameID = nid
        rec.string = s
        name.names.append(rec)
```

## Pitfalls

- **`name.sort()` does NOT exist.** `table__n_a_m_e` has no sort method — remove
  any call to it or you'll get `AttributeError`.
- **Always do this after FontForge generation.** FontForge's own `sfnt_names`
  assignment is positional and may not cover both platform tables (Mac vs.
  Windows) consistently.
- **Both platforms matter.** Kitty on Linux reads platform-3 (Windows) records
  for style matching.  Mac records are needed for cross-platform tools.
- **⚠️ CRITICAL: Mac langID must be 0, NOT 0x0409.** The Mac platform
  (platformID=1) uses **Mac language codes** where 0 = English. The value
  0x0409 is a **Windows LCID** and is invalid on Mac platform entries. Using
  it causes terminal emulators (Kitty, etc.) to silently refuse the font.
  - **WRONG:** `(1, 0, 0x0409, 1, ...)` — uses Windows LCID on Mac platform
  - **CORRECT:** `(1, 0, 0, 1, ...)` — uses Mac language ID 0 (English)
- **Platform encoding matters.** For platform 3 use `enc=1` (Unicode BMP).
  For platform 1 use `enc=0` (Mac Roman).
- **Lang ID 0x0409 = English (US).** Only valid for platform 3 (Windows).
  Change for other locales.
