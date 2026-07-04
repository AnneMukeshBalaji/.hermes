---
name: font-manipulation
description: Skills for managing, patching, and modifying font files using FontForge.
---

# Font Manipulation

Skills for managing, patching, and modifying font files (`.ttf`, `.otf`) using FontForge.

## Workflow
1.  **Preparation**:
    - Ensure `fontforge` is installed.
    - Confirm the file path for the source and destination fonts.
2.  **Patching**:
    - Use Python scripts to interface with `fontforge`.
    - **Crucial**: Always clear target glyph slots (`dst.clear()`) before pasting to avoid stale data or improper overwrites.
3.  **Application**:
    - Save changes to the font file.
    - Run `fc-cache -fv` to refresh the system font cache.
    - **Restart** target applications so they reload the font from disk.

## Pitfalls
- **UPM scaling**: FontForge copy/paste does NOT auto-scale when source and destination fonts have different `unitsPerEm` (UPM). Check with `python3 -c "from fontTools.ttLib import TTFont; print(TTFont('f.ttf')['head'].unitsPerEm)"` and manually apply `font.transform([scale, 0, 0, scale, 0, 0])` + fix `glyph.width` after pasting.
- **In-memory Caching**: Simply updating the file is often insufficient; desktop environments and applications cache fonts in memory. Restarting the application is mandatory.
- **Overwrite Failure**: Simply pasting over a filled slot in FontForge can fail or produce dirty results. Explicitly clear the slot first.
- **Cache Refreshing**: System-level font changes require `fc-cache -fv`.

## Alternative tool
- **fonttools**: When FontForge's `generate()` produces broken output, use fonttools to directly manipulate `glyf`, `hmtx`, and `name` tables on a copy of the base font — preserves original table structure and avoids generation artifacts.

## References
- `scripts/patch_font.py`: A template for copying glyphs from one font to another.
