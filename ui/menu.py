"""
Menu and Screen UI for Lone Cowboy:
- Main Menu
- 52-Level Select & Chapter Browser
- Controls Guide
- Pause Menu
- Game Over Screen
- Level Complete & Final Victory Screens
"""
import os
import json
import pygame
from config import (
    COLOR_BLACK, COLOR_WHITE, COLOR_GOLD, COLOR_RED, COLOR_DARK_BROWN,
    COLOR_DESERT_SAND, COLOR_IRON_GRAY, CHAPTERS, TOTAL_LEVELS, SAVE_FILE
)
from ui.font_manager import FontManager

def load_save_data():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"unlocked_level": 1, "completed_levels": []}

def save_game_progress(unlocked_level, completed_level=None):
    data = load_save_data()
    data["unlocked_level"] = max(data.get("unlocked_level", 1), unlocked_level)
    if completed_level and completed_level not in data.get("completed_levels", []):
        data.setdefault("completed_levels", []).append(completed_level)
    os.makedirs(os.path.dirname(SAVE_FILE), exist_ok=True)
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

class MenuSystem:
    def __init__(self):
        self.save_data = load_save_data()
        self.selected_option = 0
        self.level_select_chapter = 1
        self.level_select_cursor = 1

    def reload_save(self):
        self.save_data = load_save_data()

    # -------------------------------------------------------------
    # Main Menu
    # -------------------------------------------------------------
    def draw_main_menu(self, surface):
        surface.fill(COLOR_BLACK)

        # Decorative title banner
        center_x = surface.get_width() // 2
        FontManager.draw_text(surface, "L O N E   C O W B O Y", center_x, 40, size=28, color=COLOR_GOLD, center=True)
        FontManager.draw_text(surface, "W I L D   W E S T   O U T L A W S", center_x, 70, size=14, color=COLOR_DESERT_SAND, center=True)

        options = [
            "START ADVENTURE",
            "LEVEL SELECT (52 LEVELS)",
            "CONTROLS & HOW TO PLAY",
            "QUIT"
        ]

        start_y = 120
        for i, opt in enumerate(options):
            is_sel = (i == self.selected_option)
            prefix = "> " if is_sel else "  "
            color = COLOR_GOLD if is_sel else COLOR_WHITE
            FontManager.draw_text(surface, prefix + opt, center_x, start_y + i * 24, size=14, color=color, center=True)

        FontManager.draw_text(surface, "Use UP/DOWN Arrows + ENTER to Select", center_x, surface.get_height() - 20, size=11, color=COLOR_IRON_GRAY, center=True)

    # -------------------------------------------------------------
    # Level Select Menu (Chapters 1-5, 52 Levels)
    # -------------------------------------------------------------
    def draw_level_select(self, surface):
        surface.fill(COLOR_BLACK)
        center_x = surface.get_width() // 2

        FontManager.draw_text(surface, "LEVEL SELECT", center_x, 15, size=20, color=COLOR_GOLD, center=True)

        # Chapter Navigation Header
        chap_info = CHAPTERS[self.level_select_chapter]
        chap_title = f"< Chapter {self.level_select_chapter}: {chap_info['gang_name']} >"
        FontManager.draw_text(surface, chap_title, center_x, 38, size=13, color=COLOR_DESERT_SAND, center=True)
        FontManager.draw_text(surface, f"Theme: {chap_info['theme'].title()} | Boss: {chap_info['boss_name']}", center_x, 52, size=10, color=COLOR_IRON_GRAY, center=True)

        # Grid of levels in current chapter
        unlocked = self.save_data.get("unlocked_level", 1)
        levels = chap_info["levels"]

        start_x = 45
        start_y = 75
        col_width = 80
        row_height = 42

        for idx, lvl_num in enumerate(levels):
            c = idx % 5
            r = idx // 5
            bx = start_x + c * col_width
            by = start_y + r * row_height

            is_cur = (lvl_num == self.level_select_cursor)
            is_unlocked = (lvl_num <= unlocked) or True  # Allow sandbox selection of all 52 levels

            box_rect = pygame.Rect(bx, by, 72, 34)
            border_color = COLOR_GOLD if is_cur else (COLOR_WHITE if is_unlocked else COLOR_IRON_GRAY)
            bg_color = (60, 45, 30) if is_cur else COLOR_BLACK

            pygame.draw.rect(surface, bg_color, box_rect)
            pygame.draw.rect(surface, border_color, box_rect, 1)

            lvl_label = f"LVL {lvl_num}"
            if lvl_num in (10, 20, 30, 40, 52):
                lvl_label += " [BOSS]"
            FontManager.draw_text(surface, lvl_label, box_rect.centerx, box_rect.centery - 6, size=11, color=border_color, center=True)

            status_txt = "READY" if is_unlocked else "LOCKED"
            FontManager.draw_text(surface, status_txt, box_rect.centerx, box_rect.centery + 7, size=9, color=COLOR_WHITE if is_unlocked else COLOR_IRON_GRAY, center=True)

        FontManager.draw_text(surface, "LEFT/RIGHT to change Chapter | ARROWS to navigate | ENTER to Play | ESC to Back",
                              center_x, surface.get_height() - 16, size=10, color=COLOR_IRON_GRAY, center=True)

    # -------------------------------------------------------------
    # Controls Screen
    # -------------------------------------------------------------
    def draw_controls(self, surface):
        surface.fill(COLOR_BLACK)
        center_x = surface.get_width() // 2

        FontManager.draw_text(surface, "COWBOY CONTROLS & MECHANICS", center_x, 20, size=18, color=COLOR_GOLD, center=True)

        lines = [
            ("A / D or LEFT / RIGHT", "Walk left and right"),
            ("HOLD SHIFT", "Sprint / Run"),
            ("W / SPACE / UP", "Jump (variable height, coyote time)"),
            ("S / DOWN", "Crouch (reduces hitbox, duck under bullets)"),
            ("S + SPACE", "Drop down through wooden platforms"),
            ("LEFT CLICK / J", "Fire 6-Shooter Revolver"),
            ("R KEY", "Reload Revolver Cylinder"),
            ("F / V / MIDDLE CLICK", "Melee Bowie Knife strike (close combat)"),
            ("RIGHT CLICK / K", "Throw Dynamite Stick (fuse blast radius)"),
            ("LANTERNS", "Checkpoints (touch to save respawn point)"),
            ("SALOON DOORS", "Level Exit (clear all enemies or reach door)"),
            ("ESC / P", "Pause Game")
        ]

        start_y = 52
        for i, (ctrl, desc) in enumerate(lines):
            FontManager.draw_text(surface, ctrl, 40, start_y + i * 15, size=11, color=COLOR_GOLD)
            FontManager.draw_text(surface, "- " + desc, 195, start_y + i * 15, size=11, color=COLOR_WHITE)

        FontManager.draw_text(surface, "Press ESC or ENTER to return", center_x, surface.get_height() - 18, size=11, color=COLOR_DESERT_SAND, center=True)

    # -------------------------------------------------------------
    # In-Game Overlays: Pause, Game Over, Level Complete, Victory
    # -------------------------------------------------------------
    def draw_pause_menu(self, surface):
        # Translucent dark tint
        dim_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        dim_surf.fill((0, 0, 0, 180))
        surface.blit(dim_surf, (0, 0))

        center_x = surface.get_width() // 2
        FontManager.draw_text(surface, "PAUSED", center_x, 60, size=24, color=COLOR_GOLD, center=True)

        options = ["RESUME", "RESTART LEVEL", "LEVEL SELECT", "MAIN MENU"]
        for i, opt in enumerate(options):
            is_sel = (i == self.selected_option)
            prefix = "> " if is_sel else "  "
            color = COLOR_GOLD if is_sel else COLOR_WHITE
            FontManager.draw_text(surface, prefix + opt, center_x, 110 + i * 25, size=14, color=color, center=True)

    def draw_game_over(self, surface):
        dim_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        dim_surf.fill((40, 10, 10, 200))
        surface.blit(dim_surf, (0, 0))

        center_x = surface.get_width() // 2
        FontManager.draw_text(surface, "YOU MET YOUR MAKER", center_x, 60, size=24, color=COLOR_RED, center=True)
        FontManager.draw_text(surface, "The outlaws got the better of you this time, partner.", center_x, 90, size=11, color=COLOR_DESERT_SAND, center=True)

        options = ["RETRY FROM CHECKPOINT", "RESTART LEVEL", "LEVEL SELECT", "MAIN MENU"]
        for i, opt in enumerate(options):
            is_sel = (i == self.selected_option)
            prefix = "> " if is_sel else "  "
            color = COLOR_GOLD if is_sel else COLOR_WHITE
            FontManager.draw_text(surface, prefix + opt, center_x, 125 + i * 24, size=13, color=color, center=True)

    def draw_level_complete(self, surface, level_num):
        dim_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        dim_surf.fill((10, 30, 15, 200))
        surface.blit(dim_surf, (0, 0))

        center_x = surface.get_width() // 2
        FontManager.draw_text(surface, f"LEVEL {level_num} CLEARED!", center_x, 60, size=24, color=COLOR_GOLD, center=True)
        FontManager.draw_text(surface, "The frontier is one step closer to justice.", center_x, 90, size=11, color=COLOR_WHITE, center=True)

        options = ["CONTINUE TO NEXT LEVEL", "LEVEL SELECT", "MAIN MENU"]
        for i, opt in enumerate(options):
            is_sel = (i == self.selected_option)
            prefix = "> " if is_sel else "  "
            color = COLOR_GOLD if is_sel else COLOR_WHITE
            FontManager.draw_text(surface, prefix + opt, center_x, 130 + i * 25, size=14, color=color, center=True)

    def draw_victory_screen(self, surface):
        dim_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        dim_surf.fill((20, 20, 35, 220))
        surface.blit(dim_surf, (0, 0))

        center_x = surface.get_width() // 2
        FontManager.draw_text(surface, "THE WEST IS WON!", center_x, 45, size=26, color=COLOR_GOLD, center=True)
        FontManager.draw_text(surface, "ALL 52 LEVELS CONQUERED! GANG LEADERS VANQUISHED!", center_x, 80, size=12, color=COLOR_WHITE, center=True)
        FontManager.draw_text(surface, "From Rattlesnake Jake to El Diablo, none could outdraw you.", center_x, 100, size=10, color=COLOR_DESERT_SAND, center=True)

        options = ["LEVEL SELECT", "MAIN MENU"]
        for i, opt in enumerate(options):
            is_sel = (i == self.selected_option)
            prefix = "> " if is_sel else "  "
            color = COLOR_GOLD if is_sel else COLOR_WHITE
            FontManager.draw_text(surface, prefix + opt, center_x, 145 + i * 28, size=14, color=color, center=True)
