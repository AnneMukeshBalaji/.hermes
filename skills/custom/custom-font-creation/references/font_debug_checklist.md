# Font-not-rendering debug checklist

When a custom font doesn't render in Kitty (or another terminal) — the user sees fallback/default font — work through this list in order.

## 0. Run Kitty with font-fallback debug (fastest first check)

Before any other debugging, run Kitty in debug mode to see what font it actually loads:

```bash
kitty --debug-font-fallback -1 --session=/dev/null 2>&1 | head -10
```

Look for the **Text fonts** section. If the Normal font is not your custom font, Kitty is falling back:

```
[0.356] Text fonts:
[0.356]   Normal: NotoSansMono-Regular: /usr/share/fonts/noto/NotoSansMono-Regular.ttf:0
```

This output tells you definitively whether Kitty accepted the font or silently fell back — no guesswork. Run this first, then proceed to the checks below.

## 1. Verify fontconfig sees the font

```bash
fc-list | grep "<family>"
fc-match "<family>"
```

If `fc-match` doesn't resolve, the font isn't installed or fontconfig can't parse it.

**Check for duplicate entries** — `fc-list | grep "<family>"` should show exactly ONE path per style variant (e.g. one Regular, one Bold). If it shows multiple paths for the same style (e.g. both `~/.fonts/LordSiva...` AND `~/.fonts/lordsiva_bak/LordSiva...`), you have a **backup-inside-fontdir conflict**: a backup subdirectory inside `~/.fonts/` is being scanned by fontconfig, and the old backup may take priority over the updated font.

**Fix:** `mv ~/.fonts/<backup_dir> ~/backups/` then `rm -rf ~/.cache/fontconfig/* && fc-cache -fv`

## 2. Check the name table

```python
from fontTools.ttLib import TTFont
tt = TTFont("font.ttf")
for r in tt['name'].names:
    if r.nameID in (1,2,4,6,16,17):
        print(f"  plat={r.platformID} lang={r.langID} nameID={r.nameID} str={r.toUnicode()!r}")
```

**Critical checks:**
- `nameID=1` (Family) matches what you put in kitty.conf exactly
- Both **platform 3** (Windows, `enc=1`, `lang=0x0409`) and **platform 1** (Mac, `enc=0`, `lang=0`) are present
- ⚠️ **Mac langID must be 0, NOT 0x0409.** Mac platform uses Mac language codes (0=English), not Windows LCIDs.

## 3. Check monospace flags

```python
print(f"isFixedPitch = {tt['post'].isFixedPitch}")
print(f"panose proportion = {tt['OS/2'].panose.bProportion}")
```

**Requirements for terminal fonts:**
- `isFixedPitch` must be **1** (not 0)
- `panose.bProportion` must be **9** (monospaced), not 0 (any)

Without these, Kitty silently falls back to a default font even though fontconfig resolves correctly.

## 4. Check UPM and glyph widths

```python
src_upm = tt_source['head'].unitsPerEm
dst_upm = tt_base['head'].unitsPerEm
print(f"Source UPM={src_upm}, Base UPM={dst_upm}, Scale={dst_upm/src_upm}")
```

If source and base have different UPM values (e.g. 2000 vs 1000), the pasted glyphs will be 2× size unless manually scaled.

**Check actual letter widths:**
```python
cmap = tt.getBestCmap()
for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz':
    w = tt['hmtx'][cmap[ord(c)]][0]
    print(f"  {c}: width={w}")
```

If copied glyphs have different widths from base glyphs (e.g. 1200 vs 600), UPM scaling wasn't applied.

## 5. Verify Kitty config format

**Preferred (simple):**
```
font_family      LordSiva Nerd Font Propo
bold_font        auto
italic_font      auto
bold_italic_font auto
```

**Avoid** `family="..." style="..."` syntax — can cause matching issues in some Kitty versions.

## 6. Check if Kitty knows about the font control socket

If `listen_on` is in kitty.conf but the socket doesn't exist:
```bash
ls -la /tmp/kitty-control.sock
```

Kitty hasn't been reloaded since the config change. Do **Ctrl+Shift+F5** in Kitty (not `kitty @ load-config`).

## 7. Is it actually the config reload?

Ctrl+Shift+F5 reloads the config but **doesn't restart the font engine** completely. If you've been iterating:
1. Close all Kitty windows (fully exit Kitty)
2. Restart Kitty

## Common root causes (ranked by frequency)

1. ❌ **UPM mismatch not scaled** — source font (2000) into base (1000) without 0.5× scaling
2. ❌ **`isFixedPitch=0`** — terminal emulator silently refuses proportional font
3. ❌ **Mac langID=0x0409** — invalid Mac platform entry makes Kitty ignore the font
4. ❌ **Backup inside ~/.fonts/** — backup subdirectory scanned by fontconfig, old files take priority over updated font
5. ❌ **FontForge generate() corruption** — glyf table has stale program bytecode
6. ❌ **Config syntax** — `family="..."` wrapping doesn't match font's actual nameID
7. ❌ **Stale fontconfig cache** — old entries prevent new font from being found
