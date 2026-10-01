"""Tests F22: mundo sólido. Solo colisiones del escenario.

Sólidos: wall, pillar, column, block. No sólidos: plataformas (solo
visuales), sombras, salida, vínculo. Sin world_z jugable, sin
pathfinding ni mecánicas nuevas. No modifica tests existentes.
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pygame

from dualis import config
from dualis.core.bus import EventBus
from dualis.core.scene import SceneManager
from dualis.presentation import tiles as _tiles
from dualis.presentation.renderer_iso import RendererISO
from dualis.scenes.room_scene import RoomScene
from dualis.systems.cooperation import MountAction
from dualis.systems.link import LinkSystem
from dualis.systems.observable import ObservableRegistry
from dualis.systems.observe import ObserveSystem
from dualis.systems.slice_puzzle import EXIT_RECT as SLICE_EXIT
from dualis.systems.slice_puzzle import SlicePuzzle
from dualis.systems.transform import TransformSystem
from dualis.systems.transformable import TransformableRegistry
from dualis.world.blueprint import load_blueprint
from dualis.world.builder import RoomBuilder
from dualis.world.colliders import (
    NON_SOLID_ELEVATION,
    SOLID_KINDS,
    collides,
    move_with_collision,
    solids_for,
)
from dualis.world.entity import Entity, EntityManager
from dualis.world.phenomenon import TestPhenomenon
from dualis.world.room import RoomManager
from dualis.world.test_transformable import TestTransformable

ROOT = Path(__file__).resolve().parents[1]
ROOMS_DIR = ROOT / "data" / "rooms"
BLUEPRINTS_DIR = ROOT / "data" / "blueprints"
PATTERNS_DIR = ROOT / "data" / "patterns"

VEST_EXIT = (500, 240, 100, 80)
BIB_EXIT = (420, 40, 110, 70)
TAL_EXIT = (80, 240, 100, 80)
SPAWNS = ((120.0, 280.0), (220.0, 280.0))


def _scene(rid="VEST_01"):
    pygame.init()
    bus = EventBus()
    rooms = RoomManager(bus)
    rooms.load_directory(ROOMS_DIR)
    entities = EntityManager()
    entities.register(Entity("UNO", x=120.0, y=280.0))
    entities.register(Entity("DOS", x=220.0, y=280.0,
                             color=(90, 180, 170), shape="square"))
    registry = ObservableRegistry()
    phenomenon = registry.register(TestPhenomenon())
    entities.register(phenomenon)
    observe = ObserveSystem(registry, bus)
    tregistry = TransformableRegistry()
    testbox = tregistry.register(TestTransformable())
    entities.register(testbox)
    transform = TransformSystem(bus)
    link = LinkSystem(entities, bus)
    puzzle = SlicePuzzle(transform, phenomenon, testbox,
                         entities.get("UNO"), entities.get("DOS"), bus)
    builder = RoomBuilder(rooms)
    from dualis.systems.room_runtime import RoomRuntimeManager
    runtimes = RoomRuntimeManager(bus, transform, mount=None,
                                  uno=entities.get("UNO"), dos=entities.get("DOS"))
    runtimes.register_actors("ROOM_SLICE", [phenomenon, testbox])
    for path in sorted(BLUEPRINTS_DIR.glob("*.json")):
        blueprint = load_blueprint(path, PATTERNS_DIR)
        built = builder.build(blueprint)
        for actor in built.actors:
            entities.register(actor)
        runtimes.add_room(blueprint, built.actors)
    rooms.enter(rid)
    manager = SceneManager(bus)
    scene = RoomScene(rooms, entities, link, observe, transform, testbox,
                      puzzle, None, bus, runtimes=runtimes)
    manager.set_scene(scene)
    return manager, scene


def _has_color(surface, color):
    for x in range(surface.get_width()):
        for y in range(surface.get_height()):
            if surface.get_at((x, y))[:3] == color:
                return True
    return False


def test_solidos_derivan_del_decorado():
    solids = solids_for("VEST_01", VEST_EXIT)
    assert solids, "la sala debe tener sólidos"
    walls = [s for s in _tiles.tall_tiles("VEST_01", VEST_EXIT)
             if s["kind"] == "wall"]
    assert len([s for s in solids]) >= len(walls)
    for spec in _tiles.elevation_tiles("VEST_01", VEST_EXIT):
        rect = (float(spec["x"]), float(spec["y"]),
                float(spec["w"]), float(spec["h"]))
        if spec["kind"] in NON_SOLID_ELEVATION:
            assert rect not in solids, spec
        else:
            assert rect in solids, spec


def test_colision_muro():
    solids = solids_for("VEST_01", VEST_EXIT)
    assert ("wall" in SOLID_KINDS)
    actor = Entity("T", x=90.0, y=60.0)  # bajo el muro norte (y 0..22)
    move_with_collision(actor, 0.0, -50.0, solids)
    assert actor.y >= 22.0 + actor.radius  # no atraviesa, no teletransporta
    assert not collides(actor.x, actor.y, actor.radius, solids)
    # Aproximación gradual: contacta sin entrar.
    actor = Entity("T", x=90.0, y=60.0)
    for _ in range(30):
        move_with_collision(actor, 0.0, -2.0, solids)
    assert 22.0 + actor.radius - 2.5 <= actor.y <= 60.0
    assert not collides(actor.x, actor.y, actor.radius, solids)


def test_colision_pilar():
    solids = solids_for("VEST_01", VEST_EXIT)
    assert ("pillar" in SOLID_KINDS)
    actor = Entity("T", x=100.0, y=40.0)  # a la derecha del pilar (26..54)
    for _ in range(30):
        move_with_collision(actor, -2.0, 0.0, solids)
    assert actor.x >= 54.0 + actor.radius - 2.5
    assert not collides(actor.x, actor.y, actor.radius, solids)


def test_colision_bloque_y_columna():
    solids = solids_for("VEST_01", VEST_EXIT)
    assert "column" in SOLID_KINDS and "block" in SOLID_KINDS
    elevated = [s for s in _tiles.elevation_tiles("VEST_01", VEST_EXIT)
                if s["kind"] in ("column", "block")]
    assert elevated
    for spec in elevated:
        sx, sy, sw, sh = (float(spec[k]) for k in ("x", "y", "w", "h"))
        actor = Entity("T", x=sx + sw / 2.0, y=sy - 40.0)
        assert not collides(actor.x, actor.y, actor.radius, solids)
        for _ in range(40):
            move_with_collision(actor, 0.0, 2.0, solids)
        assert actor.y + actor.radius <= sy + 2.5, spec
        assert not collides(actor.x, actor.y, actor.radius, solids)


def test_deslizamiento_diagonal():
    solids = solids_for("VEST_01", VEST_EXIT)
    actor = Entity("T", x=60.0, y=90.0)  # a la derecha del muro oeste (x 0..22)
    move_with_collision(actor, -50.0, 30.0, solids)
    assert actor.x == 60.0  # eje X bloqueado
    assert actor.y == 120.0  # eje Y desliza intacto
    assert not collides(actor.x, actor.y, actor.radius, solids)


def test_plataformas_solo_visuales_sin_world_z():
    for rid, exit_rect in (("VEST_01", VEST_EXIT), ("BIB_01", BIB_EXIT),
                           ("TAL_01", TAL_EXIT)):
        plats = [s for s in _tiles.elevation_tiles(rid, exit_rect)
                 if s["kind"] in NON_SOLID_ELEVATION]
        assert len(plats) == 3, (rid, plats)
        solids = solids_for(rid, exit_rect)
        actor = Entity("T", x=320.0, y=300.0)
        assert not hasattr(actor, "world_z")
        for spec in plats:
            sx, sy, sw, sh = (float(spec[k]) for k in ("x", "y", "w", "h"))
            # Cruza la plataforma por su eje medio en pasos cortos (como el
            # juego real): la plataforma nunca debe detener el avance.
            actor.x, actor.y = sx - 40.0, sy + sh / 2.0
            for _ in range(60):
                if actor.x >= sx + sw - 5.0:
                    break
                move_with_collision(actor, 5.0, 0.0, solids)
            assert actor.x >= sx + sw - 5.0, (rid, spec)  # cruza libre


def test_salida_accesible_y_spawn_libre():
    cases = [("ROOM_SLICE", SLICE_EXIT), ("VEST_01", VEST_EXIT),
             ("BIB_01", BIB_EXIT), ("TAL_01", TAL_EXIT)]
    for rid, exit_rect in cases:
        solids = solids_for(rid, exit_rect)
        ex, ey, ew, eh = (float(v) for v in exit_rect)
        assert ew >= 28.0 and eh >= 28.0  # cabe el actor (r=14)
        # Centro + puntos cardinales: el actor se planta en la salida.
        # (Las esquinas pueden rozar decorado de borde preexistente F19,
        # como el pilar sobre la esquina de ROOM_SLICE; el centro manda.)
        for px, py in ((ex + ew / 2.0, ey + eh / 2.0),
                       (ex + ew / 2.0, ey + 15.0),
                       (ex + ew / 2.0, ey + eh - 15.0),
                       (ex + 15.0, ey + eh / 2.0),
                       (ex + ew - 15.0, ey + eh / 2.0)):
            assert not collides(px, py, 14, solids), (rid, px, py)
    for rid, exit_rect in cases[1:]:
        solids = solids_for(rid, exit_rect)
        for sx, sy in SPAWNS:
            assert not collides(sx, sy, 14, solids), (rid, sx, sy)


def test_entity_move_intacto_sin_colision():
    actor = Entity("T", x=90.0, y=60.0)
    actor.move(0.0, -50.0)  # crudo: la capa física vive en colliders/main
    assert (actor.x, actor.y) == (90.0, 10.0)


def _play(rid):
    bus = EventBus()
    rooms = RoomManager(bus)
    rooms.load_directory(ROOMS_DIR)
    builder = RoomBuilder(rooms)
    blueprint = load_blueprint(BLUEPRINTS_DIR / (rid.lower() + ".json"), PATTERNS_DIR)
    pattern_raw = None
    for path in PATTERNS_DIR.glob("*.json"):
        raw = json.loads(path.read_text(encoding="utf-8"))
        if raw["id"] == blueprint.pattern:
            pattern_raw = raw
            break
    built = builder.build(blueprint, pattern_raw)
    uno = Entity("UNO", x=120.0, y=280.0)
    dos = Entity("DOS", x=220.0, y=280.0)
    transform = TransformSystem(bus)
    mount = MountAction(uno, dos, bus)
    from dualis.systems.room_runtime import RoomRuntimeManager
    runtimes = RoomRuntimeManager(bus, transform, mount, uno, dos)
    runtimes.add_room(blueprint, built.actors)
    rooms.enter(rid)
    return {"bus": bus, "uno": uno, "dos": dos, "transform": transform,
            "mount": mount, "runtimes": runtimes,
            "runtime": runtimes.runtime_for(rid), "exit": blueprint.exit_rect}


def test_vest01_resoluble():
    ctx = _play("VEST_01")
    observe = ObserveSystem(ctx["runtimes"].registry_for("VEST_01"), ctx["bus"])
    observe.request("UNO")
    observe.update(0.1)
    cx = ctx["exit"][0] + ctx["exit"][2] / 2.0
    cy = ctx["exit"][1] + ctx["exit"][3] / 2.0
    ctx["uno"].x, ctx["uno"].y = cx, cy
    ctx["dos"].x, ctx["dos"].y = cx, cy
    ctx["runtimes"].update(0.1, "VEST_01")
    assert ctx["runtime"].state == "COMPLETED"


def test_bib01_resoluble():
    ctx = _play("BIB_01")
    assert ctx["runtimes"].try_transform("BIB_01", "DOS") is False
    observe = ObserveSystem(ctx["runtimes"].registry_for("BIB_01"), ctx["bus"])
    observe.request("UNO")
    observe.update(0.1)
    assert ctx["runtimes"].try_transform("BIB_01", "DOS") is True
    cx = ctx["exit"][0] + ctx["exit"][2] / 2.0
    cy = ctx["exit"][1] + ctx["exit"][3] / 2.0
    ctx["uno"].x, ctx["uno"].y = cx, cy
    ctx["dos"].x, ctx["dos"].y = cx, cy
    ctx["runtimes"].update(0.1, "BIB_01")
    assert ctx["runtime"].state == "COMPLETED"


def test_tal01_resoluble():
    ctx = _play("TAL_01")
    observe = ObserveSystem(ctx["runtimes"].registry_for("TAL_01"), ctx["bus"])
    observe.request("UNO")
    observe.update(0.1)
    cx = ctx["exit"][0] + ctx["exit"][2] / 2.0
    cy = ctx["exit"][1] + ctx["exit"][3] / 2.0
    ctx["uno"].x, ctx["uno"].y = cx, cy
    ctx["dos"].x, ctx["dos"].y = cx, cy
    ctx["runtimes"].update(0.1, "TAL_01")
    assert ctx["runtime"].state == "COMPLETED"


def test_render_intacto_tres_salas():
    renderer = RendererISO()
    for rid, exit_rect, outline in (
            ("VEST_01", VEST_EXIT, (80, 180, 100)),
            ("BIB_01", BIB_EXIT, (80, 180, 100)),
            ("TAL_01", TAL_EXIT, (80, 180, 100))):
        _, scene = _scene(rid)
        canvas = pygame.Surface(config.LOGICAL_SIZE)
        renderer.render(scene, canvas, fps=60.0)
        assert _has_color(canvas, outline), rid  # contorno F17 intacto
        assert _has_color(canvas, (40, 40, 56)), rid  # rejilla F18 intacta


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)
