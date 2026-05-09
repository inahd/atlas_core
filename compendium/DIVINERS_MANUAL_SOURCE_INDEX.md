# Diviner's Manual — Source Material Index

Generated April 23, 2026

---

## How to use this index

Each of the 8 planned volumes has a section below listing on-disk sources,
engine references, dataset references, existing compendium material, and
known gaps (material that exists only in chat history). The index is the
drafting substrate for the manual — it tells the author exactly where to
find what, and where gaps require separate retrieval or authoring.

---

## V0 — Reader's Stance

_Philosophical preamble: attestation tiers, confessional framing, what Atlas
can and cannot do as a divinatory instrument._

### On-disk sources

- `compendium/positioning_essays/01_atlas_in_the_bhaktisiddhanta_thompson_lineage.typ` — scaffold. The lineage positioning (Bhaskara → Bhaktisiddhanta → Thompson → Atlas) frames V0's methodological honesty.
- `compendium/positioning_essays/02_confessional_methodology_as_honest_stance.typ` — scaffold. "Confessional methodology, not history of science" — the epistemic humility stance.
- `docs/audit/OPEN_QUESTIONS.md` — items #7 (speculative yantra geometry), #8 (bat T=12 verification), #14 (paper audience split) exemplify the attestation discipline in practice.
- `docs/skills/atlas-state-SKILL.md` — §Confessional-Methodology Stance, §Architecture Decisions (bhedabheda filter: "harinama never appears in avoid lists").

### Engine references

None — V0 is pure philosophy.

### Dataset references

None directly. The attestation system itself (`attestation_status` column present in 100+ CSVs) is the data artifact V0 describes.

### Existing compendium material

Two positioning essay scaffolds (above). Their content, when drafted, IS V0's substrate.

### Gaps

- **Attestation tier formalization** — the TIER 1-4 system (OBSERVED:PRIMARY → OBSERVED:TRADITIONAL → SYNTHESIS → SPECULATIVE) was worked out across multiple chat sessions (March-April 2026). The existing attestation columns in CSVs embody it but no standalone document defines it.
- **"Atlas is instrument not oracle" framing** — chat history, multiple sessions. The distinction between instrument (reads the field as it is) and oracle (claims to predict) is central to V0.
- **BRS 1.2 subordination principle** — the bhedabheda filter (horoscopy subordinated to bhakti-metaphysics) is in the code but not in any prose document.

---

## V1 — Reading the Field

_Panchanga, current Nitya, wave field, graha state, nadi/swara flow, pada
petal depth (D9-D108), mahadasha context._

### On-disk sources

- `research/research_ayurveda_panchanga.md` (30KB) — panchanga computation details, dinacharya, dosha-nakshatra interaction. Directly relevant to field-reading methodology.
- `research/research_svara_shastra.md` (15KB) — svarodaya breath rules, nadi flow, tithi-dependent swara. Sections on activity_matrix and coherence_rules are V1 substrate.
- `research/two-source-interference-v3.md` (32KB) — Findings 8-14. The wave field IS the field-reading instrument. F8 (aspect = harmonic), F10 (tithi fine structure), F11 (gandanta amplification).
- `research/planetary-primes-v1.md` (16KB) — graha retrograde symmetries (3,5,7,11). The field-reading of which planetary primes are active at a given moment.
- `research/yantra_eigenvalue_exploration.md` (5KB) — Lo Shu spectral structure. The yantra IS the field's geometric face; reading it means reading these eigenvalues.
- `research/deep-research-report (7).md` (~12KB) — tithi_devi_registry: the 15 Nitya Devis mapped. Direct V1 substrate for "current Nitya" reading.

### Engine references

- `npu_engine/jyotisha_engine.py` — `compute_chart()`, `compute_tithi()`, `compute_tara_bala()`, `compute_wave_field()`, `compute_nakshatra_field()`. The computational field-reading apparatus.
- `npu_engine/jyotish_utils.py` — normalization, DMS parser, data loaders.
- `npu_engine/field/trajectory_engine.py` — `derive_trajectory()` — temporal arc, dasha context.
- `npu_engine/field/svarodaya_engine.py` — `derive_svarodaya()` — nadi/swara at this moment.
- `npu_engine/sound/sound_engine.py` — `_enrich_with_wave_field()` — the sound-as-field-reading.
- `kernel.py` — `calc_panchanga()` (line 2273+), `field_state()`, `NITYA_DEVIS` (line 276+).
- Routes: `/field`, `/spine`, `/trajectory`, `/jyotish/natal`, `/jyotish/transits`, `/jyotish/wave_field`.

### Dataset references

- `datasets/astro/` (16 CSVs) — nakshatra_master, tithi_master, graha data. The raw field.
- `datasets/cosmology/nitya_devi_master.csv` (15 rows) — current Nitya attributes.
- `datasets/cosmology/nitya_yantra_geometry.csv` (15 rows) — yantra parameters per Devi.
- `datasets/jyotish/` (5 CSV + 3 YAML) — dignity, friendship, aspects, karakas, lords.
- `datasets/svarodaya/` (6 CSVs) — activity_matrix, nadis, tithi_rules, vara_rules, coherence_rules, elements.

### Existing compendium material

- `field_dives/01_jyotish_and_wave_field.typ` — scaffold, not yet populated. Its research_source points at two-source-interference-v3.md.
- `field_dives/svarodaya.typ` — built, converted from research_svara_shastra.md.
- `research_papers/two_source_interference.typ` — built, the wave field paper.

### Gaps

- **Pada petal depth D9→D108** — chat history, April 20 2026 session. The division of each nakshatra pada into navamsha sub-petals, and further into dasamsha, dvadasamsha, and shodasamsha depths. Not on disk.
- **Mahadasha reading methodology** — the kernel has NATAL dasha data but no prose document explains how to read dasha transitions as field events.

---

## V2 — Cast Oracles

_Prasna jyotish, pasaka kevali, I Ching (Lo Shu weighted), Shalaka
(Rama/Bhagavatam/Gita variants)._

### On-disk sources

- `research/yantra_eigenvalue_exploration.md` — Lo Shu eigenvectors define the hexagram space. The hexagram IS a Lo Shu projection.
- `research/two-source-interference-v3.md` — Finding 8 shows aspect harmonics = hexagram structure. The I Ching augury IS two-source interference on the field.
- `research/iching_spectral_analysis.json` (5KB) — raw spectral computation.
- `research/loshu_iching_interaction.json` (1KB) — Lo Shu × I Ching interaction.
- `research/magic_cube_analysis.json` (4KB) + `magic_cube_extension.json` (4KB) — extended cube mathematics.

### Engine references

- `npu_engine/field/iching_augury_engine.py` (414 lines) — `score_hexagram()`, `score_omen()`, `cast_hexagram()`, `trigram_field_map()`. The complete I Ching oracle engine with Lo Shu weighting.
- `npu_engine/pasaka_engine.py` + `npu_engine/field/pasaka_engine.py` — two versions (root = simple cast, field = Lo Shu derived). The pasaka kevalī oracle.
- `npu_engine/field/reading_engine.py` — `derive_reading()` with 5 lenses: tarot, iching, jyotish, calendar, bandhu.
- `npu_engine/card_engine.py` — tarot/oracle card draws and spreads.
- Routes: `/lila/augury/hexagram/<int>`, `/lila/augury/omen/<phenom>`, `/lila/augury/cast`, `/lila/augury/field`, `/lila/augury/pasaka`, `/lila/oracle/timepointer`, `/oracle` (HTML page), `/shalaka`, `/tarot/draw`, `/reading`.

### Dataset references

- `datasets/iching/hexagrams.csv` (64 rows) — hexagrams with vastu/graha/lifecycle.
- `datasets/iching/trigrams.csv` — 8 trigrams with metadata.
- `datasets/iching/trigram_vastu_map.csv` — trigram → vastu positions.
- `datasets/iching/pasaka.csv` (64 rows) — 3d4 dice outcomes with devi names.
- `datasets/iching/hexagram_nakshatra_resonance.csv` — hexagram ↔ nakshatra.
- `datasets/iching/hexagram_devi_resonance.csv` — hexagram ↔ devi.
- `datasets/iching/hexagram_raga_resonance.csv` — hexagram ↔ raga.
- `datasets/iching/changing_lines.csv`, `hexagram_lines.csv` — line texts.
- `datasets/tarot/devi_cards.json`, `nakshatra_cards.json`, `graha_cards.json` — card decks.
- `datasets/vedic_omens.csv` (30 rows) — Brhat Samhita shakuna omens used by omen scorer.

### Existing compendium material

- `field_dives/10_oracle_instruments.typ` — scaffold. The intended home for V2 substrate.
- `research_papers/lo_shu_spectral_carrier.typ` — built. Lo Shu mathematics underlying the hexagram weighting.

### Gaps

- **Prasna jyotish methodology** — horary chart casting for a question-at-a-moment. The jyotisha engine can compute a chart for any datetime but no prose document explains prasna-specific interpretation (lagna lord as querent, 7th lord as answer, etc.).
- **Shalaka variant texts** — `static/shalaka.html` exists for Rama Shalaka but the Bhagavatam and Gita variants mentioned in the manual outline have no dataset or engine support.
- **Pasaka kevalī full methodology** — the engine exists but the Bower Manuscript tradition and the kevali (solitary, non-paired) casting protocol are not documented on disk.

---

## V3 — Nimitta (Sensed World)

_Shakuna (birds), animal omens, weather portents, plant/insect signs,
hora-modulated interpretation._

### On-disk sources

- `datasets/vedic_omens.csv` (30 rows) — Brhat Samhita Chapter 86 bird omens with direction, time, meaning, quality, field_state_indicated, attestation. **This is the primary structured substrate for V3.**
- `datasets/sources/jyotish/brhat_samhita_shakuna_chunks.jsonl` (15 chunks) — raw text passages from the Shakuna section of Brhat Samhita.
- `datasets/medicine_cards_vedic.csv` (62 rows) — animal medicine qualities with graha/nakshatra/deity parallels. SYNTHESIS attestation. Cross-cultural (Native American medicine wheel → Vedic overlay).
- `research/deep-research-report (2).md` (~31KB) — "Documented Associations of the Vedic Nakshatras." Contains nakshatra animal yoni correspondences relevant to animal-omen interpretation.

### Engine references

- `npu_engine/field/iching_augury_engine.py` — `score_omen()` function accepts a phenomenon + direction and scores against the field state using vedic_omens.csv. This IS the computational nimitta reader.
- Routes: `/lila/augury/omen/<phenomenon>`, `/lila/augury/omen/<phenomenon>/<direction>`.

### Dataset references

- `datasets/vedic_omens.csv` — the operational omen table.
- `datasets/species/nakshatra_species.csv` — animal ↔ nakshatra mappings (yoni system).
- `datasets/astrobotany/` (4 CSVs) — plant/lunar phase correlations (plant-sign reading).

### Existing compendium material

None directly. The field_dives/astrobotany.typ covers plant correspondences but not nimitta specifically.

### Gaps

- **Full Brhat Samhita shakuna corpus** — only 30 omens + 15 text chunks digitized. The original has hundreds of animal, weather, and environmental portents across chapters 85-95.
- **Weather portent tables** — not in datasets. Brhat Samhita chapters on cloud/rain/wind portents are undigitized.
- **Plant/insect sign interpretation** — astrobotany covers growth patterns, not omenic interpretation of plant events (sudden flowering, wilting, etc.).
- **Hora-modulated interpretation** — the principle that an omen's meaning changes by hora lord is in the engine (score_omen uses field_state hora) but no prose document explains the modification rules.
- **Bird call oracle design** — chat history, April 13 2026. Shakuna research prompt, bird×planet×mood mapping.

---

## V4 — Inner Oracles

_Angasphurana (body twitches), svapna (dreams), nadi pariksha (pulse)._

### On-disk sources

- `research/research_pranayama_asana.md` (55KB) — covers breath-body interface extensively. Sections on nadi flow and pranayama are substrate for the nadi pariksha aspect.
- `research/research_svara_shastra.md` (15KB) — svarodaya and nadi. The active nostril reading is a form of inner portent reading.
- `datasets/iching/pasaka.csv` — the pasaka body_region column maps each cast to a specific body location. This links the pasaka oracle to angasphurana.

### Engine references

- `npu_engine/field/svarodaya_engine.py` — active nostril / nadi state.
- `npu_engine/field/dinacharya_engine.py` — daily routine recommendations.
- Routes: `/svarodaya`, `/dinacharya`.

### Dataset references

- `datasets/svarodaya/` (6 CSVs) — nadi/element/tithi/vara rules.
- `datasets/marma/` (4 CSVs) — body region mapping (marma_points, body_region_marma). Relevant to angasphurana body-site interpretation.
- `datasets/morphogenesis/body_archetype_map.csv` (26 rows), `doctrine_of_signatures.csv` (44 rows) — body-plant-geometry morphology.

### Existing compendium material

- `field_dives/svarodaya.typ` — built, converted from svara_shastra research.
- `field_dives/yoga_and_pranayama.typ` — built, converted from pranayama_asana research.

### Gaps

- **Angasphurana table** — no CSV of body-twitch→meaning mappings exists. This is a well-documented system in Shakuna Shastra; needs sourcing from Brhat Samhita or Jyotish Ratna Mala.
- **Svapna (dream interpretation) framework** — no dataset, no engine, no research. Dream categories and their jyotish significance are in traditional texts but undigitized.
- **Nadi pariksha methodology** — the pulse-reading system. Entirely chat-history or undigitized. The svarodaya engine covers breath-nostril reading but not pulse diagnosis.

---

## V5 — Material Readings

_Metallurgical (chart as alloy), plant readings, yantra geometry interpretation._

### On-disk sources

- `research/Electromagnetic and Crystallographic Properties of Noble Metal Alloys in the Au–Ag–Cu System.docx` (27KB) — the metallurgical substrate. Cu-Ag immiscibility gap as chart-reading methodology.
- `research/Graha Friendship_Enmity and Material Interactions in Planetary Metals and Gems.docx` (27KB) — graha metal/gem correspondences from BPHS.
- `research/Ayurveda Sublayer Research — Bhasma _ Rasasastra.docx` (26KB) — material transformation (bhasma preparation) as a reading of material properties.
- `research/Coherence Atlas – Plant Profiles.docx` (20KB) — plant as field-reader (doctrine of signatures approach).
- `research/yantra_eigenvalue_exploration.md` (5KB) — yantra as geometric reading surface.
- `research/planetary-primes-v1.md` — §3 quantized field. The 44-region tidal-weighted field interpreted as material-geometric structure.

### Engine references

- `npu_engine/yantra_engine.py`, `yantra_generator.py` — yantra computation and SVG rendering.
- `npu_engine/geometry/cut_and_project.py` — N-fold quasicrystal projection for Nitya Devi portal.
- `npu_engine/nitya/devi_engine.py` — Devi yantra rendering parameters.
- Routes: `/yantra`, `/nitya/field/<tithi>`, `/nitya/mediator/<tithi>`.

### Dataset references

- `datasets/ratna/graha_gems.csv` — gem ↔ graha correspondences.
- `datasets/morphogenesis/doctrine_of_signatures.csv` (44 rows) — plant-form → body-region glyph mapping.
- `datasets/cosmology/nitya_yantra_geometry.csv` (15 rows, 81 columns) — per-Devi yantra parameters.
- `datasets/ayurveda/` (18 CSVs) — herbal correspondence matrices.

### Existing compendium material

- `research_papers/lo_shu_spectral_carrier.typ` — built. The Lo Shu IS the material-geometric reading surface.
- `research_papers/yantra_eigenvalue_exploration.typ` — built.
- `field_dives/05_ayurveda_and_the_108_herbs.typ` — built, herbal correspondences.

### Gaps

- **Metallurgical chart reading** — chat history, April 21 2026. Full alloy phase reading of natal chart. The Cu-Ag immiscibility methodology. Not on disk.
- **docx → markdown conversion** — all 4 V5-relevant docx files are trapped in binary format. Need pandoc conversion before compendium integration.
- **Rasashastra computational model** — the Bhasma research docx describes transformations but no engine implements them.

---

## V6 — Cross-Layer Inference

_Resonance, amplification, counterpoint, hinge; the Cu-Ag immiscibility
methodology case; anomalies protocol._

### On-disk sources

- `research/two-source-interference-v3.md` — the methodology paper. Findings 7-14 ARE the cross-layer inference methodology: how multiple oracular systems interact (wave interference), when they reinforce (constructive), when they conflict (destructive), when they're orthogonal (Panchaka).
- `research/planetary-primes-v1.md` — §3-5. The same prime numbers appearing in orbital mechanics AND vertebral anatomy is a case study in cross-layer inference.
- `research/vertebral-primes-v1.md` — §4-5. The yoni-vertebral correspondence IS cross-layer reading (astronomical primes → biological structure → nakshatra assignment).
- `research/yantra_eigenvalue_exploration.md` — §F5 Navagraha Composite. The 9×9 composite IS cross-layer (9 separate yantras composing into a meta-structure).

### Engine references

- `npu_engine/jyotisha_engine.py` — `compute_wave_field()` IS the cross-layer inference engine. It computes how all pairs interact at all targets.
- `npu_engine/field/reading_engine.py` — 5 lenses reading the same field = cross-layer by design.

### Dataset references

- `datasets/relations/` (27 CSVs) — the entire relation graph IS the cross-layer structure. Every edge connecting two entities from different domains is a cross-layer claim.

### Existing compendium material

- `research_papers/two_source_interference.typ` — built. The primary methodology paper.
- `research_papers/planetary_primes.typ` — built. The retrograde-symmetry case.
- `research_papers/vertebral_primes.typ` — built (private). The vertebral case.

### Gaps

- **Cu-Ag immiscibility methodology** — chat history, April 21 2026. The worked example of reading a natal chart as a metallurgical phase diagram. Not on disk.
- **Anomalies protocol** — how to handle when multiple reading systems disagree. Discussed in chat but not formalized.

---

## V7 — Worked Readings

_Annotated complete readings._

### On-disk sources

Minimal. This volume is almost entirely chat-history dependent.

### Gaps (= retrieval queue)

- **Vishakha/Punarvasu natal reading** — March 23 + April 4 2026. Two complete parallel readings of the same natal chart.
- **Jvalamalini tithi-as-natal** — April 4 2026. Tithi-at-birth as lifelong natal rasa.
- **Metallurgical chart reading** — April 21 2026. Full alloy phase reading.
- **First complete reading with all oracles** — chat history, date unknown. If it exists, it's the model for V7 annotation format.

---

## V8 — Cautions, Limits, Rest

_Short closing volume._

### On-disk sources

- `docs/audit/OPEN_QUESTIONS.md` — the open questions themselves ARE cautions (what we don't know, what's pending verification).
- The bhedabheda filter in `docs/skills/atlas-state-SKILL.md` §Architecture Decisions — "harinama never appears in avoid lists" — is the primary caution operationalized.

### Gaps

- This volume is mostly to-be-written. The cautions exist as scattered notes, not as a coherent treatment.

---

## Cross-Referenced Themes

Material serving multiple volumes:

| Theme | Primary volume | Secondary |
|-------|---------------|-----------|
| Cu-Ag immiscibility methodology | V5, V6 | V0 (attestation) |
| Wave field as reading instrument | V1 | V2 (hexagram as projection), V6 (cross-layer) |
| Lo Shu eigenvectors | V2 (hexagram weighting) | V5 (yantra reading) |
| Gandanta amplification | V1 (field reading) | V3 (nimitta sensitivity at junctions) |
| Svarodaya/nadi | V1 (field reading) | V4 (inner oracle) |
| Nakshatra yoni animals | V3 (nimitta) | V6 (vertebral cross-layer) |
| Pasaka body regions | V2 (cast oracle) | V4 (angasphurana) |
| Attestation tiers | V0 (philosophy) | every volume (applied in practice) |

---

## Chat History Retrieval Queue

Material known to exist in chat history that needs retrieval:

| Topic | Approximate date | Expected content | Target volume |
|-------|-----------------|------------------|---------------|
| Lo Shu × I Ching spectral interaction | April 12 2026 | Q₆ hypercube, Fiedler break, 7→27 eigenvalues | V2, V6 |
| Metallurgical chart reading | April 21 2026 | Full alloy phase reading, every graha as element | V5, V6 |
| Bird call oracle design | April 13 2026 | Shakuna research, bird×planet×mood mapping | V3 |
| Tarot attestation tier system | March 2026 | TIER 1-4 system formalization | V0 |
| Vishakha/Punarvasu natal reading (×2) | March 23 + April 4 2026 | Two complete parallel readings | V7 |
| Jvalamalini tithi-as-natal | April 4 2026 | Tithi-at-birth as lifelong rasa | V1, V7 |
| Prasna + nimitta + cube as three of seven | April 15 2026 | Oracle taxonomy | V2 |
| Pada petal depth D9→D108 | April 20 2026 | Divisional chart depth methodology | V1 |
| Atlas is instrument not oracle | Multiple sessions | Core framing | V0 |
| BRS 1.2 subordination principle | March-April 2026 | Bhedabheda filter rationale | V0, V8 |
| Angasphurana table design | Unknown | Body-twitch mapping proposal | V4 |

---

## Index Maintenance

This index gets updated as:
- New material is added to `research/` or `datasets/`
- Chat history material gets captured into on-disk files
- Compendium volumes get drafted (move from "gaps" to "existing compendium material")
- docx files get converted to markdown
