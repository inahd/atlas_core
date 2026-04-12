# DS-005 / ENG-005: Build astrobotany_engine.py

**Phase**: 4 — Expand dark territory  
**Priority**: MEDIUM  
**Estimated time**: 1–2 days

## Context

`datasets/astrobotany/` has 4 rich files covering the intersection of Vedic cosmology
and plant biology — astrobotanical classes (C1–C5), biodynamic-Vedic mapping, herbs
by class, and lunar plant biology research. No engine exists for it.

This connects the biodynamic calendar (element → planting day type) to the nakshatra
plant layer, the herb_spine_108 dataset, and the s5_kernel.

## Files to wire

```
datasets/astrobotany/astrobotanical_classes.csv  — 5 rows: C1-C5 classes
datasets/astrobotany/herbs_by_class.csv          — 100 rows: herb → class
datasets/astrobotany/biodynamic_vedic_mapping.csv — 12 rows: zodiac → day type
datasets/astrobotany/lunar_plant_biology.csv     — 8 rows: research claims
```

Read all four files before writing anything:
```bash
for f in ~/atlas_core/datasets/astrobotany/*.csv; do
  echo "=== $f ==="; cat $f; echo
done
```

## Instructions

### Step 1: Read sibling engines

```bash
cat ~/atlas_core/npu_engine/s5_kernel.py | head -80
cat ~/atlas_core/npu_engine/engines/plant_engine.py | head -60
```

### Step 2: Build `npu_engine/field/astrobotany_engine.py`

```python
"""
astrobotany_engine.py

Domain: S5 — Ecology & Embodiment
Purpose: Derives biodynamic planting guidance from field state using the
         astrobotanical class system (C1=plant, C2=leaf, C3=flower, C4=root, C5=rest).

Atlas Relations:
  nakshatra → element → astrobotanical_class (via biodynamic_vedic_mapping)
  tithi → moon phase → planting quality modifier
  field_state.panchanga → day_type, recommended_herbs, avoid_activities
"""
```

The engine should expose:

```python
def derive_astrobotany(field_state: dict) -> dict:
    return {
        "day_type": "plant|leaf|flower|root|rest",
        "day_class": "C1|C2|C3|C4|C5",
        "element": "fire|water|earth|air|ether",
        "planting_quality": 0.0-1.0,
        "recommended_herbs": [...],  # from herbs_by_class filtered by current class
        "nakshatra_plant": "...",    # from nakshatra_plants if available
        "lunar_note": "...",         # from lunar_plant_biology if relevant
        "source": "astrobotany_engine"
    }
```

Logic:
1. Get current nakshatra from field_state
2. Look up nakshatra element
3. Map element → biodynamic day type via `biodynamic_vedic_mapping.csv`
4. Get astrobotanical class for that day type from `astrobotanical_classes.csv`
5. Look up herbs for that class from `herbs_by_class.csv`
6. Score planting quality from tithi paksha (waxing=better for above-ground, waning=root)

### Step 3: Register route in kernel.py

```python
@app.route("/astrobotany")
def _astrobotany():
    from npu_engine.field.astrobotany_engine import derive_astrobotany
    fs = build_field_state()
    return jsonify(derive_astrobotany(fs))
```

### Step 4: Connect to s5_kernel

Read `npu_engine/s5_kernel.py` — find where it generates day type recommendations.
If it uses hardcoded logic, replace with a call to `astrobotany_engine.derive_astrobotany()`.

### Step 5: Test

```bash
curl -s localhost:5000/astrobotany | python3 -m json.tool
```

## Success check

```bash
curl -s localhost:5000/astrobotany | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert 'day_type' in d, 'missing day_type'
assert d['day_type'] in ('plant','leaf','flower','root','rest'), f'invalid: {d[\"day_type\"]}'
assert 'recommended_herbs' in d
print('astrobotany OK — day type:', d['day_type'], '| herbs:', len(d['recommended_herbs']))
"
```

## Output

- Create `npu_engine/field/astrobotany_engine.py`
- Add GET /astrobotany route to kernel.py
- Optionally update s5_kernel.py to use it
