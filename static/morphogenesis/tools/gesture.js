// GestureRecognizer — turns raw mouse input into one of 8 user intents.
// The recognizer never fires until the gesture ends (mouseup); it then
// classifies based on duration, drift, path-length, direction variance,
// angular sweep, and radial expansion.
//
//   single click            → "bloom"
//   double click (<350ms)   → "strike"
//   long press (no drift)   → "reveal"
//   right click             → "void_click"
//   right drag              → "void_drag"
//   slow / straight drag    → "flow"
//   high direction variance → "lightning"
//   ~full angular sweep     → "mandala"
//   rotation + radial drift → "twist"
//
// Drag also fires periodic "stream" callbacks during motion so the user
// sees a visible trail while the final classification is pending.

const CLICK_DRIFT_PX  = 5;
const CLICK_TIME_MS   = 250;
const DOUBLE_CLICK_MS = 350;
const LONG_PRESS_MS   = 600;

export class GestureRecognizer {
  constructor() {
    this.points = [];
    this.startMs = 0;
    this.startX = 0; this.startY = 0;
    this.lastEndMs = 0;
    this.lastEndIntent = null;
    this.button = -1;
    this.modifiers = { shift: false, alt: false, ctrl: false };
    this.endCallback   = null;
    this.streamCallback = null;
    this._streamLastMs = 0;
  }

  onEnd(fn)    { this.endCallback   = fn; }
  onStream(fn) { this.streamCallback = fn; }

  begin(x, y, t, button, modifiers) {
    this.points = [{ x, y, t }];
    this.startMs = t;
    this.startX = x; this.startY = y;
    this.button = button;
    this.modifiers = { ...modifiers };
    this._streamLastMs = t;
  }

  move(x, y, t) {
    this.points.push({ x, y, t });
    if (this.points.length > 256) this.points.shift();
    if (this.streamCallback && t - this._streamLastMs > 30) {
      this._streamLastMs = t;
      const prev = this.points[Math.max(0, this.points.length - 2)];
      this.streamCallback({
        x, y,
        dx: x - prev.x, dy: y - prev.y,
        button: this.button,
        modifiers: this.modifiers,
      });
    }
  }

  end(x, y, t) {
    const dur     = t - this.startMs;
    const drift   = Math.hypot(x - this.startX, y - this.startY);
    const totDist = this._totalPathLen();

    let intent;
    if (this.button === 2) {
      intent = (drift > 8 || totDist > 24) ? "void_drag" : "void_click";
    } else if (drift < CLICK_DRIFT_PX && totDist < CLICK_DRIFT_PX * 2) {
      // No movement — single/double/long
      const sinceLast = t - this.lastEndMs;
      if (sinceLast < DOUBLE_CLICK_MS && this.lastEndIntent === "bloom") {
        intent = "strike";
      } else if (dur > LONG_PRESS_MS) {
        intent = "reveal";
      } else {
        intent = "bloom";
      }
    } else {
      // Movement — analyze path geometry
      const dirVar = this._directionVariance();
      const sweep  = this._angularSweep();
      const radial = this._radialExpansionRatio();
      const meanV  = totDist / Math.max(1, dur);

      if (dirVar > 0.55) {
        intent = "lightning";
      } else if (sweep > 4.0 && radial < 0.35) {
        intent = "mandala";
      } else if (sweep > 1.0 && radial > 0.35) {
        intent = "twist";
      } else {
        intent = "flow";
      }
    }

    const payload = {
      x, y, dur, drift, totDist,
      points: this.points.slice(),
      modifiers: { ...this.modifiers },
      button: this.button,
    };
    this.lastEndMs = t;
    this.lastEndIntent = intent;
    this.endCallback?.(intent, payload);
  }

  cancel() { this.points = []; this.button = -1; }

  // ── path metrics ──────────────────────────────────────────────

  _totalPathLen() {
    let s = 0;
    for (let i = 1; i < this.points.length; i++) {
      const a = this.points[i - 1], b = this.points[i];
      s += Math.hypot(b.x - a.x, b.y - a.y);
    }
    return s;
  }

  _directionVariance() {
    if (this.points.length < 5) return 0;
    const angles = [];
    for (let i = 1; i < this.points.length; i++) {
      const a = this.points[i - 1], b = this.points[i];
      const dx = b.x - a.x, dy = b.y - a.y;
      if (Math.hypot(dx, dy) < 0.5) continue;
      angles.push(Math.atan2(dy, dx));
    }
    if (angles.length < 3) return 0;
    let total = 0;
    for (let i = 1; i < angles.length; i++) {
      let d = angles[i] - angles[i - 1];
      while (d > Math.PI)  d -= 2 * Math.PI;
      while (d < -Math.PI) d += 2 * Math.PI;
      total += Math.abs(d);
    }
    return total / angles.length;
  }

  _angularSweep() {
    if (this.points.length < 4) return 0;
    let cx = 0, cy = 0;
    for (const p of this.points) { cx += p.x; cy += p.y; }
    cx /= this.points.length; cy /= this.points.length;
    let total = 0, lastA = null;
    for (const p of this.points) {
      const a = Math.atan2(p.y - cy, p.x - cx);
      if (lastA !== null) {
        let d = a - lastA;
        while (d > Math.PI)  d -= 2 * Math.PI;
        while (d < -Math.PI) d += 2 * Math.PI;
        total += d;
      }
      lastA = a;
    }
    return Math.abs(total);
  }

  _radialExpansionRatio() {
    if (this.points.length < 4) return 0;
    let cx = 0, cy = 0;
    for (const p of this.points) { cx += p.x; cy += p.y; }
    cx /= this.points.length; cy /= this.points.length;
    let minR = Infinity, maxR = 0;
    for (const p of this.points) {
      const r = Math.hypot(p.x - cx, p.y - cy);
      if (r < minR) minR = r;
      if (r > maxR) maxR = r;
    }
    return (maxR - minR) / Math.max(1, maxR);
  }
}
