# ENG-003: Migrate one stub directory — npu_engine/time/

**Phase**: 5 — Architecture  
**Priority**: LOW  
**Estimated time**: 1–2 hrs per subdirectory

## Context

Several stub directories exist as planned refactor targets:
`npu_engine/core/`, `/geometry/`, `/zones/`, `/time/`, `/text/`, `/system/`

Each contains 1-line stub files. The working implementations live at
npu_engine/ top level and in npu_engine/field/.

This task migrates ONE subdirectory — `npu_engine/time/` — as a template
for the others. Do NOT migrate all at once.

## Instructions

### Step 1: Map what goes in npu_engine/time/

Time-related engines that should live here:
- `npu_engine/field/trajectory_engine.py` → `npu_engine/time/trajectory_engine.py`
- `npu_engine/field/intention_engine.py` → `npu_engine/time/intention_engine.py`
- `npu_engine/field_layers.py` → `npu_engine/time/field_layers.py`

Check what's currently a stub in time/:
```bash
for f in ~/atlas_core/npu_engine/time/*.py; do
    echo "=== $f ==="
    cat $f
done
```

### Step 2: Check all imports of the source files

```bash
grep -rn "from npu_engine.field.trajectory_engine\|from npu_engine.field_layers" \
  ~/atlas_core/kernel.py ~/atlas_core/npu_engine/ | grep -v ".pyc"
```

You must update ALL import paths or the migration will break things.

### Step 3: Migrate trajectory_engine only first

```bash
cp ~/atlas_core/npu_engine/field/trajectory_engine.py \
   ~/atlas_core/npu_engine/time/trajectory_engine.py
```

Update `npu_engine/time/trajectory_engine.py` — add any relative imports needed.

Update `npu_engine/time/__init__.py`:
```python
from npu_engine.time.trajectory_engine import derive_trajectory
```

### Step 4: Add backward-compatible re-export

In the OLD location `npu_engine/field/trajectory_engine.py`, replace contents with:
```python
# Backward compatibility shim — implementation moved to npu_engine/time/
from npu_engine.time.trajectory_engine import *  # noqa
```

This way ALL existing imports continue to work.

### Step 5: Test

```bash
cd ~/atlas_core
python3 -c "
from npu_engine.field.trajectory_engine import derive_trajectory
from npu_engine.time.trajectory_engine import derive_trajectory as dt2
print('Both imports work:', derive_trajectory is dt2)
"

curl -s localhost:5000/trajectory | python3 -c "import sys,json; d=json.load(sys.stdin); print('trajectory OK')"
```

### Step 6: Commit

```bash
git add -A && git commit -m "refactor: migrate trajectory_engine to npu_engine/time/"
```

Only proceed to the next file after this commit is stable.

## Success check

```bash
# New location works
python3 -c "from npu_engine.time.trajectory_engine import derive_trajectory; print('new path OK')"

# Old location still works (backward compat)
python3 -c "from npu_engine.field.trajectory_engine import derive_trajectory; print('old path OK')"

# Route still works
curl -s localhost:5000/trajectory | python3 -c "import sys,json; json.load(sys.stdin); print('route OK')"
```

## Output

- Populate `npu_engine/time/trajectory_engine.py` with real code
- Add backward-compat shim to old location
- Update `npu_engine/time/__init__.py`
- Do NOT touch other stub directories in this task
