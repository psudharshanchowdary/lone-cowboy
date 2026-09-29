"""
Chapter 4 Enemy: Black Powder Grenadier.
Lobs sticks of dynamite in high parabolic arcs to flush out the cowboy from cover.
"""
from entities.enemies.enemy_base import EnemyBase
from weapons.projectile import DynamiteStick

class Grenadier(EnemyBase):
    def __init__(self, x, y):
        super().__init__(x, y, width=12, height=22, max_health=3, enemy_type="grenadier")
        self.patrol_speed = 35.0
        self.sight_range = 190.0
        self.attack_range = 160.0
        self.attack_cooldown = 2.0
        self.attack_timer = 1.0

    def update_ai(self, player, tilemap, dt):
        if not self.is_alive:
            return []

        new_dynamites = []
        self.update_timers(dt)
        self.attack_timer = max(0.0, self.attack_timer - dt)

        dx = player.rect.centerx - self.rect.centerx
        dist_x = abs(dx)
        sees_player = player.is_alive and self.has_line_of_sight(player, tilemap)

        if sees_player:
            self.facing_right = (dx > 0)
            self.patrol_dir = 1 if self.facing_right else -1

            if dist_x <= self.attack_range and self.attack_timer <= 0.0:
                self.state = "ATTACK"
                self.attack_timer = self.attack_cooldown
                self.vx = 0.0

                # Calculate lob velocity towards player
                throw_dir = 1 if self.facing_right else -1
                throw_vx = throw_dir * min(200.0, max(80.0, dist_x * 1.3))
                throw_vy = -210.0

                spawn_x = self.x + (12 if self.facing_right else -4)
                spawn_y = self.y + 4
                dyn = DynamiteStick(spawn_x, spawn_y, throw_vx, throw_vy, owner="enemy", damage=3, radius=42.0)
                new_dynamites.append(dyn)
            else:
                self.state = "PATROL"
                self.vx = 0.0
        else:
            self.state = "PATROL"
            if self.on_ground:
                if self.check_ledge_ahead(tilemap) or self.check_wall_ahead(tilemap):
                    self.patrol_dir = -self.patrol_dir

            self.vx = self.patrol_dir * self.patrol_speed
            self.facing_right = (self.patrol_dir > 0)

        self.apply_gravity(dt)
        self.move_and_slide(tilemap, dt)

        return new_dynamites
