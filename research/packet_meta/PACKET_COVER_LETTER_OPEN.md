# Open Distribution: Software Research Findings Touching Indian Metallurgical Traditions

*Sent simultaneously to multiple parties working on related material. Open invitation to discourse — among yourselves as well as with me.*

---

## Context

I'm an independent software researcher building a computational system (Atlas) that integrates classical Indian sciences — jyotisha, ayurveda, rasashastra, shilpa shastra, panchanga — into a unified relational substrate. Much of this work has been ongoing for several years as my primary independent research project.

In the course of building components related to materials and timing prescriptions, the system surfaced specific findings that appear to touch domains far afield from my own. I'm sharing them openly with the people who actually work in those domains, in case they're useful, and explicitly hoping for discourse among you — about whether they're correct, refinable, dismissable, or extensible.

**I'm not a metallurgist, an Indologist, an Ayurvedic practitioner, or a corrosion scientist.** I'm a software researcher whose system produced specific testable claims that I'm not equipped to validate or refute on my own. The findings are precise enough to evaluate. Whether they hold up is your domain, not mine.

---

## What's in the packet

**Headline finding** (most distinctive):

A computational framework encoding classical BPHS graha-friendship rules, applied to the multi-metal composition of ashtadhatu sacred alloy, recovers 11 of the 12 traditionally-prescribed nakshatras for murti pratishtha (temple deity installation) — **91.7% precision and recall** — entirely from first principles, without being told the tradition's prescriptions.

This suggests the classical prescriptions for sacred alloy timing have derivable computational structure rather than being arbitrary or merely customary. The doctrine has internal logic recoverable through analysis.

**Recovery model registry** (extending the framework to specific cases):

Six documented procedures with assessment of:
- What modern materials science actually describes for each procedure
- Which intermediate substances are real and reproducible
- Where the gap is between traditional claim and modern interpretation
- Framework's predicted optimal timing for each operation

The cases:
- **Lohavada / dhatu-vada procedures** (mercury-based alchemy): Svedana, Jarana, Ranjana, Vedha — sorted by reproducibility from "fully reproduced" to "reproducible only as gilding, not as transmutation"
- **Aranmula kannadi** (delta high-tin bronze, Cu31Sn8): preserved tradition with single-family workshop in Kerala, framework predicts validation against current outputs
- **Iron Pillar of Delhi** (high-phosphorus wrought iron): reproducible chemistry with timing-microstructure predictions testable on small-scale modern P-rich iron

**Companion physics simulation**:

A 2D dendritic solidification model for wootz Damascus steel under varying ambient field conditions, demonstrating the framework architecture for transducing classical jyotish state into materials-process simulation inputs. This is plausibility modeling pending empirical calibration.

**Comparative archaeological analysis**:

Aggregated published wootz band-spacing measurements (Verhoeven, Pendray, Reibold) showing cooling rate as dominant variable, with the framework's astro-state correlation claim operating at within-category variance level not currently captured in published archaeological data.

---

## What I'm explicitly NOT claiming

- **Not claiming** that ashtadhatu murtis cast on framework-favorable nakshatras have measurably different physical properties than ones cast on unfavorable nakshatras. *That requires controlled experiments with laboratory infrastructure I don't have.*

- **Not claiming** transmutation is possible. *The lohavada recovery analysis is honest about identifying which procedures map to amalgamation, mercury sulfide formation, and gilding chemistry rather than element-level transmutation.*

- **Not claiming** the wootz simulation magnitudes are calibrated. *The framework architecture works; the specific coupling magnitudes between geomagnetic field and dendrite alignment are not established in published materials science.*

- **Not claiming** I've discovered something the field has missed. *The 91.7% structural recovery may be a finding the field would consider obvious if formally analyzed; I don't know.*

- **Not claiming** authority to interpret the texts. *I've used standard translations and contemporary panchang sources; primary Sanskrit scholarship would refine many of the encoding choices.*

---

## What I'm hoping for

**Open discourse — among you, not just with me.**

The recipients of this packet include people working on:
- Archaeometallurgy of South Indian high-tin bronzes
- Iron Pillar of Delhi corrosion research
- Rasashastra scholarship (textual and pharmaceutical)
- Wootz Damascus steel reproduction
- Indian classical timing prescriptions in metallurgical contexts
- Computational humanities applied to Sanskrit technical traditions

Some of you may already know each other. Some of you may not. The findings touch multiple domains — corrosion science, materials chemistry, textual scholarship, computational modeling — and the most valuable conversation might happen between you, with me as the originator of the input rather than the hub of the response.

**Specifically**, if you find any of this interesting:

- *Pushback*: where am I getting things wrong? Encoding choices, interpretation, methodology, scope claims — all open to correction.

- *Verification*: any of the framework predictions can be tested against existing data you may have access to. The Aranmula casting-date QC, IIT Kanpur P-rich iron samples, NBTHK tamahagane production records — each constitutes potential verification data.

- *Extension*: which cases should be added to the recovery model registry next? Yashada-bhasma has published nano-measurements. Bell-bronze acoustics are cheaply measurable. Tamahagane has well-tracked production dates. Each is a potential next case.

- *Critical engagement*: even thoughtful dismissal is useful. If the underlying methodology has a flaw I'm not seeing, that's important to know.

**I'm sharing in good faith and will not pursue or pressure**. If this is uninteresting, no response is also a response, and that's fine. If it's interesting enough for a conversation, I'm available. If it's interesting enough for collaboration, I'd value it but don't require it.

---

## What's in the attached packet

```
research_packet/
├── README.md                — orientation
├── paper/PAPER.md          — substantive research paper (~5000 words)
├── code/                    — runnable Python source
│   ├── jyotish_metallurgy.py
│   ├── panchaloha_alloy.py
│   ├── lohavada_reconstruction.py
│   ├── extended_recovery_models.py
│   ├── wootz_solidification.py
│   └── various runners
├── figures/                 — 13+ visualizations
├── verify_result.py         — run this to confirm the 91.7% headline finding
└── requirements.txt
```

To verify the headline finding in 10 seconds:
```bash
pip install numpy matplotlib
python3 verify_result.py
```

Expected output: `PRECISION: 91.7%, RECALL: 91.7% — HEADLINE RESULT VERIFIED`.

---

## On positioning

I want to be direct about something: I'm not driving metal science. I'm a software researcher whose system happened to produce findings that touch metal science.

The research direction I'm actually driving is *Atlas itself* — a computational substrate for traditional Indian sciences. The metallurgical findings are byproducts of that broader work, surfaced because my own kernel was capable of running the analysis. The findings stand or fall on their own merit; they don't depend on Atlas's broader credibility.

This is also why I'm sending to all relevant parties simultaneously rather than approaching one or two for endorsement. *I'm not seeking gatekeeper validation; I'm contributing to discourse.* The field's experts are who you are. I'm the source of an input, not a candidate for membership.

If the input is useful, please use it. If it prompts conversation among you, that's the best outcome. If it's irrelevant or wrong, please tell me so I can correct course.

---

## Contact

[author signature, contact details — to be added by sender]

I'll respond to anything that comes back, but I'm not going to chase or follow up. The packet is the work. What happens with it is yours.

🙏

— with appreciation for the work all of you have already done that this builds on
