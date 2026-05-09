// InteractionPhraseAnalyzer — parses raw input into a doshic / guna /
// rhythm grammar.  The user is not "selecting an effect": their motion
// is read as a phrase the field listens to.
//
// Output: { dosha, guna, rhythm, confidence, intensity, suggestedKey,
//           meanSpeed, meanDirVar, clickRegularity, stillFraction }
//
//   dosha   ∈ vata | pitta | kapha | mixed
//   guna    ∈ sattva | rajas | tamas
//   rhythm  ∈ erratic | jagged | sustained | regular | pulsed | still | spiral
//
// Sources of evidence:
//   - mouse movement samples (for speed, accel, jaggedness, curvature)
//   - click timestamps (for rhythm regularity, double/triple tap)
//   - key timestamps (for tap regularity)
//   - long pauses (for stillness / tamas)

const WINDOW_MS = 4500;

export class InteractionPhraseAnalyzer {
  constructor() {
    this.moves  = [];   // { t, x, y }
    this.clicks = [];   // { t, button }
    this.keys   = [];   // { t, key }
    this._lastClassifyMs = 0;
    this._lastPhrase = {
      dosha: "kapha", guna: "tamas", rhythm: "still",
      confidence: 0, intensity: 0,
    };
  }

  // P2 (issue #8) — throttle to ≥16ms gap.  High-rate cursor reports
  // (500–1000Hz on some pointers) used to hammer this and every push +
  // _trim cycle was ~10 ops.  16ms cap gives 60Hz max sampling without
  // losing classification accuracy.
  recordMove(x, y, t) {
    if (this._lastMoveT && (t - this._lastMoveT) < 16) return;
    this._lastMoveT = t;
    this.moves.push({ t, x, y });
    this._trim(t);
  }
  recordClick(t, button = 0) {
    this.clicks.push({ t, button });
    this._trim(t);
  }
  recordKey(t, key = "") {
    this.keys.push({ t, key });
    this._trim(t);
  }

  _trim(now) {
    const cutoff = now - WINDOW_MS;
    while (this.moves.length  && this.moves[0].t  < cutoff) this.moves.shift();
    while (this.clicks.length && this.clicks[0].t < cutoff) this.clicks.shift();
    while (this.keys.length   && this.keys[0].t   < cutoff) this.keys.shift();
  }

  // Returns the most recent classification.  Cached at 100ms granularity.
  classify(now = performance.now()) {
    if (now - this._lastClassifyMs < 100) return this._lastPhrase;
    this._lastClassifyMs = now;

    const m = this.moves;
    if (m.length < 2) {
      // No motion at all → still / tamas
      const stillForMs = m.length ? (now - m[m.length - 1].t) : WINDOW_MS;
      const phrase = {
        dosha: "kapha", guna: "tamas",
        rhythm: stillForMs > 1500 ? "still" : "regular",
        confidence: 0.4,
        intensity: 0.05,
        meanSpeed: 0, meanDirVar: 0,
        clickRegularity: 0, stillFraction: 1.0,
      };
      this._lastPhrase = phrase;
      return phrase;
    }

    // ── motion features ─────────────────────────────────────────
    let totalSpeed = 0, peakSpeed = 0;
    let pathLen = 0, pauseTotal = 0, pauseMax = 0;
    let lastDir = null, dirSum = 0, dirCount = 0;
    let totalAngularSweep = 0, lastAngleFromCentroid = null;
    let cx = 0, cy = 0;
    for (const p of m) { cx += p.x; cy += p.y; }
    cx /= m.length; cy /= m.length;

    const tStart = m[0].t;
    const tEnd   = m[m.length - 1].t;

    for (let i = 1; i < m.length; i++) {
      const a = m[i - 1], b = m[i];
      const dt = (b.t - a.t) / 1000;          // seconds
      const dx = b.x - a.x, dy = b.y - a.y;
      const dist = Math.hypot(dx, dy);
      pathLen += dist;
      const speed = dt > 0 ? dist / dt : 0;
      totalSpeed += speed;
      if (speed > peakSpeed) peakSpeed = speed;
      const gap = b.t - a.t;
      if (gap > 80) {
        pauseTotal += gap;
        if (gap > pauseMax) pauseMax = gap;
      }
      if (dist > 0.4) {
        const dir = Math.atan2(dy, dx);
        if (lastDir !== null) {
          let d = dir - lastDir;
          while (d >  Math.PI) d -= 2 * Math.PI;
          while (d < -Math.PI) d += 2 * Math.PI;
          dirSum += Math.abs(d);
          dirCount++;
        }
        lastDir = dir;
      }
      const angCentroid = Math.atan2(b.y - cy, b.x - cx);
      if (lastAngleFromCentroid !== null) {
        let d = angCentroid - lastAngleFromCentroid;
        while (d >  Math.PI) d -= 2 * Math.PI;
        while (d < -Math.PI) d += 2 * Math.PI;
        totalAngularSweep += d;
      }
      lastAngleFromCentroid = angCentroid;
    }
    const meanSpeed   = totalSpeed / Math.max(1, m.length - 1);
    const meanDirVar  = dirCount > 0 ? dirSum / dirCount : 0;
    const stillFrac   = pauseTotal / Math.max(1, tEnd - tStart);
    const sweepAbs    = Math.abs(totalAngularSweep);

    // ── click rhythm regularity ─────────────────────────────────
    let clickRegularity = 0;
    if (this.clicks.length >= 3) {
      const intervals = [];
      for (let i = 1; i < this.clicks.length; i++) {
        intervals.push(this.clicks[i].t - this.clicks[i - 1].t);
      }
      const mean = intervals.reduce((a, b) => a + b, 0) / intervals.length;
      const variance = intervals.reduce((s, v) => s + (v - mean) ** 2, 0) / intervals.length;
      const cv = mean > 0 ? Math.sqrt(variance) / mean : 1;
      clickRegularity = Math.max(0, 1 - cv);
    }

    // ── dosha classification ────────────────────────────────────
    let dosha;
    if      (meanSpeed > 80 && meanDirVar > 0.55) dosha = "vata";
    else if (meanSpeed > 80 && meanDirVar < 0.40) dosha = "pitta";
    else if (meanSpeed < 40 && meanDirVar < 0.45) dosha = "kapha";
    else dosha = "mixed";

    // ── guna classification ─────────────────────────────────────
    let guna;
    if (clickRegularity > 0.55 ||
        (meanDirVar < 0.30 && meanSpeed > 18 && meanSpeed < 80)) {
      guna = "sattva";
    } else if (meanSpeed > 110 || (peakSpeed > 320 && this.clicks.length > 2)) {
      guna = "rajas";
    } else if (stillFrac > 0.45 || (meanSpeed < 14 && pauseMax > 1500)) {
      guna = "tamas";
    } else {
      guna = "sattva";
    }

    // ── rhythm classification ───────────────────────────────────
    let rhythm;
    if      (pauseMax > 1800)              rhythm = "still";
    else if (clickRegularity > 0.65)       rhythm = "pulsed";
    else if (sweepAbs > 4.0)               rhythm = "spiral";
    else if (meanDirVar > 0.70)            rhythm = "erratic";
    else if (meanDirVar > 0.40)            rhythm = "jagged";
    else if (meanSpeed > 5 && meanSpeed < 90) rhythm = "sustained";
    else                                   rhythm = "regular";

    const confidence = Math.min(1, m.length / 24);
    const intensity  = Math.min(1, meanSpeed / 250 + meanDirVar * 0.15);

    const phrase = {
      dosha, guna, rhythm, confidence, intensity,
      meanSpeed, meanDirVar, clickRegularity, stillFraction: stillFrac,
      sweepAbs, peakSpeed,
    };
    this._lastPhrase = phrase;
    return phrase;
  }
}
