"""
Sound manager for Squirrel Yarn game.
Handles sound effects and dynamic music tempo based on player speed.
"""

import pygame
import os


class SoundManager:
    """Manages all game audio including dynamic music tempo."""

    # Base frequency for mixer
    BASE_FREQUENCY = 44100

    def __init__(self):
        """Initialize the sound system."""
        self.current_frequency = self.BASE_FREQUENCY

        # Initialize pygame mixer
        pygame.mixer.init(frequency=self.current_frequency, size=-16, channels=2, buffer=512)

        # Sound effects
        self.sounds = {}
        self._load_sounds()

        # Music state - prefer OGG for web compatibility
        self.gameplay_music_path = self._find_music_file("gameplay_music", ["ogg", "wav"])
        self.intro_music_path = self._find_music_file("intro_music", ["ogg", "mp3"])
        self.pause_music_path = self._find_music_file("pause_music", ["ogg", "wav"])

        # Dynamic tempo tracking
        self.current_tempo = 1.0  # 1.0 = normal speed
        self.target_tempo = 1.0
        self.tempo_lerp_speed = 0.5  # How fast tempo changes (slower = smoother)

        # Tempo range (squirrel speed goes from 1.0 to 3.0)
        self.min_tempo = 1.0   # At base speed
        self.max_tempo = 1.4   # At max speed (3x) - 40% faster

        # Track if music is playing
        self.music_playing = False
        self.current_music = None
        self.music_position = 0.0  # Track position for seamless tempo changes
        self.music_volume = 0.7

        # For frequency-based tempo changes
        self.last_applied_tempo = 1.0

    def _find_music_file(self, basename: str, extensions: list) -> str:
        """Find a music file, preferring the first extension that exists."""
        music_dir = os.path.join("assets", "music")
        for ext in extensions:
            path = os.path.join(music_dir, f"{basename}.{ext}")
            if os.path.exists(path):
                return path
        # Return first option as fallback
        return os.path.join(music_dir, f"{basename}.{extensions[0]}")

    def _load_sounds(self):
        """Load all sound effects. Prefers OGG for web compatibility."""
        sound_files = {
            "jump": "jump",
            "running": "running",
            "rainbow": "grabbed_a_rainbow",
            "start": "start_sound",
            "death": "death",
        }

        sounds_dir = os.path.join("assets", "sounds")
        for name, basename in sound_files.items():
            # Try OGG first (better for web), then WAV
            for ext in [".ogg", ".wav"]:
                path = os.path.join(sounds_dir, basename + ext)
                if os.path.exists(path):
                    try:
                        self.sounds[name] = pygame.mixer.Sound(path)
                        break
                    except pygame.error as e:
                        print(f"Could not load sound {basename}{ext}: {e}")

    def play_sound(self, name: str, volume: float = 1.0):
        """Play a sound effect."""
        if name in self.sounds:
            self.sounds[name].set_volume(volume)
            self.sounds[name].play()

    def play_intro_music(self, volume: float = 0.7):
        """Play the intro/splash screen music."""
        if os.path.exists(self.intro_music_path):
            try:
                pygame.mixer.music.load(self.intro_music_path)
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(-1)  # Loop
                self.music_playing = True
                self.current_music = "intro"
                self.music_volume = volume
            except pygame.error as e:
                print(f"Could not play intro music: {e}")

    def play_gameplay_music(self, volume: float = 0.7):
        """Start the gameplay music."""
        if os.path.exists(self.gameplay_music_path):
            try:
                pygame.mixer.music.load(self.gameplay_music_path)
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(-1)  # Loop
                self.music_playing = True
                self.current_music = "gameplay"
                self.current_tempo = 1.0
                self.target_tempo = 1.0
                self.last_applied_tempo = 1.0
                self.music_volume = volume
            except pygame.error as e:
                print(f"Could not play gameplay music: {e}")

    def stop_music(self):
        """Stop all music."""
        pygame.mixer.music.stop()
        self.music_playing = False
        self.current_music = None

    def play_pause_music(self, volume: float = 0.5):
        """Play the pause menu music."""
        if os.path.exists(self.pause_music_path):
            try:
                pygame.mixer.music.load(self.pause_music_path)
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(-1)  # Loop
                self.music_playing = True
                self.current_music = "pause"
                self.music_volume = volume
            except pygame.error as e:
                print(f"Could not play pause music: {e}")

    def pause_music(self):
        """Pause the current music."""
        pygame.mixer.music.pause()

    def unpause_music(self):
        """Unpause the current music."""
        pygame.mixer.music.unpause()

    def set_speed_multiplier(self, speed_multiplier: float):
        """
        Update target tempo based on player's speed multiplier.

        Args:
            speed_multiplier: The player's current speed (1.0 to 3.0)
        """
        # Map speed (1.0-3.0) to tempo (1.0-1.4)
        normalized = (speed_multiplier - 1.0) / 2.0  # 0.0 to 1.0
        self.target_tempo = self.min_tempo + normalized * (self.max_tempo - self.min_tempo)

    def on_player_hit(self):
        """Called when player hits an obstacle - slow down music."""
        # Immediately drop tempo back toward base
        self.target_tempo = self.min_tempo

    def update(self, dt: float):
        """
        Update music tempo smoothly.

        Args:
            dt: Delta time in seconds
        """
        # NOTE: Dynamic tempo changes are disabled because pygame's mixer
        # reinit causes audio hiccups. The tempo tracking is kept for future
        # use if we switch to a library that supports real-time tempo changes.
        if not self.music_playing or self.current_music != "gameplay":
            return

        # Track target tempo (for future use or UI display)
        if abs(self.current_tempo - self.target_tempo) > 0.01:
            if self.current_tempo < self.target_tempo:
                self.current_tempo += self.tempo_lerp_speed * dt
                self.current_tempo = min(self.current_tempo, self.target_tempo)
            else:
                self.current_tempo -= self.tempo_lerp_speed * dt
                self.current_tempo = max(self.current_tempo, self.target_tempo)

        # Tempo changes disabled to prevent audio hiccups
        # To re-enable, uncomment the following:
        # tempo_diff = abs(self.current_tempo - self.last_applied_tempo)
        # if tempo_diff > 0.05:
        #     self._apply_tempo()

    def _apply_tempo(self):
        """
        Apply the current tempo by changing the mixer frequency.

        This is a technique that changes playback speed AND pitch together.
        Higher frequency = faster + higher pitch (like a tape sped up).
        """
        # Calculate new frequency based on tempo
        new_frequency = int(self.BASE_FREQUENCY / self.current_tempo)

        # Clamp to reasonable range
        new_frequency = max(22050, min(88200, new_frequency))

        if new_frequency != self.current_frequency:
            try:
                # Save current position
                pos = pygame.mixer.music.get_pos() / 1000.0  # Convert to seconds

                # Stop current music
                pygame.mixer.music.stop()

                # Reinitialize mixer with new frequency
                pygame.mixer.quit()
                pygame.mixer.init(frequency=new_frequency, size=-16, channels=2, buffer=512)

                self.current_frequency = new_frequency

                # Reload sounds (they're invalidated by mixer reinit)
                self._load_sounds()

                # Reload and play music from saved position
                if os.path.exists(self.gameplay_music_path):
                    pygame.mixer.music.load(self.gameplay_music_path)
                    pygame.mixer.music.set_volume(self.music_volume)
                    pygame.mixer.music.play(-1, start=pos)

                self.last_applied_tempo = self.current_tempo

            except pygame.error as e:
                print(f"Could not change tempo: {e}")

    def set_music_volume(self, volume: float):
        """Set the music volume (0.0 to 1.0)."""
        self.music_volume = volume
        pygame.mixer.music.set_volume(volume)

    def set_sound_volume(self, name: str, volume: float):
        """Set volume for a specific sound effect."""
        if name in self.sounds:
            self.sounds[name].set_volume(volume)


# Global sound manager instance
_sound_manager = None


def get_sound_manager() -> SoundManager:
    """Get the global sound manager instance."""
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = SoundManager()
    return _sound_manager
