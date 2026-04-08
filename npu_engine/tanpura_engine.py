#!/usr/bin/env python3
"""tanpura_engine.py — four independent tanpura strings

Each string runs its own modal physics (via om.tanpura_string),
renders in its own background thread, crossfades on parameter change.
Audio thread never blocks, never renders.

String definitions loaded from datasets/sound/tanpura_strings.csv.
Graha → jivari/decay derived from graha_master.csv energy/element fields.
Raga variant (Pa/Ma/Dha) selectable from field state.

Default: Pa (1.5) → Sa1 (1.0) → Sa2 (1.0 + 3.5¢) → Sa_low (0.5)
"""
import csv
import os
import numpy as np
import threading
import time
import logging

log = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════
# STRING DEFINITIONS — loaded from CSV, graha values from dataset
# ══════════════════════════════════════════════════════════

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, ".."))
_STRINGS_CSV = os.path.join(_ROOT, "datasets", "sound", "tanpura_strings.csv")
_GRAHA_CSV = os.path.join(_ROOT, "datasets", "cosmology", "graha_master.csv")

_string_defs = None
_graha_data = None


def _load_string_defs():
    """Load tanpura string definitions from CSV."""
    global _string_defs
    if _string_defs is not None:
        return _string_defs
    _string_defs = {}
    try:
        with open(_STRINGS_CSV, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                sid = row.get("string_id", "")
                _string_defs[sid] = {
                    "name": row.get("name", sid),
                    "ratio": float(row.get("default_ratio", 1.0)),
                    "graha": row.get("graha", "Sun"),
                    "jivari": float(row.get("jivari", 0.4)),
                    "decay_s": float(row.get("decay_s", 8.0)),
                    "level": float(row.get("level", 0.25)),
                    "pluck_offset_s": float(row.get("pluck_offset_s", 0.0)),
                    "raga_variant": row.get("raga_variant", "Sa"),
                    "detune_cents": float(row.get("detune_cents", 0.0)),
                    "element": row.get("element", "ether"),
                    "guna": row.get("guna", "sattva"),
                }
    except Exception as e:
        log.warning("tanpura_strings.csv load failed: %s — using defaults", e)
    return _string_defs


def _load_graha_energy():
    """Load graha energy profiles from graha_master.csv."""
    global _graha_data
    if _graha_data is not None:
        return _graha_data
    _graha_data = {}
    try:
        with open(_GRAHA_CSV, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                name = row.get("graha", "").strip()
                _graha_data[name.lower()] = {
                    "element": row.get("element", "ether"),
                    "guna": row.get("guna", "sattva"),
                    "path": float(row.get("path", 0.5)),
                    "luminosity": row.get("color_luminosity", "earth"),
                }
    except Exception as e:
        log.warning("graha_master.csv load failed: %s", e)
    return _graha_data


def _graha_jivari(graha_name: str) -> float:
    """Derive jivari from graha energy: bright → less buzz, dim → more buzz."""
    data = _load_graha_energy()
    g = data.get(graha_name.lower(), {})
    path = g.get("path", 0.5)
    lum = g.get("luminosity", "earth")
    # Bright grahas (Sun, Moon, Jupiter) → cleaner tone
    # Dim grahas (Saturn, Rahu) → more buzz
    base = 0.3 + path * 0.3  # range 0.3 - 0.6
    if lum == "dim":
        base += 0.15
    elif lum == "bright":
        base -= 0.05
    return max(0.15, min(0.70, base))


def _graha_decay(graha_name: str) -> float:
    """Derive string decay from graha element: earth/water → long, fire/air → short."""
    data = _load_graha_energy()
    g = data.get(graha_name.lower(), {})
    elem = g.get("element", "ether")
    return {"earth": 10.0, "water": 9.0, "fire": 7.0, "air": 8.0, "ether": 8.5}.get(elem, 8.0)


# Build lookup dicts from CSV for backward compat
def _build_lookups():
    defs = _load_string_defs()
    graha_jivari = {}
    graha_decay = {}
    string_graha = {}
    string_levels = {}

    # Populate from graha_master energy
    for name in ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"]:
        graha_jivari[name] = _graha_jivari(name)
        graha_decay[name] = _graha_decay(name)

    # Sanskrit name aliases
    _ALIASES = {
        "surya": "sun", "chandra": "moon", "mangala": "mars",
        "budha": "mercury", "guru": "jupiter", "shukra": "venus",
        "shani": "saturn", "rahu": "rahu", "ketu": "ketu",
    }
    for alias, eng in _ALIASES.items():
        graha_jivari[alias] = graha_jivari.get(eng, 0.4)
        graha_decay[alias] = graha_decay.get(eng, 8.0)

    # String-specific overrides from CSV (use CSV jivari if defined)
    for sid, d in defs.items():
        name = d["name"]
        string_graha[name] = d["graha"].lower()
        string_levels[name] = d["level"]
        # Override graha jivari with string-specific value from CSV
        graha_jivari[d["graha"].lower()] = d["jivari"]

    return graha_jivari, graha_decay, string_graha, string_levels

# Build on first import
GRAHA_JIVARI, GRAHA_DECAY, STRING_GRAHA, STRING_LEVELS = _build_lookups()

# Raga variant map: which string replaces Pa based on raga family
RAGA_VARIANT_MAP = {
    "Pa": 1.5,     # default — Pa (Yaman, Bhairav, Bilaval families)
    "Ma": 1.333,   # Todi, Bhairavi, Asavari families
    "Dha": 1.667,  # Kafi, Khamaj families
    "Ni": 1.875,   # Marwa, Puriya families
}

CYCLE_LENGTH = 7.0


# ── Single string engine ────────────────────────────────

class TanpuraString:
    """One physical tanpura string with background rendering and crossfade."""

    def __init__(self, name, freq, graha, sample_rate=48000,
                 render_fn=None):
        self.name = name
        self.freq = freq
        self.graha = graha
        self.sr = sample_rate
        self._render_fn = render_fn  # om.tanpura_string — injected to avoid circular import

        self.jivari = GRAHA_JIVARI[graha]
        self.decay_time = GRAHA_DECAY[graha]

        # Active buffer (looping)
        self.buffer = None
        self.buf_len = 0
        self.buf_pos = 0

        # Crossfade state
        self.next_buffer = None
        self.crossfade_pos = 0
        self.crossfade_len = int(sample_rate * 3.0)
        self.crossfading = False

        self.lock = threading.Lock()

        # Render thread
        self._render_event = threading.Event()
        self._target_freq = freq
        self._target_jivari = self.jivari
        self._thread = threading.Thread(
            target=self._render_loop,
            daemon=True,
            name=f'tanpura_{name}')
        self._thread.start()

        # Trigger initial render
        self._render_event.set()

    def _render_loop(self):
        """Background render thread. Never touches audio path."""
        while True:
            self._render_event.wait()
            self._render_event.clear()

            freq = self._target_freq
            jivari = self._target_jivari

            log.info("tanpura %s: rendering %.2fHz jivari=%.2f",
                     self.name, freq, jivari)

            try:
                buf = self._render(freq, jivari)

                with self.lock:
                    if self.buffer is None:
                        self.buffer = buf
                        self.buf_len = len(buf)
                        self.buf_pos = 0
                    else:
                        self.next_buffer = buf
                        self.crossfading = True
                        self.crossfade_pos = 0

                log.info("tanpura %s: ready peak=%.3f len=%.1fs",
                         self.name, np.max(np.abs(buf)),
                         len(buf) / self.sr)

            except Exception as e:
                log.error("tanpura %s render failed: %s", self.name, e,
                          exc_info=True)

    def _render(self, freq, jivari):
        """Render one string cycle using modal physics.

        Maps jīvārī scalar (0-1) to physics parameters:
        higher jivari → higher bridge/thread stiffness → more buzz.
        """
        if self._render_fn is None:
            raise RuntimeError(f"tanpura {self.name}: no render function — pass render_fn to constructor")

        from npu_engine.relational_params import TanpuraPhysics

        # jivari 0.0 = clean, 1.0 = maximum buzz
        # Scale bridge stiffness: base 4.39e8, range 0.5x - 1.5x
        k_b_scale = 0.5 + jivari * 2.0
        k_c_scale = 0.5 + jivari * 1.5

        physics = TanpuraPhysics(
            k_b=4.39e8 * k_b_scale,
            h_b=4.0e-6,
            k_c=1.2e5 * k_c_scale,
            r_c=1.2,
            h_c=0.0,
            sigma0=0.6,
            sigma1=6.5e-3,
            M_factor=1.0,
            x_out_frac=0.9,
            description=f"{self.name} jivari={jivari:.2f}",
        )

        waveform = self._render_fn(
            sa_freq=freq,
            string_ratio=1.0,
            duration=self.decay_time,
            rate=self.sr,
            physics=physics,
        )

        # Normalize to 1.0
        peak = np.max(np.abs(waveform))
        if peak > 0.001:
            waveform /= peak

        return waveform.astype(np.float32)

    def update_freq(self, new_freq, new_jivari=None):
        """Field changed — request re-render only if change is significant.

        Thresholds: Sa change > 2Hz or jivari change > 0.05.
        Below these, the difference is inaudible and not worth the CPU.
        """
        freq_changed = abs(new_freq - self._target_freq) > 2.0
        jivari_changed = new_jivari is not None and abs(new_jivari - self._target_jivari) > 0.05
        if not freq_changed and not jivari_changed:
            return

        self._target_freq = new_freq
        if new_jivari is not None:
            self._target_jivari = new_jivari

        self._render_event.set()

    def read(self, frames):
        """Audio callback reads frames. Never blocks, never renders.

        Vectorized: no per-sample Python loop. Uses numpy index arrays
        for both normal playback and crossfade paths.
        """
        with self.lock:
            if self.buffer is None:
                return np.zeros(frames, dtype=np.float32)

            indices = (np.arange(frames) + self.buf_pos) % self.buf_len

            if self.crossfading and self.next_buffer is not None:
                cf = self.crossfade_len
                remaining = cf - self.crossfade_pos
                xf_len = min(frames, remaining)

                # Crossfade portion
                t_arr = np.arange(xf_len, dtype=np.float32) + self.crossfade_pos
                t_arr /= cf
                fade_out = 1.0 - t_arr
                fade_in = t_arr

                indices_b = (np.arange(xf_len) + self.buf_pos) % len(self.next_buffer)

                out = np.empty(frames, dtype=np.float32)
                out[:xf_len] = (
                    self.buffer[indices[:xf_len]] * fade_out +
                    self.next_buffer[indices_b] * fade_in)

                # Tail after crossfade completes (if any)
                if xf_len < frames:
                    tail_indices = (np.arange(frames - xf_len) + self.buf_pos + xf_len) % len(self.next_buffer)
                    out[xf_len:] = self.next_buffer[tail_indices]

                self.crossfade_pos += xf_len
                if self.crossfade_pos >= cf:
                    self.buffer = self.next_buffer
                    self.buf_len = len(self.buffer)
                    self.next_buffer = None
                    self.crossfading = False
                    self.crossfade_pos = 0
                    log.info("tanpura %s: crossfade complete", self.name)
            else:
                out = self.buffer[indices]

            self.buf_pos += frames
            return out


def _fallback_render(sa_freq, string_ratio, duration, rate=48000, physics=None,
                     field_params=None):
    """Simple additive tanpura — fallback when om.tanpura_string unavailable."""
    f0 = sa_freq * string_ratio
    N = int(duration * rate)
    t = np.arange(N, dtype=np.float64) / rate
    out = np.zeros(N, dtype=np.float64)
    for j, amp in enumerate([1.0, 0.5, 0.25, 0.12, 0.06]):
        freq = f0 * (j + 1)
        if freq > rate / 2:
            break
        decay = np.exp(-t * (0.3 + j * 0.4))
        out += amp * decay * np.sin(2 * np.pi * freq * t)
    peak = np.max(np.abs(out))
    if peak > 1e-10:
        out /= peak
    return out


# ── Four string engine ───────────────────────────────────

class TanpuraEngine:
    """Four independent tanpura strings. Field-responsive. Never blocks.

    String definitions from datasets/sound/tanpura_strings.csv.
    Graha → jivari/decay from graha_master.csv energy fields.
    First string variant (Pa/Ma/Dha/Ni) selectable from raga family.
    """

    def __init__(self, sa_freq=130.81, sample_rate=48000, field_state=None,
                 variant="Pa"):
        self.sa = sa_freq
        self.sa_freq = sa_freq  # alias used by om.py
        self.sr = sample_rate
        self._initialized = False

        # Resolve the render function. Import om.tanpura_string HERE,
        # not inside thread _render(), to avoid circular import deadlock
        # when om.py imports TanpuraEngine at module level.
        render_fn = self._resolve_render_fn()

        # Load string config from CSV
        defs = _load_string_defs()

        # Determine first string variant from raga family
        variant_ratio = RAGA_VARIANT_MAP.get(variant, 1.5)
        variant_def = defs.get(variant.lower(), defs.get("pa", {}))
        variant_graha = variant_def.get("graha", "venus").lower()

        # Sa2 detuning from CSV (default 3.5 cents)
        sa2_def = defs.get("sa2", {})
        detune_cents = sa2_def.get("detune_cents", 3.5)
        detune_ratio = 2 ** (detune_cents / 1200)

        log.info("TanpuraEngine: Sa=%.2fHz", sa_freq)

        self.strings = {
            variant: TanpuraString(
                variant, sa_freq * variant_ratio,
                variant_graha, sample_rate, render_fn),
            'Sa1': TanpuraString(
                'Sa1', sa_freq,
                STRING_GRAHA.get('Sa1', 'sun'), sample_rate, render_fn),
            'Sa2': TanpuraString(
                'Sa2', sa_freq * detune_ratio,
                STRING_GRAHA.get('Sa2', 'sun'), sample_rate, render_fn),
            'Sa_low': TanpuraString(
                'Sa_low', sa_freq * 0.5,
                STRING_GRAHA.get('Sa_low', 'jupiter'), sample_rate, render_fn),
        }
        self._variant = variant
        self._variant_ratio = variant_ratio

        if field_state:
            self.update_field(field_state)

        self._initialized = True
        log.info("TanpuraEngine: all strings initializing in background")

    @staticmethod
    def _resolve_render_fn():
        """Resolve om.tanpura_string, importing only when called (not at module load)."""
        try:
            from om import tanpura_string
            return tanpura_string
        except ImportError:
            log.warning("om.tanpura_string not available — using fallback additive synthesis")
            return _fallback_render

    def render(self, frames):
        """Mix all four strings. Called from audio callback."""
        mix = np.zeros(frames, dtype=np.float32)

        for name, string in self.strings.items():
            level = STRING_LEVELS.get(name, 0.22)
            audio = string.read(frames)
            mix += audio * level

        # Soft clip — tanh with mild drive
        mix = np.tanh(mix * 1.2).astype(np.float32) * 0.85

        return mix

    def update_field(self, field_state):
        """Field state changed. Update string parameters. Non-blocking."""
        sa = field_state.get('sa_freq', self.sa)
        if abs(sa - self.sa) > 1.0:
            self.sa = sa
            self.sa_freq = sa
            log.info("TanpuraEngine: Sa → %.2fHz", sa)

        nak_lord = field_state.get('nak_lord', 'surya').lower()
        active_jivari = GRAHA_JIVARI.get(nak_lord, 0.40)

        defs = _load_string_defs()
        sa2_def = defs.get("sa2", {})
        detune_cents = sa2_def.get("detune_cents", 3.5)
        detune_ratio = 2 ** (detune_cents / 1200)

        # Update variant string (Pa/Ma/Dha/Ni)
        variant = self._variant
        if variant in self.strings:
            variant_graha = STRING_GRAHA.get(variant, 'venus')
            self.strings[variant].update_freq(
                sa * self._variant_ratio,
                GRAHA_JIVARI.get(variant_graha, 0.30) *
                (0.8 + active_jivari * 0.4))

        # Update Sa strings
        if 'Sa1' in self.strings:
            sa1_graha = STRING_GRAHA.get('Sa1', 'sun')
            self.strings['Sa1'].update_freq(
                sa,
                GRAHA_JIVARI.get(sa1_graha, 0.45) *
                (0.8 + active_jivari * 0.4))
        if 'Sa2' in self.strings:
            sa2_graha = STRING_GRAHA.get('Sa2', 'sun')
            self.strings['Sa2'].update_freq(
                sa * detune_ratio,
                GRAHA_JIVARI.get(sa2_graha, 0.45) *
                (0.8 + active_jivari * 0.4))
        if 'Sa_low' in self.strings:
            low_graha = STRING_GRAHA.get('Sa_low', 'jupiter')
            self.strings['Sa_low'].update_freq(
                sa * 0.5,
                GRAHA_JIVARI.get(low_graha, 0.40) *
                (0.8 + active_jivari * 0.4))

    def get_status(self):
        return {
            'sa_freq': self.sa,
            'strings': {
                name: {
                    'freq': s.freq,
                    'graha': s.graha,
                    'jivari': s.jivari,
                    'buffer_ready': s.buffer is not None,
                    'crossfading': s.crossfading,
                }
                for name, s in self.strings.items()
            }
        }


# ── Standalone test ──────────────────────────────────────

if __name__ == '__main__':
    import sys
    sys.path.insert(0, '/home/inahd/atlas_330')

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(message)s",
        datefmt="%H:%M:%S")

    print("Initializing TanpuraEngine...")
    engine = TanpuraEngine(sa_freq=130.81, sample_rate=48000)

    print("Waiting for strings to render...")
    time.sleep(15)

    status = engine.get_status()
    ready = sum(1 for s in status['strings'].values() if s['buffer_ready'])
    if ready < 4:
        print(f"Only {ready}/4 strings ready — waiting longer...")
        time.sleep(15)

    print("Playing — Ctrl+C to stop")

    import sounddevice as sd

    BLOCKSIZE = 4096

    def callback(outdata, frames, time_info, status):
        if status:
            print(f"Status: {status}")
        audio = engine.render(frames)
        outdata[:, 0] = audio
        outdata[:, 1] = audio

    with sd.OutputStream(
        channels=2,
        samplerate=48000,
        blocksize=BLOCKSIZE,
        dtype='float32',
        callback=callback,
    ):
        try:
            while True:
                st = engine.get_status()
                ready = sum(
                    1 for s in st['strings'].values()
                    if s['buffer_ready'])
                print(f"\rStrings ready: {ready}/4   ", end='')
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopped")
