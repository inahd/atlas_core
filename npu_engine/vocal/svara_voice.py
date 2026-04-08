"""
svara_voice.py — Maps swara + raga to vocal qualities via graph.

Same note, different raga = different deity, different emotion,
different ornament. The voice knows this because it queries the graph.
"""

from typing import Dict, NamedTuple, Optional
from .graph_seed_data import SVARA_RAGA_RASA, BHAVA_STATES, GAMAKA_TYPES


class SvaraQuality(NamedTuple):
    brightness: float     # 0-1
    register: int         # -1, 0, 1
    ornament_type: str    # gamaka name or ""
    confidence: float     # 0-1 (authority of the edge)
    rasa: str
    bhava: str


# Pre-index
_SRR = {}
for tri in SVARA_RAGA_RASA:
    _SRR[(tri["swara"], tri["raga"])] = tri


def get_svara_quality(swara: str, raga_name: str,
                      graph=None) -> SvaraQuality:
    """Query swara + raga → rasa → bhava → vocal quality.

    If graph is provided (GraphEngine instance), authority weight
    comes from the graph edge. Otherwise defaults to 0.6.

    Sparse graph = neutral quality. Rich graph = deeply colored.
    """
    # Check the svara-raga-rasa triangle
    tri = _SRR.get((swara, raga_name))

    if tri:
        bhava_name = tri["bhava"]
        bhava = BHAVA_STATES.get(bhava_name, BHAVA_STATES["shanta"])
        confidence = 0.8  # these are canonical edges

        # If we have a live graph, check authority
        if graph is not None:
            try:
                entity_id = f"raga:{raga_name.lower()}"
                auth = graph.authority_weight(entity_id)
                confidence = auth
            except Exception:
                pass

        return SvaraQuality(
            brightness=bhava["brightness"],
            register=bhava["register"],
            ornament_type=tri["ornament"],
            confidence=confidence,
            rasa=tri["rasa"],
            bhava=bhava_name,
        )

    # No specific edge — return neutral quality
    return SvaraQuality(
        brightness=0.5,
        register=0,
        ornament_type="",
        confidence=0.3,  # low confidence = sparse graph
        rasa="shanta",
        bhava="shanta",
    )
