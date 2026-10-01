"""F18: proyección isométrica desacoplada. Solo presentación.

Lógica 100% cartesiana: la simulación nunca usa este módulo.
El render convierte (x, y) lógicos a pantalla isométrica 2:1.

    screen_x = (x - y)
    screen_y = (x + y) * 0.5 [- z visual]

`world_to_iso` / `iso_to_world` son inversas exactas en espacio
lógico sin escala. El escalado/offset a canvas lo aplica RendererISO.
"""

__all__ = ["raw", "world_to_iso", "iso_to_world", "LAYERS"]

LAYERS = ("ground", "objects", "actors", "effects", "ui")


def raw(wx, wy):
    """Proyección pura sin escala ni offset. Retorna (rx, ry)."""
    return (wx - wy), (wx + wy) * 0.5


def world_to_iso(x, y):
    """Cartesiano lógico -> isométrico lógico. Sin escala. Solo render."""
    return raw(x, y)


def iso_to_world(rx, ry):
    """Isométrico lógico -> cartesiano lógico. Inversa exacta de world_to_iso."""
    return (rx * 0.5 + ry), (ry - rx * 0.5)
