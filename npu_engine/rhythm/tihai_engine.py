"""
tihai_engine.py — Calculates and generates tihais.

A tihai is a phrase repeated exactly 3 times that lands on Sam.
Math: start + 3*phrase_length + 2*gap = sam_beat (mod tala_length)
Only returns a tihai when the math lands cleanly on sam.
"""

from typing import List, NamedTuple, Optional
from .graph_seed_data import TIHAI_PHRASES
from .sam_field import beats_to_sam


class Tihai(NamedTuple):
    phrase: List[str]     # bol sequence
    start_beat: int       # when to begin
    gap_beats: int        # silence between repetitions (0 = bedam)
    phrase_beats: int     # length of one repetition


def find_tihai(current_beat: int, tala_name: str, tala_beats: int,
               min_phrase: int = 2, max_phrase: int = 8) -> Optional[Tihai]:
    """Find a tihai that lands cleanly on sam from current position.

    Math: current + 3*P + 2*G = sam (mod tala_beats)
    where P = phrase length, G = gap between reps.

    Returns Tihai if one fits, None otherwise.
    """
    to_sam = beats_to_sam(current_beat, tala_name)
    if to_sam == 0:
        return None  # already at sam

    phrases = TIHAI_PHRASES.get(tala_name, TIHAI_PHRASES.get("Adi", []))

    for phrase in phrases:
        P = len(phrase)
        if P < min_phrase or P > max_phrase:
            continue

        # Try gap values 0, 1, 2
        for G in range(3):
            total = 3 * P + 2 * G
            if total == to_sam:
                return Tihai(
                    phrase=phrase,
                    start_beat=current_beat,
                    gap_beats=G,
                    phrase_beats=P,
                )
            # Also check if total fits within the next cycle
            if total == to_sam + tala_beats:
                return Tihai(
                    phrase=phrase,
                    start_beat=current_beat,
                    gap_beats=G,
                    phrase_beats=P,
                )

    return None


def is_tihai_possible(current_beat: int, tala_name: str,
                      tala_beats: int) -> bool:
    """Quick check: can any tihai fit from here to sam?"""
    return find_tihai(current_beat, tala_name, tala_beats) is not None
