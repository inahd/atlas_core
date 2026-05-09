// Vision Mode — fullscreen oracle interface around the v0.6 engine.
// No new engine concepts; this is a presentation layer that:
//   - puts the canvas fullscreen, hides debug panels
//   - applies a vision preset (overrides elements/sacred/embodiment/
//     bhasma/qc/intent + gain matrix + exposure boost)
//   - shows a fading minimal HUD on mouse move / H key
//   - binds keyboard shortcuts (1-6 presets, F/H/L/R/S/Esc/Space)
//
// Presets call already-existing hooks:
//   - elements set on state.elements (read live in frame loop)
//   - sacred via sim.rebuildSacred + sim.setSacredParams
//   - embodiment/bhasma/qc via sim.setEmbodimentBundle
//   - phase by setting sim.phaseLocked / sim.phaseMode
//   - gains via applyGainsFromPreset (pushed to sim)
//   - intent stored on the controller for HUD rendering only
//   - exposureBoost multiplies effective exposure in main.js frame loop

import { VISION_PRESETS } from "./atlas/visionPresets.js";
import { InputController } from "./tools/inputController.js";
import { BeginnerController } from "./tools/beginner.js";

const HUD_FADE_MS = 3000;

export class VisionMode {
  constructor(opts) {
    this.sim = opts.sim;
    this.state = opts.state;
    this.compositor = opts.compositor;
    this.canvas = opts.canvas;
    this.applyGainsFromPreset = opts.applyGainsFromPreset;
    this.pushGainsToSim = opts.pushGainsToSim;
    this.loadAtlasBundle = opts.loadAtlasBundle;
    this.updateEmbodimentHUD = opts.updateEmbodimentHUD;
    this.togglePauseFn = opts.togglePauseFn;
    this.reseedFn = opts.reseedFn;

    this.active = false;
    this.intent = null;            // override for HUD rendering
    this.exposureBoost = 1.0;
    this.replenishBoost = 1.0;
    this.currentPresetKey = null;

    this._hudEl = document.getElementById("vision_hud");
    this._hudContent = document.getElementById("vision_hud_content");
    this._hudFps = document.getElementById("vision_hud_fps");
    this._hudPreset = document.getElementById("vision_hud_preset");
    this._hudTools = document.getElementById("vision_tools");
    this._hudTimer = null;
    this._hudVisible = false;

    // v0.8 — gamer-style mouse + keyboard input.  Owns its own keydown
    // listener; we no longer bind keys here.
    this.input = new InputController({
      sim: this.sim,
      state: this.state,
      canvas: this.canvas,
      compositor: this.compositor,
      visionMode: this,
      togglePauseFn: opts.togglePauseFn,
      reseedFn: opts.reseedFn,
    });

    // v0.13 — Beginner controller is the default.  Gesture recognition,
    // 8 named styles, composition lock, simple HUD.  D key toggles
    // advanced (the v0.8 tool-based input).
    this.beginner = new BeginnerController({
      sim: this.sim,
      state: this.state,
      canvas: this.canvas,
      compositor: this.compositor,
      visionMode: this,
      advancedToggleFn: () => this.toggleAdvanced(),
      savePngFn:    () => this.savePNG(),
      fullscreenFn: () => this.toggleFullscreen(),
      hudToggleFn:  () => this.toggleHud(),
      exitFn:       () => this.exit(),
    });
    this.advanced = false;

    this._bindMouse();
    this._bindFullscreenChange();
  }

  // v0.13 — flip between beginner gesture mode and advanced tool mode
  toggleAdvanced() {
    if (this.advanced) {
      this.input.detach();
      this.beginner.attach();
      this.advanced = false;
      document.body.classList.remove("advanced-mode");
    } else {
      this.beginner.detach();
      this.input.attach();
      this.advanced = true;
      document.body.classList.add("advanced-mode");
    }
  }

  enter(opts = {}) {
    if (this.active) return;
    this.active = true;
    document.body.classList.add("vision-mode");
    if (!opts.skipFullscreen) {
      const root = document.documentElement;
      if (root.requestFullscreen) {
        root.requestFullscreen().catch(() => {});
      }
    }
    // v0.13 — beginner mode is default
    this.beginner.attach();
    this.advanced = false;
    this._showHud();
    this._scheduleHudFade();
  }

  exit() {
    if (!this.active) return;
    this.active = false;
    document.body.classList.remove("vision-mode");
    document.body.classList.remove("advanced-mode");
    this.intent = null;
    this.exposureBoost = 1.0;
    this.replenishBoost = 1.0;
    if (document.fullscreenElement) {
      document.exitFullscreen().catch(() => {});
    }
    this.input.detach();
    this.beginner.detach();
    this._hideHud();
  }

  toggleFullscreen() {
    if (document.fullscreenElement) {
      document.exitFullscreen().catch(() => {});
    } else {
      document.documentElement.requestFullscreen().catch(() => {});
    }
  }

  toggleHud() {
    if (this._hudVisible) {
      this._hideHud();
    } else {
      this._showHud();
      this._scheduleHudFade();
    }
  }

  // Called once per frame from main.js — updates fps display + verb readout.
  tick(fps) {
    if (!this.active) return;
    if (this._hudVisible && this._hudFps) {
      this._hudFps.textContent = fps.toFixed(0) + " fps";
    }
    if (this.advanced) this.input.tick();
  }

  async applyPreset(key) {
    const p = VISION_PRESETS[key];
    if (!p) return;
    this.currentPresetKey = key;
    if (this._hudPreset) this._hudPreset.textContent = p.name;

    if (p.kind === "atlas") {
      await this.loadAtlasBundle();
      this.intent = this._extractIntentFromSim();
      this.exposureBoost = p.exposureBoost ?? 1.0;
      this.replenishBoost = 1.10;
      if (p.gains) this.applyGainsFromPreset(p.gains);
      this._renderHud();
      this._showHud();
      this._scheduleHudFade();
      return;
    }

    // Synthetic: apply each override layer in dependency order.
    if (p.elements) this._applyElements(p.elements);
    if (p.sacred)   this._applySacred(p.sacred);
    if (p.phase)    this._applyPhase(p.phase);

    this.sim.setEmbodimentBundle({
      embodiment: p.embodiment,
      bhasma_stage: p.bhasma_stage,
      quasicrystal: p.quasicrystal,
    });

    this.intent = p.intent || null;
    this.exposureBoost = p.exposureBoost ?? 1.0;
    this.replenishBoost = 1.15;

    if (p.gains) this.applyGainsFromPreset(p.gains);

    this.updateEmbodimentHUD?.();
    this._renderHud();
    this._showHud();
    this._scheduleHudFade();
  }

  copyBundleToClipboard() {
    const bundle = {
      intent: this.intent,
      embodiment: this.sim.embodiment,
      bhasma_stage: this.sim.bhasmaStage,
      quasicrystal: this.sim.quasicrystalParams,
      elements: { ...this.state.elements },
      sacred: { ...this.state.sacred },
      gains: { ...this.state.embodimentGains },
      preset: this.currentPresetKey,
    };
    const txt = JSON.stringify(bundle, null, 2);
    if (navigator.clipboard?.writeText) {
      navigator.clipboard.writeText(txt).catch(() => {});
    }
  }

  savePNG() {
    const stamp = Date.now();
    const tag = this.currentPresetKey || "vision";
    this.compositor.exportPNG(`vision_${tag}_${stamp}.png`);
  }

  // ── private helpers ─────────────────────────────────────────────

  _applyElements(elements) {
    Object.assign(this.state.elements, elements);
    for (const [k, v] of Object.entries(elements)) {
      const slider = document.getElementById("slider_" + k);
      const val    = document.getElementById("val_" + k);
      if (slider) slider.value = v;
      if (val)    val.textContent = v.toFixed(2);
    }
  }

  _applySacred(sacred) {
    Object.assign(this.state.sacred, sacred);
    if (sacred.phyllotaxy) {
      this.state.sacred.phyllotaxy = { ...this.state.sacred.phyllotaxy, ...sacred.phyllotaxy };
    }
    this.sim.rebuildSacred({
      yantraType: this.state.sacred.yantraType,
      mandala: {
        rings:  this.state.sacred.mandalaRings,
        gates:  this.state.sacred.mandalaGates,
        invert: this.state.sacred.mandalaInvert,
      },
    });
    this.sim.setSacredParams({
      masterStrength:  this.state.sacred.masterStrength,
      vastuStrength:   this.state.sacred.vastuStrength,
      yantraStrength:  this.state.sacred.yantraStrength,
      mandalaStrength: this.state.sacred.mandalaStrength,
    });
  }

  _applyPhase(phase) {
    this.state.phaseMode = "locked";
    this.state.phaseLocked = phase;
    this.sim.phaseMode = "locked";
    this.sim.phaseLocked = phase;
    const sel = document.getElementById("select_phase");
    if (sel) sel.value = phase;
  }

  _extractIntentFromSim() {
    // The Atlas bundle's intent isn't stored on sim; if the load helper
    // attached it, surface it. Otherwise return null and HUD shows
    // embodiment/bhasma/qc only.
    return this.sim.lastAtlasIntent || null;
  }

  _showHud() {
    if (!this._hudEl) return;
    this._hudEl.classList.add("show");
    if (this._hudTools) this._hudTools.classList.add("show");
    this._hudVisible = true;
    this._renderHud();
  }

  _hideHud() {
    if (!this._hudEl) return;
    this._hudEl.classList.remove("show");
    if (this._hudTools) this._hudTools.classList.remove("show");
    this._hudVisible = false;
  }

  _scheduleHudFade(ms = HUD_FADE_MS) {
    if (this._hudTimer) clearTimeout(this._hudTimer);
    this._hudTimer = setTimeout(() => this._hideHud(), ms);
  }

  _renderHud() {
    if (!this._hudContent) return;
    const e = this.sim.embodiment;
    const b = this.sim.bhasmaStage;
    const q = this.sim.quasicrystalParams;
    const i = this.intent;
    const rows = [];
    const row = (k, v) => rows.push(`<span class="k">${k}</span><span class="v">${v}</span>`);

    if (i) {
      if (i.intention)          row("intention", i.intention);
      if (i.phase)              row("phase", i.phase);
      if (i.hiddenForm)         row("hidden form", i.hiddenForm);
      if (i.transformationGoal) row("transformation", i.transformationGoal);
    }
    if (e) {
      if (e.body_region)            row("region", e.body_region);
      if (e.asana_that_loads)       row("asana", e.asana_that_loads);
      if (e.pranayama_that_loads)   row("pranayama", e.pranayama_that_loads);
      if (e.marma_at_this_region)   row("marma", e.marma_at_this_region);
    }
    if (b?.stage) row("bhasma", b.stage);
    if (q) row("quasicrystal", q.active ? `${q.fold}-fold · ${(q.strength ?? 0).toFixed(2)}` : "off");

    this._hudContent.innerHTML = rows.join("");
  }

  _bindMouse() {
    document.addEventListener("mousemove", () => {
      if (!this.active) return;
      this._showHud();
      this._scheduleHudFade();
    });
  }

  _bindFullscreenChange() {
    document.addEventListener("fullscreenchange", () => {
      // If the user pressed browser-native Esc, also exit vision mode.
      if (this.active && !document.fullscreenElement) {
        this.exit();
      }
    });
  }

  // Keyboard handling moved to InputController (v0.8). Keys are routed
  // through the action registry and dispatched only while the controller
  // is attached (i.e. while Vision Mode is active).
}
