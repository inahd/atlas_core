// Named presets — element-slider configurations + render palette hints.
// Each preset is a structural choice about which elemental dynamics
// dominate. The visual identity emerges from the field interactions,
// not from any explicit drawing.

export const PRESETS = {
  rohini_growth: {
    name: "Rohini Growth Field",
    description:
      "Earth and wood dominant. Slow diffusion, strong branch memory. " +
      "Fronts ramify and persist — emergent root or vein architecture.",
    seed: 4271,
    elements: {
      water: 0.45,
      air: 0.20,
      fire: 0.15,
      earth: 0.85,
      wood: 0.90,
      ether: 0.30,
    },
    palette: "rohini",
  },
  ashwini_lightning: {
    name: "Ashwini Lightning Root",
    description:
      "Fire and air dominant. High advection, sharp fronts, high charge. " +
      "Rapid branching with bright filamentary discharge.",
    seed: 1827,
    elements: {
      water: 0.20,
      air: 0.85,
      fire: 0.85,
      earth: 0.15,
      wood: 0.55,
      ether: 0.50,
    },
    palette: "ashwini",
  },
  cosmic_body: {
    name: "Cosmic Body Field",
    description:
      "Ether dominant, all elements present. Slow breath of interference, " +
      "cellular partition, gentle ramification. The whole field as one organism.",
    seed: 9931,
    elements: {
      water: 0.55,
      air: 0.50,
      fire: 0.40,
      earth: 0.50,
      wood: 0.55,
      ether: 0.95,
    },
    palette: "cosmic",
  },
  air_water_flesh: {
    name: "Air–Water–Flesh",
    description:
      "Soft membranes drifting on wind. High water + air + ether, low fire " +
      "and earth. Translucent surfaces appear and dissolve as breath.",
    seed: 5503,
    elements: {
      water: 0.80,
      air: 0.70,
      fire: 0.10,
      earth: 0.15,
      wood: 0.25,
      ether: 0.75,
    },
    palette: "cosmic",
  },
};
