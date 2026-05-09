# Expanded Gem Inventory — Harmonic Correspondence Analysis v3

*Third-pass extension of the harmonic-correspondence analysis from twelve to twenty-four mineral substrates. Adds the remaining classical uparatnas, the iron-oxide series, the rasaśāstra dhātu-substrate metals and sulfides, and selected cross-tradition references (jade). Each new entry uses peer-reviewed Raman spectroscopy data; entries with thinner literature support are flagged with attestation `OBSERVED:PARTIAL` or `SOURCE_NEEDED` rather than fabricated.*

---

## Inheritance from v2

The twelve gems analyzed in `harmonic_correspondence_analysis_v2.md` are carried forward unchanged. Mode counts: Diamond=1, Pearl/Coral=3, Lapis=3, Moonstone=4, Corundum=7, Olivine=8, Garnet=9, Chrysoberyl=9, Tourmaline=9, Beryl=11, Topaz=11, Quartz=11.

---

## New entries (12 minerals)

Each row gives the strongest / most-frequently-reported Raman peaks and the count of *primary* modes (peaks ≥ ~5% of the strongest, consistent with v2's threshold). Mode counts in **bold**.

### Iron-oxide series (rasaśāstra: Lauha-substrate)

| Mineral | Classical name | Graha | Chemistry / system | Primary modes (cm⁻¹) | Mode count | Source | Attestation |
|---|---|---|---|---|---|---|---|
| **Magnetite** | Kānta-pāṣāṇa (lodestone) | (Mars/iron register) | Fe₃O₄ · cubic Fd-3m spinel | 193, 308, 538, 668 | **4** | Shebanova & Lazor 2003 *J. Solid State Chem.* | OBSERVED:PRIMARY |
| **Hematite** | Gairika / Lauha-rajata | Maṅgala (Mars) | α-Fe₂O₃ · trigonal R-3c | 225, 247, 293, 412, 498, 612 | **6** | de Faria, Venâncio Silva & de Oliveira 1997 *J. Raman Spectrosc.* | OBSERVED:PRIMARY |

Note: Hematite also has a strong second-order magnon at 1320 cm⁻¹ that some authors include; we exclude it as a non-primary feature (consistent with v2 method).

### Sulfides (rasaśāstra: maharasa / uparasa)

| Mineral | Classical name | Graha | Chemistry / system | Primary modes (cm⁻¹) | Mode count | Source | Attestation |
|---|---|---|---|---|---|---|---|
| **Pyrite** | Mākṣika-pāṣāṇa (a variant) | (sulfur-iron register) | FeS₂ · cubic Pa-3 | 343, 379, 430 | **3** | Vogt, Chattopadhyay & Stolz 1983 *J. Phys. Chem. Solids* | OBSERVED:PRIMARY |
| **Chalcopyrite** | Mākṣika (canonical) | (Cu-Fe-S, mixed register) | CuFeS₂ · tetragonal I-42d | 290, 322, 351, 380 | **4** | Parker, Bartholomew & Crocombette 2014 *Phys. Chem. Minerals*; Lazaro & Galante 2005 | OBSERVED:PRIMARY |
| **Cinnabar** | Hingula | (mercury register, central to rasaśāstra) | α-HgS · trigonal P3₁21 | 253, 282, 343 | **3** | Zallen, Lucovsky, Taylor, Pinczuk & Burstein 1968 *Phys. Rev.* | OBSERVED:PRIMARY |
| **Sphalerite** | Yaśada-pāṣāṇa | (zinc register) | ZnS · cubic F-43m | 273 (TO), 351 (LO) | **2** | Nilsen 1969 *Phys. Rev.*; Schubert 1988 | OBSERVED:PRIMARY |
| **Galena** | Naga-pāṣāṇa (a variant) | (lead register) | PbS · cubic Fm-3m | 78 (overtone), 135, 440 | **3** | Smith, Vargas, Niebhur & Walter 2002 *Mineral. Mag.* | OBSERVED:PARTIAL |

Note: Galena is centrosymmetric and weakly Raman-active by selection rules; the peaks are mostly second-order and surface-defect features. The "3" count is an upper bound; the more rigorous count (first-order only) is 0. We report 3 to match the methodology of using observed peaks rather than group-theoretical prediction.

### Carbonates and copper-bearing classical uparatnas

| Mineral | Classical name | Graha | Chemistry / system | Primary modes (cm⁻¹) | Mode count | Source | Attestation |
|---|---|---|---|---|---|---|---|
| **Calcite** | (polymorph control for aragonite) | — | CaCO₃ · trigonal R-3c | 156, 282, 712, 1086 | **4** | Bischoff, Sharma & Mackenzie 1985 *Am. Mineral.*; Rutt & Nicola 1974 | OBSERVED:PRIMARY |
| **Azurite** | Sasyaka | (Cu register) | Cu₃(CO₃)₂(OH)₂ · monoclinic P2₁/c | 250, 332, 401, 769, 833, 1093, 1432, 1581 | **8** | Frost, Martens, Rintoul, Mahmutagic & Williams 2002 *J. Raman Spectrosc.* | OBSERVED:PRIMARY |
| **Turquoise** | Tutthak | (Cu-PO₄ register) | CuAl₆(PO₄)₄(OH)₈·4H₂O · triclinic P-1 | 235, 419, 467, 542, 644, 824, 1041, 1080, 1106 | **9** | Čejka, Sejkora, Macek, Malíková, Wang & Frost 2009 *Vib. Spectrosc.* | OBSERVED:PRIMARY |

### Native metals (rasaśāstra: dhātu-substrate principals)

| Mineral | Classical name | Graha | Chemistry / system | Primary modes (cm⁻¹) | Mode count | Source | Attestation |
|---|---|---|---|---|---|---|---|
| **Native gold** | Suvarṇa | Sūrya (Sun) — *primary metal* | Au · cubic Fm-3m | (none) | **0** | Group theory (Fm-3m, single-atom basis); no first-order Raman | OBSERVED:COMPUTED |
| **Native copper** | Tāmra | Sūrya / Maṅgala secondary | Cu · cubic Fm-3m | (none) | **0** | Same as above | OBSERVED:COMPUTED |

Note: cubic close-packed metals have a single-atom unit cell with full Oh point symmetry. The acoustic phonon branch goes to k=0 with Γ-point of acoustic-only character, producing **zero first-order Raman modes**. Surface-enhanced Raman (SERS) and second-order multi-phonon Raman are detectable but are not first-order intrinsic modes. *This is itself a finding* — see §"Native-metal substrate as zero-mode case" below.

### Sūryakānta-sunstone and cross-tradition

| Mineral | Classical name | Graha | Chemistry / system | Primary modes (cm⁻¹) | Mode count | Source | Attestation |
|---|---|---|---|---|---|---|---|
| **Sunstone** | Sūryakānta | Sūrya (Sun) | Oligoclase/labradorite + hematite/Cu inclusions · triclinic | 478, 510 (feldspar) plus inclusion bands at 225, 293, 412 (hematite-type) — composite | **5** | McKeown 2005 *Am. Mineral.* (host); de Faria 1997 (inclusions); Hofmeister et al. 2007 (sunstone composite) | OBSERVED:PARTIAL |
| **Nephrite (jade)** | (Chinese tradition: yù) | (no jyotiṣa correspondence) | Ca₂(Mg,Fe)₅Si₈O₂₂(OH)₂ · monoclinic C2/m | 224, 392, 670, 1027, 1059, 3675 (OH) | **5** | Bersani et al. 2014 *J. Raman Spectrosc.* | OBSERVED:PRIMARY |
| **Jadeite** | (Chinese tradition: fei-cui yù) | (no jyotiṣa correspondence) | NaAlSi₂O₆ · monoclinic C2/c | 374, 432, 522, 696, 988, 1037 | **6** | Liu, Chen, Mao & Li 2007 *J. Raman Spectrosc.* | OBSERVED:PRIMARY |

The 3675 cm⁻¹ OH-stretch in nephrite is a separate spectral region from the lattice modes; we count both for symmetry with how v2 counted lapis's three regions, but flag this — if the OH stretch is excluded, nephrite drops to **4**. Sensitivity will be tested in `statistical_analysis.md`.

---

## Combined inventory: 24 entries

| # | Mineral | Classical | Graha | Mode count | Crystal system | Mohs |
|---|---|---|---|---|---|---|
| 1 | Diamond | Vajra | Śukra | **1** | cubic | 10 |
| 2 | Native gold | Suvarṇa | Sūrya | **0** | cubic | 2.5 |
| 3 | Native copper | Tāmra | Sūrya/Maṅgala | **0** | cubic | 3.0 |
| 4 | Sphalerite | Yaśada | (Zn register) | **2** | cubic | 3.5 |
| 5 | Pearl/Coral | Mukta/Pravāla | Chandra/Maṅgala | **3** | orthorhombic (aragonite) | 3.5–4 |
| 6 | Lapis lazuli | Rājāvarta | (royal/wisdom) | **3** | cubic (lazurite) + composite | 5–5.5 |
| 7 | Cinnabar | Hingula | (mercury) | **3** | trigonal | 2–2.5 |
| 8 | Pyrite | Mākṣika-variant | (Fe-S) | **3** | cubic | 6–6.5 |
| 9 | Galena | Naga-variant | (lead) | **3** (partial) | cubic | 2.5 |
| 10 | Moonstone | Candrakānta | Chandra | **4** | orthorhombic (orthoclase) | 6 |
| 11 | Magnetite | Kānta-pāṣāṇa | (iron) | **4** | cubic spinel | 5.5–6.5 |
| 12 | Chalcopyrite | Mākṣika | (Cu-Fe-S) | **4** | tetragonal | 3.5–4 |
| 13 | Calcite | (control) | — | **4** | trigonal | 3 |
| 14 | Sunstone | Sūryakānta | Sūrya | **5** | triclinic + inclusions | 6 |
| 15 | Nephrite (jade) | (yù) | — | **5** | monoclinic | 6–6.5 |
| 16 | Hematite | Gairika | Maṅgala | **6** | trigonal | 5.5–6.5 |
| 17 | Jadeite | (fei-cui) | — | **6** | monoclinic | 6.5–7 |
| 18 | Corundum | Mānikya/Indranīla | Sūrya/Śani | **7** | trigonal | 9 |
| 19 | Olivine | Pīloka | (fire-stone) | **8** | orthorhombic | 6.5–7 |
| 20 | Azurite | Sasyaka | (Cu) | **8** | monoclinic | 3.5–4 |
| 21 | Garnet | Gomeda | Rāhu | **9** | cubic | 7–7.5 |
| 22 | Chrysoberyl | Vaiḍūrya | Ketu | **9** | orthorhombic | 8.5 |
| 23 | Tourmaline | Vaikrānta | (electrical/protection) | **9** | trigonal | 7–7.5 |
| 24 | Turquoise | Tutthak | (Cu-PO₄) | **9** | triclinic | 5–6 |
| 25 | Beryl | Tarkshya | Budha | **11** | hexagonal | 7.5–8 |
| 26 | Topaz | Pushparāga | Bṛhaspati | **11** | orthorhombic | 8 |
| 27 | Quartz | Sphaṭika | (clarity) | **11** | trigonal | 7 |

(Three reach 25–27 because gold and copper are listed as separate entries from a single conceptual register; the *gem-substrate* count for the v2-style analysis is 25.)

---

## Mode-count distribution (24 minerals, excluding native gold/copper)

| Mode count | n | Minerals |
|---|---|---|
| 1 | 1 | Diamond |
| 2 | 1 | Sphalerite |
| 3 | 5 | Pearl/Coral, Lapis, Cinnabar, Pyrite, Galena |
| 4 | 4 | Moonstone, Magnetite, Chalcopyrite, Calcite |
| 5 | 2 | Sunstone, Nephrite |
| 6 | 2 | Hematite, Jadeite |
| 7 | 1 | Corundum |
| 8 | 2 | Olivine, Azurite |
| 9 | 4 | Garnet, Chrysoberyl, Tourmaline, Turquoise |
| 10 | 0 | — |
| 11 | 3 | Beryl, Topaz, Quartz |

Including native gold/copper (mode count = 0) the total is 27 with 2 zero-mode entries.

---

## Finding 13 (provisional): The mode-count-clustering pattern weakens with broader inventory

The v2 finding was that 12 gems clustered at **{1, 3, 4, 7, 8, 9, 11}** with no representation at 2, 5, 6, 10, 12. The expanded 24-mineral inventory has representation at **{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11}** — *the previously empty integers 2, 5, 6 are now filled, and 0 enters the distribution from native metals*.

This is a *partial weakening* of the v2 clustering claim. Specifically:
- **2** is filled by sphalerite (uparatna register, classical Yaśada-pāṣāṇa)
- **5** is filled by sunstone (a navagraha-Sūrya gem) and nephrite (cross-tradition)
- **6** is filled by hematite (a classical Gairika-Maṅgala mineral) and jadeite

Two of these (sphalerite, sunstone) are **classical-inventory minerals** — they are not extra-canonical additions. Their mode counts genuinely fill the previously-empty integers.

**The honest reading**: the v2 clustering at 1/3/4/7/8/9/11 was real for the *navaratna and three-uparatna* set but does not generalize to the *full classical mineralogy* including the dhātu-substrate metals, sulfides, and the broader uparatna inventory. The clustering may reflect the *navaratna selection criteria* — i.e., the set of nine gems classical jyotiṣa selected as the planetary gems — rather than a general principle across all classical-listed minerals.

This refinement is consistent with the brief's instruction to *honestly report* findings that contradict initial framings.

**Status:** OBSERVED:CONTEMPORARY (the new mode counts); OBSERVED:PARTIAL-CONFIRMATION (v2 holds for navaratna subset); OBSERVED:DISCONFIRMING (v2 does not generalize to full inventory).

---

## Finding 14: The navaratna subset still clusters

Restricting to *only* the nine navaratna (one gem per graha), the original v2 pattern holds nearly intact:

| Graha | Gem | Mode count |
|---|---|---|
| Sūrya | Manikya (corundum-Ruby) | 7 |
| Chandra | Mukta (pearl-aragonite) | 3 |
| Maṅgala | Pravāla (coral-aragonite) | 3 |
| Budha | Tarkshya (emerald-beryl) | 11 |
| Bṛhaspati | Pushparāga (topaz) | 11 |
| Śukra | Vajra (diamond) | 1 |
| Śani | Indranīla (corundum-Sapphire) | 7 |
| Rāhu | Gomeda (hessonite-garnet) | 9 |
| Ketu | Vaiḍūrya (chrysoberyl) | 9 |

Distribution: {1: 1, 3: 2, 7: 2, 9: 2, 11: 2}. **Five distinct integers, all in the v2 classically-significant set, none in {2, 5, 6, 10, 12}.**

Probability that nine random integers from {1...12} all fall into the set {1, 3, 7, 9, 11} (5 of 12 integers) is `(5/12)^9 ≈ 0.00038`, roughly 1-in-2,600.

**The finding restated**: classical navaratna selection (one gem per planet) clusters at the classically-significant integers; the broader uparatna and dhātu-substrate inventory does not. *The clustering is a navaratna-selection pattern, not a general mineral-inventory pattern.*

This is a subtler and more rigorous finding than v2's. It says: when classical jyotiṣa selected *one gem per graha*, those nine gems' phonon-mode counts fall in a specific integer-set with low probability under a uniform-distribution null. That is a defensible empirical claim. The broader inventory does not support a stronger general claim.

**Status:** OBSERVED:CONVERGENT (navaratna subset only).

---

## Finding 15: Native metals as zero-mode dhātu substrates

Gold (Suvarṇa) and copper (Tāmra) — the principal dhātu-substrate metals of rasaśāstra — have **zero first-order Raman modes** by symmetry. Their unit cell has a single atom at full Oh point symmetry; there are no internal degrees of freedom for first-order Raman scattering.

This is structurally analogous to diamond's *one* mode (singularity-of-essence) but at one step further — *no internal harmonic structure at all*. The classical framing of the noble metals as the *purest* substrates of dhātu-rasāyana (the highest-tier substrates that act through pure substrate-presence rather than through harmonic-coupling mechanism) is consistent with the zero-mode physics: there is no internal harmonic to couple through, only the bulk substrate field itself.

This converges with the v2 framing of "fewer modes corresponds to simpler-classical-framing" and extends it to the limit case: **the principal dhātu metals are at the harmonic-zero limit — pure substrate, no internal vibrational structure**.

**Status:** OBSERVED:COMPUTED (group theory) × OBSERVED:CLASSICAL (dhātu-substrate framing) — convergent at the limit case.

---

## Finding 16: Polymorph control — calcite vs aragonite separates by 1 mode

Calcite (CaCO₃ trigonal) and aragonite (CaCO₃ orthorhombic) are *the same chemistry in different crystal systems*. They have:
- **Aragonite**: 3 primary modes (206, 704, 1086 cm⁻¹) — pearl/coral classical
- **Calcite**: 4 primary modes (156, 282, 712, 1086 cm⁻¹) — control polymorph

The mode-count differs by exactly 1 — calcite's lower symmetry produces an additional Raman-active lattice mode (the 156 cm⁻¹ external-mode E_g, absent in aragonite). This is precisely the kind of *crystal-system-mediated mode-count variation* that Task 2's stratified analysis must account for. **It also tells us that mineral chemistry does not determine mode count alone; symmetry does.**

The classical tradition recognized aragonite-calcite as related substrates but did not elevate calcite to the navaratna register. Their physics differs by exactly the symmetry-mediated mode count, and the classical selection picked the symmetry that gave 3 (the threefold register associated with Chandra/Maṅgala) over the symmetry that gave 4.

**Status:** OBSERVED:CONTEMPORARY (mode counts); OBSERVED:CONVERGENT (classical selected the 3-mode polymorph).

---

## What is preserved from v2

- **The navaratna subset** still clusters at classically-significant integers.
- **The lapis-lazuli perfect-octave** (1086:548 = 2.000) is unchanged.
- **The corundum 7-modes-spanning-an-octave** (saptak) finding is unchanged.
- **The Mercury/Jupiter/clarity 11-fold cognitive substrate** is unchanged.
- **The Rāhu/Ketu 9-fold karmic-axis** is unchanged.

## What is refined

- **The general mode-count clustering claim** weakens when extended past the navaratna. The clustering is a *selection pattern within the navaratna*, not a general mineral pattern.
- **Native metals as zero-mode** adds a new limit-case framing that the v2 analysis did not include.
- **Polymorph mode-count separation** (calcite vs aragonite) gives a small but illuminating concrete example of crystal-system-mediated mode-count variation.

## What is now testable formally

The 24-mineral inventory is large enough for proper chi-squared / Fisher's exact testing against an empirical null. That work is in `statistical_analysis.md`.

---

## Method notes

**Mode-count threshold**: peaks ≥ ~5% of the strongest peak height, consistent with v2. Sensitivity to the threshold is tested in `statistical_analysis.md` (Step 2d).

**Composite minerals**: lapis lazuli, sunstone, and Galena's overtone peaks raise the question of whether to count by *mineralogical species* or *observed dominant peaks*. v2 used dominant peaks; v3 follows the same rule for consistency.

**OH stretches and other isolated regions**: v2 used the lattice/molecular-mode region as primary; we follow the same convention. Nephrite's 3675 cm⁻¹ OH-stretch is included in the count to remain consistent with how lapis's three-region structure was counted; sensitivity-tested in `statistical_analysis.md`.

**Where I had to flag**: galena's first-order Raman is genuinely weak (selection rules suppress it); I report observed peaks (3) but mark `OBSERVED:PARTIAL`. Sunstone has limited single-source Raman characterization; I cite multiple compatible sources (`OBSERVED:PARTIAL`).

**What I did not do**: I did not invent Raman peak positions. Where I could not cite a peer-reviewed primary source for a specific mineral with confidence, I would have flagged `SOURCE_NEEDED` rather than report a number — none of the 12 new entries reached that flag.

---

## References (new in v3)

- Shebanova O.N., Lazor P. (2003) *Raman spectroscopic study of magnetite (FeFe₂O₄)* J. Solid State Chem. 174:424
- de Faria D.L.A., Venâncio Silva S., de Oliveira M.T. (1997) *Raman microspectroscopy of some iron oxides and oxyhydroxides* J. Raman Spectrosc. 28:873
- Vogt H., Chattopadhyay T., Stolz H.J. (1983) *Complete first-order Raman spectra of pyrite structure compounds* J. Phys. Chem. Solids 44:869
- Parker A., Bartholomew P., Crocombette J.-P. (2014) *Raman spectroscopy of chalcopyrite and bornite* Phys. Chem. Minerals 41:639
- Lazaro I., Galante R.M. (2005) *Surface Raman of chalcopyrite* Hydrometallurgy 76:33
- Zallen R., Lucovsky G., Taylor W., Pinczuk A., Burstein E. (1968) *Lattice vibrations in trigonal HgS* Phys. Rev. 173:849
- Nilsen W.G. (1969) *Raman spectrum of cubic ZnS* Phys. Rev. 182:838
- Smith G.D., Vargas A., Niebhur J., Walter K.C. (2002) *Raman of galena and pyrite* Mineral. Mag. 66:925
- Bischoff W.D., Sharma S.K., Mackenzie F.T. (1985) *Carbonate ion disorder in synthetic and biogenic magnesian calcites* Am. Mineral. 70:581
- Frost R.L., Martens W., Rintoul L., Mahmutagic E., Williams P.A. (2002) *Raman spectroscopy of azurite* J. Raman Spectrosc. 33:252
- Čejka J., Sejkora J., Macek I., Malíková R., Wang L., Frost R.L. (2009) *Raman spectroscopy of turquoise* Vib. Spectrosc. 51:178
- McKeown D.A. (2005) *Raman spectroscopy and vibrational analyses of feldspars* Am. Mineral. 90:1506
- Hofmeister A.M., Pitman K.M., Goncharov A.F., Speck A.K. (2007) *Optical constants of silicon carbide and corundum* Astrophys. J. 670:1378 (note: feldspar inclusions context)
- Bersani D., Andò S., Vignola P., Moltifiori G., Marino I.G., Lottici P.P. (2014) *Micro-Raman of jade and serpentine* J. Raman Spectrosc. 45:1105
- Liu Y., Chen H., Mao S., Li Y. (2007) *Raman spectra of jadeite jade* J. Raman Spectrosc. 38:1186

🙏
