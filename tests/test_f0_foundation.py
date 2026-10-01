"""Tests F0: fundación sin ventana ni gameplay."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dualis import config
from dualis.core.loop import FixedStep
from dualis.core.state import StateManager
from dualis.core.bus import EventBus
from dualis.core.scene import SceneManager
from validation.validators import validate_room_dict


def test_config():
    assert config.TICK == 1.0 / 50.0
    assert config.MAX_STEPS_PER_FRAME == 5
    assert set(StateManager.known()) == {"BOOT", "RUNNING", "SHUTDOWN"}


def test_loop_counts_whole_steps():
    loop = FixedStep()
    assert loop.advance(config.TICK) == 1
    assert loop.advance(config.TICK) == 1
    assert loop.advance(config.TICK) == 1
    assert loop.ticks == 3


def test_loop_caps_and_never_partial():
    loop = FixedStep()
    assert loop.advance(config.TICK * 99) == config.MAX_STEPS_PER_FRAME
    assert loop.acc == 0.0


def test_state_only_granted():
    st = StateManager()
    assert st.request("SHUTDOWN") is False
    assert st.request("RUNNING") is True
    assert st.request("SHUTDOWN") is True


def test_bus_order():
    bus = EventBus()
    seen = []
    bus.subscribe("A", lambda p: seen.append("A"))
    bus.subscribe("B", lambda p: seen.append("B"))
    bus.emit("A")
    bus.emit("B")
    assert seen == ["A", "B"]
    assert bus.log == ["A", "B"]


def test_scene_empty():
    bus = EventBus()
    scene = SceneManager(bus)
    assert scene.active is None
    scene.enter_empty()
    assert scene.active == "void"
    assert bus.log == ["ROOM_ENTER"]


def test_validation_rejects_bad_and_accepts_shape():
    bad = validate_room_dict({})
    assert "sin-foco" in bad
    assert "menos-de-dos-salidas" in bad
    assert "requiere-una-idea" in bad
    good = validate_room_dict({"focus": "x", "exits": ["a", "b"], "ideas": ["una"]})
    assert good == []


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)
