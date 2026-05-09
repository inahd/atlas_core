// SceneGrammar — deterministic event-graph derived from seed.
// v0.4 additions: mode label, focalCount, voidCount, dominantAxis, scaleBias.
// Two new event kinds: coherence_pulse (oscillating charge ring),
// pressure_ridge (line accumulator into pressure + rigidity).
//
// The grammar is the structural difference between scenes — not pixel
// noise but composed events with symmetry, focus, void, and scale.

import { mulberry32 } from "../engine/prng.js";
import { phyllotaxyPoints } from "./phyllotaxy.js";

export const SYMMETRY_MODES = ["none", "bilateral", "radial", "spiral"];

// v0.4: six-state phase machine.  Phase activation never goes to zero —
// the floor is set so even decay/collapse/memory keep events nudging.
export const PHASES = [
  "dormant", "ignition", "bloom", "decay", "collapse", "memory", "renewal",
];

// Phase activation scale (multiplier on per-event strength)
export function phaseScale(phase, tick) {
  if (phase === "dormant")   return 0.20;
  if (phase === "ignition")  return 0.55 + 0.45 * Math.min(1, tick / 400);
  if (phase === "bloom")     return 1.00;
  if (phase === "decay")     return 0.55;   // always-on baseline floor
  if (phase === "collapse")  return 0.30;
  if (phase === "memory")    return 0.18;   // simulation barely active; history carries
  if (phase === "renewal")   return 0.85;   // burst of fresh activity
  return 1.0;
}

// Auto phase from tick — full cycle then loops at 3000.
export function autoPhase(tick) {
  const t = tick % 3000;
  if (t < 200)  return "dormant";
  if (t < 600)  return "ignition";
  if (t < 1500) return "bloom";
  if (t < 2200) return "decay";
  if (t < 2500) return "collapse";
  if (t < 2800) return "memory";
  return "renewal";
}

export function generateGrammar(seed, complexity, structure, W, H, opts = {}) {
  const rng = mulberry32(seed);
  const cx = W / 2, cy = H / 2;

  // Symmetry mode — either suggested by mode, or rolled from seed
  let symmetry;
  if (opts.symmetryHint && SYMMETRY_MODES.includes(opts.symmetryHint)) {
    symmetry = opts.symmetryHint;
    // Burn one rng() to keep determinism stable
    rng();
  } else {
    const symRoll = rng();
    symmetry =
      symRoll < 0.30 ? "none" :
      symRoll < 0.60 ? "bilateral" :
      symRoll < 0.85 ? "radial" : "spiral";
  }
  const radialFold = 3 + Math.floor(rng() * 5);
  const spiralTurns = 3 + Math.floor(rng() * 4);

  // Dominant axis — the orientation events bias toward
  const axisRoll = rng();
  const dominantAxis =
    axisRoll < 0.25 ? "horizontal" :
    axisRoll < 0.50 ? "vertical" :
    axisRoll < 0.75 ? "diagonal" : "none";

  // Scale bias — 0..1, controls the radius range of generated events
  const scaleBias = 0.3 + rng() * 0.5;

  // Counts
  const c = complexity;
  const counts = {
    attractor:       1 + Math.floor(c * 3),
    emitter:         2 + Math.floor(c * 4),
    sink:            Math.floor(c * 2),
    shear_band:      Math.floor(c * 2),
    rupture:         Math.floor(c * 2),
    bloom_node:      2 + Math.floor(c * 4),
    strike:          1 + Math.floor(c * 4),
    void_pocket:     Math.floor(c * 2),
    coherence_pulse: 1 + Math.floor(c * 3),  // NEW v0.4
    pressure_ridge:  Math.floor(c * 2),       // NEW v0.4
  };

  // Place — high structure → grid; low → free.
  const place = () => {
    if (structure > 0.5) {
      const gridN = 3 + Math.floor((1 - structure) * 5);
      const gx = Math.floor(rng() * gridN);
      const gy = Math.floor(rng() * gridN);
      const jitter = (1 - structure) * 12;
      return [
        (gx + 0.5) * W / gridN + (rng() - 0.5) * jitter,
        (gy + 0.5) * H / gridN + (rng() - 0.5) * jitter,
      ];
    }
    return [rng() * W, rng() * H];
  };

  // Place a line endpoint pair, biased by dominantAxis
  const placeLine = () => {
    const [x1, y1] = place();
    let ang;
    if (dominantAxis === "horizontal") ang = (rng() - 0.5) * 0.6;
    else if (dominantAxis === "vertical") ang = Math.PI / 2 + (rng() - 0.5) * 0.6;
    else if (dominantAxis === "diagonal") ang = Math.PI / 4 + (rng() - 0.5) * 0.6;
    else ang = rng() * Math.PI * 2;
    const len = (0.15 + rng() * 0.35) * Math.min(W, H);
    return [x1, y1, x1 + Math.cos(ang) * len, y1 + Math.sin(ang) * len];
  };

  // Scale events by scaleBias (small bias → tight, large → broad)
  const scaleR = (r) => r * (0.5 + scaleBias);

  const baseEvents = [];

  for (let i = 0; i < counts.attractor; i++) {
    const [x, y] = place();
    baseEvents.push({
      kind: "attractor", x, y,
      strength: 0.4 + rng() * 0.6,
      radius: scaleR(18 + rng() * 36),
    });
  }
  const emitterFields = ["density", "heat", "charge", "life", "moisture"];
  for (let i = 0; i < counts.emitter; i++) {
    const [x, y] = place();
    baseEvents.push({
      kind: "emitter", x, y,
      field: emitterFields[Math.floor(rng() * emitterFields.length)],
      rate: 0.04 + rng() * 0.10,
      radius: scaleR(6 + rng() * 12),
    });
  }
  const sinkFields = ["density", "moisture", "charge"];
  for (let i = 0; i < counts.sink; i++) {
    const [x, y] = place();
    baseEvents.push({
      kind: "sink", x, y,
      field: sinkFields[Math.floor(rng() * sinkFields.length)],
      rate: 0.03 + rng() * 0.05,
      radius: scaleR(8 + rng() * 14),
      // v0.4: attenuate-to-floor, never to absolute 0
      floor: 0.05,
    });
  }
  for (let i = 0; i < counts.shear_band; i++) {
    const [x1, y1, x2, y2] = placeLine();
    baseEvents.push({
      kind: "shear_band", x1, y1, x2, y2,
      strength: 0.4 + rng() * 0.8,
      width: 4 + rng() * 6,
    });
  }
  for (let i = 0; i < counts.rupture; i++) {
    const [x1, y1, x2, y2] = placeLine();
    baseEvents.push({
      kind: "rupture", x1, y1, x2, y2,
      depth: 0.20 + rng() * 0.30,    // softer than v0.3 (was 0.3..0.8)
      width: 2 + rng() * 3,
      floor: 0.10,                    // never drives density to 0
    });
  }
  // Bloom nodes — placement either default (place()) or from phyllotaxy
  // when opts.phyllotaxy is enabled.  Phyllotaxy gives the golden-angle
  // spiral as the deterministic spatial template for emergent bloom.
  if (opts.phyllotaxy && opts.phyllotaxy.enabled) {
    const ph = opts.phyllotaxy;
    const N = Math.min(60, Math.max(8, ph.count ?? 36));
    const scaleParam = ph.scale ?? 4;
    const points = phyllotaxyPoints(N, W / 2, H / 2, scaleParam,
                                     opts.elements || {}, rng);
    // Use phyllotaxy points as bloom_node positions (skip default count)
    for (const p of points) {
      // Skip points outside canvas
      if (p.x < 0 || p.x >= W || p.y < 0 || p.y >= H) continue;
      baseEvents.push({
        kind: "bloom_node",
        x: p.x, y: p.y,
        frequency: 0.04 + rng() * 0.06,
        radius: scaleR(8 + (1 - p.age) * 16),  // outer petals smaller
        amplitude: 0.04 + rng() * 0.08 * (p.kind === "primary" ? 1.0 : 0.6),
      });
    }
  } else {
    for (let i = 0; i < counts.bloom_node; i++) {
      const [x, y] = place();
      baseEvents.push({
        kind: "bloom_node", x, y,
        frequency: 0.04 + rng() * 0.06,
        radius: scaleR(12 + rng() * 24),
        amplitude: 0.05 + rng() * 0.10,
      });
    }
  }
  for (let i = 0; i < counts.strike; i++) {
    const [x, y] = place();
    baseEvents.push({
      kind: "strike", x, y,
      magnitude: 0.5 + rng() * 0.8,
      time: 100 + Math.floor(rng() * 1400),
      lifetime: 30 + Math.floor(rng() * 60),
      radius: 4 + rng() * 6,
      recurrence: rng() < 0.5 ? 200 + Math.floor(rng() * 600) : 0,
    });
  }
  for (let i = 0; i < counts.void_pocket; i++) {
    const [x, y] = place();
    baseEvents.push({
      kind: "void_pocket", x, y,
      radius: scaleR(14 + rng() * 22),
      depth: 0.15 + rng() * 0.20,    // softer than v0.3 (was 0.3..0.8)
      floor: 0.08,                   // never below this
    });
  }
  // NEW v0.4: coherence_pulse — oscillating charge ring (positive/negative
  // alternating).  Provides ringing structure without continuously draining.
  for (let i = 0; i < counts.coherence_pulse; i++) {
    const [x, y] = place();
    baseEvents.push({
      kind: "coherence_pulse", x, y,
      frequency: 0.05 + rng() * 0.08,
      radius: scaleR(14 + rng() * 22),
      amplitude: 0.04 + rng() * 0.06,
    });
  }
  // NEW v0.4: pressure_ridge — line accumulator into pressure and rigidity.
  // Carves bone-like / strata-like structure.
  for (let i = 0; i < counts.pressure_ridge; i++) {
    const [x1, y1, x2, y2] = placeLine();
    baseEvents.push({
      kind: "pressure_ridge", x1, y1, x2, y2,
      strength: 0.05 + rng() * 0.08,
      width: 3 + rng() * 4,
    });
  }

  // ── Symmetry application ────────────────────────────────────────
  const events = [];
  const reflect = (ev) => ({ ...ev, x: W - ev.x });
  const reflectLine = (ev) => ({ ...ev, x1: W - ev.x1, x2: W - ev.x2 });
  const rotate = (ev, ang) => {
    const cosA = Math.cos(ang), sinA = Math.sin(ang);
    if (ev.x !== undefined) {
      const dx = ev.x - cx, dy = ev.y - cy;
      return {
        ...ev,
        x: cx + dx * cosA - dy * sinA,
        y: cy + dx * sinA + dy * cosA,
      };
    } else {
      const r = (px, py) => {
        const dx = px - cx, dy = py - cy;
        return [cx + dx * cosA - dy * sinA, cy + dx * sinA + dy * cosA];
      };
      const [nx1, ny1] = r(ev.x1, ev.y1);
      const [nx2, ny2] = r(ev.x2, ev.y2);
      return { ...ev, x1: nx1, y1: ny1, x2: nx2, y2: ny2 };
    }
  };
  const isLine = (ev) =>
    ev.kind === "shear_band" || ev.kind === "rupture" || ev.kind === "pressure_ridge";

  const applySym = (ev) => {
    events.push(ev);
    if (symmetry === "bilateral") {
      events.push(isLine(ev) ? reflectLine(ev) : reflect(ev));
    } else if (symmetry === "radial") {
      for (let k = 1; k < radialFold; k++) {
        events.push(rotate(ev, (k / radialFold) * Math.PI * 2));
      }
    } else if (symmetry === "spiral") {
      for (let k = 1; k < spiralTurns; k++) {
        const ang = (k / spiralTurns) * Math.PI * 2;
        const scale = Math.pow(0.78, k);
        const r = rotate(ev, ang);
        if (r.x !== undefined) {
          r.x = cx + (r.x - cx) * scale;
          r.y = cy + (r.y - cy) * scale;
        } else {
          r.x1 = cx + (r.x1 - cx) * scale;
          r.y1 = cy + (r.y1 - cy) * scale;
          r.x2 = cx + (r.x2 - cx) * scale;
          r.y2 = cy + (r.y2 - cy) * scale;
        }
        events.push(r);
      }
    }
  };
  for (const ev of baseEvents) applySym(ev);

  // Summary metrics — used by HUD and by collapse-monitor heuristics
  const focalCount = events.filter(e =>
    e.kind === "attractor" || e.kind === "bloom_node" ||
    e.kind === "emitter" || e.kind === "coherence_pulse").length;
  const voidCount = events.filter(e =>
    e.kind === "void_pocket" || e.kind === "sink" || e.kind === "rupture").length;

  return {
    seed,
    mode: opts.mode || null,
    symmetry,
    radialFold,
    spiralTurns,
    complexity,
    structure,
    dominantAxis,
    scaleBias,
    focalCount,
    voidCount,
    phyllotaxy: opts.phyllotaxy?.enabled ? {
      count: opts.phyllotaxy.count,
      scale: opts.phyllotaxy.scale,
    } : null,
    events,
  };
}
