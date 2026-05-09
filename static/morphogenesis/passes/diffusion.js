// Diffusion pass — Laplacian smoothing on selected scalar fields.
// Each field has its own diffusion rate (driven by element sliders).

export function diffusionPass(stack, grid, rates) {
  const targets = [
    ["moisture", rates.moisture],
    ["heat", rates.heat],
    ["density", rates.density],
    ["coherence", rates.coherence],
    ["charge", rates.charge],
  ];
  for (const [name, k] of targets) {
    if (k <= 0) continue;
    const src = stack.get(name);
    const dst = stack.scratchOf(name);
    grid.laplacian(src, dst, k);
    stack.swap(name);
  }
}
