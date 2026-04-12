// ============================================================
// ATLAS 330: A COSMOLOGICAL FIELD COMPUTER
// Founding Document & Open Invitation — Version 0.2
// ============================================================

#set document(
  title: "Atlas 330: A Cosmological Field Computer",
  author: "inahd",
)

#set page(
  paper: "us-letter",
  margin: (top: 1.2in, bottom: 1.1in, left: 1.2in, right: 1.1in),
  numbering: "1",
  number-align: center,
)

#set text(
  font: ("DejaVu Serif"),
  size: 11pt,
  lang: "en",
)

#set par(
  justify: true,
  leading: 0.75em,
  spacing: 1.25em,
)

#set heading(numbering: "1.1")

#show heading.where(level: 1): it => {
  v(1.8em)
  text(size: 13.5pt, weight: "bold")[#it]
  v(0.5em)
}

#show heading.where(level: 2): it => {
  v(1.1em)
  text(size: 11.5pt, weight: "semibold")[#it]
  v(0.25em)
}

#show heading.where(level: 3): it => {
  v(0.7em)
  text(size: 11pt, weight: "semibold", style: "italic")[#it]
  v(0.15em)
}

#show raw: it => text(font: "DejaVu Sans Mono", size: 9.5pt)[#it]

// ── TITLE PAGE ──────────────────────────────────────────────

#align(center)[
  #v(1.6in)

  // [FIGURE 1 PLACEHOLDER: fig_bee_spiral.png — frontispiece]
  // Botanical illustration: cross-section fig, fig wasp, golden spiral orbit
  // on black ground. Caption: "Co-evolutionary dharmic covenant:
  // the fig and its wasp, bound by 87 million years of mutual becoming.
  // The geometry of their relationship is the geometry of this system."
  #text(size: 9pt, style: "italic", fill: luma(140))[
    [Figure 1: Co-evolutionary frontispiece — see image assets]
  ]

  #v(0.8em)
  #text(size: 24pt, weight: "bold", tracking: 1pt)[ATLAS 330]

  #v(0.5em)
  #text(size: 13pt, style: "italic")[A Cosmological Field Computer]

  #v(1.4em)
  #line(length: 3.4in, stroke: 0.4pt)
  #v(1.4em)

  #text(size: 10.5pt)[
    A founding document, architectural map, and open invitation \
    to researchers, practitioners, and builders working at the \
    intersection of Vedic sciences and living technology.
  ]

  #v(2em)
  #text(size: 10pt, style: "italic")[Version 0.2 --- April 2026]

  #v(0.5em)
  #text(size: 9.5pt, fill: luma(100))[
    Gainesville, Florida --- kanjira --- localhost:5000
  ]
]

#pagebreak()

// ── INVOCATION ──────────────────────────────────────────────

#v(0.8in)
#align(center)[#text(size: 12pt, weight: "semibold")[Invocation]]
#v(0.6em)

The knowledge has always existed. The texts have been preserved. The living traditions continue. And in the last decade, the computational tools to work with complex relational data have become accessible to a single practitioner on modest hardware. What has not yet been built is the integration --- a system that _runs_ Vedic knowledge as a living field rather than storing it as a collection of lookups.

Atlas 330 is an attempt to build that integration. It is not a jyotish calculator, though it computes panchanga continuously via Swiss Ephemeris. It is not a text corpus, though it holds twenty-six thousand passage chunks drawn from canonical sources. It is not a farm calendar, though it knows which plants resonate with today's nakshatra. It is a field computer --- a system in which all of these domains cohere around a single computational root: the present cosmological moment, understood relationally.

This document is simultaneously an architectural specification, a research map, and an open invitation. The architecture and the aspiration are not separate things. To understand how Atlas is built is to understand what it is reaching toward. We have written it this way deliberately.

The system currently runs on a van-mounted Intel NUC in Gainesville, Florida. It is a prototype. Significant portions are complete and working; others are specified but not yet built. We are publishing this document now, before the system is finished, because the gap in the landscape --- between what the Vedic sciences offer and what open technology has so far integrated --- is a gap that needs to be named and inhabited together.

#pagebreak()

#outline(
  title: [#text(size: 12pt, weight: "semibold")[Contents]],
  indent: 1.8em,
  depth: 2,
)

#pagebreak()

// ============================================================
// PART I: THE GAP
// ============================================================

= The Gap

== What Has Been Built

The open-source Vedic knowledge ecosystem is richer than most practitioners realize. In computational jyotish, VedAstro has assembled a non-profit platform offering chart calculation, prediction generation, and a public API, building since 2014 on the accumulated work of B.V. Raman and Suryanarain Rao. PyJHora provides a rigorous Python implementation of Vedic astrology following P.V.R. Narasimha Rao's integrated methodology, verified across nearly seven thousand tests. Maitreya and Saravali offer cross-platform desktop environments for both Vedic and western chart work. The PHP library `kunjara/jyotish` grounds its calculations directly in the Brihat Parashara Hora Shastra and the Surya Siddhanta. These are serious tools built with care.

In Sanskrit and textual scholarship, GRETIL (the Gottingen Register of Electronic Texts in Indian Languages) maintains a standardized machine-readable corpus of Sanskrit texts organized by genre --- from Vedic Samhitas and Sulbasutras through Ayurveda, Jyotisha, and cosmological texts --- now migrated to TEI/XML and integrated into long-term European research infrastructure. The Sanskrit Library provides digitized primary texts with computational research tools. The Vedavani project has assembled fifty-four hours of audio data across thirty thousand samples for Vedic poetry speech recognition. The Vedavaapi platform proposes a federated microservice architecture for Indic knowledge processing. Computational Sanskrit and Digital Humanities is an active research track producing peer-reviewed proceedings on nakshatra treebanks, handwritten manuscript OCR, and computational kavya annotation.

In ecology and agriculture, the biodynamic tradition has been practicing cosmologically-grounded farming for a century. Permaculture commons organize freely-shareable design knowledge. Ethnobotanical databases like PFAF hold detailed medicinal and ecological plant profiles for thousands of species.

Each of these is doing one thing well.

== What Has Not Been Built

None of these systems run the knowledge together. A jyotish calculator does not know which plants resonate with today's nakshatra. A text corpus does not know what muhurta it is. A farm calendar does not know which raga is sounding, which marma point is indicated, or which Nitya Devi is presiding over the current tithi. The knowledge domains exist in separate containers --- computed in isolation, stored separately, queried independently.

What is missing is a _living substrate_ --- a system in which cosmological time, plant intelligence, sound, sacred geometry, embodied knowledge, and textual tradition are not merely parallel databases but actively co-arising fields, each shifting when the others shift, all deriving from the same computational root.

This is not primarily a technical gap. All the ingredients exist: open ephemeris, open corpora, open graph databases, local LLMs, offline-capable web applications, accessible hardware. The gap is architectural and philosophical. It requires someone to decide that a farm calendar and a raga engine and a yantra generator and a text corpus should talk to each other --- and then to build the relational structure that makes that conversation possible.

== Why Now

Three conditions have converged. First, NUC-class hardware (sub-\$300, van-mountable, low-power) is now capable of running a complete relational knowledge system locally, including NPU-accelerated coherence scoring, without cloud dependency. Second, local language models (Ollama, Qwen3:8b) can run on the same hardware, enabling AI-assisted synthesis that respects traditional knowledge sovereignty --- the inference stays on the device. Third, the open ephemeris (Swiss Ephemeris), open Sanskrit corpora (GRETIL, DharmicData), and open botanical databases (PFAF) have reached sufficient quality and coverage that a comprehensive dataset layer is actually buildable.

The integration gap is now a choice, not a constraint.

#pagebreak()

// ============================================================
// PART II: THE ARCHITECTURE
// ============================================================

= The Architecture of Atlas 330

// [FIGURE 2 PLACEHOLDER: coherence_atlas.png]
// Caption: "Figure 2. Coherence Atlas: the descent of meaning into manifestation.
// S0 (Metaphysical Meaning) at apex radiates through S1 (Archetype & Deity),
// S2 (Sound & Mantra), S3 (Rhythm & Cycle), S4 (Geometry & Symbol), to S6
// (Human Experience) at base. Axes: Source↔Manifest (vertical),
// Cycles↔Forms (horizontal), Subtle to Gross (left), Eternal to Temporal (right).
// The base inscription — Sound → Rhythm → Geometry → Nature → Life —
// is the operational sequence of every Atlas field computation."
#align(center)[
  #text(size: 9pt, style: "italic", fill: luma(140))[
    [Figure 2: Coherence Atlas diagram — see image assets]
  ]
]
#v(0.5em)

Atlas is a coherence computer. It reads the Vedic cosmological moment and expresses it simultaneously through sound, visual topology, relational graph, and text. It is not a tool you use; it is an environment you inhabit. The cosmos is the operating system. Every nakshatra transit, every tithi change, every graha movement shifts what Atlas shows, plays, and suggests.

The descent sequence illustrated in Figure 2 is not a metaphor for software organization --- it is the actual computation order. Sound parameters are derived before geometry; geometry before ecology; ecology before practice. The system descends from the metaphysical through the archetypal, sonic, rhythmic, and geometric registers before it reaches the plant, body, and lived domains. This sequence, encoded as the S-layer system, governs every field computation.

The system runs continuously on a van-mounted Intel NUC (`kanjira`) at `localhost:5000`, outputting through a MOTU M2 audio interface and serving a web interface. It has 217 route definitions, 163 Python files across 15 subdirectories in the NPU engine, 110 CSV files across 33 knowledge domains, and a vector store of 26,000 passage chunks.

== The Epistemological Spine: Guru, Sadhu, Shastra

Atlas mirrors the traditional Guru-Sadhu-Shastra knowledge model. This is not a metaphor for software organization --- it is the actual architecture.

_Shastra_ is the canonical layer: Vedic texts, classical jyotish tables, Ayurvedic treatises, Puranic cosmology, Carnatic music theory. In Atlas, shastra-layer data lives in canonical CSV datasets and passage corpora. It is never overwritten by inference. Relations derived from primary sources carry attestation weights of 0.8--1.0.

_Sadhu_ is the practitioner layer: living observations, ritual experimentation, community contributions, overlays that expand the canonical structure without replacing it. In Atlas, sadhu data lives in overlay datasets and annotation layers. It can qualify, extend, and contextually emphasize shastra --- but it is always marked as such.

_Guru_ is the synthetic layer: AI inference, pattern discovery, proposed relations, visualization generation. In Atlas, all AI-generated content begins at `experimental / guru` authority and never promotes itself to canon automatically. The `guard_canon.py` gate enforces this.

Every entity in the system carries three independent axes: _stability_ (stable, working, experimental), _authority_ (shastra, sadhu, guru), and _visualization permission_ (relation, analytic, symbolic, canonical). These never collapse into each other. A node can be computationally stable but epistemically provisional. Visualization of a relation requires the visualization permission axis to be set independently.

The guiding principle throughout: _resonance over accumulation._ The system grows by resolving contradictions and connecting traditions, not by adding volume.

== The Field State

The central object in Atlas is `field_state` --- a Python dict computed by `kernel.py` on every request. It calls:

- `calc_panchanga(now)` via Swiss Ephemeris: tithi, nakshatra, vara, masa
- `get_muhurta(now)`: current muhurta window, associated raga, bpm
- `compute_yoga()`, `compute_karana()`, `compute_hora()`, `compute_rahu_kala()`
- `compute_swara()`: svara nadi from vara and tithi rules per Svarodaya

The result is a single dict from which every engine derives its output. No engine stores state independently. The richer `/spine` endpoint adds toroidal coordinates, graph coherence peaks, sound specification, trajectory, vastu grid, and layer mapping.

To illustrate: on the morning this document was drafted (Shukravara, Krishna Navami, Shravana nakshatra), a single call to `/field` returned simultaneously --- the tithi deity (Durga), the presiding devi (Kulasundari, "lineage transmission, tradition as living form, kula beauty"), the nakshatra lord (Candra), the associated element (air), guna (sattva), body region (ears), shakti (listening), the current raga (Bageshri, appropriate to Shravana's lunar quality), the therapeutic raga (Bhairavi for vata), the marma point (Vidhura, below the ear), the vastu zone (east, Agni/Shikhi), the vara graha (Guru/Jupiter), the current dasha (Budha mahadasha, Shani antardasha, closing 2027), the gem (Yellow Sapphire), and a ranked list of plants whose nakshatra, element, and deity resonances peak in this moment: Tulsi, Bilva, Lotus, Neem, Peepal, Ashoka, Sandalwood, Bael, Banana, Mango. All from a single endpoint. All co-arising.

This is what it means to run knowledge rather than store it.

== The Seven S-Layers

Atlas organizes all entities and engines across seven concentric layers of manifestation:

#table(
  columns: (auto, auto, auto, 2.2in),
  inset: 6pt,
  stroke: 0.4pt,
  align: left,
  [*Layer*], [*Name*], [*Domain*], [*Key Engines*],
  [S0], [Bindu], [Goloka, acintya source], [`goloka_engine.py`],
  [S1], [Archetype], [15 Nitya Devis, 9 Grahas], [`reading_engine.py`],
  [S2], [Sound], [Raga, tala, shruti, bija], [`sound_engine.py`],
  [S3], [Rhythm], [Panchanga, muhurta, dasha], [`trajectory_engine.py`],
  [S4], [Geometry], [Vastu, yantra, 108 pada], [`land_engine.py`],
  [S5], [Nature], [Ayurveda, plant, dosha], [`plant_engine.py`],
  [S6], [Lila], [Practice, lila maps, companions], [Bandhu, hexfield],
)

Each entity in the graph has coordinates on four axes: theta (S0 to S6, level of manifestation), phi (0 to 2pi, witness to participant relationship), S-layer assignment, and path (0.0 to 1.0, bheda-abheda). These are stored coordinate values used for coherence scoring, spatial projection, and sound mapping --- not metaphors.

== The Toroidal Coordinate System

// [FIGURE 3 PLACEHOLDER: yantra_toroidal_trajectory.png]
// Caption: "Figure 3. Yantra unfoldment along the spiraling toroidal trajectory.
// Two counter-rotating toroids (A at +ωt, B at −ωt) generate a spiraling
// trajectory through which yantra forms emerge at increasing symmetry orders:
// n=3 (triangle), n=4 (square), n=6 (hexagon), n=9 (star), n=12 (mandala),
// n=∞ (self-similarity). The left axis shows the symmetry-order progression;
// each yantra manifold is the nodal interference pattern of n equally-spaced
// plane waves at that stage of the ascent."
#align(center)[
  #text(size: 9pt, style: "italic", fill: luma(140))[
    [Figure 3: Yantra unfoldment / toroidal trajectory — see image assets]
  ]
]
#v(0.5em)

// [FIGURE 4 PLACEHOLDER: yantra_counterspace.png]
// Caption: "Figure 4. Yantra unfoldment along the spiraling counterspace of
// interfering toroids. Counter-toroid A (forward inference, gold) and
// counter-toroid B (reverse inference, teal) generate field resonance nodes
// at their interference surface. The timeline at base maps the progression:
// Seed Yantra → Tri-lattice → Square Field → Hexagonal Core → Star Yantra →
// Fractal Net → Meta-Yantra → Void Node, labeled Emergence → Expansion →
// Stabilization → Integration → Resonance → Convolution → Self-Reference →
// Transcendence."
#align(center)[
  #text(size: 9pt, style: "italic", fill: luma(140))[
    [Figure 4: Counterspace interference diagram — see image assets]
  ]
]
#v(0.5em)

The theta/phi coordinates that locate every Atlas entity in the S-layer system are not abstract indices. They derive from a toroidal cosmological model in which the solar year traces the torus tube (toroidal angle φ, one revolution per year) and the lunar-tithi cycle traces the poloidal angle θ (one revolution per synodic month). The dual-helix live view (`static/live.html`) renders this geometry in Three.js in real time.

The deeper implication of this coordinate system is that yantra forms are not constructed geometries but interference patterns that emerge at specific symmetry orders as the two cycles interact. Three equally-spaced wave sources produce triangular nodal cells (the Trikoṇa). Six produce hexagonal geometry (the Ṣaḍkoṇa). Eight produce the octagonal form underlying the eight-petal lotus. Fifteen --- the count of the Nitya Devis --- produce the full complexity of the Sri Yantra. This is computationally verified: the Atlas S4 instrument (`static/s4.html`) demonstrates the emergence sequence in a live Canvas 2D renderer, with the triangular nodal pattern confirmed at N=3 on April 8, 2026.

The mathematical structure underlying this model is discussed further in Part III under Toroidal Geometry and Yantra Emergence.

== The Deha Stack: Five Compositing Layers

The body domain in Atlas is not a single lookup table. It is a five-layer compositing system in which each layer derives from the field state and combines with the others to produce the Bandhu figure:

_Chakra_ (7 nodes, 20 attributes each) anchors the body to the cosmological field: each chakra carries a graha ruler, a bija mantra for sound synthesis, an element for plant resonance, a dosha for Ayurvedic mapping, and nakshatra assignments. This is the connector layer --- the single traversal that links the sound engine (bija), the plant engine (element/nakshatra), and the body renderer (color, body system).

_Dhatu_ (seven tissue layers: plasma, blood, muscle, fat, bone, marrow, reproductive) provides the biological substrate. The dhatu sequence follows a 7-day restorative cycle, and the plant engine cross-references dhatu targets when scoring plant resonance.

_Marma_ (26 active points in the current dataset, with body-region assignments and field-state scoring) provides the acupressure/energy anatomy layer. On every request, each marma point is scored against the current nakshatra, tithi, and element --- the highest-scoring point surfaces as the current field indication.

_Doctrine of Signatures_ (44 plant-form glyph entries at body regions) is the morphological mirror: plant growth tendencies (reaching/creeping/holding/yielding) correspond to body-region qualities derived from nakshatra shakti and element. This layer makes the co-evolutionary covenant visible --- not asserted philosophically but rendered computationally.

_Bandhu Geometry_ (Shilpa Shastra Uttama Dasatala proportions, encoded in `datasets/silpa/bandhu_geometry.csv`) governs the figure's physical dimensions. The six SVG rendering layers (skeleton, fluid, dhatu, doctrine of signatures, skin, and ornament) composite onto this scaffold.

The inverse traversal --- plant → nakshatra → body region → marma → chakra --- allows the plant corpus to reconstruct a human body frame from botanical data alone. This is the computational basis of the co-evolutionary dharmic covenant: the plant world and the human body share a common geometric grammar derivable from the same relational graph.

== The NPU Relational Graph

The knowledge graph is the connective tissue of Atlas. Every entity is a node; every meaningful connection is a directed, weighted, attested edge. The schema for each relation:

`subject | predicate | object | source | confidence | stability | authority`

The current graph holds 7,208 entities and 8,466 relational edges across 110 CSV files in 33 knowledge domains. Entity types include nakshatra, graha, deity, plant, place, text passage, rasa, dosha, chakra, marma point, mantra, raga, tala, yantra form, and vastu zone.

Relations are promoted through evidence: experimental, then working (cross-source confirmation), then stable (multiple independent primary sources attested). The NPU (Intel Neural Processing Unit, Meteor Lake architecture) handles toroidal coherence computation via OpenVINO.

The attestation hierarchy used throughout:

- `OBSERVED:PRIMARY_TEXT` (1.0): directly from Gita, Bhagavata, Charaka Samhita, etc.
- `OBSERVED:TRADITIONAL` (0.8): from living tradition (Narottama padas, jyotish tables)
- `OBSERVED:PFAF` (0.7): from scientific/ethnobotanical databases
- `SYNTHESIS` (0.4): derived by Atlas from multiple sources
- `INTERPRETATION` (0.2): inferred, not directly attested

Atlas never invents doctrine. When connecting two attested passages, the connection is marked `SYNTHESIS`. The passages retain their original attestation.

== The Six Application Domains

Six domains organize the interface layer, each a Flask route cluster served as offline-capable PWAs:

_Kala_ (`/kala`): Cosmological time. Jyotish computation, panchanga, tithi, nakshatra, dasha, muhurta. Biodynamic integration --- every day scored by planting quality derived from nakshatra element and phase.

_Devi_ (`/devi`): Archetypal presence. The 15 Nitya Devis mapped to tithis, each with weapons, mudras, rasa, and capability signature from primary source attestation.

_Deha_ (`/deha`): Embodied knowledge. Ayurveda: dosha, dhatu, rasa, guna, vipaka, virya. Nakshatra body mapping. 26 marma points scored by today's field state. The Bandhu figure renders here --- a full anatomical stack of six compositable SVG layers derived from Shilpa Shastra Uttama Dasatala proportions.

_Bhumi_ (`/bhumi`): Ecological ground. The agricultural calendar. Guild relations --- 216 guild connections across 27 nakshatra plants, moon phase driving activity type (observe, plant, harvest, prune, compost). LeelaMaps --- sacred geography browser with 63 Shakti Pithas, 34 global sacred sites, ley lines, vastu overlays. Lila Streams --- land design tool integrating vastu zones, permaculture mandala, and live plant palette.

_Vidya_ (`/vidya`): Knowledge infrastructure. Wiki engine indexing 219 structured pages. The 26,000-chunk passage corpus with vector search. Research infrastructure: anomaly logs, briefs, offering queue.

_Lila_ (`/lila`): Living interface. The coherence game with Wesnoth terrain tiles --- 404 routes render as dark forest, 200 responses as passable terrain, working apps as lit villages. The hex city where entities are positioned by theta/phi coordinates.

Bandhu (`/bandhu`) runs as ambient presence across all domains --- not an oracle, not a chatbot, but a field-responsive companion whose guidance derives from the Narottama das Thakura pada corpus, the current moment, and the graph.

== The Vastu Shell

The primary interface maps the six domains onto a 3x3 vastu mandala:

#align(center)[
  #table(
    columns: (1.4in, 1.4in, 1.4in),
    inset: 8pt,
    stroke: 0.4pt,
    align: center,
    [NW Vayu\ Sound, `/kala`],
    [N Kubera\ Rhythm, `/vidya`],
    [NE Ishana\ Archetype, `/devi`],
    [W Varuna\ Ecology, `/bhumi`],
    [C Brahma\ Cosmos, `/live`],
    [E Indra\ Codex, `/lila`],
    [SW Nirriti\ Plants, `/bhumi/ecology`],
    [S Yama\ Body, `/deha`],
    [SE Agni\ Action, `/lila/hexed`],
  )
]

Each zone is resolved by `mandala_schema.py`, which reads `field_state`, calls each zone engine's `render_zone()`, and returns nine zone specifications. The shell never computes content --- it only displays what the engines provide.

== Sound as Cosmological Field Expression

Sound in Atlas is not decoration. It is a structural layer derived from the same field state that drives everything else.

The descent chain: nakshatra to graha to raga (via graph traversal), element to Sa frequency (shruti-tuned just intonation), tithi to devi to bija (formant synthesis). Eight sound engines run as threaded kernels: TanpuraEngine (4 strings, additive synthesis, per-graha jivari), SarangiVoice (bowed Sa), bija_synth (formant drone per devi bija), tabla_sampler (7 percussion samples, tala-driven), MixKernel (11-layer relational mix), RhythmKernel (tala/theka/tihai/layakari), SympatheticKernel (13 taraf strings), and VocalKernel (49 phonemes, 12 gamaka types).

The MixKernel computes layer amplitudes from rasa, arc phase, and element --- not from manual mixing. The mix is cosmologically determined.

== Bandhu: Presence Without Oracle

Bandhu is an animated Hanumanji figure --- rendered through the six-layer anatomical stack, animated with toroidal breath (CSS keyframes, 4-second cycle, three torus phases at 120 degree offset) --- whose responses derive from the composition engine rather than a generic language model.

When Bandhu speaks, it classifies the question's intention (one of seven types: viraha, srishti, abhyasa, madhurya, dasya, jyotish, archetype), selects a Narottama das Thakura pada by rasa match and time-of-day, searches the passage corpus for resonant text, selects a Vedic chandas metre by rasa (shringara to Mandakranta, karuna to Anustubh, vira to Sardulvikridita), and composes a response. No LLM is required. The field answers through the tradition.

Bandhu is not an oracle. It is an ambient cosmological presence --- the system's living face, responsive to the moment without pretending to be its source.

#pagebreak()

// ============================================================
// PART III: THE RESEARCH FIELDS
// ============================================================

= Research Fields and Living Datasets

The following ten domains represent Atlas's primary research fronts. Each is both an active dataset and an open question. The datasets grow as primary sources are ingested, relations are confirmed, and practitioners contribute field observations.

== Nakshatra-Plant Correspondences and Morphological Rendering

The 27-nakshatra lunar mansion system is foundational to Jyotihshastra and appears across late Vedic and post-Vedic literature with multiple kinds of associated data: presiding deities (strongest textual attestation, anchored in Taittiriya Samhita 4.4.10), pada syllables (panchanga convention), yoni animal classifications (Ashtakuta matching tradition), and plant associations (nakshatra-vriksha tradition, later and regionally variable but widely maintained).

Atlas's current nakshatra dataset covers all 27 nakshatras with deity, graha lord, element, guna, shakti, body region, gana, dosha, yoni, and pada syllables. The plant layer adds sacred plant, Ayurvedic use, associated mantra, and ritual use. The PFAF botanical database (8,504 plants) provides cross-referenced species profiles enabling ecological deployment of nakshatra-plant knowledge into actual planting calendars.

=== The Astrobotanical Classification Layer

Beyond one-to-one nakshatra assignments, Atlas maintains a cross-traditional astrobotanical classification system organized into five functional classes: Solar-Fire/Agni (plants governed by solar rhythm, phototropic, drying, stimulating --- associated with Surya, Mangal, Ketu grahas), Lunar-Water/Soma (cooling, fluid-accumulating, tidal response --- associated with Chandra, Shukra), Wind-Air/Vayu (nervous system affinity, volatile oils, movement --- associated with Budha, Rahu), Earth-Root/Prithvi (mineral-dense, grounding, structural --- associated with Shani), and Ether-Nervine/Akasha (subtle field sensitivity, consciousness-modulating, often psychoactive within ritual contexts --- associated with Guru).

This classification is a convergence scoring system, not a lookup table. Each plant receives scores across Ayurvedic dosha action, Traditional Chinese Medicine phase affinities, Western herbalism energetics, and biodynamic plant type (root/leaf/flower/fruit-seed) simultaneously. A plant that scores high across all four traditions in the same class is flagged as a high-coherence astrobotanical anchor --- its nakshatra assignment is treated as more reliably attested.

The biodynamic integration runs as follows: nakshatra element maps to biodynamic day type (air → flower day, fire → fruit-seed day, water → leaf day, earth → root day). This is not an approximate analogy --- the element-to-day-type mapping is structurally identical across both systems, and the astrobotany datasets (`datasets/astrobotany/`) confirm this correspondence across 27 nakshatra-biodynamic pairings.

=== Morphological Rendering and the Co-evolutionary Covenant

The plant corpus encodes more than medicinal and ritual properties. Each plant's growth tendency --- reaching, creeping, holding, yielding --- is derivable from the relational properties of its nakshatra assignment: shakti (the nakshatra's force vector), element (the mode of expression), and guna (the quality of its action). A plant associated with a nakshatra whose shakti is "upward force" and element is fire will tend toward vertical, phototropic, architectural growth. A plant associated with a lunar-water nakshatra whose shakti is "flowing" will tend toward vining, submissive, soft form.

This is the doctrine of signatures made computational. The `datasets/morphogenesis/doctrine_of_signatures.csv` (44 plant-form glyph entries mapped to body regions) and `datasets/morphogenesis/body_archetype_map.csv` together enable the plant renderer to generate growth-form glyphs from graph data rather than from stored illustrations.

The inverse traversal is more significant: plant → nakshatra → body region → marma → chakra → skeletal structure. If a sufficient number of plants associated with a given nakshatra are traversed through this chain, their collective body-region mappings reconstruct a recognizable portion of the human anatomy. The plant corpus, in other words, contains a latent image of the human body. The Bandhu figure's six anatomical layers are the most visible expression of this --- but the structural claim is broader: plant morphology and human morphology share a common geometric grammar, derivable from the same relational graph.

This is the co-evolutionary dharmic covenant made visible --- not as a philosophical assertion but as a computational demonstration. The fig and its wasp, illustrated in the frontispiece, have co-evolved for 87 million years in a relationship of mutual morphological constraint. Atlas proposes that this co-evolutionary entanglement is not an exception in nature but the rule --- and that the nakshatra system encodes its geometry.

_Open questions:_ The earliest textual locus for nakshatra-plant assignments remains disputed. Regional variation in nakshatra-vana traditions (Sringeri, Kerala, North Indian) needs systematic documentation. The relationship between nakshatra plants and biodynamic plant categories (root/leaf/flower/fruit days) has been confirmed structurally but not yet validated through field observation.

== Raga Cosmology

The classical Indian music tradition encodes melody as co-structured with cosmic time. The Sangitaratnakara of Sarngadeva provides the earliest fully explicit raga-level cosmological metadata: time of day, season, presiding deity, rasa, and performance context for individual ragas. Later Hindustani and Carnatic traditions stabilized and differentiated these associations, with Carnatic practice generally not observing morning/evening/noon raga categories while Hindustani tradition maintains them strictly.

Atlas holds raga data across three strata: the Sangitaratnakara mappings (deity, rasa, performance context), Hindustani performance practice time assignments, and Gandharva Veda graha-raga correspondences (`datasets/gandharva/graha_raga_chords.csv`). The field state derives the current raga from nakshatra to graha to raga via graph traversal --- a cosmologically grounded, not arbitrarily assigned, sound environment. Therapeutic raga assignments (`datasets/gandharva/raga_therapeutic.csv`) add a clinical dimension: the system distinguishes between the raga indicated by the current field state and the raga therapeutically appropriate for the user's dosha condition.

The Carnatic melakarta system presents a significant open research frontier. The 72 parent scales (melas) are a complete, mathematically derived set of all possible heptatonic scales within just intonation --- a more systematic theoretical foundation than the Hindustani raga classification. Their relationship to nakshatra and graha mapping is underspecified in both classical texts and current Atlas datasets. The `datasets/carnatic/` directory holds tala data (35 tala definitions, gati rules, korvai structures, navagraha kritis) but the raga-cosmology mapping for the melakarta system remains a gap.

_Open questions:_ Carnatic melakarta to nakshatra/graha mapping. The relationship between raga time (prahar) and biodynamic time (leaf/flower/fruit/root quality). Whether the 72 melas map cleanly onto the 72 Laghu-based tala structures.

== Toroidal Geometry and Yantra Emergence

This research field has produced the most unexpected finding in Atlas's development to date.

The Sri Yantra --- primary geometric instrument of the Sri Vidya tradition, consisting of nine interlocked triangles, 43 triangular sub-regions, nested lotus circuits, and a central bindu --- has been computationally demonstrated to emerge as the Chladni nodal interference pattern of 15 equally-spaced plane waves. The wave count corresponds to the 15 Nitya Devis of the Sri Vidya lunar cycle. This is not a metaphor: the S4 instrument (`static/s4.html`) renders this interference field live, and on April 8, 2026 (Kṛṣṇa Saptamī, Pūrvāṣāḍhā nakshatra), the triangular nodal pattern was confirmed at N=3 and documented.

The full finding, with tithi-by-tithi verification and alignment scores, is documented in Appendix F. The key results are summarized here.

=== The 15-Wave Model

Each Nitya Devi contributes one plane wave to the superposition:

`wᵢ(x,y) = cos(k·(x·cos(θᵢ) + y·sin(θᵢ)) + φᵢ)`

where θᵢ = (i−1)·2π/N (equal angular spacing) and k is the spatial frequency tuned to Sri Yantra proportions (k ≈ 12.0 at resonance). The nodal lines of the standing wave product form closed cells whose geometry varies with N: triangular at N=3, hexagonal at N=6, octagonal at N=8, and reaching maximum complexity at N=15.

The tithi cycle is the temporal unfolding of this interference field. As each tithi activates one additional wave source, the nodal pattern evolves through a complete sequence of 2D symmetry groups --- from the seed point of Amāvasyā through the full 15-fold complexity of Pūrṇimā. The progression passes through both crystallographic symmetries (N=3, 4, 6, which can tile the plane) and quasicrystalline symmetries (N=5, 7, 8, 10, 11, 12, 15, which cannot).

=== The Quasicrystal Interpretation

The Sri Yantra is a 15-fold quasicrystal. This claim is precise: it has long-range geometric order without periodicity, non-crystallographic rotational symmetry, nested self-similar structure, and golden-ratio proportions --- the defining properties of a quasicrystal, as established by Shechtman's 1984 discovery (Nobel Prize, Chemistry, 2011). Kulaichev's 1984 demonstration that Sri Yantra construction requires solving a system of simultaneous non-linear equations is exactly what one would expect of a quasicrystalline object: it cannot be assembled by simple periodic repetition.

Of the 15 tithis, only 4 correspond to crystallographic symmetry groups (N=2, 3, 4, 6). The remaining 11 are quasicrystalline. The lunar month spends the majority of its cycle in aperiodic field configurations --- and the tradition prescribes distinct practices for each tithi, including fasting on Ekādaśī (N=11) and the major Sri Vidya ceremony at Pūrṇimā (N=15).

The computational finding bears directly on this: Ekādaśī (N=11) produces 85% Sri Yantra alignment at k=12.0, while Pūrṇimā (N=15) produces 82%. Ekādaśī shows higher Sri Yantra geometric resonance than the full moon. The tradition's prescription of Ekādaśī as the primary day for Sri Yantra practice and meditation has a physical basis in the wave interference model.

=== The Merkaba and the Counter-Rotating Field

The static Sri Yantra is a 2D projection of a 3D structure: the Merkaba (star tetrahedron), formed by two counter-rotating interlocked tetrahedra. In our model, the inner field is driven by the 15-Devi lunar cycle (counter-clockwise, 24° angular intervals), and the outer field by the 9-Graha solar cycle (clockwise, 40° angular intervals). Their product at any given moment is the current Sri Yantra interference pattern.

The critical parameter is the gear ratio: ω_lunar / ω_solar = 365.25 / 29.53 ≈ 12.368. This ratio --- the number of synodic months per solar year --- is the same spatial frequency k that produces maximum Sri Yantra alignment in the Chladni model. The Sri Yantra encodes the lunisolar gear ratio as geometry.

Figures 3 and 4 illustrate the toroidal trajectory model and the counterspace interference structure respectively. The Brahmāṇḍa toroidal engine (`npu_engine/field/kala_engine.py`) implements this model computationally, with the dual-helix live view rendering the current solar/lunar positions as a real-time toroidal trajectory.

An important parallel from fluid dynamics: Viktor Schauberger's observations of counter-rotating water vortices describe the same structural principle from a physical rather than cosmological register. Two fluid spirals rotating in opposite directions produce an implosion vortex at their center whose cross-sectional interference geometry maps to the Sri Yantra. The Vaimānika Śāstra mercury-vortex descriptions, whose historical provenance is disputed, describe geometrically consistent structures. The geometric correspondence is real and documented in the Toroidal Vortex Engine research seed (`atlas_core/docs/research/toroidal_vortex_engine.pdf`); the historical and physical claims are marked SYNTHESIS/EXPERIMENTAL and require separate investigation.

_Open questions:_ Does N=15 produce exact Sri Yantra geometry at a specific k value (implying a precise mathematical theorem)? What are the winding numbers of the individual Devi toroids, and do they correspond to traditional attributes? The 3D Thomson sphere version (15 toroids in minimum-energy configuration) --- does its equatorial cross-section produce the Sri Yantra?

== The Nitya Devi Tithi Registry

The 15 Nitya Devis of the Sri Vidya tradition preside over the 15 tithis of each paksha. Each Devi carries: weapons (ankusha, pasha, sugarcane bow, arrows), mudras, vahana, hue, garments, ornaments, capability signature, and spectral layer assignment. Atlas has conducted systematic primary-source extraction for all 15 --- from Kāmeśvarī (Pratipad) through Chidagni Kalā (Pūrṇimā/Amāvasyā).

The Devi system is not esoteric decoration. It is the primary S1 (archetype) layer that modulates sound, rasa emphasis, reading lens, and Bandhu guidance for each tithi. On Kulasundari's Navami, the system emphasizes lineage transmission. On Jvalamalini's Chaturdashi, purification and dissolution. The bija mantra assigned to each Devi drives the formant synthesis layer of the sound engine.

The computational finding described in the previous section --- that the 15 Devis as wave sources produce the Sri Yantra as their interference pattern --- reframes the entire tradition: the Devis are not 15 separate entities who happen to preside over the lunar calendar. They are 15 wave sources whose superposition produces the primary geometric instrument of their own tradition. The Sri Yantra is not the Devis' symbol. It is their field, made visible.

The symmetry transition tithis deserve particular note. Tithi 6 (Mahāvajreśvarī) produces hexagonal interference --- the geometry of crystals, ice, and honeycomb, the most efficient planar tiling. Her epithet "great lightning goddess" and her association with the vajra (crystalline thunderbolt) are geometrically precise: C6 is the maximum-efficiency crystallographic symmetry. Tithi 7 (Śivadūtī) produces 7-fold interference, which cannot tile the plane --- genuinely aperiodic, churning, transitional. She is the messenger who crosses between structured and unstructured worlds. The geometry encodes the mythology exactly.

_Open questions:_ Full vahana and directional attributes for several Devis are missing from current primary source extractions. The relationship between Nitya Devi capability signatures and therapeutic modalities needs research.

== Vedic and Puranic Cosmology

The Puranic cosmological model --- lokas, dvipas, Mount Meru, the Brahmanda --- provides the vertical and spatial structure within which all other domains locate themselves. Atlas has conducted deep primary-source research into this corpus, extracting entity-relation schemas from the Vishnu Purana, Bhagavata Purana, Brahmanda Purana, Matsya Purana, Rigveda, and Atharvaveda.

The extracted entities include: seven upper lokas (Bhur, Bhuvar, Svar, Mahar, Jana, Tapo, Satya), seven nether worlds (variant naming across traditions), seven dvipas with seven encircling oceans, Mount Meru as axis, the Brahmanda with its successive envelopes, the four-yuga cycle with duration ratios (4:3:2:1), the Kalpa as a day of Brahma, and eight lokapalas as directional governors.

The Gaudiya expansion of this cosmology --- Goloka above Satya-loka, the eternal Vraja forests, the ashtakala --- is partially implemented in `goloka_engine.py` and grounded in the `datasets/cosmology/goloka/` directory (`ashtakala_lila.csv`, `goloka_relations.csv`, `sakhi_seva.csv`, `vraja_topology.csv`). The twelve Vraja forests with geographical coordinates are held in `datasets/cosmology/vraja_forests.csv`.

_Open questions:_ The relationship between Puranic spatial cosmology and the S-layer system needs systematic documentation. Bhagavata Purana passages on plant and sound cosmology are underrepresented in the passage corpus.

== Ayurveda, Plant Properties, and Rasaśāstra

=== Samhita-Era Ayurveda

The Ayurvedic plant corpus draws on primary source extraction from Charaka Samhita, Sushruta Samhita, and Bhavaprakasha Nighantu. Each plant entry carries: botanical name, rasa (taste), guna (quality), virya (potency), vipaka (post-digestive effect), dosha-balancing action, therapeutic uses, and parts used. The key integration is that Ayurvedic plant properties cross-reference with nakshatra plant associations, biodynamic day types (via element mapping), and the PFAF ecological database. A plant is not just a medicinal entity --- it is a node in the nakshatra web, a biodynamic calendar actor, an ecological species with habitat requirements, and a ritual object with deity association.

=== Rasaśāstra and Material Transformation

Rasaśāstra --- the science of mercury, the Ayurvedic branch dealing with mineral and metal therapeutics --- represents a distinct and underrepresented knowledge domain within Atlas. Where Samhita-era Ayurveda is primarily plant-centric, rasaśāstra works primarily with metals, minerals, gems, and their processed forms (bhasma, kajjalī, kupīpakva rasa, parpaṭī).

The substance ontology follows classical classification: rasa (mercury), mahārasa (mica, pyrite, bitumen, tourmaline, and related substances), uparasa (sulfur, haematite, alum, orpiment, realgar), dhātu (the seven pure metals: gold, silver, copper, iron, lead, tin, zinc), upadhātu (slag, red lead oxide), ratna/uparatna (gems and semi-gems), and viṣa/upaviṣa (toxic substances governed by strict processing protocols).

The transformation process spine is: śodhana (purification through sequential quenching in defined media) → bhāvanā (wet trituration, typically with plant juices or decoctions) → māraṇa/bhasmīkaraṇa (incineration/calcination, repeated) → puṭa (one heat cycle; the unit of thermal processing). Each step is governed by quality-control criteria (parīkṣā tests) that function as computational stop-conditions: the preparation is not advanced until tests pass.

The plant-metal entanglement embedded in this process is significant for Atlas's S5 ecology layer. Lauha (iron) bhasma preparation, for example, requires sequential quenching in sesame oil, buttermilk, cow urine, sour gruel, Dolichos biflorus decoction, and Triphalā decoction, followed by trituration with Aloe pulp before incineration. The plant decoctions used as śodhana and bhāvanā media are themselves nakshatra-indexed entities in the graph --- which means the bhasma preparation pipeline is not a chemistry process floating above the ecology layer but a deeply embedded plant-metal relational event. Specific plants are prescribed for specific metals; the prescription encodes the same relational logic as the nakshatra-plant system.

The distinction between what is safe to operationalize and what must remain research-only is enforced at the dataset level. The Ayurvedic Pharmacopoeia of India (API) heavy metal limits, FDA adverse event signals, and peer-reviewed prevalence findings (JAMA) are held in a safety governance sublayer. Classical claims are conditional: they depend explicitly on correct śodhana and māraṇa, and on appropriate professional prescribing. Atlas never presents rasaśāstra therapeutics as operational recommendations --- they are research-layer content, available for scholarly navigation but not surfaced as prescriptions.

_Open questions:_ Systematic mapping of Ayurvedic plants to biodynamic preparations (BD500-BD508). Regional endemic species not covered by PFAF. Structured extraction of API Part-I Vol-VII (21 mineral/metal monographs) and API Part-II formulation graphs into the knowledge schema.

== Graha-Metal-Gem Correspondences

Classical jyotish assigns each graha a corresponding metal and gem: gold to Surya, silver to Chandra, copper to Shukra, iron to Shani, tin to Guru, mercury/mixed to Budha. These assignments appear in BPHS remedial measures chapters, Brihat Samhita gemological sections, and living jyotish prescription practice. Atlas holds the gem dataset in `datasets/ratna/graha_gems.csv`.

A research programme initiated within Atlas asks whether the BPHS graha friendship/enmity table --- derived from mūlatrikoṇa-based house-lord logic --- finds analogical support in the physical chemistry of the corresponding binary metal systems. The question is framed as testable: "friendship" as a hypothesis predicts miscibility, stability, and ease of mixing; "enmity" predicts phase separation, miscibility gaps, or strong non-ideality.

The two strongest analogical matches are: Au-Ag (Sun-Moon, mutual friends in BPHS) --- a textbook complete solid solution, totally miscible across all compositions, the archetypal "compatible" noble alloy; and Au-Fe (Sun-Saturn, mutual enemies) --- a system with documented positive deviation from ideality, a solid-state miscibility gap, and strong phase-separation tendencies. If friendship means "stable homogeneous mixture" and enmity means "tendency to segregate," these two pairs support the hypothesis strikingly.

The complex cases are instructive. Au-Cu (Sun-Venus, mutual enemies in BPHS) is not simply incompatible --- it forms stable ordered superstructures (AuCu, AuCu₃) at specific temperature-composition combinations, with large property changes at order-disorder transitions. This could be read as "difficult relationship with strong interaction" rather than simple repulsion. The asymmetric cases in BPHS --- Moon-Mercury (Moon calls Mercury friend; Mercury calls Moon enemy) and Jupiter-Mercury (Jupiter calls Mercury enemy; Mercury calls Jupiter neutral) --- find physical analogs in the directional nature of amalgamation (mercury penetrates silver alloy particles, not the reverse) and the strong solubility asymmetry of Ag-Zn (much more Zn dissolves in Ag than Ag in Zn).

The ternary Au-Ag-Cu system has additional significance: it is the material basis of panchaloha and ashtadhatu sacred alloy traditions, and its phase behavior (spinodal decomposition, ordering, grain-boundary precipitation) produces composition-dependent microstructures that do not vary smoothly with ratio. Small shifts in Au/Cu/Ag proportion can move an alloy between ordering-controlled and phase-separation-controlled aging paths. This is the "nonlinear behavior at specific ratios" that the sacred alloy traditions may have been empirically encoding.

One important methodological caution: the archetypal Sun-Moon gem pair (ruby + pearl) is mechanically incompatible in direct contact --- corundum (Mohs 9) will scratch pearl (Mohs 2.5). The analogy between planetary friendship and material compatibility is not global, and the paper makes no claim that it is. It is a research question, not a conclusion.

_Open questions:_ The Carnatic navagraha kritis dataset (`datasets/carnatic/navagraha_kritis.csv`) encodes graha-raga relationships in a different register from the metals work. Whether the raga-graha and metal-graha correspondence systems share underlying structural logic is unexplored.

== Svarodaya: Breath, Time, and the Nadi Calendar

Svarodaya --- the science of breath-cycle timing --- is one of the most practically applicable Vedic temporal systems and one of the least represented in computational tools. The Shiva Svarodaya describes how the dominant nadi (Ida, Pingala, or Sushumna) shifts in a predictable cycle governed by vara (weekday), tithi (lunar day), and masa (month). Activities have prescribed nadi states: Ida (lunar, cool, left nostril dominant) for receptive, watery, nighttime activities; Pingala (solar, active, right nostril) for decisive, fiery, movement activities; Sushumna (balanced, central) for meditation and transition.

Atlas computes swara nadi on every request via `compute_swara()`, deriving the current dominant nadi from vara and tithi rules encoded in `datasets/svarodaya/vara_rules.csv` and `datasets/svarodaya/tithi_rules.csv`. The activity matrix (`datasets/svarodaya/activity_matrix.csv`) scores 24 activity types against the current nadi state. The coherence rules (`datasets/svarodaya/coherence_rules.csv`) govern how the nadi state interacts with the muhurta scoring --- a good muhurta in a contradictory nadi state is downgraded.

This makes Svarodaya a real-time intention-scoring layer that sits above the panchanga calendar. The muhurta engine already computes auspicious timing; the svara engine adds a physiological/pranic dimension that the classical texts treat as equally important for practical timing.

_Open questions:_ The elements dataset (`datasets/svarodaya/elements.csv`) holds the panchamahabhuta-nadi relationships used in Svarodaya for elemental phase diagnosis. This is not yet integrated into the plant engine, but the element-to-activity prescriptions in Svarodaya overlap significantly with Ayurvedic dinacharya recommendations. Systematic cross-validation between the two systems is a natural next step.

== Vedic Ritual and Sacred Timing

The Vedic ritual corpus --- Agnihotra, Somayajna, Ashvamedha, Darsha-Purnamasa, Chaturmasya, Agnishtoma --- provides the earliest systematic framework for cosmologically-timed action. Atlas has extracted timing, offerings, associated deities, and purposes from Shrauta Sutras, Grihya Sutras, Shatapatha Brahmana, and Rig Veda sources.

The practical integration: muhurta computation scores 24 jyotish-sourced intentions against the current field state, ranking the auspiciousness of different actions --- study, planting, beginning a journey, making an offering. This is Vedic ritual timing operationalized as a live scheduling system.

The dinacharya layer (`datasets/ayurveda/dinacharya_panchanga.csv`) extends this into daily practice: Ayurvedic daily regimen timing is mapped against panchanga data, so that the recommended time for oil pulling, pranayama, meditation, or asana is scored against the current muhurta and nadi state. Practice becomes cosmologically situated rather than abstractly scheduled.

_Open questions:_ The Grihya Sutra (household ritual) corpus is underrepresented. Relationship between muhurta quality and biodynamic day quality. Soma-related plant correspondences.

== The Gaudiya Vaishnava Knowledge Frame

Atlas was built from within the Gaudiya Vaishnava tradition. The system's tradition weights, Bandhu's pada corpus (Narottama das Thakura), the Goloka layer (S0), and the ashtakala mapping all reflect this frame. The GSS epistemological architecture is itself drawn from Vaishnava epistemology.

This does not mean Atlas is closed to other traditions. The authority axis is designed to preserve sectarian integrity without imposing it: a Shaiva interpretation of a deity relation can coexist with a Vaishnava interpretation as separate overlay nodes, both marked with their tradition and authority level. Interpretive plurality is preserved as structure rather than suppressed as noise. The I Ching cross-referencing datasets (`datasets/iching/`) --- hexagram-nakshatra, hexagram-devi, hexagram-raga resonance tables --- are an example of this: they are held at SYNTHESIS authority level, available for research without claiming equivalence with the Vedic primary layer.

The sources corpus for this domain is extensive: Bhagavad Gita (complete, verse-indexed JSON), Srimad Bhagavatam (multiple cantos, JSONL chunks), Brahma Samhita, Bhakti Rasamrita Sindhu, Brihad Bhagavatamrita, Hari Bhakti Vilasa, Vedanta Sutra, Sikshashtakam, and the Narottama das Thakura pada corpus. This constitutes the most thoroughly digitized single-tradition corpus in the current system.

_Open questions:_ Systematic documentation of the relationship between Vraja geography (12 forests) and terrestrial sacred geography (Shakti Pithas, river confluences). Bhagavata Purana passages on plant and sound cosmology are underrepresented in the passage corpus.

#pagebreak()

// ============================================================
// PART IV: THE FEDERATED VISION
// ============================================================

= The Federated Vision

The architecture described in Part II is a single node. What follows describes what a network of such nodes could become --- and the protocols needed to make that network trustworthy.

== Traditional Knowledge Sovereignty

The open source movement was built around code. Its norms of attribution, licensing, and contribution assume that the primary artifact is a software function --- something that can be forked, modified, and redistributed without the act of copying constituting an appropriation of a living culture's inheritance.

Traditional knowledge is different. A nakshatra-plant association attested in the Taittiriya Samhita belongs to a textual tradition with custodians, commentators, and living practitioners who have sustained it across millennia. An Ayurvedic formulation carries the authority of a sampradaya. A Nitya Devi dhyana description draws from a lineage of initiates. These are not data points to be scraped and redistributed --- they are relational objects with provenance, authority, and obligation.

Atlas proposes a cryptographic provenance model for traditional knowledge: every entity and relation in the graph carries an immutable attestation record --- source text, lineage, authority level, and contribution chain. When a dataset is derived from a particular tradition's custodians, that custodianship is encoded in the graph structure, not just noted in a README. Attribution chains can be verified. Derivative works carry their lineage forward. The distinction between open computation (algorithms are freely shared) and open knowledge (traditional knowledge has custodians) is preserved architecturally.

This is not a restriction on research. It is an architecture for respect.

== The Seva Economy: Auspicious Microtransactions

The seva economy model proposes that resource exchange within this network be structured as offering rather than payment. In the Vedic model, the appropriate response to receiving knowledge or service is a return offering --- one that acknowledges the source, reflects the receiver's capacity, and maintains the relational circuit.

This translates concretely into an SSO exchange framework in which muhurta computation scores the auspiciousness of exchange moments, contribution flows are tracked relationally (who contributed what to which part of the knowledge graph), and local resource networks (seeds, plants, land access, labor, knowledge) can be exchanged through the same system as digital contributions.

The mandala-to-planting pipeline is the clearest example: a practitioner's field queries the vastu zone engine, the nakshatra agriculture calendar, and the local plant database to receive a planting schedule. They contribute field observations back --- which plant species were found, what grew, what failed --- enriching the dataset. That contribution, timestamped to its cosmological moment, becomes a sadhu-layer annotation on the graph. The offering completes the circuit.

The rasaśāstra sublayer adds a further dimension to this exchange model: plants used as śodhana media in bhasma preparation carry specific nakshatra and muhurta prescriptions for their harvest. A practitioner who contributes field observations about the growth timing and efficacy of these plants is contributing not just to the botany dataset but to the Ayurvedic transformation pipeline --- linking the planting calendar directly to the preparation chain.

== Mandala to Planting Pipeline

The full pipeline from cosmological field state to land action:

```
field_state()
  -> tithi, nakshatra, vara, element, devi, svara_nadi
  -> muhurta_score(intention="planting")
  -> svara_check(activity="planting")
  -> nakshatra_plant_map(nakshatra, element, dosha)
  -> astrobotanical_class_score(plant, traditions=[])
  -> vastu_zone_prescriptions(lat, lon, radius)
  -> guild_relations(primary_plant)
  -> biodynamic_day_type(element -> C1/C2/C3/C4)
  -> local_species_filter(pfaf, ecoregion)
  -> planting_calendar(30-day window)
```

Each step is a genuine relational query. The biodynamic day type is derived from the nakshatra element. The vastu zone prescriptions follow directional cosmology. The guild relations identify companion plants whose nakshatra affinities reinforce each other. The svara check adds the breath-cycle layer: planting is a Pingala-nadi activity, and a good muhurta in an Ida-dominant window may be deprioritized accordingly.

The result is a planting calendar that a biodynamic farmer, a permaculture designer, and a Vedic practitioner can each read differently --- but which derives from a single coherent system.

== Atlas as Federation Node

A federation of Atlas nodes would look like this: each node (a van, a farm, a hackerspace, a gurukula, an academic research station) runs its own local-first Atlas instance. Nodes share a common canonical ontology --- the stable shastra layer --- providing interoperability without imposing uniformity. Each node maintains its own sadhu overlay layer, reflecting local tradition, local species, local practitioners. Guru-layer synthesis is shared as proposals, never as canon.

The federation protocol rests on three principles: canonical portability (the stable ontology moves between nodes without data loss), sadhu sovereignty (each node owns its overlay layer), and guru transparency (AI inference is always marked and never self-promoting).

In five years, a network of federated Atlas nodes could constitute something unprecedented: a distributed, practitioner-maintained, cosmologically grounded knowledge infrastructure for traditional sciences --- not controlled by any single institution, not extractable by any single platform, but collectively more coherent than any of its parts.

== Coherence Spectrum: The Civilizational Simulation

Atlas is the technical substrate for three interconnected projects sharing the same cosmological ontology.

_Coherence Spectrum_ is a persistent procedural civilization simulator. Vedic frameworks --- Panchanga, Tridosha, Guna, Varna, Jyotisha --- function as gameplay mechanics. The coherence spectrum runs from 0% (Kali Band: industrial compression, ecological collapse) to 100% (Satya Band: ecological self-regulation, cosmological alignment). Dosha-based morphogenesis generates creature forms: Vata produces aerial forms, Kapha aquatic and armored, Pitta heat-resistant. The game dataset (`datasets/game/`) holds chimera type definitions, lineage structures, and the sura-asura polarity map.

_Emergent Satya Yuga_ is the worldbuilding and story framework. Late Kali Yuga collapse to Devi Field stabilization to Satya Yuga emergence. NPUs (Narrative Processing Units) use Sanskrit grammar logic as the computational model for meaning-based processing.

_The Devi Field_ is the novel. Characters: Dr. Anika Rao (soil harmonics), Eli Mercer (NPU researcher, Geneva), Maya Alvarez (Appalachian rewilded zone child). The Devi Field stabilizes not through apocalypse but through entrainment --- ecology, AI coherence, and animal relational cognition coming into alignment.

The game simulates the process. The novel narrates it. Atlas measures it. All three share the same underlying ontology: coherence is relational density, fragmentation is loss of relations, and the Satya Yuga is the state where the graph is maximally coherent.

#pagebreak()

// ============================================================
// PART V: THE INVITATION
// ============================================================

= The Invitation

Atlas is not a finished system. It is a working substrate with significant gaps, a clear architectural direction, and an urgent need for collaborators who bring depth in domains that a single practitioner-developer cannot cover alone.

== For Computational Jyotish Communities

VedAstro, PyJHora, Maitreya, and Saravali users and contributors: Atlas has what you don't, and you have what Atlas needs.

What Atlas offers: a live relational graph in which nakshatra position is not just a chart datum but a node connected to plant, sound, deity, marma, vastu zone, raga, and passage --- all simultaneously queryable. A field state that drives not just chart display but ecological and sonic environment. A federation architecture that could host chart data as natal overlay nodes on a shared cosmological substrate.

What Atlas needs: rigorous cross-validation of kala engine calculations against established jyotish software. Dasha computation testing. Ayanamsa calibration. Your experience with edge cases, historical charts, and computational precision would strengthen the system's epistemological backbone.

_Specific ask:_ Run the `/field` endpoint output against your preferred jyotish software for a month of dates and document discrepancies. If your system has an API, let's explore interoperability.

== For Sanskrit and Digital Humanities Scholars

GRETIL contributors, Vedavaapi developers, and WSC Computational Sanskrit researchers: the 26,000-chunk JSONL passage corpus in Atlas is already structured for annotation. The graph is designed for federation.

What Atlas offers: a living system in which your annotations are contextualized. Every passage is a node connected to entities, traditions, and cosmological coordinates. When you annotate a Puranic cosmology passage, Atlas can immediately show you what else in the graph it connects to, which passages share its entities, and what the current field state suggests about its emphasis.

What Atlas needs: systematic passage corpus expansion, especially in Ayurveda (only 10-12 major granthas currently in machine-readable form), Gandharva Veda, Grihya Sutras, and Gaudiya Vaishnava literature beyond the Narottama corpus. NLP tools for Sanskrit compound analysis would substantially improve entity extraction. Collaboration with Vedavaapi on federation protocol design.

_Specific ask:_ Review the current passage corpus schema. Identify which primary sources should be prioritized. If you have annotated datasets that could contribute to the graph, let's discuss attestation alignment.

== For Biodynamic and Permaculture Practitioners

The nakshatra-grounded observation framework in Atlas is something the biodynamic tradition has been practicing qualitatively for decades without a computational substrate. The Thun calendar maps planting types to moon signs; Atlas maps them to nakshatras, adds the graha lord, element, guna, and deity, adds the svara nadi layer, and scores plant resonance across four traditions simultaneously.

What Atlas offers: a computational framework that can take your field observations --- what grew when, under which nakshatra, with what results --- and integrate them as sadhu-layer annotations on the graph. A planting calendar derived from cosmological principles. A vastu zone engine that can guide garden layout from directional cosmology.

What Atlas needs: field validation. The nakshatra-plant correspondences need practitioners who are actually planting by these principles and recording results. Local species datasets. The astrobotany datasets are thin and need depth from people who are observing.

_Specific ask:_ Run the `/bhumi/agriculture` app for one planting season and keep field notes. Share your observations as dataset contributions.

== For Gaudiya Vaishnava Communities

This system was built from within the sampradaya. Bandhu is Hanumanji. The composition engine speaks in Narottama padas. The Goloka layer maps the eternal ashtakala onto material time. The system's deepest motivation is to make the devotional cosmology computationally navigable --- not to explain it to outsiders but to serve practitioners who already live within it.

What Atlas needs: theological review of the knowledge frame, especially the relationship between the shastra layer and the sadhu overlay structure. Pada corpus expansion beyond Narottama. Validation of the Vraja forest mappings. Community-based field observations from practitioners who can identify when the system's cosmological scoring is producing resonant versus discordant suggestions.

_Specific ask:_ Read the Goloka layer documentation and Bandhu composition engine. Tell us what the tradition requires that the system is not yet providing.

== For Hackerspaces and Open Hardware Builders

The van-mounted NUC running a cosmological field computer is a genuinely interesting hardware story. Under \$300 of hardware, running local-first, offline-capable, NPU-accelerated, with audio output through a MOTU M2. This is a replicable pattern.

What Atlas offers: a complete reference implementation of a local-first traditional knowledge system. The deployment pattern (Flask on NUC, PipeWire audio, ngrok for remote access, systemd for service management) is documented and reproducible. The architecture is explicitly designed for replication --- each instance can be a federation node.

What Atlas needs: replication. The system needs to be deployed in different contexts --- a farm, a hackerspace, a university research station, a community center --- to surface the assumptions that are currently invisible because there is only one instance. Hardware variations. Mesh networking experiments.

_Specific ask:_ Replicate the deployment. Document what breaks. Propose a federation protocol for node discovery and graph synchronization.

== How to Connect

The system is running at `localhost:5000` on kanjira. The `/field` endpoint requires no authentication and will tell you exactly what cosmological moment you are reading this in.

The offering cycle is the onboarding protocol:

```
impetus          -> what brought you here
cosmic context   -> what field state are you arriving in
offering plate   -> what you are bringing
seed             -> how it connects to what already exists
research lattice -> what questions it opens
construction     -> software, wiki, dataset, visualization
git push         -> committing to the record
next cycle       -> the impetus that emerges
```

If you are reading this document, you have already completed the first step.

#pagebreak()

// ============================================================
// APPENDICES
// ============================================================

= Appendix A: Current System State

_As of April 2026._ An honest snapshot.

_Working:_ 217 routes in `kernel.py`. 27 engines verified import OK, zero failures. 163 Python files in `npu_engine/` across 15 subdirectories. 110 CSV files across 33 knowledge domains (1,043 files total across 52 dataset directories). 7,208 entities, 8,466 relational edges. 26,000-chunk JSONL passage corpus with vector search. `/field` endpoint returning complete panchanga + sound + plant + devi + marma + dasha + natal data on every request. Agriculture PWA (offline-capable). Talachakra Studio (full tabla synthesis, MIDI output, panchanga integration). LeelaMaps (63 Shakti Pithas, 34 global sacred sites, 8 toggle layers). Lila Streams (land design tool). Bandhu figure (6 rendering layers). Ring engine (10 ring types). 219 wiki pages. All six domain routes returning 200. S4 instrument (Sri Yantra Chladni renderer, live). Svarodaya engine (swara nadi, activity scoring).

_Not yet working:_ Vocal SynthDef (1,154 lines written, no audio output path). SuperCollider to MOTU audio (blocked on PipeWire 1.2.6 JACK shim). 4D projection (exists in code, not exposed). Deha app (Bandhu placeholder only). Seeds pipeline (4 briefs exist, not feeding into graph). Journal UI (backend routes exist, no HTML interface). Editor (Quill specced, not built). Systemd services (scripts ready, not installed).

_Known dataset gaps:_ Ayurvedic grantha coverage (30+ major texts not yet in corpus). Grihya Sutra ritual calendar. Carnatic melakarta-to-nakshatra mapping. Vraja forest geographical coordinates. Regional endemic species beyond PFAF coverage. API mineral/metal monographs (structured extraction pending). Rasaśāstra primary texts (Rasaratna Samuccaya, Rasatarangini).

= Appendix B: Dataset Schema Summary

Core schema fields:

_Entity nodes:_ `entity_id | entity_type | name | name_key | stability | authority | s_layer | theta | phi | element | guna | dosha`

_Relation edges:_ `subject | predicate | object | source | confidence | stability | authority | attestation`

_Passage nodes:_ `chunk_id | source_text | tradition | entity_refs | domain | authority | passage_text`

The dataset layer spans 52 directories and 1,043 files. Primary domain groups: astro (14 files), astrobotany (4), ayurveda (17), carnatic (7), chandas (2), compositions (4), cosmology (16 + goloka/), entities (10 + reference/), gandharva (5), geography (4), iching (8), jyotish (3 YAML), marma (2), morphogenesis (2), ontology (7), permaculture (1), plants (11), ratna (1), relations (26), ritual (3), silpa (1), sound (2), sources (corpus hierarchy, ~800 JSONL/txt files), species (5), svarodaya (6), symbols (6), system (5), tantra (1), tarot (3), vastu (10), yoga (5).

= Appendix C: The Offering Cycle

The development rhythm that structures Atlas work:

```
impetus          -- what is drawing attention right now
cosmic context   -- what field state is this arising in
offering plate   -- what tasks and research directions are proposed
seed             -- how this connects to existing graph structure
research lattice -- what questions this opens
construction     -- software, wiki pages, datasets, visualizations
README expansion -- documenting what was built
git push         -- committing to the record
next cycle       -- the impetus that emerges from the work
```

= Appendix D: Glossary

_Nakshatra_ --- one of 27 lunar mansions; primary field coordinate driving plant scoring, raga selection, and devi mapping. _Tithi_ --- lunar day (angular distance Sun-Moon divided by 12 degrees); maps to Nitya Devi and modulates rasa emphasis. _Graha_ --- planetary body; mediates between nakshatra and downstream domains (raga, gem, mantra). _Panchanga_ --- five-limbed almanac (tithi, nakshatra, vara, yoga, karana); the computational root of `field_state()`. _Muhurta_ --- auspicious time window; scored by `intention_engine.py` for 24 types of action. _Dasha_ --- planetary period system; provides biographical temporal context. _Vastu_ --- sacred spatial science; nine directional domains mapped to plant, deity, and structural prescriptions. _Mandala_ --- geometric sacred diagram; the 3x3 vastu shell organizing the interface. _Yantra_ --- geometric compression of cosmological relations; generated from field state. _Raga_ --- melodic form with cosmological, temporal, and affective coordinates; derived from nakshatra, not arbitrarily assigned. _Bija_ --- seed syllable; synthesized as formant drone from devi data. _Sampradaya_ --- lineage of transmission; preserved as authority provenance in the graph. _Seva_ --- selfless service as offering; the model for contribution exchange in the federation economy. _Shastra_ --- authoritative text; the highest authority level in the GSS epistemic architecture. _Sadhu_ --- practitioner of spiritual discipline; the living-tradition authority layer. _Guru_ --- teacher, dispeller of darkness; the synthetic/AI inference layer, always marked and never self-promoting. _Svarodaya_ --- science of breath-cycle timing; the nadi-activity layer above the panchanga calendar. _Bhasma_ --- calcined ash preparation in rasaśāstra; metal or mineral transformed through repeated incineration cycles. _Quasicrystal_ --- ordered aperiodic structure with non-crystallographic rotational symmetry; the mathematical category to which the Sri Yantra belongs.

= Appendix E: Primary Sources and Lineages

_Jyotish:_ Brihat Parashara Hora Shastra, Jaimini Upadesha Sutras, Brihat Samhita (Varahamihira), Brihat Jataka (Varahamihira), Saravali (Kalyana Varma), Uttara Kalamritam (Kalidas), Surya Siddhanta. Computational implementation via Swiss Ephemeris.

_Cosmology:_ Rigveda (esp. 10.121, 1.25, 10.14), Atharvaveda (esp. 10.7 Skambha hymn), Vishnu Purana (H.H. Wilson trans.), Bhagavata Purana (esp. 3.11.18-19 for yuga cycles), Brahmanda Purana, Matsya Purana (ch. 273 for yuga duration).

_Music:_ Natya Shastra (Bharata, Manomohan Ghosh trans.), Sangitaratnakara (Sarngadeva), Brihaddeshi (Matanga), Raga Guide (Joep Bor et al. for Hindustani performance practice).

_Ayurveda and Rasaśāstra:_ Charaka Samhita, Sushruta Samhita, Bhavaprakasha Nighantu. Rasaratna Samuccaya, Rasatarangini (pending corpus ingestion). Ayurvedic Pharmacopoeia of India Part-I Vol-VII (minerals and metals), Part-II (formulations). Botanical cross-reference: PFAF database (8,504 species).

_Nakshatra traditions:_ Taittiriya Samhita (Black Yajurveda) for deity assignments (Keith trans.); panchanga literature for pada syllables; Ashtakuta matching tradition for yoni classifications; nakshatra-vriksha compiled lists for plant associations.

_Sri Vidya:_ Tantraraja Tantra (Nitya Devi dhyana descriptions and 15-fold structure). Varivasya Rahasya. Nityasodasikarnava.

_Gaudiya Vaishnava:_ Bhagavad Gita, Srimad Bhagavatam, Brahma Samhita, Bhakti Rasamrita Sindhu, Brihad Bhagavatamrita, Hari Bhakti Vilasa, Vedanta Sutra, Narottama das Thakura (pada corpus, primary Bandhu source), Vishvanatha Chakravarti Thakura, Bhaktivinoda Thakura.

_Ritual:_ Shrauta Sutras, Grihya Sutras, Shatapatha Brahmana.

_Svarodaya:_ Shiva Svarodaya.

_Vastu and Silpa:_ Manasara, Brihat Samhita (Varahamihira), Shilpa Shastra (Uttama Dasatala proportions).

= Appendix F: Sri Yantra Chladni Findings

_Instrument:_ Atlas S4 (`static/s4.html`), Canvas 2D JavaScript renderer.
_Date of primary verification:_ April 8, 2026, Kṛṣṇa Saptamī, Pūrvāṣāḍhā nakshatra (Śivadūtī tithi).
_Spatial frequency at resonance:_ k ≈ 12.0.

#table(
  columns: (auto, auto, auto, auto, auto),
  inset: 6pt,
  stroke: 0.4pt,
  align: left,
  [*Tithi*], [*Devi*], [*N*], [*Symmetry*], [*Alignment / Finding*],
  [3], [Nityaklinā], [3], [C₃ crystallographic], [Triangular nodal cells confirmed. Trikoṇa emergent. ✓],
  [6], [Mahāvajreśvarī], [6], [C₆ crystallographic], [Hexagonal honeycomb confirmed. ✓],
  [7], [Śivadūtī], [7], [C₇ quasicrystalline], [Irrational aperiodic field. Still bindu, churning periphery. ✓],
  [8], [Tvaritā], [8], [C₈ quasicrystalline], [Octagonal cells confirmed. ✓],
  [11], [Nīlapatākā], [11], [C₁₁ quasicrystalline], [85% Sri Yantra alignment at k=12.0. Maximum alignment. ✓],
  [15], [Chidagni Kalā], [15], [C₁₅ quasicrystalline], [82% Sri Yantra alignment at k=12.0. Full bloom. ✓],
)

Key finding: Ekādaśī (tithi 11) produces higher Sri Yantra geometric alignment than Pūrṇimā (tithi 15) at the same spatial frequency. The tradition's prescription of Ekādaśī as the primary Sri Yantra practice day is computationally supported.

Of the 15 tithis in the waxing cycle: 4 correspond to crystallographic symmetry groups (N=2, 3, 4, 6), 11 to quasicrystalline symmetry groups. The lunar month spends the majority of its duration in aperiodic field configurations.
