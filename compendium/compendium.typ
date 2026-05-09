// ============================================================
// THE ATLAS COMPENDIUM — Master Document
// Unified compilation of all volumes, filtered by edition.
// Build: typst compile --root . --input edition=public compendium.typ
// ============================================================

#import "_shared/preamble.typ": compendium-preamble, title-page
#import "_shared/volume_helpers.typ": _master_build

// ── EDITION PARAMETER ────────────────────────────────────────
// Set via: --input edition=public (or private)
// Default: private (includes everything)
#let edition = sys.inputs.at("edition", default: "private")

// Signal to volume helpers that this is a master build
#_master_build.update(true)

// ── MANIFEST ─────────────────────────────────────────────────
#let manifest = yaml("MANIFEST.yaml")
#let meta = manifest.compendium

// ── DOCUMENT METADATA (set once, not overridden by volumes) ──
#set document(title: meta.title, author: meta.author)
#let volumes = manifest.volumes

// ── PREAMBLE ─────────────────────────────────────────────────
#compendium-preamble(
  title: meta.title,
  subtitle: meta.subtitle,
  version: meta.version,
)

// ── TITLE PAGE ───────────────────────────────────────────────
#align(center)[
  #v(1.8in)
  #text(size: 26pt, weight: "bold", tracking: 1.2pt)[THE ATLAS COMPENDIUM]
  #v(0.5em)
  #text(size: 13pt, style: "italic")[#meta.subtitle]
  #v(1.4em)
  #line(length: 3.4in, stroke: 0.4pt)
  #v(1.4em)
  #text(size: 10pt, style: "italic")[
    v#meta.version · #edition edition · #datetime.today().display("[year]-[month]-[day]")
  ]
  #v(0.5em)
  #text(size: 9.5pt, fill: luma(100))[
    #meta.author · Gainesville, Florida · kanjira · localhost:5000
  ]
  #v(2em)
  #text(size: 9pt, fill: luma(140))[
    This is a living almanac. #volumes.len() volumes are registered;
    #volumes.filter(v => v.status == "built").len() contain substantive content.
    The remainder are structural scaffolds indicating planned scope.
  ]
]
#pagebreak()

// ── TABLE OF CONTENTS ────────────────────────────────────────
#outline(
  title: [#text(size: 12pt, weight: "semibold")[Contents]],
  indent: 1.8em,
  depth: 2,
)
#pagebreak()

// ── VOLUME INCLUSION ─────────────────────────────────────────
// Group volumes by kind, include in manifest order

#let kinds = (
  (key: "research_paper", label: "Research Papers"),
  (key: "positioning_essay", label: "Positioning Essays"),
  (key: "field_dive", label: "Field Dives"),
  (key: "dhatu_compendium", label: "Dhātu-Bhasma Compendium"),
  (key: "technical_reference", label: "Technical Reference"),
)

#for kind in kinds {
  let kind_volumes = volumes
    .filter(v => v.kind == kind.key)
    .filter(v => edition in v.editions)
    .sorted(key: v => v.order)

  if kind_volumes.len() > 0 {
    // Section divider
    pagebreak()
    v(2in)
    align(center)[
      #text(size: 10pt, fill: luma(120), tracking: 0.2em)[PART]
      #v(0.3em)
      #text(size: 18pt, weight: "bold")[#kind.label]
      #v(0.5em)
      #text(size: 9pt, fill: luma(140))[
        #kind_volumes.len() volumes · #kind_volumes.filter(v => v.status == "built").len() built
      ]
    ]
    pagebreak()

    for vol in kind_volumes {
      // Volume kind label (not a heading — avoids duplicate TOC entry)
      v(0.8em)
      text(size: 10pt, fill: luma(120), tracking: 0.1em)[#upper(vol.kind.replace("_", " "))]
      v(0.4em)

      if vol.status == "scaffold" {
        v(0.4em)
        rect(
          width: 100%,
          stroke: 0.5pt + luma(200),
          inset: 12pt,
          radius: 3pt,
        )[
          text(size: 9pt, fill: luma(130))[
            *SCAFFOLD* — Content pending. \
            #if vol.at("notes", default: none) != none [#vol.notes] \
            Last updated: #vol.last_updated
          ]
        ]
        v(0.4em)
      }

      // Include the volume content
      include(vol.id + ".typ")
      pagebreak()
    }
  }
}

// ── COLOPHON ─────────────────────────────────────────────────
#pagebreak()
#v(2in)
#align(center)[
  #text(size: 10pt, weight: "semibold")[Colophon]
  #v(0.6em)
  #text(size: 9pt, fill: luma(120))[
    The Atlas Compendium · v#meta.version · #edition edition \
    Built #datetime.today().display("[year]-[month]-[day]") \
    Typeset in DejaVu Serif with Typst #sys.version.at(0).#sys.version.at(1).#sys.version.at(2) \
    Source: ~/atlas_core/compendium/
  ]
]
