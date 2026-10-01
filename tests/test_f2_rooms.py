"""Tests F2: carga, validación, navegación, bidireccionalidad e inexistente."""
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
from dualis.world.room import RoomManager, load_definition, validate_definition

ROOMS_DIR = Path(__file__).resolve().parents[1] / "data" / "rooms"


def _manager():
    rooms = RoomManager(EventBus())
    rooms.load_directory(ROOMS_DIR)
    return rooms


def test_carga_room():
    definition = load_definition(ROOMS_DIR / "room_a.json")
    assert definition.rid == "ROOM_A"
    assert definition.nombre
    assert "ROOM_B" in definition.enlaces


def test_validacion_room():
    assert validate_definition({"id": "X", "nombre": "N", "enlaces": ["Y"]}) == []
    bad = validate_definition({"nombre": "Sin id", "enlaces": []})
    assert "sin-id" in bad
    assert "sin-enlaces" in bad


def test_navegacion():
    rooms = _manager()
    rooms.enter("ROOM_A")
    assert rooms.current().definition.rid == "ROOM_A"
    rooms.enter("ROOM_B")
    assert rooms.current().definition.rid == "ROOM_B"
    assert rooms.neighbours() == ("ROOM_A",)


def test_enlace_bidireccional():
    rooms = _manager()
    assert "ROOM_B" in rooms.definitions["ROOM_A"].enlaces
    assert "ROOM_A" in rooms.definitions["ROOM_B"].enlaces


def test_room_inexistente():
    rooms = _manager()
    try:
        rooms.enter("ROOM_Z")
    except KeyError:
        return
    raise AssertionError("debió fallar con room inexistente")


def test_room_scene_muestra_y_cambia():
    pygame.init()
    try:
        rooms = _manager()
        rooms.enter("ROOM_A")
        manager = SceneManager(EventBus())
        scene = RoomScene(rooms)
        manager.set_scene(scene)
        surface = pygame.Surface((640, 360))
        manager.update(0.1)
        manager.render(surface, fps=60.0)
        rooms.enter("ROOM_B")
        manager.update(0.1)
        manager.render(surface, fps=60.0)
        assert rooms.current().definition.rid == "ROOM_B"
    finally:
        pygame.quit()


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)
