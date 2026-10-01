"""Planos F10: habitaciones descritas como datos. Sin lógica de juego."""
import json
from dataclasses import dataclass
from pathlib import Path

try:
    from dualis.world.factory import KINDS
except ImportError:
    from src.dualis.world.factory import KINDS

OBSERVABLE_KINDS = {"phenomenon", "moving", "oscillating", "timed"}
TRANSFORMABLE_KINDS = {"testbox", "step", "bridge", "platform"}
GLOBAL_POWERS = {"mount", "observe", "transform"}
BOUNDS = (640, 360)


@dataclass(frozen=True)
class RoomBlueprint:
    rid: str
    nombre: str
    pattern: str
    observables: tuple = ()
    transformables: tuple = ()
    exit_rect: tuple = ()
    enlaces: tuple = ()
    ideas: tuple = ()
    proposito: str = ""
    dificultad: str = "corta"


def known_patterns(directory):
    return {p["id"] for p in (
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(Path(directory).glob("*.json"))
    )}


def validate_blueprint(raw, patterns_dir):
    errors = []
    if not raw.get("id"):
        errors.append("sin-id")
    if not raw.get("nombre"):
        errors.append("sin-nombre")
    if raw.get("pattern") not in known_patterns(patterns_dir):
        errors.append("patron-desconocido")
    for spec in raw.get("observables", []):
        if spec.get("kind") not in OBSERVABLE_KINDS or spec.get("kind") not in KINDS:
            errors.append("observable-invalido:%s" % spec.get("kind"))
            break
    for spec in raw.get("transformables", []):
        if spec.get("kind") not in TRANSFORMABLE_KINDS or spec.get("kind") not in KINDS:
            errors.append("transformable-invalido:%s" % spec.get("kind"))
            break
    rect = raw.get("exit", {}).get("rect", None)
    if (not isinstance(rect, list) or len(rect) != 4
            or min(rect) < 0 or rect[0] + rect[2] > BOUNDS[0]
            or rect[1] + rect[3] > BOUNDS[1] or rect[2] <= 0 or rect[3] <= 0):
        errors.append("salida-inaccesible")
    if not isinstance(raw.get("enlaces", None), list) or len(raw.get("enlaces", [])) < 1:
        errors.append("sin-enlaces")
    if not isinstance(raw.get("ideas", None), list) or len(raw.get("ideas", [])) != 1:
        errors.append("requiere-una-idea")
    if "proposito" in raw and not raw.get("proposito"):
        errors.append("proposito-vacio")
    if "dificultad" in raw and raw.get("dificultad") not in ("corta", "media"):
        errors.append("dificultad-invalida")
    return errors


def load_blueprint(path, patterns_dir):
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    errors = validate_blueprint(raw, patterns_dir)
    if errors:
        raise ValueError("plano inválido %s: %s" % (path, ",".join(errors)))
    return RoomBlueprint(
        rid=raw["id"],
        nombre=raw["nombre"],
        pattern=raw["pattern"],
        observables=tuple((s["kind"], tuple(sorted(s.get("params", {}).items()))) for s in raw.get("observables", [])),
        transformables=tuple((s["kind"], tuple(sorted(s.get("params", {}).items()))) for s in raw.get("transformables", [])),
        exit_rect=tuple(raw["exit"]["rect"]),
        enlaces=tuple(raw["enlaces"]),
        ideas=tuple(raw["ideas"]),
        proposito=raw.get("proposito", ""),
        dificultad=raw.get("dificultad", "corta"),
    )
