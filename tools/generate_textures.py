#!/usr/bin/env python3
"""Generates the 16x16 item textures (and the mod icon) for GazJava.

Every bottle is drawn by hand as a pixel map, so the three drinks have
different silhouettes, not just different colours:

* Gazyava Nefora   - tall slim soda bottle, purple liquid, green label
* Gazyava Ofnika   - round flask, black glass, red belt with a flame
* Gazyava Motobrata - wide squat bottle, black body, green lightning bolt

Run:  python3 tools/generate_textures.py
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
TEXTURES = ROOT / "src/main/resources/assets/gazjava/textures/item"
ICON = ROOT / "src/main/resources/assets/gazjava/icon.png"

# ---------------------------------------------------------------- Nefora ---
NEFORA_PALETTE = {
    ".": None,
    "O": "#1a0d2b",  # outline
    "C": "#7dff6a",  # cap light green
    "c": "#35c24a",  # cap mid green
    "g": "#1b7a30",  # cap dark green
    "w": "#e4efff",  # clear glass
    "W": "#ffffff",  # shine / fizz
    "L": "#c58bff",  # liquid light (left edge)
    "p": "#8f3fd8",  # liquid
    "P": "#5a1f96",  # liquid shadow (right edge)
    "G": "#4cf06a",  # label green
    "h": "#1f9a3a",  # label green shadow
    "V": "#6b2aa8",  # purple bolt on label
}
NEFORA = [
    "................",
    ".....OOOOOO.....",
    ".....OCCCcO.....",
    ".....OcccgO.....",
    "......OwWO......",
    "......OwwO......",
    "......OLpO......",
    ".....OLppPO.....",
    "....OLppWpPO....",
    "....OLGGGGhO....",
    "....OLGVGGhO....",
    "....OLGGVGhO....",
    "....OLGGGGhO....",
    "....OLppppPO....",
    "....OLpWppPO....",
    "....OOOOOOOO....",
]

# ---------------------------------------------------------------- Ofnika ---
OFNIKA_PALETTE = {
    ".": None,
    "O": "#08080c",  # outline
    "K": "#23232c",  # black glass
    "k": "#4e4e5c",  # glass highlight
    "R": "#e02222",  # red
    "r": "#8f1212",  # dark red
    "F": "#ff9a1f",  # flame orange
    "Y": "#ffe36b",  # flame yellow
    "W": "#ffffff",  # shine / fizz
    "S": "#b0b0bc",  # steel rim
}
OFNIKA = [
    "................",
    ".....OOOOOO.....",
    ".....ORRRrO.....",
    "......OSSO......",
    "......OKkO......",
    ".....OKkKKO.....",
    "....OKkWKKKO....",
    "...OKkKKKKKKO...",
    "..OKkKKKKKKKKO..",
    "..OkRRRFRRRRrO..",
    "..OkRRFYFRRRrO..",
    "..OkRRFYYFRRrO..",
    "..OKkKKFFKKKKO..",
    "...OKkKKKKKKO...",
    "....OKKKKKKO....",
    ".....OOOOOO.....",
]

# ------------------------------------------------------------- Motobrata ---
MOTOBRATA_PALETTE = {
    ".": None,
    "O": "#06100a",  # outline
    "K": "#1f2420",  # black glass
    "k": "#4b554d",  # glass highlight
    "N": "#3dff45",  # neon green
    "n": "#1fb82b",  # green
    "d": "#0e6a1c",  # deep green
    "W": "#ffffff",  # shine / fizz
    "S": "#a8b4aa",  # steel
}
MOTOBRATA = [
    "................",
    "....OOOOOOOO....",
    "....ONNNNnnO....",
    "....OnnnndnO....",
    "......OSSO......",
    ".....OKkKKO.....",
    "..OOOKkKKKOOO...",
    "..OKkKKKKNNKKO..",
    "..OKkKKKNNKKKO..",
    "..OKkKKNNNNNKO..",
    "..OKkKKKKNNKKO..",
    "..OKkKKKNNKKKO..",
    "..OKkKKNNKKKKO..",
    "..OddddddddddO..",
    "...OnnnnnnnnO...",
    "....OOOOOOOO....",
]

DRINKS = {
    "gazyava_nefora": (NEFORA, NEFORA_PALETTE),
    "gazyava_ofnika": (OFNIKA, OFNIKA_PALETTE),
    "gazyava_motobrata": (MOTOBRATA, MOTOBRATA_PALETTE),
}


def hex_to_rgba(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def render(pixel_map, palette):
    if len(pixel_map) != 16:
        raise ValueError(f"expected 16 rows, got {len(pixel_map)}")
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for y, row in enumerate(pixel_map):
        if len(row) != 16:
            raise ValueError(f"row {y} has {len(row)} chars: {row!r}")
        for x, ch in enumerate(row):
            colour = palette[ch]
            if colour is not None:
                img.putpixel((x, y), hex_to_rgba(colour))
    return img


def build_icon(images):
    size = 128
    icon = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    # dark rounded-ish background with a simple vertical gradient
    for y in range(size):
        shade = 28 + int(22 * y / size)
        for x in range(size):
            icon.putpixel((x, y), (shade, shade, shade + 10, 255))
    scale = 3  # 16px -> 48px
    positions = [(4, 40), (40, 40), (76, 40)]
    for img, (px, py) in zip(images, positions):
        big = img.resize((16 * scale, 16 * scale), Image.NEAREST)
        icon.paste(big, (px, py), big)
    return icon


def main():
    TEXTURES.mkdir(parents=True, exist_ok=True)
    rendered = []
    for name, (pixel_map, palette) in DRINKS.items():
        img = render(pixel_map, palette)
        img.save(TEXTURES / f"{name}.png")
        rendered.append(img)
        print("wrote", TEXTURES / f"{name}.png")
    build_icon(rendered).save(ICON)
    print("wrote", ICON)

    # preview sheet (not part of the mod) for visual review
    preview = Image.new("RGBA", (3 * 16 * 12 + 4 * 8, 16 * 12 + 16), (70, 70, 80, 255))
    for i, img in enumerate(rendered):
        big = img.resize((16 * 12, 16 * 12), Image.NEAREST)
        preview.paste(big, (8 + i * (16 * 12 + 8), 8), big)
    preview.save("/tmp/gazjava_preview.png")


if __name__ == "__main__":
    main()
