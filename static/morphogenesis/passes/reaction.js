// Reaction-diffusion: Gray-Scott on (density, coherence).
// Produces emergent spotting, mazes, branching depending on (f, k) and rates.
// f = feed rate (replenish density), k = kill rate (drain coherence).

export function reactionPass(stack, grid, params) {
  const {
    Du = 0.16,   // density diffusion
    Dv = 0.08,   // coherence diffusion
    f = 0.035,   // feed
    k = 0.062,   // kill
    dt = 1.0,
  } = params;

  const W = stack.W, H = stack.H;
  const a = stack.get("density");      // u (substrate)
  const b = stack.get("coherence");    // v (catalyst)
  const aNext = stack.scratchOf("density");
  const bNext = stack.scratchOf("coherence");

  for (let y = 0; y < H; y++) {
    const yp = (y - 1 + H) % H, yn = (y + 1) % H;
    for (let x = 0; x < W; x++) {
      const xp = (x - 1 + W) % W, xn = (x + 1) % W;
      const i = y * W + x;
      const ai = a[i], bi = b[i];
      const lapA =
        a[y * W + xp] + a[y * W + xn] +
        a[yp * W + x] + a[yn * W + x] -
        4 * ai;
      const lapB =
        b[y * W + xp] + b[y * W + xn] +
        b[yp * W + x] + b[yn * W + x] -
        4 * bi;
      const abb = ai * bi * bi;
      aNext[i] = ai + dt * (Du * lapA - abb + f * (1 - ai));
      bNext[i] = bi + dt * (Dv * lapB + abb - (f + k) * bi);
    }
  }
  stack.swap("density");
  stack.swap("coherence");
}
