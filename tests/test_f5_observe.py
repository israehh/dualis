"""Tests F5: Observar congela y reanuda. Sin puzzles ni habitaciones tocadas."""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pygame

from dualis.core.bus import EventBus
from dualis.systems.observable import Observable, ObservableRegistry
from dualis.systems.observe import ObserveSystem
from dualis.world.phenomenon import TestPhenomenon


def _system(bus=None):
    registry = ObservableRegistry()
    phenomenon = registry.register(TestPhenomenon(x=100.0, y=300.0, vx=90.0))
    return ObserveSystem(registry, bus), phenomenon


def test_activacion_solo_uno():
    observe, _ = _system()
    assert observe.request("DOS") is False
    assert observe.state == ObserveSystem.IDLE
    assert observe.request("UNO") is True
    assert observe.state == ObserveSystem.OBSERVING
    assert observe.request("UNO") is False


def test_duracion_exacta():
    observe, _ = _system()
    observe.request("UNO")
    elapsed = 0.0
    while elapsed < 1.9:
        observe.update(0.1)
        elapsed += 0.1
    assert observe.state == ObserveSystem.OBSERVING
    observe.update(0.2)
    assert observe.state == ObserveSystem.COOLDOWN


def test_cooldown():
    observe, _ = _system()
    observe.request("UNO")
    observe.update(2.0)
    assert observe.state == ObserveSystem.COOLDOWN
    assert observe.request("UNO") is False
    observe.update(3.0)
    assert observe.state == ObserveSystem.IDLE
    assert observe.request("UNO") is True


def test_congelacion_fenomeno():
    observe, phenomenon = _system()
    phenomenon.update(0.5)
    moving_x = phenomenon.x
    assert moving_x != 100.0
    observe.request("UNO")
    observe.update(0.1)
    frozen_x = phenomenon.x
    phenomenon.update(0.5)
    assert phenomenon.x == frozen_x


def test_reanudacion_correcta():
    observe, phenomenon = _system()
    observe.request("UNO")
    observe.update(0.1)
    frozen_x = phenomenon.x
    observe.update(2.0)
    assert observe.state == ObserveSystem.COOLDOWN
    assert phenomenon.frozen is False
    phenomenon.update(0.5)
    assert phenomenon.x != frozen_x


def test_eventos_emitidos():
    bus = EventBus()
    observe, _ = _system(bus)
    observe.request("UNO")
    observe.update(2.0)
    observe.update(3.0)
    assert bus.log == [
        "OBSERVE_STARTED",
        "OBSERVE_FINISHED",
        "OBSERVE_COOLDOWN_STARTED",
        "OBSERVE_READY",
    ]


def test_observable_generico_no_acoplado():
    registry = ObservableRegistry()
    generic = Observable()
    registry.register(generic)
    observe = ObserveSystem(registry)
    observe.request("UNO")
    assert generic.frozen is True
    observe.update(2.0)
    assert generic.frozen is False


def test_render_fenomeno_congelado():
    pygame.init()
    try:
        _, phenomenon = _system()
        surface = pygame.Surface((640, 360))
        phenomenon.render(surface)
        phenomenon.set_frozen(True)
        phenomenon.render(surface)
    finally:
        pygame.quit()


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)
