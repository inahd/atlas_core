// Pass-activity timeline — small ring buffer of recent activity scalars
// per pass, drawn as 7 stacked traces. Used to make the otherwise-hidden
// embodiment grammar visible: when does pulseMarma peak, when is bhasma
// driving, when does breath swell.
//
// Each trace is normalized into its own row band, with the pass name and
// current value labeled at left.

const COLORS = {
  bhasma:        "#d97a5a",
  dhatu:         "#a3b569",
  pulseMarma:    "#d3a76e",
  helicalShear:  "#6e9bd3",
  tensegrity:    "#9c8ad3",
  movementPhrase: "#5fb3a3",
  quasicrystal:  "#d36ea7",
};
const PASS_ORDER = [
  "bhasma", "dhatu", "pulseMarma", "helicalShear",
  "tensegrity", "movementPhrase", "quasicrystal",
];
const LABELS = {
  bhasma: "bhasma",
  dhatu: "dhātu",
  pulseMarma: "marma",
  helicalShear: "helix",
  tensegrity: "spine",
  movementPhrase: "breath",
  quasicrystal: "qc",
};

export class Timeline {
  constructor(canvas, capacity = 240) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d", { alpha: false });
    this.capacity = capacity;
    this.buf = {};
    for (const p of PASS_ORDER) {
      this.buf[p] = new Float32Array(capacity);
    }
    this.head = 0;     // next write index
    this.count = 0;    // samples written so far (capped at capacity)
  }

  push(activity) {
    for (const p of PASS_ORDER) {
      this.buf[p][this.head] = activity[p] ?? 0;
    }
    this.head = (this.head + 1) % this.capacity;
    if (this.count < this.capacity) this.count++;
  }

  render() {
    const ctx = this.ctx;
    const W = this.canvas.width;
    const H = this.canvas.height;
    ctx.fillStyle = "#0a0d1a";
    ctx.fillRect(0, 0, W, H);

    const labelW = 42;
    const valW = 36;
    const traceX0 = labelW;
    const traceW = W - labelW - valW;
    const rows = PASS_ORDER.length;
    const rowH = H / rows;

    ctx.font = "9px DejaVu Sans Mono, monospace";
    ctx.textBaseline = "middle";

    for (let r = 0; r < rows; r++) {
      const p = PASS_ORDER[r];
      const yMid = (r + 0.5) * rowH;
      const yTop = r * rowH + 1;
      const yBot = (r + 1) * rowH - 1;
      // Row baseline
      ctx.strokeStyle = "#1e242e";
      ctx.beginPath();
      ctx.moveTo(traceX0, yBot);
      ctx.lineTo(traceX0 + traceW, yBot);
      ctx.stroke();
      // Label
      ctx.fillStyle = COLORS[p];
      ctx.fillText(LABELS[p], 4, yMid);
      // Trace
      const buf = this.buf[p];
      const cap = this.capacity;
      const n = this.count;
      if (n < 2) continue;

      // Auto-scale within row: clip ceiling at 2.0 to compress over-driven values
      const ceil = 2.0;
      const rowSpan = yBot - yTop;

      ctx.strokeStyle = COLORS[p];
      ctx.fillStyle = COLORS[p] + "33";
      ctx.beginPath();
      let last = 0;
      for (let i = 0; i < n; i++) {
        const idx = (this.head - n + i + cap) % cap;
        const v = Math.min(buf[idx], ceil) / ceil;
        const x = traceX0 + (i / (cap - 1)) * traceW;
        const y = yBot - v * rowSpan;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
        last = buf[idx];
      }
      ctx.stroke();
      // Fill below the trace
      ctx.lineTo(traceX0 + ((n - 1) / (cap - 1)) * traceW, yBot);
      ctx.lineTo(traceX0, yBot);
      ctx.closePath();
      ctx.fill();
      // Current value at right
      ctx.fillStyle = "#c8cdd5";
      ctx.fillText(last.toFixed(2), W - valW + 2, yMid);
    }
  }
}
