"""
temple_geometry.py — NPU Cluster Component
============================================
Temple formation detection engine.
Not visualization — geometry computation.
The render reads from this.

Detects coherence clusters that match sacred geometric patterns.
Assigns entities to Vāstu pada positions.
Tracks formation lifecycle and Pralāya triggers.
"""

import math
from typing import Dict, List, Optional, Tuple, Any


class TempleGeometry:
    """Sacred geometry detection from coherence field data."""

    FORMATIONS = {
        4:  "chatushkona",        # square
        6:  "shatkona",           # hexagon (Śiva-Śakti)
        8:  "ashtadala",          # 8-petal lotus
        9:  "navagraha",          # 9 planetary positions
        16: "shodasha",           # 16-petal (Śrī Yantra inner)
        27: "nakshatra_mandala",  # full nakshatra wheel
        64: "vastu_pada",         # 8×8 Vāstu grid
    }

    VASTU_DIRECTIONS = {
        "brahma":  (0.5, 0.5),   # center
        "ishana":  (0.0, 1.0),   # NE
        "indra":   (0.5, 1.0),   # E
        "agni":    (1.0, 1.0),   # SE
        "yama":    (1.0, 0.5),   # S
        "nirrti":  (1.0, 0.0),   # SW
        "varuna":  (0.5, 0.0),   # W
        "vayu":    (0.0, 0.0),   # NW
        "kubera":  (0.0, 0.5),   # N
    }

    # Element → directional affinity
    _ELEM_DIR = {
        "fire":  "agni",
        "water": "varuna",
        "air":   "vayu",
        "earth": "kubera",
        "ether": "brahma",
    }

    def detect_formations(self, entities: List[Dict]) -> List[Dict]:
        """Find coherence clusters that match sacred geometric patterns.

        Args:
            entities: list of dicts with entity_id, score, theta, phi

        Returns list of formation dicts:
            {name, count, members, symmetry_score, attestation}
        """
        if not entities:
            return []

        formations = []
        n = len(entities)

        for count, name in self.FORMATIONS.items():
            if n < count:
                continue
            top = entities[:count]
            sym = self._symmetry_score(top, count)
            if sym > 0.3:
                formations.append({
                    "name": name,
                    "count": count,
                    "symmetry_score": round(sym, 3),
                    "members": [e["entity_id"] for e in top],
                    "attestation": "SYNTHESIS",
                })

        return formations

    def _symmetry_score(self, entities: List[Dict], expected: int) -> float:
        """Score how evenly entities are distributed around the θ circle.

        Perfect symmetry = 1.0 (entities at equal angular intervals).
        Random distribution ≈ 0.3-0.5.
        """
        if len(entities) < 2:
            return 0.0

        thetas = sorted(e.get("theta", 0) for e in entities)
        n = len(thetas)
        ideal_gap = 2 * math.pi / n

        # Compute angular gaps
        gaps = []
        for i in range(n):
            gap = (thetas[(i + 1) % n] - thetas[i]) % (2 * math.pi)
            gaps.append(gap)

        if not gaps:
            return 0.0

        # Variance of gaps relative to ideal
        variance = sum((g - ideal_gap) ** 2 for g in gaps) / n
        max_var = ideal_gap ** 2  # worst case
        if max_var == 0:
            return 1.0

        return max(0, 1.0 - variance / max_var)

    def vastu_grid(self, entities: List[Dict]) -> Dict[str, Tuple[float, float, str]]:
        """Assign entities to 64-pada Vāstu positions.

        High coherence → center (Brahma).
        Directional affinity from element → perimeter deity.

        Returns: {entity_id: (x, y, pada_deity)}
        """
        grid = {}
        sorted_ents = sorted(entities, key=lambda e: e.get("score", 0), reverse=True)

        for i, ent in enumerate(sorted_ents[:64]):
            eid = ent.get("entity_id", f"entity_{i}")
            score = ent.get("score", 0)
            element = ent.get("element", "ether")

            if i < 4 and score > 0.9:
                # Highest coherence → Brahmasthāna
                deity = "brahma"
                offset = i * 0.02
                x, y = 0.5 + offset, 0.5 + offset
            else:
                # Distribute by element affinity
                deity = self._ELEM_DIR.get(element, "brahma")
                base_x, base_y = self.VASTU_DIRECTIONS.get(deity, (0.5, 0.5))
                # Spread within zone
                row = (i - 4) // 8
                col = (i - 4) % 8
                x = base_x + (col - 4) * 0.06
                y = base_y + (row - 4) * 0.06
                x = max(0, min(1, x))
                y = max(0, min(1, y))

            grid[eid] = (round(x, 3), round(y, 3), deity)

        return grid

    def formation_lifecycle(self, formation: Dict,
                            arc_phase: float) -> Dict[str, Any]:
        """Determine lifecycle phase of a formation.

        Birth → Formation → Dissolution → Pralāya

        Args:
            formation: dict from detect_formations
            arc_phase: tithi lunar cycle position (0-1)

        Returns: {phase, intensity}
        """
        sym = formation.get("symmetry_score", 0)

        # Arc phase drives lifecycle
        # 0.0-0.25: birth (waxing)
        # 0.25-0.5: formation (full)
        # 0.5-0.75: dissolution (waning)
        # 0.75-1.0: pralāya (dark)
        if arc_phase < 0.25:
            phase = "birth"
            intensity = arc_phase / 0.25
        elif arc_phase < 0.5:
            phase = "formation"
            intensity = 1.0
        elif arc_phase < 0.75:
            phase = "dissolution"
            intensity = 1.0 - (arc_phase - 0.5) / 0.25
        else:
            phase = "pralaya"
            intensity = 0.1 + 0.2 * math.sin((arc_phase - 0.75) / 0.25 * math.pi)

        # Symmetry modulates intensity
        intensity *= sym

        return {
            "phase": phase,
            "intensity": round(max(0, min(1, intensity)), 3),
            "symmetry": round(sym, 3),
            "arc_phase": round(arc_phase, 3),
            "attestation": "SYNTHESIS",
        }

    def pralaya_trigger(self, old_field: Optional[Dict],
                        new_field: Dict) -> bool:
        """Detect if a Pralāya (field reset) should occur.

        True when:
        - nakshatra changes
        - tithi crosses Pūrṇimā (15) or Amāvāsyā (30)
        - arc_phase resets (new lunar cycle)
        """
        if old_field is None:
            return False

        old_p = old_field.get("panchanga", {})
        new_p = new_field.get("panchanga", {})

        # Nakshatra change
        if old_p.get("nakshatra") != new_p.get("nakshatra"):
            return True

        # Tithi boundary crossing (Pūrṇimā = tidx 14, Amāvāsyā = tidx 29)
        old_tidx = old_p.get("tidx", 0)
        new_tidx = new_p.get("tidx", 0)
        if old_tidx != new_tidx:
            if new_tidx in (14, 29) or old_tidx in (14, 29):
                return True

        return False
