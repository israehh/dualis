"""Tests F12: cada habitación valida su patrón. Sin resolución accidental."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dualis.core.bus import EventBus
from dualis.systems.cooperation import MountAction
from dualis.systems.observe import ObserveSystem
from dualis.systems.room_runtime import RoomRuntimeManager
from dualis.systems.slice_puzzle import EXIT_RECT as SLICE_EXIT
from dualis.systems.slice_puzzle import SlicePuzzle
from dualis.systems.transform import TransformSystem
from dualis.world.blueprint import load_blueprint
from dualis.world.builder import RoomBuilder
from dualis.world.entity import Entity
from dualis.world.room import RoomManager
from dualis.world.test_transformable import TestTransformable
from dualis.world.phenomenon import TestPhenomenon

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINTS_DIR = ROOT / "data" / "blueprints"
PATTERNS_DIR = ROOT / "data" / "patterns"


def _setup(rid):
    bus = EventBus()
    rooms = RoomManager(bus)
    rooms.load_directory(ROOT / "data" / "rooms")
    builder = RoomBuilder(rooms)
    blueprint = load_blueprint(BLUEPRINTS_DIR / (rid.lower() + ".json"), PATTERNS_DIR)
    built = builder.build(blueprint)
    uno = Entity("UNO", x=120.0, y=280.0)
    dos = Entity("DOS", x=220.0, y=280.0)
    transform = TransformSystem(bus)
    mount = MountAction(uno, dos, bus)
    runtimes = RoomRuntimeManager(bus, transform, mount, uno, dos)
    runtimes.add_room(blueprint, built.actors)
    observe = ObserveSystem(runtimes.registry_for(rid), bus)
    rooms.enter(rid)
    return {
        "bus": bus, "rooms": rooms, "blueprint": blueprint, "actors": built.actors,
        "uno": uno, "dos": dos, "transform": transform, "mount": mount,
        "runtimes": runtimes, "observe": observe,
        "runtime": runtimes.runtime_for(rid),
    }


def _center(rid):
    raw = load_blueprint(BLUEPRINTS_DIR / (rid.lower() + ".json"), PATTERNS_DIR)
    x, y, w, h = raw.exit_rect
    return x + w / 2.0, y + h / 2.0


def _park(ctx, rid):
    cx, cy = _center(rid)
    ctx["uno"].x, ctx["uno"].y = cx, cy
    ctx["dos"].x, ctx["dos"].y = cx, cy


def test_r1_teaches_observe():
    ctx = _setup("ROOM_01")
    _park(ctx, "ROOM_01")
    ctx["runtimes"].update(0.1, "ROOM_01")
    assert ctx["runtime"].state == "LOCKED"
    assert "ROOM_COMPLETED" not in ctx["bus"].log
    assert ctx["observe"].request("UNO") is True
    ctx["observe"].update(0.1)
    ctx["runtimes"].update(0.1, "ROOM_01")
    assert ctx["runtime"].state == "COMPLETED"
    assert "ROOM_COMPLETED" in ctx["bus"].log


def test_r2_demands_mount():
    ctx = _setup("ROOM_02")
    _park(ctx, "ROOM_02")
    ctx["runtimes"].update(0.1, "ROOM_02")
    ctx["runtimes"].update(0.1, "ROOM_02")
    assert ctx["runtime"].state == "LOCKED"
    assert "ROOM_COMPLETED" not in ctx["bus"].log
    ctx["uno"].x, ctx["uno"].y = 540.0, 110.0
    ctx["dos"].x, ctx["dos"].y = 550.0, 110.0
    assert ctx["mount"].request("UNO") is True
    ctx["dos"].x, ctx["dos"].y = 550.0, 110.0
    ctx["mount"].update(0.1)
    _park(ctx, "ROOM_02")
    ctx["dos"].x, ctx["dos"].y = 550.0, 110.0
    ctx["mount"].update(0.1)
    ctx["runtimes"].update(0.1, "ROOM_02")
    assert ctx["runtime"].state == "COMPLETED"


def test_r3_transforms_own_box():
    ctx = _setup("ROOM_03")
    control = TestTransformable(x=10.0, y=10.0)
    assert ctx["runtimes"].try_transform("ROOM_03", "DOS") is True
    assert ctx["runtime"].box.is_transformed is True
    assert control.is_transformed is False
    _park(ctx, "ROOM_03")
    ctx["runtimes"].update(0.1, "ROOM_03")
    assert ctx["runtime"].state == "COMPLETED"


def test_r4_combo():
    ctx = _setup("ROOM_04")
    assert ctx["runtimes"].try_transform("ROOM_04", "DOS") is False
    assert "ROOM_DENIED" in ctx["bus"].log
    assert ctx["observe"].request("UNO") is True
    ctx["observe"].update(0.1)
    assert ctx["runtimes"].try_transform("ROOM_04", "DOS") is True
    _park(ctx, "ROOM_04")
    ctx["runtimes"].update(0.1, "ROOM_04")
    assert ctx["runtime"].state == "COMPLETED"


def test_r5_exam():
    ctx = _setup("ROOM_05")
    _park(ctx, "ROOM_05")
    ctx["runtimes"].update(0.1, "ROOM_05")
    assert ctx["runtime"].state == "LOCKED"
    assert ctx["observe"].request("UNO") is True
    ctx["observe"].update(0.1)
    ctx["runtimes"].update(0.1, "ROOM_05")
    assert ctx["runtime"].state != "COMPLETED"
    assert ctx["runtimes"].try_transform("ROOM_05", "DOS") is True
    ctx["runtimes"].update(0.1, "ROOM_05")
    assert ctx["runtime"].state != "COMPLETED"
    ctx["uno"].x, ctx["uno"].y = 300.0, 100.0
    ctx["dos"].x, ctx["dos"].y = 310.0, 100.0
    assert ctx["mount"].request("UNO") is True
    _park(ctx, "ROOM_05")
    ctx["dos"].x, ctx["dos"].y = 320.0, 95.0
    ctx["mount"].update(0.1)
    ctx["runtimes"].update(0.1, "ROOM_05")
    assert ctx["runtime"].state == "COMPLETED"
    assert "ROOM_COMPLETED" in ctx["bus"].log


def test_isolation():
    first = _setup("ROOM_01")
    second = _setup("ROOM_03")
    assert first["runtimes"].registry_for("ROOM_01") is not second["runtimes"].registry_for("ROOM_03")
    _park(first, "ROOM_01")
    first["observe"].request("UNO")
    first["observe"].update(0.1)
    first["runtimes"].update(0.1, "ROOM_01")
    assert first["runtime"].state == "COMPLETED"
    assert second["runtime"].state == "LOCKED"


def test_no_accidental_any_room():
    for rid in ("ROOM_01", "ROOM_02", "ROOM_03", "ROOM_04", "ROOM_05"):
        ctx = _setup(rid)
        _park(ctx, rid)
        ctx["runtimes"].update(0.1, rid)
        ctx["runtimes"].update(0.1, rid)
        ctx["runtimes"].update(0.1, rid)
        assert ctx["runtime"].state != "COMPLETED", rid
        assert "ROOM_COMPLETED" not in ctx["bus"].log, rid


def test_slice_compat():
    bus = EventBus()
    uno = Entity("UNO", x=120.0, y=280.0)
    dos = Entity("DOS", x=220.0, y=280.0)
    phenomenon = TestPhenomenon()
    testbox = TestTransformable()
    transform = TransformSystem(bus)
    puzzle = SlicePuzzle(transform, phenomenon, testbox, uno, dos, bus)
    phenomenon.set_frozen(True)
    puzzle.update(0.1)
    assert puzzle.try_transform("DOS") is True
    x, y, w, h = SLICE_EXIT
    uno.x, uno.y = x + w / 2.0, y + h / 2.0
    dos.x, dos.y = x + w / 2.0, y + h / 2.0
    puzzle.update(0.1)
    assert puzzle.state == "SOLVED"
    assert "SLICE_SOLVED" in bus.log


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)
