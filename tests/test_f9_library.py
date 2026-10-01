"""Tests F9: biblioteca reutilizable, patrones y factoría. Sin contenido final."""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pygame

from dualis.core.bus import EventBus
from dualis.systems.cooperation import CooperationSystem, MountAction
from dualis.systems.mount import MountSystem
from dualis.systems.observable import ObservableRegistry
from dualis.systems.observe import ObserveSystem
from dualis.systems.transform import TransformSystem
from dualis.world.entity import Entity
from dualis.world.factory import create, load_setup
from dualis.world.observables import (
    MovingPhenomenon,
    OscillatingPhenomenon,
    TimedPhenomenon,
)
from dualis.world.transformables import (
    BridgeTransformable,
    PlatformTransformable,
    StepTransformable,
)

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = ["height", "shared_passage", "timed_window", "observe_to_cross", "transform_to_reach"]


def test_observables_implementan_observable():
    from dualis.systems.observable import Observable
    for obj in (MovingPhenomenon(), OscillatingPhenomenon(), TimedPhenomenon()):
        assert isinstance(obj, Observable)
        obj.set_frozen(True)
        assert obj.frozen is True


def test_moving_se_mueve_y_congela():
    registry = ObservableRegistry()
    moving = registry.register(MovingPhenomenon(x=100.0, y=200.0, vx=90.0))
    observe = ObserveSystem(registry)
    moving.update(0.5)
    assert moving.x != 100.0
    observe.request("UNO")
    frozen_x = moving.x
    moving.update(0.5)
    assert moving.x == frozen_x


def test_oscillating_oscila_y_congela():
    osc = OscillatingPhenomenon(ax=320.0, ay=200.0, amplitude=60.0, period=2.0)
    osc.update(0.5)
    assert osc.x != 320.0
    assert abs(osc.y - 200.0) < 1e-9
    osc.set_frozen(True)
    frozen_x = osc.x
    osc.update(0.5)
    assert osc.x == frozen_x


def test_timed_alterna_y_congela():
    timed = TimedPhenomenon(visible_for=1.0, hidden_for=1.0)
    assert timed.visible is True
    timed.update(1.5)
    assert timed.visible is False
    timed.set_frozen(True)
    timed.update(5.0)
    assert timed.visible is False
    timed.set_frozen(False)
    timed.update(1.0)
    assert timed.visible is True


def test_transformables_distintos():
    step = StepTransformable()
    bridge = BridgeTransformable()
    platform = PlatformTransformable()
    assert not (step.is_transformed or bridge.is_transformed or platform.is_transformed)
    step.transform()
    bridge.transform()
    platform.transform()
    assert (step.shape, bridge.shape, platform.shape) == ("square", "plank", "square")
    assert len({step.radius, bridge.radius, platform.radius}) == 3
    platform.restore()
    assert platform.is_transformed is False
    assert platform.shape == "circle"


def test_cooperation_delega_mount():
    bus = EventBus()
    uno = Entity("UNO", x=100.0, y=200.0)
    dos = Entity("DOS", x=120.0, y=200.0)
    coop = CooperationSystem(bus)
    mount = coop.register("mount", MountAction(uno, dos, bus))
    assert coop.action("mount") is mount
    assert mount.request("UNO") is True
    coop.update(0.016)
    assert (uno.x, uno.y) == (dos.x, dos.y - MountAction.LIFT)
    assert "MOUNT_STARTED" in bus.log


def test_mountsystem_compat():
    assert issubclass(MountSystem, MountAction)
    uno = Entity("UNO", x=0.0, y=0.0)
    dos = Entity("DOS", x=10.0, y=0.0)
    mount = MountSystem(uno, dos)
    assert mount.request("UNO") is True
    assert mount.mounted is True


def test_factory_desde_config():
    uno = create({"kind": "uno", "params": {"x": 1.0, "y": 2.0}})
    assert (uno.id, uno.x, uno.y) == ("UNO", 1.0, 2.0)
    osc = create({"kind": "oscillating", "params": {"ax": 5.0}})
    assert isinstance(osc, OscillatingPhenomenon)
    step = create({"kind": "step", "params": {}})
    assert isinstance(step, StepTransformable)
    try:
        create({"kind": "inexistente", "params": {}})
    except KeyError:
        return
    raise AssertionError("debió fallar con kind desconocido")


def test_setup_slice():
    pieces = load_setup(ROOT / "data" / "demo" / "f9_slice_setup.json")
    ids = sorted(p.id for p in pieces)
    assert ids == ["DOS", "PHENOMENON", "TESTBOX", "UNO"]


def test_patrones_validos():
    required = {"id", "intention", "mechanics", "difficulty", "combinations"}
    for name in PATTERNS:
        raw = json.loads((ROOT / "data" / "patterns" / ("pattern_" + name + ".json")).read_text(encoding="utf-8"))
        assert required <= set(raw), name
        assert raw["mechanics"], name
        assert raw["difficulty"] in ("corta", "media", "alta"), name


def test_render_biblioteca():
    pygame.init()
    try:
        surface = pygame.Surface((640, 360))
        for obj in (MovingPhenomenon(), OscillatingPhenomenon(), TimedPhenomenon(),
                    StepTransformable(), BridgeTransformable(), PlatformTransformable()):
            obj.update(0.1)
            obj.render(surface)
            if hasattr(obj, "transform"):
                obj.transform()
                obj.render(surface)
    finally:
        pygame.quit()


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)
