// Movement-phrase pass — pranayama drives the global "breath" cycle
// modulating decay/charge/coherence smoothly through the breath phases.
//
// Hidden grammar: breath texture. Smooth (Bhramari, Ujjayi) → low-frequency
// large-amplitude waves. Sharp (Kapalabhati) → high-frequency staccato
// pulses. Alternating (Nadi Shodhana) → left-right asymmetric drive.
//
// We drive: charge (additive), coherence (additive), life (multiplicative).
// All deltas are tiny — this is the ambient breath of the field.

const PRANAYAMA_PROFILE = {
  // [cycleMs, kind: "smooth"|"sharp"|"alternating"|"hold", amp]
  Bhramari:       { cycleMs: 5500, kind: "smooth",      amp: 1.0 },
  Ujjayi:         { cycleMs: 4500, kind: "smooth",      amp: 0.85 },
  Kapalabhati:    { cycleMs: 1100, kind: "sharp",       amp: 1.4 },
  NadiShodhana:   { cycleMs: 6000, kind: "alternating", amp: 0.9 },
  "Nadi Shodhana": { cycleMs: 6000, kind: "alternating", amp: 0.9 },
  Bhastrika:      { cycleMs: 1800, kind: "sharp",       amp: 1.2 },
  Sitali:         { cycleMs: 5800, kind: "smooth",      amp: 0.9 },
  KevalaKumbhaka: { cycleMs: 9000, kind: "hold",        amp: 0.4 },
  "Kevala Kumbhaka": { cycleMs: 9000, kind: "hold",     amp: 0.4 },
};

export function movementPhrasePass(stack, embodiment, tick, dtMs = 16, strength = 1.0) {
  if (!embodiment) return 0;
  if (strength <= 0) return 0;
  const pranayama = embodiment.pranayama_that_loads;
  const profile = PRANAYAMA_PROFILE[pranayama] ??
                  { cycleMs: 4000, kind: "smooth", amp: 0.7 };
  const tMs = tick * dtMs;
  const phase = (tMs % profile.cycleMs) / profile.cycleMs;   // 0..1

  let drive;
  if (profile.kind === "smooth") {
    drive = Math.sin(phase * Math.PI * 2);
  } else if (profile.kind === "sharp") {
    // staccato pulse — narrow gaussian at phase 0
    drive = Math.exp(-Math.pow((phase - 0.0) * 8, 2)) -
            Math.exp(-Math.pow((phase - 0.5) * 8, 2));
  } else if (profile.kind === "hold") {
    // long swell with mostly flat plateau
    const env = Math.sin(phase * Math.PI);
    drive = env > 0.7 ? 1.0 : env;
  } else {
    drive = Math.sin(phase * Math.PI * 2);
  }

  const charge = stack.get("charge");
  const coh = stack.get("coherence");
  const life = stack.get("life");
  const W = stack.W, H = stack.H;
  const baseAmp = 0.005 * profile.amp * strength * drive;
  const cohAmp  = 0.003 * profile.amp * strength * drive;
  // Life multiplicative: gentle gain on inhale, gentle decay on exhale
  const lifeMul = 1.0 + 0.004 * profile.amp * strength * drive;

  if (profile.kind === "alternating") {
    // Left-right asymmetric drive: nadi shodhana
    for (let y = 0; y < H; y++) {
      for (let x = 0; x < W; x++) {
        const i = y * W + x;
        const side = (x < W / 2) ? 1 : -1;
        const sideDrive = Math.sin(phase * Math.PI * 2) * side;
        charge[i] += 0.005 * profile.amp * strength * sideDrive;
        coh[i]    += 0.003 * profile.amp * strength * sideDrive;
        life[i]   *= 1.0 + 0.004 * profile.amp * strength * sideDrive;
      }
    }
    return Math.abs(Math.sin(phase * Math.PI * 2)) * profile.amp * strength;
  }

  for (let i = 0; i < charge.length; i++) {
    charge[i] += baseAmp;
    coh[i]    += cohAmp;
    life[i]   *= lifeMul;
  }
  return Math.abs(drive) * profile.amp * strength;
}

export { PRANAYAMA_PROFILE };
