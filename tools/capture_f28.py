"""Captura F28: llegada a R4_01 desde TAL_09 (bisagra R3→R4 abierta).

Render intacto; solo documenta la entrada determinista del tránsito
integrado: el dúo aparece en el par de entry_for(..., "TAL_09"), fuera
de la salida y sin sólidos, con la room aún por resolver.
"""
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
from dualis.systems.cooperation import MountAction
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
R4_DIR = ROOT / "data" / "r4_rooms"
PATTERNS_DIR = ROOT / "data" / "patterns"
OUT_DIR = ROOT / "captures"


def build_scene():
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
    mount = MountAction(uno, dos, bus)
    puzzle = SlicePuzzle(transform, phenomenon, testbox, uno, dos, bus)
    builder = RoomBuilder(rooms)
    from dualis.systems.room_runtime import RoomRuntimeManager
    runtimes = RoomRuntimeManager(bus, transform, mount, uno, dos)
    runtimes.register_actors("ROOM_SLICE", [phenomenon, testbox])
    blueprints = {}
    for path in sorted(R4_DIR.glob("*.json")):
        blueprint = load_blueprint(path, PATTERNS_DIR)
        blueprints[blueprint.rid] = blueprint
        built = builder.build(blueprint)
        for actor in built.actors:
            entities.register(actor)
        runtimes.add_room(blueprint, built.actors)
    rooms.enter("R4_01")
    runtime = runtimes.runtime_for("R4_01")
    (ux, uy), (dx, dy) = entry_for(tuple(runtime.exit_rect),
                                   solids_for("R4_01", tuple(runtime.exit_rect)),
                                   "TAL_09")
    uno.x, uno.y = ux, uy
    dos.x, dos.y = dx, dy
    room_observe = ObserveSystem(runtimes.registry_for("R4_01"), bus)
    link.update(0.016)
    runtimes.update(0.1, "R4_01")
    assert runtime.state != "COMPLETED"
    patterns = {k: v.pattern for k, v in blueprints.items()}
    manager = SceneManager(bus)
    scene = RoomScene(rooms, entities, link, room_observe, transform, testbox,
                      puzzle, mount, bus, runtimes=runtimes, patterns=patterns)
    manager.set_scene(scene)
    manager.update(0.1)
    return scene


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    renderer = RendererISO()
    scene = build_scene()
    canvas = pygame.Surface(config.LOGICAL_SIZE)
    for _ in range(5):
        renderer.render_world(scene, canvas)
    renderer.render_hud(scene, canvas, 60.0)
    big = pygame.transform.scale(canvas, (1280, 720))
    path = OUT_DIR / "f28_tal09_r401.png"
    pygame.image.save(big, str(path))
    print("captura", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
