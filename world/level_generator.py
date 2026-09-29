"""
52-Level Generator and Validator for Lone Cowboy.
Creates all 52 JSON level files across the 5 gang chapters with varied layouts,
increasing difficulty, chapter-specific hazards and enemies, culminating in
the Level 52 Boss Gauntlet.
"""
import os
import json
from config import LEVELS_DIR, CHAPTERS, TOTAL_LEVELS
from world.tilemap import (
    TILE_AIR, TILE_SANDSTONE, TILE_WOOD, TILE_PLATFORM,
    TILE_CACTUS, TILE_SPIKES, TILE_CHECKPOINT, TILE_EXIT
)

def get_chapter_for_level(level_id):
    if level_id <= 10:
        return 1
    elif level_id <= 20:
        return 2
    elif level_id <= 30:
        return 3
    elif level_id <= 40:
        return 4
    else:
        return 5

def generate_level_data(level_id):
    chapter_num = get_chapter_for_level(level_id)
    chap_info = CHAPTERS[chapter_num]

    # Level dimensions (standard ~45-60 tiles wide, 18 tiles high)
    cols = 48 + (level_id % 5) * 4
    rows = 18

    # Start with empty grid
    grid = [[TILE_AIR for _ in range(cols)] for _ in range(rows)]

    # 1. Floor & Boundary Walls
    floor_row = 15
    for r in range(floor_row, rows):
        for c in range(cols):
            grid[r][c] = TILE_WOOD if chap_info["theme"] in ("mine", "saloon_rooftops") else TILE_SANDSTONE

    # Left & Right Boundary Walls
    for r in range(rows):
        grid[r][0] = TILE_SANDSTONE
        grid[r][cols - 1] = TILE_SANDSTONE

    # 2. Player Spawn & Exit
    player_spawn = [32, (floor_row - 2) * 16]
    grid[floor_row - 1][cols - 3] = TILE_EXIT

    # 3. Checkpoint in middle of level
    mid_col = cols // 2
    grid[floor_row - 1][mid_col] = TILE_CHECKPOINT

    # 4. Platforms & Terrain variations
    is_boss_level = (level_id in (10, 20, 30, 40, 52))

    enemies = []
    boss_data = None

    if is_boss_level:
        # Open combat arena layout
        # Tiered platforms for dynamic gunplay
        for c in range(12, 20):
            grid[11][c] = TILE_PLATFORM
        for c in range(cols - 20, cols - 12):
            grid[11][c] = TILE_PLATFORM
        for c in range(mid_col - 5, mid_col + 5):
            grid[8][c] = TILE_PLATFORM

        # Boss spawning
        boss_hp = 8 + (chapter_num * 3)
        boss_data = {
            "name": chap_info["boss_name"],
            "x": (cols - 8) * 16,
            "y": (floor_row - 2) * 16,
            "health": boss_hp
        }

        # Backup grunts in later boss levels
        if level_id >= 20:
            enemies.append({"type": "bandit", "x": 16 * 14, "y": 9 * 16})
        if level_id >= 40:
            enemies.append({"type": "brawler", "x": 16 * (cols - 16), "y": 9 * 16})

    else:
        # Standard Level Layout with Platforms, Hazards & Outlaw Patrols
        # Create 3-4 elevated structures
        sections = [
            (8, 14, 12),
            (18, 25, 10),
            (29, 36, 12),
            (38, 44, 9)
        ]

        for s_idx, (start_c, end_c, plat_r) in enumerate(sections):
            if end_c >= cols - 4:
                continue

            # Build platform
            plat_type = TILE_PLATFORM if s_idx % 2 == 1 else TILE_WOOD
            for c in range(start_c, end_c):
                grid[plat_r][c] = plat_type

            # Add ground hazard under elevated areas
            hazard_type = TILE_CACTUS if chapter_num in (1, 5) else TILE_SPIKES
            if start_c + 2 < cols - 2:
                grid[floor_row - 1][start_c + 2] = hazard_type

            # Place enemy on platform or floor
            if s_idx == 0:
                e_type = "bandit"
            elif s_idx == 1:
                e_type = "brawler" if chapter_num >= 2 else "bandit"
            elif s_idx == 2:
                e_type = "sniper" if chapter_num >= 3 else ("brawler" if chapter_num >= 2 else "bandit")
            else:
                e_type = "grenadier" if chapter_num >= 4 else "bandit"

            # Spawn enemy
            enemies.append({
                "type": e_type,
                "x": int((start_c + 2) * 16),
                "y": int((plat_r - 2) * 16)
            })

        # Additional floor patrol
        enemies.append({
            "type": "bandit" if chapter_num == 1 else ("brawler" if chapter_num == 2 else "bandit"),
            "x": int((mid_col + 4) * 16),
            "y": int((floor_row - 2) * 16)
        })

    # Compose final JSON structure
    level_dict = {
        "id": level_id,
        "chapter": chapter_num,
        "name": f"Level {level_id}: {chap_info['gang_name'] if not is_boss_level else chap_info['boss_name']}",
        "theme": chap_info["theme"],
        "width": cols,
        "height": rows,
        "player_spawn": player_spawn,
        "tiles": grid,
        "enemies": enemies
    }

    if boss_data:
        level_dict["boss"] = boss_data

    return level_dict

def generate_all_levels(overwrite=False):
    os.makedirs(LEVELS_DIR, exist_ok=True)
    generated_count = 0

    for level_num in range(1, TOTAL_LEVELS + 1):
        file_path = os.path.join(LEVELS_DIR, f"level_{level_num:02d}.json")
        if not os.path.exists(file_path) or overwrite:
            level_data = generate_level_data(level_num)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(level_data, f, indent=2)
            generated_count += 1

    return generated_count

if __name__ == "__main__":
    count = generate_all_levels(overwrite=True)
    print(f"Successfully generated {count} levels in {LEVELS_DIR}")
