"""
Chapter 2 Enemy: Dust Devil Brawler.
Fast melee rusher armed with twin Bowie knives. Chases the cowboy down aggressively.
"""
from entities.enemies.enemy_base import EnemyBase
from weapons.projectile import MeleeHitbox

class Brawler(EnemyBase):
    def __init__(self, x, y):
        super().__init__(x, y, width=12, height=22, max_health=3, enemy_type="brawler")
        self.patrol_speed = 50.0
        self.chase_speed = 105.0
        self.sight_range = 180.0
        self.attack_range = 22.0
        self.attack_cooldown = 0.8
        self.attack_timer = 0.0

    def update_ai(self, player, tilemap, dt):
        if not self.is_alive:
            return []

        melee_strikes = []
        self.update_timers(dt)
        self.attack_timer = max(0.0, self.attack_timer - dt)

        dx = player.rect.centerx - self.rect.centerx
        dist_x = abs(dx)
        sees_player = player.is_alive and self.has_line_of_sight(player, tilemap)

        if sees_player:
            self.facing_right = (dx > 0)
            self.patrol_dir = 1 if self.facing_right else -1

            if dist_x <= self.attack_range and self.attack_timer <= 0.0:
                # Melee Slash!
                self.state = "ATTACK"
                self.attack_timer = self.attack_cooldown
                self.vx = 0.0
                strike = MeleeHitbox(
                    self.rect.right if self.facing_right else (self.rect.left - 20),
                    self.rect.top,
                    20, self.rect.height,
                    damage=1, owner="enemy", direction=self.patrol_dir, knockback=160.0
                )
                melee_strikes.append(strike)
            else:
                self.state = "CHASE"
                # Charge forward!
                self.vx = self.patrol_dir * self.chase_speed
                # Jump if encountering small obstacle while chasing
                if self.on_ground and self.check_wall_ahead(tilemap):
                    self.vy = -260.0
        else:
            self.state = "PATROL"
            if self.on_ground:
                if self.check_ledge_ahead(tilemap) or self.check_wall_ahead(tilemap):
                    self.patrol_dir = -self.patrol_dir

            self.vx = self.patrol_dir * self.patrol_speed
            self.facing_right = (self.patrol_dir > 0)

        self.apply_gravity(dt)
        self.move_and_slide(tilemap, dt)

        self.anim_timer += dt
        cycle_rate = 0.08 if self.state == "CHASE" else 0.15
        if self.anim_timer >= cycle_rate:
            self.anim_timer = 0.0
            self.anim_frame = (self.anim_frame + 1) % 4

        return melee_strikes
