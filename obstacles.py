"""
Obstacle classes for Squirrel Yarn game.
Handles bushes (hazards) and platforms (jumpable surfaces).
"""

import pygame
import os


class Platform(pygame.sprite.Sprite):
    """A platform the squirrel can stand/run on."""

    def __init__(self, x: float, y: float, width: int = 128, height: int = 48):
        super().__init__()

        # Try to load sprite, fall back to colored rectangle
        sprite_path = os.path.join("assets", "sprites", "platform.png")
        if os.path.exists(sprite_path):
            self.image = pygame.image.load(sprite_path).convert_alpha()
            # Scale to requested width while maintaining aspect ratio
            orig_w, orig_h = self.image.get_size()
            scale = width / orig_w
            self.width = width
            self.height = int(orig_h * scale)
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        else:
            self.width = width
            self.height = height
            self.image = pygame.Surface((width, height))
            self.image.fill((101, 67, 33))  # Brown
            # Add some detail
            pygame.draw.rect(self.image, (139, 90, 43), (0, 0, width, 8))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # World position (float for precision)
        self.world_x = float(x)
        self.world_y = float(y)

    def update(self, camera_offset: float):
        """Update screen position based on camera."""
        self.rect.x = int(self.world_x - camera_offset)

    def is_off_screen(self, camera_offset: float, buffer: int = 200) -> bool:
        """Check if platform is far enough left to be removed."""
        return self.world_x < camera_offset - buffer


class GroundTileset:
    """Manages the ground tileset - loads once and shares tiles."""

    _instance = None
    TILE_SIZE = 16  # Each tile in the tileset is 16x16

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_tileset()
        return cls._instance

    def _load_tileset(self):
        """Load and parse the ground tileset."""
        tileset_path = os.path.join("assets", "sprites", "ground_tileset.png")
        if os.path.exists(tileset_path):
            tileset = pygame.image.load(tileset_path).convert_alpha()

            # Extract key tiles from the 8x8 grid (16x16 each)
            # Multiple grass top variants for visual variety
            self.grass_tops = [
                self._get_tile(tileset, 1, 4),  # Grass with some dirt showing
                self._get_tile(tileset, 1, 5),  # Fuller grass
                self._get_tile(tileset, 1, 6),  # Another grass variant
            ]
            self.grass_top_left = self._get_tile(tileset, 1, 3)   # Grass left edge
            self.grass_top_right = self._get_tile(tileset, 2, 3)  # Grass right edge (corner piece)

            # Dirt fill variants
            self.dirt_fills = [
                self._get_tile(tileset, 2, 4),  # Dirt center
                self._get_tile(tileset, 2, 5),  # Dirt variant
                self._get_tile(tileset, 0, 3),  # Another dirt
                self._get_tile(tileset, 0, 4),  # Another dirt variant
            ]
            self.dirt_left = self._get_tile(tileset, 1, 3)   # Dirt left edge
            self.dirt_right = self._get_tile(tileset, 2, 3)  # Dirt right edge
            self.loaded = True
        else:
            self.loaded = False

    def _get_tile(self, tileset, row, col):
        """Extract a single tile from the tileset."""
        x = col * self.TILE_SIZE
        y = row * self.TILE_SIZE
        tile = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE), pygame.SRCALPHA)
        tile.blit(tileset, (0, 0), (x, y, self.TILE_SIZE, self.TILE_SIZE))
        return tile


class Ground(pygame.sprite.Sprite):
    """Ground column - grass on top, dirt filling to screen bottom."""

    TILE_SIZE = 16  # Tileset tile size
    COLUMN_WIDTH = 64  # Width of each ground column (4 tiles wide)
    SCREEN_BOTTOM = 600  # Screen height

    # Class-level tileset (shared across all instances)
    _tileset = None

    def __init__(self, x: float, y: float, is_left_edge: bool = False, is_right_edge: bool = False):
        super().__init__()
        import random

        # Load tileset singleton
        if Ground._tileset is None:
            Ground._tileset = GroundTileset()

        # Calculate height needed (from ground_y to screen bottom)
        self.height = self.SCREEN_BOTTOM - y

        # Create surface for this ground column
        self.image = pygame.Surface((self.COLUMN_WIDTH, self.height), pygame.SRCALPHA)

        if Ground._tileset.loaded:
            self._build_from_tileset(is_left_edge, is_right_edge, random)
        else:
            self._build_fallback()

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.world_x = float(x)
        self.world_y = float(y)

    def _build_from_tileset(self, is_left_edge: bool, is_right_edge: bool, random):
        """Build the ground column from tileset tiles with random variations."""
        ts = Ground._tileset
        tile_size = self.TILE_SIZE
        tiles_across = self.COLUMN_WIDTH // tile_size  # 4 tiles wide
        tiles_down = (self.height + tile_size - 1) // tile_size

        for row in range(tiles_down):
            for col in range(tiles_across):
                px = col * tile_size
                py = row * tile_size

                if row == 0:
                    # Top row - grass surface with random variants
                    if col == 0 and is_left_edge:
                        tile = ts.grass_top_left
                    elif col == tiles_across - 1 and is_right_edge:
                        tile = ts.grass_top_right
                    else:
                        # Random grass variant for visual variety
                        tile = random.choice(ts.grass_tops)
                else:
                    # Below surface - dirt fill with random variants
                    if col == 0 and is_left_edge:
                        tile = ts.dirt_left
                    elif col == tiles_across - 1 and is_right_edge:
                        tile = ts.dirt_right
                    else:
                        # Random dirt variant
                        tile = random.choice(ts.dirt_fills)

                self.image.blit(tile, (px, py))

    def _build_fallback(self):
        """Create fallback gradient if tileset not available."""
        for i in range(self.height):
            color_val = 100 + int((i / self.height) * 50)
            green = min(180, 120 + int((1 - i / self.height) * 60))
            pygame.draw.line(self.image, (color_val, green, 50), (0, i), (self.COLUMN_WIDTH, i))

    def update(self, camera_offset: float):
        """Update screen position based on camera."""
        self.rect.x = int(self.world_x - camera_offset)

    def is_off_screen(self, camera_offset: float, buffer: int = 200) -> bool:
        """Check if ground tile is far enough left to be removed."""
        return self.world_x < camera_offset - buffer


class Bush(pygame.sprite.Sprite):
    """Bush obstacle - hitting it causes yarn loss and slowdown."""

    def __init__(self, x: float, y: float, width: int = 64, height: int = 48):
        super().__init__()
        self.width = width
        self.height = height

        # Try to load sprite, fall back to colored shape
        sprite_path = os.path.join("assets", "sprites", "bush.png")
        if os.path.exists(sprite_path):
            self.image = pygame.image.load(sprite_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (width, height))
        else:
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            # Draw bush-like oval shape
            pygame.draw.ellipse(self.image, (34, 139, 34), (0, height // 4, width, height * 3 // 4))
            pygame.draw.ellipse(self.image, (0, 100, 0), (width // 4, 0, width // 2, height // 2))
            pygame.draw.ellipse(self.image, (50, 160, 50), (5, height // 3, width - 10, height // 2))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.world_x = float(x)
        self.world_y = float(y)

        # Slightly smaller hitbox for fairer collision
        self.hitbox = pygame.Rect(
            x + width // 6,
            y + height // 4,
            width * 2 // 3,
            height * 2 // 3
        )

    def update(self, camera_offset: float):
        """Update screen position based on camera."""
        self.rect.x = int(self.world_x - camera_offset)
        self.hitbox.x = int(self.world_x - camera_offset + self.width // 6)

    def is_off_screen(self, camera_offset: float, buffer: int = 200) -> bool:
        """Check if bush is far enough left to be removed."""
        return self.world_x < camera_offset - buffer


class Gap:
    """Represents a gap in the ground - falling in means game over."""

    def __init__(self, start_x: float, width: float, ground_y: float):
        self.start_x = start_x
        self.width = width
        self.end_x = start_x + width
        self.ground_y = ground_y

    def contains_x(self, x: float) -> bool:
        """Check if an x position is within this gap."""
        return self.start_x <= x <= self.end_x

    def get_fall_rect(self, camera_offset: float) -> pygame.Rect:
        """Get the rectangle area of the gap for collision detection."""
        return pygame.Rect(
            int(self.start_x - camera_offset),
            int(self.ground_y),
            int(self.width),
            200  # Extends below screen
        )

    def is_off_screen(self, camera_offset: float, buffer: int = 200) -> bool:
        """Check if gap is far enough left to be removed."""
        return self.end_x < camera_offset - buffer
