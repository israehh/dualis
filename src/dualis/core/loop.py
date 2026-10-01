"""Paso fijo F0: acumula tiempo y cuenta pasos enteros. Sin lógica de juego."""
try:
    from dualis import config
except ImportError:
    from src.dualis import config


class FixedStep:
    def __init__(self):
        self.acc = 0.0
        self.ticks = 0

    def advance(self, dt):
        self.acc += dt
        steps = 0
        while self.acc >= config.TICK and steps < config.MAX_STEPS_PER_FRAME:
            self.acc -= config.TICK
            self.ticks += 1
            steps += 1
        if self.acc >= config.TICK:
            self.acc = 0.0
        return steps
