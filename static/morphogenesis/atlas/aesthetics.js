// Aesthetic registry — turns the symbolic state of the engine
// (dhātu, bhasma stage, dominant verb, tithi, lo shu cell, primes) into
// a per-frame tint context the compositor can apply.
//
// Nothing here changes field math directly.  The point is to map
// already-present *meaning* to color so the visible output flows with the
// current state.
//
//   dhātu      → base hue signature  (which tissue is the field most like)
//   bhasma     → warmth + saturation (rasaśāstra stage temperature)
//   verb       → temperature shift   (gesture mood)
//   tithi      → hue rotation        (lunar position)
//   loShu      → spatial 3×3 cycling weight
//   primes     → pulse beat          (3, 5, 7, 11 — Atlas planetary primes)

export const PHI       = 1.6180339887498949;
export const PHI_INV   = 0.6180339887498949;
export const GOLDEN_ANGLE = 137.5077640500378 * Math.PI / 180;   // radians
export const PLANETARY_PRIMES = [3, 5, 7, 11];

// ── per-dhātu color signatures (gentle tints) ────────────────────────
//   D001 rasa     → plasma·pale aqua
//   D002 rakta    → blood·deep red
//   D003 mamsa    → muscle·flesh
//   D004 meda     → fat·cream gold
//   D005 asthi    → bone·ivory
//   D006 majja    → nerve·lilac
//   D007 shukra   → generative·pearl
export const DHATU_TINT = {
  D001: [0.55, 0.75, 0.95],
  D002: [0.85, 0.25, 0.30],
  D003: [0.65, 0.40, 0.35],
  D004: [0.95, 0.85, 0.65],
  D005: [0.85, 0.85, 0.80],
  D006: [0.65, 0.55, 0.85],
  D007: [0.85, 0.80, 0.95],
};

// ── per-bhasma-stage tonal modulation ────────────────────────────────
// [hueRotateDeg, saturationMul, warmthAdd]   warmth in [-1, +1]
export const BHASMA_TINT = {
  shodhana:           [-12,  0.95, -0.18],
  mardana:            [  0,  0.78, -0.05],
  bhavana:            [ 32,  1.05, -0.05],
  puta_agni:          [ 16,  1.20, +0.45],
  sattva_extraction:  [  0,  1.10, +0.10],
  stabilization:      [  4,  1.00, +0.02],
  marana:             [-30,  0.78, -0.30],
  amritikarana:       [-12,  1.10, +0.05],
  dormant_seed:       [-44,  0.85, -0.20],
};

// ── verb temperature (gesture mood) ──────────────────────────────────
// warmthAdd in [-1, +1].  None of these is huge — they're nudges, not
// repaints; the underlying palette still leads.
export const VERB_TEMPERATURE = {
  bloom:     +0.10,
  branch:    -0.06,
  discharge: +0.45,
  water:     -0.35,
  crystal:   +0.00,
  void:      -0.20,
  flow:      -0.10,
  pulse:     +0.20,
  yantra:    +0.00,
  reveal:    +0.05,
  breath:    +0.00,
  // ambient kinds tuned softer
  idle_drift: -0.05,
  flash:     +0.10,
  shockwave: +0.05,
  summon:    +0.05,
  ripple:     0.00,
  spark:     +0.05,
  still_pulse: -0.10,
};

// ── 9 rasas → palette mode ──────────────────────────────────────────
export const RASA_PALETTES = [
  "shanta", "shringara", "vira", "raudra", "karuna", "adbhuta",
];

// ── tithi → hue rotation ─────────────────────────────────────────────
//   pratipada(1) … purnima(15)/amavasya(0) cycle 0..360°
export function tithiHueShift(tithiPos) {
  if (typeof tithiPos !== "number") return 0;
  return ((tithiPos % 15) / 15) * 360;
}

// ── lo shu 3×3 cycle (1..9) — ticks through every 9 steps ────────────
//   3-fold magic-square traversal — soft rotational structure
export function loShuCell(tick) {
  return ((tick / 9) | 0) % 9 + 1;
}

// ── prime-tick beat ──────────────────────────────────────────────────
// Returns 1 on prime ticks (3, 5, 7, 11 cycle), 0 otherwise.  Used to
// pulse coherence/replenish gently — gives the field a low-frequency
// "heartbeat" that resonates with the Atlas planetary-prime layer.
export function primeBeat(tick) {
  for (const p of PLANETARY_PRIMES) {
    if (tick % p === 0) return p;     // returns the prime that fired
  }
  return 0;
}

// ── compute aesthetic context for the current sim state ──────────────
export function computeAestheticContext(sim) {
  const dhatuId = sim.embodiment?.dhatu;
  const bhasma  = sim.bhasmaStage?.stage;
  const tithi   = sim.bhasmaStage?.tithi_pos ?? 7;
  const verb    = sim.dominantVerb;

  return {
    dhatuTint:   DHATU_TINT[dhatuId] || null,
    bhasmaTint:  BHASMA_TINT[bhasma] || null,
    verbTemp:    VERB_TEMPERATURE[verb] || 0,
    hueShift:    tithiHueShift(tithi),
    loShuCell:   loShuCell(sim.tick),
    primeBeat:   primeBeat(sim.tick),
  };
}

// ── color helpers ────────────────────────────────────────────────────

// HSL hue rotation on RGB in [0..1].  degrees in [0, 360].
// Cheap matrix variant — close to true HSL rotation for moderate angles.
export function rotateHue(r, g, b, degrees) {
  if (!degrees) return [r, g, b];
  const u = Math.cos(degrees * Math.PI / 180);
  const w = Math.sin(degrees * Math.PI / 180);
  const m = [
    0.299 + 0.701 * u + 0.168 * w,
    0.587 - 0.587 * u + 0.330 * w,
    0.114 - 0.114 * u - 0.497 * w,
    0.299 - 0.299 * u - 0.328 * w,
    0.587 + 0.413 * u + 0.035 * w,
    0.114 - 0.114 * u + 0.292 * w,
    0.299 - 0.300 * u + 1.250 * w,
    0.587 - 0.588 * u - 1.050 * w,
    0.114 + 0.886 * u - 0.203 * w,
  ];
  return [
    r * m[0] + g * m[1] + b * m[2],
    r * m[3] + g * m[4] + b * m[5],
    r * m[6] + g * m[7] + b * m[8],
  ];
}

// Apply the per-frame aesthetic context to a single RGB pixel.
// Order: dhātu base-tint blend → bhasma warmth/saturation → verb
// temperature → tithi hue rotation.  Each step is small; the cumulative
// effect is a subtle but readable mood.
export function applyAesthetic(r, g, b, ctx) {
  if (!ctx) return [r, g, b];

  // 1. Bhasma tint — warmth additive + saturation multiplicative
  if (ctx.bhasmaTint) {
    const [, satMul, warm] = ctx.bhasmaTint;
    const lum = 0.30 * r + 0.59 * g + 0.11 * b;
    r = lum + (r - lum) * satMul;
    g = lum + (g - lum) * satMul;
    b = lum + (b - lum) * satMul;
    if (warm > 0) { r += warm * 0.05; g += warm * 0.02; }
    else          { b += -warm * 0.04; g += -warm * 0.01; }
  }

  // 2. Verb temperature — small shift
  if (ctx.verbTemp) {
    const t = ctx.verbTemp * 0.04;
    if (t > 0) { r += t; g += t * 0.4; }
    else       { b += -t; g += -t * 0.3; }
  }

  // 3. Dhātu tint — blend a tiny fraction of the dhātu signature
  if (ctx.dhatuTint) {
    const [dr, dg, db] = ctx.dhatuTint;
    const w = 0.06;       // 6% pull toward dhātu signature
    r = r * (1 - w) + dr * w;
    g = g * (1 - w) + dg * w;
    b = b * (1 - w) + db * w;
  }

  // 4. Combined hue rotation: bhasma + tithi
  let hue = (ctx.bhasmaTint?.[0] ?? 0) + (ctx.hueShift * 0.04);
  if (hue) {
    [r, g, b] = rotateHue(r, g, b, hue);
  }

  return [r, g, b];
}
