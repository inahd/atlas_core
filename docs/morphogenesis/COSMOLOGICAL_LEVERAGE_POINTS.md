# Cosmological Leverage Points

Ranked list of cosmological parameters and how they should drive visuals. **Leverage** = visible change-per-unit-input. High-leverage parameters become primary controls; low-leverage ones become slow-drift defaults or get retired.

## Ranking Methodology

For each parameter:
- **Source** — where the value comes from (Atlas Python, JS state, user gesture)
- **Current path** — the existing code path (file:line where it's consumed)
- **Visual control** — what changing the value should *look like*
- **Compute** — CPU-JS / GPU / NPU / REL
- **Risk** — what happens at extreme values (collapse, glitch, monotony)
- **Priority** — implement (P), surface (S), or retire (R)

## Top 11

### 1. Bhasma stage (`bhasmaStage.stage`)
- **Source**: REL — `morphogenesis.derive_bhasma_stage` (Python) reads tithi pos + paksha
- **Current path**: `passes/bhasmaCalcination.js` (multi-op multipliers) + `atlas/aesthetics.js:BHASMA_TINT` (hue/sat/warmth)
- **Visual control**: 9 stages × distinct material/tonal register. *Working*.
- **Compute**: REL → CPU-JS pass + per-pixel post tint
- **Risk**: marana stage drains life; can collapse into shyama if bhasma gain × sustained too long
- **Priority**: keep. Monitor for over-domination; ensure rebloom guard catches marana collapse.

### 2. Style / palette (user-driven)
- **Source**: user (style cycler / Tab key)
- **Current path**: `atlas/styles.js` + `colormap.js`
- **Visual control**: entire visual register. *Working* — biggest user-facing leverage.
- **Compute**: CPU-JS palette function (per-pixel)
- **Risk**: none
- **Priority**: keep. **S** — surface as the primary control; everything else should adapt to current style.

### 3. Interaction phrase (dosha · guṇa · rhythm)
- **Source**: user gestures → `tools/interactionPhrase.js`
- **Current path**: `tools/phraseRewardDirector.js` → `regionMap.applyTransition`
- **Visual control**: which transition fires + reward multipliers + bonus echoes (sattvic = ×1.40 + 2 echoes; pitta strike = ×1.45; vata erratic = ×0.85). *Working* (v0.15).
- **Compute**: CPU-JS heuristic
- **Risk**: low confidence early in session → falls back to default mapping
- **Priority**: keep. Tune reward curves over time based on user feedback.

### 4. Active embodiment (`embodiment.body_region`)
- **Source**: REL — `derive_embodiment` picks marma + body region from panchanga + intent
- **Current path**: `passes/pulseMarma.js:REGION_POS` (anatomical position) + `passes/helicalShear.js` (twist axis) + `passes/tensegrity.js` (vertical column)
- **Visual control**: where pulse/marma fires on canvas + helix/spine orientation
- **Compute**: REL → CPU-JS local splats
- **Risk**: pulses always at same position can feel mechanical
- **Priority**: keep. Add slight position jitter (golden-angle around the anatomical point) so the pulse feels alive.

### 5. Wave amplitude (Atlas wave field intensity)
- **Source**: REL — `morphogenesis.derive_morphogenesis_elements` reads `field_state.wave`
- **Current path**: **dormant** — value computed in Python but not piped through to event intensityMul
- **Visual control**: should multiply VisualEvent `intensityMul` and SymbolEvent intensity at the moment of creation. High amplitude = dramatic events; low = whisper events.
- **Compute**: REL → JS state
- **Risk**: high amplitude × phrase reward = potential blow-out (mitigate with ACES + tone-map)
- **Priority**: **P1** — wire into `BeginnerController._fireEvent` as `intensityMul *= 0.6 + waveAmplitude * 0.6` (range 0.6–1.2).

### 6. Dominant_k (harmonic subdivision)
- **Source**: Atlas wave field — current dominant prime k (3, 5, 7, 11)
- **Current path**: **not piped** to morphogenesis at all
- **Visual control**: drives shockwave petal count (currently fixed at 5), summon phyllotaxy count (fixed at 8), quasicrystal fold (currently a static parameter)
- **Compute**: REL → JS state
- **Risk**: changing fold mid-session may flicker the qc pattern; throttle to once per breath cycle
- **Priority**: **P2** — pipe `dominant_k` into the morphogenesis bundle and let it set qc.fold + shockwave petal count.

### 7. Tithi position
- **Source**: REL — bundle.bhasma_stage.tithi_pos (1–15)
- **Current path**: `atlas/aesthetics.js:tithiHueShift` → applied per-pixel
- **Visual control**: 0–360° hue rotation. Currently *static* per session unless preset changes.
- **Compute**: REL → CPU-JS post tint
- **Risk**: drift too fast = perceptible color flicker
- **Priority**: **P3** — bind hue shift to *real time* not just panchanga snapshot. Drift +1° per minute over a session for slow visual breath, with the panchanga value as the offset.

### 8. Paksha (waxing / waning)
- **Source**: REL — bundle.bhasma_stage.paksha
- **Current path**: partial — affects bhasma stage selection but not transition selection
- **Visual control**: should bias which transitions are picked. Waxing → bloom-to-eye, body-to-root, membrane-to-cellular. Waning → density-to-void, body-to-root (settling), eye-to-star (release).
- **Compute**: REL → JS choice
- **Risk**: low
- **Priority**: **P4** — `phraseRewardDirector` consults paksha when picking between equally-weighted reward keys.

### 9. Graha (currently active or featured planet)
- **Source**: REL — embodiment.graha (Sun/Moon/Mars/Mercury/Jupiter/Venus/Saturn/Rahu/Ketu)
- **Current path**: **dormant** — appears in HUD only
- **Visual control**: should bias palette family at preset time. Sun → vira, Moon → shanta/karuna, Mars → raudra, Mercury → adbhuta, Jupiter → shringara/cosmic, Venus → shringara, Saturn → ash_field, Rahu/Ketu → shringara/adbhuta inverted.
- **Compute**: REL → JS palette choice
- **Risk**: overrides user style — only apply when no explicit style is set
- **Priority**: **P5** — graha sets default palette family if user hasn't explicitly selected.

### 10. Nitya / yantra (sacred spatial mask)
- **Source**: REL — bundle.sacred.yantraType
- **Current path**: `atlas/yantra.js:buildYantraMask` → `passes/sacred.js`
- **Visual control**: spatial multiplier mask shaping where coherence accumulates. *Working*.
- **Compute**: REL → CPU-JS mask × N
- **Risk**: strong mask + vata phrase = mask wins, sparks lose individuality
- **Priority**: keep. Already working.

### 11. Pranayama (breath cycle)
- **Source**: REL — embodiment.pranayama_that_loads
- **Current path**: `passes/movementPhrase.js:PRANAYAMA_PROFILE` — drives charge/coherence/life modulation cycle
- **Visual control**: smooth/sharp/alternating breath rhythm. *Working*.
- **Compute**: REL → CPU-JS pass
- **Risk**: alternating profile (Nadi Shodhana) does L-R-asymmetric write — visible only at high gain
- **Priority**: keep.

## Surface These (S)

Surface as primary user controls / HUD readouts:

- **Style / palette** — already primary
- **Phrase classification** — already in HUD (v0.15)
- **Bhasma stage** — currently in advanced HUD only; promote to beginner HUD as small status line
- **Tithi position** — show as subtle indicator (not numeric — color glyph)

## Promote (P)

Wire these in priority order:

- **P1**: wave amplitude → event intensity (4-line change in beginner._fireEvent)
- **P2**: dominant_k → shockwave petals + qc fold
- **P3**: tithi-driven slow hue drift over real time
- **P4**: paksha → transition selection bias
- **P5**: graha → default palette family

## Retire (R)

Nothing to retire yet. Some passes are bounded and rarely contribute (helical shear at low asana twist, tensegrity outside specific embodiments) — they self-disable correctly.

## Anti-Patterns Found

- **Two layers driven by bhasma**: `aesthetics.js:BHASMA_TINT` rotates hue/sat/warmth; `passes/bhasmaCalcination.js` applies per-field operators. They can disagree (one moves slowly with tithi, the other can be set discretely). Consolidate or document.
- **Dominant_k is computed but not piped**: classic sign of a leverage point that was on the design board but never connected. P2 fixes.
- **Graha is HUD-only**: similar — meaningful symbolic state with no field hook.

## Constraint

Adding a new wiring (P1–P5) must NOT add a new slider. Each leverage point already has a source value somewhere; the work is connecting source to consumer, not inventing UI.
