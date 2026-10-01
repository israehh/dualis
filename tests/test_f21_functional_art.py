"""Tests F21: arte funcional generado por código. Solo presentación.

Verifica lectura UNO/DOS/observables/transformables/salidas, coherencia
regional y animación ambiental, más compatibilidad VEST_01/BIB_01/TAL_01.
No modifica tests existentes.
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pygame

from dualis import config
from dualis.core.bus import EventBus
from dualis.core.scene import SceneManager
from dualis.presentation import sprites as _sprites
from dualis.presentation import tiles as _tiles
from dualis.presentation.renderer_iso import (
    EXIT_COLORS,
    RendererISO,
    _BOX_EDGE,
    _BOX_WARM,
    _EXIT_INNER,
    _OBS_COLD,
)
from dualis.scenes.room_scene import RoomScene
from dualis.systems.cooperation import MountAction
from dualis.systems.link import LinkSystem
from dualis.systems.observable import ObservableRegistry
from dualis.systems.observe import ObserveSystem
from dualis.systems.slice_puzzle import SlicePuzzle
from dualis.systems.transform import TransformSystem
from dualis.systems.transformable import TransformableRegistry
from dualis.world.blueprint import load_blueprint
from dualis.world.builder import RoomBuilder
from dualis.world.entity import Entity, EntityManager
from dualis.world.phenomenon import TestPhenomenon
from dualis.world.room import RoomManager
from dualis.world.test_transformable import TestTransformable

ROOT = Path(__file__).resolve().parents[1]
ROOMS_DIR = ROOT / "data" / "rooms"
BLUEPRINTS_DIR = ROOT / "data" / "blueprints"
PATTERNS_DIR = ROOT / "data" / "patterns"


def _scene(rid="VEST_01"):
    pygame.init()
    bus = EventBus()
    rooms = RoomManager(bus)
    rooms.load_directory(ROOMS_DIR)
    entities = EntityManager()
    entities.register(Entity("UNO", x=120.0, y=280.0))
    entities.register(Entity("DOS", x=220.0, y=280.0))
    registry = ObservableRegistry()
    phenomenon = registry.register(TestPhenomenon())
    entities.register(phenomenon)
    observe = ObserveSystem(registry, bus)
    tregistry = TransformableRegistry()
    testbox = tregistry.register(TestTransformable())
    entities.register(testbox)
    transform = TransformSystem(bus)
    link = LinkSystem(entities, bus)
    puzzle = SlicePuzzle(transform, phenomenon, testbox,
                         entities.get("UNO"), entities.get("DOS"), bus)
    builder = RoomBuilder(rooms)
    from dualis.systems.room_runtime import RoomRuntimeManager
    runtimes = RoomRuntimeManager(bus, transform, mount=None,
                                  uno=entities.get("UNO"), dos=entities.get("DOS"))
    runtimes.register_actors("ROOM_SLICE", [phenomenon, testbox])
    for path in sorted(BLUEPRINTS_DIR.glob("*.json")):
        blueprint = load_blueprint(path, PATTERNS_DIR)
        built = builder.build(blueprint)
        for actor in built.actors:
            entities.register(actor)
        runtimes.add_room(blueprint, built.actors)
    rooms.enter(rid)
    manager = SceneManager(bus)
    scene = RoomScene(rooms, entities, link, observe, transform, testbox,
                      puzzle, None, bus, runtimes=runtimes)
    manager.set_scene(scene)
    return manager, scene


def _has_color(surface, color, box=None):
    x0, y0 = (0, 0) if box is None else (box[0], box[1])
    x1, y1 = surface.get_size() if box is None else (box[0] + box[2], box[1] + box[3])
    for x in range(max(0, x0), min(x1, surface.get_width())):
        for y in range(max(0, y0), min(y1, surface.get_height())):
            if surface.get_at((x, y))[:3] == color:
                return True
    return False


def test_uno_explorador_con_visor():
    canvas = pygame.Surface(config.LOGICAL_SIZE)
    canvas.fill(config.BACKGROUND)
    _sprites.draw_uno(canvas, 320, 180, 14, (210, 180, 120), (150, 144, 130), 10)
    assert _has_color(canvas, (210, 180, 120))
    assert _has_color(canvas, (235, 240, 250))  # lente de observador
    assert _has_color(canvas, (30, 28, 38))  # visor


def test_dos_robusto_distinto_de_uno():
    uno = pygame.Surface(config.LOGICAL_SIZE)
    uno.fill(config.BACKGROUND)
    _sprites.draw_uno(uno, 320, 180, 14, (210, 180, 120), (150, 144, 130), 10)
    dos = pygame.Surface(config.LOGICAL_SIZE)
    dos.fill(config.BACKGROUND)
    _sprites.draw_dos(dos, 320, 180, 14, (90, 180, 170), (150, 144, 130), 10)
    assert _has_color(dos, (90, 180, 170))
    assert pygame.image.tobytes(uno, "RGB") != pygame.image.tobytes(dos, "RGB")


def test_observable_es_mecanismo_frio():
    renderer = RendererISO()
    canvas = pygame.Surface(config.LOGICAL_SIZE)
    canvas.fill(config.BACKGROUND)
    _sprites.draw_observable_mechanism(
        canvas, renderer._diamond, 320, 180, 14, _OBS_COLD,
        (58, 108, 143), (38, 78, 102), (205, 232, 245),
        (150, 144, 130), 10)
    assert _has_color(canvas, _OBS_COLD)
    assert _has_color(canvas, (205, 232, 245))


def test_transformable_es_maquina_calida_distinta():
    renderer = RendererISO()
    obs = pygame.Surface(config.LOGICAL_SIZE)
    obs.fill(config.BACKGROUND)
    _sprites.draw_observable_mechanism(
        obs, renderer._diamond, 320, 180, 14, _OBS_COLD,
        (58, 108, 143), (38, 78, 102), (205, 232, 245),
        (150, 144, 130), 10)
    box = pygame.Surface(config.LOGICAL_SIZE)
    box.fill(config.BACKGROUND)
    _sprites.draw_transformable_machine(
        box, renderer._diamond, 320, 180, 14, _BOX_WARM, _BOX_EDGE,
        (226, 190, 130), (150, 144, 130), 10)
    assert _has_color(box, _BOX_WARM)
    assert pygame.image.tobytes(obs, "RGB") != pygame.image.tobytes(box, "RGB")


def test_salidas_identificables_sin_hud():
    renderer = RendererISO()
    renderer.fit(*renderer.logical)
    for state, expected in (("LOCKED", EXIT_COLORS["LOCKED"]),
                            ("READY", _EXIT_INNER["READY"]),
                            ("COMPLETED", _EXIT_INNER["COMPLETED"])):
        canvas = pygame.Surface(config.LOGICAL_SIZE)
        canvas.fill(config.BACKGROUND)
        _sprites.draw_exit_glyph(
            canvas, renderer._point, renderer._diamond,
            (500, 240, 100, 80), 0.0, state,
            {"LOCKED": EXIT_COLORS["LOCKED"],
             "READY_INNER": _EXIT_INNER["READY"],
             "COMPLETED_INNER": _EXIT_INNER["COMPLETED"]}, 10)
        assert _has_color(canvas, expected), state
    # Glifos distintos por estado.
    renders = []
    for state in ("LOCKED", "READY", "COMPLETED"):
        canvas = pygame.Surface(config.LOGICAL_SIZE)
        canvas.fill(config.BACKGROUND)
        _sprites.draw_exit_glyph(
            canvas, renderer._point, renderer._diamond,
            (500, 240, 100, 80), 0.0, state,
            {"LOCKED": EXIT_COLORS["LOCKED"],
             "READY_INNER": _EXIT_INNER["READY"],
             "COMPLETED_INNER": _EXIT_INNER["COMPLETED"]}, 10)
        renders.append(pygame.image.tobytes(canvas, "RGB"))
    assert len(set(renders)) == 3


def test_contorno_salida_intacto_para_f17():
    class _StubRuntime:
        def __init__(self, state="LOCKED", exit_rect=(500, 240, 100, 80),
                     room_id="ROOM_X"):
            self.state = state
            self.exit_rect = exit_rect
            self.room_id = room_id

    class _StubRuntimes:
        def __init__(self, runtime=None, ids=()):
            self._runtime = runtime
            self._ids = set(ids)

        def runtime_for(self, rid):
            return self._runtime

        def active_ids(self, rid):
            return set(("UNO", "DOS")) | set(self._ids)

    _, scene = _scene("VEST_01")
    renderer = RendererISO()
    for state, expected in (("LOCKED", (80, 180, 100)),
                            ("READY", (220, 170, 80)),
                            ("COMPLETED", (90, 140, 230))):
        canvas = pygame.Surface(config.LOGICAL_SIZE)
        scene.runtimes = _StubRuntimes(_StubRuntime(state=state))
        renderer.render_world(scene, canvas)
        x, y = renderer.world_to_iso(550, 240)
        found = any(canvas.get_at((int(x) + dx, int(y) + dy))[:3] == expected
                    for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                    if 0 <= int(x) + dx < 640 and 0 <= int(y) + dy < 360)
        assert found, state


def test_coherencia_regional_en_actores():
    accents = {_sprites.actor_accent(region) for region in ("R1", "R2", "R3")}
    assert len(accents) == 3
    renderer = RendererISO()
    renders = []
    for region in ("R1", "R2", "R3"):
        canvas = pygame.Surface(config.LOGICAL_SIZE)
        canvas.fill(config.BACKGROUND)
        _sprites.draw_uno(canvas, 320, 180, 14, (210, 180, 120),
                          _sprites.actor_accent(region), 10)
        renders.append(pygame.image.tobytes(canvas, "RGB"))
    assert len(set(renders)) == 3


def test_animacion_ambiental_sin_mecanica():
    assert _sprites.bob(0, 2.0, 0.25) == 0.0
    assert _sprites.bob(10, 2.0, 0.25) != _sprites.bob(20, 2.0, 0.25)
    uno = Entity("UNO", x=120.0, y=280.0)
    x0, y0 = uno.x, uno.y
    renderer = RendererISO()
    canvas = pygame.Surface(config.LOGICAL_SIZE)
    renderer.render_world(_scene("VEST_01")[1], canvas)
    assert (uno.x, uno.y) == (x0, y0)


def _play(rid):
    bus = EventBus()
    rooms = RoomManager(bus)
    rooms.load_directory(ROOMS_DIR)
    builder = RoomBuilder(rooms)
    blueprint = load_blueprint(BLUEPRINTS_DIR / (rid.lower() + ".json"), PATTERNS_DIR)
    pattern_raw = None
    for path in PATTERNS_DIR.glob("*.json"):
        raw = json.loads(path.read_text(encoding="utf-8"))
        if raw["id"] == blueprint.pattern:
            pattern_raw = raw
            break
    built = builder.build(blueprint, pattern_raw)
    uno = Entity("UNO", x=120.0, y=280.0)
    dos = Entity("DOS", x=220.0, y=280.0)
    transform = TransformSystem(bus)
    mount = MountAction(uno, dos, bus)
    from dualis.systems.room_runtime import RoomRuntimeManager
    runtimes = RoomRuntimeManager(bus, transform, mount, uno, dos)
    runtimes.add_room(blueprint, built.actors)
    rooms.enter(rid)
    return {"bus": bus, "uno": uno, "dos": dos, "transform": transform,
            "mount": mount, "runtimes": runtimes,
            "runtime": runtimes.runtime_for(rid), "exit": blueprint.exit_rect}


def test_compat_resolucion_identica():
    for rid in ("VEST_01", "BIB_01", "TAL_01"):
        ctx = _play(rid)
        if rid == "BIB_01":
            assert ctx["runtimes"].try_transform(rid, "DOS") is False
        observe = ObserveSystem(ctx["runtimes"].registry_for(rid), ctx["bus"])
        observe.request("UNO")
        observe.update(0.1)
        if rid == "BIB_01":
            assert ctx["runtimes"].try_transform(rid, "DOS") is True
        cx = ctx["exit"][0] + ctx["exit"][2] / 2.0
        cy = ctx["exit"][1] + ctx["exit"][3] / 2.0
        ctx["uno"].x, ctx["uno"].y = cx, cy
        ctx["dos"].x, ctx["dos"].y = cx, cy
        ctx["runtimes"].update(0.1, rid)
        assert ctx["runtime"].state == "COMPLETED", rid


def test_compat_render_tres_regiones():
    renderer = RendererISO()
    for rid in ("VEST_01", "BIB_01", "TAL_01"):
        _, scene = _scene(rid)
        canvas = pygame.Surface(config.LOGICAL_SIZE)
        renderer.render(scene, canvas, fps=60.0)


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)
