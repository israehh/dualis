"""Condición de vínculo F23/R4: predicado puro. No es un sistema.

No mueve, no bloquea, no emite, no renderiza. Solo lee `link.state` y
`link.distance` (LinkSystem F4, intacto) y decide si la salida de una
room acepta el estado actual del vínculo.

Las rooms LNK_* viven en data/link_rooms/, R4_05 y R4_EXAM en
data/r4_rooms/ y R5_04 en data/r5_rooms/; todas reutilizan patrones
existentes. Este módulo solo añade la puerta lógica CONNECTED/TENSION.
LIMIT nunca abre ninguna salida.
"""

try:
    from dualis.systems.link import LinkSystem
except ImportError:
    from src.dualis.systems.link import LinkSystem

REQUIREMENTS = {
    "LNK_01": LinkSystem.CONNECTED,
    "LNK_02": LinkSystem.TENSION,
    "LNK_03": LinkSystem.CONNECTED,
    "LNK_04": LinkSystem.CONNECTED,
    "R4_05": LinkSystem.TENSION,
    "R4_EXAM": LinkSystem.TENSION,
    "R5_04": LinkSystem.TENSION,
    "R5_EXAM": LinkSystem.TENSION,
}


def required_state(rid):
    return REQUIREMENTS.get(rid)


def link_allows(link, rid):
    """True si el vínculo está en el estado que exige la salida."""
    required = required_state(rid)
    if required is None:
        return False
    return link.state == required


def exit_allowed(runtime, link, rid):
    """True si el runtime completó Y el vínculo lo permite.

    El runtime (existente, sin modificar) decide LO demás; aquí solo
    se añade la condición de vínculo con los estados ya existentes.
    """
    if runtime is None:
        return False
    if getattr(runtime, "state", None) != getattr(runtime, "COMPLETED", "COMPLETED"):
        return False
    return link_allows(link, rid)
