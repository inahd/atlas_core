# Wootz Solidification Simulation — Atlas Integration Module

A working simulation of nanoscale dendritic solidification in high-carbon steel
under varying ambient electromagnetic conditions. Demonstrates the
transduction-folding architecture: cosmological/astrological state inputs
become physical inputs to a materials-process simulation.

## Files

- `wootz_solidification.py` — core simulation module
- `run_simulation.py` — example run with multiple scenarios + visualization
- `wootz_simulation_comparison.png` — generated comparison plot (4 scenarios)
- `wootz_alignment_vs_field.png` — generated bar chart showing band alignment vs field
- `simulation_summary.txt` — text summary of run results

## What it does

Models 2D dendritic growth of high-carbon steel cooling from melt. Tracks:
- Phase field (liquid → solid)
- Vanadium impurity segregation (with realistic partition coefficient k=0.4)
- Carbon distribution
- Temperature evolution

Couples ambient field conditions to dendrite-growth direction through an
anisotropy term. Field-aligned cells grow preferentially when the field is
coherent; disruptive conditions (high Kp, adversarial grahas) suppress the
directional preference.

## Headline result

Three scenarios with similar effective field strength (~120 µT) produce
dramatically different band-alignment outcomes:

| Scenario | Effective Field | Band Alignment |
|----------|----------------|----------------|
| quiet_field | 34 µT | 0.041 |
| strong_aligned | 120 µT | **0.233** |
| strong_perpendicular | 120 µT | **0.172** |
| storm_disruptive | 122 µT | 0.007 |

Field strength alone does not determine outcome — *coherence* does. This is
the central claim of the materials-cosmology framework demonstrated
computationally.

## Usage

```python
from wootz_solidification import (
    WootzMeltConditions,
    AstroFieldConditions,
    WootzSolidificationSim,
)

# Define the melt
melt = WootzMeltConditions(
    carbon_pct=1.5,
    vanadium_ppm=50.0,
    cooling_rate_c_per_min=8.0,  # accelerated for simulation
    grid_size=128,
)

# Define ambient field conditions (in production, computed from Atlas panchanga)
astro = AstroFieldConditions(
    geomagnetic_field_ut=45.0,
    field_orientation_rad=0.0,
    kp_index=2.0,
    tidal_forcing=0.5,
    wave_field_value=0.3,
    graha_compatibility=0.5,
    tithi=15,
)

# Run
sim = WootzSolidificationSim(melt, astro, random_seed=42)
sim.run(total_minutes=200.0)
print(sim.summary())
```

## Atlas integration architecture

This module is the materials-process compute layer. The transduction
between Atlas's existing engines and the simulation works as follows:

```
[Atlas existing engines]                [This module]
  panchanga_engine    ─┐
  jyotisha_engine     ─┤
  wave_field          ─┼──> AstroFieldConditions ──> WootzSolidificationSim
  geomagnetic_ingest  ─┤        (transduction              (materials
  tidal_engine        ─┘         layer)                     simulation)
                                                                │
                                                                ▼
                                                     predicted outcomes
                                                     feed back into
                                                     Atlas relational
                                                     graph
```

The `AstroFieldConditions.effective_field_strength()` method is the
transduction layer. It combines geomagnetic, tidal, wave-field, and
graha-compatibility inputs into a single coupled physical parameter that
drives the simulation.

In production, Atlas's panchanga_engine, jyotisha_engine, and wave_field
modules would compute these inputs from current cosmological state. The
simulation outputs (predicted alignment, segregation metrics) feed back
into Atlas as predicted-outcome data linkable to specific dates, sites, and
materials.

## Extending to other materials/processes

The architecture generalizes. To add a new materials-cosmology simulation:

1. Define a `<MaterialName>Conditions` dataclass (analogous to `WootzMeltConditions`)
2. Define how `AstroFieldConditions` couples to the new material's process
   (different materials respond to different astro-state combinations)
3. Implement the simulation loop with appropriate physics
4. Define output metrics relevant to that material's quality

Candidates from the materials-cosmology survey:
- Bhasma puta cycles (smaller scale, thermal-chemical primary)
- Geopolymer curing (architectural scale, hydro-chemical primary)
- Tamahagane tatara operation (slow, multi-day, master-monitored)
- Sound-affected stone working (acoustic primary)

Each would be its own module in this directory, sharing the
`AstroFieldConditions` interface.

## Honest scope and caveats

**This is plausibility modeling, not verified physics.**

Real-world coupling magnitudes between geomagnetic field (~50 µT) and
steel solidification dendrite alignment at 1380°C are not established in
the materials-science literature. The simulation demonstrates the
*framework* — what the prediction would look like *if* the coupling exists
at the magnitudes the framework hypothesizes.

Validation would require physical experiments:
- Wootz-grade steel solidification under controlled magnetic field conditions
- Comparison of resulting carbide alignment patterns
- Statistical correlation across multiple controlled trials

The framework's value is not proof of effects but:
- Generation of testable predictions
- Identification of which astro-state combinations would (per the framework)
  be optimal for specific operations
- Cross-domain integration showing how cosmological inputs could couple to
  materials processes
- Atlas's relational graph gains a working materials-process compute layer

## Calibration against empirical data

When real wootz reproduction data with documented timing becomes available,
the coupling coefficients in `effective_field_strength()` and the
field-bias terms in `_solidify_step()` can be calibrated against measured
outcomes. The framework then becomes empirically grounded.

Initial calibration targets:
- Verhoeven & Pendray reproduction data (when timing is documented)
- Tamahagane production (NBTHK has decades of documented operations
  with seasonal/winter timing — ideal calibration source)
- Historical Damascus blade analysis (for retrospective inference)

## Running the example

```bash
cd /path/to/wootz_sim
python3 run_simulation.py
```

Generates `wootz_simulation_comparison.png`, `wootz_alignment_vs_field.png`,
and `simulation_summary.txt` in the current directory.

Runtime: ~10-15 seconds on modern hardware for 4 scenarios at 128x128 grid.
For higher-resolution research runs, increase `grid_size` to 256 or 512;
runtime scales as O(N²) per timestep.
