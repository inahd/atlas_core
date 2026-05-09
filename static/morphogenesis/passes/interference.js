// Interference rings — adds a sum of cos(k·r_i) standing waves,
// where r_i is the distance from cell to seed-source i. This is
// the same two-source kernel the Atlas wave-field engine uses,
// generalised to N sources. Drift the sources slowly via the
// velocity field for animated bloom.

export class InterferenceField {
  constructor(W, H, n_sources = 5) {
    this.W = W;
    this.H = H;
    this.n = n_sources;
    this.sources = []; // {x, y}
  }
  initSources(rng) {
    this.sources = [];
    for (let i = 0; i < this.n; i++) {
      this.sources.push({
        x: rng() * this.W,
        y: rng() * this.H,
      });
    }
  }
  // Drift sources along the velocity field (sampled at int cell)
  drift(stack, dt = 0.4) {
    const vx = stack.get("vx"), vy = stack.get("vy");
    const W = this.W, H = this.H;
    for (const s of this.sources) {
      const ix = ((Math.floor(s.x) % W) + W) % W;
      const iy = ((Math.floor(s.y) % H) + H) % H;
      s.x = (s.x + dt * vx[iy * W + ix] + W) % W;
      s.y = (s.y + dt * vy[iy * W + ix] + H) % H;
    }
  }
  apply(stack, params) {
    const {
      target = "charge",
      k = 0.18,           // angular frequency in cell units
      strength = 0.05,
      decay = 0.985,
    } = params;
    const W = this.W, H = this.H;
    const arr = stack.get(target);
    const sources = this.sources;
    const n = sources.length;
    if (n === 0) return;
    for (let y = 0; y < H; y++) {
      for (let x = 0; x < W; x++) {
        let acc = 0;
        for (let s = 0; s < n; s++) {
          const dx = x - sources[s].x;
          const dy = y - sources[s].y;
          // Toroidal min distance
          const adx = Math.min(Math.abs(dx), W - Math.abs(dx));
          const ady = Math.min(Math.abs(dy), H - Math.abs(dy));
          const r = Math.sqrt(adx * adx + ady * ady);
          acc += Math.cos(k * r);
        }
        const i = y * W + x;
        arr[i] = arr[i] * decay + strength * (acc / n);
      }
    }
  }
}
