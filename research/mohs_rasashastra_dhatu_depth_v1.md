# Mohs Hardness and Classical Tissue-Depth Prescription: A Cross-Tradition Correlation Across Fourteen Gems

## Abstract

Across fourteen gems with documented classical rasaśāstra prescriptions to specific bodily tissues (dhātus), Mohs hardness correlates with the sapta-dhātu depth ordering at Spearman ρ = 0.828 (*p* ≈ 2.6 × 10⁻⁴; n = 14). The correlation is positive: softer gems are systematically prescribed for surface dhātus (rasa, rakta), harder gems for deeper dhātus (asthi, majjā, śukra). Leave-one-out sensitivity analysis confirms the result is not driven by any single observation; across all fourteen leave-one-out subsets the Spearman ρ ranges from +0.78 to +0.88, with every subset significant at *p* < 0.002. The result is reported with the full data table, aggregate-level source attribution to Bhāva-prakāśa, Rasa-ratna-samuccaya, Caraka Saṃhitā, and Suśruta Saṃhitā, and an explicit discussion of methodological gaps including the use of species-mean Mohs values rather than per-specimen measurement and the absence of per-verse source locators. We propose follow-up measurement against parīkṣā-graded specimens as the natural empirical extension. The Mohs scale (1812) and the sapta-dhātu depth ordering (~2,000+ years older) were developed independently and had no contact during their formation.

## 1. Introduction

This paper reports a single empirical result: across fourteen gems with documented classical rasaśāstra prescriptions to specific bodily tissues, contemporary Mohs hardness correlates with the classical sapta-dhātu depth ordering at Spearman ρ = 0.828 (*p* ≈ 2.6 × 10⁻⁴, n = 14). The correlation is positive and physically interpretable: softer gems are systematically prescribed for surface tissues, harder gems for deeper ones. We report the data, the method, the leave-one-out sensitivity analysis, and an honest accounting of methodological gaps.

The two scales involved are unrelated in their development. The Mohs scale of mineral hardness was introduced by Friedrich Mohs in 1812 as a comparative ordinal ranking based on scratch resistance. The sapta-dhātu depth ordering — *rasa* (plasma, surface) → *rakta* (blood) → *māṃsa* (muscle) → *meda* (adipose) → *asthi* (bone) → *majjā* (marrow / nervous tissue) → *śukra* (generative essence) — is established in the Caraka Saṃhitā and Suśruta Saṃhitā, the two foundational texts of classical Ayurveda, dated approximately to the first to fourth centuries CE and drawing on substantially older oral traditions. The two systems were developed across two thousand years and two continents with no documented historical contact.

The classical prescription literature pairs specific gems with specific dhātu-targets. Bhāva-prakāśa (~16th century), Rasa-ratna-samuccaya (~13th century), and the navaratna prescription compendia treat the gem-to-dhātu correspondence as part of a broader therapeutic system that also assigns each gem to a planetary ruler (*graha*), a constitutional type (*doṣa*), and a preparation protocol (*bhasmīkaraṇa*). For the present analysis we use only the gem-to-dhātu pairing.

The hypothesis tested here was generated within a research framework that treats classical śāstra as a primary source of structural information. The test reported in this paper is empirical and reproducible. The data, code, and computed statistics are available at the repository cited in §9; replication requires only the data file and a standard implementation of Spearman rank correlation.

## 2. Data

The dataset consists of fourteen gems, each with a documented classical rasaśāstra prescription to a single dominant dhātu-target. Mohs hardness values are species-mean values from standard mineralogical reference. Dhātu-targets are encoded as integer depth ranks (rasa = 1, rakta = 2, māṃsa = 3, meda = 4, asthi = 5, majjā = 6, śukra = 7) following the canonical sapta-dhātu sequence of the Caraka and Suśruta Saṃhitās.

| # | Gem | Sanskrit | Mohs | Dhātu-target | Depth (1–7) | Graha |
|---|---|---|---|---|---|---|
| 1 | Diamond | Vajra | 10.0 | śukra | 7 | Śukra |
| 2 | Pearl | Muktā | 3.5 | rasa | 1 | Candra |
| 3 | Coral | Pravāla | 3.5 | rakta | 2 | Maṅgala |
| 4 | Ruby (corundum) | Māṇikya | 9.0 | majjā | 6 | Sūrya |
| 5 | Sapphire (corundum) | Indranīla | 9.0 | asthi | 5 | Śani |
| 6 | Emerald (beryl) | Marakata | 7.75 | majjā | 6 | Budha |
| 7 | Topaz | Puṣparāga | 8.0 | majjā | 6 | Bṛhaspati |
| 8 | Hessonite (garnet) | Gomeda | 7.25 | asthi | 5 | Rāhu |
| 9 | Chrysoberyl | Vaiḍūrya | 8.5 | majjā | 6 | Ketu |
| 10 | Moonstone | Candrakānta | 6.0 | rasa | 1 | Candra |
| 11 | Lapis lazuli | Rājāvarta | 5.25 | rasa | 1 | N/A |
| 12 | Olivine | Pīloka | 6.75 | meda | 4 | N/A |
| 13 | Tourmaline | Vaikrānta | 7.25 | māṃsa | 3 | N/A |
| 14 | Quartz | Sphaṭika | 7.0 | majjā | 6 | N/A |

*Source attribution.* The gem-to-dhātu pairings are drawn from the classical prescription compendia: Bhāva-prakāśa, Rasa-ratna-samuccaya, and the standard navaratna prescription literature. The sapta-dhātu depth ordering is established in the Caraka Saṃhitā and Suśruta Saṃhitā as the canonical sequence of bodily tissues from surface to core. Per-verse locators for the individual gem-to-dhātu pairings are not compiled in the present dataset; attribution is at the aggregate level. We treat this as a known limitation of the dataset rather than a defect of the underlying tradition, which uses these correspondences as standard prescription practice.

*Inclusion criteria.* The dataset is restricted to gems with a defensible single-dominant classical body-region attribution. Minerals appearing in classical materia medica without a clear dhātu-target prescription, or with ambiguous attribution across multiple dhātus, are excluded. The first nine entries comprise the navaratna (nine-gem) set assigned to the nine grahas; the remaining five are uparatna (secondary-gem) entries with classical dhātu-target attributions.

*Tie structure.* The Mohs axis contains eleven unique values across the fourteen rows; ties occur at Mohs 3.5 (pearl, coral), 7.25 (hessonite, tourmaline), and 9.0 (ruby, sapphire). The dhātu-depth axis contains seven unique values, with the sample distribution: rasa (3), rakta (1), māṃsa (1), meda (1), asthi (2), majjā (5), śukra (1). The concentration of five gems at depth 6 (majjā) is a structural feature of the dataset that limits effective rank resolution. Spearman rank correlation accounts for ties in the test statistic; the consequences for effective sample size are addressed in §6.

## 3. Method

Spearman rank correlation is used as the primary test, appropriate for the ordinal encoding of the dhātu-depth axis. Pearson product-moment correlation is reported alongside as a cross-check on whether the relationship is approximately linear in addition to monotonic. Both statistics are computed with `scipy.stats.spearmanr` and `scipy.stats.pearsonr` (SciPy version 1.17.1). Spearman handles ties in the input via the standard mid-rank assignment.

A leave-one-out sensitivity analysis is performed by removing each of the fourteen gems in turn, recomputing the Spearman correlation on the remaining thirteen, and reporting the resulting ρ and *p*-value distribution. The leave-one-out range establishes whether the headline correlation depends on any single observation.

The data table, computation script, and full leave-one-out output are version-controlled in the Atlas Core repository at the commit cited in §9. The script `run_mohs_dhatu_canonical.py` reproduces all reported statistics from the canonical 14-row data table imported from `run_cross_axis.py`.

## 4. Results

The Spearman correlation between Mohs hardness and dhātu-depth across the fourteen-gem dataset is ρ = 0.828 (*p* = 2.56 × 10⁻⁴; n = 14). The Pearson correlation is r = 0.847 (*p* = 1.30 × 10⁻⁴). The Pearson coefficient slightly exceeding the Spearman value indicates that the relationship is approximately linear in addition to monotonic — the depth ordering encodes more than rank-order information about hardness.

The leave-one-out sensitivity analysis is reported in Table 2. For each gem, removing that gem from the dataset and recomputing the Spearman correlation on the remaining thirteen yields ρ values ranging from +0.783 to +0.884. Every leave-one-out subset is significant at *p* < 0.002.

| Removed gem | n | ρ | *p* (Spearman) |
|---|---|---|---|
| Diamond | 13 | +0.783 | 1.54 × 10⁻³ |
| Olivine | 13 | +0.798 | 1.09 × 10⁻³ |
| Pearl | 13 | +0.799 | 1.06 × 10⁻³ |
| Moonstone | 13 | +0.804 | 9.25 × 10⁻⁴ |
| Lapis lazuli | 13 | +0.804 | 9.25 × 10⁻⁴ |
| Coral | 13 | +0.811 | 7.74 × 10⁻⁴ |
| Ruby (corundum) | 13 | +0.826 | 5.06 × 10⁻⁴ |
| Tourmaline | 13 | +0.829 | 4.56 × 10⁻⁴ |
| Hessonite (garnet) | 13 | +0.829 | 4.53 × 10⁻⁴ |
| Emerald (beryl) | 13 | +0.835 | 3.78 × 10⁻⁴ |
| Topaz | 13 | +0.835 | 3.78 × 10⁻⁴ |
| Chrysoberyl | 13 | +0.835 | 3.78 × 10⁻⁴ |
| Quartz | 13 | +0.883 | 6.29 × 10⁻⁵ |
| Sapphire (corundum) | 13 | +0.884 | 6.18 × 10⁻⁵ |

Diamond is the highest-leverage observation; its removal causes the largest drop in ρ (Δρ = −0.045, from 0.828 to 0.783). Even with diamond removed, the result remains highly significant. The two largest *upward* shifts come from removing quartz and sapphire — gems whose Mohs values sit slightly off the local trend (quartz at Mohs 7.0 mapped to depth 6, sapphire at Mohs 9.0 mapped to depth 5). Their removal does not strengthen the headline claim but does indicate that they temper rather than drive the correlation.

The correlation is positive across every leave-one-out subset, with no observation reversing the sign or eliminating significance. The result is not driven by any single gem.

## 5. Note on Gem Maturity

The classical rasaśāstra and jyotiṣa literatures do not prescribe to gem species as such; they prescribe to specimens that have passed *parīkṣā* — the formal examination of gem quality. The *Ratna-parīkṣā* tradition (Buddhabhaṭṭa's *Ratnaparīkṣā*, the gem chapters of the Garuḍa Purāṇa, the mineral sections of Bhāva-prakāśa) specifies the criteria a gem must meet to be considered prescription-suitable: characteristic color saturation, internal *jala* (luster, water-clarity), absence of *doṣas* (cracks, color-zoning, inclusions, milkiness, "dead" optical regions), specific gravity within range, and the manner in which the gem transmits light. A specimen that fails *parīkṣā* on any of these criteria is not a weak prescription; it is, in the classical view, not a candidate for prescription at all. The classical literature treats prescription-suitability as a binary admissibility judgment over a continuous space of specimens, not as a property of the species.

The present analysis does not operationalize *parīkṣā*. The Mohs values used are species-mean values from standard mineralogical reference; the dhātu-attributions are species-level pairings drawn from the prescription compendia. The dataset thus treats each species as a uniform object, while the classical literature it cites treats each species as a category from which only specific specimens are drawn.

This mismatch is the largest single methodological gap in the analysis. We report it explicitly rather than rely on it as a hidden assumption. Two countervailing observations bear on its significance.

First, the classical attributions in the dataset are stated within a pramāṇa structure that does not depend on the species-mean / specimen distinction the contemporary measurement raises. The prescription literature pairs *māṇikya* to *majjā*, *muktā* to *rasa*, *vajra* to *śukra* as established correspondences within rasa-jyotiṣa śāstra; the *parīkṣā* tradition specifies how to identify a prescription-suitable instance of each. The two operate at different layers of the same system. From within the tradition, the species-level correspondence and the specimen-level admissibility criterion are not in tension — the correspondence holds for any specimen the *parīkṣā* admits. The maturity gap appears as a gap only when the contemporary measurement frame applies its own averaging (species-mean Mohs) to one side of the comparison without applying a corresponding admissibility filter to the other.

Second, the contemporary measurement frame is itself doing structured averaging. Mohs hardness is a species-level abstraction over the mineral lattice; real specimens vary in defect density, inclusion content, and locally effective hardness, but the species-mean is a stable property at the structural level the Mohs scale was designed to capture. The comparison the present analysis reports is therefore between two stable abstractions — one structural-mineralogical, one śāstric — both of which are downstream of richer specimen-level realities on their respective sides. The correlation at ρ = 0.83 is between these abstractions. Refining the comparison toward specimen-level data on both sides is the natural empirical extension and is treated in §8.

## 6. Limitations

The analysis carries several methodological limitations that bear on the interpretation of the result.

The sample size is small. Fourteen gems is sufficient for the Spearman correlation to reach significance at the reported level, but it does not support fine-grained subset analysis (by graha class, by crystal system, or by classical text of attribution). The correlation reported here is a single aggregate finding across the available pairs.

The dhātu-depth axis carries substantial tie structure. Five of the fourteen gems are pre-attributed to majjā (depth 6); the remaining six depth ranks are populated by one to three gems each. The effective rank resolution on the *y*-axis is therefore lower than the nominal seven-rank scale suggests. Spearman handles ties through the standard mid-rank assignment, but the concentration at majjā limits the statistical leverage the correlation can exert at the deep end of the depth ordering.

Source attribution is at the aggregate level. The dataset cites Bhāva-prakāśa, Rasa-ratna-samuccaya, the Caraka and Suśruta Saṃhitās, and the standard navaratna prescription compendia as the corpus from which gem-to-dhātu pairings are drawn, but per-verse locators for the individual pairings are not compiled. Compiling per-verse attribution is a philological task in its own right and is proposed as part of the dataset extension in §8.

The Mohs values are species-mean values. The methodological consequences of the species-mean assumption are addressed at length in §5 and are not repeated here.

The dataset is restricted to gems with a defensible single-dominant classical body-region attribution. The classical literature contains additional gems with ambiguous attribution across multiple dhātus and with attribution to compound effects rather than single tissues; these are excluded from the present analysis. The exclusion is conservative — it removes ambiguous cases — but it also means the dataset is not a complete inventory of classical gem prescription. A reader interpreting the correlation as covering "all classical gem prescription" would be overreading; the correlation covers the fourteen-gem unambiguously-attributed subset of that prescription.

The prescription literature is itself a curated record. The classical compendia report the prescriptions that were preserved and transmitted; gems that were tried, found wanting, and dropped from the tradition are not represented. This is a form of selection effect that no within-tradition dataset can avoid. The reported correlation is between the surviving prescriptions and the contemporary hardness scale, not between an unbiased random sample of gem-tissue pairings and the hardness scale.

Spearman *p*-values under heavy ties are approximate; the *p*-value reported is from `scipy.stats.spearmanr`, which uses an asymptotic approximation appropriate for the sample size and tie structure present. Pearson *p* is reported as a cross-check.

## 7. Discussion

The result reported here is a single empirical correlation between two ranking systems developed without historical contact. The Mohs scale of mineral hardness (1812) is a contemporary structural measurement, derived from scratch-resistance behavior at the lattice level. The sapta-dhātu depth ordering established in the Caraka and Suśruta Saṃhitās is a classical prescriptive ordering of bodily tissues from surface to core, transmitted within the rasa-jyotiṣa śāstra tradition for approximately two thousand years. The two systems share no developmental lineage. Their convergence at Spearman ρ = 0.828 across the fourteen-gem prescription set is the result the paper reports.

The correlation is robust to leave-one-out perturbation. No single observation drives the result; the leave-one-out range is +0.78 to +0.88 with every subset significant at *p* < 0.002. The Pearson coefficient is slightly higher than the Spearman, indicating that the relationship is approximately linear in addition to monotonic — the dhātu-depth encoding carries more than ordinal information about the corresponding hardness range.

The paper does not propose a causal mechanism. Several mechanism hypotheses are available within the existing literature. Bhasma preparation texts note that harder substrates require more energetic processing — longer *mardana* (trituration), higher *puṭa-agni* (calcination temperatures) — to reach therapeutic bioavailability, which would predict a structural relationship between hardness and the depth at which a prepared medicine acts. Lattice-mode considerations suggest that mineral mode density and frequency distribution vary systematically with hardness across these gem species, which would predict differential coupling to tissue-level resonance phenomena if such coupling exists. Both hypotheses are testable; neither is adjudicated by the present analysis.

The result is independent of the navaratna mode-count clustering finding reported separately within the same research framework. The mode-count clustering claim depends on a specific threshold for primary lattice modes and on an empirical-null estimate that does not survive crystal-system stratification at α = 0.05; the present correlation depends on neither. The two analyses operate on different axes of the same gem inventory and do not need each other to stand.

The paper takes care to maintain a single bounded empirical claim. The correlation between Mohs hardness and dhātu-depth ordering across the fourteen-gem dataset is the claim. The classical correspondences themselves are stated within rasa-jyotiṣa śāstra and are not claims the present analysis adjudicates; the analysis reports that contemporary structural measurement correlates with one such correspondence at the level documented above. Whether the correlation reflects a deeper structural commensurability between the two systems, or a localized convergence on the gem-dhātu axis specifically, is a question the present data cannot resolve. The proposed empirical and philological extensions in §8 are designed to address this question through further measurement and further textual analysis, respectively.

## 8. Proposed Follow-Up

The present analysis pairs species-mean Mohs values against species-level dhātu prescriptions. The classical prescription literature, however, does not prescribe to species — it prescribes to *parīkṣā*-graded specimens meeting specific maturity criteria (color saturation, internal *jala* / luster, absence of *doṣas*, specific gravity within range, characteristic light transmission). The natural empirical extension is a comparative study at the per-specimen level.

Such a study is methodologically tractable with current instruments. Raman spectroscopy is non-destructive, requires no sample preparation, and is already routinely applied to high-value gems for treatment-detection and origin-determination. Jyotiṣa-grade specimens are sourceable through established vendors who employ certified gemologists for verification of natural, untreated provenance. Non-prescription-grade specimens of the same species are commercially available in parallel.

A direct comparative protocol — Raman signatures, defect density, photoluminescence profiles, and where applicable mechanical mode spectra, measured across matched cohorts of jyotiṣa-grade and non-prescription-grade specimens within a single mineral species — would test whether the per-specimen criteria the classical literature relies on correspond to measurable physical properties. We are not aware of published work on this comparison. Beginning with corundum (ruby and sapphire — well-characterized lattice, well-classified defect taxonomy, established jyotiṣa-grading conventions) would isolate variables most cleanly.

A second empirical extension is philological. The seven-rank dhātu sequence used in the present encoding follows the canonical sapta-dhātu ordering, but classical commentators distinguish sub-aspects within several of the dhātus — particularly *majjā*, which the saṃhitās treat as encompassing bone marrow, central nervous tissue, and in some commentary traditions finer neural substrates. The present dataset assigns five of the fourteen gems to *majjā*; whether the classical attributions for these gems target the same sub-aspect of *majjā* or different sub-aspects is a question for textual analysis. If the latter, a refined depth-encoding incorporating dhātu sub-stratification may produce a stronger correlation than the seven-rank version reported here.

We welcome correspondence with materials scientists positioned to undertake the per-specimen extension and with Sanskritists positioned to undertake the philological extension.

## 9. Data and Code Availability

The dataset and analysis code are version-controlled in the Atlas Core repository at `git@github.com:inahd/atlas_core.git`. The canonical data table is defined in `research/harmonic_extension/scripts/run_cross_axis.py` (lines 23–54). The statistics reported in this paper are reproduced by `research/harmonic_extension/scripts/run_mohs_dhatu_canonical.py`, which depends on `scipy >= 1.17`. Replication requires only the data file and a standard Python scientific stack.

The supporting research notes referenced in this paper — including the broader cross-axis analysis (`cross_axis_correlations.md`), the navaratna mode-count statistical analysis (`statistical_analysis.md`), and the dhātu-bhasma compendium volumes — are present in the same repository under `research/harmonic_extension/` and `compendium/dhatu_bhasma/`.

The commit hash for the version used in this paper is documented at the time of submission.

## References

- Caraka. *Caraka Saṃhitā*. (~1st–2nd c. CE). Standard editions include the Trikamji Acharya edition (Bombay, 1941); English translations include those of Sharma & Dash (Chowkhamba) and Sharma (Chaukhamba Orientalia).
- Suśruta. *Suśruta Saṃhitā*. (~3rd–4th c. CE). Standard editions include the Trikamji Acharya edition (Bombay, 1938); English translations include those of Bhishagratna (Chowkhamba) and Sharma (Chaukhamba Visvabharati).
- Vāgbhaṭa. *Aṣṭāṅga Hṛdaya*. (~7th c. CE).
- Vāgbhaṭa II (attrib.). *Rasa-ratna-samuccaya*. (~13th c. CE).
- Bhāva Miśra. *Bhāva-prakāśa*. (~16th c. CE).
- Sadānanda Sharma. *Rasa Tarangiṇī*. (~19th c. CE).
- Mohs, F. (1812). *Versuch einer Elementar-Methode zur naturhistorischen Bestimmung und Erkennung der Fossilien*. Vienna.
- Virtanen, P., et al. (2020). SciPy 1.0: fundamental algorithms for scientific computing in Python. *Nature Methods* 17, 261–272.
- Atlas Core repository. https://github.com/inahd/atlas_core. Commit e00ade2.
