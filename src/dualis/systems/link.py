"""Vínculo F4: mide, clasifica y comunica. No mueve, no bloquea, no daña."""
import math


class LinkSystem:
    CONNECTED = "CONNECTED"
    TENSION = "TENSION"
    LIMIT = "LIMIT"

    def __init__(self, entities, bus=None, tension_at=240.0, limit_at=320.0,
                 release_tension=210.0, release_limit=290.0):
        self.entities = entities
        self.bus = bus
        self.tension_at = tension_at
        self.limit_at = limit_at
        self.release_tension = release_tension
        self.release_limit = release_limit
        self.state = self.CONNECTED
        self.distance = 0.0

    def measure(self):
        uno = self.entities.get("UNO")
        dos = self.entities.get("DOS")
        if uno is None or dos is None:
            return None
        return math.hypot(uno.x - dos.x, uno.y - dos.y)

    def _classify(self, d):
        if self.state == self.CONNECTED:
            if d >= self.limit_at:
                return self.LIMIT
            if d >= self.tension_at:
                return self.TENSION
            return self.CONNECTED
        if self.state == self.TENSION:
            if d >= self.limit_at:
                return self.LIMIT
            if d <= self.release_tension:
                return self.CONNECTED
            return self.TENSION
        if d <= self.release_limit:
            return self.TENSION
        return self.LIMIT

    def update(self, dt):
        d = self.measure()
        if d is None:
            return self.state
        self.distance = d
        nxt = self._classify(d)
        if nxt != self.state:
            self.state = nxt
            if self.bus is not None:
                self.bus.emit("LINK_" + nxt, {"state": nxt, "distance": d})
        return self.state
