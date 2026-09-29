"""
Base physical Entity class for Lone Cowboy.
Features sub-pixel movement, AABB tile collision, one-way platform support,
health, damage flash, knockback, and invulnerability timers.
"""
import pygame
from config import GRAVITY, TERMINAL_VELOCITY, INVULNERABILITY_TIME, COLOR_WHITE

class Entity:
    def __init__(self, x, y, width, height, max_health=3):
        self.x = float(x)
        self.y = float(y)
        self.width = width
        self.height = height

        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.facing_right = True

        self.max_health = max_health
        self.health = max_health
        self.is_alive = True

        # Damage reaction & feedback
        self.invulnerable_timer = 0.0
        self.flash_timer = 0.0
        self.knockback_active = False

        # Drop down through one-way platforms
        self.drop_through_timer = 0.0

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def apply_gravity(self, dt):
        self.vy = min(self.vy + GRAVITY * dt, TERMINAL_VELOCITY)

    def move_and_slide(self, tilemap, dt):
        """Swept AABB movement with separate X and Y collision against tilemap."""
        # 1. Horizontal movement
        self.x += self.vx * dt
        entity_rect = self.rect

        solid_tiles = tilemap.get_solid_tiles_near(entity_rect)
        for tile in solid_tiles:
            if entity_rect.colliderect(tile):
                if self.vx > 0:
                    self.x = tile.left - self.width
                    self.vx = 0.0
                elif self.vx < 0:
                    self.x = tile.right
                    self.vx = 0.0
                entity_rect = self.rect

        # 2. Vertical movement
        prev_bottom = self.y + self.height
        self.y += self.vy * dt
        entity_rect = self.rect
        self.on_ground = False

        # Check solid tiles
        solid_tiles = tilemap.get_solid_tiles_near(entity_rect)
        for tile in solid_tiles:
            if entity_rect.colliderect(tile):
                if self.vy > 0:
                    self.y = tile.top - self.height
                    self.vy = 0.0
                    self.on_ground = True
                elif self.vy < 0:
                    self.y = tile.bottom
                    self.vy = 0.0
                entity_rect = self.rect

        # Check one-way platforms (only collide when falling down and above platform)
        if self.drop_through_timer <= 0.0 and self.vy >= 0:
            platforms = tilemap.get_platform_tiles_near(entity_rect)
            for plat in platforms:
                # If was above platform previously and now intersects its top area
                if prev_bottom <= plat.top + 4 and entity_rect.bottom >= plat.top:
                    if entity_rect.right > plat.left and entity_rect.left < plat.right:
                        self.y = plat.top - self.height
                        self.vy = 0.0
                        self.on_ground = True
                        entity_rect = self.rect
                        break

    def take_damage(self, amount, knockback_x=0.0, knockback_y=0.0):
        if not self.is_alive or self.invulnerable_timer > 0.0:
            return False

        self.health -= amount
        self.invulnerable_timer = INVULNERABILITY_TIME
        self.flash_timer = 0.25

        if knockback_x != 0 or knockback_y != 0:
            self.vx = knockback_x
            self.vy = knockback_y
            self.knockback_active = True

        if self.health <= 0:
            self.health = 0
            self.is_alive = False

        return True

    def heal(self, amount):
        if not self.is_alive:
            return
        self.health = min(self.max_health, self.health + amount)

    def update_timers(self, dt):
        if self.invulnerable_timer > 0.0:
            self.invulnerable_timer -= dt
            if self.invulnerable_timer <= 0.0:
                self.invulnerable_timer = 0.0

        if self.flash_timer > 0.0:
            self.flash_timer -= dt
            if self.flash_timer <= 0.0:
                self.flash_timer = 0.0

        if self.drop_through_timer > 0.0:
            self.drop_through_timer -= dt

        if self.knockback_active and self.on_ground:
            self.knockback_active = False

    def draw_flash_silhouette(self, surface, sprite, dest_pos):
        """Draws a white/red flashing silhouette when damaged."""
        if self.flash_timer > 0.0 and (int(self.flash_timer * 30) % 2 == 0):
            flash_surf = sprite.copy()
            # Tint white
            flash_surf.fill(COLOR_WHITE, special_flags=pygame.BLEND_RGB_ADD)
            surface.blit(flash_surf, dest_pos)
        else:
            surface.blit(sprite, dest_pos)
