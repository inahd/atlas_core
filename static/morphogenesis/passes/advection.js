// Advection: semi-Lagrangian back-trace along velocity field.
// Curl flow: derive a divergence-free velocity from a scalar potential
// by taking ⟨∂y, -∂x⟩, so the flow naturally swirls without sources/sinks.

export function curlFlowPass(stack, grid, params) {
  const { strength = 0.4, scaleField = "coherence" } = params;
  const W = stack.W, H = stack.H;
  const phi = stack.get(scaleField);
  const vx = stack.get("vx"), vy = stack.get("vy");
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      const [gx, gy] = grid.gradient(phi, x, y);
      // Curl-orthogonal: rotate gradient 90° to get divergence-free flow
      const i = y * W + x;
      vx[i] = vx[i] * 0.92 + strength * gy;
      vy[i] = vy[i] * 0.92 + strength * (-gx);
    }
  }
}

export function advectionPass(stack, grid, params) {
  const { dt = 1.0, fields = ["density", "heat", "moisture", "charge"] } = params;
  const W = stack.W, H = stack.H;
  const vx = stack.get("vx"), vy = stack.get("vy");
  for (const name of fields) {
    const src = stack.get(name);
    const dst = stack.scratchOf(name);
    for (let y = 0; y < H; y++) {
      for (let x = 0; x < W; x++) {
        const i = y * W + x;
        const px = x - dt * vx[i];
        const py = y - dt * vy[i];
        dst[i] = grid.sample(src, px, py);
      }
    }
    stack.swap(name);
  }
}
