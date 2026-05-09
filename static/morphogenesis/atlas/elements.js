// Element → pass-rate binding.
// The 6 element sliders (water, air, fire, earth, wood, ether) drive the
// rate constants of the simulation passes. The mapping is designed so that
// each element manifests in a recognisable behaviour:
//
//   water  → moisture diffusion + general fluid coupling (advection scale)
//   air    → velocity strength (curl flow), advection dt
//   fire   → reaction-diffusion feed/kill toward branching, heat coupling
//   earth  → rigidity accumulation (Voronoi imprint), low diffusion
//   wood   → branch-memory accumulation (front-tracing), life growth
//   ether  → interference rings amplitude + density coupling
//
// All sliders are 0..1. The rate functions return a parameter pack consumed
// by the pass functions. Adjusting these mappings changes the visual style
// without changing the simulation algorithms themselves.

export function paramsFromElements(e) {
  const water = e.water ?? 0.5;
  const air = e.air ?? 0.5;
  const fire = e.fire ?? 0.5;
  const earth = e.earth ?? 0.5;
  const wood = e.wood ?? 0.5;
  const ether = e.ether ?? 0.5;

  return {
    diffusion: {
      moisture: 0.18 * water,
      heat: 0.10 * fire + 0.05 * water,
      density: 0.04 + 0.06 * water,
      coherence: 0.03 + 0.04 * ether,
      charge: 0.05 * (water + air) / 2,
    },
    curlFlow: {
      strength: 0.15 + 0.55 * air,
      scaleField: "coherence",
    },
    advection: {
      dt: 0.5 + 0.7 * air,
      fields: ["density", "heat", "moisture", "charge"],
    },
    reaction: {
      // Gray-Scott parameters interpolate fire-driven branching regimes
      Du: 0.16,
      Dv: 0.08,
      // f and k chosen on a path through the Pearson zoo:
      //   low fire  → coral / spots
      //   mid fire  → mazes
      //   high fire → roots / chaos
      f: 0.020 + 0.040 * fire,
      k: 0.045 + 0.025 * (1 - fire) + 0.010 * earth,
      dt: 1.0,
    },
    branchMemory: {
      grad_thresh: 0.020 + 0.040 * (1 - wood),
      density_thresh: 0.20 + 0.10 * (1 - wood),
      accumulate: 0.02 + 0.10 * wood,
      decay: 0.995 + 0.004 * wood,
      diffuse: 0.005 + 0.020 * water,
    },
    interference: {
      target: "charge",
      k: 0.10 + 0.30 * ether,
      strength: 0.02 + 0.12 * ether,
      decay: 0.96 + 0.03 * (1 - air),
    },
    voronoi: {
      strength: 0.4 * earth,
      decay: 0.85 + 0.10 * (1 - earth),
    },
    life: {
      grow_from_branch: 0.04 * wood,
      grow_from_charge: 0.02 * ether,
      decay: 0.992 - 0.005 * fire,
    },
    discharge: {
      // Charge propagation along branch_memory ridges.
      branch_thresh: 0.04,
      propagate: 0.30 + 0.40 * fire,
      leak_to_life: 0.012 + 0.020 * ether,
      decay: 0.985 - 0.010 * fire,
    },
    // Replenish parameters — fed by separate sliders, not by elements.
    // Defaulted here; main.js overrides with user-set values.
    replenish: {
      energy: 0.55,
      replenish: 0.50,
      decay: 0.95,
    },
  };
}
