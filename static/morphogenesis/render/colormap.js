// Palettes — composite fields into RGB.
// v0.4: every palette ends with shyama floor + contrast + exposure so
// the output never goes below the cosmic background and tonal range
// is artist-controllable.

function clamp01(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }
function smoothstep(e0, e1, x) {
  const t = clamp01((x - e0) / (e1 - e0));
  return t * t * (3 - 2 * t);
}

// Atlas shyama ground — never let final RGB go below this.
// #0a0d1a = (10, 13, 26) in 0..255 → (0.039, 0.051, 0.102) in 0..1
export const SHYAMA = [10 / 255, 13 / 255, 26 / 255];

// ACES-like tone curve.  Compresses highlights smoothly and lifts
// shadows just enough to avoid a hard floor.  Input/output in 0..1.
function aces(x) {
  const a = 2.51, b = 0.03, c = 2.43, d = 0.59, e = 0.14;
  const y = (x * (a * x + b)) / (x * (c * x + d) + e);
  return y < 0 ? 0 : y > 1 ? 1 : y;
}

// Apply contrast around a 0.5 pivot, exposure scale, ACES tone-map, and
// shyama floor.  All channels in 0..1.
export function postProcess(r, g, b, contrast = 1.0, exposure = 1.0) {
  let R = r * exposure, G = g * exposure, B = b * exposure;
  R = 0.5 + (R - 0.5) * contrast;
  G = 0.5 + (G - 0.5) * contrast;
  B = 0.5 + (B - 0.5) * contrast;
  // v0.13 — tone-map highlights so dominant gestures don't blow out
  R = aces(R); G = aces(G); B = aces(B);
  if (R < SHYAMA[0]) R = SHYAMA[0];
  if (G < SHYAMA[1]) G = SHYAMA[1];
  if (B < SHYAMA[2]) B = SHYAMA[2];
  return [R, G, B];
}

// ── 9 rasa palettes ─────────────────────────────────────────────────
// Each maps the same field signals to a different bhāva.  Compositor
// can cycle these alongside cosmic / rohini / ashwini.

const _shanta = (f, i) => {
  // peace — pearl, silver, sky-blue
  const dens = f.density[i], coh = f.coherence[i], life = f.life[i];
  const moist = f.moisture[i], rig = f.rigidity[i];
  const r = 0.18 + 0.30 * coh + 0.35 * life + 0.20 * dens + 0.18 * rig;
  const g = 0.22 + 0.40 * coh + 0.45 * life + 0.20 * moist + 0.18 * rig;
  const b = 0.32 + 0.50 * coh + 0.45 * moist + 0.30 * life + 0.15 * rig;
  return [r, g, b];
};

const _shringara = (f, i) => {
  // love/erotic — rose, gold, warm flesh
  const dens = f.density[i], life = f.life[i], coh = f.coherence[i];
  const heat = f.heat[i], branch = f.branch_memory[i];
  const r = 0.20 + 0.65 * dens + 0.55 * life + 0.25 * heat + 0.30 * branch;
  const g = 0.10 + 0.40 * life + 0.30 * coh + 0.18 * heat + 0.15 * branch;
  const b = 0.15 + 0.35 * coh + 0.30 * life + 0.10 * branch;
  return [r, g, b];
};

const _vira = (f, i) => {
  // heroic — bronze, copper, deep orange
  const dens = f.density[i], heat = f.heat[i];
  const charge = f.charge[i], rig = f.rigidity[i];
  const branch = f.branch_memory[i];
  const r = 0.20 + 0.50 * dens + 0.70 * heat + 0.40 * Math.abs(charge) + 0.30 * branch;
  const g = 0.12 + 0.35 * dens + 0.40 * heat + 0.20 * Math.abs(charge) + 0.20 * branch;
  const b = 0.06 + 0.10 * dens + 0.10 * heat + 0.20 * rig;
  return [r, g, b];
};

const _raudra = (f, i) => {
  // wrath — crimson, black, sulfur
  const heat = f.heat[i], charge = f.charge[i], dens = f.density[i];
  const branch = f.branch_memory[i];
  const fil = clamp01(branch * 0.8 + Math.abs(charge) * 0.6);
  const r = 0.10 + 0.85 * heat + 0.75 * fil + 0.20 * dens;
  const g = 0.04 + 0.20 * heat + 0.35 * fil + 0.10 * dens;
  const b = 0.05 + 0.10 * heat + 0.45 * fil;
  return [r, g, b];
};

const _karuna = (f, i) => {
  // compassion — pale dawn-blue, peach, soft cyan
  const moist = f.moisture[i], coh = f.coherence[i], life = f.life[i];
  const dens = f.density[i];
  const r = 0.25 + 0.35 * dens + 0.30 * life + 0.20 * coh;
  const g = 0.30 + 0.30 * life + 0.45 * coh + 0.25 * moist;
  const b = 0.40 + 0.45 * coh + 0.40 * moist + 0.15 * life;
  return [r, g, b];
};

const _adbhuta = (f, i) => {
  // wonder — violet, opal, indigo
  const coh = f.coherence[i], life = f.life[i], dens = f.density[i];
  const charge = f.charge[i], moist = f.moisture[i];
  const ring = 0.5 + 0.5 * charge;
  const r = 0.20 + 0.45 * dens + 0.30 * ring + 0.30 * life;
  const g = 0.10 + 0.20 * coh + 0.30 * life + 0.15 * moist;
  const b = 0.30 + 0.55 * coh + 0.35 * ring + 0.40 * moist;
  return [r, g, b];
};

export const PALETTES = {
  rohini: (f, i, rel = {}) => {
    const heat = f.heat[i];
    const moist = f.moisture[i];
    const branch = f.branch_memory[i];
    const life = f.life[i];
    const dens = f.density[i];
    const coh = f.coherence[i];
    const charge = f.charge[i];
    const rig = f.rigidity[i];

    const base_r = 0.18 + 0.45 * dens + 0.30 * branch;
    const base_g = 0.12 + 0.35 * coh + 0.55 * life + 0.20 * branch;
    const base_b = 0.08 + 0.20 * moist + 0.10 * coh;
    const vein = smoothstep(0.15, 0.45, branch);

    const veinToRoot = rel.veinToRoot || 0;
    const rootToLightning = rel.rootToLightning || 0;
    const waterToFlesh = rel.waterToFlesh || 0;
    const mountainToBone = rel.mountainToBone || 0;

    const lightningGlow = rootToLightning * smoothstep(0.10, 0.35, branch + Math.abs(charge) * 0.5);
    const flesh = waterToFlesh * smoothstep(0.4, 0.8, dens) * (1 - smoothstep(0.1, 0.35, branch));
    const bone = mountainToBone * smoothstep(0.2, 0.6, rig);

    const r = base_r * 0.6 + (0.6 + 0.4 * veinToRoot) * vein + 0.10 * heat
              + 0.50 * lightningGlow + 0.45 * flesh + 0.35 * bone;
    const g = base_g * 0.7 + 0.7 * vein + 0.30 * lightningGlow + 0.15 * flesh + 0.30 * bone;
    const b = base_b * 0.5 + 0.25 * vein + 0.65 * lightningGlow + 0.30 * flesh + 0.40 * bone;
    return [r, g, b];
  },

  ashwini: (f, i, rel = {}) => {
    const heat = f.heat[i];
    const charge = f.charge[i];
    const branch = f.branch_memory[i];
    const dens = f.density[i];
    const coh = f.coherence[i];

    const fil = smoothstep(0.10, 0.45, branch + 0.5 * Math.abs(charge));
    const rootToLightning = rel.rootToLightning || 0;
    const fireToSmoke = rel.fireToSmoke || 0;
    const burst = rootToLightning * fil;
    const smoke = fireToSmoke * (1 - fil);

    const r = 0.05 + 0.55 * dens + 0.85 * fil + 0.20 * heat + 0.55 * burst + 0.15 * smoke;
    const g = 0.04 + 0.20 * coh + 0.85 * fil + 0.55 * burst + 0.10 * smoke;
    const b = 0.10 + 0.65 * coh + 0.85 * fil + 0.30 * Math.abs(charge) + 0.55 * burst + 0.30 * smoke;
    return [r, g, b];
  },

  cosmic: (f, i, rel = {}) => {
    const moist = f.moisture[i];
    const charge = f.charge[i];
    const life = f.life[i];
    const branch = f.branch_memory[i];
    const dens = f.density[i];
    const coh = f.coherence[i];
    const rig = f.rigidity[i];

    const ring = 0.5 + 0.5 * charge;
    const cloudToBreath = rel.cloudToBreath || 0;
    const flowerToEye = rel.flowerToEye || 0;
    const mountainToBone = rel.mountainToBone || 0;
    const rootToLightning = rel.rootToLightning || 0;

    const breath = cloudToBreath * (1 - smoothstep(0.3, 0.7, dens));
    const eye = flowerToEye * smoothstep(0.05, 0.25, life * coh);
    const bone = mountainToBone * smoothstep(0.2, 0.6, rig);
    const lightning = rootToLightning * smoothstep(0.08, 0.32, branch + Math.abs(charge) * 0.5);

    const r = 0.06 + 0.30 * ring + 0.60 * life + 0.25 * dens + 0.10 * rig
              + 0.15 * breath + 0.55 * eye + 0.40 * bone + 0.45 * lightning;
    const g = 0.05 + 0.25 * coh + 0.55 * life + 0.20 * branch
              + 0.30 * breath + 0.45 * eye + 0.40 * bone + 0.30 * lightning;
    const b = 0.10 + 0.45 * moist + 0.50 * coh + 0.35 * ring + 0.15 * rig
              + 0.55 * breath + 0.55 * eye + 0.45 * bone + 0.55 * lightning;
    return [r, g, b];
  },

  // ── 9 rasa palettes (delegate to local helpers above) ──
  shanta:    (f, i) => _shanta(f, i),
  shringara: (f, i) => _shringara(f, i),
  vira:      (f, i) => _vira(f, i),
  raudra:    (f, i) => _raudra(f, i),
  karuna:    (f, i) => _karuna(f, i),
  adbhuta:   (f, i) => _adbhuta(f, i),
};

// Debug grayscale rendering of a single field.
export function debugFieldRGB(f, name, i, range = "auto") {
  const v = f[name][i];
  let normalized;
  if (range === "bipolar") {
    normalized = clamp01((v + 1) * 0.5);
  } else if (typeof range === "number") {
    normalized = clamp01(v / range);
  } else {
    normalized = clamp01(v);
  }
  return [normalized, normalized, normalized];
}
