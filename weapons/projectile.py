"""
Projectiles and combat hitboxes: Bullets, Dynamite Sticks, and Melee Hitboxes.
"""
import math
import random
import pygame
from config import (
    GRAVITY, BULLET_SPEED, DYNAMITE_FUSE_TIME, DYNAMITE_DAMAGE,
    DYNAMITE_RADIUS, COLOR_GOLD, COLOR_WHITE
)
from gfx.sprites import SpriteManager
from gfx.particles import ParticleManager

class Bullet:
    def __init__(self, x, y, direction_x, owner="player", damage=1):
        self.x = float(x)
        self.y = float(y)
        self.direction = 1 if direction_x >= 0 else -1
        self.vx = self.direction * BULLET_SPEED
        self.vy = 0.0
        self.damage = damage
        self.owner = owner  # "player" or "enemy"
        self.width = 6
        self.height = 3
        self.alive = True
        self.lifetime = 1.6
        self.sprite = SpriteManager.get_instance().get_bullet_sprite()
        if self.direction < 0:
            self.sprite = pygame.transform.flip(self.sprite, True, False)

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def update(self, tilemap, dt):
        if not self.alive:
            return

        self.lifetime -= dt
        if self.lifetime <= 0.0:
            self.alive = False
            return

        self.x += self.vx * dt
        b_rect = self.rect

        # Check collision with solid tiles
        solid_tiles = tilemap.get_solid_tiles_near(b_rect)
        for tile in solid_tiles:
            if b_rect.colliderect(tile):
                self.alive = False
                hit_x = b_rect.right if self.direction > 0 else b_rect.left
                ParticleManager.get_instance().emit_bullet_hit(hit_x, b_rect.centery, hit_wall=True)
                return

    def check_hit(self, target):
        """Checks if this bullet hits an entity, applying damage and knockback."""
        if not self.alive or not target.is_alive:
            return False

        if self.rect.colliderect(target.rect):
            knockback_x = 120.0 * self.direction
            knockback_y = -60.0
            hit_success = target.take_damage(self.damage, knockback_x, knockback_y)
            if hit_success:
                self.alive = False
                ParticleManager.get_instance().emit_bullet_hit(self.rect.centerx, self.rect.centery, hit_wall=False)
                return True
        return False

    def draw(self, surface, camera):
        if not self.alive:
            return
        draw_rect = camera.apply(self.rect)
        surface.blit(self.sprite, draw_rect)


class DynamiteStick:
    def __init__(self, x, y, vx, vy, owner="player", damage=DYNAMITE_DAMAGE, radius=DYNAMITE_RADIUS):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.owner = owner
        self.damage = damage
        self.radius = radius
        self.width = 8
        self.height = 8
        self.fuse = DYNAMITE_FUSE_TIME
        self.alive = True
        self.frame = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def update(self, tilemap, dt):
        if not self.alive:
            return

        self.fuse -= dt
        self.frame += 1

        # Fuse spark emission
        if random.random() < 0.4:
            from gfx.particles import Particle
            spark_x = self.x + 5
            spark_y = self.y + 1
            ParticleManager.get_instance().particles.append(
                Particle(spark_x, spark_y, random.uniform(-10, 10), random.uniform(-25, -10),
                         color=COLOR_GOLD, radius=1.5, lifetime=0.15, shrink=True)
            )

        if self.fuse <= 0.0:
            self.explode(tilemap)
            return

        # Gravity & Physics
        self.vy += GRAVITY * 0.8 * dt

        # Horizontal movement and bouncing
        self.x += self.vx * dt
        d_rect = self.rect
        solid_tiles = tilemap.get_solid_tiles_near(d_rect)
        for tile in solid_tiles:
            if d_rect.colliderect(tile):
                self.vx = -self.vx * 0.55
                self.x = tile.left - self.width if self.vx < 0 else tile.right
                d_rect = self.rect

        # Vertical movement and bouncing
        self.y += self.vy * dt
        d_rect = self.rect
        solid_tiles = tilemap.get_solid_tiles_near(d_rect)
        for tile in solid_tiles:
            if d_rect.colliderect(tile):
                if self.vy > 0:
                    self.y = tile.top - self.height
                    self.vy = -self.vy * 0.45
                    self.vx *= 0.85 # ground friction
                elif self.vy < 0:
                    self.y = tile.bottom
                    self.vy = -self.vy * 0.45
                d_rect = self.rect

    def explode(self, tilemap, entities=None, camera=None):
        if not self.alive:
            return
        self.alive = False
        center_x = self.x + self.width / 2.0
        center_y = self.y + self.height / 2.0

        # Visual and camera shake feedback
        ParticleManager.get_instance().emit_explosion(center_x, center_y, self.radius)
        if camera:
            camera.trigger_shake(magnitude=5.0, duration=0.35)

        # Damage entities in blast radius
        if entities:
            for entity in entities:
                if not entity.is_alive:
                    continue
                dx = entity.rect.centerx - center_x
                dy = entity.rect.centery - center_y
                dist = math.hypot(dx, dy)
                if dist <= self.radius:
                    # Knockback pushed radially away from explosion
                    angle = math.atan2(dy, dx)
                    kb_x = math.cos(angle) * 220.0
                    kb_y = min(-120.0, math.sin(angle) * 200.0)
                    entity.take_damage(self.damage, kb_x, kb_y)

    def draw(self, surface, camera):
        if not self.alive:
            return
        sprite = SpriteManager.get_instance().get_dynamite_sprite(self.frame)
        draw_rect = camera.apply(self.rect)
        surface.blit(sprite, draw_rect)


class MeleeHitbox:
    def __init__(self, x, y, width, height, damage=2, owner="player", direction=1, knockback=220.0):
        self.rect = pygame.Rect(x, y, width, height)
        self.damage = damage
        self.owner = owner
        self.direction = direction
        self.knockback = knockback
        self.lifetime = 0.12  # quick slash window
        self.alive = True
        self.hit_entities = set()

    def update(self, dt):
        self.lifetime -= dt
        if self.lifetime <= 0.0:
            self.alive = False

    def check_hit(self, target):
        if not self.alive or not target.is_alive or target in self.hit_entities:
            return False

        if self.rect.colliderect(target.rect):
            self.hit_entities.add(target)
            kb_x = self.direction * self.knockback
            kb_y = -100.0
            hit_success = target.take_damage(self.damage, kb_x, kb_y)
            if hit_success:
                ParticleManager.get_instance().emit_bullet_hit(target.rect.centerx, target.rect.centery, hit_wall=False)
                return True
        return False
