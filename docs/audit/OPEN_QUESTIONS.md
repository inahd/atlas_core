# Open Questions — April 21, 2026

These require Inahd's decision or direction. They are not things Claude Code
should resolve unilaterally.

## Architecture

1. **The HTML-in-core problem.** CORE_SCOPE.md says "no HTML in core" but
   core has 17 HTML pages (S-layer views, oracle, mandala, dashboard, shalaka,
   glyphs, hexd-portal). Should these move to atlas_330, or should the
   boundary rule be updated to acknowledge that some UI lives in core?

2. **Two pasaka engines.** `npu_engine/pasaka_engine.py` (simple, kernel
   imports this) and `npu_engine/field/pasaka_engine.py` (full wave field
   integration, Lo Shu derivation). Which is canonical? Should the kernel
   route point to the field version?

3. **Blueprint scope.** 147 routes in kernel.py vs 112 in blueprints.
   Should more kernel routes migrate to blueprints? The kernel is 8404 lines
   and hard to navigate. Candidate migrations: /compose, /codex, /agriculture,
   /guild, /kala, /hexfield.

4. **atlas_330 relationship.** The kala app in atlas_330 now calls
   /jyotish/calendar in atlas_core. This cross-repo dependency works but
   creates a coupling. Should atlas_330 apps be migrated into atlas_core,
   or should the boundary be preserved with the dependency documented?

## Jyotisha Layer

5. **Krishna paksha Devi ordering.** In the Krishna fortnight, do the 15
   Nitya Devis map in reverse order (Citra→Kameshvari) or forward repeat?
   `tithi_master.csv` uses forward repeat. Tantraraja tradition uses reverse.

6. **Ayanamsha default.** swe Lahiri is the current default. The lagna
   differs from natal.json by 4.46° (ASC computation method variance). Should
   the system offer a "match natal.json" mode using the custom ayanamsha
   parameter, or treat the swe Lahiri computation as authoritative?

7. **Speculative yantra geometry.** 6 of 15 Nitya Devi yantras have
   SPECULATIVE geometry (no source text describes their form). Should the
   engine:
   (a) Include them with a reduced confidence weight?
   (b) Include them but visually flag them as speculative?
   (c) Omit them until attested?

## Research

8. **Bat T=12 verification.** The vertebral primes paper claims the bat
   (*Pipistrellus*) shares the human presacral formula C7 T12 L5. This is
   from Vaughan et al. (textbook). Should we pursue genus-level verification
   from primary osteological literature before sharing the paper?

9. **Kp analysis pipeline.** The two-source paper references geomagnetic
   and tidal computations that aren't in the repo. Should we build
   `research/scripts/kp_tidal_analysis.py` for reproducibility, or is the
   paper citation sufficient?

10. **Paper format.** Current papers are in markdown. The older atlas_330
    paper is in Typst (.typ). Should new papers be written in Typst for
    typeset quality, or stay in markdown for ease of authoring?

## Sound

11. **Devi raga vs nakshatra raga.** When the Devi raga (from tithi) differs
    from the Moon's nakshatra raga (from transit), which dominates? Options:
    (a) Devi raga during observances, nakshatra raga otherwise
    (b) Blend (0.5/0.5) always
    (c) Devi raga fades in at tithi boundaries, nakshatra sustains between

12. **Rhythm voice volume.** The SC rhythm task plays at 0.04-0.06 amplitude.
    Is this audible enough on the MOTU M2? Should it be louder during high
    wave activation?

## Outreach

13. **natal.json in repo.** Contains personal birth data (date, time, place,
    full chart). Must be excluded from any public repository. Should we:
    (a) Add it to .gitignore now (before any public push)?
    (b) Create an anonymized example_natal.json for the repo?
    (c) Load natal data from an environment variable or config file?

14. **Paper audience.** The two-source interference paper makes mathematical
    claims (aspect theory = harmonic selection) alongside speculative claims
    (Sri Yantra region count). Should these be:
    (a) Published together (current state)?
    (b) Split into two papers (math paper + speculation paper)?
    (c) Published with the speculative parts in a clearly marked appendix?

15. **Demo mode.** For showing Atlas to others, should there be a "demo"
    mode that uses a sample chart (not personal natal data) and runs without
    SC audio? What should it show?
