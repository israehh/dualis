"""Tests F20: elevación visual sin altura mecánica. Solo presentación.

Regla: lógica 100% cartesiana, sin eje Z jugable. Verifica FASE 1-5 y
compatibilidad VEST_01 / BIB_01 / TAL_01 (resolubles, gates y coords intactas).
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
from dualis.presentation import tiles as _tiles
from dualis.presentation import elevation as _elev
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
    runtimes = None
    try:
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
    except ImportError:
        pass
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


# ---- FASE 1: niveles visuales, sin mecánica ----

def test_fase1_niveles_y_z_visual():
    assert _tiles.ELEVATION_Z["plat_low"] == 12.0
    assert _tiles.ELEVATION_Z["plat_mid"] == 24.0
    assert _tiles.ELEVATION_Z["plat_high"] == 36.0
    assert _tiles.ELEVATION_Z["column"] == 56.0
    assert _tiles.ELEVATION_Z["block"] == 20.0
    specs = _tiles.elevation_tiles("VEST_01", (500, 240, 100, 80))
    kinds = {s["kind"] for s in specs}
    assert {"plat_low", "plat_mid", "plat_high", "column", "block"} <= kinds
    for spec in specs:
        assert _tiles.is_elevation_spec(spec)
        assert spec["z"] > 0.0
        # Sin eje Z jugable: las entidades no exponen z.
        assert not hasattr(Entity("X"), "world_z")


def test_fase1_determinista_y_no_tapa_salida():
    first = _tiles.elevation_tiles("BIB_01", (420, 40, 110, 70))
    second = _tiles.elevation_tiles("BIB_01", (420, 40, 110, 70))
    assert first == second
    for spec in first:
        overlap = not (spec["x"] + spec["w"] + 6 <= 420 - 6 or
                       420 + 110 + 6 <= spec["x"] - 6 or
                       spec["y"] + spec["h"] + 6 <= 40 - 6 or
                       40 + 70 + 6 <= spec["y"] - 6)
        assert not overlap, spec
    # Tall tiles F19 intactos.
    tall = _tiles.tall_tiles("VEST_01", (500, 240, 100, 80))
    assert any(s["kind"] == "wall" for s in tall)
    assert any(s["kind"] == "pillar" for s in tall)
    assert any(s["kind"] == "platform" for s in tall)


# ---- FASE 2: tres caras visibles ----

def test_fase2_tres_caras():
    renderer = RendererISO()
    renderer.fit(*renderer.logical)
    palette = _tiles.palette_for("R1")
    assert len({palette["elev_top"], palette["elev_left"],
                palette["elev_right"]}) == 3
    canvas = pygame.Surface(config.LOGICAL_SIZE)
    canvas.fill(config.BACKGROUND)
    spec = {"kind": "plat_mid", "x": 250.0, "y": 200.0,
            "w": 100.0, "h": 60.0, "z": 24.0}
    _tiles.draw_elevated(canvas, renderer._point, spec, palette, "R1")
    assert _has_color(canvas, palette["elev_top"])
    assert _has_color(canvas, palette["elev_left"])
    assert _has_color(canvas, palette["elev_right"])


# ---- FASE 3: sombras simples ----

def test_fase3_sombras():
    renderer = RendererISO()
    renderer.fit(*renderer.logical)
    canvas = pygame.Surface(config.LOGICAL_SIZE)
    canvas.fill(config.BACKGROUND)
    before = pygame.image.tobytes(canvas, "RGB")
    spec = {"kind": "column", "x": 90.0, "y": 80.0,
            "w": 30.0, "h": 30.0, "z": 56.0}
    assert _tiles.draw_elevation_shadow(canvas, renderer._point, spec) is True
    assert pygame.image.tobytes(canvas, "RGB") != before
    assert _has_color(canvas, (0, 0, 0))
    flat = pygame.Surface(config.LOGICAL_SIZE)
    flat.fill(config.BACKGROUND)
    assert _tiles.draw_elevation_shadow(
        flat, renderer._point,
        {"kind": "block", "x": 0.0, "y": 0.0, "w": 10.0, "h": 10.0,
         "z": 0.0}) is False


# ---- FASE 4: profundidad visual ----

def test_fase4_depth_delante_detras():
    _, scene = _scene("VEST_01")
    renderer = RendererISO()
    renderer.fit(*renderer.logical)
    items = renderer._collect_renderables(scene)
    keys = [key for key, _ in items]
    assert keys == sorted(keys)
    # La elevación F20 participa en el mismo painter.
    elev = [d for d in items if getattr(d[1], "_elev_kind", None) is not None]
    assert len(elev) >= 5
    # Actor detrás (x+y pequeño) va antes que el bloque; delante va después.
    block = {"kind": "block", "x": 430.0, "y": 220.0,
             "w": 46.0, "h": 46.0, "z": 20.0}
    block_depth = _tiles.elevation_depth(block)
    behind = 100.0 + 100.0  # actor arriba-izquierda del bloque
    front = 500.0 + 300.0  # actor abajo-derecha del bloque
    assert behind < block_depth < front


def test_fase4_render_ordena_objetos_y_actores():
    _, scene = _scene("TAL_01")
    renderer = RendererISO()
    canvas = pygame.Surface(config.LOGICAL_SIZE)
    renderer.render_world(scene, canvas)
    layers = [getattr(draw, "_layer", None)
              for _, draw in renderer._collect_renderables(scene)]
    assert "objects" in layers and "actors" in layers


# ---- FASE 5: regionalización geométrica ----

def test_fase5_regiones_y_detalle():
    assert _tiles.region_of("VEST_01") == "R1"
    assert _tiles.region_of("BIB_01") == "R2"
    assert _tiles.region_of("TAL_01") == "R3"
    palettes = [_tiles.palette_for(region)["elev_top"]
                for region in ("R1", "R2", "R3")]
    assert len(set(palettes)) == 3
    renderer = RendererISO()
    renderer.fit(*renderer.logical)
    spec = {"kind": "column", "x": 90.0, "y": 80.0,
            "w": 30.0, "h": 30.0, "z": 56.0}
    renders = []
    for region in ("R1", "R2", "R3"):
        canvas = pygame.Surface(config.LOGICAL_SIZE)
        canvas.fill(config.BACKGROUND)
        _tiles.draw_elevated(canvas, renderer._point, spec,
                             _tiles.palette_for(region), region)
        renders.append(pygame.image.tobytes(canvas, "RGB"))
    assert len(set(renders)) == 3


def test_fase5_arquitectura_expone_niveles():
    assert _elev.LEVELS["plat_low"] == 12.0
    assert _elev.LEVELS["column"] == 56.0
    specs = _elev.specs_for("VEST_01", (500, 240, 100, 80))
    assert all(_elev.is_elevated(s) for s in specs)
    assert all(_elev.depth_of(s) == _tiles.tile_depth(s) for s in specs)


# ---- Compatibilidad: resolubles, gates y coords ----

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
            "runtime": runtimes.runtime_for(rid), "exit": blueprint.exit_rect,
            "blueprint": blueprint}


def test_compat_coordenadas_y_gates():
    expected = {"VEST_01": (500, 240, 100, 80),
                "BIB_01": (420, 40, 110, 70),
                "TAL_01": (80, 240, 100, 80)}
    for rid, rect in expected.items():
        blueprint = load_blueprint(BLUEPRINTS_DIR / (rid.lower() + ".json"), PATTERNS_DIR)
        assert tuple(blueprint.exit_rect) == rect, rid
        raw = json.loads((BLUEPRINTS_DIR / (rid.lower() + ".json")).read_text(encoding="utf-8"))
        assert raw["exit"]["rect"] == list(rect), rid


def test_compat_vest01_resoluble():
    from dualis.systems.observe import ObserveSystem
    ctx = _play("VEST_01")
    observe = ObserveSystem(ctx["runtimes"].registry_for("VEST_01"), ctx["bus"])
    observe.request("UNO")
    observe.update(0.1)
    cx = ctx["exit"][0] + ctx["exit"][2] / 2.0
    cy = ctx["exit"][1] + ctx["exit"][3] / 2.0
    ctx["uno"].x, ctx["uno"].y = cx, cy
    ctx["dos"].x, ctx["dos"].y = cx, cy
    ctx["runtimes"].update(0.1, "VEST_01")
    assert ctx["runtime"].state == "COMPLETED"


def test_compat_bib01_resoluble():
    ctx = _play("BIB_01")
    assert ctx["runtimes"].try_transform("BIB_01", "DOS") is False
    observe = ObserveSystem(ctx["runtimes"].registry_for("BIB_01"), ctx["bus"])
    observe.request("UNO")
    observe.update(0.1)
    assert ctx["runtimes"].try_transform("BIB_01", "DOS") is True
    cx = ctx["exit"][0] + ctx["exit"][2] / 2.0
    cy = ctx["exit"][1] + ctx["exit"][3] / 2.0
    ctx["uno"].x, ctx["uno"].y = cx, cy
    ctx["dos"].x, ctx["dos"].y = cx, cy
    ctx["runtimes"].update(0.1, "BIB_01")
    assert ctx["runtime"].state == "COMPLETED"


def test_compat_tal01_resoluble():
    from dualis.systems.observe import ObserveSystem
    ctx = _play("TAL_01")
    observe = ObserveSystem(ctx["runtimes"].registry_for("TAL_01"), ctx["bus"])
    observe.request("UNO")
    observe.update(0.1)
    cx = ctx["exit"][0] + ctx["exit"][2] / 2.0
    cy = ctx["exit"][1] + ctx["exit"][3] / 2.0
    ctx["uno"].x, ctx["uno"].y = cx, cy
    ctx["dos"].x, ctx["dos"].y = cx, cy
    ctx["runtimes"].update(0.1, "TAL_01")
    assert ctx["runtime"].state == "COMPLETED"


def test_compat_render_tres_salas():
    renderer = RendererISO()
    for rid in ("VEST_01", "BIB_01", "TAL_01"):
        _, scene = _scene(rid)
        canvas = pygame.Surface(config.LOGICAL_SIZE)
        renderer.render(scene, canvas, fps=60.0)


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print("ok", name)
