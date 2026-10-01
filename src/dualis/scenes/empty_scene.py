"""Escena vacía F1: fondo, título, tiempo acumulado y FPS.

Sin habitaciones, sin entidades, sin gameplay. Solo depuración mínima.
"""
import pygame

try:
    from dualis.core.scene import Scene
except ImportError:
    from src.dualis.core.scene import Scene


class EmptyScene(Scene):
    name = "empty"

    def __init__(self, bus=None):
        super().__init__(bus)
        self.elapsed = 0.0
        self.frames = 0
        self._title_font = None
        self._debug_font = None

    def enter(self):
        super().enter()
        self.elapsed = 0.0
        self.frames = 0

    def update(self, dt):
        self.elapsed += dt
        self.frames += 1

    def _fonts(self):
        if self._title_font is None:
            self._title_font = pygame.font.SysFont(None, 72)
            self._debug_font = pygame.font.SysFont(None, 28)
        return self._title_font, self._debug_font

    def render(self, surface, fps=0.0):
        try:
            from dualis import config
        except ImportError:
            from src.dualis import config

        surface.fill(config.BACKGROUND)
        title_font, debug_font = self._fonts()
        fg = (210, 180, 120)
        dim = (140, 130, 115)
        title = title_font.render("DUALIS", True, fg)
        surface.blit(title, title.get_rect(center=(surface.get_width() // 2, 140)))
        lines = (
            "t = %.1f s" % self.elapsed,
            "fps = %d" % int(round(fps)),
        )
        y = 220
        for text in lines:
            img = debug_font.render(text, True, dim)
            surface.blit(img, img.get_rect(center=(surface.get_width() // 2, y)))
            y += 34
