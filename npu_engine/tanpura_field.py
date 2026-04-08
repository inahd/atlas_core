"""
tanpura_field.py — Derives tanpura tuning from full field state.

Not a lookup table. A relational field.

The tanpura is the harmonic universe the raga inhabits.
Every parameter derives from the cosmological moment:
  - Sa frequency: raga prahar register, never below 110Hz
  - String cycle: raga vadi/samvadi determine which 4 strings
  - Shruti offsets: nakshatra's shruti position (22-shruti system)
  - Partial emphasis: graha swara determines bright harmonics
  - Cycle timing: tithi phase × tala density
"""

import math
from typing import Dict, List, Tuple

# ── Just intonation ratios for the 22 shrutis ──────────────────────────────
# Each swara has multiple shruti positions (comma variants)
# Format: swara_name → [ratio_low, ratio_mid, ratio_high]
SHRUTI_RATIOS = {
    "Sa":  [1.0],
    "re":  [256/243, 16/15],           # komal Re — 2 shrutis
    "Re":  [10/9,    9/8],             # shuddha Re — 2 shrutis
    "ga":  [32/27,   6/5],             # komal Ga — 2 shrutis
    "Ga":  [5/4,     81/64],           # shuddha Ga — 2 shrutis
    "ma":  [4/3,     27/20],           # shuddha ma — 2 shrutis
    "Ma":  [45/32,   64/45],           # tivra Ma — 2 shrutis
    "Pa":  [3/2],                      # Pa — 1 shruti (fixed)
    "dha": [128/81,  8/5],             # komal Dha — 2 shrutis
    "Dha": [5/3,     27/16],           # shuddha Dha — 2 shrutis
    "ni":  [16/9,    9/5],             # komal Ni — 2 shrutis
    "Ni":  [15/8,    243/128],         # shuddha Ni — 2 shrutis
}

# Semitone → swara name (mirrors kernel.py _SEMI_TO_SWARA)
SEMI_TO_SWARA = {
    0: "Sa", 1: "re", 2: "Re", 3: "ga", 4: "Ga", 5: "ma",
    6: "Ma", 7: "Pa", 8: "dha", 9: "Dha", 10: "ni", 11: "Ni",
}

# ── Prahar → base Sa register ──────────────────────────────────────────────
# Always in playable tanpura range (110-220Hz)
# Motivated by raga time theory: morning = lower, evening = higher
PRAHAR_SA = {
    1: 146.83,   # evening — D3, slightly bright
    2: 130.81,   # night — C3, settled
    3: 130.81,   # late night — C3
    4: 123.47,   # pre-dawn — B2, lowest acceptable
    5: 130.81,   # dawn — C3, opening
    6: 138.59,   # late morning — C#3, ascending
    7: 146.83,   # afternoon — D3
    8: 130.81,   # conclusion — C3, returning
}

# ── Element → Sa semitone offset within prahar register ───────────────────
# Element adds tonal color, not octave transposition
ELEMENT_OFFSET_SEMI = {
    "fire":   2,   # up a whole tone — bright, ascending
    "earth":  0,   # no offset — stable, grounded
    "water": -2,   # down a whole tone — fluid, descending
    "air":    1,   # up a semitone — light
    "ether":  0,   # neutral
}

# ── Graha → swara emphasis (which partial to brighten) ────────────────────
GRAHA_SWARA = {
    "Sūrya":    "Pa",    # Sun — Pa, the fifth, power
    "Surya":    "Pa",
    "Candra":   "ma",    # Moon — ma, the fourth, fluid
    "Chandra":  "ma",
    "Maṅgala":  "Re",    # Mars — Re, second, sharp
    "Mangala":  "Re",
    "Budha":    "Ga",    # Mercury — Ga, third, intellect
    "Guru":     "Dha",   # Jupiter — Dha, sixth, grace
    "Śukra":    "Ni",    # Venus — Ni, seventh, beauty
    "Shukra":   "Ni",
    "Śani":     "Sa",    # Saturn — Sa, root, depth
    "Shani":    "Sa",
    "Rāhu":     "Ma",    # Rahu — tivra Ma, transgression
    "Rahu":     "Ma",
    "Ketu":     "re",    # Ketu — komal re, dissolution
}

# ── Nakshatra → shruti preference (which comma variant) ───────────────────
# 0 = lower shruti, 1 = higher shruti where two exist
NAKSHATRA_SHRUTI = {
    "Ashwini": 1, "Bharani": 0, "Krittika": 1, "Rohini": 1,
    "Mrigashira": 0, "Ardra": 0, "Punarvasu": 1, "Pushya": 0,
    "Ashlesha": 0, "Magha": 0, "Purva Phalguni": 1, "Uttara Phalguni": 1,
    "Hasta": 0, "Chitra": 1, "Swati": 1, "Vishakha": 1,
    "Anuradha": 0, "Jyeshtha": 0, "Mula": 0, "Purva Ashadha": 1,
    "Uttara Ashadha": 1, "Shravana": 0, "Dhanishtha": 1, "Shatabhisha": 0,
    "Purva Bhadrapada": 0, "Uttara Bhadrapada": 0, "Revati": 1,
}


def tithi_string_weights(tidx: int) -> List[float]:
    """Return amplitude weights for [string1, sa, sa, Sa] from tithi.
    tidx: 0-29 (tithi index)
    """
    if tidx == 0 or tidx == 29:
        # Amavasya — Sa dominant, others present but quiet
        return [0.4, 0.5, 0.5, 1.0]
    elif tidx == 14:
        # Purnima — full consonance
        return [1.0, 1.0, 1.0, 1.0]
    elif tidx < 14:
        # Shukla paksha — building
        phase = tidx / 14.0
        return [
            0.4 + 0.6 * phase,
            0.5 + 0.5 * phase,
            0.5 + 0.5 * phase,
            1.0,
        ]
    else:
        # Krishna paksha — dissolving
        phase = (tidx - 14) / 15.0
        return [
            1.0 - 0.6 * phase,
            1.0 - 0.5 * phase,
            1.0 - 0.5 * phase,
            1.0,
        ]


def derive_tanpura_params(field_state: dict) -> dict:
    """Derive full tanpura parameters from field state.

    Returns dict with:
        sa_hz: float — Sa frequency in Hz (always 110-220)
        string_ratios: list[float] — 4 string ratios to Sa
        string_weights: list[float] — amplitude of each string
        shruti_offsets: list[float] — microtonal ratio adjustments
        bright_partial: int — which harmonic to emphasize (from graha)
        cycle_gap_ms: int — gap between string plucks in ms
        loop_duration: float — seconds per full cycle
        tuning_name: str — human readable description
    """
    p5       = field_state.get("panchanga", {})
    raga_def = field_state.get("devi_raga_def") or {}
    raga_name = field_state.get("devi_raga", "")

    element   = p5.get("element", "ether").lower()
    guna      = p5.get("guna", "sattva").lower()
    nakshatra = p5.get("nakshatra", "")
    nak_lord  = p5.get("nak_lord", "")
    tidx      = int(p5.get("tidx", 15))

    # ── 1. Sa frequency from prahar + element ──────────────────────────────
    prahar   = int(raga_def.get("prahar", 0) or 0)
    if prahar == 0:
        from datetime import datetime
        h = datetime.now().hour
        prahar = max(1, min(8, (h % 24) // 3 + 1))
    base_sa  = PRAHAR_SA.get(prahar, 130.81)
    offset   = ELEMENT_OFFSET_SEMI.get(element, 0)
    sa_hz    = base_sa * (2 ** (offset / 12.0))

    # Ensure playable range
    while sa_hz < 110.0:
        sa_hz *= 2.0
    while sa_hz > 220.0:
        sa_hz /= 2.0

    # ── 2. String ratios from raga vadi/samvadi ─────────────────────────────
    vadi    = raga_def.get("vadi", 7)     # default Pa
    samvadi = raga_def.get("samvadi", 0)  # default Sa

    vadi_name    = SEMI_TO_SWARA.get(int(vadi) if vadi is not None else 7, "Pa")
    samvadi_name = SEMI_TO_SWARA.get(int(samvadi) if samvadi is not None else 0, "Sa")

    # Get just intonation ratio for vadi
    vadi_ratios    = SHRUTI_RATIOS.get(vadi_name, [1.5])
    samvadi_ratios = SHRUTI_RATIOS.get(samvadi_name, [1.0])

    shruti_pref = NAKSHATRA_SHRUTI.get(nakshatra, 0)
    vadi_ratio    = vadi_ratios[min(shruti_pref, len(vadi_ratios) - 1)]
    samvadi_ratio = samvadi_ratios[min(shruti_pref, len(samvadi_ratios) - 1)]

    # Four strings: vadi → sa(octave) → sa(octave) → Sa
    if abs(vadi_ratio - 1.5) < 0.05:
        string_ratios = [1.5, 2.0, 2.0, 1.0]  # standard Pa-sa-sa-Sa
    else:
        sr2 = samvadi_ratio * 2.0 if samvadi_ratio < 1.5 else samvadi_ratio
        string_ratios = [vadi_ratio, 2.0, sr2, 1.0]

    # ── 3. Shruti microtonal offsets for each string ────────────────────────
    shruti_offsets = []
    for ratio in string_ratios:
        nearest = ratio
        for swara, ratios in SHRUTI_RATIOS.items():
            for r in ratios:
                if abs(r - ratio) < abs(nearest - ratio):
                    nearest = r
        shruti_offsets.append(nearest / ratio if ratio > 0 else 1.0)

    # ── 4. String weights from tithi ───────────────────────────────────────
    string_weights = tithi_string_weights(tidx)

    # ── 5. Graha → bright partial ───────────────────────────────────────────
    graha_swara  = GRAHA_SWARA.get(nak_lord, "Pa")
    swara_ratios = SHRUTI_RATIOS.get(graha_swara, [1.5])
    graha_ratio  = swara_ratios[0]
    bright_partial = 1
    for n in range(1, 9):
        if abs((n / 1.0) * graha_ratio % 1.0) < 0.1:
            bright_partial = n
            break

    # ── 6. Cycle timing from guna + tithi ──────────────────────────────────
    guna_gap = {"sattva": 1400, "rajas": 1000, "tamas": 1800}.get(guna, 1400)
    tithi_mod = 1.0 - 0.15 * math.sin(math.pi * tidx / 15.0)
    cycle_gap_ms = int(guna_gap * tithi_mod)

    loop_duration = (len(string_ratios) * cycle_gap_ms / 1000.0) + 2.0

    # ── 7. Human readable description ──────────────────────────────────────
    tuning_name = (
        f"{vadi_name}-sa-sa-Sa · "
        f"{raga_name or 'field'} · "
        f"Sa={sa_hz:.1f}Hz · "
        f"nakshatra={nakshatra} · "
        f"tidx={tidx}"
    )

    return {
        "sa_hz":          sa_hz,
        "string_ratios":  string_ratios,
        "string_weights": string_weights,
        "shruti_offsets": shruti_offsets,
        "bright_partial": bright_partial,
        "cycle_gap_ms":   cycle_gap_ms,
        "loop_duration":  loop_duration,
        "tuning_name":    tuning_name,
        "vadi":           vadi_name,
        "samvadi":        samvadi_name,
        "graha_swara":    graha_swara,
        "element":        element,
        "prahar":         prahar,
    }
