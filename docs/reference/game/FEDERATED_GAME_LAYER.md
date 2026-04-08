# Federated Game Layer (FGL) — Multi-Surface Specification
Status: SPEC (documentation only)

One field. Many nodes. Federation, not centralization.

This document specifies how independent Atlas surfaces (TUI, hexfield, 3D, simulation, narrative, companion) share:
- one canonical field contract
- a minimal shared progression/observation state
- an append-only event model for cross-node synchronization

This document does not introduce new kernel routes. Existing contracts remain canonical:
- `GET /field`
- `GET /coherence?n=N`
- `POST /observe`

## 1. PURPOSE

Atlas is splitting into multiple primary surfaces. Each surface must remain independently executable, but the user experience must feel continuous.

Federation is required because:
- the TUI (Study) and hexfield (Explorer) must share progression and observations without becoming one program
- Brahmanda 3D (Spatial) will be a different renderer with the same field and the same entities
- simulation worlds (Ecology / coherence-spectrum worlds) need to react to the field and unlock content via shared milestones
- narrative/lore systems (Codex, arcs) must advance from shared progression states
- companion interfaces (watch/mobile) must reflect the same exploration/progression state with minimal surface coupling

The goal is shared continuity without a centralized "game server" design that dictates rendering or UX.

## 2. CORE MODEL

### Canonical Field
- The canonical field is the shared contract returned by `GET /field` (see `docs/FIELDSTATE_V1.md`).
- The field is encoded on the toroidal surface using:
  - `theta` (time / manifestation axis)
  - `phi` (witness <-> participant axis)
  - `psi` (engagement mode) is optional and may expand later
- Surfaces may project the field into local representations (hex grid, mandala, 3D) but must not replace or recompute the canonical field.

### Kernel (Local Authority)
- `kernel.py` is the local field authority.
- All surfaces read from `/field` when available.
- `/coherence` is a derived view for discovery and ranking; it does not replace `/field`.
- `/observe` is the canonical cross-surface bridge for deep entity reads.

### Federation Layer
The federated game layer is a node-to-node synchronization contract for:
- shared state: progression, observations, attestation metadata, major milestones
- shared events: append-only log of what happened (observations, discoveries, thresholds)

Federation does not require centralization:
- a "federation" can be a single device with multiple processes
- a "federation" can later span devices
- the contract remains the same; transport changes are an implementation detail

## 3. NODE TYPES

All nodes:
- read from the canonical field when connected
- can run standalone (shadow field) with an explicit badge
- emit events (at minimum: observations and progression updates)
- may persist local-only state without affecting global shared state

### Study Node (TUI)
- Dominant mode: STUDY
- Reads: `/field`, `/coherence`
- Emits: `observe.entity`, `progression.updated` (via observation workflows)
- Persists local: UI state, filters, last selected entity

### Explorer Node (Hexfield)
- Dominant mode: OBSERVE / DISCOVERY (navigation + fog + relations)
- Reads: `/field`, `/coherence`, relations datasets (read-only)
- Emits: `observe.entity`, `relation.discovered`, `progression.updated`
- Persists local: exploration caches, selection state, pathfinding hints

### Spatial Node (3D Brahmanda)
- Dominant mode: OBSERVE
- Reads: `/field`, `/coherence`
- Emits: `observe.entity` (selection), optional `relation.discovered`
- Persists local: camera state, render parameters, local performance caches

### Simulation Node (Coherence Spectrum / Ecology Worlds)
- Dominant mode: PRACTICE (field-reactive worlds) or CREATE (sandbox overrides)
- Reads: `/field`, `/coherence`
- Emits: `coherence.threshold.crossed`, `world.event.triggered`, `progression.updated`
- Persists local: simulation history, procedural world state, seeds

### Narrative Node (Story Arcs / Codex)
- Dominant mode: UNDERSTAND / CREATE (narrative output with explicit attestation)
- Reads: `/field`, shared progression, world thresholds
- Emits: `world.event.triggered` (arc events), `progression.updated` (milestone promotions)
- Persists local: drafts, prompts, narrative state

### Companion Node (Watch/Mobile)
- Dominant mode: PRACTICE (glanceable cues) or OBSERVE (field presence)
- Reads: `/field` (or synced snapshots), shared progression summaries
- Emits: `observe.entity` (quick observe), optional reminders as `world.event.triggered`
- Persists local: last sync timestamp, offline cache

## 4. SHARED OBJECTS

Shared objects are the stable interchange types. Nodes can extend locally but must not break base keys.

### Entity (canonical projection target)
```json
{
  "id": "nakshatra_rohini",
  "theta": 0.7560,
  "phi": 0.7555,
  "s_layer": "S3",
  "element": "earth"
}
```

### Relation (minimal edge)
```json
{
  "source": "nakshatra_rohini",
  "target": "plant_tulsi",
  "type": "associated"
}
```

### Observation (cross-node fact of contact)
```json
{
  "entity_id": "plant_tulsi",
  "timestamp": "2026-03-23T14:22:05Z",
  "node_id": "hexfield@laptop"
}
```

### ProgressState (shared ladder)
Progression is a single ordered ladder across all nodes:
`unknown -> observed -> documented -> attested -> mastered`

Nodes may display it differently, but must not invent a different ladder.

### WorldState (shared coarse simulation gates)
WorldState is intentionally minimal and high-level. It gates unlocks and cross-surface pacing.
```json
{
  "coherence_band": "low|mid|high",
  "active_cycles": ["nakshatra", "tithi", "vara"],
  "thresholds": {
    "unlock_relations": 0.7,
    "unlock_arc": 0.85
  }
}
```

### NodeIdentity
```json
{
  "node_id": "tui@desktop",
  "node_type": "study",
  "version": "coherence-atlas-333"
}
```

## 5. EVENT MODEL

Federation uses a minimal event bus. It is:
- append-only (events are never edited in place)
- timestamped
- idempotent (replays do not double-apply)

### Event Envelope
```json
{
  "event_id": "uuid-or-stable-hash",
  "type": "observe.entity",
  "timestamp": "2026-03-23T14:22:05Z",
  "node": { "node_id": "hexfield@laptop", "node_type": "explorer", "version": "coherence-atlas-333" },
  "idempotency_key": "hexfield@laptop:observe.entity:plant_tulsi:2026-03-23T14:22:05Z",
  "payload": {}
}
```

### Canonical Event Types

`observe.entity`
- Payload: `{ "entity_id": "...", "phi": <optional>, "psi": <optional> }`
- Semantics: a node entered/selected/observed an entity; other nodes may reveal fog or update recents.

`progression.updated`
- Payload: `{ "entity_id": "...", "state": "observed|documented|attested|mastered" }`
- Semantics: shared ladder promotion for the entity.

`field.updated`
- Payload: `{ "field_state_v1": { ... } }` or `{ "field_hash": "..." }`
- Semantics: a node observed a new authoritative field snapshot (often via polling); consumers may refresh.

`relation.discovered`
- Payload: `{ "source": "...", "target": "...", "type": "..." }`
- Semantics: a relation became visible due to progression or evidence; does not redefine canonical datasets.

`coherence.threshold.crossed`
- Payload: `{ "threshold": "unlock_relations|unlock_arc|...", "value": 0.82 }`
- Semantics: global pacing signal for unlocks.

`world.event.triggered`
- Payload: `{ "world_event_id": "...", "tags": ["ecology","arc"] }`
- Semantics: a high-level world event fired (seasonal event, arc beat, simulation milestone).

## 6. PERSISTENCE RULES

Federation separates shared state (global) from node state (local).

### GLOBAL (shared across federation)
- observations: who observed what, and when
- progression state: the shared ladder per entity
- attestation metadata on promotions (what justified a promotion, and by whom)
- major milestones: unlocked arcs, unlocked relation visibility gates, threshold crossings

### LOCAL (node-specific)
- simulation history and procedural state (seeds, RNG streams, step logs)
- local UI state (camera position, filters, last selection)
- temporary caches (projection indices, pathfinding hints, render caches)
- draft content (narrative drafts, editor buffers)

Global shared persistence must be small and durable; local persistence can be large and ephemeral.

## 7. FEDERATION MODES

### CONNECTED
- Node reads the authoritative field from `/field`.
- Node syncs shared state (progression, observations) via the federation event model.
- Node emits events as append-only entries.

### STANDALONE
- Node runs with a shadow field fallback (non-authoritative) and must label it `◌ standalone`.
- Node continues to function (navigation, display, local simulation), but must not claim canonical authority.
- Node may log local events for later rejoin, but must not back-propagate standalone field computations as canonical truth.

### REJOIN
- Node reconciles local event history with shared/global state.
- Prefer higher progression/attestation level; resolve ties deterministically.
- Never silently overwrite: show a badge/state that reconciliation occurred and what changed.

## 8. CONFLICT RULES

Conflicts occur when nodes update the same shared object independently or offline.

Deterministic rules:
- highest progression level wins (`mastered` > `attested` > `documented` > `observed` > `unknown`)
- latest timestamp resolves ties at the same level
- synthesis never overrides primary sources: derived/narrative claims cannot rewrite canonical entity definitions or datasets
- local simulation data never overwrites canonical entity definitions (`Entity` is read-only outside the kernel/datasets)

Idempotency rule:
- if two events share an `idempotency_key`, they are the same event and must be applied once

## 9. INTERFACE CONTRACT

All nodes must:
- resolve BASE via configuration, never hardcode: native nodes use `ATLAS_URL`; browser nodes default to `window.location.origin` but should allow injection/override where possible
- display connection state at all times:
  - `✦ connected` when `/field` is authoritative and reachable
  - `◌ standalone` when running on a shadow field
- never silently degrade: fallback is always visible and labeled as non-authoritative
- keep a dominant mode label visible (OBSERVE / STUDY / PRACTICE / CREATE) per `docs/ARCHITECTURE.md`

## 10. EXAMPLES

### Another node observes an entity -> your fog lifts
1. Spatial node emits `observe.entity` for `nakshatra_rohini`.
2. Shared progression promotes to `observed` via `progression.updated`.
3. Explorer node receives the event, marks the hex cell observed, reveals adjacent fog.

### Simulation threshold crossed -> new entities unlock
1. Simulation node computes a world milestone and emits `coherence.threshold.crossed` with `unlock_relations`.
2. Explorer node and Study node treat relations as visible for entities at `attested` or higher.
3. Relation edges render only where progression state allows.

### Narrative arc unlocks after progression milestone
1. Explorer node promotes a set of entities to `documented`.
2. Narrative node sees a milestone condition and emits `world.event.triggered` for `arc:rohini_gate_open`.
3. Companion node shows a concise prompt keyed to the arc and current field.

### Two users explore different hex regions -> shared map expands
1. Each explorer node runs independently and emits `observe.entity` and `progression.updated`.
2. Shared state merges by conflict rules (highest level, then latest timestamp).
3. Both maps expand as new observed cells become visible through shared progression updates.

## 11. FUTURE EXTENSIONS (non-blocking)

Possible extensions that do not change the core contract:
- multiplayer sync (multiple devices, multiple identities)
- CRDT or replicated append-only event logs (transport-independent)
- offline-first sync with merge/replay
- cross-device identity (node identity + user identity separation)
