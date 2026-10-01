import json
import subprocess
import sys
from pathlib import Path

OLLAMA_MODEL = "qwen2.5-coder:7b"

SYSTEM_PROMPT = """
You are ArtLab, an isometric game asset designer.

Generate a concise image-generation prompt.

Rules:
- 2:1 isometric perspective
- top-left lighting
- consistent style
- game asset
- isolated object
- plain background
- soft contact shadow
- no explanations
- return only the final prompt
"""

def generate_prompt(spec):
    asset_id = spec["id"]
    category = spec["category"]
    region = spec["region"]
    material = spec.get("material", "stone")

    user_prompt = f"""
Asset ID: {asset_id}
Category: {category}
Region: {region}
Material: {material}

Generate one image prompt.
"""

    result = subprocess.run(
        [
            "ollama",
            "run",
            OLLAMA_MODEL
        ],
        input=f"{SYSTEM_PROMPT}\n\n{user_prompt}",
        text=True,
        capture_output=True
    )

    return result.stdout.strip()


def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("python generate_prompt.py path/to/spec.json")
        return

    spec_path = Path(sys.argv[1])

    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    prompt = generate_prompt(spec)

    prompt_file = spec_path.parent / "prompt.txt"

    with open(prompt_file, "w", encoding="utf-8") as f:
        f.write(prompt)

    print(f"[OK] Prompt generated:")
    print(prompt)
    print(f"\nSaved to: {prompt_file}")


if __name__ == "__main__":
    main()