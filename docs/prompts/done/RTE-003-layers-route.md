# RTE-003: Wire /layers route

**Phase**: 2 — Data integrity  
**Priority**: HIGH  
**Estimated time**: 30 min  
**Depends on**: DS-001 (layer_mapping.csv must exist)

## Context

`layer_engine.py` is WORKING but the /layers and /layers/summary routes are PARTIAL
because layer_mapping.csv was missing. DS-001 created that file. Now wire the routes.

## Instructions

### Step 1: Verify DS-001 completed

```bash
test -f ~/atlas_core/datasets/layer_mapping.csv && echo "EXISTS" || echo "MISSING — run DS-001 first"
head -3 ~/atlas_core/datasets/layer_mapping.csv
```

If missing, stop — DS-001 must run first.

### Step 2: Test layer_engine directly

```bash
cd ~/atlas_core
python3 -c "
from npu_engine.layer_engine import all_layer_summaries, load_layer_mapping
mapping = load_layer_mapping()
print('Mapping rows:', len(mapping))
summaries = all_layer_summaries()
print('Summaries:', list(summaries.keys())[:5])
"
```

### Step 3: Check and fix the kernel routes

```bash
grep -n "def _layers\|def _layer_" ~/atlas_core/kernel.py
```

Read each function. They should call `layer_engine`. If they're stubs, wire them:

```python
# /layers
@app.route("/layers")
def _layers():
    from npu_engine.layer_engine import all_layer_summaries
    return jsonify(all_layer_summaries())

# /layers/summary  
@app.route("/layers/summary")
def _layers_summary():
    from npu_engine.layer_engine import all_layer_summaries
    return jsonify(all_layer_summaries())

# /layers/<layer>
@app.route("/layers/<layer>")
def _layer_detail(layer):
    from npu_engine.layer_engine import load_layer_data
    return jsonify(load_layer_data(layer))
```

### Step 4: Test

```bash
curl -s localhost:5000/layers | python3 -m json.tool | head -30
curl -s localhost:5000/layers/summary | python3 -m json.tool | head -20
```

## Success check

```bash
curl -s localhost:5000/layers | python3 -c \
  "import sys,json; d=json.load(sys.stdin); assert len(d)>0; print('OK:', list(d.keys())[:4])"
```

## Output

- Modify /layers route functions in `kernel.py` if needed
- No new files required (layer_mapping.csv already created by DS-001)
