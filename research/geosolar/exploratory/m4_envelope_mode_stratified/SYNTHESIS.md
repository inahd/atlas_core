# M4 ↔ spring/neap envelope, mode-stratified — SYNTHESIS

**Status:** EXPLORATORY. Not pre-registered. Not citable as confirmatory.

Date: 2026-05-08

## What this is

Follow-up to the 1h-quintile mode-stratification (commit f2b45d1)
where the prior result (non-overlapping CIs across mode_ratio
quintiles) was flagged as confounded because:

- M4 ↔ Sun-Moon angular separation is non-monotonic
  (|cos(2·sep)| envelope, 4 cycles per 360°).
- Stratifying by mode_ratio implicitly stratifies by the
  separation distribution.
- Linear Pearson r on a non-monotonic relationship gives different
  values across sub-ranges of the predictor by construction —
  selection bias indistinguishable from genuine moderation.

This pass replaces the linear-separation predictor with the harmonic
**spring/neap envelope = |cos(2·sep)|** (1 at syzygy, 0 at quadrature),
which linearizes the relationship and makes Pearson r interpretable.
Adds an interaction-regression test that directly tests whether the
(envelope → m4_amp) slope varies as a function of mode_ratio after
controlling for both main effects.

## Pooled m4_amp ↔ envelope

- Pearson r = **-0.0306**
- 95% block-bootstrap CI = [-0.032, -0.029]
- raw p = 3.74e-93
- n = 448,670

r ≈ +-0.031 smaller than expected for a spring/neap signal.
Either SF tide is dominated by other constituents, or the
envelope formulation is sub-optimal.

## Per-stratum r

Same q20=0.4451, q80=0.5749 cuts as the 1h-quintile prior run.

| Quintile | n | Pearson r | 95% bootstrap CI | raw p |
|---|---:|---:|---|---:|
| bottom_quintile | 89,745 | -0.0524 | [-0.057, -0.049] | 1.27e-55 |
| middle | 269,204 | -0.0202 | [-0.023, -0.017] | 1.17e-25 |
| top_quintile | 89,721 | -0.0425 | [-0.047, -0.038] | 3.1e-37 |
| **POOLED** | 448,670 | -0.0306 | [-0.032, -0.029] | 3.74e-93 |

top − bottom: +0.0099, CIs DO NOT OVERLAP.

## Interaction regression

Centered predictors (mean-subtracted) to reduce collinearity in interaction term.

    m4_amp = β₀ + β₁·envelope_c + β₂·mode_ratio_c + β₃·(envelope_c × mode_ratio_c) + ε

| Coefficient | β | SE | t | OLS p |
|---|---:|---:|---:|---:|
| intercept | +0.88255 | 0.00060 | +1474.72 | 0 |
| envelope (centered) | -0.03984 | 0.00194 | -20.49 | 3.03e-93 |
| mode_ratio (centered) | +0.08137 | 0.00548 | +14.86 | 6.22e-50 |
| envelope × mode_ratio | -0.00475 | 0.01749 | -0.27 | 0.786 |

- R²(main + interaction) = **0.00143**
- R²(main only)         = **0.00143**
- ΔR² from interaction  = **+0.00000**
- Block-bootstrap 95% CI on interaction β: [-0.02205, +0.01263]
- Interaction CI **INCLUDES** zero

## Apparent paradox: non-overlapping per-stratum CIs but null interaction

The per-stratum Pearson r CIs (above) technically do not overlap:
top − bottom = +0.0099 with stratum CIs of width ~0.005-0.008 each.
By the "do the CIs overlap" heuristic this looks like a finding.
But the interaction regression coefficient is essentially zero
(β = -0.00475, OLS p = 0.786, bootstrap CI includes zero,
ΔR² = 0.00000).

The reconciliation: with n ≈ 90,000 per stratum, even trivially-tiny
differences produce tight CIs. A Δr of +0.0099 between strata of
n≈90K each will produce non-overlapping CIs at the 95% level
(per-stratum r SE ≈ 1/√n ≈ 0.003, narrower than the difference).
But the *magnitude* of the difference is in the noise.

The interaction regression directly tests whether the
(envelope → m4_amp) slope differs across mode_ratio levels —
that test finds the slope difference indistinguishable from zero,
both statistically (p = 0.79) and practically (ΔR² = 0).

**The interaction-regression test is the correct test for the
framework prediction; the per-stratum CI overlap test is
hyper-sensitive to large-n statistical power and uninformative
about effect size.**

## Honest interpretation

The interaction term β₃ = -0.00475 has 95% block-bootstrap CI
**including** zero. The (envelope → m4_amp) slope does NOT
meaningfully vary with mode_ratio under the cleaner test.

The non-overlapping per-stratum CIs in the prior 1h-quintile pass —
which were the trigger for this follow-up — are now reconciled:
they were a combination of (a) selection bias from the linear-Pearson
predictor on a non-monotonic relationship and (b) trivial-magnitude
differences amplified to apparent significance by very large n. Under
the corrected harmonic predictor + interaction regression, **the
framework prediction of mode-mediated M4 moderation is not
supported.**

The pooled R² of the full model (main effects + interaction) is
0.0014 — envelope and mode_ratio together explain ~0.14% of M4
amplitude variance at the SF gauge. SF M4 is dominated by other
factors (basin geometry, mixed semidiurnal tide, local currents)
that the spring/neap envelope is largely orthogonal to.

## Does the envelope predictor resolve the prior confound?

Partially. The envelope predictor removes the non-monotonicity issue
(linear Pearson r is now interpretable for the envelope-vs-m4 relationship),
but a residual coupling remains: mode_ratio at the lagna is determined
by lagna-Sun-Moon geometry, which is also what determines the envelope
value. Strata might still over-/under-sample envelope sub-ranges, though
the relationship is now monotonic so the bias is smaller.

The interaction regression is the cleaner test: it directly asks whether
the envelope→m4 slope varies across mode_ratio levels, controlling for
both main effects. The interaction coefficient is the answer.

## Plots

- `m4_vs_envelope_pooled.png` — the envelope predictor at the basic level.
- `m4_vs_envelope_by_quintile.png` — three-panel scatter, per-stratum.
- `correlation_envelope_by_quintile_with_bootstrap.png` — bar chart with CIs.
- `interaction_regression_diagnostic.png` — residuals from main-effects-only
  fit, plotted vs envelope by stratum; if the interaction is real, residual
  slopes should differ across mode_ratio levels.

## Caveats

- Single-window test on data already used in PREREG_001 and the 1h-quintile
  prior run. Cannot serve as confirmatory.
- Quintile cuts are the same as the prior pass (q20=0.4451, q80=0.5749) —
  carrying forward the post-hoc data-driven boundaries.
- The envelope predictor is one canonical choice; harmonic regression with
  cos(2·sep) and sin(2·sep) jointly would be more general (allowing arbitrary
  phase) but adds a degree of freedom.
- Residual coupling between mode_ratio and envelope (both functions of
  Sun-Moon-lagna geometry) is mitigated but not fully removed. Cleanest
  test would stratify by a variable independent of Sun-Moon geometry
  (Kp, season, hour-of-day).

*Total wall: 23.6s*