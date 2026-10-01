"""Puzzle F7: orquesta sistemas genéricos en la gramática del canon.

No es una mecánica nueva: solo ordena Observar → Transformar → Avanzar
con puertas lógicas y condición de éxito. Sin narrativa ni contenido extra.
"""

EXIT_RECT = (515, 35, 105, 85)
BRIDGE_RECT = (290, 150, 60, 40)


def _inside(rect, x, y):
    rx, ry, rw, rh = rect
    return rx <= x <= rx + rw and ry <= y <= ry + rh


class SlicePuzzle:
    SEALED = "SEALED"
    STILLED = "STILLED"
    BRIDGED = "BRIDGED"
    SOLVED = "SOLVED"

    def __init__(self, transform, phenomenon, testbox, uno, dos, bus=None):
        self.transform = transform
        self.phenomenon = phenomenon
        self.testbox = testbox
        self.uno = uno
        self.dos = dos
        self.bus = bus
        self.state = self.SEALED

    @property
    def exit_open(self):
        return self.testbox.is_transformed

    @property
    def can_transform(self):
        return self.phenomenon.frozen and not self.testbox.is_transformed

    def try_transform(self, actor):
        if not self.can_transform:
            if self.bus is not None:
                self.bus.emit("SLICE_DENIED", {"actor": actor})
            return False
        if not self.transform.request(actor, self.testbox):
            return False
        self.state = self.BRIDGED
        if self.bus is not None:
            self.bus.emit("SLICE_BRIDGED", {})
        return True

    def update(self, dt):
        if self.state == self.SEALED and self.phenomenon.frozen:
            self.state = self.STILLED
            if self.bus is not None:
                self.bus.emit("SLICE_STILLED", {})
        if self.state == self.BRIDGED and self.exit_open:
            if _inside(EXIT_RECT, self.uno.x, self.uno.y) and _inside(EXIT_RECT, self.dos.x, self.dos.y):
                self.state = self.SOLVED
                if self.bus is not None:
                    self.bus.emit("SLICE_SOLVED", {})
        return self.state
