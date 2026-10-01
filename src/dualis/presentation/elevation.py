"""F20 — Arquitectura de elevación visual. Solo presentación.

REGLA PRINCIPAL: la lógica sigue siendo 100% cartesiana. No existe eje Z
jugable. La elevación es exclusivamente visual (desplazamiento -z en el
plot isométrico). Ningún sistema, runtime, gate, patrón, habitación ni
coordenada cambia por este módulo.

Capas:
  ground    -> mosaico + contorno + rejilla (tiles.draw_floor)
  objects   -> muros/pilares F19 (tiles.tall_tiles) + elevación F20
               (tiles.elevation_tiles). [(depth, draw)] con depth =
               x + w/2 + y + h + z visual.
  actors    -> salida, observables, transformables, UNO, DOS, vínculo.
  effects   -> eco READY + brillo de congelados.
  ui        -> HUD por bloques (escena).

FASE 1 — niveles visuales (tiles.ELEVATION_Z):
  plat_low  = 12.0 (plataforma baja)
  plat_mid  = 24.0 (plataforma media)
  plat_high = 36.0 (plataforma alta)
  column    = 56.0 (columna)
  block     = 20.0 (bloque elevado)

FASE 2 — caras visibles: cada elemento dibuja tapa (superior) + cara
  izquierda (sur-oeste) + cara derecha (sur-este), estilo isométrico
  clásico 2:1. Implementado en tiles.draw_elevated() sobre
  tiles.draw_box(), más detalle geométrico regional.

FASE 3 — sombras simples: tiles.draw_elevation_shadow() para pilares /
  plataformas / bloques (huella desplazada + núcleo opaco) y
  RendererISO.draw_shadow() para actores. Sin iluminación dinámica,
  sin luces. Solo lectura espacial.

FASE 4 — profundidad: objects F20 y actors comparten un único painter
  ordenado por depth. Un actor con (x+y) menor que el frente de un
  bloque se dibuja antes (pasa por detrás); con (x+y) mayor se dibuja
  después (pasa por delante). Ninguna colisión cambia.

FASE 5 — regionalización (misma geometría, distinto detalle):
  R1 piedra      -> filete + grieta (mundo con volumen pétreo).
  R2 biblioteca  -> column=estantería (baldas), plat_low=mesa (filete),
                    resto=archivador/isla (cajones).
  R3 taller      -> remaches + rejilla; plat_high=prensa (pistón),
                    column=pilar industrial.
  Todo con pygame.draw.*. Sin assets externos.

Compatibilidad: tall_tiles / tile_depth / draw_* F19 intactos. Los
  specs F20 se filtran contra exit_rect para no tapar salidas ni gates.
"""

try:
    from dualis.presentation import tiles as _tiles
except ImportError:  # ejecución desde raíz sin paquete instalado
    from src.dualis.presentation import tiles as _tiles

__all__ = [
    "LEVELS", "ARCHITECTURE",
    "specs_for", "depth_of", "is_elevated",
]

LEVELS = dict(_tiles.ELEVATION_Z)

ARCHITECTURE = (
    "cartesiano-siempre",
    "z-solo-visual",
    "painter-unico-x+y+z",
    "sombras-simples",
    "region-detalle-geometrico",
)


def specs_for(room_id, exit_rect=None):
    """Decorado elevado determinista para una sala. Solo lectura."""
    return _tiles.elevation_tiles(room_id, exit_rect)


def depth_of(spec):
    """Clave de profundidad visual (frente-abajo-centro + z)."""
    return _tiles.elevation_depth(spec)


def is_elevated(spec):
    """True si el spec pertenece a la elevación F20."""
    return _tiles.is_elevation_spec(spec)
