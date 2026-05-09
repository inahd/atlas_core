"""
Run panchaloha analysis: framework prediction vs tradition's prescribed nakshatras.

THE KEY TEST:
  The Shilpa Shastra and contemporary panchang tradition prescribe a specific
  list of auspicious nakshatras for murti pratishtha (installation/casting of
  panchaloha temple murtis).

  Atlas's classical jyotish framework computes graha-compatibility scores for
  multi-metal alloys. The framework predicts certain nakshatras should be more
  favorable than others based on graha-friendship rules applied to each
  component metal of the panchaloha alloy.

  THE QUESTION: Do the framework's predictions match what the tradition
  actually prescribes?

  If YES: structural validation - the framework recovers tradition without
          being told to.
  If NO: structural correction needed - the framework's encoding has gaps.

This is the cleanest empirical test the framework can run currently.
"""

import sys
sys.path.insert(0, '/home/claude/wootz_sim')

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches

from panchaloha_alloy import (
    PANCHALOHA, ASHTADHATU, AlloyRecipe, Nakshatra,
    NAKSHATRA_LORDSHIP, MURTI_PRATISHTHA_AUSPICIOUS_NAKSHATRAS,
    INAUSPICIOUS_NAKSHATRAS, DHRUVA_NAKSHATRAS,
    predict_alloy_optimal_nakshatras, compare_framework_vs_tradition,
    assess_alloy_window,
)
from jyotish_metallurgy import Graha


def print_recipe(recipe: AlloyRecipe):
    """Print the alloy composition."""
    print(f"\n{recipe.sanskrit_name} ({recipe.name})")
    print(f"Source: {recipe.source_text}")
    print(f"\n{recipe.description}\n")
    print("Composition:")
    print(f"  {'Metal':<10} {'Sanskrit':<12} {'Graha':<10} {'Weight %':<8}")
    print("  " + "-" * 45)
    for c in recipe.components:
        print(f"  {c.metal_name:<10} {c.sanskrit_name:<12} "
              f"{c.primary_graha.value:<10} {c.weight_pct:<8}")


def plot_nakshatra_scores(predictions, recipe_name: str):
    """Plot favorability score for all 27 nakshatras."""
    nakshatras = [p['nakshatra'] for p in predictions]
    scores = [p['combined_score'] for p in predictions]
    in_tradition = [p['is_in_pratishtha_list'] for p in predictions]

    # Sort by Vedic order (not score order) for plot
    vedic_order = list(Nakshatra)
    score_by_nak = {p['nakshatra']: p for p in predictions}

    ordered_nakshatras = [n.value for n in vedic_order]
    ordered_scores = [score_by_nak[n.value]['combined_score'] for n in vedic_order]
    ordered_in_trad = [score_by_nak[n.value]['is_in_pratishtha_list'] for n in vedic_order]

    fig, ax = plt.subplots(figsize=(15, 7))

    # Color by whether it's in the tradition's auspicious list
    colors = ['#2a7a2a' if in_t else '#aa3333' for in_t in ordered_in_trad]

    # But also lighten/darken by score
    bars = ax.bar(range(len(ordered_nakshatras)), ordered_scores,
                  color=colors, alpha=0.85, edgecolor='black', linewidth=0.7)

    # Mark inauspicious nakshatras
    for i, nak in enumerate(vedic_order):
        if nak in INAUSPICIOUS_NAKSHATRAS:
            ax.annotate('✗', (i, ordered_scores[i]),
                       xytext=(0, -15) if ordered_scores[i] > 0 else (0, 5),
                       textcoords='offset points',
                       ha='center', fontsize=14, color='red', fontweight='bold')
        if nak in DHRUVA_NAKSHATRAS:
            ax.annotate('★', (i, ordered_scores[i]),
                       xytext=(0, 5) if ordered_scores[i] > 0 else (0, -15),
                       textcoords='offset points',
                       ha='center', fontsize=14, color='gold', fontweight='bold')

    ax.axhline(y=0, color='black', linewidth=0.5)
    ax.set_xticks(range(len(ordered_nakshatras)))
    ax.set_xticklabels(ordered_nakshatras, rotation=60, ha='right', fontsize=9)
    ax.set_ylabel('Framework favorability score')
    ax.set_title(f'{recipe_name} - Framework prediction vs tradition\n'
                 f'(green = in tradition\'s pratishtha list, red = not in list, '
                 f'★ = Dhruva nakshatra, ✗ = inauspicious)')
    ax.grid(True, alpha=0.3, axis='y')

    # Legend
    legend_handles = [
        mpatches.Patch(color='#2a7a2a', label='In tradition\'s auspicious list'),
        mpatches.Patch(color='#aa3333', label='Not in tradition\'s list'),
    ]
    ax.legend(handles=legend_handles, loc='lower left')

    plt.tight_layout()
    safe_name = recipe_name.lower().replace(' ', '_')
    plt.savefig(f'/home/claude/wootz_sim/panchaloha_nakshatra_predictions_{safe_name}.png',
                dpi=120, bbox_inches='tight')
    plt.close()
    print(f"Saved: panchaloha_nakshatra_predictions_{safe_name}.png")


def plot_per_component_breakdown(recipe: AlloyRecipe):
    """
    Show how each component metal's graha responds across all nakshatras.
    This visualizes WHY some nakshatras are favorable for a multi-metal alloy.
    """
    fig, ax = plt.subplots(figsize=(14, 6))

    vedic_order = list(Nakshatra)
    nak_lords = [NAKSHATRA_LORDSHIP[n] for n in vedic_order]

    # For each component, compute compatibility with each nakshatra's lord
    from jyotish_metallurgy import friendship as graha_friendship
    n_components = len(recipe.components)
    matrix = np.zeros((n_components, len(vedic_order)))

    for i, component in enumerate(recipe.components):
        for j, nak in enumerate(vedic_order):
            nak_lord = NAKSHATRA_LORDSHIP[nak]
            matrix[i, j] = graha_friendship(nak_lord, component.primary_graha)

    im = ax.imshow(matrix, cmap='RdYlGn', vmin=-1, vmax=1, aspect='auto')

    # Labels
    component_labels = [f"{c.metal_name}\n({c.primary_graha.value})"
                       for c in recipe.components]
    ax.set_yticks(range(n_components))
    ax.set_yticklabels(component_labels, fontsize=9)
    ax.set_xticks(range(len(vedic_order)))
    ax.set_xticklabels([n.value for n in vedic_order], rotation=60, ha='right', fontsize=8)

    # Annotate cells
    for i in range(n_components):
        for j in range(len(vedic_order)):
            val = matrix[i, j]
            if val == 1:
                text = "F"
            elif val == -1:
                text = "E"
            else:
                text = "N" if val == 0 else "-"
            color = "white" if abs(val) > 0.5 else "black"
            ax.text(j, i, text, ha='center', va='center',
                   color=color, fontsize=8, fontweight='bold')

    # Mark nakshatras in tradition's pratishtha list
    for j, nak in enumerate(vedic_order):
        if nak in MURTI_PRATISHTHA_AUSPICIOUS_NAKSHATRAS:
            rect = Rectangle((j - 0.5, -0.5), 1, n_components,
                            fill=False, edgecolor='blue', linewidth=2)
            ax.add_patch(rect)

    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Friendship: F=friend, N=neutral, E=enemy')

    ax.set_title(f'{recipe.name}: per-component graha compatibility across nakshatras\n'
                 f'Blue rectangles mark tradition\'s prescribed auspicious nakshatras')
    plt.tight_layout()

    safe_name = recipe.name.lower().replace(' ', '_')
    plt.savefig(f'/home/claude/wootz_sim/panchaloha_component_breakdown_{safe_name}.png',
                dpi=120, bbox_inches='tight')
    plt.close()
    print(f"Saved: panchaloha_component_breakdown_{safe_name}.png")


def main():
    print("=" * 75)
    print("PANCHALOHA ANALYSIS: Classical alloy through Atlas framework")
    print("=" * 75)

    # === Show the recipe ===
    print_recipe(PANCHALOHA)

    # === Run framework prediction ===
    print("\n" + "=" * 75)
    print("RUNNING FRAMEWORK PREDICTIONS")
    print("=" * 75)
    print("\nPredicting which nakshatras the framework considers most favorable")
    print("for panchaloha casting, using neutral baseline conditions:")
    print("  - Day: Thursday (Jupiter, generally auspicious)")
    print("  - Tithi: 10 (Dashami, very favorable)")
    print("  - Yoga: Siddha (auspicious)")
    print("  - Hora: 0 (first hora of day)")

    predictions = predict_alloy_optimal_nakshatras(
        recipe=PANCHALOHA,
        day_of_week="thursday",
        hora_index=0,
        tithi=10,
        yoga_name="Siddha",
    )

    print("\nTOP 10 framework predictions:")
    print(f"{'Rank':<5} {'Nakshatra':<22} {'Score':<8} {'Tradition?':<12}")
    print("-" * 50)
    for i, p in enumerate(predictions[:10]):
        in_trad = "✓ YES" if p['is_in_pratishtha_list'] else "✗ no"
        print(f"{i+1:<5} {p['nakshatra']:<22} {p['combined_score']:<+8.3f} {in_trad}")

    print("\nBOTTOM 5 framework predictions:")
    for i, p in enumerate(predictions[-5:]):
        in_trad = "✓ in trad" if p['is_in_pratishtha_list'] else "✗ not in trad"
        rank = len(predictions) - 4 + i
        print(f"{rank:<5} {p['nakshatra']:<22} {p['combined_score']:<+8.3f} {in_trad}")

    # === Compare framework vs tradition ===
    print("\n" + "=" * 75)
    print("COMPARISON: framework predictions vs tradition's prescriptions")
    print("=" * 75)

    comparison = compare_framework_vs_tradition(
        recipe=PANCHALOHA,
        framework_predictions=predictions,
        top_n=12,
    )

    print(f"\nTradition's prescribed auspicious nakshatras for murti pratishtha:")
    print(f"  Count: {comparison['tradition_count']}")
    print(f"  List: {', '.join([n.value for n in MURTI_PRATISHTHA_AUSPICIOUS_NAKSHATRAS])}")

    print(f"\nFramework's top {comparison['framework_top_n']} predictions:")
    print(f"  List: {', '.join([p['nakshatra'] for p in predictions[:12]])}")

    print(f"\nOVERLAP ANALYSIS:")
    print(f"  Both lists overlap on: {comparison['overlap_count']} nakshatras")
    print(f"  Precision (framework predictions in tradition): {comparison['precision']:.1%}")
    print(f"  Recall (tradition nakshatras predicted by framework): {comparison['recall']:.1%}")
    print(f"\n  Overlap: {comparison['overlap']}")
    print(f"  Framework predicted but tradition doesn't: {comparison['only_in_framework']}")
    print(f"  Tradition prescribes but framework misses: {comparison['only_in_tradition']}")

    # === Visualizations ===
    plot_nakshatra_scores(predictions, recipe_name="panchaloha")
    plot_per_component_breakdown(PANCHALOHA)

    # === Run on ashtadhatu too for comparison ===
    print("\n" + "=" * 75)
    print("ASHTADHATU (eight-metal) COMPARISON")
    print("=" * 75)
    print_recipe(ASHTADHATU)

    ashta_predictions = predict_alloy_optimal_nakshatras(
        recipe=ASHTADHATU, day_of_week="thursday", hora_index=0,
        tithi=10, yoga_name="Siddha",
    )

    ashta_comparison = compare_framework_vs_tradition(
        recipe=ASHTADHATU, framework_predictions=ashta_predictions, top_n=12,
    )

    print(f"\nAshtadhatu top 10:")
    for i, p in enumerate(ashta_predictions[:10]):
        in_trad = "✓ in trad" if p['is_in_pratishtha_list'] else "✗ not in trad"
        print(f"  #{i+1} {p['nakshatra']:<22} {p['combined_score']:<+8.3f} {in_trad}")

    print(f"\nAshtadhatu precision: {ashta_comparison['precision']:.1%}, "
          f"recall: {ashta_comparison['recall']:.1%}")

    plot_nakshatra_scores(ashta_predictions, recipe_name="ashtadhatu")
    plot_per_component_breakdown(ASHTADHATU)

    # === Interpretation ===
    print("\n" + "=" * 75)
    print("INTERPRETATION")
    print("=" * 75)

    panchaloha_match = comparison['precision']
    if panchaloha_match >= 0.7:
        verdict = "STRONG STRUCTURAL MATCH"
        meaning = ("Framework recovers tradition's prescribed nakshatras at high "
                   "rate. This is significant structural validation.")
    elif panchaloha_match >= 0.4:
        verdict = "PARTIAL MATCH"
        meaning = ("Framework partially recovers tradition's prescriptions. The "
                   "overlapping nakshatras suggest the underlying logic is captured "
                   "for some cases. The non-overlap suggests additional rules are "
                   "operating in the tradition that the current encoding misses.")
    else:
        verdict = "WEAK MATCH"
        meaning = ("Framework's predictions don't substantially align with "
                   "tradition's. This suggests significant rules are missing "
                   "from the current encoding.")

    print(f"\nPanchaloha precision: {panchaloha_match:.1%} - {verdict}")
    print(f"\n{meaning}")

    print("""
WHAT THIS TEST DEMONSTRATES:

1. The framework can take a real classical alloy recipe with documented graha
   correspondences per metal.

2. Combine those graha-correspondences with classical friendship rules to
   produce specific predictions about timing windows.

3. Compare those predictions against the tradition's own prescribed list of
   auspicious nakshatras for the same operation.

This is the framework being tested against itself - or rather, the framework's
internal consistency with the broader classical tradition's conclusions.

NEXT STEP if the match is strong: extend to ashtadhatu (8 metals), specific
deity-murti recipes (Rama, Krishna, Vishnu - each with traditional preferred
metals and timings), bhasma preparations.

NEXT STEP if the match is weak: identify which classical rules the encoding
is missing. Likely candidates: tatkalika friendship, specific deity-graha
relationships, more sophisticated tithi-yoga interactions, lunar-mansion
specific lordship beyond vimshottari.

NOTE: This test is structural, not empirical. Strong match means the
framework correctly encodes classical doctrine. It does NOT prove the
classical doctrine is empirically correct about material outcomes - only
that the framework is internally consistent with the tradition.
""")


if __name__ == '__main__':
    main()
