# Cover Letter

*For collaborators, reviewers, or recipients within the recreationist metallurgist network*

---

## What this is

A computational framework demonstrating that the classical Shilpa Shastra prescriptions for auspicious nakshatras for sacred alloy murti casting have **derivable logical structure**. When the BPHS graha-friendship rules are applied to the multi-metal composition of ashtadhatu (eight metals, equal proportion, each tied to a graha by classical correspondence), the resulting predictions match the tradition's independently-prescribed list of auspicious nakshatras with **91.7% precision and recall**.

The framework was not given the tradition's list. It derived the predictions from first principles — graha-friendship rules and graha-metal correspondences — and the resulting top-12 predictions independently match 11 of 12 traditionally-prescribed nakshatras for murti pratishtha.

---

## Why this might interest you

If you work with traditional metallurgy, sacred alloys, or classical timing prescriptions for metal operations, this work provides:

1. **A computational substrate** for the classical timing prescriptions — not just a list of "good days" but a system that can compute optimal windows for any specific alloy operation given its component metals.

2. **Validation that the doctrine is systematic** — the prescriptions are not arbitrary or merely customary, they follow from underlying graha-friendship logic. This makes the broader research program more defensible.

3. **A working physics simulation companion** — for single-metal cases (the wootz example), the framework transduces classical jyotish assessments into materials-process simulation inputs. Demonstrates the architecture for integrating cosmological state with materials processing.

4. **An honest research scope** — structural validation only. The paper is explicit that empirical validation requires laboratory work that has not yet been done. The work is positioned at the right level: making testable claims rather than overclaiming.

---

## What I'm hoping for

Honestly, I'm hoping for engagement. Specifically:

- **Practitioners**: Does this match your experience? Are there variances in your operations that the framework's predictions might explain?

- **Materials scientists**: Is the wootz simulation architecture sound? Is the empirical research program (calibrating against known operations like NBTHK tamahagane production) feasible?

- **Indologists / historians of science**: Is the structural recovery of doctrine through computation a methodological contribution? Are there textual sources I should engage with that I haven't?

- **Anyone with relevant expertise**: Pushback on what I'm getting wrong. Identification of additional rules the framework should encode. Suggestions for empirical tests that could be run with available infrastructure.

I'm an independent researcher, vanlife setup, building this work as a single developer project (Atlas). I have substantial substrate (a full computational system integrating jyotisha, panchanga, materials data, sound work, and other domains) but I lack institutional affiliation, lab access, and a research network.

If anything in this packet seems worth engaging with, I would value the conversation.

---

## What's in the packet

- `paper/PAPER.md` — substantive research document with full methods, results, discussion, references
- `code/` — all working source code, runnable to reproduce results
- `figures/` — generated visualizations
- `README.md` — orientation for the packet

The headline figures are:

- `figures/panchaloha_nakshatra_predictions_ashtadhatu.png` — bar chart showing framework predictions vs traditional prescriptions across all 27 nakshatras
- `figures/panchaloha_component_breakdown_ashtadhatu.png` — heatmap showing per-component graha compatibility, with traditional auspicious nakshatras marked

To reproduce the result end-to-end:
```bash
cd code/
python3 run_panchaloha_analysis.py
```

---

## Honest framing

I want to be direct about what this is and isn't.

**What this is**: a structural finding. The classical doctrine has computational structure. The framework recovers it. This is novel insofar as the analysis hasn't been published in this form previously.

**What this isn't**: empirical proof that operations on framework-predicted nakshatras produce measurably different outcomes than operations on unfavorable nakshatras. That requires controlled physical experiments with laboratory access and statistical power. That research program is the natural next stage but is years of work away from publication.

I'm not claiming to have proven the tradition's empirical claims. I'm claiming to have shown the tradition's prescriptions follow from a derivable logical system — which is itself a meaningful finding.

The wootz physics simulation is plausibility modeling pending calibration. The framework architecture works; the magnitudes of geomagnetic-field coupling to dendrite alignment in molten steel are not established. I'm explicit about this in the paper.

---

## Why I'm sending this now rather than continuing to refine

This work has reached a point of coherence where additional refinement before sharing would mostly be polishing. The substantive finding is stable. The code runs. The figures tell the story. *Sharing now invites the conversation that improves the work*; sitting on it invites only more polish.

If this is interesting, please let me know. If it's not — also fine, and feedback on why would be valuable.

If there's a specific extension you'd want to see — a particular alloy, a particular operation, a calibration test you have data for — I can run it against the framework. The architecture is in place; new cases are tractable to add.

---

## On the broader project

The Atlas project is the ongoing computational substrate this work emerges from. Atlas integrates classical Indian sciences (jyotisha, ayurveda, vastu, rasashastra), contemporary materials research, and lived practice into a single relational graph and computational system. This packet represents one specific output from the larger project.

If the broader Atlas direction interests you, I'm happy to share more. The project has been running for some time as my primary independent research focus.

---

🙏

Thank you for taking the time. I know an unsolicited packet from an independent researcher is unusual; I'm sending it because I think the finding is real and the work has reached a point where engagement matters more than further solo refinement.

— [author signature, contact details to be added]
