"""Biblioteca Transformable F9: posibilidades espaciales. Sin lógica de puzzle."""
import pygame

try:
    from dualis.systems.transformable import Transformable
    from dualis.world.entity import Entity
except ImportError:
    from src.dualis.systems.transformable import Transformable
    from src.dualis.world.entity import Entity


class _Base(Entity, Transformable):
    def __init__(self, eid, x, y):
        Entity.__init__(self, eid, x=x, y=y, radius=10,
                        color=(130, 140, 150), shape="circle")
        Transformable.__init__(self)

    def _affordance(self, surface):
        if self.eligible and not self.transformed:
            x, y = int(round(self.x)), int(round(self.y))
            pygame.draw.circle(surface, (230, 230, 240), (x, y), self.radius + 14, 1)


class StepTransformable(_Base):
    """Peldaño: punto → escalón bajo. Idea: altura imposible en un paso."""

    def __init__(self, x=320.0, y=140.0):
        super().__init__("STEP", x, y)

    def transform(self):
        super().transform()
        self.shape = "square"
        self.radius = 14
        self.color = (190, 170, 120)

    def restore(self):
        super().restore()
        self.shape = "circle"
        self.radius = 10
        self.color = (130, 140, 150)

    def render(self, surface):
        super().render(surface)
        self._affordance(surface)


class BridgeTransformable(_Base):
    """Tablero: poste → tablón horizontal. Idea: paso compartido sobre el vano."""

    def __init__(self, x=320.0, y=170.0):
        super().__init__("BRIDGE", x, y)

    def transform(self):
        super().transform()
        self.shape = "plank"
        self.radius = 30
        self.color = (210, 180, 120)

    def restore(self):
        super().restore()
        self.shape = "circle"
        self.radius = 10
        self.color = (130, 140, 150)

    def render(self, surface):
        if self.shape == "plank":
            x, y = int(round(self.x)), int(round(self.y))
            rect = pygame.Rect(0, 0, self.radius * 2, 12)
            rect.center = (x, y)
            pygame.draw.rect(surface, self.color, rect)
        else:
            super().render(surface)
        self._affordance(surface)


class PlatformTransformable(_Base):
    """Plataforma: marca → superficie estable. Idea: apoyo para montar y estar."""

    def __init__(self, x=320.0, y=140.0):
        super().__init__("PLATFORM", x, y)

    def transform(self):
        super().transform()
        self.shape = "square"
        self.radius = 24
        self.color = (120, 170, 130)

    def restore(self):
        super().restore()
        self.shape = "circle"
        self.radius = 10
        self.color = (130, 140, 150)

    def render(self, surface):
        super().render(surface)
        self._affordance(surface)
