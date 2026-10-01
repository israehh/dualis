"""Correo de hechos F0: entrega ordenada dentro del paso, sin retorno."""
class EventBus:
    def __init__(self):
        self._subs = {}
        self.log = []

    def subscribe(self, name, fn):
        self._subs.setdefault(name, []).append(fn)

    def emit(self, name, payload=None):
        self.log.append(name)
        for fn in list(self._subs.get(name, [])):
            fn(payload)
