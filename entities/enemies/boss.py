"""
Chapter Bosses and Level 52 Boss Gauntlet Kingpin ("El Diablo").
Features multi-phase combat, special attack patterns (dashes, dynamite clusters,
revolver barrages), and a boss health bar interface.
"""
import random
import pygame
from config import COLOR_RED, COLOR_GOLD, COLOR_BLACK
from entities.enemies.enemy_base import EnemyBase
from weapons.projectile import Bullet, DynamiteStick
from gfx.sprites import SpriteManager
from gfx.particles import ParticleManager

class Boss(EnemyBase):
    def __init__(self, x, y, boss_name="Rattlesnake Jake", max_health=10):
        super().__init__(x, y, width=16, height=26, max_health=max_health, enemy_type="boss")
        self.boss_name = boss_name
        self.phase = 1
        self.patrol_speed = 50.0
        self.dash_speed = 170.0
        self.dash_timer = 0.0
        self.is_dashing = False
        self.attack_cooldown = 1.6
        self.attack_timer = 0.8
        self.special_cooldown = 4.0
        self.special_timer = 2.0

    def update_ai(self, player, tilemap, dt):
        if not self.is_alive:
            return [], []

        bullets = []
        dynamites = []
        self.update_timers(dt)
        self.attack_timer = max(0.0, self.attack_timer - dt)
        self.special_timer = max(0.0, self.special_timer - dt)

        # Check phase transition
        health_ratio = self.health / self.max_health
        if health_ratio <= 0.4 and self.phase < 2:
            self.phase = 2
            self.patrol_speed = 70.0
            self.attack_cooldown = 1.1

        dx = player.rect.centerx - self.rect.centerx
        dist_x = abs(dx)
        self.facing_right = (dx > 0)
        self.patrol_dir = 1 if self.facing_right else -1

        # Handle dashing state
        if self.is_dashing:
            self.dash_timer -= dt
            self.vx = self.patrol_dir * self.dash_speed
            ParticleManager.get_instance().emit_dust(self.rect.centerx, self.rect.bottom)
            if self.dash_timer <= 0.0:
                self.is_dashing = False
                self.vx = 0.0
        else:
            # Special attack trigger
            if self.special_timer <= 0.0 and player.is_alive:
                self.special_timer = self.special_cooldown
                if "Pete" in self.boss_name or "Diablo" in self.boss_name:
                    # Lob cluster dynamite
                    for spread in [-60.0, 0.0, 60.0]:
                        throw_dir = 1 if self.facing_right else -1
                        dyn = DynamiteStick(
                            self.rect.centerx, self.rect.top,
                            throw_dir * 140.0 + spread, -200.0,
                            owner="enemy", damage=3, radius=40.0
                        )
                        dynamites.append(dyn)
                else:
                    # Quick forward dash attack
                    self.is_dashing = True
                    self.dash_timer = 0.35

            # Normal attack (revolver burst)
            elif self.attack_timer <= 0.0 and player.is_alive and dist_x < 220.0:
                self.attack_timer = self.attack_cooldown
                self.state = "ATTACK"
                # Double bullet burst
                for offset_y in [6, 14]:
                    spawn_x = self.x + (18 if self.facing_right else -8)
                    spawn_y = self.y + offset_y
                    ParticleManager.get_instance().emit_muzzle_flash(spawn_x, spawn_y, self.facing_right)
                    bullets.append(Bullet(spawn_x, spawn_y, 1 if self.facing_right else -1, owner="enemy", damage=1))
            else:
                # Approach or reposition
                if dist_x > 110.0:
                    self.vx = self.patrol_dir * self.patrol_speed
                else:
                    self.vx = 0.0

        self.apply_gravity(dt)
        self.move_and_slide(tilemap, dt)
        return bullets, dynamites

    def draw_boss_bar(self, surface, screen_width=480):
        """Draws the boss health bar at the top of the screen."""
        if not self.is_alive:
            return

        bar_w = 160
        bar_h = 7
        bar_x = (screen_width - bar_w) // 2
        bar_y = 10

        # Background frame
        pygame.draw.rect(surface, COLOR_BLACK, (bar_x - 1, bar_y - 1, bar_w + 2, bar_h + 2))
        fill_w = int(bar_w * (self.health / self.max_health))
        pygame.draw.rect(surface, COLOR_RED, (bar_x, bar_y, fill_w, bar_h))
        pygame.draw.rect(surface, COLOR_GOLD, (bar_x - 1, bar_y - 1, bar_w + 2, bar_h + 2), 1)
