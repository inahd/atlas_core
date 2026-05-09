// Visual state library — each state is a *feature extractor* that maps
// (fieldStack, pixelIndex, perPixelOpts) → linear RGB in [0..1].
//
// The intergenesis renderer never reads raw field buffers directly; it
// runs the top-2 dominant states per region and blends their outputs.
// This is what makes the canvas feel like *materials* rather than soup.
//
// 8 base states + 8 extended states named by the transition operators.

import { SHYAMA } from "./colormap.js";

function clamp01(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }
function smoothstep(e0, e1, x) {
  const t = clamp01((x - e0) / (e1 - e0));
  return t * t * (3 - 2 * t);
}

// Per-state feature extractor.  All take f = fieldStack.fields, i = index,
// opts = { gradMag[i], radialN[i] } precomputed by the renderer.
export const STATES = {
  // ── 8 base states ─────────────────────────────────────────────
  filament: (f, i, opts) => {
    // Thin bright veins: high branch_memory at front gradients
    const b = f.branch_memory[i];
    const g = opts.gradMag[i];
    const v = b * smoothstep(0.04, 0.30, g);
    const u = smoothstep(0.05, 0.40, b);
    return [0.18 + 0.62 * v + 0.20 * u,
            0.14 + 0.50 * v + 0.16 * u,
            0.10 + 0.30 * v + 0.10 * u];
  },
  membrane: (f, i) => {
    // Soft, smooth gradient: coherence + life dominate
    const c = f.coherence[i], l = f.life[i];
    const v = c * 0.55 + l * 0.45;
    return [0.16 + 0.40 * v + 0.05 * c,
            0.20 + 0.55 * v + 0.10 * l,
            0.30 + 0.50 * v + 0.10 * c];
  },
  flow: (f, i) => {
    // Directional streaks from velocity field
    const vx = f.vx[i], vy = f.vy[i];
    const mag = Math.min(1, Math.hypot(vx, vy) * 5.5);
    const ang = (Math.atan2(vy, vx) + Math.PI) / (2 * Math.PI);  // 0..1
    return [0.18 + 0.55 * mag * ang,
            0.20 + 0.45 * mag * (1 - Math.abs(ang - 0.5) * 2),
            0.30 + 0.50 * mag * (1 - ang)];
  },
  crystal: (f, i) => {
    // Faceted bright/dark: rigidity + density edges
    const r = f.rigidity[i], d = f.density[i];
    const facet = smoothstep(0.10, 0.55, r * 0.6 + d * 0.3);
    const sheen = smoothstep(0.35, 0.85, r);
    return [0.30 + 0.55 * facet + 0.15 * sheen,
            0.30 + 0.55 * facet + 0.15 * sheen,
            0.28 + 0.55 * facet + 0.20 * sheen];
  },
  void: () => {
    // Deep shyama; the floor enforces this anyway
    return [SHYAMA[0] * 1.05, SHYAMA[1] * 1.05, SHYAMA[2] * 1.20];
  },
  cellular: (f, i, opts) => {
    // Voronoi-like patches: solid cells with gradient borders
    const d = f.density[i];
    const g = opts.gradMag[i];
    const cell = d * (1 - smoothstep(0.04, 0.18, g));
    const edge = smoothstep(0.05, 0.22, g);
    return [0.18 + 0.45 * cell + 0.30 * edge,
            0.16 + 0.35 * cell + 0.25 * edge,
            0.20 + 0.30 * cell + 0.40 * edge];
  },
  smoke: (f, i) => {
    // Turbulent grayscale
    const ch = Math.abs(f.charge[i]);
    const m  = f.moisture[i];
    const turb = ch * 0.45 + m * 0.30 + smoothstep(0.05, 0.35, ch + m * 0.5) * 0.15;
    return [0.18 + 0.42 * turb,
            0.18 + 0.42 * turb,
            0.22 + 0.45 * turb];
  },
  body: (f, i) => {
    // Organic flesh: density + life + warmth
    const d = f.density[i], l = f.life[i], moist = f.moisture[i];
    const flesh = d * 0.50 + l * 0.30 + moist * 0.20;
    return [0.22 + 0.55 * flesh + 0.10 * d,
            0.16 + 0.30 * flesh + 0.05 * l,
            0.18 + 0.30 * flesh + 0.05 * moist];
  },

  // ── 8 extended states referenced by transitions ───────────────
  lightning: (f, i) => {
    // Sharp electric filaments: high charge + branch
    const ch = Math.abs(f.charge[i]);
    const b  = f.branch_memory[i];
    const fil = smoothstep(0.10, 0.40, ch * 0.55 + b * 0.45);
    return [0.30 + 0.60 * fil,
            0.30 + 0.55 * fil,
            0.55 + 0.45 * fil];
  },
  root: (f, i) => {
    // Deep branching veins: branch_memory dominant, density secondary
    const b = f.branch_memory[i], d = f.density[i];
    const root = smoothstep(0.06, 0.45, b * 0.7 + d * 0.3);
    return [0.20 + 0.40 * root,
            0.18 + 0.50 * root,
            0.10 + 0.20 * root];
  },
  terrain: (f, i) => {
    // Striated earth-bone
    const r = f.rigidity[i], d = f.density[i];
    const t = r * 0.55 + d * 0.45;
    return [0.30 + 0.45 * t,
            0.25 + 0.40 * t,
            0.18 + 0.30 * t];
  },
  fluid: (f, i) => {
    // Water-flowing soft
    const m = f.moisture[i], c = f.coherence[i];
    const fl = m * 0.60 + c * 0.40;
    return [0.15 + 0.30 * fl,
            0.22 + 0.45 * fl,
            0.40 + 0.55 * fl];
  },
  density: (f, i) => {
    // Solid mass — luminosity from density
    const d = smoothstep(0.10, 0.85, f.density[i]);
    return [0.10 + 0.55 * d,
            0.10 + 0.55 * d,
            0.12 + 0.55 * d];
  },
  bloom: (f, i) => {
    // Radiant coherence + life
    const c = f.coherence[i], l = f.life[i];
    const b = c * 0.60 + l * 0.40;
    return [0.30 + 0.65 * b,
            0.20 + 0.55 * b,
            0.30 + 0.50 * b];
  },
  eye: (f, i, opts) => {
    // Concentric radial coherence with bright center
    const c = f.coherence[i];
    const radial = opts.radialN[i];
    const eye = c * 0.55 + (1 - radial) * 0.45;
    return [0.25 + 0.55 * eye,
            0.22 + 0.55 * eye,
            0.30 + 0.55 * eye];
  },
  star: (f, i) => {
    // Scattered bright points: high coherence pinches
    const c = f.coherence[i];
    const pt = smoothstep(0.45, 0.82, c);
    return [0.40 + 0.60 * pt,
            0.40 + 0.60 * pt,
            0.55 + 0.45 * pt];
  },
};

export const STATE_KEYS = Object.keys(STATES);
export const N_STATES = STATE_KEYS.length;
export const STATE_INDEX = Object.fromEntries(STATE_KEYS.map((k, i) => [k, i]));
export const DEFAULT_STATE = "membrane";
