"""Punto de entrada por módulo: py -m src.dualis desde la raíz."""
try:
    from dualis.main import main
except ImportError:
    from src.dualis.main import main


if __name__ == "__main__":
    raise SystemExit(main())
