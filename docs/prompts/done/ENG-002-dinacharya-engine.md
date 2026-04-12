# ENG-002: Build S6 dinacharya_engine.py

**Phase**: 4  
**Priority**: MEDIUM  
**Estimated time**: 1–2 days

## Context

S6 (lived experience / ritual / daily practice) has 0 dedicated engines.
The journal, bandhu_chat, and reading routes are PARTIAL. A `dinacharya_engine.py`
synthesizes muhurta, observance, devi context, and ayurvedic daily practice into
a unified "what to do now" layer — the most practically useful output Atlas can produce.

## Files to use

```
datasets/ayurveda/dinacharya_panchanga.csv   — 8 rows: muhurta → practice
datasets/cosmology/daily_program.csv         — 8 rows: ashtakala → activity/mantra
datasets/cosmology/ashtakala.csv             — 8 rows: time periods
datasets/svarodaya/activity_matrix.csv       — 210 rows: nadi → activity
datasets/ayurveda/dosha_nakshatra_matrix.csv — 27 rows: nakshatra → practice
```

Read all files first:
```bash
for f in datasets/ayurveda/dinacharya_panchanga.csv \
          datasets/cosmology/daily_program.csv \
          datasets/cosmology/ashtakala.csv; do
  echo "=== $f ==="; cat ~/atlas_core/$f; echo
done
```

## Instructions

### Step 1: Read goloka_engine for ashtakala pattern

```bash
cat ~/atlas_core/npu_engine/field/goloka_engine.py | head -100
```
The dinacharya engine uses ashtakala the same way goloka_engine does.

### Step 2: Build `npu_engine/field/dinacharya_engine.py`

```python
"""
dinacharya_engine.py

Domain: S6 — Lived Experience
Purpose: Synthesizes field state into practical daily guidance — what to do,
         eat, study, avoid in this moment. The experiential layer of Atlas.

Atlas Relations:
  ashtakala → activity → mantra → offering
  muhurta → recommended_practices → herbs
  nakshatra → dosha → dietary_guidance
  nadi (svarodaya) → favored_activities
"""
```

Output structure:
```python
def derive_dinacharya(field_state: dict) -> dict:
    return {
        "ashtakala_period": "...",
        "primary_activity": "...",       # from daily_program
        "mantra": "...",                 # from daily_program
        "offering": "...",               # from daily_program
        "recommended_practices": [...],  # from dinacharya_panchanga
        "recommended_herbs": [...],      # from dinacharya_panchanga
        "dietary_guidance": "...",       # from dosha_nakshatra_matrix
        "avoid": [...],                  # from svarodaya activity_matrix
        "dosha_active": "...",           # from dinacharya_panchanga
        "raga": "...",                   # from ashtakala
        "source": "dinacharya_engine"
    }
```

### Step 3: Register route

```python
@app.route("/dinacharya")
def _dinacharya():
    from npu_engine.field.dinacharya_engine import derive_dinacharya
    fs = build_field_state()
    return jsonify(derive_dinacharya(fs))
```

### Step 4: Connect to s3.html and home.html

Check `static/s3.html` — it calls `/calendar/day` and `/field`.
The `/dinacharya` response is better suited for the practice panel.
Add a fetch call for `/dinacharya` alongside the existing ones.

### Step 5: Test

```bash
curl -s localhost:5000/dinacharya | python3 -m json.tool
```

The output should read like a coherent practice brief for the current moment.

## Success check

```bash
curl -s localhost:5000/dinacharya | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert 'ashtakala_period' in d
assert 'primary_activity' in d
assert 'recommended_practices' in d
print('dinacharya OK')
print('Period:', d['ashtakala_period'])
print('Activity:', d['primary_activity'])
print('Practices:', d['recommended_practices'][:2])
"
```

## Output

- Create `npu_engine/field/dinacharya_engine.py`
- Add GET /dinacharya route to kernel.py
- Optionally update s3.html to call /dinacharya
