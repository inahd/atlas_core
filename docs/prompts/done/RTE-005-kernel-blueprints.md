# RTE-005: Split kernel.py into Flask blueprints

**Phase**: 5 — Architecture  
**Priority**: LOW  
**Estimated time**: 3–5 days (do incrementally — one blueprint per session)

## Context

`kernel.py` is ~9,800 lines with 203 routes. This is maintainable but barely.
Splitting into Flask blueprints makes it navigable, testable, and reduces
the risk of merge conflicts during parallel development.

Strategy: one blueprint at a time. Test after each. Never break existing routes.

## Instructions

### Step 1: Understand the current structure

```bash
wc -l ~/atlas_core/kernel.py
grep -c "@app.route" ~/atlas_core/kernel.py

# Count routes per domain group:
grep "@app.route" ~/atlas_core/kernel.py | grep -oP '"/\w+' | cut -d/ -f2 | sort | uniq -c | sort -rn | head -20
```

### Step 2: Start with the smallest independent group — symbols/rings

These 6 routes are FULL and self-contained:
`/symbol/<path>`, `/symbols/stats`, `/glyphs/all`, `/glyphs/<path>`, `/rings`, `/ring/<id>`

Create `npu_engine/routes/symbols_bp.py`:

```python
"""symbols_bp.py — Symbol, glyph, and ring routes."""
from flask import Blueprint, jsonify, request

symbols_bp = Blueprint('symbols', __name__)

@symbols_bp.route("/symbol/<path:symbol>")
def _symbol_lookup(symbol):
    from npu_engine.field.symbol_engine import lookup_symbol
    result = lookup_symbol(symbol)
    return jsonify(result)

# ... move all symbol/ring route functions here
# Copy the function bodies exactly from kernel.py
```

In `kernel.py`, replace the moved functions with:
```python
from npu_engine.routes.symbols_bp import symbols_bp
app.register_blueprint(symbols_bp)
```

Test: `curl localhost:5000/glyphs/all` — must still work.

### Step 3: Move system routes

`/health`, `/system/state`, `/system/audio`, `/system/audio/restore`, `/system/services`, `/snapshot`

Create `npu_engine/routes/system_bp.py`.
Test all 6 routes before moving on.

### Step 4: Move reading/oracle routes (15 routes)

`/card/draw`, `/card/spread`, `/reading`, `/reading/tarot`, etc.

Create `npu_engine/routes/reading_bp.py`.

### Step 5: Move plants/land routes (22 routes)

Create `npu_engine/routes/plants_bp.py`.

### Step 6: Move sound routes (16 routes)

Create `npu_engine/routes/sound_bp.py`.

### Step 7: Move corpus/research routes (8 routes)

Create `npu_engine/routes/corpus_bp.py`.

### Step 8: Move render/geometry routes (14 routes)

Create `npu_engine/routes/render_bp.py`.

### IMPORTANT: One blueprint per commit

After each blueprint:
1. Run full route health check
2. `git add -A && git commit -m "blueprint: extract <domain>_bp"`
3. If anything breaks, `git revert` immediately

Never extract two blueprints in the same commit.

## Route health check script

Write `scripts/route_health.sh`:
```bash
#!/bin/bash
ROUTES="/field /goloka /helix /trajectory /rings /yantra /guild/state \
        /sound/spec /corpus/search?q=nakshatra /layers /dinacharya \
        /glyphs/all /system/state /reading/bandhu /card/deck/atlas"

echo "Route health check:"
for route in $ROUTES; do
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 3 "localhost:5000$route")
  status=$( [ "$code" = "200" ] && echo "✓" || echo "✗ $code" )
  printf "  %-35s %s\n" "$route" "$status"
done
```

Run before and after each blueprint extraction. Output must be identical.

## Success check

After all blueprints extracted:
```bash
wc -l ~/atlas_core/kernel.py
# Should be < 3000 lines (down from 9800)

grep "register_blueprint" ~/atlas_core/kernel.py | wc -l
# Should be >= 6

bash ~/atlas_core/scripts/route_health.sh
# All routes ✓
```

## Output

- Create `npu_engine/routes/` directory
- Create one `*_bp.py` per domain group
- Reduce `kernel.py` significantly
- Write `scripts/route_health.sh`

## Do this blueprint first (lowest risk):

Start with `symbols_bp` — 6 routes, all FULL, no cross-dependencies.
Commit, verify, then continue with `system_bp`.
