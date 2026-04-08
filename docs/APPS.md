# Apps

15 HTML apps in `apps/`. Served via kernel routes, opened as iframe
overlays from the atlas.html S-layer buttons.

## App Inventory

| App | S-Layer | Endpoint | Purpose |
|-----|---------|----------|---------|
| `agriculture/` | S5 | `/apps/agriculture/` | Planting calendar, WHEEL, search, guild mandala |
| `archana/` | S1 | `/apps/archana/` | Deity invocation |
| `bandhu/` | S5 | `/apps/bandhu/` | Companion interface |
| `brahmanda/` | S4 | `/apps/brahmanda/` | Toroidal field viewer |
| `codex/` | S0/S6 | `/apps/codex/` | Relational generation engine |
| `devi_tarot/` | S1 | `/apps/devi_tarot/` | 15 Nitya Devi oracle |
| `ecology/` | S3/S5 | `/apps/ecology/` | Panchanga practice portal |
| `field_graph/` | S1-S6 | `/apps/field_graph/` | Relational canvas |
| `hexfield/` | S3 | `/apps/hexfield/` | 27 nakshatra hex toroid |
| `lila/` | S6 | `/apps/lila/` | Coherence Spectrum game (Phase 1) |
| `research/` | S6 | `/apps/research/` | Deep field research portal |
| `talachakra_studio/` | S2 | `/talachakra/` | Carnatic rhythm engine |
| `vastu/` | S4 | `/apps/vastu/` | 64-pada mandala |
| `wiki/` | S0/S6 | `/apps/wiki/` | Entity knowledge graph browser |
| `yantra/` | S4 | `/apps/yantra/` | Sacred geometry cards |

## Kernel Endpoints Used by Apps

| App | Endpoints |
|-----|-----------|
| agriculture | `/plants/today`, `/plants/search`, `/plants/guild/<id>` |
| hexfield | `/spine`, `/coherence`, `/hexfield-data` |
| wiki | `/docs-list`, `/docs/<file>`, `/codex/entity/<id>`, `/codex/paths/<id>` |
| research | `/spine`, `/render`, `/observe`, `/codex/entity/<id>`, `/query/entity` |
| lila | `/spine` |
| talachakra | `/spine` (sound_state for tala/bpm sync) |

## Talachakra Integration

`tc_module.js` provides the Talachakra engine as `window.TC` namespace
for inline rendering in atlas.html's layer canvas when S2 is active.
7 percussion rings, WebAudio synthesis, drag-to-rotate-phase interaction.
