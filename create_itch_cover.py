"""Generate a static splash screen image for itch.io cover."""
import pygame
import os

pygame.init()

# Game dimensions
WIDTH = 800
HEIGHT = 600

# Need to set a display mode first for convert_alpha to work
pygame.display.set_mode((1, 1), pygame.HIDDEN)

# Create surface
screen = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

# Load and scale splash scene background
splash_scene = pygame.image.load("assets/splash/splash_scene.png").convert_alpha()
splash_scene = pygame.transform.scale(splash_scene, (WIDTH, HEIGHT))
screen.blit(splash_scene, (0, 0))

# Load and scale foreground
splash_fg = pygame.image.load("assets/splash/splash_foreground.png").convert_alpha()
splash_fg = pygame.transform.scale(splash_fg, (WIDTH, HEIGHT))
screen.blit(splash_fg, (0, 0))

# Load STASH title (scale to 400x200)
stash_img = pygame.image.load("assets/splash/title_stash.png").convert_alpha()
stash_img = pygame.transform.scale(stash_img, (400, 200))
stash_x = WIDTH // 2 - 200
stash_y = 50
screen.blit(stash_img, (stash_x, stash_y))

# Load DASH title with speedlines (scale to 200x100)
dash_img = pygame.image.load("assets/splash/title_dash_speedlines.png").convert_alpha()
dash_img = pygame.transform.scale(dash_img, (200, 100))
dash_x = WIDTH // 2 - 100
dash_y = 180
screen.blit(dash_img, (dash_x, dash_y))

# Load squirrel
squirrel = pygame.image.load("assets/sprites/squirrel.png").convert_alpha()
# Position squirrel in the scene
squirrel_x = WIDTH // 2 - squirrel.get_width() // 2 + 50
squirrel_y = HEIGHT - 200
screen.blit(squirrel, (squirrel_x, squirrel_y))

# Add "Click to Play" text
font = pygame.font.Font(None, 36)
text = font.render("Click to Play!", True, (255, 255, 255))
text_shadow = font.render("Click to Play!", True, (0, 0, 0))
text_x = WIDTH // 2 - text.get_width() // 2
text_y = HEIGHT - 80
screen.blit(text_shadow, (text_x + 2, text_y + 2))
screen.blit(text, (text_x, text_y))

# Save the image
pygame.image.save(screen, "itch_cover.png")
print(f"Saved itch_cover.png ({WIDTH}x{HEIGHT})")

pygame.quit()
