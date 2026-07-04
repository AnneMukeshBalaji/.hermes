# GoogleSansCode → JetBrainsMono Nerd Font Propo merge

## Context (this session)
- Base font: JetBrainsMono Nerd Font Propo (various style TTFs under `~/.fonts/`).
- Source glyphs: GoogleSansCodeProportionalNerdFontPropo (regular, bold, italic, bold‑italic) located in the same `~/.fonts/` directory.
- Desired output: four custom font files named `CustomFontNerdFontPropo-<Style>.ttf` containing the original JetBrainsMono glyph set **plus** the GoogleSansCode characters `{`, `}`, `(`, `)` and the full A‑Z / a‑z alphabet.

## Steps performed
1. **Copy glyphs** with a FontForge Python script (`scripts/copy_glyphs.py`).
   - Loaded both source and destination fonts.
   - Iterated over the required Unicode code points (A‑Z, a‑z, `{`, `}`, `(`, `)`).
   - Used `src.selection.select` → `src.copy` → `dst.selection.select` → `dst.paste` for each glyph.
   - Saved the modified destination as `CustomFontNerdFontPropo-<Style>.ttf`.
2. **Verify rendering** using ImageMagick (`convert`) to produce PNG samples for each style.  All samples rendered the expected glyphs.
3. **Rename family metadata** (initially the fonts still reported the old family name).  Used FontForge to set:
   - `familyname = "CustomFont Nerd Font Propo"`
   - `fontname = "CustomFontNerdFontPropo<Style>"`
   - `fullname = "CustomFont Nerd Font Propo <Style>"`
   - Regenerated the TTFs.
4. **Refresh font cache** (`fc-cache -f`).
5. **Ad‑hoc verification script** (saved as `scripts/verify_custom_font.py`) that checks for the custom block in `kitty.conf` and the presence of the four TTF files.

## Pitfalls discovered & mitigations
- **Family name unchanged** after glyph copy: Fastfetch/Kitty still displayed the old family name, causing confusion.  Solution: explicitly update the name table via FontForge (or `ttx`/`fonttools`) after glyph merging.
- **Missing glyphs**: If a glyph is not in the source font, the script logs a warning and continues.  Verify the source contains the needed Unicode points before running.
- **Font cache stale**: After any TTF modification, always run `fc-cache -f` so the system recognises the new font.
- **PostScript name collisions**: Ensure the `fontname` contains no spaces and is unique per style to avoid duplicate registration.
- **Verification**: Rendering a test string with ImageMagick (`convert -font <ttf> -pointsize 48 label:'AaBb{ }()' out.png`) is a quick sanity check.

## Re‑usable snippets
- **FontForge copy script** (`scripts/copy_glyphs.py`) – see the `font-patching` skill body for the template.
- **Rename script** (`scripts/rename_font_names.py`) – uses `ttx` to edit the `name` table.
- **Verification script** (`scripts/verify_custom_font.py`) – checks Kitty config block and file existence.

---
*This reference file captures the complete workflow and pitfalls for future sessions that need to merge custom glyph sets into a base Nerd Font.*