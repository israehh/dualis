"""F20: tiles isométricos, elevación visual y ambientación por región.

Solo presentación. Lógica 100% cartesiana: no existe eje Z jugable.
La elevación es exclusivamente visual (desplazamiento -z en pantalla).

Tipos base (F19): floor (mosaico), wall (muro), pillar (torre), platform.
Tipos F20 (elevación): plat_low / plat_mid / plat_high (plataformas baja,
media y alta), column (columna), block (bloque elevado).
Cada elemento elevado muestra cara superior + izquierda + derecha (iso 2:1).

Sin tocar datos: los tiles se derivan del id de sala y del exit_rect.
El exit_rect solo sirve para NO tapar la salida (filtro visual).

Regiones:
  R1 Vestíbulo  = piedra
  R2 Biblioteca = estanterías / mesas / archivadores (mismo volumen, detalle papel)
  R3 Taller     = maquinaria / prensa / pilares industriales (mismo volumen, detalle óxido)
Todo generado con geometría. Sin assets externos.
"""

__all__ = [
    "FLOOR_STEP_X", "FLOOR_STEP_Y",
    "WALL_Z", "PILLAR_Z",
    "LOW_Z", "MID_Z", "HIGH_Z", "COLUMN_Z", "BLOCK_Z", "ELEVATION_Z",
    "ELEVATION_KINDS",
    "PALETTES", "region_of", "palette_for",
    "iter_floor_tiles", "tall_tiles",
    "elevation_tiles", "is_elevation_spec", "tile_depth", "elevation_depth",
    "shade",
    "draw_floor", "draw_box", "draw_platform",
    "draw_elevated", "draw_elevation_shadow",
]

FLOOR_STEP_X = 40.0
FLOOR_STEP_Y = 20.0

WALL_Z = 26.0
PILLAR_Z = 40.0

# F20 — alturas puramente visuales. Sin efecto en gameplay ni colisiones.
LOW_Z = 12.0
MID_Z = 24.0
HIGH_Z = 36.0
COLUMN_Z = 56.0
BLOCK_Z = 20.0

ELEVATION_Z = {
    "plat_low": LOW_Z,
    "plat_mid": MID_Z,
    "plat_high": HIGH_Z,
    "column": COLUMN_Z,
    "block": BLOCK_Z,
}

ELEVATION_KINDS = tuple(ELEVATION_Z.keys())

PALETTES = {
    # R1: piedra clara (grises cálidos claros sobre fondo oscuro).
    "R1": {
        "floor": (56, 54, 66),
        "floor_alt": (63, 61, 73),
        "wall_top": (118, 114, 104),
        "wall_left": (78, 74, 68),
        "wall_right": (64, 60, 56),
        "pillar_top": (132, 128, 116),
        "pillar_side": (84, 80, 72),
        "platform": (72, 68, 60),
        "trim": (150, 144, 130),
        # F20 elevación R1: piedra.
        "elev_top": (124, 120, 110),
        "elev_left": (84, 80, 74),
        "elev_right": (68, 64, 60),
        "detail": (50, 48, 56),
    },
    # R2: papel / biblioteca (ocres papel).
    "R2": {
        "floor": (66, 60, 46),
        "floor_alt": (73, 67, 52),
        "wall_top": (158, 144, 108),
        "wall_left": (104, 92, 66),
        "wall_right": (88, 78, 56),
        "pillar_top": (178, 162, 122),
        "pillar_side": (112, 98, 70),
        "platform": (90, 78, 56),
        "trim": (200, 182, 140),
        # F20 elevación R2: papel / madera (mismo volumen, otro detalle).
        "elev_top": (170, 150, 110),
        "elev_left": (112, 96, 68),
        "elev_right": (94, 80, 58),
        "detail": (60, 50, 36),
    },
    # R3: taller / óxido (cobres quemados).
    "R3": {
        "floor": (68, 48, 38),
        "floor_alt": (75, 55, 43),
        "wall_top": (158, 114, 72),
        "wall_left": (104, 74, 48),
        "wall_right": (88, 62, 40),
        "pillar_top": (184, 132, 82),
        "pillar_side": (116, 82, 54),
        "platform": (92, 64, 44),
        "trim": (210, 150, 96),
        # F20 elevación R3: óxido / metal (mismo volumen, otro detalle).
        "elev_top": (172, 124, 78),
        "elev_left": (112, 78, 50),
        "elev_right": (94, 66, 42),
        "detail": (48, 32, 22),
    },
}


def region_of(room_id):
    """Prefijo de sala -> región visual. Por defecto R1. Solo render."""
    rid = str(room_id or "")
    if rid.startswith("BIB"):
        return "R2"
    if rid.startswith("TAL"):
        return "R3"
    return "R1"


def palette_for(region):
    """Paleta de la región. Sin assets externos."""
    return PALETTES.get(region, PALETTES["R1"])


def iter_floor_tiles(w=640.0, h=360.0):
    """Centros del mosaico de suelo cubriendo el mundo lógico."""
    y = FLOOR_STEP_Y / 2.0
    row = 0
    while y < h:
        off = FLOOR_STEP_X / 2.0 if (row % 2) else 0.0
        x = FLOOR_STEP_X / 2.0 + off
        while x < w:
            yield (x, y, (row + int(x // FLOOR_STEP_X)) % 2 == 0)
            x += FLOOR_STEP_X
        y += FLOOR_STEP_Y / 2.0
        row += 1


def tall_tiles(room_id, exit_rect=None):
    """Tiles altos deterministas: muros norte/oeste, pilares lejanos y
    plataforma de salida. La esquina cercana (SE) queda abierta a cámara."""
    specs = []
    # Muro norte (borde y=0): detrás de casi todo.
    x = 60.0
    while x < 580.0:
        specs.append({"kind": "wall", "x": x, "y": 0.0, "w": 60.0,
                      "h": 22.0, "z": WALL_Z})
        x += 65.0
    # Muro oeste (borde x=0).
    y = 60.0
    while y < 300.0:
        specs.append({"kind": "wall", "x": 0.0, "y": y, "w": 22.0,
                      "h": 56.0, "z": WALL_Z})
        y += 60.0
    # Pilares en esquinas lejanas (nunca delante de la salida).
    for px, py in ((40.0, 40.0), (600.0, 40.0), (40.0, 320.0)):
        specs.append({"kind": "pillar", "x": px - 14.0, "y": py - 14.0,
                      "w": 28.0, "h": 28.0, "z": PILLAR_Z})
    # Plataforma bajo la salida (misma huella, plana).
    if exit_rect is not None:
        ex, ey, ew, eh = (float(v) for v in exit_rect)
        specs.append({"kind": "platform", "x": ex, "y": ey,
                      "w": ew, "h": eh, "z": 0.0})
    return specs


def tile_depth(spec):
    """Clave de profundidad: frente-abajo-centro + altura visual."""
    return spec["x"] + spec["w"] / 2.0 + spec["y"] + spec["h"] + spec["z"]


def elevation_depth(spec):
    """Alias F20: misma clave que tile_depth para elementos elevados."""
    return tile_depth(spec)


def is_elevation_spec(spec):
    """True si el spec es elevación visual F20 (z jugable = 0 siempre)."""
    try:
        return str(spec.get("kind")) in ELEVATION_Z
    except AttributeError:
        return False


def shade(color, factor):
    """Aclarar/oscurecer un color RGB. factor>1 aclara, <1 oscurece."""
    r, g, b = (int(v) for v in tuple(color)[:3])
    if factor >= 1.0:
        f = factor - 1.0
        return (int(r + (255 - r) * min(1.0, f)),
                int(g + (255 - g) * min(1.0, f)),
                int(b + (255 - b) * min(1.0, f)))
    return (max(0, int(r * factor)), max(0, int(g * factor)),
            max(0, int(b * factor)))


def _room_hash(room_id):
    """Hash determinista estable (suma ponderada, sin random de Python)."""
    total = 0
    for index, ch in enumerate(str(room_id or "")):
        total += (ord(ch) * (31 + index)) % 4096
    return total


def _rects_overlap(a, b, margin=0.0):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return not (ax + aw + margin <= bx - margin or
                bx + bw + margin <= ax - margin or
                ay + ah + margin <= by - margin or
                by + bh + margin <= ay - margin)


def elevation_tiles(room_id, exit_rect=None):
    """Decorado elevado F20: determinista por sala, nunca sobre la salida.

    Cinco piezas como máximo: plat_low / plat_mid / plat_high / column /
    block. Posiciones base elegidas para evitar las salidas conocidas
    (SLICE, VEST_01, BIB_01, TAL_01); además se aplica jitter determinista
    por sala (±8px) y filtro de solape contra exit_rect (+6px margen).
    La lógica no cambia: solo lectura espacial.
    """
    base = [
        ("plat_low", 140.0, 110.0, 110.0, 60.0),
        ("plat_mid", 350.0, 130.0, 110.0, 60.0),
        # plat_high desplazada a (300,180): su diedro izquierdo caía sobre
        # el punto de aparición de DOS (220,280) y lo ocultaba del todo.
        # (300,180) mantiene volumen, depth intermedia y evita las salidas
        # conocidas (SLICE/VEST_01/BIB_01/TAL_01 + jitter ±8).
        ("plat_high", 300.0, 180.0, 100.0, 60.0),
        ("column", 90.0, 80.0, 30.0, 30.0),
        ("block", 430.0, 220.0, 46.0, 46.0),
    ]
    h = _room_hash(room_id)
    specs = []
    exit_box = None
    if exit_rect is not None:
        try:
            exit_box = tuple(float(v) for v in exit_rect)
        except (TypeError, ValueError):
            exit_box = None
    for index, (kind, bx, by, bw, bh) in enumerate(base):
        dx = ((h + index * 37) % 17) - 8
        dy = ((h + index * 53) % 13) - 6
        x = min(600.0, max(4.0, bx + float(dx)))
        y = min(310.0, max(30.0, by + float(dy)))
        if exit_box is not None and _rects_overlap(
                (x, y, bw, bh), exit_box, margin=6.0):
            continue
        specs.append({"kind": kind, "x": x, "y": y, "w": bw, "h": bh,
                      "z": float(ELEVATION_Z[kind])})
    return specs


def draw_floor(surface, plot, palette, w=640.0, h=360.0):
    """Mosaico de suelo en damero con la paleta regional."""
    try:
        import pygame
    except ImportError:
        return
    hw, hh = FLOOR_STEP_X / 2.0, FLOOR_STEP_Y / 2.0
    for x, y, alt in iter_floor_tiles(w, h):
        color = palette["floor_alt"] if alt else palette["floor"]
        pygame.draw.polygon(surface, color,
                            [plot(x, y - hh), plot(x + hw, y),
                             plot(x, y + hh), plot(x - hw, y)])


def draw_box(surface, plot, spec, top, left, right, cap=None):
    """Bloque iso extrusionado: tapa + 2 caras sur visibles."""
    x, y, w, h, z = (spec["x"], spec["y"], spec["w"], spec["h"], spec["z"])
    p000 = plot(x, y, 0.0)
    p100 = plot(x + w, y, 0.0)
    p110 = plot(x + w, y + h, 0.0)
    p010 = plot(x, y + h, 0.0)
    p001 = plot(x, y, z)
    p101 = plot(x + w, y, z)
    p111 = plot(x + w, y + h, z)
    p011 = plot(x, y + h, z)
    try:
        import pygame
        pygame.draw.polygon(surface, left, [p011, p111, p110, p010])
        pygame.draw.polygon(surface, right, [p101, p111, p110, p100])
        pygame.draw.polygon(surface, top, [p001, p101, p111, p011])
        void = p000  # noqa: F841 (base oculta por el suelo, sin dibujar)
        if cap is not None:
            pygame.draw.polygon(surface, cap, [p001, p101, p111, p011], 1)
    except ImportError:
        pass


def draw_platform(surface, plot, rect, fill, edge):
    """Base plana bajo la salida + filete interior (sin tocar el contorno)."""
    x, y, w, h = (float(v) for v in rect)
    try:
        import pygame
        pygame.draw.polygon(surface, fill, [plot(x, y), plot(x + w, y),
                                            plot(x + w, y + h), plot(x, y + h)])
        cx, cy = x + w / 2.0, y + h / 2.0
        inset = 0.82
        pygame.draw.polygon(surface, edge,
                            [plot(cx + (x - cx) * inset, cy + (y - cy) * inset),
                             plot(cx + (x + w - cx) * inset, cy + (y - cy) * inset),
                             plot(cx + (x + w - cx) * inset, cy + (y + h - cy) * inset),
                             plot(cx + (x - cx) * inset, cy + (y + h - cy) * inset)], 1)
    except ImportError:
        pass


def draw_elevation_shadow(surface, plot, spec, alpha=90):
    """Sombra simple proyectada (+7,+5 lógicos). Sin luces ni dinámica.

    Dibuja la huella de base desplazada con negro translúcido + núcleo
    opaco de 2px para garantizar lectura sobre cualquier fondo.
    Con z<=0 no dibuja nada (devuelve False).
    """
    try:
        import pygame
    except ImportError:
        return False
    z = float(spec.get("z", 0.0))
    if z <= 0.0:
        return False
    x, y, w, h = (float(spec[k]) for k in ("x", "y", "w", "h"))
    ox, oy = 7.0, 5.0
    try:
        layer = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        pygame.draw.polygon(layer, (0, 0, 0, alpha),
                            [plot(x + ox, y + oy), plot(x + w + ox, y + oy),
                             plot(x + w + ox, y + h + oy),
                             plot(x + ox, y + h + oy)])
        surface.blit(layer, (0, 0))
    except (pygame.error, ValueError):
        return False
    # Núcleo opaco: lectura espacial garantizada.
    try:
        cx, cy = plot(x + w / 2.0 + ox, y + h / 2.0 + oy)
        pygame.draw.ellipse(surface, (0, 0, 0),
                            (int(cx) - 1, int(cy) - 1, 3, 2))
    except (pygame.error, ValueError):
        pass
    return True


def draw_elevated(surface, plot, spec, palette, region="R1"):
    """Elemento elevado F20: tapa + cara izquierda + cara derecha + detalle.

    Cara superior / izquierda / derecha con colores de paleta regional.
    Detalle geométrico por región (sin assets):
      R1 piedra: filete superior + grieta diagonal.
      R2 papel:  estantería (líneas de baldas) / mesa (filete) / archivador.
      R3 óxido:  remaches + rejilla superior (maquinaria/prensa/pilar).
    """
    try:
        import pygame
    except ImportError:
        return
    x, y, w, h, z = (float(spec[k]) for k in ("x", "y", "w", "h", "z"))
    kind = str(spec.get("kind", "block"))
    top, left, right = (palette["elev_top"], palette["elev_left"],
                        palette["elev_right"])
    detail = palette.get("detail", (0, 0, 0))
    trim = palette.get("trim", top)
    # Volumen base: 3 caras visibles.
    draw_box(surface, plot, {"x": x, "y": y, "w": w, "h": h, "z": z},
             top, left, right, cap=None)
    # Vértices reutilizados para el detalle.
    p001 = plot(x, y, z)
    p101 = plot(x + w, y, z)
    p111 = plot(x + w, y + h, z)
    p011 = plot(x, y + h, z)
    # Cara izquierda (sur-oeste) y derecha (sur-este) a nivel de base.
    p010 = plot(x, y + h, 0.0)
    p110 = plot(x + w, y + h, 0.0)
    p100 = plot(x + w, y, 0.0)
    cx_top = ((p001[0] + p111[0]) / 2.0, (p001[1] + p111[1]) / 2.0)
    if region == "R2":
        # Biblioteca: mismo volumen, lectura de mueble.
        if kind == "column":
            # Estantería alta: 3 baldas sobre ambas caras visibles.
            for t in (0.30, 0.55, 0.80):
                ax = (p011[0] + (p010[0] - p011[0]) * t,
                      p011[1] + (p010[1] - p011[1]) * t)
                bx = (p111[0] + (p110[0] - p111[0]) * t,
                      p111[1] + (p110[1] - p111[1]) * t)
                pygame.draw.line(surface, detail, ax, bx, 1)
                cx = ((p101[0] + (p100[0] - p101[0]) * t),
                      (p101[1] + (p100[1] - p101[1]) * t))
                dx = ((p111[0] + (p110[0] - p111[0]) * t),
                      (p111[1] + (p110[1] - p111[1]) * t))
                pygame.draw.line(surface, detail, cx, dx, 1)
        elif kind == "plat_low":
            # Mesa: filete interior sobre la tapa.
            inset = 0.78
            mx, my = cx_top
            pygame.draw.polygon(surface, trim,
                                [(mx + (p001[0] - mx) * inset,
                                  mx * 0 + (p001[1] - my) * inset + my),
                                 (mx + (p101[0] - mx) * inset,
                                  (p101[1] - my) * inset + my),
                                 (mx + (p111[0] - mx) * inset,
                                  (p111[1] - my) * inset + my),
                                 (mx + (p011[0] - mx) * inset,
                                  (p011[1] - my) * inset + my)], 1)
        else:
            # Archivador / isla: cajones (líneas + tiradores).
            for t in (0.38, 0.66):
                ax = (p011[0] + (p010[0] - p011[0]) * t,
                      p011[1] + (p010[1] - p011[1]) * t)
                bx = (p111[0] + (p110[0] - p111[0]) * t,
                      p111[1] + (p110[1] - p111[1]) * t)
                pygame.draw.line(surface, detail, ax, bx, 1)
            pygame.draw.circle(surface, trim,
                               (int(cx_top[0]), int(cx_top[1])), 2)
    elif region == "R3":
        # Taller: remaches en caras + rejilla en tapa.
        for t, s in ((0.25, 0.30), (0.55, 0.50), (0.80, 0.70)):
            lx = (p011[0] + (p010[0] - p011[0]) * t,
                  p011[1] + (p010[1] - p011[1]) * t)
            lx2 = (p011[0] + (p111[0] - p011[0]) * s + (p010[0] - p011[0]) * t * 0.0,
                   p011[1] + (p111[1] - p011[1]) * s * 0.0 + (p010[1] - p011[1]) * t)
            _ = lx2
            pygame.draw.circle(surface, trim, (int(lx[0]), int(lx[1])), 1)
            rx = (p101[0] + (p100[0] - p101[0]) * t,
                  p101[1] + (p100[1] - p101[1]) * t)
            pygame.draw.circle(surface, trim, (int(rx[0]), int(rx[1])), 1)
        # Rejilla superior: 2 líneas diagonales.
        pygame.draw.line(surface, detail,
                         ((p001[0] + p011[0]) / 2.0, (p001[1] + p011[1]) / 2.0),
                         ((p101[0] + p111[0]) / 2.0, (p101[1] + p111[1]) / 2.0), 1)
        pygame.draw.line(surface, detail,
                         ((p001[0] + p101[0]) / 2.0, (p001[1] + p101[1]) / 2.0),
                         ((p011[0] + p111[0]) / 2.0, (p011[1] + p111[1]) / 2.0), 1)
        if kind == "plat_high":
            # Prensa: marca central (pistón).
            pygame.draw.circle(surface, detail,
                               (int(cx_top[0]), int(cx_top[1])), 3, 1)
    else:
        # R1 piedra: filete + grieta.
        pygame.draw.polygon(surface, trim, [p001, p101, p111, p011], 1)
        pygame.draw.line(surface, detail,
                         ((p001[0] + p111[0]) / 2.0, (p001[1] + p111[1]) / 2.0),
                         (p111[0], p111[1]), 1)
