"""
Run extended recovery model analysis: Aranmula kannadi + Iron Pillar of Delhi.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
import numpy as np

from extended_recovery_models import (
    EXTENDED_RECOVERY_PROCEDURES, ARANMULA_KANNADI, IRON_PILLAR_DELHI,
    reconstruction_report_with_timing,
)
from lohavada_reconstruction import ALL_PROCEDURES as LOHAVADA_PROCEDURES


def plot_combined_recovery_landscape():
    """
    Visualize all recovery cases (lohavada + extended) on one plot showing
    reproducibility status and reproducibility-vs-graha-complexity.
    """
    all_procs = LOHAVADA_PROCEDURES + EXTENDED_RECOVERY_PROCEDURES

    status_map = {
        'reproduced': 3,
        'partial': 2,
        'reproducible_as_gilding_NOT_as_transmutation': 1,
        'unreproduced': 1,
        'implausible': 0,
    }

    # Bar plot of reproducibility
    fig, ax = plt.subplots(figsize=(11, 6))
    names = [p.name for p in all_procs]
    statuses = [p.reproducibility_status for p in all_procs]
    numeric = [status_map.get(s, 1) for s in statuses]
    colors = []
    for v in numeric:
        if v == 3:
            colors.append('#2a7a2a')
        elif v == 2:
            colors.append('#7aa72a')
        elif v == 1:
            colors.append('#c79520')
        else:
            colors.append('#aa3333')

    ax.barh(range(len(all_procs)), numeric, color=colors, alpha=0.85,
            edgecolor='black', linewidth=0.7)
    ax.set_yticks(range(len(all_procs)))
    ax.set_yticklabels(names)
    ax.set_xlabel("Reproducibility status")
    ax.set_xticks([0, 1, 2, 3])
    ax.set_xticklabels(['implausible', 'partial /\nas gilding', 'partial', 'reproduced'])
    ax.set_xlim(0, 3.5)
    ax.invert_yaxis()

    # Annotate with type
    type_map = {}
    for p in LOHAVADA_PROCEDURES:
        type_map[p.name] = "lohavada"
    for p in EXTENDED_RECOVERY_PROCEDURES:
        type_map[p.name] = "metallurgical"

    for i, p in enumerate(all_procs):
        ax.text(numeric[i] + 0.05, i,
               f" [{type_map[p.name]}] {p.primary_graha.value if p.primary_graha else ''}",
               va='center', fontsize=8)

    ax.set_title("Atlas Recovery Models: Combined Landscape\n"
                 "(lohavada = mercury-based alchemy; metallurgical = "
                 "physical-chemistry recovery cases)")
    plt.tight_layout()
    plt.savefig('./recovery_landscape_combined.png', dpi=120, bbox_inches='tight')
    plt.close()
    print("Saved: recovery_landscape_combined.png")


def main():
    print("\n" + "█" * 75)
    print("EXTENDED RECOVERY MODELS")
    print("Aranmula delta bronze + Iron Pillar of Delhi")
    print("█" * 75)
    print()
    print("Following the same recovery-model pattern as lohavada_reconstruction.py,")
    print("but applied to two physically tractable Indian metallurgical traditions:")
    print()
    print("  1. ARANMULA KANNADI - delta high-tin bronze (Cu31Sn8, 32.6% tin)")
    print("     Status: PRESERVED (single-family workshop in Kerala)")
    print("     Two-graha alloy: copper (Mangala) + tin (Guru)")
    print()
    print("  2. IRON PILLAR OF DELHI - high-phosphorus wrought iron (P 0.11%)")
    print("     Status: REPRODUCIBLE chemistry, well-documented mechanism")
    print("     Single-graha (iron = Shani) with phosphorus-induced microstructure")
    print()
    print("Different from lohavada because both are physically tractable -")
    print("framework's contribution is different: not 'what was the procedure")
    print("producing' but 'how does timing affect known chemistry outcomes'.")
    print()

    for proc in EXTENDED_RECOVERY_PROCEDURES:
        report = reconstruction_report_with_timing(proc)
        print(report)
        print()

    print("\n" + "=" * 75)
    print("GENERATING COMBINED VISUALIZATION")
    print("=" * 75)
    plot_combined_recovery_landscape()

    print("\n" + "█" * 75)
    print("WHAT THIS GIVES ATLAS")
    print("█" * 75)
    print("""
Six recovery cases now in the registry:

LOHAVADA (mercury-based, descriptive recovery):
  - Svedana (deha-vada, reproduced)
  - Jarana (loha-vada, partial - amalgamation real, weight conservation not)
  - Ranjana (loha-vada, partial - HgS real, transmutation not)
  - Vedha (loha-vada, reproducible only as gilding)

METALLURGICAL (physical, predictive recovery):
  - Aranmula kannadi (preserved tradition, validation against current outputs)
  - Iron Pillar of Delhi (reproducible chemistry, timing-microstructure predictions)

PATTERN: The framework's contribution shifts depending on case type.

For LOST procedures (lohavada): framework helps identify what they actually
produced in modern materials terms, sorting claim from chemistry.

For PRESERVED but threatened (Aranmula): framework provides predictions
that can be validated against existing practitioner outputs - and creates
preservation-backup if the lineage breaks.

For REPRODUCIBLE chemistry (Iron Pillar): framework predicts timing-effects
on known microstructure mechanisms - testable on small-scale modern samples.

This matches the "fragmented encyclopedia of potential" framing - Atlas
accumulates these cases as reference points that practitioners and
researchers can consult, not as a finished system that claims to recover
all lost substances. Each case is a discrete encoded unit with its own
reproducibility status, chemistry, and gap assessment.

NEXT NATURAL CASES (for future work):
  - Wootz Damascus steel (lost, partially recovered by Verhoeven/Pendray)
  - Tamahagane (Japanese, preserved - NBTHK records)
  - Bell-bronze acoustic specifics (preserved, acoustically measurable)
  - Yashada-bhasma (preserved, nano-measurements available)
  - Rasaratnakara specific compounds (mostly lost, varies by compound)
  - Greek/Hellenistic alchemy (cross-tradition test)

Each is a separate encoded entry following the same pattern. Atlas
becomes a registry of recovery-model cases over time, each with its own
status and assessment.
""")


if __name__ == '__main__':
    main()
