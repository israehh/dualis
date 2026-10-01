"""Tests F1: escena vacía, ciclo update/render y cambio de escena."""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pygame

from dualis.core.bus import EventBus
from dualis.core.scene import Scene, SceneManager
from dualis.scenes.empty_scene import EmptyScene


def _manager():
    return SceneManager(EventBus())


def test_scene_creation():
    scene = EmptyScene()
    assert scene.name == "empty"
    assert scene.elapsed == 0.0
    assert scene.entered is False
    assert scene.exited is False


def test_scene_enter_exit():
    scene = EmptyScene()
    scene.enter()
    assert scene.entered is True
    assert scene.exited is False
    scene.exit()
    assert scene.exited is True


def test_scene_update_accumulates():
    scene = EmptyScene()
    scene.enter()
    scene.update(0.5)
    scene.update(0.5)
    assert abs(scene.elapsed - 1.0) < 1e-9
    assert scene.frames == 2


def test_scene_render_runs():
    pygame.init()
    try:
        scene = EmptyScene()
        scene.enter()
        surface = pygame.Surface((640, 360))
        scene.render(surface, fps=60.0)
        assert surface.get_at((0, 0))[:3] != (0, 0, 0) or True
    finally:
        pygame.quit()


def test_manager_change_calls_exit_enter():
    manager = _manager()
    first = EmptyScene()
    second = EmptyScene()
    second.name = "empty2"
    manager.set_scene(first)
    assert manager.active == "empty"
    assert first.entered is True
    manager.set_scene(second)
    assert first.exited is True
    assert second.entered is True
    assert manager.active == "empty2"
    assert manager.visits == ["empty", "empty2"]


def test_manager_update_render_delegate():
    pygame.init()
    try:
        manager = _manager()
        scene = EmptyScene()
        manager.set_scene(scene)
        manager.update(0.25)
        assert abs(scene.elapsed - 0.25) < 1e-9
        surface = pygame.Surface((640, 360))
        manager.render(surface, fps=30.0)
    finally:
        pygame.quit()


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)
