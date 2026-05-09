// Tensegrity pass — pressure ridges along the body region's vertical axis.
//
// When the embodiment archetype is "tensegrity" (or render_geometry is
// stacked_tensegrity), the field gets a column of alternating pressure
// bands — like a stack of compressive nodes held by tension lines. We
// never draw struts; we just add a 1D pressure profile that perturbs
// reaction-diffusion downstream.

const TENSEGRITY_REGIONS = new Set([
  "cervical_spine", "thoracic_spine", "lumbar_spine",
  "fascia_network", "skin_surface",
]);

export function tensegrityPass(stack, embodiment, tick, strength = 1.0) {
  if (!embodiment) return 0;
  if (strength <= 0) return 0;
  const archetype = embodiment.archetype || "";
  const geometry = embodiment.render_geometry || "";
  const isTensegrity =
    archetype.includes("tensegrity") ||
    geometry.includes("tensegrity") ||
    TENSEGRITY_REGIONS.has(embodiment.body_region);
  if (!isTensegrity) return 0;

  const W = stack.W, H = stack.H;
  const pressure = stack.get("pressure");
  const rigidity = stack.get("rigidity");
  const cx = W * 0.5;
  const nNodes = 7;
  const slowPhase = tick * 0.005;
  let activitySum = 0;
  const colSigma = W * 0.12;

  for (let n = 0; n < nNodes; n++) {
    const ny = H * (0.15 + 0.7 * (n / (nNodes - 1)));
    // Each node has a slowly-modulated amplitude
    const aN = 0.5 + 0.5 * Math.sin(slowPhase + n * 0.9);
    const ridgeAmp = 0.018 * strength * aN;
    const rowSigma = H * 0.04;
    activitySum += aN;

    const yLo = Math.max(0, Math.floor(ny - 4 * rowSigma));
    const yHi = Math.min(H - 1, Math.ceil(ny + 4 * rowSigma));
    for (let y = yLo; y <= yHi; y++) {
      const dy = y - ny;
      const wY = Math.exp(-(dy * dy) / (2 * rowSigma * rowSigma));
      if (wY < 0.02) continue;
      for (let x = 0; x < W; x++) {
        const dx = x - cx;
        const wX = Math.exp(-(dx * dx) / (2 * colSigma * colSigma));
        if (wX < 0.02) continue;
        const w = wX * wY;
        const i = y * W + x;
        pressure[i] += ridgeAmp * w;
        rigidity[i] += ridgeAmp * 0.5 * w;
      }
    }
  }
  return (activitySum / nNodes) * strength;
}
