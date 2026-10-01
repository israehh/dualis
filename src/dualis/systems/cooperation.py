"""Cooperación F9: sistema de acciones duales. Montar es la primera.

Futuras acciones (lanzar, puente) se registran aquí sin tocar el ciclo.
"""
import math


class CooperationSystem:
    def __init__(self, bus=None):
        self.bus = bus
        self._actions = {}

    def register(self, name, action):
        self._actions[name] = action
        return action

    def action(self, name):
        return self._actions.get(name)

    def update(self, dt):
        for action in self._actions.values():
            if hasattr(action, "update"):
                action.update(dt)


class MountAction:
    UNO_NORMAL = "NORMAL"
    UNO_MOUNTED = "MOUNTED"
    DOS_NORMAL = "NORMAL"
    DOS_CARRYING = "CARRYING"

    PROXIMITY = 56.0
    LIFT = 44.0
    STEP_ASIDE = 26.0

    def __init__(self, uno, dos, bus=None):
        self.uno = uno
        self.dos = dos
        self.bus = bus
        self.uno_state = self.UNO_NORMAL
        self.dos_state = self.DOS_NORMAL

    @property
    def mounted(self):
        return self.uno_state == self.UNO_MOUNTED

    def distance(self):
        return math.hypot(self.uno.x - self.dos.x, self.uno.y - self.dos.y)

    def can_mount(self):
        return not self.mounted and self.distance() <= self.PROXIMITY

    def request(self, actor):
        if actor != "UNO":
            return False
        if self.mounted:
            self._dismount()
            if self.bus is not None:
                self.bus.emit("MOUNT_ENDED", {})
            return True
        if not self.can_mount():
            return False
        self.uno_state = self.UNO_MOUNTED
        self.dos_state = self.DOS_CARRYING
        self._pin()
        if self.bus is not None:
            self.bus.emit("MOUNT_STARTED", {})
        return True

    def _pin(self):
        self.uno.x = self.dos.x
        self.uno.y = self.dos.y - self.LIFT

    def _dismount(self):
        self.uno_state = self.UNO_NORMAL
        self.dos_state = self.DOS_NORMAL
        self.uno.x = self.dos.x + self.STEP_ASIDE
        self.uno.y = self.dos.y

    def reach_top(self):
        return self.uno.y - self.uno.radius

    def update(self, dt):
        if self.mounted:
            self._pin()
        return self.mounted
