"""
Game module - Main game logic, state management, and coordination.
"""

import pygame
from player import Squirrel
from camera import Camera
from generator import LevelGenerator
from ui import UI, SplashScreen
from save import load_save, save_game, get_best_distance
from sound import get_sound_manager


class Game:
    """Main game class that manages game state, entities, and logic."""

    # Game states
    STATE_SPLASH = "splash"
    STATE_PLAYING = "playing"
    STATE_GAME_OVER = "game_over"

    def __init__(self, screen_width, screen_height):
        """Initialize the game."""
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Game state - start with splash
        self.state = self.STATE_SPLASH

        # Debug mode - press D to toggle
        self.debug_mode = False

        # Ground level - positioned so only one row of tiles (16px) shows above screen bottom
        self.ground_y = 584

        # Initialize UI components
        self.splash_screen = SplashScreen(screen_width, screen_height)
        self.ui = UI(screen_width, screen_height)

        # Load saved data
        self.save_data = load_save()
        self.high_score = self.save_data["high_score"]
        self.best_distance = self.save_data["best_distance"]
        # The sign shows the PREVIOUS best - it stays fixed during a run
        self.milestone_sign_distance = self.best_distance

        # These get initialized when game starts
        self.player = None
        self.camera = None
        self.generator = None

        # Scoring
        self.stash = 0
        self.distance = 0
        self.is_new_high_score = False
        self.is_new_distance_record = False

        # Time tracking
        self.game_time = 0

        # Sound manager
        self.sound = get_sound_manager()
        self.sound.play_intro_music()

        # Background images (try to load)
        self._load_backgrounds()
        self._load_foreground_elements()

    def _load_foreground_elements(self):
        """Load foreground sprites for parallax effect."""
        import os
        import random
        self.fg_sprites = []
        self.fg_elements = []  # Active foreground elements on screen
        self.last_fg_spawn_x = 0
        self.fg_spawn_interval = 200  # Spawn every ~200 world units (1.5x more frequent)

        fg_files = [
            ("foreground/tree_tall.png", "tree", 1.0),
            ("foreground/tree_medium.png", "tree", 1.0),
            ("foreground/tree_small.png", "tree", 1.0),
        ]

        # Load base images with type info (we'll scale them per-layer when spawning)
        self.fg_base_sprites = []
        for filename, sprite_type, size_mult in fg_files:
            path = os.path.join("assets", "sprites", filename)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                self.fg_base_sprites.append({"image": img, "type": sprite_type, "size_mult": size_mult})

    def _load_backgrounds(self):
        """Load background images or create fallbacks."""
        import os
        self.bg_layers = []

        bg_files = ["bg_far.png", "bg_mid.png"]
        parallax_speeds = [0.1, 0.3]

        for i, (filename, speed) in enumerate(zip(bg_files, parallax_speeds)):
            path = os.path.join("assets", "sprites", filename)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                # Scale image to screen height, maintaining aspect ratio
                orig_w, orig_h = img.get_size()
                scale_factor = self.screen_height / orig_h
                new_w = int(orig_w * scale_factor)
                new_h = self.screen_height
                img = pygame.transform.scale(img, (new_w, new_h))
                self.bg_layers.append({"image": img, "speed": speed, "width": new_w})
            else:
                # Create simple colored fallback
                surf = pygame.Surface((self.screen_width, self.screen_height))
                if i == 0:
                    # Sky gradient
                    for y in range(self.screen_height):
                        ratio = y / self.screen_height
                        r = int(135 - ratio * 50)
                        g = int(206 - ratio * 50)
                        b = int(235 - ratio * 30)
                        pygame.draw.line(surf, (r, g, b), (0, y), (self.screen_width, y))
                elif i == 1:
                    surf.fill((34, 80, 34))
                    surf.set_alpha(100)
                else:
                    surf.fill((50, 120, 50))
                    surf.set_alpha(80)
                self.bg_layers.append({"image": surf, "speed": speed, "width": self.screen_width})

        # Load hills background (if exists)
        self.bg_hills = None
        hills_path = os.path.join("assets", "sprites", "bg_hills.png")
        if os.path.exists(hills_path):
            hills_img = pygame.image.load(hills_path).convert_alpha()
            orig_w, orig_h = hills_img.get_size()
            scale_factor = self.screen_height / orig_h
            new_w = int(orig_w * scale_factor)
            self.bg_hills = pygame.transform.scale(hills_img, (new_w, self.screen_height))
            self.bg_hills_width = new_w

    def start_game(self):
        """Initialize/reset game for a new run."""
        self.state = self.STATE_PLAYING

        # Play start sound and gameplay music
        self.sound.play_sound("start")
        self.sound.play_gameplay_music()

        # Initialize player (position at ground level minus player height)
        start_x = 100
        self.player = Squirrel(start_x, self.ground_y - 110)  # 584 - 110 = 474

        # Initialize camera
        self.camera = Camera(self.screen_width, self.screen_height)

        # Initialize level generator
        self.generator = LevelGenerator()
        self.generator.generate_initial()

        # Reset scoring
        self.stash = 0
        self.distance = 0

        # Reset foreground elements
        self.fg_elements = []
        self.last_fg_spawn_x = 0

        # Rainbow particles for milestone sign
        self.rainbow_particles = []
        self.passed_milestone = False

        # Life regeneration milestones (1000, 2000, 4000, 8000, ...)
        self.life_milestones = [1000, 2000, 4000, 8000, 16000, 32000]
        self.next_life_milestone_idx = 0

        self.game_time = 0
        self.is_new_high_score = False
        self.is_new_distance_record = False

        # Update milestone sign to show current best (from last run's record if set)
        self.milestone_sign_distance = self.best_distance

    def handle_keypress(self, key):
        """Handle keyboard press events."""
        if self.state == self.STATE_SPLASH:
            if key == pygame.K_SPACE:
                self.start_game()
            elif key == pygame.K_ESCAPE:
                return "quit"

        elif self.state == self.STATE_PLAYING:
            if key == pygame.K_SPACE or key == pygame.K_UP or key == pygame.K_w:
                if self.player.is_grounded:
                    self.sound.play_sound("jump")
                self.player.jump()
            elif key == pygame.K_d:
                self.debug_mode = not self.debug_mode
            elif key == pygame.K_ESCAPE:
                # Return to splash/menu screen
                self._return_to_menu()

        elif self.state == self.STATE_GAME_OVER:
            if key == pygame.K_SPACE or key == pygame.K_RETURN:
                self.start_game()
            elif key == pygame.K_ESCAPE:
                # Return to splash/menu screen
                self._return_to_menu()

        return None

    def _return_to_menu(self):
        """Return to the splash/menu screen."""
        self.state = self.STATE_SPLASH
        self.sound.stop_music()
        self.sound.play_intro_music()
        # Reset splash screen animation
        self.splash_screen = SplashScreen(self.screen_width, self.screen_height)

    def update(self, dt, keys):
        """Update game state."""
        if self.state == self.STATE_SPLASH:
            self.splash_screen.update(dt)

        elif self.state == self.STATE_PLAYING:
            self.game_time += dt

            # Update player
            self.player.update(dt)

            # Update sound manager (tempo based on speed)
            self.sound.set_speed_multiplier(self.player.speed_multiplier)
            self.sound.update(dt)

            # Update distance
            self.distance = int(self.player.x / 10)

            # Check for new distance record
            if self.distance > self.best_distance:
                if not self.is_new_distance_record:
                    self.is_new_distance_record = True
                self.best_distance = self.distance

            # Check for life regeneration milestones
            self._check_life_milestones()

            # Update camera
            self.camera.update(dt, self.player.x, self.player.get_speed_percentage())

            # Update level generator
            self.generator.update(self.camera.get_offset_x(), self.distance, self.stash)

            # Update all sprites
            camera_x = self.camera.get_offset_x()
            for ground in self.generator.ground_tiles:
                ground.update(camera_x)
            for platform in self.generator.platforms:
                platform.update(camera_x)
            for bush in self.generator.bushes:
                bush.update(camera_x)
            for yarn in self.generator.yarns:
                yarn.update(camera_x, dt)

            # Update foreground elements (spawn new ones, remove old ones)
            self._update_foreground(camera_x)

            # Check if player passed the milestone sign - spawn rainbow particles
            self._check_milestone_passed()

            # Update rainbow particles
            self._update_rainbow_particles(dt)

            # Check collisions
            self._check_collisions()

            # Check if player fell in gap
            self._check_gaps()

    def _check_collisions(self):
        """Check collisions between player and objects using world coordinates."""
        # Player rect in WORLD coordinates
        player_rect = pygame.Rect(
            self.player.x,
            self.player.y,
            self.player.width,
            self.player.height
        )

        # Check bush collisions (world coordinates)
        for bush in self.generator.bushes[:]:
            # Bush hitbox in world coordinates (slightly smaller than visual)
            bush_rect = pygame.Rect(
                bush.world_x + bush.width // 6,
                bush.world_y + bush.height // 4,
                bush.width * 2 // 3,
                bush.height * 2 // 3
            )
            if player_rect.colliderect(bush_rect):
                if self.player.state != Squirrel.STATE_HIT:
                    # Player hit bush - lose half yarn and a life!
                    yarn_lost, scattered, is_dead = self.player.hit_obstacle()

                    # Slow down music when hit
                    self.sound.on_player_hit()

                    # Subtract from stash as well
                    self.stash = max(0, self.stash - yarn_lost)

                    # Create scattered yarn sprites for visual effect
                    for s in scattered:
                        from yarn import YarnSkein
                        yarn = YarnSkein(s['x'], s['y'], "red", 1)
                        # Use the pre-calculated velocities from hit_obstacle
                        yarn.is_scattered = True
                        yarn.velocity_x = s['velocity_x'] / 60  # Convert from per-second to per-frame
                        yarn.velocity_y = s['velocity_y'] / 60
                        self.generator.yarns.append(yarn)

                    # Check if player is dead (no lives left)
                    if is_dead:
                        self._end_game()
                        return

                    # Reset yarn tier progression
                    self.generator.reset_yarn_tiers()

                    # Remove bush
                    self.generator.bushes.remove(bush)
                break

        # Check yarn collection (world coordinates)
        for yarn in self.generator.yarns[:]:
            # Skip scattered yarn that's still flying (give it time to spread out)
            if yarn.is_scattered:
                if yarn.is_expired() or yarn.scatter_timer < 30:  # Skip first 0.5 seconds
                    continue
            yarn_rect = pygame.Rect(
                yarn.world_x,
                yarn.world_y,
                yarn.SIZE,
                yarn.SIZE
            )
            if player_rect.colliderect(yarn_rect):
                self.player.collect_yarn(yarn.points)
                self.stash += yarn.points
                # Play special sound for rainbow yarn (highest tier)
                if yarn.is_rainbow:
                    self.sound.play_sound("rainbow")
                self.generator.yarns.remove(yarn)

        # Check platform collisions for landing (world coordinates)
        # First, check if player is currently supported by any platform
        player_feet_y = self.player.y + self.player.height
        standing_on_platform = False

        for platform in self.generator.platforms:
            # Check if player is standing on this platform
            # Player's X must overlap with platform, and feet must be at platform level
            player_left = self.player.x
            player_right = self.player.x + self.player.width
            plat_left = platform.world_x
            plat_right = platform.world_x + platform.width

            # Check horizontal overlap
            if player_right > plat_left and player_left < plat_right:
                # Check if standing on top (within 5 pixels)
                if abs(player_feet_y - platform.world_y) < 5 and self.player.is_grounded:
                    standing_on_platform = True
                    self.player.ground_y = platform.world_y - self.player.height
                    break

                # Check if landing on platform (falling onto it)
                if self.player.velocity_y > 0:
                    player_prev_feet = player_feet_y - self.player.velocity_y * (1/60)

                    if player_prev_feet <= platform.world_y and player_feet_y >= platform.world_y:
                        self.player.y = platform.world_y - self.player.height
                        self.player.velocity_y = 0
                        self.player.is_grounded = True
                        self.player.ground_y = platform.world_y - self.player.height
                        standing_on_platform = True
                        if self.player.state == Squirrel.STATE_JUMPING:
                            self.player.state = Squirrel.STATE_RUNNING
                        break

        # If not on a platform and grounded, check if we should fall
        if not standing_on_platform and self.player.is_grounded:
            # Reset to actual ground level - gravity will handle the rest
            if self.player.y < self.ground_y - self.player.height - 10:
                # Player is above ground and not on platform - they should fall
                self.player.is_grounded = False
                self.player.ground_y = self.ground_y - self.player.height

    def _check_gaps(self):
        """Check if player fell into a gap by checking actual ground tiles."""
        # Get the player's center X position
        player_center_x = self.player.x + self.player.width / 2

        # Check if there's a ground tile under the player
        # Ground tiles are 64px wide, so check if any tile covers the player's center
        TILE_SIZE = 64
        has_ground_under_player = False

        for ground in self.generator.ground_tiles:
            tile_left = ground.world_x
            tile_right = ground.world_x + TILE_SIZE

            # If the player's center is within this tile's horizontal range
            if tile_left <= player_center_x < tile_right:
                has_ground_under_player = True
                break

        if not has_ground_under_player:
            # No ground tile under player - they're over a gap!
            self.player.ground_y = 9999  # Very far down - let them fall

            # Once player drops below ground level, enable strong gap gravity
            if self.player.y > self.ground_y - self.player.height:
                self.player.falling_in_gap = True

            # Game over if player fell far enough
            if self.player.y > self.ground_y + 50:
                self._end_game()
                return
        else:
            # There IS ground under player - reset ground level and gap flag
            self.player.falling_in_gap = False
            if self.player.y >= self.ground_y - self.player.height - 10:
                self.player.ground_y = self.ground_y - self.player.height

    def _update_foreground(self, camera_x):
        """Spawn and cleanup foreground decorative elements."""
        import random

        if not self.fg_base_sprites:
            return

        # Spawn new foreground elements ahead of camera
        spawn_x = camera_x + self.screen_width + 100
        while self.last_fg_spawn_x < spawn_x:
            self.last_fg_spawn_x += random.randint(200, 400)

            # Check if there's a bush nearby - don't spawn foreground elements near bushes
            bush_nearby = False
            for bush in self.generator.bushes:
                if abs(bush.world_x - self.last_fg_spawn_x) < 150:  # Within 150px of a bush
                    bush_nearby = True
                    break

            # Random chance to spawn (not every interval), and not near bushes
            if random.random() < 0.7 and not bush_nearby:
                sprite_data = random.choice(self.fg_base_sprites)
                base_sprite = sprite_data["image"]
                sprite_type = sprite_data["type"]
                size_mult = sprite_data["size_mult"]
                layer = random.choice(["front", "back"])

                # Scale based on layer: back = 2.5-4.5x, front = 4-6x
                if layer == "back":
                    scale = random.uniform(2.5, 4.5)
                else:
                    scale = random.uniform(4.0, 6.0)

                # Apply per-sprite size multiplier (rocks are smaller than trees)
                scale *= size_mult

                # Scale the sprite
                orig_w, orig_h = base_sprite.get_size()
                scaled_w = int(orig_w * scale)
                scaled_h = int(orig_h * scale)
                scaled_sprite = pygame.transform.scale(base_sprite, (scaled_w, scaled_h))

                # Position randomly left or right side of screen
                side = random.choice(["left", "right"])
                if side == "left":
                    x_offset = random.randint(-scaled_w // 2, 50)
                else:
                    x_offset = random.randint(self.screen_width - 50, self.screen_width + scaled_w // 2)

                # Position Y: anchor to ground line
                # Trees need more offset due to trunk transparency, rocks less
                if sprite_type == "tree":
                    # Trees have transparent padding - push down to anchor trunk to grass
                    ground_offset = int(15 * scale)
                else:
                    # Rocks sit directly on ground with minimal offset
                    ground_offset = int(5 * scale)

                y_pos = self.ground_y - scaled_h + ground_offset

                self.fg_elements.append({
                    "sprite": scaled_sprite,
                    "world_x": self.last_fg_spawn_x + x_offset,
                    "y": y_pos,
                    "layer": layer
                })

        # Remove elements that are completely off-screen to the left
        # Account for sprite width so they don't disappear while still visible
        self.fg_elements = [e for e in self.fg_elements
                           if e["world_x"] + e["sprite"].get_width() > camera_x]

    def _check_milestone_passed(self):
        """Check if player passed the milestone sign and spawn rainbow particles."""
        import random
        import math

        if self.milestone_sign_distance <= 0 or self.passed_milestone:
            return

        milestone_world_x = self.milestone_sign_distance * 10
        player_center_x = self.player.x + self.player.width / 2

        # Check if player just passed the sign
        if player_center_x > milestone_world_x and not self.passed_milestone:
            self.passed_milestone = True

            # Spawn rainbow particles shooting up from the sign
            rainbow_colors = [
                (255, 0, 0),      # Red
                (255, 127, 0),    # Orange
                (255, 255, 0),    # Yellow
                (0, 255, 0),      # Green
                (0, 0, 255),      # Blue
                (75, 0, 130),     # Indigo
                (148, 0, 211),    # Violet
                (255, 105, 180),  # Pink
                (0, 255, 255),    # Cyan
            ]

            # Create burst of particles
            for _ in range(50):
                color = random.choice(rainbow_colors)
                self.rainbow_particles.append({
                    "world_x": milestone_world_x + random.randint(-30, 30),
                    "y": self.ground_y - random.randint(50, 100),
                    "vel_x": random.uniform(-3, 3),
                    "vel_y": random.uniform(-12, -6),  # Shoot upward
                    "color": color,
                    "size": random.randint(3, 8),
                    "life": random.uniform(1.5, 3.0),  # Seconds
                    "gravity": random.uniform(0.2, 0.4),
                })

    def _update_rainbow_particles(self, dt):
        """Update rainbow particle positions and remove dead particles."""
        for particle in self.rainbow_particles[:]:
            particle["world_x"] += particle["vel_x"]
            particle["y"] += particle["vel_y"]
            particle["vel_y"] += particle["gravity"]  # Gravity
            particle["life"] -= dt

            # Remove dead particles
            if particle["life"] <= 0 or particle["y"] > self.ground_y + 50:
                self.rainbow_particles.remove(particle)

    def _check_life_milestones(self):
        """Check if player reached a distance milestone for life regeneration."""
        if self.next_life_milestone_idx >= len(self.life_milestones):
            return

        next_milestone = self.life_milestones[self.next_life_milestone_idx]
        if self.distance >= next_milestone:
            # Award a life if not at max
            if self.player.add_life():
                self.sound.play_sound("rainbow")  # Reuse rainbow sound for life gain
            self.next_life_milestone_idx += 1

    def _end_game(self):
        """End the current game."""
        self.state = self.STATE_GAME_OVER

        # Play death sound and stop gameplay music
        self.sound.play_sound("death")
        self.sound.stop_music()

        # Check for new high score
        if self.stash > self.high_score:
            self.high_score = self.stash
            self.is_new_high_score = True

        # Save progress
        save_game(self.high_score, self.best_distance)

    def render(self, surface):
        """Render the game."""
        if self.state == self.STATE_SPLASH:
            self.splash_screen.draw(surface)
            return

        # First, fill the entire screen with sky gradient (top to ground level)
        sky_top = (135, 180, 220)      # Light blue at top
        sky_bottom = (200, 220, 240)   # Lighter blue near horizon
        for y in range(self.ground_y):
            ratio = y / self.ground_y
            r = int(sky_top[0] + (sky_bottom[0] - sky_top[0]) * ratio)
            g = int(sky_top[1] + (sky_bottom[1] - sky_top[1]) * ratio)
            b = int(sky_top[2] + (sky_bottom[2] - sky_top[2]) * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (self.screen_width, y))

        # Draw background gradient below ground (dirt getting deeper)
        light_brown = (139, 90, 60)   # Top of dirt (just below ground tile)
        dark_brown = (50, 30, 15)     # Deep dirt at bottom

        for y in range(self.ground_y, self.screen_height):
            # Calculate gradient ratio (0 at ground_y, 1 at bottom)
            ratio = (y - self.ground_y) / (self.screen_height - self.ground_y)
            r = int(light_brown[0] + (dark_brown[0] - light_brown[0]) * ratio)
            g = int(light_brown[1] + (dark_brown[1] - light_brown[1]) * ratio)
            b = int(light_brown[2] + (dark_brown[2] - light_brown[2]) * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (self.screen_width, y))

        # Draw background layers with parallax
        camera_x = self.camera.get_offset_x() if self.camera else 0

        # Layer 0: Hills (slowest parallax, behind everything)
        if self.bg_hills:
            hills_offset = int(camera_x * 0.05) % self.bg_hills_width
            x = -hills_offset
            while x < self.screen_width:
                surface.blit(self.bg_hills, (x, 0))
                x += self.bg_hills_width

        # Layer 1: Far trees (transparent sky lets hills show through)
        if len(self.bg_layers) > 0:
            layer = self.bg_layers[0]
            img_width = layer["width"]
            offset = int(camera_x * layer["speed"]) % img_width
            x = -offset
            while x < self.screen_width:
                surface.blit(layer["image"], (x, 0))
                x += img_width

        # Layer 2: Mid trees (closest background layer, anchored to ground)
        if len(self.bg_layers) > 1:
            layer = self.bg_layers[1]
            img_width = layer["width"]
            img_height = layer["image"].get_height()
            offset = int(camera_x * layer["speed"]) % img_width
            # Position so tree bases are at ground level
            y_pos = self.ground_y - img_height
            x = -offset
            while x < self.screen_width:
                surface.blit(layer["image"], (x, y_pos))
                x += img_width

        # Draw foreground elements (back layer - behind ground/path)
        for elem in self.fg_elements:
            if elem["layer"] == "back":
                screen_x = elem["world_x"] - camera_x
                sprite_w = elem["sprite"].get_width()
                if -sprite_w <= screen_x <= self.screen_width:
                    surface.blit(elem["sprite"], (screen_x, elem["y"]))

        # Draw ground tiles
        for ground in self.generator.ground_tiles:
            if -64 <= ground.rect.x <= self.screen_width + 64:
                surface.blit(ground.image, ground.rect)

        # Draw platforms
        for platform in self.generator.platforms:
            if -platform.width <= platform.rect.x <= self.screen_width + platform.width:
                surface.blit(platform.image, platform.rect)

        # Draw bushes
        for bush in self.generator.bushes:
            if -bush.width <= bush.rect.x <= self.screen_width + bush.width:
                surface.blit(bush.image, bush.rect)

        # Draw yarn
        for yarn in self.generator.yarns:
            if -yarn.SIZE <= yarn.rect.x <= self.screen_width + yarn.SIZE:
                surface.blit(yarn.image, yarn.rect)

        # Draw player
        self.player.render(surface, camera_x)

        # Draw foreground elements (front layer - in front of player)
        for elem in self.fg_elements:
            if elem["layer"] == "front":
                screen_x = elem["world_x"] - camera_x
                sprite_w = elem["sprite"].get_width()
                if -sprite_w <= screen_x <= self.screen_width:
                    surface.blit(elem["sprite"], (screen_x, elem["y"]))

        # Draw milestone sign at the PREVIOUS best distance (fixed position)
        if self.milestone_sign_distance > 0:
            milestone_world_x = self.milestone_sign_distance * 10  # Convert back to world units
            self.ui.draw_milestone_sign(surface, milestone_world_x, camera_x, self.milestone_sign_distance, self.ground_y)

        # Draw rainbow particles
        for particle in self.rainbow_particles:
            screen_x = particle["world_x"] - camera_x
            if -20 <= screen_x <= self.screen_width + 20:
                # Fade out as life decreases
                alpha = min(255, int(particle["life"] * 170))
                size = particle["size"]
                color = particle["color"]

                # Draw particle as a small square/pixel
                particle_surf = pygame.Surface((size, size), pygame.SRCALPHA)
                particle_surf.fill((*color, alpha))
                surface.blit(particle_surf, (int(screen_x), int(particle["y"])))

        # Draw UI
        self.ui.draw_stash(surface, self.stash)
        self.ui.draw_distance(surface, self.distance)
        self.ui.draw_lives(surface, self.player.lives, self.player.max_lives)

        # Draw new record notification
        if self.is_new_distance_record and self.state == self.STATE_PLAYING:
            self.ui.draw_new_record(surface)

        # Draw debug overlay
        if self.debug_mode and self.state == self.STATE_PLAYING:
            self._draw_debug(surface, camera_x)

        # Draw game over screen
        if self.state == self.STATE_GAME_OVER:
            self.ui.draw_game_over(
                surface,
                self.stash,
                self.distance,
                self.high_score,
                self.is_new_high_score
            )

    def _draw_debug(self, surface, camera_x):
        """Draw debug collision boxes."""
        # Player hitbox (green)
        player_screen_x = self.player.x - camera_x
        player_rect = pygame.Rect(player_screen_x, self.player.y, self.player.width, self.player.height)
        pygame.draw.rect(surface, (0, 255, 0), player_rect, 2)

        # Platform hitboxes (blue)
        for platform in self.generator.platforms:
            screen_x = platform.world_x - camera_x
            plat_rect = pygame.Rect(screen_x, platform.world_y, platform.width, platform.height)
            pygame.draw.rect(surface, (0, 100, 255), plat_rect, 2)

        # Gap zones (red - where you die) - draw based on ACTUAL missing ground tiles
        # Only show gaps where we have ground tiles on BOTH sides (not at edges)
        TILE_SIZE = 64
        gap_height = 80

        # Get all ground tile X positions in a set for fast lookup
        ground_tile_positions = set()
        for ground in self.generator.ground_tiles:
            ground_tile_positions.add(int(ground.world_x))

        # Only check for gaps between existing ground tiles
        if ground_tile_positions:
            min_tile = min(ground_tile_positions)
            max_tile = max(ground_tile_positions)

            # Find consecutive missing tiles and draw them as gaps
            gap_start = None
            for tile_x in range(min_tile, max_tile + TILE_SIZE, TILE_SIZE):
                if tile_x not in ground_tile_positions:
                    # This is a gap tile
                    if gap_start is None:
                        gap_start = tile_x
                else:
                    # This is a ground tile - if we were tracking a gap, draw it
                    if gap_start is not None:
                        gap_width = tile_x - gap_start
                        screen_x = gap_start - camera_x
                        # Only draw if on screen
                        if -gap_width < screen_x < self.screen_width:
                            gap_rect = pygame.Rect(screen_x, self.ground_y, gap_width, gap_height)
                            pygame.draw.rect(surface, (255, 0, 0), gap_rect, 3)
                            # Draw X pattern
                            pygame.draw.line(surface, (255, 0, 0),
                                           (screen_x, self.ground_y),
                                           (screen_x + gap_width, self.ground_y + gap_height), 2)
                            pygame.draw.line(surface, (255, 0, 0),
                                           (screen_x + gap_width, self.ground_y),
                                           (screen_x, self.ground_y + gap_height), 2)
                            # Label
                            font = pygame.font.Font(None, 18)
                            label = font.render(f"Gap: {gap_width}px", True, (255, 100, 100))
                            surface.blit(label, (screen_x + 5, self.ground_y + 5))
                        gap_start = None

        # Ground level indicator (yellow line)
        pygame.draw.line(surface, (255, 255, 0), (0, self.ground_y), (self.screen_width, self.ground_y), 1)

        # Debug: show ground tile positions (small yellow dots at each tile)
        for ground in self.generator.ground_tiles:
            screen_x = ground.world_x - camera_x
            if 0 <= screen_x <= self.screen_width:
                pygame.draw.circle(surface, (255, 255, 0), (int(screen_x + 32), self.ground_y - 5), 4)

        # Player's current ground_y (magenta line at player position)
        pygame.draw.line(surface, (255, 0, 255),
                        (player_screen_x - 20, self.player.ground_y + self.player.height),
                        (player_screen_x + self.player.width + 20, self.player.ground_y + self.player.height), 2)

        # Debug text
        font = pygame.font.Font(None, 20)
        debug_info = [
            f"Player X: {self.player.x:.0f}",
            f"Player Y: {self.player.y:.0f}",
            f"Ground Y: {self.player.ground_y:.0f}",
            f"Grounded: {self.player.is_grounded}",
            f"Vel Y: {self.player.velocity_y:.0f}",
            f"Gaps: {len(self.generator.gaps)}",
            f"Platforms: {len(self.generator.platforms)}",
        ]
        for i, text in enumerate(debug_info):
            rendered = font.render(text, True, (255, 255, 255))
            surface.blit(rendered, (self.screen_width - 150, 100 + i * 18))
