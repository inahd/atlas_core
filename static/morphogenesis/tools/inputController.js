// InputController — mouse + keyboard + wheel + command-phrase input.
// Active only while Vision Mode is engaged; attach()/detach() lifecycle.
//
// Architecture:
//   - All keyboard actions go through an action registry (id → fn).
//   - Default bindings map event.key → action id.  Layout-independent
//     because event.key reports the printed character of the user's
//     active layout (Dvorak users typing "S" get event.key === "s").
//   - User overrides live in localStorage["morpho_bindings_v1"] and are
//     merged on top of defaults.
//
// Mouse mappings:
//   left drag       → active tool
//   right drag      → void carve
//   middle drag     → vortex
//   shift + left    → flow stroke
//   alt + left      → helical shear
//   ctrl + click    → drop symbol node (one-shot, no drag)
//   wheel           → brush size
//
// Drag streams emit one SymbolEvent every EMIT_INTERVAL_MS.  Each event
// has its own envelope; many events accumulate into a continuous stroke.

import { TOOLS, makeSymbolEvent } from "./symbolEvent.js";
import { VISION_NUM_TO_KEY } from "../atlas/visionPresets.js";

const STORAGE_KEY = "morpho_bindings_v1";
const EMIT_INTERVAL_MS = 32;        // ~30 events/s while dragging
const CLICK_TIME_MS = 220;
const CLICK_MAX_DRIFT_PX = 5;

const DEFAULT_BINDINGS = [
  { key: "Tab",     shift: false, action: "cycle_tool" },
  { key: "Tab",     shift: true,  action: "cycle_tool_back" },
  { key: "[",                     action: "cycle_tileset_back" },
  { key: "]",                     action: "cycle_tileset" },
  { key: " ",                     action: "breath_pulse" },
  { key: "r",                     action: "reseed" },
  { key: "s",                     action: "save_png" },
  { key: "f",                     action: "toggle_fullscreen" },
  { key: "h",                     action: "toggle_hud" },
  { key: "Escape",                action: "exit_vision" },
  { key: ":",                     action: "open_command" },
  { key: "l",                     action: "load_atlas" },
  { key: "c",                     action: "copy_bundle" },
  { key: "p",                     action: "toggle_pause" },
  { key: "1",                     action: "preset_1" },
  { key: "2",                     action: "preset_2" },
  { key: "3",                     action: "preset_3" },
  { key: "4",                     action: "preset_4" },
  { key: "5",                     action: "preset_5" },
  { key: "6",                     action: "preset_6" },
];

// 9 palettes — original 3 + 6 rasa moods.  [ ] cycles them in Vision Mode
// and gives the field a different emotional register on each press.
const PALETTE_NAMES = [
  "cosmic", "rohini", "ashwini",
  "shanta", "shringara", "vira",
  "raudra", "karuna", "adbhuta",
];

export class InputController {
  constructor(opts) {
    this.sim = opts.sim;
    this.state = opts.state;
    this.canvas = opts.canvas;
    this.compositor = opts.compositor;
    this.visionMode = opts.visionMode;
    this.actions = {};
    this.bindings = this._loadBindings();

    this.activeToolIdx = 0;
    this.brushSize = 12;          // sim cells
    this.tilesetIdx = PALETTE_NAMES.indexOf(this.state.paletteName) >= 0
                      ? PALETTE_NAMES.indexOf(this.state.paletteName) : 0;

    this.lastEmitMs = 0;
    this.dragState = null;
    this.symbolHistory = [];      // last 5 emitted events {kind, t}
    this.attached = false;
    this.cmdInputEl = null;

    // v0.9 — every keypress / gesture leaves a visual mark
    this.lastInputMs = performance.now();
    this.lastIdleMs  = performance.now();
    this.lastCursor = { x: this.sim.W * 0.5, y: this.sim.H * 0.5 };

    this._registerDefaultActions(opts);
    this._buildCommandInput();
    this._bindHandlers();
  }

  attach() {
    if (this.attached) return;
    this.attached = true;
    document.addEventListener("keydown", this._onKeyDown);
    this.canvas.addEventListener("mousedown", this._onMouseDown);
    document.addEventListener("mousemove", this._onMouseMove);
    document.addEventListener("mouseup",   this._onMouseUp);
    this.canvas.addEventListener("wheel",  this._onWheel, { passive: false });
    this.canvas.addEventListener("contextmenu", this._onContextMenu);
    this._refreshHud();
  }

  detach() {
    if (!this.attached) return;
    this.attached = false;
    document.removeEventListener("keydown", this._onKeyDown);
    this.canvas.removeEventListener("mousedown", this._onMouseDown);
    document.removeEventListener("mousemove", this._onMouseMove);
    document.removeEventListener("mouseup",   this._onMouseUp);
    this.canvas.removeEventListener("wheel",  this._onWheel);
    this.canvas.removeEventListener("contextmenu", this._onContextMenu);
    this.dragState = null;
    this._closeCommand();
  }

  // ── action registry ────────────────────────────────────────────

  registerAction(id, def) { this.actions[id] = def; }
  dispatch(id) {
    const a = this.actions[id];
    if (a && typeof a.run === "function") a.run();
  }

  _registerDefaultActions(opts) {
    const reg = (id, name, run) => this.registerAction(id, { name, run });

    // Each action also emits a visual signature so the field never sits
    // silent under a keypress.  Center coords used for non-spatial actions.
    const cx = () => this.sim.W * 0.5;
    const cy = () => this.sim.H * 0.5;

    reg("cycle_tool", "next tool", () => {
      this.cycleTool(+1);
      this._signatureBurst();
    });
    reg("cycle_tool_back", "prev tool", () => {
      this.cycleTool(-1);
      this._signatureBurst();
    });
    reg("cycle_tileset", "next palette", () => {
      this.cycleTileset(+1);
      this._emitEvent({ kind: "palette_swap", x: cx(), y: cy(), radius: 60, intensity: 1.0 });
    });
    reg("cycle_tileset_back", "prev palette", () => {
      this.cycleTileset(-1);
      this._emitEvent({ kind: "palette_swap", x: cx(), y: cy(), radius: 60, intensity: 1.0 });
    });
    reg("breath_pulse", "breath pulse", () => this.breathPulse());
    reg("reseed", "reseed grammar", () => {
      opts.reseedFn?.();
      this._emitEvent({ kind: "shockwave", x: cx(), y: cy(), radius: 28, intensity: 1.5 });
    });
    reg("save_png", "save PNG", () => {
      this.visionMode?.savePNG();
      this._emitEvent({ kind: "flash", x: cx(), y: cy(), radius: 50, intensity: 1.3 });
    });
    reg("toggle_fullscreen", "fullscreen", () => {
      this.visionMode?.toggleFullscreen();
      this._emitEvent({ kind: "ripple", x: cx(), y: cy(), radius: 36, intensity: 1.0 });
    });
    reg("toggle_hud", "toggle HUD", () => {
      this.visionMode?.toggleHud();
      this._emitEvent({ kind: "ripple", x: cx(), y: cy(), radius: 22, intensity: 0.7 });
    });
    reg("toggle_pause", "pause / play", () => {
      opts.togglePauseFn?.();
      this._emitEvent({ kind: "still_pulse", x: cx(), y: cy(), radius: 50, intensity: 1.1 });
    });
    reg("exit_vision", "exit vision", () => this.visionMode?.exit());
    reg("open_command", "command phrase", () => {
      this._openCommand();
      this._emitEvent({ kind: "ripple", x: cx(), y: cy(), radius: 18, intensity: 0.6 });
    });
    reg("load_atlas", "load atlas", () => {
      this.visionMode?.applyPreset("current_field");
      this._emitEvent({ kind: "summon", x: cx(), y: cy(), radius: 70, intensity: 1.3 });
    });
    reg("copy_bundle", "copy bundle", () => {
      this.visionMode?.copyBundleToClipboard();
      this._emitEvent({ kind: "ripple", x: cx(), y: cy(), radius: 30, intensity: 0.9 });
    });
    for (const [num, key] of Object.entries(VISION_NUM_TO_KEY)) {
      reg("preset_" + num, "preset " + num, () => {
        this.visionMode?.applyPreset(key);
        this._emitEvent({ kind: "shockwave", x: cx(), y: cy(), radius: 38, intensity: 1.5 });
      });
    }
  }

  // Emit a small instance of the active tool's primary kind at center —
  // gives an instant sample of what the tool produces.
  _signatureBurst() {
    const tool = TOOLS[this.activeToolIdx];
    if (!tool) return;
    const ev = makeSymbolEvent({
      kind: tool.id,
      x: this.sim.W * 0.5,
      y: this.sim.H * 0.5,
      radius: 18,
      intensity: 1.2,
      birthTick: this.sim.tick,
      suppress: [],            // signature should not mute passes
    });
    this.sim.addSymbolEvent(ev);
    this.symbolHistory.unshift({ kind: tool.id, t: performance.now() });
    if (this.symbolHistory.length > 5) this.symbolHistory.length = 5;
    this._refreshHud();
  }

  // ── bindings (localStorage) ────────────────────────────────────

  _loadBindings() {
    try {
      const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
      if (Array.isArray(stored) && stored.length > 0) return stored;
    } catch { /* fall through */ }
    return [...DEFAULT_BINDINGS];
  }

  saveBindings() {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(this.bindings)); }
    catch { /* ignore */ }
  }

  resetBindings() {
    this.bindings = [...DEFAULT_BINDINGS];
    this.saveBindings();
  }

  _matchBinding(e) {
    const k = e.key;
    for (const b of this.bindings) {
      if (b.key !== k) continue;
      if (b.shift !== undefined && b.shift !== e.shiftKey) continue;
      if (b.ctrl  !== undefined && b.ctrl  !== e.ctrlKey)  continue;
      if (b.alt   !== undefined && b.alt   !== e.altKey)   continue;
      return b;
    }
    return null;
  }

  // ── tool / brush / tileset ─────────────────────────────────────

  setActiveTool(idx) {
    this.activeToolIdx = ((idx % TOOLS.length) + TOOLS.length) % TOOLS.length;
    this._refreshHud();
  }

  cycleTool(dir) { this.setActiveTool(this.activeToolIdx + dir); }

  cycleTileset(dir) {
    this.tilesetIdx = ((this.tilesetIdx + dir) % PALETTE_NAMES.length
                       + PALETTE_NAMES.length) % PALETTE_NAMES.length;
    this.state.paletteName = PALETTE_NAMES[this.tilesetIdx];
    const sel = document.getElementById("select_palette");
    if (sel) sel.value = this.state.paletteName;
    this._refreshHud();
  }

  setBrushSize(n) {
    this.brushSize = Math.max(3, Math.min(60, Math.round(n)));
    this._refreshHud();
  }

  // ── breath pulse ───────────────────────────────────────────────

  breathPulse() {
    this._emitEvent({
      kind: "breath",
      x: this.sim.W * 0.5,
      y: this.sim.H * 0.5,
      radius: Math.max(40, this.sim.W * 0.35),
      intensity: 1.0,
    });
  }

  // ── DOM event handlers ─────────────────────────────────────────

  _bindHandlers() {
    this._onKeyDown = (e) => {
      const tgt = e.target;
      if (tgt && (tgt.tagName === "INPUT" || tgt.tagName === "SELECT" ||
                  tgt.tagName === "TEXTAREA" || tgt.isContentEditable)) {
        return; // never steal keys while typing
      }
      this.lastInputMs = performance.now();
      const b = this._matchBinding(e);
      if (b) {
        e.preventDefault();
        this.dispatch(b.action);
        return;
      }
      // v0.9 — unbound keys still leave a small spark so every keypress
      // (except Escape, which exits) is felt visually.
      if (e.key === "Escape") return;
      // Skip pure modifier presses
      if (e.key === "Shift" || e.key === "Control" ||
          e.key === "Alt" || e.key === "Meta") return;
      const x = this.lastCursor.x || this.sim.W * 0.5;
      const y = this.lastCursor.y || this.sim.H * 0.5;
      this._emitEvent({ kind: "spark", x, y, radius: 8, intensity: 0.7 });
    };

    this._onMouseDown = (e) => {
      e.preventDefault();
      const pos = this._canvasToSim(e.clientX, e.clientY);
      this.lastCursor = pos;
      this.lastInputMs = performance.now();
      this.dragState = {
        button: e.button,
        shift: e.shiftKey, alt: e.altKey, ctrl: e.ctrlKey,
        startMs: performance.now(),
        startSim: { ...pos },
        last: { ...pos },
        moved: false,
        toolKind: this._resolveDragTool(e.button, e),
      };
      this.lastEmitMs = 0; // force first emit
      this._streamGesture(pos, this.dragState);
    };

    this._onMouseMove = (e) => {
      // Always track cursor (used by wheel + unbound keypress fallback)
      this.lastCursor = this._canvasToSim(e.clientX, e.clientY);
      this.lastInputMs = performance.now();
      if (!this.dragState) return;
      const pos = this.lastCursor;
      const dx = pos.x - this.dragState.last.x;
      const dy = pos.y - this.dragState.last.y;
      const drift = Math.hypot(pos.x - this.dragState.startSim.x,
                               pos.y - this.dragState.startSim.y);
      if (drift > CLICK_MAX_DRIFT_PX) this.dragState.moved = true;
      this.dragState.last = pos;
      this.dragState.dx = dx;
      this.dragState.dy = dy;
      this._streamGesture(pos, this.dragState);
    };

    this._onMouseUp = (e) => {
      if (!this.dragState) return;
      const pos = this._canvasToSim(e.clientX, e.clientY);
      const dur = performance.now() - this.dragState.startMs;
      // Ctrl+click → drop a symbol node (no drag)
      if (this.dragState.ctrl && !this.dragState.moved && dur < CLICK_TIME_MS) {
        this._emitEvent({
          kind: "symbol_node",
          x: pos.x, y: pos.y,
          radius: this.brushSize * 1.2,
          intensity: 1.2,
        });
      } else if (!this.dragState.moved && dur < CLICK_TIME_MS) {
        // Plain click without ctrl → small tap so a click always says hello
        this._emitEvent({
          kind: "tap",
          x: pos.x, y: pos.y,
          radius: this.brushSize,
          intensity: 1.0,
        });
      } else if (this.dragState.moved) {
        // End-of-stroke release pulse at final position
        this._emitEvent({
          kind: "release",
          x: pos.x, y: pos.y,
          radius: this.brushSize * 1.1,
          intensity: 0.9,
        });
      }
      this.dragState = null;
      this.lastInputMs = performance.now();
    };

    this._onWheel = (e) => {
      e.preventDefault();
      const dir = Math.sign(e.deltaY);
      this.setBrushSize(this.brushSize - dir * 2);
      this.lastInputMs = performance.now();
      // Show new brush size visually as a momentary ring at cursor
      this._emitEvent({
        kind: "brush_ring",
        x: this.lastCursor.x,
        y: this.lastCursor.y,
        radius: this.brushSize,
        intensity: 1.0,
      });
    };

    this._onContextMenu = (e) => e.preventDefault();
  }

  _resolveDragTool(button, e) {
    if (button === 2) return "void";       // right
    if (button === 1) return "vortex";     // middle
    if (button === 0) {
      if (e.shiftKey) return "flow";
      if (e.altKey)   return "helical";
      if (e.ctrlKey)  return null;         // ctrl handled on mouseup
      return TOOLS[this.activeToolIdx].id;
    }
    return null;
  }

  _streamGesture(pos, ds) {
    if (!ds.toolKind) return;
    const now = performance.now();
    if (now - this.lastEmitMs < EMIT_INTERVAL_MS) return;
    this.lastEmitMs = now;
    this._emitEvent({
      kind: ds.toolKind,
      x: pos.x,
      y: pos.y,
      radius: this.brushSize,
      intensity: 1.0,
      dx: ds.dx ?? 0,
      dy: ds.dy ?? 0,
      extra: ds.toolKind === "vortex" ? { dir: ds.shift ? -1 : 1 } : null,
    });
  }

  _emitEvent({ kind, x, y, radius, intensity = 1.0, dx = 0, dy = 0, extra = null }) {
    const ev = makeSymbolEvent({
      kind, x, y, radius, intensity, dx, dy, extra,
      birthTick: this.sim.tick,
    });
    this.sim.addSymbolEvent(ev);
    this.symbolHistory.unshift({ kind, t: performance.now() });
    if (this.symbolHistory.length > 5) this.symbolHistory.length = 5;
    this._refreshHud();
  }

  _canvasToSim(clientX, clientY) {
    const rect = this.canvas.getBoundingClientRect();
    const cx = (clientX - rect.left) / rect.width;
    const cy = (clientY - rect.top)  / rect.height;
    return {
      x: Math.max(0, Math.min(this.sim.W - 1, cx * this.sim.W)),
      y: Math.max(0, Math.min(this.sim.H - 1, cy * this.sim.H)),
    };
  }

  // ── HUD ────────────────────────────────────────────────────────

  _refreshHud() {
    const tool = TOOLS[this.activeToolIdx];
    const setText = (id, t) => {
      const el = document.getElementById(id);
      if (el) el.textContent = t;
    };
    setText("vis_tool",    tool ? tool.name : "—");
    setText("vis_brush",   String(this.brushSize));
    setText("vis_tileset", PALETTE_NAMES[this.tilesetIdx]);
    setText("vis_verb",    this.sim.dominantVerb || "—");
    const evlog = document.getElementById("vis_events");
    if (evlog) {
      if (this.symbolHistory.length === 0) {
        evlog.textContent = "—";
      } else {
        const now = performance.now();
        evlog.textContent = this.symbolHistory.map(s => {
          const age = Math.max(0, (now - s.t) / 1000);
          return `${s.kind} ${age.toFixed(1)}s`;
        }).join(" · ");
      }
    }
  }

  tick() {
    // Refresh dominant verb display once per visible tick (called from main)
    const el = document.getElementById("vis_verb");
    if (el) el.textContent = this.sim.dominantVerb || "—";

    // v0.9 — idle ambient.  When no input for >2.5s, emit a small bloom
    // at a quasi-random position every ~1.6s so the field keeps morphing.
    if (this.state.running === false) return;
    const now = performance.now();
    if (now - this.lastInputMs < 2500) return;
    if (now - this.lastIdleMs   < 1600) return;
    this.lastIdleMs = now;
    this._emitIdleDrift();
  }

  _emitIdleDrift() {
    const W = this.sim.W, H = this.sim.H;
    // Quasi-random position biased away from edges
    const t = performance.now() * 0.001;
    const ang = (t * 0.37 + Math.random() * 6.28) % 6.28318;
    const rad = 0.18 + 0.32 * Math.random();
    const x = W * (0.5 + Math.cos(ang) * rad);
    const y = H * (0.5 + Math.sin(ang) * rad);
    this._emitEvent({
      kind: "idle_drift", x, y,
      radius: 10 + Math.random() * 10,
      intensity: 0.7 + Math.random() * 0.3,
    });
  }

  // ── command phrase ─────────────────────────────────────────────

  _buildCommandInput() {
    if (this.cmdInputEl) return;
    const wrap = document.createElement("div");
    wrap.className = "command-phrase";
    wrap.id = "command_phrase";
    wrap.innerHTML = `
      <span class="cp-prefix">:</span>
      <input type="text" id="command_phrase_input" autocomplete="off" spellcheck="false">
      <span class="cp-status" id="command_phrase_status"></span>
    `;
    document.body.appendChild(wrap);
    this.cmdInputEl = wrap;
    const input = document.getElementById("command_phrase_input");
    input.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        e.preventDefault();
        this._closeCommand();
      } else if (e.key === "Enter") {
        e.preventDefault();
        const phrase = input.value;
        const status = this._runCommand(phrase);
        document.getElementById("command_phrase_status").textContent = status || "";
        input.value = "";
        if (!status || status === "ok") this._closeCommand();
      }
    });
  }

  _openCommand() {
    if (!this.cmdInputEl) return;
    this.cmdInputEl.classList.add("show");
    const input = document.getElementById("command_phrase_input");
    if (input) {
      input.value = "";
      input.focus();
    }
    document.getElementById("command_phrase_status").textContent = "";
  }

  _closeCommand() {
    if (!this.cmdInputEl) return;
    this.cmdInputEl.classList.remove("show");
    const input = document.getElementById("command_phrase_input");
    if (input) input.blur();
  }

  _runCommand(phrase) {
    const p = (phrase || "").trim().toLowerCase();
    if (!p) return "";
    // Tools
    for (const t of TOOLS) {
      if (p === t.id || p === t.verb || p === t.name.toLowerCase()) {
        const idx = TOOLS.indexOf(t);
        this.setActiveTool(idx);
        return "ok";
      }
    }
    // Numeric presets
    if (/^[1-6]$/.test(p)) {
      this.dispatch("preset_" + p);
      return "ok";
    }
    // Named presets
    const presetMap = {
      current: "current_field", today: "current_field", atlas: "current_field",
      cosmic: "cosmic_body_revelation", revelation: "cosmic_body_revelation",
      twist: "twisting_flame_spine",  flame: "twisting_flame_spine", spine: "twisting_flame_spine",
      soma: "soma_bloom_body",        bloom_body: "soma_bloom_body",
      bone: "quasicrystal_bone_temple", temple: "quasicrystal_bone_temple", qc: "quasicrystal_bone_temple",
      storm: "storm_marma_discharge", lightning: "storm_marma_discharge",
    };
    if (presetMap[p]) { this.visionMode?.applyPreset(presetMap[p]); return "ok"; }
    // Tilesets / palettes
    if (PALETTE_NAMES.includes(p)) {
      this.tilesetIdx = PALETTE_NAMES.indexOf(p);
      this.state.paletteName = p;
      const sel = document.getElementById("select_palette");
      if (sel) sel.value = p;
      this._refreshHud();
      return "ok";
    }
    // Numeric brush size
    const brushMatch = p.match(/^brush\s+(\d+)$/);
    if (brushMatch) { this.setBrushSize(parseInt(brushMatch[1], 10)); return "ok"; }
    // seed N
    const seedMatch = p.match(/^seed\s+(\d+)$/);
    if (seedMatch) {
      const s = parseInt(seedMatch[1], 10);
      if (Number.isFinite(s)) {
        this.state.seed = s;
        const inp = document.getElementById("seed_input");
        if (inp) inp.value = s;
        return "ok";
      }
    }
    // Plain commands
    if (p === "clear") {
      this.compositor?.resetHistory();
      this.sim.symbolEvents = [];
      return "ok";
    }
    if (p === "save")    { this.dispatch("save_png"); return "ok"; }
    if (p === "reseed")  { this.dispatch("reseed");   return "ok"; }
    if (p === "exit" || p === "quit") { this.dispatch("exit_vision"); return "ok"; }
    if (p === "breath") { this.dispatch("breath_pulse"); return "ok"; }
    if (p === "reset_bindings") { this.resetBindings(); return "ok"; }
    return "?";
  }
}
