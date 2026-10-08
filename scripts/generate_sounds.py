import math
import os
import struct
import wave
import numpy as np


def generate_wav(filepath: str, samples: np.ndarray, sample_rate: int = 44100) -> None:
    """Writes a 16-bit mono NumPy float array (-1.0 to 1.0) to a WAV file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    int_samples = np.int16(np.clip(samples, -1.0, 1.0) * 32767)

    with wave.open(filepath, "w") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        for s in int_samples:
            wav_file.writeframes(struct.pack("<h", int(s)))


def main() -> None:
    sample_rate = 44100
    out_dir = "assets/sounds"

    # 1. Hi-Hat (Short white noise burst with fast exponential decay)
    dur = 0.1
    t = np.linspace(0, dur, int(sample_rate * dur), False)
    noise = np.random.uniform(-1.0, 1.0, len(t))
    env = np.exp(-t * 50)
    hihat = noise * env * 0.6
    generate_wav(os.path.join(out_dir, "hihat.wav"), hihat)

    # 2. Snare (Mix of noise decay + 180Hz sine tone)
    dur = 0.2
    t = np.linspace(0, dur, int(sample_rate * dur), False)
    noise = np.random.uniform(-1.0, 1.0, len(t)) * np.exp(-t * 25)
    tone = np.sin(2 * np.pi * 180 * t) * np.exp(-t * 30)
    snare = (noise * 0.7 + tone * 0.5) * 0.8
    generate_wav(os.path.join(out_dir, "snare.wav"), snare)

    # 3. High Tom (Pitch-dropping sine wave 200Hz -> 100Hz)
    dur = 0.25
    t = np.linspace(0, dur, int(sample_rate * dur), False)
    freq = 200 * np.exp(-t * 10)
    phase = 2 * np.pi * np.cumsum(freq) / sample_rate
    tom1 = np.sin(phase) * np.exp(-t * 12) * 0.8
    generate_wav(os.path.join(out_dir, "tom1.wav"), tom1)

    # 4. Low Tom (Pitch-dropping sine wave 130Hz -> 65Hz)
    dur = 0.35
    t = np.linspace(0, dur, int(sample_rate * dur), False)
    freq = 130 * np.exp(-t * 8)
    phase = 2 * np.pi * np.cumsum(freq) / sample_rate
    tom2 = np.sin(phase) * np.exp(-t * 9) * 0.85
    generate_wav(os.path.join(out_dir, "tom2.wav"), tom2)

    # 5. Crash Cymbal (Long metallic white noise decay)
    dur = 0.6
    t = np.linspace(0, dur, int(sample_rate * dur), False)
    noise = np.random.uniform(-1.0, 1.0, len(t))
    env = np.exp(-t * 7)
    crash = noise * env * 0.7
    generate_wav(os.path.join(out_dir, "crash.wav"), crash)

    print(f"Generated synthetic drum sounds in '{out_dir}/'")


if __name__ == "__main__":
    main()