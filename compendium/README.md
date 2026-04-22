# Coherence Atlas Compendium

The Coherence Atlas Compendium is the growing body of deep treatments,
research papers, positioning essays, and technical references that extend
the Atlas founding document into full-depth exposition of each domain.

The founding document (`docs/atlas_paper_v02.typ`) remains the spine. Each
compendium volume expands a specific section into standalone treatment.

## Structure

- `_shared/` — shared preamble and styling (extracted from founding document)
- `field_dives/` — 11 thematic expositions of each research domain
- `research_papers/` — 6 canonical typeset versions of research output
- `positioning_essays/` — 3 lineage and stance essays
- `technical_reference/` — 4 architecture, ontology, federation, skill docs
- `appendices/` — glossary, primary sources (shared across volumes)
- `build/` — build script + PDF artifacts

## Build

```bash
cd compendium
./build/build.sh                                            # build everything
./build/build.sh field_dives/01_jyotish_and_wave_field.typ  # one volume
./build/build.sh field_dives/01                             # prefix match
```

Requires `typst` (tested with 0.14.2).

## Status per volume

Check each `.typ` file header for its current status:
- `scaffold` — structure only, content pending
- `drafted` — content present, unrefined
- `refined` — content refined, not yet canonized
- `canonical` — ready for circulation

Promotion is explicit per `docs/LITERATURE_MATURATION.md` discipline.

## Counts

| Directory | Files | Status |
|-----------|-------|--------|
| field_dives/ | 11 | scaffold |
| research_papers/ | 6 | scaffold (wrappers around markdown drafts) |
| positioning_essays/ | 3 | scaffold |
| technical_reference/ | 4 | scaffold |
| **Total** | **24** | |
