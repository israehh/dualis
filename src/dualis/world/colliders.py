"""F22 — Colisiones físicas del escenario. Sin altura jugable.

Los elementos visuales de F20/F21 se vuelven geometría sólida cuando
corresponde. La elevación sigue siendo SOLO visual: no existe world_z
jugable, las plataformas no bloquean y ninguna mecánica nueva aparece
(sin pathfinding, IA, saltos ni escaleras).

Sólidos (bloquean a UNO y DOS):
  wall, pillar (muros y pilares F19) + column, block (elevación F20).
No sólidos:
  sombras, decoraciones, efectos, salida, vínculo y plataformas
  (plat_low / plat_mid / plat_high: solo visuales).

Integración: `move_with_collision()` aplica el desplazamiento por ejes
separados (primero X, luego Y): el eje bloqueado se cancela y el libre
avanza (deslizamiento), sin teletransporte ni atascos. `Entity.move()`
queda intacto; el bucle real (main.py) usa esta capa.

Compatibilidad: la geometría se deriva de los mismos specs que el
render (tiles.tall_tiles + tiles.elevation_tiles), filtrados contra el
exit_rect igual que el dibujo. Si un sólido tapara una solución, se
recoloca SOLO el decorado generado; los datos de rooms no se tocan.
"""

try:
    from dualis.presentation import tiles as _tiles
except ImportError:  # ejecución desde raíz sin paquete instalado
    from src.dualis.presentation import tiles as _tiles

__all__ = [
    "SOLID_KINDS", "NON_SOLID_ELEVATION", "WORLD_W", "WORLD_H",
    "solids_for", "collides", "move_with_collision",
]

# Bloquean movimiento. Las plataformas son visuales (F20) y la salida,
# las sombras y los efectos nunca bloquean.
SOLID_KINDS = ("wall", "pillar", "column", "block")
NON_SOLID_ELEVATION = ("plat_low", "plat_mid", "plat_high")

WORLD_W = 640.0
WORLD_H = 360.0


def solids_for(room_id, exit_rect=None):
    """AABBs sólidos (x, y, w, h) derivados del decorado generado.

    Misma fuente que el render: muros/pilares F19 + columnas/bloques
    F20, con el mismo filtro contra exit_rect (las salidas quedan
    libres). Las plataformas se excluyen siempre.
    """
    solids = []
    for spec in _tiles.tall_tiles(room_id, exit_rect):
        if spec.get("kind") in SOLID_KINDS:
            solids.append((float(spec["x"]), float(spec["y"]),
                           float(spec["w"]), float(spec["h"])))
    for spec in _tiles.elevation_tiles(room_id, exit_rect):
        if spec.get("kind") in SOLID_KINDS:
            solids.append((float(spec["x"]), float(spec["y"]),
                           float(spec["w"]), float(spec["h"])))
    return tuple(solids)


def collides(x, y, radius, solids):
    """True si el círculo (x, y, r) toca algún sólido (punto más cercano)."""
    r = float(radius)
    for sx, sy, sw, sh in solids:
        nearest_x = min(max(x, sx), sx + sw)
        nearest_y = min(max(y, sy), sy + sh)
        dx, dy = x - nearest_x, y - nearest_y
        if dx * dx + dy * dy < r * r:
            return True
    return False


def move_with_collision(entity, dx, dy, solids):
    """Desplaza a la entidad con deslizamiento por ejes separados.

    Intenta X y luego Y; el eje que colisionaría se cancela y el otro
    avanza. Nunca teletransporta (cada eje avanza como máximo lo pedido)
    y nunca atasca (los ejes se reintentan cada llamada). Además sujeta
    al actor dentro del mundo 640x360. Devuelve (x, y) finales.
    """
    dx, dy = float(dx), float(dy)
    radius = float(getattr(entity, "radius", 14))
    x, y = float(entity.x), float(entity.y)
    solids = tuple(solids or ())
    if dx:
        nx = x + dx
        if not collides(nx, y, radius, solids):
            x = nx
    if dy:
        ny = y + dy
        if not collides(x, ny, radius, solids):
            y = ny
    entity.x = min(max(x, radius), WORLD_W - radius)
    entity.y = min(max(y, radius), WORLD_H - radius)
    return (entity.x, entity.y)
