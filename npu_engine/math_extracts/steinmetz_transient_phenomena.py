"""
math_extracts/steinmetz_transient_phenomena.py

Mathematical content extracted from:
  Charles P. Steinmetz, "Theory and Calculation of Transient Electric
  Phenomena and Oscillations" (3rd ed., 1920, McGraw-Hill)

This is the foundational text for the four-quadrant register of Atlas's
framework. Steinmetz develops:
  - Section I: Transient phenomena in TIME (differential equations of
    circuit transients, R-L-C series, oscillations)
  - Section II: Periodic transient phenomena (rectification)
  - Section III: Transient phenomena in SPACE (transmission line as
    four-constant system: r, L, g, C; the wave equation)

Section III is particularly important for Atlas: it is where Steinmetz
treats the spatial wave-propagation problem with the same versor algebra
he developed for time-domain AC analysis. The four-constants {r, L, g, C}
correspond directly to Dollard's four-quadrant framework:
  r ↔ resistance (electric/dissipative register)
  L ↔ inductance (magnetic register)
  g ↔ leakage conductance (electric/dissipative register)
  C ↔ capacitance (dielectric register)

Atlas usage:
    from math_extracts.steinmetz_transient_phenomena import (
        rl_circuit_transient, rc_circuit_transient,
        rlc_series_three_cases, oscillation_decrement,
        TransmissionLine, propagation_constant, characteristic_impedance,
    )

Cross-reference: this module provides the *temporal* and *spatial*
equations underlying Atlas's wave-field engine. See
steinmetz_alternating_current_phenomena.py for the steady-state versor
algebra these equations reduce to in the AC limit.
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple

# Use Steinmetz/engineering convention
j = 1j


# ──────────────────────────────────────────────────────────────────────
# SECTION I — CHAPTER III: R-L CIRCUIT TRANSIENTS (§20-25)
#
# §20: "Equations of continuous-current circuit, including its
# transient term."
#
# The fundamental DE: e = R*i + L*di/dt
# Solution form: i(t) = i_steady + (i_initial - i_steady) * exp(-R*t/L)
# ──────────────────────────────────────────────────────────────────────

def rl_circuit_transient(emf: float, resistance: float, inductance: float,
                          initial_current: float, t: np.ndarray) -> np.ndarray:
    """
    §20: Solution to L*di/dt + R*i = E.

    Args:
        emf: applied E (volts) — assumed constant after switching
        resistance: R (ohms)
        inductance: L (henrys)
        initial_current: i(0) (amps)
        t: array of time points (seconds)

    Returns:
        current i(t) at each time point.

    The transient term decays with time constant tau = L/R.
    """
    if resistance <= 0:
        raise ValueError("Resistance must be > 0")
    i_steady = emf / resistance
    tau = inductance / resistance
    return i_steady + (initial_current - i_steady) * np.exp(-t / tau)


def time_constant_RL(resistance: float, inductance: float) -> float:
    """tau_RL = L/R, the time scale of magnetic-energy storage transient."""
    return inductance / resistance if resistance > 0 else float('inf')


# ──────────────────────────────────────────────────────────────────────
# SECTION I — CHAPTER V: R-L-C SERIES (§29-43)
#
# §29: "The differential equations of condenser charge and discharge."
# §33: "The three cases of condenser charge and discharge: logarithmic,
#       critical and oscillatory."
#
# DE: L*d²q/dt² + R*dq/dt + q/C = E
#
# Discriminant determines case:
#   D = (R/(2L))² - 1/(LC)
#   D > 0: logarithmic (overdamped) — two real roots
#   D = 0: critical (critically damped) — repeated root
#   D < 0: trigonometric/oscillatory (underdamped) — complex roots
# ──────────────────────────────────────────────────────────────────────

def rlc_series_discriminant(R: float, L: float, C: float) -> float:
    """§33: discriminant D = (R/(2L))² - 1/(LC).
    Sign determines whether transient is logarithmic, critical, or oscillatory."""
    if L <= 0 or C <= 0:
        return float('nan')
    return (R / (2 * L))**2 - 1.0 / (L * C)


def rlc_series_case(R: float, L: float, C: float) -> str:
    """Return one of 'logarithmic', 'critical', 'oscillatory'."""
    D = rlc_series_discriminant(R, L, C)
    if D > 0:
        return 'logarithmic'
    elif D == 0:
        return 'critical'
    else:
        return 'oscillatory'


def critical_resistance(L: float, C: float) -> float:
    """§43: R_critical = 2*sqrt(L/C). Above this, oscillation is suppressed.

    This is twice the characteristic impedance Z_0 = sqrt(L/C).
    Atlas: this is the boundary between magnetic-mode-dominant and
    dielectric-mode-dominant transient response."""
    if C <= 0:
        return float('inf')
    return 2.0 * np.sqrt(L / C)


def rlc_oscillatory_frequency(R: float, L: float, C: float) -> float:
    """§39, §41: For oscillatory case, angular frequency of damped oscillation
    omega_d = sqrt(1/(LC) - (R/(2L))²)

    Returns angular frequency in radians/second.
    Returns 0 if non-oscillatory."""
    D = rlc_series_discriminant(R, L, C)
    if D >= 0:
        return 0.0
    return np.sqrt(-D)


def rlc_damping_constant(R: float, L: float) -> float:
    """The exponential-decay rate of the oscillation envelope.
    alpha = R/(2L)."""
    return R / (2 * L) if L > 0 else float('inf')


def rlc_decrement(R: float, L: float, C: float) -> float:
    """§43: Logarithmic decrement of the oscillating wave =
    alpha * T_oscillation = (R/(2L)) * (2*pi/omega_d).

    Quantifies how much the oscillation amplitude decays per cycle."""
    omega_d = rlc_oscillatory_frequency(R, L, C)
    if omega_d == 0:
        return float('inf')
    alpha = rlc_damping_constant(R, L)
    return alpha * (2 * np.pi / omega_d)


def rlc_series_response(R: float, L: float, C: float,
                         initial_charge: float, initial_current: float,
                         t: np.ndarray) -> np.ndarray:
    """
    §31: Final equations of condenser charge and discharge, in
    exponential form.

    Solves L*d²q/dt² + R*dq/dt + q/C = 0 (free response) given
    initial conditions q(0), i(0)=dq/dt(0).

    Returns charge q(t).
    """
    case = rlc_series_case(R, L, C)
    alpha = rlc_damping_constant(R, L)

    if case == 'oscillatory':
        omega_d = rlc_oscillatory_frequency(R, L, C)
        # q(t) = exp(-alpha*t) * (A*cos(omega_d*t) + B*sin(omega_d*t))
        A = initial_charge
        B = (initial_current + alpha * initial_charge) / omega_d
        return np.exp(-alpha * t) * (A * np.cos(omega_d * t) +
                                      B * np.sin(omega_d * t))

    elif case == 'critical':
        # q(t) = exp(-alpha*t) * (A + B*t)
        A = initial_charge
        B = initial_current + alpha * initial_charge
        return np.exp(-alpha * t) * (A + B * t)

    else:  # logarithmic / overdamped
        D = rlc_series_discriminant(R, L, C)
        s1 = -alpha + np.sqrt(D)
        s2 = -alpha - np.sqrt(D)
        # q(t) = A*exp(s1*t) + B*exp(s2*t)
        # initial conditions: A + B = q(0), A*s1 + B*s2 = i(0)
        A = (initial_current - s2 * initial_charge) / (s1 - s2)
        B = initial_charge - A
        return A * np.exp(s1 * t) + B * np.exp(s2 * t)


# ──────────────────────────────────────────────────────────────────────
# SECTION I — CHAPTER VI: OSCILLATING CURRENTS (§44-54)
#
# Builds on Chapter V: the oscillatory case is the basis for AC generators
# and high-frequency engineering. §48: 'Independence of oscillating
# current frequency on size of condenser and inductance' — within
# practical limits, the LC product determines frequency.
# ──────────────────────────────────────────────────────────────────────

def lc_natural_frequency(L: float, C: float) -> float:
    """f_0 = 1/(2*pi*sqrt(L*C)). The natural frequency of an LC tank.

    §48: This is the foundation of all classical electrical oscillation —
    Atlas's cosmological wave-field engine generalizes this to any pair
    of complementary stores (graha pair) with their characteristic
    coupling structure."""
    if L <= 0 or C <= 0:
        return 0.0
    return 1.0 / (2 * np.pi * np.sqrt(L * C))


# ──────────────────────────────────────────────────────────────────────
# SECTION III — CHAPTER II: LONG-DISTANCE TRANSMISSION LINE
# (§3-12, the spatial-wave/four-constant treatment)
#
# §5: "The four constants of the transmission line: r, L, g, C"
#
# This is the spatial-wave generalization of the lumped-circuit
# treatment from Section I. Steinmetz writes the line as differential
# equations in space and time, then solves via versor algebra in the
# steady-state.
# ──────────────────────────────────────────────────────────────────────

@dataclass
class TransmissionLine:
    """
    §5: The four-constant transmission line.

    For a uniform line, r, L, g, C are PER UNIT LENGTH:
        r — series resistance per unit length (ohms/meter)
        L — series inductance per unit length (henrys/meter)
        g — shunt conductance per unit length (siemens/meter)
        C — shunt capacitance per unit length (farads/meter)

    These four constants together determine all wave-propagation
    properties of the line at any frequency.

    Atlas correspondence:
        r ↔ electric register (resistive dissipation)
        L ↔ magnetic register (inductive storage)
        g ↔ electric register (leakage dissipation)
        C ↔ dielectric register (capacitive storage)

    The four-quadrant framework Dollard articulates is operational
    here: every uniform wave-supporting medium has all four constants,
    and the wave behavior is jointly determined by the magnetic (L) and
    dielectric (C) primaries with electric (r, g) loss components.
    """
    r: float  # series resistance per unit length
    L: float  # series inductance per unit length
    g: float  # shunt conductance per unit length
    C: float  # shunt capacitance per unit length

    def series_impedance_per_length(self, omega: float) -> complex:
        """Z = r + j*omega*L  (per unit length)."""
        return self.r + j * omega * self.L

    def shunt_admittance_per_length(self, omega: float) -> complex:
        """Y = g + j*omega*C  (per unit length)."""
        return self.g + j * omega * self.C

    def propagation_constant(self, omega: float) -> complex:
        """gamma = sqrt(Z*Y)
        gamma = alpha + j*beta where:
            alpha = attenuation constant (nepers per unit length)
            beta = phase constant (radians per unit length)
        """
        Z = self.series_impedance_per_length(omega)
        Y = self.shunt_admittance_per_length(omega)
        return np.sqrt(Z * Y)

    def characteristic_impedance(self, omega: float) -> complex:
        """Z_0 = sqrt(Z/Y), the line's characteristic surge impedance.

        This is the COMPLEX generalization of Dollard's
        Z_0 = sqrt(L/C) — at finite frequency with finite r, g,
        Z_0 is itself complex, with real and imaginary parts encoding
        the line's frequency-dependent dissipation balance."""
        Z = self.series_impedance_per_length(omega)
        Y = self.shunt_admittance_per_length(omega)
        if abs(Y) == 0:
            return complex(float('inf'), 0)
        return np.sqrt(Z / Y)

    def lossless_phase_velocity(self) -> float:
        """In the r=g=0 limit: v = 1/sqrt(L*C). Wave propagation speed."""
        if self.L <= 0 or self.C <= 0:
            return 0.0
        return 1.0 / np.sqrt(self.L * self.C)

    def attenuation_constant(self, omega: float) -> float:
        """alpha = Re(gamma). Nepers per unit length of attenuation."""
        return self.propagation_constant(omega).real

    def phase_constant(self, omega: float) -> float:
        """beta = Im(gamma). Radians per unit length of phase advance."""
        return self.propagation_constant(omega).imag


# Standalone forms for convenience
def propagation_constant(r: float, L: float, g: float, C: float,
                          omega: float) -> complex:
    """Standalone: gamma = sqrt((r + jωL)(g + jωC))."""
    line = TransmissionLine(r=r, L=L, g=g, C=C)
    return line.propagation_constant(omega)


def characteristic_impedance_line(r: float, L: float, g: float, C: float,
                                   omega: float) -> complex:
    """Standalone: Z_0 = sqrt((r + jωL)/(g + jωC))."""
    line = TransmissionLine(r=r, L=L, g=g, C=C)
    return line.characteristic_impedance(omega)


# ──────────────────────────────────────────────────────────────────────
# SECTION I — CHAPTER XIII: ROTATING FIELD TRANSIENT (§106-111)
#
# §106: "Polyphase m.m.fs. producing magnetic field of constant
# intensity, revolving with uniform synchronous velocity."
#
# This is where Steinmetz treats the polyphase rotating magnetic field
# — directly relevant to Atlas's wave-field engine, since Atlas's graha
# system is a polyphase rotating arrangement at cosmological scale.
#
# §107: "The sum of instantaneous values of the permanent as well as
# the transient term of polyphase m.m.fs. equals zero."
#
# This is a profound symmetry statement: in a balanced n-phase system,
# the algebraic sum of all phase contributions (both steady and
# transient) is identically zero. Same property Atlas uses when
# evaluating multi-graha sums.
# ──────────────────────────────────────────────────────────────────────

def polyphase_mmf_sum(amplitudes: np.ndarray, phases_rad: np.ndarray,
                       omega: float, t: float) -> complex:
    """
    §108: Resultant of polyphase m.m.f. system.

    Given n phases each with amplitude A_k and starting phase phi_k,
    rotating at frequency omega, the resultant at time t is:

        F(t) = Σ_k A_k * exp(j*(omega*t + phi_k))

    For a BALANCED symmetric system (equal amplitudes, equally-spaced
    phases), the resultant is a constant-magnitude vector rotating
    uniformly — the "rotating magnetic field" of polyphase machines.

    Atlas: same algebra computes the rotating wave-field state of any
    n-graha symmetric arrangement.
    """
    return np.sum(amplitudes * np.exp(j * (omega * t + phases_rad)))


def is_balanced_polyphase(amplitudes: np.ndarray,
                          phases_rad: np.ndarray,
                          tolerance: float = 1e-9) -> bool:
    """A polyphase system is balanced if all amplitudes are equal AND
    phases are equally spaced. §107 guarantees the instantaneous sum
    is zero in this case."""
    if len(amplitudes) < 2:
        return False
    n = len(amplitudes)
    # Check equal amplitudes
    if not np.allclose(amplitudes, amplitudes[0], atol=tolerance):
        return False
    # Check equal phase spacing (modulo 2*pi/n)
    expected_spacing = 2 * np.pi / n
    sorted_phases = np.sort(phases_rad % (2 * np.pi))
    spacings = np.diff(sorted_phases)
    return np.allclose(spacings, expected_spacing, atol=tolerance)


def balanced_polyphase_resultant_magnitude(single_phase_amplitude: float,
                                            n_phases: int) -> float:
    """For a balanced n-phase system, each phase contributes A;
    the resultant rotating-field magnitude is (n/2)*A.

    §108: 'Maximum value of permanent term.'
    """
    return (n_phases / 2.0) * single_phase_amplitude


# ──────────────────────────────────────────────────────────────────────
# CONNECTION TO DOLLARD'S FOUR-QUADRANT FRAMEWORK
# ──────────────────────────────────────────────────────────────────────

class FourQuadrantConstants:
    """
    Map between Steinmetz's four transmission-line constants {r, L, g, C}
    and Dollard's four-quadrant framework. These are the SAME structure
    seen from different angles:

        Steinmetz                    Dollard
        ─────────                    ───────
        r (resistance)               electric register / loss
        g (conductance/leakage)      electric register / loss
        L (inductance)               magnetic register
        C (capacitance)              dielectric register

    The four-quadrant framework's claim is that {magnetic, dielectric}
    are the two PRIMARY storage registers, while {r, g} are dissipation
    pathways out of those registers. Steinmetz's transmission-line
    treatment makes this explicit by writing the wave equation with
    these four constants on equal footing.

    Atlas's bhumi-stratification framework should test phenomena against
    this four-quadrant decomposition: some phenomena live primarily in
    the magnetic mode (L-coupled), some primarily in the dielectric mode
    (C-coupled), some are dissipative (r or g coupled), and the
    discrimination among them is what tonight's framework correction
    operationalizes.
    """

    @staticmethod
    def storage_registers() -> dict:
        return {
            "magnetic": "L (inductance) — broadside-radial, expansion-outward",
            "dielectric": "C (capacitance) — axial-longitudinal, compression-inward",
        }

    @staticmethod
    def dissipation_registers() -> dict:
        return {
            "series_loss": "r (resistance) — power dissipated in current flow",
            "shunt_loss": "g (conductance) — power dissipated in voltage gradient",
        }


if __name__ == "__main__":
    # Self-test
    print("Steinmetz transient phenomena math extract — self test")
    print("=" * 65)

    # §20: R-L circuit transient
    print("\n§20: R-L circuit transient (E=10V, R=5Ω, L=0.1H, i(0)=0)")
    t = np.array([0.0, 0.02, 0.04, 0.06, 0.1])
    i = rl_circuit_transient(emf=10.0, resistance=5.0, inductance=0.1,
                              initial_current=0.0, t=t)
    for tk, ik in zip(t, i):
        print(f"  t={tk:.3f}s: i={ik:.4f}A")
    print(f"  time constant tau = L/R = {time_constant_RL(5.0, 0.1):.3f}s")

    # §29-43: R-L-C series oscillation
    print("\n§29-43: R-L-C series transient (R=10Ω, L=0.1H, C=1μF)")
    R, L, C = 10.0, 0.1, 1e-6
    print(f"  case: {rlc_series_case(R, L, C)}")
    print(f"  critical resistance: {critical_resistance(L, C):.2f}Ω (R={R}Ω is below → oscillatory)")
    print(f"  oscillation frequency: {rlc_oscillatory_frequency(R, L, C)/(2*np.pi):.2f} Hz")
    print(f"  decrement per cycle: {rlc_decrement(R, L, C):.4f}")

    # §5: transmission line four constants
    print("\n§5: Transmission line (typical telephone-line values)")
    line = TransmissionLine(r=10e-3, L=1e-6, g=1e-9, C=10e-12)
    omega = 2 * np.pi * 1000  # 1 kHz
    gamma = line.propagation_constant(omega)
    Z0 = line.characteristic_impedance(omega)
    print(f"  at 1 kHz:")
    print(f"    propagation constant γ = {gamma:.4e}")
    print(f"    attenuation α = {gamma.real:.4e} Np/m")
    print(f"    phase constant β = {gamma.imag:.4e} rad/m")
    print(f"    characteristic impedance Z_0 = {Z0:.4f} Ω")
    print(f"    lossless phase velocity = {line.lossless_phase_velocity():.2e} m/s")

    # §107: balanced polyphase property
    print("\n§107: Balanced 3-phase system instantaneous sum")
    amps = np.array([1.0, 1.0, 1.0])
    phases = np.array([0, 2*np.pi/3, 4*np.pi/3])
    print(f"  is_balanced: {is_balanced_polyphase(amps, phases)}")
    # Sum at several time points should be approximately zero in REAL part,
    # but rotating in complex form
    for t in [0, 0.001, 0.002]:
        r = polyphase_mmf_sum(amps, phases, omega=2*np.pi*60, t=t)
        print(f"  t={t:.3f}s: resultant = {r:.6f}, |r|={abs(r):.6f}")
    print("  (constant-magnitude rotating vector — Atlas's polyphase wave-field analog)")
