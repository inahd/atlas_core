// Bootstrap — DOM ↔ Sim ↔ Compositor ↔ Overlays.
// v0.4: expression modes, energy/replenish/decay/contrast/exposure controls,
// six-state phase machine, anti-collapse monitor, phosphor history.
// v0.6: embodiment / bhasma / quasicrystal layers from Atlas /field bundle.

import { Sim, DEFAULT_PASSES } from "./engine/sim.js";
import { Compositor } from "./render/compositor.js";
import { drawOverlays } from "./render/overlays.js";
import { Timeline } from "./render/timeline.js";
import { paramsFromElements } from "./atlas/elements.js";
import { PRESETS } from "./atlas/presets.js";
import { MODES } from "./atlas/modes.js";
import { RELATION_NAMES, RELATION_LABELS } from "./atlas/relations.js";
import { DEBUG_PRESETS, DEBUG_PRESET_KEYS, DEFAULT_GAINS } from "./atlas/debugPresets.js";
import { VisionMode } from "./visionMode.js";
import { computeAestheticContext } from "./atlas/aesthetics.js";
import { Profiler } from "./tools/profiler.js";

const SIM_W = 192;
const SIM_H = 192;

const state = {
  elements: { water: 0.5, air: 0.5, fire: 0.5, earth: 0.5, wood: 0.5, ether: 0.5 },
  seed: 4271,
  complexity: 0.55,
  structure: 0.45,
  paletteName: "cosmic",
  energy: 0.55,
  replenish: 0.55,
  decay: 0.95,
  contrast: 1.10,
  exposure: 1.00,
  showHistory: true,
  historyAlpha: 0.65,
  historyThreshold: 0.18,
  running: true,
  modeName: null,
  passes: { ...DEFAULT_PASSES },
  debugField: null,
  overlays: {
    streamlines: false,
    branch_filaments: true,
    coherence_rings: false,
    discharge_paths: false,
    nodes: false,
    void_mask: false,
  },
  phaseMode: "auto",
  phaseLocked: "bloom",
  interventions: 0,
  // v0.5 sacred-spatial state
  sacred: {
    masterStrength: 0.0,
    vastuStrength: 0.0,
    yantraType: "none",
    yantraStrength: 0.0,
    mandalaStrength: 0.0,
    mandalaRings: 0,
    mandalaGates: 0,
    mandalaInvert: false,
    phyllotaxy: { enabled: false, count: 48, scale: 4 },
  },
  // v0.7 director matrix
  embodimentGains: { ...DEFAULT_GAINS },
  stressTest: false,
};

const sim = new Sim(SIM_W, SIM_H);
sim.phaseMode = state.phaseMode;
sim.phaseLocked = state.phaseLocked;

const canvas = document.getElementById("canvas");
canvas.width = 720;
canvas.height = 720;
const compositor = new Compositor(canvas, SIM_W, SIM_H);
const timelineCanvas = document.getElementById("timeline_canvas");
const timeline = timelineCanvas ? new Timeline(timelineCanvas, 240) : null;

// ── DOM helpers ────────────────────────────────────────────────────

function $(id) { return document.getElementById(id); }

function initRelationsHUD() {
  const host = $("relations_panel");
  host.innerHTML = "";
  for (const name of RELATION_NAMES) {
    const row = document.createElement("div");
    row.className = "relation-row";
    row.innerHTML = `
      <span class="rname">${RELATION_LABELS[name]}</span>
      <div class="rbar"><div class="rfill" id="rel_${name}"></div></div>
      <span class="rval" id="rval_${name}">0.00</span>
    `;
    host.appendChild(row);
  }
}

function updateRelationsHUD(relations) {
  for (const name of RELATION_NAMES) {
    const v = relations[name] ?? 0;
    const fill = $(`rel_${name}`);
    const val = $(`rval_${name}`);
    if (fill) fill.style.width = (v * 100).toFixed(0) + "%";
    if (val) val.textContent = v.toFixed(2);
  }
}

function updateGrammarHUD() {
  const g = sim.grammar;
  if (!g) return;
  const counts = {};
  for (const ev of g.events) counts[ev.kind] = (counts[ev.kind] || 0) + 1;
  $("g_symmetry").textContent =
    g.symmetry + (g.symmetry === "radial" ? `(×${g.radialFold})` : "");
  $("g_total").textContent = g.events.length;
  $("g_focal").textContent = g.focalCount;
  $("g_void").textContent = g.voidCount;
  $("g_axis").textContent = g.dominantAxis;
  $("g_phase").textContent = sim.currentPhase();
  $("g_mode").textContent = g.mode || "(custom)";
  const order = ["attractor", "emitter", "sink", "shear_band", "rupture",
                 "bloom_node", "strike", "void_pocket",
                 "coherence_pulse", "pressure_ridge"];
  const parts = [];
  for (const k of order) {
    if (counts[k]) parts.push(`${k.replace("_", " ")}: ${counts[k]}`);
  }
  $("g_kinds").textContent = parts.join(" · ") || "(empty)";
}

function updateMonitorHUD() {
  $("m_var").textContent = sim.lastMonitor.fieldVariance.toFixed(4);
  $("m_black").textContent = (compositor.blackRatio * 100).toFixed(0) + "%";
  $("m_lum").textContent = compositor.avgLuminance.toFixed(2);
  $("m_strike").textContent = sim.collapseStrike;
  $("m_intervene").textContent = state.interventions;
}

// ── Sliders ─────────────────────────────────────────────────────────

function bindSlider(id, getter, setter, format = (v) => v.toFixed(2)) {
  const slider = $("slider_" + id);
  const display = $("val_" + id);
  slider.value = getter();
  display.textContent = format(getter());
  slider.addEventListener("input", () => {
    const v = parseFloat(slider.value);
    setter(v);
    display.textContent = format(v);
  });
}

const elementNames = ["water", "air", "fire", "earth", "wood", "ether"];
for (const name of elementNames) {
  bindSlider(name, () => state.elements[name], (v) => {
    state.elements[name] = v;
    state.modeName = null;
    $("mode_label").textContent = "(custom)";
  });
}

bindSlider("complexity", () => state.complexity, (v) => {
  state.complexity = v;
  sim.regenerateGrammar(state.seed, state.complexity, state.structure);
  updateGrammarHUD();
});

bindSlider("structure", () => state.structure, (v) => {
  state.structure = v;
  sim.regenerateGrammar(state.seed, state.complexity, state.structure);
  updateGrammarHUD();
});

bindSlider("energy", () => state.energy, (v) => state.energy = v);
bindSlider("replenish", () => state.replenish, (v) => state.replenish = v);
bindSlider("decay", () => state.decay, (v) => state.decay = v);
bindSlider("contrast", () => state.contrast, (v) => state.contrast = v);
bindSlider("exposure", () => state.exposure, (v) => state.exposure = v);
bindSlider("history_alpha", () => state.historyAlpha, (v) => state.historyAlpha = v);

// Seed
$("seed_input").value = state.seed;
$("seed_input").addEventListener("change", () => {
  const v = parseInt($("seed_input").value, 10);
  if (Number.isFinite(v)) state.seed = v;
});

function currentResetOpts() {
  return {
    sacred: {
      masterStrength: state.sacred.masterStrength,
      vastuStrength: state.sacred.vastuStrength,
      yantraType: state.sacred.yantraType,
      yantraStrength: state.sacred.yantraStrength,
      mandalaStrength: state.sacred.mandalaStrength,
      mandalaRings: state.sacred.mandalaRings,
      mandalaGates: state.sacred.mandalaGates,
      mandalaInvert: state.sacred.mandalaInvert,
      phyllotaxy: state.sacred.phyllotaxy.enabled
        ? state.sacred.phyllotaxy : { enabled: false },
    },
    elements: state.elements,
  };
}
$("btn_reset").addEventListener("click", () => {
  sim.reset(state.seed, state.complexity, state.structure, currentResetOpts());
  compositor.resetHistory();
  state.interventions = 0;
  updateGrammarHUD();
});
$("btn_random").addEventListener("click", () => {
  // Random reseeds the SCENE GRAMMAR, not pixel noise.
  state.seed = Math.floor(Math.random() * 0x7fffffff);
  $("seed_input").value = state.seed;
  sim.reset(state.seed, state.complexity, state.structure, currentResetOpts());
  compositor.resetHistory();
  state.interventions = 0;
  updateGrammarHUD();
});
$("btn_pause").addEventListener("click", () => {
  state.running = !state.running;
  $("btn_pause").textContent = state.running ? "pause" : "play";
});
$("btn_export").addEventListener("click", () => {
  const fn = `morphogenesis_${state.paletteName}_${state.seed}_${sim.tick}.png`;
  compositor.exportPNG(fn);
});
$("btn_clear_history").addEventListener("click", () => {
  compositor.resetHistory();
});

// Palette / debug
$("select_palette").addEventListener("change", () => {
  state.paletteName = $("select_palette").value;
});
$("select_debug").addEventListener("change", () => {
  const v = $("select_debug").value;
  state.debugField = v === "composite" ? null : v;
});

// Pass toggles
const passNames = [
  "replenish", "events", "sacred", "diffusion", "reaction", "curl", "advection",
  "branch", "discharge", "interference", "voronoi", "life",
  // v0.6
  "bhasma", "dhatu", "pulseMarma", "helicalShear", "tensegrity",
  "movementPhrase", "quasicrystal",
];
for (const p of passNames) {
  const cb = $("pass_" + p);
  if (!cb) continue;
  cb.checked = state.passes[p];
  cb.addEventListener("change", () => { state.passes[p] = cb.checked; });
}

// Overlay toggles (per-overlay + history toggle)
const overlayNames = [
  "streamlines", "branch_filaments", "coherence_rings",
  "discharge_paths", "nodes", "void_mask",
];
for (const o of overlayNames) {
  const cb = $("overlay_" + o);
  if (!cb) continue;
  cb.checked = state.overlays[o];
  cb.addEventListener("change", () => { state.overlays[o] = cb.checked; });
}
$("overlay_history").checked = state.showHistory;
$("overlay_history").addEventListener("change", () => {
  state.showHistory = $("overlay_history").checked;
});

// Phase
$("select_phase").addEventListener("change", () => {
  const v = $("select_phase").value;
  if (v === "auto") {
    state.phaseMode = "auto";
    sim.phaseMode = "auto";
  } else {
    state.phaseMode = "locked";
    state.phaseLocked = v;
    sim.phaseMode = "locked";
    sim.phaseLocked = v;
  }
});

// ── Expression Modes ──────────────────────────────────────────────

function applyMode(key) {
  const m = MODES[key];
  if (!m) return;
  state.modeName = key;

  // Elements
  for (const name of elementNames) {
    state.elements[name] = m.elements[name];
    $("slider_" + name).value = m.elements[name];
    $("val_" + name).textContent = m.elements[name].toFixed(2);
  }
  // Energy / decay / contrast / exposure
  state.energy = m.energy;
  $("slider_energy").value = m.energy;
  $("val_energy").textContent = m.energy.toFixed(2);

  state.replenish = m.replenish;
  $("slider_replenish").value = m.replenish;
  $("val_replenish").textContent = m.replenish.toFixed(2);

  state.decay = m.decay;
  $("slider_decay").value = m.decay;
  $("val_decay").textContent = m.decay.toFixed(2);

  state.contrast = m.contrast;
  $("slider_contrast").value = m.contrast;
  $("val_contrast").textContent = m.contrast.toFixed(2);

  state.exposure = m.exposure;
  $("slider_exposure").value = m.exposure;
  $("val_exposure").textContent = m.exposure.toFixed(2);

  // Grammar
  state.complexity = m.grammar.complexity;
  $("slider_complexity").value = m.grammar.complexity;
  $("val_complexity").textContent = m.grammar.complexity.toFixed(2);

  state.structure = m.grammar.structure;
  $("slider_structure").value = m.grammar.structure;
  $("val_structure").textContent = m.grammar.structure.toFixed(2);

  // Palette
  state.paletteName = m.palette;
  $("select_palette").value = m.palette;

  // Overlays
  for (const o of overlayNames) {
    const v = m.overlays[o] ?? false;
    state.overlays[o] = v;
    if ($("overlay_" + o)) $("overlay_" + o).checked = v;
  }
  state.showHistory = m.overlays.history ?? true;
  $("overlay_history").checked = state.showHistory;

  // v0.5 — sacred-spatial bundle
  if (m.sacred) {
    state.sacred.masterStrength  = m.sacred.masterStrength  ?? 0;
    state.sacred.vastuStrength   = m.sacred.vastuStrength   ?? 0;
    state.sacred.yantraType      = m.sacred.yantraType      ?? "none";
    state.sacred.yantraStrength  = m.sacred.yantraStrength  ?? 0;
    state.sacred.mandalaStrength = m.sacred.mandalaStrength ?? 0;
    state.sacred.mandalaRings    = m.sacred.mandalaRings    ?? 0;
    state.sacred.mandalaGates    = m.sacred.mandalaGates    ?? 0;
    state.sacred.mandalaInvert   = m.sacred.mandalaInvert   ?? false;
    state.sacred.phyllotaxy = {
      enabled: m.sacred.phyllotaxy?.enabled ?? false,
      count: m.sacred.phyllotaxy?.count ?? 48,
      scale: m.sacred.phyllotaxy?.scale ?? 4,
    };
  } else {
    // Mode without sacred-spatial config — clear all sacred fields
    state.sacred.masterStrength = 0;
    state.sacred.vastuStrength = 0;
    state.sacred.yantraType = "none";
    state.sacred.yantraStrength = 0;
    state.sacred.mandalaStrength = 0;
    state.sacred.mandalaRings = 0;
    state.sacred.mandalaGates = 0;
    state.sacred.mandalaInvert = false;
    state.sacred.phyllotaxy = { enabled: false, count: 48, scale: 4 };
  }
  // Push sacred values to UI
  $("slider_sacred_master").value = state.sacred.masterStrength;
  $("val_sacred_master").textContent = state.sacred.masterStrength.toFixed(2);
  $("slider_sacred_vastu").value = state.sacred.vastuStrength;
  $("val_sacred_vastu").textContent = state.sacred.vastuStrength.toFixed(2);
  $("slider_sacred_yantra").value = state.sacred.yantraStrength;
  $("val_sacred_yantra").textContent = state.sacred.yantraStrength.toFixed(2);
  $("slider_sacred_mandala").value = state.sacred.mandalaStrength;
  $("val_sacred_mandala").textContent = state.sacred.mandalaStrength.toFixed(2);
  $("select_yantra").value = state.sacred.yantraType;
  $("input_mandala_rings").value = state.sacred.mandalaRings;
  $("input_mandala_gates").value = state.sacred.mandalaGates;
  $("input_mandala_invert").checked = state.sacred.mandalaInvert;
  $("input_phyllotaxy_enabled").checked = state.sacred.phyllotaxy.enabled;
  $("input_phyllotaxy_count").value = state.sacred.phyllotaxy.count;
  $("input_phyllotaxy_scale").value = state.sacred.phyllotaxy.scale;

  // Seed + reset (with sacred + phyllotaxy bundle)
  state.seed = m.seed;
  $("seed_input").value = m.seed;
  sim.reset(state.seed, state.complexity, state.structure, {
    mode: m.name,
    symmetryHint: m.grammar.symmetryHint,
    sacred: m.sacred,
    elements: state.elements,
  });
  compositor.resetHistory();
  state.interventions = 0;
  $("mode_label").textContent = m.name;
  updateGrammarHUD();
}

// Wire mode buttons (v0.4 expression modes)
const modeKeys = [
  "capillary_bloom", "filament_memory", "interference_body",
  "crystal_pressure", "storm_discharge", "rohini_soma",
];
for (const key of modeKeys) {
  const btn = $("mode_" + key);
  if (btn) btn.addEventListener("click", () => applyMode(key));
}

// v0.5 sacred-spatial modes
const sacredModeKeys = [
  "rohini_soma_bloom", "ashwini_twin_discharge", "mula_root_inversion",
  "swati_wind_seed", "chitra_gem_lattice", "cosmic_body_mandala",
];
for (const key of sacredModeKeys) {
  const btn = $("mode_" + key);
  if (btn) btn.addEventListener("click", () => applyMode(key));
}

// ── Sacred-spatial controls ─────────────────────────────────────────

function rebuildSacredFromState() {
  // Push current state to sim (rebuild yantra mask + mandala + params)
  sim.rebuildSacred({
    yantraType: state.sacred.yantraType,
    mandala: {
      rings: state.sacred.mandalaRings,
      gates: state.sacred.mandalaGates,
      invert: state.sacred.mandalaInvert,
    },
  });
  sim.setSacredParams({
    masterStrength: state.sacred.masterStrength,
    vastuStrength: state.sacred.vastuStrength,
    yantraStrength: state.sacred.yantraStrength,
    mandalaStrength: state.sacred.mandalaStrength,
  });
}

function regenGrammarFromState() {
  // Regenerate grammar — phyllotaxy and elements may have shifted
  sim.regenerateGrammar(state.seed, state.complexity, state.structure, {
    phyllotaxy: state.sacred.phyllotaxy.enabled ? state.sacred.phyllotaxy : null,
    elements: state.elements,
  });
  updateGrammarHUD();
}

bindSlider("sacred_master", () => state.sacred.masterStrength,
           (v) => { state.sacred.masterStrength = v; rebuildSacredFromState(); });
bindSlider("sacred_vastu", () => state.sacred.vastuStrength,
           (v) => { state.sacred.vastuStrength = v; rebuildSacredFromState(); });
bindSlider("sacred_yantra", () => state.sacred.yantraStrength,
           (v) => { state.sacred.yantraStrength = v; rebuildSacredFromState(); });
bindSlider("sacred_mandala", () => state.sacred.mandalaStrength,
           (v) => { state.sacred.mandalaStrength = v; rebuildSacredFromState(); });

$("select_yantra").addEventListener("change", () => {
  state.sacred.yantraType = $("select_yantra").value;
  rebuildSacredFromState();
});

$("input_mandala_rings").addEventListener("change", () => {
  state.sacred.mandalaRings = parseInt($("input_mandala_rings").value, 10) || 0;
  rebuildSacredFromState();
});
$("input_mandala_gates").addEventListener("change", () => {
  state.sacred.mandalaGates = parseInt($("input_mandala_gates").value, 10) || 0;
  rebuildSacredFromState();
});
$("input_mandala_invert").addEventListener("change", () => {
  state.sacred.mandalaInvert = $("input_mandala_invert").checked;
  rebuildSacredFromState();
});

$("input_phyllotaxy_enabled").addEventListener("change", () => {
  state.sacred.phyllotaxy.enabled = $("input_phyllotaxy_enabled").checked;
  regenGrammarFromState();
});
$("input_phyllotaxy_count").addEventListener("change", () => {
  state.sacred.phyllotaxy.count = parseInt($("input_phyllotaxy_count").value, 10) || 0;
  if (state.sacred.phyllotaxy.enabled) regenGrammarFromState();
});
$("input_phyllotaxy_scale").addEventListener("change", () => {
  state.sacred.phyllotaxy.scale = parseFloat($("input_phyllotaxy_scale").value) || 4;
  if (state.sacred.phyllotaxy.enabled) regenGrammarFromState();
});

// Legacy presets (kept)
function applyPreset(key) {
  const p = PRESETS[key];
  if (!p) return;
  for (const name of elementNames) {
    state.elements[name] = p.elements[name];
    $("slider_" + name).value = p.elements[name];
    $("val_" + name).textContent = p.elements[name].toFixed(2);
  }
  state.seed = p.seed;
  $("seed_input").value = p.seed;
  state.paletteName = p.palette;
  $("select_palette").value = p.palette;
  $("mode_label").textContent = p.name;
  state.modeName = null;
  sim.reset(state.seed, state.complexity, state.structure, currentResetOpts());
  compositor.resetHistory();
  updateGrammarHUD();
}
$("btn_preset_rohini").addEventListener("click", () => applyPreset("rohini_growth"));
$("btn_preset_ashwini").addEventListener("click", () => applyPreset("ashwini_lightning"));
$("btn_preset_cosmic").addEventListener("click", () => applyPreset("cosmic_body"));
$("btn_preset_airwater").addEventListener("click", () => applyPreset("air_water_flesh"));

// ── v0.7 — Director gain matrix ────────────────────────────────────

const GAIN_NAMES = [
  "master", "bhasma", "dhatu", "pulseMarma",
  "helicalShear", "tensegrity", "movementPhrase", "quasicrystal",
];

function pushGainsToSim() {
  const g = state.embodimentGains;
  const m = g.master * (state.stressTest ? 2.0 : 1.0);
  sim.setEmbodimentStrengths({
    bhasma:         g.bhasma * m,
    dhatu:          g.dhatu * m,
    pulseMarma:     g.pulseMarma * m,
    helicalShear:   g.helicalShear * m,
    tensegrity:     g.tensegrity * m,
    movementPhrase: g.movementPhrase * m,
    quasicrystal:   g.quasicrystal * m,
  });
}

for (const name of GAIN_NAMES) {
  const slider = $("slider_gain_" + name);
  const display = $("val_gain_" + name);
  if (!slider || !display) continue;
  slider.value = state.embodimentGains[name];
  display.textContent = state.embodimentGains[name].toFixed(2);
  slider.addEventListener("input", () => {
    const v = parseFloat(slider.value);
    state.embodimentGains[name] = v;
    display.textContent = v.toFixed(2);
    pushGainsToSim();
  });
}

const stressToggle = $("toggle_stress");
if (stressToggle) {
  stressToggle.addEventListener("change", () => {
    state.stressTest = stressToggle.checked;
    pushGainsToSim();
  });
}

function applyGainsFromPreset(presetGains) {
  for (const name of GAIN_NAMES) {
    const v = presetGains[name] ?? 1.0;
    state.embodimentGains[name] = v;
    const slider = $("slider_gain_" + name);
    const display = $("val_gain_" + name);
    if (slider) slider.value = v;
    if (display) display.textContent = v.toFixed(2);
  }
  pushGainsToSim();
}

// ── v0.6 — Atlas embodiment bundle ─────────────────────────────────

function updateEmbodimentHUD() {
  const e = sim.embodiment;
  const b = sim.bhasmaStage;
  const q = sim.quasicrystalParams;
  const set = (id, v) => { const el = $(id); if (el) el.textContent = v ?? "—"; };

  if (e) {
    set("emb_region", e.body_region);
    set("emb_archetype", e.archetype);
    set("emb_graha_dhatu", `${e.graha ?? "—"} · ${e.dhatu ?? "—"}`);
    set("emb_asana", e.asana_that_loads);
    set("emb_pranayama", e.pranayama_that_loads);
    set("emb_marma", e.marma_at_this_region);
    set("emb_cycle", e.animation_cycle_ms);
  } else {
    for (const id of ["emb_region","emb_archetype","emb_graha_dhatu",
                       "emb_asana","emb_pranayama","emb_marma","emb_cycle"]) {
      set(id, "—");
    }
  }
  if (b) {
    set("bha_stage", b.stage);
    set("bha_tithi", `${b.tithi_pos ?? "—"} · ${b.paksha ?? "—"}`);
  } else {
    set("bha_stage", "—");
    set("bha_tithi", "—");
  }
  if (q && q.active) {
    set("qc_active", "ON");
    set("qc_fold", `${q.fold} · ${(q.strength ?? 0).toFixed(2)}`);
  } else {
    set("qc_active", "off");
    set("qc_fold", "—");
  }
}

async function loadAtlasBundle() {
  try {
    const r = await fetch("/field/morphogenesis");
    if (!r.ok) {
      console.warn("loadAtlasBundle: HTTP", r.status);
      return;
    }
    const bundle = await r.json();
    sim.setEmbodimentBundle(bundle);
    // Stash the live intent so Vision Mode HUD can render it
    sim.lastAtlasIntent = bundle.intent || null;
    updateEmbodimentHUD();
  } catch (err) {
    console.warn("loadAtlasBundle failed:", err);
  }
}

function clearAtlasBundle() {
  sim.embodiment = null;
  sim.bhasmaStage = null;
  sim.quasicrystalParams = { active: false, fold: 11, strength: 0, phason_amplitude: 0.3 };
  updateEmbodimentHUD();
}

const btnLoadAtlas = $("btn_load_atlas");
if (btnLoadAtlas) btnLoadAtlas.addEventListener("click", loadAtlasBundle);
const btnClearAtlas = $("btn_clear_atlas");
if (btnClearAtlas) btnClearAtlas.addEventListener("click", clearAtlasBundle);

// ── v0.7 — Debug presets ───────────────────────────────────────────

async function applyDebugPreset(key) {
  const p = DEBUG_PRESETS[key];
  if (!p) return;
  $("mode_label").textContent = p.name;

  if (p.kind === "atlas") {
    // Live Atlas state. Mode follows current mode (don't override).
    await loadAtlasBundle();
    applyGainsFromPreset(p.gains);
    return;
  }

  // Synthetic preset: apply base mode first (for elements/grammar/sacred),
  // then overwrite the embodiment/bhasma/qc payload.
  if (p.mode && MODES[p.mode]) {
    applyMode(p.mode);
  }
  sim.setEmbodimentBundle({
    embodiment: p.embodiment,
    bhasma_stage: p.bhasma_stage,
    quasicrystal: p.quasicrystal,
  });
  applyGainsFromPreset(p.gains);
  updateEmbodimentHUD();
}

for (const key of DEBUG_PRESET_KEYS) {
  const btn = $("dbg_" + key);
  if (btn) btn.addEventListener("click", () => applyDebugPreset(key));
}

// ── v0.7 — Vision Mode (fullscreen oracle) ─────────────────────────

function reseedCurrent() {
  state.seed = Math.floor(Math.random() * 0x7fffffff);
  const seedInput = $("seed_input");
  if (seedInput) seedInput.value = state.seed;
  sim.reset(state.seed, state.complexity, state.structure, currentResetOpts());
  compositor.resetHistory();
  state.interventions = 0;
  updateGrammarHUD();
}

function togglePause() {
  state.running = !state.running;
  const btn = $("btn_pause");
  if (btn) btn.textContent = state.running ? "pause" : "play";
}

const visionMode = new VisionMode({
  sim, state, compositor, canvas,
  applyGainsFromPreset,
  pushGainsToSim,
  loadAtlasBundle,
  updateEmbodimentHUD,
  togglePauseFn: togglePause,
  reseedFn: reseedCurrent,
});

const btnEnterVision = $("btn_enter_vision");
if (btnEnterVision) {
  btnEnterVision.addEventListener("click", () => visionMode.enter());
}

// ── Animation loop ─────────────────────────────────────────────────

initRelationsHUD();
applyMode("filament_memory"); // start in a non-collapsing mode
updateEmbodimentHUD();

// v0.13 — auto-enter Vision Mode on load.  Skip the browser-fullscreen
// request because that requires a user gesture; F still works to enter
// real fullscreen on demand.
visionMode.enter({ skipFullscreen: true });

// v0.16 — diagnostic profiler.  Hidden by default; backtick (`) toggles.
const profiler = new Profiler({
  sim,
  compositor,
  element: $("profiler_hud"),
});
window.addEventListener("keydown", (e) => {
  const tgt = e.target;
  if (tgt && (tgt.tagName === "INPUT" || tgt.tagName === "SELECT" ||
              tgt.tagName === "TEXTAREA" || tgt.isContentEditable)) return;
  if (e.key === "`") {
    e.preventDefault();
    profiler.toggle();
  }
});

let lastT = performance.now();
let fps_smooth = 30;
let relUpdateTick = 0;
let monUpdateTick = 0;

// P5 (issue #8) — fixed-timestep simulation accumulator.
// Decouples sim cadence from render cadence.  When frame budget is
// exceeded (auto-quality flag), sim runs at 30Hz instead of 60Hz so
// the render loop stays responsive while events keep moving.
const TARGET_SIM_DT_MS = 16.667;
let _simAccumulatorMs = 0;

function frame(t) {
  const dt = t - lastT;
  lastT = t;
  fps_smooth = fps_smooth * 0.92 + (1000 / Math.max(1, dt)) * 0.08;
  $("fps").textContent = fps_smooth.toFixed(0);

  // v0.16 — profiler frame begin
  profiler.beginFrame(t);

  // P5 (issue #8) — fixed-timestep with budget-aware step cap.
  // - Normal mode: up to 2 steps/frame (catches up after a hiccup)
  // - Auto-quality mode (sustained <30 fps): max 1 step/frame so the
  //   render loop stays responsive instead of falling further behind.
  if (state.running) {
    _simAccumulatorMs += dt;
    if (_simAccumulatorMs > 100) _simAccumulatorMs = 100;  // cap to avoid spiral
    const maxSteps = profiler.autoQuality ? 1 : 2;
    let stepsThisFrame = 0;
    while (_simAccumulatorMs >= TARGET_SIM_DT_MS && stepsThisFrame < maxSteps) {
      profiler.beginSim();
      const params = paramsFromElements(state.elements);
      const guardBoost = (sim.guard?.lumaLow || sim.guard?.varianceLow) ? 1.6 : 1.0;
      const visionReplenish = visionMode.active ? visionMode.replenishBoost : 1.0;
      params.replenish = {
        energy: state.energy,
        replenish: state.replenish * guardBoost * visionReplenish,
        decay: state.decay,
      };
      sim.step(params, state.passes, state.elements);
      if (timeline) timeline.push(sim.passActivity);
      profiler.endSim();
      _simAccumulatorMs -= TARGET_SIM_DT_MS;
      stepsThisFrame++;
    }
    // If we have leftover accumulator > 1 step in degraded mode, drain
    // half so it doesn't grow unbounded under sustained pressure
    if (profiler.autoQuality && _simAccumulatorMs > TARGET_SIM_DT_MS) {
      _simAccumulatorMs *= 0.5;
    }
  }
  profiler.sample();

  // v0.7 exposure floor when guard active — never let exposure push the
  // canvas below shyama floor; bump effective exposure if luma is low.
  // Vision Mode tightens the floor and applies its preset's exposureBoost.
  const baseFloor = sim.guard?.lumaLow ? 0.95 : 0.7;
  const visionFloor = visionMode.active ? 0.92 : 0;
  const exposureFloor = Math.max(baseFloor, visionFloor);
  const visionMul = visionMode.active ? visionMode.exposureBoost : 1.0;
  const effExposure = Math.max(state.exposure, exposureFloor) * visionMul;

  // v0.10 aesthetic context — turns the symbolic state of the engine
  // (dhātu / bhasma / dominant verb / tithi / lo shu / primes) into
  // per-frame color modulation.
  const aesthetic = computeAestheticContext(sim);

  profiler.beginRender();
  // Compose — v0.14 routes through intergenesis renderer when in
  // beginner Vision Mode (or any mode with a regionMap).  Advanced mode
  // and field-debug select still get the legacy palette path.
  const useIntergenesis = visionMode.active && !visionMode.advanced && !state.debugField;
  // P5 — under auto-quality, skip the per-pixel aesthetic tint pass
  // (rotateHue is one of the larger overlay costs)
  const aestheticToUse = profiler.autoQuality ? null : aesthetic;
  compositor.paint(sim.stack, state.paletteName, {
    relations: sim.relations,
    debugField: state.debugField,
    contrast: state.contrast,
    exposure: effExposure,
    historyDecay: 0.96 + 0.035 * state.decay,
    historyAlpha: state.historyAlpha,
    showHistory: state.showHistory,
    threshold: state.historyThreshold,
    aesthetic: aestheticToUse,
    regionMap: useIntergenesis ? sim.regionMap : null,
  });
  profiler.endRender();

  // Overlays — only when not in debug-field mode
  if (!state.debugField) {
    drawOverlays(
      compositor.ctx, sim.stack, sim.grammar, canvas,
      state.overlays, sim.tick
    );
  }

  // Anti-collapse monitor
  if (state.running && !state.debugField) {
    const intervened = sim.collapseMonitor(
      compositor.blackRatio, compositor.avgLuminance
    );
    if (intervened) state.interventions++;
  }

  // HUD updates throttled
  if (++relUpdateTick % 6 === 0) {
    updateRelationsHUD(sim.relations);
    if (sim.phaseMode === "auto") {
      $("g_phase").textContent = sim.currentPhase();
    }
  }
  if (++monUpdateTick % 12 === 0) {
    updateMonitorHUD();
    updateEmbodimentHUD();
    if (timeline) timeline.render();
    const gel = $("g_guard");
    if (gel) {
      const flags = [];
      if (sim.guard?.lumaLow) flags.push("luma↓");
      if (sim.guard?.varianceLow) flags.push("var↓");
      if (state.stressTest) flags.push("stress×2");
      gel.textContent = flags.length ? flags.join(" ") : "ok";
    }
  }
  $("tick").textContent = sim.tick;
  visionMode.tick(fps_smooth);
  // v0.16 — profiler render (throttled internally)
  // v0.18 — pull lifecycle debug snapshot from beginner controller
  profiler.render({
    phraseSamples: visionMode.beginner?.phraseAnalyzer?.moves?.length || 0,
    debug: visionMode.beginner?.getDebugState?.() || {},
  });
  requestAnimationFrame(frame);
}
updateGrammarHUD();
requestAnimationFrame(frame);
