"""Habitaciones F2: definición, instancia y gestor. Sin entidades ni gameplay."""
import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class RoomDefinition:
    rid: str
    nombre: str
    descripcion: str = ""
    enlaces: tuple = ()


@dataclass
class RoomInstance:
    definition: RoomDefinition
    visits: int = 0


def validate_definition(data):
    errors = []
    if not data.get("id"):
        errors.append("sin-id")
    if not data.get("nombre"):
        errors.append("sin-nombre")
    enlaces = data.get("enlaces", None)
    if not isinstance(enlaces, list) or len(enlaces) < 1:
        errors.append("sin-enlaces")
    elif data.get("id") in enlaces:
        errors.append("auto-enlace")
    return errors


def load_definition(path):
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    errors = validate_definition(raw)
    if errors:
        raise ValueError("room inválida %s: %s" % (path, ",".join(errors)))
    return RoomDefinition(
        rid=raw["id"],
        nombre=raw["nombre"],
        descripcion=raw.get("descripcion", ""),
        enlaces=tuple(raw["enlaces"]),
    )


class RoomManager:
    def __init__(self, bus=None):
        self.bus = bus
        self.definitions = {}
        self.instances = {}
        self.current_id = None

    def load_directory(self, directory):
        for path in sorted(Path(directory).glob("*.json")):
            definition = load_definition(path)
            self.definitions[definition.rid] = definition
        return len(self.definitions)

    def register(self, definition):
        self.definitions[definition.rid] = definition
        return definition

    def enter(self, rid):
        if rid not in self.definitions:
            raise KeyError("room inexistente: %s" % rid)
        instance = self.instances.get(rid)
        if instance is None:
            instance = RoomInstance(self.definitions[rid])
            self.instances[rid] = instance
        instance.visits += 1
        self.current_id = rid
        if self.bus is not None:
            self.bus.emit("ROOM_ENTER", {"room": rid})
        return instance

    def current(self):
        if self.current_id is None:
            return None
        return self.instances[self.current_id]

    def neighbours(self, rid=None):
        target = rid if rid is not None else self.current_id
        if target is None:
            return ()
        return self.definitions[target].enlaces
