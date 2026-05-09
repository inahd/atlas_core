// Expression modes — a mode is a complete artistic configuration:
// elements + palette + energy/decay/contrast/exposure + grammar bias +
// default overlay set + seed.
//
// Selecting a mode applies the entire bundle.  This is the move from
// "soup that decays to black" → "a series of distinct expressions."

export const MODES = {
  capillary_bloom: {
    name: "Capillary Bloom",
    description: "watercolor — water + life + ether",
    elements: { water: 0.85, air: 0.45, fire: 0.10, earth: 0.20, wood: 0.55, ether: 0.75 },
    palette: "cosmic",
    energy:    0.55,
    replenish: 0.55,
    decay:     0.92,
    contrast:  1.10,
    exposure:  1.05,
    grammar: { complexity: 0.45, structure: 0.35, symmetryHint: "bilateral" },
    overlays: {
      streamlines: false,
      branch_filaments: false,
      coherence_rings: true,
      discharge_paths: false,
      nodes: true,
      void_mask: false,
      history: true,
    },
    seed: 7321,
  },

  filament_memory: {
    name: "Filament Memory",
    description: "branch traces persisting in shyama",
    elements: { water: 0.40, air: 0.35, fire: 0.15, earth: 0.55, wood: 0.85, ether: 0.55 },
    palette: "rohini",
    energy:    0.45,
    replenish: 0.30,
    decay:     0.97,
    contrast:  1.20,
    exposure:  1.00,
    grammar: { complexity: 0.65, structure: 0.55, symmetryHint: "spiral" },
    overlays: {
      streamlines: false,
      branch_filaments: true,
      coherence_rings: false,
      discharge_paths: false,
      nodes: false,
      void_mask: true,
      history: true,
    },
    seed: 4271,
  },

  interference_body: {
    name: "Interference Body",
    description: "coherence rings on bilateral spiral substrate",
    elements: { water: 0.55, air: 0.50, fire: 0.30, earth: 0.40, wood: 0.40, ether: 0.95 },
    palette: "cosmic",
    energy:    0.55,
    replenish: 0.50,
    decay:     0.94,
    contrast:  1.05,
    exposure:  1.00,
    grammar: { complexity: 0.50, structure: 0.65, symmetryHint: "bilateral" },
    overlays: {
      streamlines: false,
      branch_filaments: false,
      coherence_rings: true,
      discharge_paths: false,
      nodes: true,
      void_mask: false,
      history: true,
    },
    seed: 9931,
  },

  crystal_pressure: {
    name: "Crystal Pressure",
    description: "rigid radial faceting under earth+fire",
    elements: { water: 0.20, air: 0.25, fire: 0.55, earth: 0.85, wood: 0.30, ether: 0.45 },
    palette: "rohini",
    energy:    0.50,
    replenish: 0.45,
    decay:     0.95,
    contrast:  1.25,
    exposure:  1.00,
    grammar: { complexity: 0.40, structure: 0.80, symmetryHint: "radial" },
    overlays: {
      streamlines: false,
      branch_filaments: false,
      coherence_rings: false,
      discharge_paths: false,
      nodes: true,
      void_mask: false,
      history: false,
    },
    seed: 1532,
  },

  storm_discharge: {
    name: "Storm Discharge",
    description: "fire + air filamentary lightning",
    elements: { water: 0.30, air: 0.85, fire: 0.85, earth: 0.20, wood: 0.55, ether: 0.50 },
    palette: "ashwini",
    energy:    0.65,
    replenish: 0.40,
    decay:     0.93,
    contrast:  1.30,
    exposure:  1.10,
    grammar: { complexity: 0.70, structure: 0.30, symmetryHint: "none" },
    overlays: {
      streamlines: false,
      branch_filaments: true,
      coherence_rings: false,
      discharge_paths: true,
      nodes: false,
      void_mask: false,
      history: true,
    },
    seed: 1827,
  },

  rohini_soma: {
    name: "Rohini Soma",
    description: "earth + wood + water lunar fertility growth",
    elements: { water: 0.65, air: 0.30, fire: 0.20, earth: 0.65, wood: 0.85, ether: 0.45 },
    palette: "rohini",
    energy:    0.55,
    replenish: 0.55,
    decay:     0.95,
    contrast:  1.15,
    exposure:  1.00,
    grammar: { complexity: 0.55, structure: 0.50, symmetryHint: "bilateral" },
    overlays: {
      streamlines: false,
      branch_filaments: true,
      coherence_rings: false,
      discharge_paths: false,
      nodes: false,
      void_mask: false,
      history: true,
    },
    seed: 4271,
  },

  // ── v0.5: Sacred-spatial modes ─────────────────────────────────
  // Each mode bundles vastu/yantra/mandala/phyllotaxy biases beyond
  // the v0.4 element/energy/grammar configuration.

  rohini_soma_bloom: {
    name: "Rohini Soma Bloom",
    description: "lunar fertility · bindu yantra · 3-ring mandala",
    elements: { water: 0.70, air: 0.30, fire: 0.20, earth: 0.65, wood: 0.85, ether: 0.50 },
    palette: "rohini",
    energy: 0.55, replenish: 0.55, decay: 0.95, contrast: 1.15, exposure: 1.00,
    grammar: { complexity: 0.55, structure: 0.55, symmetryHint: "bilateral" },
    sacred: {
      masterStrength: 0.7,
      vastuStrength: 0.6,
      yantraType: "bindu",
      yantraStrength: 0.7,
      mandalaStrength: 0.55,
      mandalaRings: 3,
      mandalaGates: 0,
      mandalaInvert: false,
      phyllotaxy: { enabled: false },
    },
    overlays: {
      streamlines: false, branch_filaments: true, coherence_rings: true,
      discharge_paths: false, nodes: false, void_mask: false, history: true,
    },
    seed: 4271,
  },

  ashwini_twin_discharge: {
    name: "Ashwini Twin Discharge",
    description: "fire + air · shatkona · twin lightning",
    elements: { water: 0.30, air: 0.85, fire: 0.85, earth: 0.20, wood: 0.55, ether: 0.55 },
    palette: "ashwini",
    energy: 0.65, replenish: 0.45, decay: 0.93, contrast: 1.30, exposure: 1.10,
    grammar: { complexity: 0.65, structure: 0.40, symmetryHint: "bilateral" },
    sacred: {
      masterStrength: 0.7,
      vastuStrength: 0.7,
      yantraType: "shatkona",
      yantraStrength: 0.6,
      mandalaStrength: 0,
      mandalaRings: 0,
      mandalaGates: 0,
      mandalaInvert: false,
      phyllotaxy: { enabled: false },
    },
    overlays: {
      streamlines: false, branch_filaments: true, coherence_rings: false,
      discharge_paths: true, nodes: false, void_mask: false, history: true,
    },
    seed: 1827,
  },

  mula_root_inversion: {
    name: "Mula Root Inversion",
    description: "earth + ether · descending spiral · void center",
    elements: { water: 0.40, air: 0.20, fire: 0.25, earth: 0.85, wood: 0.55, ether: 0.65 },
    palette: "rohini",
    energy: 0.50, replenish: 0.50, decay: 0.96, contrast: 1.20, exposure: 1.00,
    grammar: { complexity: 0.55, structure: 0.55, symmetryHint: "spiral" },
    sacred: {
      masterStrength: 0.7,
      vastuStrength: 0.65,
      yantraType: "triangle_down",
      yantraStrength: 0.55,
      mandalaStrength: 0.6,
      mandalaRings: 4,
      mandalaGates: 0,
      mandalaInvert: true,         // outer→inner reversal: roots descend
      phyllotaxy: { enabled: false },
    },
    overlays: {
      streamlines: false, branch_filaments: true, coherence_rings: false,
      discharge_paths: false, nodes: false, void_mask: true, history: true,
    },
    seed: 5821,
  },

  swati_wind_seed: {
    name: "Swati Wind Seed",
    description: "air + ether · golden-angle dispersal · circle yantra",
    elements: { water: 0.35, air: 0.85, fire: 0.20, earth: 0.30, wood: 0.40, ether: 0.85 },
    palette: "cosmic",
    energy: 0.60, replenish: 0.55, decay: 0.94, contrast: 1.15, exposure: 1.05,
    grammar: { complexity: 0.40, structure: 0.30, symmetryHint: "none" },
    sacred: {
      masterStrength: 0.7,
      vastuStrength: 0.65,           // strong NW air
      yantraType: "circle",
      yantraStrength: 0.5,
      mandalaStrength: 0,
      mandalaRings: 0,
      mandalaGates: 0,
      mandalaInvert: false,
      phyllotaxy: { enabled: true, count: 80, scale: 4 },
    },
    overlays: {
      streamlines: true, branch_filaments: false, coherence_rings: false,
      discharge_paths: false, nodes: true, void_mask: false, history: true,
    },
    seed: 3094,
  },

  chitra_gem_lattice: {
    name: "Chitra Gem Lattice",
    description: "earth + ether · square + 6-ring mandala with cardinal gates",
    elements: { water: 0.40, air: 0.30, fire: 0.40, earth: 0.80, wood: 0.30, ether: 0.85 },
    palette: "cosmic",
    energy: 0.55, replenish: 0.55, decay: 0.96, contrast: 1.20, exposure: 1.00,
    grammar: { complexity: 0.45, structure: 0.85, symmetryHint: "radial" },
    sacred: {
      masterStrength: 0.75,
      vastuStrength: 0.65,
      yantraType: "square",
      yantraStrength: 0.6,
      mandalaStrength: 0.65,
      mandalaRings: 6,
      mandalaGates: 4,             // 4 cardinal gates
      mandalaInvert: false,
      phyllotaxy: { enabled: false },
    },
    overlays: {
      streamlines: false, branch_filaments: false, coherence_rings: true,
      discharge_paths: false, nodes: true, void_mask: false, history: true,
    },
    seed: 1532,
  },

  cosmic_body_mandala: {
    name: "Cosmic Body Mandala",
    description: "all elements · 9-petal lotus + 5-ring + phyllotaxy",
    elements: { water: 0.55, air: 0.50, fire: 0.45, earth: 0.55, wood: 0.55, ether: 0.85 },
    palette: "cosmic",
    energy: 0.60, replenish: 0.55, decay: 0.95, contrast: 1.10, exposure: 1.00,
    grammar: { complexity: 0.60, structure: 0.55, symmetryHint: "radial" },
    sacred: {
      masterStrength: 0.75,
      vastuStrength: 0.55,
      yantraType: "sri_yantra_lite",   // composite: bindu + circle + shatkona + lotus
      yantraStrength: 0.55,
      mandalaStrength: 0.55,
      mandalaRings: 5,
      mandalaGates: 4,
      mandalaInvert: false,
      phyllotaxy: { enabled: true, count: 48, scale: 5 },
    },
    overlays: {
      streamlines: false, branch_filaments: true, coherence_rings: true,
      discharge_paths: false, nodes: true, void_mask: false, history: true,
    },
    seed: 9931,
  },
};

export const MODE_KEYS = Object.keys(MODES);
