// Events pass — apply SceneGrammar to fields each tick (and on initial seed).
// v0.4: softer attenuation (toward floor, never zero); two new event kinds
// (coherence_pulse, pressure_ridge); a global `replenish` baseline that
// gently refills moisture/density/coherence wherever they have drained.

import { phaseScale } from "../atlas/grammar.js";

// ── Helpers ────────────────────────────────────────────────────────
function splat(field, W, H, x, y, radius, amount) {
  const r = radius;
  const r2 = r * r;
  const x0 = Math.max(0, Math.floor(x - r));
  const x1 = Math.min(W - 1, Math.ceil(x + r));
  const y0 = Math.max(0, Math.floor(y - r));
  const y1 = Math.min(H - 1, Math.ceil(y + r));
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

// Attenuate toward `floor` (not toward 0).  Lerp:
//   v := v + (floor - v) * w * fraction
// At w=1, fraction=1 → v becomes `floor`.  At w=0 → unchanged.
// At fraction<1 → v moves part-way toward floor each call.
function attenuateToFloor(field, W, H, x, y, radius, depth, floor) {
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
      const w = Math.exp(-d2 * 3 / r2);
      const i = py * W + px;
      const v = field[i];
      if (v > floor) {
        field[i] = v + (floor - v) * w * depth;
      }
    }
  }
}

function alongLine(x1, y1, x2, y2, fn, density = 1.5) {
  const dx = x2 - x1, dy = y2 - y1;
  const len = Math.sqrt(dx * dx + dy * dy);
  const steps = Math.max(2, Math.ceil(len * density));
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    fn(x1 + dx * t, y1 + dy * t, t);
  }
}

// ── Per-event applications ────────────────────────────────────────

function applyAttractor(stack, ev, scale, dt) {
  const W = stack.W, H = stack.H;
  const vx = stack.get("vx"), vy = stack.get("vy");
  const r2 = ev.radius * ev.radius;
  const x0 = Math.max(0, Math.floor(ev.x - ev.radius));
  const x1 = Math.min(W - 1, Math.ceil(ev.x + ev.radius));
  const y0 = Math.max(0, Math.floor(ev.y - ev.radius));
  const y1 = Math.min(H - 1, Math.ceil(ev.y + ev.radius));
  for (let py = y0; py <= y1; py++) {
    for (let px = x0; px <= x1; px++) {
      const dx = ev.x - px, dy = ev.y - py;
      const d2 = dx * dx + dy * dy;
      if (d2 > r2 || d2 < 0.5) continue;
      const d = Math.sqrt(d2);
      const w = (1 - d / ev.radius) * ev.strength * scale * dt * 0.04;
      const i = py * W + px;
      vx[i] += (dx / d) * w;
      vy[i] += (dy / d) * w;
    }
  }
}

function applyEmitter(stack, ev, scale, dt) {
  const field = stack.get(ev.field);
  if (!field) return;
  splat(field, stack.W, stack.H, ev.x, ev.y, ev.radius, ev.rate * scale * dt);
}

function applySink(stack, ev, scale, dt) {
  const field = stack.get(ev.field);
  if (!field) return;
  const floor = ev.floor ?? 0.05;
  // For non-charge fields, attenuate toward floor; for charge, allow signed.
  if (ev.field === "charge") {
    splat(field, stack.W, stack.H, ev.x, ev.y, ev.radius, -ev.rate * scale * dt);
  } else {
    attenuateToFloor(field, stack.W, stack.H, ev.x, ev.y, ev.radius,
                     ev.rate * scale * dt * 4, floor);
  }
}

function applyShearBand(stack, ev, scale, dt) {
  const W = stack.W, H = stack.H;
  const vx = stack.get("vx"), vy = stack.get("vy");
  const dx = ev.x2 - ev.x1, dy = ev.y2 - ev.y1;
  const len = Math.sqrt(dx * dx + dy * dy);
  if (len < 1) return;
  const tx = dx / len, ty = dy / len;
  const nx = -ty, ny = tx;
  alongLine(ev.x1, ev.y1, ev.x2, ev.y2, (cxp, cyp) => {
    for (let off = -ev.width; off <= ev.width; off += 1) {
      const sx = Math.round(cxp + nx * off);
      const sy = Math.round(cyp + ny * off);
      if (sx < 0 || sx >= W || sy < 0 || sy >= H) continue;
      const sign = off > 0 ? 1 : -1;
      const w = (1 - Math.abs(off) / ev.width) * ev.strength * scale * dt * 0.05;
      const i = sy * W + sx;
      vx[i] += sign * tx * w;
      vy[i] += sign * ty * w;
    }
  });
}

function applyRupture(stack, ev, scale, dt) {
  const W = stack.W, H = stack.H;
  const dens = stack.get("density");
  const floor = ev.floor ?? 0.10;
  alongLine(ev.x1, ev.y1, ev.x2, ev.y2, (cxp, cyp) => {
    attenuateToFloor(dens, W, H, cxp, cyp, ev.width + 1,
                     ev.depth * scale * dt * 4, floor);
  }, 1.0);
}

function applyBloomNode(stack, ev, scale, dt, tick) {
  const W = stack.W, H = stack.H;
  const coh = stack.get("coherence");
  const pulse = (Math.sin(ev.frequency * tick) + 1) * 0.5;
  splat(coh, W, H, ev.x, ev.y, ev.radius,
        ev.amplitude * scale * dt * (0.4 + 0.6 * pulse));
}

function applyStrike(stack, ev, scale, dt, tick) {
  const W = stack.W, H = stack.H;
  const charge = stack.get("charge");
  const dueTimes = [];
  if (ev.recurrence > 0) {
    if (tick >= ev.time && ((tick - ev.time) % ev.recurrence) < ev.lifetime) {
      dueTimes.push((tick - ev.time) % ev.recurrence);
    }
  } else {
    if (tick >= ev.time && tick < ev.time + ev.lifetime) {
      dueTimes.push(tick - ev.time);
    }
  }
  for (const age of dueTimes) {
    const decay = 1 - age / ev.lifetime;
    splat(charge, W, H, ev.x, ev.y, ev.radius,
          ev.magnitude * scale * decay * dt);
  }
}

function applyVoidPocket(stack, ev, scale, dt) {
  const W = stack.W, H = stack.H;
  const dens = stack.get("density");
  const floor = ev.floor ?? 0.08;
  attenuateToFloor(dens, W, H, ev.x, ev.y, ev.radius,
                   ev.depth * scale * dt * 3, floor);
}

// NEW v0.4: coherence_pulse — alternating + and - charge ring.
// Provides ringing structure without continuously draining any field.
function applyCoherencePulse(stack, ev, scale, dt, tick) {
  const W = stack.W, H = stack.H;
  const charge = stack.get("charge");
  const sig = Math.sin(ev.frequency * tick);
  splat(charge, W, H, ev.x, ev.y, ev.radius,
        ev.amplitude * scale * dt * sig);
}

// NEW v0.4: pressure_ridge — line accumulator into pressure + rigidity.
// Carves "bone-like" / "strata-like" structure as a slow continuous
// thickening rather than a one-shot subtraction.
function applyPressureRidge(stack, ev, scale, dt) {
  const W = stack.W, H = stack.H;
  const pressure = stack.get("pressure");
  const rigidity = stack.get("rigidity");
  alongLine(ev.x1, ev.y1, ev.x2, ev.y2, (cxp, cyp) => {
    splat(pressure, W, H, cxp, cyp, ev.width + 1, ev.strength * scale * dt);
    splat(rigidity, W, H, cxp, cyp, ev.width + 1, ev.strength * scale * dt * 0.7);
  }, 1.0);
}

// ── Master apply ───────────────────────────────────────────────────
export function applyEvents(stack, grammar, tick, phase, dt = 1.0) {
  if (!grammar || !grammar.events) return;
  const scale = phaseScale(phase, tick);
  for (const ev of grammar.events) {
    switch (ev.kind) {
      case "attractor":       applyAttractor(stack, ev, scale, dt); break;
      case "emitter":         applyEmitter(stack, ev, scale, dt); break;
      case "sink":            applySink(stack, ev, scale, dt); break;
      case "shear_band":      applyShearBand(stack, ev, scale, dt); break;
      case "rupture":         applyRupture(stack, ev, scale, dt); break;
      case "bloom_node":      applyBloomNode(stack, ev, scale, dt, tick); break;
      case "strike":          applyStrike(stack, ev, scale, dt, tick); break;
      case "void_pocket":     applyVoidPocket(stack, ev, scale, dt); break;
      case "coherence_pulse": applyCoherencePulse(stack, ev, scale, dt, tick); break;
      case "pressure_ridge":  applyPressureRidge(stack, ev, scale, dt); break;
    }
  }
}

// Initial perturbations on reset
export function seedEvents(stack, grammar) {
  if (!grammar || !grammar.events) return;
  const W = stack.W, H = stack.H;
  for (const ev of grammar.events) {
    switch (ev.kind) {
      case "emitter": {
        const field = stack.get(ev.field);
        if (field) splat(field, W, H, ev.x, ev.y, ev.radius, 0.4);
        break;
      }
      case "bloom_node":
      case "coherence_pulse": {
        const coh = stack.get("coherence");
        splat(coh, W, H, ev.x, ev.y, ev.radius * 0.6, 0.45);
        const dens = stack.get("density");
        attenuateToFloor(dens, W, H, ev.x, ev.y, ev.radius * 0.5, 0.4, 0.35);
        break;
      }
      case "rupture": {
        const dens = stack.get("density");
        const floor = ev.floor ?? 0.10;
        alongLine(ev.x1, ev.y1, ev.x2, ev.y2, (cxp, cyp) => {
          attenuateToFloor(dens, W, H, cxp, cyp, ev.width + 1, 0.6, floor);
        });
        break;
      }
      case "void_pocket": {
        const dens = stack.get("density");
        const floor = ev.floor ?? 0.08;
        attenuateToFloor(dens, W, H, ev.x, ev.y, ev.radius, 0.6, floor);
        break;
      }
      case "pressure_ridge": {
        const pressure = stack.get("pressure");
        const rigidity = stack.get("rigidity");
        alongLine(ev.x1, ev.y1, ev.x2, ev.y2, (cxp, cyp) => {
          splat(pressure, W, H, cxp, cyp, ev.width + 1, 0.4);
          splat(rigidity, W, H, cxp, cyp, ev.width + 1, 0.25);
        });
        break;
      }
    }
  }
}

// NEW v0.4: replenish pass — runs every tick BEFORE event application.
// Adds a small baseline trickle into key fields so they never sit at 0.
// Driven by `energy` and `replenish` controls.
//
//   moisture: drift toward 0.4 (the natural background level)
//   density:  drift toward a low floor (0.4) — Gray-Scott substrate stays alive
//   coherence: very gentle pull toward 0.05 (background catalyst)
//   life:     drift toward 0.05 minimum
//
// The drift is multiplicative-toward-target so high values are not
// affected (only depleted regions get replenished).
export function replenishPass(stack, params) {
  const { energy = 0.5, replenish = 0.5, decay = 0.95 } = params;
  const N = stack.N;
  const e = energy * replenish;     // combined drive (0..~1)
  if (e <= 0) return;

  // Per-field target / pull-strength
  const targets = [
    { name: "moisture",  target: 0.40, pull: 0.0030 * e },
    { name: "density",   target: 0.40, pull: 0.0015 * e },
    { name: "coherence", target: 0.05, pull: 0.0040 * e },
    { name: "life",      target: 0.04, pull: 0.0010 * e },
  ];
  for (const { name, target, pull } of targets) {
    const arr = stack.get(name);
    for (let i = 0; i < N; i++) {
      // Pull toward target only when below it (don't dampen peaks)
      const v = arr[i];
      if (v < target) arr[i] = v + (target - v) * pull;
    }
  }
  // Apply user-set decay multiplier to charge (else discharge accumulates
  // unboundedly in some regimes).
  if (decay < 1) {
    const charge = stack.get("charge");
    for (let i = 0; i < N; i++) charge[i] *= decay;
  }
}
