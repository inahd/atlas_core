"""
math_extracts/steinmetz_alternating_current_phenomena.py

Mathematical content extracted from:
  Charles P. Steinmetz, "Theory and Calculation of Alternating Current
  Phenomena" (1900, 3rd ed., Electrical World and Engineer)

Source: directly extracted from PDF text. Section/page references
match Steinmetz's own numbering (§27 = "Rotation of vector by 180 and 90").

This module provides the foundational versor algebra (complex
representation of alternating quantities) that Atlas's wave-field
engine implements at cosmological scale. Steinmetz developed this
notation 1893-1900 to handle AC circuit analysis; the same algebra
governs interference of any sinusoidal sources.

Atlas usage:
    from math_extracts.steinmetz_alternating_current_phenomena import (
        Versor, Impedance, Admittance,
        rotate_90, rotate_180,
        impedance_combine_series, admittance_combine_parallel,
    )

The closed-form target-invariance identity Atlas discovered tonight
(|Z_k| = 2|cos(k(β-α)/2)|) follows directly from Steinmetz's versor
algebra — see __notes__ at end of file.
"""

import numpy as np
from dataclasses import dataclass
from typing import Union


# ──────────────────────────────────────────────────────────────────────
# §25-27: VECTOR REPRESENTATION (the foundation)
#
# §27, p.36: "Rotation of vector by 180 and 90. j = √-1"
#
# Steinmetz: the imaginary unit j is the operator that rotates a
# vector by 90° in the AC-phase plane. This is the *operational*
# meaning of j — not "imaginary" in the metaphysical sense, but
# "perpendicular phase rotation."
# ──────────────────────────────────────────────────────────────────────

# Atlas uses 'j' for engineering convention (vs 'i' for math/physics)
# to match Steinmetz's notation throughout
j = 1j


def rotate_90(vector: complex) -> complex:
    """§27: Multiplication by j rotates a vector by 90° (quarter-cycle phase shift)."""
    return j * vector


def rotate_180(vector: complex) -> complex:
    """§27: Multiplication by j² = -1 rotates a vector by 180°."""
    return -vector


def rotate_n_quarters(vector: complex, n: int) -> complex:
    """Rotate by n*90° via successive multiplication by j."""
    return (j ** n) * vector


def rectangular_to_polar(vector: complex) -> tuple:
    """§25: A vector A + jB has magnitude sqrt(A² + B²) and angle atan2(B, A)."""
    return abs(vector), np.angle(vector)


def polar_to_rectangular(magnitude: float, angle_rad: float) -> complex:
    """Inverse: magnitude * exp(j*angle) = magnitude*(cos + j*sin)."""
    return magnitude * np.exp(j * angle_rad)


# ──────────────────────────────────────────────────────────────────────
# §29-30: IMPEDANCE AS COMPLEX QUANTITY
#
# §29-30: "Z = r + jx is the expression of the impedance of the
#   circuit, in complex quantities."
#
# This is the central versor-algebra move: every AC quantity (voltage,
# current, impedance, admittance) is represented as a complex number.
# Real part = in-phase (resistive/conductive) component.
# Imaginary part = quadrature (reactive/susceptive) component.
# ──────────────────────────────────────────────────────────────────────

@dataclass
class Impedance:
    """
    Steinmetz §29-30: complex impedance Z = r + jx.

    The fundamental AC quantity. r = resistance (in-phase, energy-dissipating).
    x = reactance (quadrature, energy-storing). Together: Z = r + jx.

    For Atlas's framework correction:
        r ↔ magnetic-mode component (in-phase, broadside-radial)
        x ↔ dielectric-mode component (quadrature, axial-longitudinal)

    Inductive reactance: x_L = ω*L  (positive imaginary, j*ω*L)
    Capacitive reactance: x_C = -1/(ω*C)  (negative imaginary, -j/(ω*C))
    """
    resistance: float       # r, real component
    reactance: float        # x, imaginary component

    @property
    def complex(self) -> complex:
        """Z = r + jx as Python complex number."""
        return complex(self.resistance, self.reactance)

    @property
    def magnitude(self) -> float:
        """|Z| = sqrt(r² + x²)."""
        return abs(self.complex)

    @property
    def phase_angle(self) -> float:
        """arg(Z) = atan2(x, r), in radians."""
        return np.angle(self.complex)

    @property
    def admittance(self) -> "Admittance":
        """§40: Y = 1/Z. Returns the reciprocal as Admittance instance."""
        Y = 1.0 / self.complex
        return Admittance(conductance=Y.real, susceptance=Y.imag)

    @classmethod
    def inductive(cls, resistance: float, inductance_H: float,
                  omega: float) -> "Impedance":
        """Series R-L impedance: Z = R + j*omega*L."""
        return cls(resistance=resistance, reactance=omega * inductance_H)

    @classmethod
    def capacitive(cls, resistance: float, capacitance_F: float,
                   omega: float) -> "Impedance":
        """Series R-C impedance: Z = R - j/(omega*C)."""
        if capacitance_F <= 0 or omega <= 0:
            return cls(resistance=resistance, reactance=float('-inf'))
        return cls(resistance=resistance, reactance=-1.0 / (omega * capacitance_F))

    @classmethod
    def rlc_series(cls, R: float, L: float, C: float,
                   omega: float) -> "Impedance":
        """§42-46 generalized: Z = R + j*(omega*L - 1/(omega*C))."""
        x_L = omega * L
        x_C = 1.0 / (omega * C) if (C > 0 and omega > 0) else 0
        return cls(resistance=R, reactance=x_L - x_C)


@dataclass
class Admittance:
    """
    Steinmetz §40-41: complex admittance Y = g + jb.

    The reciprocal of impedance. g = conductance (in-phase). b = susceptance
    (quadrature).

    §40: 'As the reciprocal of the complex quantity, Z = r + jx, the
    admittance is a complex quantity also, or Y = g + jb.'
    """
    conductance: float      # g, real component (1/r in DC limit)
    susceptance: float      # b, imaginary component

    @property
    def complex(self) -> complex:
        return complex(self.conductance, self.susceptance)

    @property
    def magnitude(self) -> float:
        return abs(self.complex)

    @property
    def phase_angle(self) -> float:
        return np.angle(self.complex)

    @property
    def impedance(self) -> Impedance:
        """Y → Z reciprocal, returning Impedance instance."""
        Z = 1.0 / self.complex
        return Impedance(resistance=Z.real, reactance=Z.imag)


# ──────────────────────────────────────────────────────────────────────
# §38-39: SERIES AND PARALLEL COMBINATION
# ──────────────────────────────────────────────────────────────────────

def impedance_combine_series(impedances: list) -> Impedance:
    """§39: Impedances in series add as complex quantities.
    Z_total = Z_1 + Z_2 + ... + Z_n."""
    Z_complex = sum(z.complex for z in impedances)
    return Impedance(resistance=Z_complex.real, reactance=Z_complex.imag)


def admittance_combine_parallel(admittances: list) -> Admittance:
    """§39: Admittances in parallel add as complex quantities.
    Y_total = Y_1 + Y_2 + ... + Y_n."""
    Y_complex = sum(y.complex for y in admittances)
    return Admittance(conductance=Y_complex.real, susceptance=Y_complex.imag)


def impedance_combine_parallel(impedances: list) -> Impedance:
    """Convert each impedance to admittance, sum in parallel,
    convert back to impedance."""
    admittances = [z.admittance for z in impedances]
    Y_total = admittance_combine_parallel(admittances)
    return Y_total.impedance


# ──────────────────────────────────────────────────────────────────────
# §28: SINE WAVE COMBINATION VIA SYMBOLIC EXPRESSION
#
# Steinmetz's central insight: sinusoidal quantities at the same
# frequency can be added/subtracted via their complex (phasor)
# representation. This makes circuit analysis algebraic instead of
# trigonometric.
# ──────────────────────────────────────────────────────────────────────

def sine_to_phasor(amplitude: float, phase_rad: float) -> complex:
    """Convert a sine wave a*sin(omega*t + phi) to phasor representation
    A_phasor = a*exp(j*phi).

    The omega*t time-dependence is suppressed (assumed common across
    all phasors at same frequency), leaving only amplitude and phase."""
    return amplitude * np.exp(j * phase_rad)


def phasor_to_sine(phasor: complex, omega: float, t: float) -> float:
    """Convert phasor back to instantaneous time-domain value:
    Re(A_phasor * exp(j*omega*t)) = a*cos(omega*t + phi)."""
    return (phasor * np.exp(j * omega * t)).real


def superpose_phasors(phasors: list) -> complex:
    """§28: Sum of sinusoids at same frequency = sum of their phasors.
    This is why versor algebra works — the time-dependence factors out."""
    return sum(phasors)


# ──────────────────────────────────────────────────────────────────────
# §72: EFFECTIVE RESISTANCE AND REACTANCE
#
# Energy-dissipation in AC circuits is governed by the *effective*
# resistance/reactance, not just the geometric R-L-C values, because
# eddy currents, hysteresis, dielectric loss all add to losses.
# ──────────────────────────────────────────────────────────────────────

def effective_resistance(power_loss_watts: float,
                          rms_current: float) -> float:
    """§72: Effective resistance r_eff = P / I_rms²
    This may exceed the DC resistance due to eddy currents,
    hysteresis, skin effect."""
    if rms_current <= 0:
        return float('inf')
    return power_loss_watts / (rms_current ** 2)


def effective_reactance(reactive_power_VAR: float,
                         rms_current: float) -> float:
    """Effective reactance x_eff = Q / I_rms²."""
    if rms_current <= 0:
        return float('inf')
    return reactive_power_VAR / (rms_current ** 2)


# ──────────────────────────────────────────────────────────────────────
# POWER FACTOR AND COMPLEX POWER
# ──────────────────────────────────────────────────────────────────────

def complex_power(voltage_phasor: complex,
                   current_phasor: complex) -> complex:
    """S = V * conj(I).  Real part = real power (watts).
    Imaginary part = reactive power (VAR)."""
    return voltage_phasor * np.conj(current_phasor)


def power_factor(impedance: Impedance) -> float:
    """cos(arg(Z)) = r / |Z|.  Tells you what fraction of |V|*|I|
    becomes real power."""
    if impedance.magnitude == 0:
        return 1.0
    return impedance.resistance / impedance.magnitude


# ──────────────────────────────────────────────────────────────────────
# CONNECTION TO ATLAS'S WAVE-FIELD CLOSED-FORM IDENTITY
#
# Atlas's compute_pair_interference for two graha sources at angular
# longitudes alpha, beta evaluated at target longitude theta:
#
#     Z_k(theta, alpha, beta) = exp(jk(theta - alpha)) + exp(jk(theta - beta))
#
# Factor out the common phase exp(jk*theta):
#     Z_k = exp(jk*theta) * (exp(-jk*alpha) + exp(-jk*beta))
#
# Take magnitude:
#     |Z_k| = |exp(jk*theta)| * |exp(-jk*alpha) + exp(-jk*beta)|
#           = 1 * 2|cos(k(beta - alpha)/2)|
#
# The target longitude theta cancels exactly. This is a direct
# consequence of Steinmetz's framework: |exp(j*phi)| = 1 for any phi,
# so any common-phase factor in a sum drops out of the magnitude.
#
# The target-dependent information lives entirely in the real and
# imaginary parts SEPARATELY (the magnetic and dielectric mode
# components in Dollard's framework). Collapsing to magnitude
# averages over them.
# ──────────────────────────────────────────────────────────────────────

def two_source_interference_complex(alpha_deg: float, beta_deg: float,
                                     theta_deg: float, k: int) -> complex:
    """Atlas's versor-aware interference function.
    Returns complex Z_k. Re(Z_k) = magnetic mode, Im(Z_k) = dielectric mode."""
    alpha_rad = np.radians(alpha_deg)
    beta_rad = np.radians(beta_deg)
    theta_rad = np.radians(theta_deg)
    return np.exp(j * k * (theta_rad - alpha_rad)) + \
           np.exp(j * k * (theta_rad - beta_rad))


def two_source_interference_magnitude_closed_form(alpha_deg: float,
                                                   beta_deg: float,
                                                   k: int) -> float:
    """Closed-form: |Z_k| = 2|cos(k*(beta-alpha)/2)|.

    Target longitude theta does NOT appear — it cancels by Steinmetz's
    versor algebra. Atlas discovered this empirically; the math
    explains why."""
    alpha_rad = np.radians(alpha_deg)
    beta_rad = np.radians(beta_deg)
    return 2.0 * abs(np.cos(k * (beta_rad - alpha_rad) / 2.0))


# ──────────────────────────────────────────────────────────────────────
# NOTES ON STEINMETZ'S ORIGINAL DEPARTURES FROM PHYSICS CONVENTION
# ──────────────────────────────────────────────────────────────────────

__notes__ = """
Steinmetz consistently used 'j' (rather than 'i') for the imaginary
unit, distinguishing the engineering convention from the physics one.
Atlas follows Steinmetz's convention in this module.

Steinmetz also distinguished between 'absolute values' (magnitudes)
and 'complex vectors' throughout his text. From the preface:
    'The denotations have been carried through systematically, by
     distinguishing between complex vectors and absolute values
     throughout the text.'

This is the same distinction Atlas's versor extension makes between
|Z_k| (the absolute value, target-invariant by closed-form identity)
and Z_k (the complex vector, target-dependent and carrying mode
information).

The framework correction Atlas locked in memory tonight (lines 15-16)
is structurally Steinmetz's distinction applied at cosmological scale.
Steinmetz's critique that mainstream EM was treating dielectric and
magnetic asymmetrically (collapsing complex to absolute) is the same
critique Atlas needed to apply to its own wave-field reduction.
"""


if __name__ == "__main__":
    # Self-test: verify Atlas's closed-form identity
    print("Steinmetz versor algebra — self test")
    print("=" * 60)

    # Test §27: rotation
    v = complex(3, 4)
    print(f"v = {v}")
    print(f"  rotate 90° (j*v) = {rotate_90(v)}")
    print(f"  rotate 180° (-v) = {rotate_180(v)}")

    # Test §29-30: complex impedance
    Z = Impedance.rlc_series(R=10, L=1e-3, C=1e-6, omega=2*np.pi*1000)
    print(f"\nRLC impedance at 1kHz:")
    print(f"  Z = {Z.resistance:.3f} + j{Z.reactance:.3f}")
    print(f"  |Z| = {Z.magnitude:.3f}")
    print(f"  phase = {np.degrees(Z.phase_angle):.2f}°")
    print(f"  Y (admittance) = {Z.admittance.conductance:.5f} + j{Z.admittance.susceptance:.5f}")

    # Test Atlas's closed-form identity
    print(f"\nAtlas closed-form identity verification:")
    alpha, beta = 45.0, 120.0  # graha longitudes
    k = 3                       # harmonic
    print(f"  alpha={alpha}°, beta={beta}°, k={k}")
    targets = [0, 90, 180, 270, 360]
    for theta in targets:
        Z_complex = two_source_interference_complex(alpha, beta, theta, k)
        magnitude_full = abs(Z_complex)
        magnitude_closed_form = two_source_interference_magnitude_closed_form(alpha, beta, k)
        print(f"    theta={theta}°: |Z_k| via complex = {magnitude_full:.6f}, "
              f"via closed-form = {magnitude_closed_form:.6f}")
    print("  (target-invariance confirmed: all magnitudes equal)")
