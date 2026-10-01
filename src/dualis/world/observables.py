"""Biblioteca Observable F9: comportamientos congelables. Sin lógica de puzzle."""
import math

import pygame

try:
    from dualis.systems.observable import Observable
    from dualis.world.entity import Entity
except ImportError:
    from src.dualis.systems.observable import Observable
    from src.dualis.world.entity import Entity


class MovingPhenomenon(Entity, Observable):
    """Batidor lineal: patrulla horizontal con rebote. Idea: ritmo legible."""

    def __init__(self, x=320.0, y=240.0, vx=90.0, span=(20.0, 620.0)):
        Entity.__init__(self, "MOVING", x=x, y=y, radius=10,
                        color=(170, 120, 200), shape="triangle")
        Observable.__init__(self)
        self.vx = vx
        self.span = span

    def update(self, dt):
        if self.frozen:
            return
        self.x += self.vx * dt
        lo, hi = self.span
        if self.x > hi:
            self.x = hi
            self.vx = -self.vx
        elif self.x < lo:
            self.x = lo
            self.vx = -self.vx

    def render(self, surface):
        x, y, r = int(round(self.x)), int(round(self.y)), self.radius
        points = [(x, y - r), (x + r, y + r), (x - r, y + r)]
        pygame.draw.polygon(surface, self.color, points)
        if self.frozen:
            pygame.draw.polygon(surface, (230, 230, 240), points, 2)


class OscillatingPhenomenon(Entity, Observable):
    """Péndulo visual: oscila alrededor de un ancla. Idea: cadencia predecible."""

    def __init__(self, ax=320.0, ay=200.0, amplitude=120.0, period=3.0):
        Entity.__init__(self, "OSC", x=ax, y=ay, radius=9,
                        color=(120, 170, 200), shape="circle")
        Observable.__init__(self)
        self.ax = ax
        self.ay = ay
        self.amplitude = amplitude
        self.period = period
        self.phase = 0.0

    def update(self, dt):
        if self.frozen:
            return
        self.phase += dt
        self.x = self.ax + self.amplitude * math.sin(2.0 * math.pi * self.phase / self.period)
        self.y = self.ay

    def render(self, surface):
        pygame.draw.line(surface, (90, 100, 115),
                         (int(self.ax), int(self.ay)), (int(self.x), int(self.y)), 1)
        super().render(surface)
        if self.frozen:
            x, y = int(round(self.x)), int(round(self.y))
            pygame.draw.circle(surface, (230, 230, 240), (x, y), self.radius + 4, 1)


class TimedPhenomenon(Entity, Observable):
    """Baliza intermitente: alterna visible y oculto. Idea: ventana temporal."""

    def __init__(self, x=320.0, y=120.0, visible_for=2.0, hidden_for=2.0):
        Entity.__init__(self, "TIMED", x=x, y=y, radius=11,
                        color=(200, 160, 90), shape="diamond")
        Observable.__init__(self)
        self.visible_for = visible_for
        self.hidden_for = hidden_for
        self.timer = 0.0
        self.visible = True

    def update(self, dt):
        if self.frozen:
            return
        self.timer += dt
        cycle = self.visible_for + self.hidden_for
        self.timer %= cycle
        self.visible = self.timer < self.visible_for

    def render(self, surface):
        if not self.visible and not self.frozen:
            x, y = int(round(self.x)), int(round(self.y))
            pygame.draw.circle(surface, (70, 65, 80), (x, y), 3)
            return
        x, y, r = int(round(self.x)), int(round(self.y)), self.radius
        points = [(x, y - r), (x + r, y), (x, y + r), (x - r, y)]
        pygame.draw.polygon(surface, self.color, points)
        if self.frozen:
            pygame.draw.polygon(surface, (230, 230, 240), points, 2)
