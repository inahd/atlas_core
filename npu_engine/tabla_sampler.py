"""
tabla_sampler.py — plays tabla bol WAV samples at tala beat positions.
No synthesis. Just samples triggered at the right time.
"""
import os
import numpy as np
from pathlib import Path
from scipy.io import wavfile

# Filename stem → canonical bol name mapping.
# Multiple samples for the same bol: pick the primary (no suffix).
_FILENAME_BOL = {
    "na":           "Na",
    "na-open":      "Na_open",
    "na_sharp":     "Na_sharp",
    "tas":          "Dha",
    "tas_2":        "Dha_2",
    "tas_3":        "Dha_3",
    "tun":          "Dhin",
    "tun_2":        "Dhin_2",
    "tun_3":        "Dhin_3",
    "te":           "Te",
    "te_2":         "Te_2",
    "te_middlefinger": "Te_mid",
    "te_ne":        "Te_ne",
    "ke":           "Ka",
    "ke_2":         "Ka_2",
    "ke_3":         "Ka_3",
    "re":           "Re",
    "ghe":          "Ghe",
    "ghe_2":        "Ghe_2",
    "ghe_3":        "Ghe_3",
    "ghe_4":        "Ghe_4",
    "ghe_5":        "Ghe_5",
    "ghe_6":        "Ghe_6",
    "ghe_7":        "Ghe_7",
    "ghe_8":        "Ghe_8",
    "dhec":         "Dhec",
}

# Map tala bol strings (from kernel tala_bols) → sample key.
# Kernel bols are lowercase: dha, dhin, na, ta, tin, ke, ge, etc.
_BOL_SAMPLE = {
    "dha":   "Dha",
    "dhin":  "Dhin",
    "dhi":   "Dhin",
    "na":    "Na",
    "ta":    "Te",
    "tin":   "Te",
    "ti":    "Te",
    "ke":    "Ka",
    "ka":    "Ka",
    "ge":    "Ghe",
    "re":    "Re",
    "tu":    "Dhin",
    "kat":   "Ka",
    "kite":  "Ka",
    "trkt":  "Te",
    "din":   "Dhin",
    "sam":   "Dha",
}

TARGET_SR = 48000


def load_samples(sample_dir: str) -> dict:
    """Load all .wav files from sample_dir into a dict keyed by bol name.

    Returns: {'Na': np.float32 array, 'Dha': ..., ...}
    """
    sample_path = Path(sample_dir)
    if not sample_path.is_dir():
        return _ensure_synth_samples()

    samples = {}
    for wav_file in sorted(sample_path.glob("*.wav")):
        # Extract the meaningful part of the filename:
        # 130421__mmiron__na.wav → "na"
        stem = wav_file.stem
        parts = stem.split("__")
        key = parts[-1] if len(parts) > 1 else stem

        bol_name = _FILENAME_BOL.get(key)
        if bol_name is None:
            continue

        try:
            sr, data = wavfile.read(str(wav_file))
        except Exception:
            continue

        # Convert to float32
        if data.dtype == np.int16:
            audio = data.astype(np.float32) / 32768.0
        elif data.dtype == np.int32:
            audio = data.astype(np.float32) / 2147483648.0
        elif data.dtype == np.float32 or data.dtype == np.float64:
            audio = data.astype(np.float32)
        else:
            continue

        # Mono → use first channel if stereo
        if audio.ndim == 2:
            audio = audio[:, 0]

        # Resample if needed (simple linear interpolation)
        if sr != TARGET_SR:
            duration = len(audio) / sr
            n_out = int(duration * TARGET_SR)
            indices = np.linspace(0, len(audio) - 1, n_out)
            audio = np.interp(indices, np.arange(len(audio)), audio).astype(np.float32)

        # Normalize to peak 0.8
        peak = np.max(np.abs(audio))
        if peak > 1e-6:
            audio = audio * (0.8 / peak)

        # Keep primary sample (no suffix) or first loaded
        if bol_name not in samples:
            samples[bol_name] = audio

    if not samples:
        return _ensure_synth_samples()
    return samples


# ── Synthesized tabla bols (fallback when no samples available) ────
# Physically motivated: membrane + body modes, decay, pitch-drop

def _synth_bol(bol_name: str, sr: int = TARGET_SR) -> np.ndarray:
    """Synthesize a single tabla bol from harmonic modes."""
    _BOL_PARAMS = {
        # bol: (f0, f1_ratio, f2_ratio, body_f0, decay, pitch_drop, noise_mix)
        "Dha":  (180, 2.3, 3.8, 80,  0.25, 0.15, 0.08),  # open bass + treble
        "Dhin": (200, 2.5, 4.0, 90,  0.20, 0.20, 0.06),  # muted bass + treble
        "Na":   (400, 2.8, 4.2, 0,   0.10, 0.05, 0.12),  # treble only, crisp
        "Te":   (350, 3.0, 5.0, 0,   0.08, 0.03, 0.15),  # sharp treble tap
        "Ka":   (300, 2.0, 3.5, 0,   0.06, 0.02, 0.20),  # dry treble
        "Ghe":  (120, 1.8, 2.8, 60,  0.30, 0.25, 0.05),  # deep bass
        "Re":   (280, 2.5, 4.0, 0,   0.12, 0.10, 0.10),  # rolled treble
    }
    params = _BOL_PARAMS.get(bol_name, _BOL_PARAMS.get("Na"))
    if params is None:
        return np.zeros(int(sr * 0.1), dtype=np.float32)
    f0, f1r, f2r, body_f0, decay_time, pitch_drop, noise_mix = params
    dur = min(decay_time * 4, 0.8)
    n = int(sr * dur)
    t = np.arange(n, dtype=np.float64) / sr
    env = np.exp(-t / max(decay_time, 0.01))
    # Pitch drops slightly (membrane relaxation)
    freq = f0 * (1.0 - pitch_drop * t / dur)
    phase = np.cumsum(2 * np.pi * freq / sr)
    # Three membrane modes
    sig = 0.5 * np.sin(phase) * env
    sig += 0.25 * np.sin(phase * f1r) * env ** 1.5
    sig += 0.12 * np.sin(phase * f2r) * env ** 2.0
    # Body resonance (bass drum)
    if body_f0 > 0:
        body_env = np.exp(-t / (decay_time * 2))
        sig += 0.35 * np.sin(2 * np.pi * body_f0 * t) * body_env
    # Attack noise burst
    noise = np.random.randn(n).astype(np.float64) * noise_mix
    noise_env = np.exp(-t / 0.008)  # 8ms burst
    sig += noise * noise_env
    # Normalize
    peak = np.max(np.abs(sig))
    if peak > 1e-6:
        sig = sig * (0.8 / peak)
    return sig.astype(np.float32)


def _ensure_synth_samples() -> dict:
    """Generate synthesized tabla samples for all standard bols."""
    samples = {}
    for bol_name in ("Dha", "Dhin", "Na", "Te", "Ka", "Ghe", "Re"):
        samples[bol_name] = _synth_bol(bol_name)
    return samples


_SILENCE = np.zeros(int(TARGET_SR * 0.1), dtype=np.float32)


def get_bol_audio(samples: dict, bol_name: str, velocity: float = 1.0) -> np.ndarray:
    """Return numpy array for a bol, scaled by velocity.

    Falls back to silence if bol not found.
    """
    audio = samples.get(bol_name)
    if audio is None:
        return _SILENCE.copy()
    return audio * velocity


def render_tala_beat(samples: dict, tala_bols: list, beat_index: int,
                     bpm: int = 72, sr: int = TARGET_SR) -> np.ndarray:
    """Render audio for one tala beat.

    Args:
        samples:    loaded sample dict from load_samples()
        tala_bols:  list of bol strings from field state
        beat_index: current beat position in the tala cycle
        bpm:        beats per minute
        sr:         sample rate

    Returns:
        mono float32 array for one beat duration
    """
    if not tala_bols or not samples:
        beat_samples = int(sr * 60.0 / max(bpm, 30))
        return np.zeros(beat_samples, dtype=np.float32)

    beat_dur = 60.0 / max(bpm, 30)
    beat_samples = int(sr * beat_dur)
    n_bols = len(tala_bols)
    idx = beat_index % n_bols

    bol_str = tala_bols[idx].lower() if idx < n_bols else "—"

    # Skip silence markers
    if bol_str in ("—", "-", "·", ""):
        return np.zeros(beat_samples, dtype=np.float32)

    # Map to sample key
    sample_key = _BOL_SAMPLE.get(bol_str)
    if sample_key is None:
        return np.zeros(beat_samples, dtype=np.float32)

    # Velocity: sam=1.0, accented=0.7, other=0.4
    is_sam = (idx == 0)
    is_accent = bol_str in ("dha", "dhin", "dhi", "sam")
    velocity = 1.0 if is_sam else 0.7 if is_accent else 0.4

    audio = get_bol_audio(samples, sample_key, velocity)

    # Fit into beat-length buffer
    out = np.zeros(beat_samples, dtype=np.float32)
    copy_len = min(len(audio), beat_samples)
    out[:copy_len] = audio[:copy_len]

    return out
