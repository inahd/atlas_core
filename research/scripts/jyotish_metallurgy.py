"""
Classical Jyotish Metallurgical Baseline.

Establishes the graha-metal correspondences, friendship-enmity relations, and
timing-window calculations from classical Indian astrology and rasaśāstra
texts. This is the framework wootz (and other metals) operations fit within.

Sources:
- Brihat Parashara Hora Shastra (BPHS): chapters on graha characters, dhatu/moola/jeeva
  classification, friendships and enmities
- Brihat Samhita: Varahamihira's encyclopedia, including chapters on metals, omens
- Rasaratna-Samuccaya: graha-metal correspondences in rasaśāstra
- Traditional consensus on graha-metal pairings (with noted variations between
  Indian and Western alchemical traditions)

The classical Indian convention differs from Western alchemy in several ways:
- BPHS classifies grahas as Dhatu (metals/minerals), Jeeva (living beings), or
  Moola (roots/plants). Mars, Saturn, Rahu, and Moon are Dhatu; Sun, Mercury,
  Jupiter, Ketu are Jeeva; Venus is Moola.
- Specific metal correspondences vary between sources but the most common
  classical Indian set is encoded here.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum
import numpy as np


class Graha(Enum):
    """The nine grahas of jyotish."""
    SURYA = "surya"      # Sun
    CHANDRA = "chandra"  # Moon
    MANGALA = "mangala"  # Mars
    BUDHA = "budha"      # Mercury
    GURU = "guru"        # Jupiter (Brihaspati)
    SHUKRA = "shukra"    # Venus
    SHANI = "shani"      # Saturn
    RAHU = "rahu"        # North node
    KETU = "ketu"        # South node


class DhatuClass(Enum):
    """BPHS three-fold classification."""
    DHATU = "dhatu"    # Metals/minerals
    JEEVA = "jeeva"    # Living beings
    MOOLA = "moola"    # Roots/plants


# BPHS Chapter 3 dhatu/jeeva/moola classification
BPHS_CLASSIFICATION = {
    Graha.SURYA: DhatuClass.JEEVA,
    Graha.CHANDRA: DhatuClass.DHATU,
    Graha.MANGALA: DhatuClass.DHATU,
    Graha.BUDHA: DhatuClass.JEEVA,
    Graha.GURU: DhatuClass.JEEVA,
    Graha.SHUKRA: DhatuClass.MOOLA,
    Graha.SHANI: DhatuClass.DHATU,
    Graha.RAHU: DhatuClass.DHATU,
    Graha.KETU: DhatuClass.JEEVA,
}


# Classical Indian graha-metal correspondences
# Note: variations exist; this is the most common classical mapping
GRAHA_METALS = {
    Graha.SURYA: {
        "primary": "gold (suvarna)",
        "secondary": ["copper (tamra) — fire-element shared"],
        "cosmological_signature": "solar charge, central authority, tejas",
    },
    Graha.CHANDRA: {
        "primary": "silver (rajata/raupya)",
        "secondary": ["pearl (mukta) as gem"],
        "cosmological_signature": "lunar coolness, fluidity, manas",
    },
    Graha.MANGALA: {
        "primary": "copper (tamra) [alternative tradition: gold]",
        "secondary": ["red coral (pravala) as gem"],
        "cosmological_signature": "tapas, transformation through fire, blood",
    },
    Graha.BUDHA: {
        "primary": "brass / bell-metal (kamsya)",
        "secondary": ["mercury (parada/rasa) — quicksilver, central in rasashastra",
                      "emerald (panna) as gem"],
        "cosmological_signature": "intelligence, transformation, communication",
    },
    Graha.GURU: {
        "primary": "gold (suvarna) [shared with Sun]",
        "secondary": ["yellow sapphire (pukhraj) as gem"],
        "cosmological_signature": "wisdom, expansion, sattva",
    },
    Graha.SHUKRA: {
        "primary": "silver (rajata) [shared with Moon] / platinum",
        "secondary": ["diamond (heera) as gem"],
        "cosmological_signature": "rasa, beauty, refinement",
    },
    Graha.SHANI: {
        "primary": "iron (lauha/loha)",
        "secondary": ["steel (paulada)", "blue sapphire (neelam) as gem", "lead (sisa)"],
        "cosmological_signature": "structure, time, density, hardness",
    },
    Graha.RAHU: {
        "primary": "lead (sisa) / mixed metals (often considered ashtadhatu sources)",
        "secondary": ["hessonite (gomedha) as gem"],
        "cosmological_signature": "amplification, distortion, smoke",
    },
    Graha.KETU: {
        "primary": "lead-tin alloy / mixed metals",
        "secondary": ["cat's eye (vaidurya) as gem"],
        "cosmological_signature": "dissolution, headlessness, ash",
    },
}


# BPHS friendship matrix - simplified naisargika (natural) friendships
# Values: 1 = friend, 0 = neutral, -1 = enemy
NAISARGIKA_FRIENDSHIPS: Dict[Tuple[Graha, Graha], int] = {}

# Sun's relationships
NAISARGIKA_FRIENDSHIPS[(Graha.SURYA, Graha.CHANDRA)] = 1
NAISARGIKA_FRIENDSHIPS[(Graha.SURYA, Graha.MANGALA)] = 1
NAISARGIKA_FRIENDSHIPS[(Graha.SURYA, Graha.BUDHA)] = 0  # neutral
NAISARGIKA_FRIENDSHIPS[(Graha.SURYA, Graha.GURU)] = 1
NAISARGIKA_FRIENDSHIPS[(Graha.SURYA, Graha.SHUKRA)] = -1
NAISARGIKA_FRIENDSHIPS[(Graha.SURYA, Graha.SHANI)] = -1

# Moon's relationships
NAISARGIKA_FRIENDSHIPS[(Graha.CHANDRA, Graha.MANGALA)] = 0
NAISARGIKA_FRIENDSHIPS[(Graha.CHANDRA, Graha.BUDHA)] = 1
NAISARGIKA_FRIENDSHIPS[(Graha.CHANDRA, Graha.GURU)] = 0
NAISARGIKA_FRIENDSHIPS[(Graha.CHANDRA, Graha.SHUKRA)] = 0
NAISARGIKA_FRIENDSHIPS[(Graha.CHANDRA, Graha.SHANI)] = 0

# Mars's relationships
NAISARGIKA_FRIENDSHIPS[(Graha.MANGALA, Graha.BUDHA)] = -1
NAISARGIKA_FRIENDSHIPS[(Graha.MANGALA, Graha.GURU)] = 1
NAISARGIKA_FRIENDSHIPS[(Graha.MANGALA, Graha.SHUKRA)] = 0
NAISARGIKA_FRIENDSHIPS[(Graha.MANGALA, Graha.SHANI)] = 0

# Mercury's relationships
NAISARGIKA_FRIENDSHIPS[(Graha.BUDHA, Graha.GURU)] = 0
NAISARGIKA_FRIENDSHIPS[(Graha.BUDHA, Graha.SHUKRA)] = 1
NAISARGIKA_FRIENDSHIPS[(Graha.BUDHA, Graha.SHANI)] = 1

# Jupiter's relationships
NAISARGIKA_FRIENDSHIPS[(Graha.GURU, Graha.SHUKRA)] = -1
NAISARGIKA_FRIENDSHIPS[(Graha.GURU, Graha.SHANI)] = 0

# Venus-Saturn
NAISARGIKA_FRIENDSHIPS[(Graha.SHUKRA, Graha.SHANI)] = 1

# Rahu/Ketu - generally neutral or specific to context, simplified here
NAISARGIKA_FRIENDSHIPS[(Graha.RAHU, Graha.SHANI)] = 1
NAISARGIKA_FRIENDSHIPS[(Graha.RAHU, Graha.SHUKRA)] = 1
NAISARGIKA_FRIENDSHIPS[(Graha.RAHU, Graha.BUDHA)] = 1
NAISARGIKA_FRIENDSHIPS[(Graha.RAHU, Graha.SURYA)] = -1
NAISARGIKA_FRIENDSHIPS[(Graha.RAHU, Graha.CHANDRA)] = -1
NAISARGIKA_FRIENDSHIPS[(Graha.RAHU, Graha.MANGALA)] = -1
NAISARGIKA_FRIENDSHIPS[(Graha.RAHU, Graha.GURU)] = -1
NAISARGIKA_FRIENDSHIPS[(Graha.KETU, Graha.SHANI)] = 1
NAISARGIKA_FRIENDSHIPS[(Graha.KETU, Graha.MANGALA)] = 1
NAISARGIKA_FRIENDSHIPS[(Graha.KETU, Graha.SHUKRA)] = 0
NAISARGIKA_FRIENDSHIPS[(Graha.KETU, Graha.SURYA)] = -1
NAISARGIKA_FRIENDSHIPS[(Graha.KETU, Graha.CHANDRA)] = -1
NAISARGIKA_FRIENDSHIPS[(Graha.KETU, Graha.BUDHA)] = -1
NAISARGIKA_FRIENDSHIPS[(Graha.KETU, Graha.GURU)] = -1
NAISARGIKA_FRIENDSHIPS[(Graha.RAHU, Graha.KETU)] = 1  # nodes


def friendship(g1: Graha, g2: Graha) -> int:
    """Return friendship value between two grahas (1, 0, or -1)."""
    if g1 == g2:
        return 1
    key = (g1, g2)
    rev = (g2, g1)
    if key in NAISARGIKA_FRIENDSHIPS:
        return NAISARGIKA_FRIENDSHIPS[key]
    if rev in NAISARGIKA_FRIENDSHIPS:
        return NAISARGIKA_FRIENDSHIPS[rev]
    return 0  # default neutral


# Days of week ruled by grahas
VAARA_LORDSHIP = {
    "sunday": Graha.SURYA,
    "monday": Graha.CHANDRA,
    "tuesday": Graha.MANGALA,
    "wednesday": Graha.BUDHA,
    "thursday": Graha.GURU,
    "friday": Graha.SHUKRA,
    "saturday": Graha.SHANI,
}


# Hora system (planetary hours) - sequence of graha rulership across hours of the day
# Order follows the classical Chaldean order: Sat-Jup-Mar-Sun-Ven-Mer-Moon
HORA_ORDER = [Graha.SHANI, Graha.GURU, Graha.MANGALA, Graha.SURYA,
              Graha.SHUKRA, Graha.BUDHA, Graha.CHANDRA]


def hora_lord(day_lord: Graha, hour_index: int) -> Graha:
    """
    Return the graha ruling a specific hora (planetary hour) given the day's lord.

    Hour 0 = first hour after sunrise. The first hora of any day is ruled by the
    day's lord, then the sequence cycles in Chaldean order.
    """
    start = HORA_ORDER.index(day_lord)
    return HORA_ORDER[(start + hour_index) % len(HORA_ORDER)]


# Tithi-suitability table for metal operations
# Shukla paksha (waxing) is generally favorable; Krishna paksha (waning) less so
# Specific tithis carry specific meanings
TITHI_FAVORABILITY = {
    1: ("Pratipada", 0.6, "begin small operations, not major undertakings"),
    2: ("Dvitiya", 0.7, "growth-supporting, good for new alloys"),
    3: ("Tritiya", 0.8, "auspicious for material work"),
    4: ("Chaturthi", 0.4, "Ganesha day, OK for preparation, not for completion"),
    5: ("Panchami", 0.85, "favorable for skilled metalwork"),
    6: ("Shashthi", 0.7, "Mars-influenced, good for iron/steel"),
    7: ("Saptami", 0.75, "Sun-influenced, favorable for gold work"),
    8: ("Ashtami", 0.5, "ambivalent — Shiva tithi, transformative but unstable"),
    9: ("Navami", 0.7, "Durga tithi, energy-supporting"),
    10: ("Dashami", 0.85, "very favorable for completion of operations"),
    11: ("Ekadashi", 0.4, "fasting day, not for material operations"),
    12: ("Dvadashi", 0.7, "post-Ekadashi recovery, gentle work"),
    13: ("Trayodashi", 0.8, "favorable, especially for refined work"),
    14: ("Chaturdashi", 0.45, "Shiva tithi, intense, ambivalent"),
    15: ("Purnima", 0.9, "full moon, very favorable for completion"),
    16: ("Pratipada-K", 0.55, "krishna paksha begins, energies waning"),
    17: ("Dvitiya-K", 0.6, ""),
    18: ("Tritiya-K", 0.65, ""),
    19: ("Chaturthi-K", 0.4, ""),
    20: ("Panchami-K", 0.6, ""),
    21: ("Shashthi-K", 0.55, ""),
    22: ("Saptami-K", 0.6, ""),
    23: ("Ashtami-K", 0.4, "ambivalent"),
    24: ("Navami-K", 0.55, ""),
    25: ("Dashami-K", 0.6, ""),
    26: ("Ekadashi-K", 0.4, "fasting, not for material work"),
    27: ("Dvadashi-K", 0.55, ""),
    28: ("Trayodashi-K", 0.6, ""),
    29: ("Chaturdashi-K", 0.35, "intense, often inauspicious"),
    30: ("Amavasya", 0.3, "new moon, generally inauspicious for completion"),
}


# Inauspicious yogas to flag
INAUSPICIOUS_YOGAS = ["Vyatipata", "Vaidhriti", "Parigha", "Vajra", "Vyaghata",
                     "Vishkambha", "Atiganda", "Shoola", "Ganda", "Indra"]


def assess_metal_operation_window(
    day_of_week: str,
    hora_index: int,
    tithi: int,
    yoga_name: str,
    target_metal_graha: Graha,
    practitioner_birth_grahas: Optional[List[Graha]] = None,
) -> dict:
    """
    Assess the favorability of starting a metal operation at a given moment.

    Returns a structured assessment with breakdown by factor.

    This is the classical-jyotish baseline assessment that wootz simulation
    sits within. Same logic applies whether the metal is wootz iron or
    panchaloha or any other.
    """
    day_lord = VAARA_LORDSHIP[day_of_week.lower()]
    hour_lord = hora_lord(day_lord, hora_index)

    # Day-lord compatibility with metal's graha
    day_compat = friendship(day_lord, target_metal_graha)

    # Hora-lord compatibility (more granular than day)
    hora_compat = friendship(hour_lord, target_metal_graha)

    # Tithi favorability
    tithi_name, tithi_score, tithi_note = TITHI_FAVORABILITY[tithi]

    # Yoga assessment
    yoga_score = -0.5 if yoga_name in INAUSPICIOUS_YOGAS else 0.5

    # Practitioner compatibility
    practitioner_compat = 0
    if practitioner_birth_grahas:
        compat_sum = sum(friendship(g, target_metal_graha)
                         for g in practitioner_birth_grahas)
        practitioner_compat = compat_sum / len(practitioner_birth_grahas)

    # Combined score: weighted average
    # Day lordship is the broadest variable (24 hour window)
    # Hora is finer (1 hour window)
    # Tithi is the lunar context (~24 hour window)
    # Yoga is general atmospheric quality
    combined = (
        0.25 * day_compat +
        0.25 * hora_compat +
        0.30 * (tithi_score * 2 - 1) +  # rescale 0-1 to -1 to +1
        0.10 * yoga_score +
        0.10 * practitioner_compat
    )

    return {
        'metal_graha': target_metal_graha.value,
        'metal_dhatu_class': BPHS_CLASSIFICATION[target_metal_graha].value,
        'day_lord': day_lord.value,
        'day_compatibility': day_compat,
        'hora_lord': hour_lord.value,
        'hora_compatibility': hora_compat,
        'tithi': f"{tithi} ({tithi_name})",
        'tithi_score': tithi_score,
        'tithi_note': tithi_note,
        'yoga': yoga_name,
        'yoga_score': yoga_score,
        'practitioner_compatibility': practitioner_compat,
        'combined_score': combined,
        'assessment': _interpret_score(combined),
    }


def _interpret_score(score: float) -> str:
    if score >= 0.5:
        return "highly favorable - excellent window for operation"
    elif score >= 0.2:
        return "favorable - good window with attention to detail"
    elif score >= -0.2:
        return "neutral - operation possible but no special support"
    elif score >= -0.5:
        return "challenging - significant adverse factors, exercise caution"
    else:
        return "highly inauspicious - operation strongly discouraged"


def find_optimal_windows(
    target_metal_graha: Graha,
    days_to_scan: int = 30,
    practitioner_birth_grahas: Optional[List[Graha]] = None,
) -> List[dict]:
    """
    Scan a window of days/horas and return ranked list of most favorable windows
    for the target metal operation.

    For demonstration, uses a simplified panchanga model. In production, would
    use Atlas's panchanga_engine to get real values.
    """
    days_of_week = ["sunday", "monday", "tuesday", "wednesday",
                    "thursday", "friday", "saturday"]
    yoga_options = ["Variyana", "Parigha", "Shiva", "Siddha", "Sadhya",
                    "Subha", "Sukla", "Brahma", "Aindra", "Vyatipata"]

    rng = np.random.default_rng(seed=42)
    results = []

    for day in range(days_to_scan):
        # Synthetic panchanga (would come from Atlas in production)
        dow = days_of_week[day % 7]
        # Tithi cycles 1-30 over ~30 days (simplified; real tithi runs ~24 hours)
        tithi = ((day % 30) + 1)
        # Yoga cycles roughly daily
        yoga = yoga_options[day % len(yoga_options)]

        # Try multiple horas in this day
        for hora_idx in [0, 4, 8, 12]:  # check 4 horas across the day
            assessment = assess_metal_operation_window(
                day_of_week=dow,
                hora_index=hora_idx,
                tithi=tithi,
                yoga_name=yoga,
                target_metal_graha=target_metal_graha,
                practitioner_birth_grahas=practitioner_birth_grahas,
            )
            assessment['day_offset'] = day
            assessment['hora_index'] = hora_idx
            results.append(assessment)

    # Sort by combined score
    results.sort(key=lambda r: r['combined_score'], reverse=True)
    return results
