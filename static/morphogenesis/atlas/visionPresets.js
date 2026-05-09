// Vision presets — six oracle scenes for fullscreen Vision Mode.
// Each preset overrides a subset of {elements, sacred, phase, embodiment,
// bhasma_stage, quasicrystal, intent, gains, exposureBoost}. Empty fields
// are left untouched (so live engine state carries over).
//
// "current_field" is special: kind="atlas" tells the controller to fetch
// /field/morphogenesis instead of using a synthetic payload.
//
// All synthetic embodiments use lookup keys recognized by v0.6 passes:
//   body_region    → pulseMarma REGION_POS
//   asana          → helicalShear ASANA_TWIST
//   pranayama      → movementPhrase PRANAYAMA_PROFILE
//   dhatu          → dhatuMaterial DHATU_BIAS (D001..D007)
//   pattern/cycle  → pulseMarma envelope shaping

const DEFAULT_GAINS = {
  master: 1.0,
  bhasma: 1.0, dhatu: 1.0, pulseMarma: 1.0,
  helicalShear: 1.0, tensegrity: 1.0,
  movementPhrase: 1.0, quasicrystal: 1.0,
};

export const VISION_PRESETS = {
  current_field: {
    name: "Current Field",
    description: "live /field/morphogenesis",
    kind: "atlas",
    gains: { ...DEFAULT_GAINS, master: 1.15 },
    exposureBoost: 1.05,
  },

  cosmic_body_revelation: {
    name: "Cosmic Body Revelation",
    description: "all elements · revelation · bilateral · 11-fold",
    kind: "synthetic",
    elements: { water: 0.55, air: 0.50, fire: 0.45, earth: 0.55, wood: 0.55, ether: 0.85 },
    phase: "bloom",
    sacred: {
      masterStrength: 0.80, vastuStrength: 0.55,
      yantraType: "sri_yantra_lite", yantraStrength: 0.55,
      mandalaStrength: 0.55, mandalaRings: 5, mandalaGates: 4, mandalaInvert: false,
      phyllotaxy: { enabled: true, count: 60, scale: 5 },
    },
    intent: {
      intention: "revelation", phase: "bloom", symmetry: "bilateral",
      hiddenForm: "cosmic_body",
      transformationGoal: "river → vein → root",
      memory: 0.85, revelation: 0.90, drama: 0.55, void: 0.10, structure: 0.55,
    },
    embodiment: {
      body_region: "fascia_network", archetype: "cosmic_membrane",
      graha: "guru", dhatu: "D007",
      asana_that_loads: "Trikonasana",
      pranayama_that_loads: "Bhramari",
      marma_at_this_region: "Hridaya",
      animation_pattern: "wave_cascade", animation_cycle_ms: 6000,
    },
    bhasma_stage: {
      stage: "sattva_extraction",
      visual_operators: { coherence_rise: 1.30, light_drain: 0.96 },
      tithi_pos: 13, paksha: "Shukla",
    },
    quasicrystal: { active: true, fold: 11, strength: 0.60, phason_amplitude: 0.30 },
    gains: { ...DEFAULT_GAINS, master: 1.25, dhatu: 1.3, pulseMarma: 1.3,
             tensegrity: 1.3, movementPhrase: 1.3, quasicrystal: 1.5 },
    exposureBoost: 1.10,
  },

  twisting_flame_spine: {
    name: "Twisting Flame Spine",
    description: "thoracic helix · puta agni · Kapalabhati",
    kind: "synthetic",
    elements: { water: 0.30, air: 0.85, fire: 0.85, earth: 0.20, wood: 0.55, ether: 0.55 },
    intent: {
      intention: "discharge", phase: "ignition", symmetry: "spiral",
      hiddenForm: "spine", transformationGoal: "fire → twist → release",
      memory: 0.55, revelation: 0.60, drama: 0.85, void: 0.10, structure: 0.45,
    },
    embodiment: {
      body_region: "thoracic_spine", archetype: "spinal_helix",
      graha: "kuja", dhatu: "D003",
      asana_that_loads: "Matsyendrasana",
      pranayama_that_loads: "Kapalabhati",
      marma_at_this_region: "Hridaya",
      animation_pattern: "spiral_pulse", animation_cycle_ms: 1800,
    },
    bhasma_stage: {
      stage: "puta_agni",
      visual_operators: { heat_spike: 1.50, density_burn: 0.88, life_drain: 0.85 },
      tithi_pos: 10, paksha: "Shukla",
    },
    quasicrystal: { active: false, fold: 7, strength: 0, phason_amplitude: 0.30 },
    gains: { ...DEFAULT_GAINS, master: 1.30, helicalShear: 1.7, tensegrity: 1.4,
             bhasma: 1.4, pulseMarma: 1.4, movementPhrase: 1.4, quasicrystal: 0.5 },
    exposureBoost: 1.15,
  },

  soma_bloom_body: {
    name: "Soma Bloom Body",
    description: "water · ether · wood · phyllotaxy · Bhramari",
    kind: "synthetic",
    elements: { water: 0.85, air: 0.40, fire: 0.20, earth: 0.40, wood: 0.85, ether: 0.85 },
    phase: "bloom",
    sacred: {
      masterStrength: 0.75, vastuStrength: 0.55,
      yantraType: "lotus_8", yantraStrength: 0.55,
      mandalaStrength: 0.50, mandalaRings: 4, mandalaGates: 0, mandalaInvert: false,
      phyllotaxy: { enabled: true, count: 80, scale: 5 },
    },
    intent: {
      intention: "bloom", phase: "bloom", symmetry: "bilateral",
      hiddenForm: "flower", transformationGoal: "water → vein → flower",
      memory: 0.55, revelation: 0.50, drama: 0.30, void: 0.05, structure: 0.50,
    },
    embodiment: {
      body_region: "heart_muscle", archetype: "fluid_pump",
      graha: "chandra", dhatu: "D001",
      asana_that_loads: "Bhujangasana",
      pranayama_that_loads: "Bhramari",
      marma_at_this_region: "Hridaya",
      animation_pattern: "expansion_contraction", animation_cycle_ms: 5500,
    },
    bhasma_stage: {
      stage: "amritikarana",
      visual_operators: { coherence_rise: 1.25, moisture_push: 1.20, charge_ramp: 1.10 },
      tithi_pos: 4, paksha: "Krishna",
    },
    quasicrystal: { active: false, fold: 8, strength: 0, phason_amplitude: 0.25 },
    gains: { ...DEFAULT_GAINS, master: 1.20, dhatu: 1.5, pulseMarma: 1.5,
             movementPhrase: 1.5, tensegrity: 1.2, helicalShear: 0.8, quasicrystal: 0.7 },
    exposureBoost: 1.10,
  },

  quasicrystal_bone_temple: {
    name: "Quasicrystal Bone Temple",
    description: "earth · ether · 11-fold · Ujjayi",
    kind: "synthetic",
    elements: { water: 0.30, air: 0.30, fire: 0.40, earth: 0.85, wood: 0.30, ether: 0.85 },
    sacred: {
      masterStrength: 0.80, vastuStrength: 0.65,
      yantraType: "square", yantraStrength: 0.65,
      mandalaStrength: 0.60, mandalaRings: 6, mandalaGates: 4, mandalaInvert: false,
      phyllotaxy: { enabled: false, count: 48, scale: 4 },
    },
    intent: {
      intention: "fossilization", phase: "memory", symmetry: "radial",
      hiddenForm: "lattice", transformationGoal: "soft → mineral → temple",
      memory: 0.70, revelation: 0.65, drama: 0.40, void: 0.15, structure: 0.85,
    },
    embodiment: {
      body_region: "skull_vault", archetype: "vault_dome",
      graha: "shani", dhatu: "D005",
      asana_that_loads: "Sirsasana",
      pranayama_that_loads: "Ujjayi",
      marma_at_this_region: "Adhipati",
      animation_pattern: "micro_oscillation", animation_cycle_ms: 9200,
    },
    bhasma_stage: {
      stage: "stabilization",
      visual_operators: { rigidity_boost: 1.50, density_lock: 1.25 },
      tithi_pos: 14, paksha: "Shukla",
    },
    quasicrystal: { active: true, fold: 11, strength: 0.85, phason_amplitude: 0.35 },
    gains: { ...DEFAULT_GAINS, master: 1.20, quasicrystal: 1.7, tensegrity: 1.6,
             dhatu: 1.4, bhasma: 1.2, helicalShear: 0.5,
             pulseMarma: 0.9, movementPhrase: 0.9 },
    exposureBoost: 1.05,
  },

  storm_marma_discharge: {
    name: "Storm Marma Discharge",
    description: "fire · air · lightning · Kapalabhati",
    kind: "synthetic",
    elements: { water: 0.20, air: 0.85, fire: 0.85, earth: 0.20, wood: 0.45, ether: 0.55 },
    phase: "ignition",
    intent: {
      intention: "discharge", phase: "ignition", symmetry: "bilateral",
      hiddenForm: "lightning", transformationGoal: "charge → fork → ground",
      memory: 0.85, revelation: 0.55, drama: 0.95, void: 0.05, structure: 0.30,
    },
    embodiment: {
      body_region: "heart_muscle", archetype: "fluid_pump",
      graha: "kuja", dhatu: "D006",
      asana_that_loads: "Garudasana",
      pranayama_that_loads: "Kapalabhati",
      marma_at_this_region: "Hridaya",
      animation_pattern: "lightning_flicker", animation_cycle_ms: 1100,
    },
    bhasma_stage: {
      stage: "puta_agni",
      visual_operators: { heat_spike: 1.55, density_burn: 0.85, life_drain: 0.80 },
      tithi_pos: 11, paksha: "Shukla",
    },
    quasicrystal: { active: false, fold: 11, strength: 0, phason_amplitude: 0.30 },
    gains: { ...DEFAULT_GAINS, master: 1.30, pulseMarma: 1.9, helicalShear: 1.5,
             bhasma: 1.4, movementPhrase: 1.6, tensegrity: 1.0, quasicrystal: 0.5 },
    exposureBoost: 1.20,
  },
};

export const VISION_PRESET_KEYS = Object.keys(VISION_PRESETS);
export const VISION_NUM_TO_KEY = {
  "1": "current_field",
  "2": "cosmic_body_revelation",
  "3": "twisting_flame_spine",
  "4": "soma_bloom_body",
  "5": "quasicrystal_bone_temple",
  "6": "storm_marma_discharge",
};
