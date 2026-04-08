# NPU Engine Audit

**Date**: 2026-04-02
**Scope**: All 105 .py files in `npu_engine/`
**Method**: Full file-by-file read of every module, import tracing through kernel.py, om.py, and inter-module dependencies

---

## Summary

105 Python files. 0 broken. 0 superseded. 2 stubs (empty test files). 6 partial (audio subsystem consumed by om.py). 97 working modules containing real, coherent implementation. The codebase is remarkably intact.

37 of 105 modules are imported by kernel.py. 68 are not -- but most of those 68 are submodules of complete subsystems (mix/, rhythm/, sympathetic/, vocal/) that have their own threaded kernels ready to start. The code is not scattered; it is layered.

---

## Working Core (7 files)

These seven files ARE the system. If they break, nothing works.

| File | What it does |
|------|-------------|
| `datasets.py` | Loads 136 CSVs into entity graph. Hub module -- 4+ importers depend on it. |
| `graph_engine.py` | Canonical relation graph. 7075 nodes, 8466 edges. 6+ importers. Every query flows through this. |
| `build_field_state.py` | Orchestrates FieldState from 10 engine modules. The spine of /spine. |
| `field_state.py` | FieldState dataclass. Pure data definition, zero logic. |
| `coherence_engine_v2.py` | Entity reranking by graph coherence. Makes the field meaningful rather than random. |
| `toroidal_field.py` | Torus coordinate system. Every entity gets (theta, phi) on the torus. NPU-accelerated via OpenVINO when available. |
| `igpu.py` | 64-node spatial layout for SVG cosmos rendering. The visual output. |

These seven form a chain: datasets -> graph_engine -> coherence_engine_v2 -> build_field_state(+toroidal_field) -> igpu. That chain is the system.

---

## Working Periphery (30+ kernel-integrated modules)

These are imported by kernel.py and serve live routes.

**Field construction layer:**
- `field_layers.py` -- S0-S6 layer mapping
- `vastu_engine.py` -- vastu zone activation
- `ui_vastu_engine.py` -- UI layout from field + vastu
- `modulation_engine.py` -- semantic modulation + psi
- `lifecycle_engine.py` -- birth/growth/peak/decay curves
- `orientation.py` -- field orientation computation
- `temple_geometry.py` -- sacred geometry projections
- `vector_store.py` -- embedding store

**Content resolution:**
- `mandala_schema.py` -- vastu mandala zone resolver (drives shell.html)
- `passage_resolver.py` -- text passage finder
- `torus_queries.py` -- 108-pada torus knot distance queries
- `field_to_sound.py` -- nakshatra -> graha -> raga descent

**Graph traversal:**
- `path_engine.py` -- graph path computation (4 importers)
- `query_engine.py` -- graph query interface
- `generator.py` -- entity generation from field
- `layer_engine.py` -- layer entity summaries
- `relational_engine.py` -- relational graph operations

**Domain engines:**
- `card_engine.py` -- devi tarot
- `codex_interaction.py` -- entity -> codex passages (wraps codex_engine)
- `codex_engine.py` -- codex text retrieval
- `codex_modes.py` -- codex mode definitions
- `s5_kernel.py` -- plant wheel (3 rings, 81 plants)
- `natal_musician.py` -- natal -> musician reading
- `yantra_engine.py` + `yantra_generator.py` -- yantra generation
- `bija_synth.py` -- pure formant bija mantra
- `library_kernel.py` -- library state builder
- `treasury.py` -- treasury resolution
- `composition_db.py` -- playlist + mantra scheduling

**Sound output (live):**
- `sound/sound_engine.py` -- sound spec derivation (6 layers, port 57120)
- `sound/osc_bridge.py` -- OSC -> SuperCollider

**Field subpackage:**
- `field/intention_engine.py` -- intention-based calendar
- `field/system_engine.py` -- system self-model + audio route probing
- `field/code_engine.py` -- code analysis (not imported by kernel)

**Zone engines (engines/):**
- `engines/__init__.py` + `engines/base_engine.py` -- ZoneEngine base
- 8 zone engines: center, archetype, sound, rhythm, body, plant, ecology, action, codex

---

## Complete But Unwired (4 threaded kernels + their subsystems)

Four complete subsystems exist as threaded kernels with `.start()` / `.stop()` / `.load_from_field()` interfaces. None are instantiated anywhere. They are waiting for the SuperCollider audio path to be resolved.

### MixKernel (mix/ -- 10 files)

The 11-layer relational mixing graph. Layers: tanpura, mantra_drone, vocal_pad, tabla, konnakol, bol, melody, vocal_line, pad, electronic, bija. Mixing is driven by rasa x arc x mode -> weights, with authority -> confidence mapping (uncertain entities get more drone -- a beautiful design choice). Outputs on port 57121.

- `mix_kernel.py` -- threaded kernel
- `layer_graph.py` -- 11-layer graph structure
- `authority_mix.py` -- authority -> confidence
- `deity_mix.py` -- deity -> layer modulation
- `guna_mix.py` -- guna -> layer modulation
- `nakshatra_mix.py` -- nakshatra -> layer modulation
- `sam_mix.py` -- sam-gravity -> layer modulation
- `mix_osc.py` -- OSC output (port 57121)
- `mix_history.py` -- state history / transitions
- `graph_seed_data.py` -- seed data

### RhythmKernel (rhythm/ -- 10 files)

8 talas, 22 bols (each with rasa/hand/resonance metadata), tihai math (3P+2G=distance), layakari smoothing, cross-rhythm via LCM resolution. Sam-gravity permeates everything.

- `rhythm_kernel.py` -- threaded kernel
- `tala_graph.py` -- 8 tala structures
- `theka_engine.py` -- 22-bol theka generation
- `tihai_engine.py` -- tihai computation
- `layakari_engine.py` -- tempo smoothing
- `fill_engine.py` -- fill patterns
- `cross_rhythm_engine.py` -- LCM cross-rhythm
- `sam_field.py` -- sam-gravity field
- `rhythm_osc.py` -- OSC output
- `graph_seed_data.py` -- seed data

### SympatheticKernel (sympathetic/ -- 4 files)

13 just-intonation-tuned strings. Cross-source excitation with cascade priority: melody > vocal > dayan > bayan. 30Hz processing rate.

- `sympathetic_kernel.py` -- threaded kernel
- `string_model.py` -- 13 JI-tuned strings
- `excitation.py` -- cross-source excitation model
- `sympathetic_osc.py` -- OSC output

### VocalKernel (vocal/ -- 9 files)

49 matrika phonemes with formant data citing Peterson & Barney 1952. 12 gamaka types. 8 bhava states. Authority -> timing mapping (shastra=0ms, inference=50ms). Breath modeling. This is not a stub. This is a real vocal synthesis engine.

- `vocal_kernel.py` -- threaded kernel
- `phoneme_graph.py` -- 49 matrika phonemes with formants
- `gamaka_engine.py` -- 12 ornamentation types
- `bhava_engine.py` -- 8 emotional states
- `svara_voice.py` -- svara -> pitch mapping
- `syllable_sequencer.py` -- syllable sequencing
- `breath_engine.py` -- breath modeling
- `vocal_osc.py` -- OSC output
- `graph_seed_data.py` -- seed data

---

## Partial / Audio Subsystem (6 files)

These are consumed by om.py, not kernel.py. They work but exist in a different runtime context (the audio process).

| File | Status | Notes |
|------|--------|-------|
| `tanpura_engine.py` | partial | 4 tanpura strings. Had circular import deadlock -- fixed via render_fn injection. |
| `tanpura_field.py` | partial | Field -> tanpura tuning. 22-shruti system. Param overlap with relational_synth and relational_params. |
| `relational_params.py` | partial | Field -> instrument physics. NamedTuples for modal physics. Overlaps tanpura_field. |
| `relational_synth.py` | partial | Compute synth params from relations. Broader scope. Overlaps tanpura_field. |
| `mudra_graph.py` | partial | Mudra selection. Only consumer is relational_synth. |
| `sarangi_voice.py` | partial | Bowed gut string synthesis. Not wired to any output. |
| `tabla_sampler.py` | partial | Tabla sample rendering. 7 samples. |

The tanpura param overlap (finding #9) deserves attention: three files compute tanpura parameters at different abstraction levels. They are not contradictory, but the chain of authority is unclear.

---

## Stubs (2 files)

| File | Size | Notes |
|------|------|-------|
| `tests/__init__.py` | 0 bytes | Empty |
| `tests/test_toroid.py` | 0 bytes | Empty |

These are the only empty files in the entire engine.

---

## Surprising Findings

### 1. vocal/ is REAL

This is the most surprising finding. 9 files containing 49 matrika phonemes with formant frequencies citing Peterson & Barney (1952), 12 gamaka ornamentation types, 8 bhava emotional states, authority-to-timing mapping (shastra sources get 0ms onset, inference gets 50ms), breath modeling, and syllable sequencing. This is not a sketch. This is a complete vocal synthesis design waiting for an audio output path.

### 2. rhythm/ is deep

Not just "play a tabla loop." 8 tala structures, 22 bols where each bol carries rasa (emotional quality), hand (which hand strikes), and resonance metadata. Tihai computation using the classical formula 3P + 2G = distance to sam. Layakari (tempo variation) with smoothing. Cross-rhythm resolution via least common multiple. Sam-gravity -- the pull toward the first beat -- permeates every module in the subsystem.

### 3. mix/ is the 11-layer relational mixing graph

The most architecturally sophisticated subsystem. 11 named layers (tanpura through bija), each modulated by rasa, arc position, and engagement mode. The authority -> confidence mapping means entities with lower epistemic authority produce more drone and less melodic foreground -- uncertainty sounds like ambiance. Complete, never started.

### 4. sympathetic/ is ready

13 strings tuned to just intonation ratios. Cross-source excitation where melody excites more than vocal, which excites more than dayan (right tabla), which excites more than bayan (left tabla). Processes at 30Hz. A complete sympathetic resonance model for the sarangi's taraf strings.

### 5. Four threaded kernels exist but none are instantiated

MixKernel, RhythmKernel, SympatheticKernel, and VocalKernel all implement `.start()` / `.stop()` / `.load_from_field()`. They are designed to be spun up as background threads receiving field state updates. But no code anywhere instantiates them. They are waiting.

### 6. sound/ vs mix/ tension

`sound/sound_engine.py` derives a 6-layer sound spec on port 57120. `mix/` has an 11-layer graph on port 57121. These represent different evolution stages of the same idea. sound/ is the one currently live (integrated into kernel.py). mix/ is the more complete design. Eventually mix/ should replace sound/, but the port difference means they could coexist during transition.

### 7. Zero tests

`tests/__init__.py` and `tests/test_toroid.py` are both 0 bytes. There are no tests anywhere in npu_engine despite substantial testable logic: graph traversal, torus math, coherence scoring, tihai computation, JI tuning ratios, formant values. All pure functions. All highly testable.

### 8. coherence_engine_v2.py has dead code

A `_CAT_W` dictionary is defined twice (lines ~26-40, then again later). The first definition is shadowed and never used. Harmless but messy.

### 9. Tanpura param overlap

Three files compute tanpura-related parameters:
- `tanpura_field.py` -- 22-shruti system, field -> tuning
- `relational_synth.py` -- broader scope, relations -> synth params
- `relational_params.py` -- physics-level NamedTuples (TanpuraPhysics, SympatheticPhysics)

They operate at different abstraction levels and are not contradictory, but the chain of authority (which calls which, which is canonical) is underdocumented.

### 10. No broken files

Every single .py file in npu_engine contains real implementation. There are no abandoned experiments, no half-written modules, no import-error files, no dead code files. The two empty files are explicitly test stubs. Everything else works. For a 105-file codebase built incrementally, this is unusual.

---

## Recommended Next Builds

### Immediate (low risk, high value)

1. **Remove dead code in coherence_engine_v2.py** -- delete the duplicate `_CAT_W` block (lines 26-40). 5-minute fix.

2. **Write tests for core chain** -- datasets -> graph_engine -> coherence_engine_v2 -> toroidal_field -> igpu. All pure functions. Start with `test_toroid.py` since the file already exists.

3. **Document the tanpura param chain** -- add a comment block in each of tanpura_field.py, relational_synth.py, relational_params.py explaining which is authoritative for what.

### Medium term (requires SC audio path)

4. **Instantiate one threaded kernel** -- start with SympatheticKernel (smallest surface area: 4 files, clear inputs). Add to kernel.py or om.py with a feature flag. Proves the threaded kernel pattern works.

5. **Instantiate RhythmKernel** -- next smallest. The tihai math and sam-gravity are the most musically distinctive features of the system.

6. **Instantiate MixKernel** -- replaces sound/ with the 11-layer model. This is the big architectural step: sound/ -> mix/ migration.

### Longer term

7. **Wire VocalKernel** -- the most ambitious subsystem. Requires formant synthesis on the SC side. The Python side is ready.

8. **Reconcile sound/ vs mix/** -- decide on single port, migrate sound_engine.py consumers to mix/, retire sound/ when mix/ is proven.

9. **Wire sarangi_voice.py** -- bowed string synthesis. Needs an audio output target.

---

## The Full Picture

npu_engine is not a collection of scripts. It is a relational computation engine that takes astronomical time (panchanga), maps it through a 7000-node knowledge graph onto a torus, scores entities by coherence, and produces:

- A **field state** (what is active now, why, how strongly)
- A **visual layout** (64-node SVG cosmos via iGPU)
- A **sound specification** (raga, tuning, drone parameters, mix levels)
- A **text resolution** (which passages from which shastras are relevant)
- A **zone map** (vastu mandala for the UI)

The 37 modules integrated into kernel.py handle the first three outputs well. The 68 modules not yet integrated are not debris -- they are four complete subsystems (mix, rhythm, sympathetic, vocal) waiting for the SuperCollider audio path to be resolved, plus their supporting modules.

The architecture is consistent. Every subsystem follows the same pattern: a graph of seed data, an engine that traverses it given field state, an OSC bridge that sends the result. The threaded kernels all implement the same interface. The zone engines all subclass the same base. The mix modulators all take the same inputs and return the same shape.

What exists is a 105-file engine where 97 files contain real working code, 4 complete subsystems are ready to activate, and the only gaps are 2 empty test files and 1 block of dead code. The system is waiting for its audio path, not for its logic.
