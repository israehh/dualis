"""Entidades F3: base e identificador, posición, update y render. Sin gameplay."""
import pygame


class Entity:
    def __init__(self, eid, x=0.0, y=0.0, radius=14, color=(210, 180, 120), shape="circle"):
        self.id = eid
        self.x = float(x)
        self.y = float(y)
        self.radius = radius
        self.color = color
        self.shape = shape

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def update(self, dt):
        pass

    def render(self, surface):
        pos = (int(round(self.x)), int(round(self.y)))
        if self.shape == "square":
            side = self.radius * 2
            rect = pygame.Rect(0, 0, side, side)
            rect.center = pos
            pygame.draw.rect(surface, self.color, rect)
        else:
            pygame.draw.circle(surface, self.color, pos, self.radius)


class EntityManager:
    def __init__(self):
        self._entities = {}

    def register(self, entity):
        self._entities[entity.id] = entity
        return entity

    def get(self, eid):
        return self._entities.get(eid)

    def all(self):
        return list(self._entities.values())

    def update(self, dt):
        for entity in self._entities.values():
            entity.update(dt)

    def render(self, surface):
        for entity in self._entities.values():
            entity.render(surface)
