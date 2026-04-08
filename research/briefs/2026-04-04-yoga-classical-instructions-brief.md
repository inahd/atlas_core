# Classical Yoga Instructions

## Objective
Extract precise, practice-ready instructions from classical yoga texts (Hatha Yoga Pradipika, Gheranda Samhita, Shiva Samhita) for integration into Atlas S6 (Practice/Lila) layer.

## Research Questions
1. What are the exact asana instructions in HYP (15 asanas), GS (32 asanas), SS (84 referenced, fewer described)?
2. How do pranayama instructions differ across the three texts?
3. What are the stated prerequisites, contraindications, and sequencing rules?
4. How do these map to existing Atlas practice/codex structures?

## Sources to Consult
- Hatha Yoga Pradipika (Svatmarama) — preferably Muktibodhananda commentary
- Gheranda Samhita — Mallinson translation
- Shiva Samhita — critical edition
- Existing: `datasets/yoga/` (check current yoga datasets)
- Existing: `npu_engine/codex_engine.py` (codex text retrieval)

## Output Format
CSV: `text_source, chapter, verse, practice_type (asana/pranayama/mudra/bandha), sanskrit_name, english_name, instruction_summary, prerequisites, contraindications, benefits_stated`
Plus a sequencing document showing classical practice order from each text.

## Atlas Integration
- S6 (Lila/Practice): direct practice instructions
- S2 (Sound): pranayama → sound correspondences
- S5 (Nature): therapeutic claims → Ayurvedic validation

## Priority
High — directly actionable for practice layer

## Field Optimal
Guruvara (Thursday) — Jupiter-ruled, auspicious for textual study and transmission
