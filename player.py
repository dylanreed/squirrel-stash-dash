"""
Player module - Squirrel character with movement, jumping, and yarn collection.
"""

import pygame
import math
import os


class Squirrel:
    """Player character - a squirrel that runs, jumps, and collects yarn."""

    # State constants
    STATE_RUNNING = "running"
    STATE_JUMPING = "jumping"
    STATE_HIT = "hit"

    def __init__(self, x, y):
        """
        Initialize the squirrel.

        Args:
            x: Starting x position
            y: Starting y position
        """
        self.x = x
        self.y = y

        # Size - make squirrel nice and visible (15% bigger than 96)
        self.width = 110
        self.height = 110

        # Sprite offset - the actual squirrel in the sprite doesn't fill the full height
        # This offset adjusts rendering so the squirrel's feet touch the ground
        self.sprite_offset_y = 10  # Positive moves sprite down to align feet with ground

        # Load animations
        self.animations = {}
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.1  # Seconds per frame
        self._load_animations()

        # Movement
        self.velocity_x = 200  # Base horizontal speed (pixels/second)
        self.velocity_y = 0
        self.base_speed = 200
        self.speed_multiplier = 1.0  # Increases over time
        self.speed_increase_rate = 0.05  # Speed increase per second

        # Jumping - max height = v² / (2g) = 550² / 2400 = ~126 pixels
        self.jump_strength = -550
        self.gravity = 1200
        self.gap_gravity = 4000  # Much stronger gravity when falling in gap
        self.is_grounded = True
        self.ground_y = y  # The ground level
        self.falling_in_gap = False  # True when falling into a gap

        # State
        self.state = self.STATE_RUNNING

        # Yarn collection
        self.yarn_count = 0

        # Hit/stun mechanics
        self.hit_timer = 0
        self.hit_duration = 1.0  # Seconds of slowdown after being hit
        self.hit_speed_reduction = 0.5  # Speed reduced to 50% when hit

        # Lives system
        self.max_lives = 3
        self.lives = 3
        self.life_lost_this_hit = False  # Track if we already lost a life this hit

        # Visual representation (fallback)
        self.color = (139, 69, 19)  # Brown for squirrel
        self.hit_color = (255, 100, 100)  # Red tint when hit

    def _load_animations(self):
        """Load animation frames from sprite files."""
        base_path = os.path.join(os.path.dirname(__file__), "assets", "sprites", "animations")

        # Load running animation (east-facing for side-scroller)
        # Prefer 6-frame animation for smoother motion, fallback to 4-frame
        running_path = os.path.join(base_path, "running-6-frames", "east")
        self.animations["running"] = self._load_frames(running_path)
        if not self.animations["running"]:
            running_path = os.path.join(base_path, "running-4-frames", "east")
            self.animations["running"] = self._load_frames(running_path)

        # Load jumping animation (use running-jump for better look)
        jumping_path = os.path.join(base_path, "running-jump", "east")
        self.animations["jumping"] = self._load_frames(jumping_path)
        # Fallback to jumping-1 if running-jump not available
        if not self.animations["jumping"]:
            jumping_path = os.path.join(base_path, "jumping-1", "east")
            self.animations["jumping"] = self._load_frames(jumping_path)

        # Load hit animation (falling back death)
        hit_path = os.path.join(base_path, "falling-back-death", "east")
        self.animations["hit"] = self._load_frames(hit_path)

        # Load static sprite as fallback
        static_path = os.path.join(os.path.dirname(__file__), "assets", "sprites", "squirrel.png")
        if os.path.exists(static_path):
            try:
                static_sprite = pygame.image.load(static_path).convert_alpha()
                self.static_sprite = pygame.transform.scale(static_sprite, (self.width, self.height))
            except pygame.error:
                self.static_sprite = None
        else:
            self.static_sprite = None

        # Set hit sprite (tinted version of static)
        if self.static_sprite:
            self.hit_sprite = self.static_sprite.copy()
            self.hit_sprite.fill((255, 100, 100, 128), special_flags=pygame.BLEND_RGBA_MULT)
        else:
            self.hit_sprite = None

    def _load_frames(self, folder_path):
        """Load all frames from a folder."""
        frames = []
        if os.path.exists(folder_path):
            frame_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.png')])
            for frame_file in frame_files:
                try:
                    frame_path = os.path.join(folder_path, frame_file)
                    frame = pygame.image.load(frame_path).convert_alpha()
                    frame = pygame.transform.scale(frame, (self.width, self.height))
                    frames.append(frame)
                except pygame.error:
                    pass
        return frames

    def jump(self):
        """Make the squirrel jump if grounded."""
        if self.is_grounded and self.state != self.STATE_HIT:
            self.velocity_y = self.jump_strength
            self.is_grounded = False
            self.state = self.STATE_JUMPING

    def update(self, dt):
        """
        Update squirrel position and state.

        Args:
            dt: Delta time in seconds
        """
        # Increase speed over time (only when not hit)
        if self.state != self.STATE_HIT:
            self.speed_multiplier += self.speed_increase_rate * dt
            self.speed_multiplier = min(self.speed_multiplier, 3.0)  # Cap at 3x speed

        # Update hit timer
        if self.hit_timer > 0:
            self.hit_timer -= dt
            if self.hit_timer <= 0:
                self.state = self.STATE_RUNNING if self.is_grounded else self.STATE_JUMPING

        # Calculate current speed
        current_speed_mult = self.hit_speed_reduction if self.state == self.STATE_HIT else 1.0
        self.velocity_x = self.base_speed * self.speed_multiplier * current_speed_mult

        # Horizontal movement
        self.x += self.velocity_x * dt

        # Vertical movement (gravity and jumping)
        # Use stronger gravity when falling in a gap
        current_gravity = self.gap_gravity if self.falling_in_gap else self.gravity
        self.velocity_y += current_gravity * dt
        self.y += self.velocity_y * dt

        # Ground collision
        if self.y >= self.ground_y:
            self.y = self.ground_y
            self.velocity_y = 0
            self.is_grounded = True
            if self.state == self.STATE_JUMPING:
                self.state = self.STATE_RUNNING if self.hit_timer <= 0 else self.STATE_HIT
                self.current_frame = 0  # Reset animation frame
        else:
            self.is_grounded = False

        # Update animation
        self._update_animation(dt)

    def _update_animation(self, dt):
        """Update animation frame based on current state."""
        self.animation_timer += dt

        # Get current animation frames
        if self.state == self.STATE_RUNNING:
            frames = self.animations.get("running", [])
            # Speed up animation based on movement speed
            anim_speed = self.animation_speed / self.speed_multiplier
        elif self.state == self.STATE_JUMPING:
            frames = self.animations.get("jumping", [])
            anim_speed = self.animation_speed
        elif self.state == self.STATE_HIT:
            frames = self.animations.get("hit", [])
            anim_speed = self.animation_speed * 1.5  # Slower for hit animation
        else:
            frames = []
            anim_speed = self.animation_speed

        # Advance frame if enough time has passed
        if frames and self.animation_timer >= anim_speed:
            self.animation_timer = 0
            # For hit animation, don't loop - stay on last frame
            if self.state == self.STATE_HIT:
                self.current_frame = min(self.current_frame + 1, len(frames) - 1)
            else:
                self.current_frame = (self.current_frame + 1) % len(frames)

    def get_rect(self):
        """Get collision rectangle for hit detection."""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def collect_yarn(self, amount=1):
        """
        Collect yarn.

        Args:
            amount: Number of yarn to collect
        """
        self.yarn_count += amount

    def hit_obstacle(self):
        """
        Handle being hit by an obstacle.
        Returns tuple of (yarn_lost, yarn_positions, is_dead) for explosion effect.
        Loses HALF of current yarn and one life.
        """
        if self.state == self.STATE_HIT:
            return 0, [], False

        # Set hit state
        self.state = self.STATE_HIT
        self.hit_timer = self.hit_duration

        # Lose a life
        self.lives -= 1
        is_dead = self.lives <= 0

        # Small bounce up so the death animation falls back to ground
        self.velocity_y = -200  # Small upward bounce
        self.is_grounded = False

        # Lose HALF your yarn (as per design doc)
        yarn_to_lose = self.yarn_count // 2
        if yarn_to_lose == 0 and self.yarn_count > 0:
            yarn_to_lose = 1  # Lose at least 1 if you have any

        # Calculate yarn explosion (Sonic-style ring scatter)
        # Cap visual scatter at 10 for performance
        scatter_count = min(yarn_to_lose, 10)
        yarn_positions = []

        for i in range(scatter_count):
            # Create explosion pattern - scatter north, east, and west (not down)
            # Angles: -135° to +135° (upper half + sides, avoiding straight down)
            angle_range = math.pi * 1.5  # 270 degrees
            angle_start = -math.pi * 0.75  # Start at -135 degrees (upper left)
            angle = angle_start + (i / max(scatter_count - 1, 1)) * angle_range
            speed = 200 + (i % 3) * 50

            yarn_positions.append({
                'x': self.x + self.width / 2,
                'y': self.y + self.height / 2,
                'velocity_x': math.cos(angle) * speed,
                'velocity_y': math.sin(angle) * speed - 150,  # Upward bias
            })

        # Lose yarn from player count
        self.yarn_count -= yarn_to_lose

        return yarn_to_lose, yarn_positions, is_dead

    def add_life(self):
        """Add a life (up to max)."""
        if self.lives < self.max_lives:
            self.lives += 1
            return True
        return False

    def reset_lives(self):
        """Reset lives to max (for new game)."""
        self.lives = self.max_lives

    def get_speed_percentage(self):
        """Get current speed as percentage of max speed (for UI)."""
        return (self.speed_multiplier / 3.0) * 100

    def render(self, surface, camera_offset_x):
        """
        Render the squirrel.

        Args:
            surface: Pygame surface to draw on
            camera_offset_x: Camera x offset for rendering
        """
        screen_x = self.x - camera_offset_x

        # Get current sprite based on state
        sprite = None

        if self.state == self.STATE_HIT:
            # Use hit animation (falling-back-death)
            frames = self.animations.get("hit", [])
            if frames:
                frame_idx = min(self.current_frame, len(frames) - 1)
                sprite = frames[frame_idx]
            elif self.hit_sprite:
                sprite = self.hit_sprite
            else:
                frames = self.animations.get("running", [])
                if frames and self.current_frame < len(frames):
                    sprite = frames[self.current_frame].copy()
                    sprite.fill((255, 100, 100, 128), special_flags=pygame.BLEND_RGBA_MULT)
        elif self.state == self.STATE_JUMPING:
            frames = self.animations.get("jumping", [])
            if frames:
                frame_idx = min(self.current_frame, len(frames) - 1)
                sprite = frames[frame_idx]
        else:  # Running
            frames = self.animations.get("running", [])
            if frames:
                frame_idx = self.current_frame % len(frames)
                sprite = frames[frame_idx]

        # Fallback to static sprite
        if sprite is None:
            sprite = self.static_sprite

        # Draw the sprite or fallback to rectangle
        if sprite:
            # Apply sprite offset to align squirrel feet with ground
            # Extra offset for animations to settle on floor
            if self.state == self.STATE_HIT:
                anim_offset = 30
            elif self.state == self.STATE_RUNNING:
                anim_offset = 10
            else:
                anim_offset = 0
            surface.blit(sprite, (screen_x, self.y + self.sprite_offset_y + anim_offset))
        else:
            # Fallback: draw placeholder rectangle
            color = self.hit_color if self.state == self.STATE_HIT else self.color
            rect = pygame.Rect(screen_x, self.y, self.width, self.height)
            pygame.draw.rect(surface, color, rect)

            # Draw eyes (simple circles)
            eye_color = (255, 255, 255)
            pupil_color = (0, 0, 0)

            # Left eye
            left_eye_x = screen_x + 10
            eye_y = self.y + 12
            pygame.draw.circle(surface, eye_color, (int(left_eye_x), int(eye_y)), 5)
            pygame.draw.circle(surface, pupil_color, (int(left_eye_x + 2), int(eye_y)), 2)

            # Right eye
            right_eye_x = screen_x + 25
            pygame.draw.circle(surface, eye_color, (int(right_eye_x), int(eye_y)), 5)
            pygame.draw.circle(surface, pupil_color, (int(right_eye_x + 2), int(eye_y)), 2)

            # Draw tail (simple triangle)
            tail_color = (101, 50, 15)  # Darker brown
            tail_points = [
                (screen_x, self.y + 10),
                (screen_x - 15, self.y + 5),
                (screen_x - 10, self.y + 20)
            ]
            pygame.draw.polygon(surface, tail_color, tail_points)
