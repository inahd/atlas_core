/**
 * interaction_engine.js — Unified interaction handler for Atlas pages.
 *
 * Provides: modal overlay, click-to-detail on herbs/animals/passages/
 * yantra cells/entities, event delegation pattern.
 *
 * Load after atlas.js on every page:
 *   <script src="/static/interaction_engine.js"></script>
 */

// ── Modal DOM ─────────────────────────────────────────────

const MODAL_HTML = `
<div id="atlas-modal" style="position:fixed;inset:0;z-index:1000;display:none;align-items:flex-end">
  <div id="atlas-modal-backdrop" style="position:absolute;inset:0;background:rgba(0,0,0,0.7)"></div>
  <div id="atlas-modal-panel" style="
    position:relative;width:100%;max-width:640px;margin:0 auto;
    max-height:70vh;overflow-y:auto;background:#0a0f1a;
    border-top:1px solid rgba(200,168,75,0.3);
    padding:2rem;border-radius:12px 12px 0 0;
    font-family:'Space Mono','Courier New',monospace;font-size:11px;
    color:rgba(255,255,255,0.8);line-height:1.7">
    <div id="atlas-modal-close" style="
      position:absolute;top:12px;right:16px;cursor:pointer;
      color:rgba(255,255,255,0.3);font-size:14px" title="Close">&times;</div>
    <div id="atlas-modal-title" style="
      font-family:'Cormorant Garamond',Georgia,serif;
      font-size:1.5rem;color:#c8a84b;margin-bottom:0.75rem"></div>
    <div id="atlas-modal-body"></div>
  </div>
</div>`;

function showModal(title, bodyHTML) {
  const m = document.getElementById('atlas-modal');
  if (!m) return;
  document.getElementById('atlas-modal-title').textContent = title;
  document.getElementById('atlas-modal-body').innerHTML = bodyHTML;
  m.style.display = 'flex';
  requestAnimationFrame(() => {
    m.querySelector('#atlas-modal-panel').style.transform = 'translateY(0)';
  });
}

function hideModal() {
  const m = document.getElementById('atlas-modal');
  if (m) m.style.display = 'none';
}


// ── Formatters ────────────────────────────────────────────

function _esc(s) {
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

function formatCorpusResults(results) {
  if (!results || !results.length) return '<p style="color:rgba(255,255,255,0.4)">No corpus data found.</p>';
  return results.map(r => `
    <div style="margin-bottom:1rem">
      <p style="color:rgba(255,255,255,0.75);font-family:'Cormorant Garamond',serif;
        font-size:13px;font-style:italic;line-height:1.6">
        ${_esc((r.text || r.passage || r.excerpt || '').slice(0, 400))}
      </p>
      <p style="color:rgba(255,255,255,0.3);font-size:9px;margin-top:4px">
        ${_esc(r.source || r.text_id || '')}
      </p>
    </div>
  `).join('');
}

function formatHerbDetail(name, searchData) {
  const results = searchData?.results || searchData?.passages || [];
  return `
    <div style="margin-bottom:1rem">
      <div style="font-size:10px;color:rgba(255,255,255,0.4);margin-bottom:8px">
        Corpus references for <strong style="color:#c8a84b">${_esc(name)}</strong>
      </div>
      ${formatCorpusResults(results)}
    </div>
  `;
}

function formatAnimalMedicine(animal, searchData) {
  const results = searchData?.results || searchData?.passages || [];
  return `
    <div style="margin-bottom:1rem">
      <div style="font-size:10px;color:rgba(255,255,255,0.4);margin-bottom:8px">
        Medicine wisdom for <strong style="color:#c8a84b">${_esc(animal)}</strong>
      </div>
      ${formatCorpusResults(results)}
    </div>
  `;
}

function formatVastuZone(data) {
  if (!data || data.error) return '<p style="color:rgba(255,255,255,0.4)">No zone data available.</p>';
  const fields = [
    ['deity', data.deity], ['element', data.element],
    ['quality', data.quality], ['direction', data.direction],
    ['graha', data.graha], ['color', data.color],
  ];
  let h = '<div style="display:grid;grid-template-columns:80px 1fr;gap:4px 12px">';
  fields.forEach(([k, v]) => {
    if (v) h += `<div style="color:rgba(255,255,255,0.35);font-size:9px;text-align:right">${k}</div>
                 <div style="color:rgba(255,255,255,0.8);font-size:11px">${_esc(String(v))}</div>`;
  });
  h += '</div>';
  if (data.affinity && data.affinity.length) {
    h += `<div style="margin-top:8px;font-size:9px;color:rgba(255,255,255,0.5)">
      affinity: ${data.affinity.map(a => _esc(a)).join(', ')}</div>`;
  }
  return h;
}

function formatEntityDetail(id, searchData) {
  const results = searchData?.results || searchData?.passages || [];
  return `
    <div style="font-size:10px;color:rgba(255,255,255,0.4);margin-bottom:8px">
      ${_esc(id.replace(/_/g, ' '))}
    </div>
    ${formatCorpusResults(results)}
  `;
}


// ── Interaction Registry ──────────────────────────────────

const INTERACTIONS = {

  // Herb pills → corpus search
  '[data-herb]': async (el) => {
    const herb = el.dataset.herb;
    const data = await atlasGet(`/corpus/search?q=${encodeURIComponent(herb)}&limit=2`);
    showModal(herb, formatHerbDetail(herb, data));
  },

  // Animal medicine → corpus search
  '[data-animal]': async (el) => {
    const animal = el.dataset.animal;
    const data = await atlasGet(`/corpus/search?q=${encodeURIComponent(animal + ' medicine animal')}&limit=2`);
    showModal(animal, formatAnimalMedicine(animal, data));
  },

  // Temple streams → new tab
  '[data-stream-url]': (el) => {
    window.open(el.dataset.streamUrl, '_blank', 'noopener');
  },

  // Corpus passages → expand in modal
  '[data-passage]': (el) => {
    const text = el.dataset.passage;
    const source = el.dataset.source || '';
    showModal('Scripture', `
      <blockquote style="font-family:'Cormorant Garamond',serif;font-style:italic;
        font-size:14px;color:rgba(255,255,255,0.85);border-left:2px solid #c8a84b;
        padding-left:1rem;margin:0;line-height:1.7">
        ${_esc(text)}
      </blockquote>
      ${source ? `<p style="color:rgba(255,255,255,0.35);font-size:9px;margin-top:1rem">— ${_esc(source)}</p>` : ''}
    `);
  },

  // Yantra cells → vastu zone detail
  '[data-vastu-zone]': async (el) => {
    const zone = el.dataset.vastuZone;
    const dir = el.dataset.vastuDir || zone;
    const data = await atlasGet(`/ui/mandala/${encodeURIComponent(zone)}`);
    showModal(dir + ' zone', formatVastuZone(data));
  },

  // Entity detail
  '[data-entity-id]': async (el) => {
    const id = el.dataset.entityId;
    const label = el.dataset.label || id.replace(/_/g, ' ');
    const data = await atlasGet(`/corpus/search?q=${encodeURIComponent(label)}&limit=2`);
    showModal(label, formatEntityDetail(id, data));
  },

  // Raga phrases → play via OSC
  '[data-raga-phrase]': async (el) => {
    const phrase = el.dataset.ragaPhrase;
    try {
      await fetch('/raga/phrase', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phrase })
      });
    } catch (e) { /* silent */ }
    el.style.color = '#c8a84b';
    setTimeout(() => el.style.color = '', 2000);
  },
};


// ── Init ──────────────────────────────────────────────────

function initInteractions() {
  // Inject modal DOM
  document.body.insertAdjacentHTML('beforeend', MODAL_HTML);

  // Backdrop + close button
  document.getElementById('atlas-modal-backdrop').addEventListener('click', hideModal);
  document.getElementById('atlas-modal-close').addEventListener('click', hideModal);

  // ESC key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') hideModal();
  });

  // Single delegated click handler
  document.body.addEventListener('click', async (e) => {
    for (const [selector, handler] of Object.entries(INTERACTIONS)) {
      const target = e.target.closest(selector);
      if (target) {
        // Don't intercept regular links without data attributes
        if (target.tagName === 'A' && !target.dataset.herb && !target.dataset.animal
            && !target.dataset.passage && !target.dataset.vastuZone
            && !target.dataset.entityId && !target.dataset.streamUrl
            && !target.dataset.ragaPhrase) continue;
        e.preventDefault();
        e.stopPropagation();
        try { await handler(target); } catch (err) { console.warn('Interaction error:', err); }
        return;
      }
    }
  });

  // Add pointer cursor to interactive elements
  const style = document.createElement('style');
  style.textContent = `
    [data-herb],[data-animal],[data-passage],[data-vastu-zone],
    [data-entity-id],[data-stream-url],[data-raga-phrase]{cursor:pointer}
    [data-herb]:hover,[data-animal]:hover,[data-entity-id]:hover{
      text-decoration:underline;text-underline-offset:2px}
  `;
  document.head.appendChild(style);
}

// Auto-init
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initInteractions);
} else {
  initInteractions();
}
