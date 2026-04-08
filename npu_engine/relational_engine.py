"""
relational_engine.py — NPU Cluster Component
==============================================
Relational computation layer.
Field gives state. This gives law. Surfaces give form.

field_state → relational_state → surface_state

Not a helper. Not a utility. A first-class cluster component.
"""

import math

# Swara reverse map (semitone → name)
_SEMI_TO_SWARA = {
    0: "Sa", 1: "re", 2: "Re", 3: "ga", 4: "Ga", 5: "ma",
    6: "Ma", 7: "Pa", 8: "dha", 9: "Dha", 10: "ni", 11: "Ni",
}
_SWARA_TO_SEMI = {v: k for k, v in _SEMI_TO_SWARA.items()}

_GATI_N = {"tisra": 3, "chatusra": 4, "khanda": 5, "misra": 7, "sankirna": 9}

_ELEM_RASA = {
    "fire": "vira", "water": "karuna", "earth": "shanta",
    "air": "shringara", "ether": "adbhuta",
}

_DOMAIN_WEIGHTS = {
    "healing":   {"ayurveda": 1.0, "gandharva": 0.9, "astrology": 0.8},
    "devotion":  {"gaudiya": 1.0, "astrology": 0.8, "ayurveda": 0.5},
    "mystery":   {"astrology": 1.0, "ayurveda": 0.7, "gandharva": 0.6},
    "abundance": {"ayurveda": 0.9, "vastu": 0.8, "permaculture": 0.8},
    "structure": {"vastu": 1.0, "astrology": 0.8, "ayurveda": 0.6},
}
_DEFAULT_WEIGHTS = {
    "astrology": 0.8, "ayurveda": 0.7, "gandharva": 0.6,
    "vastu": 0.5, "gaudiya": 0.4, "permaculture": 0.4,
}

_DEPTH = {"tamas": True, "sattva": False, "rajas": False}
_PSI_PATH = {"tamas": "jijnasu", "rajas": "artharthi", "sattva": "jnani"}


class RelationalEngine:
    """Relational computation component of the NPU cluster.

    Computes the law between field state and surface expression.
    Two domains: sound and knowledge.
    """

    def __init__(self, derive_sound_fn=None):
        """
        Args:
            derive_sound_fn: callable(field_data) → sound_state dict.
                             If None, reads from field_data['sound_state'].
        """
        self._derive_sound = derive_sound_fn

    def sound_state(self, field_data):
        """Compute relational sound law from field state.

        Returns the structure served by /sound/relational.
        """
        ss = field_data.get("sound_state")
        if not ss and self._derive_sound:
            ss = self._derive_sound(field_data)
        if not ss:
            ss = {}

        v1 = field_data.get("field_state_v1", {})
        phi = v1.get("phi", {})

        # Vadi-samvadi interval
        vadi = ss.get("raga_vadi", "")
        samvadi = ss.get("raga_samvadi", "")
        vadi_semi = _SWARA_TO_SEMI.get(vadi)
        samvadi_semi = _SWARA_TO_SEMI.get(samvadi)
        vs_interval = None
        if vadi_semi is not None and samvadi_semi is not None:
            vs_interval = (samvadi_semi - vadi_semi) % 12

        # Gati-tala law
        gati = ss.get("gati", "chatusra")
        gati_n = _GATI_N.get(gati, 4)
        tala_beats = ss.get("tala_beats", 8)
        total_pulses = tala_beats * gati_n

        # Element-rasa alignment
        element = ss.get("element", "ether")
        rasa = ss.get("raga_rasa", "")
        natural_rasa = _ELEM_RASA.get(element, "shanta")
        rasa_aligned = natural_rasa in rasa.lower() if rasa else False

        # Shruti reference
        element_freq = ss.get("element_frequency", 329.63)

        # Density from arc phase
        arc = ss.get("arc_phase", 0.5)
        density = round(0.3 + 0.7 * math.sin(arc * math.pi), 3)

        return {
            "raga": ss.get("raga", ""),
            "vadi": vadi,
            "samvadi": samvadi,
            "vadi_samvadi_interval": vs_interval,
            "tala": ss.get("tala", ""),
            "tala_beats": tala_beats,
            "gati": gati,
            "gati_subdivision": gati_n,
            "total_pulses_per_cycle": total_pulses,
            "bpm": ss.get("bpm", 72),
            "element": element,
            "element_frequency": element_freq,
            "rasa": rasa,
            "natural_rasa": natural_rasa,
            "rasa_aligned": rasa_aligned,
            "arc_phase": arc,
            "density": density,
            "phi_position": phi.get("position"),
            "phi_label": phi.get("label", "center"),
            "companion": phi.get("companion"),
            "derived_from_field": True,
            "layer": "relational",
            "attestation": {
                "raga": "OBSERVED",
                "vadi_samvadi": "OBSERVED",
                "tala": "TRADITIONAL",
                "gati": "SYNTHESIS",
                "element_rasa": "TRADITIONAL",
                "density": "SYNTHESIS",
            },
        }

    def knowledge_state(self, field_data):
        """Compute relational knowledge law from field state.

        Returns the structure served by /knowledge/relational.
        """
        p = field_data.get("panchanga", {})
        nak = p.get("nakshatra", "")
        nak_data = p.get("nak_data") or {}
        element = p.get("element", "ether").lower()
        guna = p.get("guna", "tamas").lower()
        deity = nak_data.get("deity", "")
        body = nak_data.get("body_region", "")
        themes = nak_data.get("themes", "")
        graha = p.get("nak_lord", "")

        theme_key = themes.split()[0] if themes else "mystery"
        weights = _DOMAIN_WEIGHTS.get(theme_key, _DEFAULT_WEIGHTS)

        return {
            "relational_knowledge_state": {
                "primary_entity": f"nakshatra_{nak.lower().replace(' ', '_')}",
                "active_relations": [
                    {"from": nak, "relation": "ruled_by", "to": graha, "attestation": "OBSERVED"},
                    {"from": nak, "relation": "deity", "to": deity, "attestation": "OBSERVED"},
                    {"from": nak, "relation": "body_region", "to": body, "attestation": "OBSERVED"},
                    {"from": nak, "relation": "element", "to": element, "attestation": "OBSERVED"},
                ],
                "domain_weights": weights,
                "study_path": {
                    "approach": _PSI_PATH.get(guna, "jijnasu"),
                    "depth_over_breadth": _DEPTH.get(guna, True),
                    "indicated_topic": themes,
                    "attestation": "INTERPRETATION",
                },
                "cross_links": [
                    [nak, graha, element, themes.split()[0] if themes else ""],
                ],
                "attestation": {
                    "active_relations": "OBSERVED",
                    "domain_weights": "SYNTHESIS",
                    "study_path": "INTERPRETATION",
                },
            }
        }
