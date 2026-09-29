"""
Weapons systems for Lone Cowboy:
- Revolver (Six-Shooter with cylinder reload)
- Dynamite sticks (throwable explosive secondary)
- Melee Knife (quick close-quarters strike)
"""
from config import (
    REVOLVER_CAPACITY, REVOLVER_FIRE_RATE, REVOLVER_RELOAD_TIME,
    REVOLVER_DAMAGE, DYNAMITE_DAMAGE, DYNAMITE_RADIUS,
    DYNAMITE_THROW_VX, DYNAMITE_THROW_VY, MAX_DYNAMITE,
    MELEE_DAMAGE, MELEE_COOLDOWN, MELEE_RANGE, MELEE_KNOCKBACK
)
from weapons.projectile import Bullet, DynamiteStick, MeleeHitbox
from gfx.particles import ParticleManager

class Revolver:
    def __init__(self):
        self.capacity = REVOLVER_CAPACITY
        self.ammo = self.capacity
        self.fire_rate = REVOLVER_FIRE_RATE
        self.cooldown_timer = 0.0
        self.reload_time = REVOLVER_RELOAD_TIME
        self.reload_timer = 0.0
        self.is_reloading = False

    def can_shoot(self):
        return (not self.is_reloading) and (self.cooldown_timer <= 0.0) and (self.ammo > 0)

    def shoot(self, x, y, direction_x, owner="player"):
        if not self.can_shoot():
            if self.ammo <= 0 and not self.is_reloading:
                self.start_reload()
            return None

        self.ammo -= 1
        self.cooldown_timer = self.fire_rate

        # Spawn bullet and emit muzzle flash particles
        facing_right = (direction_x >= 0)
        spawn_x = x + (14 if facing_right else -6)
        spawn_y = y + 10
        ParticleManager.get_instance().emit_muzzle_flash(spawn_x, spawn_y, facing_right)

        bullet = Bullet(spawn_x, spawn_y, direction_x, owner=owner, damage=REVOLVER_DAMAGE)
        return bullet

    def start_reload(self):
        if self.ammo < self.capacity and not self.is_reloading:
            self.is_reloading = True
            self.reload_timer = self.reload_time

    def cancel_reload(self):
        self.is_reloading = False
        self.reload_timer = 0.0

    def update(self, dt):
        if self.cooldown_timer > 0.0:
            self.cooldown_timer -= dt

        if self.is_reloading:
            self.reload_timer -= dt
            if self.reload_timer <= 0.0:
                self.ammo = self.capacity
                self.is_reloading = False
                self.reload_timer = 0.0

    @property
    def reload_progress(self):
        if not self.is_reloading:
            return 1.0
        return max(0.0, 1.0 - (self.reload_timer / self.reload_time))


class DynamiteWeapon:
    def __init__(self, count=MAX_DYNAMITE):
        self.count = count
        self.max_count = MAX_DYNAMITE
        self.cooldown = 0.6
        self.cooldown_timer = 0.0

    def can_throw(self):
        return (self.count > 0) and (self.cooldown_timer <= 0.0)

    def throw(self, x, y, direction_x, owner="player"):
        if not self.can_throw():
            return None

        self.count -= 1
        self.cooldown_timer = self.cooldown

        facing_right = (direction_x >= 0)
        spawn_x = x + (12 if facing_right else -4)
        spawn_y = y + 4

        vx = DYNAMITE_THROW_VX if facing_right else -DYNAMITE_THROW_VX
        vy = DYNAMITE_THROW_VY

        dynamite = DynamiteStick(spawn_x, spawn_y, vx, vy, owner=owner)
        return dynamite

    def refill(self, amount):
        self.count = min(self.max_count, self.count + amount)

    def update(self, dt):
        if self.cooldown_timer > 0.0:
            self.cooldown_timer -= dt


class MeleeWeapon:
    def __init__(self):
        self.cooldown = MELEE_COOLDOWN
        self.cooldown_timer = 0.0

    def can_strike(self):
        return self.cooldown_timer <= 0.0

    def strike(self, entity_rect, facing_right=True, owner="player"):
        if not self.can_strike():
            return None

        self.cooldown_timer = self.cooldown
        direction = 1 if facing_right else -1

        # Position hitbox directly in front of attacker
        hitbox_w = int(MELEE_RANGE)
        hitbox_h = entity_rect.height
        hitbox_x = entity_rect.right if facing_right else (entity_rect.left - hitbox_w)
        hitbox_y = entity_rect.top

        return MeleeHitbox(hitbox_x, hitbox_y, hitbox_w, hitbox_h,
                            damage=MELEE_DAMAGE, owner=owner,
                            direction=direction, knockback=MELEE_KNOCKBACK)

    def update(self, dt):
        if self.cooldown_timer > 0.0:
            self.cooldown_timer -= dt
