// PhraseRewardDirector — receives an InteractionPhrase, picks the
// VisualEvent / transition that best rewards that phrasing, and
// applies reward multipliers (intensity, radius, echoes) before
// firing it through the intergenesis region map.
//
// Reward principle:
//   - Coherent phrasing produces cleaner, more beautiful results
//   - Sattvic rhythm increases hidden geometry (eye → star, mandala)
//   - Sustained Kapha grows large stable forms (membrane → cellular,
//     fluid → terrain)
//   - Pitta direct strikes reward decisive lines
//   - Vata erratic creates sparks but fragments unless balanced
//   - Tamas stillness settles into ash / shadow / reveal on release
//   - Rajas escalation triggers climactic discharge
//
// This module never renders dosha symbols; it only chooses transitions.

import { TRANSITIONS } from "../render/intergenesis.js";

// Phrase-key → reward bundle.  Each chooses one of the 12 transitions.
const REWARDS = {
  // ── Vata ──────────────────────────────────────────────────────
  "vata.spark":        { transition: "filament_to_lightning", radiusMul: 0.85, intensityMul: 0.95, echoBonus: 1, label: "vāta · spark" },
  "vata.smoke":        { transition: "smoke_to_body",         radiusMul: 1.10, intensityMul: 0.85, echoBonus: 0, label: "vāta · smoke" },
  "vata.seed":         { transition: "filament_to_root",      radiusMul: 1.20, intensityMul: 0.90, echoBonus: 1, label: "vāta · seed dispersal" },
  // ── Pitta ─────────────────────────────────────────────────────
  "pitta.strike":      { transition: "filament_to_lightning", radiusMul: 0.80, intensityMul: 1.45, echoBonus: 0, label: "pitta · strike clean" },
  "pitta.crystal":     { transition: "flow_to_crystal",       radiusMul: 1.00, intensityMul: 1.30, echoBonus: 0, label: "pitta · crystal cut" },
  "pitta.calcine":     { transition: "density_to_void",       radiusMul: 0.90, intensityMul: 1.50, echoBonus: 0, label: "pitta · calcine edge" },
  // ── Kapha ─────────────────────────────────────────────────────
  "kapha.bloom":       { transition: "membrane_to_cellular",  radiusMul: 1.40, intensityMul: 1.20, echoBonus: 1, label: "kapha · bloom sustained" },
  "kapha.terrain":     { transition: "fluid_to_terrain",      radiusMul: 1.50, intensityMul: 1.05, echoBonus: 1, label: "kapha · fossilization" },
  "kapha.bone":        { transition: "body_to_root",          radiusMul: 1.30, intensityMul: 1.10, echoBonus: 0, label: "kapha · bone settling" },
  // ── Sattva (rhythm-rewarded) ──────────────────────────────────
  "sattva.eye":        { transition: "bloom_to_eye",          radiusMul: 1.30, intensityMul: 1.40, echoBonus: 2, label: "sattva · rhythm rewarded" },
  "sattva.star":       { transition: "eye_to_star",           radiusMul: 1.40, intensityMul: 1.30, echoBonus: 2, label: "sattva · mandala coherence" },
  // ── Rajas (escalation) ────────────────────────────────────────
  "rajas.discharge":   { transition: "filament_to_lightning", radiusMul: 1.05, intensityMul: 1.65, echoBonus: 1, label: "rajas · escalation" },
  // ── Tamas (settling / still) ──────────────────────────────────
  "tamas.ash":         { transition: "density_to_void",       radiusMul: 1.25, intensityMul: 0.80, echoBonus: 0, label: "tamas · ash settling" },
  "tamas.cellular":    { transition: "cellular_to_membrane",  radiusMul: 1.10, intensityMul: 0.75, echoBonus: 0, label: "tamas · memory residue" },
  "tamas.reveal":      { transition: "eye_to_star",           radiusMul: 1.50, intensityMul: 1.30, echoBonus: 2, label: "tamas · reveal on release" },
};

// Phrase → reward key.  Sattvic rhythm wins precedence so coherent
// playing always lands in a rewarded place.
function selectRewardKey(phrase, intent) {
  const { dosha, guna, rhythm, intensity } = phrase;

  if (rhythm === "pulsed" && guna === "sattva") {
    return intensity > 0.45 ? "sattva.star" : "sattva.eye";
  }
  if (rhythm === "spiral") {
    return guna === "sattva" ? "sattva.star" : "kapha.bloom";
  }
  if (intent === "reveal" && guna === "tamas") {
    return "tamas.reveal";
  }
  if (rhythm === "still" && guna === "tamas") {
    return intent === "reveal" ? "tamas.reveal" : "tamas.ash";
  }
  if (rhythm === "erratic" && dosha === "vata") {
    return intensity > 0.55 ? "vata.spark" : "vata.seed";
  }
  if ((rhythm === "jagged" || guna === "rajas") &&
      (dosha === "pitta" || guna === "rajas")) {
    return guna === "rajas" ? "rajas.discharge" : "pitta.strike";
  }
  if (rhythm === "sustained" && dosha === "kapha") {
    return intensity > 0.45 ? "kapha.bloom" : "kapha.terrain";
  }
  // Defaults by dosha
  switch (dosha) {
    case "vata":  return "vata.smoke";
    case "pitta": return "pitta.crystal";
    case "kapha": return "kapha.bone";
    default:      return "sattva.eye";
  }
}

export class PhraseRewardDirector {
  constructor(sim) {
    this.sim = sim;
    this.lastLabel = null;
    this.lastChaoticAt = 0;       // for spacebar-breath alignment
    this.lastPhrase = null;
    this.lastRewardAt = 0;
  }

  // Apply a phrase to the engine.  Fires a transition into the region
  // map and schedules echo bonuses.  Returns { label, transition, key }.
  fire(phrase, intent, x, y, brushSize, nowMs = performance.now()) {
    const key = selectRewardKey(phrase, intent);
    const reward = REWARDS[key];
    if (!reward) return null;
    const t = TRANSITIONS[reward.transition];
    if (!t) return null;

    const rewardConfidence = 0.6 + 0.4 * (phrase.confidence || 0);
    const intensity   = (phrase.intensity ?? 0.5) * reward.intensityMul * rewardConfidence;
    const baseFalloff = (brushSize / 12) * 2.5 * reward.radiusMul;
    this.sim.regionMap.applyTransition(reward.transition, x, y, intensity, baseFalloff, nowMs);

    // Bonus echoes for rewarded sattvic / kapha sustained phrases
    for (let k = 1; k <= reward.echoBonus; k++) {
      this.sim.regionMap.echoes.push({
        tMs: nowMs + 220 * k,
        simX: x, simY: y,
        transitionKey: reward.transition,
        intensityMul: 0.55 * Math.pow(0.72, k),
        radiusCellsMul: 1 + 0.28 * k,
      });
    }

    if (phrase.dosha === "vata" && phrase.rhythm === "erratic") {
      this.lastChaoticAt = nowMs;
    } else if (phrase.guna === "sattva" || phrase.dosha === "kapha") {
      this.lastChaoticAt = 0;     // coherent play clears the chaotic flag
    }

    this.lastPhrase = phrase;
    this.lastLabel  = reward.label;
    this.lastRewardAt = nowMs;
    return { label: reward.label, transition: reward.transition, key };
  }

  // Spacebar breath: if recent phrasing was chaotic vāta, transform the
  // accumulated sparks into a coherent constellation (eye → star at center).
  // Otherwise return false so the caller can fire a normal breath pulse.
  alignWithBreath(nowMs = performance.now()) {
    if (!this.lastChaoticAt) return false;
    if (nowMs - this.lastChaoticAt > 5500) {
      this.lastChaoticAt = 0;
      return false;
    }
    const W = this.sim.W, H = this.sim.H;
    this.sim.regionMap.applyTransition("eye_to_star", W * 0.5, H * 0.5,
                                       1.20, 6.5, nowMs);
    // Also stamp 4 satellite stars at golden-angle positions
    const GA = 137.5077640500378 * Math.PI / 180;
    for (let k = 0; k < 4; k++) {
      const a = k * GA;
      const r = Math.min(W, H) * 0.28;
      this.sim.regionMap.applyTransition("eye_to_star",
        W * 0.5 + Math.cos(a) * r, H * 0.5 + Math.sin(a) * r,
        0.65, 3.0, nowMs + 80 * k);
    }
    this.lastChaoticAt = 0;
    this.lastLabel = "vāta · aligned by breath";
    return true;
  }
}
