"""Tests F30 — R5 Torre de los Nombres (intro): R5_01..R5_04 jugables.

Solo patrones existentes (OBSERVE_TO_CROSS, HEIGHT, TRANSFORM_TO_REACH).
Sin sistemas, runtimes, render, fisicas, world_z ni verbos nuevos.
No toca ROOM_SLICE, R1/R2/R3, R4 completa, R4_EXAM, F22/F23/F24/F28
ni tests existentes. Sin R5_05..R5_EXAM todavia.

Filosofia F25/F26: datos aislados en data/r5_rooms/, fondo de saco
temporal en R5_04, bisagra R4_EXAM->R5_01 pendiente de capa de campaña
futura (F28 congela EXTRA_LINKS con 3 aristas: no se toca).
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
from dualis.world.campaign import EXTRA_LINKS
from dualis.world.colliders import collides, solids_for
from dualis.world.entity import Entity, EntityManager
from dualis.world.link_gate import exit_allowed, link_allows
from dualis.world.room import RoomManager
from dualis.world.transit import decide_transit, entry_for, next_room

ROOT = Path(__file__).resolve().parents[1]
ROOMS_DIR = ROOT / "data" / "rooms"
BLUEPRINTS_DIR = ROOT / "data" / "blueprints"
R4_DIR = ROOT / "data" / "r4_rooms"
R5_DIR = ROOT / "data" / "r5_rooms"
PATTERNS_DIR = ROOT / "data" / "patterns"

IDS = ["R5_01", "R5_02", "R5_03", "R5_04"]
EXPECTED = {
    "R5_01": ("PATTERN_OBSERVE_TO_CROSS", "ObserveToCrossRuntime", "corta"),
    "R5_02": ("PATTERN_HEIGHT", "HeightRuntime", "corta"),
    "R5_03": ("PATTERN_TRANSFORM_TO_REACH", "TransformToReachRuntime", "corta"),
    "R5_04": ("PATTERN_OBSERVE_TO_CROSS", "ObserveToCrossRuntime", "media"),
}


def _pattern(pid):
    for path in PATTERNS_DIR.glob("*.json"):
        raw = json.loads(path.read_text(encoding="utf-8"))
        if raw["id"] == pid:
            return raw
    raise KeyError(pid)


def _load(rid):
    return load_blueprint(R5_DIR / (rid.lower() + ".json"), PATTERNS_DIR)


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


def test_enlaces_cadena_r5_sin_resto():
    got = {rid: _load(rid).enlaces for rid in IDS}
    assert got["R5_01"] == ("R4_EXAM", "R5_02")
    assert got["R5_02"] == ("R5_01", "R5_03")
    assert got["R5_03"] == ("R5_02", "R5_04")
    assert got["R5_04"] == ("R5_03",)  # fondo de saco temporal hasta F31
    for rid, enlaces in got.items():
        for target in enlaces:
            assert not target.startswith("R5_05"), (rid, target)
            assert not target.startswith("R5_EXAM"), (rid, target)
            assert not target.startswith("R6"), (rid, target)
    exam = load_blueprint(R4_DIR / "r4_exam.json", PATTERNS_DIR)
    assert exam.enlaces == ("R4_08",)  # intacta: bisagra R4_EXAM->R5_01 pendiente
    tal09 = load_blueprint(BLUEPRINTS_DIR / "tal_09.json", PATTERNS_DIR)
    assert tal09.enlaces == ("TAL_08",)  # intacta (F28 la cierra en campaña)
    assert set(EXTRA_LINKS) == {"TAL_09", "R4_04", "R4_08"}  # F28 sin regresion


def test_patrones_ideas_y_dificultad():
    for rid in IDS:
        blueprint = _load(rid)
        pattern, runtime, difficulty = EXPECTED[rid]
        assert blueprint.pattern == pattern, rid
        assert len(blueprint.ideas) == 1, rid
        assert blueprint.dificultad == difficulty, rid
        ctx = _play(rid, with_mount=(rid == "R5_02"))
        assert type(ctx["runtime"]).__name__ == runtime, rid


def test_r5_01_resoluble_ser_reconocido():
    ctx = _play("R5_01")
    assert ctx["observe"].request("UNO") is True
    ctx["observe"].update(0.1)
    cx, cy = _center(ctx["exit"])
    ctx["uno"].x, ctx["uno"].y = cx, cy
    ctx["dos"].x, ctx["dos"].y = cx, cy
    ctx["runtimes"].update(0.1, "R5_01")
    assert ctx["runtime"].state == "COMPLETED"


def test_r5_02_resoluble_sostenido_abre():
    ctx = _play("R5_02", with_mount=True)
    cx, cy = _center(ctx["exit"])
    ctx["uno"].x, ctx["uno"].y = cx, cy
    ctx["dos"].x, ctx["dos"].y = cx, cy
    ctx["runtimes"].update(0.1, "R5_02")
    assert ctx["runtime"].state != "COMPLETED"  # sin montar no cuenta
    assert ctx["mount"].request("UNO") is True
    assert ctx["mount"].mounted is True
    ctx["uno"].x, ctx["uno"].y = cx, cy  # el pin mueve a UNO: reaparcar
    ctx["dos"].x, ctx["dos"].y = cx, cy
    ctx["runtimes"].update(0.1, "R5_02")
    assert ctx["runtime"].state == "COMPLETED"


def test_r5_03_resoluble_nombre_verdadero():
    ctx = _play("R5_03")
    assert ctx["runtimes"].try_transform("R5_03", "DOS") is True
    cx, cy = _center(ctx["exit"])
    ctx["uno"].x, ctx["uno"].y = cx, cy
    ctx["dos"].x, ctx["dos"].y = cx, cy
    ctx["runtimes"].update(0.1, "R5_03")
    assert ctx["runtime"].state == "COMPLETED"


def test_r5_04_tension_juntos_a_distancia():
    ctx = _play("R5_04")
    assert ctx["observe"].request("UNO") is True
    ctx["observe"].update(0.1)
    ctx["uno"].x, ctx["uno"].y = 170.0, 240.0
    ctx["dos"].x, ctx["dos"].y = 430.0, 240.0  # d=260: TENSION, ambos dentro
    assert ctx["link"].update(0.016) == LinkSystem.TENSION
    ctx["runtimes"].update(0.1, "R5_04")
    assert ctx["runtime"].state == "COMPLETED"
    assert link_allows(ctx["link"], "R5_04") is True
    assert exit_allowed(ctx["runtime"], ctx["link"], "R5_04") is True

    ctx = _play("R5_04")
    assert ctx["observe"].request("UNO") is True
    ctx["observe"].update(0.1)
    cx, cy = _center(ctx["exit"])
    ctx["uno"].x, ctx["uno"].y = cx, cy
    ctx["dos"].x, ctx["dos"].y = cx, cy  # juntos: completa pero no abre
    assert ctx["link"].update(0.016) == LinkSystem.CONNECTED
    ctx["runtimes"].update(0.1, "R5_04")
    assert ctx["runtime"].state == "COMPLETED"
    assert exit_allowed(ctx["runtime"], ctx["link"], "R5_04") is False


def test_salidas_libres_y_entradas_f24():
    prevs = {"R5_01": "R4_EXAM", "R5_02": "R5_01",
             "R5_03": "R5_02", "R5_04": "R5_03"}
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


def test_compatibilidad_transito_r5():
    links = {}
    for rid in ("R4_EXAM",) + tuple(IDS):
        directory = R4_DIR if rid == "R4_EXAM" else R5_DIR
        links[rid] = load_blueprint(directory / (rid.lower() + ".json"),
                                    PATTERNS_DIR).enlaces
    blueprints = {rid: load_blueprint((R4_DIR if rid == "R4_EXAM" else R5_DIR) /
                                      (rid.lower() + ".json"), PATTERNS_DIR)
                  for rid in ("R4_EXAM",) + tuple(IDS)}
    assert next_room(links, "R5_01", "R4_EXAM") == "R5_02"
    assert next_room(links, "R5_02", "R5_01") == "R5_03"
    assert next_room(links, "R5_03", "R5_02") == "R5_04"
    assert next_room(links, "R5_04", "R5_03") is None  # fondo temporal
    assert next_room(links, "R5_02", "R5_03") == "R5_01"  # vuelta atras
    assert next_room(links, "R5_01", "R5_02") == "R4_EXAM"  # vuelta R5->R4
    ctx = _play("R5_01")
    assert decide_transit("R5_01", "R4_EXAM", links, ctx["runtimes"],
                          None, ctx["uno"], ctx["dos"], blueprints) is None
    assert ctx["observe"].request("UNO") is True
    ctx["observe"].update(0.1)
    cx, cy = _center(ctx["exit"])
    ctx["uno"].x, ctx["uno"].y = cx, cy
    ctx["dos"].x, ctx["dos"].y = cx, cy
    ctx["runtimes"].update(0.1, "R5_01")
    assert ctx["runtime"].state == "COMPLETED"
    assert decide_transit("R5_01", "R4_EXAM", links, ctx["runtimes"],
                          None, ctx["uno"], ctx["dos"], blueprints) == "R5_02"
    # R5_04: fondo de saco, pero el gate TENSION gobierna como en R4_05.
    gate = _play("R5_04")
    assert gate["observe"].request("UNO") is True
    gate["observe"].update(0.1)
    gate["uno"].x, gate["uno"].y = 170.0, 240.0
    gate["dos"].x, gate["dos"].y = 430.0, 240.0
    assert gate["link"].update(0.016) == LinkSystem.TENSION
    gate["runtimes"].update(0.1, "R5_04")
    assert gate["runtime"].state == "COMPLETED"
    assert exit_allowed(gate["runtime"], gate["link"], "R5_04") is True
    assert decide_transit("R5_04", "R5_03", links, gate["runtimes"],
                          None, gate["uno"], gate["dos"], blueprints) is None
    gate["link"].state = LinkSystem.CONNECTED  # junto: completa pero no abre
    assert exit_allowed(gate["runtime"], gate["link"], "R5_04") is False


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)
