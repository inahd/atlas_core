"""
Wootz nanoscale solidification simulation under ambient electromagnetic conditions.

Models 2D dendritic growth in high-carbon steel cooling from melt, with vanadium
impurity segregation producing the carbide-band structure characteristic of Damascus
steel. Adds a coupling term for ambient magnetic field that biases dendrite
alignment direction during solidification.

The physics:
- Phase-field method for dendritic growth (simplified)
- Solute (vanadium) segregation tracked separately
- Magnetic field bias term affects dendrite tip growth direction
- Output: 2D field showing dendritic structure with vanadium concentration overlay

Honest scope:
- This is plausibility modeling, not verified physics
- Geomagnetic field strength (~50 microtesla) is small; whether it actually affects
  steel dendrite alignment at solidification temperatures is uncertain in the
  literature
- The simulation demonstrates the framework; physical validation would require
  laboratory experiments

Integration with Atlas:
- Input: astro-state (panchanga, graha positions, wave-field) drives the magnetic
  field bias parameter
- Output: predicted carbide-alignment metrics that could be compared against
  empirical wootz outcomes
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass
class WootzMeltConditions:
    """Initial conditions for the wootz melt at the start of solidification."""

    # Composition
    carbon_pct: float = 1.5  # wt% carbon (wootz range: 1.0-2.0)
    vanadium_ppm: float = 50.0  # ppm vanadium (Verhoeven: critical impurity ~50 ppm)
    chromium_ppm: float = 30.0  # ppm chromium (secondary carbide-forming element)
    molybdenum_ppm: float = 10.0  # ppm molybdenum

    # Initial thermal state
    initial_temp_c: float = 1450.0  # melt temperature
    final_temp_c: float = 700.0  # forging temperature target
    cooling_rate_c_per_min: float = 8.0  # accelerated for simulation (real wootz ~2 C/min)

    # Geometry
    grid_size: int = 256  # simulation grid (nanometer-scale: 256x256 nm region)
    pixel_size_nm: float = 1.0  # 1 nm per pixel

    def carbon_mass_fraction(self) -> float:
        return self.carbon_pct / 100.0

    def vanadium_mass_fraction(self) -> float:
        return self.vanadium_ppm * 1e-6


@dataclass
class AstroFieldConditions:
    """
    Ambient field conditions during solidification, derived from astro-state.

    These are the inputs Atlas would compute from current panchanga state and
    feed into the simulation as the 'transduction' layer between cosmological
    state and materials process.
    """

    # Geomagnetic field strength (microtesla, typical Earth surface ~25-65)
    geomagnetic_field_ut: float = 45.0

    # Geomagnetic field orientation (radians, 0 = aligned with crystal growth axis)
    field_orientation_rad: float = 0.0

    # Geomagnetic disturbance (Kp index, 0=quiet, 9=major storm)
    kp_index: float = 2.0

    # Tidal forcing strength (normalized 0-1, lunar/solar gravitational pull)
    tidal_forcing: float = 0.5

    # Wave-field interference value at this moment (from Atlas two-source interference)
    wave_field_value: float = 0.0  # range typically -1 to +1

    # Atlas-specific: graha-friendship score for the operation
    # 1.0 = supportive grahas dominant, -1.0 = adversarial dominant
    graha_compatibility: float = 0.0

    # Tithi (lunar phase, 1-30 in Atlas convention; Purnima=15, Amavasya=30)
    tithi: int = 15

    def effective_field_strength(self) -> float:
        """
        Compute effective field strength for the simulation.

        Combines geomagnetic, tidal, and wave-field contributions. This is the
        transduction layer where astrological/cosmological state becomes a single
        physical input parameter for the materials simulation.

        Note: real-world coupling magnitudes are highly uncertain. The combination
        function here is illustrative and should be calibrated against empirical
        data when available.
        """
        # Base geomagnetic contribution (microtesla)
        base = self.geomagnetic_field_ut

        # Kp disturbance amplification (Kp 0-9 scaled to 1-2x multiplier)
        kp_mult = 1.0 + (self.kp_index / 9.0) * 1.0

        # Tidal contribution (modulates field by ~10%)
        tidal_mult = 1.0 + 0.1 * self.tidal_forcing

        # Wave-field contribution from Atlas (modulates by up to 20%)
        wave_mult = 1.0 + 0.2 * self.wave_field_value

        # Graha compatibility (Atlas-specific cosmological factor)
        # This is the most speculative coupling - represents the hypothesis that
        # operations under supportive graha conditions show better alignment
        graha_mult = 1.0 + 0.15 * self.graha_compatibility

        return base * kp_mult * tidal_mult * wave_mult * graha_mult


class WootzSolidificationSim:
    """
    Simplified phase-field-style simulation of dendritic solidification with
    impurity segregation and external field bias.
    """

    def __init__(self, melt: WootzMeltConditions, astro: AstroFieldConditions,
                 random_seed: Optional[int] = None):
        self.melt = melt
        self.astro = astro
        self.rng = np.random.default_rng(random_seed)

        N = melt.grid_size
        # Phase field: 0 = liquid, 1 = solid
        self.phi = np.zeros((N, N), dtype=np.float32)
        # Vanadium concentration field (mass fraction)
        self.vanadium = np.full((N, N), melt.vanadium_mass_fraction(), dtype=np.float32)
        # Carbon concentration field
        self.carbon = np.full((N, N), melt.carbon_mass_fraction(), dtype=np.float32)
        # Temperature field (uniform initially)
        self.temp = np.full((N, N), melt.initial_temp_c, dtype=np.float32)

        self.time_step = 0
        self.history = {
            'temp': [],
            'solid_fraction': [],
            'avg_vanadium_in_solid': [],
            'band_alignment_score': []
        }

        # Seed initial nuclei (random sites for dendrite initiation)
        n_nuclei = 16
        nuclei_positions = self.rng.integers(0, N, size=(n_nuclei, 2))
        for x, y in nuclei_positions:
            self.phi[x, y] = 1.0

    def _compute_solidification_velocity(self) -> np.ndarray:
        """
        Compute local solidification velocity based on temperature, undercooling,
        and external field bias.

        The field-bias term is the key transduction: external magnetic field
        modulates the directional preference of dendrite growth.
        """
        # Undercooling drives solidification (simplified)
        # For Fe-1.5%C, solidus is around 1147 C, liquidus around 1380 C
        # We'll use a simplified single-temperature model
        solidification_temp = 1380.0
        undercooling = np.maximum(solidification_temp - self.temp, 0.0)

        # Base growth rate proportional to undercooling, calibrated so meaningful
        # solidification occurs over ~30-60 simulation steps
        base_velocity = undercooling * 0.002

        # Field bias: stronger field = slightly faster directional growth
        field_strength_normalized = self.astro.effective_field_strength() / 100.0  # normalize to ~1
        field_bias_strength = field_strength_normalized * 0.2  # up to 20% modulation

        return base_velocity * (1.0 + field_bias_strength)

    def _solidify_step(self):
        """One time step of dendritic growth."""
        N = self.melt.grid_size

        # Find liquid cells adjacent to solid (the solidification front)
        # Use simple neighbor-counting via shifts
        solid = self.phi > 0.5
        liquid = ~solid

        # Count solid neighbors for each cell
        neighbors = np.zeros_like(self.phi, dtype=np.int32)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            shifted = np.roll(solid.astype(np.int32), shift=(dx, dy), axis=(0, 1))
            neighbors += shifted

        # Cells eligible to solidify: liquid with at least one solid neighbor
        front = liquid & (neighbors > 0)

        if not np.any(front):
            return

        # Solidification probability per cell
        velocity = self._compute_solidification_velocity()

        # Field-direction bias: cells whose neighbor-direction aligns with field get higher prob
        # Compute field-aligned vs field-perpendicular preference
        cos_field = np.cos(self.astro.field_orientation_rad)
        sin_field = np.sin(self.astro.field_orientation_rad)
        field_strength_norm = self.astro.effective_field_strength() / 50.0  # normalized

        # Anisotropy strength scales with field; strong field gives strong directional pref
        anisotropy = min(field_strength_norm * 0.5, 2.0)  # cap at 2x

        # For each direction, compute alignment with field
        # cells with solid neighbors in field-aligned direction get boosted growth probability
        direction_weights = {
            (1, 0): 1.0 + anisotropy * (cos_field**2 - 0.5),
            (-1, 0): 1.0 + anisotropy * (cos_field**2 - 0.5),
            (0, 1): 1.0 + anisotropy * (sin_field**2 - 0.5),
            (0, -1): 1.0 + anisotropy * (sin_field**2 - 0.5),
        }

        prob_field = np.zeros_like(self.phi)
        for (dx, dy), weight in direction_weights.items():
            shifted = np.roll(solid.astype(np.float32), shift=(dx, dy), axis=(0, 1))
            prob_field += shifted * max(weight, 0.1)

        # Combine base velocity with field-direction weight
        solidify_prob = velocity * prob_field

        # Stochastic solidification
        random_field = self.rng.random(size=self.phi.shape)
        solidifying = front & (random_field < solidify_prob)

        # When a cell solidifies, expel vanadium to neighboring liquid (segregation)
        # Vanadium has partition coefficient k ~ 0.3-0.5 in iron (most stays in liquid)
        partition_coeff = 0.4
        for x, y in zip(*np.where(solidifying)):
            # Vanadium retained in solid
            v_in_solid = self.vanadium[x, y] * partition_coeff
            # Excess pushed to liquid neighbors
            v_excess = self.vanadium[x, y] - v_in_solid
            self.vanadium[x, y] = v_in_solid

            # Distribute excess to liquid neighbors
            liquid_neighbors = []
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = (x + dx) % N, (y + dy) % N
                if liquid[nx, ny]:
                    liquid_neighbors.append((nx, ny))

            if liquid_neighbors:
                share = v_excess / len(liquid_neighbors)
                for nx, ny in liquid_neighbors:
                    self.vanadium[nx, ny] += share

        self.phi[solidifying] = 1.0

    def _cool_step(self, dt_minutes: float):
        """Advance temperature by cooling rate."""
        self.temp -= self.melt.cooling_rate_c_per_min * dt_minutes

    def _compute_band_alignment_score(self) -> float:
        """
        Quantify how aligned the vanadium-rich bands are with the field direction.

        Uses 2D FFT to find dominant orientation of vanadium-concentration variations.
        Score 0 = isotropic, 1 = perfectly aligned with field direction.
        """
        # Only compute over solidified region
        if np.sum(self.phi > 0.5) < 100:
            return 0.0

        # Mask vanadium to solidified region
        v_field = np.where(self.phi > 0.5, self.vanadium, 0)

        # 2D FFT
        fft = np.fft.fft2(v_field - np.mean(v_field))
        power = np.abs(fft) ** 2

        # Compute orientation of dominant frequencies
        N = self.melt.grid_size
        ky, kx = np.meshgrid(np.fft.fftfreq(N), np.fft.fftfreq(N), indexing='ij')

        # Skip DC component
        mask = (kx**2 + ky**2) > 1e-8

        # Weight angles by power
        angles = np.arctan2(ky, kx)
        weighted_cos2 = np.sum(power[mask] * np.cos(2 * angles[mask]))
        weighted_sin2 = np.sum(power[mask] * np.sin(2 * angles[mask]))
        total_power = np.sum(power[mask])

        if total_power == 0:
            return 0.0

        # Mean angle (using circular statistics for orientations)
        mean_angle_2x = np.arctan2(weighted_sin2 / total_power, weighted_cos2 / total_power)
        mean_angle = mean_angle_2x / 2.0

        # Anisotropy: how concentrated are the orientations
        anisotropy = np.sqrt((weighted_cos2/total_power)**2 + (weighted_sin2/total_power)**2)

        # Alignment with field direction
        field_angle = self.astro.field_orientation_rad
        angle_diff = np.abs(np.cos(2 * (mean_angle - field_angle)))

        return float(anisotropy * angle_diff)

    def step(self, dt_minutes: float = 1.0):
        """Advance simulation by dt_minutes."""
        self._cool_step(dt_minutes)
        self._solidify_step()
        self.time_step += 1

        # Record metrics
        solid_fraction = np.mean(self.phi > 0.5)
        if solid_fraction > 0:
            avg_v_solid = float(np.mean(self.vanadium[self.phi > 0.5]))
        else:
            avg_v_solid = 0.0
        band_score = self._compute_band_alignment_score()

        self.history['temp'].append(float(np.mean(self.temp)))
        self.history['solid_fraction'].append(float(solid_fraction))
        self.history['avg_vanadium_in_solid'].append(avg_v_solid)
        self.history['band_alignment_score'].append(band_score)

    def run(self, total_minutes: float = 60.0, dt_minutes: float = 1.0):
        """Run simulation to completion or to forging temperature."""
        n_steps = int(total_minutes / dt_minutes)
        for _ in range(n_steps):
            if np.mean(self.temp) <= self.melt.final_temp_c:
                break
            if np.all(self.phi > 0.5):  # fully solidified
                # Continue cooling solid
                self._cool_step(dt_minutes)
                self.time_step += 1
            else:
                self.step(dt_minutes)

    def summary(self) -> dict:
        """Return summary metrics for this run."""
        return {
            'final_temp_c': float(np.mean(self.temp)),
            'solidified_fraction': float(np.mean(self.phi > 0.5)),
            'mean_vanadium_in_solid_ppm': float(np.mean(self.vanadium[self.phi > 0.5]) * 1e6) if np.any(self.phi > 0.5) else 0.0,
            'vanadium_std_in_solid_ppm': float(np.std(self.vanadium[self.phi > 0.5]) * 1e6) if np.any(self.phi > 0.5) else 0.0,
            'band_alignment_score': float(self.history['band_alignment_score'][-1]) if self.history['band_alignment_score'] else 0.0,
            'effective_field_ut': self.astro.effective_field_strength(),
            'total_steps': self.time_step,
        }
