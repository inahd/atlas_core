# Atlas Project — Research Packet
## Computational Recovery of Classical Indian Metallurgical Doctrine

This packet contains a working research finding plus all supporting code, data, and figures.

**Headline result**: A computational framework encoding the BPHS graha-friendship rules and applied to the multi-metal composition of ashtadhatu sacred alloy recovers 11 of the 12 traditionally-prescribed nakshatras for murti pratishtha (temple deity installation) — **91.7% precision and recall** — entirely from first principles, without being told the tradition's prescriptions.

This demonstrates that the classical doctrine has derivable computational structure rather than being arbitrary or merely customary.

---

## Quick start

```bash
cd code/
python3 run_panchaloha_analysis.py
```

This regenerates the headline result and all figures.

---

## Packet contents

```
research_packet/
├── README.md                    (this file)
├── COVER_LETTER.md             (framing for collaborators / reviewers)
├── paper/
│   └── PAPER.md                 (the substantive research paper)
├── code/
│   ├── jyotish_metallurgy.py   (graha-metal correspondences, friendship rules)
│   ├── panchaloha_alloy.py     (alloy recipes, multi-metal scoring, nakshatras)
│   ├── run_panchaloha_analysis.py  (MAIN: reproduces headline result)
│   ├── run_jyotish_analysis.py     (single-metal classical analysis)
│   ├── wootz_solidification.py     (physics simulation, companion result)
│   ├── run_simulation.py            (wootz simulation runner)
│   ├── sample_database.py           (published archaeological wootz data)
│   └── morphology_comparison.py    (archaeological vs modern wootz)
├── figures/
│   ├── panchaloha_nakshatra_predictions_ashtadhatu.png  (KEY FIGURE)
│   ├── panchaloha_component_breakdown_ashtadhatu.png    (KEY FIGURE)
│   ├── panchaloha_nakshatra_predictions_panchaloha.png
│   ├── panchaloha_component_breakdown_panchaloha.png
│   ├── jyotish_friendship_matrix.png
│   ├── jyotish_windows_iron_steel_lauha.png
│   ├── jyotish_windows_gold_suvarna.png
│   ├── jyotish_windows_copper_tamra.png
│   ├── jyotish_windows_silver_rajata.png
│   ├── wootz_simulation_comparison.png
│   ├── wootz_alignment_vs_field.png
│   ├── morphology_comparison.png
│   └── morphology_residuals.png
├── data/
│   └── (see sample_database.py for the published wootz measurements compiled)
└── supplementary/
    └── simulation_summary.txt
```

---

## What you'll find in the paper

`paper/PAPER.md` is the substantive document, structured as:

1. **Abstract**
2. **Background** (Shilpa Shastra, panchaloha/ashtadhatu, graha-metal correspondences, muhurta tradition)
3. **Methods** (encoding the framework, scoring formula, comparison metrics)
4. **Results** (the 91.7% match, weighting-scheme analysis, wootz simulation, archaeological comparison)
5. **Discussion** (what it means, what it doesn't mean, limitations, why iron is Saturn)
6. **Future work** (refinements, extensions, empirical research program)
7. **Conclusion**
8. **References**

---

## Key claims and scope

**Claimed**: The classical Indian Shilpa Shastra prescriptions for auspicious nakshatras for ashtadhatu murti casting follow systematically from BPHS graha-friendship rules applied to the alloy's multi-metal composition. The framework recovers the prescribed list with 91.7% accuracy from first principles.

**Not claimed**: That ashtadhatu murtis cast on framework-favorable nakshatras have measurably different physical or spiritual properties than those cast on framework-unfavorable nakshatras. This is structural validation of the doctrine's logic, not empirical validation of physical outcomes.

**Wootz physics simulation**: Plausibility modeling of dendritic solidification under varying ambient field conditions. Demonstrates the architecture for transducing classical jyotish assessments into materials-process inputs. Empirical calibration pending.

---

## Reproducing the result

Requirements: Python 3.8+, numpy, matplotlib

```bash
pip install numpy matplotlib
cd code/
python3 run_panchaloha_analysis.py
```

Expected output: Console report showing 91.7% precision and recall for ashtadhatu, plus all figures regenerated in `figures/` (or wherever the script is run).

---

## Audience and purpose

This packet is designed to be readable by:

- **Recreationist metallurgists and traditional craft practitioners** — Figure 1 (component breakdown heatmap) and Figure 2 (nakshatra prediction bar chart) tell the story visually; the paper provides context.

- **Materials scientists with archaeometallurgy interest** — the wootz simulation and archaeological-vs-modern comparison demonstrate the architecture for materials-process integration.

- **Indologists and historians of science** — the structural recovery of classical doctrine through computation may be a novel methodological contribution.

- **Vedic astrologers / panchang scholars** — the framework provides a computational substrate for classical jyotish prescriptions in the metallurgical domain.

---

## License and use

This work is released for academic engagement. The Atlas project is an ongoing independent research effort — collaboration, feedback, and extension are welcomed.

Contact: (to be filled in by author for sending)

---

## Note on the author

This work emerges from the Atlas project, an integrative computational system for traditional Indian sciences and contemporary materials research. Atlas is currently a single-developer independent research project running on a van-based computing setup.

The work is positioned at the intersection of:
- Materials science (wootz, bhasma, sacred alloys)
- Classical Indian astronomy and astrology (jyotisha, BPHS, Brihat Samhita)
- Shilpa Shastra textual tradition
- Gaudiya Vaishnava cosmological framework
- Computational modeling and simulation

It is honest about its empirical scope: structural validation is demonstrated, empirical validation requires laboratory partnership and is the natural next research stage.
