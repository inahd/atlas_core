# HEXD Wiring Audit

Date: 2026-04-07

Scope:
- Requested docs plus Hexd frontend/backend wiring
- Related S-layer routing, object handoff, field loading, graph/content loading, command/dock behavior, and Atlas/home links

Missing requested files:
- `SYSTEM_RESTRUCTURE.md` not present in repo
- `scripts/atlas_api.py` not present in repo

## A. Fully Wired and Healthy

- `/hexd` route serves [`static/hexd.html`](/home/inahd/atlas_330/static/hexd.html) and loads [`static/js/hexd.js`](/home/inahd/atlas_330/static/js/hexd.js) and [`static/css/hexd.css`](/home/inahd/atlas_330/static/css/hexd.css).
- Live Hexd path is the `data-shell="phase1"` branch in [`static/js/hexd.js`](/home/inahd/atlas_330/static/js/hexd.js). It is not dead; it is the active runtime.
- Universal field strip is real: `/field` + `/spine` poll into the top rail and shell state.
- Left shell mode switching for `field`, `text`, `yantra` is wired and updates URL/history.
- Text mode has real backend content: `/corpus/registry`, `/corpus/read`, `/corpus/search`, `/query/entity`, `/codex/entity/<id>`, `/passages`, `/observe`.
- Yantra mode has real backend content: `/yantra/data`.
- App handoff from `apps/lila-streams` into `/hexd?...object_type=...&object_id=...` is real and lands in Hexd startup parsing.
- `/hexd/object` is real for `patch` and `plant_recommendation`, with object-specific payload construction in [`kernel.py`](/home/inahd/atlas_330/kernel.py).
- Canonical handoff routes exist for `/s0`, `/s1`, `/s3`, `/s4`, `/s6`, though they do not all land in Hexd.
- Quick note open/close and command input focus behavior are wired locally.
- Drawer resize persistence is wired via localStorage.

## B. Wired but Drifting from System Law

- Hexd live runtime is shell-mode based (`field` / `text` / `yantra`) while the declared law is S-layer based: left token ingress, main unfolding body, right textual elaboration, bottom continuity. This is partially honored in phase1 layout, but the primary navigation model drifted.
- `phase1` hard-forces left, right, and bottom open in [`static/js/hexd.js`](/home/inahd/atlas_330/static/js/hexd.js), which weakens the intended conditional continuity model.
- The center still mixes field snapshot, layer-specific bodies, invocation content, and selected-object blocks in one stack. That is workable, but it means the main body is overloaded rather than singular.
- Right drawer correctly acts as support in shell mode, but in non-phase1 code it still contains a second quasi-primary editor/study surface.
- S-layer code remains present and fetches real data, but `renderLayout()` returns early for `phase1`, so the canonical S0-S6 layer behavior path is largely bypassed.
- Canonical routing drifts at S2 and S4: `/s2` goes to Talachakra, `/s4` goes to Toroid Yantra, while Hexd still contains local S2/S4 bodies.
- Atlas/home relevance drifts: Hexd has no shared Atlas/home link even though the repo has Atlas/home navigation patterns elsewhere.

## C. Partially Wired

- Right drawer mode buttons (`reading`, `study`, `research`, `editor`) are clickable and update state, but in `phase1` rendering they do not drive distinct render branches. They mainly relabel local state.
- Shell modes `hex`, `toroid`, `map` are visible and clickable, but route to “Phase 2 mode hook” placeholders.
- S0/S1/S2/S3/S4/S5/S6 diagnostic renderers in [`static/js/hexd.js`](/home/inahd/atlas_330/static/js/hexd.js) are partially wired to real endpoints, but unreachable in normal `phase1` runtime except through shared helper calls.
- S5 selected-object flow is partially wired:
  - object payload loading is real
  - resolver summaries are real
  - `claims` arrays currently come back empty from `/hexd/object`
- Invocation context loading is partially wired:
  - entity, source, and passage loading are real
  - passage-source resolution relies on heuristic file guesses and can silently fall back to empty
- S3 timing data is partially wired:
  - `/trajectory`, `/calendar/day`, `/s3/practice`, `/intention/now` are real
  - `/intention/windows` is POST-only in backend, but Hexd calls it as GET, so that branch silently falls back to no windows
- S0 reading context is partially wired:
  - `/goloka` and `/reading/context` are real
  - `reading/context` explicitly drops `field_state`, while Hexd still expects `readingContext.field_state`
- S4 shell data is partially wired:
  - `/vastu`, `/yantra/data`, `/shell/state?layer=S4` are real
  - content is heterogeneous and partly synthesized from aggregators rather than one canonical S4 contract

## D. Placeholder Only

- Top mode pills and S0-S6 layer pills are not present in [`static/hexd.html`](/home/inahd/atlas_330/static/hexd.html), though JS still looks for `#modeBar` and `#layerBar`.
- `centerLayoutCopy` is referenced in JS but absent from HTML.
- Save action is placeholder only: sets `saveStatus` to `placeholder save`.
- Capture action is placeholder only: only updates status/log text.
- S5 action buttons are placeholder only:
  - `Generate Mandala`
  - `Inspect Guild`
  - `Select Candidate`
  - `Send to Research`
- Shell modes `hex`, `toroid`, `map` are placeholder only.
- Unsupported `/hexd/object` types return a placeholder “No object-specific analytical payload is available yet.”
- `claims` output in Hexd object payloads is placeholder-empty.

## E. Broken or Recursion-Risk Areas

- `renderLayout()` exits immediately into `renderUniversalShell()` when `data-shell="phase1"` is set. Result: most S-layer-specific UI code is effectively dead at runtime, even though it still performs fetch logic elsewhere.
- `/intention/windows` route requires `POST`, but Hexd calls `fetchJSON("/intention/windows")` with GET in `loadS3Data()`. This makes S3 window enrichment fail silently.
- `reading/context` removes `field_state`, but S0 render helpers still read `readingContext.field_state`. That path degrades silently.
- `effectiveLayerFocusEntity("S0")` only returns a focus entity when `state.context.entity` exists; otherwise S0 graph loading does not happen, even if S0 reading data exists.
- `loadInvocationContent()` and layer-specific graph/content loaders can duplicate fetches for the same entity (`/observe`, `/codex/entity`, `/codex/paths`, `/passages`) with separate caches.
- `renderCenterField()` always appends generic field snapshot blocks before layer-specific bodies. This risks region drift by mixing ingress/support data into the main body.
- `loadUniversalFieldState()` polls `/field` and `/spine`, while `fetchFieldState()` also exists for non-phase1. Dual paradigms remain in one file.

## F. Duplicated / Dead / Confusing Code Paths

- Two Hexd paradigms coexist in [`static/js/hexd.js`](/home/inahd/atlas_330/static/js/hexd.js):
  - active `phase1` shell-mode runtime
  - older layer-layout runtime behind the early return
- `modes = ["research", "field", "calendar", "journal", "editor"]` does not match live shell modes `["field", "text", "yantra", "hex", "toroid", "map"]`.
- `layerDefaults`, `renderS0Behavior`, `renderS1Behavior`, `renderS2Behavior`, `renderS3Behavior`, `renderS4Behavior`, `renderS5Behavior`, `renderS6Behavior` remain in file, but most are bypassed in live runtime.
- Right drawer `data-right-mode` buttons exist only for non-phase1 semantics; phase1 does not honor them as distinct render surfaces.
- `layer-data` is a broad legacy aggregator still used by S2 helper code, while newer routes exist for sound, trajectory, plant, and corpus data.
- Canonical S-layer routing is split across Hexd and other apps:
  - S0 -> Hexd
  - S1 -> Hexd
  - S2 -> Talachakra
  - S3 -> Kala
  - S4 -> Toroid Yantra
  - S5 is not covered by `/s5` canonical redirect here
  - S6 -> Hexd
- Requested `SYSTEM_RESTRUCTURE.md` and `scripts/atlas_api.py` are absent, which itself is evidence of documentation/path drift.

## G. Highest-Value Next Fixes

1. Fix the real broken call in S3 by changing Hexd’s `/intention/windows` request to POST with an explicit payload.
2. Decide which runtime is canonical for Hexd, then remove or fence off the inactive branch. Right now `phase1` and layer-layout code coexist and obscure actual behavior.
3. Add explicit classifications in code/comments for controls that are intentionally placeholder versus live, especially Save/Capture/S5 action buttons and `hex`/`toroid`/`map`.
4. Normalize S0/S1/S5 graph and invocation loading so one cache owns entity/codex/path/passage fetches and duplicate requests stop.
5. Add a shared Atlas/home handoff link inside Hexd and align canonical S-layer routing policy, especially for S4 handoff to Toroid Yantra and S5 surface ownership.
