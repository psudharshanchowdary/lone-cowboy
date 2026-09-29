"""
Chapter 3 Enemy: Iron Mask Sniper.
Perches on high platforms or rooftops. Aims with a visible red laser sight telegraph,
then fires a deadly high-velocity bullet.
"""
import pygame
from config import COLOR_RED
from entities.enemies.enemy_base import EnemyBase
from weapons.projectile import Bullet
from gfx.particles import ParticleManager

class Sniper(EnemyBase):
    def __init__(self, x, y):
        super().__init__(x, y, width=12, height=22, max_health=2, enemy_type="sniper")
        self.patrol_speed = 20.0
        self.sight_range = 240.0
        self.attack_range = 230.0
        self.aim_delay = 0.75
        self.aim_timer = 0.0
        self.attack_cooldown = 2.2
        self.laser_target = None

    def update_ai(self, player, tilemap, dt):
        if not self.is_alive:
            self.laser_target = None
            return []

        new_bullets = []
        self.update_timers(dt)
        self.attack_timer = max(0.0, self.attack_timer - dt)

        dx = player.rect.centerx - self.rect.centerx
        sees_player = player.is_alive and self.has_line_of_sight(player, tilemap)

        if sees_player:
            self.facing_right = (dx > 0)
            self.patrol_dir = 1 if self.facing_right else -1
            self.vx = 0.0

            if self.attack_timer <= 0.0:
                self.state = "ALERT"
                self.aim_timer += dt
                # Target lock for laser line
                self.laser_target = (player.rect.centerx, player.rect.centery)

                if self.aim_timer >= self.aim_delay:
                    # Fire sniper round!
                    self.state = "ATTACK"
                    self.aim_timer = 0.0
                    self.attack_timer = self.attack_cooldown
                    self.laser_target = None

                    spawn_x = self.x + (16 if self.facing_right else -8)
                    spawn_y = self.y + 8
                    ParticleManager.get_instance().emit_muzzle_flash(spawn_x, spawn_y, self.facing_right)
                    bullet = Bullet(spawn_x, spawn_y, 1 if self.facing_right else -1, owner="enemy", damage=2)
                    bullet.vx *= 1.4  # extra fast sniper shot
                    new_bullets.append(bullet)
            else:
                self.laser_target = None
                self.state = "PATROL"
        else:
            self.laser_target = None
            self.aim_timer = 0.0
            self.state = "PATROL"
            if self.on_ground:
                if self.check_ledge_ahead(tilemap) or self.check_wall_ahead(tilemap):
                    self.patrol_dir = -self.patrol_dir

            self.vx = self.patrol_dir * self.patrol_speed
            self.facing_right = (self.patrol_dir > 0)

        self.apply_gravity(dt)
        self.move_and_slide(tilemap, dt)

        return new_bullets

    def draw(self, surface, camera):
        super().draw(surface, camera)

        # Draw red laser aim telegraph
        if self.laser_target and self.is_alive:
            origin_x = self.x + (14 if self.facing_right else -2)
            origin_y = self.y + 10
            sx, sy = camera.apply_coords(origin_x, origin_y)
            tx, ty = camera.apply_coords(self.laser_target[0], self.laser_target[1])
            # Laser intensity increases as aim timer nears fire threshold
            thickness = 2 if self.aim_timer > (self.aim_delay * 0.6) else 1
            pygame.draw.line(surface, COLOR_RED, (int(sx), int(sy)), (int(tx), int(ty)), thickness)
