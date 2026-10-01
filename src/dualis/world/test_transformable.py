"""Objeto de prueba F6: estado original y transformado. Sin gameplay."""
import pygame

try:
    from dualis.systems.transformable import Transformable
    from dualis.world.entity import Entity
except ImportError:
    from src.dualis.systems.transformable import Transformable
    from src.dualis.world.entity import Entity


class TestTransformable(Entity, Transformable):
    def __init__(self, x=320.0, y=140.0):
        Entity.__init__(self, "TESTBOX", x=x, y=y, radius=10,
                        color=(130, 140, 150), shape="circle")
        Transformable.__init__(self)

    def transform(self):
        super().transform()
        self.shape = "square"
        self.radius = 18
        self.color = (210, 180, 120)

    def restore(self):
        super().restore()
        self.shape = "circle"
        self.radius = 10
        self.color = (130, 140, 150)

    def render(self, surface):
        super().render(surface)
        if self.eligible and not self.transformed:
            x, y = int(round(self.x)), int(round(self.y))
            pygame.draw.circle(surface, (230, 230, 240), (x, y), self.radius + 5, 1)
