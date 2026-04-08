#!/usr/bin/env python3
"""om.py — tanpura drone, always running

Jīvārī tanpura synthesis based on van Walstijn, Bridges & Mehes (DAFx-16):
  Modal expansion of stiff string with bridge contact + jīvā thread.
  Four strings: Pa(3/2) → sa(2.0) → sa(2.0) → Sa(1.0).

Reads Sa frequency and breath_rate from /brahmanda/state.
Melody, rhythm, percussion → SuperCollider (not here).
"""
import json
import logging
import math
import subprocess
import sys
import threading
import time
from pathlib import Path

import numpy as np

# ── Config ────────────────────────────────────────────────
RATE = 48000
CHANNELS = 2
BLOCKSIZE = 16384
FIELD_PATH = Path("/tmp/field.json")
KERNEL_URL = "http://localhost:5000/field"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("om")

# ── Threaded engines — instantiated in main(), started on first field update ──
_mix = None
_rhythm = None
_sympathetic = None
_phrase = None
_vocal = None

# ── Mix amp receiver — SC sends /atlas/mix/layers back on port 57122 ──────────
# Layer order matches npu_engine/mix/graph_seed_data.py LAYERS list:
#   [0] tanpura  [1] mantra_drone  [2] vocal_pad
#   [3] tabla    [4] konnakol      [5] bol
#   [6] melody   [7] vocal_line    [8] pad  [9] electronic  [10] bija
_mix_amps = [1.0] * 11   # default full — graceful before SC connects
_mix_brightness = 0.0
_mix_reverb = 0.15

def _start_mix_receiver():
    """Start UDP listener for /atlas/mix/layers on port 57122."""
    import socket, threading
    def _listen():
        global _mix_amps, _mix_brightness, _mix_reverb
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.bind(("127.0.0.1", 57122))
            sock.settimeout(1.0)
        except OSError as e:
            log.warning("mix receiver bind failed: %s", e)
            return
        log.info("✓ mix receiver listening on port 57122")
        while True:
            try:
                data, _ = sock.recvfrom(4096)
                # Parse OSC manually — address + typetag + 11 floats
                # OSC string is null-padded to 4-byte boundary
                addr_end = data.index(b"\x00")
                addr = data[:addr_end].decode("utf-8", errors="ignore")
                if addr == "/atlas/mix/layers":
                    # typetag string starts after addr padding
                    pad = (4 - (addr_end + 1) % 4) % 4
                    tt_start = addr_end + 1 + pad
                    tt_end = data.index(b"\x00", tt_start)
                    tt = data[tt_start:tt_end].decode("utf-8", errors="ignore")
                    pad2 = (4 - (tt_end + 1) % 4) % 4
                    data_start = tt_end + 1 + pad2
                    import struct
                    n = min(11, (len(data) - data_start) // 4)
                    amps = list(struct.unpack_from(f">{n}f", data, data_start))
                    _mix_amps[:n] = amps[:n]
                    log.info("mix recv: tanpura=%.2f tabla=%.2f bija=%.2f",
                             _mix_amps[0], _mix_amps[3], _mix_amps[10])
                elif addr == "/atlas/mix/global":
                    pad = (4 - (addr_end + 1) % 4) % 4
                    tt_start = addr_end + 1 + pad
                    tt_end = data.index(b"\x00", tt_start)
                    pad2 = (4 - (tt_end + 1) % 4) % 4
                    data_start = tt_end + 1 + pad2
                    import struct
                    if len(data) - data_start >= 8:
                        vals = struct.unpack_from(">2f", data, data_start)
                        _mix_brightness = vals[0]
                        _mix_reverb     = vals[1]
                    log.info("mix recv: brightness=%.2f reverb=%.2f",
                             _mix_brightness, _mix_reverb)
            except socket.timeout:
                continue
            except Exception:
                continue
    t = threading.Thread(target=_listen, daemon=True)
    t.start()


# ══════════════════════════════════════════════════════════
# TANPURA SYNTHESIS — DAFx-16 modal string model
# ══════════════════════════════════════════════════════════

def tanpura_string(sa_freq, string_ratio, duration, rate=RATE, physics=None,
                   field_params=None):
    """Synthesise one tanpura string — additive harmonics with jīvārī sweep.

    The jīvārī effect: as amplitude decays, higher harmonics emerge then fade
    at different rates. This is the physical mechanism — bridge contact
    transfers energy between modes. Modelled here as per-harmonic decay rates
    scaled by jīvārī intensity.

    Args:
        sa_freq:      Sa frequency in Hz
        string_ratio: frequency ratio to Sa (1.0=Sa, 1.5=Pa, 2.0=sa octave)
        duration:     seconds of audio to generate
        rate:         sample rate
        physics:      TanpuraPhysics from relational_params (optional)
        field_params: dict with guna/element/jivari for field modulation (optional)

    Returns:
        numpy float64 array of length duration*rate, normalized to [-1, 1]
    """
    freq = sa_freq * string_ratio
    N = int(duration * rate)
    t = np.linspace(0, duration, N)

    # Decay time from physics or defaults
    decay = 8.0
    if physics is not None:
        decay = getattr(physics, 'decay_time', None) or 8.0
        # Also accept sigma0 as inverse decay hint
        s0 = getattr(physics, 'sigma0', None)
        if s0 and s0 > 0.1:
            decay = max(4.0, 12.0 / s0)

    # Jīvārī intensity
    jivari = 0.4
    if physics is not None:
        # Derive from bridge stiffness — higher k_b = more buzz
        k_b = getattr(physics, 'k_b', 0)
        if k_b > 0:
            jivari = min(0.9, max(0.1, math.log10(k_b) / 10.0 - 0.7))
    if field_params:
        jivari = field_params.get('jivari', jivari)
        # Element modulation
        element = field_params.get('element', 'ether')
        elem_mod = {'fire': 1.2, 'air': 0.9, 'water': 0.8,
                    'earth': 1.1, 'ether': 1.0}.get(element, 1.0)
        jivari *= elem_mod
        jivari = max(0.05, min(0.9, jivari))
        # Guna modulation on decay
        guna = field_params.get('guna', 'sattva')
        decay *= {'sattva': 1.0, 'rajas': 1.1, 'tamas': 1.3}.get(guna, 1.0)

    env = np.exp(-t / decay)

    # Tanpura overtone series — odd and even harmonics present
    # Relative weights from spectral analysis of real tanpura recordings
    harmonics = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15]
    weights   = [1.0, 0.5, 0.35, 0.22, 0.15, 0.10,
                 0.08, 0.06, 0.04, 0.03, 0.02, 0.01]

    signal = np.zeros(N, dtype=np.float64)
    for h, w in zip(harmonics, weights):
        h_freq = freq * h
        if h_freq > rate / 2:
            break
        # Per-harmonic decay: higher harmonics decay faster,
        # but jīvārī slows their decay (bridge contact sustains them)
        h_decay_rate = 1.0 / decay + h * (1.0 - jivari) * 0.15
        h_env = env * np.exp(-t * h * jivari * 0.3)
        # Random phase per harmonic — prevents artificial coherence
        h_phase = np.random.uniform(0, 2 * math.pi)
        signal += w * h_env * np.sin(2 * math.pi * h_freq * t + h_phase)

    # Normalize to [-0.95, 0.95] — headroom for mixing
    peak = np.max(np.abs(signal))
    if peak > 0.001:
        signal *= 0.95 / peak
    return signal


def tanpura_cycle(sa_freq, duration_per_string, string_ratios=None,
                  loop_gap_ms=150, rate=RATE, physics=None,
                  field_params=None):
    """Full tanpura cycle with configurable tuning and gap.

    Four strings: Pa → Sa → Sa (slightly sharp) → Sa (octave below).
    Detuning on string 3 is constant in cents (3.5¢), scaling in Hz with frequency.
    """
    ratios = string_ratios or [1.5, 2.0, 2.0, 1.0]

    # Apply cents-based detuning to string 3 (second Sa, slightly sharp)
    # 3.5 cents preserves chorus shimmer at any Sa frequency
    detune_cents = 3.5
    detune_ratio = 2 ** (detune_cents / 1200)
    detuned_ratios = list(ratios)
    if len(detuned_ratios) >= 3:
        detuned_ratios[2] = ratios[2] * detune_ratio

    gap = int(rate * loop_gap_ms / 1000.0)
    strings = []
    for ratio in detuned_ratios:
        strings.append(tanpura_string(sa_freq, ratio, duration_per_string, rate,
                                      physics, field_params))
        strings.append(np.zeros(gap))
    mono = np.concatenate(strings)
    # Crossfade loop boundary to eliminate click
    fade_samples = min(int(rate * 0.05), len(mono) // 4)  # 50ms fade
    fade_in  = np.linspace(0, 1, fade_samples)
    fade_out = np.linspace(1, 0, fade_samples)
    mono[:fade_samples]  *= fade_in
    mono[-fade_samples:] *= fade_out
    # Tanpura sits at 0.55 — ground, not ceiling.
    # Leaves headroom for tabla, melody, sympathetic, bija.
    mono *= 0.55
    delay = max(1, int(rate * 0.0006))
    left = mono
    right = np.roll(mono, delay) * 0.95
    return np.column_stack([left, right]).astype(np.float32)


def tanpura_simple(sa_freq, duration, rate=RATE):
    """Simple additive tanpura — 4 strings, harmonic partials, no physics.
    Fallback when modal model sounds bad.
    """
    N = int(duration * rate)
    t = np.arange(N, dtype=np.float64) / rate
    strings = [
        (sa_freq * 1.5, [1.0, 0.6, 0.3, 0.15, 0.08]),   # Pa
        (sa_freq * 2.0, [1.0, 0.5, 0.25, 0.1, 0.05]),    # sa
        (sa_freq * 2.0, [1.0, 0.5, 0.25, 0.1, 0.05]),    # sa
        (sa_freq * 1.0, [1.0, 0.7, 0.4, 0.2, 0.1]),      # Sa
    ]
    beat_dur = 1.5  # seconds between string plucks
    out = np.zeros(N)
    for i, (f0, amps) in enumerate(strings):
        onset = int(i * beat_dur * rate) % N
        for j, amp in enumerate(amps):
            freq = f0 * (j + 1)
            if freq > rate / 2:
                break
            decay = np.exp(-t * (0.3 + j * 0.4))
            wave  = amp * decay * np.sin(2 * np.pi * freq * t)
            out += np.roll(wave, onset) * 0.25
    peak = np.max(np.abs(out))
    if peak > 1e-10:
        out /= peak
    # Crossfade loop boundary
    fade_samples = min(int(rate * 0.05), N // 4)
    out[:fade_samples]  *= np.linspace(0, 1, fade_samples)
    out[-fade_samples:] *= np.linspace(1, 0, fade_samples)
    delay = max(1, int(rate * 0.0006))
    left  = out
    right = np.roll(out, delay) * 0.95
    return np.column_stack([left, right]).astype(np.float32)


# ══════════════════════════════════════════════════════════
# FIELD STATE
# ══════════════════════════════════════════════════════════

class FieldVoice:
    def __init__(self):
        self.sa_hz = 261.63
        self.element = "ether"
        self.breath_rate = 1.0
        self.phase = 0.0
        self.tanpura = TanpuraEngine(sa_freq=self.sa_hz, sample_rate=RATE)
        self._last_sa = 0.0
        self.string_ratios = [1.5, 2.0, 2.0, 1.0]
        self.loop_gap_ms = 150
        self.synth_params = None
        # Tabla state
        self.tabla_samples = {}
        self.tala_bols = []
        self.bpm = 72
        self.beat_phase = 0.0
        self.percussion_active = True
        self.melody_voices = []
        self.melody_phase = 0.0
        # Bija drone state
        self.bija_buffer = None      # pre-rendered bija audio (looping)
        self.bija_pos = 0
        self.bija_id = "om"          # current bija mantra
        self.bija_sa = 0.0           # Sa freq used for current buffer
        # Sarangi — bowed Sa drone
        from npu_engine.sarangi_voice import SarangiString
        self.sarangi = SarangiString(freq=self.sa_hz, rate=RATE)
        # Debug flags — toggle layers on/off without restarting
        self.layer_flags = {
            "tanpura": True,
            "tabla":   True,
            "melody":  True,
            "bija":    True,
            "sarangi": True,
        }
        self._field_state = None
        self._field_params = None


def _read_layer_flags(v):
    """Read /tmp/om_flags.json if it exists and update layer flags."""
    try:
        p = Path("/tmp/om_flags.json")
        if p.exists():
            flags = json.loads(p.read_text())
            v.layer_flags.update(flags)
    except Exception:
        pass


def fetch_brahmanda():
    try:
        import urllib.request
        req = urllib.request.Request(KERNEL_URL, method="GET")
        with urllib.request.urlopen(req, timeout=2) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


def read_field_json():
    try:
        if FIELD_PATH.exists():
            return json.loads(FIELD_PATH.read_text())
    except Exception:
        pass
    return None


_RASA_MAP = {
    "shringara": "shringara", "karuna": "karuna", "vira": "vira",
    "raudra": "raudra", "hasya": "hasya", "bhayanaka": "bhayanaka",
    "bibhatsa": "bibhatsa", "adbhuta": "adbhuta", "shanta": "shanta",
}


def _update_mix(bs: dict, bpm: float, sa_hz: float = 130.81):
    """Feed current field state into MixKernel + SympatheticKernel."""
    if _mix is None and _sympathetic is None:
        return
    p5        = bs.get("panchanga", {})
    element   = p5.get("element", "ether").lower()
    guna      = p5.get("guna", "sattva").lower()
    deity     = p5.get("deity", "")
    raga_def  = bs.get("devi_raga_def") or {}
    rasa_raw  = raga_def.get("rasa", "shanta")
    rasa_key  = rasa_raw.split("·")[0].strip().lower() if rasa_raw else "shanta"
    rasa      = _RASA_MAP.get(rasa_key, "shanta")
    tidx      = p5.get("tidx", 15)
    arc       = max(0.0, min(1.0, tidx / 30.0))
    authority = float(bs.get("alpha", 0.6))
    if _mix is not None:
        try:
            _mix.load_from_field(
                rasa=rasa, arc=arc, mode="gat",
                element=element, deity=deity, guna=guna,
                authority=authority, bpm=bpm,
            )
        except Exception as e:
            log.warning("mix update failed: %s", e)
    if _sympathetic is not None:
        try:
            scale     = raga_def.get("scale", [0, 2, 4, 5, 7, 9, 11])
            vadi      = int(raga_def.get("vadi", 7))
            samvadi   = int(raga_def.get("samvadi", 0))
            raga_name = bs.get("devi_raga", "")
            _sympathetic.load_from_field(
                raga_name=raga_name, scale=scale,
                vadi=vadi, samvadi=samvadi, sa=sa_hz,
            )
        except Exception as e:
            log.warning("sympathetic field update failed: %s", e)
    if _phrase is not None:
        try:
            natal = bs.get("natal") or {}
            _phrase.load_from_field(bs, natal)
            _phrase.update_sa(sa_hz, bpm)
        except Exception as e:
            log.warning("phrase engine update failed: %s", e)


def _render_bija(v: FieldVoice, bs: dict):
    """Render bija drone buffer if bija or Sa changed."""
    try:
        _p5 = bs.get("panchanga", {})
        devi = _p5.get("devi", {})
        # Bija from devi entity or ashtakala mantra_bija
        bija_id = "om"
        if isinstance(devi, dict):
            # Devi name → bija mapping (from Tantraraja tradition)
            devi_name = devi.get("name", "").lower()
            _DEVI_BIJA = {
                "kameshvari": "aim", "kāmeśvarī": "aim",
                "bhagamalini": "hrim", "bhagamālinī": "hrim",
                "nityaklinna": "hrim", "nityāklinā": "hrim",
                "bherunda": "krim", "bheruṇḍā": "krim",
                "vahnivasini": "hum", "vahnivāsinī": "hum",
                "mahavajreshvari": "hrim", "mahāvajreśvarī": "hrim",
                "shivaduti": "shrim", "śivadūtī": "shrim",
                "tvarita": "aim", "tvaritā": "aim",
                "kulasundari": "klim", "kulasundarī": "klim",
                "nitya": "om", "nityā": "om",
                "nilapataka": "hrim", "nīlapatākā": "hrim",
                "vijaya": "aim", "vijayā": "aim",
                "sarvamangala": "shrim", "sarvamaṅgalā": "shrim",
                "jvalamalini": "hum", "jvālamālinī": "hum",
                "chitra": "aim", "citrā": "aim",
            }
            for key, bija in _DEVI_BIJA.items():
                if key in devi_name:
                    bija_id = bija
                    break

        # Only re-render if bija or Sa frequency changed
        sa = v.sa_hz
        if bija_id == v.bija_id and abs(sa - v.bija_sa) < 1.0 and v.bija_buffer is not None:
            return

        from npu_engine.bija_synth import synthesize_bija
        bija_fs = {"panchanga": _p5}
        audio = synthesize_bija(bija_id, bija_fs, duration_s=6.0, sample_rate=RATE)
        # Crossfade loop boundary
        fade = min(int(RATE * 0.1), len(audio) // 4)
        if fade > 0:
            audio[:fade] *= np.linspace(0, 1, fade).astype(np.float32)
            audio[-fade:] *= np.linspace(1, 0, fade).astype(np.float32)

        v.bija_buffer = audio
        v.bija_pos = 0
        v.bija_id = bija_id
        v.bija_sa = sa
        log.info("bija synth: %s · Sa=%.1fHz · len=%.1fs",
                 bija_id, sa, len(audio) / RATE)

    except Exception as e:
        log.warning("bija render failed: %s", e)


def update_voice(v: FieldVoice):
    bs = fetch_brahmanda()
    source = "kernel"
    if bs is None:
        bs = read_field_json()
        source = "file" if bs else "defaults"
    if bs is None:
        return

    # Compute synth params from field state
    from npu_engine.relational_synth import compute_synth_params
    params = compute_synth_params(bs)
    v.synth_params = params

    # Tanpura from relational field — raga/nakshatra/tithi/graha
    from npu_engine.tanpura_field import derive_tanpura_params
    tp = derive_tanpura_params(bs)
    v.sa_hz        = tp["sa_hz"]
    v.element      = tp["element"]
    v.string_ratios = tp["string_ratios"]
    v.loop_gap_ms  = tp["cycle_gap_ms"]
    v.tanpura_field = tp
    v._field_state = bs
    # Extract field params for tanpura physics modulation
    _p5 = bs.get("panchanga", {})
    v._field_params = {
        'guna': _p5.get("guna", "sattva").lower(),
        'element': _p5.get("element", "ether").lower(),
        'nakshatra': _p5.get("nakshatra", ""),
        'graha': _p5.get("nak_lord", ""),
    }
    log.info("tanpura field: %s", tp["tuning_name"])

    v.breath_rate = params["master"]["breath_rate"]

    rh = params["rhythm"]
    v.tala_bols = rh.get("tala_bols", [])
    v.bpm = rh.get("bpm", 72)
    v.percussion_active = rh.get("active", True)

    v.melody_voices = params.get("voices", [])

    # Update TanpuraEngine — non-blocking, re-renders only if freq changed
    v.tanpura.update_field({
        'sa_freq': v.sa_hz,
        'nak_lord': _p5.get("nak_lord", "surya"),
    })
    v._last_sa = v.sa_hz

    # Update sarangi Sa frequency
    v.sarangi.set_freq(v.sa_hz)
    log.info("sarangi: bowing Sa=%.1fHz", v.sa_hz)

    mu = params.get("mudra", {})
    log.info("synth params: %s · %d voices · %s · %d bols · mudrā: %s (%s)",
             tp.get("tuning_name", tp.get("tuning", "?")), len(params.get("voices", [])), rh.get("percussion_type", "tabla"),
             len(v.tala_bols), mu.get("primary", "?"), mu.get("quality", "?"))

    # Bija drone — derive from devi/ashtakala, render if changed
    _render_bija(v, bs)

    # Trajectory — temporal arc modulates tempo and tabla
    try:
        from npu_engine.field.trajectory_engine import derive_trajectory
        traj = derive_trajectory(bs)
        traj_music = traj.get("musical_implication", {})
        tempo_mult = float(traj_music.get("tempo_multiplier", 1.0))
        v.bpm = round(v.bpm * tempo_mult, 1)
        if not traj_music.get("tabla_active", True):
            v.percussion_active = False
        log.info("trajectory: %s · tempo×%.2f · tabla=%s",
                 traj_music.get("energy_arc", ""),
                 tempo_mult, v.percussion_active)
    except Exception as e:
        log.warning("trajectory failed: %s", e)

    _update_mix(bs, v.bpm, v.sa_hz)
    if _mix is not None and not _mix.playing:
        _mix.start()
        _start_mix_receiver()
        log.info("✦ MixKernel started → OSC 57121 out / 57122 in")
    if _sympathetic is not None and not _sympathetic.playing:
        _sympathetic.start()
        log.info("✦ SympatheticKernel started → OSC 57121")
    if _phrase is not None and not _phrase.playing:
        _phrase.start()
        log.info("✦ PhraseEngine started — %s / %s",
                 _phrase._raga_name, _phrase._perf_mode)

    # RhythmKernel — update and start
    if _rhythm is not None:
        try:
            p5 = bs.get("panchanga", {})
            rasa_raw = (bs.get("devi_raga_def") or {}).get("rasa", "shanta")
            rasa_key = rasa_raw.split("·")[0].strip().lower() if rasa_raw else "shanta"
            rasa = _RASA_MAP.get(rasa_key, "shanta")
            tidx = p5.get("tidx", 15)
            arc = max(0.0, min(1.0, tidx / 30.0))
            _rhythm.load_from_field(
                tala_name=rh.get("tradition", "Adi"),
                bpm=v.bpm, mode="gat", rasa=rasa, arc=arc,
            )
        except Exception as e:
            log.warning("rhythm update failed: %s", e)
        if not _rhythm.playing:
            _rhythm.start()
            log.info("✦ RhythmKernel started → OSC 57121")

    # VocalKernel — bija phonemes at low amplitude
    if _vocal is not None:
        try:
            p5 = bs.get("panchanga", {})
            nak_name = p5.get("nakshatra", "Rohini")
            raga_def = bs.get("devi_raga_def") or {}
            nak_entry = {
                "nakshatra": nak_name,
                "raga": raga_def.get("raga_name", bs.get("devi_raga", "Yaman")),
                "tala": rh.get("tradition", "Adi") if rh else "Adi",
                "guna": p5.get("guna", "sattva"),
                "deity": p5.get("nak_lord", ""),
                "bija": "om",
            }
            _vocal.sa = v.sa_hz
            _vocal.bpm = v.bpm
            _vocal.load_from_field(bs, nak_entry)
        except Exception as e:
            log.warning("vocal update failed: %s", e)
        if not _vocal.playing:
            _vocal.level = 0.08  # low amplitude — bija phonemes, not full voice
            _vocal.start()
            log.info("✦ VocalKernel started → OSC 57121 (bija, amp=0.08)")


def write_state(v: FieldVoice):
    try:
        state = {
            "source": "om.py",
            "sa_hz": v.sa_hz,
            "element": v.element,
            "breath_rate": v.breath_rate,
            "phase": round(v.phase, 2),
            "timestamp": time.time(),
        }
        existing = read_field_json()
        if isinstance(existing, dict):
            existing["om"] = state
        else:
            existing = {"om": state}
        FIELD_PATH.write_text(json.dumps(existing, indent=2))
    except Exception:
        pass


# ══════════════════════════════════════════════════════════
# AUDIO — double-buffer tanpura renderer
# ══════════════════════════════════════════════════════════

from npu_engine.tanpura_engine import TanpuraEngine


def _get_mix_amp(layer_name: str, fallback: float = 1.0) -> float:
    """Read layer amp directly from MixKernel — no OSC roundtrip."""
    if _mix is None:
        return fallback
    sent = _mix._history._last_sent
    if not sent:
        return fallback
    return float(sent.get(layer_name, fallback))


def fill_buffer(buf, frames, v: FieldVoice):
    _read_layer_flags(v)

    # ── Mix layer amplitudes from sclang relay (57122) ──
    # [0]tanpura [1]mantra_drone [2]vocal_pad [3]tabla [4]konnakol
    # [5]bol [6]melody [7]vocal_line [8]pad [9]electronic [10]bija
    mx = _mix_amps  # live values from sclang relay

    # Tanpura — four independent strings via TanpuraEngine
    if v.layer_flags["tanpura"]:
        tanpura_audio = v.tanpura.render(frames) * mx[0]
        buf[:frames, 0] = tanpura_audio
        buf[:frames, 1] = tanpura_audio
    else:
        buf[:] = 0

    # Bija drone — looping formant hum under tanpura (vectorized)
    if v.layer_flags.get("bija", True) and v.bija_buffer is not None:
        bija_gain = 0.06 * mx[10]
        bija_len = len(v.bija_buffer)
        indices = (np.arange(frames) + v.bija_pos) % bija_len
        bija_samples = v.bija_buffer[indices] * bija_gain
        buf[:frames, 0] += bija_samples
        buf[:frames, 1] += bija_samples
        v.bija_pos = (v.bija_pos + frames) % bija_len

    # Sarangi — bowed Sa drone sitting just above tanpura (cached loop)
    if v.layer_flags.get("sarangi", True):
        sarangi_audio = v.sarangi.render_looped(frames, amp=0.15 * mx[6])
        buf[:frames, 0] += sarangi_audio
        buf[:frames, 1] += sarangi_audio

    # Excite sympathetic strings from tanpura
    if _sympathetic is not None and _sympathetic.playing:
        for ratio in v.string_ratios:
            _sympathetic.excite_melody(v.sa_hz * ratio, amp=0.3)

    # Tabla: mix sample-based percussion
    if v.layer_flags["tabla"] and v.percussion_active and v.tala_bols and v.tabla_samples and mx[3] > 0.01:
        from npu_engine.tabla_sampler import render_tala_beat
        beat_dur = 60.0 / max(v.bpm, 30)
        beat_samples = int(RATE * beat_dur)

        # How many samples into the current beat are we?
        beat_frac = v.beat_phase - int(v.beat_phase)
        beat_offset = int(beat_frac * beat_samples)
        beat_idx = int(v.beat_phase) % max(len(v.tala_bols), 1)

        # Render one beat, extract the portion that overlaps this buffer
        bol_audio = render_tala_beat(v.tabla_samples, v.tala_bols, beat_idx, v.bpm, RATE)
        mix_len = min(frames, len(bol_audio) - beat_offset)
        if mix_len > 0 and beat_offset < len(bol_audio):
            tabla_mono = bol_audio[beat_offset:beat_offset + mix_len]
            tabla_gain = 0.35 * mx[3]
            buf[:mix_len, 0] += tabla_mono * tabla_gain
            buf[:mix_len, 1] += tabla_mono * tabla_gain

        v.beat_phase += frames / RATE / beat_dur
    elif v.tala_bols:
        # Advance beat phase even if muted
        beat_dur = 60.0 / max(v.bpm, 30)
        v.beat_phase += frames / RATE / beat_dur

    # Live melody from PhraseEngine
    if _phrase is not None and v.layer_flags.get("melody", True):
        note = _phrase.next_note()
        if note is not None and note.freq_hz > 0:
            t = np.arange(frames, dtype=np.float64) / RATE + v.melody_phase
            # Short attack/decay envelope
            env = np.ones(frames, dtype=np.float64)
            attack = min(int(RATE * 0.02), frames // 4)
            decay  = min(int(RATE * 0.05), frames // 4)
            if attack > 0:
                env[:attack] = np.linspace(0, 1, attack)
            if decay > 0:
                env[-decay:] = np.linspace(1, 0, decay)
            melody = note.amplitude * env * np.sin(2 * np.pi * note.freq_hz * t)
            melody_amp = _get_mix_amp("melody", 0.5)
            buf[:, 0] += (melody * melody_amp * 0.4).astype(np.float32)
            buf[:, 1] += (melody * melody_amp * 0.4).astype(np.float32)
            # Excite sympathetic strings
            if _sympathetic is not None and _sympathetic.playing:
                _sympathetic.excite_melody(note.freq_hz, note.amplitude)
        v.melody_phase += frames / RATE

    # Breath modulation
    t = np.arange(frames, dtype=np.float64) / RATE + v.phase
    breath_freq = 0.08 + 0.12 * v.breath_rate
    breath = (0.7 + 0.3 * v.breath_rate) + (0.15 * np.sin(2.0 * np.pi * breath_freq * t))
    buf[:, 0] *= breath.astype(np.float32)
    buf[:, 1] *= breath.astype(np.float32)

    # Soft clip
    buf[:] = np.tanh(buf * 1.5) * 0.65
    v.phase += frames / RATE


# ══════════════════════════════════════════════════════════
# OUTPUT BACKENDS
# ══════════════════════════════════════════════════════════

def run_sounddevice(v: FieldVoice):
    return False  # skip — pw-cat is the output path on this system
    try:
        import sounddevice as sd
    except (ImportError, OSError) as e:
        log.info("sounddevice unavailable: %s", e)
        return False

    # Field updates in background thread — never on audio callback
    def _field_loop():
        while True:
            time.sleep(30)
            try:
                update_voice(v)
            except Exception as e:
                log.warning("field update: %s", e)

    threading.Thread(target=_field_loop, daemon=True).start()

    last_write = 0.0

    def callback(outdata, frames, time_info, status):
        nonlocal last_write
        fill_buffer(outdata, frames, v)
        now = time.time()
        if now - last_write > 4:
            write_state(v)
            last_write = now

    # Discover output device by name — MOTU M2 via PipeWire
    _device = None
    _names = ('m series', 'motu', 'pipewire', 'pulse')
    try:
        for i, d in enumerate(sd.query_devices()):
            if d['max_output_channels'] >= 2 and any(n in d['name'].lower() for n in _names):
                _device = i
                log.info("✓ output device [%d]: %s (%d ch)", i, d['name'], d['max_output_channels'])
                break
    except Exception as _e:
        log.warning("device query failed: %s", _e)
    if _device is None:
        _device = sd.default.device[1]
        try:
            _dinfo = sd.query_devices(_device)
            log.info("✓ default output [%d]: %s", _device, _dinfo['name'])
        except Exception:
            log.info("✓ using system default output [%s]", _device)

    try:
        with sd.OutputStream(
            samplerate=RATE, channels=CHANNELS, dtype="float32",
            blocksize=BLOCKSIZE, callback=callback,
            device=_device,
        ):
            log.info("✦ om sounding via sounddevice (device=%d)", _device)
            while True:
                time.sleep(1)
    except Exception as e:
        log.warning("sounddevice error: %s", e)
        return False
    return True


def run_pwcat(v: FieldVoice):
    # Field updates in background thread — never on audio write loop
    def _field_loop():
        while True:
            time.sleep(30)
            try:
                update_voice(v)
            except Exception as e:
                log.warning("field update: %s", e)

    threading.Thread(target=_field_loop, daemon=True).start()

    last_write = 0.0
    chunk_frames = RATE

    proc = subprocess.Popen(
        ["pw-cat", "--playback", "-",
         "--rate", str(RATE), "--channels", str(CHANNELS), "--format", "f32",
         "--target", "alsa_output.usb-MOTU_M2_M20000063536-00.analog-stereo"],
        stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
    )
    log.info("✦ om sounding via pw-cat → MOTU M2")

    try:
        buf = np.zeros((chunk_frames, CHANNELS), dtype=np.float32)
        while True:
            fill_buffer(buf, chunk_frames, v)
            proc.stdin.write(buf.tobytes())
            proc.stdin.flush()
            now = time.time()
            if now - last_write > 4:
                write_state(v)
                last_write = now
            if proc.poll() is not None:
                raise RuntimeError("pw-cat exited")
    except (BrokenPipeError, RuntimeError, OSError) as e:
        log.warning("pw-cat ended: %s", e)
    finally:
        try:
            proc.kill()
        except Exception:
            pass


# ══════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════

def main():
    global _mix, _rhythm, _sympathetic, _phrase, _vocal
    log.info("om.py — tanpura drone + tabla")
    v = FieldVoice()

    # Load tabla samples once
    from npu_engine.tabla_sampler import load_samples
    sample_dir = Path(__file__).resolve().parent
    while sample_dir.name != "atlas_330" and sample_dir.parent != sample_dir:
        sample_dir = sample_dir.parent
    sample_dir = sample_dir / "samples" / "tabla"
    v.tabla_samples = load_samples(str(sample_dir))
    log.info("✓ tabla sampler: %d samples loaded", len(v.tabla_samples))

    # ── Instantiate threaded kernels ─────────────────────────
    try:
        from npu_engine.mix.mix_kernel import MixKernel
        _mix = MixKernel(bpm=72, osc_port=57121)
        log.info("✓ MixKernel loaded")
    except Exception as e:
        log.warning("MixKernel unavailable: %s", e)

    try:
        from npu_engine.rhythm.rhythm_kernel import RhythmKernel
        _rhythm = RhythmKernel(bpm=72, osc_port=57121)
        log.info("✓ RhythmKernel loaded")
    except Exception as e:
        log.warning("RhythmKernel unavailable: %s", e)

    try:
        from npu_engine.sympathetic.sympathetic_kernel import SympatheticKernel
        _sympathetic = SympatheticKernel(sa_freq=v.sa_hz, osc_port=57121)
        log.info("✓ SympatheticKernel loaded")
    except Exception as e:
        log.warning("SympatheticKernel unavailable: %s", e)

    try:
        from npu_engine.phrase_engine import PhraseEngine
        _phrase = PhraseEngine(sa_hz=v.sa_hz, bpm=72)
        log.info("✓ PhraseEngine loaded")
    except Exception as e:
        log.warning("PhraseEngine unavailable: %s", e)

    try:
        from npu_engine.vocal.vocal_kernel import VocalKernel
        _vocal = VocalKernel(sa_freq=v.sa_hz, osc_port=57121)
        log.info("✓ VocalKernel loaded")
    except Exception as e:
        log.warning("VocalKernel unavailable: %s", e)

    # Start mix receiver unconditionally — sclang (atlas_mix.scd) echoes
    # MixKernel layer amps here even if MixKernel itself isn't loaded
    _start_mix_receiver()

    update_voice(v)

    log.info("using pw-cat \u2192 PipeWire \u2192 MOTU")

    while True:
        log.info("sa=%.1fHz · %s · breath=%.1f", v.sa_hz, v.element, v.breath_rate)
        if run_sounddevice(v):
            log.info("retrying in 3s…")
            time.sleep(3)
            continue
        log.info("sounddevice failed — falling back to pw-cat")
        try:
            run_pwcat(v)
        except Exception as e:
            log.warning("audio error: %s", e)
        log.info("retrying in 3s…")
        time.sleep(3)


if __name__ == "__main__":
    main()
