# DS-008: Wire chandas/ to composition and sound engines

**Phase**: 4  
**Priority**: LOW  
**Estimated time**: 1–2 hrs  
**Depends on**: ENG-006 (chandas_engine.py)

## Context

Once chandas_engine.py exists, wire it into the sound and composition layers.
Metre affects rhythmic density, phrasing length, and syllable-to-beat mapping.

## Instructions

### Step 1: Verify chandas_engine exists

```bash
test -f ~/atlas_core/npu_engine/field/chandas_engine.py && echo "OK" || echo "Run ENG-006 first"
curl -s localhost:5000/chandas | python3 -m json.tool | head -10
```

### Step 2: Wire to phrase_engine

Read `npu_engine/phrase_engine.py` — find where phrase length is determined.
Import chandas context and use `syllables_per_pada` to set phrase length:

```python
# In phrase_engine.py PhraseEngine.generate():
from npu_engine.field.chandas_engine import derive_chandas
chandas = derive_chandas(field_state)
phrase_length = chandas.get('syllables_per_pada', 8)
```

### Step 3: Wire to composition_db

Read `npu_engine/composition_db.py` — `score_composition()` should boost
compositions whose metre matches current chandas context:

```python
# In score_composition():
from npu_engine.field.chandas_engine import derive_chandas
chandas = derive_chandas(field_state)
if comp.get('metre') == chandas.get('primary_metre'):
    score += 0.2  # boost for metre resonance
```

### Step 4: Add metre to /sound/spec response

In `_sound_spec()` kernel route, include chandas:
```python
from npu_engine.field.chandas_engine import derive_chandas
spec['chandas'] = derive_chandas(fs)
```

### Step 5: Test

```bash
curl -s localhost:5000/sound/spec | python3 -c "
import sys,json; d=json.load(sys.stdin)
print('chandas in spec:', 'chandas' in d)
if 'chandas' in d: print(d['chandas'].get('primary_metre'))
"
```

## Success check

```bash
python3 -c "
from npu_engine.build_field_state import build_field_state
from npu_engine.field.chandas_engine import derive_chandas
fs = build_field_state()
c = derive_chandas(fs)
print('Chandas wired OK:', c.get('primary_metre'), c.get('syllables_per_pada'))
"
```

## Output

- Update `npu_engine/phrase_engine.py`
- Update `npu_engine/composition_db.py`
- Update `/sound/spec` route in kernel.py
