"""
Heads-Up Display (HUD) for Lone Cowboy.
Draws cowboy hearts, revolver cylinder and reload status, dynamite count,
level title, checkpoint notifications, and boss health bars.
"""
import pygame
from config import COLOR_WHITE, COLOR_GOLD, COLOR_RED
from gfx.sprites import SpriteManager
from ui.font_manager import FontManager

class HUD:
    def __init__(self):
        self.checkpoint_banner_timer = 0.0

    def trigger_checkpoint_banner(self):
        self.checkpoint_banner_timer = 2.0

    def update(self, dt):
        if self.checkpoint_banner_timer > 0.0:
            self.checkpoint_banner_timer -= dt

    def draw(self, surface, player, level_meta, boss=None):
        sm = SpriteManager.get_instance()

        # 1. Health (Hearts row in top-left)
        start_x = 8
        start_y = 8
        for i in range(player.max_health):
            heart_full = (i < player.health)
            heart_surf = sm.get_heart_sprite(full=heart_full)
            surface.blit(heart_surf, (start_x + i * 11, start_y))

        # 2. Level & Chapter Title (top-left below hearts)
        level_name = level_meta.get("name", "Wild West Frontier")
        FontManager.draw_text(surface, level_name, start_x, start_y + 13, size=12, color=COLOR_GOLD)

        # 3. Revolver Cylinder & Ammo (bottom-left)
        rev = player.revolver
        cylinder_x = 8
        cylinder_y = surface.get_height() - 28

        # Draw cylinder icon
        cylinder_surf = sm.get_cylinder_sprite(chambers_loaded=rev.ammo)
        surface.blit(cylinder_surf, (cylinder_x, cylinder_y))

        # Ammo text / Reload prompt
        if rev.is_reloading:
            # Flashing reload indicator
            reload_txt = f"RELOADING... {int(rev.reload_progress * 100)}%"
            FontManager.draw_text(surface, reload_txt, cylinder_x + 24, cylinder_y + 6, size=12, color=COLOR_RED)
        else:
            ammo_txt = f"{rev.ammo}/{rev.capacity} [R to Reload]"
            FontManager.draw_text(surface, ammo_txt, cylinder_x + 24, cylinder_y + 6, size=12, color=COLOR_WHITE)

        # 4. Dynamite Counter (bottom-left next to revolver)
        dyn_x = cylinder_x + 130
        dyn_y = cylinder_y + 6
        dyn_surf = sm.get_dynamite_sprite()
        surface.blit(dyn_surf, (dyn_x, dyn_y - 2))
        dyn_txt = f"x{player.dynamite.count} [K/RMB]"
        FontManager.draw_text(surface, dyn_txt, dyn_x + 12, dyn_y, size=12, color=COLOR_WHITE)

        # 5. Checkpoint banner (center top)
        if self.checkpoint_banner_timer > 0.0:
            center_x = surface.get_width() // 2
            FontManager.draw_text(surface, "CHECKPOINT ACTIVATED!", center_x, 30, size=14, color=COLOR_GOLD, center=True)

        # 6. Boss health bar (if boss exists and alive)
        if boss and boss.is_alive:
            boss.draw_boss_bar(surface, surface.get_width())
            FontManager.draw_text(surface, boss.boss_name, surface.get_width() // 2, 2, size=11, color=COLOR_GOLD, center=True)
