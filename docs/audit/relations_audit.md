# Relations Layer Audit

Date: 2026-04-10

## Files: 26

### `bija_relations.csv` — 33 rows
- Columns: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence, notes`
- Subject types (from_id): {'bija:om': 3, 'bija:hrim': 3, 'bija:shrim': 3, 'bija:klim': 3, 'bija:gam': 3}
- Predicates (relation): {'bija': 9, 'deity': 8, 'element': 8, 'chakra': 8}
- Object types (to_id): {'element:fire': 3, 'element:air': 2, 'deity:universal': 1, 'element:ether': 1, 'chakra:cosmic': 1}
- Attestation (confidence): {'0.8': 33}

### `carnatic_relations.csv` — 82 rows
- Columns: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence, notes`
- Subject types (from_id): {'tala:dhruva': 10, 'tala:matya': 10, 'tala:rupaka': 10, 'tala:jhampa': 10, 'tala:triputa': 10}
- Predicates (relation): {'family': 35, 'beats': 35, 'kriti': 3, 'composer': 3, 'tala_family': 3, 'graha': 3}
- Object types (to_id): {'tala': 38, 'beats:7': 4, 'composer:muttusvami': 3, 'beats:11': 3, 'beats:8': 3}
- Attestation (confidence): {'0.9': 70, '0.6': 9, '0.8': 3}

### `deity_relations.csv` — 159 rows
- Columns: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence, notes`
- Subject types (from_id): {'deity:karttikeya': 8, 'deity:surya': 8, 'deity:chandra': 8, 'deity:durga': 7, 'deity:lakshmi': 7}
- Predicates (relation): {'vahana': 44, 'element': 40, 'domain': 39, 'weapon': 26, 'associated_graha': 10}
- Object types (to_id): {'element:fire': 12, 'element:air': 10, 'element:water': 8, 'element:earth': 7, 'vahana:hamsa': 4}
- Attestation (confidence): {'0.8': 159}

### `dosha_relations.csv` — 74 rows
- Columns: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence, notes`
- Subject types (from_id): {'nakshatra:purva': 6, 'nakshatra:uttara': 6, 'nakshatra:ashwini': 2, 'nakshatra:bharani': 2, 'nakshatra:krittika': 2}
- Predicates (relation): {'dosha': 27, 'secondary_dosha': 27, 'element': 7, 'governing_graha': 7, 'taste_quality': 6}
- Object types (to_id): {'dosha:pitta': 21, 'dosha:vata': 18, 'dosha:kapha': 15, 'graha:(to': 7, 'element:water': 3}
- Attestation (confidence): {'0.6': 37, '0.8': 33, '0.7': 4}

### `gaudiya_relations.csv` — 28 rows
- Columns: `from_id, relation, to_id, source, confidence, stability, authority`
- Subject types (from_id): {'ashtakala:nisanta': 3, 'ashtakala:pratah': 2, 'vraja:Vrindavana': 2, 'festival:Janmashtami': 2, 'ashtakala:purvahna': 1}
- Predicates (relation): {'expressed_as': 8, 'ashtakala': 4, 'ashtakala_forest': 3, 'tithi': 3, 'corresponds_to': 2, 'associated_plant': 2, 'eternal_realm': 2, 'appearance': 2}
- Object types (to_id): {'cosmology:Goloka': 3, 'raga:Darbari': 2, 'ashtakala:nisanta': 2, 'ashtakala:sayahna': 2, 'ashtakala:pratah': 2}
- Attestation (confidence): {'0.9': 10, '0.99': 8, '0.85': 6, '0.95': 3, '0.7': 1}

### `iching_relations.csv` — 1946 rows
- Columns: `from_id, relation, to_id, tradition, source, confidence, gaudiya_aligned, notes`
- Subject types (from_id): {'hexagram': 1906, 'trigram': 40}
- Predicates (relation): {'hexagram_raga_resonance': 545, 'hexagram_nakshatra_resonance': 533, 'changing_line': 384, 'hexagram_devi_resonance': 188, 'hexagram_lower_trigram': 64, 'hexagram_upper_trigram': 64, 'hexagram_graha': 64, 'hexagram_rasa': 64}
- Object types (to_id): {'raga': 545, 'nakshatra': 533, 'hexagram': 384, 'devi': 188, 'trigram': 128}
- Attestation (confidence): {'0.70': 553, '1.00': 512, '0.45': 195, '0.5': 138, '0.6': 83}

### `mythic_relations.csv` — 5 rows
- Columns: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence, notes`
- Subject types (from_id): {'mythic:krishna': 2, 'mythic:radha': 1, 'mythic:yashoda': 1, 'mythic:hanuman': 1}
- Predicates (relation): {'friend_of': 1, 'instructs': 1, 'beloved_of': 1, 'cares_for': 1, 'serves': 1}
- Object types (to_id): {'mythic:arjuna': 2, 'mythic:krishna': 2, 'mythic:rama': 1}
- Attestation (confidence): {'0.8': 5}

### `nadi_relations.csv` — 31 rows
- Columns: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence, notes`
- Subject types (from_id): {'nadi:pingala': 9, 'nadi:ida': 8, 'nadi:sushumna': 7, 'vara:ravivara': 1, 'vara:somavara': 1}
- Predicates (relation): {'favored_activity': 15, 'optimal_nadi': 7, 'element': 3, 'graha': 3, 'quality': 3}
- Object types (to_id): {'nadi:ida': 4, 'nadi:pingala': 3, 'element:water': 1, 'graha:moon': 1, 'quality:cooling': 1}
- Attestation (confidence): {'0.9': 17, '0.7': 7, '0.6': 7}

### `nakshatra_associated_deity.csv` — 73 rows
- Columns: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence, notes`
- Subject types (from_id): {'nakshatra:rohini': 5, 'nakshatra:mula': 5, 'nakshatra:purva': 5, 'nakshatra:uttara': 5, 'nakshatra:ashwini': 4}
- Predicates (relation): {'nakshatra_associated_deity': 73}
- Object types (to_id): {'deity:agni': 24, 'deity:yama': 20, 'deity:shiva': 18, 'deity:brahma': 6, 'deity:soma': 2}
- Attestation (confidence): {'attested_secondary': 73}

### `ratna_relations.csv` — 45 rows
- Columns: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence, notes`
- Subject types (from_id): {'graha:surya': 4, 'graha:chandra': 4, 'graha:mangala': 4, 'graha:budha': 4, 'graha:guru': 4}
- Predicates (relation): {'ratna': 9, 'graha': 9, 'substitute_ratna': 9, 'metal': 9, 'consecration_mantra': 9}
- Object types (to_id): {'mantra:om': 9, 'metal:gold': 4, 'metal:silver': 4, 'ratna:red': 2, 'ratna:ruby': 1}
- Attestation (confidence): {'0.8': 45}

### `relational_repair.csv` — 209 rows
- Columns: `from_id, relation, to_id, tradition, source, confidence, gaudiya_aligned, notes`
- Subject types (from_id): {'bija:aim': 14, 'devi:kulasundari': 7, 'devi:bhagamalini': 6, 'devi:bherunda': 6, 'devi:vahnivasini': 6}
- Predicates (relation): {'devi_weapon': 29, 'nakshatra_element': 27, 'nakshatra_guna': 27, 'raga_rasa': 16, 'devi_mantra': 15, 'devi_rasa': 15, 'tithi_nitya_devi': 15, 'devi_shakti': 15}
- Object types (to_id): {'mantra:om': 30, 'rasa:shringara': 12, 'guna:rajas': 9, 'guna:tamas': 9, 'guna:sattva': 9}
- Attestation (confidence): {'0.92': 113, '0.85': 35, '0.88': 31, '0.95': 15, '0.90': 15}

### `relations_devi_weapon.csv` — 15 rows
- Columns: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence, notes`
- Subject types (from_id): {'devi:bhagamalini': 1, 'devi:bherunda': 1, 'devi:chitra': 1, 'devi:jvalamalini': 1, 'devi:kameshvari': 1}
- Predicates (relation): {'devi_wields_weapon': 15}
- Object types (to_id): {}
- Attestation (confidence): {'seed_unverified': 15}

### `relations_nakshatra_deity.csv` — 27 rows
- Columns: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence, notes`
- Subject types (from_id): {'nakshatra:1': 1, 'nakshatra:2': 1, 'nakshatra:3': 1, 'nakshatra:4': 1, 'nakshatra:5': 1}
- Predicates (relation): {'nakshatra_associated_deity': 27}
- Object types (to_id): {'deity:ashwini': 1, 'deity:yama': 1, 'deity:agni': 1, 'deity:brahma': 1, 'deity:soma': 1}
- Attestation (confidence): {'attested_secondary': 19, 'seed_unverified': 8}

### `relations_nakshatra_graha.csv` — 27 rows
- Columns: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence, notes`
- Subject types (from_id): {'nakshatra:1': 1, 'nakshatra:2': 1, 'nakshatra:3': 1, 'nakshatra:4': 1, 'nakshatra:5': 1}
- Predicates (relation): {'nakshatra_ruling_graha': 27}
- Object types (to_id): {'graha:ketu': 3, 'graha:venus': 3, 'graha:sun': 3, 'graha:moon': 3, 'graha:mars': 3}
- Attestation (confidence): {'attested_secondary': 25, 'seed_unverified': 2}

### `relations_nakshatra_plants.csv` — 135 rows
- Columns: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence, notes`
- Subject types (from_id): {'plant:Ashvagandha': 4, 'plant:Amalaki': 4, 'plant:Udumbara': 4, 'plant:Mallika': 4, 'plant:Khadira': 4}
- Predicates (relation): {'nakshatra_sacred_plant': 27, 'sacred_to': 27, 'dosha_balance': 27, 'element': 27, 'body_region': 27}
- Object types (to_id): {'ayurveda:Vata': 10, 'ayurveda:Pitta': 9, 'element:Fire': 8, 'ayurveda:Kapha': 8, 'element:Water': 8}
- Attestation (confidence): {'verified': 135}

### `relations_raga_ritual.csv` — 0 rows
- Columns: ``

### `relations_resolved_canon.csv` — 44 rows
- Columns: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence, notes`
- Subject types (from_id): {'nakshatra:2': 2, 'nakshatra:3': 2, 'nakshatra:4': 2, 'nakshatra:5': 2, 'nakshatra:6': 2}
- Predicates (relation): {'nakshatra_ruling_graha': 25, 'nakshatra_associated_deity': 19}
- Object types (to_id): {'graha:venus': 3, 'graha:sun': 3, 'graha:moon': 3, 'graha:mars': 3, 'graha:rahu': 3}
- Attestation (confidence): {'attested_secondary': 44}

### `relations_resolved_inference.csv` — 132 rows
- Columns: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence, notes`
- Subject types (from_id): {'nakshatra:uttara': 10, 'nakshatra:purva': 10, 'nakshatra:mula': 8, 'nakshatra:rohini': 8, 'nakshatra:punarvasu': 8}
- Predicates (relation): {'nakshatra_associated_deity': 132}
- Object types (to_id): {'deity:agni': 81, 'deity:yama': 23, 'deity:shiva': 18, 'deity:brahma': 7, 'deity:vishnu': 2}
- Attestation (confidence): {'inferred_coherent': 132}

### `relations_resolved_overlays.csv` — 323 rows
- Columns: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence, notes`
- Subject types (from_id): {'nakshatra:rohini': 21, 'nakshatra:uttara': 18, 'nakshatra:anuradha': 16, 'nakshatra:purva': 16, 'nakshatra:punarvasu': 15}
- Predicates (relation): {'nakshatra_associated_deity': 272, 'nakshatra_sacred_plant': 27, 'devi_wields_weapon': 15, 'ritual_prescribed_on': 7, 'nakshatra_ruling_graha': 2}
- Object types (to_id): {'deity:ashwini': 143, 'deity:agni': 48, 'deity:brahma': 30, 'deity:vishnu': 14, 'deity:yama': 12}
- Attestation (confidence): {'seed_unverified': 323}

### `relations_resolved_proto_canon.csv` — 0 rows
- Columns: ``

### `relations_ritual_calendar.csv` — 10 rows
- Columns: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence, notes`
- Subject types (from_id): {'ritual:fast': 10}
- Predicates (relation): {'ritual_prescribed_on': 10}
- Object types (to_id): {'tithi:Ekadashi': 3, 'tithi:Dvadashi': 3, 'tithi:Trayodashi': 3, 'tithi:Navami': 1}
- Attestation (confidence): {'seed_unverified': 10}

### `s0_roots.csv` — 84 rows
- Columns: `from_id, relation, to_id, attestation, notes`
- Subject types (from_id): {'nakshatra': 25, 'art': 25, 'raga': 12, 'graha': 9, 'deity': 8}
- Predicates (relation): {'s0_root': 84}
- Object types (to_id): {'tattva': 64, 'rasa': 19, 'parampara': 1}
- Attestation (attestation): {'SYNTHESIS': 54, 'TRADITIONAL': 30}

### `sound_relations.csv` — 315 rows
- Columns: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence, notes`
- Subject types (from_id): {'chandas:ved': 68, 'chandas:cls': 20, 'chandas:vern': 16, 'chandas:prose': 12, 'raga:Bhairavi': 9}
- Predicates (relation): {'optimal_nadi': 67, 'direction': 37, 'vastu_element': 32, 'nakshatra_family': 32, 'optimal_time': 18, 'best_activity': 17, 'treats_condition': 16, 'purpose': 14}
- Object types (to_id): {'nadi:ida': 37, 'nakshatra': 32, 'nadi:pingala': 30, 'element:fire': 11, 'direction:west': 9}
- Attestation (confidence): {'0.9': 173, '0.8': 70, '0.6': 46, '0.95': 18, '0.7': 8}

### `species_relations.csv` — 163 rows
- Columns: `from_id, relation, to_id, tradition, source, confidence, gaudiya_aligned, notes`
- Subject types (from_id): {'species:ashva': 6, 'species:gaja': 6, 'species:mesha': 6, 'species:sarpa': 6, 'species:shvan': 6}
- Predicates (relation): {'species_graha': 44, 'species_element': 44, 'species_plant': 35, 'nakshatra_yoni': 27, 'deity_vahana': 13}
- Object types (to_id): {'element:fire': 12, 'element:air': 10, 'element:earth': 10, 'element:water': 9, 'graha:mars': 8}
- Attestation (confidence): {'0.95': 58, '0.92': 15, '0.855': 14, '0.8075': 14, '0.90': 8}

### `text_entity_relations.csv` — 1442 rows
- Columns: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence, notes`
- Subject types (from_id): {'chunk:brihat': 681, 'chunk:bhagavata': 626, 'chunk:charaka': 49, 'chunk:hatha': 38, 'chunk:gheranda': 10}
- Predicates (relation): {'mentions': 1442}
- Object types (to_id): {'vastu': 263, 'deity': 229, 'parampara': 209, 'plant': 199, 'graha': 185}
- Attestation (confidence): {'0.7': 1442}

### `vastu_relations.csv` — 145 rows
- Columns: `from_id, relation, to_id, source_title, source_locator, excerpt, tradition, confidence, notes`
- Subject types (from_id): {'vastu': 109, 'direction:east': 4, 'direction:southeast': 4, 'direction:south': 4, 'direction:southwest': 4}
- Predicates (relation): {'element': 41, 'direction': 32, 'function': 32, 'domain': 13, 'deity': 9, 'graha': 9, 'activity': 9}
- Object types (to_id): {'element:earth': 11, 'element:air': 9, 'element:water': 8, 'direction:east': 8, 'direction:south': 8}
- Attestation (confidence): {'0.9': 109, '0.8': 36}

## Summary

- Total rows: 5547
- Unique subjects: 1687
- Unique objects: 913
- Top predicates: {'mentions': 1442, 'hexagram_raga_resonance': 545, 'hexagram_nakshatra_resonance': 533, 'nakshatra_associated_deity': 523, 'changing_line': 384, 'hexagram_devi_resonance': 188, 'element': 126, 's0_root': 84, 'optimal_nadi': 74, 'direction': 69}
- Attestation distribution: {'0.7': 1462, '0.70': 556, '1.00': 512, '0.8': 431, '0.9': 429, 'seed_unverified': 358, '0.45': 195, '0.6': 182}

## Entity Resolution

- Known entity IDs: 202
- Relation subjects: 1687
- Unresolved: 1682 (5 shown)
  - `art_agriculture`
  - `art_architecture`
  - `art_astrology`
  - `art_cooking`
  - `art_dancing`
