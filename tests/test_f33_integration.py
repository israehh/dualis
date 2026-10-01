"""Tests F33 — Integración de R4: campaña completa sin tocar datos congelados.

Los JSON siguen intactos (TAL_09, R4_04 y R4_08 declaran fondos de saco
temporales; los tests F24–F27 los congelan). F28 añade la capa de campaña
world/campaign.py (overlay en memoria) + carga R4 en main.py + gate LINK
opcional en decide_transit. Sin rooms, mecánicas, render ni sistemas nuevos.

Verifica: overlay puro, cadena ROOM_SLICE→…→R4_EXAM recorrible en ambos
sentidos, las tres bisagras disparando, TENSION gobernando el tránsito
real donde hay puerta declarada, y compatibilidad total sin link.
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
from dualis.world.campaign import EXTRA_LINKS, R4_ORDER, R5_EXTRA_LINKS, R5_ORDER, with_integration
from dualis.world.colliders import collides, solids_for
from dualis.world.entity import Entity, EntityManager
from dualis.world.link_gate import exit_allowed
from dualis.world.room import RoomManager
from dualis.world.transit import decide_transit, entry_for, next_room, slice_exit_target

ROOT = Path(__file__).resolve().parents[1]
ROOMS_DIR = ROOT / "data" / "rooms"
BLUEPRINTS_DIR = ROOT / "data" / "blueprints"
R4_DIR = ROOT / "data" / "r4_rooms"
R5_DIR = ROOT / "data" / "r5_rooms"
PATTERNS_DIR = ROOT / "data" / "patterns"

CHAIN_R13 = (["VEST_%02d" % n for n in range(1, 15)] +
             ["BIB_%02d" % n for n in range(1, 9)] +
             ["TAL_%02d" % n for n in range(1, 10)])
FULL_CHAIN = CHAIN_R13 + list(R4_ORDER)
CHAIN_R5 = list(R5_ORDER)


def _pattern(pid):
    for path in PATTERNS_DIR.glob("*.json"):
        raw = json.loads(path.read_text(encoding="utf-8"))
        if raw["id"] == pid:
            return raw
    raise KeyError(pid)


def _blueprints():
    out = {}
    for directory in (BLUEPRINTS_DIR, R4_DIR, R5_DIR):
        for path in sorted(directory.glob("*.json")):
            blueprint = load_blueprint(path, PATTERNS_DIR)
            out[blueprint.rid] = blueprint
    return out


def _base_links():
    rooms = RoomManager(EventBus())
    rooms.load_directory(ROOMS_DIR)
    builder = RoomBuilder(rooms)
    for blueprint in _blueprints().values():
        builder.build(blueprint)
    return {rid: definition.enlaces for rid, definition in rooms.definitions.items()}


def _integrated():
    return with_integration(_base_links())


def _play(rid):
    for directory in (BLUEPRINTS_DIR, R4_DIR, R5_DIR):
        path = directory / (rid.lower() + ".json")
        if path.exists():
            blueprint = load_blueprint(path, PATTERNS_DIR)
            break
    bus = EventBus()
    rooms = RoomManager(bus)
    rooms.load_directory(ROOMS_DIR)
    builder = RoomBuilder(rooms)
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
    rooms.enter(rid)
    observe = ObserveSystem(runtimes.registry_for(rid), bus)
    return {"bus": bus, "rooms": rooms, "uno": uno, "dos": dos,
            "link": link, "observe": observe, "mount": mount,
            "runtimes": runtimes, "runtime": runtimes.runtime_for(rid),
            "exit": blueprint.exit_rect, "blueprint": blueprint}


def _center(exit_rect):
    ex, ey, ew, eh = exit_rect
    return (ex + ew / 2.0, ey + eh / 2.0)


def _park_center(ctx):
    cx, cy = _center(ctx["exit"])
    ctx["uno"].x, ctx["uno"].y = cx, cy
    ctx["dos"].x, ctx["dos"].y = cx, cy


def _observe(ctx):
    assert ctx["observe"].request("UNO") is True
    ctx["observe"].update(0.1)


def _solve_exam_like(ctx, rid):
    """OBSERVE → TRANSFORM → juntar → MOUNT → completar (TAL_09, R4_EXAM)."""
    _observe(ctx)
    assert ctx["runtimes"].try_transform(rid, "DOS") is True
    _park_center(ctx)
    assert ctx["mount"].request("UNO") is True
    _park_center(ctx)
    ctx["runtimes"].update(0.1, rid)
    assert ctx["runtime"].state == "COMPLETED"


def test_datos_congelados_intactos():
    blueprints = _blueprints()
    assert blueprints["TAL_09"].enlaces == ("TAL_08",)
    assert blueprints["R4_04"].enlaces == ("R4_03",)
    assert blueprints["R4_08"].enlaces == ("R4_07",)
    assert blueprints["R4_EXAM"].enlaces == ("R4_08",)
    assert set(EXTRA_LINKS) == {"TAL_09", "R4_04", "R4_08"}
    assert tuple(R4_ORDER) == ("R4_01", "R4_02", "R4_03", "R4_04",
                               "R4_05", "R4_06", "R4_07", "R4_08", "R4_EXAM")


def test_overlay_no_muta_el_mapa_base():
    base = _base_links()
    integrated = with_integration(base)
    assert integrated is not base
    assert base["TAL_09"] == ("TAL_08",)  # el mapa F24 no cambia: F24 sigue verde
    assert base["R4_04"] == ("R4_03",)
    assert base["R4_08"] == ("R4_07",)
    assert integrated["TAL_09"] == ("TAL_08", "R4_01")
    assert integrated["R4_04"] == ("R4_03", "R4_05")
    assert integrated["R4_08"] == ("R4_07", "R4_EXAM")
    assert next_room(base, "TAL_09", "TAL_08") is None
    assert next_room(integrated, "TAL_09", "TAL_08") == "R4_01"


def test_cadena_completa_recorrible_ida_y_sigue_a_r5():
    links = _integrated()
    rid, prev, seen = "VEST_01", "ROOM_SLICE", ["VEST_01"]
    for _ in range(len(FULL_CHAIN) + len(CHAIN_R5)):
        nxt = next_room(links, rid, prev)
        if nxt is None:
            break
        seen.append(nxt)
        prev, rid = rid, nxt
    assert seen == FULL_CHAIN + list(R5_ORDER)
    assert seen[14] == "BIB_01" and seen[22] == "TAL_01"
    assert seen[31] == "R4_01" and seen[-1] == "R5_EXAM"
    assert next_room(links, "R4_EXAM", "R4_08") == "R5_01"  # bisagra F33: seguir


def test_cadena_completa_vuelta_atras():
    links = _integrated()
    assert next_room(links, "R4_EXAM", None) == "R4_08"
    assert next_room(links, "R4_01", "R4_02") == "TAL_09"
    assert next_room(links, "R4_04", "R4_05") == "R4_03"
    assert next_room(links, "R4_08", "R4_EXAM") == "R4_07"
    assert next_room(links, "TAL_09", "R4_01") == "TAL_08"
    assert next_room(links, "VEST_01", "VEST_02") == "ROOM_SLICE"


def test_slice_sigue_llevando_a_vest01():
    assert slice_exit_target(_blueprints()) == "VEST_01"


def test_bisagra_tal09_a_r401_dispara():
    links = _integrated()
    blueprints = _blueprints()
    ctx = _play("TAL_09")
    _solve_exam_like(ctx, "TAL_09")
    assert decide_transit("TAL_09", "TAL_08", links, ctx["runtimes"],
                          None, ctx["uno"], ctx["dos"], blueprints,
                          link=ctx["link"]) == "R4_01"
    base = _base_links()
    assert decide_transit("TAL_09", "TAL_08", base, ctx["runtimes"],
                          None, ctx["uno"], ctx["dos"], blueprints) is None


def test_brecha_r404_a_r405_dispara():
    links = _integrated()
    blueprints = _blueprints()
    ctx = _play("R4_04")
    assert ctx["runtimes"].try_transform("R4_04", "DOS") is True
    _park_center(ctx)
    ctx["runtimes"].update(0.1, "R4_04")
    assert ctx["runtime"].state == "COMPLETED"
    assert decide_transit("R4_04", "R4_03", links, ctx["runtimes"],
                          None, ctx["uno"], ctx["dos"], blueprints,
                          link=ctx["link"]) == "R4_05"


def test_bisagra_r408_exam_r501():
    links = _integrated()
    blueprints = _blueprints()
    ctx = _play("R4_08")
    _observe(ctx)
    assert ctx["runtimes"].try_transform("R4_08", "DOS") is True
    _park_center(ctx)
    ctx["runtimes"].update(0.1, "R4_08")
    assert ctx["runtime"].state == "COMPLETED"
    assert decide_transit("R4_08", "R4_07", links, ctx["runtimes"],
                          None, ctx["uno"], ctx["dos"], blueprints,
                          link=ctx["link"]) == "R4_EXAM"
    exam = _play("R4_EXAM")
    _solve_exam_like(exam, "R4_EXAM")
    exam["uno"].x, exam["uno"].y = 170.0, 240.0
    exam["dos"].x, exam["dos"].y = 430.0, 240.0
    assert exam["link"].update(0.016) == LinkSystem.TENSION
    exam["runtimes"].update(0.1, "R4_EXAM")
    assert exit_allowed(exam["runtime"], exam["link"], "R4_EXAM") is True
    assert decide_transit("R4_EXAM", "R4_08", links, exam["runtimes"],
                          None, exam["uno"], exam["dos"], blueprints,
                          link=exam["link"]) == "R5_01"


def test_gate_tension_gobierna_el_transito_real():
    links = _integrated()
    blueprints = _blueprints()
    ctx = _play("R4_05")
    _observe(ctx)
    ctx["uno"].x, ctx["uno"].y = 170.0, 240.0
    ctx["dos"].x, ctx["dos"].y = 430.0, 240.0
    assert ctx["link"].update(0.016) == LinkSystem.TENSION
    ctx["runtimes"].update(0.1, "R4_05")
    assert ctx["runtime"].state == "COMPLETED"
    assert decide_transit("R4_05", "R4_04", links, ctx["runtimes"],
                          None, ctx["uno"], ctx["dos"], blueprints,
                          link=ctx["link"]) == "R4_06"
    ctx["link"].state = LinkSystem.CONNECTED  # junto: completa pero no abre
    assert decide_transit("R4_05", "R4_04", links, ctx["runtimes"],
                          None, ctx["uno"], ctx["dos"], blueprints,
                          link=ctx["link"]) is None
    assert decide_transit("R4_05", "R4_04", links, ctx["runtimes"],
                          None, ctx["uno"], ctx["dos"], blueprints) == "R4_06"


def test_sin_puerta_el_vinculo_no_bloquea():
    links = _integrated()
    blueprints = _blueprints()
    ctx = _play("R4_01")
    _observe(ctx)
    _park_center(ctx)
    ctx["runtimes"].update(0.1, "R4_01")
    assert ctx["runtime"].state == "COMPLETED"
    ctx["link"].state = LinkSystem.LIMIT  # sin puerta declarada: LIMIT no bloquea
    assert decide_transit("R4_01", "TAL_09", links, ctx["runtimes"],
                          None, ctx["uno"], ctx["dos"], blueprints,
                          link=ctx["link"]) == "R4_02"


def test_r4_registrable_en_mundo_sin_colisiones():
    rooms = RoomManager(EventBus())
    rooms.load_directory(ROOMS_DIR)
    before = set(rooms.definitions)
    builder = RoomBuilder(rooms)
    for rid in R4_ORDER:
        blueprint = _blueprints()[rid]
        builder.build(blueprint, _pattern(blueprint.pattern))
    assert set(rooms.definitions) - before == set(R4_ORDER)
    for rid in R4_ORDER:
        assert rooms.definitions[rid].enlaces == _blueprints()[rid].enlaces


def test_entradas_de_vuelta_seguras():
    blueprints = _blueprints()
    for rid, from_rid in (("TAL_09", "R4_01"), ("R4_04", "R4_05"),
                          ("R4_08", "R4_EXAM")):
        exit_rect = tuple(blueprints[rid].exit_rect)
        solids = solids_for(rid, exit_rect)
        (ux, uy), (dx, dy) = entry_for(exit_rect, solids, from_rid)
        ex, ey, ew, eh = (float(v) for v in exit_rect)
        for px, py in ((ux, uy), (dx, dy)):
            assert not (ex <= px <= ex + ew and ey <= py <= ey + eh), (rid, from_rid)
            assert not collides(px, py, 14, solids), (rid, from_rid)
        assert math.hypot(ux - dx, uy - dy) < 210.0, (rid, from_rid)
        assert entry_for(exit_rect, solids, from_rid) == ((ux, uy), (dx, dy))


def test_overlay_f33_anade_bisagra_y_cierre_r5():
    assert R5_EXTRA_LINKS == {
        "R4_EXAM": ("R4_08", "R5_01"),
        "R5_08": ("R5_07", "R5_EXAM"),
    }
    assert set(EXTRA_LINKS) == {"TAL_09", "R4_04", "R4_08"}
    assert list(R5_ORDER) == ["R5_01", "R5_02", "R5_03", "R5_04", "R5_05",
                              "R5_06", "R5_07", "R5_08", "R5_EXAM"]
    merged = with_integration(_base_links())
    assert merged["R4_EXAM"] == ("R4_08", "R5_01")
    assert merged["R5_08"] == ("R5_07", "R5_EXAM")
    assert merged["R5_EXAM"] == ("R5_08",)


def test_json_r5_congelados_tras_overlay():
    blueprints = _blueprints()
    assert blueprints["R4_EXAM"].enlaces == ("R4_08",)
    assert blueprints["R5_01"].enlaces == ("R4_EXAM", "R5_02")
    assert blueprints["R5_04"].enlaces == ("R5_03",)
    assert blueprints["R5_05"].enlaces == ("R5_04", "R5_06")
    assert blueprints["R5_08"].enlaces == ("R5_07",)
    assert blueprints["R5_EXAM"].enlaces == ("R5_08",)
    for rid, bp in blueprints.items():
        if rid.startswith("R5"):
            for target in bp.enlaces:
                assert not target.startswith("R6")


def test_tramo_r5_continua_hasta_r5_exam():
    links = _integrated()
    rid, prev, seen = "R5_01", "R4_EXAM", ["R5_01"]
    for _ in range(len(CHAIN_R5)):
        nxt = next_room(links, rid, prev)
        if nxt is None:
            break
        prev, rid, seen = rid, nxt, seen + [nxt]
    assert seen == list(R5_ORDER)


def test_tramo_r5_segundo_hasta_r5_exam_fondo_final():
    links = _integrated()
    rid, prev, seen = "R5_05", "R5_04", ["R5_05"]
    for _ in range(len(CHAIN_R5)):
        nxt = next_room(links, rid, prev)
        if nxt is None:
            break
        prev, rid, seen = rid, nxt, seen + [nxt]
    assert seen == ["R5_05", "R5_06", "R5_07", "R5_08", "R5_EXAM"]
    assert next_room(links, "R5_EXAM", "R5_08") is None
    assert next_room(links, "R5_EXAM", None) == "R5_08"


def test_r5_exam_fondo_final_no_transita():
    links = _base_links()
    exam = _play("R5_EXAM")
    _solve_exam_like(exam, "R5_EXAM")
    exam["runtimes"].update(0.1, "R5_EXAM")
    assert exam["runtime"].state == "COMPLETED"
    exam["uno"].x, exam["uno"].y = 170.0, 240.0
    exam["dos"].x, exam["dos"].y = 430.0, 240.0
    assert exam["link"].update(0.016) == LinkSystem.TENSION
    exam["runtimes"].update(0.1, "R5_EXAM")
    blueprints = _blueprints()
    assert decide_transit("R5_EXAM", "R5_08", links, exam["runtimes"],
                          None, exam["uno"], exam["dos"], blueprints,
                          link=exam["link"]) is None


def test_entradas_de_vuelta_r5_seguras():
    blueprints = _blueprints()
    for rid, from_rid in (("R5_01", "R4_EXAM"), ("R5_05", "R5_04"),
                          ("R5_08", "R5_07"), ("R5_EXAM", "R5_08")):
        exit_rect = tuple(blueprints[rid].exit_rect)
        solids = solids_for(rid, exit_rect)
        (ux, uy), (dx, dy) = entry_for(exit_rect, solids, from_rid)
        ex, ey, ew, eh = (float(v) for v in exit_rect)
        for px, py in ((ux, uy), (dx, dy)):
            assert not (ex <= px <= ex + ew and ey <= py <= ey + eh), (rid, from_rid)
            assert not collides(px, py, 14, solids), (rid, from_rid)


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)
