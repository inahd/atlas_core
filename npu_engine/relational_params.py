"""
relational_params.py — Field state → physical instrument parameters.

Not a lookup table. A physics translation layer.

The field state encodes a cosmological moment.
This module translates that moment into the physical parameters
that govern how instruments behave — not what notes they play,
but how the strings themselves vibrate.

Two instruments currently supported:
  tanpura_string()  — modal string model (DAFx-16)
  sympathetic SC    — Karplus-Strong delay line

Both read the same relational field. Their physical behavior
becomes a coherent expression of the same cosmological moment.
"""

import math
from typing import Dict, NamedTuple


class TanpuraPhysics(NamedTuple):
    """Physical parameters for tanpura_string() modal model."""
    k_b: float          # bridge stiffness
    h_b: float          # bridge height offset
    k_c: float          # thread stiffness
    r_c: float          # thread damping
    h_c: float          # thread height
    sigma0: float       # frequency-independent damping
    sigma1: float       # frequency-dependent damping
    M_factor: float     # multiplier on number of modes
    x_out_frac: float   # observation point as fraction of L
    description: str


class SympatheticPhysics(NamedTuple):
    """Physical parameters for sympathetic string SC synths."""
    decay_base: float
    decay_vadi_mult: float
    decay_samvadi_mult: float
    bandwidth_hz: float
    bandwidth_vadi_hz: float
    coupling_strength: float
    coupling_tithi_mult: float
    brightness: float
    damping: float
    description: str


_ELEMENT_DECAY = {
    "earth": {"sigma0": 0.45, "sigma1": 5.5e-3, "desc": "slow sustained"},
    "water": {"sigma0": 0.35, "sigma1": 4.5e-3, "desc": "slow dissolving"},
    "fire":  {"sigma0": 0.85, "sigma1": 8.5e-3, "desc": "quick bright"},
    "air":   {"sigma0": 0.70, "sigma1": 7.5e-3, "desc": "medium airy"},
    "ether": {"sigma0": 0.60, "sigma1": 6.5e-3, "desc": "neutral balanced"},
}

_GUNA_JIVAR = {
    "sattva": {"k_b_mult": 0.85, "k_c_mult": 0.90, "r_c_mult": 1.0,
               "desc": "clear subtle buzz"},
    "rajas":  {"k_b_mult": 1.15, "k_c_mult": 1.20, "r_c_mult": 1.1,
               "desc": "sharp aggressive buzz"},
    "tamas":  {"k_b_mult": 1.30, "k_c_mult": 0.80, "r_c_mult": 0.8,
               "desc": "heavy sustained resonance"},
}

def _tithi_tension(tidx: int) -> float:
    if tidx <= 14:
        return tidx / 14.0
    else:
        return 1.0 - (tidx - 14) / 15.0

def _tithi_coupling(tidx: int) -> float:
    t = _tithi_tension(tidx)
    return 0.4 + 0.6 * t

_NAK_PLUCK = {
    "Krittika": 0.85, "Vishakha": 0.82, "Mula": 0.88,
    "Rohini": 0.90, "Hasta": 0.87, "Shravana": 0.89,
    "Swati": 0.78, "Punarvasu": 0.80, "Shatabhisha": 0.75,
    "Uttara Phalguni": 0.70, "Uttara Ashadha": 0.72,
    "Uttara Bhadrapada": 0.68,
}
_DEFAULT_PLUCK = 0.90

def _arc_modes(arc: float) -> float:
    if arc < 0.15:   return 0.5
    if arc < 0.45:   return 0.75
    if arc < 0.80:   return 1.0
    return 1.3


def derive_tanpura_physics(field_state: dict) -> TanpuraPhysics:
    """Translate field state into tanpura_string() physics parameters."""
    p5      = field_state.get("panchanga", {})
    element = p5.get("element", "ether").lower()
    guna    = p5.get("guna", "sattva").lower()
    nak     = p5.get("nakshatra", "Rohini")
    tidx    = int(p5.get("tidx", 15))
    arc     = tidx / 30.0

    elem_decay = _ELEMENT_DECAY.get(element, _ELEMENT_DECAY["ether"])
    sigma0 = elem_decay["sigma0"]
    sigma1 = elem_decay["sigma1"]

    guna_jivar = _GUNA_JIVAR.get(guna, _GUNA_JIVAR["sattva"])
    k_b = 4.39e8 * guna_jivar["k_b_mult"]
    k_c = 1.2e5  * guna_jivar["k_c_mult"]
    r_c = 1.2    * guna_jivar["r_c_mult"]

    tension = _tithi_tension(tidx)
    h_b = 4.0e-6 * (1.0 + 0.3 * tension)

    x_out_frac = _DEFAULT_PLUCK
    for nak_key, frac in _NAK_PLUCK.items():
        if nak_key.lower() in nak.lower():
            x_out_frac = frac
            break

    M_factor = _arc_modes(arc)

    desc = (
        f"{element}/{guna} · {elem_decay['desc']} · "
        f"{guna_jivar['desc']} · "
        f"tidx={tidx} tension={tension:.2f} · "
        f"nak={nak} x_out={x_out_frac:.2f} · "
        f"arc={arc:.2f} M×{M_factor:.1f}"
    )

    return TanpuraPhysics(
        k_b=k_b, h_b=h_b,
        k_c=k_c, r_c=r_c, h_c=0.0,
        sigma0=sigma0, sigma1=sigma1,
        M_factor=M_factor,
        x_out_frac=x_out_frac,
        description=desc,
    )


def derive_sympathetic_physics(field_state: dict) -> SympatheticPhysics:
    """Translate field state into sympathetic string SC parameters."""
    p5      = field_state.get("panchanga", {})
    element = p5.get("element", "ether").lower()
    guna    = p5.get("guna", "sattva").lower()
    tidx    = int(p5.get("tidx", 15))

    tension  = _tithi_tension(tidx)
    coupling = _tithi_coupling(tidx)

    _ELEM_SYMP_DECAY = {
        "earth": 3.5, "water": 4.0, "fire": 1.5,
        "air": 2.0, "ether": 2.5,
    }
    decay_base = _ELEM_SYMP_DECAY.get(element, 2.5)

    _GUNA_BW = {"sattva": 5.0, "rajas": 9.0, "tamas": 3.0}
    bandwidth_hz = _GUNA_BW.get(guna, 5.0)

    brightness = 0.4 + 0.5 * tension
    damping    = 0.8 - 0.3 * tension

    desc = (
        f"{element}/{guna} · decay={decay_base:.1f}s · "
        f"bw={bandwidth_hz:.1f}Hz · "
        f"coupling={coupling:.2f} · "
        f"brightness={brightness:.2f} (tidx={tidx})"
    )

    return SympatheticPhysics(
        decay_base=decay_base,
        decay_vadi_mult=1.6,
        decay_samvadi_mult=1.3,
        bandwidth_hz=bandwidth_hz,
        bandwidth_vadi_hz=bandwidth_hz * 1.5,
        coupling_strength=0.7,
        coupling_tithi_mult=coupling,
        brightness=brightness,
        damping=damping,
        description=desc,
    )
