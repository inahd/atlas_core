#import "../_shared/preamble.typ": compendium-preamble, title-page

#compendium-preamble(
  title: "Architecture and API Reference",
  subtitle: "Technical Reference",
  version: "0.1 — scaffold",
)

#title-page(
  title: "Architecture and API Reference",
  subtitle: "Kernel, npu_engine, route map, and field state pipeline",
  volume: "COHERENCE ATLAS · TECHNICAL REFERENCE",
  version: "0.1 — scaffold · April 2026",
)

#v(0.6in)
#align(center)[#text(size: 11pt, weight: "semibold")[Abstract]]
#v(0.4em)

_Status: scaffold. Content to be drawn from docs/audit/ and codebase._

#pagebreak()

// ─── MAIN CONTENT ────────────────────────────────────────────────

= System Architecture

// TBD: Flask kernel, npu_engine package, 8 blueprints.

= Field State Pipeline

// TBD: calc_panchanga → field_state → engines → routes.

= Route Registry

// TBD: 259 routes organized by domain. Blueprint map.

= Engine Inventory

// TBD: 238 Python files across 15+ subdirectories.

= Dataset Schema

// TBD: 42 domains, 240 CSVs, attestation tracking.

= Deployment

// TBD: kanjira Intel NUC, PipeWire, MOTU M2, systemd.

