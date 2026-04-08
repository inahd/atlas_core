"""
swara_engine.py — The bridge between planetary gaze and musical expression.

At every moment answers:
  Which notes are currently being gazed at
  by which planets
  with what force and direction?

Two sources of gaze:
  1. Canonical (traditional planet→swara assignments) — always present
  2. Live panchanga (actual sky today) — today's ruling graha aspects specific positions

The classical_experimental axis blends these:
  0.0 = pure canonical (textbook raga grammar)
  1.0 = pure live (today's unique sky configuration)
"""

from typing import Dict, List, Optional, Set

from .aspect_repair import (
    ASPECT_RULES, PLANETARY_SWARA_AFFINITY,
    SWARA_ENTITIES, POSITION_TO_SWARAS,
    add_aspect_edges,
)


class SwaraEngine:
    """Planetary gaze → swara character for the phrase engine."""

    def __init__(self, graph, field_state: dict):
        self.graph = graph
        self.field_state = field_state
        self.current_raga = None

        # Ensure aspect edges are in the graph
        add_aspect_edges(graph)

        self._load_raga(field_state)

    def _load_raga(self, field_state: dict):
        """Load current raga from field state and graph."""
        raga_name = field_state.get("devi_raga", "Bhairavi")
        # Try graph lookup
        raga_id = f"raga_{raga_name.lower().replace(' ', '_')}"
        meta = self.graph.meta(raga_id)
        attrs = meta.get("attributes", {})

        # Parse aroha/avaroha from graph metadata
        aroha_raw = attrs.get("aroha", [""])[0] if attrs.get("aroha") else ""
        avaroha_raw = attrs.get("avaroha", [""])[0] if attrs.get("avaroha") else ""
        vadi_raw = attrs.get("vadi", ["Pa"])[0] if attrs.get("vadi") else "Pa"
        samvadi_raw = attrs.get("samvadi", ["Sa"])[0] if attrs.get("samvadi") else "Sa"

        self.current_raga = {
            "id": raga_id,
            "name": raga_name,
            "aroha": self._parse_swaras(aroha_raw),
            "avaroha": self._parse_swaras(avaroha_raw),
            "vadi": self._swara_name_to_id(vadi_raw),
            "samvadi": self._swara_name_to_id(samvadi_raw),
            "vakra_swaras": set(),
        }

    def _parse_swaras(self, aroha_str: str) -> List[str]:
        """Parse 'Sa re ga Ma Pa dha ni Sa' → list of swara entity IDs."""
        if not aroha_str:
            return []
        _MAP = {
            "Sa": "swara_sa", "re": "swara_komal_re", "Re": "swara_shuddha_re",
            "Ri": "swara_shuddha_re", "ri": "swara_komal_re",
            "ga": "swara_komal_ga", "Ga": "swara_shuddha_ga",
            "ma": "swara_shuddha_ma", "Ma": "swara_shuddha_ma",
            "Ma#": "swara_teevra_ma",
            "Pa": "swara_pa",
            "dha": "swara_komal_dha", "Dha": "swara_shuddha_dha",
            "ni": "swara_komal_ni", "Ni": "swara_shuddha_ni",
        }
        result = []
        for token in aroha_str.replace(",", " ").split():
            token = token.strip()
            sid = _MAP.get(token)
            if sid:
                result.append(sid)
        return result

    def _swara_name_to_id(self, name: str) -> str:
        """Convert vadi/samvadi name like 'Ma' or 'Pa' to entity ID."""
        _MAP = {
            "Sa": "swara_sa", "Re": "swara_shuddha_re", "re": "swara_komal_re",
            "Ri": "swara_shuddha_re", "ri": "swara_komal_re",
            "Ga": "swara_shuddha_ga", "ga": "swara_komal_ga",
            "Ma": "swara_shuddha_ma", "ma": "swara_shuddha_ma",
            "Pa": "swara_pa",
            "Dha": "swara_shuddha_dha", "dha": "swara_komal_dha",
            "Ni": "swara_shuddha_ni", "ni": "swara_komal_ni",
        }
        return _MAP.get(name, "swara_pa")

    # ── Gaze computation ──────────────────────────────────────────

    def get_active_gazes(self) -> Dict[str, List[dict]]:
        """Which planets are currently gazing at which swaras?

        Returns {swara_id: [{planet, force, quality, duration, source}, ...]}
        """
        gazes: Dict[str, List[dict]] = {}

        # 1. Canonical gaze — traditional planet→swara assignments
        for planet_id, swara_id in PLANETARY_SWARA_AFFINITY.items():
            strength = self._get_planet_strength(planet_id)
            if strength < 0.2:
                continue
            rules = ASPECT_RULES.get(planet_id, {})
            gazes.setdefault(swara_id, []).append({
                "planet": planet_id,
                "force": strength * rules.get("force", 0.5),
                "quality": rules.get("quality", ""),
                "duration": rules.get("gaze_duration", ""),
                "source": "canonical",
                "retrograde": rules.get("retrograde", False),
            })

        # 2. Live panchanga gaze — actual sky today
        live = self._compute_live_gazes()
        for swara_id, gaze_list in live.items():
            gazes.setdefault(swara_id, []).extend(gaze_list)

        return gazes

    def _compute_live_gazes(self) -> Dict[str, List[dict]]:
        """Use actual planetary positions from panchanga to compute gaze."""
        gazes: Dict[str, List[dict]] = {}
        p5 = self.field_state.get("panchanga", {})

        # The nakshatra lord is today's active graha
        nak_lord = p5.get("nak_lord", "")
        if not nak_lord:
            return gazes

        graha_id = f"graha_{nak_lord.lower()}"
        rules = ASPECT_RULES.get(graha_id)
        if not rules:
            return gazes

        for house_offset in rules["aspects"]:
            target_swaras = POSITION_TO_SWARAS.get(house_offset, [])
            if not target_swaras and house_offset > 8:
                wrapped = ((house_offset - 1) % 8) + 1
                target_swaras = POSITION_TO_SWARAS.get(wrapped, [])

            for swara_id in target_swaras:
                gazes.setdefault(swara_id, []).append({
                    "planet": graha_id,
                    "force": rules["force"],
                    "quality": rules["quality"],
                    "duration": rules["gaze_duration"],
                    "source": "live_panchanga",
                    "retrograde": rules.get("retrograde", False),
                })

        return gazes

    def _get_planet_strength(self, planet_id: str) -> float:
        """How strong is this planet in today's field?"""
        p5 = self.field_state.get("panchanga", {})
        nak_lord = p5.get("nak_lord", "")
        nak_graha = f"graha_{nak_lord.lower()}" if nak_lord else ""

        if planet_id == nak_graha:
            return 1.0  # today's ruling planet

        # Check graha strengths if available
        strengths = self.field_state.get("graha_strengths", {})
        if planet_id in strengths:
            return float(strengths[planet_id])

        return 0.4  # baseline presence

    # ── Core: swara character ─────────────────────────────────────

    def get_swara_character(self, swara_id: str, direction: str) -> dict:
        """THE CORE FUNCTION.

        What is the character of this note right now, in this direction?

        Returns everything the phrase engine and gamaka engine need:
          gazed, force, duration_factor, gamaka_intensity, gamaka_type,
          emphasis, quality, vakra, skip_probability
        """
        gazes = self.get_active_gazes()
        swara_gazes = gazes.get(swara_id, [])

        if not swara_gazes:
            return {
                "gazed": False,
                "duration_factor": 0.5,
                "gamaka_intensity": 0.2,
                "emphasis": "passing",
                "skip_probability": 0.0,
                "vakra": False,
            }

        primary_gaze = max(swara_gazes, key=lambda g: g["force"])

        if direction == "ascending":
            return {
                "gazed": True,
                "planet": primary_gaze["planet"],
                "force": primary_gaze["force"],
                "duration_factor": self._duration_factor(primary_gaze["duration"]),
                "gamaka_intensity": primary_gaze["force"],
                "gamaka_type": self._gamaka_for_planet(primary_gaze["planet"]),
                "emphasis": "strong",
                "quality": primary_gaze["quality"],
                "vakra": primary_gaze.get("retrograde", False),
                "skip_probability": 0.0,
            }

        else:  # descending
            is_vadi = swara_id == self.current_raga.get("vadi")
            is_sa = swara_id in ("swara_sa", "swara_tara_sa")

            if is_vadi or is_sa:
                return {
                    "gazed": True,
                    "planet": primary_gaze["planet"],
                    "force": primary_gaze["force"] * 0.7,
                    "duration_factor": 0.8,
                    "gamaka_intensity": 0.5,
                    "emphasis": "resting",
                    "quality": primary_gaze["quality"],
                    "vakra": False,
                    "skip_probability": 0.0,
                }
            else:
                return {
                    "gazed": False,
                    "duration_factor": 0.3,
                    "gamaka_intensity": 0.1,
                    "emphasis": "released",
                    "skip_probability": 0.2,
                    "vakra": primary_gaze.get("retrograde", False),
                }

    def _duration_factor(self, gaze_duration: str) -> float:
        return {
            "insistent": 2.5,   # Mangala — holds
            "dwelling":  2.0,   # Guru — lingers
            "weighted":  2.2,   # Shani — presses
            "commanding": 1.8,  # Surya
            "touching":  0.8,   # Chandra — brief
            "caressing": 1.2,   # Shukra
            "darting":   0.6,   # Budha — quick
            "returning": 1.5,   # Rahu — returns
            "fading":    0.7,   # Ketu
        }.get(gaze_duration, 1.0)

    def _gamaka_for_planet(self, planet_id: str) -> str:
        """Each planet's gaze produces a characteristic gamaka."""
        return {
            "graha_mangala": "kampita",     # strong oscillation
            "graha_guru":    "andolan",     # slow gentle wave
            "graha_shani":   "meend",       # slow glide
            "graha_surya":   "pratyahata",  # sharp attack
            "graha_chandra": "andolan",     # soft wave
            "graha_shukra":  "murcchana",   # sweet glide
            "graha_budha":   "sparsha",     # brief touch
            "graha_rahu":    "kampita",     # strong, shadowy
            "graha_ketu":    "meend",       # dissolving glide
        }.get(planet_id, "andolan")

    # ── Vakra notes ───────────────────────────────────────────────

    def get_vakra_notes(self) -> Set[str]:
        """Notes requiring vakra (crooked/doubled-back) movement."""
        vakra = set()
        vakra.update(self.current_raga.get("vakra_swaras", set()))

        gazes = self.get_active_gazes()
        for swara_id, gaze_list in gazes.items():
            for gaze in gaze_list:
                if gaze.get("retrograde"):
                    vakra.add(swara_id)

        return vakra

    # ── Compose variation ─────────────────────────────────────────

    def get_compose_variation(self, classical_experimental: float,
                               acoustic_electronic: float,
                               composed_improvised: float) -> dict:
        """Generate variation params for a position in expression space.

        classical_experimental: 0.0=canonical only, 1.0=live sky only
        acoustic_electronic:    0.0=pure acoustic, 1.0=electronic timbres
        composed_improvised:    0.0=strict grammar, 1.0=free rhythm
        """
        if classical_experimental < 0.5:
            weight_canonical = 1.0
            weight_live = classical_experimental * 2
        else:
            weight_canonical = (1 - classical_experimental) * 2
            weight_live = 1.0

        return {
            "weight_canonical": round(weight_canonical, 3),
            "weight_live": round(weight_live, 3),
            "use_extended_swaras": classical_experimental > 0.7,
            "allow_microtonal": acoustic_electronic > 0.5,
            "free_rhythm": composed_improvised > 0.6,
        }


# ── Swara ID ↔ phrase_engine node name mapping ──────────────────

SWARA_TO_NODE = {
    "swara_sa":          "Sa",
    "swara_komal_re":    "Re_k",
    "swara_shuddha_re":  "Re",
    "swara_komal_ga":    "Ga_k",
    "swara_shuddha_ga":  "Ga",
    "swara_shuddha_ma":  "Ma",
    "swara_teevra_ma":   "Ma_t",
    "swara_pa":          "Pa",
    "swara_komal_dha":   "Dha_k",
    "swara_shuddha_dha": "Dha",
    "swara_komal_ni":    "Ni_k",
    "swara_shuddha_ni":  "Ni",
    "swara_tara_sa":     "Sa",
}

NODE_TO_SWARA = {v: k for k, v in SWARA_TO_NODE.items()}
# Handle duplicates manually
NODE_TO_SWARA["Sa"] = "swara_sa"
NODE_TO_SWARA["Ma"] = "swara_shuddha_ma"
