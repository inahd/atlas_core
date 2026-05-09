// Bhasma calcination pass — applies the visual_operators dict from the
// current rasaśāstra stage to the field stack each tick.
//
// The 9 stages encode where the work is in its transformation cycle.
// We never draw "fire" or "ash" literally; we modulate field tendencies:
//   shodhana       — gentle wash: moisture push, low life drain
//   mardana        — grinding: pressure ridges form, density flattens
//   bhavana        — soaking: moisture saturates, charge gentle rise
//   puta_agni      — calcination: heat spike, life drain, density burn-back
//   sattva_extract — distillate: coherence boost, light drain
//   stabilization  — settling: rigidity hold, low decay
//   marana         — mineralization: density lock, life drain, rigidity boost
//   amritikarana   — ambrosia: coherence + moisture rise, charge ramp
//   dormant_seed   — sealed: minimal motion, branch_memory locked
//
// Each operator is a multiplicative or additive nudge on a single field.

const OP_HANDLERS = {
  // Multiplicative life damping
  life_drain: (stack, v) => mulField(stack, "life", v),
  // Boost rigidity field (multiplicative — caps at 1)
  rigidity_boost: (stack, v) => mulFieldClamp(stack, "rigidity", v, 1),
  // Lock density toward current value (low-pass: dens = dens*v)
  density_lock: (stack, v) => mulField(stack, "density", v),
  // Heat spike — additive scaled by v - 1.0
  heat_spike: (stack, v) => addField(stack, "heat", (v - 1.0) * 0.05),
  // Density burn-back during puta_agni
  density_burn: (stack, v) => mulField(stack, "density", v),
  // Moisture flow during bhavana / amritikarana
  moisture_push: (stack, v) => addField(stack, "moisture", (v - 1.0) * 0.04),
  // Coherence rise during sattva extraction / amritikarana
  coherence_rise: (stack, v) => addField(stack, "coherence", (v - 1.0) * 0.03),
  // Charge ramp during amritikarana
  charge_ramp: (stack, v) => addField(stack, "charge", (v - 1.0) * 0.02),
  // Pressure ridge formation during mardana
  pressure_ridge: (stack, v) => addField(stack, "pressure", (v - 1.0) * 0.04),
  // Branch memory lock during dormant_seed
  memory_lock: (stack, v) => mulField(stack, "branch_memory", v),
  // Light drain during sattva extraction (drops density gently)
  light_drain: (stack, v) => mulField(stack, "density", v),
};

export function bhasmaCalcinationPass(stack, bhasmaStage, strength = 1.0) {
  if (!bhasmaStage || !bhasmaStage.visual_operators) return 0;
  if (strength <= 0) return 0;
  const ops = bhasmaStage.visual_operators;
  let actSum = 0, actN = 0;
  for (const [opName, value] of Object.entries(ops)) {
    const handler = OP_HANDLERS[opName];
    if (!handler) continue;
    const v = 1.0 + (value - 1.0) * strength;
    handler(stack, v);
    actSum += Math.abs(value - 1.0);
    actN++;
  }
  return actN > 0 ? (actSum / actN) * strength : 0;
}

function mulField(stack, name, v) {
  const f = stack.get(name);
  if (!f) return;
  for (let i = 0; i < f.length; i++) f[i] *= v;
}

function mulFieldClamp(stack, name, v, cap) {
  const f = stack.get(name);
  if (!f) return;
  for (let i = 0; i < f.length; i++) {
    const x = f[i] * v;
    f[i] = x > cap ? cap : x;
  }
}

function addField(stack, name, delta) {
  const f = stack.get(name);
  if (!f) return;
  for (let i = 0; i < f.length; i++) f[i] += delta;
}
