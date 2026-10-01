"""Tests F23 — El Vínculo Existe: LINK como condición jugable real.

Solo usa link.distance / link.state (CONNECTED, TENSION, LIMIT) ya
existentes. Sin mecánicas, teclas, acciones, sistemas, render,
colliders ni world_z nuevos. Rooms LNK_* en data/link_rooms/ con
patrones existentes; R1/R2/R3 y exámenes intactos.
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pygame

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

ROOT = Path(__file__).resolve().parents[1]
ROOMS_DIR = ROOT / "data" / "rooms"
LINK_ROOMS_DIR = ROOT / "data" / "link_rooms"
PATTERNS_DIR = ROOT / "data" / "patterns"

IDS = ["LNK_01", "LNK_02", "LNK_03", "LNK_04"]
LESSONS = {
    "LNK_01": "link-connected",
    "LNK_02": "link-tension",
    "LNK_03": "link-limit",
    "LNK_04": "link-denied",
}


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
    blueprint = load_blueprint(LINK_ROOMS_DIR / (rid.lower() + ".json"), PATTERNS_DIR)
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


def _observe(ctx):
    assert ctx["observe"].request("UNO") is True
    ctx["observe"].update(0.1)


def _center(exit_rect):
    ex, ey, ew, eh = exit_rect
    return (ex + ew / 2.0, ey + eh / 2.0)


def test_rooms_validas_una_idea_y_cluster_cerrado():
    seen = set()
    for rid in IDS:
        blueprint = load_blueprint(LINK_ROOMS_DIR / (rid.lower() + ".json"), PATTERNS_DIR)
        assert len(blueprint.ideas) == 1, rid
        assert blueprint.ideas[0] == LESSONS[rid], rid
        ex, ey, ew, eh = blueprint.exit_rect
        assert 0 <= ex and 0 <= ey and ex + ew <= 640 and ey + eh <= 360, rid
        missing = RoomBuilder(RoomManager(EventBus())).coverage(
            blueprint, _pattern(blueprint.pattern))
        assert missing == [], (rid, missing)
        for target in blueprint.enlaces:
            assert target in IDS, (rid, target)  # no toca R1/R2/R3
        seen.add(rid)
    assert seen == set(IDS)


def test_salidas_libres_de_decorado():
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


def test_lnk01_salida_exige_connected():
    ctx = _play("LNK_01")
    _observe(ctx)
    cx, cy = _center(ctx["exit"])
    ctx["uno"].x, ctx["uno"].y = cx, cy
    ctx["dos"].x, ctx["dos"].y = cx, cy
    assert ctx["link"].update(0.016) == LinkSystem.CONNECTED
    ctx["runtimes"].update(0.1, "LNK_01")
    assert ctx["runtime"].state == "COMPLETED"
    assert exit_allowed(ctx["runtime"], ctx["link"], "LNK_01") is True

    ctx = _play("LNK_01")
    _observe(ctx)
    ctx["uno"].x, ctx["uno"].y = 300.0, 180.0
    ctx["dos"].x, ctx["dos"].y = 550.0, 180.0  # d=250: TENSION, no cabe en la salida
    assert ctx["link"].update(0.016) == LinkSystem.TENSION
    ctx["runtimes"].update(0.1, "LNK_01")
    assert ctx["runtime"].state != "COMPLETED"
    assert link_allows(ctx["link"], "LNK_01") is False


def test_lnk02_salida_exige_tension():
    ctx = _play("LNK_02")
    _observe(ctx)
    ctx["uno"].x, ctx["uno"].y = 180.0, 180.0
    ctx["dos"].x, ctx["dos"].y = 440.0, 180.0  # d=260: TENSION, ambos dentro
    assert ctx["link"].update(0.016) == LinkSystem.TENSION
    ctx["runtimes"].update(0.1, "LNK_02")
    assert ctx["runtime"].state == "COMPLETED"
    assert exit_allowed(ctx["runtime"], ctx["link"], "LNK_02") is True

    ctx = _play("LNK_02")
    _observe(ctx)
    cx, cy = _center(ctx["exit"])
    ctx["uno"].x, ctx["uno"].y = cx, cy
    ctx["dos"].x, ctx["dos"].y = cx, cy  # juntos: el runtime completa, el vínculo no deja
    assert ctx["link"].update(0.016) == LinkSystem.CONNECTED
    ctx["runtimes"].update(0.1, "LNK_02")
    assert ctx["runtime"].state == "COMPLETED"
    assert exit_allowed(ctx["runtime"], ctx["link"], "LNK_02") is False


def test_lnk03_limit_rechaza_y_se_recupera():
    ctx = _play("LNK_03")
    _observe(ctx)
    ctx["uno"].x, ctx["uno"].y = 60.0, 100.0
    ctx["dos"].x, ctx["dos"].y = 410.0, 100.0  # d=350: LIMIT
    assert ctx["link"].update(0.016) == LinkSystem.LIMIT
    ctx["runtimes"].update(0.1, "LNK_03")
    assert ctx["runtime"].state != "COMPLETED"
    assert link_allows(ctx["link"], "LNK_03") is False
    assert exit_allowed(ctx["runtime"], ctx["link"], "LNK_03") is False

    ctx["dos"].x, ctx["dos"].y = 160.0, 100.0  # d=100: LIMIT->TENSION->CONNECTED
    assert ctx["link"].update(0.016) == LinkSystem.TENSION
    assert ctx["link"].update(0.016) == LinkSystem.CONNECTED
    cx, cy = _center(ctx["exit"])
    ctx["uno"].x, ctx["uno"].y = cx, cy
    ctx["dos"].x, ctx["dos"].y = cx, cy
    ctx["runtimes"].update(0.1, "LNK_03")
    assert ctx["runtime"].state == "COMPLETED"
    assert exit_allowed(ctx["runtime"], ctx["link"], "LNK_03") is True


def test_lnk04_room_denied_correcto():
    ctx = _play("LNK_04")
    assert ctx["runtimes"].try_transform("LNK_04", "DOS") is False
    assert "ROOM_DENIED" in ctx["bus"].log
    _observe(ctx)
    assert ctx["runtimes"].try_transform("LNK_04", "DOS") is True
    cx, cy = _center(ctx["exit"])
    ctx["uno"].x, ctx["uno"].y = cx, cy
    ctx["dos"].x, ctx["dos"].y = cx, cy
    assert ctx["link"].update(0.016) == LinkSystem.CONNECTED
    ctx["runtimes"].update(0.1, "LNK_04")
    assert ctx["runtime"].state == "COMPLETED"
    assert exit_allowed(ctx["runtime"], ctx["link"], "LNK_04") is True


def test_gate_sin_estados_inventados():
    ctx = _play("LNK_01")
    assert link_allows(ctx["link"], "DESCONOCIDA") is False
    assert exit_allowed(None, ctx["link"], "LNK_01") is False
    assert exit_allowed(ctx["runtime"], ctx["link"], "LNK_01") is False  # LOCKED aún
    for rid in IDS:
        ctx = _play(rid)
        ctx["uno"].x, ctx["uno"].y = 40.0, 40.0
        ctx["dos"].x, ctx["dos"].y = 600.0, 320.0  # d>500: LIMIT en las cuatro
        assert ctx["link"].update(0.016) == LinkSystem.LIMIT
        assert link_allows(ctx["link"], rid) is False, rid


def test_hud_actual_basta_para_leer_el_vinculo():
    from dualis.scenes.room_scene import RoomScene, STATE_COLORS
    pygame.init()
    try:
        assert set(STATE_COLORS) >= {"CONNECTED", "TENSION", "LIMIT"}
        ctx = _play("LNK_02")
        scene = RoomScene(ctx["rooms"], None, ctx["link"], None,
                          None, None, None, None, ctx["bus"], runtimes=ctx["runtimes"])
        surface = pygame.Surface((640, 360))
        scene.render_hud_blocks(surface, fps=60.0)  # "vínculo %s d=%d max=%d"
        ctx["uno"].x, ctx["uno"].y = 180.0, 180.0
        ctx["dos"].x, ctx["dos"].y = 440.0, 180.0
        ctx["link"].update(0.016)
        assert ctx["link"].state == LinkSystem.TENSION
        assert int(ctx["link"].distance) == 260
    finally:
        pygame.quit()


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)
