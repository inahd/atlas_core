"""
lifecycle_engine.py — Arc phase + formation lifecycle computation.

Wraps TempleGeometry.formation_lifecycle() and adds stability/phase
derivation for the FieldState spine.

Does NOT modify geometry detection logic.
Reads formations and arc_phase, returns lifecycle metadata.
"""

import math
from typing import Any, Dict, List


def compute_lifecycle(arc_phase: float,
                      formations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute lifecycle state from arc_phase and active formations.

    Returns:
        {
          "phase":     "birth" | "formation" | "dissolution" | "pralaya",
          "intensity": 0..1,
          "stability": 0..1,
          "strongest_formation": name or None,
          "formation_count": int,
        }
    """
    arc = max(0.0, min(1.0, float(arc_phase)))

    # Phase boundaries (same as TempleGeometry.formation_lifecycle)
    if arc < 0.25:
        phase = "birth"
        raw_intensity = arc / 0.25
    elif arc < 0.5:
        phase = "formation"
        raw_intensity = 1.0
    elif arc < 0.75:
        phase = "dissolution"
        raw_intensity = 1.0 - (arc - 0.5) / 0.25
    else:
        phase = "pralaya"
        raw_intensity = 0.1 + 0.2 * math.sin((arc - 0.75) / 0.25 * math.pi)

    # Formation modulation
    strongest_name = None
    best_sym = 0.0
    if formations:
        best = max(formations, key=lambda f: f.get("symmetry_score", 0))
        best_sym = best.get("symmetry_score", 0)
        strongest_name = best.get("name")

    intensity = max(0.0, min(1.0, raw_intensity * (0.5 + 0.5 * best_sym) if best_sym else raw_intensity))

    # Stability: mid-cycle = stable, edges = unstable
    if 0.2 <= arc <= 0.6:
        stability = 0.7 + 0.3 * (1.0 - abs(arc - 0.4) / 0.2)
    elif arc < 0.2:
        stability = 0.3 + arc * 2.0
    else:
        stability = max(0.1, 1.0 - (arc - 0.6) * 2.5)

    return {
        "phase": phase,
        "intensity": round(max(0.0, min(1.0, intensity)), 4),
        "stability": round(max(0.0, min(1.0, stability)), 4),
        "strongest_formation": strongest_name,
        "formation_count": len(formations),
    }
