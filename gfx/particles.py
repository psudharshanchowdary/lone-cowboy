"""
Particle system for muzzle flashes, gunpowder smoke, bullet sparks,
blood/dust puffs, and dynamite explosions.
"""
import random
import pygame
from config import COLOR_GOLD, COLOR_WHITE, COLOR_RED, COLOR_SMOKE, COLOR_DARK_BROWN

class Particle:
    def __init__(self, x, y, vx, vy, color, radius, lifetime, gravity=0.0, shrink=True):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.radius = radius
        self.initial_radius = radius
        self.lifetime = lifetime
        self.age = 0.0
        self.gravity = gravity
        self.shrink = shrink
        self.alive = True

    def update(self, dt):
        self.age += dt
        if self.age >= self.lifetime:
            self.alive = False
            return

        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

        if self.shrink:
            progress = 1.0 - (self.age / self.lifetime)
            self.radius = max(0.5, self.initial_radius * progress)

    def draw(self, surface, camera):
        if not self.alive:
            return
        draw_x, draw_y = camera.apply_coords(self.x, self.y)
        pygame.draw.circle(surface, self.color, (int(draw_x), int(draw_y)), int(max(1, self.radius)))

class ParticleManager:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ParticleManager()
        return cls._instance

    def __init__(self):
        self.particles = []

    def clear(self):
        self.particles.clear()

    def update(self, dt):
        for p in self.particles:
            if p is not None:
                p.update(dt)
        self.particles = [p for p in self.particles if p is not None and p.alive]

    def draw(self, surface, camera):
        for p in self.particles:
            if p is not None:
                p.draw(surface, camera)

    # -------------------------------------------------------------
    # Specialized Emitters
    # -------------------------------------------------------------
    def emit_muzzle_flash(self, x, y, facing_right=True):
        direction = 1 if facing_right else -1
        # Quick flash spark
        for _ in range(5):
            vx = direction * random.uniform(80, 180)
            vy = random.uniform(-40, 40)
            color = random.choice([COLOR_GOLD, COLOR_WHITE, (255, 120, 30)])
            self.particles.append(Particle(x, y, vx, vy, color, radius=2.5, lifetime=0.08, shrink=True))

        # Gunpowder smoke puff
        for _ in range(3):
            vx = direction * random.uniform(10, 40)
            vy = random.uniform(-20, -5)
            self.particles.append(Particle(x, y, vx, vy, COLOR_SMOKE, radius=random.uniform(2, 4), lifetime=0.35, shrink=True))

    def emit_bullet_hit(self, x, y, hit_wall=True):
        count = 6 if hit_wall else 8
        base_colors = [COLOR_GOLD, COLOR_WHITE, COLOR_DARK_BROWN] if hit_wall else [COLOR_RED, (140, 20, 20)]
        for _ in range(count):
            angle_vx = random.uniform(-90, 90)
            angle_vy = random.uniform(-110, 40)
            color = random.choice(base_colors)
            self.particles.append(Particle(x, y, angle_vx, angle_vy, color, radius=random.uniform(1.0, 2.0), lifetime=random.uniform(0.15, 0.3), gravity=200.0))

    def emit_explosion(self, x, y, radius=48):
        # Fireballs
        for _ in range(25):
            vx = random.uniform(-160, 160)
            vy = random.uniform(-160, 160)
            color = random.choice([COLOR_GOLD, (255, 90, 20), COLOR_RED, COLOR_WHITE])
            self.particles.append(Particle(x, y, vx, vy, color, radius=random.uniform(3, 7), lifetime=random.uniform(0.25, 0.45), shrink=True))

        # Heavy billowing smoke
        for _ in range(16):
            vx = random.uniform(-60, 60)
            vy = random.uniform(-100, -20)
            self.particles.append(Particle(x, y, vx, vy, (80, 80, 90), radius=random.uniform(4, 9), lifetime=random.uniform(0.5, 0.9), shrink=True))

    def emit_dust(self, x, y):
        for _ in range(3):
            vx = random.uniform(-25, 25)
            vy = random.uniform(-15, -5)
            self.particles.append(Particle(x, y, vx, vy, (190, 160, 120), radius=random.uniform(1.5, 2.5), lifetime=0.25, shrink=True))
