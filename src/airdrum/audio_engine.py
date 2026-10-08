import logging
import os
from typing import Dict, Optional

import pygame

from airdrum.config import AudioConfig

logger = logging.getLogger(__name__)

# Fallback alias map to bridge layout IDs with filenames
PAD_ALIASES = {
    "hightom": "tom1",
    "lowtom": "tom2",
    "tom1": "hightom",
    "tom2": "lowtom",
}


class AudioEngine:
    """Low-latency audio playback engine using Pygame mixer."""

    def __init__(self, config: AudioConfig, sounds_dir: str = "assets/sounds") -> None:
        self.config = config
        self.sounds_dir = sounds_dir
        self.sounds: Dict[str, pygame.mixer.Sound] = {}

        try:
            pygame.mixer.pre_init(
                frequency=self.config.sample_rate,
                size=self.config.bit_depth,
                channels=self.config.channels,
                buffer=self.config.buffer_size,
            )
            pygame.mixer.init()
            pygame.mixer.set_num_channels(self.config.polyphony_channels)
            logger.info(
                "AudioEngine initialized (%d Hz, %d channels, buffer size: %d)",
                self.config.sample_rate,
                self.config.channels,
                self.config.buffer_size,
            )
        except Exception as e:
            logger.error("Failed to initialize Pygame mixer: %s", e)

        self.load_sounds()

    def load_sounds(self) -> None:
        """Pre-loads WAV audio samples in the sounds directory into memory, including alias aliases."""
        if not os.path.exists(self.sounds_dir):
            logger.warning("Sounds directory %s does not exist.", self.sounds_dir)
            return

        for filename in os.listdir(self.sounds_dir):
            if filename.endswith(".wav"):
                pad_id = os.path.splitext(filename)[0]
                filepath = os.path.join(self.sounds_dir, filename)
                try:
                    sound = pygame.mixer.Sound(filepath)
                    self.sounds[pad_id] = sound
                    logger.info("Loaded sound sample: %s -> %s", pad_id, filepath)

                    # Register alias mapping (e.g. tom1 -> hightom)
                    if pad_id in PAD_ALIASES:
                        alias_id = PAD_ALIASES[pad_id]
                        self.sounds[alias_id] = sound
                        logger.info("Mapped alias sound sample: %s -> %s", alias_id, filepath)

                except Exception as e:
                    logger.error("Could not load sound %s: %s", filepath, e)

    def play_sound(self, pad_id: str, velocity: float = 1.0) -> None:
        """Triggers audio playback for a given pad ID with volume scaled by velocity."""
        # Fallback check if pad_id alias exists in loaded sounds
        target_id = pad_id
        if target_id not in self.sounds and target_id in PAD_ALIASES:
            target_id = PAD_ALIASES[target_id]

        if target_id not in self.sounds:
            logger.warning("No sound loaded for pad ID: %s", pad_id)
            return

        sound = self.sounds[target_id]
        volume = max(0.0, min(1.0, velocity))
        sound.set_volume(volume)
        sound.play()

    def stop_all(self) -> None:
        """Stops all currently playing audio channels."""
        pygame.mixer.stop()

    def close(self) -> None:
        """Quits the Pygame mixer driver."""
        pygame.mixer.quit()
        logger.info("AudioEngine closed.")