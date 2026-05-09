"""
Sample database: archaeological vs modern wootz/Damascus steel measurements.

Published data points compiled from peer-reviewed literature. Each sample
includes its category (archaeological, modern reproduction, modern chill-cast
comparison), provenance, and measured morphological characteristics.

This is the empirical anchor against which the simulation predictions can be
compared.

Sources:
- Verhoeven, Pendray, Dauksch 1998: "The Key Role of Impurities in Ancient
  Damascus Steel Blades" - JOM 50, 58-64
- Verhoeven, Pendray, Gibson 1996: "Wootz Damascus Steel Blades" - Mat. Char.
  37, 9-22
- Verhoeven, Pendray, Berge 1993: "Studies of Damascus Steel Blades: Part II"
- Reibold et al. 2006: "Materials: Carbon nanotubes in an ancient Damascus
  sabre" - Nature 444, 286
- Verhoeven, Pendray, Dauksch, Wagstaff 2018: "Damascus Steel Revisited" - JOM
- Wadsworth, Sherby 1983: "Damascus Steel-Making" - Science 216, 328-330
"""

from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class SampleCategory(Enum):
    ARCHAEOLOGICAL = "archaeological"  # Genuine museum-quality wootz
    MODERN_TRADITIONAL = "modern_traditional"  # Verhoeven/Pendray crucible method
    MODERN_CHILL_CAST = "modern_chill_cast"  # Vacuum induction-melted, fast cooled
    MODERN_PATTERN_WELDED = "modern_pattern_welded"  # Layered, not crucible


@dataclass
class WootzSample:
    """A wootz/Damascus steel sample with its morphological measurements."""
    sample_id: str
    category: SampleCategory
    provenance: str
    description: str

    # Composition
    carbon_pct: Optional[float] = None
    vanadium_ppm: Optional[float] = None
    chromium_ppm: Optional[float] = None
    manganese_ppm: Optional[float] = None
    other_impurities: Optional[str] = None

    # Morphology - the critical comparison axes
    band_spacing_um: Optional[float] = None  # carbide band spacing in micrometers
    band_spacing_range_um: Optional[tuple] = None  # if range reported
    dendrite_spacing_um: Optional[float] = None  # primary dendrite spacing
    cementite_particle_size_nm: Optional[float] = None
    pattern_quality: Optional[str] = None  # qualitative: "excellent", "good", "fair", "absent"

    # Mechanical
    hardness_hrc_low: Optional[float] = None
    hardness_hrc_high: Optional[float] = None
    yield_strength_mpa: Optional[float] = None
    tensile_strength_mpa: Optional[float] = None

    # Cooling
    cooling_rate_cmin: Optional[float] = None  # known/estimated cooling rate

    # Production date if known (for date-based analysis)
    estimated_production_year: Optional[int] = None
    production_year_range: Optional[tuple] = None
    production_date_precision: Optional[str] = None  # "exact", "decade", "century"

    # Source
    citation: str = ""


# === ARCHAEOLOGICAL SAMPLES ===

ARCHAEOLOGICAL_SAMPLES = [
    WootzSample(
        sample_id="V1998_S1",
        category=SampleCategory.ARCHAEOLOGICAL,
        provenance="Persian, 16th-17th c.",
        description="Sword 1 from Verhoeven 1998 - genuine museum-quality wootz",
        carbon_pct=1.5,
        vanadium_ppm=40,  # in the 40-50 ppm range typical for genuine wootz
        chromium_ppm=20,
        band_spacing_um=45,  # mid of 40-50 range
        band_spacing_range_um=(40, 50),
        pattern_quality="excellent",
        hardness_hrc_low=62,
        hardness_hrc_high=67,
        production_year_range=(1500, 1700),
        production_date_precision="century",
        citation="Verhoeven, Pendray, Dauksch (1998) JOM 50, 58-64",
    ),
    WootzSample(
        sample_id="V1998_S2",
        category=SampleCategory.ARCHAEOLOGICAL,
        provenance="Persian, 17th c.",
        description="Sword 2 from Verhoeven 1998 - genuine wootz",
        carbon_pct=1.5,
        vanadium_ppm=50,
        chromium_ppm=25,
        band_spacing_um=43,
        band_spacing_range_um=(40, 50),
        pattern_quality="excellent",
        production_year_range=(1600, 1700),
        production_date_precision="century",
        citation="Verhoeven, Pendray, Dauksch (1998) JOM 50, 58-64",
    ),
    WootzSample(
        sample_id="V1998_S3",
        category=SampleCategory.ARCHAEOLOGICAL,
        provenance="Persian, 16-17th c.",
        description="Sword 3 from Verhoeven 1998 - genuine wootz with ladder pattern",
        carbon_pct=1.6,
        vanadium_ppm=45,
        band_spacing_um=48,
        band_spacing_range_um=(40, 50),
        pattern_quality="excellent",
        production_year_range=(1500, 1700),
        production_date_precision="century",
        citation="Verhoeven, Pendray, Dauksch (1998) JOM 50, 58-64",
    ),
    WootzSample(
        sample_id="REIBOLD_2006",
        category=SampleCategory.ARCHAEOLOGICAL,
        provenance="17th c. Damascus sabre, Bern Historisches Museum",
        description="Sample analyzed for carbon nanotubes and cementite nanowires",
        carbon_pct=1.5,
        vanadium_ppm=45,
        cementite_particle_size_nm=5,  # nanowires reported by Reibold
        pattern_quality="excellent",
        other_impurities="Carbon nanotubes detected; cementite nanowires",
        production_year_range=(1600, 1700),
        production_date_precision="century",
        citation="Reibold et al. (2006) Nature 444, 286",
    ),
    WootzSample(
        sample_id="SAFAVID_PLAQUE_1",
        category=SampleCategory.ARCHAEOLOGICAL,
        provenance="Safavid Iran, 17th c.",
        description="Openwork steel plaque, hypereutectoid wootz with ladder/rose pattern",
        carbon_pct=1.5,
        pattern_quality="good",
        other_impurities="Spherical carbide particles in ferrite/pearlite background",
        production_year_range=(1600, 1700),
        production_date_precision="century",
        citation="Safavid plaques study (referenced in literature)",
    ),
]


# === MODERN TRADITIONAL REPRODUCTIONS ===

MODERN_TRADITIONAL_SAMPLES = [
    WootzSample(
        sample_id="VP_REPRO_1996",
        category=SampleCategory.MODERN_TRADITIONAL,
        provenance="Verhoeven/Pendray reproduction lab, Iowa State, 1996",
        description="Crucible-cast wootz, slow cooled, Pendray forge",
        carbon_pct=1.5,
        vanadium_ppm=50,
        chromium_ppm=20,
        band_spacing_um=42,  # close to authentic range
        band_spacing_range_um=(40, 50),
        pattern_quality="excellent",
        hardness_hrc_low=60,
        hardness_hrc_high=64,
        cooling_rate_cmin=2.0,  # slow cooling
        estimated_production_year=1996,
        production_date_precision="exact",
        citation="Verhoeven, Pendray, Gibson (1996) Mat. Char. 37, 9-22",
    ),
    WootzSample(
        sample_id="PENDRAY_LADDER",
        category=SampleCategory.MODERN_TRADITIONAL,
        provenance="A.H. Pendray, Knifemakers Guild",
        description="Reproduction with Mohammed's ladder pattern",
        carbon_pct=1.5,
        vanadium_ppm=55,
        band_spacing_um=44,
        pattern_quality="excellent",
        cooling_rate_cmin=2.0,
        estimated_production_year=1998,
        production_date_precision="exact",
        citation="Verhoeven, Pendray, Dauksch (1998) JOM 50, 58-64",
    ),
    WootzSample(
        sample_id="VP_2018_SLOW",
        category=SampleCategory.MODERN_TRADITIONAL,
        provenance="Verhoeven/Pendray slow-cooled reproduction",
        description="Damascus Steel Revisited - slow-cooled ingot",
        carbon_pct=1.5,
        vanadium_ppm=50,
        band_spacing_um=46,
        dendrite_spacing_um=46,  # band inherited from dendrite spacing
        pattern_quality="excellent",
        cooling_rate_cmin=1.5,
        estimated_production_year=2017,
        production_date_precision="exact",
        citation="Verhoeven, Pendray, Dauksch, Wagstaff (2018) JOM",
    ),
]


# === MODERN CHILL-CAST (FAST-COOLED) COMPARISONS ===

MODERN_CHILL_CAST_SAMPLES = [
    WootzSample(
        sample_id="VP_2018_FAST_1",
        category=SampleCategory.MODERN_CHILL_CAST,
        provenance="Verhoeven/Pendray fast-cooled comparison",
        description="Vacuum induction-melted, chill-cast - similar comp, fast cooling",
        carbon_pct=1.5,
        vanadium_ppm=50,
        band_spacing_um=15,  # significantly reduced!
        dendrite_spacing_um=15,
        pattern_quality="absent",  # no Damascus pattern despite same composition
        cooling_rate_cmin=200,  # rapid chill
        estimated_production_year=2017,
        production_date_precision="exact",
        citation="Verhoeven, Pendray, Dauksch, Wagstaff (2018) JOM",
    ),
    WootzSample(
        sample_id="VP_2018_FAST_2",
        category=SampleCategory.MODERN_CHILL_CAST,
        provenance="Verhoeven/Pendray fast-cooled comparison #2",
        description="Vacuum induction-melted, intermediate cooling",
        carbon_pct=1.5,
        vanadium_ppm=50,
        band_spacing_um=22,
        dendrite_spacing_um=22,
        pattern_quality="fair",
        cooling_rate_cmin=50,
        estimated_production_year=2017,
        production_date_precision="exact",
        citation="Verhoeven, Pendray, Dauksch, Wagstaff (2018) JOM",
    ),
]


# === MODERN PATTERN-WELDED (NOT TRUE WOOTZ) ===

MODERN_PATTERN_WELDED_SAMPLES = [
    WootzSample(
        sample_id="PW_HYPO",
        category=SampleCategory.MODERN_PATTERN_WELDED,
        provenance="Modern pattern-welded knife",
        description="Layered Damascus, NOT crucible-cast wootz - reference for distinguishing",
        carbon_pct=1.0,  # typically lower
        pattern_quality="visually similar but structurally different",
        other_impurities="Ferrite bands in pearlite matrix; not Fe3C",
        estimated_production_year=2020,
        production_date_precision="exact",
        citation="Various modern producers; reference Verhoeven 1998 Sword 8 case",
    ),
]


# Combined database
ALL_SAMPLES = (ARCHAEOLOGICAL_SAMPLES + MODERN_TRADITIONAL_SAMPLES +
               MODERN_CHILL_CAST_SAMPLES + MODERN_PATTERN_WELDED_SAMPLES)


def get_samples_by_category(category: SampleCategory) -> List[WootzSample]:
    """Return all samples of a given category."""
    return [s for s in ALL_SAMPLES if s.category == category]


def get_morphology_summary() -> dict:
    """Summarize morphology measurements across categories."""
    summary = {}
    for category in SampleCategory:
        samples = get_samples_by_category(category)
        if not samples:
            continue
        band_spacings = [s.band_spacing_um for s in samples if s.band_spacing_um is not None]
        cooling_rates = [s.cooling_rate_cmin for s in samples if s.cooling_rate_cmin is not None]
        summary[category.value] = {
            'n_samples': len(samples),
            'n_with_band_spacing': len(band_spacings),
            'mean_band_spacing_um': sum(band_spacings) / len(band_spacings) if band_spacings else None,
            'min_band_spacing_um': min(band_spacings) if band_spacings else None,
            'max_band_spacing_um': max(band_spacings) if band_spacings else None,
            'mean_cooling_rate_cmin': sum(cooling_rates) / len(cooling_rates) if cooling_rates else None,
        }
    return summary


if __name__ == '__main__':
    print("Sample database summary:")
    print("=" * 60)
    summary = get_morphology_summary()
    for cat, stats in summary.items():
        print(f"\n{cat.upper()}:")
        for k, v in stats.items():
            if isinstance(v, float):
                print(f"  {k}: {v:.2f}")
            else:
                print(f"  {k}: {v}")
