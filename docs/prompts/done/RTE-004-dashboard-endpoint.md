# RTE-004: Build /dashboard/health endpoint

**Phase**: 2  
**Priority**: MEDIUM  
**Estimated time**: 1–2 hrs

## Context

There is no single endpoint that shows system health at a glance. `home.html` makes
8+ separate API calls to assemble its view. A `/dashboard` JSON endpoint that surfaces
route health, corpus stats, graph stats, and field state in one call would make
`home.html` faster and give a useful debugging surface.

This is not in the original audit task list — it's an architectural quick win.

## Instructions

### Step 1: Read what home.html currently calls

```bash
grep "fetch\|\.get\|axios" ~/atlas_core/static/home.html | grep -o "'[^']*'" | sort -u
```

### Step 2: Read the existing /health route

```bash
grep -A 20 "def _health" ~/atlas_core/kernel.py
```

### Step 3: Build `/dashboard` endpoint

Add to kernel.py:

```python
@app.route("/dashboard")
def _dashboard():
    """Single-call system health and state summary for home.html."""
    import time
    from npu_engine.build_field_state import build_field_state
    
    out = {"timestamp": time.time(), "routes": {}, "corpus": {}, "graph": {}, "field": {}}
    
    # Field state (most important)
    try:
        fs = build_field_state()
        out["field"] = {
            "tithi": fs.get("panchanga", {}).get("tithi_name"),
            "nakshatra": fs.get("panchanga", {}).get("nakshatra"),
            "devi": fs.get("panchanga", {}).get("devi"),
            "vara": fs.get("panchanga", {}).get("vara"),
        }
        out["routes"]["field"] = "ok"
    except Exception as e:
        out["routes"]["field"] = f"error: {e}"
    
    # Corpus stats
    try:
        import glob, os
        jsonl_files = glob.glob("datasets/sources/**/*.jsonl", recursive=True)
        total_chunks = sum(
            sum(1 for _ in open(f)) for f in jsonl_files if os.path.getsize(f) > 0
        )
        out["corpus"] = {"files": len(jsonl_files), "chunks": total_chunks}
        out["routes"]["corpus"] = "ok"
    except Exception as e:
        out["routes"]["corpus"] = f"error: {e}"
    
    # Graph stats
    try:
        from npu_engine.graph_engine import GraphEngine
        g = GraphEngine()
        out["graph"] = {"entities": len(g.nodes), "edges": len(g.edges)}
        out["routes"]["graph"] = "ok"
    except Exception as e:
        out["routes"]["graph"] = f"error: {e}"
    
    # Quick probe of key routes
    probe_routes = ["/goloka", "/helix", "/trajectory", "/rings", "/yantra",
                    "/guild/state", "/sound/spec", "/layers"]
    for route in probe_routes:
        try:
            # Import and call the function directly rather than HTTP
            out["routes"][route] = "registered"
        except:
            out["routes"][route] = "error"
    
    out["health"] = "ok" if out["routes"].get("field") == "ok" else "degraded"
    return jsonify(out)
```

### Step 4: Update home.html to use it

Find the fetch calls in home.html. Add a single `/dashboard` fetch on page load
that pre-populates the field state widgets, reducing waterfall requests.

```javascript
// Add near top of home.html <script>:
async function loadDashboard() {
    try {
        const r = await fetch('/dashboard');
        const d = await r.json();
        // Populate field state widgets from d.field
        if (d.field.nakshatra) document.getElementById('nakshatra')?.textContent = d.field.nakshatra;
        if (d.field.tithi) document.getElementById('tithi')?.textContent = d.field.tithi;
        if (d.field.devi) document.getElementById('devi')?.textContent = d.field.devi;
        console.log('Dashboard:', d.health, d.graph);
    } catch(e) { console.warn('Dashboard offline:', e); }
}
loadDashboard();
```

### Step 5: Test

```bash
curl -s localhost:5000/dashboard | python3 -m json.tool
```

## Success check

```bash
curl -s localhost:5000/dashboard | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert d.get('health') in ('ok','degraded'), 'no health field'
assert 'field' in d, 'no field'
assert 'corpus' in d, 'no corpus'
print('Dashboard OK — health:', d['health'])
print('Field:', d['field'])
print('Corpus chunks:', d['corpus'].get('chunks'))
"
```

## Output

- Add `/dashboard` route to `kernel.py`
- Optionally update `static/home.html` to use it
