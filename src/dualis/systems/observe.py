"""Observar F5: UNO congela fenómenos 2s. Sin puzzles, sin habitaciones tocadas."""
try:
    from dualis.systems.observable import ObservableRegistry
except ImportError:
    from src.dualis.systems.observable import ObservableRegistry


class ObserveSystem:
    IDLE = "IDLE"
    OBSERVING = "OBSERVING"
    COOLDOWN = "COOLDOWN"

    DURATION = 2.0

    def __init__(self, registry=None, bus=None, duration=None, cooldown=3.0):
        self.registry = registry if registry is not None else ObservableRegistry()
        self.bus = bus
        self.duration = duration if duration is not None else self.DURATION
        self.cooldown_total = cooldown
        self.state = self.IDLE
        self.remaining = 0.0
        self.cooldown_remaining = 0.0

    @property
    def active(self):
        return self.state == self.OBSERVING

    def request(self, actor):
        if actor != "UNO":
            return False
        if self.state != self.IDLE:
            return False
        self.state = self.OBSERVING
        self.remaining = self.duration
        self.registry.set_all_frozen(True)
        if self.bus is not None:
            self.bus.emit("OBSERVE_STARTED", {"actor": actor, "duration": self.duration})
        return True

    def update(self, dt):
        if self.state == self.OBSERVING:
            self.remaining -= dt
            if self.remaining <= 0.0:
                self.remaining = 0.0
                self.registry.set_all_frozen(False)
                if self.bus is not None:
                    self.bus.emit("OBSERVE_FINISHED", {})
                self.state = self.COOLDOWN
                self.cooldown_remaining = self.cooldown_total
                if self.bus is not None:
                    self.bus.emit("OBSERVE_COOLDOWN_STARTED", {"cooldown": self.cooldown_total})
        elif self.state == self.COOLDOWN:
            self.cooldown_remaining -= dt
            if self.cooldown_remaining <= 0.0:
                self.cooldown_remaining = 0.0
                self.state = self.IDLE
                if self.bus is not None:
                    self.bus.emit("OBSERVE_READY", {})
        return self.state
