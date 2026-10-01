"""Constructor F10: plano → definición registrada + actores instanciados.

Reutiliza factory, biblioteca observable/transformable y RoomManager.
No duplica creación de entidades ni valida por su cuenta: delega.
"""
from dataclasses import dataclass

try:
    from dualis.world.blueprint import GLOBAL_POWERS
    from dualis.world.factory import create
    from dualis.world.room import RoomDefinition
except ImportError:
    from src.dualis.world.blueprint import GLOBAL_POWERS
    from src.dualis.world.factory import create
    from src.dualis.world.room import RoomDefinition


@dataclass
class BuiltRoom:
    blueprint: object
    definition: object
    actors: list


class RoomBuilder:
    def __init__(self, rooms):
        self.rooms = rooms

    def _specs(self, frozen_specs):
        return [{"kind": kind, "params": dict(params)} for kind, params in frozen_specs]

    def coverage(self, blueprint, pattern):
        provided = {kind for kind, _ in blueprint.observables}
        provided |= {kind for kind, _ in blueprint.transformables}
        concrete = [m for m in pattern.get("mechanics", []) if m not in GLOBAL_POWERS]
        if concrete and not any(m in provided for m in concrete):
            return list(concrete)
        return []

    def build(self, blueprint, pattern=None):
        if pattern is not None:
            missing = self.coverage(blueprint, pattern)
            if missing:
                raise ValueError("patrón sin cubrir %s: %s" % (blueprint.rid, ",".join(missing)))
        definition = RoomDefinition(
            rid=blueprint.rid,
            nombre=blueprint.nombre,
            descripcion="",
            enlaces=blueprint.enlaces,
        )
        self.rooms.register(definition)
        actors = [create(spec) for spec in (
            self._specs(blueprint.observables) + self._specs(blueprint.transformables)
        )]
        return BuiltRoom(blueprint, definition, actors)
