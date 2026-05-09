"""
Run wootz solidification simulations under varying astro-field conditions.

Demonstrates the core hypothesis the simulation tests: ambient field conditions
during slow-cooling phase affect dendrite alignment and therefore the
characteristic banding pattern of wootz Damascus steel.

Outputs:
- Comparison plots showing dendritic structure under different field conditions
- Quantitative metrics (band alignment, vanadium distribution)
- Summary report
"""

import sys
sys.path.insert(0, '/home/claude/wootz_sim')

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from wootz_solidification import (
    WootzMeltConditions,
    AstroFieldConditions,
    WootzSolidificationSim,
)


def run_scenario(name: str, melt: WootzMeltConditions,
                 astro: AstroFieldConditions, total_minutes: float = 200.0,
                 seed: int = 42) -> dict:
    """Run a single scenario and return results."""
    sim = WootzSolidificationSim(melt, astro, random_seed=seed)
    sim.run(total_minutes=total_minutes)
    return {
        'name': name,
        'sim': sim,
        'summary': sim.summary(),
    }


def main():
    # Standard wootz melt conditions
    melt = WootzMeltConditions(
        carbon_pct=1.5,
        vanadium_ppm=50.0,
        cooling_rate_c_per_min=2.0,
        grid_size=128,  # smaller for speed
    )

    # Define scenarios that vary astro conditions
    scenarios = [
        # Baseline: minimal field, geomagnetically quiet
        ('quiet_field', AstroFieldConditions(
            geomagnetic_field_ut=30.0,
            field_orientation_rad=0.0,
            kp_index=1.0,
            tidal_forcing=0.2,
            wave_field_value=0.0,
            graha_compatibility=0.0,
            tithi=8,
        )),
        # Strong field aligned: high geomagnetic, supportive grahas
        ('strong_aligned', AstroFieldConditions(
            geomagnetic_field_ut=60.0,
            field_orientation_rad=0.0,  # aligned with horizontal
            kp_index=4.0,
            tidal_forcing=0.8,
            wave_field_value=0.7,
            graha_compatibility=0.8,
            tithi=15,  # purnima
        )),
        # Strong field perpendicular
        ('strong_perpendicular', AstroFieldConditions(
            geomagnetic_field_ut=60.0,
            field_orientation_rad=np.pi/2,  # perpendicular
            kp_index=4.0,
            tidal_forcing=0.8,
            wave_field_value=0.7,
            graha_compatibility=0.8,
            tithi=15,
        )),
        # Storm conditions (Kp high, disruptive)
        ('storm_disruptive', AstroFieldConditions(
            geomagnetic_field_ut=80.0,
            field_orientation_rad=np.pi/4,
            kp_index=7.0,
            tidal_forcing=0.5,
            wave_field_value=-0.5,
            graha_compatibility=-0.6,  # adversarial
            tithi=30,  # amavasya
        )),
    ]

    results = []
    print("Running simulations...")
    for name, astro in scenarios:
        print(f"  scenario: {name}")
        result = run_scenario(name, melt, astro, total_minutes=200.0, seed=42)
        results.append(result)
        s = result['summary']
        print(f"    effective field: {s['effective_field_ut']:.1f} uT")
        print(f"    solidified: {s['solidified_fraction']*100:.1f}%")
        print(f"    band alignment: {s['band_alignment_score']:.4f}")
        print(f"    V in solid: {s['mean_vanadium_in_solid_ppm']:.1f} ± {s['vanadium_std_in_solid_ppm']:.1f} ppm")

    # Visualization: 4x3 grid (4 scenarios x 3 plots: solid phase, vanadium, alignment)
    fig, axes = plt.subplots(len(results), 3, figsize=(14, 4 * len(results)))
    if len(results) == 1:
        axes = axes[np.newaxis, :]

    # Custom colormap for vanadium
    v_cmap = LinearSegmentedColormap.from_list('vanadium',
        ['#0a0a14', '#1a1a3e', '#3c3c8c', '#7878d0', '#c8c8ff'])

    for i, result in enumerate(results):
        sim = result['sim']
        name = result['name']
        s = result['summary']

        # Plot 1: V concentration with field-direction arrow indicator
        ax = axes[i, 0]
        # Use enhanced contrast for V concentration
        v_norm = (sim.vanadium - sim.vanadium.min()) / (sim.vanadium.max() - sim.vanadium.min() + 1e-10)
        ax.imshow(v_norm, cmap='magma', origin='lower', vmin=0, vmax=1)
        # Draw field-direction arrow
        N = sim.melt.grid_size
        cx, cy = N * 0.85, N * 0.15
        arrow_len = N * 0.1
        dx_arrow = arrow_len * np.cos(sim.astro.field_orientation_rad)
        dy_arrow = arrow_len * np.sin(sim.astro.field_orientation_rad)
        ax.annotate('', xy=(cx + dx_arrow, cy + dy_arrow), xytext=(cx - dx_arrow, cy - dy_arrow),
                    arrowprops=dict(arrowstyle='->', color='cyan', lw=2))
        ax.text(N * 0.85, N * 0.05, f'B = {sim.astro.effective_field_strength():.0f}uT',
                color='cyan', fontsize=9, ha='center')
        ax.set_title(f"{name}\nV banding pattern (enhanced)")
        ax.set_xticks([])
        ax.set_yticks([])

        # Plot 2: vanadium concentration
        ax = axes[i, 1]
        v_display = np.where(sim.phi > 0.5, sim.vanadium, np.nan)
        im = ax.imshow(v_display, cmap=v_cmap, origin='lower')
        ax.set_title(f"V concentration\n(mean {s['mean_vanadium_in_solid_ppm']:.0f} ppm)")
        ax.set_xticks([])
        ax.set_yticks([])
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label='V mass frac')

        # Plot 3: alignment score over time
        ax = axes[i, 2]
        history = sim.history['band_alignment_score']
        ax.plot(history, linewidth=2, color='#8c4400')
        ax.axhline(y=s['band_alignment_score'], color='red', linestyle='--', alpha=0.5)
        ax.set_xlabel('time step')
        ax.set_ylabel('band alignment score')
        ax.set_title(f"Alignment evolution\n(final: {s['band_alignment_score']:.3f})")
        ax.set_ylim(0, max(0.5, max(history) * 1.1) if history else 0.5)
        ax.grid(True, alpha=0.3)

    plt.suptitle('Wootz Solidification Under Varying Astro-Field Conditions',
                 fontsize=14, y=1.001)
    plt.tight_layout()
    plt.savefig('/home/claude/wootz_sim/wootz_simulation_comparison.png', dpi=120, bbox_inches='tight')
    plt.close()
    print(f"\nSaved comparison plot: wootz_simulation_comparison.png")

    # Summary bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    names = [r['name'] for r in results]
    alignment_scores = [r['summary']['band_alignment_score'] for r in results]
    field_strengths = [r['summary']['effective_field_ut'] for r in results]

    x = np.arange(len(names))
    width = 0.35

    bars1 = ax.bar(x - width/2, alignment_scores, width, label='Band alignment score',
                    color='#8c4400', alpha=0.85)
    ax2 = ax.twinx()
    bars2 = ax2.bar(x + width/2, field_strengths, width, label='Effective field (uT)',
                    color='#3c3c8c', alpha=0.85)

    ax.set_xlabel('Astro-field scenario')
    ax.set_ylabel('Band alignment score', color='#8c4400')
    ax2.set_ylabel('Effective field strength (uT)', color='#3c3c8c')
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=20, ha='right')
    ax.set_title('Wootz solidification outcomes vs. astro-field conditions')
    ax.tick_params(axis='y', labelcolor='#8c4400')
    ax2.tick_params(axis='y', labelcolor='#3c3c8c')
    ax.grid(True, alpha=0.3, axis='y')

    fig.tight_layout()
    plt.savefig('/home/claude/wootz_sim/wootz_alignment_vs_field.png', dpi=120, bbox_inches='tight')
    plt.close()
    print(f"Saved alignment-vs-field plot: wootz_alignment_vs_field.png")

    # Generate text summary
    summary_text = ["Wootz Solidification Simulation - Summary Report", "=" * 60, ""]
    summary_text.append(f"Melt conditions:")
    summary_text.append(f"  Carbon: {melt.carbon_pct}%")
    summary_text.append(f"  Vanadium: {melt.vanadium_ppm} ppm")
    summary_text.append(f"  Cooling rate: {melt.cooling_rate_c_per_min} C/min")
    summary_text.append(f"  Grid: {melt.grid_size}x{melt.grid_size} nm")
    summary_text.append("")
    summary_text.append("Scenarios:")
    for r in results:
        s = r['summary']
        summary_text.append(f"\n  {r['name']}:")
        summary_text.append(f"    Effective field strength: {s['effective_field_ut']:.1f} uT")
        summary_text.append(f"    Solidified fraction: {s['solidified_fraction']*100:.1f}%")
        summary_text.append(f"    Mean V in solid: {s['mean_vanadium_in_solid_ppm']:.1f} ppm")
        summary_text.append(f"    V std in solid: {s['vanadium_std_in_solid_ppm']:.2f} ppm")
        summary_text.append(f"    Band alignment score: {s['band_alignment_score']:.4f}")

    summary_text.append("")
    summary_text.append("Interpretation:")
    summary_text.append("  Higher band alignment scores indicate more directional")
    summary_text.append("  organization of vanadium-rich regions, which would correspond")
    summary_text.append("  to clearer Damascus pattern in the final forged blade.")
    summary_text.append("")
    summary_text.append("  Standard deviation of vanadium concentration in the solid")
    summary_text.append("  indicates the degree of segregation - higher std = more")
    summary_text.append("  pronounced banding.")
    summary_text.append("")
    summary_text.append("Caveats:")
    summary_text.append("  - This is plausibility modeling, not verified physics.")
    summary_text.append("  - Real-world coupling magnitudes between geomagnetic field")
    summary_text.append("    and steel solidification dendrite alignment are uncertain.")
    summary_text.append("  - Validation requires physical experiments with controlled")
    summary_text.append("    field conditions during high-carbon steel solidification.")
    summary_text.append("")
    summary_text.append("Atlas integration:")
    summary_text.append("  Inputs (panchanga, Kp, tidal, wave-field, graha-compat) are")
    summary_text.append("  computed by Atlas's existing engines. The transduction layer")
    summary_text.append("  combines them into the effective_field_strength used by")
    summary_text.append("  the simulation. Outputs feed back into Atlas's relational")
    summary_text.append("  graph as predicted-outcome data.")

    summary_str = "\n".join(summary_text)
    with open('/home/claude/wootz_sim/simulation_summary.txt', 'w') as f:
        f.write(summary_str)
    print(f"\nSaved summary: simulation_summary.txt")
    print()
    print(summary_str)


if __name__ == '__main__':
    main()
