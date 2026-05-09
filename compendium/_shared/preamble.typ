// ============================================================
// COHERENCE ATLAS COMPENDIUM — Shared Preamble
// Imported by every volume for consistent typesetting.
// Style values extracted from the founding document (v0.2).
//
// In master mode (_master_build state = true):
//   - title-page renders nothing (master provides headings)
//   - Volume outlines still render (harmless inside master sections)
// In standalone mode:
//   - title-page renders a full title page with pagebreak
// ============================================================

#import "volume_helpers.typ": _master_build

#let compendium-preamble(
  title: none,
  subtitle: none,
  volume: none,
  version: none,
) = {
  // NOTE: set document(title:) is NOT called here.
  // For standalone volumes, the title shows on the rendered title page.
  // For master, compendium.typ sets the document title once.

  // Typographic setup — always apply (idempotent)
  set page(
    paper: "us-letter",
    margin: (top: 1.2in, bottom: 1.1in, left: 1.2in, right: 1.1in),
    numbering: "1",
    number-align: center,
  )

  set text(
    font: ("DejaVu Serif"),
    size: 11pt,
    lang: "en",
  )

  set par(
    justify: true,
    leading: 0.75em,
    spacing: 1.25em,
  )

  set heading(numbering: "1.1")

  show heading.where(level: 1): it => {
    v(1.8em)
    text(size: 13.5pt, weight: "bold")[#it]
    v(0.5em)
  }

  show heading.where(level: 2): it => {
    v(1.1em)
    text(size: 11.5pt, weight: "semibold")[#it]
    v(0.25em)
  }

  show heading.where(level: 3): it => {
    v(0.7em)
    text(size: 11pt, weight: "semibold", style: "italic")[#it]
    v(0.15em)
  }

  show raw: it => text(font: "DejaVu Sans Mono", size: 9.5pt)[#it]
}

#let title-page(
  title: none,
  subtitle: none,
  volume: none,
  version: none,
  location: "Gainesville, Florida --- kanjira --- localhost:5000",
) = context {
  // In master mode, skip title page — master provides section headings
  if _master_build.get() {
    // Render nothing
  } else {
    align(center)[
      #v(2in)

      #if volume != none [
        #text(size: 10pt, style: "italic", fill: luma(120))[#volume]
        #v(0.3em)
      ]

      #text(size: 24pt, weight: "bold", tracking: 1pt)[#title]

      #if subtitle != none [
        #v(0.5em)
        #text(size: 13pt, style: "italic")[#subtitle]
      ]

      #v(1.4em)
      #line(length: 3.4in, stroke: 0.4pt)
      #v(1.4em)

      #if version != none [
        #text(size: 10pt, style: "italic")[#version]
        #v(0.5em)
      ]

      #text(size: 9.5pt, fill: luma(100))[#location]
    ]
    pagebreak()
  }
}
