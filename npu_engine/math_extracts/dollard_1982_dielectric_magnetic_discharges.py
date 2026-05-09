"""
math_extracts/dollard_1982_dielectric_magnetic_discharges.py

Mathematical content extracted from:
  Eric Dollard, "Introduction to Dielectric & Magnetic Discharges in
  Electrical Windings" (1982)

Source: directly extracted from PDF. All equations verified against text.
Section references match Dollard's numbered sections (§1-§23) and his
Appendix Tables I-II.

This module provides the operational mathematical structure of the
four-quadrant framework as it appears in Dollard's monograph. Heavier
mathematical foundation (versor algebra, transient analysis) lives in
steinmetz_*.py modules.

Atlas usage:
    from math_extracts.dollard_1982_dielectric_magnetic_discharges import (
        MagneticCircuit, DielectricCircuit,
        characteristic_impedance, oscillation_frequency,
        magnetic_energy, dielectric_energy,
        FourQuadrantDimensions,
    )

Cross-reference: this file is the *prose-articulation-level* math.
For the underlying versor algebra Steinmetz used (which Dollard cites
as foundation), see steinmetz_transient_phenomena.py.
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional


# ──────────────────────────────────────────────────────────────────────
# CONSTANTS (Dollard's Appendix Tables I-II)
# ──────────────────────────────────────────────────────────────────────

# Dollard uses CGS in Table I: "v = 3 X 10^10 = velocity of light"
v_LIGHT_CGS = 3.0e10  # cm/sec

# MKS values for Atlas's modern usage
EPSILON_0 = 8.854e-12   # farad/meter, free-space permittivity
MU_0 = 4 * np.pi * 1e-7  # henry/meter, free-space permeability
c_LIGHT = 2.998e8        # m/sec, velocity of light (MKS)


# ──────────────────────────────────────────────────────────────────────
# §13–14: PARALLEL REGISTERS (the load-bearing structural claim)
#
# Dollard quoting Steinmetz (§2-3):
#   "the prehistoric conception of the electrostatic charge (electron)
#    on the conductor still exists, and by its use destroys the
#    analogy between the two components of the electric field"
#
# §14: "Voltage Is to Dielectricity as Current Is to Magnetism"
# ──────────────────────────────────────────────────────────────────────

@dataclass
class MagneticCircuit:
    """
    Magnetic circuit quantities (Dollard Appendix Table II, left column).

    The magnetic register: broadside-radial geometry, expansion-outward,
    energy storage in field volume swept by lines of force.

    Quantity-level analogy: magnetic-current = magnetic flux phi,
    magnetomotive-force F = ni, inductance L, magnetic energy Li²/2.
    """
    flux: float          # phi, lines of magnetic force
    current: float       # i, amperes
    turns: int           # n, number of turns
    inductance: float    # L, henrys
    permeability: float  # mu

    @property
    def magnetomotive_force(self) -> float:
        """F = ni  (Table II)."""
        return self.turns * self.current

    @property
    def reluctance(self) -> float:
        """R = F/phi  (Table II)."""
        return self.magnetomotive_force / self.flux if self.flux else float('inf')

    @property
    def permeance(self) -> float:
        """1/R = phi/F  (inverse of reluctance, Table II)."""
        return self.flux / self.magnetomotive_force if self.magnetomotive_force else float('inf')

    @property
    def stored_energy(self) -> float:
        """W = (L*i²)/2  joules  (Table I, Magnetic energy)."""
        return 0.5 * self.inductance * self.current**2

    @property
    def induced_voltage(self) -> float:
        """e' = L * di/dt — at static field, di/dt=0, so this requires
        time-derivative context. Returned form is the magnitude
        coefficient L for use with external di/dt."""
        return self.inductance  # caller multiplies by di/dt


@dataclass
class DielectricCircuit:
    """
    Dielectric circuit quantities (Dollard Appendix Table II, middle column).

    The dielectric register: axial-longitudinal geometry, compression-inward,
    energy storage in compression of medium between conducting surfaces.

    Quantity-level analogy: dielectric-current = dielectric flux psi,
    electromotive-force e (voltage), capacity C, dielectric energy Ce²/2.
    """
    flux: float          # psi, lines of dielectric force
    voltage: float       # e, volts
    capacity: float      # C, farads
    permittivity: float  # kappa (specific capacity)

    @property
    def elastance(self) -> float:
        """1/C = e/(4*pi*v² * psi)  (Table II, the dielectric analog
        of reluctance — Dollard marks this with '?' suggesting the
        terminology was not fully standardized in 1982)."""
        return 1.0 / self.capacity if self.capacity else float('inf')

    @property
    def stored_energy(self) -> float:
        """W = (C*e²)/2  joules  (Table I, Dielectric energy)."""
        return 0.5 * self.capacity * self.voltage**2

    @property
    def induced_current(self) -> float:
        """i' = C * de/dt — coefficient form, caller multiplies by de/dt.

        §14: 'The reaction of capacitance to change of applied force is
        the production of current. The current is directly proportional
        to the velocity of field strength.'"""
        return self.capacity  # caller multiplies by de/dt


# ──────────────────────────────────────────────────────────────────────
# §13: GEOMETRIC DISTINCTION (broadside-radial vs axial-longitudinal)
#
# "Dielectric lines of force push inward into internal space and along
#  axis, rather than pushed outward broadside to axis as in the magnetic
#  field. ... the smaller the space bounded by the conducting structure
#  the more energy that can be stored. This is the exact opposite of
#  magnetism."
# ──────────────────────────────────────────────────────────────────────

class FieldGeometry:
    """
    Constants and helpers for the broadside-radial vs axial-longitudinal
    distinction Dollard articulates in §13.

    For Atlas's versor decomposition:
        BROADSIDE_RADIAL → magnetic mode → Re(Σ Z_k)
        AXIAL_LONGITUDINAL → dielectric mode → Im(Σ Z_k)
    """
    BROADSIDE_RADIAL = "magnetic"      # expansion-outward, parallel volumes
    AXIAL_LONGITUDINAL = "dielectric"  # compression-inward, series volumes

    @staticmethod
    def magnetic_volumes_combine_in_parallel(volumes: list) -> float:
        """§13: 'the units volumes of energy can be thought of as working
        in parallel' for magnetic storage."""
        return sum(volumes)

    @staticmethod
    def dielectric_volumes_combine_in_series(volumes: list) -> float:
        """§13: 'the unit volumes of energy in association with
        dielectricity can be thought of as working in series'."""
        if any(v == 0 for v in volumes):
            return float('inf')
        return 1.0 / sum(1.0/v for v in volumes)


# ──────────────────────────────────────────────────────────────────────
# §17–18: ENERGY PULSATION AND CHARACTERISTIC IMPEDANCE
#
# §17: "The capacitance dumps all its energy back into the magnetic
#   field and the whole process starts over again. The inverse of the
#   product of magnetic storage capacity and dielectric storage capacity
#   represents the frequency or pitch at which this energy interchange
#   occurs."
#
# §18: "The ratio of magnetic storage ability to that of the dielectric
#   is called the characteristic impedance. ... the total or double
#   energy field pulsates in shape or size. The axis of this pulsation
#   of force is the impedance of the system displaying oscillations and
#   pulsation occurs at the frequency of oscillation."
# ──────────────────────────────────────────────────────────────────────

def oscillation_frequency(L: float, C: float) -> float:
    """
    Frequency of LC energy interchange.

    Dollard §17: "The inverse of the product of magnetic storage
    capacity and dielectric storage capacity represents the frequency
    or pitch at which this energy interchange occurs."

    Standard form: f = 1 / (2*pi*sqrt(L*C))

    Args:
        L: inductance in henrys
        C: capacitance in farads

    Returns:
        frequency in Hz
    """
    if L <= 0 or C <= 0:
        return 0.0
    return 1.0 / (2.0 * np.pi * np.sqrt(L * C))


def angular_frequency(L: float, C: float) -> float:
    """omega = 1/sqrt(L*C)  (radians per second)."""
    if L <= 0 or C <= 0:
        return 0.0
    return 1.0 / np.sqrt(L * C)


def characteristic_impedance(L: float, C: float) -> float:
    """
    Characteristic impedance Z_0 = sqrt(L/C)  ohms.

    §18: "The ratio of magnetic storage ability to that of the
    dielectric is called the characteristic impedance. This gives
    the ratio of maximum voltage to maximum current in the
    oscillatory structure."

    Args:
        L: inductance in henrys
        C: capacitance in farads

    Returns:
        characteristic impedance in ohms
    """
    if C <= 0:
        return float('inf')
    return np.sqrt(L / C)


def voltage_to_current_ratio_at_resonance(L: float, C: float,
                                          v_max: Optional[float] = None,
                                          i_max: Optional[float] = None) -> dict:
    """
    Return the voltage-current relationship at resonance per §18.

    If v_max provided: returns expected i_max for given Z_0.
    If i_max provided: returns expected v_max for given Z_0.
    """
    Z = characteristic_impedance(L, C)
    out = {"characteristic_impedance": Z}
    if v_max is not None:
        out["expected_i_max"] = v_max / Z if Z else 0.0
    if i_max is not None:
        out["expected_v_max"] = i_max * Z
    return out


# ──────────────────────────────────────────────────────────────────────
# §10–11, §15–16: LIMITING CASES (zero/infinity behavior)
#
# §10: "If we remove the current supply by shorting the terminals of
#   the inductor we have isolated it without interrupting any current.
#   ... No E.M.F. can combine with current to form power, therefore,
#   the energy will remain in the field."
#
# §11: "Because the current vanished instantly the field collapses at
#   a velocity approaching that of light. As E.M.F. is directly
#   released to velocity of flux, it tends towards infinity."
#
# §15-16: parallel statements for dielectric: open-circuit traps energy,
#   short-circuit produces explosive discharge (inverse pattern from
#   inductor).
# ──────────────────────────────────────────────────────────────────────

class LimitingCase:
    """Boundary-condition behaviors for inductor and capacitor at limits."""

    @staticmethod
    def inductor_short_circuit_traps_energy() -> dict:
        """§10: shorting an ideal inductor preserves stored magnetic energy.
        Returns the constraint relations."""
        return {
            "voltage_across": 0.0,         # short-circuit definition
            "energy_change_rate": 0.0,     # no E*I to dissipate
            "current_persists": True,
            "field_persists": True,
            "interpretation": "energy_trapped_in_magnetic_field",
        }

    @staticmethod
    def inductor_open_circuit_explodes() -> dict:
        """§11: opening an inductor with stored energy produces explosive
        discharge — E.M.F. tends to infinity as current vanishes instantly."""
        return {
            "current_through": 0.0,        # open-circuit definition
            "voltage_tendency": float('inf'),
            "field_collapse_velocity": "approaches_c",
            "interpretation": "explosive_dielectric_emergence_from_collapsing_magnetic_field",
        }

    @staticmethod
    def capacitor_open_circuit_traps_energy() -> dict:
        """§15: opening an ideal capacitor preserves stored dielectric energy."""
        return {
            "current_through": 0.0,        # open-circuit definition
            "energy_change_rate": 0.0,
            "voltage_persists": True,
            "field_persists": True,
            "interpretation": "energy_trapped_in_dielectric_field",
        }

    @staticmethod
    def capacitor_short_circuit_explodes() -> dict:
        """§16: shorting a capacitor with stored energy produces explosive
        discharge — current tends to infinity as voltage vanishes instantly.

        '...the field explodes against the bounding conductors with a
        velocity that may exceed light. Because the current is directly
        related to the velocity of field it jumps to infinity in its
        attempt to produce finite voltage across zero resistance.'"""
        return {
            "voltage_across": 0.0,         # short-circuit definition
            "current_tendency": float('inf'),
            "field_velocity": "may_exceed_c",  # Dollard's claim; note carefully
            "interpretation": "explosive_magnetic_emergence_from_collapsing_dielectric_field",
        }


# ──────────────────────────────────────────────────────────────────────
# APPENDIX TABLE I: Field-quantity relationships (Steinmetz form)
# ──────────────────────────────────────────────────────────────────────

class TableI_FieldQuantities:
    """Dollard Appendix Table I — parallel field-quantity formulas in
    Steinmetz's notation. These are the dimensional-relationship
    formulas connecting flux, density, intensity, and force."""

    @staticmethod
    def magnetic_flux(L: float, i: float) -> float:
        """phi = L*i * 10^8 lines of magnetic force  (Table I, CGS)."""
        return L * i * 1e8

    @staticmethod
    def magnetic_field_intensity(magnetomotive_force_per_cm: float) -> float:
        """H = 4*pi * f * 10^-1  lines per cm² (Table I).
        Where f is magnetomotive force per cm."""
        return 4.0 * np.pi * magnetomotive_force_per_cm * 1e-1

    @staticmethod
    def magnetic_density(H: float, mu: float) -> float:
        """B = mu * H  lines per cm² (Table I)."""
        return mu * H

    @staticmethod
    def dielectric_flux(C: float, e: float) -> float:
        """psi = C*e  lines of dielectric force (Table I)."""
        return C * e

    @staticmethod
    def dielectric_field_intensity(voltage_gradient: float,
                                   v_light: float = v_LIGHT_CGS) -> float:
        """K = G / (4*pi*v²)  lines per cm² (Table I).
        Where G is voltage gradient (volts per cm)."""
        return voltage_gradient / (4.0 * np.pi * v_light**2)

    @staticmethod
    def dielectric_density(K: float, kappa: float) -> float:
        """D = kappa * K  lines per cm² (Table I)."""
        return kappa * K


# ──────────────────────────────────────────────────────────────────────
# APPENDIX TABLE II: Magnetic / Dielectric / Electric circuit dual
# ──────────────────────────────────────────────────────────────────────

@dataclass
class TableII_CircuitDualities:
    """Dollard Appendix Table II — the three-column dual structure of
    magnetic, dielectric, and electric (resistive) circuits.

    This is the dimensional table that makes the four-quadrant framework
    structurally explicit. Each column is a distinct register; rows are
    parallel quantities across registers.
    """

    # --- Magnetic column ---
    magnetic_flux: float
    magnetomotive_force: float
    permeance: float
    inductance: float
    reluctance: float
    magnetic_energy: float
    magnetic_density: float
    magnetic_field_intensity: float
    permeability: float

    # --- Dielectric column ---
    dielectric_flux: float
    electromotive_force: float
    permittance: float    # capacity
    dielectric_energy: float
    dielectric_density: float
    dielectric_gradient: float
    dielectric_field_intensity: float
    permittivity: float

    # --- Electric (resistive) column, completes the four-quadrant ---
    electric_current: float
    voltage: float
    conductance: float
    resistance: float
    electric_power: float
    current_density: float
    electric_gradient: float
    conductivity: float

    @classmethod
    def magnetic_dual_of(cls, **dielectric_quantities) -> dict:
        """Map dielectric-register quantities to their magnetic duals.
        Useful when the framework predicts a phenomenon in one register
        and you want the parallel quantity in the other."""
        dual_map = {
            "dielectric_flux": "magnetic_flux",
            "electromotive_force": "magnetomotive_force",
            "permittance": "permeance",
            "dielectric_energy": "magnetic_energy",
            "dielectric_density": "magnetic_density",
            "dielectric_field_intensity": "magnetic_field_intensity",
            "permittivity": "permeability",
        }
        return {dual_map[k]: v for k, v in dielectric_quantities.items() if k in dual_map}


# ──────────────────────────────────────────────────────────────────────
# §22: STEINMETZ-CITED RESULT — FREE-SPACE INDUCTANCE IS INFINITE
#
# "Steinmetz in his book on the general or unified behavior of
#  electricity 'The Theory and Calculation of Transient Electric
#  Phenomena and Oscillation,' points out that the inductance of any
#  unit length of an isolated filamentary conductor must be infinite.
#  Because no image currents exist to contain the magnetic field it
#  can grow to infinite size."
# ──────────────────────────────────────────────────────────────────────

def free_space_inductance_per_unit_length(image_current_present: bool) -> float:
    """
    Returns inductance per unit length of an isolated filamentary
    conductor.

    Dollard §22 (citing Steinmetz Transient Phenomena §III, Ch. VIII):
    Without image currents to contain the magnetic field, inductance
    is infinite. With image currents (return path), inductance is finite.

    This has a structural parallel for dielectric (§20):
    'free space capacitance of an object is the sum mutual capacity of
    it to all the conducting objects of the universe.'
    """
    if not image_current_present:
        return float('inf')
    raise NotImplementedError(
        "Finite-inductance computation requires image-current geometry; "
        "see steinmetz_transient_phenomena.py Section III, Chapter VIII."
    )


def free_space_capacitance(other_conductors_present: bool) -> float:
    """
    §20: 'If we take any conductor and remove it to the most remote
    portion of the universe, no lines of force can extend from this
    electrode to other conductors. It can have no free space capacity,
    regardless of the size of the electrode, therefore it can store
    no energy. This indicates that the free space capacitance of an
    object is the sum mutual capacity of it to all the conducting
    objects of the universe.'

    Without other conductors as termination points, capacitance is zero.
    """
    if not other_conductors_present:
        return 0.0
    raise NotImplementedError(
        "Mutual-capacity computation requires geometric configuration; "
        "see Steinmetz Transient Phenomena for the general method."
    )


# ──────────────────────────────────────────────────────────────────────
# §23: CONJUGATE SPACE HYPOTHESIS (SPECULATIVE — explicitly hedged)
# ──────────────────────────────────────────────────────────────────────

class ConjugateSpaceHypothesis:
    """
    §23: 'It is possible that additional or conjugate space exists
    within the same boundaries as ordinary space. The properties of
    lines of force within this conjugate space may not obey the laws
    of normally conceived space.'

    This is Dollard's most speculative claim, hedged in the original
    ('It is possible that...'). Atlas should NOT use this as established
    framework — it is recorded as Dollard's open question.

    Structural parallel to vyāpaka ākāśa in classical Indian cosmology
    (interpenetrating space-register that does not obey conventional
    spatial laws). Convergence is structural, not equivalent.
    """

    STATUS = "SPECULATIVE_HEDGED_BY_AUTHOR"

    HYPOTHESIS = (
        "Additional/conjugate space may coexist within ordinary space. "
        "Dielectric flux propagation may use this register, with "
        "different propagation laws than ordinary 3D space."
    )

    OPEN_QUESTION = (
        "Question raised by §23: how does dielectric flux maintain "
        "the constraint that no line of force can end in space, during "
        "the time before the field has propagated to a distant neutral "
        "conductor? Three resolutions: instant propagation, always-existing "
        "modulated lines, or conjugate-space propagation."
    )

    VEDIC_PARALLEL = "vyāpaka ākāśa (interpenetrating space)"


# ──────────────────────────────────────────────────────────────────────
# UTILITY: cross-tradition lookup for the framework
# ──────────────────────────────────────────────────────────────────────

DIELECTRIC_REGISTER_TERMS = {
    "engineering": ["dielectric", "axial", "longitudinal", "compression-inward",
                    "voltage", "capacitance", "elastance"],
    "schauberger": ["implosion", "centripetal", "inward-spiral", "living-water"],
    "russell":     ["generative", "compressed-tone", "centripetal-octave"],
    "vedic":       ["vyāpaka ākāśa", "ākāśa-mahābhūta-substrate",
                    "longitudinal-prāṇa-flow"],
}

MAGNETIC_REGISTER_TERMS = {
    "engineering": ["magnetic", "broadside", "transverse", "expansion-outward",
                    "current", "inductance", "reluctance"],
    "schauberger": ["explosion", "centrifugal", "outward-spiral", "dead-water"],
    "russell":     ["radiative", "decompressed-tone", "centrifugal-octave"],
    "vedic":       ["bahirmukha-prāṇa", "outward-vāyu",
                    "broadside-vāyu-component"],
}


if __name__ == "__main__":
    # Quick self-test
    print("Dollard 1982 math extract — self test")
    print("=" * 60)

    # §17-18 worked example: a 50 microhenry / 0.001 microfarad system
    # (these are the values from Miller's Fig. 4 in Part II of Dollard's
    # combined volume — a real test case)
    L = 50e-6
    C = 1e-9
    f = oscillation_frequency(L, C)
    Z0 = characteristic_impedance(L, C)
    print(f"L = {L} H, C = {C} F")
    print(f"  oscillation frequency f = {f:.2e} Hz  ({f/1e6:.2f} MHz)")
    print(f"  characteristic impedance Z_0 = {Z0:.2f} ohms")

    # Magnetic ↔ dielectric duality demonstration
    diel_state = {
        "dielectric_flux": 1e-6,
        "electromotive_force": 1000.0,
        "permittance": 1e-9,
    }
    mag_dual = TableII_CircuitDualities.magnetic_dual_of(**diel_state)
    print(f"\nDielectric → magnetic dual quantities:")
    for k, v in mag_dual.items():
        print(f"  {k}: {v}")

    # Limiting case demonstration
    print(f"\nLimiting cases:")
    print(f"  inductor short → {LimitingCase.inductor_short_circuit_traps_energy()['interpretation']}")
    print(f"  inductor open  → {LimitingCase.inductor_open_circuit_explodes()['interpretation']}")
    print(f"  capacitor open → {LimitingCase.capacitor_open_circuit_traps_energy()['interpretation']}")
    print(f"  capacitor short → {LimitingCase.capacitor_short_circuit_explodes()['interpretation']}")
