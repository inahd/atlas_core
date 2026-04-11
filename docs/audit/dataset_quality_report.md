# Dataset Quality Report — Bhakti Practice Audit

Date: 2026-04-11
Status: **HUMAN REVIEW REQUIRED** — do not auto-fix

## Summary

The svarodaya activity matrix marks **meditation** and **remembrance_of_supreme**
as "avoid" under certain nadi/element combinations. These are navavidha bhakti
practices that are **never contraindicated** in Gauḍīya Vaiṣṇava tradition.

The live `/dinacharya` endpoint currently returns `remembrance_of_supreme`
and `meditation` in its avoid list for the current period.

---

## FLAG 1: Bhakti Practices Marked 'avoid'

**10 rows** in `datasets/svarodaya/activity_matrix.csv` flag bhakti practices as "avoid":

### meditation (4 rows)

| Line | Nadi | Element | Recommendation | Attestation |
|------|------|---------|----------------|-------------|
| 4 | ida | fire | **avoid** | SPECULATIVE |
| 7 | pingala | earth | **avoid** | SPECULATIVE |
| 8 | pingala | water | **avoid** | SPECULATIVE |
| 9 | pingala | fire | **avoid** | SPECULATIVE |

### remembrance_of_supreme (6 rows)

| Line | Nadi | Element | Recommendation | Attestation |
|------|------|---------|----------------|-------------|
| 199 | ida | fire | **avoid** | SPECULATIVE |
| 200 | ida | air | **avoid** | SPECULATIVE |
| 202 | pingala | earth | **avoid** | SPECULATIVE |
| 203 | pingala | water | **avoid** | SPECULATIVE |
| 204 | pingala | fire | **avoid** | SPECULATIVE |
| 205 | pingala | air | **avoid** | SPECULATIVE |

### Analysis

The source for ALL flagged rows is:
> "Matrix synthesized from Shiva Svarodaya nadi activity classes and element auspiciousness rules."

The attestation for ALL flagged rows is: **SPECULATIVE**

The Shiva Svarodaya does state that **pingala** nadi favors "cruel/daring works"
and that **sushumna** is the only nadi suitable for "yoga/dhyana/remembrance of the Supreme."
The matrix extrapolation then marked meditation/remembrance as "avoid" under pingala
and fire-element ida — this is a **mechanical inference** that contradicts the
Gauḍīya principle that harinām/smarana is **always auspicious** regardless of
astronomical or physiological conditions.

### Gauḍīya Position (for human reviewer)

From Caitanya Caritāmṛta (CC Antya 20.18):
> nāma cintāmaṇiḥ kṛṣṇaś caitanya-rasa-vigrahaḥ
> pūrṇaḥ śuddho nitya-mukto 'bhinnatvān nāma-nāminoḥ

The holy name is:
- cintāmaṇi (touchstone — always purifying)
- pūrṇa (complete)
- śuddha (pure)
- nitya-mukta (eternally liberated)

It cannot be contaminated by material conditions (nāma-aparādha excepted,
but that is an offense category, not a timing restriction).

**Harinām, smarana, kīrtana, śravaṇa are NEVER to be avoided.**

---

## FLAG 2: Source/Attestation Distribution

| Attestation | Rows | Percentage |
|-------------|------|------------|
| OBSERVED | 75 | 35.7% |
| INTERPRETATION | 107 | 51.0% |
| SPECULATIVE | 28 | 13.3% |

ALL 210 rows cite the same source text:
> "Matrix synthesized from Shiva Svarodaya nadi activity classes and element auspiciousness rules."

This is a single-source matrix expansion. The Shiva Svarodaya provides
activity categories for nadis (ida = amiable works, pingala = daring works,
sushumna = yoga only). The 210-row matrix is a Cartesian product expansion
of 14 activities × 3 nadis × 5 elements.

The SPECULATIVE rows are where the original text does not address
the specific (activity, nadi, element) combination — the recommendation
was inferred by the matrix builder.

---

## FLAG 3: Same Activity in Both Recommend and Avoid

No conflicts found within the activity_matrix.csv — each
(activity, nadi, element) triple has exactly one recommendation.

However, the **live /dinacharya endpoint** shows:
```
Period: Aparahna
Avoid: ['eating', 'hunting', 'meditation', 'remembrance_of_supreme', 'sleep', 'travel', 'warfare']
Practices: ['creative work', 'tea', 'stretching']
```

The avoid list comes from the svarodaya activity matrix filtering.
`meditation` and `remembrance_of_supreme` appear in the avoid list
because the current nadi+element combination triggers the SPECULATIVE
"avoid" rows identified above.

---

## FLAG 4: Generic Astrology vs Gauḍīya Sources

No rows reference generic jyotiṣa/muhūrta/graha doṣa sources directly.
However, the Shiva Svarodaya is a **Śaiva tantra** text, not a Gauḍīya
Vaiṣṇava source. Its activity classifications reflect a different
tradition's values:

- Hunting and warfare are "favored" under pingala — these are adharmic
  from a Vaiṣṇava perspective (ahiṃsā principle)
- "Remembrance of the Supreme" is categorized alongside meditation as
  a "yogic" practice suitable only for sushumna — this reflects a
  haṭha-yoga framework, not a bhakti framework
- The Gauḍīya position is that nāma is **independent of all conditions**
  (ahaituky apratihatā — unmotivated and unimpeded, SB 1.2.6)

### The dinacharya_panchanga.csv is cleaner

This file's sources include "Ayurveda secondary" and "calendar tradition"
and correctly recommends "meditation/japa" during Brahma Muhurta without
contraindication. It does not mark bhakti practices as avoidable.

### The daily_program.csv is Gauḍīya-sourced

All 8 rows reference ISKCON/Gauḍīya temple schedule with attested
classical songs and mantras. No bhakti practices are contraindicated.

---

## RECOMMENDED ACTIONS (for human review)

### Option A: Override bhakti practices as always-acceptable
Change the 10 flagged rows from "avoid" to "acceptable" and add a note:
> "Overridden: navavidha bhakti practices are never contraindicated per
> Gauḍīya siddhānta (CC Antya 20.18, SB 1.2.6)"

### Option B: Add a Gauḍīya filter layer
Keep the Shiva Svarodaya data as-is (it's technically accurate to that text)
but add a filter in the dinacharya engine:
```python
ALWAYS_ACCEPTABLE = {'meditation', 'remembrance_of_supreme', 'yoga_sadhana', 'study'}
avoid = [a for a in raw_avoid if a not in ALWAYS_ACCEPTABLE]
```

### Option C: Split into separate traditions
Create a `tradition` column in activity_matrix.csv:
- `shaiva_tantric` for the raw Svarodaya rules
- `gaudiya_vaishnava` for the override rules
Let the engine select which tradition to apply based on user preference.

### NOT Recommended
- Auto-fixing without review
- Removing the Svarodaya data entirely (it's valid for its tradition)
- Silently hiding the data from the API

---

## Files Audited

| File | Rows | Source | Issues |
|------|------|--------|--------|
| `datasets/svarodaya/activity_matrix.csv` | 210 | Shiva Svarodaya | **10 rows flag bhakti as avoid** |
| `datasets/ayurveda/dinacharya_panchanga.csv` | 8 | Ayurveda + calendar | Clean |
| `datasets/cosmology/daily_program.csv` | 8 | Gauḍīya classical | Clean |
| Live `/dinacharya` endpoint | — | Engine synthesis | **Currently returns bhakti in avoid list** |
