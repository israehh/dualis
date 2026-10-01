"""Validación F0 derivada del lenguaje: foco, doble salida, una idea.

Recibe diccionarios simples, no carga habitaciones del Vestíbulo.
Devuelve lista de errores; vacía significa válida.
"""


def validate_room_dict(room):
    errors = []
    if not room.get("focus"):
        errors.append("sin-foco")
    exits = room.get("exits", [])
    if len(exits) < 2:
        errors.append("menos-de-dos-salidas")
    ideas = room.get("ideas", [])
    if len(ideas) != 1:
        errors.append("requiere-una-idea")
    return errors
