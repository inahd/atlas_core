// Helical-shear pass — twist velocity around the body region's vertical
// axis when the loading asana implies helical strain.
//
// We never draw the asana. We add a tangential velocity component whose
// magnitude depends on:
//   - asana category (twists/inversions = strong, restoratives = none)
//   - radial distance from the axis (zero on axis, peak mid-radius)
//   - vertical band centered on the body region's y position
//
// Result: density and coherence rotate around the spine line, creating
// helical bands that cannot arise from diffusion alone.

const ASANA_TWIST = {
  // strong helical strain
  Matsyendrasana: 0.9,
  ArdhaMatsyendrasana: 0.85,
  Garudasana: 0.7,
  ParivrttaTrikonasana: 0.75,
  // moderate
  Trikonasana: 0.35,
  Virabhadrasana: 0.3,
  Tadasana: 0.05,
  // inversions add mild twist
  Sarvangasana: 0.45,
  Sirsasana: 0.5,
  Halasana: 0.4,
  // arches don't twist much
  Bhujangasana: 0.1,
  Urdhvadhanurasana: 0.15,
  Ustrasana: 0.1,
  // folds don't twist
  Paschimottanasana: 0.05,
  Uttanasana: 0.05,
  Janusirsasana: 0.1,
  // seated / restorative
  Padmasana: 0.1,
  Sukhasana: 0.05,
  Savasana: 0.0,
};

const REGION_AXIS_Y = {
  skull_vault: 0.08, eye_socket: 0.18, eye_lens: 0.18, iris: 0.18,
  cochlea: 0.20, nasal_cavity: 0.22, jaw_masseter: 0.26,
  cervical_spine: 0.32, thoracic_spine: 0.45, lumbar_spine: 0.62,
  sternum: 0.42, ribs: 0.45, clavicle: 0.34, scapula: 0.40,
  humerus: 0.48, radius_ulna: 0.58, carpals: 0.66, phalanges: 0.72,
  pelvis: 0.68, femur: 0.78, tibia_fibula: 0.88, tarsals: 0.94,
  lung_bronchial: 0.40, heart_muscle: 0.42, fascia_network: 0.50,
  skin_surface: 0.50,
};

export function helicalShearPass(stack, embodiment, strength = 1.0) {
  if (!embodiment) return 0;
  const asana = embodiment.asana_that_loads;
  const twistMag = (ASANA_TWIST[asana] ?? 0.15) * strength;
  if (twistMag <= 0) return 0;

  const W = stack.W, H = stack.H;
  const vx = stack.get("vx");
  const vy = stack.get("vy");
  const cx = W * 0.5;
  const cyN = REGION_AXIS_Y[embodiment.body_region] ?? 0.5;
  const cy = cyN * H;

  // Vertical band of influence — width 0.35*H around cy
  const bandSigma = 0.18 * H;
  // Radial peak at mid-radius
  const rMax = Math.min(W, H) * 0.45;

  for (let y = 0; y < H; y++) {
    const dyAxis = y - cy;
    const bandW = Math.exp(-(dyAxis * dyAxis) / (2 * bandSigma * bandSigma));
    if (bandW < 0.02) continue;
    for (let x = 0; x < W; x++) {
      const dx = x - cx;
      const dy = dyAxis;
      const r = Math.sqrt(dx * dx + dy * dy);
      if (r < 1e-3 || r > rMax) continue;
      // Tangential unit vector: (-dy, dx) / r
      const tx = -dy / r;
      const ty = dx / r;
      // Magnitude: peaks mid-radius, zero on axis and at rMax
      const rN = r / rMax;
      const radialW = 4 * rN * (1 - rN);    // bell in [0, rMax], peak 1 at 0.5
      const m = twistMag * 0.04 * bandW * radialW;
      const i = y * W + x;
      vx[i] += m * tx;
      vy[i] += m * ty;
    }
  }
  return twistMag;
}

export { ASANA_TWIST };
