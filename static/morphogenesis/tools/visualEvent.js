// VisualEvent registry — 8 beginner-facing event types.  Each maps a
// recognized gesture intent to a structured visual response with full
// envelope (attack→peak→decay→memory) AND a composition lock that
// names which passes should dominate, support, accent, or be muted
// while the event is active.
//
// The event also carries a `fields` injection schema describing what
// the gesture writes into the field stack at peak intensity.  The
// SymbolEvent applier reads this; styles can override scaling.

import { makeSymbolEvent } from "./symbolEvent.js";

// Real-time → simulation-tick conversion (the engine runs ~60 ticks/s).
const MS_PER_TICK = 16;
const ms = (n) => Math.max(1, Math.round(n / MS_PER_TICK));

// Pass families.  Used to suppress entire families during certain events.
const FAMILY = {
  noise:    ["voronoi"],
  edges:    ["branch"],
  blur:     ["diffusion"],
  electric: ["discharge"],
  flow:     ["advection", "curl"],
  ring:     ["interference"],
  reaction: ["reaction"],
  sacred:   ["sacred"],
};

// ── 8 visual event definitions ─────────────────────────────────────
export const VISUAL_EVENTS = {
  bloom: {
    label: "Bloom",
    attackMs:  300, peakMs:  500, decayMs: 1400, memoryMs: 4000,
    radiusMul: 1.4, intensityMul: 1.2,
    fieldKind: "bloom",      // SymbolEvent kind dispatched
    dominant:   ["reaction", "diffusion", "sacred"],
    secondary:  ["interference"],
    accent:     ["dhatu"],
    suppress:   [...FAMILY.noise, ...FAMILY.electric],
  },
  strike: {
    label: "Strike",
    attackMs:   80, peakMs:  140, decayMs:  600, memoryMs: 2400,
    radiusMul: 0.9, intensityMul: 1.6,
    fieldKind: "discharge",
    dominant:   [...FAMILY.electric, ...FAMILY.edges],
    secondary:  [...FAMILY.ring],
    accent:     [],
    suppress:   [...FAMILY.noise, ...FAMILY.blur],
  },
  reveal: {
    label: "Reveal",
    attackMs:  700, peakMs: 1500, decayMs: 2400, memoryMs: 6000,
    radiusMul: 1.9, intensityMul: 1.0,
    fieldKind: "reveal",
    dominant:   [...FAMILY.ring, ...FAMILY.sacred],
    secondary:  [...FAMILY.reaction],
    accent:     ["quasicrystal"],
    suppress:   [...FAMILY.electric, ...FAMILY.noise],
  },
  flow: {
    label: "Flow",
    attackMs:  120, peakMs:  220, decayMs:  900, memoryMs: 1800,
    radiusMul: 1.0, intensityMul: 1.0,
    fieldKind: "flow",
    dominant:   [...FAMILY.flow, ...FAMILY.blur],
    secondary:  [],
    accent:     [],
    suppress:   [...FAMILY.noise],
  },
  mandala: {
    label: "Mandala",
    attackMs:  450, peakMs:  800, decayMs: 1700, memoryMs: 4500,
    radiusMul: 1.5, intensityMul: 1.2,
    fieldKind: "yantra",
    dominant:   [...FAMILY.sacred, ...FAMILY.ring],
    secondary:  [...FAMILY.reaction],
    accent:     ["quasicrystal"],
    suppress:   [...FAMILY.electric, ...FAMILY.noise],
  },
  twist: {
    label: "Twist",
    attackMs:  220, peakMs:  380, decayMs: 1200, memoryMs: 2600,
    radiusMul: 1.2, intensityMul: 1.3,
    fieldKind: "helical",
    dominant:   ["helicalShear", ...FAMILY.flow],
    secondary:  [...FAMILY.edges],
    accent:     ["tensegrity"],
    suppress:   [...FAMILY.noise],
  },
  lightning: {
    label: "Lightning",
    attackMs:   60, peakMs:  120, decayMs:  700, memoryMs: 3000,
    radiusMul: 0.8, intensityMul: 1.8,
    fieldKind: "discharge",
    dominant:   [...FAMILY.electric, ...FAMILY.edges],
    secondary:  [...FAMILY.ring],
    accent:     [],
    suppress:   [...FAMILY.blur, ...FAMILY.noise],
  },
  void_click: {
    label: "Void",
    attackMs:  150, peakMs:  250, decayMs: 1000, memoryMs: 1800,
    radiusMul: 1.3, intensityMul: 1.0,
    fieldKind: "void",
    dominant:   [],
    secondary:  [],
    accent:     [],
    suppress:   [...FAMILY.reaction, ...FAMILY.noise, ...FAMILY.edges],
  },
  void_drag: {
    label: "Void Carve",
    attackMs:   80, peakMs:  140, decayMs:  600, memoryMs: 1200,
    radiusMul: 1.0, intensityMul: 0.9,
    fieldKind: "void",
    dominant:   [],
    secondary:  [],
    accent:     [],
    suppress:   [...FAMILY.reaction, ...FAMILY.noise, ...FAMILY.edges],
  },
};

// Build a SymbolEvent for a recognized intent within a chosen style.
// Returns the SymbolEvent + a "lock" object the caller installs on sim.
export function buildVisualEvent({
  intent, x, y, brushSize, tick,
  dx = 0, dy = 0, styleOverrides = null,
}) {
  const def = VISUAL_EVENTS[intent];
  if (!def) return null;

  const radiusMul    = (styleOverrides?.radiusMul    ?? 1) * def.radiusMul;
  const intensityMul = (styleOverrides?.intensityMul ?? 1) * def.intensityMul;
  const radius    = brushSize * radiusMul;
  const intensity = intensityMul;

  const ev = makeSymbolEvent({
    kind: def.fieldKind,
    x, y, radius, intensity, dx, dy,
    birthTick: tick,
    suppress: def.suppress,
  });
  // Override the symbolEvent envelope with VisualEvent's real-time timings
  ev.attackTicks = ms(def.attackMs);
  ev.peakTicks   = ms(def.peakMs);
  ev.decayTicks  = ms(def.decayMs);
  ev.memoryTicks = ms(def.memoryMs);
  // Tag the event so the HUD can show the gesture label
  ev.label = def.label;
  ev.intent = intent;

  // v0.18 — composition lock now uses performance.now() consistently.
  // Tick-based expiry can stall if sim.tick stops advancing for any reason
  // (paused, frame budget overrun, error mid-step).  performance.now() is
  // monotonic and independent of sim state.
  const nowMs = (typeof performance !== "undefined" && performance.now)
                ? performance.now() : Date.now();
  const lock = {
    intent,
    label: def.label,
    dominant:  def.dominant,
    secondary: def.secondary,
    accent:    def.accent,
    suppress:  def.suppress,
    activeUntilMs: nowMs + def.attackMs + def.peakMs,
  };

  return { ev, lock, def };
}
