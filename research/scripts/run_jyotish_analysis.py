"""
Run classical jyotish metallurgy analysis.

Establishes the framework that wootz (and other metals) simulations sit within.

For each metal-graha, this analysis produces:
1. The classical correspondence and dhatu-classification
2. Friendship matrix showing which grahas support its operations
3. Optimal-window scan showing predicted favorable times across a 30-day cycle
4. Connection to the wootz physical simulation - these classical assessments
   set the AstroFieldConditions parameters in the materials simulation.
"""

import sys
sys.path.insert(0, '/home/claude/wootz_sim')

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from jyotish_metallurgy import (
    Graha, DhatuClass, BPHS_CLASSIFICATION, GRAHA_METALS,
    NAISARGIKA_FRIENDSHIPS, friendship, VAARA_LORDSHIP, hora_lord,
    TITHI_FAVORABILITY, INAUSPICIOUS_YOGAS,
    assess_metal_operation_window, find_optimal_windows,
)


def print_classical_correspondences():
    """Print the graha-metal correspondence table."""
    print("=" * 70)
    print("CLASSICAL JYOTISH METAL-GRAHA CORRESPONDENCES")
    print("=" * 70)
    print()
    print("BPHS three-fold dhatu/jeeva/moola classification:")
    for graha, dhatu_class in BPHS_CLASSIFICATION.items():
        print(f"  {graha.value:10s} -> {dhatu_class.value}")
    print()
    print("Metal correspondences:")
    for graha, info in GRAHA_METALS.items():
        print(f"\n  {graha.value.upper()}:")
        print(f"    Primary metal:    {info['primary']}")
        print(f"    Secondary:        {', '.join(info['secondary'])}")
        print(f"    Cosmological:     {info['cosmological_signature']}")


def plot_friendship_matrix():
    """Render the graha friendship matrix as a heatmap."""
    grahas = list(Graha)
    n = len(grahas)
    matrix = np.zeros((n, n))
    for i, g1 in enumerate(grahas):
        for j, g2 in enumerate(grahas):
            matrix[i, j] = friendship(g1, g2)

    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(matrix, cmap='RdYlGn', vmin=-1, vmax=1, aspect='equal')

    # Labels
    labels = [g.value.capitalize() for g in grahas]
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.set_yticklabels(labels)

    # Annotate cells with friendship value
    for i in range(n):
        for j in range(n):
            val = matrix[i, j]
            if val == 1:
                text = "F"  # friend
                color = "white"
            elif val == -1:
                text = "E"  # enemy
                color = "white"
            elif val == 0 and i != j:
                text = "N"  # neutral
                color = "black"
            else:
                text = "—"
                color = "black"
            ax.text(j, i, text, ha='center', va='center',
                   color=color, fontweight='bold')

    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Friendship value (1=friend, 0=neutral, -1=enemy)')

    ax.set_title('Graha Naisargika Friendship Matrix\n(BPHS Classical)')
    ax.set_xlabel('Graha B')
    ax.set_ylabel('Graha A (relationship to B)')
    plt.tight_layout()
    plt.savefig('/home/claude/wootz_sim/jyotish_friendship_matrix.png',
                dpi=120, bbox_inches='tight')
    plt.close()
    print("Saved: jyotish_friendship_matrix.png")


def analyze_metal_windows(metal_graha: Graha, days: int = 30,
                          practitioner_grahas=None) -> list:
    """Find optimal windows for a specific metal's operations."""
    print(f"\nScanning {days}-day window for {metal_graha.value.upper()} operations...")
    windows = find_optimal_windows(
        target_metal_graha=metal_graha,
        days_to_scan=days,
        practitioner_birth_grahas=practitioner_grahas,
    )

    print(f"\nTOP 5 favorable windows for {metal_graha.value} metal operations:")
    for i, w in enumerate(windows[:5]):
        print(f"\n  #{i+1} (score: {w['combined_score']:+.3f})")
        print(f"    Day offset: +{w['day_offset']} days, Hora: {w['hora_index']}")
        print(f"    {w['day_lord'].capitalize()}'s day, {w['hora_lord'].capitalize()}'s hora")
        print(f"    Tithi: {w['tithi']} (score {w['tithi_score']:.2f})")
        print(f"    Yoga: {w['yoga']}")
        print(f"    Assessment: {w['assessment']}")

    print(f"\nBOTTOM 3 unfavorable windows:")
    for i, w in enumerate(windows[-3:]):
        print(f"\n  rank #{len(windows)-2+i} (score: {w['combined_score']:+.3f})")
        print(f"    Day offset: +{w['day_offset']} days, Hora: {w['hora_index']}")
        print(f"    {w['day_lord'].capitalize()}'s day, {w['hora_lord'].capitalize()}'s hora")
        print(f"    Tithi: {w['tithi']}, Yoga: {w['yoga']}")
        print(f"    Assessment: {w['assessment']}")

    return windows


def plot_window_distribution(windows: list, metal_name: str):
    """Plot distribution of favorability scores across the scan."""
    scores = [w['combined_score'] for w in windows]
    day_offsets = [w['day_offset'] + w['hora_index']/24.0 for w in windows]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Time series of favorability
    ax = axes[0]
    colors = ['green' if s > 0.2 else 'red' if s < -0.2 else 'gray' for s in scores]
    ax.scatter(day_offsets, scores, c=colors, alpha=0.6, s=30)
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax.axhline(y=0.5, color='green', linestyle='--', alpha=0.5, label='highly favorable')
    ax.axhline(y=0.2, color='lightgreen', linestyle='--', alpha=0.5, label='favorable')
    ax.axhline(y=-0.2, color='salmon', linestyle='--', alpha=0.5, label='challenging')
    ax.axhline(y=-0.5, color='red', linestyle='--', alpha=0.5, label='inauspicious')
    ax.set_xlabel('Day offset (with hora resolution)')
    ax.set_ylabel('Combined favorability score')
    ax.set_title(f'{metal_name} operation favorability over 30-day scan')
    ax.legend(loc='lower left', fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-1, 1)

    # Histogram of scores
    ax = axes[1]
    ax.hist(scores, bins=20, color='#4a4a8a', alpha=0.7, edgecolor='black')
    ax.axvline(x=np.mean(scores), color='red', linestyle='--',
               label=f'mean: {np.mean(scores):.3f}')
    ax.axvline(x=np.median(scores), color='green', linestyle='--',
               label=f'median: {np.median(scores):.3f}')
    ax.set_xlabel('Combined favorability score')
    ax.set_ylabel('Frequency')
    ax.set_title(f'{metal_name} window score distribution')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    safe_name = (metal_name.lower().replace(' ', '_').replace('(', '').replace(')', '')
                 .replace('/', '_').replace('\\', '_'))
    plt.savefig(f'/home/claude/wootz_sim/jyotish_windows_{safe_name}.png',
                dpi=120, bbox_inches='tight')
    plt.close()
    print(f"Saved: jyotish_windows_{safe_name}.png")


def connect_to_wootz_simulation():
    """
    Demonstrate the connection between classical jyotish assessment and the
    wootz physical simulation.

    This is the transduction layer: classical assessment values become the
    AstroFieldConditions inputs to the physics simulation.
    """
    from wootz_solidification import (
        WootzMeltConditions, AstroFieldConditions, WootzSolidificationSim
    )

    # Wootz operation - target metal is iron, which is Saturn (Shani) in classical
    target = Graha.SHANI

    print("\n" + "=" * 70)
    print("CONNECTING JYOTISH ASSESSMENT TO WOOTZ SIMULATION")
    print("=" * 70)
    print(f"\nTarget metal: iron (lauha) - ruled by {target.value.upper()}")

    # Find the most favorable and least favorable windows
    windows = find_optimal_windows(target_metal_graha=target, days_to_scan=30)
    best = windows[0]
    worst = windows[-1]

    print(f"\nBest window found (score {best['combined_score']:+.3f}):")
    print(f"  Day {best['day_offset']}, hora {best['hora_index']}")
    print(f"  {best['day_lord']}'s day, {best['hora_lord']}'s hora")
    print(f"  Tithi {best['tithi']}, yoga {best['yoga']}")

    print(f"\nWorst window found (score {worst['combined_score']:+.3f}):")
    print(f"  Day {worst['day_offset']}, hora {worst['hora_index']}")
    print(f"  {worst['day_lord']}'s day, {worst['hora_lord']}'s hora")
    print(f"  Tithi {worst['tithi']}, yoga {worst['yoga']}")

    # Translate the jyotish assessments to physics-simulation inputs
    print("\n" + "-" * 70)
    print("TRANSDUCTION TO PHYSICS SIMULATION")
    print("-" * 70)

    # Map combined_score (-1 to +1) to graha_compatibility for the physics sim
    melt = WootzMeltConditions(grid_size=128, cooling_rate_c_per_min=8.0)

    scenarios_from_jyotish = []
    for label, w in [("best_jyotish", best), ("worst_jyotish", worst)]:
        # Jyotish-derived parameters
        graha_compat = w['combined_score']
        # Inauspicious yoga -> chaotic field
        kp = 6.0 if w['yoga'] in INAUSPICIOUS_YOGAS else 1.5
        # Favorable tithi -> coherent wave field
        wave_field = (w['tithi_score'] - 0.5) * 1.4

        astro = AstroFieldConditions(
            geomagnetic_field_ut=50.0,  # baseline
            field_orientation_rad=0.0,  # arbitrary
            kp_index=kp,
            tidal_forcing=w['tithi_score'],  # tidal stronger near purnima/amavasya
            wave_field_value=wave_field,
            graha_compatibility=graha_compat,
            tithi=int(w['tithi'].split()[0]),
        )

        print(f"\n{label} -> physics inputs:")
        print(f"  graha_compatibility: {graha_compat:+.3f}")
        print(f"  kp_index: {kp:.1f}")
        print(f"  wave_field_value: {wave_field:+.3f}")
        print(f"  tidal_forcing: {w['tithi_score']:.3f}")
        print(f"  effective field: {astro.effective_field_strength():.1f} uT")

        # Run the simulation
        sim = WootzSolidificationSim(melt, astro, random_seed=42)
        sim.run(total_minutes=200.0)
        summary = sim.summary()
        print(f"  -> simulation result:")
        print(f"     band_alignment: {summary['band_alignment_score']:.4f}")
        print(f"     V std in solid: {summary['vanadium_std_in_solid_ppm']:.1f} ppm")

        scenarios_from_jyotish.append({
            'label': label,
            'jyotish_window': w,
            'astro_inputs': astro,
            'physics_summary': summary,
        })

    return scenarios_from_jyotish


def main():
    print_classical_correspondences()
    plot_friendship_matrix()

    # Analyze windows for several metals
    print("\n\n" + "=" * 70)
    print("OPTIMAL OPERATION WINDOWS BY METAL")
    print("=" * 70)

    metals_to_analyze = [
        (Graha.SHANI, "Iron/Steel (Lauha)"),
        (Graha.SURYA, "Gold (Suvarna)"),
        (Graha.MANGALA, "Copper (Tamra)"),
        (Graha.CHANDRA, "Silver (Rajata)"),
    ]

    for graha, name in metals_to_analyze:
        windows = analyze_metal_windows(graha, days=30)
        plot_window_distribution(windows, name)

    # Connect classical analysis to wootz physics simulation
    scenarios = connect_to_wootz_simulation()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("""
The classical jyotish baseline is established:

1. Graha-metal correspondences encoded from BPHS and traditional sources
2. Friendship matrix defining which grahas support which operations
3. Tithi-favorability scoring rooted in lunar-cycle context
4. Yoga screening for inauspicious atmospheric conditions
5. Hora-system providing hour-resolution windows
6. Optimal-window scanning across multi-day periods
7. Connection to physical simulation: jyotish assessment becomes
   AstroFieldConditions for materials-process modeling

Wootz now sits within this framework rather than alongside it.
The same baseline applies to copper alloys (panchaloha), silver work,
gold (Suvarna) operations, bhasma preparations, and any other
metallurgical operation that can be characterized by:
  - target metal's graha
  - operation timing (day, hora, tithi, yoga)
  - practitioner's relationship to the operation

The physical simulation provides the testable predictions; the
classical jyotish baseline provides the framework for selecting
which conditions to test.
""")


if __name__ == '__main__':
    main()
