# Font Name Table Structure (OpenType/TrueType)

The `name` table (tag `name`) stores font metadata as a series of `NameRecord`
entries. Each record targets a specific platform, encoding, language, and nameID.

## Platform IDs

| ID | Platform  | Encoding IDs                     | Language IDs                  |
|----|-----------|----------------------------------|-------------------------------|
| 1  | Macintosh | 0 = Roman, 1 = Japanese, ...     | Mac language codes (0=English)|
| 3  | Windows   | 1 = Unicode BMP, 10 = Full Unicode | Windows LCIDs (0x0409=en-US) |

### Key rules
- **Platform 1 (Mac)** uses **enc=0** (Mac Roman) and **lang=0** (English).
  ⚠️ **lang=0** — NOT `0x0409`. The value 0x0409 is a Windows LCID, invalid on Mac.
- **Platform 3 (Windows)** uses **enc=1** (Unicode BMP) and **lang=0x0409** (English US).

## Critical Name IDs

| ID | Field             | Purpose                              | Example                          |
|----|-------------------|--------------------------------------|----------------------------------|
| 0  | Copyright         | Legal attribution                    | "Copyright 2020 ..."             |
| 1  | **Family**        | Font family name (primary)           | "LordSiva Nerd Font Propo"       |
| 2  | **SubFamily**     | Style / weight variant               | "Regular", "Bold", "Italic"      |
| 3  | Unique ID         | Unique font identifier               | "LordSiva Nerd Font Propo Regular" |
| 4  | **Full Name**     | Full human-readable name             | "LordSiva Nerd Font Propo Regular" |
| 5  | Version           | Version string                       | "Version 2.304"                  |
| 6  | **PostScript Name** | PS name (no spaces)                | "LordSivaNerdFontPropo-Regular"  |
| 16 | **Preferred Family** | Preferred family (supersedes ID 1) | "LordSiva Nerd Font Propo"       |
| 17 | **Preferred Styles** | Preferred style (supersedes ID 2) | "Regular"                        |

## Correct Add Record Calls

```python
from fontTools.ttLib.tables._n_a_m_e import NameRecord

def add_record(name, plat, enc, lang, name_id, string):
    rec = NameRecord()
    rec.platformID = plat
    rec.platEncID = enc
    rec.langID = lang
    rec.nameID = name_id
    rec.string = string
    name.names.append(rec)

# Mac — lang=0 (NOT 0x0409)
add_record(name, 1, 0, 0, 1, "LordSiva Nerd Font Propo")       # Family
add_record(name, 1, 0, 0, 2, "Regular")                          # SubFamily
add_record(name, 1, 0, 0, 4, "LordSiva Nerd Font Propo Regular") # Full Name
add_record(name, 1, 0, 0, 6, "LordSivaNerdFontPropo-Regular")    # PostScript Name

# Windows — lang=0x0409
add_record(name, 3, 1, 0x0409, 1, "LordSiva Nerd Font Propo")
add_record(name, 3, 1, 0x0409, 2, "Regular")
add_record(name, 3, 1, 0x0409, 4, "LordSiva Nerd Font Propo Regular")
add_record(name, 3, 1, 0x0409, 6, "LordSivaNerdFontPropo-Regular")
add_record(name, 3, 1, 0x0409, 16, "LordSiva Nerd Font Propo")  # Preferred Family
add_record(name, 3, 1, 0x0409, 17, "Regular")                    # Preferred Styles
```

## Common Mistakes

| Mistake | Effect |
|---------|--------|
| `lang=0x0409` on platform 1 (Mac) | **Font silently rejected** by terminal emulators (Kitty, etc.) |
| Missing nameID 16/17 | Kitty may not match style variants correctly |
| PostScript name with spaces | Font loading errors in many renderers |
| `name.sort()` call | `AttributeError` — `table__n_a_m_e` has no sort method |
| Only setting Windows records | Cross-platform tools (macOS, Linux DE font pickers) may not see the font |
