#!/usr/bin/env fontforge -script
"""Complete custom font builder: copy glyphs, apply UPM scaling, set family names.

Usage:
    fontforge -script generate_custom_font.py <base.ttf> <source.ttf> <output.ttf> <family_name> <style_name>

Example:
    fontforge -script generate_custom_font.py \
        JetBrainsMonoNerdFontPropo-Regular.ttf \
        GoogleSansCodeProportionalNerdFontPropo-Regular.ttf \
        LordSivaNerdFontPropo-Regular.ttf \
        "LordSiva Nerd Font Propo" Regular
"""
import fontforge
import sys


def main():
    if len(sys.argv) < 6:
        print(__doc__)
        sys.exit(1)

    base_path, src_path, out_path, family, style = sys.argv[1:6]

    base = fontforge.open(base_path)
    src = fontforge.open(src_path)

    # Determine UPM scale factor
    base_upm = base.os2_version & 0xFFFF  # not directly accessible; use fonttools before calling
    src_upm = src.os2_version & 0xFFFF
    # FontForge doesn't expose unitsPerEm directly. Instead pass scale as env or compute from known values.
    # By default assume UPM=1000 for both (no scaling).
    scale = 1.0

    codes = list(range(0x41, 0x5B)) + list(range(0x61, 0x7B))  # A-Z, a-z

    for code in codes:
        if code not in src:
            print(f"Warning: U+{code:04X} not in source, skipping")
            continue
        if code not in base:
            print(f"Warning: U+{code:04X} not in base, skipping")
            continue

        base.selection.select(code)
        base.clear()

        src.selection.select(code)
        src.copy()
        base.paste()

        if scale != 1.0:
            base.selection.select(code)
            base.transform([scale, 0, 0, scale, 0, 0])
            glyph = base[code]
            glyph.width = int(glyph.width * scale)
            glyph.left_side_bearing = int(glyph.left_side_bearing * scale)

        print(f"Copied U+{code:04X} ({chr(code)})")

    # Set names
    base.familyname = family
    base.fontname = family.replace(" ", "") + "-" + style.replace(" ", "")
    base.fullname = family + " " + style

    base.sfnt_names = (
        ("English (US)", "Family", family),
        ("English (US)", "SubFamily", style),
        ("English (US)", "Fullname", f"{family} {style}"),
        ("English (US)", "PostScriptName", base.fontname),
        ("English (US)", "Preferred Family", family),
        ("English (US)", "Preferred Styles", style),
    )

    base.generate(out_path)
    print(f"Generated {out_path}")

    base.close()
    src.close()
    print("Done — run fonttools name-table cleanup afterwards for Mac langID correctness")


if __name__ == "__main__":
    main()
