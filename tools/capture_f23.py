"""Capturas F23: LNK_01..LNK_04. Render intacto; solo muestra el vínculo jugable."""
import json
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
LINK_ROOMS_DIR = ROOT / "data" / "link_rooms"
PATTERNS_DIR = ROOT / "data" / "patterns"
OUT_DIR = ROOT / "captures"

PARKS = {
    # rid: (uno_xy, dos_xy, transformar_tras_observar)
    "LNK_01": ((320.0, 180.0), (320.0, 180.0), False),  # CONNECTED + COMPLETED
    "LNK_02": ((180.0, 180.0), (440.0, 180.0), False),  # TENSION + COMPLETED
    "LNK_03": ((60.0, 100.0), (410.0, 100.0), False),  # LIMIT rechaza (READY)
    "LNK_04": ((510.0, 260.0), (510.0, 260.0), True),  # DENIED superado + COMPLETED
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
    puzzle = SlicePuzzle(transform, phenomenon, testbox,
                         entities.get("UNO"), entities.get("DOS"), bus)
    builder = RoomBuilder(rooms)
    from dualis.systems.room_runtime import RoomRuntimeManager
    runtimes = RoomRuntimeManager(bus, transform, mount=None,
                                  uno=entities.get("UNO"), dos=entities.get("DOS"))
    runtimes.register_actors("ROOM_SLICE", [phenomenon, testbox])
    blueprints = {}
    for path in sorted(LINK_ROOMS_DIR.glob("*.json")):
        blueprint = load_blueprint(path, PATTERNS_DIR)
        blueprints[blueprint.rid] = blueprint
        built = builder.build(blueprint)
        for actor in built.actors:
            entities.register(actor)
        runtimes.add_room(blueprint, built.actors)
    rooms.enter(rid)
    uno_xy, dos_xy, do_transform = PARKS[rid]
    uno, dos = entities.get("UNO"), entities.get("DOS")
    room_observe = ObserveSystem(runtimes.registry_for(rid), bus)
    room_observe.request("UNO")
    room_observe.update(0.1)
    if do_transform:
        runtimes.try_transform(rid, "DOS")
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
    for rid in ("LNK_01", "LNK_02", "LNK_03", "LNK_04"):
        scene = build_scene(rid)
        canvas = pygame.Surface(config.LOGICAL_SIZE)
        for _ in range(5):
            renderer.render_world(scene, canvas)
        renderer.render_hud(scene, canvas, 60.0)
        big = pygame.transform.scale(canvas, (1280, 720))
        path = OUT_DIR / ("f23_%s.png" % rid.lower())
        pygame.image.save(big, str(path))
        print("captura", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
