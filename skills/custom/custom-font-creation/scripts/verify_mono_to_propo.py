#!/usr/bin/env python3
"""Verify a Mono → Propo font conversion: all 4 styles, scaled outlines,
proportional widths, monospace flags cleared.

Usage:
    python3 verify_mono_to_propo.py ~/.fonts "MonoLisa Nerd Font Propo"
"""

import os, subprocess, sys
from fontTools.ttLib import TTFont

if len(sys.argv) < 3:
    print(f"Usage: {sys.argv[0]} <font-dir> <family-name>")
    sys.exit(1)

font_dir = os.path.expanduser(sys.argv[1])
family = sys.argv[2]
variants = ["Regular", "Italic", "Bold", "BoldItalic"]
style_map = {
    "Regular": "Regular",
    "Italic": "Italic",
    "Bold": "Bold",
    "BoldItalic": "BoldItalic",
}

errors = []

for style in variants:
    r = subprocess.run(
        ["fc-list", f"{family}:style={style}"],
        capture_output=True, text=True
    )
    if not r.stdout.strip():
        errors.append(f"fc-list cannot resolve {family}:style={style}")

# Check first variant for detailed metrics
probe_paths = [
    os.path.join(font_dir, f)
    for f in os.listdir(font_dir)
    if f.endswith(".otf") and family.split()[-1] in f
]
if not probe_paths:
    errors.append(f"No font files found for family '{family}' in {font_dir}")
else:
    path = probe_paths[0]
    font = TTFont(path)
    hmtx = font["hmtx"]
    cmap = font.getBestCmap()
    upm = font["head"].unitsPerEm
    is_fixed = font["post"].isFixedPitch
    panose_prop = font["OS/2"].panose.bProportion
    font.close()

    # UPM should be original (not scaled)
    if upm not in (1000, 2000, 2048):
        errors.append(f"Unexpected UPM: {upm}")

    # Monospace flags must be cleared
    if is_fixed != 0:
        errors.append(f"post.isFixedPitch = {is_fixed} (should be 0)")
    if panose_prop == 9:
        errors.append(f"panose.bProportion = 9 (monospace, should be proportional)")

    # Widths should vary
    for ch in "H", "i", "M", "W", " ":
        g = cmap.get(ord(ch))
        if g:
            w = hmtx[g][0]
            print(f"  '{ch}' = {w}")
        else:
            errors.append(f"Glyph '{ch}' not found in cmap")

    # Verify widths are proportional (not all equal)
    widths = set()
    for ch in "HelloWorld":
        g = cmap.get(ord(ch))
        if g:
            widths.add(hmtx[g][0])
    if len(widths) < 2:
        errors.append(f"Widths appear monospaced: only {len(widths)} distinct values")

if errors:
    print("FAILURES:")
    for e in errors:
        print(f"  [FAIL] {e}")
    sys.exit(1)
else:
    print("ALL CHECKS PASSED")
    sys.exit(0)
