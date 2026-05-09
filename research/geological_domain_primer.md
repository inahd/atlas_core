# Geological-Domain Primer for Atlas

*Implementation-prep document for atlas_core. Specifies what the geological dataset extension needs to cover, what existing taxonomies are available to draw from, and how to structure the data to support the materials-cosmology integration. Companion to wootz, materials-cosmology, and tamahagane research consolidations.*

---

## Purpose

The metals dataset is mature. The materials-cosmology integration that surfaced May 2, 2026 (bhasma-geopolymer-silpi-deity-stone-form unification) requires extending Atlas to include stones, minerals, and geological materials at all scales of preciousness — not just the navaratna gems and panchaloha-class metals already represented.

The geological extension is the gap. This primer scopes what it needs to contain, identifies the existing taxonomies (both contemporary mineralogy and traditional silpi-shastra) Atlas can draw from, and structures the dataset architecture to fold into the existing relational graph and transduction-folding software.

---

## What the geological domain must cover

Six interlocking subdomains, each populating different aspects of the relational graph:

### 1. Stone classification by formation pathway

Contemporary mineralogy classifies rocks into three broad categories with subdivisions:

**Igneous** (formed from cooling magma/lava):
- Intrusive (slow-cooling, large crystals): granite, diorite, gabbro, peridotite
- Extrusive (fast-cooling, small or no crystals): basalt, andesite, rhyolite, obsidian
- Pyroclastic (from volcanic eruption fragments): tuff, pumice, ignimbrite

**Sedimentary** (formed from deposition and lithification):
- Clastic (mechanical fragments): sandstone, shale, conglomerate, breccia
- Chemical (mineral precipitation): limestone, dolomite, evaporites, chert
- Biogenic (biological origin): coal, fossiliferous limestone, diatomite

**Metamorphic** (formed by heat/pressure transformation):
- Foliated: slate, schist, gneiss, phyllite
- Non-foliated: marble, quartzite, hornfels
- Contact metamorphic vs regional metamorphic

Each pathway carries different alchemical character in the materials-cosmology framework. *Igneous stones carry fire-element signature from their formation. Sedimentary stones carry water-element and time-deep-accumulation signature. Metamorphic stones carry transformation-under-pressure signature.* These map onto graha-quality and elemental classifications.

### 2. Mineral composition and structural properties

Beyond rock-type classification, individual minerals carry specific qualities:

**Primary mineral families** (chemical composition):
- Silicates (quartz, feldspars, micas, pyroxenes, amphiboles, olivine)
- Carbonates (calcite, dolomite, aragonite)
- Oxides (hematite, magnetite, ilmenite)
- Sulfides (pyrite, galena, chalcopyrite)
- Halides (halite, fluorite)
- Sulfates (gypsum, barite)
- Phosphates (apatite)
- Native elements (gold, silver, copper, sulfur, diamond)

**Crystal structure** (geometric organization):
- Cubic, tetragonal, orthorhombic, hexagonal, trigonal, monoclinic, triclinic
- Crystal-structure determines optical properties, hardness anisotropy, cleavage planes
- Cosmologically: crystal symmetry corresponds to yantra-geometric character — cubic stones for stability/grounding, hexagonal for resonance, etc.

**Hardness** (Mohs scale): determines durability, working-resistance, suitability for specific uses.

**Density / specific gravity**: relevant for vastu (which materials at which positions in building), for ritual instruments (weight for specific functions), for medical preparation (settling rates in bhasma processing).

**Magnetic susceptibility**: paramagnetic, diamagnetic, ferromagnetic. Critical for the field-state research — paramagnetic minerals organize charge differently than diamagnetic. Soil paramagnetism is a documented variable in biodynamic agriculture.

**Optical properties**: refractive index, birefringence, dichroism, fluorescence. Relevant for gem-quality classification but also for traditional stone-recognition.

**Trace element content**: minor and trace elements often determine the cosmologically-relevant character even when major composition is similar. Vanadium in iron ores (wootz), specific trace minerals in Gandaki riverbed (Śālagrāma chemistry), specific ash-content of plant additions (bhasma).

### 3. Geographic provenance with cosmological-significance

Specific stones from specific places carry irreplaceable signature. The geological extension must include:

**Deity-stone-form provenance**:
- Gandaki River, Nepal: Śālagrāma (Vishnu, fossil ammonites with specific chakra-marks)
- Narmada River, Madhya Pradesh: Bāṇa-liṅga (Shiva, cryptocrystalline quartz cylinders)
- Govardhan Hill, Vraja, Mathura district: Govardhana-śilā (Krishna, specific surface qualities)
- Dvārakā coast, Gujarat: Dvārakā-śilā (Krishna, marine fossilization)
- Various regional Devi-stones with specific provenance

**Traditional metallurgy provenance**:
- Iron ore belts of Karnataka (Bhadravati, Chitradurga, Gulbarga): wootz iron sources
- Tamil Nadu (Kodumanal, Mel-siruvalur, South Arcot): wootz crucible production
- Andhra Pradesh / Telangana (Konasamudram, Golconda): wootz steel production
- Sri Lanka (Alutnuvara, others): wootz (continued through 1903)
- Shimane Prefecture, Japan: tamahagane iron sand (satetsu)
- Cornwall, UK: tin (historical bronze production)
- Sinai Peninsula, Egypt: malachite, copper sources (ancient Egyptian metallurgy)

**Sacred site geological signatures**:
- Akhara grounds (specific paramagnetic mineral content from generations of cultivation)
- Temple sites (specific stones selected through silpi-shastra principles)
- Pilgrimage geology (specific geological features at major tirtha sites)
- Lost / hypothesized akhara sites (the South American site referenced in the novel substrate work — terra preta soils, specific mineral signatures)

**Industrial/mundane provenance**: needed for completeness and for distinguishing high-cosmological-signature materials from low-signature manufactured materials. Standard concrete, standard steel, standard glass — these are mineralogically real but qualitatively flattened.

### 4. Geological time-scale information

Stones carry biographical depth. The geological extension should encode:

**Formation age**: when did the rock/mineral form? Triassic limestone vs Eocene limestone have measurably different signatures even when composition matches.

**Formation duration**: rapid solidification vs slow crystallization affects the structural depth of signature. Volcanic glass formed in seconds vs intrusive granite formed over millions of years carry different time-encoded information.

**Weathering history**: surface-exposure age, freeze-thaw cycles, water-interaction history. A river-tumbled stone has biography distinct from a quarry-cut stone of identical composition.

**Continuous worship / use history**: specifically for deity-stone-forms and ritual-significant stones. A Śālagrāma worshipped continuously for 200 years carries cumulative state distinct from a newly-collected Śālagrāma. This temporal-worship dimension is operationally crucial in the tradition and should be representable.

### 5. Bhasma-relevant characteristics

For stones and minerals processed alchemically (rather than worshipped as deity-forms), the geological extension cross-references with the bhasma protocol dataset (separate but linked):

**Suitability for śodhana**: which solvents/plant-juices the mineral responds to.
**Behavior under puta cycles**: what temperature ranges, how many cycles, what plant mediators required.
**Final bhasma properties**: nano-scale structure expected, therapeutic associations, dosha-rasa-virya-vipaka classifications.
**Compatibility with other minerals**: which alchemical combinations work, which require intermediates.

### 6. Sound-stone interaction parameters

For stones that respond significantly to acoustic input:

**Resonant frequency ranges**: characteristic frequencies for the stone's bulk properties.
**Acoustic-coupling characteristics**: how readily the stone accepts acoustic energy from different sources.
**Density and crystalline-structure information**: relevant to whether sound can affect structure beyond surface.
**Documented acoustic-archaeological associations**: which stones are used in acoustic-significant ancient sites.

---

## Existing taxonomies to draw from

**Contemporary mineralogy**:
- USGS mineral databases
- Mineralogical Society of America datasets
- mindat.org (extensive crowd-sourced mineral database)
- Various university geological department open data
- IUPAC chemical-compositional standards

**Indian traditional sources**:

The major silpi-shastra texts containing materials-classification frameworks:

**Northern (Visvakarma) tradition**:
- *Visvakarma-prakāśa* — comprehensive treatise
- *Samarāṅgaṇa-sūtradhāra* — Bhoja's 11th-century compilation
- *Aparājita-pṛcchā* — extensive temple architecture
- *Rūpa-Maṇḍana* — image-making focus

**Southern (Maya) tradition**:
- *Mayamata* — ~9th century Tamil Nadu, 36 chapters, 3300 verses, well-translated (Bruno Dagens, IGNCA 1994)
- *Mānasāra* — pan-Indian, 70 chapters, 10,000 verses, complete manuscript survives, P.K. Acharya English translation (early 20th century)
- *Aṃśumad-bheda* — Vaishnava-aligned text
- *Agastya-Sakalādhikāra* — attributed to sage Agastya
- *Śilparatna* — 16th-century Kerala
- *Kāśyapa-śilpa-śāstra* — north/west tradition

**Other key texts**:
- *Bṛhat Saṃhitā* (Varāhamihira, 6th c.) — chapter on building materials, gemstones, geological omens
- *Viṣṇudharmottara Purāṇa* (chapters on art and architecture)
- *Agni Purāṇa* (chapters on temple-building)
- *Citra-laksaṇa* (image-making text)
- *Śilpa-prakāśa* (specifically Odishan tradition)

**Rasaśāstra texts** (for bhasma-relevant mineral knowledge):
- *Rasaratna-Samuccaya* — comprehensive
- *Rasarṇava* — early major text
- *Rasendra-Maṅgala* — often cited
- *Rasa-Tarangiṇi* (Sadanand Sharma) — late and synthetic
- *Āyurveda-prakāśa* — herbo-mineral focus

**Ratnaśāstra texts** (gemology):
- *Ratna-parīkṣā* (Buddhabhaṭṭa) — major gemological text
- *Agastya-mata* on gems
- *Garuḍa Purāṇa* gem chapter
- Various regional ratnaśāstra commentaries

**Critical observation:** Most of these texts are partially or fully untranslated. Where translations exist, they often skip the technical materials-classification chapters in favor of architectural/iconographic content. **The materials-classification data within silpi-shastra is substantially under-engaged from a contemporary materials-science perspective.** This is an enormous research opportunity.

---

## Schema design proposal

The geological extension should be implemented as multiple linked tables in the existing CSV-based dataset architecture, with cross-references to other Atlas datasets through the relational graph.

### Core tables

**stones.csv** — primary stone/rock entries:
```
stone_id | name_english | name_sanskrit | name_regional | rock_category | formation_pathway | primary_mineral_composition | crystal_system | mohs_hardness | density | magnetic_susceptibility | optical_properties | trace_elements | typical_color | regional_variation_notes
```

**minerals.csv** — primary mineral entries (more granular than stones):
```
mineral_id | name | chemical_formula | mineral_family | crystal_system | hardness | density | optical_properties | magnetic_susceptibility | electrical_properties | typical_occurrences | trace_element_associations
```

**stone_provenance.csv** — geographic-significance mapping:
```
provenance_id | stone_id | location_name | location_coordinates | river_or_region | tradition_significance | deity_form_associations | ritual_use_history | continuous_worship_record
```

**deity_stone_forms.csv** — specific deity-stone-form catalog:
```
form_id | deity | form_name | provenance_id | recognition_criteria | chakra_marks_or_features | typical_size_range | color_variations | acquisition_protocols | worship_protocol_references
```

**stone_graha_correspondences.csv** — graha associations (extending the existing gem-graha table):
```
correspondence_id | stone_id | primary_graha | secondary_graha | quality_notes | ritual_applications | astrological_timing
```

**stone_temporal.csv** — geological time-scale and use-history information:
```
temporal_id | stone_id | formation_age_range | formation_duration | weathering_history | first_recorded_use | continuous_use_periods | known_significant_specimens
```

### Cross-references (implemented through transduction-folding fields)

**To bhasma protocols**: which stones/minerals enter which bhasma preparations, with cross-reference to the (separately scoped) bhasma protocol dataset.

**To architectural materials (vastu)**: which stones appropriate for which positions in which building types.

**To panchamahabhuta**: which stones carry which elemental signatures (igneous = fire, sedimentary = water, metamorphic = transformation, etc., refined through specific mineral-element correspondences).

**To plant correspondences**: stones often have associated plants (the plant grows in the soil derived from the stone, the plant's ash is used in alchemical processing of the stone, etc.).

**To nakshatra correspondences**: regional nakshatra-rulership maps to specific geographic provenance — stones from a specific region carry the nakshatra-quality of that region.

**To temple-deity associations**: specific deities at specific temples are worshipped with specific stones — extending the deity-stone-form catalog into the broader temple-architecture domain.

---

## Data sources to populate

In rough order of accessibility:

**Already-digitized**:
- USGS mineral data
- mindat.org records
- Wikipedia mineral and rock taxonomies (as starting reference)
- Open-access geological survey data from various countries
- *Mayamata* (Bruno Dagens edition with translation)
- *Mānasāra* (P.K. Acharya edition)
- *Bṛhat Saṃhitā* (multiple translations exist)

**Partially digitized / requires effort**:
- Full silpi-shastra corpus translations (many texts have partial translations only)
- Rasaśāstra primary texts
- Ratnaśāstra primary texts
- Regional silpi-shastra traditions (Odishan, Kerala, Bengal-specific texts)

**Living-tradition consultation**:
- Practicing silpis (sculptors, temple-builders) carry working knowledge that doesn't exist in texts
- Practicing rasaśāstra vaidyas carry bhasma-protocol knowledge
- Practicing astrologers carry ratnaśāstra application knowledge
- Specific traditional families with deity-stone-form expertise (Śālagrāma identification specialists, etc.)

**Archive access**:
- Bhaktivedanta Research Centre Kolkata (Vaishnava tradition material)
- IGNCA (Indira Gandhi National Centre for the Arts) — major silpi-shastra preservation institution
- Archaeological Survey of India publications
- Various state archaeology departments

**Modern materials-science research**:
- Specific peer-reviewed papers on traditional materials (bhasma standardization, geopolymer studies, Damascus steel analysis, tamahagane characterization)
- Gemological Institute datasets
- Specific provenance-tracing studies (Śālagrāma authentication, etc.)

---

## Implementation phases

### Phase 1 — Scaffold (no data yet)

Create the table structures with proper schemas, foreign-key relationships, and integration with existing Atlas datasets. Run validation tests to confirm the schema folds correctly into the relational graph and supports test queries across domains.

Estimated effort: 1-2 focused days. *This is what the kanjira-side Claude Code work would look like.*

### Phase 2 — Major reference data population

Populate from accessible digitized sources:
- USGS / mindat.org for mineralogy basics (~500 minerals)
- Wikipedia for rock taxonomy (~150 rock types)
- *Mayamata* and *Mānasāra* for silpi-shastra materials chapters (~50-100 stone-classification entries)
- *Bṛhat Saṃhitā* for traditional materials and timing rules
- Existing Atlas metals/gems data extended where stones-and-minerals overlap

Estimated effort: 2-4 focused weeks. Cross-checking and validation continues throughout.

### Phase 3 — Deity-stone-form catalog

Specific population for Śālagrāma, Bāṇa-liṅga, Govardhana-śilā, Dvārakā-śilā, major Devi-stones. Smaller dataset but high cosmological density. Requires careful cross-reference with worship-tradition material.

Estimated effort: 1-2 focused weeks.

### Phase 4 — Bhasma protocol cross-linking

Once the bhasma protocol dataset (separately scoped) exists, cross-link each entry to the geological extension. Establishes which specific minerals enter which bhasma preparations under which protocols.

Estimated effort: integrated with bhasma dataset development.

### Phase 5 — Provenance and temporal data deepening

Specific high-cosmological-significance provenance research:
- Akhara ground geological surveys (where accessible)
- Specific temple-stone provenance research
- Continuous-worship tracking for major deity-stone-forms

Estimated effort: ongoing, distributed across years. This is data that accumulates as Atlas matures.

### Phase 6 — Untranslated source engagement

Selective translation/transcription work on the under-engaged silpi-shastra and rasaśāstra materials-classification chapters. Could be:
- Individual research project (focused on specific text/chapter)
- Collaborative work with Sanskrit-trained scholars
- Long-term effort engaging with IGNCA or similar institutions

Estimated effort: years of distributed work. This is the deep substrate.

---

## What this enables

Once the geological extension exists and is populated:

**Novel substrate work**: Anika's research can be modeled in Atlas. Soil samples from specific provenance with specific mineral profiles produce specific instrument readings that her analytical work could surface. The field-active sites the novel references (akhara grounds, deity-stone sites, the South American akhara, household land) become representable as substrate-positions in the relational graph. The fisherman's water-perception, the akhara warrior's ground-tasting, the homeless man's tunnel-wall reading — all become operations within a represented materials-cosmology.

**Research on the materials-cosmology integration**: Specific cross-references can be tested. If bhasma-grade alkaline processing produces specific structural signatures, do those signatures appear in geopolymer-hypothesis pyramid samples? If sound-stone interaction is real at specific resonant frequencies, can specific stone types be identified for specific acoustic applications? The questions become tractable rather than vague.

**Wootz testbed**: The wootz research becomes testable through Atlas. Specific iron-ore provenance + specific plant carbon sources + specific timing protocols → predicted material outcomes. The transduction-folding software has the data domain it needs to function.

**Architectural-scale alchemy modeling**: Geopolymer hypothesis, vastu-shastra material specifications, traditional temple construction protocols all become representable. Atlas could model specific historical buildings (Pyramid of Khufu, specific Indian temples, Tiwanaku megalithic sites) with their specific material substrate-state.

**Field-state modeling at substrate-density levels**: Atlas's existing wave-field and Chladni alignment work integrates with materials-cosmology when the materials are specified at substrate-property level. The Chladni patterns at specific tithis become predictively linked to specific material substrates' resonance characteristics.

**Comparative tradition entries**: Tamahagane, Roman concrete, Maya blue, Egyptian faience, Damascus steel — all become representable cases within the same framework. Cross-cultural verification of the materials-cosmology principle becomes systematic rather than anecdotal.

**Cross-domain queries**: "Which stones support which dhatus when used as bhasma?" "Which architectural materials correspond to which graha-conditions?" "Which iron-ore provenance is most likely to produce wootz-grade outcomes given current conditions?" These become tractable queries against the unified relational graph.

---

## Risks and considerations

**Risk: Forcing contemporary mineralogy into traditional vocabulary or vice versa.** The two registers are not in 1:1 correspondence. Some traditional categories don't map cleanly to mineralogical species (e.g., the "rasa" of a stone in silpi-shastra is not just chemistry). Some mineralogical categories don't have traditional equivalents (e.g., trace-element profiles). The schema must accommodate both registers without forcing reduction.

**Risk: Inventing tradition where it isn't there.** When silpi-shastra texts are silent on a question, the schema should allow "unknown / not in tradition" rather than fabricated entries. Especially for specific historical claims (which exact stone was used at which ancient site) — these need to be flagged as inferential where they are.

**Risk: Cosmological overclaim.** The materials-cosmology framework is genuinely supported by multiple research programs but is not yet established science. Atlas should represent it as a unified framework that integrates traditional knowledge with contemporary measurement, while keeping the metaphysical commitments distinguishable from the empirical claims. Future researchers using Atlas should be able to engage either register without being forced into both.

**Risk: Over-comprehensive scope.** Trying to cover all minerals, all stones, all traditions exhaustively will exhaust the project. Better to start with a focused subset (say, the 50 most cosmologically-significant stones across traditions, the 30 standard bhasma preparations, the major deity-stone-forms) and let the dataset grow organically as research questions surface.

**Risk: Sanskrit transliteration inconsistency.** Sanskrit terms across Atlas should follow consistent transliteration (IAST preferred). The geological extension introduces many new Sanskrit terms; consistency must be maintained from the start.

---

## Specific next steps

In order from most-tractable to most-deep:

**1. Scaffold the schema** (Claude Code task). Generate the seven core CSV templates with proper field definitions and validation rules. Set up cross-references to existing Atlas tables. Run integration tests against the existing relational graph.

**2. Populate from digitized contemporary sources** (research + data-entry task). USGS mineral database extracted to atlas-format. Wikipedia rock taxonomy extracted. Basic mineralogy populated.

**3. Read and extract from *Mayamata* and *Mānasāra* materials-classification chapters** (translation/extraction task). These two texts have decent English translations and are the entry-point to silpi-shastra materials knowledge. Specific chapters on stones, materials selection for buildings, materials testing.

**4. Cross-reference *Bṛhat Saṃhitā* sections on building materials and gems** (textual research task). Varāhamihira's 6th-century compendium has substantial materials sections that connect to graha-timing and astrological frameworks.

**5. Begin deity-stone-form catalog** (devotional-research task). Śālagrāma criteria, Bāṇa-liṅga criteria, Govardhana-śilā criteria. Living tradition consultation as needed for verification.

**6. Cross-link with existing Atlas metals/gems data** (integration task). Where the new stones/minerals data overlaps with existing entries, establish proper relationships. Verify nothing breaks.

**7. Document cross-domain query examples** (validation task). Run specific queries that test the integration: "soil signatures of akhara grounds," "stone-graha correspondences at specific temple sites," "wootz-relevant iron-ore provenance," etc. Confirm Atlas produces useful results.

This sequence is roughly a focused 1-2 month effort for the scaffolding and basic population, with deeper data acquisition continuing for years.

---

## Summary

The geological-domain extension is the missing data layer for Atlas's materials-cosmology integration. The structure is implementable on top of the existing Atlas architecture without restructuring. The data sources exist, with varying levels of accessibility. The traditional silpi-shastra and rasaśāstra texts contain substantial under-engaged materials-classification knowledge that contemporary materials science is independently rediscovering through different vocabulary.

Atlas's relational graph is positioned to integrate these registers. The transduction-folding software, when implemented, will operate on the populated geological domain as part of its cross-scale alchemical modeling. The wootz research becomes testable. The novel substrate work gains representable ground. The materials-cosmology framework gains empirical grounding through cross-tradition data integration.

The work is substantial but tractable. The architecture is correct. The next move is scaffolding the schema, which is a Claude-Code-on-kanjira task of 1-2 days, after which population can proceed in parallel with other Atlas work over months and years.

The geological extension is not the deep substrate of Atlas — that's the cosmological framework itself. The geological extension is the missing data layer that lets the substrate operate at materials-scale resolution. With it in place, the integration that surfaced May 2 becomes implementable rather than aspirational.
