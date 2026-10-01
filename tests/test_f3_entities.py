"""Tests F3: entidades UNO/DOS independientes en el EntityManager."""
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
from dualis.world.entity import Entity, EntityManager
from dualis.world.room import RoomManager

ROOMS_DIR = Path(__file__).resolve().parents[1] / "data" / "rooms"


def test_creacion_entidad():
    entity = Entity("UNO", x=10.0, y=20.0)
    assert entity.id == "UNO"
    assert (entity.x, entity.y) == (10.0, 20.0)


def test_actualizacion():
    entity = Entity("UNO")
    entity.update(0.5)
    assert (entity.x, entity.y) == (0.0, 0.0)


def test_movimiento_uno():
    uno = Entity("UNO", x=100.0, y=100.0)
    uno.move(0.0, -24.0)
    assert uno.y == 76.0
    assert uno.x == 100.0


def test_movimiento_dos():
    dos = Entity("DOS", x=100.0, y=100.0)
    dos.move(24.0, 0.0)
    assert dos.x == 124.0
    assert dos.y == 100.0


def test_independencia_controles():
    manager = EntityManager()
    uno = manager.register(Entity("UNO", x=0.0, y=0.0))
    dos = manager.register(Entity("DOS", x=0.0, y=0.0))
    uno.move(5.0, 0.0)
    assert (dos.x, dos.y) == (0.0, 0.0)
    dos.move(0.0, 7.0)
    assert (uno.x, uno.y) == (5.0, 0.0)


def test_registro_en_manager():
    manager = EntityManager()
    manager.register(Entity("UNO"))
    manager.register(Entity("DOS"))
    assert manager.get("UNO").id == "UNO"
    assert manager.get("DOS").id == "DOS"
    assert len(manager.all()) == 2
    manager.update(0.1)
    pygame.init()
    try:
        surface = pygame.Surface((640, 360))
        manager.render(surface)
    finally:
        pygame.quit()


def test_entidades_permanecen_al_cambiar_room():
    rooms = RoomManager(EventBus())
    rooms.load_directory(ROOMS_DIR)
    rooms.enter("ROOM_A")
    entities = EntityManager()
    uno = entities.register(Entity("UNO", x=11.0, y=22.0))
    rooms.enter("ROOM_B")
    assert rooms.current().definition.rid == "ROOM_B"
    assert (uno.x, uno.y) == (11.0, 22.0)


def test_room_scene_integra_entidades():
    pygame.init()
    try:
        rooms = RoomManager(EventBus())
        rooms.load_directory(ROOMS_DIR)
        rooms.enter("ROOM_A")
        entities = EntityManager()
        entities.register(Entity("UNO", x=240.0, y=200.0))
        entities.register(Entity("DOS", x=400.0, y=200.0))
        manager = SceneManager(EventBus())
        scene = RoomScene(rooms, entities)
        manager.set_scene(scene)
        surface = pygame.Surface((640, 360))
        manager.update(0.1)
        manager.render(surface, fps=60.0)
    finally:
        pygame.quit()


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)
