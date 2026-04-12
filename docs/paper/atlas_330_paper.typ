// ============================================================
// ATLAS 330: A COSMOLOGICAL FIELD COMPUTER
// Founding Document & Open Invitation
// ============================================================
// Typst source — compile with: python -c "import typst; typst.Compiler('atlas_330_paper.typ').compile('atlas_330_paper.pdf')"
// Or install typst CLI: https://typst.app

#set document(
  title: "Atlas 330: A Cosmological Field Computer",
  author: "inahd",
)

#set page(
  paper: "us-letter",
  margin: (top: 1.2in, bottom: 1.1in, left: 1.15in, right: 1.15in),
  numbering: "1",
  number-align: center,
)

#set text(
  font: "Linux Libertine",
  size: 11pt,
  lang: "en",
)

#set par(
  justify: true,
  leading: 0.72em,
  spacing: 1.2em,
)

#set heading(numbering: "1.1")

#show heading.where(level: 1): it => {
  v(1.8em)
  text(size: 14pt, weight: "bold", it)
  v(0.5em)
}

#show heading.where(level: 2): it => {
  v(1.2em)
  text(size: 12pt, weight: "semibold", it)
  v(0.3em)
}

#show heading.where(level: 3): it => {
  v(0.8em)
  text(size: 11pt, weight: "semibold", style: "italic", it)
  v(0.2em)
}

// ── TITLE PAGE ──────────────────────────────────────────────

#align(center)[
  #v(2.5in)

  #text(size: 22pt, weight: "bold")[Atlas 330]

  #v(0.4em)
  #text(size: 14pt, style: "italic")[A Cosmological Field Computer]

  #v(1.2em)
  #line(length: 3.2in, stroke: 0.5pt)
  #v(1.2em)

  #text(size: 11pt)[
    A founding document, architectural map, and open invitation \
    to researchers, practitioners, and builders working at the \
    intersection of Vedic sciences and living technology.
  ]

  #v(1.8em)
  #text(size: 10pt, style: "italic")[
    Version 0.1 — April 2026
  ]

  #v(0.6em)
  #text(size: 10pt)[
    atlas330.local · kanjira · Gainesville, Florida
  ]
]

#pagebreak()

// ── ABSTRACT / INVOCATION ───────────────────────────────────

#align(center)[#text(size: 12pt, weight: "semibold")[Invocation]]

#v(0.5em)

// TODO: Write 3–4 paragraph opening — part dharmic invocation,
// part problem statement. Tone: neither academic nor promotional.
// Should feel like the opening of a founding charter.
// Key beats:
//   - The knowledge exists. The tools exist. The integration does not.
//   - What it means to *run* a knowledge system vs. store one.
//   - Atlas as a living substrate, not a lookup tool.
//   - The invitation framing: this document is the offering.

_[Invocation to be written here.]_

#pagebreak()

// ── TABLE OF CONTENTS ───────────────────────────────────────

#outline(
  title: "Contents",
  indent: 1.5em,
)

#pagebreak()

// ============================================================
// PART I — THE GAP
// ============================================================

= The Gap

// One tight section. Name what exists, name what's missing.
// Not a literature review — a field observation.

== What Has Been Built

// Paragraph on: GRETIL, VedAstro, PyJHora, Vedavaapi, Sanskrit DH,
// biodynamic orgs, permaculture commons. Each doing one thing well.
// Acknowledge the depth and seriousness of these efforts.

_[Survey of existing open initiatives — to be written.]_

== What Has Not Been Built

// The missing piece: a living substrate that *runs* the knowledge
// as a coherent field rather than storing or computing it in isolation.
// The distinction between:
//   - a chart calculator (computes jyotish)
//   - a text corpus (stores shastra)
//   - a field computer (runs the relations between all of it, live)
// One or two paragraphs. Sharp.

_[The gap statement — to be written.]_

== Why Now

// Local hardware (NUC-class), local LLMs, NPU acceleration, PWA
// offline capability, open ephemeris (Swiss Ephemeris), open corpora
// — all the ingredients exist. The integration gap is architectural
// and philosophical, not technical.

_[Why the moment is right — to be written.]_

#pagebreak()

// ============================================================
// PART II — THE ARCHITECTURE
// ============================================================

= The Architecture of Atlas 330

// This is the heart of the document. Not a features list.
// A system map that shows how the domains cohere.
// Reader should finish this section understanding:
//   - Why the seven-mandala structure is not arbitrary
//   - How the graph is the connective tissue between all domains
//   - Why local-first matters for this kind of knowledge
//   - How the field state (tithi × nakshatra) drives everything

== The Epistemological Spine: Guru · Sadhu · Shastra

// The GSS model as the epistemological architecture.
// Shastra = canonical datasets + textual passages (the kernel)
// Sadhu = overlays, annotations, practitioner interpretation
// Guru = AI-assisted synthesis and inference (never overrides canon)
// Resonance over accumulation.
// The three axes: stability / authority / visualization permission.

_[GSS model description — to be written.]_

== The Seven-Maṇḍala Structure

// The seven domains as concentric cosmological zones:
// Jyoti · Bhūmi · Kāla · Nāda · Deha · Vāstu · Nitya
// Each domain as a Flask route cluster.
// Vāk / Codex / Bandhu as connective thread.
// Include a diagram placeholder here (Typst box or SVG embed later).

_[Seven-mandala description — to be written.]_

#figure(
  rect(width: 3.5in, height: 3.5in, stroke: 0.5pt)[
    #align(center + horizon)[
      _[Seven-mandala diagram — to be placed here]_
    ]
  ],
  caption: [The seven-maṇḍala structure of Atlas 330 domains.]
)

== The NPU Relational Graph

// The knowledge graph as the connective tissue.
// Entity types: nakshatra, graha, deity, plant, place, text, rasa, dosha...
// Relation grammar: subject | predicate | object | source | confidence | stability | authority
// ~7200 entities, ~8500 edges (current state)
// Tradition weights favoring Gaudiya Vaishnava framework
// Three-axis metadata: stability / authority / visualization permission
// How relations are promoted from experimental → working → stable

_[Graph architecture description — to be written.]_

== The Field State: Tithi × Nakshatra as Computational Root

// kernel.field_state() as the spine — everything derives from it.
// Tithi = angular relation between Sun and Moon
// Nakshatra = lunar mansion of the moment
// How this pulls in: devi, raga, bpm, geometry, muhurta, dasha
// The toroidal model: torus tube = solar year, φ = solar position, θ = tithi
// Field state as a live relational snapshot, not a static lookup

_[Field state architecture — to be written.]_

== Domain Layers

=== Kāla — Cosmological Time
// Jyotish computation, panchanga, tithi, nakshatra, dasha, muhurta
// Live calendar apps, kala-wheel, biodynamic integration
// Data: nakshatra_master, graha_master, tithi_core, nakshatra_padas

_[Kāla domain — to be written.]_

=== Bhūmi — Ecological Ground
// Biodynamic agriculture, astrobotany, ethnobotany, ecoregions
// Nakshatra-grounded biological observation framework
// Sacred water geography, mound cosmology
// Data: nakshatra_agriculture.csv, nakshatra_plants.csv, herbs_by_class.csv

_[Bhūmi domain — to be written.]_

=== Vāstu — Sacred Spatial Intelligence
// Vastu as ecological design (not just architecture)
// Nine vastu zones mapped to graha colors
// Leaflet map integration, directional cosmology
// From dwelling to land mandala

_[Vāstu domain — to be written.]_

=== Nāda — Sound as Field Expression
// Raga melody with gamaka types, tanpura drone, tabla bols
// Bija mantra formant synthesis
// Sound as cosmological field expression, not decoration
// SuperCollider SynthDefs, WirePlumber/JACK routing

_[Nāda domain — to be written.]_

=== Deha — Embodied Knowledge
// Ayurveda: dosha, guna, rasa, vipaka, virya
// Nakshatra body mapping
// Nadi, prana, embodied field indicators

_[Deha domain — to be written.]_

=== Vidyā — Knowledge Graph & Research
// JSONL passage corpus (26k chunks)
// Wiki engine, seed interpretation, offering cycle
// Research lattice, gap detection, relation promotion pipeline
// Vector memory via local Ollama embeddings

_[Vidyā domain — to be written.]_

=== Līlā — Living Interface
// Bandhu: Hanumanji figure as ambient cosmological field presence
// HEXD: research workspace / IDE with hex city renderer
// The hex terrain as live system state visualization
// 404 = dark forest, 200 = passable terrain, working apps = lit villages

_[Līlā domain — to be written.]_

== Bandhu: Presence Without Oracle

// Bandhu is explicitly NOT a chat interface or oracle.
// An animated Hanumanji figure responding to cosmological field state
// via Narottama das Thakura padas.
// The distinction: field-responsive ambient presence vs. query-response AI.
// This distinction matters philosophically and practically.

_[Bandhu philosophy — to be written.]_

== Hardware: The Van-Mounted Field Computer

// Intel NUC (kanjira) running Atlas 330 at localhost:5000
// Local-first by design: no cloud dependency for core function
// Van-mounted as a portable cosmological field computer
// What "local sovereignty" means for traditional knowledge systems

_[Hardware philosophy — to be written.]_

#pagebreak()

// ============================================================
// PART III — THE RESEARCH FIELDS
// ============================================================

= Research Fields and Living Datasets

// Each of the seven Deep Research briefs becomes a named section here.
// Each follows the same structure:
//   - Domain description (2-3 sentences)
//   - Primary sources and lineages
//   - Dataset schema (field names, types, open questions)
//   - Current state (what exists, what's gaps)
//   - Connection points to other Atlas domains (the relational web)

== Ethnobotany and Nakshatra-Plant Correspondences

_[Dataset documentation — to be written.]_

== Mound Cosmology and Sacred Geography

_[Dataset documentation — to be written.]_

== Sacred Water Geography

_[Dataset documentation — to be written.]_

== Ecoregions as Cosmological Territories

_[Dataset documentation — to be written.]_

== Astrobotany: Planetary Rhythms in Plant Biology

_[Dataset documentation — to be written.]_

== Vastu as Ecological Design

_[Dataset documentation — to be written.]_

== The Gaudiya Vaishnava Knowledge Frame

// Special section: the tradition weight system.
// Why GV is the primary frame without being exclusionary.
// The co-evolutionary dharmic covenant model.
// How sectarian integrity is preserved through the authority axis.

_[GV knowledge frame — to be written.]_

#pagebreak()

// ============================================================
// PART IV — THE FEDERATED VISION
// ============================================================

= The Federated Vision

// This is where the document opens outward.
// The architecture becomes an invitation.
// Not "contribute to my project" but "here is where your work lives."

== Traditional Knowledge Sovereignty

// The problem: existing open source models were built for code,
// not for living knowledge systems with custodians and lineages.
// Cryptographic tokenization for traditional knowledge provenance:
//   - Attribution chains that respect lineage, sampradaya, custodianship
//   - Immutable provenance records for shastra-layer knowledge
//   - Distinction between open computation and open knowledge
// Not extraction — stewardship.

_[Traditional knowledge sovereignty architecture — to be written.]_

== The Seva Economy: Auspicious Microtransactions

// SSO exchange framing: not payment rails but offering infrastructure.
// Auspicious timing (muhurta) as a parameter in resource exchange.
// Locally sourced resource networks feeding the mandala-to-planting pipeline.
// The gift economy model: seva as the unit of exchange.
// How microtransactions can be cosmologically timed.

_[Seva economy architecture — to be written.]_

== Mandala to Planting Pipeline

// The full arc from cosmological field state to land action:
//   field_state() → muhurta scoring → nakshatra-plant mapping →
//   vastu zone assignment → planting calendar → local resource network
// This is the integration that no existing system provides.
// A farmer, a gardener, a land steward — what the pipeline gives them.

_[Mandala-to-planting pipeline — to be written.]_

== Atlas as Federation Node

// Any node (another van, a farm, a hackerspace, a gurukula)
// can run their own Atlas and share the graph.
// The federation protocol:
//   - Shared canonical ontology (the stable layer)
//   - Local sadhu overlays (practitioner-specific, non-overriding)
//   - Guru synthesis shared as proposals, never as canon
// What a federated Atlas network looks like in five years.

_[Federation architecture — to be written.]_

== Coherence Spectrum: The Civilizational Simulation

// Atlas is the technical substrate for three interconnected projects:
//   - Coherence Spectrum (persistent procedural civilization simulator)
//   - Emergent Satya Yuga (worldbuilding / story framework)
//   - The Devi Field (speculative eco-mythic sci-fi novel)
// The game simulates it. The novel narrates it. Atlas measures it.
// Coherence as relational density. Fragmentation as loss of relations.
// Satya Yuga as the state where the graph is maximally coherent.

_[Coherence Spectrum vision — to be written.]_

#pagebreak()

// ============================================================
// PART V — THE INVITATION
// ============================================================

= The Invitation

// Now the ask. Specific, named, honest about what Atlas needs.
// Different asks for different communities.
// Not "help me" — "here is where your work lives in this system."

== For Computational Jyotish Communities

// VedAstro, PyJHora, Maitreya users and contributors.
// What Atlas has that they don't: nakshatra-species-place-time
// as a live relational mesh, not just chart computation.
// Specific ask: cross-validation of kala engine computations,
// shared ephemeris calibration, API interoperability.

_[Jyotish community invitation — to be written.]_

== For Sanskrit and Digital Humanities Scholars

// GRETIL, Vedavaapi, WSC Computational Sanskrit community.
// What Atlas offers: 26k JSONL passage chunks already structured,
// a living graph that can host and contextualize their annotations.
// Specific ask: annotation collaboration, corpus expansion,
// federation with Vedavaapi's microservice architecture.

_[DH community invitation — to be written.]_

== For Biodynamic and Permaculture Practitioners

// The astrobotany and nakshatra-grounded observation framework
// is something they've been doing qualitatively for decades
// with no computational substrate.
// Specific ask: field validation of nakshatra-plant correlations,
// seasonal observation data, local species datasets.

_[Biodynamic community invitation — to be written.]_

== For Gaudiya Vaishnava Communities

// The dharmic covenant framing. Bandhu. The devotional orientation.
// This system was built from within the tradition, not about it.
// Specific ask: theological review of knowledge frame,
// pada and stotra corpus contributions, practitioner validation.

_[GV community invitation — to be written.]_

== For Hackerspaces and Open Hardware Builders

// The van-mounted NUC as a portable cosmological field computer
// is a genuinely interesting hardware/software story.
// Local-first, offline-capable, NPU-accelerated, sub-$500 hardware.
// Specific ask: replication, hardware variations,
// edge deployment patterns, mesh networking experiments.

_[Hackerspace community invitation — to be written.]_

== How to Connect

// Practical: where to find the code, how to reach out,
// what a first contribution looks like.
// The offering cycle as onboarding: impetus → research → build → push.

_[Connection details — to be written.]_

#pagebreak()

// ============================================================
// APPENDICES
// ============================================================

= Appendix A: Current System State

// Honest snapshot of what's working and what isn't.
// 217 routes in kernel.py, 46 verified 200 responses.
// 27 engines OK. ~7200 graph entities, ~8500 edges.
// 26k JSONL passage chunks.
// Wiring state of all apps.
// This builds trust — it shows we're not overselling.

_[System audit snapshot — to be written.]_

= Appendix B: Dataset Schemas

// For each major dataset: field names, types, source lineage,
// current row count, known gaps.
// The schema-first CSV format used throughout.

_[Dataset schemas — to be written.]_

= Appendix C: The Offering Cycle

// The development rhythm as a practice.
// impetus → cosmic context → offering plate → seed interpretation
// → research lattice → software/wiki/visualization construction
// → README expansion → git push → next cycle
// How contributors plug into this rhythm.

_[Offering cycle documentation — to be written.]_

= Appendix D: Glossary

// Sanskrit terms used throughout, with brief technical definitions
// in the Atlas context. Not a general Sanskrit glossary —
// specifically how these terms map to system components.
//
// nakshatra, tithi, graha, vastu, panchanga, muhurta, dasha,
// shastra, sadhu, guru, seva, mandala, yantra, raga, bija,
// sampradaya, dharmic covenant, etc.

_[Glossary — to be written.]_

= Appendix E: Bibliography and Source Lineages

// Primary sources for each knowledge domain.
// Organized by domain, not alphabetically.
// Distinguishes: shastra (canonical texts), sadhu (practitioner works),
// modern computational tools, open datasets.

_[Bibliography — to be written.]_
