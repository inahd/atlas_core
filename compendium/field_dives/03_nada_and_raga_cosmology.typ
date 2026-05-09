#import "../_shared/preamble.typ": compendium-preamble, title-page

#compendium-preamble(
  title: "Nada and Raga Cosmology",
  subtitle: "Field Dive",
  version: "1.0 — converted from markdown",
)

#title-page(
  title: "Nada and Raga Cosmology",
  subtitle: "Sound as the medium of descent: para through vaikhari",
  volume: "COHERENCE ATLAS · FIELD DIVE III",
  version: "1.0 · April 2026",
)

#v(0.6in)
#align(center)[#text(size: 11pt, weight: "semibold")[Status]]
#v(0.4em)

_Converted from `research/research_gandharva_veda.md`. Content-lossless conversion._

#pagebreak()

#outline(
  title: [#text(size: 12pt, weight: "semibold")[Contents]],
  indent: 1.8em,
  depth: 2,
)

#pagebreak()

// ─── CONVERTED CONTENT ──────────────────────────────────

= Gandharva Veda Music Therapy Knowledge Graph Dataset


== Source base and attestation framework


=== What “Gāndharvaveda” and “Gandharva Veda music therapy” can mean in practice

“Gāndharvaveda / Gandharvaveda” is commonly glossed in Sanskrit lexicographic tradition as the _science/veda of music_ (often treated as connected to Sāmaveda and sometimes described as an appendix/upaveda in later classificatory schemes). citeturn61search8 In modern “music-as-therapy” contexts, the term is often used more broadly for “Vedic” or “Vedic-inspired” sound-based self-regulation systems, but most _rāga → dosha → disease_ mappings are _not explicitly found_ in the earliest music śāstra sources and must therefore be tagged by _attestation status_ rather than presented as uniformly “Vedic.”

=== Primary classical anchors used here

This dataset is built on _three tiers_ of sources, to keep “traditional musicology” separate from “therapeutic claims”:

- _Tier A: Core music-śāstra sources_ (directly cited for sound theory / śruti theory / definitions):
  - _Nāṭyaśāstra_ (Bharata), especially its account of two grāmas and the classic _22-śruti_ distribution across svaras. citeturn33view0
  - _Saṅgītaratnākara_ (Śārṅgadeva), using _C. Kunhan Raja’s_ translation for: āhata/anāhata nāda, nāda-brahman, the bodily “path” of sound manifestation, and the _named śruti varieties_ with semantic glosses (e.g., _tīvrā_, _raudrī_, _krodha_, etc.). citeturn24view0turn24view2turn41view1
  - _Bṛhaddeśī_ (Mataṅga), here accessed indirectly via a scholarly summary quoting Matanga’s rāga-definition (see Tier B below). citeturn35view0

- _Tier B: Scholarly/curatorial secondary sources_ (definitions, context, and interpretive bridges):
  - A detailed secondary digest quoting Matanga’s definition of rāga (“that which colours/delights the mind…”), attributed to Bṛhaddeśī. citeturn35view0

- _Tier C: Modern therapeutic / experimental studies_ (peer-reviewed when available):
  - A validated “Rāga Module” (RM) for _Pitta imbalance / anger trait / Amlapitta (GERD)_ with explicit rāga timing and listening parameters. citeturn54view0
  - A randomized controlled trial on cardiovascular/HRV effects of listening to _Rāga Bhimpalās_. citeturn57view0
  - A month-long intervention study using _Rāga Toḍī_ reporting reductions in BP, pulse, and respiratory rate in older adults. citeturn57view1
  - A randomized controlled trial using ERPs (oddball task) with 10-minute listening to _Miyā̃ kī Toḍī, Mālkauṃs, Pūriyā_ (attention/cognitive engagement proxy). citeturn60view0

=== Attestation status schema used in all CSVs

Every row includes an `attestation_status` field encoded as `field:STATUS` pairs. The statuses used are:

- `PRIMARY_TEXT`: explicitly stated in Nāṭyaśāstra / Saṅgītaratnākara (as cited).
- `SECONDARY_SCHOLARLY`: scholarly/curatorial secondary summary quoting or discussing primary texts.
- `PEER_REVIEWED`: peer-reviewed modern study with methods/results.
- `TRADITIONAL_PRACTICE`: widely taught practice convention (e.g., samay/time-theory), not a primary-text “medical” claim.
- `ENGINEERED_PROTOCOL`: designed protocol (yoga + listening) grounded in plausible mechanisms but not text-attested.
- `INFERRED_MODEL`: a knowledge-graph mapping choice (e.g., S0–S6 layering) not asserted by the texts.

== Raga × Dosha × Condition dataset


=== Notes on scope and how to read the claims

The _priority ragas_ you listed are treated as “major ragas” for this deliverable. The _only_ dosha-specific rāga selection in the retrieved corpus with explicit validation and clinical feasibility is the _Pitta imbalance RM_ paper (GERD/Amlapitta + anger trait), which provides timing and listening parameters and anchors Pitta-oriented rāga selection in a reproducible protocol. citeturn54view0

Everything else (especially “vata/kapha for each rāga”) must be treated as _traditional-practice inference_ unless a peer-reviewed intervention exists for that specific rāga.

=== CSV: `part1_raga_dosha_condition.csv`

```csv
raga_id,name_iast,primary_dosha_effect,secondary_dosha_effect,best_time_prahar,therapeutic_conditions,contraindications,optimal_duration_minutes,optimal_volume,instrument_primary,source_text,attestation_status,modern_research
R001,Bhairava,"pitta:reduces","vata:reduces","dawn (approx 4-7am)","pitta_imbalance;anger_trait;Amlapitta/GERD_support","none_specific;avoid high volume if headache/migraine sensitivity","15","soft-medium","sitar_or_rudraveena","RM for Pitta imbalance (timing + feasibility)","best_time:PEER_REVIEWED;dosha_effect:PEER_REVIEWED;conditions:PEER_REVIEWED;duration:PEER_REVIEWED;volume:PEER_REVIEWED;instrument:PEER_REVIEWED","Nagarajan+Varma RM (Pitta/Amlapitta) – Bhairav used morning"
R002,Bhairavi,"vata:reduces","pitta:reduces","morning (approx 7-10am)","anxiety_downregulation(traditional);sleep_support(traditional);grief/karuna_processing(traditional)","may_increase_kapha_lethargy_if_overused(traditional)","20","soft","vocal_or_bansuri","Traditional therapy claims (non-primary); use as soothing late/morning raga","best_time:TRADITIONAL_PRACTICE;dosha_effect:INFERRED_MODEL;conditions:TRADITIONAL_PRACTICE;duration:ENGINEERED_PROTOCOL",""
R003,Yaman,"kapha:reduces","vata:reduces","early night (approx 6-9pm)","mood_uplift(traditional);creative_activation(traditional);focus_support(traditional)","if_acid_heat/pitta_aggravation_then_reduce_tempo_and_volume","15","medium","sitar","General Hindustani use; no specific dosha trial located in retrieved set","best_time:TRADITIONAL_PRACTICE;dosha_effect:INFERRED_MODEL;conditions:TRADITIONAL_PRACTICE",""
R004,Mārwā,"pitta:reduces","vata:neutral","night (approx 7-10pm)","anger_trait_support;stress_downshift","none_specific","15","soft-medium","sitar_or_vocal","RM for Pitta imbalance lists Marwa with time window","best_time:PEER_REVIEWED;dosha_effect:PEER_REVIEWED;conditions:PEER_REVIEWED","Nagarajan+Varma RM (Pitta/Amlapitta) – Marwa listed 7-10pm"
R005,Dārbārī (Kānaḍā lineage),"vata:reduces","pitta:reduces","late night (approx 9pm-12am)","blood_pressure_support(traditional+literature);sleep_induction(traditional)","daytime_use_may_increase_dullness/kapha(traditional)","22","soft","vocal_or_sarod","Referenced in raga-therapy BP literature; Darbari mentioned as part of multi-raga hypertension listening in the Todi paper discussion","best_time:TRADITIONAL_PRACTICE;dosha_effect:INFERRED_MODEL;conditions:SECONDARY_SCHOLARLY",""
R006,Bāgeśrī,"vata:reduces","pitta:neutral","late night (approx 10pm-1am)","sleep_support(traditional);anxiety_support(traditional)","kapha_static_mood_if_overused(traditional)","20","soft","bansuri_or_vocal","Traditional late-night soothing use; no direct clinical trial in retrieved set","best_time:TRADITIONAL_PRACTICE;dosha_effect:INFERRED_MODEL;conditions:TRADITIONAL_PRACTICE",""
R007,Bhīmpalāsī,"pitta:reduces","vata:reduces","afternoon (approx 1-4pm)","BP_and_HRV_modulation;stress_support","none_specific","10","soft-medium","recorded_instrumental","Randomized controlled trial evaluated ‘raga Bhimpalas’ with BP/HRV endpoints","best_time:TRADITIONAL_PRACTICE;dosha_effect:INFERRED_MODEL;conditions:PEER_REVIEWED;duration:PEER_REVIEWED","IJPP RCT: passive listening to raga Bhimpalas – BP/HRV"
R008,Toḍī (incl. Miyā̃ kī Toḍī family),"pitta:reduces","vata:reduces","morning (approx 6-9am)","BP_reduction;respiratory_rate_reduction;attention_modulation(ERP)","if_excess_lethargy_then_reduce_duration","10;30","soft-medium","instrumental","30-day morning listening to raga Todi reduced SBP/DBP/pulse/respiration; ERP RCT used Miyān ki Todi","best_time:TRADITIONAL_PRACTICE;conditions:PEER_REVIEWED;duration:PEER_REVIEWED","BHU JSR 2020 (BP/pulse/resp); Music&Medicine 2025 ERP RCT (Miyan ki Todi)"
R009,Multānī,"pitta:reduces","vata:neutral","afternoon (approx 1-4pm)","heat/pitta_downshift(traditional);calm_focus(traditional)","avoid_if_low_energy_kapha_dominant(traditional)","15","soft","bansuri_or_vocal","No direct trial in retrieved set; mapped by note-structure similarity to pitta-reducing komal Re/Dha families","best_time:TRADITIONAL_PRACTICE;dosha_effect:INFERRED_MODEL;conditions:TRADITIONAL_PRACTICE",""
R010,Sāraṅg (umbrella Sarang family),"kapha:reduces","pitta:neutral","midday (approx 12-3pm)","fatigue_downshift(traditional);heat_season_regulation(traditional)","avoid_if_high_pitta_and_raga_feels_activating","15","medium","bansuri","General seasonal/time association; no direct retrieved clinical trial","best_time:TRADITIONAL_PRACTICE;dosha_effect:INFERRED_MODEL",""
R011,Kedāra,"vata:reduces","pitta:neutral","night (approx 9pm-12am)","sleep_support(traditional);devotional_downshift(traditional)","none_specific","20","soft","vocal","Traditional night devotional use","best_time:TRADITIONAL_PRACTICE;dosha_effect:INFERRED_MODEL",""
R012,Mālkauṃs,"vata:reduces","kapha:neutral","late night (approx 12-3am)","attention_engagement_shift(ERP);meditation_support(traditional)","may_feel_heavy_in_depression(traditional)","10","soft","instrumental_drone_based","ERP RCT tested Malkauns (attention/cognitive engagement proxy)","best_time:TRADITIONAL_PRACTICE;conditions:PEER_REVIEWED;duration:PEER_REVIEWED","Music&Medicine 2025 ERP RCT (Malkauns)"
R013,Pūriyā,"pitta:reduces","vata:neutral","evening-night (approx 7-10pm)","attention_engagement_shift(ERP);pitta_module_related_raga_set","none_specific","10;15","soft-medium","instrumental","ERP RCT used Puriya; Pitta RM includes closely related Purvi/Marwa families and lists Puriya timing","best_time:PEER_REVIEWED;conditions:PEER_REVIEWED","Music&Medicine 2025 ERP RCT (Puriya); Nagarajan+Varma RM includes Puriya 7-10pm"
R014,Śrī,"pitta:reduces","vata:neutral","evening (approx 4-7pm)","anger_trait_support;pitta_module_raga","none_specific","15","soft-medium","instrumental","Pitta RM lists Shree 4-7pm with high expert agreement","best_time:PEER_REVIEWED;dosha_effect:PEER_REVIEWED;conditions:PEER_REVIEWED","Nagarajan+Varma RM (Pitta/Amlapitta) – Shree 4-7pm"
R015,Lalita,"pitta:reduces","vata:neutral","dawn (approx 4-7am)","pitta_module_raga;calm_mind_support(traditional)","none_specific","15","soft-medium","instrumental","Pitta RM lists Lalit 4-7am","best_time:PEER_REVIEWED;dosha_effect:PEER_REVIEWED","Nagarajan+Varma RM – Lalit 4-7am"
R016,Bhūpālī,"kapha:reduces","vata:reduces","early night (approx 6-9pm)","motivation_activation(traditional);concentration_support(traditional)","if_pitta_spike_then_use_softer_tempo","12","medium","bansuri","No specific clinical trial in retrieved set","best_time:TRADITIONAL_PRACTICE;dosha_effect:INFERRED_MODEL",""
R017,Kāfī,"vata:reduces","pitta:neutral","evening (approx 6-9pm)","grief_processing(traditional);social_emotional_regulation(traditional)","none_specific","20","soft","vocal","Traditional rasa/emotion framing; no retrieved clinical trial","best_time:TRADITIONAL_PRACTICE;dosha_effect:INFERRED_MODEL",""
R018,Khāmāj,"vata:neutral","pitta:increases","late night (approx 9pm-12am)","affective_opening(traditional);creative_support(traditional)","avoid_if_anger/pitta_aggravation","15","medium","vocal","Traditional romantic rasa association; not validated dosha study in retrieved set","best_time:TRADITIONAL_PRACTICE;dosha_effect:INFERRED_MODEL",""
R019,Bilāvalā,"kapha:reduces","vata:neutral","morning (approx 7-10am)","mood_uplift(traditional);cognitive_clarity(traditional)","none_specific","15","medium","vocal","General ‘shuddha scale’ uplifting framing; no retrieved clinical trial","best_time:TRADITIONAL_PRACTICE;dosha_effect:INFERRED_MODEL",""
```

_Key high-confidence anchors inside Part One_: (a) the _Pitta RM_ paper explicitly links a rāga-module to Pitta imbalance and anger trait with time windows and listening parameters (including 50–70 dB guidance and instrument choice). citeturn54view0 (b) BP/HRV and physiological endpoints exist for _Bhimpalās_ and _Toḍī_ interventions. citeturn57view0turn57view1 (c) ERP-based cognitive-engagement differences were tested with _Miyā̃ kī Toḍī, Mālkauṃs, Pūriyā_. citeturn60view0

== Nada Brahma sound cosmology mapping


=== Anāhata and Āhata nāda in Saṅgītaratnākara

Saṅgītaratnākara (as translated by Kunhan Raja) explicitly distinguishes _two kinds of nāda_—_āhata_ and _anāhata_—with the simple explanatory gloss _audible vs. inaudible_. citeturn24view0 It further explains _āhata_ as “beaten” (subject to modification; articulated; audible) and _anāhata_ as “not beaten” (immutable; pure; inarticulate; inaudible). citeturn24view0

The same translation frames _Nāda-Brahman_ as the life/sentience/bliss of all beings, and notes that worship of nāda is thereby worship of Brahmā/Viṣṇu/Maheśvara insofar as they are of its nature. citeturn24view2

=== The bodily “path” of sound manifestation (a crucial bridge to chakra-style mappings)

Saṅgītaratnākara describes a causal chain—self desires to speak → mind → fire → wind—and then the wind rising to manifest sound “successively” at _navel, heart, throat, head, mouth_, with a graded series of subtlety labels (very subtle → subtle → developed → undeveloped → artificial). citeturn24view2 This is the strongest classical anchor available in the retrieved corpus for connecting sound phenomenology to embodied “levels.”

=== Four levels of sound and Vāc

The earliest “fourfold speech” motif is already present in the Ṛgveda verse _1.164.45_ (“four measured parts of speech…” with “three hidden” and “the fourth spoken by humans”). citeturn39search3 The explicit technical labels _Parā / Paśyantī / Madhyamā / Vaikharī_ are widely transmitted in later grammatical and tantric traditions; they are not consistently explicit in the passages of Nāṭyaśāstra/Saṅgītaratnākara surfaced here, so their mapping into an NPU layer-system must be tagged as _model-level inference_ rather than primary-text attestation.

=== CSV: `part2_nada_brahma_sound_cosmology.csv`

```csv
record_id,concept_category,name_iast,english_label,description,related_to,mapped_to_chakra,mapped_to_element,mapped_to_S_layer,source_text,attestation_status
NB001,nada_type,anāhata-nāda,unstruck_sound,"Inaudible/immutable ‘unbeaten’ sound; described as not subject to modification; inarticulate/inaudible in the translation notes",nāda,"(yogic mapping often links to anāhata-cakra but SR distinguishes conceptually)","(not specified in SR)","S0 (unmanifest core)","Saṅgītaratnākara (Kunhan Raja tr.): nāda of two kinds; anāhata vs āhata; anāhata described as ‘not beaten’ and inaudible",definition:PRIMARY_TEXT;chakra_element_mapping:INFERRED_MODEL
NB002,nada_type,āhata-nāda,struck_sound,"Audible/articulated ‘beaten’ sound; cause of śruti etc. and basis for manifest music",śruti+svara,"(voice/instrument pathway intersects throat/mouth articulation chain)","(not specified in SR)","S4–S6 (manifest acoustic)","Saṅgītaratnākara (Kunhan Raja tr.): āhata = beaten; audible; cause of śruti etc.",definition:PRIMARY_TEXT;S_layer_mapping:INFERRED_MODEL
NB003,metaphysics,nāda-brahman,ultimate_sound_principle,"Nāda-Brahman described as life of beings; world as transformation; worship of nāda worships deities insofar as they are of its nature",Brahman,"(not specified)","(not specified)","S0","Saṅgītaratnākara (Kunhan Raja tr.): ‘We worship the Nuda-Brahman…’; deities worshiped through nāda",PRIMARY_TEXT
NB004,somatic_path,nābhi→hṛt→kaṇṭha→mūrdhā→āsya,navel_to_mouth_sound_path,"Sound (via prāṇa/wind) manifests successively at navel, heart, throat, head, mouth",levels_of_sound,"manipūra/anāhata/viśuddha/ājñā/(vaikharī mouth)","(not specified in SR)","S2–S6 ladder","Saṅgītaratnākara (Kunhan Raja tr.): wind rises and manifests sound; five positions and five subtlety labels",path:PRIMARY_TEXT;chakra_mapping:INFERRED_MODEL
NB005,levels,five_sr_levels,very_subtle_to_artificial,"Five labels: atisūkṣma (navel), sūkṣma (heart), puṣṭa (throat), apuṣṭa (head), kṛtrima (mouth)",NB004,"see NB004","(not specified)","S2–S6","Saṅgītaratnākara (Kunhan Raja tr.): verse on five names at five positions",PRIMARY_TEXT
NB006,vac_doctrine,catuṣpad_vāk,four_parts_of_speech,"Rigveda 1.164.45: ‘four parts’ of speech; three hidden; fourth spoken",para_pashyanti_madhyama_vaikhari,"(not specified)","(not specified)","S0–S3 (proposed)","Ṛgveda 1.164.45 (fourfold speech motif)",PRIMARY_TEXT_FOR_VERSE;mapping_to_named_levels:INFERRED_MODEL
NB007,levels,parā/paśyantī/madhyamā/vaikharī,levels_of_vac,"Standard later doctrine: Para (transcendent), Pashyanti (visionary), Madhyama (mental), Vaikhari (spoken/sung)",catuṣpad_vāk,"(often mapped to sahasrāra/ājñā/viśuddha/mouth)","(not specified)","S0/S1/S2/S3","Included to serve NPU mapping needs; not directly surfaced as explicit terms in retrieved SR/NS excerpts",terms:SECONDARY_SCHOLARLY;mapping:INFERRED_MODEL
```

== Shruti science dataset


=== What Nāṭyaśāstra and Saṅgītaratnākara clearly attest

Nāṭyaśāstra (Ghosh tr.) explains the two grāmas and their internal constitution, stating that each grāma includes _22 śrutis_, and it gives the classic distribution (Sadja grāma: Sa 4, Re 3, Ga 2, Ma 4, Pa 4, Dha 3, Ni 2). citeturn33view0

Saṅgītaratnākara explains 22 śruti varieties as “heard” (from √śru) and situates them in a physiology-inflected account (22 nāḍīs and the production/organization of śrutis). citeturn24view2turn40view3

It also provides a _named set of śruti varieties_, grouped under five kinds (dīpta/āyata/mṛdu/madhya/kāruṇa), whose sub-varieties total _22_ and are glossed semantically (e.g., _tīvrā_ “fierce,” _krodha_ “wrathful,” _ramyā_ “charming,” etc.). citeturn41view1

=== Ratios

Saṅgītaratnākara’s excerpted translation discusses relative pitch relationships but does not provide a single “canonical modern ratio table” for all 22 named śrutis in the surfaced passages. citeturn41view2 Therefore this dataset uses a _modern mathematical reconstruction_ of the 22-śruti Shadaj-grām as ratios (a just-intonation style model) via the PureTones “Bharat & Sarang Dev’s 22 Shrutis” reconstruction table. citeturn50view0 This must be marked `INFERRED_MODEL` for the _name↔position_ alignment.

=== CSV: `part3_shruti_science.csv`

```csv
shruti_id,name_iast,sruti_jati_category,gloss_english,ratio_just_intonation,psychological_quality,physical_resonance,swara_association,raga_usage,source_text,attestation_status
S01,Tīvrā,Dīpta,fierce,9/10,"energetic/penetrating (semantic)","micro-position within Sa region (model)","Sa","all ragas (Sa present)","Names+glosses from Saṅgītaratnākara; ratios from modern Shadaj-gram reconstruction table","name+gloss:PRIMARY_TEXT;ratio:SECONDARY_SCHOLARLY;name↔ratio_alignment:INFERRED_MODEL"
S02,Kumudvatī,Āyata,lily-pond,15/16,"cooling/soothing imagery (semantic)","micro-position within Sa region (model)","Sa","all ragas (Sa present)","SR names+glosses; PureTones ratios table","name+gloss:PRIMARY_TEXT;ratio:SECONDARY_SCHOLARLY;alignment:INFERRED_MODEL"
S03,Mandā,Mṛdu,slow,80/81,"settling/downshifting (semantic)","micro-position within Sa region (model)","Sa","all ragas (Sa present)","SR names+glosses; PureTones ratios","name+gloss:PRIMARY_TEXT;ratio:SECONDARY_SCHOLARLY;alignment:INFERRED_MODEL"
S04,Chandovatī,Madhya,metrical,1/1,"structured/steady (semantic)","Sa anchor point (model)","Sa","all ragas (Sa present)","SR names+glosses; PureTones table sets Sa at 1","name+gloss:PRIMARY_TEXT;ratio:SECONDARY_SCHOLARLY;alignment:INFERRED_MODEL"
S05,Dayāvatī,Kāruṇa,merciful,25/24,"compassion/softening (semantic)","micro-position entering Ri/Ga domain (model)","Ri","ragas with komal/shuddha Ri (most)","SR names+glosses show Dayavati as Karuna-type; ratios from PureTones table","name+gloss:PRIMARY_TEXT;ratio:SECONDARY_SCHOLARLY;alignment:INFERRED_MODEL"
S06,Rañjanī,Madhya,pleasing,800/729,"pleasant/attractive (semantic)","Ri region (model)","Ri","ragas using Ri prominently","SR names+glosses; PureTones ratios","name+gloss:PRIMARY_TEXT;ratio:SECONDARY_SCHOLARLY;alignment:INFERRED_MODEL"
S07,Raktikā,Mṛdu,loving,10/9,"affective warmth (semantic)","Ri anchor (model)","Ri","Yaman/Bilawal families (Ri shuddha); Bhairav-family (Ri komal)","SR names+glosses; PureTones table gives Re at 10/9","name+gloss:PRIMARY_TEXT;ratio:SECONDARY_SCHOLARLY;alignment:INFERRED_MODEL"
S08,Raudrī,Dīpta,terrible,2560/2187,"intense/forceful (semantic)","transition toward Ga (model)","Ga","ragas emphasizing Ga inflections","SR names+glosses; PureTones ratios","name+gloss:PRIMARY_TEXT;ratio:SECONDARY_SCHOLARLY;alignment:INFERRED_MODEL"
S09,Krodha,Āyata,wrathful,32/27,"arousal/irritability (semantic)","Ga anchor (model)","Ga","ragas with Ga prominent","SR names+glosses; PureTones gives ga at 32/27","name+gloss:PRIMARY_TEXT;ratio:SECONDARY_SCHOLARLY;alignment:INFERRED_MODEL"
S10,Vajrīkā,Dīpta,thunderbolt,6/5,"decisive/striking (semantic)","Ga→Ma region (model)","Ma","ragas with Ma focus","SR names+glosses; PureTones ratios","name+gloss:PRIMARY_TEXT;ratio:SECONDARY_SCHOLARLY;alignment:INFERRED_MODEL"
S11,Prasāriṇī,Āyata,spreading,5/4,"expansive (semantic)","Ga/Ma region (model)","Ma","Malkauns/Puriya/Todi families (Ma emphasized)","SR names+glosses; PureTones ratios","name+gloss:PRIMARY_TEXT;ratio:SECONDARY_SCHOLARLY;alignment:INFERRED_MODEL"
S12,Prīti,Mṛdu,happiness,320/243,"joy/affiliation (semantic)","Ma region (model)","Ma","ragas with Ma prominence","SR names+glosses; PureTones ratios","name+gloss:PRIMARY_TEXT;ratio:SECONDARY_SCHOLARLY;alignment:INFERRED_MODEL"
S13,Mārjanī,Madhya,cleaning,4/3,"clarifying (semantic)","Ma anchor (model)","Ma","ragas with Ma stability","SR names+glosses; PureTones sets ma=4/3","name+gloss:PRIMARY_TEXT;ratio:SECONDARY_SCHOLARLY;alignment:INFERRED_MODEL"
S14,Kṣiti,Mṛdu,earth,27/20,"grounding (semantic)","Pa approach (model)","Pa","ragas with Pa strong (most)","SR names+glosses; PureTones ratios","name+gloss:PRIMARY_TEXT;ratio:SECONDARY_SCHOLARLY;alignment:INFERRED_MODEL"
S15,Rakta,Madhya,beloved,45/32,"attachment/affinity (semantic)","Pa approach (model)","Pa","ragas relying on Pa–Dha–Ni movement","SR names+glosses; PureTones ratios","name+gloss:PRIMARY_TEXT;ratio:SECONDARY_SCHOLARLY;alignment:INFERRED_MODEL"
S16,Sandīpanī,Āyata,shining,40/27,"brightening/illumination (semantic)","upper tetrachord approach (model)","Pa","evening ragas with Pa emphasis","SR names+glosses; PureTones ratios","name+gloss:PRIMARY_TEXT;ratio:SECONDARY_SCHOLARLY;alignment:INFERRED_MODEL"
S17,Ālāpinī,Kāruṇa,singing,3/2,"expressive vocality (semantic)","Pa anchor (model)","Pa","all ragas; Pa is steady note in theory","SR names+glosses; PureTones sets Pa=3/2","name+gloss:PRIMARY_TEXT;ratio:SECONDARY_SCHOLARLY;alignment:INFERRED_MODEL"
S18,Madantī,Kāruṇa,intoxicating,25/16,"absorptive/trance-like (semantic)","Dha approach (model)","Dha","ragas with Dha emphasis","SR names+glosses; PureTones ratios","name+gloss:PRIMARY_TEXT;ratio:SECONDARY_SCHOLARLY;alignment:INFERRED_MODEL"
S19,Rohiṇī,Āyata,ascending,400/243,"rising/aspiring (semantic)","Dha region (model)","Dha","Shree/Puriya/Bhairav-family (komal Dha contexts)","SR names+glosses; PureTones ratios","name+gloss:PRIMARY_TEXT;ratio:SECONDARY_SCHOLARLY;alignment:INFERRED_MODEL"
S20,Ramyā,Madhya,charming,5/3,"charm/beauty (semantic)","Dha anchor (model)","Dha","ragas with strong Dha (e.g., Bhimpalasi phrases)","SR names+glosses; PureTones sets Dha=5/3","name+gloss:PRIMARY_TEXT;ratio:SECONDARY_SCHOLARLY;alignment:INFERRED_MODEL"
S21,Ugrā,Dīpta,mighty,1280/729,"power/force (semantic)","Ni approach (model)","Ni","night ragas with komal Ni color","SR names+glosses; PureTones ratios","name+gloss:PRIMARY_TEXT;ratio:SECONDARY_SCHOLARLY;alignment:INFERRED_MODEL"
S22,Kṣobhiṇī,Madhya,agitating,16/9,"agitation/activation (semantic)","Ni anchor (model)","Ni","ragas with Ni emphasis (Bageshri/Darbari phrases)","SR names+glosses; PureTones sets ni=16/9","name+gloss:PRIMARY_TEXT;ratio:SECONDARY_SCHOLARLY;alignment:INFERRED_MODEL"
```

_Classical grounding for the 22-name set and glosses_: these names and semantic glosses are taken from the Saṅgītaratnākara translation pages showing the five śruti categories and their named varieties. citeturn41view1
_Grounding for the numeric ratios_: the ratio set is taken from the modern reconstruction table of the 22-śruti Shadaj-grām experiment (Achal/Chal vīṇā) presented by PureTones. citeturn50view0

== Raga × body region dataset and therapeutic protocols


=== What can be reasonably “attested” here

The strongest text-attested “body mapping” in the retrieved corpus is not “each rāga maps to an organ,” but rather:
- Saṅgītaratnākara’s _embodied pathway_ of nāda’s manifestation (navel→heart→throat→head→mouth). citeturn24view2
- Modern intervention studies that measure physiological endpoints (BP/HRV, respiration, ERP indices). citeturn57view0turn57view1turn60view0

Therefore, the _body-region mapping_ below is built as a _knowledge-graph bridge_: it prioritizes (a) measured endpoints where available, and (b) traditional mood/time associations otherwise.

=== Nakshatra correspondence note

Your example rule uses _Śravaṇa = ears_. A Vedic astrology reference identifying Śravaṇa as “the Ear” is used solely to support that _symbolic correspondence_ (not a medical claim). citeturn61search1

=== CSV: `part4_raga_body_region.csv`

```csv
raga_id,name_iast,body_region,nakshatra_correspondence,healing_mechanism_traditional,modern_parallel,practice_combination,source_text,attestation_status
R007,Bhīmpalāsī,"cardiovascular (BP/HRV)","Śravaṇa (ear; listening gateway)","shānta-rasa induction; downshifts arousal via slow listening","RCT reports BP/HRV changes during passive listening","Viparita_Karani + Nadi_Shodhana (10–15 min) while listening softly","Bhimpalas BP/HRV RCT; Shravana=ear reference","modern_parallel:PEER_REVIEWED;nakshatra:SECONDARY_SCHOLARLY;asana_pranayama:ENGINEERED_PROTOCOL"
R008,Toḍī,"cardiovascular + respiratory (BP/pulse/resp rate)","Śravaṇa","slow rāga phrases stabilize prāṇa (traditional framing)","30-day listening associated with lower SBP/DBP/pulse/resp; ERP changes suggest altered attention allocation","Supta_Baddha_Konasana + Bhramari (or Nadi_Shodhana)","Todi BP study; ERP RCT includes Miyān ki Todi; Shravana reference","modern_parallel:PEER_REVIEWED;practice_combo:ENGINEERED_PROTOCOL"
R012,Mālkauṃs,"cognitive engagement / attention networks","Śravaṇa","pratyāhāra-support (traditional meditative framing)","ERP RCT shows raga-specific modulation of N1/P3 indices","Vajrasana (comfortable seat) + Nadi_Shodhana (10 min)","ERP RCT (Malkauns)","modern_parallel:PEER_REVIEWED;practice_combo:ENGINEERED_PROTOCOL"
R013,Pūriyā,"cognitive engagement + affect regulation","Śravaṇa","evening transition rāga; supports settling of mind","ERP RCT shows P3 latency changes; Pitta-RM family usage cited","Seated forward fold (Paschimottanasana, gentle) + slow nasal breathing","ERP RCT; Pitta RM timing family","modern_parallel:PEER_REVIEWED;practice_combo:ENGINEERED_PROTOCOL"
R001,Bhairava,"digestive + affect (anger trait)","Śravaṇa","cooling/soothing listening for pitta-type reactivity","Validated Pitta-RM uses Bhairav in morning within GERD/Amlapitta feasibility","Sheetali/Sheetkari (cooling breath) + gentle restorative supine rest","Pitta-RM protocol; Shravana reference","modern_parallel:PEER_REVIEWED;practice_combo:ENGINEERED_PROTOCOL"
R014,Śrī,"affect regulation (anger/heat)","Śravaṇa","shānta/serious evening rasa supports pitta settling","Validated Pitta-RM lists Shree 4–7pm","Supported_bridge + long exhale breathing (1:2 inhale:exhale)","Pitta-RM table","modern_parallel:PEER_REVIEWED;practice_combo:ENGINEERED_PROTOCOL"
```

=== CSV: `part5_therapeutic_protocols.csv`

This includes your specified Vata protocol verbatim (structured as data), and adds the remaining protocols as engineered sequences that cite any available parameter anchors (especially the Pitta RM listening parameters).

```csv
protocol_id,goal,dosha_target,time_window,raga_recommendation,tempo_bpm,duration_minutes,instrument_primary,volume,adjuncts,asana,pranayama,notes,source_text,attestation_status
P001,Vata_pacification,vata,"evening (5-7pm)","Bhairavi|Bageshri","40-50","20","veena_or_sarod","soft","warm_oil_massage","Supta_Baddha_Konasana","Nadi_Shodhana","User-specified protocol; keep lights low; avoid fast taan patterns","Provided by user (protocol spec)","ENGINEERED_PROTOCOL"
P002,Pitta_pacification,pitta,"dawn+evening windows","Bhairav (dawn)|Shree (4-7pm)|Puriya (7-10pm)","40-55","15","sitar_or_rudraveena","soft-medium (50-70dB)","cooling_routine;avoid_spicy_food","Supported_reclined_rest","Sheetali_or_Nadi_Shodhana","Raga timing and low-volume constraint anchored to validated Pitta RM feasibility protocol","Pitta imbalance RM (timing + 50–70 dB + sitar/rudraveena); additional yoga elements engineered","timing+volume+instrument:PEER_REVIEWED;asana_pranayama:ENGINEERED_PROTOCOL"
P003,Kapha_activation,kapha,"morning (6-8am)","Bilawal|Bhupali","60-75","12","bansuri_or_vocal","medium","warm_tea;light_walk","Surya_Namaskar (gentle)","Kapalabhati (light)","Aim: mobilize; stop if dizziness; keep bright tempo but not harsh volume","Kapha-time inference in therapy writing; music choices engineered","ENGINEERED_PROTOCOL"
P004,Sleep_induction,vata,"late_night (10pm-12am)","Bageshri|Darbari","35-50","20","soft_instrumental_drone","soft","screen_off;warm_blanket","Viparita_Karani (legs_up_wall)","Bhramari (5-7 rounds)","Prefer alap/slow vilambit; no fast percussion","Raga night association (traditional); physiology aim informed by BP/resp studies as analogs","best_time:TRADITIONAL_PRACTICE;sequence:ENGINEERED_PROTOCOL"
P005,Creative_activation,kapha,"late_afternoon (3-5pm)","Yaman|Bhupali","65-80","15","sitar","medium","journaling (5 min after)","Seated_twist (gentle)","Nadi_Shodhana","Use after a brief walk; end with 2 minutes silence","ERP study suggests ragas differ in attention allocation; creative use is engineered","raga_cognition:PEER_REVIEWED_ANALOGY;protocol:ENGINEERED_PROTOCOL"
P006,Grief_processing,vata,"evening (7-9pm)","Kafi|Bhairavi","40-55","20","vocal_or_bansuri","soft","support_person_if_needed","Supported_child_pose","Long_exhale_breathing","Focus on karuna/shanta affect; stop if overwhelming","Raga-as-affect tradition; no direct trial in retrieved set","ENGINEERED_PROTOCOL"
P007,Anxiety_reduction,vata,"evening (6-8pm)","Bhairavi|Bageshri|Darbari","40-55","15","slow_string","soft","warm_shower_before","Supta_Baddha_Konasana","Nadi_Shodhana","Select one raga for 10 days before switching (stability)","Physiology anchor: low-volume listening guidance from RM; otherwise engineered","volume_anchor:PEER_REVIEWED;rest:ENGINEERED_PROTOCOL"
P008,Concentration,kapha_or_vata,"morning (8-10am)","Bilawal|Yaman","60-70","12","tanpura_drone+lead","medium","single_task_focus","Vajrasana","Box_breathing (light)","Avoid multitasking; post-listen 2 minutes quiet","ERP trial shows raga-specific engagement shifts (generalizable principle)","cognition_anchor:PEER_REVIEWED;protocol:ENGINEERED_PROTOCOL"
P009,Spiritual_practice_support,all,"pre_dawn (4-6am)","Bhairav|Lalit","slow_alap","15","vocal+tanpura","soft","incense_optional","Meditation_seat","Nadi_Shodhana","Aligns with dawn practice; keep minimal stimulation","Pitta RM lists Bhairav/Lalit dawn windows; SR frames nāda contemplation as path","timing:PEER_REVIEWED;spiritual_frame:PRIMARY_TEXT;protocol:ENGINEERED_PROTOCOL"
```

== Modern research evidence and NPU coherence rules


=== Evidence snapshots used for Part Six

- _Bhimpalās (Bhimpalasi)_: A randomized controlled trial reports short-term evaluation of a standardized Hindustani rāga (Bhimpalās) on BP and HRV metrics. citeturn57view0
- _Toḍī_: A 30-day program of daily morning listening reported significant reductions in SBP/DBP, pulse rate, and respiratory rate. citeturn57view1
- _Pitta imbalance RM_: A validated 24-rāga module is reported with expert validation (CVR) and feasibility in Amlapitta patients, including explicit time windows and listening constraints (50–70 dB; sitar/rudraveena at 396 Hz). citeturn54view0
- _Cognitive/attention (ERP)_: A triple-blinded RCT using an oddball task tested 10-minute listening to Miyan ki Toḍī, Mālkauṃs, and Pūriyā and observed raga-specific modulation of N1/P3 indices (attention allocation proxy). citeturn60view0

=== CSV: `part6_modern_research.csv`

```csv
evidence_id,topic,raga_or_intervention,design,population,duration,primary_outcomes,findings_summary,evidence_level,source_text,attestation_status
E001,cardiovascular_regulation,"Raga Bhimpalās (passive listening)",randomized_controlled_trial,healthy_young_individuals,"single-session (short-term)","BP;HRV","Trial evaluated short-term effects of raga Bhimpalās on cardiovascular electrophysiology endpoints","PEER_REVIEWED","Indian Journal of Physiology and Pharmacology RCT page","PEER_REVIEWED"
E002,cardiovascular_and_respiratory,"Raga Toḍī (instrumental listening)",pre_post_with_control_rest,elderly_males,"30 days daily morning","SBP;DBP;pulse;resp_rate","Significant reductions in SBP/DBP/pulse/resp rate after 30 days of listening vs rest control","PEER_REVIEWED","Journal of Scientific Research (BHU) PDF","PEER_REVIEWED"
E003,affect_pitta_module,"24-raga module for Pitta imbalance (Amlapitta/GERD)",module_development+expert_validation+pilot_feasibility,GERD/Amlapitta_patients,"6 weeks; 4x/day 15 min (feasibility subset)","dosha_scores;anger_trait;feasibility","Validated raga module; feasibility with decreases in Pitta imbalance and anger trait; listening guidance (50-70 dB; sitar/rudraveena; timing windows)","PEER_REVIEWED","Swarsindhu paper PDF text","PEER_REVIEWED"
E004,cognitive_engagement,"Miyan ki Toḍī vs Mālkauṃs vs Pūriyā vs nature sounds",randomized_controlled_trial_triple_blinded,healthy_young_individuals,"10 min listening; ERPs before/during/after","ERP N1/P3 amplitude/latency","Different ragas showed different patterns of delayed/smaller N1/P3 suggesting altered attention allocation during/after listening","PEER_REVIEWED","Music & Medicine 2025 PDF","PEER_REVIEWED"
```

=== CSV: `part7_npu_coherence_rules.csv`

Because your coherence scores are system parameters (not classical-text quantities), they are tagged `INFERRED_MODEL` / `NPU_SCHEMA`.

```csv
rule_id,if_conditions,then_actions,coherence_score,boost_or_penalty,rationale,source_text,attestation_status
C001,"dosha_current=vata AND time_window=evening","recommend_raga=Bhairavi;recommend_duration=20;recommend_tempo=40-50",0.92,"","Matches engineered vata protocol (slow tempo + evening settling)","User protocol P001","INFERRED_MODEL"
C002,"nakshatra=Śravaṇa","listening_coherence_boost=+0.10",0.10,"boost","+hearing-symbolic alignment: Śravaṇa is ‘the ear’ in nakshatra lore","Shravana as ‘Ear’ reference","SECONDARY_SCHOLARLY;INFERRED_MODEL"
C003,"raga_rasa=karuṇa AND approach=Ārta","therapeutic_coherence=0.95",0.95,"","Karuṇa (compassion/pathos) aligned with grief-oriented approach; modeled parameter","Rasa framework used in modern discussions; not computed in texts","INFERRED_MODEL"
C004,"dosha_current=pitta AND symptom_cluster=anger_trait AND time_window=dawn","recommend_raga=Bhairav;volume=50-70dB;duration=15",0.90,"","Anchored to validated Pitta RM feasibility protocol (Bhairav morning; low volume)","Pitta RM paper timing/volume/instrument guidance","PEER_REVIEWED;INFERRED_MODEL"
C005,"goal=cognitive_downshift AND time_window=night","recommend_raga=Malkauns|Puriya;duration=10;post_silence=2min",0.86,"","ERP RCT suggests raga-specific reduction/delay in N1/P3 components (attention allocation proxy)","Music & Medicine ERP RCT","PEER_REVIEWED;INFERRED_MODEL"
C006,"condition=hypertension_risk AND preference=passive_listening","recommend_raga=Bhimpalasi|Todi;duration=10-20;volume=soft-medium",0.88,"","Uses available cardiovascular endpoint studies to prefer ragas with measured BP/HRV effects","Bhimpalas BP/HRV RCT; Todi BP/resp study","PEER_REVIEWED;INFERRED_MODEL"
```

=== Minimal rationale for the NPU “dosha-time” principle used in some rules

A modern music-therapy writing used in this research explicitly frames dosha timing as a selection heuristic (kapha morning, pitta midday, vata afternoon), though it is not a primary music-śāstra claim. citeturn55search10 The Pitta RM paper operationalizes the “circadian cycle of doshas” in its module development and time-theory alignment. citeturn54view0



== All CSV deliverables summary

The report includes the following CSV blocks for direct ingestion into an NPU knowledge graph:

- `part1_raga_dosha_condition.csv`
- `part2_nada_brahma_sound_cosmology.csv`
- `part3_shruti_science.csv`
- `part4_raga_body_region.csv`
- `part5_therapeutic_protocols.csv`
- `part6_modern_research.csv`
- `part7_npu_coherence_rules.csv`

All “Vedic/classical” claims are anchored where possible to Nāṭyaśāstra and Saṅgītaratnākara passages on śruti/nāda. citeturn33view0turn24view0turn24view2turn41view1 All explicit dosha-linked rāga selection that appears as a studied protocol is anchored to the Pitta RM feasibility paper. citeturn54view0
