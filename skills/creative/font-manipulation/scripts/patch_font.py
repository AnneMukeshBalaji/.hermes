import fontforge


def replace_glyphs(source_path, dest_path, glyph_names, scale=1.0):
    """Copy glyphs from source to destination font, with UPM scaling.

    Args:
        source_path: Path to the source font file.
        dest_path: Path to the destination font file (modified in-place).
        glyph_names: List of glyph names or Unicode code points to copy.
        scale: UPM scale factor (dest_upm / src_upm). Required when the two
               fonts have different unitsPerEm values.
    """
    src = fontforge.open(source_path)
    dst = fontforge.open(dest_path)

    for name in glyph_names:
        if name not in src:
            print(f"Glyph {name} not found in source font {source_path}")
            continue
        if name not in dst:
            print(f"Glyph {name} not found in dest font {dest_path}")
            continue

        # Clear destination glyph before pasting
        dst.selection.select(name)
        dst.clear()

        # Copy from source and paste into destination
        src.selection.select(name)
        src.copy()
        dst.paste()

        # Handle UPM scaling
        if scale != 1.0:
            dst.selection.select(name)
            dst.transform([scale, 0, 0, scale, 0, 0])
            glyph = dst[name]
            glyph.width = int(glyph.width * scale)
            glyph.left_side_bearing = int(glyph.left_side_bearing * scale)
            glyph.right_side_bearing = int(glyph.right_side_bearing * scale)

        print(f"Replaced {name} in {dest_path}")

    dst.generate(dest_path)
    print(f"Saved changes to {dest_path}")


def replace_by_unicode(source_path, dest_path, codes, scale=1.0):
    """Copy glyphs by Unicode code point instead of glyph name."""
    names = []
    for cp in codes:
        if isinstance(cp, str):
            cp = ord(cp)
        src = fontforge.open(source_path)
        if cp in src:
            glyph_name = src[cp].glyphname
            names.append(glyph_name)
        src.close()
    replace_glyphs(source_path, dest_path, names, scale)


# Example: copy A-Z, a-z with UPM scaling (GSC UPM=2000 -> JetBrains UPM=1000)
# replace_by_unicode(
#     "GoogleSansCode.ttf",
#     "JetBrainsMono.ttf",
#     list(range(0x41, 0x5B)) + list(range(0x61, 0x7B)),
#     scale=0.5,
# )
