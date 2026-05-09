// Phyllotaxy — golden-angle point distribution.
// Used as the deterministic spatial template for emitter (and optionally
// bloom_node) placement when the mode requests it.  Each successive point
// rotates by the golden angle (≈137.508°) and steps outward by √i, the
// arrangement found in sunflower seedheads, pinecones, etc.
//
// Element sliders distort the base spiral so the same phyllotaxy template
// expresses water-clustering, fire-expansion, earth-tightening, air-
// jitter, wood-branching, ether-radial-coherence differently.

const GOLDEN_ANGLE = Math.PI * (3 - Math.sqrt(5));   // ≈ 137.508°

// Generate N golden-angle points around (cx, cy) with element distortion.
// Returns array of { x, y, idx, kind, age } where age 0..1 is i/N.
//
// Distortions:
//   water: smooth-cluster — multiplies r by (1 - 0.3·water·decay_with_idx)
//          → more inner clustering when water is high
//   fire:  expand — multiplies r by (1 + 0.4·fire·age)
//   earth: tighten — multiplies r by (1 - 0.3·earth)
//   air:   angular jitter — adds (rng - 0.5)·0.15·air to each angle
//   wood:  branching offshoots — every ~10th point spawns a child
//   ether: inner ring overlay — adds extra dense cluster near center
export function phyllotaxyPoints(N, cx, cy, scale, elements = {}, rng = Math.random) {
  const points = [];
  const water = elements.water ?? 0.5;
  const air   = elements.air   ?? 0.5;
  const fire  = elements.fire  ?? 0.5;
  const earth = elements.earth ?? 0.5;
  const wood  = elements.wood  ?? 0.5;
  const ether = elements.ether ?? 0.5;

  for (let i = 0; i < N; i++) {
    const age = N > 1 ? i / (N - 1) : 0;
    let angle = i * GOLDEN_ANGLE + air * (rng() - 0.5) * 0.15;
    let r = scale * Math.sqrt(i);
    // Water: cluster inward, especially for early points
    r *= (1 - 0.30 * water * (1 - age));
    // Fire: expand outward, especially for late points
    r *= (1 + 0.40 * fire * age);
    // Earth: uniform tighten
    r *= (1 - 0.30 * earth);

    const x = cx + r * Math.cos(angle);
    const y = cy + r * Math.sin(angle);
    points.push({ x, y, idx: i, age, kind: "primary" });

    // Wood: branching — every ~10th point (when wood > 0.4) spawns a child
    if (wood > 0.4 && (i % 10) === 0 && i > 0) {
      const branchAngle = angle + (rng() - 0.5) * 0.6;
      const branchR = r * (0.7 + 0.2 * rng());
      points.push({
        x: cx + branchR * Math.cos(branchAngle),
        y: cy + branchR * Math.sin(branchAngle),
        idx: i, age, kind: "branch",
      });
    }
  }

  // Ether: inner ring overlay — extra cluster at small radius
  if (ether > 0.5) {
    const inner = Math.floor(ether * 8);
    for (let k = 0; k < inner; k++) {
      const ang = (k / inner) * Math.PI * 2;
      const rr = scale * 0.6;
      points.push({
        x: cx + rr * Math.cos(ang),
        y: cy + rr * Math.sin(ang),
        idx: 1000 + k, age: 0.0, kind: "inner",
      });
    }
  }

  return points;
}
