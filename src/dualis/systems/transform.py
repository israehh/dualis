"""Transformar F6: DOS reinterpreta un objeto. Sin puzzles ni progresión."""


class TransformSystem:
    READY = "READY"
    TRANSFORMING = "TRANSFORMING"
    COOLDOWN = "COOLDOWN"

    TRANSFORM_TIME = 0.4

    def __init__(self, bus=None, transform_time=None, cooldown=4.0):
        self.bus = bus
        self.transform_time = transform_time if transform_time is not None else self.TRANSFORM_TIME
        self.cooldown_total = cooldown
        self.state = self.READY
        self.remaining = 0.0
        self.cooldown_remaining = 0.0
        self.target = None

    def request(self, actor, target):
        if actor != "DOS":
            return False
        if self.state != self.READY:
            return False
        if target is None or not getattr(target, "eligible", False):
            return False
        if getattr(target, "is_transformed", False):
            return False
        target.transform()
        self.target = target
        self.state = self.TRANSFORMING
        self.remaining = self.transform_time
        if self.bus is not None:
            self.bus.emit("TRANSFORM_STARTED", {"actor": actor})
        return True

    def update(self, dt):
        if self.state == self.TRANSFORMING:
            self.remaining -= dt
            if self.remaining <= 0.0:
                self.remaining = 0.0
                if self.bus is not None:
                    self.bus.emit("TRANSFORM_COMPLETED", {})
                self.state = self.COOLDOWN
                self.cooldown_remaining = self.cooldown_total
        elif self.state == self.COOLDOWN:
            self.cooldown_remaining -= dt
            if self.cooldown_remaining <= 0.0:
                self.cooldown_remaining = 0.0
                self.state = self.READY
                self.target = None
                if self.bus is not None:
                    self.bus.emit("TRANSFORM_READY", {})
        return self.state
