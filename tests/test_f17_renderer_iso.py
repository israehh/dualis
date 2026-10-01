"""Tests F17: renderer isométrico con la misma interfaz que Renderer2D."""
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


class _StubRuntime:
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


def _scene(rid="ROOM_SLICE"):
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
                      puzzle, None, bus, runtimes=runtimes)
    manager.set_scene(scene)
    return manager, scene


def _has_color(surface, color, box):
    x0, y0, w, h = box
    for x in range(x0, min(x0 + w, surface.get_width())):
        for y in range(y0, min(y0 + h, surface.get_height())):
            if surface.get_at((x, y))[:3] == color:
                return True
    return False


def test_instancia():
    renderer = RendererISO()
    assert renderer.name == "iso"
    assert renderer.debug_iso_grid is True
    for method in ("render_world", "render_hud", "render"):
        assert callable(getattr(renderer, method))
        assert callable(getattr(Renderer2D(), method))


def test_render_no_excepciones():
    renderer = RendererISO()
    for rid in ("ROOM_SLICE", "VEST_01", "ROOM_01"):
        manager, scene = _scene(rid)
        canvas = pygame.Surface(config.LOGICAL_SIZE)
        manager.update(0.1)
        renderer.render(scene, canvas, fps=60.0)


def test_world_to_iso_coherente():
    renderer = RendererISO()
    assert RendererISO.raw(0, 0) == (0, 0)
    assert RendererISO.raw(640, 0) == (640, 320)
    scale, ox, oy = renderer.fit(640, 360)[:3]
    assert abs(scale - 0.64) < 1e-9
    corners = [renderer.world_to_iso(x, y) for x, y in
               ((0, 0), (640, 0), (640, 360), (0, 360))]
    for sx, sy in corners:
        assert 0 <= sx <= 640, (sx, sy)
        assert 0 <= sy <= 360, (sx, sy)
    assert renderer.world_to_iso(0, 0, scale=2.0, ox=10.0, oy=5.0) == (10.0, 5.0)


def test_resize_sigue_funcionando():
    _, scene = _scene("VEST_01")
    renderer = RendererISO()
    canvas = pygame.Surface(config.LOGICAL_SIZE)
    renderer.render(scene, canvas, fps=60.0)
    for size in ((800, 450), (1920, 1080)):
        window = pygame.display.set_mode(size)
        scale, ox, oy, dw, dh = present(window, canvas)
        assert dw <= size[0] and dh <= size[1]


def test_hud_visible():
    _, scene = _scene("ROOM_SLICE")
    renderer = RendererISO()
    canvas = pygame.Surface(config.LOGICAL_SIZE)
    renderer.render(scene, canvas, fps=60.0)
    assert _has_color(canvas, (210, 180, 120), (10, 8, 200, 60))


def test_salida_iso_por_estado():
    _, scene = _scene("VEST_01")
    renderer = RendererISO()
    for state, expected in (("LOCKED", (80, 180, 100)),
                            ("READY", (220, 170, 80)),
                            ("COMPLETED", (90, 140, 230))):
        canvas = pygame.Surface(config.LOGICAL_SIZE)
        scene.runtimes = _StubRuntimes(_StubRuntime(state=state))
        renderer.render_world(scene, canvas)
        x, y = renderer.world_to_iso(550, 240)
        found = any(canvas.get_at((int(x) + dx, int(y) + dy))[:3] == expected
                    for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                    if 0 <= int(x) + dx < 640 and 0 <= int(y) + dy < 360)
        assert found, state


def test_renderer2d_sigue_funcionando():
    manager, scene = _scene("ROOM_SLICE")
    renderer = Renderer2D()
    canvas = pygame.Surface(config.LOGICAL_SIZE)
    manager.update(0.1)
    renderer.render(scene, canvas, fps=60.0)


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)
