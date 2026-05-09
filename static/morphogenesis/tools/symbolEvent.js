// SymbolEvent — a parametric, time-shaped gesture that acts on the field
// stack each tick.  Unlike raw splats, SymbolEvents have:
//   - attack  ramp (0 → 1)
//   - peak    hold (1)
//   - decay   ramp (1 → 0)
//   - memory  faint trace (~0.2 fading)
//
// Each gesture (mouse drag spot, breath pulse, command phrase) emits a
// SymbolEvent into sim.symbolEvents; the sim steps them every tick.
//
// "Hidden" verbs: each event carries a verb (bloom, void, flow, ...)
// and a list of suppressed pass names.  When any event is in attack or
// peak phase, those passes are muted for the tick — the gesture
// dominates the field while it lasts.

export const TOOLS = [
  { id: "bloom",     name: "Bloom Brush",     verb: "bloom",     suppress: ["voronoi"] },
  { id: "branch",    name: "Branch Brush",    verb: "branch",    suppress: [] },
  { id: "discharge", name: "Discharge Brush", verb: "discharge", suppress: ["diffusion"] },
  { id: "water",     name: "Water Brush",     verb: "water",     suppress: ["reaction"] },
  { id: "crystal",   name: "Crystal Ridge",   verb: "crystal",   suppress: ["curl"] },
  { id: "void",      name: "Void Carver",     verb: "void",      suppress: ["reaction", "voronoi"] },
  { id: "flow",      name: "Flow Stroke",     verb: "flow",      suppress: [] },
  { id: "marma",     name: "Marma Pulse",     verb: "pulse",     suppress: [] },
  { id: "yantra",    name: "Yantra Stamp",    verb: "yantra",    suppress: ["voronoi"] },
  { id: "reveal",    name: "Reveal Lens",     verb: "reveal",    suppress: [] },
];
export const TOOL_BY_ID = Object.fromEntries(TOOLS.map(t => [t.id, t]));

export const DEFAULT_ENVELOPE = {
  attackTicks: 4,
  peakTicks:   12,
  decayTicks:  20,
  memoryTicks: 40,
};

const TOOL_OVERRIDES = {
  marma:    { attackTicks: 2, peakTicks: 24, decayTicks: 14, memoryTicks: 30 },
  yantra:   { attackTicks: 3, peakTicks: 18, decayTicks: 26, memoryTicks: 90 },
  reveal:   { attackTicks: 6, peakTicks: 24, decayTicks: 30, memoryTicks: 60 },
  breath:   { attackTicks: 3, peakTicks:  8, decayTicks: 18, memoryTicks: 30 },
  vortex:   { attackTicks: 2, peakTicks:  6, decayTicks: 12, memoryTicks: 20 },
  helical:  { attackTicks: 2, peakTicks:  8, decayTicks: 14, memoryTicks: 22 },
  symbol_node: { attackTicks: 4, peakTicks: 30, decayTicks: 40, memoryTicks: 180 },
  // v0.9 — visual response signatures (every action becomes felt)
  flash:        { attackTicks: 1, peakTicks: 4,  decayTicks: 6,  memoryTicks: 8 },
  shockwave:    { attackTicks: 1, peakTicks: 3,  decayTicks: 36, memoryTicks: 24 },
  summon:       { attackTicks: 6, peakTicks: 24, decayTicks: 36, memoryTicks: 60 },
  tap:          { attackTicks: 2, peakTicks: 4,  decayTicks: 12, memoryTicks: 16 },
  release:      { attackTicks: 1, peakTicks: 2,  decayTicks: 14, memoryTicks: 12 },
  palette_swap: { attackTicks: 4, peakTicks: 14, decayTicks: 24, memoryTicks: 32 },
  still_pulse:  { attackTicks: 3, peakTicks: 8,  decayTicks: 30, memoryTicks: 30 },
  ripple:       { attackTicks: 2, peakTicks: 4,  decayTicks: 18, memoryTicks: 16 },
  idle_drift:   { attackTicks: 4, peakTicks: 10, decayTicks: 20, memoryTicks: 24 },
  brush_ring:   { attackTicks: 1, peakTicks: 2,  decayTicks: 14, memoryTicks: 10 },
  spark:        { attackTicks: 1, peakTicks: 3,  decayTicks: 8,  memoryTicks: 8 },
  ribbon:       { attackTicks: 2, peakTicks: 6,  decayTicks: 18, memoryTicks: 24 },
};

let nextEventId = 1;

export function makeSymbolEvent({
  kind, x, y, radius, intensity = 1.0,
  birthTick, dx = 0, dy = 0, verb = null, suppress = null, extra = null,
}) {
  const env = TOOL_OVERRIDES[kind] || DEFAULT_ENVELOPE;
  const tool = TOOL_BY_ID[kind];
  return {
    id: nextEventId++,
    kind,
    x, y, radius, intensity,
    dx, dy,
    birthTick,
    attackTicks: env.attackTicks,
    peakTicks:   env.peakTicks,
    decayTicks:  env.decayTicks,
    memoryTicks: env.memoryTicks,
    verb:     verb     ?? tool?.verb     ?? kind,
    suppress: suppress ?? tool?.suppress ?? [],
    extra,
    phaseName: "attack",
  };
}

// Phi-curved smoothstep — same shape as Hermite smoothstep but biased
// by golden ratio so attack feels organic (slow start, faster mid, ease out).
//   t in [0, 1] → curved [0, 1]
const PHI = 1.6180339887498949;
const PHI_INV = 0.6180339887498949;
function phiSmooth(t) {
  if (t <= 0) return 0;
  if (t >= 1) return 1;
  // weighted blend: smoothstep + sqrt-shape, with phi/phi-inv weights
  const s = t * t * (3 - 2 * t);
  const r = Math.sqrt(t);
  return s * PHI_INV + r * (1 - PHI_INV);
}
// Decay curve — slightly weighted toward longer tail (life ≠ death symmetry)
function phiFall(t) {
  if (t <= 0) return 1;
  if (t >= 1) return 0;
  const s = (1 - t) * (1 - t) * (1 + 2 * t);   // mirrored smoothstep
  const r = Math.pow(1 - t, PHI);              // phi-power tail
  return s * 0.6 + r * 0.4;
}

// Compute the time-shaped intensity scalar for an event at age (ticks).
// Returns { phaseName, intensity } or null if expired.
export function eventEnvelope(ev, age) {
  const a = ev.attackTicks, p = ev.peakTicks, d = ev.decayTicks, m = ev.memoryTicks;
  if (age < 0) return null;
  if (age < a) {
    const t = age / Math.max(1, a);
    return { phaseName: "attack", intensity: ev.intensity * phiSmooth(t) };
  }
  if (age < a + p) return { phaseName: "peak", intensity: ev.intensity };
  if (age < a + p + d) {
    const t = (age - a - p) / Math.max(1, d);
    return { phaseName: "decay", intensity: ev.intensity * phiFall(t) };
  }
  if (age < a + p + d + m) {
    const t = (age - a - p - d) / Math.max(1, m);
    // memory tail — slow phi-decay from 20% baseline
    return { phaseName: "memory", intensity: ev.intensity * 0.20 * phiFall(t) };
  }
  return null;
}

// ── Field paint helpers ──────────────────────────────────────────────

function splat(field, W, H, x, y, radius, amount) {
  if (!field || radius <= 0) return;
  const r2 = radius * radius;
  const x0 = Math.max(0, Math.floor(x - radius));
  const x1 = Math.min(W - 1, Math.ceil(x + radius));
  const y0 = Math.max(0, Math.floor(y - radius));
  const y1 = Math.min(H - 1, Math.ceil(y + radius));
  for (let py = y0; py <= y1; py++) {
    for (let px = x0; px <= x1; px++) {
      const dx = px - x, dy = py - y;
      const d2 = dx * dx + dy * dy;
      if (d2 > r2) continue;
      const w = Math.exp(-d2 * 4 / r2);
      field[py * W + px] += amount * w;
    }
  }
}

function attenuateToFloor(field, W, H, x, y, radius, depth, floor) {
  if (!field) return;
  const r2 = radius * radius;
  const x0 = Math.max(0, Math.floor(x - radius));
  const x1 = Math.min(W - 1, Math.ceil(x + radius));
  const y0 = Math.max(0, Math.floor(y - radius));
  const y1 = Math.min(H - 1, Math.ceil(y + radius));
  for (let py = y0; py <= y1; py++) {
    for (let px = x0; px <= x1; px++) {
      const ddx = px - x, ddy = py - y;
      const d2 = ddx * ddx + ddy * ddy;
      if (d2 > r2) continue;
      const w = Math.exp(-d2 * 3 / r2);
      const i = py * W + px;
      const v = field[i];
      if (v > floor) field[i] = v + (floor - v) * w * depth;
    }
  }
}

function splatRing(field, W, H, x, y, ringR, innerR, amount) {
  if (!field) return;
  const sigma = (ringR - innerR) * 0.6 + 0.5;
  const x0 = Math.max(0, Math.floor(x - ringR - 1));
  const x1 = Math.min(W - 1, Math.ceil(x + ringR + 1));
  const y0 = Math.max(0, Math.floor(y - ringR - 1));
  const y1 = Math.min(H - 1, Math.ceil(y + ringR + 1));
  for (let py = y0; py <= y1; py++) {
    for (let px = x0; px <= x1; px++) {
      const dx = px - x, dy = py - y;
      const d = Math.sqrt(dx * dx + dy * dy);
      const dRing = d - (innerR + ringR) * 0.5;
      const w = Math.exp(-(dRing * dRing) / (2 * sigma * sigma));
      if (w < 0.04) continue;
      field[py * W + px] += amount * w;
    }
  }
}

// ── Per-kind apply ───────────────────────────────────────────────────

export function applySymbolEvent(stack, ev, age, intensity) {
  const W = stack.W, H = stack.H;
  const r = ev.radius;

  switch (ev.kind) {
    case "bloom": {
      splat(stack.get("coherence"), W, H, ev.x, ev.y, r * 1.0, intensity * 0.18);
      splat(stack.get("density"),   W, H, ev.x, ev.y, r * 1.2, intensity * 0.14);
      splat(stack.get("life"),      W, H, ev.x, ev.y, r * 0.9, intensity * 0.06);
      break;
    }
    case "branch": {
      splat(stack.get("branch_memory"), W, H, ev.x, ev.y, r * 0.8, intensity * 0.30);
      splat(stack.get("density"),       W, H, ev.x, ev.y, r * 0.7, intensity * 0.10);
      // Gradient seed: nudge density slightly higher on one side to invite
      // a propagating front (which branchMemory will then trace).
      splat(stack.get("density"), W, H, ev.x + r * 0.5, ev.y, r * 0.5, intensity * 0.05);
      break;
    }
    case "discharge": {
      const sign = (Math.sin(age * 0.45) > 0) ? 1 : -1;
      splat(stack.get("charge"), W, H, ev.x, ev.y, r * 0.7, intensity * 0.40 * sign);
      // Tiny life depletion under strong discharge
      splat(stack.get("life"),   W, H, ev.x, ev.y, r * 0.5, -intensity * 0.04);
      break;
    }
    case "water": {
      splat(stack.get("moisture"),  W, H, ev.x, ev.y, r * 1.5, intensity * 0.18);
      splat(stack.get("coherence"), W, H, ev.x, ev.y, r * 1.1, intensity * 0.06);
      splat(stack.get("density"),   W, H, ev.x, ev.y, r * 1.2, intensity * 0.04);
      break;
    }
    case "crystal": {
      splat(stack.get("pressure"), W, H, ev.x, ev.y, r * 0.7, intensity * 0.28);
      splat(stack.get("rigidity"), W, H, ev.x, ev.y, r * 0.7, intensity * 0.20);
      // Drag orientation extends ridge
      if (ev.dx !== 0 || ev.dy !== 0) {
        const len = Math.sqrt(ev.dx * ev.dx + ev.dy * ev.dy);
        if (len > 0.5) {
          const tx = ev.dx / len, ty = ev.dy / len;
          for (let s = -1; s <= 1; s += 0.5) {
            const px = ev.x + tx * r * 0.6 * s;
            const py = ev.y + ty * r * 0.6 * s;
            splat(stack.get("rigidity"), W, H, px, py, r * 0.4, intensity * 0.06);
          }
        }
      }
      break;
    }
    case "void": {
      attenuateToFloor(stack.get("density"),   W, H, ev.x, ev.y, r * 1.0, intensity * 0.32, 0.05);
      attenuateToFloor(stack.get("coherence"), W, H, ev.x, ev.y, r * 0.9, intensity * 0.28, 0.0);
      attenuateToFloor(stack.get("life"),      W, H, ev.x, ev.y, r * 1.0, intensity * 0.25, 0.0);
      break;
    }
    case "flow": {
      const vx = stack.get("vx"), vy = stack.get("vy");
      const vlen = Math.sqrt(ev.dx * ev.dx + ev.dy * ev.dy);
      if (vlen < 0.001) break;
      const ux = ev.dx / vlen, uy = ev.dy / vlen;
      const r2 = r * r;
      const x0 = Math.max(0, Math.floor(ev.x - r));
      const x1 = Math.min(W - 1, Math.ceil(ev.x + r));
      const y0 = Math.max(0, Math.floor(ev.y - r));
      const y1 = Math.min(H - 1, Math.ceil(ev.y + r));
      const mag = intensity * 0.05;
      for (let py = y0; py <= y1; py++) {
        for (let px = x0; px <= x1; px++) {
          const ddx = px - ev.x, ddy = py - ev.y;
          const d2 = ddx * ddx + ddy * ddy;
          if (d2 > r2) continue;
          const w = Math.exp(-d2 * 3 / r2);
          const i = py * W + px;
          vx[i] += ux * mag * w;
          vy[i] += uy * mag * w;
        }
      }
      break;
    }
    case "marma": {
      // Periodic micro-pulse during peak phase
      const t = age % 7;
      const mp = Math.exp(-((t - 0) ** 2) / 2);
      splat(stack.get("charge"),    W, H, ev.x, ev.y, r * 0.5, intensity * 0.22 * mp);
      splat(stack.get("coherence"), W, H, ev.x, ev.y, r * 0.4, intensity * 0.14 * mp);
      break;
    }
    case "yantra": {
      // Bindu center + concentric ring on coherence
      splat(stack.get("coherence"), W, H, ev.x, ev.y, r * 0.35, intensity * 0.32);
      splatRing(stack.get("coherence"), W, H, ev.x, ev.y, r * 1.0, r * 0.85, intensity * 0.14);
      // Subtle rigidity at the seat (yantra is "fixed" symbol)
      splat(stack.get("rigidity"), W, H, ev.x, ev.y, r * 0.5, intensity * 0.06);
      break;
    }
    case "reveal": {
      // Wide gentle coherence boost
      splat(stack.get("coherence"), W, H, ev.x, ev.y, r * 1.6, intensity * 0.10);
      splat(stack.get("life"),      W, H, ev.x, ev.y, r * 1.4, intensity * 0.04);
      break;
    }
    case "breath": {
      // Global pulse — additive coherence + life over wide radius
      splat(stack.get("coherence"), W, H, ev.x, ev.y, r * 1.8, intensity * 0.14);
      splat(stack.get("life"),      W, H, ev.x, ev.y, r * 1.6, intensity * 0.08);
      splat(stack.get("moisture"),  W, H, ev.x, ev.y, r * 1.5, intensity * 0.06);
      break;
    }
    case "vortex": {
      // Add tangential velocity around (ev.x, ev.y)
      const vx = stack.get("vx"), vy = stack.get("vy");
      const r2 = r * r;
      const x0 = Math.max(0, Math.floor(ev.x - r));
      const x1 = Math.min(W - 1, Math.ceil(ev.x + r));
      const y0 = Math.max(0, Math.floor(ev.y - r));
      const y1 = Math.min(H - 1, Math.ceil(ev.y + r));
      const sign = ev.extra?.dir ?? 1;
      const mag = intensity * 0.06 * sign;
      for (let py = y0; py <= y1; py++) {
        for (let px = x0; px <= x1; px++) {
          const ddx = px - ev.x, ddy = py - ev.y;
          const d2 = ddx * ddx + ddy * ddy;
          if (d2 > r2 || d2 < 1) continue;
          const d = Math.sqrt(d2);
          // Tangent: rotate (dx, dy) by 90° → (-dy, dx)
          const tx = -ddy / d, ty = ddx / d;
          const w = Math.exp(-d2 * 2 / r2);
          const i = py * W + px;
          vx[i] += tx * mag * w;
          vy[i] += ty * mag * w;
        }
      }
      break;
    }
    case "helical": {
      // Vortex + vertical compression bias (twist around vertical axis at ev.x)
      const vx = stack.get("vx"), vy = stack.get("vy");
      const r2 = r * r;
      const x0 = Math.max(0, Math.floor(ev.x - r));
      const x1 = Math.min(W - 1, Math.ceil(ev.x + r));
      const y0 = Math.max(0, Math.floor(ev.y - r));
      const y1 = Math.min(H - 1, Math.ceil(ev.y + r));
      const mag = intensity * 0.06;
      for (let py = y0; py <= y1; py++) {
        for (let px = x0; px <= x1; px++) {
          const ddx = px - ev.x, ddy = py - ev.y;
          const d2 = ddx * ddx + ddy * ddy;
          if (d2 > r2 || d2 < 1) continue;
          const d = Math.sqrt(d2);
          const tx = -ddy / d, ty = ddx / d;
          const w = Math.exp(-d2 * 2 / r2);
          const sign = ddy > 0 ? 1 : -1;       // upper / lower halves twist opposite
          const i = py * W + px;
          vx[i] += tx * mag * w * sign;
          vy[i] += ty * mag * w * sign;
        }
      }
      // Modest compression on rigidity along axis
      splat(stack.get("rigidity"), W, H, ev.x, ev.y, r * 0.6, intensity * 0.04);
      break;
    }
    case "symbol_node": {
      // A long-lived symbol at the click point — combines yantra + bloom
      // with extended memory (set in TOOL_OVERRIDES).
      splat(stack.get("coherence"), W, H, ev.x, ev.y, r * 0.4, intensity * 0.28);
      splatRing(stack.get("coherence"), W, H, ev.x, ev.y, r * 1.1, r * 0.95, intensity * 0.16);
      splat(stack.get("rigidity"),  W, H, ev.x, ev.y, r * 0.6, intensity * 0.10);
      splat(stack.get("life"),      W, H, ev.x, ev.y, r * 0.7, intensity * 0.04);
      break;
    }
    // ── v0.9 visual response signatures ──────────────────────────
    case "flash": {
      // Camera-shutter brightness spike across a wide radius
      splat(stack.get("coherence"), W, H, ev.x, ev.y, r * 2.4, intensity * 0.22);
      splat(stack.get("life"),      W, H, ev.x, ev.y, r * 2.2, intensity * 0.14);
      splat(stack.get("density"),   W, H, ev.x, ev.y, r * 2.0, intensity * 0.10);
      break;
    }
    case "shockwave": {
      // Expanding ring — radius grows with age regardless of envelope.
      // Adds 5 satellite blooms on a golden-angle phyllotaxy spiral so
      // the wave carries a hidden structure as it propagates.
      const ringR = r * 0.4 + age * 1.4;
      const ringW = Math.max(2, r * 0.20);
      splatRing(stack.get("coherence"), W, H, ev.x, ev.y, ringR, ringR - ringW, intensity * 0.24);
      splatRing(stack.get("life"),      W, H, ev.x, ev.y, ringR, ringR - ringW, intensity * 0.06);
      const GA = 137.5077640500378 * Math.PI / 180;
      for (let k = 0; k < 5; k++) {
        const a = age * 0.06 + k * GA;
        const sx = ev.x + Math.cos(a) * ringR;
        const sy = ev.y + Math.sin(a) * ringR;
        splat(stack.get("coherence"), W, H, sx, sy, ringW * 0.7, intensity * 0.06);
      }
      if (ringR > r * 0.8) {
        splat(stack.get("coherence"), W, H, ev.x, ev.y, ringR * 0.5, intensity * 0.04);
      }
      break;
    }
    case "summon": {
      // Wide slow oracle bloom — coherence + life + moisture saturation.
      // 8 phyllotaxy petals at golden-angle spacing for a Sri-yantra-like
      // structure that grows from within.
      splat(stack.get("coherence"), W, H, ev.x, ev.y, r * 1.5, intensity * 0.12);
      splat(stack.get("life"),      W, H, ev.x, ev.y, r * 1.3, intensity * 0.07);
      splat(stack.get("moisture"),  W, H, ev.x, ev.y, r * 1.4, intensity * 0.09);
      const ringR = r * 0.5 + age * 0.5;
      splatRing(stack.get("coherence"), W, H, ev.x, ev.y, ringR, ringR * 0.85, intensity * 0.06);
      const GA = 137.5077640500378 * Math.PI / 180;
      const PHI = 1.6180339887498949;
      for (let k = 0; k < 8; k++) {
        const a = k * GA;
        const rad = r * (0.4 + 0.18 * Math.sqrt(k + 1));
        const sx = ev.x + Math.cos(a) * rad;
        const sy = ev.y + Math.sin(a) * rad;
        splat(stack.get("coherence"), W, H, sx, sy, r * 0.18 * PHI, intensity * 0.05);
        splat(stack.get("life"),      W, H, sx, sy, r * 0.15 * PHI, intensity * 0.025);
      }
      break;
    }
    case "tap": {
      splat(stack.get("coherence"), W, H, ev.x, ev.y, r * 0.6, intensity * 0.20);
      splatRing(stack.get("coherence"), W, H, ev.x, ev.y, r * 1.2, r * 0.95, intensity * 0.10);
      break;
    }
    case "release": {
      // Soft echo at end of stroke
      splat(stack.get("coherence"), W, H, ev.x, ev.y, r * 0.5, intensity * 0.10);
      splat(stack.get("life"),      W, H, ev.x, ev.y, r * 0.4, intensity * 0.04);
      break;
    }
    case "palette_swap": {
      // Wide gentle pulse so palette change is felt across the canvas
      splat(stack.get("coherence"), W, H, ev.x, ev.y, r * 2.4, intensity * 0.10);
      splat(stack.get("life"),      W, H, ev.x, ev.y, r * 2.2, intensity * 0.05);
      splat(stack.get("moisture"),  W, H, ev.x, ev.y, r * 2.0, intensity * 0.04);
      break;
    }
    case "still_pulse": {
      // Slow expanding ring that damps density inside it (pause feel)
      const ringR = r * 0.5 + age * 0.65;
      splatRing(stack.get("coherence"), W, H, ev.x, ev.y, ringR, ringR * 0.85, intensity * 0.10);
      attenuateToFloor(stack.get("density"), W, H, ev.x, ev.y, ringR * 0.6,
                       intensity * 0.08, 0.30);
      break;
    }
    case "ripple": {
      // Fast small expanding ring
      const ringR = r * 0.5 + age * 0.85;
      splatRing(stack.get("coherence"), W, H, ev.x, ev.y, ringR, ringR * 0.85, intensity * 0.14);
      break;
    }
    case "idle_drift": {
      // Gentle ambient bloom at random position — keeps the field alive
      splat(stack.get("coherence"), W, H, ev.x, ev.y, r * 0.7, intensity * 0.10);
      splat(stack.get("life"),      W, H, ev.x, ev.y, r * 0.6, intensity * 0.05);
      splat(stack.get("moisture"),  W, H, ev.x, ev.y, r * 0.6, intensity * 0.04);
      break;
    }
    case "brush_ring": {
      // Single ring at cursor — shows the new brush size visually
      splatRing(stack.get("coherence"), W, H, ev.x, ev.y, r, r * 0.85, intensity * 0.18);
      break;
    }
    case "spark": {
      // Tiny bright dot for unbound keypress feedback
      splat(stack.get("coherence"), W, H, ev.x, ev.y, r * 0.4, intensity * 0.16);
      splat(stack.get("life"),      W, H, ev.x, ev.y, r * 0.3, intensity * 0.06);
      break;
    }
    case "ribbon": {
      // Curving stroke from (ev.x, ev.y) along (dx, dy) — leaves a coherent line
      const len = Math.sqrt(ev.dx * ev.dx + ev.dy * ev.dy);
      if (len < 0.5) {
        splat(stack.get("coherence"), W, H, ev.x, ev.y, r * 0.5, intensity * 0.16);
      } else {
        const ux = ev.dx / len, uy = ev.dy / len;
        for (let s = -2; s <= 2; s++) {
          const px = ev.x + ux * r * 0.4 * s;
          const py = ev.y + uy * r * 0.4 * s;
          splat(stack.get("coherence"), W, H, px, py, r * 0.4, intensity * 0.10);
        }
      }
      break;
    }
  }
}
