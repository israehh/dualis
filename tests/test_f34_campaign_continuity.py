"""F34: continuidad R5 añadida únicamente en el overlay de campaña."""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dualis.core.bus import EventBus
from dualis.world.blueprint import load_blueprint
from dualis.world.builder import RoomBuilder
from dualis.world.campaign import (
    EXTRA_LINKS,
    F34_EXTRA_LINKS,
    R4_ORDER,
    R5_EXTRA_LINKS,
    R5_ORDER,
    with_integration,
)
from dualis.world.room import RoomManager
from dualis.world.transit import next_room, slice_exit_target


ROOT = Path(__file__).resolve().parents[1]
ROOMS_DIR = ROOT / "data" / "rooms"
BLUEPRINTS_DIR = ROOT / "data" / "blueprints"
R4_DIR = ROOT / "data" / "r4_rooms"
R5_DIR = ROOT / "data" / "r5_rooms"
PATTERNS_DIR = ROOT / "data" / "patterns"

R13_ORDER = (
    ["VEST_%02d" % number for number in range(1, 15)]
    + ["BIB_%02d" % number for number in range(1, 9)]
    + ["TAL_%02d" % number for number in range(1, 10)]
)
CAMPAIGN_ORDER = (
    ["ROOM_SLICE"] + R13_ORDER + list(R4_ORDER) + list(R5_ORDER)
)


def _blueprints():
    result = {}
    for directory in (BLUEPRINTS_DIR, R4_DIR, R5_DIR):
        for path in sorted(directory.glob("*.json")):
            blueprint = load_blueprint(path, PATTERNS_DIR)
            result[blueprint.rid] = blueprint
    return result


def _base_links():
    rooms = RoomManager(EventBus())
    rooms.load_directory(ROOMS_DIR)
    builder = RoomBuilder(rooms)
    for blueprint in _blueprints().values():
        builder.build(blueprint)
    return {rid: definition.enlaces for rid, definition in rooms.definitions.items()}


def _integrated_route(links, blueprints):
    first_room = slice_exit_target(blueprints)
    assert first_room == "VEST_01"
    route = ["ROOM_SLICE", first_room]
    previous, current = "ROOM_SLICE", first_room

    for _ in range(len(CAMPAIGN_ORDER)):
        target = next_room(links, current, previous)
        if target is None:
            break
        route.append(target)
        previous, current = current, target

    return route


def test_f34_anade_r504_r505_sin_mutar_mapa_base():
    base = _base_links()
    original_r504 = base["R5_04"]
    original_r505 = base["R5_05"]

    integrated = with_integration(base)

    assert integrated is not base
    assert F34_EXTRA_LINKS == {"R5_04": ("R5_03", "R5_05")}
    assert integrated["R5_04"] == ("R5_03", "R5_05")
    assert next_room(integrated, "R5_04", "R5_03") == "R5_05"
    assert base["R5_04"] == original_r504 == ("R5_03",)
    assert base["R5_05"] == original_r505 == ("R5_04", "R5_06")


def test_json_r504_y_r505_permanecen_intactos():
    blueprints = _blueprints()

    assert blueprints["R5_04"].enlaces == ("R5_03",)
    assert blueprints["R5_05"].enlaces == ("R5_04", "R5_06")


def test_room_slice_alcanza_r5_exam_por_la_cadena_completa():
    links = with_integration(_base_links())
    route = _integrated_route(links, _blueprints())

    assert route == CAMPAIGN_ORDER
    assert route[-1] == "R5_EXAM"


def test_r5_exam_sigue_siendo_terminal_de_la_campana():
    links = with_integration(_base_links())

    assert links["R5_EXAM"] == ("R5_08",)
    assert next_room(links, "R5_EXAM", "R5_08") is None


def test_f28_y_aristas_f33_se_conservan():
    base = _base_links()
    integrated = with_integration(base)

    assert EXTRA_LINKS == {
        "TAL_09": ("TAL_08", "R4_01"),
        "R4_04": ("R4_03", "R4_05"),
        "R4_08": ("R4_07", "R4_EXAM"),
    }
    assert R5_EXTRA_LINKS == {
        "R4_EXAM": ("R4_08", "R5_01"),
        "R5_08": ("R5_07", "R5_EXAM"),
    }
    for overlay in (EXTRA_LINKS, R5_EXTRA_LINKS):
        for rid, links in overlay.items():
            assert integrated[rid] == links


def test_cadena_sin_ciclos_ni_nodos_huerfanos():
    links = with_integration(_base_links())
    route = _integrated_route(links, _blueprints())

    assert len(route) == len(set(route))
    assert set(route) == set(CAMPAIGN_ORDER)
    assert links["R5_04"] == ("R5_03", "R5_05")
    assert links["R5_05"] == ("R5_04", "R5_06")
    assert links["R5_08"] == ("R5_07", "R5_EXAM")


if __name__ == "__main__":
    for name, function in sorted(globals().items()):
        if name.startswith("test_"):
            function()
            print("ok", name)