"""F21 — Arte funcional generado por código. Solo presentación.

Sustituye la geometría abstracta por siluetas reconocibles SIN arte final
y SIN assets externos (todo pygame.draw). Lógica 100% cartesiana: la
animación (bobbing, pulsos, brillo) es puramente visual; ninguna mecánica
ni colisión cambia.

Lectura:
  UNO            -> observador/explorador vertical y ligero (túnica + capucha
                  + visor con lente; "piensa antes de actuar").
  DOS            -> soporte/constructora ancha y pesada (torso + hombreras
                  + casco con perno; "actúa antes de pensar").
  Observables    -> mecanismos/dispositivos fríos (carcasa + dientes + aguja).
  Transformables -> máquinas manipulables cálidas (bloque + pernos + palanca).
  Salidas        -> glifos por estado (candado / chevrones / anillos) + baliza.

Compatibilidad: los colores exactos exigidos por la serie F17-F20
(EXIT_COLORS, _EXIT_FILL/_EXIT_INNER, pedestal, elev_*, rejilla, HUD)
se siguen pintando con el mismo RGB y la misma geometría; los glifos
añaden píxeles con el MISMO color de estado para no romper la detección.
El contorno de salida se dibuja siempre el último (puro, sin alfa encima).
"""

try:
    from dualis.presentation import tiles as _tiles
except ImportError:  # ejecución desde raíz sin paquete instalado
    from src.dualis.presentation import tiles as _tiles

__all__ = [
    "bob",
    "draw_uno", "draw_dos",
    "draw_observable_mechanism", "draw_transformable_machine",
    "draw_exit_glyph", "draw_exit_beacon",
    "actor_accent",
]

import math


def bob(tick, amp=2.0, speed=0.25, phase=0.0):
    """Desplazamiento vertical suave en px. Solo visual."""
    return math.sin(tick * speed + phase) * amp


def actor_accent(region):
    """Detalle regional coherente (usa el trim de la paleta visual)."""
    return _tiles.palette_for(region).get("trim", (140, 130, 115))


def draw_uno(surface, cx, cy, radius, body, accent, tick):
    """UNO: observador vertical, ligero y elegante.

    Anclado en la base (cx, cy) = punto de suelo: anillo de apoyo + túnica
    estrecha que sube (~3.2r) + capucha + visor oscuro con lente brillante
    ("percepción/precisión"). Bufanda regional ondeando (respiración visual).

    Conserva los RGB exigidos: cuerpo (210,180,120), visor (30,28,38) y
    lente (235,240,250). El acento regional tiñe bufanda y base.
    Orden: halo -> anillo base -> túnica -> cabeza -> visor/lente -> bufanda.
    """
    import pygame
    r = max(2, int(round(radius)))
    breathe = math.sin(tick * 0.5)
    # Halo esbelto alrededor de la figura (no ensancha la base).
    halo = pygame.Surface((r * 3 + 8, r * 7 + 8), pygame.SRCALPHA)
    pygame.draw.ellipse(halo, (body[0], body[1], body[2], 30),
                        (4, 4, r * 3, r * 7))
    surface.blit(halo, (cx - (r * 3 + 8) // 2, cy - r * 7 - 8 + r * 2))
    dark = (30, 28, 38)
    # Anillo de apoyo: elipse fina con el acento regional (lectura de base).
    pygame.draw.ellipse(surface, accent, (cx - r, cy - 3, r * 2, 6), 1)
    # Túnica: polígono alto y estrecho (ancho ~1.2r, alto ~2.2r).
    sway = int(round(breathe))
    shoulder_y = cy - int(round(r * 2.2))
    base_y = cy - 2
    half_top = max(3, int(round(r * 0.45)))
    half_base = max(4, int(round(r * 0.65)) + (1 if breathe > 0.5 else 0))
    pygame.draw.polygon(surface, body,
                        [(cx - half_top + sway, shoulder_y),
                         (cx + half_top + sway, shoulder_y),
                         (cx + half_base, base_y),
                         (cx - half_base, base_y)])
    pygame.draw.polygon(surface, dark,
                        [(cx - half_top + sway, shoulder_y),
                         (cx + half_top + sway, shoulder_y),
                         (cx + half_base, base_y),
                         (cx - half_base, base_y)], 1)
    # Capucha / cabeza sobre los hombros (círculo color cuerpo).
    head_cy = shoulder_y - max(3, int(round(r * 0.45)))
    head_r = max(3, int(round(r * 0.55)))
    pygame.draw.circle(surface, body, (cx + sway, head_cy), head_r)
    pygame.draw.circle(surface, dark, (cx + sway, head_cy), head_r, 1)
    # Visor de observador: banda oscura + lente brillante pulsante.
    visor_h = max(3, head_r * 2 // 3)
    pygame.draw.rect(surface, dark,
                     (cx + sway - head_r + 1, head_cy - visor_h // 2,
                      (head_r - 1) * 2, visor_h))
    lens = 2 + int(round(1.0 + math.sin(tick * 0.35)))
    pygame.draw.circle(surface, (235, 240, 250),
                       (cx + sway, head_cy), max(1, lens))
    # Báculo de precisión: línea vertical fina con punta-lente.
    staff_x = cx + half_base + 2
    pygame.draw.line(surface, dark, (staff_x, cy - 2),
                     (staff_x, shoulder_y - head_r), 1)
    pygame.draw.circle(surface, (235, 240, 250),
                       (staff_x, shoulder_y - head_r - 1), 1)
    # Bufanda regional ondeando + mochila (garantizan acento visible).
    wave = int(round(math.sin(tick * 0.5 + 1.0) * 2.0))
    pygame.draw.polygon(surface, accent,
                        [(cx + sway - half_top, shoulder_y + 1),
                         (cx + sway - half_top - 6, shoulder_y + 4 + wave),
                         (cx + sway - half_top - 1, shoulder_y + 6)])
    pygame.draw.circle(surface, accent, (cx - half_base + 1, base_y - 3), 2)
    # Botas asentadas sobre la base (píxeles de identidad a ras de suelo:
    # la figura sigue leyéndose aunque la parte alta quede tras un bloque).
    for side in (-1, 1):
        boot = pygame.Rect(cx + side * 5 - 2, cy - 4, 4, 6)
        pygame.draw.rect(surface, body, boot)
        pygame.draw.rect(surface, dark, boot, 1)
    # Brillo superior de la capucha.
    pygame.draw.circle(surface, (255, 250, 235),
                       (cx + sway - head_r // 3, head_cy - head_r // 2), 1)


def draw_dos(surface, cx, cy, radius, body, accent, tick):
    """DOS: soporte ancho, pesado y estable ("actúa antes de pensar").

    Anclado en la base (cx, cy): plataforma de apoyo + torso macizo
    (~2.4r de ancho, ~1.3r de alto) + hombreras laterales + casco con
    perno central. Silueta opuesta a UNO: baja y ancha frente a alta y
    estrecha. Conserva el RGB base de DOS y tiñe contorno/remaches con
    el acento regional.
    """
    import pygame
    r = max(2, int(round(radius)))
    breathe = math.sin(tick * 0.5 + 2.0)
    lift = 0 if breathe > -0.9 else 1  # asentamiento pesado, casi inmóvil
    shade = tuple(max(0, c - 45) for c in body)
    # Plataforma de apoyo ancha (estabilidad) + sombra de contacto.
    pygame.draw.ellipse(surface, shade, (cx - r - 4, cy - 4, (r + 4) * 2, 8))
    pygame.draw.ellipse(surface, accent, (cx - r - 4, cy - 4, (r + 4) * 2, 8), 1)
    # Torso macizo.
    w = int(round(r * 2.4))
    h = int(round(r * 1.3))
    top = cy - h - 2 + lift
    rect = pygame.Rect(cx - w // 2, top, w, h)
    pygame.draw.rect(surface, body, rect, border_radius=3)
    pygame.draw.rect(surface, accent, rect, 2, border_radius=3)
    # Faja inferior pesada + cruceta de constructora.
    pygame.draw.rect(surface, shade,
                     (rect.left + 2, rect.bottom - 7, rect.width - 4, 5))
    pygame.draw.line(surface, shade,
                     (rect.left + 4, rect.centery), (rect.right - 4, rect.centery), 2)
    pygame.draw.line(surface, shade,
                     (cx, rect.top + 6), (cx, rect.bottom - 8), 2)
    # Hombreras laterales (anchura) con remaches regionales.
    pad_w, pad_h = max(4, r // 2 + 2), max(6, h - 4)
    for side in (-1, 1):
        pad_left = rect.right - 2 if side > 0 else rect.left - pad_w + 2
        pad = pygame.Rect(pad_left, top + 2, pad_w, pad_h)
        pygame.draw.rect(surface, body, pad, border_radius=2)
        pygame.draw.rect(surface, accent, pad, 1, border_radius=2)
        pygame.draw.circle(surface, accent, (pad.centerx, pad.centery), 1)
    # Casco: barra superior con ranura + perno central.
    pygame.draw.rect(surface, shade, (rect.left + 3, rect.top + 2, rect.width - 6, 5))
    pygame.draw.line(surface, (20, 26, 24),
                     (rect.left + 5, rect.top + 4), (rect.right - 5, rect.top + 4), 1)
    pygame.draw.circle(surface, accent, (cx, rect.top + 9), 3)
    pygame.draw.circle(surface, shade, (cx, rect.top + 9), 1)
    # Remaches de las esquinas del torso.
    for px, py in ((rect.left + 3, rect.bottom - 3), (rect.right - 3, rect.bottom - 3)):
        pygame.draw.circle(surface, accent, (px, py), 1)
    # Pies macizos a ras de suelo (identidad visible aun con solape alto).
    for side in (-1, 1):
        foot = pygame.Rect(cx + side * 11 - 4, cy - 3, 8, 5)
        pygame.draw.rect(surface, body, foot, border_radius=1)
        pygame.draw.rect(surface, accent, foot, 1, border_radius=1)
    # Pulso de trabajo tenue (no altera el color base).
    if int(tick * 0.35) % 4 == 0:
        pygame.draw.circle(surface, (235, 245, 245), (cx, rect.top + 9), 1)


def draw_observable_mechanism(surface, diamond, cx, cy, r, cold, core,
                              axle, rivet, accent, tick, frozen=False):
    """Mecanismo frío: carcasa + dientes + núcleo + aguja móvil + antena.

    `diamond` es el helper RendererISO._diamond. La carcasa conserva el
    color frío base; la aguja rota con el tick (movimiento ambiental).
    """
    import pygame
    r = max(3, int(round(r)))
    # Carcasa del dispositivo (color frío puro exigido por coherencia F19).
    diamond(surface, cold, cx, cy, r)
    # Dientes del mecanismo: 4 muescas en los vértices del rombo.
    tooth = tuple(max(0, c - 30) for c in cold)
    for dx, dy in ((0, -r), (r, 0), (0, r), (-r, 0)):
        pygame.draw.circle(surface, tooth, (cx + dx, cy + dy), 2)
    # Núcleo + eje.
    diamond(surface, core, cx, cy, max(2, int(r * 0.55)))
    pygame.draw.line(surface, axle, (cx - r, cy), (cx + r, cy), 2)
    # Aguja móvil (ángulo ambiental, sin mecánica).
    ang = tick * 0.9
    nx, ny = cx + int(round(math.cos(ang) * r * 0.8)), cy + int(round(math.sin(ang) * r * 0.4))
    pygame.draw.line(surface, rivet, (cx, cy), (nx, ny), 1)
    pygame.draw.circle(surface, rivet, (nx, ny), 1)
    # Antena del artefacto + remaches laterales.
    pygame.draw.line(surface, axle, (cx, cy - r), (cx, cy - r - 5), 1)
    pygame.draw.circle(surface, accent, (cx, cy - r - 6), 2)
    pygame.draw.circle(surface, rivet, (cx - r, cy), 1)
    pygame.draw.circle(surface, rivet, (cx + r, cy), 1)
    # Congelado: anillo de escarcha + destello.
    if frozen:
        diamond(surface, (230, 230, 240), cx, cy, r + 3, 1)
        diamond(surface, (200, 230, 245), cx, cy - 1, max(2, r - 4), 1)


def draw_transformable_machine(surface, diamond, cx, cy, radius, warm, edge,
                                top, accent, tick, transformed=False,
                                eligible=True):
    """Máquina cálida manipulable: bloque + pernos + palanca / motor.

    Paleta cálida frente al frío de los observables. La palanca indica
    "manipulable"; al transformarse se lee como motor compacto con brillo.
    """
    import pygame
    if transformed:
        # Motor compacto: tapa + núcleo + chispa orbital ambiental.
        diamond(surface, top, cx, cy, 10 + int(round(tick * 0.0)) + 2)
        diamond(surface, warm, cx, cy, 6)
        pygame.draw.circle(surface, edge, (cx, cy), 2)
        ang = tick * 1.3
        sx, sy = cx + int(round(math.cos(ang) * 8)), cy + int(round(math.sin(ang) * 4))
        pygame.draw.circle(surface, accent, (sx, sy), 1)
        pygame.draw.circle(surface, (255, 246, 220), (cx - 2, cy - 3), 1)
        return
    # Estructura sin transformar: bastidor + cuerpo + correas + palanca.
    diamond(surface, edge, cx, cy, 10, 2)
    diamond(surface, warm, cx, cy, 8)
    pygame.draw.line(surface, edge, (cx - 8, cy), (cx + 8, cy), 1)
    pygame.draw.line(surface, edge, (cx, cy - 4), (cx, cy + 4), 1)
    # Pernos del bastidor.
    for dx, dy in ((-8, 0), (8, 0), (0, -4), (0, 4)):
        pygame.draw.circle(surface, edge, (cx + dx, cy + dy), 1)
    # Palanca manipulable (lateral, con pomo de acento regional).
    pygame.draw.line(surface, edge, (cx + 8, cy), (cx + 12, cy - 5), 2)
    pygame.draw.circle(surface, accent, (cx + 12, cy - 5), 2)
    if eligible:
        diamond(surface, (230, 230, 240), cx, cy, 15, 1)


def draw_exit_beacon(surface, point, rect, exit_z, color, tick):
    """Baliza vertical sobre la salida: lectura a simple vista sin HUD.

    Se dibuja ANTES del relleno/contorno para no alterar sus RGB puros.
    Haz translúcido + punta brillante pulsante (mismo color de estado).
    """
    import pygame
    x, y, w, h = (float(v) for v in rect)
    cx, cy = x + w / 2.0, y + h / 2.0
    top_x, top_y = point(cx, cy, exit_z + 34.0)
    base_x, base_y = point(cx, cy, exit_z)
    width = max(3, int(w * 0.10))
    layer = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(layer, (color[0], color[1], color[2], 44),
                        [(base_x - width, base_y), (base_x + width, base_y),
                         (top_x + width // 2, top_y), (top_x - width // 2, top_y)])
    surface.blit(layer, (0, 0))
    pulse = 2 + int(round(1.5 * (0.5 + 0.5 * math.sin(tick * 0.35))))
    pygame.draw.circle(surface, color, (int(top_x), int(top_y)), pulse)


def draw_exit_glyph(surface, point, diamond, rect, exit_z, state, colors,
                    tick):
    """Glifo central por estado, con el MISMO color exigido por F17/F18.

    LOCKED: candado (arco + cuerpo) en verde. READY: doble chevrón en
    ámbar. COMPLETED: anillos + estrella en azul. Se dibujan sobre el
    relleno pero sin taparlo entero (los colores base siguen presentes).
    """
    import pygame
    x, y, w, h = (float(v) for v in rect)
    cx, cy = x + w / 2.0, y + h / 2.0
    ccx, ccy = point(cx, cy, exit_z)
    if state == "LOCKED":
        color = colors["LOCKED"]
        # Cuerpo del candado + arco (misma tinta verde -> test intacto).
        pygame.draw.rect(surface, color, (ccx - 5, ccy - 1, 10, 7), border_radius=1)
        pygame.draw.arc(surface, color, (ccx - 4, ccy - 8, 8, 8), math.pi, 2 * math.pi, 2)
        pygame.draw.circle(surface, (20, 26, 22), (ccx, ccy + 2), 1)
    elif state == "READY":
        color = colors["READY_INNER"]
        # Doble chevrón apuntando al centro (ámbar puro).
        off = int(round(2 + math.sin(tick * 0.35)))
        for k in (-1, 1):
            pygame.draw.lines(surface, color, False,
                              [(ccx - 6 + k * off, ccy - 4),
                               (ccx - 2 + k * off, ccy),
                               (ccx - 6 + k * off, ccy + 4)], 2)
    elif state == "COMPLETED":
        color = colors["COMPLETED_INNER"]
        # Anillos concéntricos + estrella (azul puro).
        diamond(surface, color, ccx, ccy, 8, 1)
        diamond(surface, color, ccx, ccy, 4, 1)
        pygame.draw.circle(surface, color, (ccx, ccy), 1)
