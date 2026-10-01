"""Renderers F13.5: separan mundo lógico y presentación visual. Solo presentación.

Renderer2D dibuja la vista cenital actual. Un futuro renderer_iso.py
implementará los mismos tres métodos sin tocar lógica, escenas ni sistemas.
"""
import pygame


class Renderer2D:
    name = "2d"

    def render_world(self, scene, surface):
        scene.render_background(surface)
        scene.render_exits(surface)
        scene.render_entities(surface)
        scene.render_link(surface)

    def render_hud(self, scene, surface, fps=0.0):
        scene.render_hud_blocks(surface, fps)
        if getattr(scene, "debug", False):
            scene.render_debug_overlay(surface, fps)

    def render(self, scene, surface, fps=0.0):
        self.render_world(scene, surface)
        self.render_hud(scene, surface, fps)


DEFAULT_RENDERER = Renderer2D()


def draw_rect_outline(surface, color, rect, width=3):
    pygame.draw.rect(surface, color, pygame.Rect(*tuple(rect)), width)
