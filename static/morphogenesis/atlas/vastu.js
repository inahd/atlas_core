// Vastu — directional bias as hidden field constraint.
// The 9-zone (3×3) vastu grid is NEVER drawn; it only nudges per-field
// values each tick so emergent forms pick up the directional logic of
// the canonical mandala without any visible diagram.
//
// Zones laid out so that screen-Y-down matches South-down (image
// convention).  Origin at top-left:
//
//     NW  N   NE
//     W   C   E
//     SW  S   SE
//
// Each zone has a small per-tick delta on a few specific fields.
// Strengths are tuned tiny — they nudge over hundreds of ticks rather
// than dominating any single frame.

// Zone IDs (0..8).
export const ZONE_NW = 0, ZONE_N = 1, ZONE_NE = 2;
export const ZONE_W  = 3, ZONE_C = 4, ZONE_E  = 5;
export const ZONE_SW = 6, ZONE_S = 7, ZONE_SE = 8;

export const ZONE_NAMES = ["NW","N","NE","W","C","E","SW","S","SE"];

// Per-zone affinities — which fields get nudged, by how much per tick
// (before strength multiplier).  Tiny deltas: ~0.001/tick max.
//
//   E  light/reveal       → coherence + life
//   S  heat               → heat
//   W  condensation       → moisture + branch_memory
//   N  growth/stability   → rigidity + density
//   NE water/ether        → moisture + coherence
//   SE fire               → heat + charge
//   SW density/rigidity   → rigidity + density
//   NW air/velocity       → outward swirl on velocity (special)
//   C  coherence          → coherence (strongest of all)
const ZONE_DELTAS = {
  [ZONE_C]:  { coherence: 0.0014, life: 0.0006 },
  [ZONE_N]:  { rigidity: 0.0006, density: 0.0004 },
  [ZONE_NE]: { moisture: 0.0006, coherence: 0.0008 },
  [ZONE_E]:  { coherence: 0.0010, life: 0.0008 },
  [ZONE_SE]: { heat: 0.0008, charge: 0.0006 },
  [ZONE_S]:  { heat: 0.0010 },
  [ZONE_SW]: { rigidity: 0.0010, density: 0.0008 },
  [ZONE_W]:  { moisture: 0.0008, branch_memory: 0.0004 },
  [ZONE_NW]: { /* velocity-only — handled separately */ },
};

// Soft 3-band split — instead of hard step boundaries we use smoothstep
// so the zone weighting transitions gradually.  This avoids visible
// 3×3 stepping in the resulting field.
function smoothBand(t) {
  // Three soft bands at [0, 1/3], [1/3, 2/3], [2/3, 1].
  // Returns [w0, w1, w2] with sum = 1.
  if (t < 0.25) return [1, 0, 0];
  if (t < 0.42) {
    const u = (t - 0.25) / 0.17;
    const s = u * u * (3 - 2 * u);
    return [1 - s, s, 0];
  }
  if (t < 0.58) return [0, 1, 0];
  if (t < 0.75) {
    const u = (t - 0.58) / 0.17;
    const s = u * u * (3 - 2 * u);
    return [0, 1 - s, s];
  }
  return [0, 0, 1];
}

// Build vastu context — per-cell zone-weight tables and pre-multiplied
// per-field delta tables.  Computed once on reset; reused every tick.
//
// Layout: deltas[fieldName] is a Float32Array of length N where
// deltas[fieldName][i] is the per-tick increment that vastu would add
// at cell i, before the user's vastu-strength multiplier.
export function buildVastuContext(W, H) {
  const N = W * H;
  const fieldNames = ["coherence", "life", "heat", "moisture", "charge",
                       "density", "rigidity", "branch_memory"];
  const deltas = {};
  for (const fn of fieldNames) deltas[fn] = new Float32Array(N);

  // Velocity bias for NW (air): outward swirl
  const vxBias = new Float32Array(N);
  const vyBias = new Float32Array(N);

  for (let y = 0; y < H; y++) {
    const v = y / H;
    const [wn, wm, ws] = smoothBand(v);
    for (let x = 0; x < W; x++) {
      const u = x / W;
      const [ww, wc, we] = smoothBand(u);
      // 3×3 zone weights
      const w = [
        wn * ww, wn * wm, wn * we,   // NW, N, NE
        ws !== undefined ? wm * ww : 0, wm * wm, wm * we, // W, C, E
        ws * ww, ws * wm, ws * we,   // SW, S, SE
      ];
      // Re-fix W row (i=3) to be properly assigned
      w[3] = wm * ww;

      const i = y * W + x;
      // For each field name, sum (zone_weight * zone_delta_for_this_field)
      for (const fn of fieldNames) {
        let total = 0;
        for (let z = 0; z < 9; z++) {
          if (w[z] === 0) continue;
          const zd = ZONE_DELTAS[z];
          if (zd[fn] !== undefined) total += w[z] * zd[fn];
        }
        deltas[fn][i] = total;
      }
      // NW velocity bias — outward swirl, only at NW zone
      if (w[ZONE_NW] > 0.01) {
        const cx = W / 2, cy = H / 2;
        const dx = x - cx, dy = y - cy;
        const r = Math.sqrt(dx*dx + dy*dy) + 1e-6;
        // Tangent (counter-clockwise): rotate radial 90°
        const tx = -dy / r, ty = dx / r;
        vxBias[i] = w[ZONE_NW] * tx * 0.0006;
        vyBias[i] = w[ZONE_NW] * ty * 0.0006;
      }
    }
  }
  return { deltas, vxBias, vyBias };
}

// Apply vastu to fields.  Strength 0..1 gates the effect.
export function applyVastu(stack, vastuCtx, strength) {
  if (!vastuCtx || strength <= 0) return;
  const N = stack.N;
  const fields = stack.fields;
  const d = vastuCtx.deltas;
  for (const fn of Object.keys(d)) {
    const arr = fields[fn];
    if (!arr) continue;
    const da = d[fn];
    for (let i = 0; i < N; i++) {
      arr[i] += da[i] * strength;
    }
  }
  // Velocity bias
  const vx = fields.vx, vy = fields.vy;
  const vxb = vastuCtx.vxBias, vyb = vastuCtx.vyBias;
  for (let i = 0; i < N; i++) {
    vx[i] += vxb[i] * strength;
    vy[i] += vyb[i] * strength;
  }
}
