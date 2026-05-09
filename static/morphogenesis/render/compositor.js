// Compositor — paint the field stack into RGB, with phosphor-style
// bright-feature history that does NOT accumulate darkness.
//
// v0.3 used an EMA blend on the canvas (canvas := canvas * persist
// + new * (1-persist)).  Combined with the void-mask multiply and
// continuous sinks, this drove the canvas to black.
//
// v0.4 strategy:
//   1. Render current frame at sim resolution into a Float32 RGB buffer.
//   2. Update history Float32 RGB by `max(history * decay, currentBright)`
//      where currentBright is the frame's pixels above a luminance threshold.
//   3. Final compose = max(current, history * historyAlpha).
//   4. Apply contrast + exposure + shyama floor before drawing.
//
// History never accumulates dark — dark pixels in current produce no
// history write.  This is the phosphor-display model.

import { PALETTES, debugFieldRGB, postProcess, SHYAMA } from "./colormap.js";
import { applyAesthetic } from "../atlas/aesthetics.js";
import { renderIntergenesis } from "./intergenesis.js";

const DEBUG_FIELD_RANGES = {
  density: 1.2,
  moisture: 1.0,
  heat: 1.0,
  pressure: 1.5,
  rigidity: 1.0,
  coherence: 1.0,
  branch_memory: 0.8,
  charge: "bipolar",
  life: 1.0,
  vx: "bipolar",
  vy: "bipolar",
};

export class Compositor {
  constructor(canvas, simW, simH) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d", { alpha: false });
    this.simW = simW;
    this.simH = simH;

    // Sim-resolution work buffers (3 channels each)
    const N = simW * simH;
    this.curRGB = new Float32Array(N * 3);   // current frame palette output
    this.histRGB = new Float32Array(N * 3);  // bright-feature memory
    this.outRGB = new Float32Array(N * 3);   // final composited

    // ImageData for upload to canvas
    this.buffer = document.createElement("canvas");
    this.buffer.width = simW;
    this.buffer.height = simH;
    this.bctx = this.buffer.getContext("2d");
    this.imgData = this.bctx.createImageData(simW, simH);

    // History parameters (set externally)
    this.historyDecay = 0.985;
    this.historyAlpha = 0.7;
    this.historyThreshold = 0.18;

    // Last-frame stats (used by collapse monitor)
    this.blackRatio = 0;
    this.avgLuminance = 0;
  }

  resetHistory() {
    this.histRGB.fill(0);
  }

  // Compute the current-frame RGB (0..1 floats) into curRGB.
  // v0.14 — when a regionMap is provided, render via the intergenesis
  // feature-extraction system (top-2 visual states per region blended).
  // Palette-based painting is kept only for the field-debug overlay.
  _paintCurrent(stack, paletteName, debugField, relations, contrast, exposure,
                aesthetic, regionMap) {
    const f = stack.fields;
    const N = stack.N;
    const dst = this.curRGB;

    if (debugField && DEBUG_FIELD_RANGES[debugField] !== undefined) {
      const range = DEBUG_FIELD_RANGES[debugField];
      for (let i = 0; i < N; i++) {
        const [r, g, b] = debugFieldRGB(f, debugField, i, range);
        const off = i * 3;
        dst[off] = Math.max(r, SHYAMA[0]);
        dst[off + 1] = Math.max(g, SHYAMA[1]);
        dst[off + 2] = Math.max(b, SHYAMA[2]);
      }
      return;
    }

    if (regionMap) {
      // v0.14 — feature-extraction renderer (intergenesis).  No raw
      // field buffer painting; pixels come from blended state extractors.
      renderIntergenesis(stack, dst, regionMap, this.simW, this.simH,
                         contrast, exposure);
      // Apply aesthetic tint as a light overlay if present
      if (aesthetic) {
        for (let i = 0; i < N; i++) {
          const off = i * 3;
          const [R, G, B] = applyAesthetic(dst[off], dst[off + 1], dst[off + 2], aesthetic);
          dst[off] = R; dst[off + 1] = G; dst[off + 2] = B;
        }
      }
      return;
    }

    // Fallback (advanced-mode debug): legacy palette-based render
    const pal = PALETTES[paletteName] || PALETTES.cosmic;
    const haveAesthetic = !!aesthetic;
    for (let i = 0; i < N; i++) {
      let [r, g, b] = pal(f, i, relations);
      if (haveAesthetic) [r, g, b] = applyAesthetic(r, g, b, aesthetic);
      const [R, G, B] = postProcess(r, g, b, contrast, exposure);
      const off = i * 3;
      dst[off] = R; dst[off + 1] = G; dst[off + 2] = B;
    }
  }

  // Update bright-feature history.  History pixels decay each frame; bright
  // features in the current frame are written via max-blend, never darker.
  _updateHistory() {
    const N = this.simW * this.simH;
    const decay = this.historyDecay;
    const t = this.historyThreshold;
    const h = this.histRGB;
    const c = this.curRGB;
    for (let i = 0; i < N; i++) {
      const off = i * 3;
      const cr = c[off], cg = c[off + 1], cb = c[off + 2];
      // Decay history
      h[off]     *= decay;
      h[off + 1] *= decay;
      h[off + 2] *= decay;
      // Luminance of current pixel
      const lum = 0.30 * cr + 0.60 * cg + 0.10 * cb;
      if (lum > t) {
        const w = (lum - t) / (1 - t);
        const wr = cr * w, wg = cg * w, wb = cb * w;
        if (wr > h[off])     h[off]     = wr;
        if (wg > h[off + 1]) h[off + 1] = wg;
        if (wb > h[off + 2]) h[off + 2] = wb;
      }
    }
  }

  // Final composite: max(current, history * alpha) per pixel, then shyama
  // floor (already in current after postProcess, but apply again in case
  // history is below ground — it cannot drag below).  Returns frame stats.
  _composite(showHistory) {
    const N = this.simW * this.simH;
    const c = this.curRGB;
    const h = this.histRGB;
    const o = this.outRGB;
    const a = showHistory ? this.historyAlpha : 0;
    let blackCount = 0, lumSum = 0;
    const blackThresh = 0.06;
    for (let i = 0; i < N; i++) {
      const off = i * 3;
      const hr = h[off] * a, hg = h[off + 1] * a, hb = h[off + 2] * a;
      let r = c[off]   > hr ? c[off]   : hr;
      let g = c[off+1] > hg ? c[off+1] : hg;
      let b = c[off+2] > hb ? c[off+2] : hb;
      // Shyama floor (defensive — postProcess already applied)
      if (r < SHYAMA[0]) r = SHYAMA[0];
      if (g < SHYAMA[1]) g = SHYAMA[1];
      if (b < SHYAMA[2]) b = SHYAMA[2];
      o[off] = r; o[off + 1] = g; o[off + 2] = b;
      const lum = 0.30 * r + 0.60 * g + 0.10 * b;
      lumSum += lum;
      if (lum < blackThresh) blackCount++;
    }
    this.blackRatio = blackCount / N;
    this.avgLuminance = lumSum / N;
  }

  // Push outRGB into imageData and draw to canvas
  _present() {
    const data = this.imgData.data;
    const o = this.outRGB;
    const N = this.simW * this.simH;
    for (let i = 0; i < N; i++) {
      const off = i * 3;
      const offImg = i * 4;
      data[offImg]     = (o[off]     * 255) | 0;
      data[offImg + 1] = (o[off + 1] * 255) | 0;
      data[offImg + 2] = (o[off + 2] * 255) | 0;
      data[offImg + 3] = 255;
    }
    this.bctx.putImageData(this.imgData, 0, 0);
    const ctx = this.ctx;
    ctx.globalAlpha = 1.0;
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = "high";
    // Background prefill is the shyama ground itself — never pure black
    ctx.fillStyle = `rgb(${(SHYAMA[0]*255)|0},${(SHYAMA[1]*255)|0},${(SHYAMA[2]*255)|0})`;
    ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    ctx.drawImage(this.buffer, 0, 0, this.canvas.width, this.canvas.height);
  }

  // Public entry point.  Updates history (unless paused or debug) and
  // presents the composited frame.  Returns this.blackRatio / this.avgLuminance.
  paint(stack, paletteName, opts = {}) {
    const {
      relations = {},
      debugField = null,
      contrast = 1.0,
      exposure = 1.0,
      historyDecay = 0.985,
      historyAlpha = 0.7,
      showHistory = true,
      threshold = 0.18,
      aesthetic = null,
      regionMap = null,
    } = opts;
    this.historyDecay = historyDecay;
    this.historyAlpha = historyAlpha;
    this.historyThreshold = threshold;

    this._paintCurrent(stack, paletteName, debugField, relations, contrast, exposure,
                       aesthetic, regionMap);

    if (debugField) {
      // Debug view bypasses history entirely — clean inspection
      this.outRGB.set(this.curRGB);
      // Recompute stats on debug view too (cheap)
      const N = this.simW * this.simH;
      let blackCount = 0, lumSum = 0;
      const o = this.outRGB;
      for (let i = 0; i < N; i++) {
        const off = i * 3;
        const lum = 0.30 * o[off] + 0.60 * o[off + 1] + 0.10 * o[off + 2];
        lumSum += lum;
        if (lum < 0.06) blackCount++;
      }
      this.blackRatio = blackCount / N;
      this.avgLuminance = lumSum / N;
    } else {
      this._updateHistory();
      this._composite(showHistory);
    }
    this._present();
  }

  exportPNG(filename = "morphogenesis.png") {
    this.canvas.toBlob((blob) => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      a.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    }, "image/png");
  }
}
