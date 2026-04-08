"""
sarangi_voice.py — Bowed sarangi synthesis.

The sarangi is the voice of the raga made physical.
Three main gut strings (Sa, Pa, Sa+) bowed with heavy pressure
and short strokes. Sympathetic taraf strings tuned to the raga
ring beneath every note via SympatheticKernel.

Main strings: Sa (tonic), Pa (fifth), Sa+ (octave)
Bow: heavy pressure, short strokes, gut string grain
Body: nasal resonance, skin membrane buzz
Sympathetic: every note excites the taraf
"""

import math
import numpy as np
from typing import Optional, List

RATE = 48000


class SarangiString:
    """Bowed sarangi gut string — vectorized additive synthesis.

    Fast enough for real-time. Sounds like a bowed gut string:
    - Odd harmonics stronger than even (bowed string characteristic)
    - Slight inharmonicity (gut string stretching)
    - Nasal body resonance via IIR filter
    - Rosin grain noise
    """

    def __init__(self, freq: float, rate: int = RATE):
        self.freq   = max(20.0, freq)
        self.rate   = rate
        self.bow_force  = 0.55
        self.bow_noise  = 0.008
        self.inharmonicity = 0.0006

        # Phase continuity
        self._phase = 0.0

        # Body resonance IIR state
        self._bx1 = self._bx2 = self._by1 = self._by2 = 0.0

        # Looping cache — pre-rendered 1 second of bowed tone
        self._cache = None       # np.float32 array
        self._cache_freq = 0.0
        self._cache_pos = 0

    def set_freq(self, freq: float):
        freq = max(20.0, freq)
        if abs(freq - self.freq) > 1.0:
            self._cache = None  # invalidate cache on freq change
        self.freq = freq

    def render(self, frames: int, amp: float = 0.8) -> np.ndarray:
        """Vectorized bowed string — additive synthesis with bow character."""
        t = np.arange(frames, dtype=np.float64) / self.rate

        out = np.zeros(frames, dtype=np.float64)

        # Bowed string harmonic series — odd harmonics dominate
        harmonics = [
            (1, 1.000), (2, 0.200), (3, 0.600), (4, 0.080),
            (5, 0.350), (6, 0.040), (7, 0.200), (8, 0.020),
            (9, 0.120), (11, 0.060),
        ]

        B = self.inharmonicity
        for n, strength in harmonics:
            fn = self.freq * n * math.sqrt(1 + B * n * n)
            if fn > self.rate * 0.45:
                break
            decay = np.exp(-t * (0.15 + n * 0.08))
            phase = 2 * math.pi * fn * t + self._phase * n
            out += strength * decay * np.sin(phase)

        self._phase += 2 * math.pi * self.freq * frames / self.rate

        # Rosin grain noise
        noise = self.bow_noise * np.random.randn(frames)
        out += noise * np.exp(-t * 8.0)

        # Body resonance IIR — nasal ~400Hz (scipy lfilter for vectorized speed)
        try:
            from scipy.signal import lfilter
            b_coeff = np.array([1.0, 0.0, -0.68])
            a_coeff = np.array([1.0, -1.65, 0.72])
            zi = np.array([self._by1 * a_coeff[1] + self._bx1 * b_coeff[0],
                           self._by2 * a_coeff[2] + self._bx2 * b_coeff[2]])
            out, zf = lfilter(b_coeff, a_coeff, out, zi=zi)
            self._bx1 = out[-1] if len(out) > 0 else 0.0
            self._bx2 = out[-2] if len(out) > 1 else 0.0
            self._by1 = zf[0] if len(zf) > 0 else 0.0
            self._by2 = zf[1] if len(zf) > 1 else 0.0
        except ImportError:
            a1, a2 = -1.65, 0.72
            b0, b2 = 1.0, -0.68
            for i in range(frames):
                y = b0 * out[i] + b2 * self._bx2 - a1 * self._by1 - a2 * self._by2
                self._bx2 = self._bx1
                self._bx1 = out[i]
                self._by2 = self._by1
                self._by1 = y
                out[i] = y

        # Normalize and apply amplitude
        peak = np.max(np.abs(out))
        if peak > 1e-6:
            out /= peak
        return out * amp * self.bow_force * 1.5

    def render_looped(self, frames: int, amp: float = 0.8) -> np.ndarray:
        """Read from a pre-rendered 1-second cache, looping. Zero per-call synthesis.

        Cache is built once per frequency change. Audio callback just reads indices.
        """
        if self._cache is None or abs(self.freq - self._cache_freq) > 1.0:
            # Render 1 second of bowed tone into cache
            raw = self.render(self.rate, amp=1.0)
            # Crossfade loop boundary (50ms)
            fade = min(int(self.rate * 0.05), len(raw) // 4)
            if fade > 0:
                raw[:fade] *= np.linspace(0, 1, fade)
                raw[-fade:] *= np.linspace(1, 0, fade)
            self._cache = raw.astype(np.float32)
            self._cache_freq = self.freq
            self._cache_pos = 0

        cache_len = len(self._cache)
        indices = (np.arange(frames) + self._cache_pos) % cache_len
        self._cache_pos = (self._cache_pos + frames) % cache_len
        return self._cache[indices] * amp


class SarangiVoice:
    """Sarangi lead voice with phrase-level playing and sympathetic feed."""

    def __init__(self, sa_hz: float = 130.81, rate: int = RATE,
                 sympathetic_kernel=None):
        self.sa_hz       = sa_hz
        self.rate        = rate
        self._sympathetic = sympathetic_kernel

        self._current_string: Optional[SarangiString] = None
        self._current_freq   = sa_hz
        self._note_remaining = 0
        self._vadi_swara     = "Pa"

        # Portamento
        self._porto_start   = 0.0
        self._porto_end     = 0.0
        self._porto_samples = 0
        self._porto_pos     = 0
        self._in_porto      = False

        # Vibrato — slower, wider than cello
        self._vib_phase   = 0.0
        self._vib_rate    = 5.2
        self._vib_depth   = 0.006
        self._vib_delay   = int(rate * 0.25)
        self._vib_attack  = int(rate * 0.35)
        self._vib_sample  = 0

        # Phrase
        self._phrase_queue: List[dict] = []
        self._phrase_pos   = 0

        # Envelope
        self._env_attack  = int(rate * 0.04)   # faster attack — bow bites
        self._env_release = int(rate * 0.12)
        self._env_pos     = 0
        self._releasing   = False

        self._target_amp  = 0.0
        self.mix_amp      = 0.55

    def retune(self, sa_hz: float):
        if abs(sa_hz - self.sa_hz) > 0.5:
            self.sa_hz = sa_hz
            self._current_string = None

    def _ji_tune(self, freq: float) -> float:
        if self.sa_hz <= 0:
            return freq
        ratio = freq / self.sa_hz
        JI = [0.5, 256/243, 9/8, 32/27, 5/4, 4/3, 45/32,
              3/2, 128/81, 5/3, 16/9, 15/8, 2.0, 3.0, 4.0]
        nearest = min(JI, key=lambda r: abs(r - ratio))
        return self.sa_hz * nearest

    def set_note(self, freq_hz: float, duration_sec: float,
                 amplitude: float = 0.7, gamak: str = "none"):
        if freq_hz <= 0:
            self._releasing = True
            self._note_remaining = int(duration_sec * self.rate)
            return

        freq_hz = self._ji_tune(freq_hz)

        # Portamento — sarangi always slides a little
        # Planetary gamakas have characteristic slide qualities
        porto_times = {
            "meend": 0.22, "andolana": 0.06, "andolan": 0.06,
            "kan": 0.05, "none": 0.02,
            "kampita": 0.04,      # Mangala — quick to pitch, then oscillates
            "pratyahata": 0.01,   # Surya — sharp attack from above
            "murcchana": 0.18,    # Shukra — sweet rising glide
            "sparsha": 0.03,      # Budha — brief touch
        }
        porto_time = porto_times.get(gamak, 0.02)

        if self._current_freq > 0 and porto_time > 0:
            self._porto_start   = self._current_freq
            self._porto_end     = freq_hz
            self._porto_samples = int(porto_time * self.rate)
            self._porto_pos     = 0
            self._in_porto      = True

        self._current_freq = freq_hz

        if self._current_string is None:
            self._current_string = SarangiString(freq_hz, self.rate)
        else:
            self._current_string.set_freq(freq_hz)

        # Bow pressure from gamak — planetary gamakas have distinct bowing
        _BOW = {
            "andolana": 0.62, "andolan": 0.62, "none": 0.55,
            "meend": 0.40, "kan": 0.35,
            "kampita": 0.70,      # Mangala — fierce pressure
            "pratyahata": 0.75,   # Surya — sharp attack
            "murcchana": 0.45,    # Shukra — sweet, lighter
            "sparsha": 0.30,      # Budha — barely touching
        }
        self._current_string.bow_force = _BOW.get(gamak, 0.55)

        self._target_amp = amplitude
        self._note_remaining = int(duration_sec * self.rate)
        self._vib_sample = 0
        self._env_pos = 0
        self._releasing = False

        # Excite sympathetic strings
        if self._sympathetic is not None:
            try:
                self._sympathetic.excite_melody(freq_hz, amplitude * 0.8)
                self._sympathetic.excite_melody(freq_hz * 2, amplitude * 0.3)
            except Exception:
                pass

    def set_phrase(self, notes: list, mode: str = "gat"):
        self._phrase_queue = list(notes)
        self._phrase_pos = 0
        if self._phrase_queue:
            self._play_next()

    def set_vadi(self, swara: str):
        self._vadi_swara = swara

    def _play_next(self):
        if not self._phrase_queue:
            self._releasing = True
            return
        note = self._phrase_queue.pop(0)
        idx  = self._phrase_pos
        self._phrase_pos += 1

        freq     = note.get("freq_hz", 0)
        dur      = note.get("duration_sec", 1.5)
        gamak    = note.get("gamak", "none")
        is_nyasa = note.get("is_nyasa", False)

        # Phrase arc amplitude
        n_total = self._phrase_pos + len(self._phrase_queue)
        arc = idx / max(n_total - 1, 1)
        amp = 0.55 + 0.35 * math.sin(arc * math.pi)
        if is_nyasa:
            amp = min(1.0, amp * 1.2)
            dur *= 1.4

        self.set_note(freq, dur, amp, gamak)

    def render(self, frames: int) -> np.ndarray:
        out = np.zeros(frames, dtype=np.float64)

        if self._current_string is None:
            return np.zeros((frames, 2), dtype=np.float32)

        # Portamento
        if self._in_porto and self._porto_pos < self._porto_samples:
            t = self._porto_pos / self._porto_samples
            freq = self._porto_start * (self._porto_end / max(self._porto_start, 1)) ** t
            self._current_string.set_freq(freq)
            self._porto_pos += frames
            if self._porto_pos >= self._porto_samples:
                self._in_porto = False
                self._current_string.set_freq(self._porto_end)

        # Render string
        raw = self._current_string.render(frames, self._target_amp)

        # Vibrato — delayed entry (vectorized)
        sample_indices = np.arange(frames) + self._vib_sample + 1
        vib_active = sample_indices > self._vib_delay
        if np.any(vib_active):
            elapsed = sample_indices[vib_active] - self._vib_delay
            depth = self._vib_depth * np.minimum(1.0, elapsed / self._vib_attack)
            phase_arr = self._vib_phase + 2 * math.pi * self._vib_rate * np.arange(np.sum(vib_active)) / self.rate
            raw[vib_active] *= 1.0 + depth * np.sin(phase_arr)
        self._vib_sample += frames
        self._vib_phase += 2 * math.pi * self._vib_rate * frames / self.rate

        # Envelope (vectorized)
        env = np.ones(frames, dtype=np.float64)
        if self._releasing:
            pos_arr = np.arange(frames) + self._env_pos
            env = np.maximum(0.0, 1.0 - pos_arr / max(1, self._env_release))
            self._env_pos += frames
        elif self._env_pos < self._env_attack:
            pos_arr = np.arange(frames) + self._env_pos
            attack_part = pos_arr < self._env_attack
            env[attack_part] = pos_arr[attack_part] / self._env_attack
            self._env_pos += frames
        raw *= env

        out = raw * self.mix_amp

        # Stereo — centered (sarangi sits center stage)
        delay = max(1, int(self.rate * 0.0006))
        left  = out
        right = np.roll(out, delay) * 0.88

        self._note_remaining = max(0, self._note_remaining - frames)
        if self._note_remaining <= 0 and self._phrase_queue:
            self._play_next()

        return np.column_stack([left, right]).astype(np.float32)

    @property
    def note_finished(self) -> bool:
        return self._note_remaining <= 0 and not self._phrase_queue


if __name__ == "__main__":
    import wave
    print("Rendering sarangi — Bhairava alap at Sa=130.81Hz...")
    voice = SarangiVoice(sa_hz=130.81)
    phrase = [
        {"freq_hz": 130.81, "duration_sec": 2.5, "gamak": "none",
         "is_nyasa": False, "swara": "Sa"},
        {"freq_hz": 138.59, "duration_sec": 1.8, "gamak": "meend",
         "is_nyasa": False, "swara": "re"},
        {"freq_hz": 164.81, "duration_sec": 3.0, "gamak": "andolana",
         "is_nyasa": True, "swara": "Ga"},
        {"freq_hz": 174.61, "duration_sec": 1.2, "gamak": "none",
         "is_nyasa": False, "swara": "Ma"},
        {"freq_hz": 196.00, "duration_sec": 3.5, "gamak": "none",
         "is_nyasa": True, "swara": "Pa"},
        {"freq_hz": 130.81, "duration_sec": 4.0, "gamak": "meend",
         "is_nyasa": True, "swara": "Sa"},
    ]
    voice.set_phrase(phrase, mode="alap")
    total = sum(int(n["duration_sec"] * RATE) for n in phrase) + RATE * 2
    buf = np.zeros((total, 2), dtype=np.float32)
    pos = 0
    while pos < total:
        chunk = min(2048, total - pos)
        buf[pos:pos + chunk] = voice.render(chunk)
        pos += chunk
    buf = np.clip(buf, -1, 1)
    pcm = (buf * 32767).astype(np.int16)
    with wave.open("/tmp/sarangi_test.wav", "w") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(RATE)
        w.writeframes(pcm.tobytes())
    print(f"Written /tmp/sarangi_test.wav ({total / RATE:.1f}s)")
    print("Play: aplay /tmp/sarangi_test.wav")
