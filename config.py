"""
Game Configuration and Constants for Lone Cowboy: Wild West Outlaws
"""
import os
import pygame

# ---------------------------------------------------------
# Display & Resolution
# ---------------------------------------------------------
# Base internal virtual canvas (rendered to, then scaled to window)
INTERNAL_WIDTH = 480
INTERNAL_HEIGHT = 270
SCALE_FACTOR = 2  # Window size = 960 x 540
SCREEN_WIDTH = INTERNAL_WIDTH * SCALE_FACTOR
SCREEN_HEIGHT = INTERNAL_HEIGHT * SCALE_FACTOR
FPS = 60
TITLE = "Lone Cowboy: Wild West Outlaws"

TILE_SIZE = 16

# ---------------------------------------------------------
# File Paths
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LEVELS_DIR = os.path.join(DATA_DIR, "levels")
SAVES_DIR = os.path.join(DATA_DIR, "saves")
SAVE_FILE = os.path.join(SAVES_DIR, "save_game.json")

# Ensure required runtime folders exist
os.makedirs(LEVELS_DIR, exist_ok=True)
os.makedirs(SAVES_DIR, exist_ok=True)

# ---------------------------------------------------------
# Western Color Palette
# ---------------------------------------------------------
COLOR_BLACK = (16, 12, 10)
COLOR_DARK_BROWN = (42, 28, 22)
COLOR_SADDLE_BROWN = (90, 52, 34)
COLOR_WOOD = (138, 86, 52)
COLOR_SANDSTONE = (206, 150, 98)
COLOR_DESERT_SAND = (235, 196, 142)
COLOR_SUNSET_SKY = (245, 178, 110)
COLOR_SKY_BLUE = (118, 166, 198)
COLOR_NIGHT_SKY = (22, 24, 44)
COLOR_WHITE = (248, 244, 236)
COLOR_RED = (196, 44, 38)
COLOR_CRIMSON = (138, 24, 28)
COLOR_GOLD = (238, 184, 48)
COLOR_GREEN = (68, 138, 64)
COLOR_RATTLESNAKE_GREEN = (78, 112, 62)
COLOR_IRON_GRAY = (112, 116, 128)
COLOR_DARK_SLATE = (48, 52, 64)
COLOR_SMOKE = (180, 180, 190)

# ---------------------------------------------------------
# Physics & Movement
# ---------------------------------------------------------
GRAVITY = 950.0                # pixels / s^2
TERMINAL_VELOCITY = 460.0      # max fall speed
PLAYER_WALK_SPEED = 120.0      # pixels / s
PLAYER_RUN_SPEED = 185.0       # pixels / s
PLAYER_CROUCH_SPEED = 60.0     # pixels / s
PLAYER_JUMP_FORCE = -340.0     # vertical impulse
PLAYER_MAX_HEALTH = 5
COYOTE_TIME = 0.12             # seconds allowed to jump after leaving ground
JUMP_BUFFER_TIME = 0.12        # seconds to buffer jump input before landing
INVULNERABILITY_TIME = 1.0     # seconds of i-frames after taking damage
KNOCKBACK_FORCE_X = 140.0
KNOCKBACK_FORCE_Y = -120.0

# ---------------------------------------------------------
# Combat & Weapons
# ---------------------------------------------------------
# Revolver (Six-Shooter)
REVOLVER_CAPACITY = 6
REVOLVER_FIRE_RATE = 0.22      # min delay between shots
REVOLVER_RELOAD_TIME = 1.0     # seconds to reload full cylinder
REVOLVER_DAMAGE = 1
BULLET_SPEED = 420.0

# Secondary: Dynamite
DYNAMITE_FUSE_TIME = 2.0       # seconds before explosion
DYNAMITE_DAMAGE = 4
DYNAMITE_RADIUS = 48.0
DYNAMITE_THROW_VX = 210.0
DYNAMITE_THROW_VY = -220.0
MAX_DYNAMITE = 3

# Melee (Knife / Gun-butt)
MELEE_DAMAGE = 2
MELEE_COOLDOWN = 0.35
MELEE_RANGE = 24.0
MELEE_KNOCKBACK = 220.0

# ---------------------------------------------------------
# Chapters & Gangs Blueprint
# ---------------------------------------------------------
CHAPTERS = {
    1: {
        "title": "Chapter 1: The Rattlesnake Rustlers",
        "gang_name": "Rattlesnake Rustlers",
        "levels": list(range(1, 11)),
        "theme": "canyon",
        "sky_color": COLOR_SUNSET_SKY,
        "primary_enemy": "bandit",
        "boss_level": 10,
        "boss_name": "Rattlesnake Jake",
        "description": "Bandits hiding out in the arid canyon trails and frontier shanties."
    },
    2: {
        "title": "Chapter 2: The Dust Devil Syndicate",
        "gang_name": "Dust Devil Syndicate",
        "levels": list(range(11, 21)),
        "theme": "mine",
        "sky_color": (50, 40, 45),
        "primary_enemy": "brawler",
        "boss_level": 20,
        "boss_name": "Iron Bull Logan",
        "description": "Cutthroat miners and vicious knife-brawlers guarding gold shafts."
    },
    3: {
        "title": "Chapter 3: The Iron Mask Outlaws",
        "gang_name": "Iron Mask Outlaws",
        "levels": list(range(21, 31)),
        "theme": "saloon_rooftops",
        "sky_color": COLOR_NIGHT_SKY,
        "primary_enemy": "sniper",
        "boss_level": 30,
        "boss_name": "One-Eyed Silas",
        "description": "Ruthless sharp-shooters who control the ghost towns from the rooftops."
    },
    4: {
        "title": "Chapter 4: The Black Powder Marauders",
        "gang_name": "Black Powder Marauders",
        "levels": list(range(31, 41)),
        "theme": "quarry",
        "sky_color": (64, 40, 30),
        "primary_enemy": "grenadier",
        "boss_level": 40,
        "boss_name": "Mad Pete 'Kaboom'",
        "description": "Dynamite fiends who blow apart anyone trespassing their oil fields."
    },
    5: {
        "title": "Chapter 5: The Desperado Cartel & Final Gauntlet",
        "gang_name": "The Desperado Cartel",
        "levels": list(range(41, 53)),
        "theme": "fortress",
        "sky_color": (32, 20, 36),
        "primary_enemy": "mixed",
        "boss_level": 52,
        "boss_name": "El Diablo (The Shadow Kingpin)",
        "description": "The elite fortress. Level 52 is the grand gauntlet of all gang leaders!"
    }
}

TOTAL_LEVELS = 52
FINAL_BOSS_LEVEL = 52

# ---------------------------------------------------------
# Default Key Bindings
# ---------------------------------------------------------
KEY_LEFT = [pygame.K_a, pygame.K_LEFT]
KEY_RIGHT = [pygame.K_d, pygame.K_RIGHT]
KEY_UP = [pygame.K_w, pygame.K_UP]
KEY_DOWN = [pygame.K_s, pygame.K_DOWN]
KEY_JUMP = [pygame.K_SPACE, pygame.K_w, pygame.K_UP]
KEY_RUN = [pygame.K_LSHIFT, pygame.K_RSHIFT]
KEY_SHOOT = [pygame.K_j, pygame.K_z]          # Also mouse left click
KEY_RELOAD = [pygame.K_r]
KEY_MELEE = [pygame.K_f, pygame.K_v, pygame.K_x]  # Also mouse middle click
KEY_DYNAMITE = [pygame.K_k, pygame.K_c]      # Also mouse right click
KEY_INTERACT = [pygame.K_e]
KEY_PAUSE = [pygame.K_ESCAPE, pygame.K_p]
