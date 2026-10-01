"""Tests F13.5: HUD por bloques, overlay debug, salidas y separación de render."""
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
from dualis.presentation.renderer import Renderer2D, draw_rect_outline
from dualis.presentation.viewport import compute_view, present
from dualis.scenes.room_scene import (
    RoomScene,
    pattern_of,
    region_of,
)
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
SIZES = [(640, 360), (800, 450), (1280, 720), (1600, 900), (1920, 1080)]


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


def _scene(rid="ROOM_SLICE", patterns=None, debug=True):
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
                      puzzle, None, bus, runtimes=runtimes,
                      patterns=patterns, debug=debug)
    manager.set_scene(scene)
    return manager, scene


def test_region_of():
    assert region_of("VEST_01") == "El Vestíbulo"
    assert region_of("VEST_14") == "El Vestíbulo"
    assert region_of("ROOM_SLICE") == "Umbral"
    assert region_of("ROOM_01") == "Umbral"
    assert region_of("ZONE_03") == "Umbral"
    assert region_of(None) == "Umbral"


def test_pattern_of():
    assert pattern_of(None) == "—"
    assert pattern_of(None, {"ROOM_01": "PATTERN_HEIGHT"}) == "—"
    assert pattern_of(_StubRuntime(), {"ROOM_X": "PATTERN_HEIGHT"}) == "PATTERN_HEIGHT"
    assert pattern_of(_StubRuntime()) == "—"


def test_salida_estado_color():
    _, scene = _scene("VEST_01")
    for state, expected in (("LOCKED", (200, 110, 100)),
                            ("READY", (120, 170, 130)),
                            ("COMPLETED", (150, 220, 160))):
        canvas = pygame.Surface(config.LOGICAL_SIZE)
        canvas.fill(config.BACKGROUND)
        scene.runtimes = _StubRuntimes(_StubRuntime(state=state, exit_rect=(500, 240, 100, 80)))
        scene._draw_exit(canvas)
        assert canvas.get_at((550, 241))[:3] == expected, state


def test_salida_siempre_dibujada():
    for rid in ("VEST_01", "VEST_14", "ROOM_01", "ROOM_SLICE"):
        manager, scene = _scene(rid)
        canvas = pygame.Surface(config.LOGICAL_SIZE)
        manager.update(0.1)
        manager.render(canvas, fps=60.0)
        assert scene._active_runtime() is not None or rid == "ROOM_SLICE"


def test_debug_toggle():
    manager, scene = _scene("VEST_01")
    assert scene.debug is True
    canvas = pygame.Surface(config.LOGICAL_SIZE)
    manager.update(0.1)
    manager.render(canvas, fps=60.0)
    scene.debug = not scene.debug
    assert scene.debug is False
    manager.render(canvas, fps=60.0)


def test_renderer_split_equivale():
    manager, scene = _scene("VEST_05")
    from dualis.presentation.renderer import Renderer2D
    renderer = Renderer2D()
    assert renderer.name == "2d"
    manager.update(0.1)
    full = pygame.Surface(config.LOGICAL_SIZE)
    split = pygame.Surface(config.LOGICAL_SIZE)
    scene.render(full, fps=60.0)
    renderer.render_world(scene, split)
    renderer.render_hud(scene, split, fps=60.0)
    assert pygame.image.tobytes(full, "RGB") == pygame.image.tobytes(split, "RGB")


def test_hud_bloques_dentro():
    for rid in ("VEST_01", "VEST_14", "ROOM_SLICE", "ROOM_A"):
        manager, scene = _scene(rid)
        canvas = pygame.Surface(config.LOGICAL_SIZE)
        manager.update(0.1)
        manager.render(canvas, fps=60.0)


def test_present_tamanos_f13p5():
    pygame.init()
    canvas = pygame.Surface(config.LOGICAL_SIZE)
    canvas.fill(config.BACKGROUND)
    for size in SIZES:
        window = pygame.display.set_mode(size)
        scale, ox, oy, dw, dh = present(window, canvas)
        assert dw <= size[0] and dh <= size[1]
        assert 0 <= ox <= size[0] and 0 <= oy <= size[1]
        assert abs(dw / 640.0 - dh / 360.0) < 0.01


def test_render_escalado_sin_deformar():
    _, scene = _scene("VEST_14")
    canvas = pygame.Surface(config.LOGICAL_SIZE)
    scene.render(canvas, fps=60.0)
    window = pygame.display.set_mode((1600, 900))
    scale, ox, oy, dw, dh = present(window, canvas)
    assert (dw, dh) == (1600, 900)
    window = pygame.display.set_mode((800, 450))
    scale, ox, oy, dw, dh = present(window, canvas)
    assert (dw, dh) == (800, 450)


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)
