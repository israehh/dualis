"""Capturas F26: R4_05..R4_08 resueltas. Render intacto; solo rooms nuevas."""
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
from dualis.world.entity import Entity, EntityManager
from dualis.world.phenomenon import TestPhenomenon
from dualis.world.room import RoomManager
from dualis.world.test_transformable import TestTransformable

ROOMS_DIR = ROOT / "data" / "rooms"
R4_DIR = ROOT / "data" / "r4_rooms"
PATTERNS_DIR = ROOT / "data" / "patterns"
OUT_DIR = ROOT / "captures"

PARKS = {
    "R4_05": ((170.0, 240.0), (430.0, 240.0), "observe"),  # TENSION dentro
    "R4_06": (None, None, "observe"),
    "R4_07": (None, None, "observe"),
    "R4_08": (None, None, "transform"),
}


def build_scene(rid):
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
    uno, dos = entities.get("UNO"), entities.get("DOS")
    puzzle = SlicePuzzle(transform, phenomenon, testbox, uno, dos, bus)
    builder = RoomBuilder(rooms)
    from dualis.systems.room_runtime import RoomRuntimeManager
    runtimes = RoomRuntimeManager(bus, transform, None, uno, dos)
    runtimes.register_actors("ROOM_SLICE", [phenomenon, testbox])
    blueprints = {}
    for path in sorted(R4_DIR.glob("*.json")):
        blueprint = load_blueprint(path, PATTERNS_DIR)
        blueprints[blueprint.rid] = blueprint
        built = builder.build(blueprint)
        for actor in built.actors:
            entities.register(actor)
        runtimes.add_room(blueprint, built.actors)
    rooms.enter(rid)
    runtime = runtimes.runtime_for(rid)
    ex, ey, ew, eh = runtime.exit_rect
    uno_xy, dos_xy, solve = PARKS[rid]
    room_observe = ObserveSystem(runtimes.registry_for(rid), bus)
    if solve in ("observe", "transform"):
        room_observe.request("UNO")
        room_observe.update(0.1)
    if solve == "transform":
        runtimes.try_transform(rid, "DOS")
    if uno_xy is None:
        uno.x, uno.y = ex + ew / 2.0, ey + eh / 2.0
        dos.x, dos.y = ex + ew / 2.0, ey + eh / 2.0
    else:
        uno.x, uno.y = uno_xy
        dos.x, dos.y = dos_xy
    link.update(0.016)
    runtimes.update(0.1, rid)
    patterns = {k: v.pattern for k, v in blueprints.items()}
    manager = SceneManager(bus)
    scene = RoomScene(rooms, entities, link, room_observe, transform, testbox,
                      puzzle, None, bus, runtimes=runtimes, patterns=patterns)
    manager.set_scene(scene)
    manager.update(0.1)
    return scene


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    renderer = RendererISO()
    for rid in ("R4_05", "R4_06", "R4_07", "R4_08"):
        scene = build_scene(rid)
        canvas = pygame.Surface(config.LOGICAL_SIZE)
        for _ in range(5):
            renderer.render_world(scene, canvas)
        renderer.render_hud(scene, canvas, 60.0)
        big = pygame.transform.scale(canvas, (1280, 720))
        path = OUT_DIR / ("f26_%s.png" % rid.lower())
        pygame.image.save(big, str(path))
        print("captura", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
