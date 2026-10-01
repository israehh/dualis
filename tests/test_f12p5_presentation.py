"""Tests F12.5: canvas lógico, escalado, HUD multilínea y salidas visibles."""
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
from dualis.presentation.viewport import compute_view, present
from dualis.scenes.room_scene import RoomScene
from dualis.systems.link import LinkSystem
from dualis.systems.observable import ObservableRegistry
from dualis.systems.observe import ObserveSystem
from dualis.systems.slice_puzzle import EXIT_RECT, SlicePuzzle
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
SIZES = [(640, 360), (1280, 720), (1920, 1080)]


def _scene(rid="ROOM_SLICE"):
    pygame.init()
    bus = EventBus()
    rooms = RoomManager(bus)
    rooms.load_directory(ROOMS_DIR)
    entities = EntityManager()
    uno = entities.register(Entity("UNO", x=120.0, y=280.0))
    dos = entities.register(Entity("DOS", x=220.0, y=280.0))
    registry = ObservableRegistry()
    phenomenon = registry.register(TestPhenomenon())
    entities.register(phenomenon)
    observe = ObserveSystem(registry, bus)
    tregistry = TransformableRegistry()
    testbox = tregistry.register(TestTransformable())
    entities.register(testbox)
    transform = TransformSystem(bus)
    link = LinkSystem(entities, bus)
    puzzle = SlicePuzzle(transform, phenomenon, testbox, uno, dos, bus)
    builder = RoomBuilder(rooms)
    runtimes = None
    try:
        from dualis.systems.room_runtime import RoomRuntimeManager
        from dualis.systems.cooperation import CooperationSystem, MountAction
        runtimes = RoomRuntimeManager(bus, transform, mount=None, uno=uno, dos=dos)
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


def test_logical_canvas_fija():
    assert config.LOGICAL_SIZE == (640, 360)
    assert config.WINDOW_SIZE == (1280, 720)
    assert config.WINDOW_RESIZABLE is True


def test_compute_view_exactas():
    assert compute_view(640, 360) == (1.0, 0, 0, 640, 360)
    assert compute_view(1280, 720) == (2.0, 0, 0, 1280, 720)
    assert compute_view(1920, 1080) == (3.0, 0, 0, 1920, 1080)


def test_compute_view_letterbox():
    scale, ox, oy, dw, dh = compute_view(1000, 700)
    assert dw <= 1000 and dh <= 700
    assert ox == (1000 - dw) // 2 and oy == (700 - dh) // 2
    assert dw == 1000 and dh == 562


def test_present_tres_tamanos():
    pygame.init()
    canvas = pygame.Surface(config.LOGICAL_SIZE)
    canvas.fill(config.BACKGROUND)
    for size in SIZES:
        window = pygame.display.set_mode(size)
        scale, ox, oy, dw, dh = present(window, canvas)
        assert dw <= size[0] and dh <= size[1]
        assert 0 <= ox <= size[0] and 0 <= oy <= size[1]


def test_overlay_multilinea_cabe():
    manager, scene = _scene()
    _, debug_font = scene._fonts()
    items = ["UNO WASD (120,280)", "DOS flechas (220,280)",
             "vinculo CONNECTED d=100 max=320", "observar Q: LISTO",
             "transformar E: READY", "objeto: original", "corte: SEALED",
             "sala: LOCKED"]
    lines = scene._pack_lines(items, debug_font, 640 - 2 * config.HUD_MARGIN)
    assert len(lines) > 1
    for line in lines:
        assert debug_font.size(line)[0] <= 640 - 2 * config.HUD_MARGIN


def test_render_tres_tamanos_sin_recorte():
    manager, scene = _scene("ROOM_01")
    canvas = pygame.Surface(config.LOGICAL_SIZE)
    manager.update(0.1)
    manager.render(canvas, fps=60.0)
    runtime = scene._active_runtime()
    assert runtime is not None
    x, y, w, h = runtime.exit_rect
    assert 0 <= x and 0 <= y and x + w <= 640 and y + h <= 360
    for size in SIZES:
        window = pygame.display.set_mode(size)
        scale, ox, oy, dw, dh = present(window, canvas)
        for px, py in ((x, y), (x + w, y + h)):
            sx, sy = ox + px * scale, oy + py * scale
            assert 0 <= sx <= size[0] and 0 <= sy <= size[1]


def test_salida_slice_visible_tres_tamanos():
    manager, scene = _scene("ROOM_SLICE")
    canvas = pygame.Surface(config.LOGICAL_SIZE)
    manager.update(0.1)
    manager.render(canvas, fps=60.0)
    x, y, w, h = EXIT_RECT
    for size in SIZES:
        window = pygame.display.set_mode(size)
        scale, ox, oy, _, _ = present(window, canvas)
        for px, py in ((x, y), (x + w, y + h)):
            sx, sy = ox + px * scale, oy + py * scale
            assert 0 <= sx <= size[0] and 0 <= sy <= size[1]


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)
