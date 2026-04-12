# ENG-006: Build chandas_engine.py

**Phase**: 4  
**Priority**: LOW  
**Estimated time**: 1 day

## Context

`datasets/chandas/` has 2 rich files:
- `metres_forms.csv` (24 rows) — Sanskrit metres with syllable counts, padas, cadence
- `metre_correspondence_matrix.csv` (32 rows) — metre → graha/nakshatra correspondences

No engine uses them. Chandas (prosody) connects to composition_db (each composition
has a metre), the sound engine (metre affects rhythm), and the corpus layer.

## Instructions

### Step 1: Read both files

```bash
cat ~/atlas_core/datasets/chandas/metres_forms.csv
cat ~/atlas_core/datasets/chandas/metre_correspondence_matrix.csv
cat ~/atlas_core/npu_engine/composition_db.py | head -80
```

### Step 2: Build npu_engine/field/chandas_engine.py

```python
"""
chandas_engine.py

Domain: S2/S3 — Sound & Time
Purpose: Derives prosodic context — which metres resonate with current
         graha/nakshatra, what rhythmic character they suggest.

Atlas Relations:
  metre → graha_correspondence (metre_correspondence_matrix)
  metre → syllable_count → tala_beat_count
  composition → metre → chandas_character
"""

def derive_chandas(field_state: dict) -> dict:
    return {
        "resonant_metres": [...],    # metres matching current graha/nakshatra
        "primary_metre": "...",      # strongest match
        "syllables_per_pada": 8,     # rhythmic unit for current moment
        "graha_connection": "...",
        "rhythmic_character": "flowing|vigorous|stately|rapid",
        "source": "chandas_engine"
    }
```

Logic:
1. Get current graha and nakshatra from field_state
2. Look up `metre_correspondence_matrix.csv` for metres matching current graha
3. Look up `metres_forms.csv` for syllable/pada details of those metres
4. Score by resonance_score column if present

### Step 3: Connect to composition_db

In `composition_db.py`, import chandas_engine and use it to boost compositions
whose metre matches the current chandas context.

### Step 4: Register route

```python
@app.route("/chandas")
def _chandas():
    from npu_engine.field.chandas_engine import derive_chandas
    fs = build_field_state()
    return jsonify(derive_chandas(fs))
```

### Step 5: Test

```bash
curl -s localhost:5000/chandas | python3 -m json.tool
```

## Success check

```bash
curl -s localhost:5000/chandas | python3 -c "
import sys,json
d=json.load(sys.stdin)
assert 'primary_metre' in d
assert 'syllables_per_pada' in d
print('chandas OK — metre:', d['primary_metre'])
"
```

## Output

- Create `npu_engine/field/chandas_engine.py`
- Add GET /chandas route to kernel.py
- Update `composition_db.py` to use chandas context
