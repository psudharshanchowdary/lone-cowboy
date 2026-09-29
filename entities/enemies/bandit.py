"""
Chapter 1 Enemy: Rattlesnake Bandit.
Armed with an outlaw revolver, patrols platforms, spots the player,
telegraphs aim, and fires.
"""
from entities.enemies.enemy_base import EnemyBase
from weapons.projectile import Bullet
from gfx.particles import ParticleManager

class Bandit(EnemyBase):
    def __init__(self, x, y):
        super().__init__(x, y, width=12, height=22, max_health=2, enemy_type="bandit")
        self.patrol_speed = 40.0
        self.sight_range = 170.0
        self.attack_range = 130.0
        self.aim_delay = 0.35
        self.aim_timer = 0.0

    def update_ai(self, player, tilemap, dt):
        if not self.is_alive:
            return []

        new_bullets = []
        self.update_timers(dt)
        self.attack_timer = max(0.0, self.attack_timer - dt)

        # Distance & direction to player
        dx = player.rect.centerx - self.rect.centerx
        dist_x = abs(dx)
        sees_player = player.is_alive and self.has_line_of_sight(player, tilemap)

        if sees_player:
            # Face towards player
            self.facing_right = (dx > 0)
            self.patrol_dir = 1 if self.facing_right else -1

            if dist_x <= self.attack_range and self.attack_timer <= 0.0:
                # Begin aiming telegraph
                self.state = "ALERT"
                self.vx = 0.0
                self.aim_timer += dt
                if self.aim_timer >= self.aim_delay:
                    # FIRE!
                    self.state = "ATTACK"
                    self.aim_timer = 0.0
                    self.attack_timer = self.attack_cooldown

                    spawn_x = self.x + (14 if self.facing_right else -6)
                    spawn_y = self.y + 10
                    ParticleManager.get_instance().emit_muzzle_flash(spawn_x, spawn_y, self.facing_right)
                    bullet = Bullet(spawn_x, spawn_y, 1 if self.facing_right else -1, owner="enemy", damage=1)
                    new_bullets.append(bullet)
            else:
                self.aim_timer = 0.0
                # Reposition: move toward attack range if on same platform
                if dist_x > self.attack_range:
                    if not self.check_ledge_ahead(tilemap) and not self.check_wall_ahead(tilemap):
                        self.vx = self.patrol_dir * self.patrol_speed
                        self.state = "CHASE"
                    else:
                        self.vx = 0.0
                        self.state = "PATROL"
                else:
                    self.vx = 0.0
                    self.state = "PATROL"
        else:
            self.aim_timer = 0.0
            self.state = "PATROL"

            # Patrol back and forth
            if self.on_ground:
                if self.check_ledge_ahead(tilemap) or self.check_wall_ahead(tilemap):
                    self.patrol_dir = -self.patrol_dir
                    self.facing_right = (self.patrol_dir > 0)

            self.vx = self.patrol_dir * self.patrol_speed
            self.facing_right = (self.patrol_dir > 0)

        # Physics
        self.apply_gravity(dt)
        self.move_and_slide(tilemap, dt)

        # Walk animation
        self.anim_timer += dt
        if self.anim_timer >= 0.15:
            self.anim_timer = 0.0
            self.anim_frame = (self.anim_frame + 1) % 4

        return new_bullets
