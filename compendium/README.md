# The Atlas Compendium

A living almanac of Vedic cosmological computation.

## What this is

The founding document (`docs/atlas_paper_v02.typ`) is the spine. The compendium
extends it: each volume deepens one section into a standalone treatment. Research
papers present mathematical results. Positioning essays frame Atlas in its
intellectual lineage. Field dives explore each domain at full depth. Technical
references document architecture and ontology.

The compendium is 5% written. 1 of 25 volumes has substantive content (Lo Shu
Spectral Carrier). The other 24 are structural scaffolds indicating planned
scope. This is honest by design: the infrastructure is complete; the contents
grow volume by volume.

## Building

```bash
cd compendium
./build/build_all.sh                        # everything: master + volumes, both editions
./build/build_all.sh --edition=public       # public edition only
./build/build_all.sh --master-only          # just the master PDF
./build/build_all.sh --volumes-only         # just per-volume PDFs
./build/build_all.sh --clean                # wipe output first, then build
./build/build_all.sh --version              # print version from manifest
```

Output goes to `build/output/{public,private}/`. Requires `typst` (tested with
0.14.2) and `python3` with `pyyaml`.

## Editions

- **Public**: all volumes except those marked private in MANIFEST.yaml
- **Private**: everything, including personal chart material and unverified claims

A volume defaults to both editions. Flag as `[private]` in the manifest when
there's a specific reason (personal data, unverified claims, institutional names).

## Adding a volume

1. Create `{kind}/{filename}.typ` using the shared preamble import
2. Add an entry to `MANIFEST.yaml` with id, title, kind, order, status, editions
3. Run `./build/build_all.sh`

## Structure

- `_shared/preamble.typ` — typographic identity (DejaVu Serif 11pt, Cinzel headings)
- `_shared/volume_helpers.typ` — dual-context helpers (standalone vs master)
- `MANIFEST.yaml` — single source of truth for all volumes
- `compendium.typ` — master document (includes all volumes, filtered by edition)
- `build/build_all.sh` — full pipeline
- `build/output/` — generated PDFs (git-ignored)

## Versioning

Every PDF carries: `Atlas Compendium · v{version} · {date} · {git hash}`.
Version is in MANIFEST.yaml. Bump it when releasing a new edition.
