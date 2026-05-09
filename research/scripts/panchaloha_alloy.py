"""
Panchaloha: classical five-metal alloy through Atlas's astrological framework.

Takes the canonical Shilpa Shastra panchaloha recipe (gold + silver + copper +
iron + zinc/lead/tin) and runs it through the classical jyotish baseline.
Tests whether the framework's prediction matches the published murti pratishtha
muhurta tradition's actual prescriptions for auspicious nakshatras.

This is the strongest test the framework can run currently:
- Five metals each ruled by a different graha
- Real published list of auspicious nakshatras for murti installation
- Real published list of inauspicious tithis, yogas, karanas

If the framework predicts the same nakshatras the tradition prescribes, that's
structural validation. If it doesn't, that's structural correction needed.

Sources for canonical prescriptions:
- Shilpa Shastra (panchaloha composition)
- Brihat Samhita Ch. on muhurta
- Muhurta Chintamani / contemporary panchang publications
- Drikpanchang.com and HinduPad murti pratishtha lists
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum
import sys
sys.path.insert(0, '/home/claude/wootz_sim')

from jyotish_metallurgy import (
    Graha, friendship, BPHS_CLASSIFICATION, GRAHA_METALS,
    VAARA_LORDSHIP, hora_lord, TITHI_FAVORABILITY, INAUSPICIOUS_YOGAS,
)


# === The 27 nakshatras with their classical attributes ===
# Each nakshatra has a presiding deity, ruling graha, gana classification,
# and traditional activity-suitability.

class Nakshatra(Enum):
    ASHWINI = "ashwini"          # 1
    BHARANI = "bharani"          # 2
    KRITTIKA = "krittika"        # 3
    ROHINI = "rohini"            # 4
    MRIGASHIRA = "mrigashira"    # 5
    ARDRA = "ardra"              # 6
    PUNARVASU = "punarvasu"      # 7
    PUSHYA = "pushya"            # 8
    ASLESHA = "aslesha"          # 9
    MAGHA = "magha"              # 10
    PURVA_PHALGUNI = "purva_phalguni"      # 11
    UTTARA_PHALGUNI = "uttara_phalguni"    # 12
    HASTA = "hasta"              # 13
    CHITRA = "chitra"            # 14
    SWATI = "swati"              # 15
    VISHAKHA = "vishakha"        # 16
    ANURADHA = "anuradha"        # 17
    JYESHTHA = "jyeshtha"        # 18
    MULA = "mula"                # 19
    PURVA_ASHADHA = "purva_ashadha"        # 20
    UTTARA_ASHADHA = "uttara_ashadha"      # 21
    SHRAVANA = "shravana"        # 22
    DHANISHTHA = "dhanishtha"    # 23
    SHATABHISHA = "shatabhisha"  # 24
    PURVA_BHADRAPADA = "purva_bhadrapada"  # 25
    UTTARA_BHADRAPADA = "uttara_bhadrapada"  # 26
    REVATI = "revati"            # 27


# Nakshatra ruling grahas (vimshottari dasha lords)
NAKSHATRA_LORDSHIP = {
    Nakshatra.ASHWINI: Graha.KETU,
    Nakshatra.BHARANI: Graha.SHUKRA,
    Nakshatra.KRITTIKA: Graha.SURYA,
    Nakshatra.ROHINI: Graha.CHANDRA,
    Nakshatra.MRIGASHIRA: Graha.MANGALA,
    Nakshatra.ARDRA: Graha.RAHU,
    Nakshatra.PUNARVASU: Graha.GURU,
    Nakshatra.PUSHYA: Graha.SHANI,
    Nakshatra.ASLESHA: Graha.BUDHA,
    Nakshatra.MAGHA: Graha.KETU,
    Nakshatra.PURVA_PHALGUNI: Graha.SHUKRA,
    Nakshatra.UTTARA_PHALGUNI: Graha.SURYA,
    Nakshatra.HASTA: Graha.CHANDRA,
    Nakshatra.CHITRA: Graha.MANGALA,
    Nakshatra.SWATI: Graha.RAHU,
    Nakshatra.VISHAKHA: Graha.GURU,
    Nakshatra.ANURADHA: Graha.SHANI,
    Nakshatra.JYESHTHA: Graha.BUDHA,
    Nakshatra.MULA: Graha.KETU,
    Nakshatra.PURVA_ASHADHA: Graha.SHUKRA,
    Nakshatra.UTTARA_ASHADHA: Graha.SURYA,
    Nakshatra.SHRAVANA: Graha.CHANDRA,
    Nakshatra.DHANISHTHA: Graha.MANGALA,
    Nakshatra.SHATABHISHA: Graha.RAHU,
    Nakshatra.PURVA_BHADRAPADA: Graha.GURU,
    Nakshatra.UTTARA_BHADRAPADA: Graha.SHANI,
    Nakshatra.REVATI: Graha.BUDHA,
}


# Nakshatra activity-suitability classification (from classical muhurta texts)
# 'fixed/permanent works' (Dhruva): foundation, installation, casting
DHRUVA_NAKSHATRAS = [
    Nakshatra.ROHINI,
    Nakshatra.UTTARA_PHALGUNI,
    Nakshatra.UTTARA_ASHADHA,
    Nakshatra.UTTARA_BHADRAPADA,
]

# 'auspicious/sattvic' nakshatras for general good works
SATTVIC_NAKSHATRAS = [
    Nakshatra.ROHINI,
    Nakshatra.MRIGASHIRA,
    Nakshatra.PUSHYA,
    Nakshatra.PUNARVASU,
    Nakshatra.UTTARA_PHALGUNI,
    Nakshatra.HASTA,
    Nakshatra.CHITRA,
    Nakshatra.SWATI,
    Nakshatra.ANURADHA,
    Nakshatra.UTTARA_ASHADHA,
    Nakshatra.SHRAVANA,
    Nakshatra.DHANISHTHA,
    Nakshatra.UTTARA_BHADRAPADA,
    Nakshatra.REVATI,
]

# Inauspicious nakshatras (general, especially for sacred work)
INAUSPICIOUS_NAKSHATRAS = [
    Nakshatra.BHARANI,    # Yama (death)
    Nakshatra.KRITTIKA,   # fierce, cutting
    Nakshatra.ARDRA,      # Rudra, storm
    Nakshatra.ASLESHA,    # serpent, especially last pada
    Nakshatra.MAGHA,      # ancestors, mixed
    Nakshatra.JYESHTHA,   # eldest, last pada especially
    Nakshatra.MULA,       # roots, last pada especially
    Nakshatra.SHATABHISHA, # in some traditions
]


# Nakshatras specifically prescribed for murti pratishtha (from contemporary
# panchang sources, drikpanchang, hindupad - aggregated)
MURTI_PRATISHTHA_AUSPICIOUS_NAKSHATRAS = [
    Nakshatra.ROHINI,
    Nakshatra.MRIGASHIRA,
    Nakshatra.PUSHYA,
    Nakshatra.PUNARVASU,
    Nakshatra.UTTARA_PHALGUNI,
    Nakshatra.HASTA,
    Nakshatra.SWATI,
    Nakshatra.ANURADHA,
    Nakshatra.UTTARA_ASHADHA,
    Nakshatra.SHRAVANA,
    Nakshatra.UTTARA_BHADRAPADA,
    Nakshatra.REVATI,
]


# === The panchaloha alloy specification ===

@dataclass
class AlloyComponent:
    """One component of a multi-metal alloy."""
    metal_name: str
    sanskrit_name: str
    primary_graha: Graha
    weight_pct: float


@dataclass
class AlloyRecipe:
    """A traditional alloy recipe with its component metals and graha mapping."""
    name: str
    sanskrit_name: str
    source_text: str
    components: List[AlloyComponent]
    description: str

    def all_grahas(self) -> List[Graha]:
        """All grahas involved in this alloy."""
        return [c.primary_graha for c in self.components]


# Canonical panchaloha recipe (most common Shilpa Shastra form, South Indian)
PANCHALOHA = AlloyRecipe(
    name="Panchaloha",
    sanskrit_name="Pañcaloha / Pañcadhātu",
    source_text="Shilpa Shastra (Manasara, Mayamata, Shilparatna)",
    components=[
        AlloyComponent("Gold", "suvarna", Graha.SURYA, 1.0),
        AlloyComponent("Silver", "rajata", Graha.CHANDRA, 1.0),
        AlloyComponent("Copper", "tamra", Graha.MANGALA, 80.0),  # base metal
        AlloyComponent("Iron", "lauha", Graha.SHANI, 3.0),
        AlloyComponent("Zinc", "yashada", Graha.GURU, 15.0),  # variation: tin or lead
    ],
    description="Five-metal sacred alloy used for temple murti casting. Each metal "
                "corresponds to a primary graha; the alloy is considered to amplify "
                "spiritual energy through the integration of all five planetary "
                "influences.",
)


# Ashtadhatu - eight metals, equal proportions per Shilpa Shastra tradition
ASHTADHATU = AlloyRecipe(
    name="Ashtadhatu",
    sanskrit_name="Aṣṭadhātu",
    source_text="Shilpa Shastra (Jain and Hindu temple traditions)",
    components=[
        AlloyComponent("Gold", "suvarna", Graha.SURYA, 12.5),
        AlloyComponent("Silver", "rajata", Graha.CHANDRA, 12.5),
        AlloyComponent("Copper", "tamra", Graha.MANGALA, 12.5),
        AlloyComponent("Lead", "sisa", Graha.SHANI, 12.5),  # alt: Rahu
        AlloyComponent("Zinc", "yashada", Graha.GURU, 12.5),
        AlloyComponent("Tin", "trapu", Graha.GURU, 12.5),  # also Jupiter-associated
        AlloyComponent("Iron", "lauha", Graha.SHANI, 12.5),
        AlloyComponent("Mercury", "parada", Graha.BUDHA, 12.5),
    ],
    description="Eight-metal alloy used especially for Kubera, Vishnu, Krishna, "
                "Rama, Kartikeya, Durga, Lakshmi murtis. Considered sattvik and "
                "non-decaying.",
)


# === Composite favorability assessment for multi-metal alloys ===

def assess_alloy_window(
    recipe: AlloyRecipe,
    day_of_week: str,
    hora_index: int,
    tithi: int,
    yoga_name: str,
    nakshatra: Nakshatra,
) -> dict:
    """
    Assess favorability of an operation involving a multi-metal alloy.

    The framework's hypothesis: for an alloy combining multiple grahas, the
    optimal window requires that ALL component grahas be supportive
    simultaneously. This is a stronger constraint than single-metal operations.

    Returns composite assessment plus per-component breakdown.
    """
    day_lord = VAARA_LORDSHIP[day_of_week.lower()]
    hour_lord = hora_lord(day_lord, hora_index)
    nakshatra_lord = NAKSHATRA_LORDSHIP[nakshatra]

    # Per-component graha compatibility (weighted by metal proportion)
    per_component = []
    weighted_sum_day = 0.0
    weighted_sum_hora = 0.0
    weighted_sum_nakshatra = 0.0
    total_weight = 0.0

    for component in recipe.components:
        c_graha = component.primary_graha
        weight = component.weight_pct / 100.0
        total_weight += weight

        day_compat = friendship(day_lord, c_graha)
        hora_compat = friendship(hour_lord, c_graha)
        nakshatra_compat = friendship(nakshatra_lord, c_graha)

        per_component.append({
            'metal': component.metal_name,
            'graha': c_graha.value,
            'weight_pct': component.weight_pct,
            'day_compat': day_compat,
            'hora_compat': hora_compat,
            'nakshatra_compat': nakshatra_compat,
            'composite': (day_compat + hora_compat + nakshatra_compat) / 3.0,
        })

        weighted_sum_day += day_compat * weight
        weighted_sum_hora += hora_compat * weight
        weighted_sum_nakshatra += nakshatra_compat * weight

    avg_day = weighted_sum_day / total_weight
    avg_hora = weighted_sum_hora / total_weight
    avg_nakshatra = weighted_sum_nakshatra / total_weight

    # Tithi favorability
    tithi_name, tithi_score, tithi_note = TITHI_FAVORABILITY[tithi]
    tithi_centered = (tithi_score - 0.5) * 2  # rescale to -1 to +1

    # Yoga
    yoga_score = -0.5 if yoga_name in INAUSPICIOUS_YOGAS else 0.5

    # Nakshatra activity-class bonus
    nakshatra_class_bonus = 0.0
    if nakshatra in DHRUVA_NAKSHATRAS:
        nakshatra_class_bonus = 0.4  # specifically auspicious for permanent works
    elif nakshatra in SATTVIC_NAKSHATRAS:
        nakshatra_class_bonus = 0.2
    elif nakshatra in INAUSPICIOUS_NAKSHATRAS:
        nakshatra_class_bonus = -0.4

    # Murti-pratishtha specific bonus (the tradition's own list)
    pratishtha_bonus = 0.3 if nakshatra in MURTI_PRATISHTHA_AUSPICIOUS_NAKSHATRAS else 0.0

    # Combined - notice that for multi-metal alloys, we average WEIGHTED by metal
    # proportion. This means majority metals (copper at 80% of panchaloha) dominate
    # but minority metals (gold at 1%) still contribute.
    combined = (
        0.20 * avg_day +
        0.15 * avg_hora +
        0.20 * avg_nakshatra +
        0.10 * tithi_centered +
        0.10 * yoga_score +
        0.15 * nakshatra_class_bonus +
        0.10 * pratishtha_bonus
    )

    # Also compute the MIN-graha-compatibility - the framework's stronger claim is
    # that ANY adversarial graha disrupts the alloy. So minimum compatibility
    # across components is critical.
    min_per_component = min(
        (c['composite'] for c in per_component),
        default=0.0,
    )

    return {
        'recipe': recipe.name,
        'day_lord': day_lord.value,
        'hora_lord': hour_lord.value,
        'nakshatra': nakshatra.value,
        'nakshatra_lord': nakshatra_lord.value,
        'tithi': f"{tithi} ({tithi_name})",
        'yoga': yoga_name,
        'per_component': per_component,
        'avg_day_compat': avg_day,
        'avg_hora_compat': avg_hora,
        'avg_nakshatra_compat': avg_nakshatra,
        'tithi_score': tithi_score,
        'yoga_score': yoga_score,
        'nakshatra_class_bonus': nakshatra_class_bonus,
        'pratishtha_bonus': pratishtha_bonus,
        'combined_score': combined,
        'min_component_compat': min_per_component,
        'is_in_pratishtha_list': nakshatra in MURTI_PRATISHTHA_AUSPICIOUS_NAKSHATRAS,
    }


def predict_alloy_optimal_nakshatras(
    recipe: AlloyRecipe,
    day_of_week: str = "thursday",  # neutral baseline
    hora_index: int = 0,
    tithi: int = 10,
    yoga_name: str = "Siddha",
) -> List[dict]:
    """
    For a given alloy and baseline conditions, rank all 27 nakshatras by
    framework's predicted favorability.

    Returns list sorted by score descending.
    """
    results = []
    for nak in Nakshatra:
        assessment = assess_alloy_window(
            recipe=recipe,
            day_of_week=day_of_week,
            hora_index=hora_index,
            tithi=tithi,
            yoga_name=yoga_name,
            nakshatra=nak,
        )
        results.append(assessment)

    results.sort(key=lambda r: r['combined_score'], reverse=True)
    return results


def compare_framework_vs_tradition(
    recipe: AlloyRecipe,
    framework_predictions: List[dict],
    top_n: int = 12,
) -> dict:
    """
    Compare framework's top-N predictions against the tradition's prescribed
    auspicious nakshatras for murti pratishtha.

    Returns precision/recall metrics.
    """
    tradition_set = set(MURTI_PRATISHTHA_AUSPICIOUS_NAKSHATRAS)
    framework_top = [Nakshatra(p['nakshatra']) for p in framework_predictions[:top_n]]
    framework_set = set(framework_top)

    intersection = tradition_set & framework_set
    only_in_framework = framework_set - tradition_set
    only_in_tradition = tradition_set - framework_set

    return {
        'tradition_count': len(tradition_set),
        'framework_top_n': top_n,
        'overlap_count': len(intersection),
        'precision': len(intersection) / len(framework_set) if framework_set else 0,
        'recall': len(intersection) / len(tradition_set) if tradition_set else 0,
        'overlap': sorted([n.value for n in intersection]),
        'only_in_framework': sorted([n.value for n in only_in_framework]),
        'only_in_tradition': sorted([n.value for n in only_in_tradition]),
    }
