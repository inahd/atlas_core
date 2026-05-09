// Beginner-facing styles — 8 visual moods.  Each style is a base
// composition (elements + palette + sacred bias) plus per-event tuning.
// Cycling styles re-skins the same gestures with a different feel
// without changing how gestures work.

export const STYLES = {
  soma_watercolor: {
    name: "Soma Watercolor",
    description: "wet · blooming · gentle",
    palette: "shanta",
    elements: { water: 0.85, air: 0.45, fire: 0.10, earth: 0.30, wood: 0.65, ether: 0.65 },
    energy: 0.55, replenish: 0.60, decay: 0.95, contrast: 1.05, exposure: 1.05,
    sacred: { masterStrength: 0.55, vastuStrength: 0.45, yantraType: "bindu",
              yantraStrength: 0.45, mandalaStrength: 0.35,
              mandalaRings: 3, mandalaGates: 0,
              phyllotaxy: { enabled: false } },
    eventBoosts: {
      bloom:     { intensityMul: 1.4, radiusMul: 1.3 },
      flow:      { intensityMul: 1.3 },
      reveal:    { intensityMul: 1.4 },
      strike:    { intensityMul: 0.5 },
      lightning: { intensityMul: 0.4 },
    },
  },

  storm_nerve: {
    name: "Storm Nerve",
    description: "fire · charge · forking",
    palette: "ashwini",
    elements: { water: 0.20, air: 0.85, fire: 0.85, earth: 0.20, wood: 0.45, ether: 0.55 },
    energy: 0.65, replenish: 0.45, decay: 0.93, contrast: 1.30, exposure: 1.10,
    sacred: { masterStrength: 0.50, vastuStrength: 0.55, yantraType: "shatkona",
              yantraStrength: 0.55, mandalaStrength: 0.0,
              mandalaRings: 0, mandalaGates: 0,
              phyllotaxy: { enabled: false } },
    eventBoosts: {
      strike:    { intensityMul: 1.6 },
      lightning: { intensityMul: 1.7, radiusMul: 1.1 },
      bloom:     { intensityMul: 0.8 },
      flow:      { intensityMul: 0.9 },
      mandala:   { intensityMul: 0.7 },
    },
  },

  crystal_temple: {
    name: "Crystal Temple",
    description: "earth · bone · radial",
    palette: "raudra",
    elements: { water: 0.20, air: 0.30, fire: 0.45, earth: 0.85, wood: 0.30, ether: 0.85 },
    energy: 0.55, replenish: 0.55, decay: 0.96, contrast: 1.20, exposure: 1.00,
    sacred: { masterStrength: 0.75, vastuStrength: 0.65, yantraType: "square",
              yantraStrength: 0.65, mandalaStrength: 0.60,
              mandalaRings: 6, mandalaGates: 4,
              phyllotaxy: { enabled: false } },
    eventBoosts: {
      mandala:   { intensityMul: 1.5, radiusMul: 1.2 },
      reveal:    { intensityMul: 1.4 },
      bloom:     { intensityMul: 1.0 },
      twist:     { intensityMul: 0.7 },
      flow:      { intensityMul: 0.7 },
      lightning: { intensityMul: 0.6 },
    },
  },

  root_forest: {
    name: "Root Forest",
    description: "wood · earth · veining",
    palette: "rohini",
    elements: { water: 0.45, air: 0.30, fire: 0.20, earth: 0.65, wood: 0.85, ether: 0.45 },
    energy: 0.50, replenish: 0.45, decay: 0.97, contrast: 1.20, exposure: 1.00,
    sacred: { masterStrength: 0.45, vastuStrength: 0.50, yantraType: "lotus_8",
              yantraStrength: 0.40, mandalaStrength: 0.30,
              mandalaRings: 3, mandalaGates: 0,
              phyllotaxy: { enabled: true, count: 64, scale: 4 } },
    eventBoosts: {
      flow:      { intensityMul: 1.4 },
      twist:     { intensityMul: 1.3 },
      bloom:     { intensityMul: 1.2 },
      mandala:   { intensityMul: 1.0 },
      lightning: { intensityMul: 0.5 },
    },
  },

  cosmic_body: {
    name: "Cosmic Body",
    description: "all elements · symmetry · pearl",
    palette: "cosmic",
    elements: { water: 0.55, air: 0.55, fire: 0.45, earth: 0.55, wood: 0.55, ether: 0.85 },
    energy: 0.60, replenish: 0.55, decay: 0.95, contrast: 1.10, exposure: 1.00,
    sacred: { masterStrength: 0.75, vastuStrength: 0.55, yantraType: "sri_yantra_lite",
              yantraStrength: 0.55, mandalaStrength: 0.55,
              mandalaRings: 5, mandalaGates: 4,
              phyllotaxy: { enabled: true, count: 48, scale: 5 } },
    eventBoosts: {
      reveal:    { intensityMul: 1.4 },
      mandala:   { intensityMul: 1.3 },
      bloom:     { intensityMul: 1.1 },
      twist:     { intensityMul: 1.0 },
      flow:      { intensityMul: 1.0 },
    },
  },

  smoke_lightning: {
    name: "Smoke Lightning",
    description: "air · ether · bright shock",
    palette: "adbhuta",
    elements: { water: 0.30, air: 0.85, fire: 0.55, earth: 0.20, wood: 0.30, ether: 0.85 },
    energy: 0.60, replenish: 0.50, decay: 0.93, contrast: 1.20, exposure: 1.10,
    sacred: { masterStrength: 0.55, vastuStrength: 0.55, yantraType: "circle",
              yantraStrength: 0.45, mandalaStrength: 0.30,
              mandalaRings: 2, mandalaGates: 0,
              phyllotaxy: { enabled: false } },
    eventBoosts: {
      lightning: { intensityMul: 1.6 },
      strike:    { intensityMul: 1.4 },
      reveal:    { intensityMul: 1.2 },
      flow:      { intensityMul: 1.1 },
      bloom:     { intensityMul: 0.7 },
    },
  },

  flower_eye: {
    name: "Flower Eye",
    description: "water · wood · ether · bloom symmetry",
    palette: "shringara",
    elements: { water: 0.65, air: 0.40, fire: 0.20, earth: 0.40, wood: 0.85, ether: 0.85 },
    energy: 0.55, replenish: 0.55, decay: 0.96, contrast: 1.10, exposure: 1.00,
    sacred: { masterStrength: 0.70, vastuStrength: 0.55, yantraType: "lotus_12",
              yantraStrength: 0.55, mandalaStrength: 0.45,
              mandalaRings: 4, mandalaGates: 0,
              phyllotaxy: { enabled: true, count: 80, scale: 5 } },
    eventBoosts: {
      bloom:     { intensityMul: 1.4 },
      mandala:   { intensityMul: 1.4, radiusMul: 1.1 },
      reveal:    { intensityMul: 1.3 },
      flow:      { intensityMul: 1.0 },
      lightning: { intensityMul: 0.5 },
    },
  },

  ash_field: {
    name: "Ash Field",
    description: "earth · ether · dim memory",
    palette: "karuna",
    elements: { water: 0.30, air: 0.40, fire: 0.30, earth: 0.65, wood: 0.30, ether: 0.65 },
    energy: 0.45, replenish: 0.40, decay: 0.97, contrast: 1.05, exposure: 0.95,
    sacred: { masterStrength: 0.60, vastuStrength: 0.55, yantraType: "triangle_down",
              yantraStrength: 0.50, mandalaStrength: 0.55,
              mandalaRings: 4, mandalaGates: 0, mandalaInvert: true,
              phyllotaxy: { enabled: false } },
    eventBoosts: {
      void_click: { intensityMul: 1.4 },
      void_drag:  { intensityMul: 1.3 },
      reveal:     { intensityMul: 1.2 },
      bloom:      { intensityMul: 0.8 },
      strike:     { intensityMul: 0.7 },
      lightning:  { intensityMul: 0.6 },
    },
  },
};

export const STYLE_KEYS = Object.keys(STYLES);
