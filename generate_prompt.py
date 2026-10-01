import json
import sys
from pathlib import Path

if len(sys.argv) != 2:
    print("Uso:")
    print("python generate_prompt.py ruta/spec.json")
    sys.exit(1)

spec_path = Path(sys.argv[1])

with open(spec_path, "r", encoding="utf-8") as f:
    spec = json.load(f)

asset_id = spec["id"]
category = spec["category"]
region = spec["region"]
material = spec["material"]
footprint = spec["footprint"]
height = spec["height"]
anchor = spec["anchor"]
style = spec["style"]

prompt = f"""
{asset_id},
single isometric game asset,
2:1 isometric perspective,
{material} material,
region {region},
footprint {footprint[0]}x{footprint[1]} tiles,
height {height} tiles,
anchor {anchor},
top-left lighting,
soft painterly shading,
clean geometry,
isolated object,
plain background,
soft contact shadow,
style {style},
high quality fantasy puzzle game prop
""".strip()

prompt_path = spec_path.parent / "prompt.txt"

with open(prompt_path, "w", encoding="utf-8") as f:
    f.write(prompt)

print("\n=== PROMPT GENERADO ===\n")
print(prompt)

print(f"\nGuardado en:")
print(prompt_path)