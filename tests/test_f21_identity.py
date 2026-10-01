"""Tests F21-identidad: UNO y DOS reconocibles en <1s. Solo presentación.

Verifica silueta (vertical ligera vs ancha pesada), colores de identidad,
lectura con solape parcial, animación sin gameplay y compatibilidad
VEST_01/BIB_01/TAL_01. No modifica ningún test existente.
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
from dualis.presentation.renderer_iso import RendererISO
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

UNO_BODY = (210, 180, 120)
DOS_BODY = (90, 180, 170)
UNO_VISOR = (30, 28, 38)
UNO_LENS = (235, 240, 250)


def _scene(rid="VEST_01"):
    pygame.init()
    bus = EventBus()
    rooms = RoomManager(bus)
    rooms.load_directory(ROOMS_DIR)
    entities = EntityManager()
    entities.register(Entity("UNO", x=120.0, y=280.0))
    # DOS con su color/forma de fábrica (como en main.py vía load_setup):
    # la identidad debe leerse por silueta Y color, como ve el jugador.
    entities.register(Entity("DOS", x=220.0, y=280.0,
                             color=(90, 180, 170), shape="square"))
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


def _paint(draw_fn, *args):
    canvas = pygame.Surface(config.LOGICAL_SIZE)
    canvas.fill(config.BACKGROUND)
    draw_fn(canvas, *args)
    return canvas


def _has_color(surface, color):
    for x in range(surface.get_width()):
        for y in range(surface.get_height()):
            if surface.get_at((x, y))[:3] == color:
                return True
    return False


def _bbox(surface, threshold=40):
    """Caja de la silueta opaca: ignora el fondo y el halo translúcido.

    El halo (alfa ~30 sobre fondo oscuro) apenas se separa del fondo;
    la silueta reconocible es el trazo opaco, que debe superar el umbral.
    """
    bg = config.BACKGROUND
    xs, ys = [], []
    for x in range(surface.get_width()):
        for y in range(surface.get_height()):
            px = surface.get_at((x, y))[:3]
            if sum(abs(a - b) for a, b in zip(px, bg)) >= threshold:
                xs.append(x)
                ys.append(y)
    if not xs:
        return (0, 0, 0, 0)
    return (min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1)


def test_siluetas_opuestas_vertical_vs_ancha():
    uno = _paint(_sprites.draw_uno, 320, 200, 14, UNO_BODY,
                 (150, 144, 130), 10)
    dos = _paint(_sprites.draw_dos, 320, 200, 14, DOS_BODY,
                 (150, 144, 130), 10)
    _, _, uw, uh = _bbox(uno)
    _, _, dw, dh = _bbox(dos)
    assert uh > uw, (uw, uh)  # UNO: alto y estrecho
    assert dw > dh, (dw, dh)  # DOS: bajo y ancho
    assert uh > dh  # UNO más alto
    assert dw > uw  # DOS más ancho


def test_colores_identidad_intactos():
    uno = _paint(_sprites.draw_uno, 320, 200, 14, UNO_BODY,
                 (150, 144, 130), 10)
    dos = _paint(_sprites.draw_dos, 320, 200, 14, DOS_BODY,
                 (150, 144, 130), 10)
    assert _has_color(uno, UNO_BODY)
    assert _has_color(uno, UNO_VISOR)
    assert _has_color(uno, UNO_LENS)
    assert _has_color(dos, DOS_BODY)
    assert pygame.image.tobytes(uno, "RGB") != pygame.image.tobytes(dos, "RGB")


def test_lectura_con_solape_parcial():
    # DOS detrás + UNO delante desplazado: ambos colores deben sobrevivir.
    for order in ("uno_delante", "dos_delante"):
        canvas = pygame.Surface(config.LOGICAL_SIZE)
        canvas.fill(config.BACKGROUND)
        if order == "uno_delante":
            _sprites.draw_dos(canvas, 320, 200, 14, DOS_BODY,
                              (150, 144, 130), 10)
            _sprites.draw_uno(canvas, 328, 200, 14, UNO_BODY,
                              (150, 144, 130), 10)
        else:
            _sprites.draw_uno(canvas, 320, 200, 14, UNO_BODY,
                              (150, 144, 130), 10)
            _sprites.draw_dos(canvas, 328, 200, 14, DOS_BODY,
                              (150, 144, 130), 10)
        assert _has_color(canvas, UNO_BODY), order
        assert _has_color(canvas, DOS_BODY), order


def test_acento_regional_visible_en_ambos():
    for fn, body in ((_sprites.draw_uno, UNO_BODY),
                     (_sprites.draw_dos, DOS_BODY)):
        renders = set()
        for region in ("R1", "R2", "R3"):
            canvas = pygame.Surface(config.LOGICAL_SIZE)
            canvas.fill(config.BACKGROUND)
            fn(canvas, 320, 200, 14, body, _sprites.actor_accent(region), 10)
            renders.add(pygame.image.tobytes(canvas, "RGB"))
        assert len(renders) == 3, fn


def test_animacion_sin_gameplay():
    uno = Entity("UNO", x=120.0, y=280.0)
    dos = Entity("DOS", x=220.0, y=280.0)
    before = (uno.x, uno.y, dos.x, dos.y, uno.radius, dos.radius)
    frames = set()
    for tick in (0, 10, 20, 30):
        canvas = pygame.Surface(config.LOGICAL_SIZE)
        canvas.fill(config.BACKGROUND)
        _sprites.draw_uno(canvas, 320, 200, 14, UNO_BODY,
                          (150, 144, 130), tick)
        _sprites.draw_dos(canvas, 360, 200, 14, DOS_BODY,
                          (150, 144, 130), tick)
        frames.add(pygame.image.tobytes(canvas, "RGB"))
    assert len(frames) > 1  # respiración/bob visibles
    assert (uno.x, uno.y, dos.x, dos.y, uno.radius, dos.radius) == before
    assert _sprites.bob(0, 2.0, 0.25) == 0.0


def test_renderer_conserva_sombra_profundidad_sort():
    _, scene = _scene("VEST_01")
    renderer = RendererISO()
    renderer.fit(*renderer.logical)
    items = renderer._collect_renderables(scene)
    keys = [key for key, _ in items]
    assert keys == sorted(keys)
    assert 400.0 in keys  # UNO en aparición (120+280), sin montar
    assert 500.0 in keys  # DOS en aparición (220+280)
    canvas = pygame.Surface(config.LOGICAL_SIZE)
    canvas.fill(config.BACKGROUND)
    renderer.render_world(scene, canvas)
    assert _has_color(canvas, UNO_BODY)
    assert _has_color(canvas, DOS_BODY)


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


def test_compat_resolucion_identica_tres_salas():
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


def test_render_tres_salas_sin_excepcion():
    renderer = RendererISO()
    for rid in ("VEST_01", "BIB_01", "TAL_01"):
        _, scene = _scene(rid)
        canvas = pygame.Surface(config.LOGICAL_SIZE)
        renderer.render(scene, canvas, fps=60.0)
        big = pygame.transform.scale(canvas, (1280, 720))
        assert _has_color(big, UNO_BODY), rid
        assert _has_color(big, DOS_BODY), rid


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)
