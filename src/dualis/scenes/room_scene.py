"""Escena de habitación F13.5: mundo lógico + HUD por bloques. Sin narrativa."""
import pygame

try:
    from dualis.core.scene import Scene
    from dualis.presentation.renderer import DEFAULT_RENDERER, draw_rect_outline
    from dualis.systems.slice_puzzle import BRIDGE_RECT, EXIT_RECT
except ImportError:
    from src.dualis.core.scene import Scene
    from src.dualis.presentation.renderer import DEFAULT_RENDERER, draw_rect_outline
    from src.dualis.systems.slice_puzzle import BRIDGE_RECT, EXIT_RECT

STATE_COLORS = {
    "CONNECTED": (120, 170, 130),
    "TENSION": (210, 180, 120),
    "LIMIT": (200, 110, 100),
}

REGION_LABELS = {
    "VEST": "El Vestíbulo",
}

PATTERN_LABELS = {
    "ObserveToCrossRuntime": "OBSERVE_TO_CROSS",
    "HeightRuntime": "HEIGHT",
    "TransformToReachRuntime": "TRANSFORM_TO_REACH",
    "SharedPassageRuntime": "SHARED_PASSAGE",
    "ExamRuntime": "EXAMEN",
}


def region_of(room_id):
    prefix = (room_id or "").split("_")[0]
    return REGION_LABELS.get(prefix, "Umbral")


def pattern_of(runtime, patterns=None):
    if patterns is not None and runtime is not None:
        label = patterns.get(runtime.room_id)
        if label:
            return label
    if runtime is None:
        return "—"
    return PATTERN_LABELS.get(type(runtime).__name__, "—")


class RoomScene(Scene):
    name = "room"

    RUNTIME_COLORS = {
        "LOCKED": (200, 110, 100),
        "READY": (120, 170, 130),
        "COMPLETED": (150, 220, 160),
    }

    def __init__(self, manager, entities=None, link=None, observe=None,
                 transform=None, testbox=None, puzzle=None, mount=None, bus=None,
                 runtimes=None, patterns=None, debug=True):
        super().__init__(bus)
        self.manager = manager
        self.entities = entities
        self.link = link
        self.observe = observe
        self.transform = transform
        self.testbox = testbox
        self.puzzle = puzzle
        self.mount = mount
        self.runtimes = runtimes
        self.patterns = patterns
        self.debug = debug
        self.elapsed = 0.0
        self._title_font = None
        self._debug_font = None
        self._small_font = None

    def _fonts(self):
        if self._title_font is None:
            self._title_font = pygame.font.SysFont(None, 44)
            self._debug_font = pygame.font.SysFont(None, 24)
            self._small_font = pygame.font.SysFont(None, 20)
        return self._title_font, self._debug_font

    def _small(self):
        self._fonts()
        return self._small_font

    def update(self, dt):
        self.elapsed += dt
        if self.entities is not None:
            self.entities.update(dt)

    def _current_id(self):
        return getattr(self.manager, "current_id", "ROOM_SLICE")

    def _active_runtime(self):
        if self.runtimes is None:
            return None
        return self.runtimes.runtime_for(self._current_id())

    def _config(self):
        try:
            from dualis import config
        except ImportError:
            from src.dualis import config
        return config

    def _blit(self, surface, img, x, y, anchor="left"):
        config = self._config()
        width = surface.get_width()
        height = surface.get_height()
        rect = img.get_rect()
        if anchor == "right":
            rect.topright = (x, y)
        elif anchor == "center":
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        rect.left = max(rect.left, config.HUD_MARGIN)
        rect.right = min(rect.right, width - config.HUD_MARGIN)
        rect.top = max(rect.top, 0)
        rect.bottom = min(rect.bottom, height)
        surface.blit(img, rect)
        return rect

    # ---- mundo lógico ----

    def render_background(self, surface):
        surface.fill(self._config().BACKGROUND)

    def render_exits(self, surface):
        self._draw_slice(surface)
        self._draw_exit(surface)

    def render_entities(self, surface):
        if self.entities is None:
            return
        self._draw_entities(surface)

    def render_link(self, surface):
        if self.entities is None:
            return
        uno = self.entities.get("UNO")
        dos = self.entities.get("DOS")
        if uno is None or dos is None:
            return
        _, debug_font = self._fonts()
        dim = (140, 130, 115)
        state = self.link.state if self.link is not None else "—"
        color = STATE_COLORS.get(state, dim)
        pygame.draw.line(surface, color,
                         (int(uno.x), int(uno.y)), (int(dos.x), int(dos.y)), 2)
        if self.link is not None:
            pygame.draw.circle(surface, color, (int(uno.x), int(uno.y)),
                               int(self.link.limit_at), 1)

    def _draw_slice(self, surface):
        if self.puzzle is None:
            return
        if self._current_id() != "ROOM_SLICE":
            return
        gap_color = (70, 60, 80)
        for x in range(0, surface.get_width(), 24):
            pygame.draw.line(surface, gap_color, (x, 150), (x + 12, 190), 3)
        if self.testbox is not None and self.testbox.is_transformed:
            pygame.draw.rect(surface, (210, 180, 120), pygame.Rect(*BRIDGE_RECT))
        if self.puzzle.state == "SOLVED":
            color = (150, 220, 160)
        elif self.puzzle.exit_open:
            color = (120, 170, 130)
        else:
            color = (200, 110, 100)
        draw_rect_outline(surface, color, EXIT_RECT)

    def _draw_exit(self, surface):
        runtime = self._active_runtime()
        if runtime is None:
            return
        color = self.RUNTIME_COLORS.get(runtime.state, (140, 130, 115))
        draw_rect_outline(surface, color, runtime.exit_rect)

    def _draw_entities(self, surface):
        if self.runtimes is None:
            self.entities.render(surface)
            return
        allowed = self.runtimes.active_ids(self._current_id())
        for entity in self.entities.all():
            if entity.id in allowed:
                entity.render(surface)

    # ---- HUD ----

    def _pack_lines(self, items, font, max_width):
        lines = []
        current = ""
        for item in items:
            candidate = item if not current else current + "   " + item
            if font.size(candidate)[0] <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = item
                while font.size(current)[0] > max_width and len(current) > 1:
                    current = current[:-1]
        if current:
            lines.append(current)
        return lines

    def _runtime_state(self):
        runtime = self._active_runtime()
        if runtime is not None:
            return runtime.state, self.RUNTIME_COLORS.get(runtime.state, (140, 130, 115))
        if self.puzzle is not None and self._current_id() == "ROOM_SLICE":
            mapping = {"SOLVED": ("COMPLETED", (150, 220, 160)),
                       "BRIDGED": ("READY", (120, 170, 130)),
                       "STILLED": ("READY", (120, 170, 130))}
            return mapping.get(self.puzzle.state, ("LOCKED", (200, 110, 100)))
        return "—", (140, 130, 115)

    def render_hud_blocks(self, surface, fps=0.0):
        title_font, debug_font = self._fonts()
        small = self._small()
        fg = (210, 180, 120)
        dim = (140, 130, 115)
        width = surface.get_width()
        height = surface.get_height()
        current = self.manager.current()
        if current is None:
            text = title_font.render("SIN ROOM", True, fg)
            self._blit(surface, text, width // 2, 60, anchor="center")
            return
        definition = current.definition
        runtime = self._active_runtime()
        state_label, state_color = self._runtime_state()
        # Superior izquierda: región + habitación + patrón.
        self._blit(surface, small.render(region_of(definition.rid), True, dim), 10, 8)
        self._blit(surface, debug_font.render(definition.nombre, True, fg), 10, 28)
        self._blit(surface, small.render("patrón: %s" % pattern_of(runtime, self.patterns),
                                         True, dim), 10, 52)
        # Superior derecha: estado del runtime.
        state_img = debug_font.render(state_label, True, state_color)
        self._blit(surface, state_img, width - 10, 8, anchor="right")
        # Inferior izquierda: vínculo.
        if self.link is not None:
            self._blit(surface, small.render("vínculo %s d=%d max=%d" % (
                self.link.state, int(self.link.distance), int(self.link.limit_at)),
                True, dim), 10, height - 46)
        if self.mount is not None:
            self._blit(surface, small.render("montar M: %s/%s" % (
                self.mount.uno_state, self.mount.dos_state), True, dim), 10, height - 26)
        # Inferior derecha: ayuda de controles.
        for index, text in enumerate(("WASD/Flechas: mover",
                                      "Q observar · E transformar",
                                      "M montar · F1 debug")):
            img = small.render(text, True, dim)
            self._blit(surface, img, width - 10,
                       height - 26 - index * 20, anchor="right")

    def render_debug_overlay(self, surface, fps=0.0):
        _, debug_font = self._fonts()
        small = self._small()
        dim = (110, 110, 125)
        items = []
        if self.entities is not None:
            uno = self.entities.get("UNO")
            dos = self.entities.get("DOS")
            if uno is not None:
                items.append("UNO (%d,%d)" % (int(uno.x), int(uno.y)))
            if dos is not None:
                items.append("DOS (%d,%d)" % (int(dos.x), int(dos.y)))
        if self.observe is not None:
            items.append("observar %s %.1fs" % (self.observe.state, self.observe.remaining))
        if self.transform is not None:
            items.append("transformar %s" % self.transform.state)
        if self.testbox is not None:
            items.append("objeto: %s" % ("TRANSFORMADO" if self.testbox.is_transformed else "original"))
        if self.puzzle is not None:
            items.append("corte: %s" % self.puzzle.state)
        runtime = self._active_runtime()
        if runtime is not None:
            items.append("sala: %s %s" % (runtime.room_id, runtime.state))
        current = self.manager.current()
        if current is not None:
            items.append("room: %s vec:%d" % (
                current.definition.rid, len(self.manager.neighbours())))
            if runtime is not None:
                items.append("salida: %s" % (runtime.exit_rect,))
        items.append("t=%.0fs fps=%d rooms=%d" % (
            self.elapsed, int(round(fps)), len(self.manager.definitions)))
        config = self._config()
        lines = self._pack_lines(items, small, surface.get_width() - 2 * config.HUD_MARGIN)
        y = 104
        for text in lines:
            if y > surface.get_height() - 80:
                break
            self._blit(surface, small.render(text, True, dim), 10, y)
            y += 20
        return lines

    def render(self, surface, fps=0.0):
        DEFAULT_RENDERER.render(self, surface, fps)
