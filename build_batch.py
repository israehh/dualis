from pathlib import Path
import subprocess
import sys

if len(sys.argv) != 2:
    print("Uso:")
    print("python build_batch.py archivo.txt")
    sys.exit(1)

batch_file = Path(sys.argv[1])

if not batch_file.exists():
    print(f"[ERROR] No existe: {batch_file}")
    sys.exit(1)

total = 0
ok = 0
errors = 0

for line_num, line in enumerate(
    batch_file.read_text(encoding="utf-8").splitlines(),
    start=1
):
    line = line.strip()

    # Ignorar líneas vacías
    if not line:
        continue

    # Ignorar comentarios
    if line.startswith("#"):
        continue

    parts = line.split()

    if len(parts) != 4:
        print(
            f"[ERROR] Línea {line_num}: "
            f"se esperaban 4 campos y se encontraron {len(parts)}"
        )
        print(f"        {line}")
        errors += 1
        continue

    asset_id, region, category, material = parts

    total += 1

    print("\n" + "=" * 60)
    print(f"[CREANDO] {asset_id}")
    print("=" * 60)

    result = subprocess.run(
        [
            "python",
            "artlab.py",
            asset_id,
            region,
            category,
            material
        ]
    )

    if result.returncode == 0:
        ok += 1
    else:
        errors += 1

print("\n" + "=" * 60)
print("RESUMEN")
print("=" * 60)
print(f"Assets procesados : {total}")
print(f"Correctos         : {ok}")
print(f"Errores           : {errors}")