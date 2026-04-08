#!/usr/bin/env python3
"""
symbol_automapper.py — Map all Unicode emoji to Atlas Vedic categories.

Deterministic keyword rules, no LLM.
Outputs datasets/symbols/emoji_auto_mapped.csv

Confidence: 1.0=textual, 0.8=keyword, 0.5=group inference, 0.3=fallback
"""

import csv
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER = os.path.join(ROOT, "datasets", "symbols", "emoji_master.csv")
OUTPUT = os.path.join(ROOT, "datasets", "symbols", "emoji_auto_mapped.csv")

# ══════════════════════════════════════════════════════════
# CANONICAL MAPS (from Puranas, tradition, textual sources)
# ══════════════════════════════════════════════════════════

# Direct vahana/deity associations (TRADITIONAL attestation)
VAHANA_MAP = {
    "elephant": {"graha": "guru", "element": "earth", "layer": "S1", "varna": "universal", "conf": 1.0, "att": "TRADITIONAL"},
    "eagle": {"graha": "surya", "element": "fire", "layer": "S1", "varna": "universal", "conf": 1.0, "att": "TRADITIONAL"},
    "peacock": {"graha": "mangala", "element": "fire", "layer": "S1", "varna": "universal", "conf": 1.0, "att": "TRADITIONAL"},
    "snake": {"graha": "rahu", "element": "water", "layer": "S1", "varna": "universal", "conf": 1.0, "att": "TRADITIONAL"},
    "cow": {"graha": "chandra", "element": "earth", "layer": "S0", "varna": "universal", "conf": 1.0, "att": "TRADITIONAL"},
    "horse": {"graha": "ketu", "element": "fire", "layer": "S1", "varna": "universal", "conf": 1.0, "att": "TRADITIONAL"},
    "lion": {"graha": "surya", "element": "fire", "layer": "S1", "varna": "kshatriya", "conf": 1.0, "att": "TRADITIONAL"},
    "tiger": {"graha": "mangala", "element": "fire", "layer": "S1", "varna": "kshatriya", "conf": 1.0, "att": "TRADITIONAL"},
    "turtle": {"graha": "shani", "element": "water", "layer": "S1", "varna": "universal", "conf": 1.0, "att": "TRADITIONAL"},
    "swan": {"graha": "guru", "element": "air", "layer": "S1", "varna": "brahmana", "conf": 1.0, "att": "TRADITIONAL"},
    "owl": {"graha": "shani", "element": "ether", "layer": "S1", "varna": "universal", "conf": 0.9, "att": "TRADITIONAL"},
    "monkey": {"graha": "mangala", "element": "air", "layer": "S6", "varna": "universal", "conf": 1.0, "att": "TRADITIONAL"},
    "rat": {"graha": "budha", "element": "earth", "layer": "S1", "varna": "universal", "conf": 1.0, "att": "TRADITIONAL"},
    "buffalo": {"graha": "shani", "element": "earth", "layer": "S1", "varna": "universal", "conf": 0.9, "att": "TRADITIONAL"},
    "fish": {"graha": "chandra", "element": "water", "layer": "S1", "varna": "universal", "conf": 1.0, "att": "TRADITIONAL"},
    "deer": {"graha": "chandra", "element": "earth", "layer": "S5", "varna": "universal", "conf": 0.8, "att": "SYNTHESIS"},
    "parrot": {"graha": "shukra", "element": "air", "layer": "S2", "varna": "universal", "conf": 0.8, "att": "TRADITIONAL"},
    "rabbit": {"graha": "chandra", "element": "earth", "layer": "S5", "varna": "universal", "conf": 0.7, "att": "SYNTHESIS"},
    "dog": {"graha": "rahu", "element": "air", "layer": "S5", "varna": "universal", "conf": 0.8, "att": "SYNTHESIS"},
    "cat": {"graha": "rahu", "element": "air", "layer": "S5", "varna": "universal", "conf": 0.7, "att": "SYNTHESIS"},
    "crocodile": {"graha": "mangala", "element": "water", "layer": "S5", "varna": "universal", "conf": 0.8, "att": "TRADITIONAL"},
}

# Rasa mapping for food keywords
RASA_MAP = {
    "sweet": {"rasa": "madhura", "dosha": "kapha", "graha": "shukra"},
    "honey": {"rasa": "madhura", "dosha": "kapha", "graha": "guru"},
    "sugar": {"rasa": "madhura", "dosha": "kapha", "graha": "shukra"},
    "cake": {"rasa": "madhura", "dosha": "kapha", "graha": "shukra"},
    "chocolate": {"rasa": "madhura", "dosha": "kapha", "graha": "shukra"},
    "candy": {"rasa": "madhura", "dosha": "kapha", "graha": "shukra"},
    "ice cream": {"rasa": "madhura", "dosha": "kapha", "graha": "chandra"},
    "lemon": {"rasa": "amla", "dosha": "pitta", "graha": "surya"},
    "orange": {"rasa": "amla", "dosha": "pitta", "graha": "surya"},
    "pepper": {"rasa": "katu", "dosha": "pitta", "graha": "mangala"},
    "hot": {"rasa": "katu", "dosha": "pitta", "graha": "mangala"},
    "chili": {"rasa": "katu", "dosha": "pitta", "graha": "mangala"},
    "garlic": {"rasa": "katu", "dosha": "pitta", "graha": "mangala"},
    "ginger": {"rasa": "katu", "dosha": "pitta", "graha": "surya"},
    "coffee": {"rasa": "tikta", "dosha": "vata", "graha": "shani"},
    "tea": {"rasa": "tikta", "dosha": "vata", "graha": "budha"},
    "beer": {"rasa": "tikta", "dosha": "pitta", "graha": "rahu"},
    "wine": {"rasa": "madhura", "dosha": "pitta", "graha": "shukra"},
    "salt": {"rasa": "lavana", "dosha": "kapha", "graha": "chandra"},
    "rice": {"rasa": "madhura", "dosha": "kapha", "graha": "chandra"},
    "bread": {"rasa": "madhura", "dosha": "kapha", "graha": "budha"},
    "meat": {"rasa": "madhura", "dosha": "pitta", "graha": "mangala"},
    "egg": {"rasa": "madhura", "dosha": "kapha", "graha": "chandra"},
    "milk": {"rasa": "madhura", "dosha": "kapha", "graha": "chandra"},
    "fruit": {"rasa": "madhura", "dosha": "kapha", "graha": "shukra"},
    "vegetable": {"rasa": "kashaya", "dosha": "vata", "graha": "budha"},
    "broccoli": {"rasa": "kashaya", "dosha": "vata", "graha": "budha"},
    "corn": {"rasa": "madhura", "dosha": "kapha", "graha": "surya"},
    "mushroom": {"rasa": "kashaya", "dosha": "kapha", "graha": "shani"},
}

# Profession → varna + graha
PROFESSION_MAP = {
    "doctor": {"varna": "brahmana", "graha": "budha", "layer": "S5"},
    "teacher": {"varna": "brahmana", "graha": "guru", "layer": "S1"},
    "student": {"varna": "brahmana", "graha": "budha", "layer": "S6"},
    "scientist": {"varna": "brahmana", "graha": "budha", "layer": "S4"},
    "technolog": {"varna": "brahmana", "graha": "budha", "layer": "S4"},
    "artist": {"varna": "brahmana", "graha": "shukra", "layer": "S2"},
    "cook": {"varna": "vaishya", "graha": "mangala", "layer": "S5"},
    "farmer": {"varna": "vaishya", "graha": "chandra", "layer": "S5"},
    "mechanic": {"varna": "shudra", "graha": "mangala", "layer": "S4"},
    "factory": {"varna": "shudra", "graha": "shani", "layer": "S6"},
    "office": {"varna": "vaishya", "graha": "budha", "layer": "S6"},
    "pilot": {"varna": "kshatriya", "graha": "surya", "layer": "S4"},
    "astronaut": {"varna": "sannyasa", "graha": "ketu", "layer": "S0"},
    "police": {"varna": "kshatriya", "graha": "mangala", "layer": "S6"},
    "soldier": {"varna": "kshatriya", "graha": "mangala", "layer": "S6"},
    "judge": {"varna": "brahmana", "graha": "guru", "layer": "S3"},
    "firefighter": {"varna": "kshatriya", "graha": "mangala", "layer": "S6"},
    "construct": {"varna": "shudra", "graha": "mangala", "layer": "S4"},
    "singer": {"varna": "brahmana", "graha": "shukra", "layer": "S2"},
    "musician": {"varna": "brahmana", "graha": "shukra", "layer": "S2"},
    "detective": {"varna": "kshatriya", "graha": "mangala", "layer": "S6"},
    "nurse": {"varna": "brahmana", "graha": "chandra", "layer": "S5"},
    "king": {"varna": "kshatriya", "graha": "surya", "layer": "S1"},
    "queen": {"varna": "kshatriya", "graha": "chandra", "layer": "S1"},
    "prince": {"varna": "kshatriya", "graha": "surya", "layer": "S1"},
    "guard": {"varna": "kshatriya", "graha": "mangala", "layer": "S6"},
    "superhero": {"varna": "kshatriya", "graha": "surya", "layer": "S1"},
    "vampire": {"varna": "universal", "graha": "rahu", "layer": "S1"},
    "zombie": {"varna": "universal", "graha": "shani", "layer": "S1"},
    "mage": {"varna": "brahmana", "graha": "rahu", "layer": "S1"},
    "fairy": {"varna": "universal", "graha": "shukra", "layer": "S1"},
    "elf": {"varna": "universal", "graha": "chandra", "layer": "S1"},
    "baby": {"varna": "universal", "graha": "chandra", "layer": "S5"},
    "child": {"varna": "universal", "graha": "chandra", "layer": "S5"},
    "old": {"varna": "universal", "graha": "shani", "layer": "S6"},
    "person": {"varna": "universal", "graha": "surya", "layer": "S6"},
}

# Group → default element
GROUP_ELEMENT = {
    "Smileys & Emotion": "ether",
    "People & Body": "ether",
    "Animals & Nature": "earth",
    "Food & Drink": "earth",
    "Travel & Places": "earth",
    "Activities": "fire",
    "Objects": "earth",
    "Symbols": "ether",
    "Flags": "earth",
}

# Group → default layer
GROUP_LAYER = {
    "Smileys & Emotion": "S6",
    "People & Body": "S6",
    "Animals & Nature": "S5",
    "Food & Drink": "S5",
    "Travel & Places": "S4",
    "Activities": "S6",
    "Objects": "S4",
    "Symbols": "S3",
    "Flags": "S4",
}

# Weather/sky keywords → element
WEATHER_MAP = {
    "sun": "fire", "moon": "water", "star": "fire", "cloud": "water",
    "rain": "water", "snow": "water", "wind": "air", "tornado": "air",
    "thunder": "fire", "lightning": "fire", "rainbow": "water",
    "fog": "water", "comet": "fire", "volcano": "fire",
}

# Habitat → element for animals
HABITAT_MAP = {
    "whale": "water", "dolphin": "water", "shark": "water", "octopus": "water",
    "crab": "water", "lobster": "water", "shrimp": "water", "squid": "water",
    "blowfish": "water", "seal": "water",
    "bird": "air", "dove": "air", "duck": "air", "flamingo": "air",
    "bat": "air", "butterfly": "air", "bee": "air", "fly": "air",
    "beetle": "earth", "ant": "earth", "worm": "earth", "snail": "earth",
    "spider": "earth", "scorpion": "fire",
}


def map_emoji(emoji, name, group):
    """Map one emoji to Atlas categories. Returns dict."""
    name_l = name.lower()
    result = {
        "emoji": emoji, "unicode_name": name, "group": group,
        "graha": "", "element": GROUP_ELEMENT.get(group, "ether"),
        "layer": GROUP_LAYER.get(group, "S6"),
        "nakshatra": "", "varna": "universal",
        "rasa": "", "dosha": "", "vastu_zone": "",
        "confidence": 0.3, "method": "group_default",
        "attestation": "SYNTHESIS",
    }

    # Animals — check vahana map first
    if group == "Animals & Nature":
        for key, val in VAHANA_MAP.items():
            if key in name_l:
                result.update(val)
                result["confidence"] = val["conf"]
                result["method"] = "vahana_map"
                result["attestation"] = val["att"]
                return result
        # Habitat element
        for key, elem in HABITAT_MAP.items():
            if key in name_l:
                result["element"] = elem
                result["confidence"] = 0.5
                result["method"] = "habitat_element"
                break
        # Plants
        if any(w in name_l for w in ("flower", "blossom", "rose", "tulip", "hibiscus", "sunflower", "cherry")):
            result["graha"] = "shukra"
            result["element"] = "water"
            result["confidence"] = 0.5
            result["method"] = "plant_venus"
        elif any(w in name_l for w in ("tree", "wood", "leaf", "herb", "seedling", "cactus", "palm")):
            result["graha"] = "guru"
            result["element"] = "earth"
            result["layer"] = "S5"
            result["confidence"] = 0.5
            result["method"] = "plant_jupiter"
        # Weather
        for key, elem in WEATHER_MAP.items():
            if key in name_l:
                result["element"] = elem
                result["layer"] = "S3"
                result["confidence"] = 0.6
                result["method"] = "weather"
                if "sun" in name_l: result["graha"] = "surya"
                elif "moon" in name_l: result["graha"] = "chandra"
                elif "star" in name_l: result["graha"] = "surya"
                break

    # Food — rasa mapping
    elif group == "Food & Drink":
        for key, val in RASA_MAP.items():
            if key in name_l:
                result["rasa"] = val["rasa"]
                result["dosha"] = val["dosha"]
                result["graha"] = val["graha"]
                result["vastu_zone"] = "SE"  # kitchen
                result["confidence"] = 0.7
                result["method"] = "rasa_map"
                result["layer"] = "S5"
                return result
        # Default food
        result["graha"] = "shukra"
        result["vastu_zone"] = "SE"
        result["confidence"] = 0.4
        result["method"] = "food_default"

    # People — profession mapping
    elif group == "People & Body":
        for key, val in PROFESSION_MAP.items():
            if key in name_l:
                result.update(val)
                result["confidence"] = 0.7
                result["method"] = "profession_map"
                return result
        # Body parts
        if any(w in name_l for w in ("hand", "finger", "fist", "palm", "wave")):
            result["graha"] = "budha"
            result["layer"] = "S5"
            result["confidence"] = 0.5
            result["method"] = "body_mercury"
        elif any(w in name_l for w in ("eye", "ear", "nose", "mouth", "tongue")):
            result["graha"] = "surya"
            result["layer"] = "S5"
            result["confidence"] = 0.5
            result["method"] = "sense_sun"
        elif any(w in name_l for w in ("heart", "brain")):
            result["graha"] = "chandra"
            result["layer"] = "S5"
            result["confidence"] = 0.5
            result["method"] = "organ_moon"

    # Symbols — direct where possible
    elif group == "Symbols":
        if any(w in name_l for w in ("om", "wheel", "dharma", "peace", "yin")):
            result["graha"] = "guru"
            result["layer"] = "S0"
            result["varna"] = "sannyasa"
            result["confidence"] = 0.8
            result["method"] = "symbol_direct"
            result["attestation"] = "OBSERVED"
        elif any(w in name_l for w in ("cross", "star of david", "menorah", "church", "mosque")):
            result["graha"] = "guru"
            result["layer"] = "S1"
            result["confidence"] = 0.6
            result["method"] = "symbol_religious"
        elif any(w in name_l for w in ("arrow", "triangle", "square", "circle", "diamond")):
            result["layer"] = "S4"
            result["element"] = "ether"
            result["confidence"] = 0.5
            result["method"] = "symbol_geometry"

    # Activities
    elif group == "Activities":
        if any(w in name_l for w in ("trophy", "medal", "award", "crown")):
            result["graha"] = "surya"
            result["varna"] = "kshatriya"
            result["confidence"] = 0.6
            result["method"] = "activity_victory"
        elif any(w in name_l for w in ("art", "paint", "music", "guitar", "piano", "violin", "drum")):
            result["graha"] = "shukra"
            result["varna"] = "brahmana"
            result["layer"] = "S2"
            result["confidence"] = 0.7
            result["method"] = "activity_art"

    # Travel/Places
    elif group == "Travel & Places":
        if any(w in name_l for w in ("mountain", "volcano", "desert")):
            result["element"] = "earth"
            result["graha"] = "shani"
            result["confidence"] = 0.5
            result["method"] = "landscape_earth"
        elif any(w in name_l for w in ("ocean", "wave", "water", "river", "lake")):
            result["element"] = "water"
            result["graha"] = "chandra"
            result["confidence"] = 0.5
            result["method"] = "landscape_water"
        elif any(w in name_l for w in ("temple", "church", "mosque", "synagogue")):
            result["graha"] = "guru"
            result["layer"] = "S4"
            result["varna"] = "brahmana"
            result["confidence"] = 0.6
            result["method"] = "building_sacred"

    # Objects
    elif group == "Objects":
        if any(w in name_l for w in ("sword", "dagger", "shield", "bow")):
            result["graha"] = "mangala"
            result["varna"] = "kshatriya"
            result["element"] = "fire"
            result["confidence"] = 0.7
            result["method"] = "weapon"
        elif any(w in name_l for w in ("book", "scroll", "notebook", "pen")):
            result["graha"] = "budha"
            result["varna"] = "brahmana"
            result["confidence"] = 0.6
            result["method"] = "writing"
        elif any(w in name_l for w in ("gem", "ring", "crown", "jewel")):
            result["graha"] = "shukra"
            result["element"] = "water"
            result["confidence"] = 0.6
            result["method"] = "jewel_venus"
        elif any(w in name_l for w in ("bell", "candle", "prayer", "incense")):
            result["graha"] = "guru"
            result["varna"] = "brahmana"
            result["layer"] = "S6"
            result["confidence"] = 0.7
            result["method"] = "ritual_object"

    return result


def main():
    rows = []
    with open(MASTER, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            mapped = map_emoji(row["emoji"], row["unicode_name"], row["group"])
            rows.append(mapped)

    fields = ["emoji", "unicode_name", "group",
              "graha", "element", "layer", "nakshatra",
              "varna", "rasa", "dosha", "vastu_zone",
              "confidence", "method", "attestation"]
    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    # Stats
    methods = {}
    confs = {"high": 0, "med": 0, "low": 0}
    for r in rows:
        m = r.get("method", "?")
        methods[m] = methods.get(m, 0) + 1
        c = float(r.get("confidence", 0))
        if c >= 0.7: confs["high"] += 1
        elif c >= 0.5: confs["med"] += 1
        else: confs["low"] += 1

    print(f"mapped {len(rows)} emoji to {OUTPUT}")
    print(f"confidence: {confs}")
    print(f"methods: {sorted(methods.items(), key=lambda x: -x[1])[:10]}")


if __name__ == "__main__":
    main()
