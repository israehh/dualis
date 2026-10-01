import json
import sys
from pathlib import Path

if len(sys.argv) != 5:
    print("Uso:")
    print("python create_asset.py ID REGION CATEGORY MATERIAL")
    sys.exit(1)

asset_id = sys.argv[1]
region = sys.argv[2]
category = sys.argv[3]
material = sys.argv[4]

asset_dir = Path("artlab") / "assets" / f"{category}s" / region / asset_id

asset_dir.mkdir(parents=True, exist_ok=True)

spec = {
    "id": asset_id,
    "category": category,
    "region": region,
    "material": material,
    "footprint": [1, 1],
    "height": 1,
    "anchor": "bottom_center",
    "style": "dualis_v1"
}

with open(asset_dir / "spec.json", "w", encoding="utf-8") as f:
    json.dump(spec, f, indent=2)

with open(asset_dir / "notes.md", "w", encoding="utf-8") as f:
    f.write(f"# {asset_id}\n\nNotas del asset.\n")

with open(asset_dir / "prompt.txt", "w", encoding="utf-8") as f:
    f.write("PENDIENTE DE GENERAR\n")

print(f"[OK] Asset creado en:\n{asset_dir}")