// Dhātu-material pass — each of the 7 dhātus biases the field toward a
// distinct material tendency. The embodiment layer picks one body region
// each tick with a dhatu code (D001..D007); we read that and apply a
// gentle global bias.
//
//   D001 rasa     — plasma: moisture rise, low rigidity
//   D002 rakta    — blood: heat + charge mild rise
//   D003 mamsa    — muscle: density firm-up, pressure mild
//   D004 meda     — fat: moisture + density saturate, low contrast
//   D005 asthi    — bone: rigidity strong, density firm
//   D006 majja    — nerve: charge rise, life rise
//   D007 shukra   — generative: coherence + life rise (regenerative)

const DHATU_BIAS = {
  D001: { moisture: +0.012, rigidity: -0.004 },
  D002: { heat: +0.008, charge: +0.006 },
  D003: { density: +0.006, pressure: +0.004 },
  D004: { moisture: +0.008, density: +0.004 },
  D005: { rigidity: +0.012, density: +0.005 },
  D006: { charge: +0.010, life: +0.004 },
  D007: { coherence: +0.010, life: +0.006 },
};

export function dhatuMaterialPass(stack, embodiment, strength = 1.0) {
  if (!embodiment || !embodiment.dhatu) return 0;
  if (strength <= 0) return 0;
  const bias = DHATU_BIAS[embodiment.dhatu];
  if (!bias) return 0;
  let actSum = 0, actN = 0;
  for (const [field, delta] of Object.entries(bias)) {
    const f = stack.get(field);
    if (!f) continue;
    const d = delta * strength;
    for (let i = 0; i < f.length; i++) f[i] += d;
    actSum += Math.abs(delta) * 50; // scale so trace is visible
    actN++;
  }
  return actN > 0 ? (actSum / actN) * strength : 0;
}
