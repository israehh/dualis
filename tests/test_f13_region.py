"""Tests F13: R1 El Vestíbulo, primera región real. Solo datos + runtimes existentes."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dualis.core.bus import EventBus
from dualis.systems.cooperation import MountAction
from dualis.systems.observable import Observable
from dualis.systems.room_runtime import RoomRuntimeManager
from dualis.systems.transform import TransformSystem
from dualis.systems.transformable import Transformable
from dualis.world.blueprint import load_blueprint
from dualis.world.builder import RoomBuilder
from dualis.world.entity import Entity
from dualis.world.room import RoomManager

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINTS_DIR = ROOT / "data" / "blueprints"
PATTERNS_DIR = ROOT / "data" / "patterns"
REGION = json.loads((ROOT / "data" / "regions" / "vestibulo.json").read_text(encoding="utf-8"))
CHAIN = REGION["rooms"]
EXPECTED = {
    "VEST_01": "PATTERN_OBSERVE_TO_CROSS",
    "VEST_02": "PATTERN_TIMED_WINDOW",
    "VEST_03": "PATTERN_HEIGHT",
    "VEST_04": "PATTERN_TRANSFORM_TO_REACH",
    "VEST_05": "PATTERN_SHARED_PASSAGE",
    "VEST_06": "PATTERN_TIMED_WINDOW",
    "VEST_07": "PATTERN_OBSERVE_TO_CROSS",
    "VEST_08": "PATTERN_HEIGHT",
    "VEST_09": "PATTERN_TRANSFORM_TO_REACH",
    "VEST_10": "PATTERN_SHARED_PASSAGE",
    "VEST_11": "PATTERN_TIMED_WINDOW",
    "VEST_12": "PATTERN_HEIGHT",
    "VEST_13": "PATTERN_SHARED_PASSAGE",
    "VEST_14": "PATTERN_TRANSFORM_TO_REACH",
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


def _play(rid):
    bus = EventBus()
    rooms = RoomManager(bus)
    rooms.load_directory(ROOT / "data" / "rooms")
    builder = RoomBuilder(rooms)
    blueprint = load_blueprint(BLUEPRINTS_DIR / (rid.lower() + ".json"), PATTERNS_DIR)
    built = builder.build(blueprint, _pattern(blueprint.pattern))
    uno = Entity("UNO", x=120.0, y=280.0)
    dos = Entity("DOS", x=220.0, y=280.0)
    transform = TransformSystem(bus)
    mount = MountAction(uno, dos, bus)
    runtimes = RoomRuntimeManager(bus, transform, mount, uno, dos)
    runtimes.add_room(blueprint, built.actors)
    rooms.enter(rid)
    return {"bus": bus, "uno": uno, "dos": dos, "transform": transform,
            "mount": mount, "runtimes": runtimes,
            "runtime": runtimes.runtime_for(rid), "exit": blueprint.exit_rect}


def _center(rect):
    x, y, w, h = rect
    return x + w / 2.0, y + h / 2.0


def _park(ctx, rect):
    cx, cy = _center(rect)
    ctx["uno"].x, ctx["uno"].y = cx, cy
    ctx["dos"].x, ctx["dos"].y = cx, cy


def test_region_manifiesto_coherente():
    assert REGION["id"] == "R1_VESTIBULO"
    assert len(CHAIN) == 14
    assert len(set(CHAIN)) == 14
    assert REGION["rooms"][0] == "VEST_01"
    assert REGION["rooms"][-1] == "VEST_14"


def test_tamano_region():
    assert 12 <= len(CHAIN) <= 15


def test_cadena_lineal():
    rooms, _ = _load_all()
    assert rooms.definitions["VEST_01"].enlaces == ("ROOM_SLICE", "VEST_02")
    for prev, rid, nxt in zip(CHAIN, CHAIN[1:-1], CHAIN[2:]):
        assert rooms.definitions[rid].enlaces == (prev, nxt), rid
    assert rooms.definitions["VEST_14"].enlaces == ("VEST_13", "BIB_01")


def test_patron_dificultad_y_proposito():
    short = {"VEST_01", "VEST_02", "VEST_03", "VEST_04"}
    for rid in CHAIN:
        blueprint = load_blueprint(BLUEPRINTS_DIR / (rid.lower() + ".json"), PATTERNS_DIR)
        assert blueprint.pattern == EXPECTED[rid], rid
        assert len(blueprint.ideas) == 1, rid
        assert blueprint.proposito, rid
        assert blueprint.dificultad == ("corta" if rid in short else "media"), rid


def test_sin_mecanicas_ni_patrones_nuevos():
    for rid in CHAIN:
        raw = json.loads((BLUEPRINTS_DIR / (rid.lower() + ".json")).read_text(encoding="utf-8"))
        kinds = {s["kind"] for s in raw["observables"] + raw["transformables"]}
        assert kinds <= LIBRARY_KINDS, (rid, kinds)


def test_todas_con_runtime():
    _, built = _load_all()
    bus = EventBus()
    uno = Entity("UNO")
    dos = Entity("DOS")
    runtimes = RoomRuntimeManager(bus, TransformSystem(bus), MountAction(uno, dos, bus), uno, dos)
    for rid in CHAIN:
        blueprint = load_blueprint(BLUEPRINTS_DIR / (rid.lower() + ".json"), PATTERNS_DIR)
        assert runtimes.add_room(blueprint, built[rid].actors) is not None, rid


def test_examen_regional_evalua_todo():
    ctx = _play("VEST_14")
    _park(ctx, ctx["exit"])
    ctx["runtimes"].update(0.1, "VEST_14")
    assert ctx["runtime"].state == "LOCKED"
    assert "ROOM_COMPLETED" not in ctx["bus"].log


def test_examen_regional_se_resuelve():
    from dualis.systems.observe import ObserveSystem
    ctx = _play("VEST_14")
    observe = ObserveSystem(ctx["runtimes"].registry_for("VEST_14"), ctx["bus"])
    assert observe.request("UNO") is True
    observe.update(0.1)
    assert ctx["runtimes"].try_transform("VEST_14", "DOS") is True
    ctx["uno"].x, ctx["uno"].y = 300.0, 100.0
    ctx["dos"].x, ctx["dos"].y = 310.0, 100.0
    assert ctx["mount"].request("UNO") is True
    _park(ctx, ctx["exit"])
    ctx["dos"].x, ctx["dos"].y = 320.0, 95.0
    ctx["mount"].update(0.1)
    ctx["runtimes"].update(0.1, "VEST_14")
    assert ctx["runtime"].state == "COMPLETED"
    assert "ROOM_COMPLETED" in ctx["bus"].log


def test_puerta_entrada_enseña_observar():
    from dualis.systems.observe import ObserveSystem
    ctx = _play("VEST_01")
    _park(ctx, ctx["exit"])
    ctx["runtimes"].update(0.1, "VEST_01")
    assert ctx["runtime"].state == "LOCKED"
    observe = ObserveSystem(ctx["runtimes"].registry_for("VEST_01"), ctx["bus"])
    observe.request("UNO")
    observe.update(0.1)
    ctx["runtimes"].update(0.1, "VEST_01")
    assert ctx["runtime"].state == "COMPLETED"


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)
