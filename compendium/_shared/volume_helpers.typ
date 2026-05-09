// ============================================================
// VOLUME HELPERS — conditional title/footer for dual-context builds
// When master_build is true (set by compendium.typ), these are no-ops.
// When standalone, they render full title pages and footers.
// ============================================================

// Master sets this to true before including volumes.
// Standalone compiles leave it false (default).
#let _master_build = state("master_build", false)

#let volume-title(
  title: none,
  kind: none,
  version: none,
  date: none,
) = context {
  if not _master_build.get() [
    #align(center)[
      #v(2in)
      #if kind != none [
        #text(size: 10pt, style: "italic", fill: luma(120))[COHERENCE ATLAS · #upper(kind)]
        #v(0.3em)
      ]
      #text(size: 22pt, weight: "bold", tracking: 0.8pt)[#title]
      #v(1.2em)
      #line(length: 3in, stroke: 0.4pt)
      #v(1.2em)
      #if version != none [
        #text(size: 10pt, style: "italic")[v#version]
        #v(0.3em)
      ]
      #if date != none [
        #text(size: 9.5pt, fill: luma(100))[#date]
      ]
    ]
    #pagebreak()
  ]
}

#let volume-footer() = context {
  if not _master_build.get() [
    // No-op for now — footer is handled by page setup
  ]
}

#let scaffold-notice(status: "scaffold", notes: none) = {
  v(0.8in)
  align(center)[
    #rect(
      width: 4in,
      stroke: 0.5pt + luma(180),
      inset: 20pt,
      radius: 4pt,
    )[
      #align(center)[
        #text(size: 11pt, weight: "semibold", fill: luma(100))[SCAFFOLD]
        #v(0.4em)
        #text(size: 10pt, style: "italic", fill: luma(130))[
          Content pending. This volume exists as a structural placeholder
          in the compendium. Its section headings indicate planned scope.
        ]
        #if notes != none [
          #v(0.6em)
          #text(size: 9pt, fill: luma(150))[#notes]
        ]
      ]
    ]
  ]
  pagebreak()
}
