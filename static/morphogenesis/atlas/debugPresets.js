// v0.7 debug presets — six named scenes that bundle a base mode with a
// synthetic embodiment + bhasma + quasicrystal payload and a gain matrix.
//
// "today_field" is the special live-Atlas preset: it tells main.js to
// fetch /field/morphogenesis instead of using a synthetic payload.
//
// Each synthetic embodiment must use field values that the passes
// recognize: body_region (in pulseMarma REGION_POS), asana_that_loads
// (in helicalShear ASANA_TWIST), pranayama_that_loads (in movementPhrase
// PRANAYAMA_PROFILE), dhatu (D001..D007), animation_pattern + cycle_ms.

const DEFAULT_GAINS = {
  master: 1.0,
  bhasma: 1.0, dhatu: 1.0, pulseMarma: 1.0,
  helicalShear: 1.0, tensegrity: 1.0,
  movementPhrase: 1.0, quasicrystal: 1.0,
};

export const DEBUG_PRESETS = {
  today_field: {
    name: "Today Field",
    description: "live Atlas /field/morphogenesis bundle",
    kind: "atlas",
    gains: { ...DEFAULT_GAINS },
  },

  twisting_flame_spine: {
    name: "Twisting Flame Spine",
    description: "thoracic helix · puta_agni · Bhastrika fire",
    kind: "synthetic",
    mode: "storm_discharge",
    embodiment: {
      body_region: "thoracic_spine",
      archetype: "spinal_helix",
      graha: "kuja",
      dhatu: "D003",
      mathematical_equation: "twist_torque",
      render_geometry: "helical_column",
      asana_that_loads: "Matsyendrasana",
      pranayama_that_loads: "Bhastrika",
      marma_at_this_region: "Hridaya",
      color_primary: "#d97a5a",
      color_secondary: "#d3a76e",
      animation_pattern: "spiral_pulse",
      animation_cycle_ms: 2200,
    },
    bhasma_stage: {
      stage: "puta_agni",
      material_action: "puta agni — calcination, the fire-pass",
      visual_operators: { heat_spike: 1.45, density_burn: 0.92, life_drain: 0.85 },
      tithi_pos: 10, paksha: "Shukla",
    },
    quasicrystal: { active: false, fold: 11, strength: 0, phason_amplitude: 0.3 },
    gains: { ...DEFAULT_GAINS, helicalShear: 1.6, tensegrity: 1.3, bhasma: 1.3, movementPhrase: 1.2 },
  },

  soma_bloom_body: {
    name: "Soma Bloom Body",
    description: "heart muscle · amritikarana · Bhramari",
    kind: "synthetic",
    mode: "rohini_soma_bloom",
    embodiment: {
      body_region: "heart_muscle",
      archetype: "fluid_pump",
      graha: "chandra",
      dhatu: "D002",
      mathematical_equation: "lub_dub_circulation",
      render_geometry: "pulsing_chamber",
      asana_that_loads: "Bhujangasana",
      pranayama_that_loads: "Bhramari",
      marma_at_this_region: "Hridaya",
      color_primary: "#a3b569",
      color_secondary: "#d3a76e",
      animation_pattern: "expansion_contraction",
      animation_cycle_ms: 5500,
    },
    bhasma_stage: {
      stage: "amritikarana",
      material_action: "amritikarana — ambrosial saturation",
      visual_operators: { coherence_rise: 1.20, moisture_push: 1.15, charge_ramp: 1.10 },
      tithi_pos: 4, paksha: "Krishna",
    },
    quasicrystal: { active: false, fold: 8, strength: 0, phason_amplitude: 0.25 },
    gains: { ...DEFAULT_GAINS, pulseMarma: 1.5, movementPhrase: 1.4, dhatu: 1.3 },
  },

  quasicrystal_bone_temple: {
    name: "Quasicrystal Bone Temple",
    description: "skull vault · stabilization · 11-fold aperiodic",
    kind: "synthetic",
    mode: "chitra_gem_lattice",
    embodiment: {
      body_region: "skull_vault",
      archetype: "vault_dome",
      graha: "shani",
      dhatu: "D005",
      mathematical_equation: "geodesic_dome",
      render_geometry: "stacked_tensegrity",
      asana_that_loads: "Sirsasana",
      pranayama_that_loads: "Ujjayi",
      marma_at_this_region: "Adhipati",
      color_primary: "#9c8ad3",
      color_secondary: "#445566",
      animation_pattern: "micro_oscillation",
      animation_cycle_ms: 9200,
    },
    bhasma_stage: {
      stage: "stabilization",
      material_action: "stabilization — settled lattice",
      visual_operators: { rigidity_boost: 1.45, density_lock: 1.2 },
      tithi_pos: 14, paksha: "Shukla",
    },
    quasicrystal: { active: true, fold: 11, strength: 0.8, phason_amplitude: 0.35 },
    gains: { ...DEFAULT_GAINS, quasicrystal: 1.5, tensegrity: 1.4, dhatu: 1.3, helicalShear: 0.5 },
  },

  mula_root_inversion_dbg: {
    name: "Mula Root Inversion",
    description: "pelvic basin · dormant_seed · 7-fold inversion",
    kind: "synthetic",
    mode: "mula_root_inversion",
    embodiment: {
      body_region: "pelvis",
      archetype: "cradle_basin",
      graha: "shani",
      dhatu: "D005",
      mathematical_equation: "inverted_dome",
      render_geometry: "stacked_tensegrity",
      asana_that_loads: "Halasana",
      pranayama_that_loads: "Kevala Kumbhaka",
      marma_at_this_region: "Guda",
      color_primary: "#445566",
      color_secondary: "#9c8ad3",
      animation_pattern: "rooted_breath",
      animation_cycle_ms: 8800,
    },
    bhasma_stage: {
      stage: "dormant_seed",
      material_action: "dormant seed — sealed potential",
      visual_operators: { memory_lock: 0.99, density_lock: 1.15, rigidity_boost: 1.3 },
      tithi_pos: 7, paksha: "Krishna",
    },
    quasicrystal: { active: true, fold: 7, strength: 0.5, phason_amplitude: 0.25 },
    gains: { ...DEFAULT_GAINS, tensegrity: 1.5, movementPhrase: 1.2, dhatu: 1.2, quasicrystal: 1.2 },
  },

  storm_marma_discharge: {
    name: "Storm Marma Discharge",
    description: "heart marma · puta_agni · Kapalabhati staccato",
    kind: "synthetic",
    mode: "ashwini_twin_discharge",
    embodiment: {
      body_region: "heart_muscle",
      archetype: "fluid_pump",
      graha: "kuja",
      dhatu: "D006",
      mathematical_equation: "discharge_ring",
      render_geometry: "pulsing_chamber",
      asana_that_loads: "Garudasana",
      pranayama_that_loads: "Kapalabhati",
      marma_at_this_region: "Hridaya",
      color_primary: "#d97a5a",
      color_secondary: "#d36ea7",
      animation_pattern: "lightning_flicker",
      animation_cycle_ms: 1100,
    },
    bhasma_stage: {
      stage: "puta_agni",
      material_action: "puta agni — calcination, the fire-pass",
      visual_operators: { heat_spike: 1.5, density_burn: 0.88, life_drain: 0.80 },
      tithi_pos: 11, paksha: "Shukla",
    },
    quasicrystal: { active: false, fold: 11, strength: 0, phason_amplitude: 0.3 },
    gains: { ...DEFAULT_GAINS, pulseMarma: 1.8, movementPhrase: 1.5, helicalShear: 1.4, bhasma: 1.3 },
  },
};

export const DEBUG_PRESET_KEYS = Object.keys(DEBUG_PRESETS);
export { DEFAULT_GAINS };
