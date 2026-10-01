"""Runtime F12: patrones como comportamiento verificable. Sin mecánicas nuevas.

Cada runtime ordena sistemas genéricos (observar, transformar, montar)
según un patrón de datos. La salida solo cuenta con requisitos cumplidos:
caminar hasta ella no resuelve la habitación.
"""


def _inside(rect, x, y):
    rx, ry, rw, rh = rect
    return rx <= x <= rx + rw and ry <= y <= ry + rh


class PatternRuntime:
    LOCKED = "LOCKED"
    READY = "READY"
    COMPLETED = "COMPLETED"

    def __init__(self, room_id, exit_rect, bus=None):
        self.room_id = room_id
        self.exit_rect = tuple(exit_rect)
        self.bus = bus
        self.state = self.LOCKED

    def duo_in_exit(self, uno, dos):
        return _inside(self.exit_rect, uno.x, uno.y) and _inside(self.exit_rect, dos.x, dos.y)

    def _complete(self):
        if self.state != self.COMPLETED:
            self.state = self.COMPLETED
            if self.bus is not None:
                self.bus.emit("ROOM_COMPLETED", {"room": self.room_id})
        return self.state

    def try_transform(self, actor, transform):
        return False

    def update(self, dt):
        return self.state


class ObserveToCrossRuntime(PatternRuntime):
    def __init__(self, room_id, exit_rect, bus=None, phenomenon=None, uno=None, dos=None):
        super().__init__(room_id, exit_rect, bus)
        self.phenomenon = phenomenon
        self.uno = uno
        self.dos = dos
        self.observed = False

    def update(self, dt):
        if self.state == self.COMPLETED:
            return self.state
        if self.phenomenon is not None and self.phenomenon.frozen:
            self.observed = True
        if self.observed and self.duo_in_exit(self.uno, self.dos):
            return self._complete()
        if self.observed:
            self.state = self.READY
        return self.state


class HeightRuntime(PatternRuntime):
    def __init__(self, room_id, exit_rect, bus=None, mount=None, uno=None, dos=None):
        super().__init__(room_id, exit_rect, bus)
        self.mount = mount
        self.uno = uno
        self.dos = dos

    def update(self, dt):
        if self.state == self.COMPLETED:
            return self.state
        if self.mount is not None and self.mount.mounted and self.duo_in_exit(self.uno, self.dos):
            return self._complete()
        if self.mount is not None and self.mount.mounted:
            self.state = self.READY
        else:
            self.state = self.LOCKED
        return self.state


class TransformToReachRuntime(PatternRuntime):
    def __init__(self, room_id, exit_rect, bus=None, box=None, uno=None, dos=None):
        super().__init__(room_id, exit_rect, bus)
        self.box = box
        self.uno = uno
        self.dos = dos

    def try_transform(self, actor, transform):
        if self.box is None:
            return False
        return bool(transform.request(actor, self.box))

    def update(self, dt):
        if self.state == self.COMPLETED:
            return self.state
        if self.box is not None and self.box.is_transformed:
            if self.duo_in_exit(self.uno, self.dos):
                return self._complete()
            self.state = self.READY
        return self.state


class SharedPassageRuntime(PatternRuntime):
    def __init__(self, room_id, exit_rect, bus=None, phenomenon=None, box=None, uno=None, dos=None):
        super().__init__(room_id, exit_rect, bus)
        self.phenomenon = phenomenon if phenomenon is not None else _AlwaysStill()
        self.box = box
        self.uno = uno
        self.dos = dos
        self.observed = self.phenomenon.frozen

    def try_transform(self, actor, transform):
        if self.box is None:
            return False
        if not self.phenomenon.frozen:
            if self.bus is not None:
                self.bus.emit("ROOM_DENIED", {"room": self.room_id, "actor": actor})
            return False
        return bool(transform.request(actor, self.box))

    def update(self, dt):
        if self.state == self.COMPLETED:
            return self.state
        if self.phenomenon.frozen:
            self.observed = True
        if self.observed and self.box is not None and self.box.is_transformed:
            if self.duo_in_exit(self.uno, self.dos):
                return self._complete()
            self.state = self.READY
        elif self.observed:
            self.state = self.READY
        return self.state


class ExamRuntime(PatternRuntime):
    def __init__(self, room_id, exit_rect, bus=None, phenomenon=None, box=None,
                 mount=None, uno=None, dos=None):
        super().__init__(room_id, exit_rect, bus)
        self.phenomenon = phenomenon
        self.box = box
        self.mount = mount
        self.uno = uno
        self.dos = dos
        self.observed = False

    def try_transform(self, actor, transform):
        if self.box is None:
            return False
        if self.phenomenon is None or not self.phenomenon.frozen:
            if self.bus is not None:
                self.bus.emit("ROOM_DENIED", {"room": self.room_id, "actor": actor})
            return False
        return bool(transform.request(actor, self.box))

    def _ready(self):
        if self.phenomenon is None or self.box is None or self.mount is None:
            return False
        return self.observed and self.box.is_transformed and self.mount.mounted

    def update(self, dt):
        if self.state == self.COMPLETED:
            return self.state
        if self.phenomenon is not None and self.phenomenon.frozen:
            self.observed = True
        if self._ready() and self.duo_in_exit(self.uno, self.dos):
            return self._complete()
        if self.observed:
            self.state = self.READY
        return self.state


class _AlwaysStill:
    frozen = True
