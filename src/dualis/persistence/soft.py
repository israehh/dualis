"""Persistencia suave F24: solo la room actual. Sin savegames complejos.

Guarda únicamente (room, prev): dónde está el jugador y de dónde vino
para mantener la dirección del tránsito. Nada de entidades, runtimes,
inventario ni progreso: el progreso vive en el mundo, no en el fichero.
"""

import json
import os


def save_soft(path, room, prev=None):
    """Escribe la room actual de forma atómica (tmp + replace)."""
    text = json.dumps({"room": room, "prev": prev}, sort_keys=True)
    tmp = "%s.tmp" % path
    with open(tmp, "w", encoding="utf-8") as handle:
        handle.write(text)
    os.replace(tmp, path)


def load_soft(path):
    """Lee la room actual o (None, None) si falta o está corrupta."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            raw = json.load(handle)
        room = raw.get("room")
        prev = raw.get("prev")
        if not isinstance(room, str) or not room:
            return (None, None)
        if prev is not None and not isinstance(prev, str):
            return (None, None)
        return (room, prev)
    except (OSError, ValueError, AttributeError):
        return (None, None)
