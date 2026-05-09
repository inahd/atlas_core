# REAL_MATH_INVENTORY

Substantive mathematical computations in the Atlas core. Trivial expressions, string manipulation, dataset lookups, and database queries are excluded. Formulas are quoted from source as written.

Organized by domain. Each entry: function · file:line · formula · meaning · inputs · domain tag.

---

## Domain: WAVE_FIELD (two-source interference)

### 1. `compute_pair_interference` · npu_engine/jyotisha_engine.py:528
```python
d1 = math.radians(target_long - source_1_long)
d2 = math.radians(target_long - source_2_long)
return math.cos(k * d1) + math.cos(k * d2)
```
Two-source wave interference at a target ecliptic point. `k` is the harmonic order; output is amplitude in `[-2.0, +2.0]`. The kernel of the planetary wave field — every aspect/yoga interpretation reduces to this.
**Inputs:** sidereal longitudes (Sun, Moon, Mars … Lagna), `k ∈ {1,2,3,4,6,7,12}` mapping to conjunction/opposition/trine/square/sextile/septile/rashi.
**Tag:** `wave_field`

### 2. `compute_wave_field` · npu_engine/jyotisha_engine.py:545
For all `(a,b)` pairs in `combinations(graha_names, 2)`, for every target longitude `t` and every harmonic `k`:
```python
total = sum(abs(a) for _, a in entries)        # composite per (target,k)
target_results[t]["composite_normalized"][k] = (vals[t] - mn) / rng
```
Aggregates pair amplitudes into a per-target composite, normalizes across targets per harmonic, then takes the mean across harmonics.
**Inputs:** graha longitudes from `compute_chart`, optional explicit `targets`.
**Tag:** `wave_field`

### 3. `compute_nakshatra_field` · npu_engine/jyotisha_engine.py:658
```python
nak_size = 360.0 / 27.0  # 13.333...
samples = [arc_start + d for d in range(int(nak_size) + 1)]
# for each sample, pair, k:
amp = compute_pair_interference(g_longs[a], g_longs[b], s, k)
total += abs(amp)
mean_amp = total / count
```
Integrates the two-source field over each nakshatra arc by 1° sampling, then min/max-normalizes the 27-entry vector. Produces the Chladni-style "field_vector" used downstream.
**Inputs:** graha longitudes, optional `k_values`.
**Tag:** `wave_field`

---

## Domain: COHERENCE (toroidal geometry)

### 4. `toroidal_distance` · npu_engine/toroidal_field.py:160
```python
d_theta = math.pi - abs(abs(theta1 - theta2) - math.pi)
d_phi   = math.pi - abs(abs(phi1   - phi2)   - math.pi)
arc_theta = d_theta * (R + r)
arc_phi   = d_phi   * r
return math.sqrt(arc_theta**2 + arc_phi**2)
```
Wrapped angular distance on a torus surface, then Pythagorean combination of major-arc and minor-arc lengths. Wraps cleanly: distance from θ=0 to θ=2π is 0. `R=3.0`, `r=1.0`.
**Inputs:** two `(θ, φ)` coordinates on the toroid.
**Tag:** `coherence`

### 5. `coherence_from_distance` · npu_engine/toroidal_field.py:187
```python
normalized = dist / max_dist
return (math.cos(normalized * math.pi) + 1) / 2
```
Cosine falloff converting toroidal distance to coherence score in `[0, 1]`. Smooth — no hard threshold.
**Tag:** `coherence`

### 6. `max_toroidal_distance` · npu_engine/toroidal_field.py:181
```python
return math.sqrt((math.pi * (R + r))**2 + (math.pi * r)**2)
```
Antipodal distance on the toroid — used as the normalizer for coherence falloff.
**Tag:** `coherence`

### 7. `toroid_3d` · npu_engine/toroidal_field.py:147
```python
x = (R + r * math.cos(phi)) * math.cos(theta)
y = (R + r * math.cos(phi)) * math.sin(theta)
z = r * math.sin(phi)
```
Standard parametric torus embedding. Used for visualization of the brahmanda canvas; cached in numpy arrays in `_build_arrays`.
**Tag:** `coherence`

### 8. `_circular_mean` · npu_engine/toroidal_field.py:251
```python
sin_sum = sum(w * math.sin(a) for a, w in angle_weight_pairs)
cos_sum = sum(w * math.cos(a) for a, w in angle_weight_pairs)
return math.atan2(sin_sum, cos_sum) % (2 * math.pi)
```
Weighted circular mean — collapses (nakshatra=0.5, tithi=0.35, vara=0.15) signals into the panchanga's θ coordinate without wrap discontinuities.
**Tag:** `coherence`

### 9. `ToroidalField.field_query` · npu_engine/toroidal_field.py:378 (vectorized)
```python
d_theta = np.pi - np.abs(np.abs(self.entity_theta - theta1) - np.pi)
d_phi   = np.pi - np.abs(np.abs(self.entity_phi   - phi1)   - np.pi)
arc_theta = d_theta * (self.R + self.r)
arc_phi   = d_phi   * self.r
distances = np.sqrt(arc_theta**2 + arc_phi**2)
normalized = distances / self.max_dist
scores = (np.cos(normalized * np.pi) + 1) / 2
scores = scores * self._cat_weights
scores = np.minimum(1.0, scores + self._bhakti_boost)
```
Vectorized batch coherence over all 16k entities; the same formula compiled to OpenVINO with entity coords baked as constants in `_compile_npu` (moment as the only runtime input).
**Tag:** `coherence`

### 10. `rerank_entities` (composite score) · npu_engine/coherence_engine_v2.py:122
```python
sem_mod = (sem - 0.5) * 2 * MAX_SEMANTIC_MOD     # ±0.05
composite = _cat_w(eid) * (
    W_GEOMETRIC * geo            # 0.65
    + W_RELATIONAL * rel         # 0.25
    + W_AUTHORITY * auth         # 0.10
    + sem_mod
)
```
Weighted blend — geometric toroidal proximity (0.65) + graph relational support (0.25) + canonical authority (0.10) ± bounded semantic modulation (≤0.05). Category weight applied multiplicatively after.
**Tag:** `coherence`

### 11. `score_hybrid` · core/coherence_engine.py:203
```python
rule_norm = r.score / _MAX_RULE_SCORE                  # _MAX_RULE_SCORE = 13.0
hybrid = (rule_norm * RULE_WEIGHT) + (sem_score * SEMANTIC_WEIGHT)
r.score = round(hybrid * _cat_w(r.candidate), 6)
```
Tithi×graha×plant rule scoring (4+4+2+3 max=13) blended with vector-store semantic score; default RULE_WEIGHT=0.5.
**Tag:** `coherence`

### 12. `VectorStore._search_bm25` · npu_engine/vector_store.py:519
```python
# idf
return math.log(1.0 + (self._num_docs - df + 0.5) / (df + 0.5))
# scoring loop (k1=1.5, b=0.75)
denom = tf + k1 * (1.0 - b + b * (dl / (self._avg_len + 1e-9)))
scores[doc_id] += idf * (tf * (k1 + 1.0)) / (denom + 1e-9)
```
Standard BM25 with length normalization. The default search backend over 140k corpus chunks.
**Tag:** `coherence`

---

## Domain: JYOTISH (chart computation)

### 13. `compute_chart` · npu_engine/jyotisha_engine.py:66
Sidereal longitudes from Swiss Ephemeris:
```python
hour_dec = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour_dec)
sid_lon = (trop_lon - aya_deg) % 360
bhava = ((graha_rashi_idx - asc_rashi_idx) % 12) + 1
```
Gregorian → Julian day, ayanamsha subtraction (Lahiri/Raman/KP/etc.) to convert tropical → sidereal, whole-sign bhava from rashi offset to lagna.
**Inputs:** `dt_utc`, `lat`, `lon`, ayanamsha mode.
**Tag:** `jyotish`

### 14. `_navamsha_longitude` · npu_engine/jyotisha_engine.py:234
```python
rashi_idx = int((sid_lon % 360) / 30) % 12
deg_in_rashi = sid_lon % 30
navamsha_offset = int(deg_in_rashi / (30 / 9))
element_group = rashi_idx % 4
origins = {0: 0, 1: 9, 2: 6, 3: 3}        # fire/earth/air/water Parashara origins
nav_rashi_idx = (origins[element_group] + navamsha_offset) % 12
return nav_rashi_idx * 30.0 + (deg_in_rashi % (30 / 9)) * 9
```
D9 navamsha mapping per Parashara. Splits each 30° rashi into 9×3°20' navamshas, with origin rashi by element class.
**Tag:** `jyotish`

### 15. `assess_combustion` · npu_engine/jyotisha_engine.py:253
```python
elongation = abs((g["deg_absolute"] - sun_long + 180) % 360 - 180)
orb = orbs[1] if g.get("retrograde") else orbs[0]
g["combust"] = elongation < orb
```
Sun-relative elongation with orb cutoffs per planet (Mars 17°, Mercury 14/12°, Jupiter 11°, etc.). The `(x + 180) mod 360 − 180` trick gives signed shortest-arc distance.
**Tag:** `jyotish`

### 16. `compute_tithi` · npu_engine/jyotisha_engine.py:420
```python
phase = (moon_long - sun_long) % 360
tidx = min(int(phase / 12), 29)
paksha = "Shukla" if tidx < 15 else "Krishna"
```
Sun-Moon phase angle / 12° gives tithi index 0..29; first 15 = Shukla paksha.
**Tag:** `panchanga`

### 17. `compute_tara_bala` · npu_engine/jyotisha_engine.py:393
```python
tara = (transit_nak_index - birth_nak_index) % 27
category_idx = tara % 9
cycle = (tara // 9) + 1
```
Distance from natal nakshatra mod 27, broken into three 9-cycles giving Janma/Sampat/Vipat/Kshema/Pratyari/Sadhaka/Vadha/Mitra/Ati-Mitra.
**Tag:** `jyotish`

### 18. `bisection_search` (ayanamsha calibration) · drik_panchanga.py:188
```python
while True:
    middle = (left + right) / 2
    midval = func(middle)
    if midval * rtval >= 0: right = middle
    else: left = middle
    if (right - left) <= epsilon: break
```
Root-finder used to derive a custom ayanamsha by placing Citra at 180° (Citra-paksha calibration). Termination at `epsilon = 5e-10`.
**Tag:** `jyotish`

### 19. `inverse_lagrange` · drik_panchanga.py:213
Lagrange polynomial interpolation solving for `xa` such that `f(xa) = ya`:
```python
for i in range(len(x)):
    numer = 1; denom = 1
    for j in range(len(x)):
        if j != i:
            numer *= (ya - y[j])
            denom *= (y[i] - y[j])
    total += numer * x[i] / denom
```
Used to invert nakshatra/tithi end-time functions back to Julian day.
**Tag:** `jyotish`

### 20. `derive_helix_field` · npu_engine/field/helix_engine.py:113-170
```python
phi = day_frac * math.pi * 2          # toroidal (solar year)
theta = (tidx / 30.0) * math.pi * 2   # poloidal (lunar month)
rahu_phi = (rl / 360.0) * math.pi * 2
moon_rahu_dist = abs(((ml - rl + 180) % 360) - 180)
is_eclipse = moon_rahu_dist < 18
fav = nak_q * 0.35 + tit_q * 0.30 + rahu_q * 0.20 + vara_q * 0.15
tp = _torus_point(phi, phi * 13)      # spiral: theta = phi * 13
```
Per-day torus helix for a 90-day forward window. Solar-year angle on the major axis, lunar phase on the minor axis, eclipse zone via shortest-arc moon-Rahu distance, weighted favorability.
**Tag:** `jyotish`

---

## Domain: SOUND (synthesis & timbre)

### 21. `_glottal_source` · npu_engine/bija_synth.py:82
```python
t = np.arange(n_samples) / SR
vib = 1.0 + vibrato_depth * np.sin(2 * np.pi * vibrato_hz * t)
phase = np.cumsum(f0 * vib / SR)
frac = phase % 1.0
pulse = np.where(frac < 0.4, 0.5 * (1 - np.cos(np.pi * frac / 0.4)),
                 np.where(frac < 0.6, 0.5 * (1 + np.cos(np.pi * (frac - 0.4) / 0.2)),
                          0))
```
Vibrato-modulated glottal pulse for bīja synthesis. FM via `cumsum` of instantaneous frequency, then a piecewise raised-cosine pulse shape.
**Tag:** `sound`

### 22. `_envelope` · npu_engine/bija_synth.py:144
```python
env[:atk] = 0.5 * (1 - np.cos(np.pi * np.arange(atk) / atk))           # raised-cosine attack
env[atk:atk + sus] = 1.0 - (1 - sustain_ratio) * np.linspace(0, 1, sus) ** 2
env[atk + sus:] = start_level * 0.5 * (1 + np.cos(np.pi * np.arange(rel) / rel))
```
ADSR built from raised-cosine attack/release with a quadratic sustain decay.
**Tag:** `sound`

### 23. `SarangiString.render` · npu_engine/sarangi_voice.py:56
```python
B = self.inharmonicity                          # 0.0006
for n, strength in harmonics:                   # weighted odd-dominant
    fn = self.freq * n * math.sqrt(1 + B * n * n)
    decay = np.exp(-t * (0.15 + n * 0.08))
    phase = 2 * math.pi * fn * t + self._phase * n
    out += strength * decay * np.sin(phase)
```
Bowed-string additive synth: stretched-string inharmonicity (`fn = n·f0·√(1 + B·n²)`), per-harmonic exponential decay, then a 2nd-order IIR (`b=[1, 0, -0.68]`, `a=[1, -1.65, 0.72]`) for nasal body resonance.
**Tag:** `sound`

### 24. `SarangiVoice._ji_tune` · npu_engine/sarangi_voice.py:183
```python
JI = [0.5, 256/243, 9/8, 32/27, 5/4, 4/3, 45/32,
      3/2, 128/81, 5/3, 16/9, 15/8, 2.0, 3.0, 4.0]
nearest = min(JI, key=lambda r: abs(r - ratio))
return self.sa_hz * nearest
```
Snaps incoming frequencies to the nearest 22-shruti just-intonation ratio against `sa_hz`. The same swara→ratio table appears in `santoor_engine.SWARA_RATIOS`.
**Tag:** `sound`

### 25. `_synth_bol` · npu_engine/tabla_sampler.py:130
```python
env = np.exp(-t / max(decay_time, 0.01))
freq = f0 * (1.0 - pitch_drop * t / dur)        # membrane-relaxation glide
phase = np.cumsum(2 * np.pi * freq / sr)
sig  = 0.50 * np.sin(phase)        * env
sig += 0.25 * np.sin(phase * f1r)  * env ** 1.5
sig += 0.12 * np.sin(phase * f2r)  * env ** 2.0
body = 0.35 * np.sin(2 * np.pi * body_f0 * t) * np.exp(-t / (decay_time * 2))
noise * np.exp(-t / 0.008)                       # 8ms attack burst
```
Three-mode tabla membrane synthesis with linear pitch drop, body resonance for bass bols (Dha/Ghe), and an exponential noise transient. Mode ratios per-bol (Dha=1, 2.3, 3.8 etc.).
**Tag:** `sound`

### 26. `_fallback_render` (additive tanpura) · npu_engine/tanpura_engine.py:342
```python
for j, amp in enumerate([1.0, 0.5, 0.25, 0.12, 0.06]):
    freq = f0 * (j + 1)
    decay = np.exp(-t * (0.3 + j * 0.4))
    out += amp * decay * np.sin(2 * np.pi * freq * t)
```
Pure additive harmonic tanpura with per-partial exponential decay; the modal-physics `om.tanpura_string` is preferred when available.
**Tag:** `sound`

### 27. `derive_tanpura_params` · npu_engine/tanpura_field.py:128
```python
sa_hz = base_sa * (2 ** (offset / 12.0))         # equal-temp semitone offset from element
while sa_hz < 110.0: sa_hz *= 2.0
while sa_hz > 220.0: sa_hz /= 2.0
tithi_mod = 1.0 - 0.15 * math.sin(math.pi * tidx / 15.0)
cycle_gap_ms = int(guna_gap * tithi_mod)
```
Field-driven tanpura tuning: prahar→base Sa, element offset in semitones (12-TET), wrap-octave to playable range; tithi-modulated cycle timing (`sin(π·tidx/15)` peaks at Pūrṇimā).
**Tag:** `sound`

### 28. `tithi_string_weights` · npu_engine/tanpura_field.py:98
```python
# Shukla paksha (1..14)
phase = tidx / 14.0
return [0.4 + 0.6*phase, 0.5 + 0.5*phase, 0.5 + 0.5*phase, 1.0]
# Krishna paksha (15..28)
phase = (tidx - 14) / 15.0
return [1.0 - 0.6*phase, 1.0 - 0.5*phase, 1.0 - 0.5*phase, 1.0]
```
Per-string amplitude envelope across the lunar month: tanpura strings build through Shukla, fully consonant at Pūrṇimā, dissolve through Krishna; Sa string remains constant.
**Tag:** `sound`

---

## Domain: GEOMETRY (yantra & quasicrystal)

### 29. `project_nfold` · npu_engine/geometry/cut_and_project.py:22
```python
for j in range(N):
    angle = 2 * np.pi * j / N + phase
    proj = X * np.cos(angle) + Y * np.sin(angle)
    field += np.cos(proj + gamma * j)
```
Multigrid-method N-fold quasicrystal: sum of N plane-wave cosines at equal angular spacing `2π·j/N`. Equivalent to the cut-and-project tiling's Fourier transform; produces aperiodic patterns for `N ∈ {5,7,8,9,10,11,12,13,14,15}`.
**Tag:** `geometry`

### 30. `project_sri_yantra` · npu_engine/geometry/cut_and_project.py:106
```python
for tithi, N in DEVI_N.items():            # 1..15 → 3,6,3,3,8,6,7,8,9,10,11,12,13,14,15
    phase = 2 * np.pi * (tithi - 1) / 15
    layer = project_nfold(N, phase=phase, k=k, size=size)
    composite += w * layer
```
Superposition of all 15 Nitya Devi N-fold fields, each rotated by `2π·(tithi−1)/15`. Composite is then min/max normalized.
**Tag:** `geometry`

### 31. `_rhombic_triacontahedron` · npu_engine/geometry/cut_and_project.py:234
```python
phi = (1 + np.sqrt(5)) / 2                 # golden ratio
# icosidodecahedron vertices: (0,0,±phi) perms + (±½, ±phi/2, ±(1+phi)/2) perms
hull_id = ConvexHull(iv)
# face-center centroids → 32 RT vertices
rt_hull = ConvexHull(rt_verts)
# pair triangles sharing a T-T edge → 30 rhombic faces (= 30 tithis)
```
Constructs the 32-vertex / 60-triangle rhombic triacontahedron as the dual of the icosidodecahedron, then pairs near-coplanar triangles (T-T edge sharing) into 30 rhombic faces, sorted by centroid azimuth for deterministic tithi ordering.
**Tag:** `geometry`

### 32. `_euclidean_rhythm` (Bjorklund-ish) · npu_engine/yantra_engine.py:47
```python
result = []
acc = 0
for i in range(pulses):
    result.append(round(acc))
    acc += beats / pulses
return sorted(set(r % beats for r in result))
```
Even-distribution accent placement on a polygon perimeter. Produces e.g. tresillo `[0,3,6]` for `(8,3)`.
**Tag:** `geometry`

### 33. `_polygon_points` & `_lotus_petals` · npu_engine/yantra_engine.py:81 / :93
```python
angle = rotation + (i / sides) * math.pi * 2 - math.pi / 2
x = cx + r * math.cos(angle); y = cy + r * math.sin(angle)
```
Polygon vertices and lotus-petal tip/side computation around `(cx, cy)`. Rotation offset is keyed to guṇa (`sattva=0`, `rajas=π/6`, `tamas=π/4`).
**Tag:** `geometry`

### 34. `TempleGeometry._symmetry_score` · npu_engine/temple_geometry.py:82
```python
ideal_gap = 2 * math.pi / n
gaps = [(thetas[(i+1) % n] - thetas[i]) % (2*math.pi) for i in range(n)]
variance = sum((g - ideal_gap) ** 2 for g in gaps) / n
return max(0, 1.0 - variance / ideal_gap**2)
```
Detects sacred-geometry formations (chatushkona/shatkona/ashtadala/navagraha/shodasha/nakshatra-mandala/vastu-pada) by measuring how evenly entities are distributed around the θ-circle.
**Tag:** `geometry`

### 35. `_dim` / `_mid` (per-yuga color falloff) · npu_engine/yantra_generator.py:28
```python
return f"#{r//5:02x}{g//5:02x}{b//5:02x}"        # ~20% brightness
return f"#{r*2//5:02x}{g*2//5:02x}{b*2//5:02x}"  # ~40% brightness
```
Integer-divide hex-color brightness reduction used to render co-triangulars at medium and inactive triangles dim in the Sri Yantra SVG.
**Tag:** `geometry`

---

## Domain: VASTU & SITE (terrain / direction)

### 36. `_compute_slope` (Horn's method) · npu_engine/field/site_engine.py:168
```python
dz_dx = ((g[r-1,c+1] + 2*g[r,c+1] + g[r+1,c+1]) -
         (g[r-1,c-1] + 2*g[r,c-1] + g[r+1,c-1])) / (8 * cell_size_m)
dz_dy = ((g[r+1,c-1] + 2*g[r+1,c] + g[r+1,c+1]) -
         (g[r-1,c-1] + 2*g[r-1,c] + g[r-1,c+1])) / (8 * cell_size_m)
slope[r,c] = math.sqrt(dz_dx**2 + dz_dy**2) * 100
```
Horn's 3×3 Sobel-weighted finite-difference slope on a DEM, in percent. `_compute_aspect` (line 186) uses the same kernel with `math.atan2(dz_dy, -dz_dx)` for compass-bearing aspect.
**Tag:** `terrain`

### 37. `_compute_flow_direction` (D8) · npu_engine/field/site_engine.py:205
```python
dr = [0,1,1,1,0,-1,-1,-1]; dc = [1,1,0,-1,-1,-1,0,1]
codes = [1,2,4,8,16,32,64,128]
dist = [1, 1.414, 1, 1.414, 1, 1.414, 1, 1.414]
drop = (g[r,c] - g[nr,nc]) / dist[i]
# pick max-drop neighbor
```
Standard D8 flow direction: assigns each cell to the steepest descent neighbor, scaled by Euclidean distance to handle diagonals. `_compute_flow_accumulation` propagates upstream cell counts iteratively.
**Tag:** `terrain`

### 38. `_compute_solar` · npu_engine/field/site_engine.py:370
```python
summer = min(90, 90 - abs_lat + 23.5)
winter = max(0, 90 - abs_lat - 23.5)
house_shadow_radius = round(house_h / math.tan(math.radians(winter)), 1)
```
Solar altitude at solstices (±23.5° axial tilt) and resulting winter shadow radius from a 5m reference structure.
**Tag:** `terrain`

### 39. `vastu_engine._build_grid` · npu_engine/vastu_engine.py:96
```python
dx = col - 3.5; dy = row - 3.5
dist = math.sqrt(dx*dx + dy*dy)
# cells sorted ascending by dist → priority order (Brahmasthāna fills first)
```
The 64-pada (8×8) Vastu grid keyed on Euclidean distance from center; deities and elements fill from inside out.
**Tag:** `geometry`

### 40. `geosolar_engine.get_geosolar_state` (field modifier) · npu_engine/field/geosolar_engine.py:204
```python
kp_norm   = min(kp["kp"] / 9, 1.0)
xray_norm = min(max((math.log10(xray["flux"]) + 8) / 5, 0), 1.0)
wind_norm = min(wind["speed"] / 800, 1.0)
bz_norm   = min(max(-wind["bz"], 0) / 20, 1.0)
seis_norm = min(seis["max_magnitude"] / 8, 1.0)
modifier  = 0.30*kp_norm + 0.20*xray_norm + 0.15*wind_norm + 0.15*bz_norm + 0.20*seis_norm
```
Combined geomagnetic + solar + seismic disturbance modifier `[0,1]`. Logarithmic X-ray normalization (5 decades over `1e-8` to `1e-3` W/m²); southward Bz emphasized (`-bz` clipped at 0).
**Tag:** `geosolar`

---

## Domain: RHYTHM (tala dynamics)

### 41. `sam_field.get_gravity` · npu_engine/rhythm/sam_field.py:12
```python
dist_to_sam = (beats - pos) % beats
norm_dist = dist_to_sam / beats
approach_factor = 0.0
if dist_to_sam <= 3:
    approach_factor = math.exp(-dist_to_sam * 0.8) * 0.4
gravity = vib_gravity * (1 - approach_factor) + approach_factor
# layakari scaling
gravity = gravity ** (1 / layakari)
```
Sam-gravity per beat: vibhag baseline + exponential spike in last 3 beats before sam, then layakari power-curve compression/expansion.
**Tag:** `rhythm`

### 42. `cross_rhythm_engine.get_cross_rhythm` · npu_engine/rhythm/cross_rhythm_engine.py:18
```python
from math import gcd
lcm = (sub * tala_beats) // gcd(sub, tala_beats)
if lcm > tala_beats * 2:
    return None
tension = cross["tension"] * (0.5 + arc * 0.5)
```
LCM resolution test: a polyrhythmic subdivision is admitted only if it lands back on a tala beat within 2 cycles. Tension scales linearly with arc position past 0.3.
**Tag:** `rhythm`

### 43. `tihai_engine.find_tihai` · npu_engine/rhythm/tihai_engine.py:21
```python
# math: current + 3*P + 2*G ≡ sam (mod tala_beats)
for phrase in phrases:
    P = len(phrase)
    for G in range(3):                  # gap 0/1/2
        total = 3 * P + 2 * G
        if total == to_sam or total == to_sam + tala_beats:
            return Tihai(...)
```
Tihai (3-fold phrase landing on sam) solved as a Diophantine condition `3P + 2G = to_sam (mod cycle)`.
**Tag:** `rhythm`

### 44. `sam_field.get_tension` (cross-rhythm misalignment) · npu_engine/rhythm/sam_field.py:52
```python
base_unit = tala.beats / len(tala.vibhag)
nearest_grid = round(pos / base_unit) * base_unit
offset = abs(pos - nearest_grid) / base_unit
return min(1.0, offset * 2)
```
Polyrhythmic tension as the normalized distance from the cross-rhythm subdivision to the nearest vibhag grid point.
**Tag:** `rhythm`

---

## Domain: PSI / LIFECYCLE (expression dynamics)

### 45. `temple_geometry.formation_lifecycle` · npu_engine/temple_geometry.py:149
```python
if arc_phase < 0.25:    intensity = arc_phase / 0.25                 # birth
elif arc_phase < 0.5:   intensity = 1.0                              # formation
elif arc_phase < 0.75:  intensity = 1.0 - (arc_phase - 0.5) / 0.25   # dissolution
else:                   intensity = 0.1 + 0.2 * math.sin((arc_phase - 0.75) / 0.25 * math.pi)
intensity *= sym
```
Lunar-arc-driven formation lifecycle envelope (Birth/Formation/Dissolution/Pralāya), modulated by the formation's symmetry score.
**Tag:** `lifecycle`

### 46. `modulation_engine.derive_psi` · npu_engine/modulation_engine.py:53
```python
# intensity from top-8 mean composite, blended with best formation symmetry
intensity = sum(top_scores) / len(top_scores)
intensity = intensity * 0.7 + best_sym * 0.3
# focus = top3_mean - tail3_mean (concentration)
spread = (sum(top3) / 3) - (sum(tail3) / 3)
focus  = min(1.0, spread * 2)
# stability — triangular peak at arc=0.4
if 0.2 <= arc <= 0.6:
    stability = 0.7 + 0.3 * (1.0 - abs(arc - 0.4) / 0.2)
elif arc < 0.2:    stability = 0.3 + arc * 2.0
else:              stability = max(0.1, 1.0 - (arc - 0.6) * 2.5)
```
Derives the ψ expression triple `(intensity, focus, stability)` purely from downstream field structure — top/tail score spread for concentration, arc position for stability envelope.
**Tag:** `lifecycle`

---

## Domain: ORIENTATION (philosophical 2-axis)

### 47. `orientation.nearest_position` · npu_engine/orientation.py:109
```python
d = math.sqrt((oneness - pos["o"])**2 + (path - pos["p"])**2)
```
Euclidean distance on the bhedābheda 2-axis (oneness ∈ [-1,+1], path ∈ [-1,+1]) to the 8 canonical philosophical positions (Śūnyatā, Advaita, Trika, Viśiṣṭādvaita, Śrī Vidyā, Acintya-bhedābheda, Anekāntavāda, Dvaita).
**Tag:** `orientation`

### 48. `torus_queries.torus_knot_distance` · npu_engine/torus_queries.py:20
```python
return math.sqrt((ax - bx)**2 + (ay - by)**2 + (az - bz)**2)
```
3D Euclidean distance between two padas on the precomputed torus-knot embedding — used to score nearest cross-ribbon padas for a given nakshatra.
**Tag:** `geometry`

---

## Notes

- Several "engines" (e.g. `swara_engine`, `phrase_engine`, `sound_engine`) are predominantly graph traversals + dictionary lookups; their substantive math lives in the synthesizers (`sarangi_voice`, `tabla_sampler`, `bija_synth`, `tanpura_field`) which are inventoried above.
- `npu_engine/sound/*.py` (top-level package init plus stubs) are 1-line re-export shims; the real implementations live one directory up at `npu_engine/<name>.py`.
- The OpenVINO NPU model in `toroidal_field._compile_npu` (line 439) re-implements entry #4–#5 in op-graph form so `compute(moment) → scores[N]` runs entirely on-device.
- `swisseph` (Swiss Ephemeris) provides the planetary-position primitives consumed by `compute_chart` and `helix_engine`; the math attributed to them above is what Atlas adds on top of `swe.calc_ut`.
