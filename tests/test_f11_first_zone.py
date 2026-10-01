"""Tests F11: primera mini-zona pedagógica, solo datos."""
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
from dualis.world.factory import KINDS
from dualis.world.room import RoomManager

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINTS_DIR = ROOT / "data" / "blueprints"
PATTERNS_DIR = ROOT / "data" / "patterns"
CHAIN = ["ROOM_01", "ROOM_02", "ROOM_03", "ROOM_04", "ROOM_05"]
EXPECTED_PATTERNS = {
    "ROOM_01": "PATTERN_OBSERVE_TO_CROSS",
    "ROOM_02": "PATTERN_HEIGHT",
    "ROOM_03": "PATTERN_TRANSFORM_TO_REACH",
    "ROOM_04": "PATTERN_SHARED_PASSAGE",
    "ROOM_05": "PATTERN_TRANSFORM_TO_REACH",
}
LIBRARY_KINDS = {"moving", "oscillating", "timed", "phenomenon",
                 "step", "bridge", "platform", "testbox"}


def _pattern(pid):
    for path in PATTERNS_DIR.glob("*.json"):
        raw = json.loads(path.read_text(encoding="utf-8"))
        if raw["id"] == pid:
            return raw
    raise KeyError(pid)


def _load_all():
    rooms = RoomManager(EventBus())
    rooms.load_directory(ROOT / "data" / "rooms")
    builder = RoomBuilder(rooms)
    built = {}
    for rid in CHAIN:
        blueprint = load_blueprint(BLUEPRINTS_DIR / (rid.lower() + ".json"), PATTERNS_DIR)
        built[rid] = builder.build(blueprint, _pattern(blueprint.pattern))
    return rooms, built


def test_cadena_lineal_sin_ramas():
    rooms, _ = _load_all()
    assert rooms.definitions["ROOM_01"].enlaces == ("ROOM_SLICE", "ROOM_02")
    assert rooms.definitions["ROOM_02"].enlaces == ("ROOM_01", "ROOM_03")
    assert rooms.definitions["ROOM_03"].enlaces == ("ROOM_02", "ROOM_04")
    assert rooms.definitions["ROOM_04"].enlaces == ("ROOM_03", "ROOM_05")
    assert rooms.definitions["ROOM_05"].enlaces == ("ROOM_04",)


def test_patron_por_habitacion():
    for rid, pid in EXPECTED_PATTERNS.items():
        blueprint = load_blueprint(BLUEPRINTS_DIR / (rid.lower() + ".json"), PATTERNS_DIR)
        assert blueprint.pattern == pid, rid
        assert len(blueprint.ideas) == 1, rid


def test_lecciones():
    _, built = _load_all()
    assert built["ROOM_01"].actors and all(isinstance(a, Observable) for a in built["ROOM_01"].actors)
    assert built["ROOM_02"].actors and all(isinstance(a, Transformable) for a in built["ROOM_02"].actors)
    assert built["ROOM_03"].actors and all(isinstance(a, Transformable) for a in built["ROOM_03"].actors)
    r4 = built["ROOM_04"].actors
    assert any(isinstance(a, Observable) for a in r4)
    assert any(isinstance(a, Transformable) for a in r4)


def test_examen_requiere_todo():
    _, built = _load_all()
    actors = built["ROOM_05"].actors
    assert any(isinstance(a, Observable) for a in actors)
    assert any(isinstance(a, Transformable) for a in actors)
    from dualis.systems.cooperation import MountAction
    assert MountAction is not None


def test_sin_mecanicas_nuevas():
    for rid in CHAIN:
        raw = json.loads((BLUEPRINTS_DIR / (rid.lower() + ".json")).read_text(encoding="utf-8"))
        kinds = {s["kind"] for s in raw["observables"] + raw["transformables"]}
        assert kinds <= LIBRARY_KINDS, (rid, kinds)
        assert kinds <= set(KINDS), (rid, kinds)


def test_resolubles_por_construccion():
    rooms, built = _load_all()
    for rid in CHAIN:
        blueprint = load_blueprint(BLUEPRINTS_DIR / (rid.lower() + ".json"), PATTERNS_DIR)
        x, y, w, h = blueprint.exit_rect
        assert 0 <= x and 0 <= y and x + w <= 640 and y + h <= 360, rid
        assert w > 0 and h > 0, rid
        missing = RoomBuilder(rooms).coverage(blueprint, _pattern(blueprint.pattern))
        assert missing == [], (rid, missing)
        assert built[rid].actors, rid


def test_todos_los_blueprints_cargan():
    rooms = RoomManager(EventBus())
    rooms.load_directory(ROOT / "data" / "rooms")
    builder = RoomBuilder(rooms)
    count = 0
    for path in sorted(BLUEPRINTS_DIR.glob("*.json")):
        blueprint = load_blueprint(path, PATTERNS_DIR)
        builder.build(blueprint)
        count += 1
    assert count == 44
    assert len(rooms.definitions) == 47


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)
