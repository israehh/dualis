"""Tests F15: R3 El Taller de los Ecos, decisiones sin verbos nuevos."""
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
REGION = json.loads((ROOT / "data" / "regions" / "taller.json").read_text(encoding="utf-8"))
CHAIN = REGION["rooms"]
EXPECTED = {
    "TAL_01": "PATTERN_OBSERVE_TO_CROSS",
    "TAL_02": "PATTERN_TIMED_WINDOW",
    "TAL_03": "PATTERN_HEIGHT",
    "TAL_04": "PATTERN_TRANSFORM_TO_REACH",
    "TAL_05": "PATTERN_SHARED_PASSAGE",
    "TAL_06": "PATTERN_OBSERVE_TO_CROSS",
    "TAL_07": "PATTERN_TRANSFORM_TO_REACH",
    "TAL_08": "PATTERN_SHARED_PASSAGE",
    "TAL_09": "PATTERN_TRANSFORM_TO_REACH",
}
LIBRARY_KINDS = {"moving", "oscillating", "timed", "phenomenon",
                 "step", "bridge", "platform", "testbox"}
KNOWN_PATTERNS = {"PATTERN_OBSERVE_TO_CROSS", "PATTERN_TIMED_WINDOW", "PATTERN_HEIGHT",
                  "PATTERN_TRANSFORM_TO_REACH", "PATTERN_SHARED_PASSAGE"}


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
    bib = load_blueprint(BLUEPRINTS_DIR / "bib_08.json", PATTERNS_DIR)
    builder.build(bib, _pattern(bib.pattern))
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


def _mount_near(ctx, x, y):
    ctx["uno"].x, ctx["uno"].y = x - 5.0, y
    ctx["dos"].x, ctx["dos"].y = x, y
    assert ctx["mount"].request("UNO") is True


def _freeze(ctx, rid):
    from dualis.systems.observe import ObserveSystem
    observe = ObserveSystem(ctx["runtimes"].registry_for(rid), ctx["bus"])
    assert observe.request("UNO") is True
    observe.update(0.1)
    return observe


def test_region_manifiesto_coherente():
    assert REGION["id"] == "R3_TALLER"
    assert len(CHAIN) == 9
    assert len(set(CHAIN)) == 9
    assert REGION["rooms"][0] == "TAL_01"
    assert REGION["rooms"][-1] == "TAL_09"


def test_cadena_lineal_desde_biblioteca():
    rooms, _ = _load_all()
    assert "TAL_01" in rooms.definitions["BIB_08"].enlaces
    assert rooms.definitions["TAL_01"].enlaces == ("BIB_08", "TAL_02")
    for prev, rid, nxt in zip(CHAIN, CHAIN[1:-1], CHAIN[2:]):
        assert rooms.definitions[rid].enlaces == (prev, nxt), rid
    assert rooms.definitions["TAL_09"].enlaces == ("TAL_08",)


def test_patron_dificultad_y_proposito():
    for rid in CHAIN:
        blueprint = load_blueprint(BLUEPRINTS_DIR / (rid.lower() + ".json"), PATTERNS_DIR)
        assert blueprint.pattern == EXPECTED[rid], rid
        assert len(blueprint.ideas) == 1, rid
        assert blueprint.proposito, rid
        assert blueprint.dificultad in ("corta", "media"), rid


def test_sin_mecanicas_ni_patrones_nuevos():
    for rid in CHAIN:
        raw = json.loads((BLUEPRINTS_DIR / (rid.lower() + ".json")).read_text(encoding="utf-8"))
        assert raw["pattern"] in KNOWN_PATTERNS, rid
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


def test_primer_turno_resuelve():
    ctx = _play("TAL_01")
    _park(ctx, ctx["exit"])
    ctx["runtimes"].update(0.1, "TAL_01")
    assert ctx["runtime"].state == "LOCKED"
    _freeze(ctx, "TAL_01")
    _park(ctx, ctx["exit"])
    ctx["runtimes"].update(0.1, "TAL_01")
    assert ctx["runtime"].state == "COMPLETED"


def test_cota_exige_montaje():
    ctx = _play("TAL_03")
    _park(ctx, ctx["exit"])
    ctx["runtimes"].update(0.1, "TAL_03")
    assert ctx["runtime"].state == "LOCKED"
    _mount_near(ctx, 200.0, 150.0)
    ctx["mount"].update(0.1)
    ctx["runtimes"].update(0.1, "TAL_03")
    assert ctx["runtime"].state == "COMPLETED"


def test_viaje_transforma_y_resuelve():
    ctx = _play("TAL_04")
    assert ctx["runtimes"].try_transform("TAL_04", "DOS") is True
    _park(ctx, ctx["exit"])
    ctx["runtimes"].update(0.1, "TAL_04")
    assert ctx["runtime"].state == "COMPLETED"


def test_tablero_ordena():
    ctx = _play("TAL_05")
    assert ctx["runtimes"].try_transform("TAL_05", "DOS") is False
    assert "ROOM_DENIED" in ctx["bus"].log
    _freeze(ctx, "TAL_05")
    assert ctx["runtimes"].try_transform("TAL_05", "DOS") is True
    _park(ctx, ctx["exit"])
    ctx["runtimes"].update(0.1, "TAL_05")
    assert ctx["runtime"].state == "COMPLETED"


def test_orden_distinto_acepta_montar_primero():
    ctx = _play("TAL_07")
    _mount_near(ctx, 300.0, 240.0)
    _freeze(ctx, "TAL_07")
    assert ctx["runtimes"].try_transform("TAL_07", "DOS") is True
    _park(ctx, ctx["exit"])
    ctx["dos"].x, ctx["dos"].y = 320.0, 250.0
    ctx["mount"].update(0.1)
    ctx["runtimes"].update(0.1, "TAL_07")
    assert ctx["runtime"].state == "COMPLETED"


def test_examen_taller_evalua_todo():
    ctx = _play("TAL_09")
    _park(ctx, ctx["exit"])
    ctx["runtimes"].update(0.1, "TAL_09")
    assert ctx["runtime"].state == "LOCKED"
    assert "ROOM_COMPLETED" not in ctx["bus"].log
    _freeze(ctx, "TAL_09")
    assert ctx["runtimes"].try_transform("TAL_09", "DOS") is True
    ctx["runtimes"].update(0.1, "TAL_09")
    assert ctx["runtime"].state != "COMPLETED"
    _mount_near(ctx, 130.0, 300.0)
    _park(ctx, ctx["exit"])
    ctx["dos"].x, ctx["dos"].y = 115.0, 140.0
    ctx["mount"].update(0.1)
    ctx["runtimes"].update(0.1, "TAL_09")
    assert ctx["runtime"].state == "COMPLETED"
    assert "ROOM_COMPLETED" in ctx["bus"].log


def test_sin_resolucion_accidental():
    for rid in CHAIN:
        ctx = _play(rid)
        _park(ctx, ctx["exit"])
        ctx["runtimes"].update(0.1, rid)
        assert ctx["runtime"].state != "COMPLETED", rid
        assert "ROOM_COMPLETED" not in ctx["bus"].log, rid


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)
