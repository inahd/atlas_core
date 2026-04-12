# ENG-001: Build svarodaya_engine.py

**Phase**: 4 — Expand dark territory  
**Priority**: MEDIUM  
**Estimated time**: 1 day

## Context

`datasets/svarodaya/` has 6 rich files covering the ancient science of breath cycles
(svarodaya) — which nadi (ida/pingala/sushumna) is active at which tithi/vara/time,
and what activities are recommended. This connects to field_state, intention_engine,
and the body layer. No engine exists for it.

## Files to wire

```
datasets/svarodaya/activity_matrix.csv   — 210 rows: activity × nadi × element
datasets/svarodaya/tithi_rules.csv       — 60 rows: tithi+paksha → optimal nadi
datasets/svarodaya/vara_rules.csv        — 7 rows: vara → optimal nadi
datasets/svarodaya/elements.csv          — 5 rows: svara elements
datasets/svarodaya/nadis.csv             — 3 rows: ida, pingala, sushumna
datasets/svarodaya/coherence_rules.csv   — 6 rows: coherence rules
```

## Instructions

### Step 1: Read all source files

```bash
for f in datasets/svarodaya/*.csv; do
  echo "=== $f ==="; head -3 ~/atlas_core/$f; echo
done
```

### Step 2: Read sibling engines for pattern

```bash
cat ~/atlas_core/npu_engine/field/intention_engine.py | head -80
cat ~/atlas_core/npu_engine/engines/body_engine.py
```

### Step 3: Build `npu_engine/field/svarodaya_engine.py`

The engine should expose:

```python
def derive_svarodaya(field_state: dict) -> dict:
    """
    Given current field_state (tithi_num, vara, hora, nakshatra),
    return:
    - optimal_nadi: 'ida' | 'pingala' | 'sushumna'
    - recommended_activities: list of activity names
    - avoid_activities: list
    - element_of_breath: fire/water/earth/air/ether
    - coherence_score: float 0–1 (how aligned current activity context is)
    - source: citation from tithi_rules or vara_rules
    """
```

Logic:
1. Check `tithi_rules.csv` for tithi+paksha → nadi recommendation
2. Check `vara_rules.csv` for vara override
3. Look up `activity_matrix.csv` for activities matching the recommended nadi
4. Score coherence against any active intention in field_state
5. Return structured dict

### Step 4: Register in kernel.py

Add route:
```python
@app.route("/svarodaya")
def _svarodaya():
    from npu_engine.field.svarodaya_engine import derive_svarodaya
    fs = build_field_state()
    return jsonify(derive_svarodaya(fs))
```

### Step 5: Test

```bash
curl -s localhost:5000/svarodaya | python3 -m json.tool
```

Should return a JSON object with `optimal_nadi`, `recommended_activities`, etc.

## Success check

```bash
curl -s localhost:5000/svarodaya | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert 'optimal_nadi' in d, 'missing optimal_nadi'
assert d['optimal_nadi'] in ('ida','pingala','sushumna'), 'invalid nadi'
assert 'recommended_activities' in d, 'missing activities'
print('svarodaya_engine: OK —', d['optimal_nadi'])
"
```

## Output

- Create `npu_engine/field/svarodaya_engine.py`
- Add GET /svarodaya route to kernel.py
- Add import to `npu_engine/__init__.py` (check existing pattern)
