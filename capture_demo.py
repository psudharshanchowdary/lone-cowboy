"""
Demo screenshot generator for Lone Cowboy.
Runs the game engine and saves screenshots of:
1. Main Menu
2. Level 1 Gameplay (Cowboy facing Rattlesnake Bandit)
3. Combat action (Revolver gunshot, muzzle flash, bullet trail, particles)
4. Level Select screen (52 levels across 5 chapters)
5. Level 52 Boss Gauntlet showdown (Facing El Diablo)
"""
import os
import sys

# Headless rendering so it works reliably in any environment
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from core.game import GameManager, STATE_LEVEL_SELECT, STATE_PLAYING
from core.input_handler import InputHandler

def main():
    pygame.init()
    pygame.font.init()

    output_dir = os.path.join(PROJECT_ROOT, "screenshots")
    os.makedirs(output_dir, exist_ok=True)

    # 960 x 540 window surface
    display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    game = GameManager(display)

    # 1. Main Menu Screenshot
    game.draw()
    pygame.image.save(display, os.path.join(output_dir, "01_main_menu.png"))
    print("Saved 01_main_menu.png")

    # 2. Level Select Screen Screenshot
    game.state = STATE_LEVEL_SELECT
    game.menus.level_select_cursor = 1
    game.menus.level_select_chapter = 1
    game.draw()
    pygame.image.save(display, os.path.join(output_dir, "02_level_select.png"))
    print("Saved 02_level_select.png")

    # 3. Level 1 Gameplay Screenshot
    game.load_level(1)
    # Simulate a few steps for camera & physics to settle
    for _ in range(30):
        game.update(1.0 / 60.0)
    game.draw()
    pygame.image.save(display, os.path.join(output_dir, "03_level_1_gameplay.png"))
    print("Saved 03_level_1_gameplay.png")

    # 4. Combat Gunfight Action Screenshot (Shooting revolver, muzzle flash, bullet tracer)
    inputs = InputHandler()
    inputs.shoot_pressed = True
    new_bullets, _, _ = game.player.handle_input(inputs, game.tilemap)
    if new_bullets:
        game.bullets.extend(new_bullets)
    # Step forward 2 frames so bullet travels and particles expand
    for _ in range(2):
        game.update(1.0 / 60.0)
    game.draw()
    pygame.image.save(display, os.path.join(output_dir, "04_gunfight_action.png"))
    print("Saved 04_gunfight_action.png")

    # 5. Level 52 Boss Gauntlet Showdown Screenshot
    game.load_level(52)
    # Move player towards boss arena center
    game.player.x = (game.tilemap.cols // 2 - 4) * 16
    for _ in range(15):
        game.update(1.0 / 60.0)
    game.draw()
    pygame.image.save(display, os.path.join(output_dir, "05_boss_gauntlet_level52.png"))
    print("Saved 05_boss_gauntlet_level52.png")

    pygame.quit()
    print("All demo screenshots generated successfully!")

if __name__ == "__main__":
    main()
