"""Capturas F24: pre-tránsito en VEST_01 y entradas en VEST_02 / BIB_01. Render intacto."""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import pygame

from dualis import config
from dualis.core.bus import EventBus
from dualis.core.scene import SceneManager
from dualis.presentation.renderer_iso import RendererISO
from dualis.scenes.room_scene import RoomScene
from dualis.systems.link import LinkSystem
from dualis.systems.observable import ObservableRegistry
from dualis.systems.observe import ObserveSystem
from dualis.systems.slice_puzzle import SlicePuzzle
from dualis.systems.transform import TransformSystem
from dualis.systems.transformable import TransformableRegistry
from dualis.world.blueprint import load_blueprint
from dualis.world.builder import RoomBuilder
from dualis.world.colliders import solids_for
from dualis.world.entity import Entity, EntityManager
from dualis.world.phenomenon import TestPhenomenon
from dualis.world.room import RoomManager
from dualis.world.test_transformable import TestTransformable
from dualis.world.transit import entry_for

ROOMS_DIR = ROOT / "data" / "rooms"
BLUEPRINTS_DIR = ROOT / "data" / "blueprints"
PATTERNS_DIR = ROOT / "data" / "patterns"
OUT_DIR = ROOT / "captures"


def build_scene(rid, park=None, solve=False):
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
    blueprints = {}
    for path in sorted(BLUEPRINTS_DIR.glob("*.json")):
        blueprint = load_blueprint(path, PATTERNS_DIR)
        blueprints[blueprint.rid] = blueprint
        built = builder.build(blueprint)
        for actor in built.actors:
            entities.register(actor)
        runtimes.add_room(blueprint, built.actors)
    rooms.enter(rid)
    uno, dos = entities.get("UNO"), entities.get("DOS")
    room_observe = ObserveSystem(runtimes.registry_for(rid), bus)
    if solve:
        room_observe.request("UNO")
        room_observe.update(0.1)
    if park is not None:
        uno.x, uno.y = park[0]
        dos.x, dos.y = park[1]
    link.update(0.016)
    runtimes.update(0.1, rid)
    patterns = {k: v.pattern for k, v in blueprints.items()}
    manager = SceneManager(bus)
    scene = RoomScene(rooms, entities, link, room_observe, transform, testbox,
                      puzzle, None, bus, runtimes=runtimes, patterns=patterns)
    manager.set_scene(scene)
    manager.update(0.1)
    return scene


def _entry(rid, from_rid):
    blueprint = load_blueprint(BLUEPRINTS_DIR / (rid.lower() + ".json"), PATTERNS_DIR)
    solids = solids_for(rid, blueprint.exit_rect)
    return entry_for(blueprint.exit_rect, solids, from_rid)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    renderer = RendererISO()
    shots = (
        ("f24_exit_vest01.png", "VEST_01", ((550.0, 280.0), (550.0, 280.0)), True),
        ("f24_entry_vest02.png", "VEST_02", _entry("VEST_02", "VEST_01"), False),
        ("f24_entry_bib01.png", "BIB_01", _entry("BIB_01", "VEST_14"), False),
    )
    for name, rid, park, solve in shots:
        scene = build_scene(rid, park, solve)
        canvas = pygame.Surface(config.LOGICAL_SIZE)
        for _ in range(5):
            renderer.render_world(scene, canvas)
        renderer.render_hud(scene, canvas, 60.0)
        big = pygame.transform.scale(canvas, (1280, 720))
        path = OUT_DIR / name
        pygame.image.save(big, str(path))
        print("captura", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
