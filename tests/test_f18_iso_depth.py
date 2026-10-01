"""Tests F18: altura visual, sombras, orden de profundidad y suelo 32x16."""
import os
import sys
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pygame

from dualis import config
from dualis.core.bus import EventBus
from dualis.core.scene import SceneManager
from dualis.presentation.renderer import Renderer2D
from dualis.presentation.renderer_iso import RendererISO
from dualis.presentation.viewport import present
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

ROOT = Path(__file__).resolve().parents[1]
ROOMS_DIR = ROOT / "data" / "rooms"
BLUEPRINTS_DIR = ROOT / "data" / "blueprints"
PATTERNS_DIR = ROOT / "data" / "patterns"


class HeightRuntime:
    def __init__(self, state="LOCKED", exit_rect=(500, 240, 100, 80), room_id="ROOM_X"):
        self.state = state
        self.exit_rect = exit_rect
        self.room_id = room_id


class _StubRuntimes:
    def __init__(self, runtime=None, ids=()):
        self._runtime = runtime
        self._ids = set(ids)

    def runtime_for(self, rid):
        return self._runtime

    def active_ids(self, rid):
        return set(("UNO", "DOS")) | set(self._ids)


def _scene(rid="ROOM_SLICE", mount=None):
    pygame.init()
    bus = EventBus()
    rooms = RoomManager(bus)
    rooms.load_directory(ROOMS_DIR)
    entities = EntityManager()
    entities.register(Entity("UNO", x=120.0, y=280.0))
    entities.register(Entity("DOS", x=220.0, y=280.0))
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
    runtimes = None
    try:
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
    except ImportError:
        pass
    rooms.enter(rid)
    manager = SceneManager(bus)
    scene = RoomScene(rooms, entities, link, observe, transform, testbox,
                      puzzle, mount, bus, runtimes=runtimes)
    manager.set_scene(scene)
    return manager, scene


def _has_color(surface, color, box=None):
    x0, y0 = (0, 0) if box is None else (box[0], box[1])
    x1, y1 = surface.get_size() if box is None else (box[0] + box[2], box[1] + box[3])
    for x in range(max(0, x0), min(x1, surface.get_width())):
        for y in range(max(0, y0), min(y1, surface.get_height())):
            if surface.get_at((x, y))[:3] == color:
                return True
    return False


def test_world_to_iso_acepta_z():
    renderer = RendererISO()
    base = renderer.world_to_iso(100, 100)
    assert renderer.world_to_iso(100, 100, 0.0) == base
    lifted = renderer.world_to_iso(100, 100, 44.0)
    assert lifted[0] == base[0]
    assert lifted[1] < base[1]
    assert abs((base[1] - lifted[1]) - 44.0 * renderer._scale) < 1e-6


def test_mounted_uno_por_encima():
    _, scene = _scene("ROOM_SLICE")
    scene.mount = SimpleNamespace(mounted=True)
    renderer = RendererISO()
    uno = scene.entities.get("UNO")
    dos = scene.entities.get("DOS")
    assert renderer._uno_z(scene) == 44.0
    px_uno = renderer._point(uno.x, uno.y, 44.0)
    px_dos = renderer._point(dos.x, dos.y, 0.0)
    assert px_uno[1] < px_dos[1]
    canvas = pygame.Surface(config.LOGICAL_SIZE)
    renderer.render_world(scene, canvas)


def test_sombras_se_generan():
    renderer = RendererISO()
    canvas = pygame.Surface(config.LOGICAL_SIZE)
    canvas.fill(config.BACKGROUND)
    before = pygame.image.tobytes(canvas, "RGB")
    renderer.draw_shadow(canvas, 320, 180, 14, 44.0)
    assert pygame.image.tobytes(canvas, "RGB") != before
    assert _has_color(canvas, (0, 0, 0), (300, 160, 60, 50))
    plain = pygame.Surface(config.LOGICAL_SIZE)
    plain.fill(config.BACKGROUND)
    renderer.draw_shadow(plain, 320, 180, 14, 0.0)
    assert pygame.image.tobytes(plain, "RGB") == before


def test_sort_profundidad_estable():
    _, scene = _scene("ROOM_SLICE")
    scene.mount = SimpleNamespace(mounted=True)
    renderer = RendererISO()
    renderer.fit(*renderer.logical)
    items = renderer._collect_renderables(scene)
    keys = [key for key, _ in items]
    assert keys == sorted(keys)
    assert 444.0 in keys
    assert 500.0 in keys
    canvas = pygame.Surface(config.LOGICAL_SIZE)
    renderer.render_world(scene, canvas)


def test_grid_visible():
    _, scene = _scene("ROOM_SLICE")
    renderer = RendererISO()
    assert renderer.show_floor_grid is True
    canvas = pygame.Surface(config.LOGICAL_SIZE)
    renderer.render_world(scene, canvas)
    assert _has_color(canvas, (40, 40, 56))
    quiet = RendererISO(show_floor_grid=False)
    canvas2 = pygame.Surface(config.LOGICAL_SIZE)
    quiet.render_world(scene, canvas2)
    assert not _has_color(canvas2, (40, 40, 56))


def test_salida_pedestal_height():
    _, scene = _scene("VEST_01")
    renderer = RendererISO()
    canvas = pygame.Surface(config.LOGICAL_SIZE)
    scene.runtimes = _StubRuntimes(HeightRuntime(state="READY",
                                                 exit_rect=(500, 240, 100, 80)))
    renderer.render_world(scene, canvas)
    assert _has_color(canvas, (96, 84, 52), (340, 250, 130, 70))
    assert _has_color(canvas, (220, 170, 80), (340, 240, 130, 90))


def test_renderer2d_intacto():
    manager, scene = _scene("ROOM_SLICE")
    renderer = Renderer2D()
    canvas = pygame.Surface(config.LOGICAL_SIZE)
    manager.update(0.1)
    renderer.render(scene, canvas, fps=60.0)


def test_iso_render_sin_excepciones():
    renderer = RendererISO()
    for rid in ("ROOM_SLICE", "VEST_01", "ROOM_01"):
        manager, scene = _scene(rid)
        canvas = pygame.Surface(config.LOGICAL_SIZE)
        manager.update(0.1)
        renderer.render(scene, canvas, fps=60.0)
    window = pygame.display.set_mode((800, 450))
    present(window, canvas)


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)
