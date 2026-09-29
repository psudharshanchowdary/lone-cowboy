"""
Headless Automated Engine Verification Suite for Lone Cowboy.
Tests physics, player controls, combat mechanics, enemy AI, tile collision,
JSON level loading, and all 52 level files without requiring an interactive window.
"""
import os
import sys

# Force headless dummy video/audio drivers for automated testing
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

import pygame
import unittest
from config import TOTAL_LEVELS, LEVELS_DIR
from world.level_generator import generate_all_levels
from world.level_loader import LevelLoader
from entities.player import Player
from entities.enemies.bandit import Bandit
from entities.enemies.brawler import Brawler
from entities.enemies.sniper import Sniper
from entities.enemies.grenadier import Grenadier
from entities.enemies.boss import Boss
from core.game import GameManager, STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER, STATE_LEVEL_COMPLETE
from core.input_handler import InputHandler
from gfx.sprites import SpriteManager

class TestLoneCowboyGame(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.font.init()
        cls.display = pygame.display.set_mode((960, 540))
        # Ensure all 52 levels are generated
        generate_all_levels(overwrite=True)

    def setUp(self):
        self.game = GameManager(self.display)

    def test_01_all_52_levels_exist_and_load(self):
        """Verify that all 52 levels parse correctly into tilemaps, spawns, and enemies."""
        for lvl_id in range(1, TOTAL_LEVELS + 1):
            lvl_path = os.path.join(LEVELS_DIR, f"level_{lvl_id:02d}.json")
            self.assertTrue(os.path.exists(lvl_path), f"Level file missing: {lvl_path}")
            tilemap, spawn, enemies, meta = LevelLoader.load_level(lvl_path)
            self.assertIsNotNone(tilemap)
            self.assertEqual(meta["id"], lvl_id)
            self.assertGreater(tilemap.cols, 0)
            self.assertGreater(tilemap.rows, 0)
            self.assertGreater(len(spawn), 0)

            # Boss levels check
            if lvl_id in (10, 20, 30, 40, 52):
                has_boss = any(isinstance(e, Boss) for e in enemies)
                self.assertTrue(has_boss, f"Boss missing in designated boss level {lvl_id}")

    def test_02_sprite_generation(self):
        """Verify procedural pixel art surfaces render without error."""
        sm = SpriteManager.get_instance()
        # Player states
        for state in ("idle", "walk", "jump", "crouch", "shoot", "melee"):
            surf_r = sm.get_player_sprite(state, facing_right=True)
            surf_l = sm.get_player_sprite(state, facing_right=False)
            self.assertIsNotNone(surf_r)
            self.assertIsNotNone(surf_l)

        # Enemies
        for e_type in ("bandit", "brawler", "sniper", "grenadier", "boss"):
            surf = sm.get_enemy_sprite(e_type, state="patrol", facing_right=True)
            self.assertIsNotNone(surf)

        # Tiles & Props
        for t_type in ("sandstone", "wood", "platform", "cactus", "spikes", "checkpoint_on", "checkpoint_off", "exit"):
            surf = sm.get_tile_sprite(t_type)
            self.assertIsNotNone(surf)

        # Bullets and items
        self.assertIsNotNone(sm.get_bullet_sprite())
        self.assertIsNotNone(sm.get_dynamite_sprite())
        self.assertIsNotNone(sm.get_heart_sprite(True))
        self.assertIsNotNone(sm.get_heart_sprite(False))
        self.assertIsNotNone(sm.get_cylinder_sprite(6))

    def test_03_player_movement_and_physics(self):
        """Verify walking, gravity, jumping, and crouching adjustments."""
        self.game.load_level(1)
        player = self.game.player
        initial_y = player.y

        # 1. Simulate running right
        inputs = InputHandler()
        inputs.move_x = 1
        inputs.is_running = True
        player.handle_input(inputs, self.game.tilemap)
        self.assertGreater(player.vx, 100.0)

        # Step physics forward
        for _ in range(10):
            player.update(self.game.tilemap, dt=1.0/60.0)
        self.assertGreater(player.x, player.spawn_x)

        # 2. Simulate jumping
        inputs = InputHandler()
        inputs.jump_pressed = True
        inputs.jump_held = True
        player.handle_input(inputs, self.game.tilemap)
        self.assertLess(player.vy, -200.0)

        # 3. Simulate crouch
        inputs = InputHandler()
        inputs.is_crouching = True
        player.on_ground = True
        player.handle_input(inputs, self.game.tilemap)
        self.assertTrue(player.is_crouching)
        self.assertEqual(player.height, player.crouch_height)

    def test_04_revolver_combat_and_reloading(self):
        """Verify 6-round capacity, firing, bullet physics, and cylinder reload."""
        self.game.load_level(1)
        player = self.game.player

        self.assertEqual(player.revolver.ammo, 6)

        # Fire 6 shots
        inputs = InputHandler()
        inputs.shoot_pressed = True

        for i in range(6):
            player.revolver.cooldown_timer = 0.0
            bullets, _, _ = player.handle_input(inputs, self.game.tilemap)
            self.assertEqual(len(bullets), 1)
            self.assertEqual(player.revolver.ammo, 5 - i)

        # 7th shot when empty should fail and trigger reload
        player.revolver.cooldown_timer = 0.0
        bullets, _, _ = player.handle_input(inputs, self.game.tilemap)
        self.assertEqual(len(bullets), 0)
        self.assertTrue(player.revolver.is_reloading)

        # Fast forward reload timer
        player.revolver.update(1.5)
        self.assertFalse(player.revolver.is_reloading)
        self.assertEqual(player.revolver.ammo, 6)

    def test_05_melee_knife_attack(self):
        """Verify knife slash hitbox creation and damage to enemy."""
        self.game.load_level(1)
        player = self.game.player
        bandit = Bandit(player.x + 16, player.y)

        inputs = InputHandler()
        inputs.melee_pressed = True
        _, _, melee_strikes = player.handle_input(inputs, self.game.tilemap)
        self.assertEqual(len(melee_strikes), 1)

        strike = melee_strikes[0]
        initial_hp = bandit.health
        hit = strike.check_hit(bandit)
        self.assertTrue(hit)
        self.assertLess(bandit.health, initial_hp)

    def test_06_dynamite_throwing_and_explosion(self):
        """Verify dynamite projectile throwing, fuse countdown, and explosion."""
        self.game.load_level(1)
        player = self.game.player
        bandit = Bandit(player.x + 30, player.y)

        inputs = InputHandler()
        inputs.dynamite_pressed = True
        _, dynamites, _ = player.handle_input(inputs, self.game.tilemap)
        self.assertEqual(len(dynamites), 1)
        dyn = dynamites[0]

        # Fast forward fuse
        dyn.fuse = 0.01
        dyn.update(self.game.tilemap, dt=0.02)
        dyn.explode(self.game.tilemap, [bandit, player])
        self.assertFalse(dyn.alive)

    def test_07_enemy_ai_and_player_damage(self):
        """Verify enemy detects player and fires back."""
        self.game.load_level(1)
        player = self.game.player
        bandit = Bandit(player.x + 80, player.y)

        # Step AI until bandit fires
        fired = False
        for _ in range(60):
            bullets = bandit.update_ai(player, self.game.tilemap, dt=1.0/60.0)
            if bullets:
                fired = True
                # Check bullet damage to player
                bullet = bullets[0]
                bullet.x = player.x + 2
                bullet.y = player.y + 2
                initial_hp = player.health
                hit = bullet.check_hit(player)
                self.assertTrue(hit)
                self.assertLess(player.health, initial_hp)
                break
        self.assertTrue(fired, "Bandit did not shoot when player in line of sight")

    def test_08_checkpoint_activation(self):
        """Verify touching checkpoint changes respawn position and activates lantern."""
        self.game.load_level(1)
        player = self.game.player
        mid_col = self.game.tilemap.cols // 2
        cp_x = mid_col * 16

        # Move player to checkpoint location
        player.x = cp_x
        player.y = (15 - 2) * 16
        cp_pos = self.game.tilemap.check_checkpoints(player.rect)
        self.assertIsNotNone(cp_pos)
        player.set_checkpoint(cp_pos[0], cp_pos[1])
        self.assertEqual(player.checkpoint_x, cp_pos[0])

        # Test respawn returns to checkpoint
        player.x = 999
        player.take_damage(99)
        player.respawn_at_checkpoint()
        self.assertEqual(player.x, cp_pos[0])
        self.assertEqual(player.health, player.max_health)

    def test_09_full_game_loop_step(self):
        """Verify game updates and draws without throwing errors."""
        self.game.load_level(1)
        for _ in range(120):  # Simulate 2 seconds of gameplay
            self.game.update(dt=1.0/60.0)
            self.game.draw()
        self.assertEqual(self.game.state, STATE_PLAYING)

    def test_10_level_52_boss_gauntlet(self):
        """Verify Level 52 multi-phase boss gauntlet progression through all 5 gang waves."""
        from core.game import STATE_VICTORY
        self.game.load_level(52)
        self.assertEqual(self.game.gauntlet_wave, 1)

        # Defeat waves sequentially
        for expected_wave in range(1, 6):
            self.assertEqual(self.game.gauntlet_wave, expected_wave)
            self.assertIsNotNone(self.game.boss)

            # Eliminate all enemies in current wave
            for e in self.game.enemies:
                e.health = 0
                e.is_alive = False

            # Update game loop to trigger next wave or victory
            self.game.update(dt=1.0/60.0)

        # After wave 5 defeat, state should be VICTORY!
        self.assertEqual(self.game.state, STATE_VICTORY)

if __name__ == "__main__":
    unittest.main()
