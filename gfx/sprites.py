"""
Procedural Pixel Art and Asset Manager for Lone Cowboy
Generates clean, charming 16x16 and 24x24 retro pixel art surfaces,
with automatic fallback to custom PNG files in 'assets/sprites/' if provided.
"""
import os
import pygame
from config import (
    TILE_SIZE, COLOR_DARK_BROWN, COLOR_SADDLE_BROWN, COLOR_WOOD,
    COLOR_SANDSTONE, COLOR_DESERT_SAND, COLOR_WHITE, COLOR_RED,
    COLOR_CRIMSON, COLOR_GOLD, COLOR_GREEN, COLOR_RATTLESNAKE_GREEN,
    COLOR_IRON_GRAY, COLOR_DARK_SLATE, COLOR_BLACK
)

class SpriteManager:
    _instance = None
    _cache = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = SpriteManager()
        return cls._instance

    def __init__(self):
        self.assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "sprites")
        os.makedirs(self.assets_dir, exist_ok=True)

    def load_or_create(self, name, generator_func, *args):
        key = f"{name}_{args}"
        if key in self._cache:
            return self._cache[key]

        # Check if user provided custom PNG
        custom_file = os.path.join(self.assets_dir, f"{name}.png")
        if os.path.exists(custom_file):
            try:
                img = pygame.image.load(custom_file).convert_alpha()
                self._cache[key] = img
                return img
            except Exception:
                pass

        # Otherwise generate procedural pixel art
        surface = generator_func(*args)
        self._cache[key] = surface
        return surface

    # ------------------------------------------------------------------
    # Procedural Player Sprites (Cowboy: 16x24)
    # ------------------------------------------------------------------
    def get_player_sprite(self, state="idle", facing_right=True, frame=0):
        name = f"player_{state}_{'r' if facing_right else 'l'}_{frame}"
        surf = self.load_or_create(name, self._draw_cowboy, state, frame)
        if not facing_right:
            return pygame.transform.flip(surf, True, False)
        return surf

    def _draw_cowboy(self, state, frame):
        # 16 wide x 24 high canvas
        surf = pygame.Surface((16, 24), pygame.SRCALPHA)

        # Palette
        hat_color = (68, 42, 28)
        bandana_color = (196, 44, 38)
        skin_color = (240, 192, 150)
        poncho_color = (170, 110, 54)
        pants_color = (48, 64, 88)
        boots_color = (40, 24, 18)
        gun_color = (80, 84, 92)

        crouching = (state == "crouch")
        y_offset = 6 if crouching else 0

        # Hat (Stetson wide brim + crown)
        hat_y = 2 + y_offset
        # Crown
        surf.fill(hat_color, (5, hat_y, 6, 4))
        # Hat belt
        surf.fill(COLOR_GOLD, (5, hat_y + 3, 6, 1))
        # Wide brim
        surf.fill(hat_color, (2, hat_y + 4, 12, 2))

        # Face & eyes
        surf.fill(skin_color, (5, hat_y + 6, 6, 3))
        surf.fill(COLOR_BLACK, (8, hat_y + 6, 1, 1))  # eye

        # Red Bandana
        surf.fill(bandana_color, (4, hat_y + 8, 8, 2))

        if not crouching:
            # Poncho / Torso
            surf.fill(poncho_color, (4, 12, 8, 5))
            # Belt & holster
            surf.fill(COLOR_DARK_BROWN, (4, 16, 8, 2))
            surf.fill(COLOR_GOLD, (7, 16, 2, 2))  # buckle

            # Legs / Boots animation
            if state == "walk":
                leg_cycle = frame % 4
                if leg_cycle == 0:
                    surf.fill(pants_color, (5, 18, 3, 4))
                    surf.fill(pants_color, (8, 18, 3, 4))
                    surf.fill(boots_color, (4, 21, 4, 3))
                    surf.fill(boots_color, (8, 21, 4, 3))
                elif leg_cycle == 1:
                    surf.fill(pants_color, (4, 18, 3, 3))
                    surf.fill(pants_color, (9, 18, 3, 4))
                    surf.fill(boots_color, (3, 20, 4, 3))
                    surf.fill(boots_color, (9, 21, 4, 3))
                elif leg_cycle == 2:
                    surf.fill(pants_color, (5, 18, 3, 4))
                    surf.fill(pants_color, (8, 18, 3, 4))
                    surf.fill(boots_color, (5, 21, 4, 3))
                    surf.fill(boots_color, (7, 21, 4, 3))
                else:
                    surf.fill(pants_color, (6, 18, 3, 4))
                    surf.fill(pants_color, (3, 18, 3, 3))
                    surf.fill(boots_color, (6, 21, 4, 3))
                    surf.fill(boots_color, (2, 20, 4, 3))
            elif state in ("jump", "fall"):
                surf.fill(pants_color, (4, 18, 3, 3))
                surf.fill(pants_color, (9, 17, 3, 3))
                surf.fill(boots_color, (3, 20, 4, 3))
                surf.fill(boots_color, (9, 19, 4, 3))
            else:
                # Idle legs
                surf.fill(pants_color, (5, 18, 3, 4))
                surf.fill(pants_color, (8, 18, 3, 4))
                surf.fill(boots_color, (4, 21, 4, 3))
                surf.fill(boots_color, (8, 21, 4, 3))

            # Arm / Weapon
            if state == "shoot":
                # Arm pointed forward holding gun
                surf.fill(poncho_color, (9, 12, 4, 3))
                surf.fill(gun_color, (12, 12, 4, 2))
                surf.fill(COLOR_GOLD, (15, 12, 1, 1))  # tip/flash
            elif state == "melee":
                # Knife slash arm
                surf.fill(skin_color, (10, 11, 4, 3))
                surf.fill(COLOR_WHITE, (13, 9, 3, 5))  # blade flash
            else:
                # Resting gun at hip
                surf.fill(skin_color, (9, 14, 3, 3))
                surf.fill(gun_color, (10, 15, 3, 2))
        else:
            # Crouched legs
            surf.fill(poncho_color, (4, 16, 8, 3))
            surf.fill(pants_color, (4, 19, 8, 3))
            surf.fill(boots_color, (3, 21, 10, 3))
            if state == "shoot":
                surf.fill(gun_color, (12, 17, 4, 2))

        return surf

    # ------------------------------------------------------------------
    # Procedural Enemy Sprites
    # ------------------------------------------------------------------
    def get_enemy_sprite(self, enemy_type="bandit", state="patrol", facing_right=True, frame=0):
        name = f"enemy_{enemy_type}_{state}_{'r' if facing_right else 'l'}_{frame}"
        surf = self.load_or_create(name, self._draw_enemy, enemy_type, state, frame)
        if not facing_right:
            return pygame.transform.flip(surf, True, False)
        return surf

    def _draw_enemy(self, enemy_type, state, frame):
        surf = pygame.Surface((16, 24), pygame.SRCALPHA)

        skin = (230, 180, 140)
        eye = COLOR_BLACK

        if enemy_type == "bandit":
            # Rattlesnake Outlaw (Green bandana, worn vest)
            hat_c = (50, 40, 35)
            bandana_c = COLOR_RATTLESNAKE_GREEN
            vest_c = (86, 68, 52)
            pants_c = (60, 50, 44)
            boots_c = (35, 25, 20)

            # Hat
            surf.fill(hat_c, (5, 3, 6, 3))
            surf.fill(hat_c, (3, 6, 10, 2))
            # Face & green bandana
            surf.fill(skin, (5, 8, 6, 3))
            surf.fill(eye, (8, 8, 1, 1))
            surf.fill(bandana_c, (4, 10, 8, 2))
            # Body & revolver
            surf.fill(vest_c, (5, 12, 6, 5))
            surf.fill(pants_c, (5, 17, 3, 4))
            surf.fill(pants_c, (8, 17, 3, 4))
            surf.fill(boots_c, (4, 21, 4, 3))
            surf.fill(boots_c, (8, 21, 4, 3))

            if state == "shoot":
                surf.fill((90, 94, 100), (10, 12, 5, 2))  # Aiming gun
            else:
                surf.fill((70, 74, 80), (9, 14, 3, 2))

        elif enemy_type == "brawler":
            # Dust Devil Melee Knife Brawler (bare arms, red mohawk/bandana, twin blades)
            surf.fill(COLOR_CRIMSON, (6, 2, 4, 4))  # Red hair / headband
            surf.fill(skin, (5, 6, 6, 4))
            surf.fill(eye, (8, 7, 1, 1))
            surf.fill((110, 75, 45), (5, 10, 6, 6)) # Leather vest
            surf.fill(skin, (3, 11, 2, 5))          # Bare arm
            surf.fill(skin, (11, 11, 2, 5))
            surf.fill(COLOR_WHITE, (12, 13, 4, 2))   # Knife
            surf.fill((70, 60, 50), (5, 16, 3, 5))  # Pants
            surf.fill((70, 60, 50), (8, 16, 3, 5))
            surf.fill(COLOR_BLACK, (4, 21, 4, 3))

        elif enemy_type == "sniper":
            # Iron Mask Sniper (metallic mask, dark long duster coat, long rifle)
            surf.fill((30, 30, 35), (4, 2, 8, 4))    # Dark hat
            surf.fill(COLOR_IRON_GRAY, (5, 6, 6, 4)) # Iron mask
            surf.fill(COLOR_RED, (8, 7, 1, 1))       # Glowing scope eye
            surf.fill((45, 45, 55), (4, 10, 8, 9))   # Long coat
            # Long rifle barrel
            surf.fill((100, 105, 115), (10, 11, 6, 2))
            surf.fill((20, 20, 24), (5, 19, 6, 4))   # Pants / boots

        elif enemy_type == "grenadier":
            # Black Powder Marauder (Mining helmet with lamp, dynamite stick)
            surf.fill((80, 85, 90), (4, 2, 8, 4))    # Helmet
            surf.fill(COLOR_GOLD, (11, 3, 2, 2))     # Lamp
            surf.fill(skin, (5, 6, 6, 4))
            surf.fill((60, 50, 40), (4, 10, 8, 6))   # Overalls
            surf.fill(COLOR_RED, (11, 10, 3, 4))     # Dynamite in hand
            surf.fill(COLOR_GOLD, (12, 8, 2, 2))     # Fuse spark
            surf.fill((40, 35, 30), (5, 16, 6, 6))   # Boots

        elif enemy_type == "boss":
            # Gang Leader / Boss (Bigger, armored, imposing Stetson & coat)
            surf = pygame.Surface((20, 28), pygame.SRCALPHA)
            surf.fill(COLOR_BLACK, (5, 2, 10, 5))      # Large black hat
            surf.fill(COLOR_GOLD, (5, 6, 10, 1))       # Gold hat band
            surf.fill(COLOR_BLACK, (2, 7, 16, 2))      # Wide brim
            surf.fill(skin, (6, 9, 8, 4))
            surf.fill(COLOR_RED, (11, 10, 2, 1))       # Menacing eye
            surf.fill(COLOR_CRIMSON, (5, 13, 10, 8))   # Heavy coat
            surf.fill(COLOR_GOLD, (8, 14, 4, 3))       # Golden breastplate
            surf.fill(COLOR_IRON_GRAY, (13, 14, 7, 3)) # Dual weapons
            surf.fill((30, 25, 25), (6, 21, 8, 6))     # Boots

        return surf

    # ------------------------------------------------------------------
    # Procedural Tiles & Props (16x16)
    # ------------------------------------------------------------------
    def get_tile_sprite(self, tile_type="sandstone"):
        return self.load_or_create(f"tile_{tile_type}", self._draw_tile, tile_type)

    def _draw_tile(self, tile_type):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))

        if tile_type == "sandstone":
            surf.fill(COLOR_SANDSTONE)
            # Sandy top layer
            surf.fill(COLOR_DESERT_SAND, (0, 0, TILE_SIZE, 3))
            # Rock fissures
            surf.fill(COLOR_SADDLE_BROWN, (3, 6, 4, 1))
            surf.fill(COLOR_SADDLE_BROWN, (10, 11, 5, 1))
            surf.fill((185, 130, 80), (1, 14, 6, 1))

        elif tile_type == "wood":
            # Saloon wooden planks
            surf.fill(COLOR_WOOD)
            # Board seams
            surf.fill(COLOR_DARK_BROWN, (0, 0, TILE_SIZE, 1))
            surf.fill(COLOR_DARK_BROWN, (0, 8, TILE_SIZE, 1))
            surf.fill(COLOR_DARK_BROWN, (7, 1, 1, 7))
            # Wood grain highlights
            surf.fill((160, 105, 68), (2, 3, 4, 1))
            surf.fill((160, 105, 68), (10, 11, 5, 1))

        elif tile_type == "platform":
            # One-way wooden bridge / scaffolding
            surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            surf.fill(COLOR_WOOD, (0, 0, TILE_SIZE, 4))
            surf.fill(COLOR_SADDLE_BROWN, (0, 4, TILE_SIZE, 2))
            surf.fill(COLOR_DARK_BROWN, (2, 6, 2, 10))
            surf.fill(COLOR_DARK_BROWN, (12, 6, 2, 10))

        elif tile_type == "cactus":
            # Hazard: Prickly desert cactus
            surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            surf.fill(COLOR_GREEN, (6, 2, 4, 14))
            surf.fill(COLOR_GREEN, (2, 6, 4, 3))
            surf.fill(COLOR_GREEN, (10, 8, 4, 3))
            # Needles
            surf.fill(COLOR_WHITE, (5, 4, 1, 1))
            surf.fill(COLOR_WHITE, (10, 5, 1, 1))
            surf.fill(COLOR_WHITE, (6, 10, 1, 1))

        elif tile_type == "spikes":
            # Hazard: Mine spikes / barbed iron
            surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            for i in range(4):
                x = i * 4
                points = [(x, 16), (x + 2, 6), (x + 4, 16)]
                pygame.draw.polygon(surf, COLOR_IRON_GRAY, points)
                pygame.draw.line(surf, COLOR_WHITE, (x + 2, 6), (x + 2, 8))

        elif tile_type == "checkpoint_off":
            # Lantern checkpoint unlit
            surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            surf.fill(COLOR_IRON_GRAY, (4, 4, 8, 10))
            surf.fill(COLOR_DARK_BROWN, (5, 6, 6, 6))
            surf.fill(COLOR_WHITE, (7, 8, 2, 3))

        elif tile_type == "checkpoint_on":
            # Lantern glowing warmly
            surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            surf.fill(COLOR_GOLD, (3, 3, 10, 12))
            surf.fill(COLOR_RED, (6, 6, 4, 6))
            surf.fill(COLOR_WHITE, (7, 7, 2, 3))

        elif tile_type == "exit":
            # Saloon swinging doors / stagecoach exit
            surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            surf.fill(COLOR_DARK_BROWN, (1, 1, 14, 15))
            surf.fill(COLOR_WOOD, (2, 2, 5, 13))
            surf.fill(COLOR_WOOD, (9, 2, 5, 13))
            surf.fill(COLOR_GOLD, (6, 8, 1, 2))
            surf.fill(COLOR_GOLD, (9, 8, 1, 2))

        return surf

    # ------------------------------------------------------------------
    # Projectiles, Items & UI Elements
    # ------------------------------------------------------------------
    def get_bullet_sprite(self):
        surf = pygame.Surface((6, 3), pygame.SRCALPHA)
        surf.fill(COLOR_GOLD, (0, 0, 5, 3))
        surf.fill(COLOR_WHITE, (2, 1, 2, 1))
        return surf

    def get_dynamite_sprite(self, frame=0):
        surf = pygame.Surface((8, 8), pygame.SRCALPHA)
        surf.fill(COLOR_RED, (2, 3, 5, 4))
        surf.fill(COLOR_WHITE, (4, 4, 1, 2))  # label
        # Sparking fuse
        surf.fill(COLOR_DARK_BROWN, (5, 1, 1, 2))
        spark_color = COLOR_GOLD if (frame % 2 == 0) else COLOR_WHITE
        surf.fill(spark_color, (5, 0, 2, 2))
        return surf

    def get_heart_sprite(self, full=True):
        surf = pygame.Surface((9, 9), pygame.SRCALPHA)
        if full:
            # Full heart / badge
            surf.fill(COLOR_RED, (1, 2, 7, 4))
            surf.fill(COLOR_RED, (2, 6, 5, 2))
            surf.fill(COLOR_RED, (3, 8, 3, 1))
            surf.fill(COLOR_WHITE, (2, 2, 2, 2)) # highlight
        else:
            # Empty / depleted heart
            surf.fill(COLOR_DARK_SLATE, (1, 2, 7, 4))
            surf.fill(COLOR_DARK_SLATE, (2, 6, 5, 2))
            surf.fill(COLOR_DARK_SLATE, (3, 8, 3, 1))
        return surf

    def get_cylinder_sprite(self, chambers_loaded=6):
        # 20x20 revolver cylinder HUD
        surf = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(surf, COLOR_DARK_SLATE, (10, 10), 9)
        pygame.draw.circle(surf, COLOR_IRON_GRAY, (10, 10), 9, 1)
        pygame.draw.circle(surf, COLOR_BLACK, (10, 10), 3)

        # 6 chamber positions around the center
        import math
        for i in range(6):
            angle = i * (2 * math.pi / 6) - math.pi / 2
            cx = int(10 + 6 * math.cos(angle))
            cy = int(10 + 6 * math.sin(angle))
            color = COLOR_GOLD if i < chambers_loaded else COLOR_BLACK
            pygame.draw.circle(surf, color, (cx, cy), 2)
        return surf
