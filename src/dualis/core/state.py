"""Gestor de modo F0: solo transiciones concedidas. Sin gameplay."""
try:
    from dualis import config
except ImportError:
    from src.dualis import config

_ALLOWED = {
    "BOOT": ("RUNNING",),
    "RUNNING": ("SHUTDOWN",),
    "SHUTDOWN": (),
}


class StateManager:
    def __init__(self):
        self.state = "BOOT"

    def request(self, nxt):
        if nxt in _ALLOWED.get(self.state, ()):
            self.state = nxt
            return True
        return False

    @staticmethod
    def known():
        return tuple(config.STATES)
