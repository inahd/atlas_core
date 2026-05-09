// Profiler — measures and displays per-frame cost so we can decide
// whether the engine bog is in sim, render, or events.  Toggleable
// with backtick (`).  Hidden by default.
//
// Tracks rolling EMA of:
//   fps, frame ms, sim ms, render ms,
//   active SymbolEvents, scheduled echoes,
//   phrase sample count, region transitions per second,
//   grid resolution, GPU mode, dropped frames,
//   auto-quality flag (true if sustained < 30 fps).
//
// Diagnostic-only.  Adds a tiny per-frame cost (~0.05 ms).

const ALPHA = 0.10;       // EMA smoothing factor

export class Profiler {
  constructor(opts = {}) {
    this.sim = opts.sim;
    this.compositor = opts.compositor;
    this.element = opts.element;
    this.visible = false;

    // Rolling metrics
    this.fps = 60;
    this.frameMs = 16;
    this.simMs = 0;
    this.renderMs = 0;
    this.eventCount = 0;
    this.echoCount = 0;
    this.phraseSamples = 0;
    this.transitionsPerSec = 0;
    this.droppedFrames = 0;
    this.belowThirtyConsecutive = 0;
    this.autoQuality = false;
    this.gpuMode = "Canvas2D";

    // Per-frame timing markers
    this._tFrameStart = 0;
    this._tSimStart = 0;
    this._tSimEnd = 0;
    this._tRenderStart = 0;
    this._tRenderEnd = 0;
    this._lastFrameAt = 0;

    // Transition rate counter (windowed)
    this._transitionCountWindow = [];
    this._lastDisplayMs = 0;
  }

  toggle() {
    this.visible = !this.visible;
    if (this.element) {
      this.element.classList.toggle("show", this.visible);
    }
  }

  // Call at the very start of frame()
  beginFrame(nowMs) {
    this._tFrameStart = nowMs;
    if (this._lastFrameAt > 0) {
      const dt = nowMs - this._lastFrameAt;
      const instFps = 1000 / Math.max(1, dt);
      this.fps = this.fps * (1 - ALPHA) + instFps * ALPHA;
      this.frameMs = this.frameMs * (1 - ALPHA) + dt * ALPHA;
      if (instFps < 30) this.belowThirtyConsecutive++;
      else this.belowThirtyConsecutive = 0;
      // Auto-quality flag if sustained < 30 fps for 2 s
      this.autoQuality = this.belowThirtyConsecutive > 60;
      // Dropped frame heuristic — frame > 33ms means we missed at least one
      if (dt > 33) this.droppedFrames++;
    }
    this._lastFrameAt = nowMs;
  }

  beginSim() { this._tSimStart = performance.now(); }
  endSim()   {
    this._tSimEnd = performance.now();
    const ms = this._tSimEnd - this._tSimStart;
    this.simMs = this.simMs * (1 - ALPHA) + ms * ALPHA;
  }

  beginRender() { this._tRenderStart = performance.now(); }
  endRender()   {
    this._tRenderEnd = performance.now();
    const ms = this._tRenderEnd - this._tRenderStart;
    this.renderMs = this.renderMs * (1 - ALPHA) + ms * ALPHA;
  }

  // Bookkeeping for transition rate (call each time a transition fires)
  recordTransition(nowMs) {
    this._transitionCountWindow.push(nowMs);
    const cutoff = nowMs - 1000;
    while (this._transitionCountWindow.length &&
           this._transitionCountWindow[0] < cutoff) {
      this._transitionCountWindow.shift();
    }
    this.transitionsPerSec = this._transitionCountWindow.length;
  }

  // Update derived state from sim (called each frame after sim step)
  sample() {
    if (!this.sim) return;
    this.eventCount = this.sim.symbolEvents?.length || 0;
    this.echoCount  = this.sim.regionMap?.echoes?.length || 0;
  }

  // Render the HUD if visible (called once per ~6 frames from main)
  render(extraInfo = {}) {
    if (!this.visible || !this.element) return;
    const now = performance.now();
    if (now - this._lastDisplayMs < 100) return;
    this._lastDisplayMs = now;

    const grid = this.sim ? `${this.sim.W}×${this.sim.H}` : "—";
    const phraseSamples = extraInfo.phraseSamples ?? 0;
    // v0.18 — lifecycle diagnostics from BeginnerController.getDebugState()
    const dbg = extraInfo.debug || {};
    const lock = dbg.lockRemainingMs > 0
        ? `${dbg.lockLabel || "lock"} (${dbg.lockRemainingMs.toFixed(0)} ms)`
        : "—";
    const ptr = dbg.pointerActive
        ? `down (btn ${dbg.pointerButton})`
        : "up";
    const err = dbg.lastError
        ? `[${dbg.lastError.where}] ${dbg.lastError.msg}`.slice(0, 60)
        : "—";
    const lines = [
      `FPS         ${this.fps.toFixed(0)}`,
      `frame       ${this.frameMs.toFixed(1)} ms`,
      `  sim       ${this.simMs.toFixed(1)} ms`,
      `  render    ${this.renderMs.toFixed(1)} ms`,
      `events      ${this.eventCount}`,
      `echoes      ${this.echoCount}`,
      `transitions ${this.transitionsPerSec}/s`,
      `phrase n    ${phraseSamples}`,
      `lock        ${lock}`,
      `pointer     ${ptr}`,
      `last err    ${err}`,
      `grid        ${grid}`,
      `gpu         ${this.gpuMode}`,
      `dropped     ${this.droppedFrames}`,
      `quality     ${this.autoQuality ? "DOWNGRADE" : "ok"}`,
    ];
    this.element.textContent = lines.join("\n");
  }
}
