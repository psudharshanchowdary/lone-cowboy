"""
Font rendering helper with drop-shadow effects for retro aesthetic readability.
"""
import pygame
from config import COLOR_WHITE, COLOR_BLACK

class FontManager:
    _fonts = {}

    @classmethod
    def get_font(cls, size=14):
        if not pygame.font.get_init():
            pygame.font.init()
        if size not in cls._fonts:
            # None loads Pygame's built-in bitmap-styled font
            cls._fonts[size] = pygame.font.Font(None, size)
        return cls._fonts[size]

    @classmethod
    def draw_text(cls, surface, text, x, y, size=14, color=COLOR_WHITE, shadow=True, center=False):
        font = cls.get_font(size)
        text_surf = font.render(str(text), False, color)
        rect = text_surf.get_rect()

        if center:
            rect.center = (int(x), int(y))
        else:
            rect.topleft = (int(x), int(y))

        if shadow:
            shadow_surf = font.render(str(text), False, COLOR_BLACK)
            shadow_rect = rect.copy()
            shadow_rect.x += 1
            shadow_rect.y += 1
            surface.blit(shadow_surf, shadow_rect)

        surface.blit(text_surf, rect)
        return rect
