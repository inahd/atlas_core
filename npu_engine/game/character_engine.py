"""
character_engine.py — Atlas game character state from natal + field.

Reads natal chart, field state, interaction history.
Returns full character state dict.
Pattern follows ui_vastu_engine.py. Never raises.
"""

import csv
import io
import json
import os
from typing import Dict, List

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
_NATAL_PATH = os.path.join(_ROOT, "instance", "personal", "natal.json")
_OBJECTS_CSV = os.path.join(_ROOT, "datasets", "game", "sacred_objects.csv")
_INTERACTIONS = os.path.join(_ROOT, "instance", "city", "interactions.jsonl")

_DOSHA_FROM_ELEMENT = {"fire": "pitta", "water": "kapha", "earth": "kapha",
                       "air": "vata", "ether": "vata"}
_SIGN_ELEM = {"aries": "fire", "taurus": "earth", "gemini": "air",
              "cancer": "water", "leo": "fire", "virgo": "earth",
              "libra": "air", "scorpio": "water", "sagittarius": "fire",
              "capricorn": "earth", "aquarius": "air", "pisces": "water"}


def _load_natal():
    try:
        with open(_NATAL_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _load_objects():
    try:
        with open(_OBJECTS_CSV, encoding="utf-8") as f:
            return list(csv.DictReader(io.StringIO(f.read().lstrip())))
    except Exception:
        return []


def _load_interactions():
    entries = []
    try:
        with open(_INTERACTIONS, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
    except Exception:
        pass
    return entries


def _prakriti(natal):
    """Dosha composition from lagna + moon sign."""
    lagna_sign = natal.get("lagna", {}).get("sign", "").lower()
    moon_sign = natal.get("planets", {}).get("moon", {}).get("sign", "").lower()
    lagna_elem = _SIGN_ELEM.get(lagna_sign, "earth")
    moon_elem = _SIGN_ELEM.get(moon_sign, "water")
    d1 = _DOSHA_FROM_ELEMENT.get(lagna_elem, "kapha")
    d2 = _DOSHA_FROM_ELEMENT.get(moon_elem, "vata")
    return {"primary": d1, "secondary": d2, "lagna_element": lagna_elem, "moon_element": moon_elem}


def _varna_tendency(interactions):
    """Most-visited district types → varna tendency."""
    counts = {}
    _DISTRICT_VARNA = {"NE": "brahmana", "N": "brahmana", "E": "vaishya",
                       "SE": "kshatriya", "S": "kshatriya", "SW": "vaishya",
                       "W": "brahmana", "NW": "brahmana", "C": "sannyasa"}
    for entry in interactions:
        gate = entry.get("gate", "")
        varna = _DISTRICT_VARNA.get(gate, "")
        if varna:
            counts[varna] = counts.get(varna, 0) + 1
    if not counts:
        return "universal"
    return max(counts, key=counts.get)


def _check_encounters(natal, district):
    """Check sacred objects in a district against natal relations."""
    objects = _load_objects()
    results = []
    planets = natal.get("planets", {})
    special = natal.get("special", {})
    lagna = natal.get("lagna", {})

    for obj in objects:
        if obj.get("district_location", "") != district:
            continue
        # Check recognition relation against natal
        rel = obj.get("recognition_relation", "").lower()
        recognized = False

        # Check specific natal conditions
        if "rohini_lagna" in rel and "rohini" in lagna.get("nakshatra", "").lower():
            recognized = True
        if "venus_dhanishta" in rel:
            venus = planets.get("venus", {})
            if "dhanishta" in venus.get("nakshatra", "").lower():
                recognized = True
        if "mars_fire" in rel:
            mars = planets.get("mars", {})
            if mars:
                recognized = True
        if "jupiter_anuradha" in rel:
            jup = planets.get("jupiter", {})
            if "anuradha" in jup.get("nakshatra", "").lower():
                recognized = True
        if "saturn_swati" in rel:
            sat = planets.get("saturn", {})
            if "swati" in sat.get("nakshatra", "").lower() and sat.get("exalted"):
                recognized = True
        if "ketu_mula" in rel:
            ketu = planets.get("ketu", {})
            if "mula" in ketu.get("nakshatra", "").lower():
                recognized = True
        if "moon_punarvasu" in rel:
            moon = planets.get("moon", {})
            if "punarvasu" in moon.get("nakshatra", "").lower():
                recognized = True
        if "sun_shravana" in rel:
            sun = planets.get("sun", {})
            if "shravana" in sun.get("nakshatra", "").lower():
                recognized = True

        if recognized:
            results.append({
                "object_id": obj.get("object_id", ""),
                "name_sanskrit": obj.get("name_sanskrit", ""),
                "name_english": obj.get("name_english", ""),
                "recognition_text": obj.get("recognition_text", ""),
                "attestation_level": obj.get("attestation_level", ""),
                "attestation_symbol": obj.get("attestation_symbol", ""),
                "reward_type": obj.get("reward_type", ""),
            })

    return results


def derive_character_state(natal: dict = None, field_state: dict = None) -> dict:
    """Full character state from natal + field. Never raises."""
    try:
        if natal is None:
            natal = _load_natal()
        if field_state is None:
            field_state = {}

        p5 = field_state.get("panchanga", {})
        interactions = _load_interactions()

        # Prakriti
        prakriti = _prakriti(natal)

        # Guna today from field
        guna_today = p5.get("guna", "sattva")

        # Varna tendency from interactions
        varna = _varna_tendency(interactions)

        # Accessible lineages
        from .lineage_engine import calculate_accessible_lineages
        lineages = calculate_accessible_lineages(natal)

        # Active chimera (highest-scoring chimeric lineage)
        chimeric = [l for l in lineages if l.get("type") == "chimeric"]
        active_chimera = chimeric[0] if chimeric else None

        # Sura/asura from element balance
        from .orientation_engine import derive_sura_asura
        orientation = derive_sura_asura(field_state, natal)

        return {
            "prakriti": prakriti,
            "guna_today": guna_today,
            "varna_tendency": varna,
            "accessible_lineages": lineages[:6],
            "active_chimera": active_chimera,
            "sura_asura_today": orientation,
            "natal_summary": {
                "lagna": natal.get("lagna", {}).get("nakshatra", ""),
                "moon": natal.get("planets", {}).get("moon", {}).get("nakshatra", ""),
                "dasha": natal.get("special", {}).get("dasha_current", ""),
            },
            "attestation": "SYNTHESIS",
        }
    except Exception:
        return {
            "prakriti": {"primary": "kapha", "secondary": "vata"},
            "guna_today": "sattva", "varna_tendency": "universal",
            "accessible_lineages": [], "active_chimera": None,
            "sura_asura_today": {}, "natal_summary": {},
            "attestation": "SYNTHESIS",
        }
