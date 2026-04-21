# Next Phase Readiness — April 21, 2026

## A. Nitya Devi Layer Build

**Readiness: 80% — mostly data wiring, not new creation.**

Already exists:
- `nitya_devi_master.csv` (15 rows, attested_classical)
- `nitya_yantra_geometry.csv` (15 rows, 81 columns, mixed attestation)
- `tithi_master.csv` with nitya_devi column
- Kernel NITYA_DEVIS + _devi_dict() + field_state["panchanga"]["devi"]
- Layer composer S1 integration
- S1 HTML yantra rendering + mantra + weapons
- 45 yantra PNG renders
- compute_tithi() with null stub fields ready for Devi data

What's missing:
- Data loaders in jyotish_utils.py (load_nitya_devi_master, load_nitya_yantra_geometry)
- Filling the 4 null fields in compute_tithi()
- Devi-specific routes (/jyotish/devi/today, /devi/<id>)
- Chladni field computation from yantra geometry wave params
- Sound engine blending Devi raga with nakshatra raga

Blockers:
- Krishna paksha Devi ordering (forward repeat or reverse?) — needs decision
- SPECULATIVE yantra geometry for 6 of 15 Devis — use or omit?
- Angular positions (equal spacing assumed, no canonical source)

**See: docs/design/devi_layer_framework.md for full analysis.**

## B. Gaudiya Cosmological Corpus (Navadvipa Panjika)

**Readiness: 20% — needs primary source access.**

Already exists:
- Gaudiya text corpus in sources/gaudiya/ (BG chunks, Bhagavatam, Vedanta Sutra)
- Composition corpus (Narottama padas, navagraha kritis)
- Goloka engine (ashtakala, sakhi, forest, seva)
- S0 Goloka layer page

What's needed:
- 1914 Bengali Navadvipa Panjika text (not in corpus)
- Mapping between panjika festivals and Atlas panchanga system
- Observance-specific liturgical sequences
- Gaudiya-specific tithi significance (beyond generic Vedic)

Blockers:
- Primary source access (1914 Panjika is a rare document)
- Bengali OCR/transcription if only scanned
- Scholarly apparatus for establishing attestation level

## C. Documentation Substrate

**Readiness: 60% — exists but fragmented.**

Already exists:
- CLAUDE.md (primary orientation, maintained)
- SYSTEM_MAP.md (engine/route map, dated April 8)
- CORE_SCOPE.md (boundary definition)
- docs/ARCHITECTURE.md (detailed, dated April 5)
- This audit set (docs/audit/)
- Design docs (docs/design/devi_layer_framework.md)
- Memory files (.claude/projects/.../memory/)

What's needed:
- CLAUDE.md update to reflect jyotisha layer + wave field
- SYSTEM_MAP.md update (stale by 2 weeks)
- ADR (Architecture Decision Records) for key choices:
  - Lahiri ayanamsha as default
  - Whole-sign house system
  - Simplified IAST naming convention
  - Wave field k-value set {1,2,3,4,6,7,12}
- Single consolidated skill file for Claude Code orientation
- Route registry document (259 routes is too many to discover by grep)

Blockers: None — documentation work, no source access needed.

## D. Paper Consolidation

**Readiness: varies by paper.**

### Two-Source Interference (v3, 5005 words)
- 8 findings (F7-F14), well-structured
- Ready for: internal review, sharing with mathematical audience
- Needs: the composite amplification numbers are from one chart (needs systematic study caveat)
- Kp analysis pipeline not in repo yet (noted as pending)

### Yantra Eigenvalue Exploration (complete, Apr 12)
- 7 findings, self-contained
- Ready for: sharing as-is
- No blocking issues

### Planetary Primes (v1, 2633 words)
- Combines retrograde symmetries + vertebral anatomy
- Needs: bat T=12 verification, frog vertebral count clarification
- Ready for: internal review after bat verification

### Vertebral Primes (v1, 3368 words)
- 10 findings, comprehensive cross-species analysis
- Needs: systematic vertebral survey (beyond anecdotal species), micro-CT prediction is untested
- Ready for: internal review, hypothesis generation

### Dependency order:
1. Yantra eigenvalue (standalone, ready now)
2. Two-source interference (needs Kp pipeline script)
3. Planetary primes (needs bat verification)
4. Vertebral primes (needs systematic survey data)

## E. Outreach Preparation

**Readiness: 40%.**

Papers ready first:
1. Yantra eigenvalue exploration — self-contained mathematical result
2. Two-source interference — aspect theory derivation is clean

Supporting material that exists:
- 45 yantra visualization PNGs
- Working mandala visualization (jyotish_chart.html)
- Live demo capability (kernel + SC running)

What's missing:
- Typeset versions (the .typ paper exists but is older; new papers are in .md)
- Abstract/summary for each paper
- GitHub repo cleaned for public sharing (sensitive personal data in natal.json)
- README for external audience

Blockers:
- natal.json contains personal birth data — must be excluded or anonymized
- API keys or credentials — audit needed before pushing
