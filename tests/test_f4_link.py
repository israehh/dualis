"""Tests F4: vínculo medido, estable y comunicado. Sin gameplay."""
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
from dualis.systems.link import LinkSystem
from dualis.world.entity import Entity, EntityManager
from dualis.world.room import RoomManager

ROOMS_DIR = Path(__file__).resolve().parents[1] / "data" / "rooms"


def _duo(x1=0.0, y1=0.0, x2=100.0, y2=0.0):
    entities = EntityManager()
    entities.register(Entity("UNO", x=x1, y=y1))
    entities.register(Entity("DOS", x=x2, y=y2))
    return entities


def test_calculo_distancia():
    link = LinkSystem(_duo(0.0, 0.0, 30.0, 40.0))
    assert abs(link.measure() - 50.0) < 1e-9


def test_cambio_estados():
    link = LinkSystem(_duo(), tension_at=240.0, limit_at=320.0)
    assert link.update(0.016) == LinkSystem.CONNECTED
    link.entities.get("DOS").move(160.0, 0.0)
    assert link.update(0.016) == LinkSystem.TENSION
    link.entities.get("DOS").move(100.0, 0.0)
    assert link.update(0.016) == LinkSystem.LIMIT


def test_histeresis_estable():
    link = LinkSystem(_duo(0.0, 0.0, 235.0, 0.0), tension_at=240.0, limit_at=320.0,
                      release_tension=210.0, release_limit=290.0)
    assert link.update(0.016) == LinkSystem.CONNECTED
    link.entities.get("DOS").move(10.0, 0.0)
    assert link.update(0.016) == LinkSystem.TENSION
    link.entities.get("DOS").move(-10.0, 0.0)
    assert link.update(0.016) == LinkSystem.TENSION
    link.entities.get("DOS").move(-30.0, 0.0)
    assert link.update(0.016) == LinkSystem.CONNECTED


def test_emision_eventos():
    bus = EventBus()
    link = LinkSystem(_duo(), bus=bus)
    link.update(0.016)
    assert "LINK_CONNECTED" not in bus.log
    link.entities.get("DOS").move(150.0, 0.0)
    link.update(0.016)
    assert "LINK_TENSION" in bus.log
    link.entities.get("DOS").move(100.0, 0.0)
    link.update(0.016)
    assert "LINK_LIMIT" in bus.log


def test_recuperacion_al_acercarse():
    bus = EventBus()
    link = LinkSystem(_duo(0.0, 0.0, 350.0, 0.0), bus=bus)
    assert link.update(0.016) == LinkSystem.LIMIT
    link.entities.get("DOS").move(-70.0, 0.0)
    assert link.update(0.016) == LinkSystem.TENSION
    link.entities.get("DOS").move(-120.0, 0.0)
    assert link.update(0.016) == LinkSystem.CONNECTED
    assert "LINK_CONNECTED" in bus.log


def test_vinculo_no_mueve():
    entities = _duo(10.0, 20.0, 60.0, 20.0)
    link = LinkSystem(entities)
    link.update(0.1)
    assert (entities.get("UNO").x, entities.get("UNO").y) == (10.0, 20.0)
    assert (entities.get("DOS").x, entities.get("DOS").y) == (60.0, 20.0)


def test_escena_muestra_vinculo():
    pygame.init()
    try:
        rooms = RoomManager(EventBus())
        rooms.load_directory(ROOMS_DIR)
        rooms.enter("ROOM_A")
        entities = _duo(240.0, 200.0, 400.0, 200.0)
        link = LinkSystem(entities)
        link.update(0.016)
        manager = SceneManager(EventBus())
        manager.set_scene(RoomScene(rooms, entities, link))
        surface = pygame.Surface((640, 360))
        manager.update(0.1)
        link.update(0.1)
        manager.render(surface, fps=60.0)
        assert link.state in ("CONNECTED", "TENSION", "LIMIT")
    finally:
        pygame.quit()


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)
