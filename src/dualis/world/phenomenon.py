"""Fenómeno de prueba F5: se mueve solo; congelable vía Observable. Sin gameplay."""
import pygame

try:
    from dualis.systems.observable import Observable
    from dualis.world.entity import Entity
except ImportError:
    from src.dualis.systems.observable import Observable
    from src.dualis.world.entity import Entity


class TestPhenomenon(Entity, Observable):
    def __init__(self, x=320.0, y=300.0, vx=90.0, bounds=(640, 360)):
        Entity.__init__(self, "PHENOMENON", x=x, y=y, radius=10,
                        color=(170, 120, 200), shape="diamond")
        Observable.__init__(self)
        self.vx = vx
        self.bounds = bounds

    def update(self, dt):
        if self.frozen:
            return
        self.x += self.vx * dt
        width = self.bounds[0]
        if self.x > width - 20:
            self.x = width - 20
            self.vx = -self.vx
        elif self.x < 20:
            self.x = 20
            self.vx = -self.vx

    def render(self, surface):
        x, y, r = int(round(self.x)), int(round(self.y)), self.radius
        points = [(x, y - r), (x + r, y), (x, y + r), (x - r, y)]
        pygame.draw.polygon(surface, self.color, points)
        if self.frozen:
            pygame.draw.polygon(surface, (230, 230, 240), points, 2)
