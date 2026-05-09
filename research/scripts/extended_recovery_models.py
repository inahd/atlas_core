"""
Extended Recovery Models: Aranmula kannadi and Iron Pillar of Delhi.

Applies the same recovery-model pattern as lohavada_reconstruction.py to two
additional Indian metallurgical traditions:

1. ARANMULA KANNADI - delta high-tin bronze mirror (Cu31Sn8, 32.6% tin)
   - Partially preserved: single workshop family in Kerala still making them
   - Studied by Sharada Srinivasan, NIAS Bangalore
   - Continuous use from Iron Age megalithic cultures to present
   - Two-graha alloy: copper (Mangala) + tin (Guru)

2. IRON PILLAR OF DELHI - Gupta period c.400 CE
   - High-phosphorus wrought iron (P ~0.11%, ~10x modern steel)
   - Three-stage misawite protective layer formation
   - Reproducible in principle: P-rich iron is tractable modern metallurgy
   - Primary research: R. Balasubramaniam (IIT Kanpur)
   - Single-graha (iron = Shani) with phosphorus-induced microstructure

These two cases demonstrate framework applicability across the spectrum:
- Aranmula: PRESERVED tradition, validation against current outputs possible
- Iron Pillar: REPRODUCIBLE chemistry, framework predicts timing effects on
  microstructure / P-segregation that could be tested experimentally

Different from lohavada because both are physically tractable - the question
isn't "what was the procedure actually producing" (we know) but "how does
classical timing prescription map to known chemistry effects."

Sources:
- Srinivasan S. (1997, 2007, 2013, 2023) - Aranmula and high-tin bronze papers
- Glover I. (1992) - field documentation of Kerala mirror making
- Balasubramaniam R. (2000) Corrosion Science 42:2103-2129 - Iron Pillar
- Wikipedia: Iron pillar of Delhi (corrosion mechanism summary)
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
from lohavada_reconstruction import (
    LohavadaProcedure, TextualPropertyDescription, ModernMaterialMatch,
    procedure_to_alloy_recipe, analyze_procedure_timing,
)


# ============================================================
# ARANMULA KANNADI - delta high-tin bronze mirror
# ============================================================

ARANMULA_KANNADI = LohavadaProcedure(
    name="Aranmula Kannadi",
    sanskrit_name="आरण्मुल कण्णाटि",
    source_text=(
        "Living tradition: Pathanamthitta workshops, Kerala. "
        "Documentation: Srinivasan 1997 MRS Proc 462, "
        "Srinivasan & Glover 2007, "
        "Srinivasan 2023 NIAS/CSIR-NIScPR SVASTIK Stories Vol.1"
    ),
    samskara_position=None,
    is_deha_vada=False,
    is_loha_vada=False,
    primary_substance="copper-tin delta bronze (Cu31Sn8, 32.6% tin)",
    primary_graha=Graha.MANGALA,  # copper-dominant by atom count
    co_substances=["tin (vanga)"],
    co_substance_grahas=[Graha.GURU],  # tin → Jupiter in classical Indian convention
    described_properties=[
        TextualPropertyDescription(
            description="exact 32.6% tin composition (intermetallic delta phase Cu31Sn8)",
            sanskrit_term=None,
            measurable_or_qualitative="measurable",
        ),
        TextualPropertyDescription(
            description="produces distortion-free specular reflection without silver coating",
            sanskrit_term=None,
            measurable_or_qualitative="measurable",
        ),
        TextualPropertyDescription(
            description="brittle - shatters if dropped, requires careful polishing",
            sanskrit_term=None,
            measurable_or_qualitative="measurable",
        ),
        TextualPropertyDescription(
            description="considered auspicious - traditionally one of ashtamangalyam (8 sacred items) of Kerala",
            sanskrit_term="ashtamangalyam",
            measurable_or_qualitative="qualitative",
        ),
        TextualPropertyDescription(
            description="composition tightly controlled - small deviation from 32.6% causes failure",
            measurable_or_qualitative="measurable",
        ),
    ],
    described_outcome=(
        "Specular metallic mirror with no need for silvering. The delta-phase "
        "intermetallic compound exhibits high specular reflectance due to "
        "ordered atomic structure. The exact composition is critical - the "
        "delta phase exists in a narrow compositional window."
    ),
    modern_chemical_interpretation=(
        "INTERMETALLIC PHASE METALLURGY. Cu31Sn8 is a stoichiometric "
        "intermetallic compound with ordered crystal structure (cubic, space "
        "group F-43m). Unlike random alloys, intermetallics have specific "
        "compositions and well-defined crystal structures. The delta phase's "
        "high specular reflectance comes from this ordered structure plus "
        "polishing to atomic-scale flatness.\n\n"
        "Critical factors known to modern materials science:\n"
        "- Composition window is narrow (~32-33% tin)\n"
        "- Cooling rate matters: too fast -> retained beta phase (different "
        "  properties); too slow -> peritectic decomposition\n"
        "- Quenching from ~600-700°C preserves delta phase\n"
        "- Polishing must achieve <100nm surface roughness for true specular "
        "  reflection\n\n"
        "The Aranmula tradition successfully manages all these factors "
        "empirically. The exact recipe is a closely-held family secret, "
        "passed through generations of the Vishwakarma community."
    ),
    modern_material_matches=[
        ModernMaterialMatch(
            material_name="Delta phase Cu31Sn8 intermetallic",
            chemical_formula="Cu31Sn8",
            matching_properties=[
                "32.6% tin composition exact",
                "specular reflectance ~80% in visible spectrum",
                "ordered cubic crystal structure",
                "produces distortion-free mirror images",
            ],
            confidence="high",
            citation=(
                "Srinivasan 2007 'Skilled mirror craft of intermetallic delta "
                "high-tin bronze (Cu31Sn8, 32.6% tin) from Aranmula, Kerala'"
            ),
        ),
        ModernMaterialMatch(
            material_name="Beta-phase high-tin bronze (22-24% tin)",
            chemical_formula="Cu-Sn beta solid solution",
            matching_properties=[
                "wrought-and-quenched form",
                "musical alloy with golden lustre",
                "improved tensile strength vs as-cast",
                "used for Kerala temple bells, ritual vessels",
            ],
            confidence="high",
            citation=(
                "Srinivasan 1995 J Historical Metallurgy 29(2); "
                "Srinivasan 2013 Trans Indian Inst Metals"
            ),
        ),
    ],
    reproducibility_status="reproduced",
    gap_assessment=(
        "GAP TYPE: tradition is preserved but THREATENED. The chemistry is "
        "fully understood by modern materials science. The framework's "
        "contribution here is different from lohavada:\n\n"
        "1. VALIDATION OPPORTUNITY: the Aranmula workshop family currently "
        "operates. Their casting dates can be tracked. Framework can predict "
        "which dates should produce best-quality outputs (clearest specularity, "
        "fewest casting defects) and these predictions can be validated "
        "against the workshop's own QC records over time.\n\n"
        "2. PRESERVATION VALUE: documenting the framework's predictions for "
        "this living tradition creates a knowledge-preservation backup. If "
        "the family lineage breaks, framework + Srinivasan's published "
        "documentation provides a path to restart.\n\n"
        "3. EXTENSION TO BELL-BRONZE: the same framework applies to beta-bronze "
        "(22-24% tin) used for temple bells. Bells are ACOUSTICALLY MEASURABLE - "
        "FFT analysis is cheap. Framework predictions for bell-casting could "
        "be tested by frequency/harmonic analysis of bells cast on "
        "framework-favorable vs unfavorable dates.\n\n"
        "Natural collaboration target: Sharada Srinivasan at NIAS Bangalore."
    ),
)


# ============================================================
# IRON PILLAR OF DELHI
# ============================================================

IRON_PILLAR_DELHI = LohavadaProcedure(
    name="Iron Pillar of Delhi",
    sanskrit_name="मेहरौली लौह स्तम्भ",
    source_text=(
        "Primary analysis: Balasubramaniam R. (2000) Corrosion Science "
        "42:2103-2129. Inscriptions: Chandragupta II Vikramaditya, "
        "early 5th c. CE. Originally at Udayagiri (Madhya Pradesh) "
        "or Mathura, moved to Delhi ~7 centuries ago."
    ),
    samskara_position=None,
    is_deha_vada=False,
    is_loha_vada=False,
    primary_substance="high-phosphorus wrought iron (P ~0.11%, C ~0.15%)",
    primary_graha=Graha.SHANI,  # iron = Shani in classical Indian convention
    co_substances=["phosphorus", "slag inclusions (FeO, SiO2)"],
    co_substance_grahas=[Graha.RAHU],  # phosphorus as transformative element
    described_properties=[
        TextualPropertyDescription(
            description="forge-welded from individual wrought iron pieces (~6 tons total)",
            measurable_or_qualitative="measurable",
        ),
        TextualPropertyDescription(
            description="phosphorus content ~0.11% - approximately 10x modern structural steel",
            measurable_or_qualitative="measurable",
        ),
        TextualPropertyDescription(
            description="essentially rust-free after 1600+ years exposure",
            measurable_or_qualitative="measurable",
        ),
        TextualPropertyDescription(
            description=(
                "thin protective layer of crystalline iron(III) hydrogen "
                "phosphate hydrate (FePO4·H3PO4·4H2O) at metal-rust interface"
            ),
            measurable_or_qualitative="measurable",
        ),
        TextualPropertyDescription(
            description="brittleness ('cold shortness') from high P - paradoxically the same property that protects",
            measurable_or_qualitative="measurable",
        ),
    ],
    described_outcome=(
        "Massive iron pillar with extraordinary corrosion resistance. The "
        "high phosphorus, normally a metallurgical defect, creates the "
        "very protection that has preserved it. Ancient Indian smiths either "
        "knew this empirically or selected iron ore with high P content for "
        "other reasons that happened to produce the effect."
    ),
    modern_chemical_interpretation=(
        "PHOSPHORUS-MEDIATED PASSIVATION. Modern understanding (Balasubramaniam "
        "2000, Misawa et al. earlier work):\n\n"
        "Stage 1: Initial corrosion produces lepidocrocite (γ-FeOOH) and "
        "goethite (α-FeOOH) - amorphous iron oxyhydroxides.\n\n"
        "Stage 2: Phosphorus migrates from bulk iron to metal-scale interface. "
        "The high local P concentration plus alternating wet-dry cycles "
        "produces phosphoric acid which converts amorphous corrosion products "
        "to dense δ-FeOOH (misawite) layer.\n\n"
        "Stage 3: Slow precipitation of crystalline iron hydrogen phosphate "
        "hydrate (FePO4·H3PO4·4H2O) forms continuous protective layer at "
        "metal-rust interface. This crystalline layer is impermeable to "
        "further corrosion. Crystalline form indicates great age - the "
        "precipitation is slow.\n\n"
        "Three factors required: (a) P in metal, (b) slag inclusions providing "
        "second-phase nucleation sites, (c) wet-dry environmental cycling. "
        "Delhi's monsoon climate provides factor (c). The 6-ton thermal mass "
        "prevents nighttime dew formation, paradoxically reducing corrosion "
        "by avoiding constant wetting.\n\n"
        "REPRODUCIBLE: high-P iron production is tractable modern metallurgy. "
        "Issue is brittleness - P-rich iron has reduced ductility, making "
        "modern industrial use limited."
    ),
    modern_material_matches=[
        ModernMaterialMatch(
            material_name="High-phosphorus wrought iron",
            chemical_formula="Fe with 0.11% P, 0.15% C, slag inclusions",
            matching_properties=[
                "phosphorus 10x modern structural steel",
                "wrought iron microstructure (ferrite + slag stringers)",
                "high yield strength typical of modern structural steel",
                "reduced ductility (cold shortness)",
            ],
            confidence="high",
            citation="Balasubramaniam 2000, Hadfield 1912 original analysis",
        ),
        ModernMaterialMatch(
            material_name="Misawite protective film",
            chemical_formula="δ-FeOOH (compact phase)",
            matching_properties=[
                "forms preferentially in P-rich, Cu-bearing irons",
                "compact dense form vs amorphous lepidocrocite",
                "requires alternating wet-dry conditions",
            ],
            confidence="high",
            citation="Misawa et al. (foundational research on this mechanism)",
        ),
        ModernMaterialMatch(
            material_name="Crystalline iron hydrogen phosphate hydrate",
            chemical_formula="FePO4·H3PO4·4H2O",
            matching_properties=[
                "forms slowly over centuries",
                "crystalline form is age indicator",
                "continuous impermeable layer at metal-rust interface",
                "primary corrosion-resistance agent",
            ],
            confidence="high",
            citation="Balasubramaniam 2000 Corrosion Science 42:2103-2129",
        ),
    ],
    reproducibility_status="reproduced",
    gap_assessment=(
        "GAP TYPE: chemistry is fully understood; ancient method has subtler "
        "details. The framework's contribution here:\n\n"
        "1. TIMING-MICROSTRUCTURE PREDICTION: forge-welding 6 tons of wrought "
        "iron took multiple operations over multiple days. Framework predicts "
        "which timing windows should produce most uniform P-distribution and "
        "most consistent slag-inclusion patterns. Modern reproductions could "
        "test this by producing P-rich iron pieces on framework-favorable vs "
        "unfavorable dates and comparing microstructure.\n\n"
        "2. WHY GUPTA-PERIOD SUCCESS: the framework can compute astrological "
        "conditions for the inscribed date (early 5th c. CE Chandragupta II "
        "Vikramaditya period). Were those conditions especially favorable "
        "for iron-Shani operations? This is retrospective and not strictly "
        "validatable, but the computation is tractable.\n\n"
        "3. WET-DRY CYCLE TUNING: misawite formation requires specific moisture "
        "cycling. Framework's connection to panchanga and seasonal cycles "
        "could predict which years/seasons accelerate vs retard the protective "
        "layer formation. Testable on small-scale modern P-rich iron samples.\n\n"
        "4. ROOT-CAUSE QUESTION: did Gupta smiths KNOW about phosphorus, "
        "or did they select certain iron ores for other reasons (color, "
        "smelting behavior, ritual significance) that incidentally produced "
        "high-P iron? The framework can't answer this; textual scholarship "
        "and ore-source archaeology are needed.\n\n"
        "Natural collaboration target: IIT Kanpur metallurgy department "
        "(Balasubramaniam's institutional home). Also IGNCA for Sanskrit "
        "metallurgical text scholarship."
    ),
)


# ============================================================
# Combined registry
# ============================================================

EXTENDED_RECOVERY_PROCEDURES = [ARANMULA_KANNADI, IRON_PILLAR_DELHI]


def reconstruction_report_with_timing(procedure: LohavadaProcedure) -> str:
    """Generate a reconstruction report including framework timing predictions."""
    out = []
    out.append("=" * 75)
    out.append(f"RECOVERY MODEL: {procedure.name}")
    if procedure.sanskrit_name:
        out.append(f"             ({procedure.sanskrit_name})")
    out.append("=" * 75)
    out.append(f"\nSource: {procedure.source_text}")
    out.append(f"Primary substance: {procedure.primary_substance}")
    if procedure.primary_graha:
        out.append(f"Primary graha: {procedure.primary_graha.value}")
    if procedure.co_substances:
        out.append(f"Co-substances: {', '.join(procedure.co_substances)}")

    out.append(f"\n--- Documented Properties ---")
    for prop in procedure.described_properties:
        marker = "[measurable]" if prop.measurable_or_qualitative == "measurable" else "[qualitative]"
        sanskrit = f" ({prop.sanskrit_term})" if prop.sanskrit_term else ""
        out.append(f"  {marker} {prop.description}{sanskrit}")

    out.append(f"\n--- Outcome ---")
    out.append(f"  {procedure.described_outcome}")

    out.append(f"\n--- Modern Chemical Interpretation ---")
    for line in procedure.modern_chemical_interpretation.split("\n"):
        out.append(f"  {line}")

    out.append(f"\n--- Modern Material Matches ---")
    for match in procedure.modern_material_matches:
        out.append(f"  • {match.material_name} ({match.chemical_formula})")
        out.append(f"    Confidence: {match.confidence}")
        out.append(f"    Properties: {', '.join(match.matching_properties)}")
        out.append(f"    Citation: {match.citation}")

    out.append(f"\n--- Reproducibility Status ---")
    out.append(f"  {procedure.reproducibility_status}")

    out.append(f"\n--- Gap Assessment ---")
    for line in procedure.gap_assessment.split("\n"):
        out.append(f"  {line}")

    if procedure.primary_graha is not None:
        timing_predictions = analyze_procedure_timing(procedure)
        if timing_predictions:
            out.append(f"\n--- Framework Timing Predictions (top 5 nakshatras) ---")
            for i, pred in enumerate(timing_predictions[:5]):
                in_trad = "✓ in pratishtha tradition" if pred['is_in_pratishtha_list'] else "  not in pratishtha tradition"
                out.append(f"  #{i+1} {pred['nakshatra']:<22} {pred['combined_score']:+.3f}  {in_trad}")

    return "\n".join(out)
