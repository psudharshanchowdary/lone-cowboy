"""
Main Game Engine and Scene Manager for Lone Cowboy.
Connects input, physics simulation, combat collision, camera, HUD,
and state transitions.
"""
import os
import pygame
from config import (
    INTERNAL_WIDTH, INTERNAL_HEIGHT, SCALE_FACTOR,
    LEVELS_DIR, CHAPTERS, TOTAL_LEVELS, FINAL_BOSS_LEVEL,
    COLOR_SUNSET_SKY, COLOR_DESERT_SAND, COLOR_SANDSTONE
)
from core.camera import Camera
from core.input_handler import InputHandler
from entities.player import Player
from entities.enemies.bandit import Bandit
from entities.enemies.brawler import Brawler
from entities.enemies.sniper import Sniper
from entities.enemies.grenadier import Grenadier
from entities.enemies.boss import Boss
from world.level_loader import LevelLoader
from world.level_generator import generate_all_levels
from ui.hud import HUD
from ui.menu import MenuSystem, save_game_progress
from gfx.particles import ParticleManager

STATE_MAIN_MENU = "MAIN_MENU"
STATE_LEVEL_SELECT = "LEVEL_SELECT"
STATE_CONTROLS = "CONTROLS"
STATE_PLAYING = "PLAYING"
STATE_PAUSED = "PAUSED"
STATE_GAME_OVER = "GAME_OVER"
STATE_LEVEL_COMPLETE = "LEVEL_COMPLETE"
STATE_VICTORY = "VICTORY"

class GameManager:
    def __init__(self, display_surface):
        self.display = display_surface
        self.canvas = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))

        # Core subsystems
        self.camera = Camera(INTERNAL_WIDTH, INTERNAL_HEIGHT)
        self.input = InputHandler()
        self.hud = HUD()
        self.menus = MenuSystem()
        self.particles = ParticleManager.get_instance()

        # Gameplay state
        self.state = STATE_MAIN_MENU
        self.current_level_num = 1
        self.level_meta = {}
        self.tilemap = None
        self.player = None
        self.enemies = []
        self.boss = None
        self.bullets = []
        self.dynamites = []
        self.melee_hitboxes = []
        self.gauntlet_wave = 1

        # Ensure all 52 levels exist
        generate_all_levels(overwrite=False)

    def setup_gauntlet_wave(self, wave_index):
        """Sets up escalating gang leader waves for Level 52 Boss Gauntlet."""
        self.gauntlet_wave = wave_index
        arena_cx = (self.tilemap.cols // 2) * 16
        boss_x = (self.tilemap.cols - 8) * 16
        boss_y = (15 - 2) * 16

        if wave_index == 1:
            self.boss = Boss(boss_x, boss_y, boss_name="Gauntlet 1/5: Rattlesnake Jake", max_health=8)
            self.enemies = [self.boss, Bandit(arena_cx, boss_y)]
        elif wave_index == 2:
            self.boss = Boss(boss_x, boss_y, boss_name="Gauntlet 2/5: Iron Bull Logan", max_health=10)
            self.enemies = [self.boss, Brawler(arena_cx - 40, boss_y), Brawler(arena_cx + 40, boss_y)]
        elif wave_index == 3:
            self.boss = Boss(boss_x, boss_y, boss_name="Gauntlet 3/5: One-Eyed Silas", max_health=10)
            self.enemies = [self.boss, Sniper(arena_cx, 10 * 16)]
        elif wave_index == 4:
            self.boss = Boss(boss_x, boss_y, boss_name="Gauntlet 4/5: Mad Pete 'Kaboom'", max_health=12)
            self.enemies = [self.boss, Grenadier(arena_cx, 10 * 16)]
        elif wave_index == 5:
            self.boss = Boss(boss_x, boss_y, boss_name="Final Boss: El Diablo", max_health=18)
            self.enemies = [self.boss, Bandit(arena_cx - 60, boss_y), Brawler(arena_cx + 60, boss_y)]

        self.hud.trigger_checkpoint_banner()

    def load_level(self, level_num):
        self.current_level_num = max(1, min(TOTAL_LEVELS, level_num))
        level_file = os.path.join(LEVELS_DIR, f"level_{self.current_level_num:02d}.json")

        self.tilemap, spawn_pos, self.enemies, self.level_meta = LevelLoader.load_level(level_file)

        # Initialize Player at spawn
        self.player = Player(spawn_pos[0], spawn_pos[1])
        self.player.set_checkpoint(spawn_pos[0], spawn_pos[1])

        # If Level 52, initiate Wave 1 of the Boss Gauntlet
        if self.current_level_num == FINAL_BOSS_LEVEL:
            self.setup_gauntlet_wave(1)
        else:
            # Find boss among enemies if present
            self.boss = next((e for e in self.enemies if e.enemy_type == "boss"), None)

        # Clear active projectiles & particles
        self.bullets.clear()
        self.dynamites.clear()
        self.melee_hitboxes.clear()
        self.particles.clear()

        # Configure camera bounds
        self.camera.set_bounds(self.tilemap.width_px, self.tilemap.height_px)
        self.camera.x = max(0, spawn_pos[0] - INTERNAL_WIDTH // 2)
        self.camera.y = max(0, spawn_pos[1] - INTERNAL_HEIGHT // 2)

        self.state = STATE_PLAYING

    def handle_events(self, events):
        self.input.process_events(events)

        if self.state == STATE_MAIN_MENU:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.menus.selected_option = (self.menus.selected_option - 1) % 4
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.menus.selected_option = (self.menus.selected_option + 1) % 4
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        sel = self.menus.selected_option
                        if sel == 0:
                            # Start Adventure
                            unlocked = self.menus.save_data.get("unlocked_level", 1)
                            self.load_level(unlocked)
                        elif sel == 1:
                            self.state = STATE_LEVEL_SELECT
                            self.menus.level_select_cursor = 1
                            self.menus.level_select_chapter = 1
                        elif sel == 2:
                            self.state = STATE_CONTROLS
                        elif sel == 3:
                            pygame.event.post(pygame.event.Event(pygame.QUIT))

        elif self.state == STATE_LEVEL_SELECT:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = STATE_MAIN_MENU
                        self.menus.selected_option = 1
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        if pygame.key.get_mods() & pygame.KMOD_SHIFT or event.key == pygame.K_LEFT:
                            self.menus.level_select_cursor = max(1, self.menus.level_select_cursor - 1)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.menus.level_select_cursor = min(TOTAL_LEVELS, self.menus.level_select_cursor + 1)
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        self.menus.level_select_cursor = max(1, self.menus.level_select_cursor - 5)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.menus.level_select_cursor = min(TOTAL_LEVELS, self.menus.level_select_cursor + 5)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.load_level(self.menus.level_select_cursor)

            # Auto sync active chapter preview based on cursor
            cur = self.menus.level_select_cursor
            if cur <= 10:
                self.menus.level_select_chapter = 1
            elif cur <= 20:
                self.menus.level_select_chapter = 2
            elif cur <= 30:
                self.menus.level_select_chapter = 3
            elif cur <= 40:
                self.menus.level_select_chapter = 4
            else:
                self.menus.level_select_chapter = 5

        elif self.state == STATE_CONTROLS:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                        self.state = STATE_MAIN_MENU

        elif self.state == STATE_PLAYING:
            if self.input.pause_pressed:
                self.state = STATE_PAUSED
                self.menus.selected_option = 0

        elif self.state == STATE_PAUSED:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.menus.selected_option = (self.menus.selected_option - 1) % 4
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.menus.selected_option = (self.menus.selected_option + 1) % 4
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        sel = self.menus.selected_option
                        if sel == 0:
                            self.state = STATE_PLAYING
                        elif sel == 1:
                            self.load_level(self.current_level_num)
                        elif sel == 2:
                            self.state = STATE_LEVEL_SELECT
                        elif sel == 3:
                            self.state = STATE_MAIN_MENU

        elif self.state == STATE_GAME_OVER:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.menus.selected_option = (self.menus.selected_option - 1) % 4
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.menus.selected_option = (self.menus.selected_option + 1) % 4
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        sel = self.menus.selected_option
                        if sel == 0:
                            # Retry from Checkpoint
                            self.player.respawn_at_checkpoint()
                            self.state = STATE_PLAYING
                        elif sel == 1:
                            self.load_level(self.current_level_num)
                        elif sel == 2:
                            self.state = STATE_LEVEL_SELECT
                        elif sel == 3:
                            self.state = STATE_MAIN_MENU

        elif self.state == STATE_LEVEL_COMPLETE:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.menus.selected_option = (self.menus.selected_option - 1) % 3
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.menus.selected_option = (self.menus.selected_option + 1) % 3
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        sel = self.menus.selected_option
                        if sel == 0:
                            # Next Level
                            if self.current_level_num < TOTAL_LEVELS:
                                self.load_level(self.current_level_num + 1)
                            else:
                                self.state = STATE_VICTORY
                        elif sel == 1:
                            self.state = STATE_LEVEL_SELECT
                        elif sel == 2:
                            self.state = STATE_MAIN_MENU

        elif self.state == STATE_VICTORY:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s):
                        self.menus.selected_option = (self.menus.selected_option + 1) % 2
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if self.menus.selected_option == 0:
                            self.state = STATE_LEVEL_SELECT
                        else:
                            self.state = STATE_MAIN_MENU

    def update(self, dt):
        if self.state != STATE_PLAYING:
            return

        # 1. Update Player Input & Actions
        new_bullets, new_dyn, new_melee = self.player.handle_input(self.input, self.tilemap)
        if new_bullets:
            self.bullets.extend(new_bullets)
            self.camera.trigger_shake(magnitude=1.5, duration=0.1)
        if new_dyn:
            self.dynamites.extend(new_dyn)
        if new_melee:
            self.melee_hitboxes.extend(new_melee)
            self.camera.trigger_shake(magnitude=2.0, duration=0.12)

        # 2. Update Player Physics
        self.player.update(self.tilemap, dt)

        # Fall out of world death check
        if self.player.y > self.tilemap.height_px + 32:
            self.player.health = 0
            self.player.is_alive = False

        if not self.player.is_alive:
            self.state = STATE_GAME_OVER
            self.menus.selected_option = 0
            return

        # 3. Hazard Check (Cactus / Spikes)
        hazards = self.tilemap.get_hazards_near(self.player.rect)
        for hz in hazards:
            if self.player.rect.colliderect(hz):
                self.player.take_damage(1, knockback_x=-100 if self.player.facing_right else 100, knockback_y=-140)

        # 4. Checkpoints
        new_cp = self.tilemap.check_checkpoints(self.player.rect)
        if new_cp:
            self.player.set_checkpoint(new_cp[0], new_cp[1])
            self.hud.trigger_checkpoint_banner()

        # 5. Exit door / Level Completion Check
        if self.current_level_num == FINAL_BOSS_LEVEL:
            all_wave_defeated = all(not e.is_alive for e in self.enemies)
            if all_wave_defeated:
                if self.gauntlet_wave < 5:
                    self.setup_gauntlet_wave(self.gauntlet_wave + 1)
                else:
                    save_game_progress(TOTAL_LEVELS, TOTAL_LEVELS)
                    self.menus.reload_save()
                    self.state = STATE_VICTORY
                    self.menus.selected_option = 0
                    return
        else:
            # Complete if exit reached and (if boss level, boss is defeated)
            boss_defeated = (self.boss is None) or (not self.boss.is_alive)
            if self.tilemap.check_exit(self.player.rect) and boss_defeated:
                save_game_progress(self.current_level_num + 1, self.current_level_num)
                self.menus.reload_save()
                self.state = STATE_LEVEL_COMPLETE
                self.menus.selected_option = 0
                return

        # 6. Update Enemies AI
        for enemy in self.enemies:
            if not enemy.is_alive:
                continue
            if enemy.enemy_type == "boss":
                b_bullets, b_dyn = enemy.update_ai(self.player, self.tilemap, dt)
                if b_bullets:
                    self.bullets.extend(b_bullets)
                if b_dyn:
                    self.dynamites.extend(b_dyn)
            elif enemy.enemy_type in ("bandit", "sniper"):
                e_bullets = enemy.update_ai(self.player, self.tilemap, dt)
                if e_bullets:
                    self.bullets.extend(e_bullets)
            elif enemy.enemy_type == "grenadier":
                e_dyn = enemy.update_ai(self.player, self.tilemap, dt)
                if e_dyn:
                    self.dynamites.extend(e_dyn)
            elif enemy.enemy_type == "brawler":
                e_melee = enemy.update_ai(self.player, self.tilemap, dt)
                if e_melee:
                    self.melee_hitboxes.extend(e_melee)

        # 7. Update Bullets
        for b in self.bullets:
            b.update(self.tilemap, dt)
            if not b.alive:
                continue

            if b.owner == "player":
                for enemy in self.enemies:
                    if enemy.is_alive and b.check_hit(enemy):
                        break
            elif b.owner == "enemy":
                if self.player.is_alive and b.check_hit(self.player):
                    self.camera.trigger_shake(magnitude=3.0, duration=0.2)

        self.bullets = [b for b in self.bullets if b.alive]

        # 8. Update Dynamites
        for d in self.dynamites:
            d.update(self.tilemap, dt)
            if not d.alive:
                # Trigger explosion against all entities in blast radius
                all_targets = [self.player] + [e for e in self.enemies if e.is_alive]
                d.explode(self.tilemap, all_targets, self.camera)

        self.dynamites = [d for d in self.dynamites if d.alive]

        # 9. Update Melee Hitboxes
        for m in self.melee_hitboxes:
            m.update(dt)
            if not m.alive:
                continue
            if m.owner == "player":
                for enemy in self.enemies:
                    if enemy.is_alive:
                        m.check_hit(enemy)
            elif m.owner == "enemy":
                if self.player.is_alive:
                    m.check_hit(self.player)

        self.melee_hitboxes = [m for m in self.melee_hitboxes if m.alive]

        # 10. Update Particles & HUD
        self.particles.update(dt)
        self.hud.update(dt)

        # 11. Camera follow player
        self.camera.update(self.player.rect, self.player.facing_right, dt)

    def draw(self):
        # 1. Background
        chap_num = self.level_meta.get("chapter", 1)
        sky_color = CHAPTERS.get(chap_num, {}).get("sky_color", COLOR_SUNSET_SKY)
        self.canvas.fill(sky_color)

        if self.state in (STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER, STATE_LEVEL_COMPLETE):
            # Draw Tilemap
            self.tilemap.draw(self.canvas, self.camera)

            # Draw Particles
            self.particles.draw(self.canvas, self.camera)

            # Draw Enemies
            for enemy in self.enemies:
                enemy.draw(self.canvas, self.camera)

            # Draw Player
            self.player.draw(self.canvas, self.camera)

            # Draw Projectiles
            for b in self.bullets:
                b.draw(self.canvas, self.camera)
            for d in self.dynamites:
                d.draw(self.canvas, self.camera)

            # Draw In-Game HUD
            self.hud.draw(self.canvas, self.player, self.level_meta, self.boss)

        # Menu overlays
        if self.state == STATE_MAIN_MENU:
            self.menus.draw_main_menu(self.canvas)
        elif self.state == STATE_LEVEL_SELECT:
            self.menus.draw_level_select(self.canvas)
        elif self.state == STATE_CONTROLS:
            self.menus.draw_controls(self.canvas)
        elif self.state == STATE_PAUSED:
            self.menus.draw_pause_menu(self.canvas)
        elif self.state == STATE_GAME_OVER:
            self.menus.draw_game_over(self.canvas)
        elif self.state == STATE_LEVEL_COMPLETE:
            self.menus.draw_level_complete(self.canvas, self.current_level_num)
        elif self.state == STATE_VICTORY:
            self.menus.draw_victory_screen(self.canvas)

        # Scale canvas to display window
        scaled_surf = pygame.transform.scale(self.canvas, self.display.get_size())
        self.display.blit(scaled_surf, (0, 0))
