"""Tests F32 — R5_EXAM: cierre de la Torre de los Nombres.

Combina los cuatro verbos sin ideas, sistemas, runtimes, render,
físicas, world_z, gravedad, teleports ni hubs nuevos:

- OBSERVE: congelar la sombra (moving) antes de nada.
- TRANSFORM: la fuente (bridge) solo cede tras observar (si no, DENIED).
- MOUNT: ExamRuntime exige montar para completar.
- LINK TENSION: la salida ancha solo abre en TENSION (puerta lógica).

Mecánica existente: PATTERN_TRANSFORM_TO_REACH con observable +
transformable selecciona ExamRuntime; link_gate añade la puerta
TENSION. COMPLETED es pegajoso: se completa montado y junto, y se
abre separado en TENSION. No toca R1/R2/R3, exámenes, F22/F23/F24,
TAL_09, R4_01..R4_EXAM, R5_01..R5_08 ni tests existentes.
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
from dualis.world.link_gate import exit_allowed, link_allows
from dualis.world.room import RoomManager
from dualis.world.transit import decide_transit, entry_for, next_room

ROOT = Path(__file__).resolve().parents[1]
ROOMS_DIR = ROOT / "data" / "rooms"
R5_DIR = ROOT / "data" / "r5_rooms"
PATTERNS_DIR = ROOT / "data" / "patterns"

RID = "R5_EXAM"
WIDE_UNO = (170.0, 240.0)
WIDE_DOS = (430.0, 240.0)  # d=260: TENSION, ambos dentro de [140,200,360,80]


def _pattern(pid):
    for path in PATTERNS_DIR.glob("*.json"):
        raw = json.loads(path.read_text(encoding="utf-8"))
        if raw["id"] == pid:
            return raw
    raise KeyError(pid)


def _load(rid):
    return load_blueprint(R5_DIR / (rid.lower() + ".json"), PATTERNS_DIR)


def _play():
    bus = EventBus()
    rooms = RoomManager(bus)
    rooms.load_directory(ROOMS_DIR)
    builder = RoomBuilder(rooms)
    blueprint = _load(RID)
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
    mount = MountAction(uno, dos, bus)
    runtimes = RoomRuntimeManager(bus, transform, mount, uno, dos)
    runtimes.add_room(blueprint, built.actors)
    rooms.enter(RID)
    observe = ObserveSystem(runtimes.registry_for(RID), bus)
    return {"bus": bus, "rooms": rooms, "uno": uno, "dos": dos,
            "link": link, "observe": observe, "mount": mount,
            "runtimes": runtimes, "runtime": runtimes.runtime_for(RID),
            "exit": blueprint.exit_rect, "blueprint": blueprint}


def _center(exit_rect):
    ex, ey, ew, eh = exit_rect
    return (ex + ew / 2.0, ey + eh / 2.0)


def _observe(ctx):
    assert ctx["observe"].request("UNO") is True
    ctx["observe"].update(0.1)


def _park_center(ctx):
    cx, cy = _center(ctx["exit"])
    ctx["uno"].x, ctx["uno"].y = cx, cy
    ctx["dos"].x, ctx["dos"].y = cx, cy


def _complete_mounted(ctx):
    """Rutina completa: observar, transformar, juntar, montar, completar."""
    _observe(ctx)
    assert ctx["runtimes"].try_transform(RID, "DOS") is True
    _park_center(ctx)  # d=0: el dúo junto para poder montar
    assert ctx["mount"].request("UNO") is True
    assert ctx["mount"].mounted is True
    _park_center(ctx)  # el pin mueve a UNO: reaparcar tras montar
    ctx["runtimes"].update(0.1, RID)
    assert ctx["runtime"].state == "COMPLETED"


def test_metadatos_exam_una_idea_sin_r6():
    blueprint = _load(RID)
    assert blueprint.pattern == "PATTERN_TRANSFORM_TO_REACH"
    assert len(blueprint.ideas) == 1
    assert blueprint.ideas == ("examen-torre",)
    assert blueprint.dificultad == "media"
    assert blueprint.enlaces == ("R5_08",)
    for target in blueprint.enlaces:
        assert not target.startswith("R6"), target
    missing = RoomBuilder(RoomManager(EventBus())).coverage(
        blueprint, _pattern(blueprint.pattern))
    assert missing == []
    ctx = _play()
    assert type(ctx["runtime"]).__name__ == "ExamRuntime"
    assert tuple(ctx["exit"]) == (140, 200, 360, 80)
    assert _load("R5_08").enlaces == ("R5_07",)  # intacta: R5_08 sigue fondo temporal (R5_EXAM declara la vuelta)


def test_observe_antes_de_transform():
    ctx = _play()
    assert ctx["runtimes"].try_transform(RID, "DOS") is False
    assert "ROOM_DENIED" in ctx["bus"].log
    _observe(ctx)
    assert ctx["runtimes"].try_transform(RID, "DOS") is True


def test_mount_exigido_para_completar():
    ctx = _play()
    _observe(ctx)
    assert ctx["runtimes"].try_transform(RID, "DOS") is True
    _park_center(ctx)
    ctx["runtimes"].update(0.1, RID)
    assert ctx["runtime"].state != "COMPLETED"  # sin montar no cuenta
    assert ctx["mount"].request("UNO") is True
    _park_center(ctx)
    ctx["runtimes"].update(0.1, RID)
    assert ctx["runtime"].state == "COMPLETED"


def test_exam_completo_cuatro_verbos():
    ctx = _play()
    _complete_mounted(ctx)  # OBSERVE + TRANSFORM + MOUNT
    assert ctx["link"].update(0.016) == LinkSystem.CONNECTED
    assert exit_allowed(ctx["runtime"], ctx["link"], RID) is False
    ctx["uno"].x, ctx["uno"].y = WIDE_UNO
    ctx["dos"].x, ctx["dos"].y = WIDE_DOS
    assert ctx["link"].update(0.016) == LinkSystem.TENSION  # LINK
    ctx["runtimes"].update(0.1, RID)  # COMPLETED pegajoso: sigue valiendo
    assert ctx["runtime"].state == "COMPLETED"
    assert link_allows(ctx["link"], RID) is True
    assert exit_allowed(ctx["runtime"], ctx["link"], RID) is True


def test_connected_completa_pero_no_abre():
    ctx = _play()
    _complete_mounted(ctx)
    cx, cy = _center(ctx["exit"])
    ctx["uno"].x, ctx["uno"].y = cx, cy
    ctx["dos"].x, ctx["dos"].y = cx, cy
    assert ctx["link"].update(0.016) == LinkSystem.CONNECTED
    ctx["runtimes"].update(0.1, RID)
    assert ctx["runtime"].state == "COMPLETED"
    assert exit_allowed(ctx["runtime"], ctx["link"], RID) is False


def test_limit_nunca_abre():
    ctx = _play()
    _complete_mounted(ctx)
    ctx["uno"].x, ctx["uno"].y = 40.0, 40.0
    ctx["dos"].x, ctx["dos"].y = 600.0, 320.0  # d>500: LIMIT
    assert ctx["link"].update(0.016) == LinkSystem.LIMIT
    assert link_allows(ctx["link"], RID) is False
    assert exit_allowed(ctx["runtime"], ctx["link"], RID) is False


def test_salidas_libres_y_entradas_f24():
    ctx = _play()
    solids = solids_for(RID, tuple(ctx["exit"]))
    ex, ey, ew, eh = (float(v) for v in ctx["exit"])
    for px, py in ((ex + ew / 2.0, ey + eh / 2.0),
                   (ex + ew / 2.0, ey + 15.0),
                   (ex + ew / 2.0, ey + eh - 15.0),
                   (ex + 15.0, ey + eh / 2.0),
                   (ex + ew - 15.0, ey + eh / 2.0)):
        assert not collides(px, py, 14, solids), (px, py)
    for from_rid in (None, "R5_08"):
        (ux, uy), (dx, dy) = entry_for(tuple(ctx["exit"]), solids, from_rid)
        for px, py in ((ux, uy), (dx, dy)):
            assert not (ex <= px <= ex + ew and ey <= py <= ey + eh), from_rid
            assert not collides(px, py, 14, solids), from_rid
        assert math.hypot(ux - dx, uy - dy) < 210.0
        assert entry_for(tuple(ctx["exit"]), solids, from_rid) == ((ux, uy), (dx, dy))


def test_compatibilidad_transito_exam_fondo_de_saco():
    links = {"R5_08": _load("R5_08").enlaces, RID: _load(RID).enlaces}
    blueprints = {"R5_08": _load("R5_08"), RID: _load(RID)}
    assert next_room(links, "R5_08", "R5_07") is None  # R5_08 intacta: fondo temporal
    assert next_room(links, RID, "R5_08") is None  # EXAM fondo de saco: quedarse
    assert next_room(links, RID, None) == "R5_08"  # vuelta atrás declarada
    ctx = _play()
    assert decide_transit(RID, "R5_08", links, ctx["runtimes"],
                          None, ctx["uno"], ctx["dos"], blueprints) is None
    _complete_mounted(ctx)
    ctx["uno"].x, ctx["uno"].y = WIDE_UNO
    ctx["dos"].x, ctx["dos"].y = WIDE_DOS
    assert ctx["link"].update(0.016) == LinkSystem.TENSION
    ctx["runtimes"].update(0.1, RID)
    assert exit_allowed(ctx["runtime"], ctx["link"], RID) is True
    assert decide_transit(RID, "R5_08", links, ctx["runtimes"],
                          None, ctx["uno"], ctx["dos"], blueprints) is None


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)






