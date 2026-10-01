"""Tests F7: el primer puzzle encadena observar → transformar → avanzar."""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pygame

from dualis.core.bus import EventBus
from dualis.core.scene import SceneManager
from dualis.scenes.room_scene import RoomScene
from dualis.systems.observable import ObservableRegistry
from dualis.systems.observe import ObserveSystem
from dualis.systems.slice_puzzle import EXIT_RECT, SlicePuzzle
from dualis.systems.transform import TransformSystem
from dualis.systems.transformable import TransformableRegistry
from dualis.world.entity import Entity, EntityManager
from dualis.world.phenomenon import TestPhenomenon
from dualis.world.room import RoomManager
from dualis.world.test_transformable import TestTransformable

ROOMS_DIR = Path(__file__).resolve().parents[1] / "data" / "rooms"


def _slice(bus=None):
    bus = bus if bus is not None else EventBus()
    entities = EntityManager()
    uno = entities.register(Entity("UNO", x=120.0, y=280.0))
    dos = entities.register(Entity("DOS", x=220.0, y=280.0))
    registry = ObservableRegistry()
    phenomenon = registry.register(TestPhenomenon())
    observe = ObserveSystem(registry, bus)
    tregistry = TransformableRegistry()
    testbox = tregistry.register(TestTransformable())
    transform = TransformSystem(bus)
    puzzle = SlicePuzzle(transform, phenomenon, testbox, uno, dos, bus)
    return observe, transform, phenomenon, testbox, uno, dos, puzzle, bus


def _exit_center():
    rx, ry, rw, rh = EXIT_RECT
    return rx + rw / 2.0, ry + rh / 2.0


def test_congelacion_requerida_para_transformar():
    observe, transform, phenomenon, testbox, uno, dos, puzzle, bus = _slice()
    assert puzzle.try_transform("DOS") is False
    assert "SLICE_DENIED" in bus.log
    assert testbox.is_transformed is False


def test_transformacion_tras_congelar():
    observe, transform, phenomenon, testbox, uno, dos, puzzle, bus = _slice()
    observe.request("UNO")
    observe.update(0.1)
    puzzle.update(0.1)
    assert puzzle.state == SlicePuzzle.STILLED
    assert puzzle.try_transform("DOS") is True
    assert testbox.is_transformed is True
    assert puzzle.exit_open is True


def test_desbloqueo_ruta():
    observe, transform, phenomenon, testbox, uno, dos, puzzle, bus = _slice()
    cx, cy = _exit_center()
    uno.x, uno.y = cx, cy
    dos.x, dos.y = cx, cy
    puzzle.update(0.1)
    assert puzzle.state != SlicePuzzle.SOLVED
    observe.request("UNO")
    observe.update(0.1)
    puzzle.update(0.1)
    puzzle.try_transform("DOS")
    puzzle.update(0.1)
    assert puzzle.state == SlicePuzzle.SOLVED
    assert "SLICE_SOLVED" in bus.log


def test_condicion_exito_exige_duo():
    observe, transform, phenomenon, testbox, uno, dos, puzzle, bus = _slice()
    observe.request("UNO")
    observe.update(0.1)
    puzzle.update(0.1)
    puzzle.try_transform("DOS")
    cx, cy = _exit_center()
    uno.x, uno.y = cx, cy
    puzzle.update(0.1)
    assert puzzle.state == SlicePuzzle.BRIDGED
    dos.x, dos.y = cx, cy
    puzzle.update(0.1)
    assert puzzle.state == SlicePuzzle.SOLVED


def test_gramatica_completa_en_orden():
    observe, transform, phenomenon, testbox, uno, dos, puzzle, bus = _slice()
    assert puzzle.state == SlicePuzzle.SEALED
    observe.request("UNO")
    observe.update(0.1)
    puzzle.update(0.1)
    assert puzzle.state == SlicePuzzle.STILLED
    assert "SLICE_STILLED" in bus.log
    puzzle.try_transform("DOS")
    assert puzzle.state == SlicePuzzle.BRIDGED
    assert "SLICE_BRIDGED" in bus.log
    cx, cy = _exit_center()
    uno.x, uno.y = cx, cy
    dos.x, dos.y = cx, cy
    puzzle.update(0.1)
    assert puzzle.state == SlicePuzzle.SOLVED


def test_room_slice_existe_y_enlaza():
    rooms = RoomManager(EventBus())
    rooms.load_directory(ROOMS_DIR)
    rooms.enter("ROOM_SLICE")
    assert rooms.current().definition.rid == "ROOM_SLICE"
    assert rooms.definitions["ROOM_SLICE"].enlaces == ("ROOM_A",)
    assert rooms.definitions["ROOM_A"].enlaces == ("ROOM_B",)
    assert rooms.definitions["ROOM_B"].enlaces == ("ROOM_A",)


def test_escena_dibuja_puzzle():
    pygame.init()
    try:
        rooms = RoomManager(EventBus())
        rooms.load_directory(ROOMS_DIR)
        rooms.enter("ROOM_SLICE")
        observe, transform, phenomenon, testbox, uno, dos, puzzle, bus = _slice()
        entities = EntityManager()
        entities.register(uno)
        entities.register(dos)
        manager = SceneManager(EventBus())
        manager.set_scene(RoomScene(rooms, entities, None, observe, transform, testbox, puzzle))
        surface = pygame.Surface((640, 360))
        manager.update(0.1)
        manager.render(surface, fps=60.0)
        observe.request("UNO")
        observe.update(0.1)
        puzzle.update(0.1)
        puzzle.try_transform("DOS")
        manager.update(0.1)
        manager.render(surface, fps=60.0)
        assert puzzle.state == SlicePuzzle.BRIDGED
    finally:
        pygame.quit()


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)
