# Atlas TODO
*Updated: 2026-03-31 21:02*

## Priority 1 — Audio stability
- [ ] Verify MOTU M2 selected (not HDMI) after restart
- [ ] Note queue drain/refill gap — occasional silence between phrases
- [ ] Tabla volume too quiet (0.35 gain) — try 0.5
- [ ] Test 10-minute continuous playback — report any skips

## Priority 2 — Visual shell
- [ ] /coherence-field returns 500 — core/coherence_engine.py runtime bug
- [ ] Shell.js node click -> igpu orbit animation — verify working
- [ ] Wire brahmanda4 iframe into shell mode switcher
- [ ] Test command layer backtick toggle in browser

## Priority 3 — Vocal engine
- [ ] Wire VocalKernel into om_engines.py
- [ ] Write SC synthdef for /atlas/vocal/phoneme formant synthesis
- [ ] Build NAKSHATRA_MAP in vocal/graph_seed_data.py if missing

## Priority 4 — SC synthdefs
- [ ] atlas_mix.scd: rhythm synthdef (tabla percussion from /atlas/rhythm/bol)
- [ ] atlas_mix.scd: sympathetic synthdef (Karplus-Strong 13-string)
- [ ] atlas_mix.scd: vocal synthdef (formant)

## Priority 5 — State broadcast
- [ ] Engines write /tmp/rhythm_state.json, /tmp/mix_state.json
- [ ] Talachakra reads state files instead of recomputing
- [ ] Shell.js reads mix amps from state files

## Priority 6 — Relational navigation
- [ ] /attend endpoint live after kernel restart
- [ ] Test: click deity node -> music nudges toward element
- [ ] Entity detail panel in shell — relations, not just JSON

## Priority 7 — kernel.service
- [ ] kernel.service crash-loops (stale process at PID works)
- [ ] Restart kernel to pick up /attend, deity_attributes, plant_identity

## Done
- [x] Microkernel: om_audio + om_engines separated
- [x] PhraseEngine: live raga graph traversal, natal-aware
- [x] tanpura_field: relational tuning from raga/nakshatra/tithi
- [x] relational_params: field -> instrument physics
- [x] atlas_mix.scd: SC OSC receiver
- [x] talachakra: audio command center with layer toggles
- [x] shell command layer: backtick, tabbed editor, :observe/:seed/:field
- [x] Audio: pre-rendered buffers, zero allocation in callback
- [x] Purnima raga fallback: maps to raga by hour
- [x] /attend endpoint: node click -> mix nudge (needs kernel restart)
- [x] deity_attributes: 27 nakshatra deities + items + vahanas
- [x] plant_identity: tradition data in portrait panel
- [x] 108 pada topology in NPU graph
- [x] Yantra: 9 triangles, vastu compass
- [x] Bija synth: pure formant, no TTS
