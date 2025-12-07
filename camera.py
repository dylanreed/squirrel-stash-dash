"""
Camera module - Handles dynamic camera following with smooth interpolation.
"""


class Camera:
    """Camera that follows the player with smooth lerp-based movement."""

    def __init__(self, screen_width, screen_height):
        """
        Initialize the camera.

        Args:
            screen_width: Width of the game screen
            screen_height: Height of the game screen
        """
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Camera position (top-left corner of view)
        self.x = 0
        self.y = 0

        # Target position
        self.target_x = 0

        # Lerp/smoothing settings
        self.lerp_speed = 5.0  # Higher = faster/snappier camera

        # Dynamic offset - how far ahead of player the camera looks
        # This changes based on player speed
        self.base_offset = screen_width * 0.3  # Player at 30% of screen when slow
        self.max_offset = screen_width * 0.5   # Player at 50% of screen when fast

    def update(self, dt, player_x, player_speed_percentage):
        """
        Update camera position to follow the player.

        Args:
            dt: Delta time in seconds
            player_x: Player's x position in world space
            player_speed_percentage: Player's speed as percentage (0-100)
        """
        # Calculate dynamic offset based on player speed
        # When player is faster, they move more to the left side of screen
        speed_factor = player_speed_percentage / 100.0
        current_offset = self.base_offset + (self.max_offset - self.base_offset) * speed_factor

        # Calculate target camera position
        # Camera x = player x - how far from left edge we want player to be
        self.target_x = player_x - current_offset

        # Smooth lerp to target position
        # x = x + (target - x) * lerp_speed * dt
        self.x += (self.target_x - self.x) * self.lerp_speed * dt

        # Prevent camera from going negative (at start of game)
        self.x = max(0, self.x)

        # Y camera is typically fixed for a 2D runner, but can be modified
        self.y = 0

    def get_offset_x(self):
        """
        Get the camera's x offset for rendering.

        Returns:
            Camera x position (what to subtract from world positions)
        """
        return self.x

    def get_offset_y(self):
        """
        Get the camera's y offset for rendering.

        Returns:
            Camera y position
        """
        return self.y

    def world_to_screen(self, world_x, world_y):
        """
        Convert world coordinates to screen coordinates.

        Args:
            world_x: X position in world space
            world_y: Y position in world space

        Returns:
            Tuple of (screen_x, screen_y)
        """
        screen_x = world_x - self.x
        screen_y = world_y - self.y
        return (screen_x, screen_y)

    def screen_to_world(self, screen_x, screen_y):
        """
        Convert screen coordinates to world coordinates.

        Args:
            screen_x: X position on screen
            screen_y: Y position on screen

        Returns:
            Tuple of (world_x, world_y)
        """
        world_x = screen_x + self.x
        world_y = screen_y + self.y
        return (world_x, world_y)

    def is_visible(self, world_x, object_width):
        """
        Check if an object is visible on screen.

        Args:
            world_x: Object's x position in world space
            object_width: Width of the object

        Returns:
            True if object is visible, False otherwise
        """
        screen_x = world_x - self.x
        return -object_width <= screen_x <= self.screen_width
