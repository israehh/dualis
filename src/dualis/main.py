"""Ejecutable F9: slice desde datos + biblioteca. Sin contenido nuevo."""
from pathlib import Path

import pygame

try:
    from dualis import config
    from dualis.core.bus import EventBus
    from dualis.core.loop import FixedStep
    from dualis.core.scene import SceneManager
    from dualis.core.state import StateManager
    from dualis.presentation.renderer import Renderer2D
    from dualis.presentation.renderer_iso import RendererISO
    from dualis.presentation.viewport import present
    from dualis.scenes.room_scene import RoomScene
    from dualis.systems.cooperation import CooperationSystem, MountAction
    from dualis.systems.link import LinkSystem
    from dualis.systems.observable import Observable, ObservableRegistry
    from dualis.systems.observe import ObserveSystem
    from dualis.systems.slice_puzzle import SlicePuzzle
    from dualis.systems.transform import TransformSystem
    from dualis.systems.transformable import Transformable, TransformableRegistry
    from dualis.world.blueprint import load_blueprint
    from dualis.world.builder import RoomBuilder
    from dualis.world.campaign import with_integration
    from dualis.world.colliders import move_with_collision, solids_for
    from dualis.world.entity import EntityManager
    from dualis.world.factory import load_setup
    from dualis.world.room import RoomManager
    from dualis.world.transit import decide_transit, entry_for, restore_actors, snapshot_actors
    from dualis.persistence.soft import load_soft, save_soft
    from dualis.systems.room_runtime import RoomRuntimeManager
except ImportError:
    from src.dualis import config
    from src.dualis.core.bus import EventBus
    from src.dualis.core.loop import FixedStep
    from src.dualis.core.scene import SceneManager
    from src.dualis.core.state import StateManager
    from src.dualis.presentation.renderer import Renderer2D
    from src.dualis.presentation.renderer_iso import RendererISO
    from src.dualis.presentation.viewport import present
    from src.dualis.scenes.room_scene import RoomScene
    from src.dualis.systems.cooperation import CooperationSystem, MountAction
    from src.dualis.systems.link import LinkSystem
    from src.dualis.systems.observable import Observable, ObservableRegistry
    from src.dualis.systems.observe import ObserveSystem
    from src.dualis.systems.slice_puzzle import SlicePuzzle
    from src.dualis.systems.transform import TransformSystem
    from src.dualis.systems.transformable import Transformable, TransformableRegistry
    from src.dualis.world.blueprint import load_blueprint
    from src.dualis.world.builder import RoomBuilder
    from src.dualis.world.campaign import with_integration
    from src.dualis.world.colliders import move_with_collision, solids_for
    from src.dualis.world.entity import EntityManager
    from src.dualis.world.factory import load_setup
    from src.dualis.world.room import RoomManager
    from src.dualis.world.transit import decide_transit, entry_for, restore_actors, snapshot_actors
    from src.dualis.persistence.soft import load_soft, save_soft
    from src.dualis.systems.room_runtime import RoomRuntimeManager

ROOMS_DIR = Path(__file__).resolve().parents[2] / "data" / "rooms"
SETUP = Path(__file__).resolve().parents[2] / "data" / "demo" / "f9_slice_setup.json"
BLUEPRINTS_DIR = Path(__file__).resolve().parents[2] / "data" / "blueprints"
R4_DIR = Path(__file__).resolve().parents[2] / "data" / "r4_rooms"
R5_DIR = Path(__file__).resolve().parents[2] / "data" / "r5_rooms"
PATTERNS_DIR = Path(__file__).resolve().parents[2] / "data" / "patterns"
SOFT_PATH = Path(__file__).resolve().parents[2] / "saves" / "soft.json"
SPEED = 240.0
RENDER_MODE = "iso"
DIGITS = {
    pygame.K_1: 0,
    pygame.K_2: 1,
    pygame.K_3: 2,
    pygame.K_4: 3,
    pygame.K_5: 4,
    pygame.K_6: 5,
    pygame.K_7: 6,
    pygame.K_8: 7,
    pygame.K_9: 8,
    pygame.K_0: 9,
}


def main():
    pygame.init()
    flags = pygame.RESIZABLE if config.WINDOW_RESIZABLE else 0
    screen = pygame.display.set_mode(config.WINDOW_SIZE, flags)
    canvas = pygame.Surface(config.LOGICAL_SIZE)
    pygame.display.set_caption(config.WINDOW_TITLE)
    clock = pygame.time.Clock()
    loop = FixedStep()
    states = StateManager()
    bus = EventBus()
    rooms = RoomManager(bus)
    rooms.load_directory(ROOMS_DIR)
    entities = EntityManager()
    registry = ObservableRegistry()
    tregistry = TransformableRegistry()
    pieces = {}
    for piece in load_setup(SETUP):
        entities.register(piece)
        if isinstance(piece, Observable):
            registry.register(piece)
        if isinstance(piece, Transformable):
            tregistry.register(piece)
        pieces[piece.id] = piece
    uno, dos = pieces["UNO"], pieces["DOS"]
    builder = RoomBuilder(rooms)
    blueprints = {}
    room_pieces = {}
    for path in sorted(BLUEPRINTS_DIR.glob("*.json")) + sorted(R4_DIR.glob("*.json")) + sorted(R5_DIR.glob("*.json")):
        blueprint = load_blueprint(path, PATTERNS_DIR)
        blueprints[blueprint.rid] = blueprint
        actors = []
        for actor in builder.build(blueprint).actors:
            entities.register(actor)
            actors.append(actor)
        room_pieces[blueprint.rid] = actors
    order = sorted(rooms.definitions)
    travel_prev = None
    snapshots = {}
    all_pieces = {}

    def _room_exit(rid):
        if rid == "ROOM_SLICE":
            try:
                from dualis.systems.slice_puzzle import EXIT_RECT
            except ImportError:
                from src.dualis.systems.slice_puzzle import EXIT_RECT
            return EXIT_RECT
        runtime = runtimes.runtime_for(rid)
        return runtime.exit_rect if runtime is not None else None

    def enter_room(rid, prev=None):
        """Entrada F24: reset local, posición coherente y persistencia mínima."""
        nonlocal travel_prev
        travel_prev = prev
        rooms.enter(rid)
        observe.registry = runtimes.registry_for(rid)
        if rid in snapshots:
            restore_actors(all_pieces[rid], snapshots[rid])
        uno_xy, dos_xy = entry_for(_room_exit(rid), current_solids(), prev)
        if mount.mounted:
            dos.x, dos.y = uno_xy
            uno.x, uno.y = uno_xy
        else:
            uno.x, uno.y = uno_xy
            dos.x, dos.y = dos_xy
        save_soft(str(SOFT_PATH), rid, prev)

    def current_solids():
        """Sólidos F22 de la sala activa (misma geometría que el render)."""
        rid = rooms.current_id
        runtime = runtimes.runtime_for(rid)
        if rid == "ROOM_SLICE":
            try:
                from dualis.systems.slice_puzzle import EXIT_RECT
            except ImportError:
                from src.dualis.systems.slice_puzzle import EXIT_RECT
            return solids_for(rid, EXIT_RECT)
        if runtime is not None:
            return solids_for(rid, runtime.exit_rect)
        return solids_for(rid, None)

    rooms.enter("ROOM_SLICE")
    phenomenon = next(p for p in pieces.values() if isinstance(p, Observable))
    testbox = next(p for p in pieces.values() if isinstance(p, Transformable))
    link = LinkSystem(entities, bus)
    observe = ObserveSystem(registry, bus)
    transform = TransformSystem(bus)
    coop = CooperationSystem(bus)
    mount = coop.register("mount", MountAction(uno, dos, bus))
    puzzle = SlicePuzzle(transform, phenomenon, testbox, uno, dos, bus)
    runtimes = RoomRuntimeManager(bus, transform, mount, uno, dos)
    runtimes.register_actors("ROOM_SLICE", [phenomenon, testbox])
    for rid, blueprint in blueprints.items():
        runtimes.add_room(blueprint, room_pieces[rid])
    all_pieces = dict(room_pieces)
    all_pieces["ROOM_SLICE"] = [phenomenon, testbox]
    snapshots = {rid: snapshot_actors(actors) for rid, actors in all_pieces.items()}
    links = with_integration(
        {rid: definition.enlaces for rid, definition in rooms.definitions.items()})
    soft_room, soft_prev = load_soft(str(SOFT_PATH))
    start = soft_room if soft_room in rooms.definitions else "ROOM_SLICE"
    enter_room(start, soft_prev if soft_prev in rooms.definitions else None)
    patterns = {rid: blueprint.pattern for rid, blueprint in blueprints.items()}
    renderer = RendererISO() if RENDER_MODE == "iso" else Renderer2D()
    manager = SceneManager(bus)
    states.request("RUNNING")
    manager.set_scene(RoomScene(rooms, entities, link, observe, transform, testbox,
                                puzzle, mount, bus, runtimes=runtimes,
                                patterns=patterns))
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), flags)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in DIGITS and DIGITS[event.key] < len(order):
                    enter_room(order[DIGITS[event.key]], rooms.current_id)
                elif event.key == pygame.K_n:
                    enter_room(order[(order.index(rooms.current_id) + 1) % len(order)],
                               rooms.current_id)
                elif event.key == pygame.K_p:
                    enter_room(order[(order.index(rooms.current_id) - 1) % len(order)],
                               rooms.current_id)
                elif event.key == pygame.K_q:
                    observe.request("UNO")
                elif event.key == pygame.K_e:
                    if rooms.current_id == "ROOM_SLICE":
                        puzzle.try_transform("DOS")
                    else:
                        runtimes.try_transform(rooms.current_id, "DOS")
                elif event.key == pygame.K_m:
                    mount.request("UNO")
                elif event.key == pygame.K_F1:
                    scene = manager.active_scene
                    if scene is not None and hasattr(scene, "debug"):
                        scene.debug = not scene.debug
        pressed = pygame.key.get_pressed()
        solids = current_solids()
        if not mount.mounted:
            dx = (pressed[pygame.K_d] - pressed[pygame.K_a]) * SPEED * dt
            dy = (pressed[pygame.K_s] - pressed[pygame.K_w]) * SPEED * dt
            move_with_collision(uno, dx, dy, solids)
        dx = (pressed[pygame.K_RIGHT] - pressed[pygame.K_LEFT]) * SPEED * dt
        dy = (pressed[pygame.K_DOWN] - pressed[pygame.K_UP]) * SPEED * dt
        move_with_collision(dos, dx, dy, solids)
        coop.update(dt)
        link.update(dt)
        observe.update(dt)
        transform.update(dt)
        puzzle.update(dt)
        runtimes.update(dt, rooms.current_id)
        target = decide_transit(rooms.current_id, travel_prev, links,
                                runtimes, puzzle, uno, dos, blueprints, link=link)
        if target is not None and target != rooms.current_id:
            bus.emit("ROOM_TRANSIT", {"from": rooms.current_id, "to": target})
            enter_room(target, rooms.current_id)
        loop.advance(dt)
        manager.update(dt)
        scene = manager.active_scene
        if scene is not None:
            renderer.render_world(scene, canvas)
            renderer.render_hud(scene, canvas, clock.get_fps())
        present(screen, canvas)
        pygame.display.flip()
    states.request("SHUTDOWN")
    pygame.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
