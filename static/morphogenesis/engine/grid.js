// Wrap-around toroidal grid index helpers.
// Working on a torus avoids edge artifacts and matches Atlas's
// theta/phi toroidal field convention.

export class Grid {
  constructor(W, H) {
    this.W = W;
    this.H = H;
    this.N = W * H;
  }
  idx(x, y) {
    const W = this.W, H = this.H;
    return ((y % H + H) % H) * W + ((x % W + W) % W);
  }
  // 4-neighbor Laplacian on a Float32Array (5-point stencil)
  laplacian(src, dst, k = 1.0) {
    const { W, H } = this;
    for (let y = 0; y < H; y++) {
      const yp = (y - 1 + H) % H, yn = (y + 1) % H;
      for (let x = 0; x < W; x++) {
        const xp = (x - 1 + W) % W, xn = (x + 1) % W;
        const c = src[y * W + x];
        const lap =
          src[y * W + xp] + src[y * W + xn] +
          src[yp * W + x] + src[yn * W + x] -
          4 * c;
        dst[y * W + x] = c + k * lap;
      }
    }
  }
  // Bilinear sample at fractional (x,y) with toroidal wrap
  sample(field, fx, fy) {
    const W = this.W, H = this.H;
    const x0 = Math.floor(fx), y0 = Math.floor(fy);
    const sx = fx - x0, sy = fy - y0;
    const x1 = ((x0 % W) + W) % W;
    const x2 = ((x0 + 1) % W + W) % W;
    const y1 = ((y0 % H) + H) % H;
    const y2 = ((y0 + 1) % H + H) % H;
    const a = field[y1 * W + x1] * (1 - sx) + field[y1 * W + x2] * sx;
    const b = field[y2 * W + x1] * (1 - sx) + field[y2 * W + x2] * sx;
    return a * (1 - sy) + b * sy;
  }
  // Central-difference gradient at (x,y) → [gx, gy]
  gradient(field, x, y) {
    const W = this.W, H = this.H;
    const xp = (x - 1 + W) % W, xn = (x + 1) % W;
    const yp = (y - 1 + H) % H, yn = (y + 1) % H;
    const gx = 0.5 * (field[y * W + xn] - field[y * W + xp]);
    const gy = 0.5 * (field[yn * W + x] - field[yp * W + x]);
    return [gx, gy];
  }
}
