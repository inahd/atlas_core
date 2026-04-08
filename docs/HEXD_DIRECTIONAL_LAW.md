# Hexd Directional Law

Applied: 2026-04-07

The Hexd layout follows the Vastu cardinal cross from `docs/MANDALA_SCHEMA.md`.
Each screen region maps to a fixed direction. This is structural law, not decoration.

## Cardinal Cross

| Direction | Region | Content type | Deity | Element |
|-----------|--------|-------------|-------|---------|
| **North** | Top rail | Dashboard, selection, field state | Kubera | water |
| **South** | Bottom dock | Continuity, command, scratch, trace | Yama | earth |
| **West** | Left drawer | Ingress tokens, references, relations | Varuna | water |
| **East** | Right drawer | Textual elaboration, study, support | Indra | fire |
| **Center** | Main body | Active unfolding — the thing itself | Brahma | all |

## What goes where

**North** — Layer selection, mode selection, live panchanga chips, clock, online status.
Selection and dashboard only. Never primary content.

**South** — Scratch buffer, notes, trace log, command line, tabs.
Continuity surface. Things that persist across mode changes. Never navigation.

**West** — Token list first, then active token detail, relation shelf, live references, jumps.
Ingress-first: compact tokens before descriptions. Things enter from the West.

**East** — Text surfaces: reading, study, research, editor.
Elaboration: extended text, passages, codex content. Support for center, not a primary stage.

**Center** — The unfolding body. Field snapshot in field mode, corpus in text mode,
yantra data in yantra mode. This is the semantic center — everything else serves it.

## Diagonals (semantic only, no visible panes)

| Diagonal | Influence |
|----------|-----------|
| NE (Ishana) | Sacred knowledge accent — appears in East drawer when devi/mantra content is active |
| NW (Vayu) | Sound accent — appears in West drawer when raga/svara tokens are active |
| SE (Agni) | Action accent — appears in South dock when practice/capture actions are active |
| SW (Nirriti) | Ancestry accent — appears in West drawer when plant/guild/seed content is active |

These are mode-conditional accents, not permanent layout regions.

## CSS implementation

Directional classes: `.hexd-north`, `.hexd-south`, `.hexd-west`, `.hexd-east`, `.hexd-center`
Border accent colors from `--north-accent` through `--center-accent` CSS variables.
Data attributes on `.hexd-app`: `data-north="dashboard"` etc.

## Responsibility split: /study vs Hexd

| App | Route | Responsibility | Layers |
|-----|-------|---------------|--------|
| **/study** | `/study` | Text substrate. Reading, study, annotation, corpus navigation. | S0 canonical home |
| **Hexd** | `/hexd` | Layer interaction shell. Field-form, graph, unfold, source views. | S1–S6 |

`/s0` redirects to `/study`.
S1 classical source anchors redirect to `/study?text=X`.
Future S2/S5 textual references should also route into `/study`.

Hexd should NOT try to be a text viewer.
/study should NOT try to be a multi-layer interaction shell.

## What this law does NOT do

- Does not create diagonal panes (NE/NW/SE/SW are semantic influences only)
- Does not add new fetch paths or runtime branches beyond the /study handoff
- Does not change the phase1 canonical runtime for S1-S6
- Does not reactivate legacy S-layer layout code
