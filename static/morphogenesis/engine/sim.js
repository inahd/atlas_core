// Simulation orchestrator — fields, passes, time step, grammar, sacred-spatial.
// v0.5: vastu/yantra/mandala fields built on reset, applied each tick.
// v0.6: embodiment + bhasma + quasicrystal layers (asana/marma/dhatu hidden grammar).

import { mulberry32 } from "./prng.js";
import { Grid } from "./grid.js";
import { FieldStack } from "./fields.js";
import { diffusionPass } from "../passes/diffusion.js";
import { curlFlowPass, advectionPass } from "../passes/advection.js";
import { reactionPass } from "../passes/reaction.js";
import { branchMemoryPass } from "../passes/branchMemory.js";
import { dischargePass } from "../passes/discharge.js";
import { InterferenceField } from "../passes/interference.js";
import { VoronoiField } from "../passes/voronoi.js";
import { applyEvents, seedEvents, replenishPass } from "../passes/events.js";
import { applySacred } from "../passes/sacred.js";
import { bhasmaCalcinationPass } from "../passes/bhasmaCalcination.js";
import { quasicrystalPass, QuasicrystalState } from "../passes/quasicrystal.js";
import { dhatuMaterialPass } from "../passes/dhatuMaterial.js";
import { pulseMarmaPass } from "../passes/pulseMarma.js";
import { helicalShearPass } from "../passes/helicalShear.js";
import { tensegrityPass } from "../passes/tensegrity.js";
import { movementPhrasePass } from "../passes/movementPhrase.js";
import { generateGrammar, autoPhase } from "../atlas/grammar.js";
import { computeRelations } from "../atlas/relations.js";
import { buildVastuContext } from "../atlas/vastu.js";
import { buildYantraMask } from "../atlas/yantra.js";
import { buildMandalaContext } from "../atlas/mandala.js";
import { applySymbolEvent, eventEnvelope } from "../tools/symbolEvent.js";
import { primeBeat, loShuCell } from "../atlas/aesthetics.js";
import { RegionMap } from "../render/intergenesis.js";

export const DEFAULT_PASSES = {
  replenish: true,
  events: true,
  sacred: true,            // v0.5
  diffusion: true,
  reaction: true,
  curl: true,
  advection: true,
  branch: true,
  discharge: true,
  interference: true,
  voronoi: true,
  life: true,
  // v0.6 — embodiment / bhasma / quasicrystal
  bhasma: true,
  quasicrystal: true,
  dhatu: true,
  pulseMarma: true,
  helicalShear: true,
  tensegrity: true,
  movementPhrase: true,
};

const COLLAPSE_THRESHOLDS = {
  fieldVarianceMin: 0.002,
  blackRatioMax: 0.55,
  avgLuminanceMin: 0.07,
  consecutiveTicks: 90,
  cooldown: 240,
};

// P1 (issue #8) — caps to prevent unbounded growth under long drags
const MAX_SYMBOL_EVENTS = 200;
const MAX_ECHOES = 50;

export class Sim {
  constructor(W, H) {
    this.W = W;
    this.H = H;
    this.grid = new Grid(W, H);
    this.stack = new FieldStack(W, H);
    this.interference = new InterferenceField(W, H, 6);
    this.voronoi = new VoronoiField(W, H, 10);
    this.tick = 0;
    this.relations = {};
    this.stats = {};
    this.grammar = null;
    this.phaseMode = "auto";
    this.phaseLocked = "bloom";

    // v0.5 sacred-spatial context
    this.sacredCtx = {
      vastu: buildVastuContext(W, H),
      yantraMask: null,        // built per-mode
      yantraType: "none",
      mandala: null,
      mandalaOpts: null,
    };
    this.sacredParams = {
      masterStrength: 0,
      vastuStrength: 0,
      yantraStrength: 0,
      mandalaStrength: 0,
    };

    // v0.6 — embodiment / bhasma / quasicrystal state
    this.embodiment = null;
    this.bhasmaStage = null;
    this.quasicrystalState = new QuasicrystalState(W, H);
    this.quasicrystalParams = { active: false, fold: 11, strength: 0, phason_amplitude: 0.3 };
    this.embodimentStrengths = {
      bhasma: 1.0,
      quasicrystal: 1.0,
      dhatu: 1.0,
      pulseMarma: 1.0,
      helicalShear: 1.0,
      tensegrity: 1.0,
      movementPhrase: 1.0,
    };

    this.collapseStrike = 0;
    this.collapseLastIntervention = -1000;
    this.lastMonitor = { fieldVariance: 0, blackRatio: 0, avgLuminance: 0 };

    // v0.7 — per-pass activity for timeline + guard signals
    this.passActivity = {
      bhasma: 0, dhatu: 0, pulseMarma: 0,
      helicalShear: 0, tensegrity: 0, movementPhrase: 0, quasicrystal: 0,
    };
    this.guard = {
      lumaLow: false,
      varianceLow: false,
      consec: 0,
      lastBoost: -1000,
    };

    // v0.8 — gesture-driven SymbolEvents.  Each tick, every active event
    // applies its envelope-shaped contribution to the field stack, and
    // its `suppress` list mutes competing passes for the tick.
    this.symbolEvents = [];
    this.dominantVerb = null;
    this._suppressed = new Set();

    // v0.13 — Composition lock.  When a beginner gesture fires, this
    // is set to {dominant, suppress, activeUntilTick}.  While active,
    // unrelated passes are muted so the gesture reads as a single
    // dominant visual family.  Cleared automatically when expired.
    this.compositionLock = null;

    // v0.14 — Intergenesis region map (16×16 visual-state grid).
    // Drives the new feature-extraction renderer.  The map is stepped
    // every frame and updated by transition events from the user.
    this.regionMap = new RegionMap(W, H);
  }

  // P1 (issue #8) — cap active SymbolEvents.  When the cap is hit, drop
  // the worst event by score:
  //    score = (isMemoryPhase ? 0 : 100) + intensity*10 − ageRatio*50
  // i.e. memory-phase events go first, then lowest-intensity / oldest.
  // Echoes scheduled in regionMap.echoes are capped separately below.
  addSymbolEvent(ev) {
    if (!ev) return;
    this.symbolEvents.push(ev);
    if (this.symbolEvents.length > MAX_SYMBOL_EVENTS) {
      this._evictSymbolEvent();
    }
    // Cap regionMap echoes too — they spawn future events, and a long
    // erratic gesture can pile up dozens.
    if (this.regionMap && this.regionMap.echoes &&
        this.regionMap.echoes.length > MAX_ECHOES) {
      // Drop oldest scheduled echo (smallest tMs)
      let worstIdx = 0, worstT = Infinity;
      for (let i = 0; i < this.regionMap.echoes.length; i++) {
        if (this.regionMap.echoes[i].tMs < worstT) {
          worstT = this.regionMap.echoes[i].tMs;
          worstIdx = i;
        }
      }
      this.regionMap.echoes.splice(worstIdx, 1);
    }
  }

  _evictSymbolEvent() {
    let worstIdx = -1, worstScore = Infinity;
    for (let i = 0; i < this.symbolEvents.length; i++) {
      const ev = this.symbolEvents[i];
      const age = this.tick - ev.birthTick;
      const total = ev.attackTicks + ev.peakTicks + ev.decayTicks + ev.memoryTicks;
      const isMemory = age > ev.attackTicks + ev.peakTicks + ev.decayTicks;
      const ageRatio = total > 0 ? age / total : 0;
      const score = (isMemory ? 0 : 100) + (ev.intensity || 0) * 10 - ageRatio * 50;
      if (score < worstScore) { worstScore = score; worstIdx = i; }
    }
    if (worstIdx >= 0) this.symbolEvents.splice(worstIdx, 1);
  }

  _stepSymbolEvents() {
    if (this.symbolEvents.length === 0) {
      this.dominantVerb = null;
      this._suppressed.clear();
      return;
    }
    const next = [];
    let strongestIntensity = 0;
    let strongestVerb = null;
    this._suppressed.clear();
    for (const ev of this.symbolEvents) {
      const age = this.tick - ev.birthTick;
      const env = eventEnvelope(ev, age);
      if (!env) continue;
      ev.phaseName = env.phaseName;
      applySymbolEvent(this.stack, ev, age, env.intensity);
      // Suppress competing passes only during attack / peak
      if ((env.phaseName === "attack" || env.phaseName === "peak") &&
          ev.suppress && ev.suppress.length) {
        for (const p of ev.suppress) this._suppressed.add(p);
      }
      // Track dominant verb (highest current intensity)
      if (env.intensity > strongestIntensity) {
        strongestIntensity = env.intensity;
        strongestVerb = ev.verb;
      }
      next.push(ev);
    }
    this.symbolEvents = next;
    this.dominantVerb = strongestVerb;
  }

  // v0.6 — set the embodiment / bhasma / quasicrystal payload from
  // the Atlas-derived bundle (or any compatible source).
  setEmbodimentBundle(bundle) {
    if (!bundle) return;
    if (bundle.embodiment !== undefined)   this.embodiment   = bundle.embodiment;
    if (bundle.bhasma_stage !== undefined) this.bhasmaStage  = bundle.bhasma_stage;
    if (bundle.quasicrystal !== undefined) this.quasicrystalParams = bundle.quasicrystal;
  }

  setEmbodimentStrengths(s) {
    this.embodimentStrengths = { ...this.embodimentStrengths, ...s };
  }

  // Rebuild yantra and mandala fields without resetting simulation state.
  // Called when the user changes yantra type, mandala settings, etc.
  rebuildSacred(opts = {}) {
    const W = this.W, H = this.H;
    if (opts.yantraType !== undefined) {
      this.sacredCtx.yantraMask = buildYantraMask(opts.yantraType, W, H);
      this.sacredCtx.yantraType = opts.yantraType;
    }
    if (opts.mandala !== undefined) {
      const m = opts.mandala;
      const gates = (m.gates ?? 0) > 0
        ? Array.from({ length: m.gates }, (_, k) => (k / m.gates) * Math.PI * 2)
        : [];
      this.sacredCtx.mandala = buildMandalaContext(W, H, {
        nRings: m.rings ?? 0,
        gateAngles: gates,
        gateWidth: 0.25,
        invertWeight: !!m.invert,
      });
      this.sacredCtx.mandalaOpts = m;
    }
  }

  setSacredParams(p) {
    this.sacredParams = { ...this.sacredParams, ...p };
  }

  regenerateGrammar(seed, complexity, structure, opts = {}) {
    this.grammar = generateGrammar(seed, complexity, structure, this.W, this.H, opts);
    return this.grammar;
  }

  reset(seed, complexity = 0.5, structure = 0.5, opts = {}) {
    const rng = mulberry32(seed);
    this.stack.clearAll();
    this.stack.seedNoise(rng);
    this.interference.initSources(rng);
    this.voronoi.initSeeds(rng);
    this.tick = 0;
    this.collapseStrike = 0;
    this.collapseLastIntervention = -1000;
    this.relations = {};
    this.stats = {};
    // v0.8 — clear in-flight gestures on reset
    this.symbolEvents = [];
    this.dominantVerb = null;
    this._suppressed.clear();

    // Build / rebuild sacred context based on opts.sacred
    if (opts.sacred) {
      const s = opts.sacred;
      this.rebuildSacred({
        yantraType: s.yantraType,
        mandala: {
          rings: s.mandalaRings ?? 0,
          gates: s.mandalaGates ?? 0,
          invert: s.mandalaInvert ?? false,
        },
      });
      this.setSacredParams({
        masterStrength: s.masterStrength ?? 0,
        vastuStrength: s.vastuStrength ?? 0,
        yantraStrength: s.yantraStrength ?? 0,
        mandalaStrength: s.mandalaStrength ?? 0,
      });
    }

    // Grammar — pass phyllotaxy from sacred opts if present, plus elements
    // (so phyllotaxy point distortion can read them deterministically).
    const grammarOpts = {
      mode: opts.mode,
      symmetryHint: opts.symmetryHint,
      phyllotaxy: opts.sacred?.phyllotaxy,
      elements: opts.elements,
    };
    this.grammar = generateGrammar(seed, complexity, structure, this.W, this.H, grammarOpts);
    seedEvents(this.stack, this.grammar);
  }

  currentPhase() {
    return this.phaseMode === "auto" ? autoPhase(this.tick) : this.phaseLocked;
  }

  step(params, passes = DEFAULT_PASSES, elements = null) {
    const { stack, grid } = this;
    const phase = this.currentPhase();
    const eS = this.embodimentStrengths;

    // v0.8 — process gesture SymbolEvents first (shapes field, sets
    // dominant verb + pass suppression set used below).
    this._stepSymbolEvents();

    // v0.13 — composition lock: while a beginner gesture is active, mute
    // its declared suppress list on top of the per-event suppression.
    // v0.18 — expiry uses performance.now() (consistent with how the
    // lock is set in tools/visualEvent.js); tick-based expiry could
    // stall if sim is paused or step is skipped.
    let lockSuppress = null;
    if (this.compositionLock) {
      const nowMs = performance.now();
      const expiry = this.compositionLock.activeUntilMs ??
                     // legacy fallback: convert tick-based locks
                     (typeof this.compositionLock.activeUntilTick === "number"
                       ? nowMs + (this.compositionLock.activeUntilTick - this.tick) * 16.667
                       : 0);
      if (nowMs < expiry) {
        lockSuppress = this.compositionLock.suppress;
      } else {
        this.compositionLock = null;
      }
    }
    const ok = (name) => {
      if (!passes[name] || this._suppressed.has(name)) return false;
      if (lockSuppress && lockSuppress.includes(name)) return false;
      return true;
    };

    // v0.10 — prime-tick coherence beat (Atlas planetary primes 3,5,7,11).
    // On each prime tick add a tiny global coherence pulse — the field
    // gains a low-frequency "heartbeat" that's just-perceptible.
    const beat = primeBeat(this.tick);
    if (beat > 0) {
      const coh = stack.get("coherence");
      const add = 0.005 / beat;       // smaller bump for higher primes
      for (let i = 0; i < stack.N; i++) coh[i] += add;
    }
    // Lo Shu cell biases replenish slightly toward one of 9 archetypes
    this._loShu = loShuCell(this.tick);

    // 0. Replenish
    if (ok("replenish")) replenishPass(stack, params.replenish);
    // 1. Sacred (v0.5) — vastu / yantra / mandala biases
    if (ok("sacred")) applySacred(stack, this.sacredCtx, this.sacredParams);
    const act = this.passActivity;
    act.bhasma = act.dhatu = act.pulseMarma = 0;
    act.helicalShear = act.tensegrity = act.movementPhrase = act.quasicrystal = 0;

    // 1b. Bhasma (v0.6) — stage operators (rigidity, density-lock, heat, etc.)
    if (ok("bhasma") && this.bhasmaStage) {
      act.bhasma = bhasmaCalcinationPass(stack, this.bhasmaStage, eS.bhasma) || 0;
    }
    // 1c. Dhātu material bias (v0.6)
    if (ok("dhatu") && this.embodiment) {
      act.dhatu = dhatuMaterialPass(stack, this.embodiment, eS.dhatu) || 0;
    }
    // 1d. Tensegrity ridges (v0.6) — pre-events so reaction can pick them up
    if (ok("tensegrity") && this.embodiment) {
      act.tensegrity = tensegrityPass(stack, this.embodiment, this.tick, eS.tensegrity) || 0;
    }
    // 2. Events
    if (ok("events") && this.grammar) {
      applyEvents(stack, this.grammar, this.tick, phase, 1.0);
    }
    // 2b. Marma pulse (v0.6) — periodic charge/coherence at body region
    if (ok("pulseMarma") && this.embodiment) {
      act.pulseMarma = pulseMarmaPass(stack, this.embodiment, this.tick, 16, eS.pulseMarma) || 0;
    }
    // 2c. Movement phrase (v0.6) — pranayama-driven breath modulation
    if (ok("movementPhrase") && this.embodiment) {
      act.movementPhrase = movementPhrasePass(stack, this.embodiment, this.tick, 16, eS.movementPhrase) || 0;
    }
    // 3. Diffuse
    if (ok("diffusion")) diffusionPass(stack, grid, params.diffusion);
    // 4. Reaction-diffusion
    if (ok("reaction")) reactionPass(stack, grid, params.reaction);
    // 4b. Quasicrystal (v0.6) — coherence perturbation when active
    if (ok("quasicrystal") && this.quasicrystalParams?.active) {
      act.quasicrystal = quasicrystalPass(stack, this.quasicrystalState, {
        ...this.quasicrystalParams,
        strength: (this.quasicrystalParams.strength ?? 0) * eS.quasicrystal,
      }, this.tick) || 0;
    }
    // 5. Curl flow
    if (ok("curl")) curlFlowPass(stack, grid, params.curlFlow);
    // 5b. Helical shear (v0.6) — twist velocity from asana
    if (ok("helicalShear") && this.embodiment) {
      act.helicalShear = helicalShearPass(stack, this.embodiment, eS.helicalShear) || 0;
    }
    // 6. Advection
    if (ok("advection")) advectionPass(stack, grid, params.advection);
    // 7. Branch memory
    if (ok("branch")) branchMemoryPass(stack, grid, params.branchMemory);
    // 8. Discharge
    if (ok("discharge")) dischargePass(stack, grid, params.discharge);
    // 9. Interference rings
    if (ok("interference")) {
      this.interference.drift(stack, 0.6 * (params.advection?.dt ?? 1));
      this.interference.apply(stack, params.interference);
    }
    // 10. Voronoi
    if (ok("voronoi") && (this.tick % 3) === 0) {
      this.voronoi.drift(stack, 0.2);
      this.voronoi.apply(stack, params.voronoi);
    }
    // 11. Life
    if (ok("life")) {
      const life = stack.get("life");
      const branch = stack.get("branch_memory");
      const charge = stack.get("charge");
      const lp = params.life;
      for (let i = 0; i < stack.N; i++) {
        let next =
          life[i] * lp.decay +
          lp.grow_from_branch * branch[i] +
          lp.grow_from_charge * Math.max(0, charge[i]);
        if (next > 1) next = 1;
        life[i] = next;
      }
    }
    // 12. Relations
    if (elements) {
      const r = computeRelations(stack, elements);
      this.relations = r.relations;
      this.stats = r.stats;
    }

    // v0.13 — Edge-density budget.  Branch memory + |charge| both
    // accumulate fast and turn the field into a noisy mess.  Cap
    // the canvas-mean of each so a "lightning" or "branch" gesture
    // produces a few clean strokes instead of a noise field.
    const memArr = stack.get("branch_memory");
    const chgArr = stack.get("charge");
    let memSum = 0, chgSum = 0;
    for (let i = 0; i < stack.N; i++) {
      memSum += memArr[i];
      chgSum += Math.abs(chgArr[i]);
    }
    const memMean = memSum / stack.N;
    const chgMean = chgSum / stack.N;
    if (memMean > 0.32) {
      const s = 0.32 / memMean;
      for (let i = 0; i < stack.N; i++) memArr[i] *= s;
    }
    if (chgMean > 0.20) {
      const s = 0.20 / chgMean;
      for (let i = 0; i < stack.N; i++) chgArr[i] *= s;
    }

    // v0.14 — step the visual-state region map (lerp toward targets,
    // fire pending echoes, decay back toward the default state)
    if (this.regionMap) this.regionMap.step(performance.now());

    this.tick++;
  }

  // v0.7 — anti-collapse guard signals (read by main.js to bump replenish/exposure)
  updateGuard(blackRatio, avgLuminance, fieldVariance) {
    const lumaLow = avgLuminance < 0.10;
    const varLow  = fieldVariance < 0.003;
    if (lumaLow || varLow) {
      this.guard.consec++;
    } else {
      this.guard.consec = Math.max(0, this.guard.consec - 1);
    }
    this.guard.lumaLow     = lumaLow && this.guard.consec >= 30;
    this.guard.varianceLow = varLow  && this.guard.consec >= 30;
    if ((this.guard.lumaLow || this.guard.varianceLow) &&
        this.tick - this.guard.lastBoost > 90) {
      this.guard.lastBoost = this.tick;
    }
  }

  collapseMonitor(blackRatio, avgLuminance) {
    const N = this.stack.N;
    let dMean = 0, lMean = 0;
    const dens = this.stack.fields.density;
    const life = this.stack.fields.life;
    for (let i = 0; i < N; i++) { dMean += dens[i]; lMean += life[i]; }
    dMean /= N; lMean /= N;
    let dVar = 0, lVar = 0;
    for (let i = 0; i < N; i++) {
      const dd = dens[i] - dMean;
      const dl = life[i] - lMean;
      dVar += dd * dd; lVar += dl * dl;
    }
    dVar /= N; lVar /= N;
    const fieldVariance = dVar + lVar;
    this.lastMonitor = { fieldVariance, blackRatio, avgLuminance };
    this.updateGuard(blackRatio, avgLuminance, fieldVariance);

    const T = COLLAPSE_THRESHOLDS;
    const flagged =
      fieldVariance < T.fieldVarianceMin ||
      blackRatio > T.blackRatioMax ||
      avgLuminance < T.avgLuminanceMin;
    if (flagged) this.collapseStrike++;
    else this.collapseStrike = Math.max(0, this.collapseStrike - 1);

    if (this.collapseStrike >= T.consecutiveTicks &&
        this.tick - this.collapseLastIntervention > T.cooldown) {
      this.collapseStrike = 0;
      this.collapseLastIntervention = this.tick;
      this.injectRebloom();
      return true;
    }
    return false;
  }

  injectRebloom() {
    if (!this.grammar) return;
    const W = this.W, H = this.H;
    for (const ev of this.grammar.events) {
      if (ev.kind === "emitter") {
        const arr = this.stack.get(ev.field);
        if (!arr) continue;
        splat(arr, W, H, ev.x, ev.y, ev.radius * 1.5, 0.6);
      } else if (ev.kind === "bloom_node" || ev.kind === "coherence_pulse") {
        const coh = this.stack.get("coherence");
        splat(coh, W, H, ev.x, ev.y, ev.radius * 1.2, 0.5);
      }
    }
  }
}

function splat(field, W, H, x, y, radius, amount) {
  const r2 = radius * radius;
  const x0 = Math.max(0, Math.floor(x - radius));
  const x1 = Math.min(W - 1, Math.ceil(x + radius));
  const y0 = Math.max(0, Math.floor(y - radius));
  const y1 = Math.min(H - 1, Math.ceil(y + radius));
  for (let py = y0; py <= y1; py++) {
    for (let px = x0; px <= x1; px++) {
      const dx = px - x, dy = py - y;
      const d2 = dx * dx + dy * dy;
      if (d2 > r2) continue;
      const w = Math.exp(-d2 * 4 / r2);
      field[py * W + px] += amount * w;
    }
  }
}
