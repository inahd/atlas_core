// Sacred pass — applies vastu, yantra, and mandala biases each tick.
// All three systems are precomputed once on reset and stored in
// `sim.sacredCtx`; this pass just iterates and adds their deltas.

import { applyVastu } from "../atlas/vastu.js";
import { applyYantra } from "../atlas/yantra.js";
import { applyMandala } from "../atlas/mandala.js";

export function applySacred(stack, sacredCtx, params) {
  if (!sacredCtx || !params) return;
  const masterStrength = params.masterStrength ?? 1.0;
  if (masterStrength <= 0) return;

  const vS = (params.vastuStrength    ?? 0) * masterStrength;
  const yS = (params.yantraStrength   ?? 0) * masterStrength;
  const mS = (params.mandalaStrength  ?? 0) * masterStrength;

  applyVastu(stack, sacredCtx.vastu, vS);
  applyYantra(stack, sacredCtx.yantraMask, yS);
  applyMandala(stack, sacredCtx.mandala, mS);
}
