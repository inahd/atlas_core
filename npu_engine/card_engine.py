"""
card_engine.py — Oracle card engine for Coherence Atlas.

Builds cards from the NPU graph, draws spreads weighted by field
coherence, and applies the four Gita approaches (arta/jijnasu/
artharthi/jnani) to shape the reading.

Decks: nakshatra (27), devi (15), graha (9), mixed
Spreads: resonance (3-card: now/approaching/preparation)
"""

import math
import random
import time
from typing import Dict, List, Optional, Any

from .graph_engine import GraphEngine
from .datasets import load_entity_metadata


# ── Deck definitions ──────────────────────────────────────────

DECK_PREFIXES = {
    "nakshatra": "nakshatra_",
    "devi":      "devi_",
    "graha":     "graha_",
}

# Four approaches from Bhagavad Gita 7.16
APPROACHES = {
    "arta": {
        "name": "Ārta",
        "quality": "the distressed — seeking relief",
        "tone": "compassionate, practical, immediate",
        "focus": "what alleviates suffering now",
    },
    "jijnasu": {
        "name": "Jijñāsu",
        "quality": "the seeker — seeking understanding",
        "tone": "contemplative, curious, patient",
        "focus": "what this reveals about the nature of things",
    },
    "artharthi": {
        "name": "Arthārthī",
        "quality": "the purposeful — seeking specific outcomes",
        "tone": "strategic, directed, empowering",
        "focus": "what action serves the intention",
    },
    "jnani": {
        "name": "Jñānī",
        "quality": "the wise — seeking the field itself",
        "tone": "still, witnessing, non-dual",
        "focus": "what is already complete here",
    },
}

# Element colors
ELEM_COLOR = {
    "fire": "#e05020", "water": "#4080d0", "earth": "#c8a96e",
    "air": "#60c0d0", "ether": "#9060c0",
}

# Body region → practice suggestions
BODY_PRACTICE = {
    "head": "meditation, pranayama, shirodhara",
    "eyes": "trataka, eye palming, distant gazing",
    "throat": "singing, jalandhara bandha, ujjayi breath",
    "chest": "heart opening asanas, bhakti, kirtan",
    "hands": "mudra practice, craft work, seva",
    "digestive": "dietary adjustment, agni kindling, triphala",
    "reproductive": "mula bandha, creative expression",
    "lungs": "pranayama, arjuna herb, open air",
    "spine": "spinal twists, grounding, banyan",
    "legs": "walking meditation, standing asanas",
    "feet": "grounding, earthing, reflexology",
    "skin": "abhyanga, neem, sun exposure",
}


class Card:
    """A single oracle card built from an NPU entity."""

    def __init__(self, entity_id: str, name: str, sanskrit: str = "",
                 element: str = "ether", guna: str = "sattva",
                 color: str = "#c8a96e", qualities: list = None,
                 process: str = "", reading: str = "",
                 yantra_params: dict = None, domains: dict = None,
                 field_score: float = 0.5):
        self.id = entity_id
        self.name = name
        self.sanskrit = sanskrit
        self.element = element
        self.guna = guna
        self.color = color
        self.qualities = qualities or []
        self.process = process
        self.reading = reading
        self.yantra_params = yantra_params or {}
        self.domains = domains or {}
        self.field_score = field_score

    def to_dict(self) -> dict:
        return {
            "id": self.id, "name": self.name, "sanskrit": self.sanskrit,
            "element": self.element, "guna": self.guna, "color": self.color,
            "qualities": self.qualities, "process": self.process,
            "reading": self.reading, "yantra_params": self.yantra_params,
            "domains": self.domains, "field_score": round(self.field_score, 3),
        }


class CardEngine:
    """Oracle card engine — builds cards from graph, draws spreads."""

    def __init__(self):
        self._graph = GraphEngine()
        self._meta = load_entity_metadata()

    def build_card(self, entity_id: str, field_state: dict = None) -> Card:
        """Build a complete card from an entity ID."""
        meta = self._meta.get(entity_id, {})
        attrs = meta.get("attributes", {})
        p5 = (field_state or {}).get("panchanga", {})

        name = meta.get("name", entity_id.split("_", 1)[-1].replace("_", " ").title())
        sanskrit = ""
        for alias in meta.get("aliases", []):
            if any(ord(c) > 0x900 for c in alias):
                sanskrit = alias
                break

        elem = _first(attrs, "element", "ether").lower()
        guna = _first(attrs, "guna", "sattva").lower()
        color = ELEM_COLOR.get(elem, "#c8a96e")

        # Qualities from graph attributes
        qualities = []
        for key in ["shakti", "themes", "symbol", "quality"]:
            val = attrs.get(key, [])
            if isinstance(val, list):
                qualities.extend(val)
            elif val:
                qualities.append(str(val))

        # Process — what this entity does
        process = _first(attrs, "description", "")
        if not process:
            process = f"{name} — {elem} element, {guna} guna"

        # Yantra params from torus topology
        yantra = self._yantra_params(entity_id)

        # Domain-specific data
        domains = self._build_domains(entity_id, attrs)

        # Field score — how resonant is this entity right now
        score = self._field_score(entity_id, p5)

        return Card(
            entity_id=entity_id, name=name, sanskrit=sanskrit,
            element=elem, guna=guna, color=color,
            qualities=qualities[:6], process=process,
            yantra_params=yantra, domains=domains,
            field_score=score,
        )

    def draw_spread(self, n: int = 3, deck: str = "mixed",
                    field_state: dict = None, natal: dict = None) -> List[Card]:
        """Draw n cards weighted by field coherence."""
        candidates = self._get_deck(deck)
        if not candidates:
            return []

        p5 = (field_state or {}).get("panchanga", {})

        # Score each candidate
        scored = []
        for eid in candidates:
            score = self._field_score(eid, p5)
            # Add natal resonance if available
            if natal:
                score += self._natal_score(eid, natal) * 0.3
            scored.append((eid, score))

        # Weighted random selection
        scored.sort(key=lambda x: -x[1])
        weights = [max(0.01, s) for _, s in scored]
        total = sum(weights)
        probs = [w / total for w in weights]

        chosen = set()
        cards = []
        for _ in range(min(n, len(candidates))):
            r = random.random()
            cumul = 0
            for i, (eid, _) in enumerate(scored):
                if eid in chosen:
                    continue
                cumul += probs[i]
                if r <= cumul:
                    chosen.add(eid)
                    cards.append(self.build_card(eid, field_state))
                    break

        return cards

    def resonance_spread(self, field_state: dict,
                         natal: dict = None,
                         intention: str = "") -> dict:
        """3-card spread: now / approaching / preparation."""
        p5 = (field_state or {}).get("panchanga", {})

        # Card 1: NOW — highest resonance with current field
        now_cards = self.draw_spread(1, "mixed", field_state, natal)
        now = now_cards[0] if now_cards else None

        # Card 2: APPROACHING — weighted toward upcoming transits
        approach_deck = "graha" if natal else "devi"
        approach_cards = self.draw_spread(1, approach_deck, field_state, natal)
        approaching = approach_cards[0] if approach_cards else None

        # Card 3: PREPARATION — practice by body region
        body = p5.get("body_region", "chest")
        practice = BODY_PRACTICE.get(body, "meditation and awareness")
        prep_cards = self.draw_spread(1, "nakshatra", field_state, natal)
        preparation = prep_cards[0] if prep_cards else None
        if preparation:
            preparation.process = f"Practice: {practice}"

        return {
            "spread_type": "resonance",
            "intention": intention,
            "timestamp": time.time(),
            "field": {
                "nakshatra": p5.get("nakshatra"),
                "element": p5.get("element"),
                "tithi": p5.get("tithi"),
            },
            "cards": {
                "now": now.to_dict() if now else None,
                "approaching": approaching.to_dict() if approaching else None,
                "preparation": preparation.to_dict() if preparation else None,
            },
        }

    def apply_approach(self, spread: dict, approach: str = "jijnasu") -> dict:
        """Shape the reading through one of the four Gita approaches."""
        ap = APPROACHES.get(approach, APPROACHES["jijnasu"])
        cards = spread.get("cards", {})

        readings = {}
        for position, card_data in cards.items():
            if not card_data:
                continue
            name = card_data.get("name", "?")
            elem = card_data.get("element", "ether")
            qualities = card_data.get("qualities", [])
            q_str = ", ".join(qualities[:3]) if qualities else elem

            if approach == "arta":
                readings[position] = (
                    f"{name} offers relief through {elem}. "
                    f"The quality of {q_str} is medicine for this moment."
                )
            elif approach == "jijnasu":
                readings[position] = (
                    f"{name} reveals: {q_str}. "
                    f"The {elem} element here points toward understanding."
                )
            elif approach == "artharthi":
                readings[position] = (
                    f"{name} in the {position} position directs action through {elem}. "
                    f"Apply {q_str} to serve the intention."
                )
            elif approach == "jnani":
                readings[position] = (
                    f"{name}. {elem}. {q_str}. "
                    f"Already complete."
                )

        return {
            **spread,
            "approach": ap,
            "readings": readings,
        }

    def get_deck(self, deck: str = "mixed") -> List[dict]:
        """Return full deck listing."""
        eids = self._get_deck(deck)
        return [{"id": eid, "name": self._meta.get(eid, {}).get("name", eid)}
                for eid in eids]

    # ── Private helpers ───────────────────────────────────────

    def _get_deck(self, deck: str) -> List[str]:
        """Get entity IDs for a deck."""
        if deck == "mixed":
            ids = []
            for prefix in DECK_PREFIXES.values():
                ids.extend(eid for eid in self._meta
                           if eid.startswith(prefix)
                           and not eid.startswith("nakshatra_pada"))
            return ids

        prefix = DECK_PREFIXES.get(deck)
        if not prefix:
            return []
        return [eid for eid in self._meta
                if eid.startswith(prefix)
                and not eid.startswith("nakshatra_pada")]

    def _field_score(self, entity_id: str, panchanga: dict) -> float:
        """Score entity resonance with current field."""
        score = 0.3  # base
        attrs = self._meta.get(entity_id, {}).get("attributes", {})

        current_nak = (panchanga.get("nakshatra", "")).lower()
        current_elem = (panchanga.get("element", "")).lower()
        current_guna = (panchanga.get("guna", "")).lower()

        # Nakshatra match
        nak_vals = [v.lower() for v in attrs.get("nakshatra", [])
                    if isinstance(v, str)]
        if current_nak in nak_vals or current_nak in entity_id.lower():
            score += 0.4

        # Element match
        elem_vals = [v.lower() for v in attrs.get("element", [])
                     if isinstance(v, str)]
        if current_elem in elem_vals:
            score += 0.2

        # Guna match
        guna_vals = [v.lower() for v in attrs.get("guna", [])
                     if isinstance(v, str)]
        if current_guna in guna_vals:
            score += 0.1

        return min(1.0, score)

    def _natal_score(self, entity_id: str, natal: dict) -> float:
        """Score entity resonance with natal chart."""
        score = 0.0
        planets = natal.get("planets", {})
        lagna_nak = natal.get("lagna", {}).get("nakshatra", "").lower()

        if lagna_nak and lagna_nak in entity_id.lower():
            score += 0.5

        for planet, data in planets.items():
            p_nak = data.get("nakshatra", "").lower()
            if p_nak and p_nak in entity_id.lower():
                score += 0.2
                break

        return min(0.5, score)

    def _yantra_params(self, entity_id: str) -> dict:
        """Derive yantra rendering parameters from entity."""
        attrs = self._meta.get(entity_id, {}).get("attributes", {})

        triangle = _first(attrs, "yantra_triangle_id", "")
        polarity = _first(attrs, "yantra_polarity", "")
        yuga = _first(attrs, "yantra_yuga", "")

        if not triangle:
            # Infer from element
            elem = _first(attrs, "element", "ether").lower()
            _ELEM_TRI = {
                "fire": "shakti_treta", "water": "shakti_kali",
                "earth": "shiva_dvapara_1", "air": "shiva_treta",
                "ether": "shiva_satya",
            }
            triangle = _ELEM_TRI.get(elem, "shiva_satya")
            polarity = "Shakti" if "shakti" in triangle else "Shiva"
            yuga = triangle.split("_")[-1].title() if "_" in triangle else "Satya"

        _COMPASS = {
            "shakti_kali": "SW", "shakti_dvapara": "SE",
            "shakti_treta": "E", "shakti_satya": "NE",
            "shiva_satya": "N", "shiva_treta": "NW",
            "shiva_dvapara_1": "W", "shiva_dvapara_2": "W",
            "shiva_kali": "S",
        }

        return {
            "triangle": triangle,
            "polarity": polarity,
            "yuga": yuga,
            "compass": _COMPASS.get(triangle, ""),
            "element": _first(attrs, "element", "ether"),
        }

    def _build_domains(self, entity_id: str, attrs: dict) -> dict:
        """Build domain-specific data for the card."""
        domains = {}

        # Astrology
        astro = {}
        for key in ["nakshatra", "graha", "ruler", "deity", "shakti",
                     "symbol", "themes"]:
            val = attrs.get(key)
            if val:
                astro[key] = val[0] if isinstance(val, list) else val
        if astro:
            domains["astrology"] = astro

        # Ayurveda
        ayur = {}
        for key in ["dosha", "body_part", "rasa", "element"]:
            val = attrs.get(key)
            if val:
                ayur[key] = val[0] if isinstance(val, list) else val
        if ayur:
            domains["ayurveda"] = ayur

        # Gandharva (music)
        gandh = {}
        for key in ["raga", "bija", "tala"]:
            val = attrs.get(key)
            if val:
                gandh[key] = val[0] if isinstance(val, list) else val
        if gandh:
            domains["gandharva"] = gandh

        return domains


def _first(attrs: dict, key: str, default: str = "") -> str:
    """Get first value from attribute list or string."""
    val = attrs.get(key, default)
    if isinstance(val, list):
        return val[0] if val else default
    return str(val) if val else default


# ── Test ──────────────────────────────────────────────────────
if __name__ == "__main__":
    import json

    print("✦ Card Engine test")
    engine = CardEngine()

    # Build a single card
    card = engine.build_card("nakshatra_rohini")
    print(f"\nCard: {card.name}")
    print(f"  element: {card.element}, guna: {card.guna}")
    print(f"  qualities: {card.qualities}")
    print(f"  yantra: {card.yantra_params}")
    print(f"  domains: {json.dumps(card.domains, indent=2)}")

    # Draw a spread
    print("\n3-card draw (mixed deck):")
    cards = engine.draw_spread(3, "mixed")
    for c in cards:
        print(f"  {c.name} ({c.element}) score={c.field_score:.2f}")

    # Full deck counts
    for deck in ["nakshatra", "devi", "graha", "mixed"]:
        n = len(engine._get_deck(deck))
        print(f"  {deck}: {n} cards")
