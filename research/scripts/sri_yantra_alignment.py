"""
sri_yantra_alignment.py — reproduce the Coherence Atlas v0.5 §2.5 finding.

The lunisolar gear ratio k ≈ 12.368 (= 365.25/29.53) is the spatial frequency
at which the toroidal interference pattern most closely matches the classical
Sri Yantra structure. Per v0.5 §2.5 page 17:

    "The alignment peaks at Ekadashi (tithi 11) with 85% structural match
     at k=12.0, and at Purnima (tithi 15) the field reaches 82% full bloom."

Originating algorithm: `static/s4.html` at commit 594b3cf (2026-04-08), the
ALIGNED-mode JavaScript renderer. This file is the offline Python reproducer
that lifts the same metric out of the browser into a runnable script. The
JavaScript source is preserved at:

    git show 594b3cf:static/s4.html

The metric, in plain words:
  1. For each tithi t, the field is the standing-wave product of n=t plane-
     wave pairs (each pair: a wave in direction θ_i and a wave perpendicular
     to it), with the n directions evenly spaced on the unit circle.
  2. The Sri Yantra is the canonical 9 interlocking triangles (4 Shiva
     upward, 5 Shakti downward) in normalized coordinates.
  3. Alignment is measured along the triangle EDGES: 22 sample points per
     edge × 3 edges × 9 triangles = 594 sample points total (the "22" matches
     the count of svara-shrutis — a tantric structural choice).
  4. At each sample point, evaluate |field|. If the field is small at the
     edge, the edge sits on a nodal line of the standing wave; that's
     alignment. If |field| is large, the edge is in an antinode region;
     that's misalignment.
  5. Score = (1 − mean|field| over all samples) × 100. Higher = better
     nodal alignment.

This is reproducible. The result is a function alignment(tithi, k, t=0).

Usage:

    python3 sri_yantra_alignment.py
    # Reports alignment scores per tithi at k=12.0; expects ~85% at T11,
    # ~82% at T15 (per v0.5 §2.5).

Provenance: Coherence Atlas v0.5 §2.5 page 17 (founding document, primary
source). Originating JavaScript: static/s4.html at commit 594b3cf (Apr 8, 2026).
This Python lift: 2026-05-03, kanjira.
"""

import math
import json
import os
import sys

# ── Sri Yantra reference (verbatim from s4.html @ 594b3cf) ────────────────

SRI_TRIS = [
    # Shakti (teal) — downward
    {"up": False, "sc": 0.95, "rot": 0.00},
    {"up": False, "sc": 0.72, "rot": 0.02},
    {"up": False, "sc": 0.52, "rot": 0.04},
    {"up": False, "sc": 0.35, "rot": 0.03},
    {"up": False, "sc": 0.18, "rot": 0.00},
    # Shiva (gold) — upward
    {"up": True,  "sc": 0.85, "rot": 0.00},
    {"up": True,  "sc": 0.62, "rot": 0.03},
    {"up": True,  "sc": 0.42, "rot": 0.02},
    {"up": True,  "sc": 0.22, "rot": 0.00},
]

TAU = 2 * math.pi


def sri_triangle_points(tri, R=1.0):
    """Three vertices of one Sri Yantra triangle (returns 4 points; last = first, for edge iteration)."""
    pts = []
    for i in range(3):
        a = (-math.pi / 2 if tri["up"] else math.pi / 2) + i * TAU / 3 + tri["rot"]
        pts.append((R * tri["sc"] * math.cos(a), R * tri["sc"] * math.sin(a)))
    pts.append(pts[0])
    return pts


# ── Field model (verbatim from s4.html @ 594b3cf) ─────────────────────────

def get_active_devis(tithi):
    """Active Devi count for tithi: rises 1..15 across paksha, then mirrors back.

    Per s4.html: tithi <=15 returns 1..tithi; tithi 16..29 returns the
    descending mirror. We use tithi 1..15 here, so n = tithi.
    """
    if tithi <= 0:
        return [1]
    if tithi <= 15:
        return list(range(1, tithi + 1))
    rem = max(1, 30 - tithi + 1)
    return list(range(1, min(rem, 15) + 1))


def sample_field(x, y, angles, k, t=0.0):
    """Evaluate the standing-wave product field at (x,y).

    Each angle a in `angles` contributes a product cos(k·u_a)·cos(k·u_{a+π/2})
    where u_a = x cos(a) + y sin(a). This is the same product-of-perpendicular-
    plane-waves used in s4.html's bloom and aligned modes.
    """
    f = 0.0
    n = len(angles)
    for i, a in enumerate(angles):
        phase = t * 0.003 * i
        u1 = x * math.cos(a) + y * math.sin(a)
        u2 = x * math.cos(a + math.pi / 2) + y * math.sin(a + math.pi / 2)
        w1 = math.cos(k * u1 + phase)
        w2 = math.cos(k * u2 + phase)
        f += w1 * w2
    return f / max(n, 1)


def alignment(tithi, k, t=0.0, samples_per_edge=22, R=1.0):
    """Sri Yantra structural-match score: 0..100.

    For each Sri Yantra triangle edge, sample |field| at samples_per_edge
    equally-spaced points. Report (1 − mean(|field|)) × 100.

    Higher score = field is small at triangle edges = edges sit on nodal lines.
    """
    active = get_active_devis(tithi)
    n = len(active)
    angles = [i * TAU / n for i in range(n)]

    total_abs = 0.0
    samples = 0
    for tri in SRI_TRIS:
        pts = sri_triangle_points(tri, R=R)
        for e in range(3):
            x0, y0 = pts[e]
            x1, y1 = pts[e + 1]
            for s in range(samples_per_edge):
                frac = s / samples_per_edge
                sx = x0 + (x1 - x0) * frac
                sy = y0 + (y1 - y0) * frac
                total_abs += abs(sample_field(sx, sy, angles, k, t))
                samples += 1
    if samples == 0:
        return 0.0
    score = max(0, min(100, round((1 - total_abs / samples) * 100)))
    return score


# ── Run on all 15 tithis at k=12.0 (the v0.5 §2.5 setting) ────────────────

def main():
    print("=" * 70)
    print("SRI YANTRA ALIGNMENT — Coherence Atlas v0.5 §2.5 reproduction")
    print("=" * 70)
    print("Source: static/s4.html @ commit 594b3cf (Apr 8, 2026), lifted to Python.")
    print()

    LUNISOLAR_GEAR = 365.25 / 29.53  # = 12.3683...
    print(f"Lunisolar gear ratio (365.25 / 29.53): {LUNISOLAR_GEAR:.4f}")
    print()

    print(f"{'Tithi':>5}  {'N (active)':>10}  {'k=12.0':>10}  {'k=12.37':>10}  notes")
    print("-" * 70)
    results = {}
    for tithi in range(1, 16):
        score_120 = alignment(tithi, k=12.0)
        score_124 = alignment(tithi, k=LUNISOLAR_GEAR)
        results[tithi] = {
            "n_active": len(get_active_devis(tithi)),
            "alignment_at_k_12.0_pct": score_120,
            "alignment_at_k_12.368_pct": score_124,
        }
        note = ""
        if tithi == 11:
            note = "Ekadashi — v0.5 reports 85% at k=12.0"
        elif tithi == 15:
            note = "Purnima — v0.5 reports 82% at k=12.0"
        print(f"{tithi:>5}  {len(get_active_devis(tithi)):>10}  {score_120:>9}%  {score_124:>9}%  {note}")

    print()
    peak_120 = max(results, key=lambda t: results[t]["alignment_at_k_12.0_pct"])
    peak_124 = max(results, key=lambda t: results[t]["alignment_at_k_12.368_pct"])
    print(f"Peak alignment at k=12.0:    Tithi {peak_120} ({results[peak_120]['alignment_at_k_12.0_pct']}%)")
    print(f"Peak alignment at k=12.368:  Tithi {peak_124} ({results[peak_124]['alignment_at_k_12.368_pct']}%)")

    # Also k-sweep around 12.0–12.5 at T11 and T15 to map the gear-resonance
    print()
    print("k-sweep around lunisolar gear (T11 Ekadashi and T15 Purnima):")
    print(f"{'k':>6}  {'T11':>6}  {'T15':>6}")
    sweep_results = {}
    for k_int in range(110, 130):
        k_val = k_int / 10.0
        s11 = alignment(11, k=k_val)
        s15 = alignment(15, k=k_val)
        sweep_results[k_val] = {"T11": s11, "T15": s15}
        print(f"{k_val:>6.1f}  {s11:>5}%  {s15:>5}%")

    # Time-sweep at T11/T15 with k=12.0 — does the score peak at specific t?
    # The s4.html runs t as an animation parameter; v0.5 reports 85%/82% which
    # may be the peak across an oscillation cycle.
    print()
    print("t-sweep at k=12.0 (does the score peak at a specific phase?):")
    print(f"{'t':>6}  {'T11':>6}  {'T15':>6}")
    t_sweep = {}
    peak_t11 = (0, 0)
    peak_t15 = (0, 0)
    for t_int in range(0, 100):
        t_val = t_int * 0.5
        s11 = alignment(11, k=12.0, t=t_val)
        s15 = alignment(15, k=12.0, t=t_val)
        t_sweep[t_val] = {"T11": s11, "T15": s15}
        if s11 > peak_t11[1]:
            peak_t11 = (t_val, s11)
        if s15 > peak_t15[1]:
            peak_t15 = (t_val, s15)
        if t_int % 10 == 0 or s11 >= 84 or s15 >= 81:
            print(f"{t_val:>6.1f}  {s11:>5}%  {s15:>5}%")
    print(f"\nPeak T11 alignment over t-sweep: {peak_t11[1]}% at t={peak_t11[0]:.2f}")
    print(f"Peak T15 alignment over t-sweep: {peak_t15[1]}% at t={peak_t15[0]:.2f}")
    print(f"v0.5 §2.5 reports: T11 = 85%, T15 = 82% (animated-time peaks)")

    # Save JSON record
    out = {
        "metric": "Sri Yantra structural match — mean |field| along triangle edges, inverted to 0-100 score",
        "source_javascript": "static/s4.html @ commit 594b3cf (Apr 8 2026)",
        "founding_doc_reference": "Coherence Atlas v0.5 §2.5 page 17",
        "lunisolar_gear_ratio": round(LUNISOLAR_GEAR, 6),
        "per_tithi_at_k_12.0_and_12.368": results,
        "k_sweep_T11_T15": sweep_results,
        "t_sweep_T11_T15_at_k_12": t_sweep,
        "peak_T11_over_t": {"t": peak_t11[0], "score": peak_t11[1]},
        "peak_T15_over_t": {"t": peak_t15[0], "score": peak_t15[1]},
        "samples_per_edge": 22,
        "n_triangles": 9,
        "total_samples_per_score": 9 * 3 * 22,
    }
    out_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "snapshots", "bloom_20260408_2122",
        "alignment_metric.json",
    )
    out_path = os.path.abspath(out_path)
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nResults written to: {out_path}")
    return out


if __name__ == "__main__":
    main()
