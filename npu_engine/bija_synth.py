"""
bija_synth.py — Pure formant synthesis for bīja mantras.

No TTS. No voice. Pure resonance.
Each bīja is a sequence of varṇas (phonemic components),
each varṇa shaped by bandpass filters at its formant frequencies.

The bīja should sound like a singing bowl finding its tone.

Synthesis chain:
  source (glottal pulse / noise / breathy mix)
  → bandpass F1, F2, F3 (scipy biquad)
  → amplitude envelope (slow sattva rise/fall)
  → sum varṇas with crossfade

Sample rate: 48000 Hz (MOTU M2 native).
"""

import numpy as np
from scipy.signal import sosfilt, butter
from typing import Dict, List, Optional


SR = 48000  # MOTU M2 native

# ── Varṇa formant table ────────────────────────────────────────────
# F1, F2, F3 in Hz. Source type: vowel, nasal, fricative, stop, breathy.
VARNA = {
    "A":  {"f1": 700, "f2": 1100, "f3": 2800, "src": "vowel"},
    "I":  {"f1": 300, "f2": 2200, "f3": 3000, "src": "vowel"},
    "U":  {"f1": 350, "f2": 800,  "f3": 2600, "src": "vowel"},
    "E":  {"f1": 400, "f2": 2000, "f3": 2800, "src": "vowel"},
    "O":  {"f1": 400, "f2": 900,  "f3": 2400, "src": "vowel"},
    "M":  {"f1": 250, "f2": 900,  "f3": 2200, "src": "nasal", "nasality": 0.9},
    "N":  {"f1": 250, "f2": 1500, "f3": 2500, "src": "nasal", "nasality": 0.7},
    "H":  {"f1": 500, "f2": 1500, "f3": 2500, "src": "breathy", "breathiness": 0.8},
    "R":  {"f1": 400, "f2": 1600, "f3": 2700, "src": "vowel"},
    "L":  {"f1": 350, "f2": 1100, "f3": 2800, "src": "vowel"},
    "K":  {"f1": 300, "f2": 1800, "f3": 2800, "src": "stop"},
    "SH": {"f1": 400, "f2": 2200, "f3": 3200, "src": "fricative"},
    "S":  {"f1": 400, "f2": 2600, "f3": 3600, "src": "fricative"},
}

# ── Bīja decomposition ─────────────────────────────────────────────
# Each bīja → ordered varṇa sequence with relative duration weights.
BIJA_PATH = {
    "aim":   [("A", 1.0), ("I", 1.2), ("M", 1.8)],
    "om":    [("A", 0.8), ("U", 1.0), ("M", 2.0)],
    "hrim":  [("H", 0.4), ("R", 0.6), ("I", 1.0), ("M", 1.8)],
    "hum":   [("H", 0.4), ("U", 1.0), ("M", 2.0)],
    "shrim": [("SH", 0.3), ("R", 0.5), ("I", 1.0), ("M", 1.8)],
    "krim":  [("K", 0.2), ("R", 0.5), ("I", 1.0), ("M", 1.8)],
    "klim":  [("K", 0.2), ("L", 0.5), ("I", 1.0), ("M", 1.8)],
    "dum":   [("K", 0.2), ("U", 1.0), ("M", 2.0)],  # D as stop
    "gam":   [("K", 0.2), ("A", 1.0), ("M", 1.8)],  # G as stop
    "lam":   [("L", 0.6), ("A", 1.0), ("M", 1.8)],
    "vam":   [("U", 0.4), ("A", 1.0), ("M", 1.8)],  # V as labiodental → U-like
    "ram":   [("R", 0.6), ("A", 1.0), ("M", 1.8)],
    "ham":   [("H", 0.4), ("A", 1.0), ("M", 1.8)],
}

# ── Guna → synthesis parameters ────────────────────────────────────
GUNA_PARAMS = {
    "sattva": {"attack": 1.5, "sustain_ratio": 0.5, "release": 2.0, "brightness": 0.7, "vibrato_hz": 4.0, "vibrato_depth": 0.008},
    "rajas":  {"attack": 0.8, "sustain_ratio": 0.4, "release": 1.2, "brightness": 0.9, "vibrato_hz": 5.5, "vibrato_depth": 0.012},
    "tamas":  {"attack": 2.0, "sustain_ratio": 0.5, "release": 2.5, "brightness": 0.4, "vibrato_hz": 3.0, "vibrato_depth": 0.005},
}


def _bandpass(signal: np.ndarray, center_hz: float, q: float = 8.0) -> np.ndarray:
    """Apply a biquad bandpass filter."""
    if center_hz <= 20 or center_hz >= SR / 2 - 100:
        return signal * 0.0
    low = max(center_hz / (q ** 0.5), 20)
    high = min(center_hz * (q ** 0.5), SR / 2 - 1)
    if low >= high:
        return signal * 0.0
    sos = butter(2, [low, high], btype="bandpass", fs=SR, output="sos")
    return sosfilt(sos, signal)


def _glottal_source(n_samples: int, f0: float, vibrato_hz: float = 4.0,
                    vibrato_depth: float = 0.008) -> np.ndarray:
    """Glottal pulse train with vibrato — the singing bowl fundamental."""
    t = np.arange(n_samples) / SR
    # Vibrato modulates f0
    vib = 1.0 + vibrato_depth * np.sin(2 * np.pi * vibrato_hz * t)
    phase = np.cumsum(f0 * vib / SR)
    # Rosenberg glottal waveform (smoother than sawtooth)
    frac = phase % 1.0
    pulse = np.where(frac < 0.4, 0.5 * (1 - np.cos(np.pi * frac / 0.4)),
                     np.where(frac < 0.6, 0.5 * (1 + np.cos(np.pi * (frac - 0.4) / 0.2)),
                              0.0))
    return pulse


def _noise_source(n_samples: int) -> np.ndarray:
    """Shaped noise for fricatives and breathy components."""
    return np.random.randn(n_samples) * 0.5


def _synth_varna(varna_key: str, n_samples: int, f0: float,
                 brightness: float, vibrato_hz: float,
                 vibrato_depth: float) -> np.ndarray:
    """Synthesize a single varṇa through formant filtering."""
    v = VARNA.get(varna_key, VARNA["A"])
    src_type = v["src"]

    # Build source signal
    if src_type == "vowel":
        source = _glottal_source(n_samples, f0, vibrato_hz, vibrato_depth)
    elif src_type == "nasal":
        nasality = v.get("nasality", 0.8)
        glottal = _glottal_source(n_samples, f0, vibrato_hz, vibrato_depth * 0.5)
        noise = _noise_source(n_samples) * 0.15
        source = glottal * (1 - nasality * 0.3) + noise * nasality
    elif src_type == "breathy":
        breathiness = v.get("breathiness", 0.7)
        glottal = _glottal_source(n_samples, f0, vibrato_hz, vibrato_depth)
        noise = _noise_source(n_samples)
        source = glottal * (1 - breathiness) + noise * breathiness
    elif src_type == "fricative":
        noise = _noise_source(n_samples)
        # High-pass shape for sibilance
        sos_hp = butter(2, 2000, btype="highpass", fs=SR, output="sos")
        source = sosfilt(sos_hp, noise)
    elif src_type == "stop":
        # Brief burst then silence → vowel transition handled by crossfade
        burst_len = min(int(0.015 * SR), n_samples)
        source = np.zeros(n_samples)
        source[:burst_len] = _noise_source(burst_len) * 2.0
    else:
        source = _glottal_source(n_samples, f0, vibrato_hz, vibrato_depth)

    # Formant filtering: parallel F1 + F2 + F3
    f1 = _bandpass(source, v["f1"], q=6.0)
    f2 = _bandpass(source, v["f2"], q=8.0) * brightness
    f3 = _bandpass(source, v["f3"], q=10.0) * brightness * 0.5

    out = f1 + f2 * 0.7 + f3 * 0.3
    return out


def _envelope(n_samples: int, attack_s: float, sustain_ratio: float,
              release_s: float) -> np.ndarray:
    """Smooth attack-sustain-release envelope."""
    atk = min(int(attack_s * SR), n_samples // 3)
    rel = min(int(release_s * SR), n_samples // 2)
    sus = n_samples - atk - rel
    if sus < 0:
        # Not enough room — proportional split
        atk = int(n_samples * 0.3)
        rel = int(n_samples * 0.5)
        sus = n_samples - atk - rel

    env = np.ones(n_samples)
    # Raised cosine attack
    if atk > 0:
        env[:atk] = 0.5 * (1 - np.cos(np.pi * np.arange(atk) / atk))
    # Sustain with gentle droop
    if sus > 0:
        env[atk:atk + sus] = 1.0 - (1 - sustain_ratio) * np.linspace(0, 1, sus) ** 2
    # Raised cosine release
    if rel > 0:
        start_level = env[atk + sus - 1] if (atk + sus - 1) < n_samples else sustain_ratio
        env[atk + sus:] = start_level * 0.5 * (1 + np.cos(np.pi * np.arange(rel) / rel))
    return env


def _crossfade(a: np.ndarray, b: np.ndarray, fade_samples: int) -> np.ndarray:
    """Crossfade two signals, overlapping by fade_samples."""
    if fade_samples <= 0 or len(a) == 0:
        return np.concatenate([a, b])
    fade = min(fade_samples, len(a), len(b))
    out = np.zeros(len(a) + len(b) - fade)
    out[:len(a)] = a
    # Crossfade region
    ramp_out = np.linspace(1, 0, fade)
    ramp_in = np.linspace(0, 1, fade)
    out[len(a) - fade:len(a)] = a[-fade:] * ramp_out + b[:fade] * ramp_in
    out[len(a):] = b[fade:]
    return out


def synthesize_bija(bija_id: str, field_state: dict,
                    duration_s: float = 5.0,
                    sample_rate: int = 48000) -> np.ndarray:
    """Synthesize a bīja mantra as pure formant resonance.

    Returns float32 numpy array at 48kHz.
    """
    from .field_to_sound import element_to_sa, guna_to_character

    p = field_state.get("panchanga", {})
    element = (p.get("element", "earth")).lower()
    guna = (p.get("guna", "sattva")).lower()

    # Sa frequency from element
    f0 = element_to_sa(element)
    gp = GUNA_PARAMS.get(guna, GUNA_PARAMS["sattva"])

    # Get bija path
    bija_key = bija_id.lower().strip()
    path = BIJA_PATH.get(bija_key)
    if not path:
        # Fallback: decompose character by character
        path = [(ch.upper(), 1.0) for ch in bija_key]

    # Calculate per-varṇa durations
    total_weight = sum(w for _, w in path)
    crossfade_s = 0.15  # 150ms crossfade between varṇas
    crossfade_samples = int(crossfade_s * SR)

    # Synthesize each varṇa
    segments = []
    for varna_key, weight in path:
        frac = weight / total_weight
        seg_dur = duration_s * frac
        n_samples = max(int(seg_dur * SR), SR // 10)

        sig = _synth_varna(
            varna_key, n_samples, f0,
            brightness=gp["brightness"],
            vibrato_hz=gp["vibrato_hz"],
            vibrato_depth=gp["vibrato_depth"],
        )

        # Per-varṇa envelope (gentle)
        env = _envelope(n_samples, gp["attack"] * frac, 0.85, gp["release"] * frac)
        sig *= env
        segments.append(sig)

    # Assemble with crossfade
    audio = segments[0]
    for seg in segments[1:]:
        audio = _crossfade(audio, seg, crossfade_samples)

    # Global envelope
    global_env = _envelope(len(audio), gp["attack"], gp["sustain_ratio"], gp["release"])
    audio *= global_env

    # Normalize
    peak = np.max(np.abs(audio))
    if peak > 0.001:
        audio = audio * (0.4 / peak)

    return audio.astype(np.float32)
