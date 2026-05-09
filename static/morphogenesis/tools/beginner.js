// BeginnerController — default Vision Mode interaction.
// Simple, satisfying, beautiful.
//
//   Left click  → Bloom
//   Left drag   → shape (flow / mandala / twist / lightning by curve)
//   Right       → Void carve / clear
//   Wheel       → brush size
//   Tab         → cycle style
//   Space       → breath pulse
//   R           → reset field
//   S           → save PNG
//   F           → fullscreen
//   H           → hud
//   D           → toggle advanced (returns to v0.10 tool-based input)
//   Esc         → exit Vision Mode
//
// The recognizer classifies each gesture, the visualEvent module
// builds a SymbolEvent + composition lock from it, and the lock is
// installed on sim so unrelated passes are muted during the event's
// attack/peak window.

import { GestureRecognizer } from "./gesture.js";
import { buildVisualEvent } from "./visualEvent.js";
import { STYLES, STYLE_KEYS } from "../atlas/styles.js";
import { makeSymbolEvent } from "./symbolEvent.js";
import { TRANSITIONS } from "../render/intergenesis.js";
import { InteractionPhraseAnalyzer } from "./interactionPhrase.js";
import { PhraseRewardDirector } from "./phraseRewardDirector.js";

// v0.14 — map gesture intent → transition operator name.  Each style
// can override these (style.transitions.<intent>) for a custom feel.
const DEFAULT_INTENT_TO_TRANSITION = {
  bloom:      "bloom_to_eye",
  strike:     "filament_to_lightning",
  reveal:     "eye_to_star",
  flow:       "crystal_to_flow",
  mandala:    "membrane_to_cellular",
  twist:      "flow_to_crystal",
  lightning:  "filament_to_lightning",
  void_click: "density_to_void",
  void_drag:  "density_to_void",
};
// Optional per-style transition overrides
const STYLE_TRANSITIONS = {
  soma_watercolor: { bloom: "membrane_to_cellular", flow: "fluid_to_terrain", reveal: "smoke_to_body" },
  storm_nerve:     { bloom: "filament_to_lightning", flow: "filament_to_lightning", strike: "filament_to_lightning" },
  crystal_temple:  { bloom: "bloom_to_eye", flow: "flow_to_crystal", twist: "flow_to_crystal", mandala: "eye_to_star" },
  root_forest:     { bloom: "smoke_to_body", flow: "filament_to_root", twist: "body_to_root" },
  cosmic_body:     { bloom: "bloom_to_eye", reveal: "eye_to_star", mandala: "membrane_to_cellular" },
  smoke_lightning: { bloom: "filament_to_lightning", reveal: "smoke_to_body", flow: "filament_to_lightning" },
  flower_eye:      { bloom: "bloom_to_eye", reveal: "eye_to_star", mandala: "bloom_to_eye" },
  ash_field:       { bloom: "density_to_void", flow: "fluid_to_terrain", reveal: "body_to_root" },
};

const HUD_FADE_MS = 2800;

export class BeginnerController {
  constructor(opts) {
    this.sim       = opts.sim;
    this.state     = opts.state;
    this.canvas    = opts.canvas;
    this.compositor = opts.compositor;
    this.visionMode = opts.visionMode;
    this.advancedToggleFn = opts.advancedToggleFn;
    this.savePngFn  = opts.savePngFn;
    this.fullscreenFn = opts.fullscreenFn;
    this.hudToggleFn  = opts.hudToggleFn;
    this.exitFn       = opts.exitFn;

    this.gesture = new GestureRecognizer();
    this.gesture.onEnd((intent, payload) => this._fireEvent(intent, payload));
    this.gesture.onStream((p) => this._fireStream(p));

    // v0.15 — interaction phrase analyzer + reward director.  Every
    // gesture passes through here so the field reads HOW the user
    // moves, not just where.
    this.phraseAnalyzer = new InteractionPhraseAnalyzer();
    this.phraseDirector = new PhraseRewardDirector(this.sim);

    this.activeStyleIdx = 0;
    this.brushSize = 14;
    this.lastEvent = null;          // {label, t}
    this.attached = false;

    // v0.18 — diagnostic state for the debug HUD
    this.lastError = null;          // { msg, where, t }
    this.pointerActive = false;     // true while a button is held
    this.pointerButton = -1;

    this._bind();
  }

  attach() {
    if (this.attached) return;
    this.attached = true;
    document.addEventListener("keydown",   this._onKeyDown);
    this.canvas.addEventListener("mousedown", this._onMouseDown);
    document.addEventListener("mousemove", this._onMouseMove);
    document.addEventListener("mouseup",   this._onMouseUp);
    this.canvas.addEventListener("wheel",  this._onWheel, { passive: false });
    this.canvas.addEventListener("contextmenu", this._onContext);
    // v0.18 — pointer-state reset on every escape path.  Without these
    // a pointer can get "stuck down" if the user drags off-canvas, the
    // window loses focus, or pointer is cancelled by the OS.  After
    // that, every subsequent click would be misread as a continuation.
    this.canvas.addEventListener("pointercancel", this._onCancel);
    this.canvas.addEventListener("mouseleave",    this._onCancel);
    window.addEventListener("blur",      this._onCancel);
    document.addEventListener("visibilitychange", this._onVisChange);
    this._applyStyle(this.activeStyleIdx, false);
    this._refreshHud(true);
  }

  detach() {
    if (!this.attached) return;
    this.attached = false;
    document.removeEventListener("keydown",   this._onKeyDown);
    this.canvas.removeEventListener("mousedown", this._onMouseDown);
    document.removeEventListener("mousemove", this._onMouseMove);
    document.removeEventListener("mouseup",   this._onMouseUp);
    this.canvas.removeEventListener("wheel",  this._onWheel);
    this.canvas.removeEventListener("contextmenu", this._onContext);
    this.canvas.removeEventListener("pointercancel", this._onCancel);
    this.canvas.removeEventListener("mouseleave",    this._onCancel);
    window.removeEventListener("blur",      this._onCancel);
    document.removeEventListener("visibilitychange", this._onVisChange);
    this._resetPointer();
  }

  // v0.18 — full reset of gesture + pointer tracking.  Safe to call
  // anytime; idempotent.
  _resetPointer() {
    this.pointerActive = false;
    this.pointerButton = -1;
    if (this.gesture) this.gesture.cancel();
  }

  // v0.18 — debug snapshot for the profiler HUD
  getDebugState() {
    const lock = this.sim?.compositionLock;
    let lockRemainingMs = 0;
    if (lock?.activeUntilMs) {
      lockRemainingMs = Math.max(0, lock.activeUntilMs - performance.now());
    }
    return {
      eventCount:   this.sim?.symbolEvents?.length || 0,
      echoCount:    this.sim?.regionMap?.echoes?.length || 0,
      lockRemainingMs,
      lockLabel:    lock?.label || null,
      pointerActive: this.pointerActive,
      pointerButton: this.pointerButton,
      lastError:    this.lastError,
    };
  }

  // ── style ──────────────────────────────────────────────────────

  cycleStyle(dir = +1) {
    this.activeStyleIdx = ((this.activeStyleIdx + dir) % STYLE_KEYS.length
                          + STYLE_KEYS.length) % STYLE_KEYS.length;
    this._applyStyle(this.activeStyleIdx, true);
  }

  _applyStyle(idx, fanfare = false) {
    const style = STYLES[STYLE_KEYS[idx]];
    if (!style) return;
    Object.assign(this.state.elements, style.elements);
    this.state.paletteName = style.palette;
    if (style.energy    !== undefined) this.state.energy    = style.energy;
    if (style.replenish !== undefined) this.state.replenish = style.replenish;
    if (style.decay     !== undefined) this.state.decay     = style.decay;
    if (style.contrast  !== undefined) this.state.contrast  = style.contrast;
    if (style.exposure  !== undefined) this.state.exposure  = style.exposure;
    if (style.sacred) {
      Object.assign(this.state.sacred, style.sacred);
      if (style.sacred.phyllotaxy) {
        this.state.sacred.phyllotaxy = { ...this.state.sacred.phyllotaxy,
                                          ...style.sacred.phyllotaxy };
      }
      this.sim.rebuildSacred({
        yantraType: this.state.sacred.yantraType,
        mandala: { rings: this.state.sacred.mandalaRings,
                   gates: this.state.sacred.mandalaGates,
                   invert: !!this.state.sacred.mandalaInvert },
      });
      this.sim.setSacredParams({
        masterStrength:  this.state.sacred.masterStrength,
        vastuStrength:   this.state.sacred.vastuStrength,
        yantraStrength:  this.state.sacred.yantraStrength,
        mandalaStrength: this.state.sacred.mandalaStrength,
      });
    }
    // Mirror palette select if panel is visible
    const sel = document.getElementById("select_palette");
    if (sel) sel.value = this.state.paletteName;
    if (fanfare) {
      // Visible style-change feedback
      const ev = makeSymbolEvent({
        kind: "palette_swap",
        x: this.sim.W * 0.5, y: this.sim.H * 0.5,
        radius: 60, intensity: 1.0,
        birthTick: this.sim.tick, suppress: [],
      });
      this.sim.addSymbolEvent(ev);
    }
    this._refreshHud(true);
  }

  // ── gesture handlers ──────────────────────────────────────────

  // v0.18 — every click MUST produce a visible SymbolEvent.  Each side
  // path (phrase classification, reward director, regionMap transition,
  // VisualEvent build) is independently try/wrapped so one failure
  // never cancels the rest.  A guaranteed fallback splat fires last
  // if every other path produced nothing.
  _fireEvent(intent, payload) {
    const styleKey = STYLE_KEYS[this.activeStyleIdx];
    const style = STYLES[styleKey];
    const overrides = style?.eventBoosts?.[intent] || null;
    const lastP = payload.points[payload.points.length - 1] || payload;
    const prevP = payload.points[payload.points.length - 2] || lastP;
    const dx = lastP.x - prevP.x;
    const dy = lastP.y - prevP.y;
    const nowMs = performance.now();
    let firedSomething = false;
    let phrase = null;
    let phraseResult = null;
    let built = null;

    // 1. Phrase analysis (defensive — never blocks the rest)
    try {
      if (intent === "bloom" || intent === "strike" || intent === "reveal" ||
          intent === "void_click") {
        this.phraseAnalyzer.recordClick(nowMs, payload.button ?? 0);
      }
      phrase = this.phraseAnalyzer.classify(nowMs);
    } catch (err) {
      this._reportError("phraseAnalyzer", err);
      phrase = null;
    }

    // 2. Phrase-driven reward (independently wrapped)
    if (phrase && phrase.confidence >= 0.18) {
      try {
        phraseResult = this.phraseDirector.fire(
          phrase, intent, payload.x, payload.y, this.brushSize, nowMs,
        );
        if (phraseResult) firedSomething = true;
      } catch (err) {
        this._reportError("phraseDirector.fire", err);
        phraseResult = null;
      }
    }

    // 3. Default-mapping transition (always run if phrase didn't fire one).
    //    Independent try/catch so a regionMap error doesn't block step 4.
    if (!phraseResult) {
      try {
        const transitionKey =
          STYLE_TRANSITIONS[styleKey]?.[intent] ||
          DEFAULT_INTENT_TO_TRANSITION[intent] ||
          "bloom_to_eye";
        const tDef = TRANSITIONS[transitionKey];
        if (tDef && this.sim.regionMap) {
          const intensityMul = overrides?.intensityMul ?? 1.0;
          const radiusMul    = overrides?.radiusMul    ?? 1.0;
          this.sim.regionMap.applyTransition(
            transitionKey, payload.x, payload.y,
            intensityMul, (this.brushSize / 12) * 2.5 * radiusMul, nowMs,
          );
          firedSomething = true;
        }
      } catch (err) {
        this._reportError("regionMap.applyTransition", err);
      }
    }

    // 4. SymbolEvent — independently wrapped.  This is what the
    //    feature-extraction renderer actually reads for visible response.
    try {
      built = buildVisualEvent({
        intent, x: payload.x, y: payload.y,
        brushSize: this.brushSize, tick: this.sim.tick,
        dx, dy, styleOverrides: overrides,
      });
      if (built) {
        this.sim.addSymbolEvent(built.ev);
        this.sim.compositionLock = built.lock;
        firedSomething = true;
      }
    } catch (err) {
      this._reportError("buildVisualEvent", err);
      built = null;
    }

    // 5. Guarantee: if NOTHING above fired, drop a raw fallback bloom
    //    SymbolEvent so the user always sees a response.
    if (!firedSomething) {
      try {
        const fallback = makeSymbolEvent({
          kind: "bloom",
          x: payload.x ?? this.sim.W * 0.5,
          y: payload.y ?? this.sim.H * 0.5,
          radius: this.brushSize,
          intensity: 1.0,
          birthTick: this.sim.tick,
          suppress: [],
        });
        this.sim.addSymbolEvent(fallback);
      } catch (err) {
        this._reportError("fallback bloom", err);
      }
    }

    // HUD label — never blocks if any field is missing
    this.lastEvent = {
      label: phraseResult?.label ?? (built?.def?.label || intent),
      phrase, t: nowMs,
    };
    try { this._refreshHud(true); } catch (err) {
      this._reportError("_refreshHud", err);
    }
  }

  _reportError(where, err) {
    const msg = (err && err.message) ? err.message : String(err);
    this.lastError = { where, msg, t: performance.now() };
    if (typeof console !== "undefined") {
      console.warn(`[beginner.${where}]`, err);
    }
  }

  _fireStream(p) {
    // v0.14 — drag stream applies the active style's flow transition
    // along the cursor path.  Right-drag is always density_to_void.
    const styleKey = STYLE_KEYS[this.activeStyleIdx];
    const isVoid = p.button === 2;
    const intent = isVoid ? "void_drag" : "flow";
    const transitionKey = isVoid
      ? "density_to_void"
      : (STYLE_TRANSITIONS[styleKey]?.[intent] || DEFAULT_INTENT_TO_TRANSITION[intent]);
    if (transitionKey && TRANSITIONS[transitionKey]) {
      this.sim.regionMap.applyTransition(
        transitionKey, p.x, p.y,
        0.45,
        (this.brushSize / 12) * 1.6,
        performance.now(),
      );
    }
    // Light underlying field nudge so extractors have something to read
    const ev = makeSymbolEvent({
      kind: isVoid ? "void" : "tap",
      x: p.x, y: p.y,
      radius: this.brushSize * 0.65,
      intensity: 0.45,
      birthTick: this.sim.tick,
      suppress: isVoid ? ["reaction", "voronoi", "branch"] : [],
    });
    this.sim.addSymbolEvent(ev);
  }

  // ── DOM event bindings ─────────────────────────────────────────

  _bind() {
    this._onKeyDown = (e) => { try {
      const tgt = e.target;
      if (tgt && (tgt.tagName === "INPUT" || tgt.tagName === "SELECT" ||
                  tgt.tagName === "TEXTAREA" || tgt.isContentEditable)) return;
      const k = e.key;
      // v0.15 — record key events into the phrase analyzer for tap rhythm
      this.phraseAnalyzer.recordKey(performance.now(), k);
      switch (k) {
        case "Tab":     e.preventDefault();
                        this.cycleStyle(e.shiftKey ? -1 : +1); break;
        case " ":       e.preventDefault(); this._breathPulse(); break;
        case "r": case "R": this._reseed(); break;
        case "s": case "S": this.savePngFn?.(); break;
        case "f": case "F": this.fullscreenFn?.(); break;
        case "h": case "H": this.hudToggleFn?.(); break;
        case "d": case "D": this.advancedToggleFn?.(); break;
        case "Escape":  this.exitFn?.(); break;
        case "[":       this.cycleStyle(-1); break;
        case "]":       this.cycleStyle(+1); break;
      }
    } catch (err) { this._reportError("onKeyDown", err); } };

    this._onMouseDown = (e) => { try {
      e.preventDefault();
      const pos = this._canvasToSim(e.clientX, e.clientY);
      this.pointerActive = true;
      this.pointerButton = e.button;
      this.gesture.begin(pos.x, pos.y, performance.now(), e.button,
                         { shift: e.shiftKey, alt: e.altKey, ctrl: e.ctrlKey });
    } catch (err) { this._reportError("onMouseDown", err); this._resetPointer(); } };

    this._onMouseMove = (e) => { try {
      const pos = this._canvasToSim(e.clientX, e.clientY);
      // v0.15 — record every move into the phrase analyzer so phrase
      // classification has full motion context regardless of buttons.
      this.phraseAnalyzer.recordMove(pos.x, pos.y, performance.now());
      if (this.gesture.button < 0) return;
      this.gesture.move(pos.x, pos.y, performance.now());
    } catch (err) { this._reportError("onMouseMove", err); } };

    this._onMouseUp = (e) => { try {
      if (this.gesture.button < 0) {
        // Pointer state may have got stuck — reset just in case
        this._resetPointer();
        return;
      }
      const pos = this._canvasToSim(e.clientX, e.clientY);
      this.gesture.end(pos.x, pos.y, performance.now());
      this.gesture.cancel();
      this.pointerActive = false;
      this.pointerButton = -1;
    } catch (err) {
      this._reportError("onMouseUp", err);
      this._resetPointer();
    } };

    this._onWheel = (e) => { try {
      e.preventDefault();
      const dir = Math.sign(e.deltaY);
      this.brushSize = Math.max(4, Math.min(60, this.brushSize - dir * 2));
      this._refreshHud(true);
    } catch (err) { this._reportError("onWheel", err); } };

    this._onContext = (e) => e.preventDefault();

    // v0.18 — pointer-cancel paths.  Any of these can leave the gesture
    // in a "down" state otherwise, blocking subsequent clicks.
    this._onCancel = () => { try {
      this._resetPointer();
    } catch (err) { this._reportError("onCancel", err); } };

    this._onVisChange = () => { try {
      if (document.hidden) this._resetPointer();
    } catch (err) { this._reportError("onVisChange", err); } };
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

  _breathPulse() {
    const nowMs = performance.now();
    // v0.15 — if the recent phrase was chaotic vāta, breath ALIGNS the
    // sparks into a coherent constellation (eye → star at center +
    // 4 golden-angle satellites) instead of a plain breath bloom.
    const aligned = this.phraseDirector.alignWithBreath(nowMs);
    const ev = makeSymbolEvent({
      kind: "breath",
      x: this.sim.W * 0.5, y: this.sim.H * 0.5,
      radius: this.sim.W * (aligned ? 0.5 : 0.4),
      intensity: aligned ? 1.2 : 1.0,
      birthTick: this.sim.tick, suppress: [],
    });
    this.sim.addSymbolEvent(ev);
    this.lastEvent = {
      label: aligned ? "vāta · aligned by breath" : "Breath",
      t: nowMs,
    };
    this._refreshHud(true);
  }

  _reseed() {
    // Reset the canvas + grammar but keep current style
    this.sim.reset(
      Math.floor(Math.random() * 0x7fffffff),
      this.state.complexity, this.state.structure,
      {
        sacred: this.state.sacred,
        elements: this.state.elements,
      },
    );
    this.compositor?.resetHistory?.();
    this.lastEvent = { label: "Reset", t: performance.now() };
    this._refreshHud(true);
  }

  // ── HUD ────────────────────────────────────────────────────────

  _refreshHud(showFresh = false) {
    const set = (id, txt) => {
      const el = document.getElementById(id);
      if (el) el.textContent = txt;
    };
    const style = STYLES[STYLE_KEYS[this.activeStyleIdx]];
    set("beg_style", style?.name || "—");
    set("beg_brush", "brush " + this.brushSize);
    set("beg_last",  this.lastEvent?.label || "—");
    // v0.15 — show current phrase classification (subtle, secondary)
    const phrase = this.lastEvent?.phrase || this.phraseAnalyzer._lastPhrase;
    if (phrase) {
      set("beg_phrase",
        `${phrase.dosha} · ${phrase.guna} · ${phrase.rhythm}`);
    }
    if (showFresh) {
      const root = document.getElementById("beginner_hud");
      if (root) {
        root.classList.add("show");
        clearTimeout(this._hudTimer);
        this._hudTimer = setTimeout(() => root.classList.remove("show"), HUD_FADE_MS);
      }
    }
  }
}
