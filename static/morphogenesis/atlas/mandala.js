// Mandala — radial ring zones with optional cardinal gates.
// Like vastu and yantra, this is never drawn.  It is a per-cell scalar
// field that biases simulation behavior by polar coordinate:
//   ring 0 (inner) → boosts coherence (the bindu)
//   ring 1         → boosts life (sukshma sharira)
//   ring 2         → boosts moisture (rasa)
//   ring 3         → boosts density (sthula)
//   ring 4 (outer) → boosts rigidity (bhupura)
//
// Gates are angular gaps where the ring boundary thins, allowing
// flow to pass between rings — represent the cardinal-directional
// openings of classical mandala architecture.

function clamp01(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }

// Per-ring field affinities — which field gets boosted in which ring.
// Indexed by ring number 0..N-1.
const RING_FIELD_BY_INDEX = ["coherence", "life", "moisture", "density", "rigidity",
                              "branch_memory", "heat", "charge"];

// Build mandala context: a 3-channel Float32Array per cell:
//   [0] = ring index (0..nRings-1)
//   [1] = ring boundary intensity (peaks at boundaries between rings)
//   [2] = gate openness (1 = on a gate, 0 = solid wall)
//
// Plus per-cell delta tables indexed by the field that the active
// ring boosts.
export function buildMandalaContext(W, H, opts = {}) {
  const {
    nRings = 4,
    gateAngles = [],          // radians, e.g. [0, π/2, π, 3π/2] for 4 cardinal
    gateWidth = 0.25,         // radians
    invertWeight = false,     // for "root inversion" — inner becomes outer
  } = opts;

  const N = W * H;
  const ringIndex = new Uint8Array(N);
  const boundaryIntensity = new Float32Array(N);
  const gateOpen = new Float32Array(N);
  // Pre-multiplied per-field deltas (only the fields actually used)
  const deltas = {
    coherence: new Float32Array(N),
    life: new Float32Array(N),
    moisture: new Float32Array(N),
    density: new Float32Array(N),
    rigidity: new Float32Array(N),
  };

  const cx = W / 2, cy = H / 2;
  const maxR = Math.min(W, H) * 0.5;

  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      const dx = x - cx, dy = y - cy;
      const r = Math.sqrt(dx*dx + dy*dy);
      const t = clamp01(r / maxR);

      // Ring assignment (uniform spacing for v0.5)
      const rt = invertWeight ? (1 - t) : t;
      const idx = Math.min(nRings - 1, Math.floor(rt * nRings));
      ringIndex[y * W + x] = idx;

      // Boundary intensity: triangle wave that peaks at ring boundaries
      const ringSpan = 1 / nRings;
      const within = (rt % ringSpan) / ringSpan; // 0..1
      const distToEdge = Math.min(within, 1 - within);
      boundaryIntensity[y * W + x] = clamp01(1 - distToEdge * 4);

      // Gate openness: 1 inside any gate angular span, 0 elsewhere.
      // Gate is a smoothed open region.
      let openness = 0;
      if (gateAngles.length > 0) {
        const theta = Math.atan2(dy, dx);
        for (const ga of gateAngles) {
          let d = ((theta - ga + Math.PI * 3) % (Math.PI * 2)) - Math.PI;
          d = Math.abs(d);
          if (d < gateWidth) {
            const v = 1 - d / gateWidth;
            if (v > openness) openness = v;
          }
        }
      }
      gateOpen[y * W + x] = openness;

      // Per-ring field bias (only the ring's affinity field gets a delta)
      const fname = RING_FIELD_BY_INDEX[idx % RING_FIELD_BY_INDEX.length];
      if (deltas[fname]) {
        // Stronger near the ring center, weaker at boundaries
        const ringAffinity = 1 - boundaryIntensity[y * W + x];
        // Gate cells get a small reduction (lets things flow through)
        const gateMul = 1 - 0.5 * openness;
        deltas[fname][y * W + x] = ringAffinity * gateMul * 0.0008;
      }
    }
  }

  return {
    nRings,
    gateAngles,
    invertWeight,
    ringIndex,
    boundaryIntensity,
    gateOpen,
    deltas,
  };
}

// Apply mandala biases to fields.
export function applyMandala(stack, mandalaCtx, strength) {
  if (!mandalaCtx || strength <= 0) return;
  const N = stack.N;
  const fields = stack.fields;
  const d = mandalaCtx.deltas;
  for (const fn of Object.keys(d)) {
    const arr = fields[fn];
    if (!arr) continue;
    const da = d[fn];
    for (let i = 0; i < N; i++) {
      arr[i] += da[i] * strength;
    }
  }
}
