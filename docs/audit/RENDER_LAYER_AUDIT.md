# Atlas HTML Render Layer — Audit

April 21, 2026

---

## Inventory

### atlas_core/static/ — 16 HTML files + 9 widgets

All served via kernel.py send_from_directory routes.

| File | Size | Date | Type | Route | Status |
|------|------|------|------|-------|--------|
| index.html | 25K | Apr 12 | Portal | `GET /` | Active |
| home.html | 58K | Apr 10 | Portal | `GET /home` | Active |
| dashboard.html | 3.6K | Apr 10 | Admin | `GET /dashboard` | Active |
| s0.html | 7.6K | Apr 12 | S-layer | `GET /s0` | Active |
| s1.html | 13K | Apr 12 | S-layer | `GET /s1` | Active |
| s2.html | 14K | Apr 12 | S-layer | `GET /s2` | Active |
| s3.html | 12K | Apr 12 | S-layer | `GET /s3` | Active |
| s4.html | 10K | Apr 12 | S-layer | `GET /s4` | Active |
| s4-bloom.html | 54K | Apr 11 | S-layer variant | Not routed | Orphan |
| s5.html | 14K | Apr 12 | S-layer | `GET /s5` | Active |
| s6.html | 10K | Apr 12 | S-layer | `GET /s6` | Active |
| oracle.html | 60K | Apr 16 | Domain app | `GET /oracle` | Active |
| shalaka.html | 14K | Apr 13 | Domain app | `GET /shalaka` | Active |
| jyotish_chart.html | 28K | Apr 16 | Domain app | `GET /jyotish/chart` | Active |
| glyphs.html | 5.8K | Apr 10 | Reference | `GET /glyphs` | Active |
| hexd-portal.html | 7.9K | Apr 10 | Workspace | `GET /hexd-portal` | Active |

**Widgets (static/widgets/):** 9 small HTML fragments (2-5K each), served via
`GET /widgets/<name>`. These are field, coherence, dasha, goloka, guild, natal,
sound, system, transits — embeddable dashboard components.

**Catch-all routes:** `GET /static/<name>` serves any file in static/.
`GET /apps/<path>` serves from apps/ directory (which doesn't exist in
atlas_core, so this routes to atlas_330 when the repos share a working
directory).

### atlas_330/apps/ — 23 HTML files across 11 domains

These are the presentation-layer apps. They call atlas_core JSON routes
for data. They don't exist in atlas_core.

| Domain | Files | Total size | Notes |
|--------|-------|-----------|-------|
| devi (archana, mala, tarot, yantra) | 4 | 257K | Tarot is 111K alone — largest app |
| bhumi (agriculture, ecology, guild, streams, vastu) | 5 | 171K | Land/permaculture tools |
| lila (hexed city/research/shrine, lila, lila-streams) | 5 | 168K | Game/hexfield |
| kala (calendar, wheel) | 2 | 76K | Calendar + circular view |
| bandhu (chat, bandhu figure) | 2 | 58K | Composition/figure |
| leela-maps | 2 | 41K | Sacred geography |
| study | 1 | 26K | Study tool |
| toroid_yantra | 2 | 43K | Toroid visualization |
| vidya (wiki) | 1 | 19K | Wiki browser |
| vishvakarma | 1 | 16K | GIS vastu design |

### atlas_330/static/ — 8 HTML files

| File | Size | Notes |
|------|------|-------|
| shell.html | 77K | 3x3 vastu mandala grid — the main instrument |
| shell-cosmos.html | 34K | Two-sphere cosmology view |
| atlas.html | 25K | Atlas core status/overview |
| live.html | 20K | Live toroid + field |
| index.html | 19K | Landing page |
| home.html | 18K | Home page (different from atlas_core home.html) |
| hexd.html | 15K | Hex field game |
| portal.html | 2K | Simple redirect portal |

### Research artifact — 1 HTML

`research/artifacts/2026-04-04-foot-cosmology.html` (17K) — standalone
research visualization. Copy exists in both repos.

---

## What's Live

Currently served by the running kernel (atlas_core):

**Portals:** index.html (at `/`), home.html (at `/home`)
**S-layers:** s0-s6 (7 pages, at `/s0` through `/s6`)
**Domain apps:** oracle.html, shalaka.html, jyotish_chart.html
**Tools:** glyphs.html, hexd-portal.html, dashboard.html
**Widgets:** 9 fragments at `/widgets/*`

Additionally, the kala app in atlas_330 is live (updated Apr 16 to call
`/jyotish/calendar`) and the atlas_330 shell/cosmos apps call the kernel's
JSON routes.

---

## What's Redundant

### Portal / Landing — 4 versions

| File | Repo | Size | Approach |
|------|------|------|----------|
| atlas_core/static/index.html | core | 25K | Dashboard-like grid with status per route |
| atlas_core/static/home.html | core | 58K | Field-aware landing with app cards by domain |
| atlas_330/static/index.html | 330 | 19K | Landing page |
| atlas_330/static/home.html | 330 | 18K | Home page |

**Assessment:** atlas_core/home.html (58K) is the most developed — it's a
full field-aware portal with domain cards. atlas_core/index.html is a route
status dashboard. The atlas_330 versions are older.
**Recommendation:** Keep atlas_core/home.html as canonical portal.
atlas_core/index.html serves a different purpose (admin status) and should
be renamed dashboard.html or merged into the existing dashboard.

### Hexfield — 3 versions

| File | Repo | Size |
|------|------|------|
| atlas_core/static/hexd-portal.html | core | 8K |
| atlas_330/static/hexd.html | 330 | 15K |
| atlas_330/hexfield/index.html | 330 | 31K |

**Assessment:** atlas_330/hexfield/index.html (31K) is the most complete.
atlas_core/hexd-portal.html is a lightweight preview.

### S4 Yantra — 3 versions

| File | Repo | Size | Notes |
|------|------|------|-------|
| atlas_core/static/s4.html | core | 10K | Current S4 layer page |
| atlas_core/static/s4-bloom.html | core | 54K | Elaborate Chladni variant, NOT routed |
| atlas_330/apps/toroid_yantra/*.html | 330 | 43K | Toroid yantra visualization |

**Assessment:** s4-bloom.html (54K) is the most ambitious — it appears to be
the "Chladni nodal interference + tithi slider" from commit `b4cf116`. It's
unrouted. s4.html (10K) is the self-assembled version from layer_composer.

### Calendar — 1 canonical + 1 alternate view

| File | Repo | Size |
|------|------|------|
| atlas_330/apps/kala/index.html | 330 | 47K |
| atlas_330/apps/kala/wheel.html | 330 | 29K |

Both are in atlas_330 and both are live. index.html is the grid calendar,
wheel.html is the circular view. No atlas_core equivalent.

---

## What's Archived (atlas_330 Only)

These exist only in atlas_330 and have no atlas_core equivalent:

| App | Size | Domain | Significance |
|-----|------|--------|-------------|
| devi/tarot | 111K | S1/Devi | Largest single app — full tarot draw/spread |
| devi/mala | 78K | S1/Devi | 108-bead mala with mantra |
| devi/archana | 54K | S1/Devi | Archana ritual interface |
| bhumi/ecology | 56K | S5/Nature | Ecological browser |
| bhumi/streams | 57K | S5/Nature | Land design tool (Leaflet maps) |
| bhumi/agriculture | 43K | S5/Nature | Agricultural calendar |
| lila-streams | 84K | S6/Lila | Land design tool v2 |
| shell.html | 77K | Portal | 3x3 vastu mandala — the original instrument |
| shell-cosmos.html | 34K | Portal | Two-sphere (material + eternal) |
| bandhu/bandhu.html | 39K | S6/Body | SVG figure with layers |
| leela-maps/main.html | 34K | S4/Geography | Sacred geography (Leaflet) |

The shell.html (77K) in atlas_330 is architecturally significant — it's the
original mandala instrument that the whole system was designed around.

---

## What's Orphaned

### HTML files not served by any route

| File | Repo | Notes |
|------|------|-------|
| s4-bloom.html | core | 54K, unrouted. The Chladni variant S4 page. |
| research/artifacts/2026-04-04-foot-cosmology.html | core | Research artifact, not served |
| atlas_330/static/portal.html | 330 | 2K redirect, superseded |

### atlas_330 apps with no atlas_core JSON route backing

Most atlas_330 apps call routes that DO exist in the kernel. But:
- `apps/vishvakarma/` — calls `/land/layout` (exists) but also needs GIS
  tile serving which isn't in kernel.
- `apps/study/` — unclear what JSON routes it calls.

---

## Design Patterns Observed

### Pattern: inline CSS/JS single-file pages
All atlas_core pages follow this pattern: `<style>` block with CSS vars
(--bg, --gold, --teal, --dim, --serif, --mono, --cinzel), `<script>` block
with `atlasGet()` for data fetching. No build tools, no framework.

### Pattern: dark + gold + teal palette
Consistent across: oracle.html, jyotish_chart.html, shalaka.html, all S-layer
pages, home.html. The CSS vars are defined in atlas-theme.css and repeated
inline in each page.

### Pattern: field strip header
Most pages have a `#topbar` with brand name left, field state strip center
(hora + nakshatra + tithi), live dot right.

### Pattern: layer-body content blocks
Reading/detail panels use `.layer-hdr` (mono, 9px, gold, uppercase) +
`.layer-body` with `.lbl` / `.val` / `.val-gold` / `.val-dim` hierarchy.
Oracle.html and jyotish_chart.html both use this pattern extensively.

### Pattern: SVG center + side panel
jyotish_chart.html uses this: SVG mandala in center (~70%), detail panel
on right (30%). oracle.html uses a different split but similar principle
(Three.js left, reading right).

### Pages matching established patterns well
- **oracle.html** (60K) — most mature. Two-panel, Three.js cube, 4 reading
  layers, field strip, atlasGet() for all data. Pasaka + hexagram as peer
  instruments.
- **jyotish_chart.html** (28K) — clean SVG mandala, click interactions,
  wave field overlay, engine_name matching.
- **shalaka.html** (14K) — simple grid interaction, clean.
- **S-layer pages** (s0-s6) — self-assembled from layer_composer, consistent
  structure.

### Pages diverging from patterns
- **home.html** (58K) — complex layout with many embedded components,
  more portal than instrument.
- **s4-bloom.html** (54K) — ambitious Chladni visualization, elaborate but
  unrouted and possibly abandoned.
- **hexd-portal.html** (8K) — lightweight, more of a placeholder.

---

## Consolidation Recommendation

### Portals
- **Keep:** atlas_core/home.html as the canonical portal
- **Rename:** atlas_core/index.html → admin.html or merge into dashboard.html
  (it's a route status page, not a user-facing portal)
- **Archive but study:** atlas_330/shell.html — the original instrument concept.
  Its 3x3 vastu mandala with zone collapse/expand is architecturally important
  even if the page isn't migrated.
- **Decision needed:** atlas_330/shell-cosmos.html — the two-sphere view is
  unique and may want preservation as a standalone surface.

### S-Layer Pages
- **Keep:** s0-s6 as-is. They self-assemble from layer_composer and are
  consistent.
- **Archive:** s4-bloom.html — either route it as `/s4/bloom` or remove it.
  54K of unrouted code is technical debt.
- **Decision needed:** Should s4-bloom's Chladni slider concept be integrated
  into the standard s4.html?

### Domain Apps
- **Keep in atlas_core:** oracle.html, shalaka.html, jyotish_chart.html.
  These are instruments, not presentation layers. They compute and interact
  with the field. The "JSON-only" boundary doesn't apply to instruments
  that are integral to the field computation UI.
- **Keep in atlas_330:** All apps/ (kala, devi, bhumi, lila, vidya, bandhu,
  leela-maps, vishvakarma). These are presentation surfaces.
- **Decision needed:** Should the boundary rule be restated as "atlas_core
  serves instruments; atlas_330 serves apps"?

### Widgets
- **Keep:** The 9 widget fragments are useful embeddable components.
- **Consider:** Making them reusable in atlas_330 apps too (they're
  currently only used by dashboard.html).

### Missing Surfaces
- No Devi cycle visualization (S1 shows current Devi but not the 15-Devi
  cycle or yantra navigation)
- No wiki browser in atlas_core (atlas_330/apps/vidya/wiki exists)
- No journal UI (backend routes exist)
- No dedicated wave field visualization page (wave data shows in mandala
  overlay but deserves its own surface)

---

## Open Questions for Inahd

1. **Boundary rule update.** The stated rule is "Core = JSON. Period."
   The practice is "Core = JSON + instruments." Should CORE_SCOPE.md be
   updated to: "Core = JSON API + field instruments. Presentation apps
   live in atlas_330."?

2. **index.html identity.** atlas_core/index.html at `/` is a route status
   dashboard, not a user-facing portal. home.html at `/home` is the actual
   portal. Should `/` redirect to `/home`, or should index.html be the admin
   surface it currently is?

3. **s4-bloom.html fate.** 54K unrouted file. Route it, merge its Chladni
   content into s4.html, or remove it?

4. **Shell preservation.** atlas_330/shell.html (77K) is the original 3x3
   vastu mandala instrument. Should it be ported to atlas_core as a live
   surface, archived as reference, or superseded by the S-layer pages?

5. **Wiki in core.** The wiki browser exists in atlas_330 (19K). The wiki
   content (219 .md files) is in atlas_330/wiki/. Should the wiki move to
   atlas_core (it's a knowledge surface, arguably core), or stay in 330
   (it's presentation)?

6. **Kala cross-repo dependency.** atlas_330/apps/kala/ now calls
   atlas_core's /jyotish/calendar. This works but means atlas_330 apps
   depend on atlas_core jyotish features. Is this the right pattern going
   forward, or should kala move into atlas_core?

---

*This document is inventory and recommendation only. No files were moved,
deleted, or modified.*
