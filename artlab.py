import subprocess
import sys

if len(sys.argv) != 5:
    print("Uso:")
    print("python artlab.py ID REGION CATEGORY MATERIAL")
    sys.exit(1)

asset_id = sys.argv[1]
region = sys.argv[2]
category = sys.argv[3]
material = sys.argv[4]

subprocess.run([
    "python",
    "create_asset.py",
    asset_id,
    region,
    category,
    material
])

spec_path = (
    f"artlab/assets/{category}s/"
    f"{region}/{asset_id}/spec.json"
)

subprocess.run([
    "python",
    "generate_prompt.py",
    spec_path
])

print("\n[ARTLAB] Pipeline completado.")