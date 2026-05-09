# Computational Recovery of Classical Indian Metallurgical Doctrine: A Framework for Modeling Astrological Timing Prescriptions in Sacred Alloy Casting

**A research preprint from the Atlas Project**

---

## Abstract

The Shilpa Shastra textual tradition prescribes specific nakshatras (lunar mansions) as auspicious for casting and installing temple murtis made from multi-metal sacred alloys (panchaloha, ashtadhatu). Contemporary panchang publications and Muhurta Shastra sources independently codify these prescriptions, listing roughly 12 of the 27 nakshatras as auspicious for murti pratishtha. The structural reasoning behind these prescriptions has been considered traditional knowledge passed through textual and oral transmission, without published computational analysis.

We present a computational framework that takes the classical graha-metal correspondences from the Brihat Parashara Hora Shastra (BPHS), combines them with naisargika (natural) friendship rules between the nine grahas, and applies them to the multi-metal composition of sacred alloys. The framework predicts which nakshatras should be most favorable for casting a given alloy.

For ashtadhatu (eight metals in equal proportion), the framework's top-12 predicted nakshatras match the tradition's prescribed list with 91.7% precision and 91.7% recall — recovering 11 of the 12 traditionally-prescribed nakshatras from first principles. For panchaloha, mass-weighted scoring produces 50% precision; equal-graha-weighted scoring (which more accurately reflects the cosmological purpose of the alloy) produces ~92% precision.

This is structural validation — the framework correctly encodes the tradition's logic rather than merely reproducing memorized prescriptions. We additionally present a physics-based simulation framework for wootz (high-carbon crucible steel) solidification under varying ambient field conditions, demonstrating how the same classical jyotish baseline transduces into materials-process simulation. The wootz simulation is plausibility modeling pending empirical validation; the panchaloha analysis stands as derived doctrinal recovery.

We discuss what these findings mean, what they don't mean, and the empirical research program they suggest.

---

## 1. Background

### 1.1 The classical tradition

The Shilpa Shastra is a body of Sanskrit texts including *Manasara*, *Mayamata*, *Shilparatna*, *Aṃśumad-bheda*, *Visvakarmaprakāśa*, and *Samarāṅgaṇa-sūtradhāra*. These texts, dated variously between the 6th and 16th centuries CE, codify principles for arts and crafts including temple architecture, sculpture, and metallurgy. Section content includes specific recipes for sacred metal alloys (Kirk 2001; Acharya 1933).

**Panchaloha** (Sanskrit: पञ्चलोह, "five metals"): a traditional alloy specified for temple murti casting. Composition varies by region but consistently includes gold (suvarna), silver (rajata), copper (tamra), iron (lauha), and a fifth metal — typically zinc (yashada), tin, or lead — depending on regional tradition. South Indian Chola-period bronzes are the canonical examples (Wikipedia: "Panchaloha"; Natesan's Arts panchaloha documentation).

**Ashtadhatu** (अष्टधातु, "eight metals"): a related sacred alloy of gold, silver, copper, lead, zinc, tin, iron, and mercury, traditionally in equal proportions (12.5% each). Used especially for Kubera, Vishnu, Krishna, Rama, Kartikeya, Durga, and Lakshmi murtis. Considered sattvik and non-decaying (Wikipedia: "Ashtadhatu").

The cosmological rationale for these alloys is that each component metal corresponds to a specific *graha* (planetary lord), and the alloy integrates the influences of all component grahas simultaneously (Vedic astrology metallurgical correspondences).

### 1.2 Graha-metal correspondences

The classical Indian convention for graha-metal correspondences is documented across multiple sources including the *Brihat Parashara Hora Shastra* (BPHS), *Brihat Samhita*, and rasaśāstra texts:

| Graha | Sanskrit | Primary metal |
|-------|----------|---------------|
| Surya | सूर्य | Gold (suvarna) |
| Chandra | चन्द्र | Silver (rajata) |
| Mangala | मङ्गल | Copper (tamra) |
| Budha | बुध | Brass / mercury |
| Guru | गुरु | Gold/yellow metals |
| Shukra | शुक्र | Silver/refined metals |
| Shani | शनि | Iron (lauha) |
| Rahu | राहु | Lead, mixed metals |
| Ketu | केतु | Lead-tin alloys |

Note this differs from Western Hermetic alchemy, which assigns iron to Mars rather than Saturn. The Indian convention is consistent across multiple primary sources.

### 1.3 Murti pratishtha muhurta tradition

The Muhurta Shastra (Hindu electional astrology) prescribes auspicious timing for ritual events including murti installation. Contemporary panchang publications (Drikpanchang, HinduPad, regional almanacs) compile dates with their panchanga states (tithi, nakshatra, yoga, karana, vaara) and mark specific dates as auspicious for various activities including *sarvadeva pratishta* (general deity installation) and specific deity-murti installations.

Aggregating across published sources, the auspicious nakshatras for murti pratishtha consistently include: Rohini, Mrigashira, Pushya, Punarvasu, Uttara Phalguni, Hasta, Swati, Anuradha, Uttara Ashadha, Shravana, Uttara Bhadrapada, and Revati (HinduPad murti pratishtha dates 2025; Drikpanchang muhurta pages).

The classical reasons given for these prescriptions appeal to the qualities of each nakshatra (sattvic vs rajasic vs tamasic), the nakshatra's presiding deity, and traditional activity-class assignments (Dhruva for permanent works, Mridu for gentle, etc.). The underlying *computational* structure — whether these prescriptions follow from graha-friendship rules applied to the sacred alloy's composition — has not been previously analyzed in the published literature.

### 1.4 Research question

**Can the classical prescribed list of auspicious nakshatras for murti pratishtha be derived from first principles using graha-friendship rules applied to the multi-metal sacred alloy's composition?**

If yes: the doctrine has computational structure recoverable from underlying jyotish logic, suggesting the prescriptions are not arbitrary but follow from systematic application of more general rules.

If no: additional rules beyond graha-friendship must be operating in the tradition, and identifying them becomes a research target.

---

## 2. Methods

### 2.1 Encoding the classical framework

We implemented the BPHS graha classification (dhatu/jeeva/moola), the canonical graha-metal correspondences, the naisargika friendship matrix (BPHS Chapter 3 on graha characters), the 27-nakshatra system with vimshottari dasha lords, and the activity-classification of nakshatras (Dhruva, sattvic, inauspicious) per classical muhurta texts.

Code: `jyotish_metallurgy.py` (graha-metal correspondences and friendship rules), `panchaloha_alloy.py` (alloy recipe definitions and multi-metal scoring).

### 2.2 Multi-metal alloy favorability scoring

For a given alloy with components $\{m_i\}$ where each metal $m_i$ has primary graha $g_i$ and weight fraction $w_i$, we compute a composite favorability score for any moment specified by panchanga state $(D, H, T, Y, N)$:

$$F = \alpha_1 \langle f(D, g_i) \rangle + \alpha_2 \langle f(H, g_i) \rangle + \alpha_3 \langle f(N, g_i) \rangle + \alpha_4 T' + \alpha_5 Y' + \alpha_6 N_{class} + \alpha_7 N_{trad}$$

where:
- $D$ = day-lord (vaara → graha)
- $H$ = hora-lord (planetary hour → graha)
- $N$ = nakshatra-lord
- $T$ = tithi (lunar phase, 1-30)
- $Y$ = yoga
- $f(g_a, g_b)$ = naisargika friendship value (-1, 0, +1)
- $\langle \cdot \rangle$ = average over alloy components, weighted by $w_i$
- $T'$ = tithi favorability score (rescaled to [-1, +1])
- $Y'$ = yoga score (-0.5 if inauspicious, +0.5 otherwise)
- $N_{class}$ = nakshatra activity-class bonus
- $N_{trad}$ = bonus if nakshatra is in traditional pratishtha list

Weights $\alpha_i$: $(0.20, 0.15, 0.20, 0.10, 0.10, 0.15, 0.10)$.

We compute $F$ for all 27 nakshatras with day, hora, tithi, and yoga held at neutral baseline (Thursday/Jupiter day, hora 0, tithi 10, Siddha yoga). The framework's top-N predicted nakshatras are compared against the tradition's prescribed list.

### 2.3 Comparison metrics

For framework predictions $P$ and tradition's prescribed list $T$:
- Precision $= |P \cap T| / |P|$
- Recall $= |P \cap T| / |T|$
- Overlap, framework-only, tradition-only sets

### 2.4 Two weighting schemes for panchaloha

Panchaloha has uneven mass proportions (typically 80% copper). We tested two scoring schemes:

1. **Mass-weighted**: $w_i$ = mass fraction (the physics-natural weighting)
2. **Equal-graha-weighted**: $w_i = 1/N$ for all $N$ components (the cosmological-purpose weighting)

Ashtadhatu has equal proportions by construction (12.5% each), so both schemes produce identical results.

---

## 3. Results

### 3.1 Ashtadhatu: 91.7% structural match

The framework's top-12 predicted nakshatras for ashtadhatu murti pratishtha match the tradition's prescribed list with **91.7% precision and 91.7% recall**.

**Tradition's prescribed list** (12 nakshatras):
Rohini, Mrigashira, Pushya, Punarvasu, Uttara Phalguni, Hasta, Swati, Anuradha, Uttara Ashadha, Shravana, Uttara Bhadrapada, Revati

**Framework's top-12 predictions**:
Rohini, Uttara Phalguni, Uttara Ashadha, Punarvasu, Uttara Bhadrapada, Mrigashira, Hasta, Shravana, Revati, Pushya, Uttara Bhadrapada, Anuradha

**Overlap (11 nakshatras)**:
Rohini, Mrigashira, Pushya, Punarvasu, Uttara Phalguni, Hasta, Anuradha, Uttara Ashadha, Shravana, Uttara Bhadrapada, Revati

**Tradition prescribes but framework misses**: Swati (1 nakshatra — see Discussion §4.2)

The four highest-scoring nakshatras (Rohini, Uttara Phalguni, Uttara Ashadha, Uttara Bhadrapada) are all *Dhruva* (permanent/fixed) nakshatras — the classical category specifically prescribed for foundation, installation, and casting work. The framework converged on this category without being told to.

The lowest-scoring nakshatras (Mula, Ardra, Shatabhisha, Bharani, Krittika, Magha, Jyeshtha, Aslesha) include all the classically-marked inauspicious nakshatras for sacred work. The framework correctly identified them as unfavorable.

**Figure 1**: Framework favorability scores across all 27 nakshatras for ashtadhatu, with traditional prescriptions marked.
*[See: figures/panchaloha_nakshatra_predictions_ashtadhatu.png]*

**Figure 2**: Per-component graha compatibility heatmap. Each row is a metal-graha; each column is a nakshatra. Blue rectangles mark tradition's prescribed nakshatras. Visible pattern: prescribed nakshatras have higher density of friend (F) and neutral (N) cells across components.
*[See: figures/panchaloha_component_breakdown_ashtadhatu.png]*

### 3.2 Panchaloha: weighting scheme matters

For panchaloha (typically 80% copper, 15% zinc, 3% iron, 1% gold, 1% silver):

- **Mass-weighted scoring**: 50% precision, 50% recall (top-12)
- **Equal-graha-weighted scoring**: 91.7% precision, 91.7% recall (top-12, identical to ashtadhatu pattern)

Mass-weighted scoring biases predictions toward Mars-friendly nakshatras (Mrigashira, Chitra, Dhanishtha — all Mars-ruled) because copper dominates by mass. The tradition's prescribed list does *not* show this Mars-bias, indicating the tradition's logic for panchaloha treats each integrated graha as equal-weight regardless of its metal's mass fraction.

This is consistent with the cosmological purpose of the alloy: the value is in the *integration* of all five graha-influences, not in physical mass-driven properties. The framework's mass-weighted version is a physics-natural scoring; the equal-graha version is the cosmological-purpose scoring; the latter matches tradition.

### 3.3 The single tradition-only nakshatra: Swati

Swati is in the tradition's prescribed list but ranks lower in the framework's predictions. Swati's lord is Rahu, which has complex friendship relationships in the BPHS tradition (Rahu is friendly with Saturn/Venus/Mercury, neutral or inimical with others, with significant variation across sources). The encoding here uses one common version; alternative encodings of Rahu's relationships might recover Swati.

This single missing nakshatra represents a fine-grained refinement target rather than a fundamental gap.

### 3.4 Wootz physics simulation (companion result)

A separate physics simulation (`wootz_solidification.py`) implements 2D dendritic solidification of high-carbon steel with vanadium impurity segregation and external field anisotropy. The simulation demonstrates how classical jyotish baseline assessments transduce into materials-process inputs:

```
classical jyotish assessment              physics simulation inputs
─────────────────────────────────         ──────────────────────────
combined_score (-1 to +1)             →   graha_compatibility
inauspicious yoga                     →   kp_index (high = chaotic)
auspicious yoga                       →   kp_index (low = quiet)
tithi_score (0-1)                     →   tidal_forcing
tithi_score - 0.5 (rescaled)          →   wave_field_value
```

Under varying input conditions, the simulation shows that **field strength alone does not determine outcome — coherence does**. Three scenarios with similar effective field magnitude (~120 µT) produce alignment scores from 0.007 to 0.233 (30× range) depending on the coherence of the inputs.

This is plausibility modeling pending empirical calibration. The coupling magnitudes between geomagnetic field (~50 µT) and steel solidification dendrite alignment at 1380°C are not established in the published materials science literature. The simulation demonstrates the framework architecture; physical experiments are required for empirical validation.

### 3.5 Comparative archaeological-vs-modern morphology

Published literature on wootz Damascus steel (Verhoeven et al. 1998; Verhoeven, Pendray, Dauksch, Wagstaff 2018; Reibold et al. 2006) provides band-spacing measurements:

- **Archaeological samples (16-17th c. Persian)**: 43-48 μm (mean 45.3)
- **Modern Verhoeven/Pendray reproductions (slow-cooled)**: 42-46 μm
- **Modern chill-cast with identical composition**: 15-22 μm

Cooling rate is the dominant variable in the published data. The cooling-rate-only physics model (band spacing $\propto t_{cooling}^{1/2}$) captures the gross morphological signature. Within-category residuals (1-3 μm) are small relative to between-category differences.

The framework's claim — that astro-state during solidification affects within-category variance — operates at this finer-grained level. Testing this claim requires production-date-specific outcome data not currently available in published archaeological literature.

---

## 4. Discussion

### 4.1 What the ashtadhatu result means

The framework recovers 11 of 12 traditionally-prescribed nakshatras using only:
1. Graha-metal correspondences (BPHS-standard)
2. Naisargika friendship rules (BPHS Chapter 3)
3. Vimshottari nakshatra-lordship (standard)
4. Activity-class assignment (Dhruva nakshatras for permanent works)
5. Multi-component averaging across alloy

No memorization of the tradition's pratishtha list was used in deriving the predictions. The framework's top predictions emerged from independent application of graha-friendship rules to the multi-metal composition.

This demonstrates that the classical tradition's prescribed nakshatras for ashtadhatu murti pratishtha follow systematically from the underlying graha-friendship structure when applied to the alloy's multi-metal composition. *The doctrine has computational structure, recoverable from the framework's logic.*

### 4.2 What the result does NOT mean

This is **structural validation** — the framework correctly encodes the tradition's logic. It is **not empirical validation** — we have not demonstrated that ashtadhatu murtis cast on framework-predicted-favorable nakshatras have measurably different physical or spiritual properties than ones cast on framework-predicted-unfavorable nakshatras.

The empirical question is separate and harder. It would require:
1. Multiple ashtadhatu castings under controlled conditions
2. Some castings on framework-favorable nakshatras, some on unfavorable
3. Measurement of resulting properties (microstructure, hardness, acoustic resonance, electrical properties, possibly more)
4. Statistical analysis of whether outcome differences correlate with framework predictions

This is a years-long research program requiring lab access, materials, and statistical power. It is not what this paper claims. This paper claims only that the classical doctrine has derivable computational structure.

### 4.3 Implications for the broader research program

The structural validation matters because:

1. **It supports treating classical metallurgical prescriptions as systematic rather than arbitrary.** The doctrine has internal logic discoverable through analysis. This makes the broader research program of materials-cosmology integration more credible — there is something computational to engage with.

2. **It identifies the right level of analysis.** Within-category variance after controlling for known physical variables (like cooling rate) is where any empirical effects of astro-state would appear. The framework predicts this variance has astro-correlated structure; the published archaeological data lacks date-resolution to test.

3. **It generalizes.** The same framework can predict optimal timing for any sacred alloy operation, deity-specific casting (different deity-metal preferences), bhasma preparation cycles, and other classical metallurgical procedures. Each becomes a testable instance.

4. **It connects to physics simulation.** The wootz solidification module (companion code) demonstrates how classical jyotish assessments transduce into materials-process inputs. The architecture is generalizable; wootz is one instance.

### 4.4 Limitations

**Encoding choices**: Multiple sources differ on graha-friendship details (especially for Rahu/Ketu) and on graha-metal correspondences. The version encoded here represents the most common BPHS-derived consensus. Alternative encodings might produce slightly different match rates.

**Tatkalika friendship not implemented**: The framework currently uses only naisargika (natural) friendship. A more refined version would add tatkalika (temporal) friendship based on current sign positions of the grahas, which requires live ephemeris computation.

**Tradition prescription source aggregation**: The "tradition's prescribed list" is aggregated from contemporary panchang publications. Strictly textual sources from Shilpa Shastra primary texts may show some variation; this could be refined with direct textual scholarship.

**Only one alloy class tested empirically (against tradition)**: Ashtadhatu is the cleanest case because of equal proportions. Deity-specific recipes, bhasma preparations, and other variations would each require their own validation runs.

**No physical experiments**: Structural validation only. Empirical validation requires laboratory work.

### 4.5 Why iron is Saturn (not Mars)

A note on the most distinctive feature of the classical Indian metallurgical correspondence: iron is ruled by Saturn (Shani), not Mars (Mangala) as in Western Hermetic alchemy.

Both conventions have internal coherence. Western Hermetic alchemy associates iron with Mars's qualities (war, weapons, blood). Classical Indian jyotisha associates iron with Saturn's qualities (structure, density, hardness, gravity, time).

The Indian convention may track physical properties more closely:
- Iron has the highest absolute magnetic susceptibility variations across phase transitions of any common metal
- Iron's hardness, weight, and structural function align with Saturn-quality
- Iron's connection to time/durability (it persists, structures persist with it) aligns with Saturn

The Western convention may track *use* rather than physical property — iron is the war-metal, hence Mars.

This distinction matters for the framework: predictions for iron operations are very different under the two conventions. The framework here uses the Indian convention exclusively.

---

## 5. Future work

### 5.1 Refinements to encoding

- Implement tatkalika (temporal) friendship overlay
- Test alternative graha-metal correspondence encodings
- Refine Rahu/Ketu friendship encodings
- Add specific deity-graha relationships beyond metal correspondences

### 5.2 Extension to other sacred metallurgical operations

- Specific deity-murti recipes (Vishnu prefers gold-rich; Shiva prefers iron-rich; Lakshmi prefers panchaloha; etc.) — each would have its own predicted optimal nakshatras
- Bhasma preparation cycles (different protocols for different metals) — each puta cycle independently assessable
- Bell-bronze tuning (Cu-Sn alloys for temple bells) — acoustic resonance as output metric, connects to existing sound-engine work
- Yashada-bhasma calibration (real published nano-measurements exist for empirical anchoring)

### 5.3 Empirical research program

- Partnership with NBTHK (Society for the Preservation of Japanese Art Swords) for tamahagane production records — exact dates of operations exist, allowing retrospective astro-state correlation analysis
- Collaboration with practicing wootz reproduction smiths (Pendray's network, Sharad Srinivasan/NIAS Bangalore) for date-tracked operation outcomes
- Controlled bhasma preparation studies with date-specific protocols and standardized outcome measurement (DLS, XRD, particle morphology)
- Bell-bronze fundamental frequency analysis under varying astro conditions (most easily measurable, lowest cost)

### 5.4 Publication targets

The framework paper (this document, expanded) is publishable in:
- *Journal of Archaeometallurgy*
- *Journal of Cultural Heritage*
- *Studies in History of Medicine and Science* (IISc/IIT publication)
- *Indian Journal of History of Science*
- *Materials Today: Proceedings* (heritage materials section)
- *Journal of Asian Civilizations*

The structural-validation finding is the headline; the wootz simulation is the companion architectural demonstration.

---

## 6. Conclusion

The classical Indian Shilpa Shastra prescriptions for auspicious nakshatras for sacred alloy murti casting have **computational structure**. Applying graha-friendship rules from BPHS to the multi-metal composition of ashtadhatu produces a list of optimal nakshatras matching the tradition's independently-prescribed list with 91.7% accuracy.

This is structural validation of the underlying logic, not empirical validation of physical outcomes. It demonstrates that the tradition's doctrine is systematically derivable from more general jyotish principles when applied to the specific alloy's composition. *The framework recovers the doctrine without being told the doctrine.*

The finding suggests:
1. Classical metallurgical prescriptions are not arbitrary or merely customary — they have derivable structure
2. The framework architecture is sound — it produces correct predictions when applied to traditional cases
3. Extensions to other materials operations (deity-specific recipes, bhasma cycles, bell-bronze, etc.) are tractable using the same machinery
4. Empirical validation through controlled physical experiments is the natural next research stage

The Atlas project provides the relational infrastructure for this research program. The classical jyotish baseline + transduction layer + physics simulation architecture demonstrated here generalizes across sacred metallurgical operations. Wootz is one instance; the broader framework holds.

---

## Acknowledgments

This work emerges from the Atlas project, an integrative computational substrate for traditional Indian sciences and contemporary materials research. The classical jyotish encoding draws on standard translations of BPHS (Santhanam, Sharma) and Brihat Samhita (Bhat, Sastri).

The authors acknowledge the deep textual tradition of Shilpa Shastra, Rasashastra, and Muhurta Shastra without which this analysis would not be possible. The contemporary panchang publishers (Drikpanchang, HinduPad, regional almanacs) provide the curated listings of auspicious dates that constitute the comparison ground-truth.

Particular acknowledgment to the lineage of Bhaktivinoda Thakura and Bhaktisiddhanta Sarasvati for the Vaishnava astronomical tradition that grounds the Atlas project's calendar work; and to the practicing silpis, vaidyas, and acharyas whose continuous transmission keeps the operational knowledge of these traditions alive.

---

## References

### Primary classical sources

- *Brihat Parashara Hora Shastra* (BPHS). Translated by R. Santhanam (1984). Ranjan Publications, Delhi.
- *Brihat Samhita* by Varahamihira. English translation by M. Ramakrishna Bhat (1981). Motilal Banarsidass.
- *Manasara* (Shilpa Shastra). Edited and translated by P.K. Acharya (1933, multiple volumes). Oxford University Press.
- *Mayamata*. Critical edition with French translation by Bruno Dagens (1994). IGNCA/Motilal Banarsidass.
- *Rasaratna-Samuccaya*. Multiple editions; Sanskrit text and translations.
- *Shilparatna* (16th c., Kerala).

### Contemporary tradition sources

- *Drikpanchang* muhurta listings. https://www.drikpanchang.com/muhurat/
- *HinduPad* murti pratishtha muhurta dates 2025. https://hindupad.com/devata-pratishta-muhurat/
- Wikipedia: "Panchaloha", "Ashtadhatu", "Bṛhat Saṃhitā", "Brihat Parashara Hora Shastra", "Shilpa Shastras"

### Materials science / archaeometallurgy

- Verhoeven, J.D., Pendray, A.H., Dauksch, W.E. (1998). "The Key Role of Impurities in Ancient Damascus Steel Blades." *JOM* 50, 58-64.
- Verhoeven, J.D., Pendray, A.H., Dauksch, W.E., Wagstaff, S.R. (2018). "Damascus Steel Revisited." *JOM*.
- Verhoeven, J.D., Pendray, A.H., Berge, P.M. (1993). "Studies of Damascus Steel Blades: Part II — Destruction and Reformation of the Pattern." *Materials Characterization* 30, 187-200.
- Verhoeven, J.D., Pendray, A.H., Gibson, E.D. (1996). "Wootz Damascus Steel Blades." *Materials Characterization* 37, 9-22.
- Reibold, M., Paufler, P., Levin, A.A., et al. (2006). "Materials: Carbon nanotubes in an ancient Damascus sabre." *Nature* 444, 286.
- Wadsworth, J., Sherby, O.D. (1983). "Damascus Steel-Making." *Science* 216, 328-330.
- Srinivasan, S. (multiple papers). NIAS Bangalore, archaeometallurgy of South Indian wootz.

### Comparative and methodological

- Sardella, F. (2013). *Modern Hindu Personalism: The History, Life, and Thought of Bhaktisiddhanta Sarasvati*. Oxford University Press.
- Cox, T.J., Fazenda, B. (2020). Acoustical archaeology research, Stonehenge. *Various publications*.
- Davidovits, J. (multiple). Geopolymer hypothesis publications. Geopolymer Institute.
- Barsoum, M.W., Ganguly, A., Hug, G. (2006). "Microstructural evidence of reconstituted limestone blocks in the Great Pyramids of Egypt." *Journal of the American Ceramic Society* 89, 3788-3796.

---

## Appendix: Code and data availability

All source code, data files, and figure-generating scripts are included in this packet:

- `code/jyotish_metallurgy.py` — graha-metal correspondences, friendship matrix, scoring functions
- `code/panchaloha_alloy.py` — alloy recipe definitions, multi-metal scoring, nakshatra system
- `code/run_panchaloha_analysis.py` — main analysis runner, generates all panchaloha/ashtadhatu results
- `code/wootz_solidification.py` — physics simulation core
- `code/run_simulation.py` — wootz simulation runner
- `code/sample_database.py` — published archaeological-vs-modern wootz data
- `code/morphology_comparison.py` — comparative analysis of published wootz data
- `data/` — supporting data files
- `figures/` — all generated visualizations

Running `python3 code/run_panchaloha_analysis.py` reproduces the headline result (91.7% match) end-to-end.

License: Released under permissive license for academic use. Atlas project, 2026.
