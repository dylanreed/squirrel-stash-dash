"""
UI elements for Squirrel Yarn game.
Handles score display, milestone signs, and game over screen.
"""

import pygame
import os
import math
import time
from typing import Optional, List, Tuple


class SplashScreen:
    """Animated splash screen with bouncing yarn and squirrel."""

    def __init__(self, screen_width: int = 800, screen_height: int = 600):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.start_time = time.time()

        # Fonts
        pygame.font.init()
        self.font_title = pygame.font.Font(None, 72)
        self.font_subtitle = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)

        # Colors
        self.title_color = (255, 215, 0)  # Gold
        self.bg_color = (135, 206, 235)  # Sky blue

        # Animated yarn balls
        self.yarn_balls: List[dict] = []
        yarn_colors = [
            (220, 20, 60),   # Red
            (34, 139, 34),   # Green
            (30, 144, 255),  # Blue
            (255, 215, 0),   # Yellow
            (255, 0, 255),   # Magenta
            (0, 255, 255),   # Cyan
        ]
        for i, color in enumerate(yarn_colors):
            self.yarn_balls.append({
                "x": 100 + i * 120,
                "y": 450,
                "color": color,
                "phase": i * 0.5,
                "size": 20,
            })

        # Squirrel position for animation
        self.squirrel_x = -100
        self.squirrel_entered = False

        # Try to load squirrel sprite
        self.squirrel_image = None
        sprite_path = os.path.join("assets", "sprites", "squirrel.png")
        if os.path.exists(sprite_path):
            try:
                self.squirrel_image = pygame.image.load(sprite_path).convert_alpha()
            except pygame.error:
                pass  # Will use fallback

        # Title images - STASH drops from top, DASH zooms from left
        self.stash_image = None
        self.dash_image = None
        self.stash_x = screen_width // 2 - 200  # Centered horizontally (400px wide / 2)
        self.stash_y = -250  # Start off-screen top (bigger image)
        self.stash_velocity_y = 0  # For bounce physics
        self.stash_settled = False
        self.dash_x = -300  # Start off-screen left (west)
        self.dash_y = 150  # Below STASH (STASH is 200px tall, starts at y=50)
        self.titles_entered = False

        # Load title images
        stash_path = os.path.join("assets", "splash", "title_stash.png")
        dash_path = os.path.join("assets", "splash", "title_dash.png")
        if os.path.exists(stash_path):
            try:
                self.stash_image = pygame.image.load(stash_path).convert_alpha()
                # Scale up STASH to be twice as big (400x200)
                self.stash_image = pygame.transform.scale(self.stash_image, (400, 200))
            except pygame.error:
                pass
        if os.path.exists(dash_path):
            try:
                self.dash_image = pygame.image.load(dash_path).convert_alpha()
                # Scale up for visibility
                self.dash_image = pygame.transform.scale(self.dash_image, (200, 100))
            except pygame.error:
                pass

        # Load splash scene background
        self.splash_scene = None
        splash_scene_path = os.path.join("assets", "splash", "splash_scene.png")
        if os.path.exists(splash_scene_path):
            try:
                self.splash_scene = pygame.image.load(splash_scene_path).convert_alpha()
                # Scale to fit screen
                self.splash_scene = pygame.transform.scale(self.splash_scene, (screen_width, screen_height))
            except pygame.error:
                pass

        # Load splash foreground (trees framing the scene)
        self.splash_foreground = None
        splash_fg_path = os.path.join("assets", "splash", "splash_foreground.png")
        if os.path.exists(splash_fg_path):
            try:
                self.splash_foreground = pygame.image.load(splash_fg_path).convert_alpha()
                # Scale to fit screen
                self.splash_foreground = pygame.transform.scale(self.splash_foreground, (screen_width, screen_height))
            except pygame.error:
                pass

    def update(self, dt: float) -> None:
        """Update splash screen animations."""
        elapsed = time.time() - self.start_time

        stash_target_y = 30  # Where STASH settles
        dash_target_x = self.screen_width // 2 + 50  # Right of center, under STASH

        # Phase 1: STASH drops from top with bounce
        if not self.stash_settled:
            # Apply gravity
            self.stash_velocity_y += 800 * dt  # Gravity
            self.stash_y += self.stash_velocity_y * dt

            # Bounce when hitting target
            if self.stash_y >= stash_target_y:
                self.stash_y = stash_target_y
                self.stash_velocity_y = -self.stash_velocity_y * 0.5  # Bounce with dampening

                # Settle if bounce is small enough
                if abs(self.stash_velocity_y) < 50:
                    self.stash_velocity_y = 0
                    self.stash_settled = True

        # Phase 2: DASH zooms in fast from left (west) after STASH settles
        if self.stash_settled and not self.titles_entered:
            self.dash_x += 1200 * dt  # Fast zoom
            if self.dash_x >= dash_target_x:
                self.dash_x = dash_target_x
                self.titles_entered = True

        # Phase 3: Gentle bobbing when both settled
        if self.titles_entered:
            bob = math.sin(elapsed * 1.5) * 5
            self.stash_y = stash_target_y + bob
            self.dash_x = dash_target_x + bob

        # Animate squirrel running in from left (starts after titles)
        if self.titles_entered and not self.squirrel_entered:
            self.squirrel_x += 300 * dt
            if self.squirrel_x > 350:
                self.squirrel_x = 350
                self.squirrel_entered = True
        elif self.squirrel_entered:
            # Gentle bobbing when stopped
            self.squirrel_x = 350 + math.sin(elapsed * 2) * 5

    def draw(self, surface: pygame.Surface) -> bool:
        """Draw the splash screen. Returns True when ready to proceed."""
        elapsed = time.time() - self.start_time

        # Draw splash scene background if available
        if self.splash_scene:
            surface.blit(self.splash_scene, (0, 0))
        else:
            # Fallback: Background gradient
            for y in range(self.screen_height):
                ratio = y / self.screen_height
                r = int(135 + (34 - 135) * ratio * 0.5)
                g = int(206 + (139 - 206) * ratio * 0.5)
                b = int(235 + (34 - 235) * ratio * 0.3)
                pygame.draw.line(surface, (r, g, b), (0, y), (self.screen_width, y))

            # Ground
            pygame.draw.rect(surface, (34, 139, 34), (0, 500, self.screen_width, 100))
            pygame.draw.rect(surface, (101, 67, 33), (0, 520, self.screen_width, 80))

            # Animated bouncing yarn balls (only if no splash scene)
            for yarn in self.yarn_balls:
                bounce = abs(math.sin(elapsed * 3 + yarn["phase"])) * 30
                y = yarn["y"] - bounce
                pygame.draw.circle(surface, yarn["color"], (int(yarn["x"]), int(y)), yarn["size"])
                # Highlight
                lighter = tuple(min(255, c + 80) for c in yarn["color"])
                pygame.draw.circle(surface, lighter, (int(yarn["x"] - 5), int(y - 5)), 6)

        # Draw STASH behind the foreground trees
        if self.stash_image:
            surface.blit(self.stash_image, (int(self.stash_x), int(self.stash_y)))

        # Fallback to text if images not loaded
        if not self.stash_image or not self.dash_image:
            title_y = 50
            title_text = "STASH DASH"
            # Shadow
            shadow = self.font_title.render(title_text, True, (0, 0, 0))
            surface.blit(shadow, (self.screen_width // 2 - shadow.get_width() // 2 + 4, title_y + 4))
            # Main title with color shift
            hue_shift = (math.sin(elapsed * 2) + 1) / 2
            r = int(255 * (0.8 + 0.2 * hue_shift))
            g = int(215 * (0.9 + 0.1 * math.sin(elapsed * 3)))
            title = self.font_title.render(title_text, True, (r, g, 0))
            surface.blit(title, (self.screen_width // 2 - title.get_width() // 2, title_y))

        # Draw splash foreground (trees framing the scene)
        if self.splash_foreground:
            surface.blit(self.splash_foreground, (0, 0))

        # Draw DASH in front of foreground trees
        if self.dash_image:
            surface.blit(self.dash_image, (int(self.dash_x), int(self.dash_y)))

        # Pulsing "Press SPACE" after titles enter
        if self.titles_entered:
            alpha = int(150 + 105 * math.sin(elapsed * 4))
            prompt = self.font_subtitle.render("Press SPACE to start", True, (255, 255, 255))
            prompt.set_alpha(alpha)
            surface.blit(prompt, (self.screen_width // 2 - prompt.get_width() // 2, 550))

        # Credits at bottom
        credits = self.font_small.render("Made with Pygame", True, (100, 100, 100))
        surface.blit(credits, (self.screen_width // 2 - credits.get_width() // 2, 580))

        return self.squirrel_entered


class UI:
    """Manages all UI elements."""

    def __init__(self, screen_width: int = 800, screen_height: int = 600):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Initialize fonts - larger sizes for better visibility
        pygame.font.init()
        self.font_large = pygame.font.Font(None, 72)   # Was 48
        self.font_medium = pygame.font.Font(None, 54)  # Was 36
        self.font_small = pygame.font.Font(None, 36)   # Was 24

        # Colors
        self.text_color = (255, 255, 255)
        self.shadow_color = (0, 0, 0)
        self.highlight_color = (255, 215, 0)

        # Milestone sign properties
        self.milestone_visible = False
        self.milestone_x = 0
        self.milestone_distance = 0

        # Load acorn sprite for lives display
        self.acorn_image = None
        self.acorn_faded = None
        acorn_path = os.path.join("assets", "sprites", "acorn.png")
        if os.path.exists(acorn_path):
            try:
                acorn = pygame.image.load(acorn_path).convert_alpha()
                # Scale to 40x40 for UI (was 24x24)
                self.acorn_image = pygame.transform.scale(acorn, (40, 40))
                # Create faded version (50% opacity)
                self.acorn_faded = self.acorn_image.copy()
                self.acorn_faded.set_alpha(80)
            except pygame.error:
                pass

    def draw_stash(self, surface: pygame.Surface, stash: int) -> None:
        """Draw the stash (score) display."""
        text = f"Stash = {stash}"

        # Shadow
        shadow = self.font_large.render(text, True, self.shadow_color)
        surface.blit(shadow, (22, 22))

        # Main text
        main = self.font_large.render(text, True, self.text_color)
        surface.blit(main, (20, 20))

    def draw_distance(self, surface: pygame.Surface, distance: int) -> None:
        """Draw the distance traveled."""
        text = f"{distance}m"

        # Render to get width for right-alignment
        main = self.font_medium.render(text, True, (200, 200, 200))
        text_width = main.get_width()

        # Shadow (right-aligned with padding)
        shadow = self.font_medium.render(text, True, self.shadow_color)
        surface.blit(shadow, (self.screen_width - text_width - 18, 22))

        # Main text (right-aligned with padding)
        surface.blit(main, (self.screen_width - text_width - 20, 20))

    def draw_lives(self, surface: pygame.Surface, lives: int, max_lives: int = 3) -> None:
        """Draw acorn icons representing lives."""
        # Position below the stash display (adjusted for larger fonts)
        start_x = 20
        start_y = 80  # Was 60
        spacing = 48  # Was 28

        for i in range(max_lives):
            x = start_x + i * spacing
            if self.acorn_image:
                if i < lives:
                    # Full acorn for remaining lives
                    surface.blit(self.acorn_image, (x, start_y))
                else:
                    # Faded acorn for lost lives
                    surface.blit(self.acorn_faded, (x, start_y))
            else:
                # Fallback to circles if no acorn sprite
                if i < lives:
                    pygame.draw.circle(surface, (139, 90, 43), (x + 20, start_y + 20), 16)
                else:
                    pygame.draw.circle(surface, (80, 50, 25), (x + 20, start_y + 20), 16)

    def draw_milestone_sign(self, surface: pygame.Surface, world_x: float,
                            camera_offset: float, best_distance: int, ground_y: int = 584) -> None:
        """Draw the milestone sign showing best distance."""
        screen_x = int(world_x - camera_offset)

        # Only draw if on screen
        if -100 < screen_x < self.screen_width + 100:
            # Anchor sign to ground level
            sign_bottom = ground_y
            post_height = 80
            sign_height = 50
            sign_top = sign_bottom - post_height - sign_height + 30

            # Sign post
            pygame.draw.rect(surface, (101, 67, 33), (screen_x + 20, sign_top + sign_height - 10, 10, post_height))

            # Sign board
            pygame.draw.rect(surface, (139, 90, 43), (screen_x - 20, sign_top, 90, sign_height))
            pygame.draw.rect(surface, (101, 67, 33), (screen_x - 20, sign_top, 90, sign_height), 3)

            # Text on sign
            text = f"{best_distance}m"
            rendered = self.font_small.render(text, True, (255, 255, 255))
            text_x = screen_x + 25 - rendered.get_width() // 2
            surface.blit(rendered, (text_x, sign_top + 15))

            # "BEST" label
            best_text = self.font_small.render("BEST", True, self.highlight_color)
            best_x = screen_x + 25 - best_text.get_width() // 2
            surface.blit(best_text, (best_x, sign_top + 2))

    def draw_new_record(self, surface: pygame.Surface) -> None:
        """Draw new record notification."""
        text = "NEW RECORD!"

        # Pulsing effect
        alpha = int(200 + 55 * math.sin(time.time() * 5))

        # Create surface with alpha
        text_surface = self.font_large.render(text, True, self.highlight_color)
        text_surface.set_alpha(alpha)

        x = self.screen_width // 2 - text_surface.get_width() // 2
        y = 70

        # Shadow
        shadow = self.font_large.render(text, True, self.shadow_color)
        surface.blit(shadow, (x + 2, y + 2))

        surface.blit(text_surface, (x, y))

    def draw_game_over(self, surface: pygame.Surface, final_stash: int,
                       distance: int, high_score: int, is_new_high: bool) -> None:
        """Draw the game over screen."""
        # Darken background
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(150)
        surface.blit(overlay, (0, 0))

        center_x = self.screen_width // 2
        y = 150

        # Game Over title
        title = self.font_large.render("GAME OVER", True, (255, 80, 80))
        surface.blit(title, (center_x - title.get_width() // 2, y))
        y += 70

        # Final stash
        stash_text = f"Final Stash: {final_stash}"
        stash = self.font_medium.render(stash_text, True, self.text_color)
        surface.blit(stash, (center_x - stash.get_width() // 2, y))
        y += 45

        # Distance
        dist_text = f"Distance: {distance}m"
        dist = self.font_medium.render(dist_text, True, self.text_color)
        surface.blit(dist, (center_x - dist.get_width() // 2, y))
        y += 45

        # High score
        if is_new_high:
            hs_text = f"NEW HIGH SCORE: {high_score}"
            color = self.highlight_color
        else:
            hs_text = f"High Score: {high_score}"
            color = (180, 180, 180)

        hs = self.font_medium.render(hs_text, True, color)
        surface.blit(hs, (center_x - hs.get_width() // 2, y))
        y += 80

        # Restart prompt
        prompt = self.font_medium.render("Press SPACE to play again", True, self.text_color)
        surface.blit(prompt, (center_x - prompt.get_width() // 2, y))

        prompt2 = self.font_small.render("Press ESC to quit", True, (150, 150, 150))
        surface.blit(prompt2, (center_x - prompt2.get_width() // 2, y + 40))

    def draw_title_screen(self, surface: pygame.Surface) -> None:
        """Draw the title/start screen."""
        center_x = self.screen_width // 2

        # Title
        title = self.font_large.render("STASH DASH", True, self.highlight_color)
        surface.blit(title, (center_x - title.get_width() // 2, 180))

        # Subtitle
        subtitle = self.font_medium.render("Collect yarn for your stash!", True, self.text_color)
        surface.blit(subtitle, (center_x - subtitle.get_width() // 2, 250))

        # Controls
        y = 350
        controls = [
            "Arrow Keys / WASD - Move",
            "SPACE / UP - Jump",
            "Avoid bushes, don't fall in gaps!",
        ]
        for line in controls:
            text = self.font_small.render(line, True, (200, 200, 200))
            surface.blit(text, (center_x - text.get_width() // 2, y))
            y += 30

        # Start prompt
        alpha = int(150 + 105 * math.sin(time.time() * 3))
        prompt = self.font_medium.render("Press SPACE to start", True, self.text_color)
        prompt.set_alpha(alpha)
        surface.blit(prompt, (center_x - prompt.get_width() // 2, 480))
