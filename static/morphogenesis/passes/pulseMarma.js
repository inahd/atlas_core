// Pulse-marma pass — drops a periodic charge + coherence pulse at a
// canvas position derived from the embodiment's body_region. The cycle
// length comes from animation_cycle_ms (modulated by bhasma stage).
//
// The marma is HIDDEN — we never label it. But the periodic ping at a
// region-specific point changes where new structure nucleates.

// Map body_region to normalized canvas (cx, cy) — anatomical mapping.
// (0,0) top-left, (1,1) bottom-right; head at top, feet at bottom.
const REGION_POS = {
  skull_vault:    [0.50, 0.08],
  eye_socket:     [0.42, 0.18],
  eye_lens:       [0.42, 0.18],
  iris:           [0.42, 0.18],
  cochlea:        [0.36, 0.20],
  nasal_cavity:   [0.50, 0.22],
  jaw_masseter:   [0.50, 0.26],
  cervical_spine: [0.50, 0.32],
  thoracic_spine: [0.50, 0.45],
  lumbar_spine:   [0.50, 0.62],
  sternum:        [0.50, 0.42],
  ribs:           [0.50, 0.45],
  clavicle:       [0.42, 0.34],
  scapula:        [0.36, 0.40],
  humerus:        [0.30, 0.48],
  radius_ulna:    [0.22, 0.58],
  carpals:        [0.16, 0.66],
  phalanges:      [0.12, 0.72],
  pelvis:         [0.50, 0.68],
  femur:          [0.42, 0.78],
  tibia_fibula:   [0.42, 0.88],
  tarsals:        [0.42, 0.94],
  lung_bronchial: [0.45, 0.40],
  heart_muscle:   [0.50, 0.42],
  fascia_network: [0.50, 0.50],
  skin_surface:   [0.50, 0.50],
};

export function pulseMarmaPass(stack, embodiment, tick, dtMs = 16, strength = 1.0) {
  if (!embodiment || !embodiment.body_region) return 0;
  if (strength <= 0) return 0;
  const cycleMs = embodiment.animation_cycle_ms ?? 4000;
  if (cycleMs <= 0) return 0;

  const W = stack.W, H = stack.H;
  const pos = REGION_POS[embodiment.body_region] ?? [0.5, 0.5];
  const px = pos[0] * W;
  const py = pos[1] * H;

  const tMs = tick * dtMs;
  const phase = (tMs % cycleMs) / cycleMs;
  const envelope = Math.exp(-Math.pow((phase - 0.0) * 6.0, 2));
  if (envelope < 0.02) return 0;

  const pattern = embodiment.animation_pattern ?? "steady_flame";
  const radius = patternRadius(pattern, phase);
  const amp = patternAmp(pattern, envelope) * strength;

  splat(stack.get("charge"), W, H, px, py, radius, amp * 0.18);
  splat(stack.get("coherence"), W, H, px, py, radius * 0.7, amp * 0.10);
  return envelope * strength;
}

function patternRadius(pattern, phase) {
  switch (pattern) {
    case "micro_oscillation": return 5;
    case "steady_flame":       return 8;
    case "expansion_contraction": return 6 + 6 * Math.sin(phase * Math.PI * 2);
    case "twin_pulse":         return 7;
    case "lightning_flicker":  return 4;
    case "spiral_pulse":       return 6 + 4 * phase;
    case "rooted_breath":      return 9;
    case "wave_cascade":       return 7;
    default:                   return 7;
  }
}

function patternAmp(pattern, envelope) {
  switch (pattern) {
    case "micro_oscillation":     return envelope * 0.6;
    case "lightning_flicker":     return envelope * 1.6;
    case "expansion_contraction": return envelope * 1.0;
    case "rooted_breath":         return envelope * 0.8;
    default:                      return envelope;
  }
}

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
