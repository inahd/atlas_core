// Cellular partitioning — soft Voronoi field.
// Each cell records the squared distance to the nearest seed,
// normalized to [0, 1]. This produces emergent cell-walls that
// bias local field rates without drawing explicit polygons.
//
// Implementation: brute-force nearest-seed scan (cheap at moderate
// resolution and few seeds, ~10ms at 192² × 12 seeds).

export class VoronoiField {
  constructor(W, H, n_cells = 12) {
    this.W = W;
    this.H = H;
    this.n = n_cells;
    this.seeds = [];
  }
  initSeeds(rng) {
    this.seeds = [];
    for (let i = 0; i < this.n; i++) {
      this.seeds.push({ x: rng() * this.W, y: rng() * this.H });
    }
  }
  // Drift seeds slowly (velocity-field driven) to keep the partition alive
  drift(stack, dt = 0.15) {
    const vx = stack.get("vx"), vy = stack.get("vy");
    const W = this.W, H = this.H;
    for (const s of this.seeds) {
      const ix = ((Math.floor(s.x) % W) + W) % W;
      const iy = ((Math.floor(s.y) % H) + H) % H;
      s.x = (s.x + dt * vx[iy * W + ix] + W) % W;
      s.y = (s.y + dt * vy[iy * W + ix] + H) % H;
    }
  }
  // Write a partition-distance field into stack.rigidity:
  //   rigidity = 1 - normalized_min_distance
  // Cells near seed centers are "rigid" (high), cells on cell walls are
  // soft/low. This gives the partition a presence in the simulation
  // without requiring any drawing.
  apply(stack, params) {
    const { strength = 1.0, decay = 0.6 } = params;
    const W = this.W, H = this.H;
    const rig = stack.get("rigidity");
    const seeds = this.seeds;
    if (seeds.length === 0) return;
    // Find a per-frame max for normalization
    let maxR2 = 1;
    for (let y = 0; y < H; y++) {
      for (let x = 0; x < W; x++) {
        let best = 1e9;
        for (let s = 0; s < seeds.length; s++) {
          const dx = x - seeds[s].x;
          const dy = y - seeds[s].y;
          const adx = Math.min(Math.abs(dx), W - Math.abs(dx));
          const ady = Math.min(Math.abs(dy), H - Math.abs(dy));
          const r2 = adx * adx + ady * ady;
          if (r2 < best) best = r2;
        }
        const i = y * W + x;
        if (best > maxR2) maxR2 = best;
        rig[i] = rig[i] * decay + strength * Math.exp(-best / 80);
      }
    }
  }
}
