// Branch-memory accumulation:
// Wherever the density field has both high value AND high gradient
// (i.e., a propagating front rather than a flat region), accumulate
// into branch_memory. The result is a slowly-fading record of where
// fronts have passed — visible as filamentary traces.
//
// branch_memory itself diffuses very slowly (so traces blur over time)
// and decays multiplicatively (so they fade rather than persisting forever).

export function branchMemoryPass(stack, grid, params) {
  const {
    grad_thresh = 0.04,
    density_thresh = 0.25,
    accumulate = 0.06,
    decay = 0.997,
    diffuse = 0.02,
  } = params;

  const W = stack.W, H = stack.H;
  const density = stack.get("density");
  const mem = stack.get("branch_memory");
  const memScratch = stack.scratchOf("branch_memory");

  // Accumulate where front gradient is large
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      const i = y * W + x;
      if (density[i] > density_thresh) {
        const [gx, gy] = grid.gradient(density, x, y);
        const g = Math.sqrt(gx * gx + gy * gy);
        if (g > grad_thresh) {
          mem[i] += accumulate * Math.min(1, g * 4);
        }
      }
      mem[i] *= decay;
    }
  }
  // Slow diffusion to spread memory
  if (diffuse > 0) {
    grid.laplacian(mem, memScratch, diffuse);
    stack.swap("branch_memory");
  }
}
