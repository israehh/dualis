"""Transformable F6: interfaz reutilizable para lo reinterpretable por DOS.

La habilidad nunca referencia objetos concretos; solo este registro.
Futuros objetos (pasos, apoyos, aliados temporales) implementan Transformable.
"""


class Transformable:
    def __init__(self):
        self.transformed = False
        self.eligible = True

    @property
    def is_transformed(self):
        return self.transformed

    def transform(self):
        self.transformed = True

    def restore(self):
        self.transformed = False


class TransformableRegistry:
    def __init__(self):
        self._items = []

    def register(self, transformable):
        self._items.append(transformable)
        return transformable

    def all(self):
        return list(self._items)
