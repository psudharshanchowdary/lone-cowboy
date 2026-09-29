"""
Tilemap system for Lone Cowboy.
Manages grid layers, solid blocks, one-way platforms, hazards,
checkpoints, and viewport culling.
"""
import pygame
from config import TILE_SIZE
from gfx.sprites import SpriteManager

TILE_AIR = 0
TILE_SANDSTONE = 1
TILE_WOOD = 2
TILE_PLATFORM = 3
TILE_CACTUS = 4
TILE_SPIKES = 5
TILE_CHECKPOINT = 6
TILE_EXIT = 7

class Tilemap:
    def __init__(self, cols, rows, tiles_2d=None):
        self.cols = cols
        self.rows = rows
        self.tile_size = TILE_SIZE
        self.width_px = cols * TILE_SIZE
        self.height_px = rows * TILE_SIZE

        if tiles_2d:
            self.tiles = tiles_2d
        else:
            self.tiles = [[TILE_AIR for _ in range(cols)] for _ in range(rows)]

        # Checkpoints state: {(col, row): is_activated}
        self.checkpoints = {}
        for r in range(self.rows):
            for c in range(self.cols):
                if self.tiles[r][c] == TILE_CHECKPOINT:
                    self.checkpoints[(c, r)] = False

    def is_solid_at(self, col, row):
        if 0 <= col < self.cols and 0 <= row < self.rows:
            return self.tiles[row][col] in (TILE_SANDSTONE, TILE_WOOD)
        # Treat bounds as solid horizontally and bottom
        return False

    def is_platform_at(self, col, row):
        if 0 <= col < self.cols and 0 <= row < self.rows:
            return self.tiles[row][col] == TILE_PLATFORM
        return False

    def get_solid_tiles_near(self, rect):
        """Returns list of solid tile bounding Rects overlapping or adjacent to rect."""
        min_c = max(0, rect.left // self.tile_size - 1)
        max_c = min(self.cols - 1, rect.right // self.tile_size + 1)
        min_r = max(0, rect.top // self.tile_size - 1)
        max_r = min(self.rows - 1, rect.bottom // self.tile_size + 1)

        solids = []
        for r in range(min_r, max_r + 1):
            for c in range(min_c, max_c + 1):
                if self.tiles[r][c] in (TILE_SANDSTONE, TILE_WOOD):
                    solids.append(pygame.Rect(c * self.tile_size, r * self.tile_size, self.tile_size, self.tile_size))
        return solids

    def get_platform_tiles_near(self, rect):
        """Returns list of one-way platform Rects."""
        min_c = max(0, rect.left // self.tile_size - 1)
        max_c = min(self.cols - 1, rect.right // self.tile_size + 1)
        min_r = max(0, rect.top // self.tile_size - 1)
        max_r = min(self.rows - 1, rect.bottom // self.tile_size + 1)

        platforms = []
        for r in range(min_r, max_r + 1):
            for c in range(min_c, max_c + 1):
                if self.tiles[r][c] == TILE_PLATFORM:
                    platforms.append(pygame.Rect(c * self.tile_size, r * self.tile_size, self.tile_size, self.tile_size))
        return platforms

    def get_hazards_near(self, rect):
        """Returns list of hazard tile rects."""
        min_c = max(0, rect.left // self.tile_size)
        max_c = min(self.cols - 1, rect.right // self.tile_size)
        min_r = max(0, rect.top // self.tile_size)
        max_r = min(self.rows - 1, rect.bottom // self.tile_size)

        hazards = []
        for r in range(min_r, max_r + 1):
            for c in range(min_c, max_c + 1):
                if self.tiles[r][c] in (TILE_CACTUS, TILE_SPIKES):
                    hazards.append(pygame.Rect(c * self.tile_size + 2, r * self.tile_size + 4, self.tile_size - 4, self.tile_size - 4))
        return hazards

    def check_checkpoints(self, player_rect):
        """Checks if player touched an unlit checkpoint. Activates it and returns (x, y) if new."""
        for (c, r), active in self.checkpoints.items():
            cp_rect = pygame.Rect(c * self.tile_size, r * self.tile_size, self.tile_size, self.tile_size)
            if player_rect.colliderect(cp_rect) and not active:
                self.checkpoints[(c, r)] = True
                return (c * self.tile_size + 2, r * self.tile_size)
        return None

    def check_exit(self, player_rect):
        """Checks if player touched an exit door."""
        min_c = max(0, player_rect.left // self.tile_size)
        max_c = min(self.cols - 1, player_rect.right // self.tile_size)
        min_r = max(0, player_rect.top // self.tile_size)
        max_r = min(self.rows - 1, player_rect.bottom // self.tile_size)

        for r in range(min_r, max_r + 1):
            for c in range(min_c, max_c + 1):
                if self.tiles[r][c] == TILE_EXIT:
                    exit_rect = pygame.Rect(c * self.tile_size, r * self.tile_size, self.tile_size, self.tile_size)
                    if player_rect.colliderect(exit_rect):
                        return True
        return False

    def draw(self, surface, camera):
        """Viewport-culled tile rendering."""
        sm = SpriteManager.get_instance()

        start_col = max(0, int(camera.x // self.tile_size))
        end_col = min(self.cols, int((camera.x + camera.width) // self.tile_size) + 1)
        start_row = max(0, int(camera.y // self.tile_size))
        end_row = min(self.rows, int((camera.y + camera.height) // self.tile_size) + 1)

        for r in range(start_row, end_row):
            for c in range(start_col, end_col):
                tile_id = self.tiles[r][c]
                if tile_id == TILE_AIR:
                    continue

                draw_x, draw_y = camera.apply_coords(c * self.tile_size, r * self.tile_size)

                if tile_id == TILE_SANDSTONE:
                    surface.blit(sm.get_tile_sprite("sandstone"), (draw_x, draw_y))
                elif tile_id == TILE_WOOD:
                    surface.blit(sm.get_tile_sprite("wood"), (draw_x, draw_y))
                elif tile_id == TILE_PLATFORM:
                    surface.blit(sm.get_tile_sprite("platform"), (draw_x, draw_y))
                elif tile_id == TILE_CACTUS:
                    surface.blit(sm.get_tile_sprite("cactus"), (draw_x, draw_y))
                elif tile_id == TILE_SPIKES:
                    surface.blit(sm.get_tile_sprite("spikes"), (draw_x, draw_y))
                elif tile_id == TILE_CHECKPOINT:
                    active = self.checkpoints.get((c, r), False)
                    sprite_name = "checkpoint_on" if active else "checkpoint_off"
                    surface.blit(sm.get_tile_sprite(sprite_name), (draw_x, draw_y))
                elif tile_id == TILE_EXIT:
                    surface.blit(sm.get_tile_sprite("exit"), (draw_x, draw_y))
