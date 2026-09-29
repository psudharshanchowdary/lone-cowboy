"""
JSON Level Loader for Lone Cowboy.
Parses external JSON level files and instantiates tilemaps, player spawns,
patrolling enemies, and bosses.
"""
import os
import json
from world.tilemap import Tilemap
from entities.enemies.bandit import Bandit
from entities.enemies.brawler import Brawler
from entities.enemies.sniper import Sniper
from entities.enemies.grenadier import Grenadier
from entities.enemies.boss import Boss

class LevelLoader:
    @staticmethod
    def load_level(level_path):
        if not os.path.exists(level_path):
            raise FileNotFoundError(f"Level file not found: {level_path}")

        with open(level_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return LevelLoader.parse_level_data(data)

    @staticmethod
    def parse_level_data(data):
        cols = data.get("width", 30)
        rows = data.get("height", 18)
        tiles_data = data.get("tiles", [])

        tilemap = Tilemap(cols, rows, tiles_data)
        player_spawn = tuple(data.get("player_spawn", [32, 180]))

        # Spawn Enemies
        enemies = []
        for e_info in data.get("enemies", []):
            e_type = e_info.get("type", "bandit")
            ex = e_info.get("x", 100)
            ey = e_info.get("y", 100)

            if e_type == "bandit":
                enemies.append(Bandit(ex, ey))
            elif e_type == "brawler":
                enemies.append(Brawler(ex, ey))
            elif e_type == "sniper":
                enemies.append(Sniper(ex, ey))
            elif e_type == "grenadier":
                enemies.append(Grenadier(ex, ey))

        # Spawn Boss if present
        boss_info = data.get("boss")
        if boss_info:
            bx = boss_info.get("x", 400)
            by = boss_info.get("y", 180)
            b_name = boss_info.get("name", "Outlaw Boss")
            b_hp = boss_info.get("health", 12)
            enemies.append(Boss(bx, by, boss_name=b_name, max_health=b_hp))

        meta = {
            "id": data.get("id", 1),
            "chapter": data.get("chapter", 1),
            "name": data.get("name", "Desert Pass"),
            "theme": data.get("theme", "canyon")
        }

        return tilemap, player_spawn, enemies, meta
