"""Tests F25 — R4 Jardín Invertido (intro): R4_01..R4_04 jugables.

Solo patrones existentes (OBSERVE_TO_CROSS, HEIGHT, TRANSFORM_TO_REACH).
Sin sistemas, runtimes, render, físicas, world_z, gravedad, teleports
ni hubs nuevos. No toca R1/R2/R3, exámenes, F22, F23, F24 ni tests
existentes. Sin R4_05..R4_EXAM todavía.
"""
import json
import math
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dualis.core.bus import EventBus
from dualis.systems.cooperation import MountAction
from dualis.systems.link import LinkSystem
from dualis.systems.observe import ObserveSystem
from dualis.systems.room_runtime import RoomRuntimeManager
from dualis.systems.transform import TransformSystem
from dualis.world.blueprint import load_blueprint
from dualis.world.builder import RoomBuilder
from dualis.world.colliders import collides, solids_for
from dualis.world.entity import Entity, EntityManager
from dualis.world.room import RoomManager
from dualis.world.transit import decide_transit, entry_for, next_room

ROOT = Path(__file__).resolve().parents[1]
ROOMS_DIR = ROOT / "data" / "rooms"
BLUEPRINTS_DIR = ROOT / "data" / "blueprints"
R4_DIR = ROOT / "data" / "r4_rooms"
PATTERNS_DIR = ROOT / "data" / "patterns"

IDS = ["R4_01", "R4_02", "R4_03", "R4_04"]
EXPECTED = {
    "R4_01": ("PATTERN_OBSERVE_TO_CROSS", "ObserveToCrossRuntime", "corta"),
    "R4_02": ("PATTERN_HEIGHT", "HeightRuntime", "corta"),
    "R4_03": ("PATTERN_OBSERVE_TO_CROSS", "ObserveToCrossRuntime", "media"),
    "R4_04": ("PATTERN_TRANSFORM_TO_REACH", "TransformToReachRuntime", "corta"),
}


def _pattern(pid):
    for path in PATTERNS_DIR.glob("*.json"):
        raw = json.loads(path.read_text(encoding="utf-8"))
        if raw["id"] == pid:
            return raw
    raise KeyError(pid)


def _load(rid):
    return load_blueprint(R4_DIR / (rid.lower() + ".json"), PATTERNS_DIR)


def _play(rid, with_mount=False):
    bus = EventBus()
    rooms = RoomManager(bus)
    rooms.load_directory(ROOMS_DIR)
    builder = RoomBuilder(rooms)
    blueprint = _load(rid)
    built = builder.build(blueprint, _pattern(blueprint.pattern))
    entities = EntityManager()
    uno = Entity("UNO", x=120.0, y=280.0)
    dos = Entity("DOS", x=220.0, y=280.0)
    entities.register(uno)
    entities.register(dos)
    for actor in built.actors:
        entities.register(actor)
    link = LinkSystem(entities, bus)
    transform = TransformSystem(bus)
    mount = MountAction(uno, dos, bus) if with_mount else None
    runtimes = RoomRuntimeManager(bus, transform, mount, uno, dos)
    runtimes.add_room(blueprint, built.actors)
    rooms.enter(rid)
    observe = ObserveSystem(runtimes.registry_for(rid), bus)
    return {"bus": bus, "rooms": rooms, "uno": uno, "dos": dos,
            "link": link, "observe": observe, "mount": mount,
            "runtimes": runtimes, "runtime": runtimes.runtime_for(rid),
            "exit": blueprint.exit_rect, "blueprint": blueprint}


def _center(exit_rect):
    ex, ey, ew, eh = exit_rect
    return (ex + ew / 2.0, ey + eh / 2.0)


def test_enlaces_cadena_r4_sin_r5():
    got = {rid: _load(rid).enlaces for rid in IDS}
    assert got["R4_01"] == ("TAL_09", "R4_02")
    assert got["R4_02"] == ("R4_01", "R4_03")
    assert got["R4_03"] == ("R4_02", "R4_04")
    assert got["R4_04"] == ("R4_03",)  # fondo de saco temporal
    for rid, enlaces in got.items():
        for target in enlaces:
            assert not target.startswith("R5"), (rid, target)
    tal09 = load_blueprint(BLUEPRINTS_DIR / "tal_09.json", PATTERNS_DIR)
    assert tal09.enlaces == ("TAL_08",)  # intacta: la arista TAL_09→R4_01
    # queda pendiente hasta revisión humana de los tests que la congelan.


def test_patrones_ideas_y_dificultad():
    for rid in IDS:
        blueprint = _load(rid)
        pattern, runtime, difficulty = EXPECTED[rid]
        assert blueprint.pattern == pattern, rid
        assert len(blueprint.ideas) == 1, rid
        assert blueprint.dificultad == difficulty, rid
        ctx = _play(rid, with_mount=(rid == "R4_02"))
        assert type(ctx["runtime"]).__name__ == runtime, rid


def test_r4_01_resoluble_alejarse_para_llegar():
    ctx = _play("R4_01")
    assert ctx["observe"].request("UNO") is True
    ctx["observe"].update(0.1)
    cx, cy = _center(ctx["exit"])
    ctx["uno"].x, ctx["uno"].y = cx, cy
    ctx["dos"].x, ctx["dos"].y = cx, cy
    ctx["runtimes"].update(0.1, "R4_01")
    assert ctx["runtime"].state == "COMPLETED"


def test_r4_02_resoluble_montado():
    ctx = _play("R4_02", with_mount=True)
    cx, cy = _center(ctx["exit"])
    ctx["uno"].x, ctx["uno"].y = cx, cy
    ctx["dos"].x, ctx["dos"].y = cx, cy
    ctx["runtimes"].update(0.1, "R4_02")
    assert ctx["runtime"].state != "COMPLETED"  # sin montar no cuenta
    assert ctx["mount"].request("UNO") is True
    assert ctx["mount"].mounted is True
    ctx["uno"].x, ctx["uno"].y = cx, cy  # el pin mueve a UNO: reaparcar tras montar
    ctx["dos"].x, ctx["dos"].y = cx, cy
    ctx["runtimes"].update(0.1, "R4_02")
    assert ctx["runtime"].state == "COMPLETED"


def test_r4_03_resoluble_sombra_revela():
    ctx = _play("R4_03")
    assert ctx["observe"].request("UNO") is True
    ctx["observe"].update(0.1)
    cx, cy = _center(ctx["exit"])
    ctx["uno"].x, ctx["uno"].y = cx, cy
    ctx["dos"].x, ctx["dos"].y = cx, cy
    ctx["runtimes"].update(0.1, "R4_03")
    assert ctx["runtime"].state == "COMPLETED"


def test_r4_04_resoluble_transformar_fuente():
    ctx = _play("R4_04")
    assert ctx["runtimes"].try_transform("R4_04", "DOS") is True
    cx, cy = _center(ctx["exit"])
    ctx["uno"].x, ctx["uno"].y = cx, cy
    ctx["dos"].x, ctx["dos"].y = cx, cy
    ctx["runtimes"].update(0.1, "R4_04")
    assert ctx["runtime"].state == "COMPLETED"


def test_salidas_libres_y_entradas_f24():
    prevs = {"R4_01": "TAL_09", "R4_02": "R4_01",
             "R4_03": "R4_02", "R4_04": "R4_03"}
    for rid in IDS:
        ctx = _play(rid)
        solids = solids_for(rid, tuple(ctx["exit"]))
        ex, ey, ew, eh = (float(v) for v in ctx["exit"])
        for px, py in ((ex + ew / 2.0, ey + eh / 2.0),
                       (ex + ew / 2.0, ey + 15.0),
                       (ex + ew / 2.0, ey + eh - 15.0),
                       (ex + 15.0, ey + eh / 2.0),
                       (ex + ew - 15.0, ey + eh / 2.0)):
            assert not collides(px, py, 14, solids), (rid, px, py)
        for from_rid in (None, prevs[rid]):
            (ux, uy), (dx, dy) = entry_for(tuple(ctx["exit"]), solids, from_rid)
            for px, py in ((ux, uy), (dx, dy)):
                assert not (ex <= px <= ex + ew and ey <= py <= ey + eh), (rid, from_rid)
                assert not collides(px, py, 14, solids), (rid, from_rid)
            assert math.hypot(ux - dx, uy - dy) < 210.0, rid
            assert entry_for(tuple(ctx["exit"]), solids, from_rid) == ((ux, uy), (dx, dy))


def test_compatibilidad_transito_r4():
    tal09 = load_blueprint(BLUEPRINTS_DIR / "tal_09.json", PATTERNS_DIR)
    links = {"TAL_09": tal09.enlaces}
    blueprints = {"TAL_09": tal09}
    for rid in IDS:
        blueprint = _load(rid)
        links[rid] = blueprint.enlaces
        blueprints[rid] = blueprint
    assert next_room(links, "R4_01", "TAL_09") == "R4_02"
    assert next_room(links, "R4_02", "R4_01") == "R4_03"
    assert next_room(links, "R4_03", "R4_02") == "R4_04"
    assert next_room(links, "R4_04", "R4_03") is None  # fondo de saco temporal
    assert next_room(links, "R4_02", "R4_03") == "R4_01"  # vuelta atrás
    ctx = _play("R4_01")
    assert decide_transit("R4_01", "TAL_09", links, ctx["runtimes"],
                          None, ctx["uno"], ctx["dos"], blueprints) is None
    assert ctx["observe"].request("UNO") is True
    ctx["observe"].update(0.1)
    cx, cy = _center(ctx["exit"])
    ctx["uno"].x, ctx["uno"].y = cx, cy
    ctx["dos"].x, ctx["dos"].y = cx, cy
    ctx["runtimes"].update(0.1, "R4_01")
    assert ctx["runtime"].state == "COMPLETED"
    assert decide_transit("R4_01", "TAL_09", links, ctx["runtimes"],
                          None, ctx["uno"], ctx["dos"], blueprints) == "R4_02"


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)
