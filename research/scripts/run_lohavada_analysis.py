"""
Run the lohavada reconstruction analysis.

For each documented procedure in the rasashastra corpus, generate:
1. The reconstruction report (textual description, modern interpretation, gap)
2. Framework timing predictions for the procedure
3. A summary visualization comparing procedures

Output: console reports + figures/lohavada_*.png
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
import numpy as np

from lohavada_reconstruction import (
    ALL_PROCEDURES, SVEDANA, JARANA, RANJANA, VEDHA,
    LohavadaProcedure, reconstruction_report, analyze_procedure_timing,
    procedure_to_alloy_recipe,
)


def plot_procedure_grahas():
    """Visualize which grahas each procedure involves."""
    from jyotish_metallurgy import Graha
    
    grahas = list(Graha)
    procs = [p for p in ALL_PROCEDURES if p.primary_graha is not None]
    
    matrix = np.zeros((len(procs), len(grahas)))
    
    for i, proc in enumerate(procs):
        # Mark primary graha
        if proc.primary_graha:
            j = grahas.index(proc.primary_graha)
            matrix[i, j] = 2  # primary
        # Mark co-substance grahas
        for co_g in proc.co_substance_grahas:
            j = grahas.index(co_g)
            if matrix[i, j] == 0:
                matrix[i, j] = 1  # co-substance
    
    fig, ax = plt.subplots(figsize=(12, 5))
    cmap = plt.cm.YlOrRd
    im = ax.imshow(matrix, cmap=cmap, vmin=0, vmax=2, aspect='auto')
    
    ax.set_xticks(range(len(grahas)))
    ax.set_xticklabels([g.value for g in grahas], rotation=45, ha='right')
    ax.set_yticks(range(len(procs)))
    ax.set_yticklabels([f"{p.name}\n({p.sanskrit_name})" for p in procs])
    
    # Annotate
    for i in range(len(procs)):
        for j in range(len(grahas)):
            val = matrix[i, j]
            if val == 2:
                text = "P"  # primary
                color = "white"
            elif val == 1:
                text = "C"  # co-substance
                color = "black"
            else:
                text = ""
                color = "black"
            if text:
                ax.text(j, i, text, ha='center', va='center',
                       color=color, fontweight='bold')
    
    ax.set_title("Lohavada Procedures: Graha Involvement\n"
                 "P = primary substance's graha, C = co-substance's graha")
    plt.tight_layout()
    plt.savefig('./lohavada_graha_involvement.png', dpi=120, bbox_inches='tight')
    plt.close()
    print("Saved: lohavada_graha_involvement.png")


def plot_reproducibility_summary():
    """Visualize reproducibility status across procedures."""
    procs = ALL_PROCEDURES
    statuses = [p.reproducibility_status for p in procs]
    
    # Convert to numeric for visualization
    status_map = {
        'reproduced': 3,
        'partial': 2,
        'reproducible_as_gilding_NOT_as_transmutation': 1,
        'unreproduced': 1,
        'implausible': 0,
    }
    numeric_status = [status_map.get(s, 1) for s in statuses]
    colors = ['#2a7a2a' if v == 3 else '#7aa72a' if v == 2 
              else '#c79520' if v == 1 else '#aa3333' for v in numeric_status]
    
    fig, ax = plt.subplots(figsize=(10, 5))
    names = [f"{p.name}\n({p.sanskrit_name})" for p in procs]
    bars = ax.barh(range(len(procs)), numeric_status, color=colors, alpha=0.85,
                   edgecolor='black', linewidth=0.7)
    
    ax.set_yticks(range(len(procs)))
    ax.set_yticklabels(names)
    ax.set_xlabel("Reproducibility status")
    ax.set_xticks([0, 1, 2, 3])
    ax.set_xticklabels(['implausible', 'unreproduced /\nas gilding', 'partial', 'reproduced'])
    ax.set_xlim(0, 3.5)
    ax.invert_yaxis()
    
    # Annotate with samskara position
    for i, p in enumerate(procs):
        if p.samskara_position:
            class_marker = "deha-vada" if p.is_deha_vada else "loha-vada" if p.is_loha_vada else ""
            ax.text(numeric_status[i] + 0.05, i,
                   f" #{p.samskara_position} ({class_marker})",
                   va='center', fontsize=8)
    
    ax.set_title("Lohavada Reconstruction: Reproducibility of Documented Procedures\n"
                 "(deha-vada = first 8 samskaras, currently practiced; "
                 "loha-vada = last 10, mostly not practiced)")
    plt.tight_layout()
    plt.savefig('./lohavada_reproducibility.png', dpi=120, bbox_inches='tight')
    plt.close()
    print("Saved: lohavada_reproducibility.png")


def main():
    print("\n" + "█" * 75)
    print("LOHAVADA RECONSTRUCTION ANALYSIS")
    print("Atlas framework applied to documented rasashastra alchemical procedures")
    print("█" * 75)
    print()
    print("This analysis takes documented procedures from rasashastra texts and")
    print("identifies what they actually produce in modern materials terms.")
    print("It does NOT validate transmutation claims (no framework can; nuclear")
    print("chemistry doesn't permit ambient-condition element transmutation).")
    print()
    print("It DOES identify:")
    print("  - Which procedures map to known modern chemistry")
    print("  - Which intermediate substances are real and reproducible")
    print("  - Where the gap is between traditional claim and modern interpretation")
    print("  - Framework's predicted optimal timing for each procedure")
    print()
    
    # Generate reconstruction reports for each procedure
    for proc in ALL_PROCEDURES:
        report = reconstruction_report(proc)
        print(report)
        print()
    
    # Generate visualizations
    print("\n" + "=" * 75)
    print("GENERATING VISUALIZATIONS")
    print("=" * 75)
    plot_procedure_grahas()
    plot_reproducibility_summary()
    
    # Summary
    print("\n" + "█" * 75)
    print("SUMMARY")
    print("█" * 75)
    print("""
The four documented procedures examined span the deha-vada/loha-vada divide:

DEHA-VADA (medicinal, currently practiced):
  - Svedana: REPRODUCED. No gap.

LOHA-VADA (alchemical, mostly not currently practiced):
  - Jarana: PARTIAL. Amalgamation chemistry is real and reproducible.
    Specific weight-conservation claim is not modernly verified.
  - Ranjana: PARTIAL. Red mercury compounds (HgS) are real and reproducible.
    The subsequent transmutation claim is not.
  - Vedha (loha-vedha): REPRODUCIBLE AS GILDING, NOT AS TRANSMUTATION.
    Mercury-gilding produces visually identical results to claimed transmutation.

CRITICAL INTERPRETATION:
The classical lohavada procedures appear to describe REAL CHEMISTRY producing
REAL INTERMEDIATE MATERIALS (amalgams, mercury sulfide, gilded surfaces) but
framed within a cosmological model that makes claims about element-level
transmutation that the chemistry does not support.

This is consistent with the panchaloha structural validation finding:
classical practitioners had rigorous understanding of metal-graha relationships
(91.7% computational match with prescribed nakshatras). They likely knew the
distinction between surface-gilding and element-level transmutation. The
'transmutation' framing may have been:
  (a) Theoretical/aspirational (the goal-state, never achieved)
  (b) Symbolic/ritual (transformation of the practitioner via the work)
  (c) Surface-level operational (gilding, described in cosmological terms)

The framework can identify what the procedures actually produced. It cannot
resolve which interpretation is correct without textual scholarship and
experimental work.

WHAT THIS GIVES ATLAS:
A registry of documented procedures with:
  - Modern chemical interpretation
  - Material matches with confidence levels
  - Honest reproducibility status
  - Framework timing predictions for any procedure that could be reproduced

This is reconstruction, not validation. It identifies what's been lost
(the operational protocols), what's preserved (the deha-vada line), and
where the gaps are between traditional description and modern chemistry.

For substances "lost from past yugas" — this is the framework's honest answer:
many described substances are recoverable as real chemistry under modern
interpretation. Some are known modern materials with traditional cosmological
framing. Some are aspirational/symbolic and don't correspond to specific
materials. The framework can sort them into these categories.
""")


if __name__ == '__main__':
    main()
