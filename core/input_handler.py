"""
Input state manager for Lone Cowboy.
Translates raw Pygame events and keyboard/mouse state into gameplay actions.
"""
import pygame
from config import (
    KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN, KEY_JUMP, KEY_RUN,
    KEY_SHOOT, KEY_RELOAD, KEY_MELEE, KEY_DYNAMITE, KEY_INTERACT, KEY_PAUSE
)

class InputHandler:
    def __init__(self):
        self.move_x = 0
        self.move_y = 0
        self.is_running = False
        self.is_crouching = False
        self.jump_pressed = False
        self.jump_held = False
        self.shoot_pressed = False
        self.reload_pressed = False
        self.melee_pressed = False
        self.dynamite_pressed = False
        self.interact_pressed = False
        self.pause_pressed = False

        self.mouse_pos = (0, 0)
        self.mouse_clicked = False

    def process_events(self, events):
        """Reset per-frame single-press triggers and parse events."""
        self.jump_pressed = False
        self.shoot_pressed = False
        self.reload_pressed = False
        self.melee_pressed = False
        self.dynamite_pressed = False
        self.interact_pressed = False
        self.pause_pressed = False
        self.mouse_clicked = False

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in KEY_JUMP:
                    self.jump_pressed = True
                if event.key in KEY_SHOOT:
                    self.shoot_pressed = True
                if event.key in KEY_RELOAD:
                    self.reload_pressed = True
                if event.key in KEY_MELEE:
                    self.melee_pressed = True
                if event.key in KEY_DYNAMITE:
                    self.dynamite_pressed = True
                if event.key in KEY_INTERACT:
                    self.interact_pressed = True
                if event.key in KEY_PAUSE:
                    self.pause_pressed = True

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left Click = Shoot
                    self.shoot_pressed = True
                    self.mouse_clicked = True
                elif event.button == 2:  # Middle Click = Melee
                    self.melee_pressed = True
                elif event.button == 3:  # Right Click = Dynamite
                    self.dynamite_pressed = True

        # Continuous / held state polling
        keys = pygame.key.get_pressed()
        self.move_x = 0
        if any(keys[k] for k in KEY_LEFT):
            self.move_x -= 1
        if any(keys[k] for k in KEY_RIGHT):
            self.move_x += 1

        self.is_crouching = any(keys[k] for k in KEY_DOWN)
        self.is_running = any(keys[k] for k in KEY_RUN)
        self.jump_held = any(keys[k] for k in KEY_JUMP)
        self.mouse_pos = pygame.mouse.get_pos()
