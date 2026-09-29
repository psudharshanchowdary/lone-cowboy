"""
Smooth scrolling 2D camera with deadzone, lookahead, level boundary clamping,
and screen shake support.
"""
import random
import pygame
from config import INTERNAL_WIDTH, INTERNAL_HEIGHT

class Camera:
    def __init__(self, viewport_width=INTERNAL_WIDTH, viewport_height=INTERNAL_HEIGHT):
        self.width = viewport_width
        self.height = viewport_height
        self.x = 0.0
        self.y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0
        self.level_width = viewport_width
        self.level_height = viewport_height

        # Lerp smoothing factors
        self.smooth_speed_x = 8.0
        self.smooth_speed_y = 6.0

        # Lookahead offset in direction player is moving/facing
        self.lookahead_dist = 28.0
        self.current_lookahead = 0.0

        # Screen shake
        self.shake_duration = 0.0
        self.shake_magnitude = 0.0
        self.shake_offset_x = 0.0
        self.shake_offset_y = 0.0

    def set_bounds(self, level_width_px, level_height_px):
        self.level_width = max(self.width, level_width_px)
        self.level_height = max(self.height, level_height_px)

    def trigger_shake(self, magnitude=3.0, duration=0.2):
        self.shake_magnitude = max(self.shake_magnitude, magnitude)
        self.shake_duration = max(self.shake_duration, duration)

    def update(self, target_rect, facing_right=True, dt=1.0/60.0):
        # Target lookahead
        desired_lookahead = self.lookahead_dist if facing_right else -self.lookahead_dist
        self.current_lookahead += (desired_lookahead - self.current_lookahead) * min(1.0, 5.0 * dt)

        # Center target on screen
        self.target_x = target_rect.centerx - self.width // 2 + self.current_lookahead
        self.target_y = target_rect.centery - self.height // 2

        # Smooth interpolation (lerp)
        self.x += (self.target_x - self.x) * min(1.0, self.smooth_speed_x * dt)
        self.y += (self.target_y - self.y) * min(1.0, self.smooth_speed_y * dt)

        # Clamp within level boundaries
        max_x = max(0.0, self.level_width - self.width)
        max_y = max(0.0, self.level_height - self.height)
        self.x = max(0.0, min(self.x, max_x))
        self.y = max(0.0, min(self.y, max_y))

        # Handle screen shake
        if self.shake_duration > 0.0:
            self.shake_duration -= dt
            decay = max(0.0, self.shake_duration)
            self.shake_offset_x = random.uniform(-self.shake_magnitude, self.shake_magnitude) * decay
            self.shake_offset_y = random.uniform(-self.shake_magnitude, self.shake_magnitude) * decay
        else:
            self.shake_offset_x = 0.0
            self.shake_offset_y = 0.0
            self.shake_magnitude = 0.0

    def apply(self, rect):
        """Returns a new Rect translated into screen coordinates."""
        draw_x = rect.x - int(self.x) + int(self.shake_offset_x)
        draw_y = rect.y - int(self.y) + int(self.shake_offset_y)
        return pygame.Rect(draw_x, draw_y, rect.width, rect.height)

    def apply_coords(self, world_x, world_y):
        """Translates world x,y to screen x,y."""
        draw_x = world_x - self.x + self.shake_offset_x
        draw_y = world_y - self.y + self.shake_offset_y
        return draw_x, draw_y
