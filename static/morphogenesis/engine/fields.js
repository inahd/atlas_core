// Field buffer registry. All fields are Float32Arrays of length W*H.
// Vector fields (velocity) are stored as separate vx/vy components.
// Scratch buffers are pre-allocated for double-buffered passes.

const SCALAR_FIELDS = [
  "density",
  "moisture",
  "heat",
  "pressure",
  "rigidity",
  "coherence",
  "branch_memory",
  "charge",
  "life",
];

export class FieldStack {
  constructor(W, H) {
    this.W = W;
    this.H = H;
    this.N = W * H;
    this.fields = {};
    this.scratch = {};
    for (const name of SCALAR_FIELDS) {
      this.fields[name] = new Float32Array(this.N);
      this.scratch[name] = new Float32Array(this.N);
    }
    // Velocity is 2D
    this.fields.vx = new Float32Array(this.N);
    this.fields.vy = new Float32Array(this.N);
    this.scratch.vx = new Float32Array(this.N);
    this.scratch.vy = new Float32Array(this.N);
  }
  get(name) { return this.fields[name]; }
  scratchOf(name) { return this.scratch[name]; }
  // Swap a field with its scratch (used after a double-buffered pass)
  swap(name) {
    const t = this.fields[name];
    this.fields[name] = this.scratch[name];
    this.scratch[name] = t;
  }
  clearAll() {
    for (const k of Object.keys(this.fields)) this.fields[k].fill(0);
  }
  // Initialize fields for reaction-diffusion + general flow.
  // Gray-Scott regime: substrate ≈ 1.0 everywhere with small noise;
  // catalyst ≈ 0 except for a few localized seed patches that break
  // symmetry. Without the localized seeds the system stays homogeneous.
  seedNoise(rng) {
    const W = this.W, H = this.H, N = this.N;
    const dens = this.fields.density;       // u (substrate)
    const coh = this.fields.coherence;      // v (catalyst)
    const moist = this.fields.moisture;
    const life = this.fields.life;

    for (let i = 0; i < N; i++) {
      dens[i] = 1.0 - 0.02 * rng();         // ≈ 1.0 with subtle noise
      coh[i] = 0.0 + 0.005 * rng();         // ≈ 0
      moist[i] = 0.45 + 0.06 * rng();
      life[i] = 0.02 + 0.02 * rng();
    }
    // Drop ~12 catalyst seed patches to break symmetry
    const nSeeds = 12;
    for (let s = 0; s < nSeeds; s++) {
      const cx = Math.floor(rng() * W);
      const cy = Math.floor(rng() * H);
      const r = 4 + Math.floor(rng() * 5);
      for (let dy = -r; dy <= r; dy++) {
        for (let dx = -r; dx <= r; dx++) {
          const d2 = dx * dx + dy * dy;
          if (d2 > r * r) continue;
          const x = ((cx + dx) % W + W) % W;
          const y = ((cy + dy) % H + H) % H;
          const i = y * W + x;
          const intensity = (1 - d2 / (r * r));
          coh[i] = Math.max(coh[i], 0.45 * intensity);
          dens[i] = Math.min(dens[i], 1.0 - 0.5 * intensity);
        }
      }
    }
  }
}

export const FIELD_NAMES = SCALAR_FIELDS;
