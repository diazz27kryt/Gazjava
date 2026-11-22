#!/usr/bin/env python3
"""Sanity checks for the GazJava resources. Exits non-zero on the first problem set found.

Checks:
* every .json file under src/main/resources parses;
* every drink has a texture (16x16 PNG), model, item definition, recipe and en/ru translation;
* recipes only reference valid shapes (<= 9 ingredients) and point at existing result items;
* gradle.properties pins Minecraft 1.21.11 and mod version 0.1.0-alpha.
"""
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "src/main/resources"
MOD_ID = "gazjava"
DRINKS = ["gazyava_nefora", "gazyava_ofnika", "gazyava_motobrata"]

errors = []


def fail(message):
    errors.append(message)


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - report any parse problem
        fail(f"{path.relative_to(ROOT)}: invalid JSON ({exc})")
        return None


# 1. all JSON parses (fabric.mod.json contains ${...} placeholders, which are still valid strings)
for path in sorted(RES.rglob("*.json")):
    load_json(path)

# 2. per-drink files
lang = {}
for code in ("en_us", "ru_ru"):
    data = load_json(RES / f"assets/{MOD_ID}/lang/{code}.json") or {}
    lang[code] = data
    if f"itemGroup.{MOD_ID}" not in data:
        fail(f"{code}: missing itemGroup.{MOD_ID}")

for name in DRINKS:
    tex = RES / f"assets/{MOD_ID}/textures/item/{name}.png"
    if not tex.exists():
        fail(f"missing texture {tex.relative_to(ROOT)}")
    else:
        with Image.open(tex) as img:
            if img.size != (16, 16) or img.mode != "RGBA":
                fail(f"{tex.name}: expected 16x16 RGBA, got {img.size} {img.mode}")

    model = load_json(RES / f"assets/{MOD_ID}/models/item/{name}.json") or {}
    if model.get("textures", {}).get("layer0") != f"{MOD_ID}:item/{name}":
        fail(f"model {name}: wrong layer0 texture")

    item_def = load_json(RES / f"assets/{MOD_ID}/items/{name}.json") or {}
    if item_def.get("model", {}).get("model") != f"{MOD_ID}:item/{name}":
        fail(f"item definition {name}: wrong model reference")

    for code, data in lang.items():
        if not data.get(f"item.{MOD_ID}.{name}"):
            fail(f"{code}: missing translation for {name}")

    recipe = load_json(RES / f"data/{MOD_ID}/recipe/{name}.json") or {}
    if recipe.get("type") != "minecraft:crafting_shapeless":
        fail(f"recipe {name}: unexpected type {recipe.get('type')}")
    ingredients = recipe.get("ingredients", [])
    if not 1 <= len(ingredients) <= 9:
        fail(f"recipe {name}: {len(ingredients)} ingredients do not fit a 3x3 crafting grid")
    if "minecraft:glass_bottle" not in ingredients:
        fail(f"recipe {name}: no glass bottle")
    if recipe.get("result", {}).get("id") != f"{MOD_ID}:{name}":
        fail(f"recipe {name}: wrong result id")

# 3. recipe contents match the spec (with the documented Motobrata deviation)
expected = {
    "gazyava_nefora": {"minecraft:apple": 1, "minecraft:sugar": 1, "minecraft:glass_bottle": 1},
    "gazyava_ofnika": {"minecraft:apple": 2, "minecraft:sugar": 2, "minecraft:honey_bottle": 1,
                       "minecraft:glass_bottle": 1},
    "gazyava_motobrata": {"minecraft:apple": 2, "minecraft:sugar": 2, "minecraft:honey_bottle": 2,
                          "minecraft:golden_apple": 1, "minecraft:glass_bottle": 1},
}
for name, want in expected.items():
    recipe = json.loads((RES / f"data/{MOD_ID}/recipe/{name}.json").read_text(encoding="utf-8"))
    got = {}
    for ing in recipe["ingredients"]:
        got[ing] = got.get(ing, 0) + 1
    if got != want:
        fail(f"recipe {name}: ingredients {got} != expected {want}")

# 4. gradle.properties pins
props = {}
for line in (ROOT / "gradle.properties").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.lstrip().startswith("#"):
        key, value = line.split("=", 1)
        props[key.strip()] = value.strip()
if props.get("minecraft_version") != "1.21.11":
    fail(f"minecraft_version is {props.get('minecraft_version')}, expected 1.21.11")
if props.get("mod_version") != "0.1.0-alpha":
    fail(f"mod_version is {props.get('mod_version')}, expected 0.1.0-alpha")

if errors:
    print("VALIDATION FAILED:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print("OK: all resource checks passed")
