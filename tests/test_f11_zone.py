"""Tests Zona Umbral: 5 habitaciones conectadas solo con datos."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dualis.core.bus import EventBus
from dualis.systems.observable import Observable
from dualis.systems.transformable import Transformable
from dualis.world.blueprint import load_blueprint
from dualis.world.builder import RoomBuilder
from dualis.world.room import RoomManager

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINTS_DIR = ROOT / "data" / "blueprints"
PATTERNS_DIR = ROOT / "data" / "patterns"
ZONE = ["ZONE_01", "ZONE_02", "ZONE_03", "ZONE_04", "ZONE_05"]


def _pattern(pid):
    for path in PATTERNS_DIR.glob("*.json"):
        raw = json.loads(path.read_text(encoding="utf-8"))
        if raw["id"] == pid:
            return raw
    raise KeyError(pid)


def _zone():
    rooms = RoomManager(EventBus())
    rooms.load_directory(ROOT / "data" / "rooms")
    builder = RoomBuilder(rooms)
    built = {}
    for zid in ZONE:
        blueprint = load_blueprint(BLUEPRINTS_DIR / (zid.lower() + ".json"), PATTERNS_DIR)
        built[zid] = builder.build(blueprint, _pattern(blueprint.pattern))
    return rooms, built


def test_cadena_conectada():
    rooms, _ = _zone()
    assert "ROOM_SLICE" in rooms.definitions["ZONE_01"].enlaces
    for a, b in zip(ZONE, ZONE[1:]):
        assert b in rooms.definitions[a].enlaces, a
        assert a in rooms.definitions[b].enlaces, b
    assert "ZONE_01" in rooms.definitions["ZONE_05"].enlaces


def test_cada_una_ensena_algo():
    for zid in ZONE:
        blueprint = load_blueprint(BLUEPRINTS_DIR / (zid.lower() + ".json"), PATTERNS_DIR)
        assert len(blueprint.ideas) == 1, zid
        assert blueprint.observables or blueprint.transformables, zid
        assert builder_coverage_ok(blueprint)


def builder_coverage_ok(blueprint):
    rooms = RoomManager(EventBus())
    missing = RoomBuilder(rooms).coverage(blueprint, _pattern(blueprint.pattern))
    return missing == []


def test_examen_combina():
    blueprint = load_blueprint(BLUEPRINTS_DIR / "zone_05.json", PATTERNS_DIR)
    assert blueprint.observables and blueprint.transformables
    assert blueprint.pattern == "PATTERN_TRANSFORM_TO_REACH"


def test_salidas_distintas_y_accesibles():
    rects = []
    for zid in ZONE:
        blueprint = load_blueprint(BLUEPRINTS_DIR / (zid.lower() + ".json"), PATTERNS_DIR)
        x, y, w, h = blueprint.exit_rect
        assert 0 <= x and 0 <= y and x + w <= 640 and y + h <= 360, zid
        rects.append(tuple(blueprint.exit_rect))
    assert len(set(rects)) == 5


def test_actores_de_biblioteca():
    _, built = _zone()
    for zid, room in built.items():
        for actor in room.actors:
            assert isinstance(actor, (Observable, Transformable)), (zid, actor)
    kinds = {type(a).__name__ for r in built.values() for a in r.actors}
    assert kinds >= {"MovingPhenomenon", "StepTransformable", "OscillatingPhenomenon",
                     "BridgeTransformable", "TimedPhenomenon", "PlatformTransformable"}


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)
