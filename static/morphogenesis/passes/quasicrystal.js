// Quasicrystal pass — when active, adds a coherence perturbation made of
// `fold` plane waves at non-crystallographic angles (e.g. 11-fold has no
// integer tiling). Phason amplitude controls aperiodic drift of the wave
// vectors, so the pattern slowly reorganizes without ever locking.
//
// Hidden grammar: aperiodic order. The viewer should see "structure that
// almost-repeats" — Penrose-like, not lattice-like. We never draw tiles
// or rhombs; we just bias coherence so reaction-diffusion finds those
// quasiperiodic minima.

const TWO_PI = Math.PI * 2;

export class QuasicrystalState {
  constructor(W, H) {
    this.W = W;
    this.H = H;
    this.fold = 11;
    this.phasons = null;     // per-wave random phase offset
    this.angles = null;      // fixed wave directions
    this.lastFold = 0;
  }
  rebuild(fold, rng) {
    this.fold = fold;
    this.phasons = new Float32Array(fold);
    this.angles = new Float32Array(fold);
    for (let k = 0; k < fold; k++) {
      this.angles[k] = (k / fold) * TWO_PI;
      this.phasons[k] = (rng ? rng() : Math.random()) * TWO_PI;
    }
    this.lastFold = fold;
  }
}

export function quasicrystalPass(stack, qcState, params, tick, rng) {
  if (!params || !params.active) return 0;
  const fold = params.fold | 0;
  if (fold < 5) return 0;
  const strength = params.strength ?? 0.0;
  // P3 (issue #8) — early exit when effective strength is visually negligible.
  // 11-cos-per-pixel sum is one of the most expensive per-frame loops,
  // and below ~0.05 you can't see the perturbation anyway.
  if (strength < 0.05) return 0;
  const phasonAmp = params.phason_amplitude ?? 0.3;

  if (!qcState.angles || qcState.lastFold !== fold) {
    qcState.rebuild(fold, rng);
  }

  // Drift phasons slowly — aperiodic reorganization
  for (let k = 0; k < fold; k++) {
    qcState.phasons[k] += phasonAmp * 0.0015 * Math.sin(tick * 0.011 + k);
  }

  const W = stack.W, H = stack.H;
  const coh = stack.get("coherence");
  const cx = W * 0.5, cy = H * 0.5;
  // Wavelength tuned so a few rings fit in the canvas
  const kappa = 18 / Math.min(W, H) * TWO_PI;

  for (let y = 0; y < H; y++) {
    const dy = y - cy;
    for (let x = 0; x < W; x++) {
      const dx = x - cx;
      let sum = 0;
      for (let m = 0; m < fold; m++) {
        const a = qcState.angles[m];
        const phase = (Math.cos(a) * dx + Math.sin(a) * dy) * kappa
                    + qcState.phasons[m];
        sum += Math.cos(phase);
      }
      // Normalize: sum is in [-fold, fold], remap to [-1, 1]
      const v = sum / fold;
      coh[y * W + x] += strength * 0.04 * v;
    }
  }
  return strength;
}
