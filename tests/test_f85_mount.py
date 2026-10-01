"""Tests F8.5: montar es cooperación espacial real. Sin contenido nuevo."""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pygame

from dualis.core.bus import EventBus
from dualis.systems.link import LinkSystem
from dualis.systems.mount import MountSystem
from dualis.world.entity import Entity


def _duo(uno_xy=(100.0, 200.0), dos_xy=(120.0, 200.0), bus=None):
    uno = Entity("UNO", x=uno_xy[0], y=uno_xy[1])
    dos = Entity("DOS", x=dos_xy[0], y=dos_xy[1])
    return uno, dos, MountSystem(uno, dos, bus)


def test_solo_uno_monta():
    uno, dos, mount = _duo()
    assert mount.request("DOS") is False
    assert mount.mounted is False
    assert mount.request("UNO") is True
    assert mount.mounted is True


def test_requiere_proximidad():
    uno, dos, mount = _duo(uno_xy=(0.0, 0.0), dos_xy=(500.0, 0.0))
    assert mount.request("UNO") is False
    assert mount.mounted is False


def test_estados_duales():
    uno, dos, mount = _duo()
    assert (mount.uno_state, mount.dos_state) == ("NORMAL", "NORMAL")
    mount.request("UNO")
    assert (mount.uno_state, mount.dos_state) == ("MOUNTED", "CARRYING")


def test_acarreo_con_dos():
    uno, dos, mount = _duo(uno_xy=(100.0, 200.0), dos_xy=(120.0, 200.0))
    mount.request("UNO")
    dos.move(60.0, 30.0)
    mount.update(0.016)
    assert (uno.x, uno.y) == (dos.x, dos.y - MountSystem.LIFT)


def test_altura_adicional():
    uno, dos, mount = _duo(uno_xy=(120.0, 200.0), dos_xy=(120.0, 200.0))
    pie = mount.reach_top()
    mount.request("UNO")
    montado = mount.reach_top()
    assert pie - montado == MountSystem.LIFT


def test_desmontaje_devuelve_control():
    uno, dos, mount = _duo()
    mount.request("UNO")
    assert mount.request("UNO") is True
    assert mount.mounted is False
    assert (mount.uno_state, mount.dos_state) == ("NORMAL", "NORMAL")
    uno.move(10.0, 0.0)
    mount.update(0.016)
    assert uno.x == dos.x + MountSystem.STEP_ASIDE + 10.0


def test_eventos():
    bus = EventBus()
    uno, dos, mount = _duo(bus=bus)
    mount.request("UNO")
    mount.request("UNO")
    assert bus.log == ["MOUNT_STARTED", "MOUNT_ENDED"]


def test_convive_con_vinculo():
    bus = EventBus()
    uno, dos, mount = _duo(uno_xy=(100.0, 200.0), dos_xy=(120.0, 200.0), bus=bus)
    from dualis.world.entity import EntityManager
    entities = EntityManager()
    entities.register(uno)
    entities.register(dos)
    link = LinkSystem(entities, bus)
    mount.request("UNO")
    mount.update(0.016)
    assert link.update(0.016) == LinkSystem.CONNECTED
    assert link.distance == MountSystem.LIFT


def test_render_apilado():
    pygame.init()
    try:
        uno, dos, mount = _duo(uno_xy=(300.0, 200.0), dos_xy=(310.0, 200.0))
        mount.request("UNO")
        mount.update(0.016)
        surface = pygame.Surface((640, 360))
        surface.fill((16, 14, 22))
        dos.render(surface)
        uno.render(surface)
        assert uno.y < dos.y
    finally:
        pygame.quit()


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)
