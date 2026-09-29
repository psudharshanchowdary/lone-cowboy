"""
Base Enemy Class for Lone Cowboy outlaws.
Provides patrol behavior with cliff/ledge edge detection, line-of-sight raycasting,
state machine (PATROL, ALERT, CHASE, ATTACK), and death particle bursts.
"""
import math
import pygame
from config import TILE_SIZE
from entities.entity import Entity
from gfx.sprites import SpriteManager
from gfx.particles import ParticleManager

class EnemyBase(Entity):
    def __init__(self, x, y, width=12, height=22, max_health=2, enemy_type="bandit"):
        super().__init__(x, y, width, height, max_health=max_health)
        self.enemy_type = enemy_type

        # AI States
        self.state = "PATROL"  # PATROL, ALERT, CHASE, ATTACK, RETREAT
        self.patrol_dir = 1
        self.patrol_speed = 45.0
        self.chase_speed = 75.0
        self.sight_range = 160.0
        self.attack_range = 100.0

        # Timers
        self.state_timer = 0.0
        self.attack_cooldown = 1.4
        self.attack_timer = 0.5
        self.anim_timer = 0.0
        self.anim_frame = 0

    def has_line_of_sight(self, target, tilemap):
        """Checks if a direct ray from enemy center to target center is clear of solid tiles."""
        dx = target.rect.centerx - self.rect.centerx
        dy = target.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        if dist > self.sight_range:
            return False

        # Raycast steps across grid
        steps = max(2, int(dist / (TILE_SIZE / 2)))
        for i in range(1, steps):
            t = i / steps
            check_x = self.rect.centerx + dx * t
            check_y = self.rect.centery + dy * t
            tile_col = int(check_x // TILE_SIZE)
            tile_row = int(check_y // TILE_SIZE)
            if tilemap.is_solid_at(tile_col, tile_row):
                return False

        return True

    def check_ledge_ahead(self, tilemap):
        """Checks if moving forward would step off an edge/cliff."""
        lookahead = 12 if self.patrol_dir > 0 else -12
        test_x = self.rect.centerx + lookahead
        test_y = self.rect.bottom + 4
        tile_col = int(test_x // TILE_SIZE)
        tile_row = int(test_y // TILE_SIZE)
        return not (tilemap.is_solid_at(tile_col, tile_row) or tilemap.is_platform_at(tile_col, tile_row))

    def check_wall_ahead(self, tilemap):
        """Checks if there's a solid block directly in front of enemy."""
        lookahead = 8 if self.patrol_dir > 0 else -8
        test_x = self.rect.centerx + lookahead
        tile_col = int(test_x // TILE_SIZE)
        tile_row = int(self.rect.centery // TILE_SIZE)
        return tilemap.is_solid_at(tile_col, tile_row)

    def update_ai(self, player, tilemap, dt):
        """Overridden by specific enemy types."""
        pass

    def take_damage(self, amount, knockback_x=0.0, knockback_y=0.0):
        damaged = super().take_damage(amount, knockback_x, knockback_y)
        if damaged and not self.is_alive:
            # Emit defeat particles
            ParticleManager.get_instance().emit_bullet_hit(self.rect.centerx, self.rect.centery, hit_wall=False)
            ParticleManager.get_instance().emit_dust(self.rect.centerx, self.rect.bottom)
        return damaged

    def draw(self, surface, camera):
        if not self.is_alive:
            return

        sprite_state = "shoot" if self.state == "ATTACK" else ("walk" if abs(self.vx) > 5 else "idle")
        sprite = SpriteManager.get_instance().get_enemy_sprite(
            enemy_type=self.enemy_type,
            state=sprite_state,
            facing_right=self.facing_right,
            frame=self.anim_frame
        )

        draw_rect = camera.apply(self.rect)
        sprite_y = draw_rect.bottom - sprite.get_height()
        sprite_x = draw_rect.centerx - sprite.get_width() // 2

        self.draw_flash_silhouette(surface, sprite, (sprite_x, sprite_y))
