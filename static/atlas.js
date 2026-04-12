// atlas.js — shared utilities for all Atlas frontend pages

const ATLAS_API = '';  // same-origin, relative paths
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

// Fetch with offline fallback
async function atlasGet(path, fallback = null) {
    const cacheKey = 'atlas_cache_' + path;
    try {
        const r = await fetch(path, { signal: AbortSignal.timeout(3000) });
        if (!r.ok) throw new Error('HTTP ' + r.status);
        const data = await r.json();
        try { localStorage.setItem(cacheKey, JSON.stringify({ data, ts: Date.now() })); } catch(e) {}
        setOfflineIndicator(false);
        return data;
    } catch(e) {
        // Try cache
        try {
            const cached = JSON.parse(localStorage.getItem(cacheKey) || 'null');
            if (cached && Date.now() - cached.ts < CACHE_TTL * 12) { // 1hr stale ok
                console.warn('Atlas offline — using cached ' + path);
                setOfflineIndicator(true);
                return cached.data;
            }
        } catch(e2) {}
        setOfflineIndicator(true);
        return fallback;
    }
}

// POST variant
async function atlasPost(path, body, fallback = null) {
    try {
        const r = await fetch(path, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
            signal: AbortSignal.timeout(3000)
        });
        if (!r.ok) throw new Error('HTTP ' + r.status);
        const data = await r.json();
        setOfflineIndicator(false);
        return data;
    } catch(e) {
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
    el.textContent = offline ? '\u25CB standalone' : '\u25CF live';
    el.style.color = offline ? '#e0a030' : '#50c878';
}

// Default field state for offline use
const DEFAULT_FIELD = {
    panchanga: { nakshatra: '\u2014', tithi: '\u2014', tithi_name: '\u2014', vara: '\u2014', devi: '\u2014' },
    sound_state: { raga: 'Bhairavi', bpm: 60 },
    field: { s_layer: 0 }
};
