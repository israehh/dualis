import json
from pathlib import Path

assets_root = Path("artlab/assets")

catalog = {}

for spec_file in assets_root.rglob("spec.json"):
    with open(spec_file, "r", encoding="utf-8") as f:
        spec = json.load(f)

    catalog[spec["id"]] = spec

registry_dir = Path("artlab/registry")
registry_dir.mkdir(exist_ok=True)

output = registry_dir / "assets.json"

with open(output, "w", encoding="utf-8") as f:
    json.dump(catalog, f, indent=2)

print(f"[OK] Catálogo generado: {output}")
print(f"Assets registrados: {len(catalog)}")