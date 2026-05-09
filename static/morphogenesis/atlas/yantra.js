// Yantra — geometric masks as hidden field constraints.
// Each yantra type is a per-cell scalar field 0..1 indicating where the
// yantra's "presence" is strong.  This mask MULTIPLIES into replenish
// rates and ADDS small biases to coherence + life — so emergent forms
// concentrate within the yantra geometry without the geometry ever being
// drawn.
//
// Available yantra types:
//   "none"          — flat mask = 0 everywhere
//   "bindu"         — gaussian point at center
//   "circle"        — ring at fractional radius R, soft falloff
//   "triangle_up"   — upward triangle (Shiva, ascending fire)
//   "triangle_down" — downward triangle (Shakti, descending water)
//   "shatkona"      — six-pointed star (up + down triangle)
//   "square"        — square boundary frame
//   "lotus_8"       — eight-petal lotus
//   "lotus_12"      — twelve-petal lotus

function clamp01(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }

// Generic point-in-triangle test using barycentric coordinates.
// Returns 1 if (x,y) is inside the triangle defined by (a, b, c), else 0.
function inTriangle(x, y, ax, ay, bx, by, cx, cy) {
  const v0x = cx - ax, v0y = cy - ay;
  const v1x = bx - ax, v1y = by - ay;
  const v2x = x - ax,  v2y = y - ay;
  const d00 = v0x*v0x + v0y*v0y;
  const d01 = v0x*v1x + v0y*v1y;
  const d11 = v1x*v1x + v1y*v1y;
  const d20 = v2x*v0x + v2y*v0y;
  const d21 = v2x*v1x + v2y*v1y;
  const denom = d00 * d11 - d01 * d01;
  if (denom === 0) return 0;
  const u = (d11 * d20 - d01 * d21) / denom;
  const v = (d00 * d21 - d01 * d20) / denom;
  if (u < 0 || v < 0 || u + v > 1) return 0;
  // Soft inside — taper near the edges
  const inset = Math.min(u, v, 1 - u - v);
  return clamp01(inset * 4);
}

// ── Mask functions ───────────────────────────────────────────────────
// All take normalized coordinates (cx, cy) at center and W, H sim size,
// return value 0..1 at cell (x, y).

function bindu(x, y, W, H) {
  const cx = W/2, cy = H/2;
  const dx = x - cx, dy = y - cy;
  const r2 = dx*dx + dy*dy;
  const sigma = Math.min(W, H) * 0.10;
  return Math.exp(-r2 / (sigma * sigma));
}

function circle(x, y, W, H, fracRadius = 0.35) {
  const cx = W/2, cy = H/2;
  const dx = x - cx, dy = y - cy;
  const r = Math.sqrt(dx*dx + dy*dy);
  const R = Math.min(W, H) * 0.5 * fracRadius;
  const sigma = Math.min(W, H) * 0.025;
  const d = r - R;
  return Math.exp(-(d*d) / (sigma * sigma));
}

function triangle(x, y, W, H, polarity = "up", fracScale = 0.45) {
  const cx = W/2, cy = H/2;
  const r = Math.min(W, H) * 0.5 * fracScale;
  let ax, ay, bx, by, cxv, cy2;
  if (polarity === "up") {
    // Apex up (image y down → ay < cy)
    ax = cx;            ay = cy - r;
    bx = cx - r * 0.866; by = cy + r * 0.5;
    cxv = cx + r * 0.866; cy2 = cy + r * 0.5;
  } else {
    // Apex down
    ax = cx;            ay = cy + r;
    bx = cx - r * 0.866; by = cy - r * 0.5;
    cxv = cx + r * 0.866; cy2 = cy - r * 0.5;
  }
  return inTriangle(x, y, ax, ay, bx, by, cxv, cy2);
}

function shatkona(x, y, W, H) {
  // Union of upward + downward triangles
  const a = triangle(x, y, W, H, "up", 0.45);
  const b = triangle(x, y, W, H, "down", 0.45);
  return Math.max(a, b);
}

function square(x, y, W, H, fracSide = 0.78) {
  const cx = W/2, cy = H/2;
  const half = Math.min(W, H) * 0.5 * fracSide;
  const dx = Math.abs(x - cx), dy = Math.abs(y - cy);
  // Square boundary frame — strong on the edges of the inscribed square
  const onEdge = Math.max(0, half - Math.abs(Math.max(dx, dy) - half) * 8);
  // Normalize to 0..1
  return clamp01(onEdge / half);
}

function lotus(x, y, W, H, nPetals) {
  const cx = W/2, cy = H/2;
  const dx = x - cx, dy = y - cy;
  const r = Math.sqrt(dx*dx + dy*dy);
  const theta = Math.atan2(dy, dx);
  const R = Math.min(W, H) * 0.42;
  // Petal radial profile: peaks at R*0.65 with smooth falloff
  const radial = Math.exp(-Math.pow((r - R*0.65) / (R*0.18), 2));
  // Angular profile: cos(N·θ)^4, positive only where cos > 0
  const c = Math.cos(nPetals * theta);
  const angular = c > 0 ? Math.pow(c, 4) : 0;
  return radial * angular;
}

// ── Build mask Float32Array for a given yantra type ────────────────
export function buildYantraMask(type, W, H) {
  const mask = new Float32Array(W * H);
  if (!type || type === "none") return mask;

  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      let v = 0;
      switch (type) {
        case "bindu":         v = bindu(x, y, W, H); break;
        case "circle":        v = circle(x, y, W, H, 0.35); break;
        case "triangle_up":   v = triangle(x, y, W, H, "up"); break;
        case "triangle_down": v = triangle(x, y, W, H, "down"); break;
        case "shatkona":      v = shatkona(x, y, W, H); break;
        case "square":        v = square(x, y, W, H); break;
        case "lotus_8":       v = lotus(x, y, W, H, 8); break;
        case "lotus_12":      v = lotus(x, y, W, H, 12); break;
        case "sri_yantra_lite": {
          // Composite: bindu + small circle + shatkona + 8-lotus
          v = Math.max(
            0.8 * bindu(x, y, W, H),
            0.5 * circle(x, y, W, H, 0.2),
            0.4 * shatkona(x, y, W, H),
            0.6 * lotus(x, y, W, H, 8),
          );
          break;
        }
      }
      mask[y * W + x] = v;
    }
  }
  return mask;
}

// Apply yantra to fields — boost coherence and life proportional to
// mask × strength.  This is the only place the yantra appears in the
// simulation: as a small per-cell field bias, never as a drawn shape.
export function applyYantra(stack, mask, strength) {
  if (!mask || strength <= 0) return;
  const N = stack.N;
  const coh = stack.fields.coherence;
  const life = stack.fields.life;
  for (let i = 0; i < N; i++) {
    const w = mask[i] * strength;
    if (w === 0) continue;
    coh[i]  += w * 0.0012;
    life[i] += w * 0.0006;
  }
}
