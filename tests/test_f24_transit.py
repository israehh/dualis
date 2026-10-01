"""Tests F24 — Tránsitos y Persistencia Suave: R1→R2→R3 navegable.

Solo añade tests nuevos. No toca lenguaje, exámenes, F22, F23, render
ni colliders. Sin savegames complejos, teleports, hubs, inventario,
acciones, IA ni world_z.
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
from dualis.persistence.soft import load_soft, save_soft
from dualis.systems.link import LinkSystem
from dualis.systems.observable import ObservableRegistry
from dualis.systems.observe import ObserveSystem
from dualis.systems.room_runtime import RoomRuntimeManager
from dualis.systems.slice_puzzle import EXIT_RECT as SLICE_EXIT
from dualis.systems.slice_puzzle import SlicePuzzle
from dualis.systems.transform import TransformSystem
from dualis.systems.transformable import TransformableRegistry
from dualis.world.blueprint import load_blueprint
from dualis.world.builder import RoomBuilder
from dualis.world.colliders import collides, solids_for
from dualis.world.entity import Entity, EntityManager
from dualis.world.phenomenon import TestPhenomenon
from dualis.world.room import RoomManager
from dualis.world.test_transformable import TestTransformable
from dualis.world.transit import (
    decide_transit,
    entry_for,
    next_room,
    restore_actors,
    slice_exit_target,
    snapshot_actors,
)

ROOT = Path(__file__).resolve().parents[1]
ROOMS_DIR = ROOT / "data" / "rooms"
BLUEPRINTS_DIR = ROOT / "data" / "blueprints"
PATTERNS_DIR = ROOT / "data" / "patterns"

CHAIN = ["VEST_%02d" % n for n in range(1, 15)] + \
        ["BIB_%02d" % n for n in range(1, 9)] + \
        ["TAL_%02d" % n for n in range(1, 10)]


def _blueprints():
    out = {}
    for path in sorted(BLUEPRINTS_DIR.glob("*.json")):
        blueprint = load_blueprint(path, PATTERNS_DIR)
        out[blueprint.rid] = blueprint
    return out


def _links():
    rooms = RoomManager(EventBus())
    rooms.load_directory(ROOMS_DIR)
    builder = RoomBuilder(rooms)
    for rid, blueprint in _blueprints().items():
        builder.build(blueprint)
    return {rid: definition.enlaces for rid, definition in rooms.definitions.items()}


def _pattern(pid):
    for path in PATTERNS_DIR.glob("*.json"):
        raw = json.loads(path.read_text(encoding="utf-8"))
        if raw["id"] == pid:
            return raw
    raise KeyError(pid)


def _play(rid):
    bus = EventBus()
    rooms = RoomManager(bus)
    rooms.load_directory(ROOMS_DIR)
    builder = RoomBuilder(rooms)
    blueprint = load_blueprint(BLUEPRINTS_DIR / (rid.lower() + ".json"), PATTERNS_DIR)
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
    return {"bus": bus, "uno": uno, "dos": dos, "link": link,
            "observe": observe, "runtimes": runtimes,
            "runtime": runtimes.runtime_for(rid),
            "exit": blueprint.exit_rect, "actors": built.actors}


def _solve(ctx):
    assert ctx["observe"].request("UNO") is True
    ctx["observe"].update(0.1)
    return ctx


def _park_center(ctx):
    ex, ey, ew, eh = ctx["exit"]
    ctx["uno"].x, ctx["uno"].y = ex + ew / 2.0, ey + eh / 2.0
    ctx["dos"].x, ctx["dos"].y = ex + ew / 2.0, ey + eh / 2.0


def test_cadena_r1_r2_r3_navegable_por_enlaces():
    links = _links()
    rid, prev = "VEST_01", "ROOM_SLICE"
    seen = [rid]
    for _ in range(len(CHAIN)):
        nxt = next_room(links, rid, prev)
        if nxt is None:
            break
        seen.append(nxt)
        prev, rid = rid, nxt
    assert seen == CHAIN  # VEST_01..VEST_14, BIB_01..08, TAL_01..09
    assert seen[14] == "BIB_01" and seen[22] == "TAL_01"
    assert next_room(links, "TAL_09", "TAL_08") is None  # fondo de saco: quedarse


def test_next_room_direccion_atras_y_bordes():
    links = _links()
    assert next_room(links, "VEST_02", "VEST_03") == "VEST_01"
    assert next_room(links, "VEST_01", "VEST_02") == "ROOM_SLICE"
    assert next_room(links, "VEST_05", None) == "VEST_04"  # salto manual: primer enlace
    assert next_room(links, "VEST_05", "DESCONOCIDA") == "VEST_04"
    assert next_room(links, "DESCONOCIDA", None) is None
    assert next_room(links, "TAL_09", "TAL_08") is None


def test_slice_sale_hacia_r1():
    assert slice_exit_target(_blueprints()) == "VEST_01"


def test_entradas_coherentes_seguras_y_conectadas():
    blueprints = _blueprints()
    cases = [("ROOM_SLICE", SLICE_EXIT)]
    cases += [(rid, bp.exit_rect) for rid, bp in sorted(blueprints.items())]
    for rid, exit_rect in cases:
        solids = solids_for(rid, tuple(exit_rect))
        for from_rid in (None, "VEST_01", "TAL_09"):
            (ux, uy), (dx, dy) = entry_for(tuple(exit_rect), solids, from_rid)
            for px, py in ((ux, uy), (dx, dy)):
                ex, ey, ew, eh = exit_rect
                assert not (ex <= px <= ex + ew and ey <= py <= ey + eh), (rid, from_rid)
                assert not collides(px, py, 14, solids), (rid, from_rid)
            dist = math.hypot(ux - dx, uy - dy)
            assert dist < 210.0, (rid, dist)  # el vínculo se mantiene en CONNECTED
            again = entry_for(tuple(exit_rect), solids, from_rid)
            assert again == ((ux, uy), (dx, dy)), (rid, from_rid)  # determinista


def test_reset_local_sin_reinicio_global():
    solved = _play("VEST_01")
    _solve(solved)
    _park_center(solved)
    solved["runtimes"].update(0.1, "VEST_01")
    assert solved["runtime"].state == "COMPLETED"

    other = _play("VEST_02")
    snap = snapshot_actors(other["actors"])
    for actor in other["actors"]:
        actor.x += 60.0
        actor.y += 40.0
        if hasattr(actor, "frozen"):
            actor.frozen = True
        if hasattr(actor, "is_transformed"):
            actor.is_transformed = True
    restore_actors(other["actors"], snap)
    for actor in other["actors"]:
        assert (actor.x, actor.y) == (snap[actor.id]["x"], snap[actor.id]["y"])
        if hasattr(actor, "frozen"):
            assert actor.frozen is snap[actor.id]["frozen"]
        if hasattr(actor, "is_transformed"):
            assert actor.is_transformed is snap[actor.id]["is_transformed"]
    assert solved["runtime"].state == "COMPLETED"  # el progreso global sigue


def test_persistencia_minima_ida_y_vuelta(tmp_path):
    path = str(tmp_path / "soft.json")
    save_soft(path, "VEST_07", "VEST_06")
    assert load_soft(path) == ("VEST_07", "VEST_06")
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    assert set(raw) == {"room", "prev"}  # mínima: nada de entidades ni runtimes
    save_soft(path, "BIB_01")
    assert load_soft(path) == ("BIB_01", None)


def test_persistencia_rota_devuelve_nada(tmp_path):
    missing = str(tmp_path / "noexiste.json")
    assert load_soft(missing) == (None, None)
    corrupt = tmp_path / "roto.json"
    corrupt.write_text("{no json", encoding="utf-8")
    assert load_soft(str(corrupt)) == (None, None)
    wrong = tmp_path / "raro.json"
    wrong.write_text(json.dumps({"room": 42}), encoding="utf-8")
    assert load_soft(str(wrong)) == (None, None)


def test_decide_transito_vest01_a_vest02():
    links = _links()
    blueprints = _blueprints()
    ctx = _play("VEST_01")
    assert decide_transit("VEST_01", "ROOM_SLICE", links, ctx["runtimes"],
                          None, ctx["uno"], ctx["dos"], blueprints) is None
    _solve(ctx)
    ctx["uno"].x, ctx["uno"].y = 120.0, 280.0  # resuelto pero fuera de la salida
    ctx["dos"].x, ctx["dos"].y = 220.0, 280.0
    ctx["runtimes"].update(0.1, "VEST_01")
    assert ctx["runtime"].state == "READY"
    assert decide_transit("VEST_01", "ROOM_SLICE", links, ctx["runtimes"],
                          None, ctx["uno"], ctx["dos"], blueprints) is None
    _park_center(ctx)
    ctx["runtimes"].update(0.1, "VEST_01")
    assert ctx["runtime"].state == "COMPLETED"
    assert decide_transit("VEST_01", "ROOM_SLICE", links, ctx["runtimes"],
                          None, ctx["uno"], ctx["dos"], blueprints) == "VEST_02"


def test_decide_transito_fondo_de_saco_se_queda():
    links = _links()
    blueprints = _blueprints()
    ctx = _play("TAL_09")
    assert ctx["runtime"] is not None
    assert decide_transit("TAL_09", "TAL_08", links, ctx["runtimes"],
                          None, ctx["uno"], ctx["dos"], blueprints) is None


def test_decide_transito_slice_a_r1():
    bus = EventBus()
    entities = EntityManager()
    uno = entities.register(Entity("UNO", x=120.0, y=280.0))
    dos = entities.register(Entity("DOS", x=220.0, y=280.0))
    registry = ObservableRegistry()
    phenomenon = registry.register(TestPhenomenon())
    observe = ObserveSystem(registry, bus)
    tregistry = TransformableRegistry()
    testbox = tregistry.register(TestTransformable())
    transform = TransformSystem(bus)
    puzzle = SlicePuzzle(transform, phenomenon, testbox, uno, dos, bus)
    links = _links()
    blueprints = _blueprints()
    assert decide_transit("ROOM_SLICE", None, links, None, puzzle,
                          uno, dos, blueprints) is None
    observe.request("UNO")
    observe.update(0.1)
    puzzle.update(0.1)
    assert puzzle.try_transform("DOS") is True
    cx, cy = SLICE_EXIT[0] + SLICE_EXIT[2] / 2.0, SLICE_EXIT[1] + SLICE_EXIT[3] / 2.0
    uno.x, uno.y = cx, cy
    dos.x, dos.y = cx, cy
    puzzle.update(0.1)
    assert puzzle.state == SlicePuzzle.SOLVED
    assert decide_transit("ROOM_SLICE", None, links, None, puzzle,
                          uno, dos, blueprints) == "VEST_01"


def test_examenes_y_bisagra_intactos():
    blueprints = _blueprints()
    assert tuple(blueprints["VEST_01"].exit_rect) == (500, 240, 100, 80)
    assert tuple(blueprints["BIB_01"].exit_rect) == (420, 40, 110, 70)
    assert tuple(blueprints["TAL_01"].exit_rect) == (80, 240, 100, 80)
    assert blueprints["TAL_09"].enlaces == ("TAL_08",)
    assert blueprints["VEST_14"].enlaces == ("VEST_13", "BIB_01")
    assert blueprints["BIB_08"].enlaces == ("BIB_07", "TAL_01")


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)
