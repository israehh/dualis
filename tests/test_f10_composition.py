"""Tests F10: habitaciones nacen de datos, no de código."""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dualis.core.bus import EventBus
from dualis.systems.observable import Observable
from dualis.systems.observe import ObserveSystem
from dualis.systems.transformable import Transformable
from dualis.world.blueprint import load_blueprint, validate_blueprint
from dualis.world.builder import RoomBuilder
from dualis.world.factory import KINDS
from dualis.world.room import RoomManager

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINTS_DIR = ROOT / "data" / "blueprints"
PATTERNS_DIR = ROOT / "data" / "patterns"
DEMOS = ["room_height", "room_timed", "room_observe"]


def _pattern(pid):
    for path in PATTERNS_DIR.glob("*.json"):
        raw = json.loads(path.read_text(encoding="utf-8"))
        if raw["id"] == pid:
            return raw
    raise KeyError(pid)


def test_blueprints_validos():
    for name in DEMOS:
        blueprint = load_blueprint(BLUEPRINTS_DIR / (name + ".json"), PATTERNS_DIR)
        assert blueprint.ideas and len(blueprint.ideas) == 1
        assert len(blueprint.exit_rect) == 4


def test_blueprint_invalido_rechazado():
    base = {
        "id": "BAD", "nombre": "Mala", "pattern": "PATTERN_HEIGHT",
        "observables": [], "transformables": [],
        "exit": {"rect": [0, 0, 10, 10]}, "enlaces": ["ROOM_SLICE"], "ideas": ["x"],
    }
    assert validate_blueprint(dict(base), PATTERNS_DIR) == []
    bad = dict(base, pattern="PATTERN_NOPE")
    assert "patron-desconocido" in validate_blueprint(bad, PATTERNS_DIR)
    bad = dict(base, exit={"rect": [600, 300, 100, 80]})
    assert "salida-inaccesible" in validate_blueprint(bad, PATTERNS_DIR)
    bad = dict(base, ideas=["a", "b"])
    assert "requiere-una-idea" in validate_blueprint(bad, PATTERNS_DIR)
    bad = dict(base, observables=[{"kind": "uno", "params": {}}])
    assert any(e.startswith("observable-invalido") for e in validate_blueprint(bad, PATTERNS_DIR))
    try:
        import tempfile
        tmp = Path(tempfile.mkdtemp()) / "bad.json"
        tmp.write_text(json.dumps(bad), encoding="utf-8")
        load_blueprint(tmp, PATTERNS_DIR)
    except ValueError:
        return
    raise AssertionError("debió fallar el plano inválido")


def test_builder_registra_y_crea():
    rooms = RoomManager(EventBus())
    rooms.load_directory(ROOT / "data" / "rooms")
    builder = RoomBuilder(rooms)
    for name in DEMOS:
        blueprint = load_blueprint(BLUEPRINTS_DIR / (name + ".json"), PATTERNS_DIR)
        built = builder.build(blueprint, _pattern(blueprint.pattern))
        assert rooms.definitions[blueprint.rid].nombre == blueprint.nombre
        assert built.definition.rid == blueprint.rid
        assert built.actors, name


def test_observables_y_transformables_registrados():
    from dualis.systems.observable import ObservableRegistry
    from dualis.systems.transformable import TransformableRegistry
    rooms = RoomManager(EventBus())
    builder = RoomBuilder(rooms)
    oreg, treg = ObservableRegistry(), TransformableRegistry()
    counts = {"obs": 0, "trs": 0}
    for name in DEMOS:
        blueprint = load_blueprint(BLUEPRINTS_DIR / (name + ".json"), PATTERNS_DIR)
        for actor in builder.build(blueprint).actors:
            if isinstance(actor, Observable):
                oreg.register(actor)
                counts["obs"] += 1
            if isinstance(actor, Transformable):
                treg.register(actor)
                counts["trs"] += 1
    assert counts == {"obs": 2, "trs": 1}
    observe = ObserveSystem(oreg)
    assert observe.request("UNO") is True
    assert all(o.frozen for o in oreg.all())


def test_salida_accesible():
    for name in DEMOS:
        blueprint = load_blueprint(BLUEPRINTS_DIR / (name + ".json"), PATTERNS_DIR)
        x, y, w, h = blueprint.exit_rect
        assert 0 <= x and 0 <= y and x + w <= 640 and y + h <= 360
        assert w > 0 and h > 0


def test_patron_aplicado():
    rooms = RoomManager(EventBus())
    builder = RoomBuilder(rooms)
    for name in DEMOS:
        blueprint = load_blueprint(BLUEPRINTS_DIR / (name + ".json"), PATTERNS_DIR)
        missing = builder.coverage(blueprint, _pattern(blueprint.pattern))
        assert missing == [], (name, missing)


def test_sin_duplicar_factory():
    import dualis.world.builder as builder_mod
    import dualis.world.factory as factory_mod
    assert builder_mod.create is factory_mod.create
    rooms = RoomManager(EventBus())
    built = RoomBuilder(rooms).build(
        load_blueprint(BLUEPRINTS_DIR / "room_height.json", PATTERNS_DIR))
    assert type(built.actors[0]).__module__ == "dualis.world.transformables"


def test_rooms_origen_intactas():
    rooms = RoomManager(EventBus())
    rooms.load_directory(ROOT / "data" / "rooms")
    assert rooms.definitions["ROOM_A"].enlaces == ("ROOM_B",)
    assert rooms.definitions["ROOM_B"].enlaces == ("ROOM_A",)
    assert rooms.definitions["ROOM_SLICE"].enlaces == ("ROOM_A",)


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)
