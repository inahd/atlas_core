# FE-002: Add offline error handling to frontend pages

**Phase**: 3  
**Priority**: MEDIUM  
**Estimated time**: 2–3 hrs

## Context

All 20 frontend HTML files make fetch() calls to localhost:5000. When the kernel
is not running (van parked, boot not complete, etc.) the pages show blank panels
or JS errors. They should degrade gracefully with a clear "standalone mode" indicator
and cached/default values.

## Instructions

### Step 1: Audit current error handling

```bash
grep -c "catch\|onerror\|offline" ~/atlas_core/static/*.html
grep -c "catch\|onerror\|offline" ~/atlas_core/static/widgets/*.html
```

Find which pages have no error handling at all.

### Step 2: Build a shared offline utility

Add to a new file `static/atlas.js`:

```javascript
// atlas.js — shared utilities for all Atlas frontend pages

const ATLAS_API = 'http://localhost:5000';
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

// Fetch with offline fallback
async function atlasGet(path, fallback = null) {
    const cacheKey = `atlas_cache_${path}`;
    try {
        const r = await fetch(`${ATLAS_API}${path}`, { signal: AbortSignal.timeout(3000) });
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        const data = await r.json();
        // Cache successful response
        try { localStorage.setItem(cacheKey, JSON.stringify({data, ts: Date.now()})); } catch(e) {}
        return data;
    } catch(e) {
        // Try cache
        try {
            const cached = JSON.parse(localStorage.getItem(cacheKey) || 'null');
            if (cached && Date.now() - cached.ts < CACHE_TTL * 12) { // 1hr stale ok
                console.warn(`Atlas offline — using cached ${path}`);
                setOfflineIndicator(true);
                return cached.data;
            }
        } catch(e2) {}
        setOfflineIndicator(true);
        return fallback;
    }
}

function setOfflineIndicator(offline) {
    let el = document.getElementById('atlas-status');
    if (!el) {
        el = document.createElement('div');
        el.id = 'atlas-status';
        el.style.cssText = 'position:fixed;bottom:8px;right:8px;font-size:11px;' +
            'padding:3px 8px;border-radius:4px;z-index:9999;font-family:monospace;';
        document.body.appendChild(el);
    }
    el.textContent = offline ? '○ standalone' : '● live';
    el.style.color = offline ? '#e0a030' : '#50c878';
}

// Default field state for offline use
const DEFAULT_FIELD = {
    panchanga: { nakshatra: '—', tithi_name: '—', vara: '—', devi: '—' },
    sound_state: { raga: 'Bhairavi', bpm: 60 }
};
```

### Step 3: Update home.html to use atlas.js

```bash
head -20 ~/atlas_core/static/home.html
```

Add `<script src="/static/atlas.js"></script>` in head.
Replace direct `fetch('localhost:5000/field')` calls with `atlasGet('/field', DEFAULT_FIELD)`.

### Step 4: Update all widget pages

Each widget page in `static/widgets/` makes 1–2 fetch calls.
Replace each bare `fetch()` with `atlasGet()` pattern.

For each file in `static/widgets/`:
1. Find the fetch call(s)
2. Wrap with try/catch using `atlasGet()`
3. Show sensible default/placeholder values when offline

### Step 5: Test offline behavior

```bash
# Stop the kernel
# Open a page in browser
# Should show "○ standalone" indicator in bottom right
# Should show cached or default values, not blank/error
```

## Success check

```bash
# Verify atlas.js exists and has key functions
grep -c "atlasGet\|setOfflineIndicator\|DEFAULT_FIELD" ~/atlas_core/static/atlas.js
# Should be >= 3

# Verify home.html references it
grep "atlas.js" ~/atlas_core/static/home.html
# Should match

# Verify widgets use atlasGet
grep -l "atlasGet" ~/atlas_core/static/widgets/*.html | wc -l
# Should be >= 5
```

## Output

- Create `static/atlas.js`
- Update `static/home.html`
- Update `static/widgets/*.html`
