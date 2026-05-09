"""
Lohavada Reconstruction: applying the framework to classical alchemical procedures.

This module takes documented procedures from rasashastra texts (especially the
lohavada — metal-transformation — procedures that are not currently practiced)
and applies the Atlas framework to:

1. Identify what modern materials science would describe each procedure as producing
2. Predict optimal timing windows using the panchaloha-style framework logic
3. Map textual property descriptions to known modern materials
4. Surface the gap between traditional claim and modern interpretation

This is honest reconstruction — NOT a claim that the framework can produce gold
from base metals (no framework can; the chemistry doesn't permit it). It is
investigation of what the procedures actually produce in modern materials terms,
identifying the substances the texts may have been describing, and applying the
framework's timing logic to operations that involve specific graha-metal
combinations.

Sources:
- Rasaratnakara (Nityanatha Siddha), Rasahridayatantra
- Rasarnava (11th c., earliest extant rasashastra tantra)
- Rasaratnasamuccaya (Vagbhata, ~13th c.)
- Modern peer-reviewed analysis: Singh et al. on swarnabhasma nanostructure;
  multiple papers on parada-samskaras
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jyotish_metallurgy import Graha, friendship
from panchaloha_alloy import (
    Nakshatra, NAKSHATRA_LORDSHIP, AlloyComponent, AlloyRecipe,
    predict_alloy_optimal_nakshatras,
)


@dataclass
class TextualPropertyDescription:
    """A property described in a classical text, in original framing."""
    description: str
    sanskrit_term: Optional[str] = None
    measurable_or_qualitative: str = "qualitative"  # or "measurable"


@dataclass
class ModernMaterialMatch:
    """A modern material that may correspond to a textual description."""
    material_name: str
    chemical_formula: str
    matching_properties: List[str]
    confidence: str  # "high", "medium", "low", "speculative"
    citation: str


@dataclass
class LohavadaProcedure:
    """A classical alchemical procedure, with framework-relevant metadata."""
    name: str
    sanskrit_name: str
    source_text: str
    
    # Stage in the 18-samskara sequence
    samskara_position: Optional[int] = None
    is_deha_vada: bool = False  # True for first 8 (medicinal); False for last 10
    is_loha_vada: bool = False  # True for last 10 (alchemical/transmutation)
    
    # Operational specifics
    primary_substance: str = ""
    primary_graha: Optional[Graha] = None
    co_substances: List[str] = field(default_factory=list)
    co_substance_grahas: List[Graha] = field(default_factory=list)
    
    # Textual property descriptions
    described_properties: List[TextualPropertyDescription] = field(default_factory=list)
    described_outcome: str = ""
    
    # Modern interpretation
    modern_chemical_interpretation: str = ""
    modern_material_matches: List[ModernMaterialMatch] = field(default_factory=list)
    
    # Honest assessment
    reproducibility_status: str = ""  # "reproduced", "partial", "unreproduced", "implausible"
    gap_assessment: str = ""


# ============================================================
# Documented procedures from the rasashastra corpus
# ============================================================

# The deha-vada samskaras (1-8) - these ARE practiced and reproducible
SVEDANA = LohavadaProcedure(
    name="Svedana",
    sanskrit_name="स्वेदन",
    source_text="Rasaratnasamuccaya, Rasahridayatantra",
    samskara_position=1,
    is_deha_vada=True,
    primary_substance="mercury",
    primary_graha=Graha.BUDHA,
    co_substances=["herbal decoctions", "kanji (sour gruel)"],
    described_properties=[
        TextualPropertyDescription(
            description="mercury becomes more receptive to subsequent processing",
            sanskrit_term="mridutvam",
        ),
    ],
    described_outcome="initial purification through fomentation",
    modern_chemical_interpretation=(
        "Surface-cleaning of mercury through prolonged contact with mildly acidic "
        "(kanji) and herbal solutions. Removes surface oxide layers and trace "
        "contaminants. Modern equivalent: chemical surface preparation."
    ),
    reproducibility_status="reproduced",
    gap_assessment="No significant gap. Modern rasashastra labs reproduce reliably.",
)

JARANA = LohavadaProcedure(
    name="Jarana",
    sanskrit_name="जारणा",
    source_text="Rasahridayatantra II.6, Rasaratnasamuccaya 8",
    samskara_position=11,  # one of loha-vada samskaras
    is_loha_vada=True,
    primary_substance="mercury",
    primary_graha=Graha.BUDHA,
    co_substances=["gold (bija)", "mica (abhraka)", "sulfur (gandhaka)"],
    co_substance_grahas=[Graha.SURYA, Graha.RAHU, Graha.MANGALA],
    described_properties=[
        TextualPropertyDescription(
            description="mercury 'swallows' three times its weight of bija",
            sanskrit_term="grasta-bija",
            measurable_or_qualitative="measurable",
        ),
        TextualPropertyDescription(
            description="mercury form and weight remain unchanged",
            sanskrit_term="purvavastha-pratipannatva",
            measurable_or_qualitative="measurable",
        ),
        TextualPropertyDescription(
            description="mica also 'exhausted' in equal weight",
            measurable_or_qualitative="measurable",
        ),
        TextualPropertyDescription(
            description="sulfur exhausted in 100-1000x weight",
            measurable_or_qualitative="measurable",
        ),
    ],
    described_outcome=(
        "Mercury that has 'digested' gold/mica/sulfur, capable of subsequent "
        "transformation operations"
    ),
    modern_chemical_interpretation=(
        "AMALGAMATION CHEMISTRY. Mercury readily forms amalgams with gold "
        "(Au-Hg solid solution up to ~16 wt% Au, then forms Au2Hg, Au3Hg, etc.). "
        "The texts' description of mercury 'swallowing' gold without weight change "
        "appears to describe an idealized form of amalgam dissolution. The "
        "weight-conservation claim is testable but contradicts simple stoichiometry — "
        "if 3x gold weight is added, total weight should increase 4x. Either: "
        "(a) the texts describe gold dissolution into amalgam followed by mercury "
        "evaporation, with weight measured at different stages, or "
        "(b) the texts describe a process distinct from simple amalgamation. "
        "Modern reproduction has not validated the weight-conservation claim."
    ),
    modern_material_matches=[
        ModernMaterialMatch(
            material_name="Gold-mercury amalgam (Au-Hg solid solution)",
            chemical_formula="Au_xHg_y (variable composition)",
            matching_properties=[
                "mercury dissolves gold",
                "appears as amalgamated mass",
            ],
            confidence="high",
            citation="Standard amalgam chemistry, multiple sources",
        ),
        ModernMaterialMatch(
            material_name="Mercury sulfide (cinnabar/HgS)",
            chemical_formula="HgS",
            matching_properties=[
                "mercury combines with sulfur",
                "bright red color",
                "stable solid form",
            ],
            confidence="high",
            citation="Khedekar et al. on makaradhwaja (HgS analysis)",
        ),
    ],
    reproducibility_status="partial",
    gap_assessment=(
        "Amalgamation is real and reproducible. The specific WEIGHT-CONSERVATION "
        "claim of jarana is not independently verified by modern reproduction. "
        "Texts may be describing a more complex process than simple amalgamation, "
        "or the description may be idealized. This is a clear case where modern "
        "experimental work could test the textual claim directly."
    ),
)

RANJANA = LohavadaProcedure(
    name="Ranjana",
    sanskrit_name="रञ्जन",
    source_text="Rasarnava, Rasa Jala Nidhi vol. 1",
    samskara_position=12,
    is_loha_vada=True,
    primary_substance="processed mercury",
    primary_graha=Graha.BUDHA,
    co_substances=[
        "rakta-tailam (red oil)",
        "wax", "honey", "tallow", "blood",
        "takana (borax)", "earthworm",
        "incinerated lead (naga bhasma)",
        "oil",
    ],
    co_substance_grahas=[
        Graha.MANGALA,  # red oil — Mars
        Graha.SHANI,  # incinerated lead — Saturn
        Graha.GURU,  # honey — generally beneficial
    ],
    described_properties=[
        TextualPropertyDescription(
            description="mercury acquires deep color through processing",
            sanskrit_term="ranjita",
            measurable_or_qualitative="measurable",
        ),
        TextualPropertyDescription(
            description="becomes capable of imparting transformation to base metals",
            measurable_or_qualitative="qualitative",
        ),
    ],
    described_outcome=(
        "Colored mercury preparation said to enable 'vedha' (transformation) "
        "of base metals"
    ),
    modern_chemical_interpretation=(
        "RED COLORATION OF MERCURY COMPOUNDS. The most stable red mercury compound "
        "is alpha-HgS (cinnabar/sindoor). Alpha-HgS forms readily when mercury is "
        "combined with sulfur under appropriate conditions and is bright red with "
        "specific optical properties (high refractive index ~3.0). The "
        "'red oil' procedure with multiple organic ingredients (wax, honey, blood) "
        "creates conditions where mercury can disperse into nano-scale particles. "
        "Modern nano-gold preparations (swarnabhasma) show similar nano-scale "
        "dispersion in organic matrix. The 'transformation' claim that follows "
        "(gold from base metal) is implausible chemistry, but the intermediate "
        "RED MERCURY COMPOUND is real and corresponds to nano-cinnabar dispersions "
        "or HgS-organic composites."
    ),
    modern_material_matches=[
        ModernMaterialMatch(
            material_name="Alpha-mercury sulfide (cinnabar)",
            chemical_formula="α-HgS",
            matching_properties=[
                "bright red color",
                "stable solid",
                "high refractive index",
                "forms from Hg + S under appropriate conditions",
            ],
            confidence="high",
            citation="Standard inorganic chemistry; Khedekar 2018 makaradhwaja XRD",
        ),
        ModernMaterialMatch(
            material_name="HgS-organic nanocomposite",
            chemical_formula="HgS in organic matrix",
            matching_properties=[
                "red color",
                "dispersed in organic medium",
                "nano-scale particle size",
            ],
            confidence="medium",
            citation=(
                "Singh et al. on swarnabhasma nano-structure suggests similar "
                "nano-organic composite formation in rasashastra preparations"
            ),
        ),
    ],
    reproducibility_status="partial",
    gap_assessment=(
        "Red mercury compounds are reproducible (this is essentially makaradhwaja "
        "or sindoor chemistry). What is NOT reproducible is the subsequent claim "
        "that this preparation transforms base metals into gold. The intermediate "
        "substance is real chemistry; the claimed final outcome is not. "
        "FRAMEWORK INSIGHT: the procedure may have been describing real "
        "preparation of HgS-based functional materials whose actual properties "
        "(antimicrobial, photoactive, semiconducting) were observed and "
        "described in cosmological terms. Worth investigating: do classical "
        "ranjana preparations match modern HgS nano-functional materials?"
    ),
)

VEDHA = LohavadaProcedure(
    name="Vedha (Loha-Vedha)",
    sanskrit_name="वेध / लोह-वेध",
    source_text="Rasaratnasamuccaya, Rasarnava",
    samskara_position=16,
    is_loha_vada=True,
    primary_substance="processed mercury (after ranjana)",
    primary_graha=Graha.BUDHA,
    co_substances=["base metal (copper, lead, iron)"],
    co_substance_grahas=[Graha.MANGALA, Graha.SHANI],
    described_properties=[
        TextualPropertyDescription(
            description="base metal transforms into gold",
            sanskrit_term="dhatu-vedha",
            measurable_or_qualitative="measurable",
        ),
    ],
    described_outcome="transmutation of base metal to gold",
    modern_chemical_interpretation=(
        "TRANSMUTATION CLAIM. Modern chemistry: nuclear transmutation requires "
        "particle accelerators or nuclear reactors and is energetically prohibitive "
        "at ambient conditions. Chemical processes cannot transmute one element "
        "into another. The claim as stated is not physically possible.\n\n"
        "HOWEVER, the texts may be describing:\n"
        "(a) GILDING — covering base metal with thin gold layer via amalgamation; "
        "Hg-Au amalgam paint applied to base metal then heated drives off mercury "
        "leaving gold layer. This is the historical mercury-gilding technique used "
        "for centuries in Indian and other metallurgy.\n"
        "(b) SURFACE ALLOY FORMATION — base metal acquires gold-colored surface "
        "through diffusion or alloy formation under mercury catalysis.\n"
        "(c) APPARENT TRANSMUTATION through gold-content increase from gold "
        "originally embedded in the mercury preparation.\n\n"
        "The framework cannot validate the transmutation claim. It can identify "
        "that mercury-gilding chemistry produces visually similar outcomes "
        "(base metal becoming gold-colored) and may be what the procedure "
        "actually produced."
    ),
    modern_material_matches=[
        ModernMaterialMatch(
            material_name="Mercury-gilded base metal",
            chemical_formula="Au surface layer over Cu/Pb/Fe substrate",
            matching_properties=[
                "base metal acquires gold appearance",
                "gold layer is real (came from mercury preparation)",
                "process uses mercury as carrier/solvent",
            ],
            confidence="high",
            citation=(
                "Historical mercury-gilding (fire-gilding) was used extensively "
                "in Indian, European, and East Asian metallurgy through 19th c."
            ),
        ),
    ],
    reproducibility_status="reproducible_as_gilding_NOT_as_transmutation",
    gap_assessment=(
        "GAP: textual claim is element-level transmutation. Modern interpretation "
        "is mercury-gilding (which produces visually identical results). "
        "FRAMEWORK CANNOT VALIDATE TRANSMUTATION. It can identify that the "
        "described procedure produces GOLD-APPEARING SURFACE on base metal "
        "via real chemistry (gilding). Whether the original practitioners "
        "considered this 'real' transmutation or knew it was surface-only "
        "is a matter for textual scholarship.\n\n"
        "Worth noting: the framework's structural validation result for "
        "ashtadhatu (91.7%) suggests classical practitioners had RIGOROUS "
        "computational understanding of metal-graha relationships. They may "
        "have known surface-gilding was distinct from element-level "
        "transformation, with the latter being aspirational or theoretical "
        "while the former was operational."
    ),
)


ALL_PROCEDURES = [SVEDANA, JARANA, RANJANA, VEDHA]


# ============================================================
# Framework-based timing prediction for procedures
# ============================================================

def procedure_to_alloy_recipe(procedure: LohavadaProcedure) -> AlloyRecipe:
    """
    Convert a procedure into an alloy recipe form for use with
    predict_alloy_optimal_nakshatras().
    """
    components = [
        AlloyComponent(
            metal_name=procedure.primary_substance,
            sanskrit_name=procedure.sanskrit_name,
            primary_graha=procedure.primary_graha,
            weight_pct=50.0,  # primary
        ),
    ]
    
    # Add co-substances with their grahas, equal-weighted (cosmological purpose
    # weighting per the panchaloha analysis insight)
    n_co = len(procedure.co_substance_grahas)
    if n_co > 0:
        co_weight = 50.0 / n_co
        for sub_name, sub_graha in zip(
            procedure.co_substances[:n_co],
            procedure.co_substance_grahas
        ):
            components.append(AlloyComponent(
                metal_name=sub_name,
                sanskrit_name="",
                primary_graha=sub_graha,
                weight_pct=co_weight,
            ))
    
    return AlloyRecipe(
        name=procedure.name,
        sanskrit_name=procedure.sanskrit_name,
        source_text=procedure.source_text,
        components=components,
        description=procedure.described_outcome,
    )


def analyze_procedure_timing(procedure: LohavadaProcedure) -> List[Dict]:
    """
    Predict optimal nakshatras for performing this procedure, using the
    same framework that achieved 91.7% match for ashtadhatu.
    """
    if procedure.primary_graha is None:
        return []
    
    recipe = procedure_to_alloy_recipe(procedure)
    return predict_alloy_optimal_nakshatras(
        recipe=recipe,
        day_of_week="thursday",  # neutral baseline
        hora_index=0,
        tithi=10,
        yoga_name="Siddha",
    )


def reconstruction_report(procedure: LohavadaProcedure) -> str:
    """Generate a reconstruction report for a procedure."""
    out = []
    out.append("=" * 75)
    out.append(f"LOHAVADA RECONSTRUCTION: {procedure.name} ({procedure.sanskrit_name})")
    out.append("=" * 75)
    out.append(f"\nSource: {procedure.source_text}")
    out.append(f"Samskara position: {procedure.samskara_position}")
    out.append(f"Class: {'deha-vada (medicinal)' if procedure.is_deha_vada else 'loha-vada (alchemical)'}")
    out.append(f"Primary substance: {procedure.primary_substance} (graha: {procedure.primary_graha.value if procedure.primary_graha else 'n/a'})")
    if procedure.co_substances:
        out.append(f"Co-substances: {', '.join(procedure.co_substances)}")
    
    out.append(f"\n--- Textually Described Properties ---")
    for prop in procedure.described_properties:
        marker = "[measurable]" if prop.measurable_or_qualitative == "measurable" else "[qualitative]"
        sanskrit = f" ({prop.sanskrit_term})" if prop.sanskrit_term else ""
        out.append(f"  {marker} {prop.description}{sanskrit}")
    
    out.append(f"\n--- Described Outcome ---")
    out.append(f"  {procedure.described_outcome}")
    
    out.append(f"\n--- Modern Chemical Interpretation ---")
    out.append(f"  {procedure.modern_chemical_interpretation}")
    
    out.append(f"\n--- Modern Material Matches ---")
    for match in procedure.modern_material_matches:
        out.append(f"  • {match.material_name} ({match.chemical_formula})")
        out.append(f"    Confidence: {match.confidence}")
        out.append(f"    Matching properties: {', '.join(match.matching_properties)}")
        out.append(f"    Citation: {match.citation}")
    
    out.append(f"\n--- Reproducibility Status ---")
    out.append(f"  {procedure.reproducibility_status}")
    
    out.append(f"\n--- Gap Assessment ---")
    out.append(f"  {procedure.gap_assessment}")
    
    if procedure.primary_graha is not None:
        timing_predictions = analyze_procedure_timing(procedure)
        if timing_predictions:
            out.append(f"\n--- Framework Timing Predictions (top 5 nakshatras) ---")
            for i, pred in enumerate(timing_predictions[:5]):
                in_trad = "✓ in pratishtha tradition" if pred['is_in_pratishtha_list'] else "  not in pratishtha tradition"
                out.append(f"  #{i+1} {pred['nakshatra']:<22} {pred['combined_score']:+.3f}  {in_trad}")
    
    return "\n".join(out)
