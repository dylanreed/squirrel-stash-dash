"""
Yarn skein collectibles for Squirrel Yarn game.
Different colors have different point values and appear at different distances.
"""

import pygame
import os
import random
import math
from typing import Tuple, Optional


# Yarn color tiers with their properties
# Tiers unlock based on stash count, not distance
YARN_TIERS = {
    "basic": {
        "colors": ["red", "green", "blue"],
        "points": 1,
        "min_stash": 0,  # Available from start
    },
    "mid": {
        "colors": ["cyan", "magenta", "yellow", "black"],
        "points": 2,
        "min_stash": 10,  # Need 10 in stash to unlock
    },
    "late": {
        "colors": ["orange", "purple", "lime", "teal", "pink", "brown"],
        "points": 3,
        "min_stash": 25,  # Need 25 in stash to unlock
    },
    "rare": {
        "colors": ["rainbow"],
        "points": 5,
        "min_stash": 0,  # Can appear anytime, but rarely
        "spawn_chance": 0.05,  # 5% chance when spawning yarn
    },
}

# Color RGB values for fallback rendering
COLOR_RGB = {
    "red": (220, 20, 60),
    "green": (34, 139, 34),
    "blue": (30, 144, 255),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
    "yellow": (255, 215, 0),
    "black": (40, 40, 40),
    "orange": (255, 140, 0),
    "purple": (148, 0, 211),
    "lime": (50, 205, 50),
    "teal": (0, 128, 128),
    "pink": (255, 105, 180),
    "brown": (139, 69, 19),
    "rainbow": None,  # Special case - animated
}


class YarnSkein(pygame.sprite.Sprite):
    """A collectible yarn skein."""

    SIZE = 56  # Doubled for better visibility

    def __init__(self, x: float, y: float, color: str, points: int):
        super().__init__()
        self.color_name = color
        self.points = points

        # Try to load sprite
        sprite_path = os.path.join("assets", "sprites", f"yarn_{color}.png")
        if os.path.exists(sprite_path):
            self.image = pygame.image.load(sprite_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.SIZE, self.SIZE))
            self.base_image = self.image.copy()
        else:
            self.image = self._create_fallback_image(color)
            self.base_image = self.image.copy()

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.world_x = float(x)
        self.world_y = float(y)

        # Animation properties
        self.bob_offset = random.random() * math.pi * 2  # Random starting phase
        self.bob_speed = 3.0
        self.bob_amplitude = 4.0
        self.wiggle_offset = random.random() * math.pi * 2  # Random wiggle phase
        self.wiggle_speed = 5.0  # Faster than bob for wiggly effect
        self.wiggle_amplitude = 2.0  # Subtle horizontal movement
        self.time = 0

        # Rainbow animation frame
        self.rainbow_hue = 0
        self.is_rainbow = (color == "rainbow")

        # For scattered yarn (after being hit)
        self.velocity_x = 0
        self.velocity_y = 0
        self.is_scattered = False
        self.scatter_timer = 0
        self.scatter_duration = 180  # 3 seconds at 60fps

    def _create_fallback_image(self, color: str) -> pygame.Surface:
        """Create a simple yarn ball shape as fallback."""
        surface = pygame.Surface((self.SIZE, self.SIZE), pygame.SRCALPHA)

        if color == "rainbow":
            # Draw rainbow gradient
            for i in range(6):
                hue = i / 6
                rgb = self._hsv_to_rgb(hue, 0.8, 1.0)
                pygame.draw.arc(
                    surface, rgb,
                    (4, 4, self.SIZE - 8, self.SIZE - 8),
                    math.pi * i / 3, math.pi * (i + 1) / 3 + 0.2,
                    4
                )
            # Center
            pygame.draw.circle(surface, (255, 255, 255), (self.SIZE // 2, self.SIZE // 2), 6)
        else:
            rgb = COLOR_RGB.get(color, (200, 200, 200))
            # Draw yarn ball
            pygame.draw.circle(surface, rgb, (self.SIZE // 2, self.SIZE // 2), self.SIZE // 2 - 2)
            # Highlight
            lighter = tuple(min(255, c + 60) for c in rgb)
            pygame.draw.circle(surface, lighter, (self.SIZE // 3, self.SIZE // 3), 4)
            # Yarn lines
            darker = tuple(max(0, c - 40) for c in rgb)
            for i in range(3):
                start_angle = i * 0.7
                pygame.draw.arc(
                    surface, darker,
                    (4, 4, self.SIZE - 8, self.SIZE - 8),
                    start_angle, start_angle + 0.5,
                    2
                )

        return surface

    def _hsv_to_rgb(self, h: float, s: float, v: float) -> Tuple[int, int, int]:
        """Convert HSV to RGB color."""
        if s == 0:
            return (int(v * 255), int(v * 255), int(v * 255))

        i = int(h * 6)
        f = (h * 6) - i
        p = v * (1 - s)
        q = v * (1 - s * f)
        t = v * (1 - s * (1 - f))

        i = i % 6
        if i == 0:
            r, g, b = v, t, p
        elif i == 1:
            r, g, b = q, v, p
        elif i == 2:
            r, g, b = p, v, t
        elif i == 3:
            r, g, b = p, q, v
        elif i == 4:
            r, g, b = t, p, v
        else:
            r, g, b = v, p, q

        return (int(r * 255), int(g * 255), int(b * 255))

    def update(self, camera_offset: float, dt: float = 1/60):
        """Update yarn position and animation."""
        self.time += dt

        if self.is_scattered:
            # Physics for scattered yarn
            self.world_x += self.velocity_x
            self.world_y += self.velocity_y
            self.velocity_y += 0.3  # Gravity
            self.velocity_x *= 0.99  # Air resistance

            self.scatter_timer += 1

            # Blink when about to disappear
            if self.scatter_timer > self.scatter_duration - 60:
                if (self.scatter_timer // 5) % 2 == 0:
                    self.image.set_alpha(100)
                else:
                    self.image.set_alpha(255)
        else:
            # Bobbing animation (vertical)
            bob = math.sin(self.time * self.bob_speed + self.bob_offset) * self.bob_amplitude
            self.rect.y = int(self.world_y + bob)

            # Wiggle animation (horizontal)
            wiggle = math.sin(self.time * self.wiggle_speed + self.wiggle_offset) * self.wiggle_amplitude
            self.rect.x = int(self.world_x - self.rect.width // 2 + wiggle)

        # Rainbow yarn - just use the base image, no shimmer effect
        # (shimmer removed for cleaner look)

        # Update screen position
        self.rect.x = int(self.world_x - camera_offset)

    def scatter(self, direction: int = 1):
        """Make yarn scatter outward (Sonic-style when hit)."""
        self.is_scattered = True
        angle = random.uniform(-math.pi / 2, math.pi / 2)
        speed = random.uniform(4, 10)
        self.velocity_x = math.cos(angle) * speed * direction
        self.velocity_y = -abs(math.sin(angle) * speed) - 3

    def is_expired(self) -> bool:
        """Check if scattered yarn should be removed."""
        return self.is_scattered and self.scatter_timer >= self.scatter_duration

    def is_off_screen(self, camera_offset: float, buffer: int = 200) -> bool:
        """Check if yarn is far enough left to be removed."""
        return self.world_x < camera_offset - buffer


def get_available_colors(stash: int) -> list:
    """Get list of yarn colors available at current stash count."""
    available = []
    for tier_name, tier in YARN_TIERS.items():
        if tier_name == "rare":
            continue  # Rare handled separately
        if stash >= tier["min_stash"]:
            available.extend(tier["colors"])

    return available if available else YARN_TIERS["basic"]["colors"].copy()


def get_min_stash_for_color(color: str) -> int:
    """Get the minimum stash required for a yarn color."""
    for tier in YARN_TIERS.values():
        if color in tier["colors"]:
            return tier.get("min_stash", 0)
    return 0


def spawn_yarn(x: float, y: float, stash: int) -> Optional[YarnSkein]:
    """Spawn a yarn skein with color based on stash count."""
    # Check for rare spawn
    if random.random() < YARN_TIERS["rare"]["spawn_chance"]:
        return YarnSkein(x, y, "rainbow", YARN_TIERS["rare"]["points"])

    # Get available colors at current stash
    available = get_available_colors(stash)

    color = random.choice(available)

    # Find points for this color
    points = 1
    for tier in YARN_TIERS.values():
        if color in tier["colors"]:
            points = tier["points"]
            break

    return YarnSkein(x, y, color, points)
