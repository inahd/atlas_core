// Overlays — abstract structural readouts drawn on top of the field render.
//
// Each overlay reads from grammar + fields and draws minimal canvas marks.
// All drawings are non-illustrative: thin strokes, dots, rings, gradient
// masks. No labels, no glyphs, no characters. The overlay just makes the
// grammar's structure legible against the soft field background.
//
// Coordinates: grammar/fields live in sim space (W × H); canvas is the
// outer drawing surface. We scale by canvas.width / sim.W on draw.

function clamp01(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }

// Bilinear sample of a Float32Array at fractional (x,y) with toroidal wrap.
function sampleField(arr, W, H, fx, fy) {
  const x0 = Math.floor(fx), y0 = Math.floor(fy);
  const sx = fx - x0, sy = fy - y0;
  const x1 = ((x0 % W) + W) % W;
  const x2 = ((x0 + 1) % W + W) % W;
  const y1 = ((y0 % H) + H) % H;
  const y2 = ((y0 + 1) % H + H) % H;
  const a = arr[y1 * W + x1] * (1 - sx) + arr[y1 * W + x2] * sx;
  const b = arr[y2 * W + x1] * (1 - sx) + arr[y2 * W + x2] * sx;
  return a * (1 - sy) + b * sy;
}

// ── Streamlines from velocity ──────────────────────────────────────
// Trace short curves following the velocity field at scattered seed points.
// Sparse — ~80 paths × 60 steps. Drawn additive with low alpha.
export function drawStreamlines(ctx, stack, scale, opts = {}) {
  const { count = 90, steps = 70, stepLen = 0.8 } = opts;
  const W = stack.W, H = stack.H;
  const vx = stack.get("vx"), vy = stack.get("vy");

  ctx.save();
  ctx.globalCompositeOperation = "lighter";
  ctx.strokeStyle = "rgba(220, 200, 160, 0.18)";
  ctx.lineWidth = 0.7;
  for (let i = 0; i < count; i++) {
    // Pseudo-random stable seed positions per call (no PRNG state needed —
    // we just use index+tick offset for variety).
    const sx = ((i * 9319 + 17) % W);
    const sy = ((i * 7993 + 53) % H);
    let px = sx, py = sy;
    ctx.beginPath();
    ctx.moveTo(px * scale, py * scale);
    for (let s = 0; s < steps; s++) {
      const u = sampleField(vx, W, H, px, py);
      const v = sampleField(vy, W, H, px, py);
      const m = Math.sqrt(u * u + v * v) + 1e-6;
      px += (u / m) * stepLen;
      py += (v / m) * stepLen;
      ctx.lineTo(px * scale, py * scale);
    }
    ctx.stroke();
  }
  ctx.restore();
}

// ── Branch memory filaments ───────────────────────────────────────
// Find local maxima of branch_memory; draw short tangent strokes there.
// The "filaments" are perpendicular to the gradient (along the ridge).
export function drawBranchFilaments(ctx, stack, scale, opts = {}) {
  const { thresh = 0.18, max_count = 240, length = 4 } = opts;
  const W = stack.W, H = stack.H;
  const branch = stack.get("branch_memory");
  ctx.save();
  ctx.globalCompositeOperation = "lighter";
  ctx.strokeStyle = "rgba(255, 220, 180, 0.55)";
  ctx.lineWidth = 0.85;
  ctx.beginPath();
  let drawn = 0;
  // Stride to keep cost bounded
  const stride = 2;
  for (let y = 1; y < H - 1; y += stride) {
    for (let x = 1; x < W - 1; x += stride) {
      const c = branch[y * W + x];
      if (c < thresh) continue;
      // Local maximum check (4-neighborhood)
      if (
        c < branch[y * W + x + 1] ||
        c < branch[y * W + x - 1] ||
        c < branch[(y + 1) * W + x] ||
        c < branch[(y - 1) * W + x]
      ) continue;
      // Gradient → perpendicular tangent
      const gx = 0.5 * (branch[y * W + x + 1] - branch[y * W + x - 1]);
      const gy = 0.5 * (branch[(y + 1) * W + x] - branch[(y - 1) * W + x]);
      const m = Math.sqrt(gx * gx + gy * gy) + 1e-6;
      // tangent perpendicular to gradient
      const tx = -gy / m, ty = gx / m;
      const px = x * scale, py = y * scale;
      const dx = tx * length * scale * 0.5;
      const dy = ty * length * scale * 0.5;
      ctx.moveTo(px - dx, py - dy);
      ctx.lineTo(px + dx, py + dy);
      drawn++;
      if (drawn >= max_count) break;
    }
    if (drawn >= max_count) break;
  }
  ctx.stroke();
  ctx.restore();
}

// ── Coherence rings — at bloom-node positions ─────────────────────
// Concentric circles whose radii pulse with time.
export function drawCoherenceRings(ctx, grammar, scale, tick) {
  if (!grammar || !grammar.events) return;
  ctx.save();
  ctx.globalCompositeOperation = "lighter";
  for (const ev of grammar.events) {
    if (ev.kind !== "bloom_node") continue;
    const cx = ev.x * scale, cy = ev.y * scale;
    const baseR = ev.radius * scale;
    const pulse = (Math.sin(ev.frequency * tick) + 1) * 0.5;
    for (let r = 0; r < 4; r++) {
      const radius = baseR * (0.4 + r * 0.35 + 0.2 * pulse);
      const alpha = 0.12 * (1 - r / 4);
      ctx.strokeStyle = `rgba(220, 200, 240, ${alpha})`;
      ctx.lineWidth = 0.9;
      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.stroke();
    }
  }
  ctx.restore();
}

// ── Discharge paths — trace high-charge cells along branch gradient ─
// Visualize where the discharge pass is propagating: starting at
// high-|charge| local cells, walk along increasing branch_memory.
export function drawDischargePaths(ctx, stack, scale, opts = {}) {
  const { count = 40, steps = 30, charge_thresh = 0.05 } = opts;
  const W = stack.W, H = stack.H;
  const charge = stack.get("charge");
  const branch = stack.get("branch_memory");

  // Find seed cells: high |charge| sampled randomly
  const seeds = [];
  const stride = 3;
  for (let y = 0; y < H; y += stride) {
    for (let x = 0; x < W; x += stride) {
      if (Math.abs(charge[y * W + x]) > charge_thresh) {
        seeds.push([x, y]);
      }
    }
  }
  if (seeds.length === 0) return;

  ctx.save();
  ctx.globalCompositeOperation = "lighter";
  ctx.strokeStyle = "rgba(180, 200, 255, 0.55)";
  ctx.lineWidth = 0.9;
  ctx.beginPath();

  // Pick `count` seeds roughly evenly
  const nDraw = Math.min(count, seeds.length);
  const step = Math.max(1, Math.floor(seeds.length / nDraw));
  for (let s = 0; s < seeds.length; s += step) {
    let [px, py] = seeds[s];
    ctx.moveTo(px * scale, py * scale);
    for (let i = 0; i < steps; i++) {
      // Walk along branch gradient (toward higher branch_memory)
      const xp = ((Math.floor(px) - 1 + W) % W);
      const xn = ((Math.floor(px) + 1) % W);
      const yp = ((Math.floor(py) - 1 + H) % H);
      const yn = ((Math.floor(py) + 1) % H);
      const ix = ((Math.floor(px) % W) + W) % W;
      const iy = ((Math.floor(py) % H) + H) % H;
      const gx = branch[iy * W + xn] - branch[iy * W + xp];
      const gy = branch[yn * W + ix] - branch[yp * W + ix];
      const m = Math.sqrt(gx * gx + gy * gy) + 1e-6;
      px += (gx / m) * 0.8;
      py += (gy / m) * 0.8;
      ctx.lineTo(px * scale, py * scale);
      // Stop if we've left the high-branch region
      if (sampleField(branch, W, H, px, py) < 0.05) break;
    }
  }
  ctx.stroke();
  ctx.restore();
}

// ── Cellular / bloom node markers ─────────────────────────────────
// Small soft dots at attractor + bloom-node locations.
export function drawNodes(ctx, grammar, scale) {
  if (!grammar || !grammar.events) return;
  ctx.save();
  ctx.globalCompositeOperation = "lighter";
  for (const ev of grammar.events) {
    let r, color;
    if (ev.kind === "bloom_node") {
      r = 2.4; color = "rgba(240, 220, 255, 0.55)";
    } else if (ev.kind === "attractor") {
      r = 1.8; color = "rgba(255, 220, 180, 0.45)";
    } else if (ev.kind === "emitter") {
      r = 1.4; color = "rgba(255, 200, 200, 0.35)";
    } else {
      continue;
    }
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(ev.x * scale, ev.y * scale, r, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();
}

// ── Void masking — non-compounding shyama-tinted depression ───────
// v0.4 fix: the v0.3 implementation used `globalCompositeOperation = "multiply"`
// against pure rgba(0,0,0, ~0.5) which compounded across frames into absolute
// black — one of the primary causes of collapse-to-black.
//
// v0.4 instead uses additive `source-over` with a *shyama-tinted* radial
// gradient that visually depresses the void region toward the cosmic ground
// without ever multiplying the canvas toward zero.  Bounded effect.
export function drawVoidMask(ctx, grammar, scale) {
  if (!grammar || !grammar.events) return;
  ctx.save();
  ctx.globalCompositeOperation = "source-over";
  for (const ev of grammar.events) {
    if (ev.kind !== "void_pocket") continue;
    const cx = ev.x * scale, cy = ev.y * scale;
    const r = ev.radius * scale;
    const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, r);
    const a = 0.40 + 0.40 * ev.depth;
    // Shyama tint, not pure black.  Approx (10, 13, 26).
    grad.addColorStop(0, `rgba(10, 13, 26, ${a})`);
    grad.addColorStop(0.7, `rgba(10, 13, 26, ${a * 0.4})`);
    grad.addColorStop(1, `rgba(10, 13, 26, 0)`);
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();
}

// ── Master overlay dispatcher ─────────────────────────────────────
export function drawOverlays(ctx, stack, grammar, canvas, toggles, tick) {
  const scale = canvas.width / stack.W;
  if (toggles.streamlines) drawStreamlines(ctx, stack, scale);
  if (toggles.branch_filaments) drawBranchFilaments(ctx, stack, scale);
  if (toggles.coherence_rings) drawCoherenceRings(ctx, grammar, scale, tick);
  if (toggles.discharge_paths) drawDischargePaths(ctx, stack, scale);
  if (toggles.nodes) drawNodes(ctx, grammar, scale);
  if (toggles.void_mask) drawVoidMask(ctx, grammar, scale);
}
