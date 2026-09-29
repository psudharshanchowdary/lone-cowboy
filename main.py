"""
Main entry point for Lone Cowboy: Wild West Outlaws.
Initializes Pygame, creates window display, and drives the main 60 FPS game loop.
"""
import sys
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE
from core.game import GameManager

def main():
    # Initialize core Pygame modules
    pygame.init()
    pygame.font.init()

    # Create game window (960 x 540)
    display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF)
    pygame.display.set_caption(TITLE)

    # Clock for delta-time regulation
    clock = pygame.time.Clock()
    game_manager = GameManager(display)

    running = True
    while running:
        # Calculate delta time in seconds (clamped to prevent tunneling on lag)
        dt = min(0.05, clock.tick(FPS) / 1000.0)

        # Event handling
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        # Propagate events to game manager
        game_manager.handle_events(events)

        # Update gameplay / physics
        game_manager.update(dt)

        # Render frame
        game_manager.draw()
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
