import struct
import wave
import pytest

from airdrum.audio_engine import AudioEngine
from airdrum.config import AudioConfig


def create_dummy_wav(filepath: str) -> None:
    """Generates a short dummy 16-bit mono WAV file for testing."""
    sample_rate = 44100
    duration = 0.05  # 50 ms
    num_samples = int(sample_rate * duration)
    with wave.open(filepath, "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for _ in range(num_samples):
            wav_file.writeframes(struct.pack("<h", 0))


def test_audio_engine_initialization(tmp_path):
    sounds_dir = tmp_path / "sounds"
    sounds_dir.mkdir()

    create_dummy_wav(str(sounds_dir / "snare.wav"))
    create_dummy_wav(str(sounds_dir / "hihat.wav"))

    config = AudioConfig(buffer_size=256)
    engine = AudioEngine(config, sounds_dir=str(sounds_dir))

    assert "snare" in engine.sounds
    assert "hihat" in engine.sounds

    engine.play_sound("snare", velocity=0.8)
    engine.stop_all()
    engine.close()