"""RendererISO F20: mundo isométrico con elevación visual. Solo presentación.

Misma interfaz pública que Renderer2D: render_world() / render_hud() / render().
Lógica 100% cartesiana: el mundo sigue en 640x360 sin world_z en gameplay.
No existe eje Z jugable; la elevación es exclusivamente visual.
La proyección (ver presentation/iso.py) afecta exclusivamente al render.

Tiles (ver presentation/tiles.py + elevation.py): floor, wall, pillar,
platform (F19) + plat_low / plat_mid / plat_high / column / block (F20).
Cada elemento elevado muestra cara superior + izquierda + derecha (iso 2:1).
Sombras simples para pilares, plataformas/bloques y actores con z>0.
Sin arte definitivo: solo geometría y color, sin assets externos.

Capas: ground -> objects -> actors -> effects -> ui.
Profundidad: painter único ordenado por (x + y [+ z visual]); a igual X,
mayor Y lógica encima. Tiles altos, elevación F20 y actores comparten el
mismo sort: los actores pasan delante/detrás visualmente sin colisión.

Lectura visual: observable = mecánico frío; transformable = manipulable
cálido; salida LOCKED/READY/COMPLETED distinguible (mismo contorno F18).
Regionalización solo-detalle: R1 piedra, R2 estantería/mesa/archivador,
R3 maquinaria/prensa/pilar industrial. Sin combate, físicas, enemigos
ni iluminación avanzada.
"""
import math

import pygame

try:
    from dualis.presentation import tiles as _tiles
    from dualis.presentation import sprites as _sprites
    from dualis.presentation.iso import LAYERS
    from dualis.presentation.iso import raw as _iso_raw
    from dualis.systems.observable import Observable
    from dualis.systems.transformable import Transformable
except ImportError:
    from src.dualis.presentation import tiles as _tiles
    from src.dualis.presentation import sprites as _sprites
    from src.dualis.presentation.iso import LAYERS
    from src.dualis.presentation.iso import raw as _iso_raw
    from src.dualis.systems.observable import Observable
    from src.dualis.systems.transformable import Transformable

# Span del mundo 640x360 proyectado sin escala: x en [-360, 640], y en [0, 500].
_ISO_SPAN_X = 1000.0
_ISO_SPAN_Y = 500.0
_ISO_MIN_X = -360.0

# Alturas puramente visuales por kind. Sin modificar datos.
_BOX_Z = {
    "STEP": 16.0,
    "BRIDGE": 8.0,
    "PLATFORM": 24.0,
}
_UNO_LIFT_Z = 44.0
_EXIT_PEDESTAL_Z = 12.0

EXIT_COLORS = {
    "LOCKED": (80, 180, 100),
    "READY": (220, 170, 80),
    "COMPLETED": (90, 140, 230),
}

# Rellenos interiores de salida (el contorno F18 no cambia).
_EXIT_FILL = {
    "READY": (112, 86, 40),
    "COMPLETED": (46, 70, 116),
}
_EXIT_INNER = {
    "READY": (220, 170, 80),
    "COMPLETED": (140, 180, 240),
}

# Lectura visual F19: observable frío / transformable cálido.
_OBS_COLD = (105, 175, 210)
_OBS_CORE = (58, 108, 143)
_OBS_AXLE = (38, 78, 102)
_OBS_RIVET = (205, 232, 245)
_BOX_WARM = (205, 160, 100)
_BOX_EDGE = (120, 90, 55)
_BOX_TOP = (226, 190, 130)

_SLICE_TO_STATE = {
    "SOLVED": "COMPLETED",
    "BRIDGED": "READY",
    "STILLED": "READY",
}


def world_to_iso(x, y):
    """Utilidad desacoplada: cartesiano -> iso (sin escala). Solo render."""
    try:
        from dualis.presentation.iso import world_to_iso as _w2i
    except ImportError:
        from src.dualis.presentation.iso import world_to_iso as _w2i
    return _w2i(x, y)


def iso_to_world(rx, ry):
    """Utilidad desacoplada: iso -> cartesiano (sin escala). Solo render."""
    try:
        from dualis.presentation.iso import iso_to_world as _i2w
    except ImportError:
        from src.dualis.presentation.iso import iso_to_world as _i2w
    return _i2w(rx, ry)


class RendererISO:
    name = "iso"
    layers = LAYERS

    def __init__(self, logical=(640, 360), debug_iso_grid=True, show_floor_grid=True):
        self.logical = tuple(logical)
        self.debug_iso_grid = debug_iso_grid
        self.show_floor_grid = show_floor_grid
        self._tick = 0
        self.fit(*self.logical)

    def fit(self, width, height):
        scale = min(width / _ISO_SPAN_X, height / _ISO_SPAN_Y)
        if scale <= 0:
            scale = 1.0
        ox = -_ISO_MIN_X * scale + (width - _ISO_SPAN_X * scale) / 2.0
        oy = (height - _ISO_SPAN_Y * scale) / 2.0
        self._scale, self._ox, self._oy = scale, ox, oy
        return scale, ox, oy

    @staticmethod
    def raw(wx, wy):
        return _iso_raw(wx, wy)

    def world_to_iso(self, wx, wy, wz=0.0, scale=None, ox=None, oy=None):
        s = self._scale if scale is None else scale
        x0 = self._ox if ox is None else ox
        y0 = self._oy if oy is None else oy
        rx, ry = self.raw(wx, wy)
        return rx * s + x0, ry * s + y0 - wz * s

    def iso_to_world(self, sx, sy, scale=None, ox=None, oy=None):
        """Inversa de world_to_iso (plano z=0). Solo render/debug."""
        try:
            from dualis.presentation.iso import iso_to_world as _iso_inv
        except ImportError:
            from src.dualis.presentation.iso import iso_to_world as _iso_inv
        s = self._scale if scale is None else scale
        x0 = self._ox if ox is None else ox
        y0 = self._oy if oy is None else oy
        rx = (sx - x0) / s
        ry = (sy - y0) / s
        return _iso_inv(rx, ry)

    def _point(self, wx, wy, wz=0.0):
        return (int(round(self.world_to_iso(wx, wy, wz)[0])),
                int(round(self.world_to_iso(wx, wy, wz)[1])))

    def _diamond(self, surface, color, cx, cy, r, width=0):
        r = max(1, int(round(r)))
        pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
        if width:
            pygame.draw.polygon(surface, color, pts, width)
        else:
            pygame.draw.polygon(surface, color, pts)

    def _rect_diamond(self, surface, color, rect, width=3, wz=0.0):
        x, y, w, h = (float(v) for v in rect)
        pts = [self._point(x, y, wz), self._point(x + w, y, wz),
               self._point(x + w, y + h, wz), self._point(x, y + h, wz)]
        pygame.draw.polygon(surface, color, pts, width)

    def _floor(self, surface):
        w, h = self.logical
        pts = [self._point(0, 0), self._point(w, 0),
               self._point(w, h), self._point(0, h)]
        pygame.draw.polygon(surface, (48, 48, 66), pts, 1)

    def _grid(self, surface):
        if not (self.debug_iso_grid and self.show_floor_grid):
            return
        w, h = self.logical
        color = (40, 40, 56)
        step_x, step_y = 32, 16
        row = 0
        cy = 0
        while cy <= h + step_y:
            off = step_x // 2 if (row % 2) else 0
            cx = off
            while cx <= w + step_x:
                x, y = self.world_to_iso(cx, cy)
                self._diamond(surface, color, int(round(x)), int(round(y)),
                              step_x // 2 * self._scale, 1)
                cx += step_x
            cy += step_y // 2
            row += 1

    def draw_shadow(self, surface, cx, cy, base_r, z):
        if z <= 0:
            return
        factor = max(0.35, 1.0 - z / 160.0)
        rx = max(2, int(round(base_r * factor)))
        ry = max(1, int(round(base_r * factor * 0.45)))
        blob = pygame.Surface((rx * 2 + 2, ry * 2 + 2), pygame.SRCALPHA)
        pygame.draw.ellipse(blob, (0, 0, 0, 90), (0, 0, rx * 2 + 2, ry * 2 + 2))
        surface.blit(blob, (cx - rx + 5, cy - ry + 3))
        # Núcleo opaco de 1px: garantiza sombra visible sobre cualquier fondo
        # (el blit con alfa nunca produce negro puro por mezcla).
        pygame.draw.ellipse(surface, (0, 0, 0), (cx + 4, cy + 2, 2, 2))

    def _exit_state(self, scene):
        active = getattr(scene, "_active_runtime", None)
        runtime = active() if callable(active) else None
        if runtime is not None:
            return runtime.state, runtime.exit_rect
        puzzle = getattr(scene, "puzzle", None)
        current = scene._current_id() if hasattr(scene, "_current_id") else None
        if puzzle is not None and current == "ROOM_SLICE":
            try:
                from dualis.systems.slice_puzzle import EXIT_RECT
            except ImportError:
                from src.dualis.systems.slice_puzzle import EXIT_RECT
            state = _SLICE_TO_STATE.get(getattr(puzzle, "state", ""), "LOCKED")
            return state, EXIT_RECT
        return None, None

    def _is_height_room(self, scene):
        active = getattr(scene, "_active_runtime", None)
        runtime = active() if callable(active) else None
        return type(runtime).__name__ == "HeightRuntime"

    def _region_of(self, scene):
        current = scene._current_id() if hasattr(scene, "_current_id") else None
        return _tiles.region_of(current)

    def _palette(self, scene):
        return _tiles.palette_for(self._region_of(scene))

    def _split_entities(self, scene):
        uno = dos = None
        observables, boxes, others = [], [], []
        entities = getattr(scene, "entities", None)
        if entities is None:
            return uno, dos, observables, boxes
        runtimes = getattr(scene, "runtimes", None)
        if runtimes is not None and hasattr(scene, "_current_id"):
            allowed = runtimes.active_ids(scene._current_id())
            pool = [e for e in entities.all() if e.id in allowed]
        else:
            pool = list(entities.all())
        for entity in pool:
            eid = getattr(entity, "id", "")
            if eid == "UNO":
                uno = entity
            elif eid == "DOS":
                dos = entity
            elif isinstance(entity, Transformable):
                boxes.append(entity)
            elif isinstance(entity, Observable):
                observables.append(entity)
            else:
                others.append(entity)
        return uno, dos, observables, boxes + others

    def _uno_z(self, scene):
        mount = getattr(scene, "mount", None)
        if mount is not None and bool(getattr(mount, "mounted", False)):
            return _UNO_LIFT_Z
        return 0.0

    def _box_z(self, entity):
        return _BOX_Z.get(getattr(entity, "id", ""), 0.0)

    def _draw_observable(self, surface, entity, pulse, tick=None, accent=None):
        """Mecanismo frío F21: artefacto/dispositivo, nunca caja genérica."""
        if tick is None:
            tick = self._tick
        if accent is None:
            accent = (205, 232, 245)
        bob = _sprites.bob(tick, 2.0, 0.25)
        cx, cy = self._point(entity.x, entity.y, 0.0)
        cy += int(round(bob))
        self.draw_shadow(surface, *self._point(entity.x, entity.y, 0.0),
                         entity.radius, 0.0)
        r = entity.radius + pulse
        _sprites.draw_observable_mechanism(
            surface, self._diamond, cx, cy, r,
            _OBS_COLD, _OBS_CORE, _OBS_AXLE, _OBS_RIVET, accent,
            tick, frozen=getattr(entity, "frozen", False))

    def _draw_box(self, surface, entity, z, pulse, tick=None, accent=None):
        """Máquina cálida F21: estructura manipulable, distinta del observable."""
        if tick is None:
            tick = self._tick
        if accent is None:
            accent = (230, 230, 240)
        cx, cy = self._point(entity.x, entity.y, z)
        self.draw_shadow(surface, *self._point(entity.x, entity.y, 0.0),
                         entity.radius, z)
        _sprites.draw_transformable_machine(
            surface, self._diamond, cx, cy, entity.radius,
            _BOX_WARM, _BOX_EDGE, _BOX_TOP, accent, tick,
            transformed=getattr(entity, "is_transformed", False),
            eligible=getattr(entity, "eligible", True))

    def _draw_exit(self, surface, rect, state, height_room, exit_z):
        """Salida F21: contorno F18 + relleno + glifo + baliza por estado.

        Geometría y RGB base intactos (F17/F18/F20). La baliza se dibuja
        primero (alfa, sin tapar el contorno) y el glifo usa el MISMO
        color de estado; el contorno se dibuja siempre el último.
        """
        if height_room:
            x, y, w, h = (float(v) for v in rect)
            base = [self._point(x, y, 0.0), self._point(x + w, y, 0.0),
                    self._point(x + w, y + h, 0.0), self._point(x, y + h, 0.0)]
            pygame.draw.polygon(surface, (96, 84, 52), base)
        # Baliza de lectura a simple vista (antes del relleno puro).
        beacon_color = EXIT_COLORS.get(state, (140, 130, 115))
        if state in EXIT_COLORS:
            _sprites.draw_exit_beacon(surface, self._point, rect, exit_z,
                                      beacon_color, self._tick)
        fill = _EXIT_FILL.get(state)
        if fill is not None:
            x, y, w, h = (float(v) for v in rect)
            cx, cy = x + w / 2.0, y + h / 2.0
            inset = 0.72
            pygame.draw.polygon(surface, fill,
                                [self._point(cx + (x - cx) * inset,
                                             cy + (y - cy) * inset, exit_z),
                                 self._point(cx + (x + w - cx) * inset,
                                             cy + (y - cy) * inset, exit_z),
                                 self._point(cx + (x + w - cx) * inset,
                                             cy + (y + h - cy) * inset, exit_z),
                                 self._point(cx + (x - cx) * inset,
                                             cy + (y + h - cy) * inset, exit_z)])
            inner = _EXIT_INNER[state]
            ccx, ccy = self._point(cx, cy, exit_z)
            breathe = 1.5 * math.sin(self._tick * 0.35)
            self._diamond(surface, inner, ccx, ccy, 5 + breathe)
        elif state == "LOCKED":
            x, y, w, h = (float(v) for v in rect)
            ax, ay = self._point(x + w * 0.35, y + h / 2.0, exit_z)
            bx, by = self._point(x + w * 0.65, y + h / 2.0, exit_z)
            pygame.draw.line(surface, EXIT_COLORS["LOCKED"],
                             (ax, ay), (bx, by), 2)
        _sprites.draw_exit_glyph(
            surface, self._point, self._diamond, rect, exit_z, state,
            {"LOCKED": EXIT_COLORS["LOCKED"],
             "READY_INNER": _EXIT_INNER["READY"],
             "COMPLETED_INNER": _EXIT_INNER["COMPLETED"]},
            self._tick)
        self._rect_diamond(surface, EXIT_COLORS.get(state, (140, 130, 115)),
                           rect, 3, exit_z)

    def _collect_objects(self, scene):
        """Capa objects: muros, pilares, plataforma (F19) + elevación (F20).

        [(depth, draw)] con depth = x + w/2 + y + h + z visual. La elevación
        F20 se filtra contra exit_rect (no tapa salidas) y comparte el
        painter único con actors (delante/detrás visual, sin colisión).
        """
        items = []
        palette = self._palette(scene)
        region = self._region_of(scene)
        room_id = scene._current_id() if hasattr(scene, "_current_id") else None
        _, rect = self._exit_state(scene)
        height_room = self._is_height_room(scene)
        for spec in _tiles.tall_tiles(room_id, rect):
            kind = spec["kind"]
            if kind == "platform" and height_room:
                continue  # el pedestal de altura ya es la plataforma
            if kind == "platform":
                def draw(surface, spec=spec, palette=palette):
                    _tiles.draw_platform(
                        surface, self._point,
                        (spec["x"], spec["y"], spec["w"], spec["h"]),
                        palette["platform"], palette["trim"])
                draw._layer = "objects"
            elif kind == "pillar":
                def draw(surface, spec=spec, palette=palette):
                    # F20 FASE 3: sombra simple del pilar antes del volumen.
                    _tiles.draw_elevation_shadow(surface, self._point, spec)
                    _tiles.draw_box(surface, self._point, spec,
                                    palette["pillar_top"], palette["pillar_side"],
                                    palette["wall_right"], cap=palette["trim"])
                draw._layer = "objects"
            else:
                def draw(surface, spec=spec, palette=palette):
                    _tiles.draw_box(surface, self._point, spec,
                                    palette["wall_top"], palette["wall_left"],
                                    palette["wall_right"])
                draw._layer = "objects"
            items.append((_tiles.tile_depth(spec), draw))
        # F20: plataformas baja/media/alta, columna y bloque elevado.
        for spec in _tiles.elevation_tiles(room_id, rect):
            def draw(surface, spec=spec, palette=palette, region=region):
                # Sombra primero (lectura espacial), volumen después.
                _tiles.draw_elevation_shadow(surface, self._point, spec)
                _tiles.draw_elevated(surface, self._point, spec,
                                     palette, region)
            draw._layer = "objects"
            draw._elev_kind = spec["kind"]
            items.append((_tiles.tile_depth(spec), draw))
        return items

    def _collect_actors(self, scene):
        """Capa actors: salida, observables, transformables, UNO, DOS y
        vínculo. [(depth, draw)] sin ordenar; el sort lo hace el llamador."""
        uno, dos, observables, boxes = self._split_entities(scene)
        items = []
        pulse = 2.0 * math.sin(self._tick * 0.35)
        tick = self._tick
        accent = _sprites.actor_accent(self._region_of(scene))
        for entity in observables:
            def draw(surface, entity=entity, pulse=pulse, tick=tick,
                     accent=accent):
                self._draw_observable(surface, entity, pulse, tick, accent)
            draw._layer = "actors"
            items.append((entity.x + entity.y, draw))
        for entity in boxes:
            z = self._box_z(entity)
            def draw(surface, entity=entity, z=z, pulse=pulse, tick=tick,
                     accent=accent):
                self._draw_box(surface, entity, z, pulse, tick, accent)
            draw._layer = "actors"
            items.append((entity.x + entity.y + z, draw))
        state, rect = self._exit_state(scene)
        if rect is not None:
            height_room = self._is_height_room(scene)
            exit_z = _EXIT_PEDESTAL_Z if height_room else 0.0
            def draw(surface, rect=rect, state=state, height_room=height_room,
                     exit_z=exit_z):
                self._draw_exit(surface, rect, state, height_room, exit_z)
            draw._layer = "actors"
            cx = rect[0] + rect[2] / 2.0
            cy = rect[1] + rect[3] / 2.0
            items.append((cx + cy + exit_z, draw))
        if uno is not None and dos is not None:
            uz = self._uno_z(scene)
            def draw(surface, uno=uno, dos=dos, uz=uz):
                pygame.draw.line(surface, (140, 130, 115),
                                 self._point(uno.x, uno.y, uz),
                                 self._point(dos.x, dos.y, 0.0), 2)
            draw._layer = "actors"
            items.append(((uno.x + uno.y + uz + dos.x + dos.y) / 2.0, draw))
        if dos is not None:
            def draw(surface, dos=dos, tick=tick, accent=accent):
                lift = _sprites.bob(tick, 1.0, 0.25, phase=1.0)
                cx, cy = self._point(dos.x, dos.y, 0.0)
                cy += int(round(lift))
                self.draw_shadow(surface, *self._point(dos.x, dos.y, 0.0),
                                 dos.radius, 0.0)
                _sprites.draw_dos(surface, cx, cy, dos.radius, dos.color,
                                  accent, tick)
            draw._layer = "actors"
            items.append((dos.x + dos.y, draw))
        if uno is not None:
            uz = self._uno_z(scene)
            def draw(surface, uno=uno, uz=uz, tick=tick, accent=accent):
                lift = _sprites.bob(tick, 2.0, 0.25)
                cx, cy = self._point(uno.x, uno.y, uz)
                cy += int(round(lift))
                self.draw_shadow(surface, *self._point(uno.x, uno.y, 0.0),
                                 uno.radius, uz)
                _sprites.draw_uno(surface, cx, cy, uno.radius, uno.color,
                                  accent, tick)
            draw._layer = "actors"
            items.append((uno.x + uno.y + uz, draw))
        return items

    def _collect_renderables(self, scene):
        """Painter único F20: objects (F19 + elevación) + actors por depth.

        Lista [(depth, draw)] ya ordenada. depth = x + y [+ z visual].
        A igual X, mayor Y lógica se dibuja encima. Lógica cartesiana:
        la elevación solo añade z visual al sort, sin colisión.
        """
        items = self._collect_objects(scene) + self._collect_actors(scene)
        items.sort(key=lambda item: item[0])
        return items

    # ---- capas F20: ground -> objects -> actors -> effects -> ui ----
    def render_ground(self, surface, scene=None):
        """Capa ground: mosaico regional + contorno + rejilla de depuración."""
        palette = self._palette(scene) if scene is not None else _tiles.PALETTES["R1"]
        w, h = self.logical
        _tiles.draw_floor(surface, self._point, palette, w, h)
        self._floor(surface)
        self._grid(surface)

    def render_objects(self, surface, scene):
        """Capa objects: muros, pilares, plataforma y elevación F20."""
        for _, draw in self._collect_renderables(scene):
            if getattr(draw, "_layer", "actors") == "objects":
                draw(surface)

    def render_actors(self, surface, scene):
        """Capa actors: salida, observables, transformables, UNO, DOS, vínculo."""
        for _, draw in self._collect_renderables(scene):
            if getattr(draw, "_layer", "actors") == "actors":
                draw(surface)

    def render_effects(self, surface, scene):
        """Capa effects: eco de salida READY + brillo de congelados. Mínimo."""
        state, rect = self._exit_state(scene)
        if state == "READY" and rect is not None:
            height_room = self._is_height_room(scene)
            exit_z = _EXIT_PEDESTAL_Z if height_room else 0.0
            color = EXIT_COLORS["READY"]
            x, y, w, h = (float(v) for v in rect)
            cx, cy = x + w / 2.0, y + h / 2.0
            grow = 1.06 + 0.03 * math.sin(self._tick * 0.35)
            pygame.draw.polygon(surface, color,
                                [self._point(cx + (x - cx) * grow,
                                             cy + (y - cy) * grow, exit_z),
                                 self._point(cx + (x + w - cx) * grow,
                                             cy + (y - cy) * grow, exit_z),
                                 self._point(cx + (x + w - cx) * grow,
                                             cy + (y + h - cy) * grow, exit_z),
                                 self._point(cx + (x - cx) * grow,
                                             cy + (y + h - cy) * grow, exit_z)], 1)
        _, _, observables, _ = self._split_entities(scene)
        shimmer = 6 + 1.5 * math.sin(self._tick * 0.5)
        for entity in observables:
            if getattr(entity, "frozen", False):
                cx, cy = self._point(entity.x, entity.y, 0.0)
                self._diamond(surface, (200, 230, 245), cx, cy,
                              entity.radius + shimmer, 1)

    def render_ui(self, surface, scene, fps=0.0):
        """Capa ui: HUD por bloques (delegado a la escena)."""
        self.render_hud(scene, surface, fps)

    def render_world(self, scene, surface):
        try:
            from dualis import config
        except ImportError:
            from src.dualis import config

        self.fit(*self.logical)
        self._tick += 1
        surface.fill(config.BACKGROUND)
        self.render_ground(surface, scene)     # ground
        for _, draw in self._collect_renderables(scene):
            draw(surface)                      # objects + actors interleados
        self.render_effects(surface, scene)    # effects (mínimo)

    def render_hud(self, scene, surface, fps=0.0):
        scene.render_hud_blocks(surface, fps)
        if getattr(scene, "debug", False):
            scene.render_debug_overlay(surface, fps)

    def render(self, scene, surface, fps=0.0):
        self.render_world(scene, surface)
        self.render_hud(scene, surface, fps)
