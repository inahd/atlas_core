# Classical Jyotish Metallurgical Baseline

*Atlas materials-process compute layer — classical foundation. Wootz physics simulation sits within this framework rather than beside it.*

---

## What this establishes

A working computational baseline for classical Indian metallurgical timing analysis, derived from BPHS (Brihat Parashara Hora Shastra), Brihat Samhita (Varahamihira), and rasaśāstra textual tradition. Implements:

1. **Graha-metal correspondences** — which planetary lord governs which metal
2. **BPHS dhatu/jeeva/moola classification** — the three-fold framework distinguishing metallurgy-relevant grahas from those governing living beings or plants
3. **Naisargika friendship matrix** — the classical compatibility table between grahas, encoded from BPHS Chapter 3
4. **Tithi favorability** — lunar-cycle context for operations
5. **Yoga screening** — atmospheric-quality filtering with explicit list of inauspicious yogas
6. **Hora system** — planetary-hour resolution within each day
7. **Optimal-window scanning** — multi-day sweep producing ranked favorable times per metal
8. **Transduction to physics simulation** — classical assessment values become AstroFieldConditions inputs to the materials-process simulation

---

## The graha-metal correspondences (classical Indian)

| Graha | Primary metal | Dhatu class (BPHS) | Cosmological signature |
|-------|--------------|-------------------|------------------------|
| Surya (Sun) | Gold (Suvarna) | Jeeva | Solar charge, tejas, central authority |
| Chandra (Moon) | Silver (Rajata) | Dhatu | Lunar fluidity, manas |
| Mangala (Mars) | Copper (Tamra) | Dhatu | Tapas, fire-transformation, blood |
| Budha (Mercury) | Brass / mercury | Jeeva | Intelligence, transformation |
| Guru (Jupiter) | Gold (shared) | Jeeva | Wisdom, expansion, sattva |
| Shukra (Venus) | Silver / platinum | Moola | Rasa, beauty, refinement |
| Shani (Saturn) | **Iron (Lauha)** | Dhatu | **Structure, time, density, hardness** |
| Rahu | Lead, mixed metals | Dhatu | Amplification, distortion |
| Ketu | Lead-tin alloys | Jeeva | Dissolution, ash |

**Critical observation**: The classical Indian convention places iron under Saturn, not Mars. This differs from Western Hermetic alchemy (which assigns iron to Mars). The convention matters operationally — wootz iron operations follow Saturnine timing logic in the Indian tradition.

---

## What the baseline produces

For any metal-graha, the framework computes favorability scores across timing windows by combining:

- **Day-lord compatibility** (vaara → graha): does the day's ruling graha befriend the target metal's graha?
- **Hora-lord compatibility** (planetary hour → graha): does the current hour's ruler befriend the target?
- **Tithi favorability** (lunar phase): does the lunar context support material work?
- **Yoga assessment** (atmospheric quality): is the current yoga inauspicious?
- **Practitioner compatibility** (optional): does the practitioner's natal grahas support work on this metal?

Combined into a single score from -1 (highly inauspicious) to +1 (highly favorable).

---

## Headline finding from the analysis

When scanning a 30-day window for **Iron (Saturn-metal) operations**:

- **Best windows**: Saturday-Saturn hora combinations during waxing-moon Saptami/Trayodashi tithis with non-disruptive yogas
- **Worst windows**: Sundays (Sun-Saturn enmity) on Krishna-paksha Chaturdashi or Amavasya with inauspicious yogas (Aindra, Parigha, Vyatipata)
- The framework correctly recovers the classical principle: **Saturday is naturally optimal for iron operations** because Saturn rules both the day and the metal

When scanning the same window for **Gold (Sun-metal) operations**:

- The pattern inverts: Sundays become favorable, Saturdays become unfavorable
- Sun-Saturn enmity produces opposite outcomes for the two metals on the same days
- This is the framework demonstrating internally consistent classical logic

**Each metal has its own characteristic favorability profile derived from its graha's relationships.** The framework is not just labeling days as good/bad in general — it's producing metal-specific timing predictions consistent with classical doctrine.

---

## Connection to physics simulation

The classical assessment produces parameter values that feed directly into the wootz physics simulation:

```
classical jyotish assessment              physics simulation inputs
─────────────────────────────────         ──────────────────────────
combined_score (-1 to +1)             →   graha_compatibility
inauspicious yoga (Vyatipata etc.)    →   kp_index (high = chaotic)
auspicious yoga                       →   kp_index (low = quiet)
tithi_score (0-1)                     →   tidal_forcing
tithi_score - 0.5 (rescaled)          →   wave_field_value
```

This is the **transduction layer** that connects cosmological state to materials process. The classical jyotish framework selects which conditions to test; the physics simulation generates testable predictions about material outcomes.

For wootz specifically: a Saturn's day with Saturn hora on Trayodashi tithi with Shiva yoga produces:
- High graha_compatibility (+0.73) → strong field coherence
- Low kp_index (1.5) → quiet ambient field
- Strong tidal_forcing (0.8) → coherent lunar contribution
- Positive wave_field_value (+0.42) → supportive Atlas wave field

The simulation under these inputs predicts: **higher band alignment, more pronounced carbide segregation, better Damascus pattern** than under inverted inputs (Sunday-Sun-hora on Krishna-Chaturdashi).

---

## Generalization

The same framework applies to any metallurgical operation that can be characterized by:

1. **Target metal's graha** (lookup in correspondences table)
2. **Operation timing** (panchanga state at proposed start time)
3. **Practitioner's natal chart** (optional enhancement)

This means **panchaloha alloy casting**, **bhasma preparation cycles**, **silver work**, **copper alloy operations**, and **gold-craft** all use the same baseline. Only the target metal's graha changes — the framework then identifies windows where that specific graha's friends dominate the panchanga.

For **panchaloha (five-metal alloy)**, the framework would assess compatibility for each component metal's graha simultaneously, producing windows where ideally all five grahas are harmoniously placed. *This is the cosmologically richest case and would be the natural next implementation.*

For **bhasma puta cycles**, the timing of each puta (incineration cycle) can be assessed independently — different stages of bhasma preparation may be best suited to different graha-conditions.

---

## Caveats and honest scope

**This is the classical doctrinal framework computationally encoded, not empirical validation.** The framework expresses what BPHS and Brihat Samhita say should be favorable. Whether actual material outcomes correlate with these timing predictions is a separate empirical question.

**Variations exist between sources.** The graha-metal correspondences are standardized here per the most common classical Indian convention, but individual texts vary (especially regarding which graha rules iron vs steel). The encoded version follows mainstream BPHS-derived consensus.

**The friendship matrix is naisargika (natural).** It does not include tatkalika (temporal) friendships that depend on specific moment-of-time graha positions. Adding tatkalika layer would require live ephemeris computation and a more sophisticated scoring model.

**Practitioner compatibility is simplified.** A full assessment would consider practitioner's lagna, dasha period, and current transits relative to natal chart. This baseline uses only natal-graha relationships to target metal.

---

## Files

- `jyotish_metallurgy.py` — core module (correspondences, friendship, scoring functions)
- `run_jyotish_analysis.py` — analysis runner with visualizations
- `jyotish_friendship_matrix.png` — graha friendship heatmap
- `jyotish_windows_iron_steel_lauha.png` — iron/Saturn window distribution
- `jyotish_windows_gold_suvarna.png` — gold/Sun window distribution
- `jyotish_windows_copper_tamra.png` — copper/Mars window distribution
- `jyotish_windows_silver_rajata.png` — silver/Moon window distribution

---

## Position in the Atlas architecture

This module is the **classical baseline** that the wootz physical simulation extends. The architecture flows:

```
                    ┌─────────────────────────────────────┐
                    │  CLASSICAL JYOTISH BASELINE         │
                    │  (this module)                       │
                    │  - graha-metal correspondences       │
                    │  - friendship matrix                 │
                    │  - tithi/yoga/hora favorability      │
                    │  - optimal window scanning           │
                    └────────────────┬────────────────────┘
                                     │
                                     ▼ (transduction)
                    ┌─────────────────────────────────────┐
                    │  PHYSICS SIMULATION                  │
                    │  (wootz_solidification.py)           │
                    │  - dendritic growth                  │
                    │  - vanadium segregation              │
                    │  - field-coupled anisotropy          │
                    │  - band alignment metrics            │
                    └────────────────┬────────────────────┘
                                     │
                                     ▼
                          predicted material outcomes
                          (back into Atlas relational graph)
```

**Wootz now sits within the framework rather than alongside it.** The same machinery applies to any other Vedic alloy operation: panchaloha, ashtadhatu, bhasma cycles, bell-bronze tuning, gold work, silver work. Each becomes an instance of the same pattern with different target graha and different physics-simulation specifics.

This is what makes the framework fungible. *One baseline; many materials; consistent logic.*

---

## Atlas integration path

To wire into atlas_core on kanjira:

1. **Replace synthetic panchanga** in `find_optimal_windows()` with calls to Atlas's existing `panchanga_engine`. The engine already produces tithi, nakshatra, yoga, karana, vaara — these become inputs rather than synthetic placeholders.

2. **Wire to ephemeris** for current/historical analysis. Atlas's `jyotisha_engine.py` computes graha positions; cross-reference with current-time scanning becomes meaningful when grounded in real ephemeris.

3. **Add tatkalika layer** for full friendship assessment. Requires live graha positions in signs to determine temporal friendship overlay on the naisargika base.

4. **Cross-reference with natal charts** in instance/personal/. Practitioner compatibility scoring becomes operationally meaningful.

5. **Expose via Flask routes**: `/jyotish/metallurgy/windows?metal=iron&days=30`, `/jyotish/metallurgy/assessment?date=...&metal=...`. Becomes part of Atlas's API surface alongside existing routes.

6. **Publish as reference dataset**: the classical correspondences, friendship matrix, and tithi favorability tables become CSVs in datasets/, queryable from the relational graph.

This is a focused 1-2 day Claude Code task on kanjira to wire the existing classical baseline into Atlas's live infrastructure.

---

## Summary

The classical jyotish metallurgical baseline is established and working. Wootz physics simulation now has its proper place: *within* the classical framework, not parallel to it. The architecture extends naturally to other Vedic alloys, bhasma preparations, and any metallurgical operation characterizable by graha correspondence.

The framework correctly recovers classical doctrine (Saturday-Saturn for iron, Sunday-Sun for gold, opposite patterns for grahas in enmity) and produces metal-specific timing predictions ready to feed into physics simulations.

Wootz simulation is no longer a standalone demonstration — it is one specific instance of a generalized framework Atlas now supports. The same pattern produces predictions for panchaloha, ashtadhatu, bhasma, and other classical operations. *The framework is fungible.*
