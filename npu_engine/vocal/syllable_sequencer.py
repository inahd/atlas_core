"""
syllable_sequencer.py — Assembles phonemes into singable sequences.

Every sequence is a graph traversal result, tagged with:
phoneme_ids, formant_profiles, gamaka_instructions, bhava_state,
breath_positions, confidence_per_syllable.
"""

from typing import Dict, List, Optional
from .phoneme_graph import get_formant_profile, get_syllable_sequence
from .gamaka_engine import get_gamaka, GamakaInstruction
from .bhava_engine import BhavaState
from .breath_engine import get_breath_positions


class VocalElement:
    """A single element in a vocal sequence."""
    __slots__ = ("syllable", "formant", "gamaka", "bhava_params",
                 "confidence", "is_breath", "duration", "role")

    def __init__(self, syllable="", formant=None, gamaka=None,
                 bhava_params=None, confidence=0.5,
                 is_breath=False, duration=0.4, role=""):
        self.syllable = syllable
        self.formant = formant or {"f1": 600, "f2": 1200, "f3": 2500, "bw": 80}
        self.gamaka = gamaka
        self.bhava_params = bhava_params or {}
        self.confidence = confidence
        self.is_breath = is_breath
        self.duration = duration
        self.role = role  # "bija", "pada", "vowel", "breath", "bol"


def sequence_for_alap(nakshatra_entry: dict, raga_name: str,
                      bhava_state: BhavaState, rasa: str,
                      arc: float, tala_name: str = "Adi",
                      graph=None) -> List[VocalElement]:
    """Build an alap vocal phrase from nakshatra graph traversal.

    Alap: pada syllables interspersed with open vowels (aa, ee, oo).
    Spacious, breath-rich, ornament-rich.
    """
    elements = []
    base_syls = get_syllable_sequence(nakshatra_entry)

    # Get bhava coloring
    bhava = bhava_state.update(rasa, arc)

    # Get breath map
    breath_map = get_breath_positions(tala_name, "alap", arc, rasa)

    # Build phrase: bija → vowel → pada → vowel → breath
    beat = 0
    for i, syl_info in enumerate(base_syls):
        # Check if this beat is a breath point
        if beat in breath_map.positions:
            idx = breath_map.positions.index(beat)
            elements.append(VocalElement(
                is_breath=True,
                duration=breath_map.durations[idx],
                role="breath",
            ))

        # Check for gamaka on this note
        gamaka = None
        if syl_info["role"] == "bija":
            # Bija syllables may have deity-characteristic gamaka
            gamaka = get_gamaka("S", raga_name, arc, 0.7)

        confidence = _authority_for_role(syl_info["role"], graph, nakshatra_entry)

        elements.append(VocalElement(
            syllable=syl_info["syllable"],
            formant={"f1": syl_info["f1"], "f2": syl_info["f2"],
                     "f3": syl_info["f3"], "bw": syl_info["bw"]},
            gamaka=gamaka,
            bhava_params=bhava,
            confidence=confidence,
            duration=0.6 if syl_info["role"] == "bija" else 0.4,
            role=syl_info["role"],
        ))

        # Intersperse open vowels in alap
        if i < len(base_syls) - 1 and syl_info["role"] in ("bija", "pada"):
            vowel = ["aa", "ee", "oo"][i % 3]
            elements.append(VocalElement(
                syllable=vowel,
                formant=get_formant_profile(vowel.rstrip("aeiou")[:1] or "a"),
                bhava_params=bhava,
                confidence=confidence * 0.8,
                duration=0.8,
                role="vowel",
            ))

        beat += 1

    return elements


def sequence_for_bija(nakshatra_entry: dict, bhava_state: BhavaState,
                      rasa: str, arc: float) -> List[VocalElement]:
    """Build a bija mantra phrase (2-4 syllables, triggered on nakshatra change)."""
    bhava = bhava_state.update(rasa, arc)
    bija_syls = nakshatra_entry.get("bija", ["om"])

    return [
        VocalElement(
            syllable=syl,
            formant=get_formant_profile(syl),
            bhava_params=bhava,
            confidence=0.85,  # bija is always authoritative
            duration=[0.5, 0.4, 0.35, 0.3][min(i, 3)],
            role="bija",
        )
        for i, syl in enumerate(bija_syls)
    ]


def sequence_for_bol(theka_bols: List[str], bhava_state: BhavaState,
                     rasa: str, arc: float) -> List[VocalElement]:
    """Build a bol sequence from tala theka."""
    bhava = bhava_state.update(rasa, arc)

    return [
        VocalElement(
            syllable=bol,
            formant=get_formant_profile(bol[:2]),  # first 2 chars as approx
            bhava_params=bhava,
            confidence=0.9,  # bol patterns are canonical
            duration=0.15,
            role="bol",
        )
        for bol in theka_bols
    ]


def _authority_for_role(role: str, graph, nakshatra_entry: dict) -> float:
    """Derive confidence from graph authority for a syllable role."""
    if graph is not None:
        try:
            deity = nakshatra_entry.get("deity", "")
            entity_id = f"deity:{deity.lower().replace(' ', '_')}"
            return graph.authority_weight(entity_id)
        except Exception:
            pass

    # Defaults by role
    return {"bija": 0.85, "pada": 0.7, "deity_bija": 0.8,
            "vowel": 0.5, "bol": 0.9}.get(role, 0.5)
