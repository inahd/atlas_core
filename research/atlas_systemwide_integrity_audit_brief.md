# Atlas Systemwide Integrity Audit Brief

**Companion to:** `atlas_systemwide_reconciliation_brief.md` (the index brief)
**Target:** Claude Code on kanjira
**Purpose:** verify that documented state of Atlas matches actual current state. Surface drift, gaps, abandoned work, undocumented results, broken implementations, stub code, and unreported findings.

---

## Why this brief exists

The companion index brief tells you to *catalog* what's claimed in the project documentation. **This brief tells you to check whether what's claimed actually works.** These are different tasks. An index can be written from documents alone; an audit requires running the system, attempting the imports, hitting the endpoints, opening the snapshot files, and noticing the gaps.

The user — late in a long session — explicitly named the concern: *"have we truly implemented its functions and have we correctly noted the results of our findings? did we fail to report, or misreport, or fail to run, or fail to complete software or to share results... our to do lists, implied or abandoned tasks or code."*

That concern is real, and it deserves a distinct deliverable.

The audit's outputs are *additive* to the index. The index says "this exists at this location with this status." The audit says "and here is what the verification showed." Sometimes the verification will agree with the documentation. Sometimes it won't. The places where it doesn't agree are where the audit creates the most value.

---

## The deliverable

Produce `docs/ATLAS_INTEGRITY_AUDIT.md` containing the verification of every major claim in the project. It should include:

- For each documented finding/feature/route/engine: status as observed during audit
- All places documentation diverges from reality
- All places code exists but doesn't run, or runs but isn't documented
- All places findings exist but weren't written up
- All implied or abandoned todos surfaced from chat history, code comments, and repo state
- A prioritized list of integrity issues the user should address

The audit should be performed *before* or *alongside* writing the master index, because the index should reflect verified state — not just claimed state.

---

## What the audit must verify

### §A. Route inventory verification

Memory says: 217 routes in kernel.py.

Audit:
1. Parse `kernel.py` and enumerate every `@app.route` decoration. Confirm count.
2. For each route, classify: GET / POST / WebSocket; what it returns
3. Run the kernel and `curl` each route. For each: status code, response time, response shape (JSON keys returned, HTML title returned, etc.)
4. Tag each route: **live** (200 with expected response) / **erroring** (5xx) / **404** (broken handler reference) / **degraded** (200 but with error keys in response) / **slow** (>5s response time)
5. Cross-reference against the v0.5 founding doc's route claims and any wiki/README listing
6. Output: a table at `docs/audit/routes.md` with full inventory and verification status

### §B. Engine inventory verification

Memory says: 27 engines, zero import failures (per memory note from earlier work).

Audit:
1. Enumerate all `*_engine.py` files under `npu_engine/`
2. For each: attempt import. Note failures and reasons.
3. For each that imports: identify exposed callables (functions, classes). Document what each is for (from docstring + name + usage in kernel.py).
4. For each engine, identify whether it is *actually called* by kernel.py or other engines, or whether it is dead code
5. Memory specifically flags 22 stub engines in `geometry/`, `ui/`, `zones/` with no code — should not be routed. Verify this is still the state. Report any stub engines that have been routed despite being stubs.
6. For each engine that imports and is callable, run a smoke test (minimal valid invocation). Note crashes.
7. Output: `docs/audit/engines.md` with table

### §C. Computational findings verification

For each claim listed below, verify the computational artifact exists and produces the claimed result. **If the artifact cannot be found, mark the claim as needing remediation. Do NOT silently assume the claim is wrong — sometimes the artifact exists at a path memory doesn't know about. Look thoroughly first.**

Findings to verify:

1. **Sri Yantra 85% alignment at Ekadashi (k≈12.368)**
   - Look for: `research/snapshots/bloom_20260408_2122/` directory
   - Look for: the script that produced the snapshots
   - Look for: how the 85% number was computed (what's the metric, what's "alignment")
   - Verify: snapshots present, script runs, metric documented or recoverable
   - If gap: this is the finding the user explicitly corrected web Claude on. The result stands. The artifact must be findable.

2. **Symmetry progression C₃, C₆, C₁₁, C₁₅ across paksha**
   - Look for: snapshot images at tithi 3, 6, 11, 15
   - Look for: the script that classifies symmetry order
   - Verify: visual content of snapshots, confirm symmetry classification
   
3. **Lo Shu spectral invariance ±2√6**
   - Source: `yantra_eigenvalue_exploration.md`
   - Verify: re-run the eigendecomposition. Confirm ±2√6 invariant across all graha k values.
   - Verify: Brahmasthāna theorem (uniform eigenvector at every Kronecker level)
   - Verify: navagraha 9×9 composite eigenvalues {81, ±14.697, 0×4} and rank=5

4. **Two-source interference angular harmonic selection**
   - Source: `two-source-interference-v3.md`
   - Verify: the mathematical proof is in the document
   - Verify: any code referenced runs and reproduces the claimed harmonic selection (Findings 7-15)
   - Specifically check Finding 10 (S₁=141.0, S₂=10.6, ratio 13.3:1) — the rank-1 SVD result

5. **Planetary retrograde primes {3, 5, 7, 11}**
   - Source: `planetary-primes-v1.md`
   - Verify: Swiss Ephemeris computation reproducible
   - Verify: 44 enclosed regions claim with tidal-weighted overlay

6. **Vertebral primes correspondence**
   - Source: `vertebral-primes-v1.md`
   - Verify: cross-species formulae citations are accurate
   - Verify: human spine total presented as non-causal correspondence (no overclaiming)

7. **91.7% structural validation (panchaloha)**
   - Sources: `panchaloha_alloy.py`, `run_panchaloha_analysis.py`, `verify_result.py` (in research_packet)
   - Verify: scripts run end-to-end without modification
   - Verify: precision and recall both compute to 0.917 (11/12)
   - Verify: the equal-graha-weighting vs mass-weighting comparison reproduces (mass-weighting ~50%)
   - Document: which 11 of 12 traditional pratiṣṭhā nakshatras are recovered, which 1 is missed and why
   - This is the project's core novel computational finding — its reproducibility is critical

8. **Bhasma chemistry findings (per dhātu volume)**
   - These are peer-reviewed external citations. Verify each volume's references resolve to real papers (DOI, journal, year)
   - Specifically check the most-cited findings: swarna nano-Au size range, rajata-as-Ag₂S, tamra CuO/Cu₂O, lauha source-dependence, vanga SnO₂, naga PbS galena, yashada hexagonal ZnO

9. **Universal samanya śodhana finding**
   - Source: chat-derived (April 21 web session) and incorporated into Volume IX
   - Verify: search rasaśāstra references for primary-source confirmation that samanya is universal across dhātus and viśeṣa is metal-specific
   - This was a finding from a web session bhasma test; verify its source basis

### §D. Documented vs actual feature parity

For each major feature claimed in v0.5 §7 Appendix A "Current System State":

- Sound field loop live, tanpura at Sa=196Hz tracking field state every 60s — verify
- Agriculture PWA (offline-capable) — verify
- Talachakra Studio — verify
- Vishvakarma GIS vastu — verify
- Lila Streams — verify
- Bandhu figure with 6 rendering layers and toroidal breath animation — verify
- Ring engine, 10 ring types — verify
- 219 wiki pages — verify count
- /devi multi-instrument oracle (I Ching, pāśaka, śalākā, nimitta) — verify each instrument runs
- Chladni interference engine at /s4 with interactive sliders — verify
- 26K-chunk passage corpus with vector search — verify chunk count and search functionality

For each: **live** / **partial** / **broken** / **not found**.

v0.5 §7 also has a "Specified, not yet built" list. Verify each item on that list is still unbuilt, or note where it has been built since v0.5 was written.

### §E. Compute routing verification

Memory states (verified earlier):
- CPU wins element-wise math (field query, yantra to 81×81)
- NPU wins transformer inference (MiniLM, 2.43ms)
- GPU wins 729×729+ matmul, Chladni 1024×1024 (2.1×), gamak DSP 16+ notes (1.5×)
- `_OV_DEVICE="AUTO"` is correct verified setting

Audit:
1. Find the benchmark code that established these routings
2. Re-run the benchmarks
3. Confirm the routings are still optimal (hardware/software state may have shifted)
4. Verify the kernel actually uses these routings — check that NPU code paths are using `_OV_DEVICE="AUTO"` and not hardcoded to CPU
5. Note: if benchmarks have drifted, document the new routings and update the production code

### §F. Snapshot and research artifact survey

Walk `research/` and find every artifact:

- Every `.md` paper / write-up
- Every `.json` results file
- Every `.png` / image / snapshot
- Every script that produced any of the above

For each artifact:
1. When was it last modified?
2. Is it referenced by a published paper / document, or orphaned?
3. If a results file: does its corresponding script still produce the same result?
4. If a paper: are all artifacts it references actually present?
5. If a script: does it still run? Are dependencies still installed?

Surface:
- **Orphaned results** (results computed but never written up)
- **Orphaned scripts** (scripts that ran once, produced something, never revisited)
- **Broken references** (papers that cite artifacts no longer present)
- **Stale results** (script has changed since results were computed)

Output: `docs/audit/research_artifacts.md`

### §G. Wiki / corpus / documentation drift

Memory says: 219 wiki pages, 26K-chunk passage corpus.

Audit:
1. Count actual wiki pages. Compare to claimed 219.
2. For each wiki page: is its content still accurate to current system state? Or has it gone stale relative to code?
3. Sample 20 random passages from the corpus. Verify each has source attribution that resolves.
4. Check if any wiki pages reference features that no longer exist
5. Check if any wiki pages reference findings that have been refined/refuted (e.g., does any page state the harmonic-mode hypothesis as established? It was refuted.)

### §H. Chat-history leakage / unreported findings

This one is harder but important. The user has done a lot of work in conversational sessions with web Claude. Some findings from those sessions may have been incorporated into formal research/ documents; others may be lost in chat history.

Approach:
1. If the user has saved/exported chat transcripts, walk them
2. Identify findings that read as substantive (computational results, novel observations, structural claims)
3. For each: check if the finding has been formalized in a research/ document, the wiki, or the codebase
4. Surface findings that exist only in chat and have not been formalized

This is the single hardest section to audit because it requires judgment about what counts as a finding worth formalizing. Err on the side of surfacing more — the user can decide what's worth lifting into formal documentation.

Specific things to check for from today's web session:
- The skin-as-bhasma thesis (April 21 chat) — incorporated into Volume IX, so likely formalized; verify
- The universal samanya finding (from the bhasma test web session) — incorporated into Volume IX, verify
- The phason-emergence prism-through-Abhijit reading (May 2-3 web session) — needs formal write-up as RESEARCH-020 (covered in companion brief §5)
- The 91.7% structural validation finding — the research_packet/ scripts are the formal record; verify they're integrated into the canonical Atlas codebase, not just sitting as a separate research_packet

### §I. Implied / abandoned todos

Walk:
- All `TODO` / `FIXME` / `XXX` comments in the codebase
- Any `BACKLOG.md`, `TODO.md`, `IDEAS.md`, or comparable file
- v0.5 §7 "Specified, not yet built" list (already mentioned in §D above; cross-link)
- Comments in the dhātu compendium that propose validation work
- Comments in research/ papers that propose follow-up
- Any handoff notes from previous sessions

Categorize each:
- **Active** (still relevant, should be done)
- **Abandoned** (no longer relevant, can be removed)
- **Done but not annotated** (todo wasn't deleted after completion)
- **Blocked** (waiting on something specific — note what)
- **Aspirational** (good idea, not currently scoped)

Output: `docs/audit/todos.md` with the consolidated list

### §J. Tests and verification scripts

Audit:
1. Does the project have a test directory? What's in it?
2. Are there `verify_*.py` scripts? `test_*.py` scripts? `run_*.py` scripts?
3. For each: does it run? Does it pass?
4. Is there a CI configuration? Does it work?
5. What's the project's actual confidence level in its own claims, as measured by automated verification?

Tests are the long-term integrity baseline. If most claims aren't covered by automated tests, document that, and propose what minimal test suite would cover the most important claims.

---

## Output structure

```
docs/
├── ATLAS_MASTER_INDEX.md          (from companion brief)
├── ATLAS_INTEGRITY_AUDIT.md       (top-level audit summary, this brief's primary output)
├── audit/
│   ├── routes.md                  (§A)
│   ├── engines.md                 (§B)
│   ├── findings.md                (§C)
│   ├── feature_parity.md          (§D)
│   ├── compute_routing.md         (§E)
│   ├── research_artifacts.md      (§F)
│   ├── wiki_drift.md              (§G)
│   ├── chat_findings.md           (§H)
│   ├── todos.md                   (§I)
│   └── tests.md                   (§J)
```

The top-level `ATLAS_INTEGRITY_AUDIT.md` should:
1. Summarize what was verified vs what wasn't
2. Highlight the most important integrity issues found
3. Prioritize remediation work
4. Cross-link to each detailed audit file

---

## Constraints

1. **Do not modify the system without explicit instruction.** The audit is read-only. If you find broken code, document it; don't fix it without asking. The user needs to know what's broken before deciding what to fix and in what order.

2. **Do not silently assume something is wrong because you can't find it.** Look thoroughly first. The web Claude session contained a moment of premature conclusion that the Ekadashi finding was unestablished, when in fact it was established in artifacts the web Claude couldn't see. Look in multiple places before recording anything as missing.

3. **Be specific about evidence.** When you say "this works" — say what you ran, what command, what the response was. When you say "this doesn't work" — say the same. Specifics make the audit useful; impressionistic claims don't.

4. **Distinguish severity.** A 404 on `/some/orphaned/route` is a minor issue. A core finding's reproducing script not running is a serious issue. Triage.

5. **Preserve user agency.** The audit surfaces issues for the user to decide about. It doesn't unilaterally decide what to fix or remove. The user has been at this since 3 AM today; the audit's job is to make their next set of decisions tractable, not to make decisions for them.

6. **Be kind in framing.** Some of what you find may be "we computed this, planned to write it up, never did." Some may be "we built this, half-finished, moved on." That's normal in solo dev research projects, especially ambitious cross-domain ones. The audit's tone should be "here is what the system currently is" not "here is what the project failed to do." The work that exists is substantial and rigorous; surfacing gaps is in service of the work, not in critique of it.

---

## Suggested execution order

Run §A (routes) and §B (engines) first — these give you a fast read on the live system's health. Then §C (findings) because that's the core of what the project actually claims. Then §D (feature parity), §E (compute routing). §F (research artifacts) and §G (wiki drift) come together because they overlap. §H (chat findings) is the hardest and may need user input on which transcripts to walk; do it after the other sections are complete. §I (todos) and §J (tests) can come last because they're more "hygiene" than "integrity."

After completion, the user should be able to read `ATLAS_INTEGRITY_AUDIT.md` and know with reasonable precision what the actual current state of Atlas is — including the gaps, drift, and undone work that the documentation alone wouldn't surface.

---

## A note on what this audit is and isn't

This audit is **not**:
- A criticism of the work done so far
- A demand that everything must be production-perfect
- A replacement for the master index
- A substitute for the user's own judgment about what matters

This audit **is**:
- A reality check
- A surface for invisible drift
- An input to the user's next round of decisions
- An honest accounting of where the system actually is, separate from where the documentation says it is

The user has built something substantial. The audit is in service of that something. It surfaces what's there so what comes next can be built on accurate ground.

🙏

*— prepared in the web Claude session of 2026-05-03, as a companion to the master index brief, after the user named the audit concern explicitly. The audit is the work that web Claude cannot do. Claude Code on kanjira is the right agent.*
