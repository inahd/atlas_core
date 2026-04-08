# Cross-tradition Doctrine of Signatures

## Objective
Map plant-body correspondences across Ayurveda, Western Herbalism, and Traditional Chinese Medicine to find convergent "signatures" — where multiple traditions agree a plant's form indicates its therapeutic target.

## Research Questions
1. What are the core Ayurvedic dravyaguna principles linking plant morphology to therapeutic action?
2. How does Paracelsian Doctrine of Signatures map onto Ayurvedic rasa/guna/virya/vipaka?
3. Which plants in our existing `datasets/plants/` have cross-tradition signature agreement?
4. Can we derive a "signature confidence score" based on number of traditions agreeing?

## Sources to Consult
- Charaka Samhita, Sutrasthana (dravyaguna classification)
- Culpeper's Complete Herbal (Western signatures)
- Li Shizhen, Bencao Gangmu (TCM morphological correspondences)
- Existing: `datasets/plants/guild_relations.csv` (216 rows)
- Existing: `datasets/ayurveda/` (dhatu, herb matrices)

## Output Format
CSV: `plant_id, common_name, signature_type (color/shape/habitat/texture), body_target, ayurveda_match, western_match, tcm_match, confidence`
Plus narrative on convergence patterns.

## Atlas Integration
- S5 (Nature): extends plant wheel with cross-tradition validation
- S4 (Geometry): signature morphology → yantra form correspondences

## Priority
Medium — enriches existing plant data

## Field Optimal
Shukravara (Friday) — Venus-ruled, auspicious for plant/beauty/form work
