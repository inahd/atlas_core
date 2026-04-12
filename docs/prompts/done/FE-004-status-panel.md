# FE-004: Surface all working routes in home.html status panel

**Phase**: 3  
**Priority**: MEDIUM  
**Estimated time**: 1–2 hrs  
**Depends on**: RTE-004 (/dashboard endpoint)

## Context

`home.html` is the root dashboard. Currently it shows field state widgets but
gives no visibility into which Atlas subsystems are live. A small status panel
showing the health of each S-layer domain makes it easy to see what's working
and what needs attention.

## Instructions

### Step 1: Read home.html structure

```bash
wc -l ~/atlas_core/static/home.html
grep -n "class=\|id=\|<div\|<section" ~/atlas_core/static/home.html | head -40
```

Understand the current layout — find where to add a status panel.

### Step 2: Design the status panel

Add a collapsible status panel to home.html — small, bottom of page or sidebar.
Shows: kernel health, route group counts, corpus chunks, graph entities.

```html
<details id="atlas-status-panel" style="margin:1rem 0;font-size:12px;opacity:0.7">
  <summary style="cursor:pointer">System status</summary>
  <div id="status-grid" style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:8px">
    <!-- Populated by JS -->
  </div>
</details>
```

### Step 3: Add status fetch

```javascript
async function loadSystemStatus() {
    const d = await atlasGet('/dashboard', null);
    if (!d) return;
    
    const grid = document.getElementById('status-grid');
    if (!grid) return;
    
    const items = [
        { label: 'field', value: d.routes?.field === 'ok' ? '●' : '○' },
        { label: 'corpus', value: d.corpus?.chunks?.toLocaleString() + ' chunks' },
        { label: 'graph', value: d.graph?.entities + ' entities' },
        { label: 'sound', value: d.routes?.sound || '—' },
    ];
    
    grid.innerHTML = items.map(i =>
        `<div><span style="color:var(--gold)">${i.label}</span><br>${i.value}</div>`
    ).join('');
}
loadSystemStatus();
```

### Step 4: Add route health probe to /dashboard

If /dashboard doesn't already probe route health, add quick checks:

```python
# In _dashboard():
# Probe key routes by calling their handlers directly
probe = {}
try:
    from npu_engine.field.goloka_engine import derive_goloka
    derive_goloka(fs)
    probe['goloka'] = 'ok'
except Exception as e:
    probe['goloka'] = 'error'

try:
    from npu_engine.field.trajectory_engine import derive_trajectory
    derive_trajectory(fs)
    probe['trajectory'] = 'ok'
except Exception as e:
    probe['trajectory'] = 'error'

# etc for 5-6 key engines
out['probe'] = probe
```

### Step 5: Test

Open `localhost:5000/home` in browser.
The status panel should appear at the bottom showing live system stats.

## Success check

```bash
# dashboard returns probe data
curl -s localhost:5000/dashboard | python3 -c "
import sys,json
d=json.load(sys.stdin)
print('Dashboard keys:', list(d.keys()))
assert 'health' in d
print('OK — health:', d['health'])
"

# home.html references atlas.js and status panel
grep -c "atlas-status-panel\|loadSystemStatus\|atlasGet" ~/atlas_core/static/home.html
# Should be >= 2
```

## Output

- Update `static/home.html` with status panel
- Update `/dashboard` route to include engine probe results
