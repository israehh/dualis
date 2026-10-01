"""Observable F5: interfaz reutilizable para lo congelable por Observar.

La habilidad nunca referencia fenómenos concretos; solo este registro.
Futuras mecánicas (resonadores, ecos, relojes) implementan Observable.
"""


class Observable:
    def __init__(self):
        self.frozen = False

    def set_frozen(self, frozen):
        self.frozen = bool(frozen)


class ObservableRegistry:
    def __init__(self):
        self._items = []

    def register(self, observable):
        self._items.append(observable)
        return observable

    def set_all_frozen(self, frozen):
        for item in self._items:
            item.set_frozen(frozen)

    def all(self):
        return list(self._items)
