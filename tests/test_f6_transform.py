"""Tests F6: Transformar cambia estado y persiste. Sin puzzles."""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pygame

from dualis.core.bus import EventBus
from dualis.systems.transform import TransformSystem
from dualis.systems.transformable import Transformable, TransformableRegistry
from dualis.world.test_transformable import TestTransformable


def _system(bus=None):
    registry = TransformableRegistry()
    box = registry.register(TestTransformable())
    return TransformSystem(bus), box


def test_activacion_solo_dos():
    transform, box = _system()
    assert transform.request("UNO", box) is False
    assert box.is_transformed is False
    assert transform.request("DOS", box) is True
    assert transform.state == TransformSystem.TRANSFORMING


def test_transformacion():
    transform, box = _system()
    assert box.shape == "circle"
    transform.request("DOS", box)
    assert box.is_transformed is True
    assert box.shape == "square"


def test_cooldown():
    transform, box = _system()
    transform.request("DOS", box)
    transform.update(0.4)
    assert transform.state == TransformSystem.COOLDOWN
    other = TestTransformable()
    assert transform.request("DOS", other) is False
    transform.update(4.0)
    assert transform.state == TransformSystem.READY
    assert transform.request("DOS", other) is True


def test_eventos():
    bus = EventBus()
    transform, box = _system(bus)
    transform.request("DOS", box)
    transform.update(0.4)
    transform.update(4.0)
    assert bus.log == [
        "TRANSFORM_STARTED",
        "TRANSFORM_COMPLETED",
        "TRANSFORM_READY",
    ]


def test_persistencia_transformado():
    transform, box = _system()
    transform.request("DOS", box)
    for _ in range(10):
        transform.update(0.5)
        box.update(0.5)
    assert box.is_transformed is True
    assert box.shape == "square"


def test_transformable_generico_no_acoplado():
    registry = TransformableRegistry()
    generic = Transformable()
    registry.register(generic)
    transform = TransformSystem()
    assert transform.request("DOS", generic) is True
    assert generic.is_transformed is True


def test_render_ambos_estados():
    pygame.init()
    try:
        _, box = _system()
        surface = pygame.Surface((640, 360))
        box.render(surface)
        box.transform()
        box.render(surface)
    finally:
        pygame.quit()


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)
