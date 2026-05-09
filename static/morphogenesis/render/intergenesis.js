// Intergenesis — region-based visual-state transition system.
//
// The canvas is divided into a coarse grid of regions (16×16 by default).
// Each region holds a state-weight vector over the 16 visual states.
// User events update a "target" weight; weights smoothly lerp toward
// the target each frame, so visuals always feel like material transitions
// rather than instant snaps.
//
// Composition constraint: render uses the top two states per region
// only — winner-takes-most ensures one dominant visual family per area.
//
// Transitions are named operators that move a region from state A to
// state B with a duration, an echo count, and a spatial falloff.  Each
// echo is a delayed, weaker re-application of the same transition.

import { STATES, STATE_KEYS, N_STATES, STATE_INDEX, DEFAULT_STATE }
  from "./visualStates.js";
import { SHYAMA, postProcess } from "./colormap.js";

const REGION_W = 16, REGION_H = 16;

// ── 12 transition operators ────────────────────────────────────────
export const TRANSITIONS = {
  filament_to_lightning: { from: "filament", to: "lightning", durMs:  600, echoCount: 2, echoDelay: 200, falloff: 1.5 },
  filament_to_root:      { from: "filament", to: "root",      durMs: 1000, echoCount: 1, echoDelay: 350, falloff: 1.2 },
  membrane_to_cellular:  { from: "membrane", to: "cellular",  durMs:  800, echoCount: 1, echoDelay: 250, falloff: 1.4 },
  cellular_to_membrane:  { from: "cellular", to: "membrane",  durMs: 1000, echoCount: 1, echoDelay: 300, falloff: 1.4 },
  flow_to_crystal:       { from: "flow",     to: "crystal",   durMs: 1200, echoCount: 1, echoDelay: 400, falloff: 1.0 },
  crystal_to_flow:       { from: "crystal",  to: "flow",      durMs:  900, echoCount: 1, echoDelay: 300, falloff: 1.2 },
  fluid_to_terrain:      { from: "fluid",    to: "terrain",   durMs: 1500, echoCount: 1, echoDelay: 450, falloff: 1.0 },
  density_to_void:       { from: "density",  to: "void",      durMs:  800, echoCount: 0, echoDelay: 0,   falloff: 1.5 },
  smoke_to_body:         { from: "smoke",    to: "body",      durMs: 1100, echoCount: 1, echoDelay: 350, falloff: 1.2 },
  body_to_root:          { from: "body",     to: "root",      durMs: 1300, echoCount: 1, echoDelay: 400, falloff: 1.0 },
  bloom_to_eye:          { from: "bloom",    to: "eye",       durMs:  900, echoCount: 2, echoDelay: 250, falloff: 1.3 },
  eye_to_star:           { from: "eye",      to: "star",      durMs:  700, echoCount: 3, echoDelay: 180, falloff: 1.5 },
};
export const TRANSITION_KEYS = Object.keys(TRANSITIONS);

// ── RegionMap ──────────────────────────────────────────────────────

export class RegionMap {
  constructor(simW, simH) {
    this.simW = simW; this.simH = simH;
    this.rw = REGION_W; this.rh = REGION_H;
    this.cellW = simW / REGION_W;
    this.cellH = simH / REGION_H;
    this.weights = new Float32Array(REGION_W * REGION_H * N_STATES);
    this.target  = new Float32Array(REGION_W * REGION_H * N_STATES);
    this.defaultStateIdx = STATE_INDEX[DEFAULT_STATE];
    // Initialize: all regions in default state
    for (let r = 0; r < REGION_W * REGION_H; r++) {
      this.weights[r * N_STATES + this.defaultStateIdx] = 1.0;
      this.target [r * N_STATES + this.defaultStateIdx] = 1.0;
    }
    // Pending echoes: { tMs, x, y, transitionKey, intensityMul, falloffMul }
    this.echoes = [];

    // P4 (issue #8) — precomputed top-2 state per region cell.
    // Refreshed once per frame in step().  Saves ~64 ops/pixel in the
    // renderer's per-pixel loop (was: 16-state × 4-cell bilinear blend).
    const cellCount = REGION_W * REGION_H;
    this.cellTopIdx0 = new Int8Array(cellCount);
    this.cellTopIdx1 = new Int8Array(cellCount);
    this.cellTopW0   = new Float32Array(cellCount);
    this.cellTopW1   = new Float32Array(cellCount);
    // Pre-allocated per-pixel candidate scratch (max 8 unique states from 4 cells × 2)
    this._candIdx = new Int8Array(8);
    this._candW   = new Float32Array(8);
    this._precomputeTopStates();
  }

  // Recompute top-2 indices + weights per region cell.  Called once per
  // step() so the per-pixel renderer just looks them up.
  _precomputeTopStates() {
    const total = REGION_W * REGION_H;
    for (let r = 0; r < total; r++) {
      const off = r * N_STATES;
      let bi = 0, bw = -1, si = 0, sw = -1;
      for (let s = 0; s < N_STATES; s++) {
        const v = this.weights[off + s];
        if (v > bw) { si = bi; sw = bw; bi = s; bw = v; }
        else if (v > sw) { si = s; sw = v; }
      }
      this.cellTopIdx0[r] = bi;
      this.cellTopIdx1[r] = si;
      this.cellTopW0[r]   = bw < 0 ? 0 : bw;
      this.cellTopW1[r]   = sw < 0 ? 0 : sw;
    }
  }

  setDefaultState(stateName) {
    if (STATE_INDEX[stateName] !== undefined) {
      this.defaultStateIdx = STATE_INDEX[stateName];
    }
  }

  // Apply a transition centered at (x, y) sim coords.
  applyTransition(transitionKey, simX, simY, intensity = 1.0,
                  baseFalloffCells = 2.5, nowMs = 0) {
    const t = TRANSITIONS[transitionKey];
    if (!t) return;
    const fromIdx = STATE_INDEX[t.from];
    const toIdx   = STATE_INDEX[t.to];
    if (toIdx === undefined) return;
    const radiusCells = baseFalloffCells * (t.falloff || 1);
    this._stampTarget(simX, simY, fromIdx, toIdx, intensity, radiusCells);
    // Schedule echoes
    for (let k = 1; k <= (t.echoCount || 0); k++) {
      this.echoes.push({
        tMs: nowMs + k * (t.echoDelay || 250),
        simX, simY,
        transitionKey,
        intensityMul: Math.pow(0.62, k),
        radiusCellsMul: 1 + 0.20 * k,
      });
    }
  }

  // Stamp target weights in a soft disk around the region
  _stampTarget(simX, simY, fromIdx, toIdx, intensity, radiusCells) {
    const rcx = simX / this.cellW;
    const rcy = simY / this.cellH;
    const rR = Math.max(1, radiusCells);
    const x0 = Math.max(0, Math.floor(rcx - rR));
    const x1 = Math.min(REGION_W - 1, Math.ceil(rcx + rR));
    const y0 = Math.max(0, Math.floor(rcy - rR));
    const y1 = Math.min(REGION_H - 1, Math.ceil(rcy + rR));
    for (let ry = y0; ry <= y1; ry++) {
      for (let rx = x0; rx <= x1; rx++) {
        const dx = rx + 0.5 - rcx;
        const dy = ry + 0.5 - rcy;
        const d  = Math.hypot(dx, dy);
        if (d > rR) continue;
        const fall = Math.exp(-(d * d) / (rR * rR * 0.7));
        const off = (ry * REGION_W + rx) * N_STATES;
        const w = fall * intensity;
        // Scale every other state down a touch (composition constraint:
        // the new state takes over) and boost the target.
        for (let s = 0; s < N_STATES; s++) {
          if (s !== toIdx && s !== fromIdx) {
            this.target[off + s] *= (1 - w * 0.55);
          } else if (s === fromIdx) {
            this.target[off + s] *= (1 - w * 0.85);
          }
        }
        this.target[off + toIdx] += w * 1.4;
      }
    }
  }

  // Each frame: apply due echoes, lerp weights toward targets, decay
  // targets gently back toward the default state so the field always
  // returns home if untouched.
  step(nowMs, lerpRate = 0.06, decayRate = 0.0035) {
    if (this.echoes.length) {
      const remain = [];
      for (const e of this.echoes) {
        if (nowMs >= e.tMs) {
          this.applyTransition(e.transitionKey, e.simX, e.simY,
                               e.intensityMul, 2.5 * e.radiusCellsMul, nowMs);
        } else remain.push(e);
      }
      this.echoes = remain;
    }
    // Decay every cell's target toward (default = 1.0, others *= 1-decay)
    const total = REGION_W * REGION_H;
    const def = this.defaultStateIdx;
    for (let r = 0; r < total; r++) {
      const off = r * N_STATES;
      for (let s = 0; s < N_STATES; s++) {
        if (s === def) {
          this.target[off + s] += (1.0 - this.target[off + s]) * decayRate;
        } else {
          this.target[off + s] *= (1 - decayRate * 1.5);
        }
      }
    }
    // Lerp weights toward targets
    for (let i = 0; i < this.weights.length; i++) {
      this.weights[i] += (this.target[i] - this.weights[i]) * lerpRate;
    }
    // P4 — refresh per-cell top-2 cache for the renderer
    this._precomputeTopStates();
  }

  // P4 (issue #8) — fast per-pixel top-2 lookup.
  // Each region cell has precomputed top-2 (idx, weight).  We pull 4
  // neighbor cells' top-2 (max 8 candidates), bilinear-blend their
  // weights, find the top 2 of those candidates.  ~40 ops/pixel vs.
  // the previous ~80 ops (16 states × 4 cells blend + sort).
  topStatesAt(simX, simY) {
    const fx = simX / this.cellW - 0.5;
    const fy = simY / this.cellH - 0.5;
    const rx0 = Math.max(0, Math.min(REGION_W - 1, Math.floor(fx)));
    const ry0 = Math.max(0, Math.min(REGION_H - 1, Math.floor(fy)));
    const rx1 = Math.min(REGION_W - 1, rx0 + 1);
    const ry1 = Math.min(REGION_H - 1, ry0 + 1);
    const sx = clamp01(fx - rx0), sy = clamp01(fy - ry0);
    const w00 = (1 - sx) * (1 - sy);
    const w10 = sx * (1 - sy);
    const w01 = (1 - sx) * sy;
    const w11 = sx * sy;
    const r00 = ry0 * REGION_W + rx0;
    const r10 = ry0 * REGION_W + rx1;
    const r01 = ry1 * REGION_W + rx0;
    const r11 = ry1 * REGION_W + rx1;

    const candIdx = this._candIdx;
    const candW   = this._candW;
    let nC = 0;

    // Inline `add(idx, w)` — search existing candidates, sum if found
    const add = (idx, w) => {
      for (let i = 0; i < nC; i++) {
        if (candIdx[i] === idx) { candW[i] += w; return; }
      }
      candIdx[nC] = idx; candW[nC] = w; nC++;
    };
    add(this.cellTopIdx0[r00], this.cellTopW0[r00] * w00);
    add(this.cellTopIdx1[r00], this.cellTopW1[r00] * w00);
    add(this.cellTopIdx0[r10], this.cellTopW0[r10] * w10);
    add(this.cellTopIdx1[r10], this.cellTopW1[r10] * w10);
    add(this.cellTopIdx0[r01], this.cellTopW0[r01] * w01);
    add(this.cellTopIdx1[r01], this.cellTopW1[r01] * w01);
    add(this.cellTopIdx0[r11], this.cellTopW0[r11] * w11);
    add(this.cellTopIdx1[r11], this.cellTopW1[r11] * w11);

    // Find top-2 among ≤8 candidates
    let bi = candIdx[0], bw = candW[0], si = 0, sw = -1;
    for (let i = 1; i < nC; i++) {
      const v = candW[i];
      if (v > bw) { si = bi; sw = bw; bi = candIdx[i]; bw = v; }
      else if (v > sw) { si = candIdx[i]; sw = v; }
    }
    const tot = bw + sw;
    if (tot <= 0) return [this.defaultStateIdx, 0, 1.0, 0.0];
    return [bi, si, bw / tot, sw / tot];
  }
}

function clamp01(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }

// ── Renderer ───────────────────────────────────────────────────────
// Replaces the per-pixel palette function.  For each sim pixel:
//   1. Look up top-2 visual states + weights from RegionMap
//   2. Run extractor for each, blend by weight
//   3. Apply contrast/exposure/tone-map via existing postProcess

export function renderIntergenesis(stack, dst, regionMap, simW, simH,
                                   contrast, exposure) {
  const f = stack.fields;
  const N = simW * simH;
  // Precompute per-pixel features used by extractors
  const opts = _ensureOpts(simW, simH);
  _computeGradMag(f.density, opts.gradMag, simW, simH);
  _computeRadialN(opts.radialN, simW, simH);

  // For each pixel
  for (let y = 0; y < simH; y++) {
    for (let x = 0; x < simW; x++) {
      const i = y * simW + x;
      const [a, b, wa, wb] = regionMap.topStatesAt(x, y);
      const ra = STATES[STATE_KEYS[a]](f, i, opts);
      const rb = wb > 0.01 ? STATES[STATE_KEYS[b]](f, i, opts) : ra;
      const r = ra[0] * wa + rb[0] * wb;
      const g = ra[1] * wa + rb[1] * wb;
      const bl = ra[2] * wa + rb[2] * wb;
      const [R, G, B] = postProcess(r, g, bl, contrast, exposure);
      const off = i * 3;
      dst[off]     = R;
      dst[off + 1] = G;
      dst[off + 2] = B;
    }
  }
}

let _opts = null;
function _ensureOpts(W, H) {
  if (_opts && _opts.W === W && _opts.H === H) return _opts;
  const N = W * H;
  _opts = {
    W, H,
    gradMag: new Float32Array(N),
    radialN: new Float32Array(N),
  };
  return _opts;
}
function _computeGradMag(field, dst, W, H) {
  for (let y = 0; y < H; y++) {
    const ym = (y - 1 + H) % H, yp = (y + 1) % H;
    for (let x = 0; x < W; x++) {
      const xm = (x - 1 + W) % W, xp = (x + 1) % W;
      const gx = field[y * W + xp] - field[y * W + xm];
      const gy = field[yp * W + x] - field[ym * W + x];
      dst[y * W + x] = Math.sqrt(gx * gx + gy * gy);
    }
  }
}
function _computeRadialN(dst, W, H) {
  // Normalized distance from center, [0..1]
  const cx = W * 0.5, cy = H * 0.5;
  const maxR = Math.sqrt(cx * cx + cy * cy);
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      const dx = x - cx, dy = y - cy;
      dst[y * W + x] = Math.min(1, Math.sqrt(dx * dx + dy * dy) / maxR);
    }
  }
}
