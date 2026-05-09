# math_extracts/ — Manifest

Mathematical content extracted from the dielectric-register lineage,
ready for direct import into Atlas's engine layer.

Each module provides executable Python code (not prose commentary)
extracted from a specific primary source. All equations are verified
against source text. Self-tests demonstrate the math runs and produces
correct results.

## Modules

### `dollard_1982_dielectric_magnetic_discharges.py`

Source: Eric Dollard, *Introduction to Dielectric & Magnetic
Discharges in Electrical Windings* (1982).

Provides:
- `MagneticCircuit` and `DielectricCircuit` dataclasses with the
  parallel-register quantity relations from Dollard's Appendix Tables
- `FieldGeometry` — broadside-radial vs axial-longitudinal energy
  storage rules (§13)
- `oscillation_frequency()`, `characteristic_impedance()` — §17-18
- `LimitingCase` — boundary-condition behaviors at zero/infinity
  (§10-11, §15-16)
- `TableI_FieldQuantities`, `TableII_CircuitDualities` — Steinmetz's
  parallel quantity formulations from Dollard's appendices
- `free_space_inductance_per_unit_length()`,
  `free_space_capacitance()` — §22 free-space behavior
- `ConjugateSpaceHypothesis` — §23 *speculative* claim, hedged

Atlas integration: the four-quadrant framework's prose-articulation-
level math. Use this for documentation, framing, and the structural
duality between magnetic and dielectric registers in Atlas's wave-field
engine.

### `steinmetz_alternating_current_phenomena.py`

Source: Charles P. Steinmetz, *Theory and Calculation of Alternating
Current Phenomena* (3rd ed., 1900).

Provides:
- `j = sqrt(-1)` as the rotation-by-90° operator (§27)
- `rotate_90()`, `rotate_180()`, `rotate_n_quarters()` — versor algebra
  primitives
- `Impedance` and `Admittance` dataclasses (§29-31, §40-41)
- `impedance_combine_series()`, `admittance_combine_parallel()`,
  `impedance_combine_parallel()` — §38-39 combination rules
- `sine_to_phasor()`, `phasor_to_sine()`, `superpose_phasors()` —
  §28 sinusoid combination
- `effective_resistance()`, `effective_reactance()` — §72 hysteresis-
  inclusive losses
- `complex_power()`, `power_factor()` — energy/reactive decomposition
- **`two_source_interference_complex()`,
  `two_source_interference_magnitude_closed_form()`** — these are
  the functions implementing Atlas's tonight discovery; the magnitude
  closed-form proves target-invariance by Steinmetz's framework

Atlas integration: this module is the *mathematical foundation* of
Atlas's versor extension. The closed-form identity Atlas discovered
tonight (|Z_k| = 2|cos(k(β-α)/2)|) is demonstrated and verified here.
Import into `npu_engine/jyotisha_engine.py` for the wave-field state.

### `steinmetz_transient_phenomena.py`

Source: Charles P. Steinmetz, *Theory and Calculation of Transient
Electric Phenomena and Oscillations* (3rd ed., 1920).

Provides:
- `rl_circuit_transient()`, `time_constant_RL()` — §20 first-order
  transient
- `rlc_series_discriminant()`, `rlc_series_case()`,
  `critical_resistance()`, `rlc_oscillatory_frequency()`,
  `rlc_damping_constant()`, `rlc_decrement()`, `rlc_series_response()`
  — §29-43 second-order transient (logarithmic / critical / oscillatory)
- `lc_natural_frequency()` — §48 LC tank natural frequency
- `TransmissionLine` dataclass with the four-constant {r, L, g, C}
  formulation (§5, Section III Ch II)
- `propagation_constant()`, `characteristic_impedance_line()` — wave
  propagation on uniform transmission line
- `polyphase_mmf_sum()`, `is_balanced_polyphase()`,
  `balanced_polyphase_resultant_magnitude()` — §106-111 rotating field
- `FourQuadrantConstants` — explicit map between Steinmetz's four
  transmission-line constants and Dollard's four-quadrant framework

Atlas integration: provides the *temporal* and *spatial* wave equations
that govern the wave-field engine. The transmission-line treatment in
particular is where the four-quadrant framework becomes operational —
{r, L, g, C} is the exact dimensional structure Dollard articulates,
and it has well-developed mathematics that predate the Dollard
articulation by 80 years.

## Integration into Atlas

Recommended location: `~/atlas_core/npu_engine/math_extracts/` (move
from `~/atlas_session_outputs/math_extracts/` after committing).

Recommended imports in existing engines:

```python
# In npu_engine/jyotisha_engine.py
from npu_engine.math_extracts.steinmetz_alternating_current_phenomena import (
    two_source_interference_complex,
    two_source_interference_magnitude_closed_form,
)

# Use these in compute_pair_interference and compute_wave_field
# instead of bare numpy expressions — provides documented foundations
# for the math.
```

```python
# In npu_engine/sound_engine.py or wherever oscillation modeling happens
from npu_engine.math_extracts.dollard_1982_dielectric_magnetic_discharges import (
    oscillation_frequency,
    characteristic_impedance,
)

# Use for any LC-tank-style natural frequency computation.
```

```python
# For future bhumi-stratification work involving distributed-parameter
# physical systems (the atmospheric-electric circuit, telluric currents):
from npu_engine.math_extracts.steinmetz_transient_phenomena import (
    TransmissionLine,
    propagation_constant,
)

# Atmospheric column as transmission line: the global electric circuit
# can be modeled with the four-constant structure (r=atmospheric
# conductivity, L=inductance per height, g=fair-weather conductance,
# C=capacity per area).
```

## Cross-references and lineage

Steinmetz wrote *Alternating Current Phenomena* in 1893 (1st ed),
substantially expanding through 1900 (3rd ed). The versor algebra in
that book is what Dollard cites as the foundation for the
dielectric-register critique. The *Transient Phenomena* book (1909
1st ed, 1920 3rd ed) extends the versor algebra to time-domain and
spatial-domain wave problems.

Dollard's 1982 monograph is essentially a recapitulation and extension
of these Steinmetz frameworks for an audience that had largely lost
the original mathematical literacy. The math in Dollard's prose is
already in Steinmetz; what Dollard adds is the structural articulation
("four quadrants") and the speculative extensions (§19, §23).

## Status of additional modules pending

Not yet extracted (sources need either better digital editions or
vision-based reading):

- **Heaviside operational calculus** (Electromagnetic Theory vol. 1-3) —
  the differential-operator formalism that complements Steinmetz's
  versor algebra. Particularly important for transient analysis.
  The deep research report identifies the Chelsea 1971 reprint as
  the cleanest modern edition.

- **Maxwell's Treatise** (vol. 1-2) — the canonical EM text.
  Important for documenting where the dielectric/magnetic asymmetry
  Steinmetz critiques originates. Dover reprint of 3rd edition
  available.

- **Dollard's Symbolic Representation of the Generalized Electric
  Wave** — image-only PDF, requires vision-based reading or a clean
  edition from Borderland Sciences directly.

- **Faraday's Experimental Researches** — primary observational data
  for lines-of-force concept. Better as historical-philological
  foundation than as live math.

- **Whittaker's History of Theories of Aether and Electricity** vols
  1-2 — historical documentation, not directly extractable as math.

- **MacFarlane and McAulay quaternion papers** — Project Gutenberg
  has born-digital TeX source for several. Direct quaternion algebra
  modules can be added cleanly.

## Notes on integration

These modules are pure Python with numpy as the only dependency.
They contain no Atlas-specific imports; they can be tested in
isolation. The intent is that Atlas's existing engines IMPORT FROM
these modules rather than re-implementing the same math inline.

The modules are documented at the section/page level matching the
source texts. When Atlas writes about the framework or cites the math,
the citation can point to the specific section in the module which
points to the specific section in the original work.

Self-tests (`if __name__ == "__main__"`) run on import-by-script and
demonstrate the math produces correct values. These also serve as
usage examples for downstream code.
