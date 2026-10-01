"""Tests F26 — R4 Jardín Invertido (cierre): R4_05..R4_08.

Objetivo: TENSION como lenguaje jugable real dentro de la campaña
principal (R4_05 lo exige por puerta lógica + geometría ancha).
Solo patrones existentes. Sin sistemas, runtimes, render, físicas,
world_z, gravedad, teleports ni hubs nuevos. No toca R1/R2/R3,
exámenes, F22/F23/F24 ni tests existentes. Sin R4_EXAM todavía.
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
from dualis.systems.link import LinkSystem
from dualis.systems.observe import ObserveSystem
from dualis.systems.room_runtime import RoomRuntimeManager
from dualis.systems.transform import TransformSystem
from dualis.world.blueprint import load_blueprint
from dualis.world.builder import RoomBuilder
from dualis.world.colliders import collides, solids_for
from dualis.world.entity import Entity, EntityManager
from dualis.world.link_gate import exit_allowed, link_allows
from dualis.world.room import RoomManager
from dualis.world.transit import decide_transit, entry_for, next_room

ROOT = Path(__file__).resolve().parents[1]
ROOMS_DIR = ROOT / "data" / "rooms"
R4_DIR = ROOT / "data" / "r4_rooms"
PATTERNS_DIR = ROOT / "data" / "patterns"

IDS = ["R4_05", "R4_06", "R4_07", "R4_08"]
EXPECTED = {
    "R4_05": ("PATTERN_OBSERVE_TO_CROSS", "ObserveToCrossRuntime", "media"),
    "R4_06": ("PATTERN_TIMED_WINDOW", "ObserveToCrossRuntime", "corta"),
    "R4_07": ("PATTERN_TIMED_WINDOW", "ObserveToCrossRuntime", "media"),
    "R4_08": ("PATTERN_SHARED_PASSAGE", "SharedPassageRuntime", "corta"),
}


def _pattern(pid):
    for path in PATTERNS_DIR.glob("*.json"):
        raw = json.loads(path.read_text(encoding="utf-8"))
        if raw["id"] == pid:
            return raw
    raise KeyError(pid)


def _load(rid):
    return load_blueprint(R4_DIR / (rid.lower() + ".json"), PATTERNS_DIR)


def _play(rid):
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
    runtimes = RoomRuntimeManager(bus, transform, None, uno, dos)
    runtimes.add_room(blueprint, built.actors)
    rooms.enter(rid)
    observe = ObserveSystem(runtimes.registry_for(rid), bus)
    return {"bus": bus, "rooms": rooms, "uno": uno, "dos": dos,
            "link": link, "observe": observe, "runtimes": runtimes,
            "runtime": runtimes.runtime_for(rid),
            "exit": blueprint.exit_rect, "blueprint": blueprint}


def _center(exit_rect):
    ex, ey, ew, eh = exit_rect
    return (ex + ew / 2.0, ey + eh / 2.0)


def _links():
    links = {}
    for rid in ("R4_04",) + tuple(IDS):
        links[rid] = _load(rid).enlaces
    return links


def test_enlaces_cierre_r4_sin_exam():
    got = {rid: _load(rid).enlaces for rid in IDS}
    assert got["R4_05"] == ("R4_04", "R4_06")
    assert got["R4_06"] == ("R4_05", "R4_07")
    assert got["R4_07"] == ("R4_06", "R4_08")
    assert got["R4_08"] == ("R4_07",)  # fondo de saco hasta R4_EXAM
    assert _load("R4_04").enlaces == ("R4_03",)  # intacta: R4_04→R4_05 pendiente
    for rid, enlaces in got.items():
        for target in enlaces:
            assert not target.startswith("R4_EXAM"), (rid, target)
            assert not target.startswith("R5"), (rid, target)


def test_patrones_ideas_y_dificultad():
    for rid in IDS:
        blueprint = _load(rid)
        pattern, runtime, difficulty = EXPECTED[rid]
        assert blueprint.pattern == pattern, rid
        assert len(blueprint.ideas) == 1, rid
        assert blueprint.dificultad == difficulty, rid
        ctx = _play(rid)
        assert type(ctx["runtime"]).__name__ == runtime, rid


def test_r4_05_tension_lenguaje_real_en_campana():
    ctx = _play("R4_05")
    assert ctx["observe"].request("UNO") is True
    ctx["observe"].update(0.1)
    ctx["uno"].x, ctx["uno"].y = 170.0, 240.0
    ctx["dos"].x, ctx["dos"].y = 430.0, 240.0  # d=260: TENSION, ambos dentro
    assert ctx["link"].update(0.016) == LinkSystem.TENSION
    ctx["runtimes"].update(0.1, "R4_05")
    assert ctx["runtime"].state == "COMPLETED"
    assert link_allows(ctx["link"], "R4_05") is True
    assert exit_allowed(ctx["runtime"], ctx["link"], "R4_05") is True

    ctx = _play("R4_05")
    assert ctx["observe"].request("UNO") is True
    ctx["observe"].update(0.1)
    cx, cy = _center(ctx["exit"])
    ctx["uno"].x, ctx["uno"].y = cx, cy
    ctx["dos"].x, ctx["dos"].y = cx, cy  # juntos: completa pero no abre
    assert ctx["link"].update(0.016) == LinkSystem.CONNECTED
    ctx["runtimes"].update(0.1, "R4_05")
    assert ctx["runtime"].state == "COMPLETED"
    assert exit_allowed(ctx["runtime"], ctx["link"], "R4_05") is False


def test_r4_06_resoluble_ventana_avisada():
    ctx = _play("R4_06")
    assert ctx["observe"].request("UNO") is True
    ctx["observe"].update(0.1)
    cx, cy = _center(ctx["exit"])
    ctx["uno"].x, ctx["uno"].y = cx, cy
    ctx["dos"].x, ctx["dos"].y = cx, cy
    ctx["runtimes"].update(0.1, "R4_06")
    assert ctx["runtime"].state == "COMPLETED"


def test_r4_07_resoluble_eco_intacto():
    ctx = _play("R4_07")
    assert ctx["observe"].request("UNO") is True
    ctx["observe"].update(0.1)
    cx, cy = _center(ctx["exit"])
    ctx["uno"].x, ctx["uno"].y = cx, cy
    ctx["dos"].x, ctx["dos"].y = cx, cy
    ctx["runtimes"].update(0.1, "R4_07")
    assert ctx["runtime"].state == "COMPLETED"


def test_r4_08_denied_y_salida_detras():
    ctx = _play("R4_08")
    assert ctx["runtimes"].try_transform("R4_08", "DOS") is False
    assert "ROOM_DENIED" in ctx["bus"].log
    assert ctx["observe"].request("UNO") is True
    ctx["observe"].update(0.1)
    assert ctx["runtimes"].try_transform("R4_08", "DOS") is True
    cx, cy = _center(ctx["exit"])
    ctx["uno"].x, ctx["uno"].y = cx, cy
    ctx["dos"].x, ctx["dos"].y = cx, cy
    ctx["runtimes"].update(0.1, "R4_08")
    assert ctx["runtime"].state == "COMPLETED"


def test_salidas_libres_y_entradas_f24():
    prevs = {"R4_05": "R4_04", "R4_06": "R4_05",
             "R4_07": "R4_06", "R4_08": "R4_07"}
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


def test_compatibilidad_transito_cierre():
    links = _links()
    blueprints = {rid: _load(rid) for rid in ("R4_04",) + tuple(IDS)}
    assert next_room(links, "R4_05", "R4_04") == "R4_06"
    assert next_room(links, "R4_06", "R4_05") == "R4_07"
    assert next_room(links, "R4_07", "R4_06") == "R4_08"
    assert next_room(links, "R4_08", "R4_07") is None  # fondo de saco hasta EXAM
    assert next_room(links, "R4_06", "R4_07") == "R4_05"  # vuelta atrás
    ctx = _play("R4_05")
    assert decide_transit("R4_05", "R4_04", links, ctx["runtimes"],
                          None, ctx["uno"], ctx["dos"], blueprints) is None
    assert ctx["observe"].request("UNO") is True
    ctx["observe"].update(0.1)
    ctx["uno"].x, ctx["uno"].y = 170.0, 240.0
    ctx["dos"].x, ctx["dos"].y = 430.0, 240.0
    assert ctx["link"].update(0.016) == LinkSystem.TENSION
    ctx["runtimes"].update(0.1, "R4_05")
    assert ctx["runtime"].state == "COMPLETED"
    assert decide_transit("R4_05", "R4_04", links, ctx["runtimes"],
                          None, ctx["uno"], ctx["dos"], blueprints) == "R4_06"
    assert exit_allowed(ctx["runtime"], ctx["link"], "R4_05") is True


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)
