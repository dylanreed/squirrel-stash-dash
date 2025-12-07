"""
Squirrel Yarn - Main Entry Point
An endless runner game where you play as a squirrel collecting yarn.
"""

import pygame
import sys
import asyncio
from game import Game


async def main():
    """Initialize Pygame and run the main game loop."""
    # Initialize Pygame
    pygame.init()

    # Set up display
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Stash Dash")

    # Set up clock for FPS control
    clock = pygame.time.Clock()
    FPS = 60

    # Create game instance
    game = Game(SCREEN_WIDTH, SCREEN_HEIGHT)

    # Main game loop
    running = True
    while running:
        # Calculate delta time (in seconds)
        dt = clock.tick(FPS) / 1000.0

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Pass keyboard events to game
            if event.type == pygame.KEYDOWN:
                result = game.handle_keypress(event.key)
                if result == "quit":
                    running = False

        # Get continuous keyboard input
        keys = pygame.key.get_pressed()

        # Update game state
        game.update(dt, keys)

        # Render game
        game.render(screen)

        # Update display
        pygame.display.flip()

        # Required for web (Pygbag)
        await asyncio.sleep(0)

    # Cleanup
    pygame.quit()


asyncio.run(main())
