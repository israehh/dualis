"""Tránsitos F24+F28: la cadena R1→R2→R3→R4 como mundo navegable.

Decisiones puras e instantáneas de actores. Solo lee lo existente
(runtimes, puzzle, enlaces, sólidos): no toca systems/, render,
colliders, lenguaje ni exámenes. Sin teleports, hubs ni inventario:
el destino siempre es un enlace declarado y la entrada es coherente
y segura (fuera de la salida, sin sólidos, vínculo en CONNECTED).

F28: decide_transit acepta link opcional. Sin link todo sigue idéntico
(F24–F27 intactos); con link, las rooms con puerta lógica declarada en
world/link_gate.py solo transitan en el estado exigido (R4_05 y R4_EXAM
piden TENSION, LIMIT nunca abre). Las rooms sin puerta declarada
transitan igual con o sin link.
"""

ENTRY_PAIRS = (
    ((120.0, 280.0), (220.0, 280.0)),
    ((420.0, 280.0), (520.0, 280.0)),
    ((120.0, 90.0), (220.0, 90.0)),
    ((420.0, 90.0), (520.0, 90.0)),
    ((320.0, 300.0), (420.0, 300.0)),
)

BOUNDS = (640.0, 360.0)
RADIUS = 14.0


def _inside(exit_rect, x, y):
    if exit_rect is None:
        return False
    ex, ey, ew, eh = exit_rect
    return ex <= x <= ex + ew and ey <= y <= ey + eh


def _point_safe(point, exit_rect, solids):
    from dualis.world.colliders import collides
    x, y = point
    if not (RADIUS <= x <= BOUNDS[0] - RADIUS):
        return False
    if not (RADIUS <= y <= BOUNDS[1] - RADIUS):
        return False
    if _inside(exit_rect, x, y):
        return False
    return not collides(x, y, RADIUS, solids)


def _pair_safe(pair, exit_rect, solids):
    return all(_point_safe(p, exit_rect, solids) for p in pair)


def _stable_index(from_rid, count):
    if not from_rid or count <= 1:
        return 0
    return sum(ord(c) for c in str(from_rid)) % count


def entry_for(exit_rect, solids, from_rid=None):
    """Par de entrada (UNO, DOS) según el enlace de llegada.

    Determinista para el mismo (destino, origen): el mismo enlace
    siempre deja al dúo en el mismo sitio seguro.
    """
    safe = [pair for pair in ENTRY_PAIRS if _pair_safe(pair, exit_rect, solids)]
    if not safe:
        return ENTRY_PAIRS[0]
    return safe[_stable_index(from_rid, len(safe))]


def next_room(enlaces_map, rid, prev):
    """Siguiente room por enlaces, con memoria de dirección.

    Avanza al primer enlace distinto del origen; en fondo de saco
    (TAL_09) o destino desconocido devuelve None: quedarse.
    """
    links = list(enlaces_map.get(rid, ()))
    if not links:
        return None
    if prev in links:
        rest = [e for e in links if e != prev]
        nxt = rest[0] if rest else None
    else:
        nxt = links[0]
    if nxt is None or nxt not in enlaces_map:
        return None
    return nxt


def slice_exit_target(blueprints):
    """Destino al resolver ROOM_SLICE: quien declare ese enlace, R1 primero."""
    cands = sorted(rid for rid, bp in blueprints.items() if "ROOM_SLICE" in bp.enlaces)
    if not cands:
        return None
    for cand in cands:
        if cand.startswith("VEST"):
            return cand
    return cands[0]


def snapshot_actors(actors):
    """Foto local de la room: posiciones y banderas, sin progreso global."""
    return {a.id: dict(vars(a)) for a in actors}


def restore_actors(actors, snap):
    """Reset local: restaura la foto sin tocar otras rooms ni runtimes."""
    for actor in actors:
        state = snap.get(actor.id)
        if state is None:
            continue
        vars(actor).clear()
        vars(actor).update(state)


def _link_allows(rid, link):
    """True si la puerta lógica de la room acepta el vínculo actual.

    Sin puerta declarada en link_gate.py siempre True: el gate solo
    cierra donde existe, nunca abre donde no hay.
    """
    try:
        from dualis.world.link_gate import required_state
    except ImportError:
        from src.dualis.world.link_gate import required_state
    required = required_state(rid)
    if required is None:
        return True
    return link.state == required


def duo_in_rect(rect, uno, dos):
    if rect is None:
        return False
    return _inside(rect, uno.x, uno.y) and _inside(rect, dos.x, dos.y)


def decide_transit(current, prev, enlaces_map, runtimes, puzzle, uno, dos,
                   blueprints, link=None):
    """Destino del tránsito automático o None si hay que quedarse.

    link es opcional (F28): sin link el comportamiento es el de F24;
    con link, las rooms con puerta lógica declarada solo transitan en
    el estado exigido.
    """
    if current == "ROOM_SLICE":
        if puzzle is None or getattr(puzzle, "state", None) != "SOLVED":
            return None
        try:
            from dualis.systems.slice_puzzle import EXIT_RECT
        except ImportError:
            from src.dualis.systems.slice_puzzle import EXIT_RECT
        if not duo_in_rect(EXIT_RECT, uno, dos):
            return None
        target = slice_exit_target(blueprints)
        return target if target in enlaces_map else None
    runtime = runtimes.runtime_for(current) if runtimes is not None else None
    if runtime is None:
        return None
    if getattr(runtime, "state", None) != getattr(runtime, "COMPLETED", "COMPLETED"):
        return None
    if not duo_in_rect(getattr(runtime, "exit_rect", None), uno, dos):
        return None
    if link is not None and not _link_allows(current, link):
        return None
    return next_room(enlaces_map, current, prev)
