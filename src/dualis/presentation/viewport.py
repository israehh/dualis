"""Viewport F12.5: canvas lógico fijo + escalado con letterbox. Solo presentación."""
import pygame


def compute_view(window_w, window_h, logical_w=640, logical_h=360):
    scale = min(window_w / logical_w, window_h / logical_h)
    if scale <= 0:
        scale = 1.0
    draw_w = max(1, int(logical_w * scale))
    draw_h = max(1, int(logical_h * scale))
    offset_x = (window_w - draw_w) // 2
    offset_y = (window_h - draw_h) // 2
    return scale, offset_x, offset_y, draw_w, draw_h


def present(window, canvas):
    try:
        from dualis import config
    except ImportError:
        from src.dualis import config

    window_w, window_h = window.get_size()
    canvas_w, canvas_h = canvas.get_size()
    scale, ox, oy, dw, dh = compute_view(window_w, window_h, canvas_w, canvas_h)
    window.fill(config.BACKGROUND)
    if (dw, dh) == (canvas_w, canvas_h):
        window.blit(canvas, (ox, oy))
    else:
        window.blit(pygame.transform.smoothscale(canvas, (dw, dh)), (ox, oy))
    return scale, ox, oy, dw, dh
