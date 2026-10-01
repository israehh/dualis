"""Gestor F12: un runtime por habitación blueprint + aislamiento. Sin mecánicas nuevas.

Cada habitación activa solo usa sus actores: render filtrado, E enrutada
a su transformable y registro observable propio. El slice F7 queda intacto.
"""
try:
    from dualis.systems.observable import Observable, ObservableRegistry
    from dualis.systems.pattern_runtime import (
        ExamRuntime,
        HeightRuntime,
        ObserveToCrossRuntime,
        SharedPassageRuntime,
        TransformToReachRuntime,
    )
    from dualis.systems.transformable import Transformable
except ImportError:
    from src.dualis.systems.observable import Observable, ObservableRegistry
    from src.dualis.systems.pattern_runtime import (
        ExamRuntime,
        HeightRuntime,
        ObserveToCrossRuntime,
        SharedPassageRuntime,
        TransformToReachRuntime,
    )
    from src.dualis.systems.transformable import Transformable

TRAVELER_IDS = ("UNO", "DOS")


class RoomRuntimeManager:
    def __init__(self, bus=None, transform=None, mount=None, uno=None, dos=None):
        self.bus = bus
        self.transform = transform
        self.mount = mount
        self.uno = uno
        self.dos = dos
        self.runtimes = {}
        self.actor_ids = {}
        self.registries = {}
        self.empty_registry = ObservableRegistry()

    def register_actors(self, rid, actors):
        actors = list(actors)
        self.actor_ids[rid] = [a.id for a in actors]
        registry = ObservableRegistry()
        for actor in actors:
            if isinstance(actor, Observable):
                registry.register(actor)
        self.registries[rid] = registry

    def add_room(self, blueprint, actors):
        actors = list(actors)
        self.register_actors(blueprint.rid, actors)
        observables = [a for a in actors if isinstance(a, Observable)]
        boxes = [a for a in actors if isinstance(a, Transformable)]
        box = boxes[0] if boxes else None
        phenomenon = observables[0] if observables else None
        rid = blueprint.rid
        runtime = self._select(blueprint, phenomenon, box)
        if runtime is not None:
            self.runtimes[rid] = runtime
        return runtime

    def _select(self, blueprint, phenomenon, box):
        rid = blueprint.rid
        exit_rect = blueprint.exit_rect
        bus = self.bus
        uno, dos = self.uno, self.dos
        pattern = blueprint.pattern
        if pattern in ("PATTERN_OBSERVE_TO_CROSS", "PATTERN_TIMED_WINDOW"):
            if phenomenon is None:
                return None
            return ObserveToCrossRuntime(rid, exit_rect, bus, phenomenon, uno, dos)
        if pattern == "PATTERN_HEIGHT":
            return HeightRuntime(rid, exit_rect, bus, self.mount, uno, dos)
        if pattern == "PATTERN_TRANSFORM_TO_REACH":
            if box is None:
                return None
            if phenomenon is not None:
                return ExamRuntime(rid, exit_rect, bus, phenomenon, box, self.mount, uno, dos)
            return TransformToReachRuntime(rid, exit_rect, bus, box, uno, dos)
        if pattern == "PATTERN_SHARED_PASSAGE":
            if box is None:
                return None
            return SharedPassageRuntime(rid, exit_rect, bus, phenomenon, box, uno, dos)
        return None

    def runtime_for(self, rid):
        return self.runtimes.get(rid)

    def registry_for(self, rid):
        return self.registries.get(rid, self.empty_registry)

    def active_ids(self, rid):
        ids = set(TRAVELER_IDS)
        ids.update(self.actor_ids.get(rid, ()))
        return ids

    def try_transform(self, rid, actor):
        runtime = self.runtimes.get(rid)
        if runtime is None:
            return False
        return bool(runtime.try_transform(actor, self.transform))

    def update(self, dt, rid):
        runtime = self.runtimes.get(rid)
        if runtime is None:
            return None
        return runtime.update(dt)
