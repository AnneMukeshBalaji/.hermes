#!/usr/bin/env python3
"""Build a custom font by merging glyphs from a source font into a base font,
using fonttools directly (no FontForge). Handles UPM scaling, name table cleanup,
and monospace flags for terminal use.

Usage:
    python3 build_custom_font_fonttools.py \\
        --base JetBrainsMonoNerdFontPropo-Regular.ttf \\
        --source GoogleSansCodeProportionalNerdFontPropo-Regular.ttf \\
        --output LordSivaNerdFontPropo-Regular.ttf \\
        --family "LordSiva Nerd Font Propo" \\
        --style "Regular"
"""
import argparse, os, shutil
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates
from fontTools.ttLib.tables._n_a_m_e import NameRecord
from fontTools.ttLib.tables.ttProgram import Program


def get_upm(tt):
    return tt['head'].unitsPerEm


def copy_and_scale_glyphs(base, source, codes, scale, force_width=None):
    """Copy glyphs from source to base, scaling coordinates and widths."""
    cmap_b = base.getBestCmap()
    cmap_s = source.getBestCmap()
    glyf_b = base['glyf']
    glyf_s = source['glyf']
    hmtx_b = base['hmtx']
    hmtx_s = source['hmtx']

    for code in codes:
        if code not in cmap_b:
            print(f"  Warning: U+{code:04X} not in base, skipping")
            continue
        if code not in cmap_s:
            print(f"  Warning: U+{code:04X} not in source, skipping")
            continue

        gn_b = cmap_b[code]
        gn_s = cmap_s[code]
        src = glyf_s[gn_s]

        if not (hasattr(src, 'numberOfContours') and src.numberOfContours > 0):
            print(f"  Warning: U+{code:04X} is composite, skipping")
            continue

        # Scale coordinates
        new_coords = GlyphCoordinates()
        for x, y in src.coordinates:
            new_coords.append((int(x * scale), int(y * scale)))

        new_glyph = Glyph()
        new_glyph.numberOfContours = src.numberOfContours
        new_glyph.coordinates = new_coords
        new_glyph.endPtsOfContours = src.endPtsOfContours[:]
        new_glyph.flags = src.flags[:]
        new_glyph.program = Program()

        if src.xMin is not None:
            new_glyph.xMin = int(src.xMin * scale)
            new_glyph.yMin = int(src.yMin * scale)
            new_glyph.xMax = int(src.xMax * scale)
            new_glyph.yMax = int(src.yMax * scale)

        glyf_b[gn_b] = new_glyph

        # Force uniform width if requested (critical for terminal fonts),
        # otherwise scale source width to target UPM.
        if force_width is not None:
            _, old_lsb = hmtx_s[gn_s]
            hmtx_b[gn_b] = (force_width, int(old_lsb * scale))
        else:
            old_width, old_lsb = hmtx_s[gn_s]
            hmtx_b[gn_b] = (int(old_width * scale), int(old_lsb * scale))

        print(f"  Copied U+{code:04X} ({chr(code)})")


def fix_name_table(tt, family, style, output_name):
    """Replace critical name records with clean entries."""
    name = tt['name']
    # Preserve copyright, version, trademark, URLs, license
    keep_ids = {0, 5, 7, 8, 9, 10, 11, 12, 13, 14}
    name.names = [r for r in name.names if r.nameID in keep_ids]

    def add(plat, enc, lang, nid, val):
        r = NameRecord()
        r.platformID = plat
        r.platEncID = enc
        r.langID = lang
        r.nameID = nid
        r.string = val
        name.names.append(r)

    entries = [
        (1, family),                     # Family
        (2, style),                      # SubFamily
        (4, f"{family} {style}"),        # Full name
        (6, output_name),                # PostScript name
    ]
    for nid, val in entries:
        add(1, 0, 0, nid, val)           # Mac (lang=0, NOT 0x0409!)
        add(3, 1, 0x0409, nid, val)      # Windows

    # Preferred family/styles (Windows only, no Mac equivalents expected)
    add(3, 1, 0x0409, 16, family)
    add(3, 1, 0x0409, 17, style)


def set_monospace_flags(tt):
    """Mark font as monospace for terminal emulators."""
    tt['post'].isFixedPitch = 1
    tt['OS/2'].panose.bProportion = 9   # Monospaced
    tt['OS/2'].panose.bFamilyType = 2   # Latin Text
    tt['OS/2'].panose.bSerifStyle = 0   # Sans Serif


def main():
    ap = argparse.ArgumentParser(description="Build custom font with fonttools")
    ap.add_argument("--base", required=True, help="Base font path (target)")
    ap.add_argument("--source", required=True, help="Source font path (glyph donor)")
    ap.add_argument("--output", required=True, help="Output font path")
    ap.add_argument("--family", default="CustomFont", help="Font family name")
    ap.add_argument("--style", default="Regular", help="Font style name")
    ap.add_argument("--codes",
                    default="41-5A,61-7A",
                    help="Unicode ranges to copy, e.g. '41-5A,61-7A'")
    ap.add_argument("--force-width", type=int, default=None,
                    help="Force all substituted glyphs to this advance width (e.g. 600 for terminal fonts). "
                         "Critical for terminal emulators: a single non-uniform glyph width "
                         "causes silent fallback to a different font.")
    args = ap.parse_args()

    # Parse code ranges
    codes = []
    for part in args.codes.split(","):
        if "-" in part:
            start, end = part.split("-")
            codes.extend(range(int(start, 16), int(end, 16) + 1))
        else:
            codes.append(int(part, 16))

    # Copy base font
    shutil.copy2(args.base, args.output)
    base = TTFont(args.output)
    source = TTFont(args.source)

    base_upm = get_upm(base)
    source_upm = get_upm(source)
    scale = base_upm / source_upm

    print(f"Base UPM:   {base_upm}")
    print(f"Source UPM: {source_upm}")
    print(f"Scale:      {scale:.4f}")
    print(f"Output:     {args.output}")

    if scale != 1.0:
        print("UPM mismatch detected — glyphs will be scaled.")

    # Output name for PostScript (spaces -> empty)
    output_name = f"{args.family.replace(' ', '')}-{args.style.replace(' ', '')}"

    copy_and_scale_glyphs(base, source, codes, scale, args.force_width)

    set_monospace_flags(base)

    fix_name_table(base, args.family, args.style, output_name)

    base.save(args.output)
    base.close()
    source.close()
    print(f"\nDone: {args.output}")
    print("Next: cp to ~/.fonts/ && rm -rf ~/.cache/fontconfig/* && fc-cache -fv")


if __name__ == "__main__":
    main()
