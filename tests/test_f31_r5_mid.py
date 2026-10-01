"""Tests F31 — R5 Torre de los Nombres (segunda mitad): R5_05..R5_08.

Solo patrones existentes (TRANSFORM_TO_REACH, TIMED_WINDOW,
SHARED_PASSAGE, HEIGHT). Sin sistemas, runtimes, render, fisicas,
world_z ni verbos nuevos. Sin gate LINK nuevo (regla F31: las salidas
pequenas exigen CONNECTED por geometria; ningun REQUIREMENTS nuevo).
No toca ROOM_SLICE, R1/R2/R3, R4 completa, R4_EXAM, R5_01..R5_04,
F22/F23/F24/F28/F30 ni tests existentes. Sin R5_EXAM ni R6 todavia.

Filosofia F25/F26/F30: datos aislados en data/r5_rooms/, r5_04 intacta
como fondo de saco historico en datos, cadena nueva solo con enlaces
hacia atras, fondo temporal en R5_08, integracion futura por overlay.
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
from dualis.world.link_gate import link_allows, required_state
from dualis.world.room import RoomManager
from dualis.world.transit import decide_transit, entry_for, next_room

ROOT = Path(__file__).resolve().parents[1]
ROOMS_DIR = ROOT / "data" / "rooms"
BLUEPRINTS_DIR = ROOT / "data" / "blueprints"
R4_DIR = ROOT / "data" / "r4_rooms"
R5_DIR = ROOT / "data" / "r5_rooms"
PATTERNS_DIR = ROOT / "data" / "patterns"

IDS = ["R5_05", "R5_06", "R5_07", "R5_08"]
EXPECTED = {
    "R5_05": ("PATTERN_TRANSFORM_TO_REACH", "TransformToReachRuntime", "media"),
    "R5_06": ("PATTERN_TIMED_WINDOW", "ObserveToCrossRuntime", "corta"),
    "R5_07": ("PATTERN_SHARED_PASSAGE", "SharedPassageRuntime", "media"),
    "R5_08": ("PATTERN_HEIGHT", "HeightRuntime", "corta"),
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


def test_enlaces_cadena_r5_sin_exam():
    got = {rid: _load(rid).enlaces for rid in IDS}
    assert got["R5_05"] == ("R5_04", "R5_06")
    assert got["R5_06"] == ("R5_05", "R5_07")
    assert got["R5_07"] == ("R5_06", "R5_08")
    assert got["R5_08"] == ("R5_07",)  # fondo de saco temporal hasta examen
    assert _load("R5_04").enlaces == ("R5_03",)  # intacta: F30 la congela
    for rid, enlaces in got.items():
        for target in enlaces:
            assert not target.startswith("R5_EXAM"), (rid, target)
            assert not target.startswith("R6"), (rid, target)
    exam = load_blueprint(R4_DIR / "r4_exam.json", PATTERNS_DIR)
    assert exam.enlaces == ("R4_08",)  # intacta
    assert set(EXTRA_LINKS) == {"TAL_09", "R4_04", "R4_08"}  # F28 sin regresion


def test_patrones_ideas_y_dificultad():
    for rid in IDS:
        blueprint = _load(rid)
        pattern, runtime, difficulty = EXPECTED[rid]
        assert blueprint.pattern == pattern, rid
        assert len(blueprint.ideas) == 1, rid
        assert blueprint.dificultad == difficulty, rid
        ctx = _play(rid, with_mount=(rid == "R5_08"))
        assert type(ctx["runtime"]).__name__ == runtime, rid


def test_sin_gate_link_nuevo():
    for rid in IDS:
        assert required_state(rid) is None, rid
        ctx = _play(rid)
        assert link_allows(ctx["link"], rid) is False, rid


def test_r5_05_resoluble_mira_sostiene():
    ctx = _play("R5_05")
    assert ctx["runtimes"].try_transform("R5_05", "DOS") is True
    cx, cy = _center(ctx["exit"])
    ctx["uno"].x, ctx["uno"].y = cx, cy
    ctx["dos"].x, ctx["dos"].y = cx, cy
    ctx["runtimes"].update(0.1, "R5_05")
    assert ctx["runtime"].state == "COMPLETED"


def test_r5_06_resoluble_relevo():
    ctx = _play("R5_06")
    assert ctx["observe"].request("UNO") is True
    ctx["observe"].update(0.1)
    cx, cy = _center(ctx["exit"])
    ctx["uno"].x, ctx["uno"].y = cx, cy
    ctx["dos"].x, ctx["dos"].y = cx, cy
    ctx["runtimes"].update(0.1, "R5_06")
    assert ctx["runtime"].state == "COMPLETED"


def test_r5_07_denied_ninguno_solo():
    ctx = _play("R5_07")
    assert ctx["runtimes"].try_transform("R5_07", "DOS") is False
    assert "ROOM_DENIED" in ctx["bus"].log
    assert ctx["observe"].request("UNO") is True
    ctx["observe"].update(0.1)
    assert ctx["runtimes"].try_transform("R5_07", "DOS") is True
    cx, cy = _center(ctx["exit"])
    ctx["uno"].x, ctx["uno"].y = cx, cy
    ctx["dos"].x, ctx["dos"].y = cx, cy
    ctx["runtimes"].update(0.1, "R5_07")
    assert ctx["runtime"].state == "COMPLETED"


def test_r5_08_resoluble_orden_reconocimiento():
    ctx = _play("R5_08", with_mount=True)
    cx, cy = _center(ctx["exit"])
    ctx["uno"].x, ctx["uno"].y = cx, cy
    ctx["dos"].x, ctx["dos"].y = cx, cy
    ctx["runtimes"].update(0.1, "R5_08")
    assert ctx["runtime"].state != "COMPLETED"  # sin montar no cuenta
    assert ctx["observe"].request("UNO") is True
    ctx["observe"].update(0.1)
    assert ctx["mount"].request("UNO") is True
    assert ctx["mount"].mounted is True
    ctx["uno"].x, ctx["uno"].y = cx, cy  # el pin mueve a UNO: reaparcar
    ctx["dos"].x, ctx["dos"].y = cx, cy
    ctx["runtimes"].update(0.1, "R5_08")
    assert ctx["runtime"].state == "COMPLETED"


def test_salidas_libres_y_entradas_f24():
    prevs = {"R5_05": "R5_04", "R5_06": "R5_05",
             "R5_07": "R5_06", "R5_08": "R5_07"}
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


def test_compatibilidad_transito_r5_mid():
    links = {rid: _load(rid).enlaces for rid in ("R5_04",) + tuple(IDS)}
    blueprints = {rid: _load(rid) for rid in ("R5_04",) + tuple(IDS)}
    assert next_room(links, "R5_05", "R5_04") == "R5_06"
    assert next_room(links, "R5_06", "R5_05") == "R5_07"
    assert next_room(links, "R5_07", "R5_06") == "R5_08"
    assert next_room(links, "R5_08", "R5_07") is None  # fondo temporal
    assert next_room(links, "R5_06", "R5_07") == "R5_05"  # vuelta atras
    assert next_room(links, "R5_05", "R5_06") == "R5_04"  # vuelta al tramo F30
    ctx = _play("R5_05")
    assert decide_transit("R5_05", "R5_04", links, ctx["runtimes"],
                          None, ctx["uno"], ctx["dos"], blueprints) is None
    assert ctx["runtimes"].try_transform("R5_05", "DOS") is True
    cx, cy = _center(ctx["exit"])
    ctx["uno"].x, ctx["uno"].y = cx, cy
    ctx["dos"].x, ctx["dos"].y = cx, cy
    ctx["runtimes"].update(0.1, "R5_05")
    assert ctx["runtime"].state == "COMPLETED"
    assert decide_transit("R5_05", "R5_04", links, ctx["runtimes"],
                          None, ctx["uno"], ctx["dos"], blueprints) == "R5_06"
    # Sin puerta declarada el vinculo nunca bloquea (ni siquiera LIMIT).
    ctx["link"].state = LinkSystem.LIMIT
    assert decide_transit("R5_05", "R5_04", links, ctx["runtimes"],
                          None, ctx["uno"], ctx["dos"], blueprints,
                          link=ctx["link"]) == "R5_06"


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)
