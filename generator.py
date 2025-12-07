"""
Procedural level generation for Squirrel Yarn game.
Ensures there's always a safe path while creating interesting terrain.
"""

import random
from typing import List, Tuple, Optional
from obstacles import Platform, Ground, Bush, Gap
from yarn import spawn_yarn, YarnSkein, get_min_stash_for_color


class LevelGenerator:
    """Generates terrain, obstacles, and collectibles procedurally."""

    # Screen dimensions
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600

    # Ground level (Y position where ground sits) - only one row of tiles visible
    GROUND_Y = 584
    GROUND_TILE_SIZE = 64

    # Platform settings (Y values - remember lower Y = higher on screen)
    # Ground is at 584, player jumps ~126px, so can reach about Y=458
    # Platforms need their TOP to be reachable
    PLATFORM_LOW_Y = 514    # Just above ground (easy jump)
    PLATFORM_MID_Y = 474    # Medium height
    PLATFORM_HIGH_Y = 434   # High platform (near max jump)
    PLATFORM_WIDTH = 128
    PLATFORM_MIN_SPACING = 250  # Minimum X distance between platforms

    # Generation settings
    CHUNK_WIDTH = 400  # Generate terrain in chunks

    def __init__(self):
        self.last_generated_x = 0
        self.difficulty = 1.0

        # Tracking what we've generated
        self.ground_tiles: List[Ground] = []
        self.platforms: List[Platform] = []
        self.bushes: List[Bush] = []
        self.gaps: List[Gap] = []
        self.yarns: List[YarnSkein] = []

        # State for generation continuity
        self.last_platform_x = -1000  # Start far back so first platform can spawn
        self.last_platform_y = self.GROUND_Y

        # Track unlocked yarn tiers
        self.yarn_reset_to_basic = False

    def generate_initial(self) -> None:
        """Generate initial terrain at game start."""
        # Fill screen with ground and some ahead (no edges at start - solid ground)
        for x in range(-self.GROUND_TILE_SIZE, self.SCREEN_WIDTH + self.CHUNK_WIDTH, self.GROUND_TILE_SIZE):
            self.ground_tiles.append(Ground(x, self.GROUND_Y, is_left_edge=False, is_right_edge=False))

        self.last_generated_x = self.SCREEN_WIDTH + self.CHUNK_WIDTH

        # Add some initial yarn on the ground path
        for i in range(3):
            x = 300 + i * 150
            y = self.GROUND_Y - 60  # Just above ground, easy to grab
            yarn = spawn_yarn(x, y, 0)
            if yarn:
                self.yarns.append(yarn)

    def update(self, camera_x: float, distance: float, stash: int = 0) -> None:
        """Generate new terrain as camera moves and clean up old terrain."""
        # Update difficulty based on distance
        self.difficulty = 1.0 + (distance / 1000) * 0.3  # Gentler increase

        # Store current stash for yarn spawning
        self.current_stash = stash

        # Generate new terrain ahead
        generate_ahead = camera_x + self.SCREEN_WIDTH + self.CHUNK_WIDTH
        while self.last_generated_x < generate_ahead:
            self._generate_chunk(self.last_generated_x, distance)
            self.last_generated_x += self.CHUNK_WIDTH

        # Clean up off-screen elements
        self._cleanup(camera_x)

    def _generate_chunk(self, start_x: float, distance: float) -> None:
        """Generate a chunk of terrain."""
        # First, decide which tile positions will be gaps
        tile_positions = []
        x = start_x
        while x < start_x + self.CHUNK_WIDTH:
            tile_positions.append(x)
            x += self.GROUND_TILE_SIZE

        # Track which positions are gaps
        gap_positions = set()

        # Decide where gaps go
        gap_chance = 0.05 * self.difficulty if distance > 100 else 0
        i = 0
        while i < len(tile_positions):
            if random.random() < gap_chance and i + 1 < len(tile_positions):
                # Create a gap of 2-3 tiles
                num_tiles = random.randint(2, 3)
                gap_start_x = tile_positions[i]

                # Mark these positions as gap
                tiles_added = 0
                for j in range(num_tiles):
                    if i + j < len(tile_positions):
                        gap_positions.add(tile_positions[i + j])
                        tiles_added += 1

                # Calculate the exact gap width
                gap_width = tiles_added * self.GROUND_TILE_SIZE

                # Create the gap object
                self.gaps.append(Gap(gap_start_x, gap_width, self.GROUND_Y))

                # Add rescue platform over gap
                platform_y = self.PLATFORM_LOW_Y
                platform_width = gap_width + 40  # Slightly wider than gap
                self.platforms.append(Platform(gap_start_x - 10, platform_y, platform_width))
                self.last_platform_x = gap_start_x
                self.last_platform_y = platform_y

                # Yarn on the rescue platform
                stash = getattr(self, 'current_stash', 0)
                yarn = spawn_yarn(gap_start_x + gap_width // 2, platform_y - 45, stash)
                if yarn:
                    self.yarns.append(yarn)

                # Skip past the gap tiles
                i += tiles_added
                continue

            i += 1

        # Now place ground tiles ONLY where there is no gap
        for idx, tile_x in enumerate(tile_positions):
            if tile_x in gap_positions:
                continue  # Skip - this is a gap

            # Check if this tile is at the edge of a gap
            prev_x = tile_positions[idx - 1] if idx > 0 else None
            next_x = tile_positions[idx + 1] if idx < len(tile_positions) - 1 else None

            is_left_edge = prev_x is not None and prev_x in gap_positions
            is_right_edge = next_x is not None and next_x in gap_positions

            # Place ground tile with edge info
            self.ground_tiles.append(Ground(tile_x, self.GROUND_Y, is_left_edge, is_right_edge))

            # Chance for bush on ground (appears after 50m)
            bush_chance = 0.06 * self.difficulty if distance > 50 else 0
            if random.random() < bush_chance:
                bush_x = tile_x + random.randint(10, 30)
                bush_height = 48  # Default bush height
                # Offset to anchor bush to ground (sprite has transparent padding)
                bush_y_offset = 12  # Move down to compensate for sprite padding
                self.bushes.append(Bush(bush_x, self.GROUND_Y - bush_height + bush_y_offset))

            # Chance for platform (spaced apart properly)
            platform_chance = 0.08 if distance > 80 else 0
            if random.random() < platform_chance and (tile_x - self.last_platform_x) > self.PLATFORM_MIN_SPACING:
                # Pick a height that's reachable from ground or last platform
                heights = [self.PLATFORM_LOW_Y, self.PLATFORM_MID_Y]
                if distance > 200:
                    heights.append(self.PLATFORM_HIGH_Y)

                platform_y = random.choice(heights)
                platform_width = random.choice([96, 128, 160])
                self.platforms.append(Platform(tile_x, platform_y, platform_width))
                self.last_platform_x = tile_x
                self.last_platform_y = platform_y

                # Yarn on platform
                if random.random() < 0.7:
                    stash = getattr(self, 'current_stash', 0)
                    yarn = spawn_yarn(tile_x + platform_width // 2 - 16, platform_y - 45, stash)
                    if yarn:
                        self.yarns.append(yarn)

            # Chance for yarn floating in air (reachable by jump)
            # More frequent at beginning, slightly less as game progresses
            else:
                stash = getattr(self, 'current_stash', 0)
                # Higher spawn rate at start (20%), decreasing to 12% as stash grows
                yarn_chance = 0.20 - min(0.08, stash * 0.004)
                if random.random() < yarn_chance:
                    yarn_x = tile_x + random.randint(10, 50)
                    # Heights that are reachable: ground jump reaches about y=380
                    yarn_y = self.GROUND_Y - random.choice([60, 90, 120])
                    yarn = spawn_yarn(yarn_x, yarn_y, stash)
                    if yarn:
                        self.yarns.append(yarn)

    def _cleanup(self, camera_x: float) -> None:
        """Remove elements that are off-screen to the left."""
        buffer = 200

        self.ground_tiles = [g for g in self.ground_tiles if not g.is_off_screen(camera_x, buffer)]
        self.platforms = [p for p in self.platforms if not p.is_off_screen(camera_x, buffer)]
        self.bushes = [b for b in self.bushes if not b.is_off_screen(camera_x, buffer)]
        self.gaps = [g for g in self.gaps if not g.is_off_screen(camera_x, buffer)]

        # Remove yarns that are off-screen, expired, or above current stash tier
        stash = getattr(self, 'current_stash', 0)
        self.yarns = [
            y for y in self.yarns
            if not y.is_off_screen(camera_x, buffer)
            and not y.is_expired()
            and get_min_stash_for_color(y.color_name) <= stash
        ]

    def reset_yarn_tiers(self) -> None:
        """Reset available yarn colors to basic tier (after being hit)."""
        self.yarn_reset_to_basic = True

    def restore_yarn_progression(self) -> None:
        """Restore normal yarn tier progression."""
        self.yarn_reset_to_basic = False

    def get_ground_at(self, x: float) -> Optional[float]:
        """Get the ground Y position at a given X, or None if in a gap."""
        for gap in self.gaps:
            if gap.contains_x(x):
                return None
        return self.GROUND_Y

    def get_all_sprites(self) -> Tuple[List, List, List, List]:
        """Get all sprite lists for rendering and collision."""
        return self.ground_tiles, self.platforms, self.bushes, self.yarns
