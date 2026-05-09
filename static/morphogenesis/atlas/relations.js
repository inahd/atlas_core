// Relations — the bridge between field state and form-becoming.
//
// Each frame, after the simulation passes have updated the fields,
// we compute a small set of scalar "relation activations": how strongly
// is one form-class transmuting into another right now?  These are NOT
// pixel values.  They are the engine's own readout of what's emerging.
//
// The renderer consumes them to bias palette mixing, and the side-panel
// HUD displays them as bars.  Together they give the system its "instrument"
// quality: you can watch the field decide that water is becoming vein,
// vein becoming root, root igniting.
//
// All formulas are placeholders for v0.2 — they need to exist before they
// can be tuned.  The structure of the registry is what matters.

export const RELATION_NAMES = [
  "waterToVein",
  "veinToRoot",
  "rootToLightning",
  "cloudToBreath",
  "mountainToBone",
  "flowerToEye",
  "fireToSmoke",
  "waterToFlesh",
];

// Pretty labels for the HUD
export const RELATION_LABELS = {
  waterToVein: "water → vein",
  veinToRoot: "vein → root",
  rootToLightning: "root → lightning",
  cloudToBreath: "cloud → breath",
  mountainToBone: "mountain → bone",
  flowerToEye: "flower → eye",
  fireToSmoke: "fire → smoke",
  waterToFlesh: "water → flesh",
};

function clamp01(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }

// Compute mean field values + a flow-persistence proxy in a single pass.
function fieldStats(stack) {
  const N = stack.N;
  const f = stack.fields;
  let dens = 0, moist = 0, heat = 0, charge = 0,
      coh = 0, branch = 0, rig = 0, life = 0, vmag = 0;
  for (let i = 0; i < N; i++) {
    dens   += f.density[i];
    moist  += f.moisture[i];
    heat   += f.heat[i];
    charge += Math.abs(f.charge[i]);
    coh    += f.coherence[i];
    branch += f.branch_memory[i];
    rig    += f.rigidity[i];
    life   += f.life[i];
    const vx = f.vx[i], vy = f.vy[i];
    vmag   += Math.sqrt(vx * vx + vy * vy);
  }
  return {
    densAvg: dens / N,
    moistAvg: moist / N,
    heatAvg: heat / N,
    chargeAvg: charge / N,
    cohAvg: coh / N,
    branchAvg: branch / N,
    rigAvg: rig / N,
    lifeAvg: life / N,
    flowPersistence: clamp01(vmag / N),
  };
}

// Compute the 8 relation activations.  Element sliders 0..1.
// Returns { name → 0..1 }.
export function computeRelations(stack, elements) {
  const s = fieldStats(stack);
  const water = elements.water ?? 0.5;
  const air = elements.air ?? 0.5;
  const fire = elements.fire ?? 0.5;
  const earth = elements.earth ?? 0.5;
  const wood = elements.wood ?? 0.5;
  const ether = elements.ether ?? 0.5;

  // Relations — each tuned so a "high" reading is structurally meaningful.
  // Constants chosen to put activation at a useful working scale (0.2..0.8)
  // when the relevant fields are in their natural range.
  const r = {};

  r.waterToVein = clamp01(
    3.0 * water * s.moistAvg * s.flowPersistence * (0.3 + 1.5 * s.branchAvg)
  );
  r.veinToRoot = clamp01(
    2.5 * r.waterToVein * wood * (0.4 + 6 * s.lifeAvg) * (0.5 + s.rigAvg * 0.3)
  );
  r.rootToLightning = clamp01(
    14 * s.branchAvg * s.chargeAvg * fire * (0.5 + 0.6 * s.cohAvg)
  );
  r.cloudToBreath = clamp01(
    1.6 * air * s.moistAvg * (1 - s.densAvg) * (0.3 + 1.4 * s.cohAvg)
  );
  r.mountainToBone = clamp01(
    2.2 * earth * s.rigAvg * (0.5 + 1.2 * s.cohAvg)
  );
  r.flowerToEye = clamp01(
    8 * s.lifeAvg * s.cohAvg * ether
  );
  r.fireToSmoke = clamp01(
    1.4 * fire * s.heatAvg * (1 - s.moistAvg) * (0.4 + 1.5 * s.flowPersistence)
  );
  r.waterToFlesh = clamp01(
    2.0 * water * s.moistAvg * s.densAvg * (1 - s.rigAvg) * (0.3 + 1.0 * s.cohAvg)
  );

  return { relations: r, stats: s };
}
