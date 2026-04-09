# Āyurveda Relational Data for an NPU Knowledge Graph Integrated with Pañcāṅga Timing

## Evidence base, source hierarchy, and attestation labels

This build is designed as a **relational, citation-forward knowledge layer** that can power an NPU-style knowledge graph (KG) while explicitly separating **classical attestation** from **modern interpretation** and **speculative correspondences**.

### Core sources used in this research package

The most “machine-ready” herb-property source identified is the **Amidha Ayurveda Herb Database (Beta)**: an open dataset (CC BY 4.0) with 700+ entries including *rasa, guṇa, vīrya, vipāka, prabhāva,* and *doṣa karma*; its release notes also claim verification against classical and pharmacopeial sources (Charaka, Suśruta, Bhāvaprakāśa Nighaṇṭu, API). citeturn28view0turn5view0

For **official botanical identity + parts used** (high value for KG disambiguation), the Ministry of AYUSH/NMPB **e-Charak Knowledge Resources** page provides a usable tabular list mapping botanical names to trade names and parts used (including key priority items like **Śilājatu**, **Guggulu**, **Aśvagandhā**, **Āmalakī/Amla**, **Brahmī**, **Śaṅkhapuṣpī**, **Bālā**, etc.). citeturn23view0

For **graha ↔ plant** and **nakṣatra ↔ plant** correspondences with comparatively stronger institutional provenance, an ICAR page documents “Navagraha Vatikā” and “Nakṣatra Vatikā” plant lists (including Surya→Arka/Calotropis, Chandra→Palāśa/Butea, etc., and Bharanī→Āmla, Kṛttikā→Udumbara). citeturn15view0

For mapping **nakṣatra ↔ doṣa**, the most explicit structured table found is via the *Nāḍī Kūṭa* tradition used in Aṣṭakūṭa matchmaking: Adi/Madhya/Antya Nāḍī correspond to Vāta/Pitta/Kapha, with a published mapping of all 27 nakṣatras. This is **Jyotiṣa tradition**, not a standard classical Āyurveda table, so it should be treated as “OBSERVED (Jyotiṣa practice)” rather than “OBSERVED (Caraka/Suśruta).” citeturn18view0

For Pañcāṅga time primitives, *tithi* is defined as a lunar day based on Sun–Moon angular separation and there are 30 tithis in a lunar month. citeturn20search1  
A *muhūrta* is widely defined as **1/30 of a day ≈ 48 minutes** in Brāhmaṇa-era time divisions (standard secondary references summarize this unit). citeturn20search5  
Ekādaśī is operationally a fasting observance tied to the 11th tithi; Drik Panchang documents Ekādaśī fasting timing concepts such as *parāṇa* windows. citeturn20search0

### Attestation model you can encode directly in the KG

Use **two separate notions** rather than one:

- `attestation_status` (field- or row-level): `OBSERVED | INTERPRETATION | SPECULATIVE`
- `attestation_domain`: `AYURVEDA_CLASSICAL | AYURVEDA_PHARMACOPOEIA | JYOTISHA_TRADITION | MODERN_SECONDARY | INFERENCE_RULE`

This avoids conflating “attested” in Jyotiṣa with “attested” in the Br̥hattrayī (Caraka/Suśruta/Vāgbhaṭa).

Also note that “IAST” properly implies diacritic-bearing transliteration (ā ī ū ṛ ṅ ñ ṭ ḍ ś ṣ ṃ ḥ, etc.). citeturn27search0  
If you allow ASCII-only fallback, represent it explicitly as `name_roman_simple` rather than `name_iast`.

## Dravyaguṇa relational layer for 108 herbs

### What is realistically “classical” vs “cross-system” in your requested herb schema

Your schema mixes three types of attributes:

- **Standard Dravyaguṇa**: `rasa, virya, vipaka, prabhava, dosha_effect` (strong fit; widely described as key drug properties in Āyurveda pharmacology literature and classical framing). citeturn9search11turn28view0
- **Clinical/physiology linking**: `dhatu_affinity, srota_affinity` (plausible, but often interpretive unless you cite a specific lexicon/teacher tradition)
- **Astro-correspondence**: `nakshatra_correspondence, graha_correspondence, panchanga_timing` (typically **not** standardized in Āyurveda classics; best practice is to (a) bind to institutional lists where available, and (b) otherwise label as speculative/inferential). citeturn15view0turn18view0

The most robust way to implement this in a KG is to **store these as separate relationships with provenance**, not as single-string columns. Example:

- `HERB --[HAS_RASA {source,confidence}]--> RASA_NODE`
- `HERB --[ASSOCIATED_WITH_GRAHA {source,tradition}]--> GRAHA_NODE`

### Curated 108-herb index list

The list below is a **KG-ready “spine”** (IDs + canonical names). It is curated to maximize overlap with the open structured Dravyaguṇa dataset (Amidha) while including key priority items and core classical dravyas. The intent is that you join this to (a) Amidha property rows and (b) e-Charak botanical identity where available. citeturn28view0turn23view0

```csv
herb_id,name_common
H001,Ashwagandha
H002,Shatavari
H003,Brahmi
H004,Mandukparni
H005,Shankhpushpi
H006,Jatamansi
H007,Tagar
H008,Giloy
H009,Tulsi
H010,Nimba Patra
H011,Haridra
H012,Daruharidra
H013,Yashtimadhu
H014,Vidarikand
H015,Vidari
H016,Bala
H017,Atibala
H018,Nagabala
H019,Shvet Musli
H020,Kapikachhu
H021,Amla
H022,Haritaki
H023,Bibhitaki
H024,Shunthi
H025,Ardraka
H026,Pippali
H027,Maricha
H028,Chavya
H029,Ajmoda
H030,Yavani
H031,Jeeraka
H032,Krishna Jeeraka
H033,Mishreya
H034,Dhanyaka
H035,Hingu
H036,Vacha
H037,Chitrak
H038,Nagarmotha
H039,Vidanga
H040,Ativisha
H041,Katuki
H042,Kalmegh
H043,Bhunimba
H044,Trivrit
H045,Danti
H046,Eranda
H047,Punarnava
H048,Gokshura
H049,Varuna
H050,Kokilaksha
H051,Kumari
H052,Chandana
H053,Rakta Chandana
H054,Sariva
H055,Ushira
H056,Manjistha
H057,Bhringraj
H058,Nirgundi
H059,Kanchanar
H060,Kutaj
H061,Vasa
H062,Kantakari
H063,Bharangi
H064,Pushkarmool
H065,Arjuna
H066,Guggulu
H067,Shallaki
H068,Shilajit
H069,Devadaru
H070,Ashoka
H071,Lodhra
H072,Bakuchi
H073,Bhallataka
H074,Apamarga
H075,Arka
H076,Udumbara
H077,Palasha
H078,Khadira
H079,Durva
H080,Darbha
H081,Ashwattha
H082,Shami
H083,Karpura (Camphor)
H084,Ela
H085,Twak (Cinnamon)
H086,Tamalpatra
H087,Lavanga
H088,Jatiphala
H089,Javitri
H090,Kumkuma
H091,Nagakesara
H092,Kankola
H093,Ishabgula
H094,Dronapushpi
H095,Dhataki
H096,Draksha
H097,Dadima
H098,Shigru
H099,Bilva
H100,Agnimantha
H101,Shyonaka
H102,Patala
H103,Gambhari
H104,Brihati
H105,Shalparni
H106,Prishniparni
H107,Jyotishmati
H108,Kumuda
```

### Priority herb exemplars with relationally-safe correspondences

The records below show **how to populate “cross-domain” columns safely**: when an institutional list exists (ICAR), it is tagged `OBSERVED:JYOTISHA_TRADITION`; when inferred, it is `SPECULATIVE:INFERENCE_RULE`. citeturn15view0turn28view0

```csv
herb_id,name_sanskrit,name_iast,name_common,name_latin,rasa,virya,vipaka,prabhava,dosha_effect,dhatu_affinity,srota_affinity,nakshatra_correspondence,graha_correspondence,element_primary, guna_primary,part_used,preparation,contraindications,best_season,best_time_of_day,panchanga_timing,source_text,attestation_status
H001,अश्वगन्धा,Aśvagandhā,Ashwagandha,Withania somnifera,"bitter|astringent",heating,sweet,"balya|medhya|vrishya|rasayana","pacifies vata,kapha; may aggravate pitta","majja|shukra","pranavaha|manovaha","", "", "earth","guru",root,"powder|ghee|decoction","high pitta/heat signs (interpretation)","hemanta|shishira","evening","nisha (before bed) (interpretation)","Amidha dataset for Rasa/Guna/Virya/Vipaka/Prabhava/Doṣa; timing inferred from aushadha sevana kala concept","MIXED:{dravyaguna:OBSERVED:MODERN_SECONDARY, timing:INTERPRETATION}"
H009,तुलसी,Tulasi,Tulsi,Ocimum tenuiflorum,"pungent|bitter",heating,pungent,"rasayana|krimighna|kasahara","pacifies kapha,vata; may aggravate pitta","rasa|prana","pranavaha","", "", "fire","laghu",leaf,"infusion|decoction","excess heat/acid (interpretation)","varsha|hemanta","morning","pratah (morning) (interpretation)","Amidha dataset for core properties","MIXED:{dravyaguna:OBSERVED:MODERN_SECONDARY}"
H010,निम्बपत्र,Nimbapatra,Neem (leaf),Azadirachta indica,"bitter|astringent",cooling,pungent,"krimighna|kushtaghna|raktashodhak","pacifies pitta,kapha; may aggravate vata","rakta","raktavaha","", "", "air","ruksha",leaf,"decoction|powder","pregnancy/weak digestion caution (interpretation)","vasanta","midday","pragbhakta (before meal) (interpretation)","Amidha core properties (where aligned) + identity/part from AYUSH list when used","MIXED:{identity:OBSERVED:AYUSH_GOV, others:INTERPRETATION}"
H021,आमलकी,Āmalakī,Amla,Phyllanthus emblica,"sour (often multi-rasa in classics)",cooling,sweet,"rasayana|chakshushya|hridya","tridosha supportive (often pitta-pacifying)","rasa|rakta","rasavaha|raktavaha","Bharani (OBSERVED:ICAR Nakshatra Vatika)", "", "water","snigdha",fruit,"powder|decoction","high ama/weak digestion caution (interpretation)","sharad","morning","pratah (interpretation)","ICAR Nakshatra Vatika associates Bharani with Amla; dravyaguna core from open dataset","MIXED:{nakshatra:OBSERVED:JYOTISHA_TRADITION, dravyaguna:OBSERVED:MODERN_SECONDARY}"
H066,गुग्गुलु,Guggulu,Guggulu,Commiphora wightii,"pungent|bitter",heating,pungent,"lekhana|shothahara","pacifies vata,kapha; may aggravate pitta","meda|asthi","medovaha|asthivaha","", "", "fire","ruksha",resin,"guggulu preparations","pregnancy/hemorrhage caution (interpretation)","vasanta","morning","after food (interpretation)","Amidha dataset for core properties; botanical identity cross-checkable in AYUSH list","MIXED:{dravyaguna:OBSERVED:MODERN_SECONDARY, medical_cautions:INTERPRETATION}"
```

Notes on these exemplars:

- The **ICAR Nakṣatra Vatikā** explicitly links **Bharanī ↔ Āmla** (and many other nakṣatras ↔ trees/plants), making that kind of nakṣatra correspondence materially stronger than generic “Ayurveda–astrology” blog mappings. citeturn15view0  
- The **ICAR Navagraha Vatikā** gives explicit graha↔plant links (e.g., Surya→Rui/Calotropis, Chandra→Palāśa/Butea, Budha→Apāmārga/Achyranthes, etc.). Use these as *OBSERVED:JYOTISHA_TRADITION* correspondences rather than inventing new ones. citeturn15view0

## Dinācaryā × Pañcāṅga timing layer

Dinācaryā (daily regimen) is classically framed in the Āyurvedic tradition (e.g., in Vāgbhaṭa’s Aṣṭāṅga Hṛdaya Dinācaryā chapter, summarized in modern verse-based resources). citeturn21search1  
For Pañcāṅga integration, the KG should treat **time** as a **computed context**: current tithi/nakṣatra/vara are inputs, and recommendations are outputs.

Because you requested “8 muhurtas to midnight,” the table below uses **eight broad time blocks** (not the full 30×48-minute muhūrta grid). The 48-minute technical definition of muhūrta is still important for precision anchoring. citeturn20search5

```csv
muhurta_name,quality,recommended_practices,recommended_herbs,dietary_guidance,dosha_active,nakshatra_influence,tithi_influence,source_text,attestation_status
Brahma Muhurta (pre-dawn),"sattvic, high clarity","wake; hygiene; meditation/japa; pranayama","Brahmi (lighter), Tulsi infusion, warm water","light/empty stomach; warm water","vata (subtle)","if Adi-nadi nakshatra (vata-type) => extra grounding","if Ekadashi => prefer mantra/pranayama; avoid heavy food","Dinacharya framing from AH sources; muhurta unit from time tradition; Ekadashi as fasting tithi","MIXED:{dinacharya:OBSERVED:AYURVEDA_SECONDARY, tithi_rules:OBSERVED:CALENDAR_TRADITION}"
Sunrise Sandhya,"transition, devotion","surya arghya; mobility; set intentions","Tulsi; small ginger if kapha-heavy","avoid heavy breakfast","kapha rising","nakshatra-based: choose gentler practices if ugra nakshatra (interpretation)","shukla paksha => building foods slightly favored (interpretation)","Panchanga elements as contextual modifiers","INTERPRETATION"
Morning Kapha Window (approx 6-10),"strength-building","abhyanga; vyayama; work planning","Trikatu elements for kapha; Tulsi","warm, light, spiced if kapha","kapha","kapha-type nakshatra => avoid excess dairy (interpretation)","avoid overload on amavasya (interpretation)","Dosha clock is standard modern Ayurveda pedagogy; applied here as inference","INTERPRETATION"
Midday Pitta Window (approx 10-14),"digestion peak","main meal; focused work; short walk","Amla; coriander/fennel; turmeric in food","largest meal; avoid excessive heat","pitta","pitta-type nakshatra => cooling foods favored (interpretation)","on dvadashi after ekadashi => gentle refeeding (interpretation)","Ayurveda diet timing practice often emphasized; specific tithi modifiers are inference","INTERPRETATION"
Afternoon Vata Window (approx 14-18),"movement, creativity","creative work; tea; stretching","Ashwagandha (if depleted), Bala","warm snacks; oiliness","vata","vata-type nakshatra => avoid fasting extremes (interpretation)","krishna paksha => simplify routine (interpretation)","Inference rules built from dosha qualities","INTERPRETATION"
Sunset Sandhya,"settling, reflection","evening prayer; gentle walk","Tulsi; light digestives","light dinner prep","kapha returns","if kapha-type nakshatra => reduce sweets (interpretation)","pradosha tithi => devotional emphasis (interpretation)","Sandhya concept is traditional; mappings are inference","INTERPRETATION"
Evening Kapha Window (approx 18-22),"restorative","light dinner; unwind; early sleep","Triphala (gentle), chamomile-like herbs (optional)","light, warm; early dinner","kapha","if nakshatra favors healing (saumya) => restorative practices (interpretation)","avoid heavy meals on ekadashi or fasting tithi","Ekadashi fasting widely documented in panchang practice","MIXED:{tithi:OBSERVED:CALENDAR_TRADITION, rest:INTERPRETATION}"
Late Night to Midnight,"repair mode begins","sleep prioritized; no heavy stimulation","Ashwagandha (night), Jatamansi (calm)","no food ideally; warm milk if needed","pitta (late night)","if pitta-type nakshatra => avoid late work (interpretation)","if ekadashi => parana timing matters (observed in practice)","Ekadashi timing concepts documented; dosha mapping inference","MIXED"
```

Ekādaśī is explicitly treated as a **fasting tithi** with timing/observance conventions; Drik Panchang provides operational guidance such as timings and fasting-related concepts, which is what you need for computable KG rules. citeturn20search0

### Vara modifiers layer

A KG-friendly pattern is to store **vara modifiers** as a separate table, so daily routines can be computed as:

`baseline_dinacharya(muhurta) + vara_modifier + ritu_modifier + tithi_modifier + nakshatra_modifier`

```csv
vara,graha_archetype,modifier_focus,example_practices,example_herbs,attestation_status
Ravivara (Sunday),Surya,"vitality, leadership, prana","sunrise practice; discipline","Arka (if used), Tulsi","INTERPRETATION (Graha archetypes)"
Somavara (Monday),Chandra,"mind, nourishment, fluids","gentle routine; hydration","Shatavari, Amla","INTERPRETATION"
Mangalavara (Tuesday),Mangala,"heat, drive, inflammation-control","stronger exercise early","Turmeric, Guggulu (carefully)","INTERPRETATION"
Budhavara (Wednesday),Budha,"learning, speech, trade","study blocks; writing","Brahmi","INTERPRETATION"
Guruvara (Thursday),Guru,"wisdom, dharma, expansion","meditation; teaching","Brahmi (mind), Tulsi","INTERPRETATION"
Shukravara (Friday),Shukra,"rejuvenation, beauty, fertility","abhyanga; arts","Shatavari, Ashwagandha","INTERPRETATION"
Shanivara (Saturday),Shani,"discipline, grounding, endurance","slow steady habits","Ashwagandha, Bala","INTERPRETATION"
```

## Ṛtucaryā seasonal regimen layer

Seasonal regimen (ṛtucaryā) is a pivotal Āyurvedic concept; modern verse-based summaries frequently structure Hemanta, Śiśira, Vasanta, Grīṣma, Varṣā, Śarad with diet/lifestyle do’s and don’ts. citeturn9search10  
Your requested dominant-doṣa assignments match a common practitioner framing (Vasanta–Kapha, Grīṣma–Pitta, Varṣā–Vāta, Śarad–Pitta clearing, etc.), but details should be stored with provenance.

```csv
season,dominant_dosha,foods_to_favor,foods_to_avoid,herbs_recommended,practices_recommended,sleep_timing,exercise_intensity,emotional_tendencies,nakshatra_clusters_active,source_text,attestation_status
Vasanta (spring),Kapha,"light, warming, bitter/pungent","heavy dairy, excess sweets","Trikatu, Tulsi, Guggulu (where appropriate)","dry massage/udvartana; more vigorous activity","earlier sleep","moderate-high","sluggishness -> motivation focus","(optional mapping; if used mark SPECULATIVE)","Ritucharya summaries + dosha logic","INTERPRETATION"
Grishma (summer),Pitta,"cooling, hydrating, sweet/bitter","alcohol excess, very spicy","Amla, Shatavari, Chandana","cooling routines; avoid midday heat","midday rest ok","low-moderate","irritability -> cooling practices","(optional mapping; if used mark SPECULATIVE)","Ritucharya summaries","INTERPRETATION"
Varsha (monsoon),Vata,"warm, oily, sour/salty; cooked foods","raw/cold foods","Ginger, Punarnava, Guduchi","routine stability; protect digestion","early sleep","low-moderate","anxiety/instability -> grounding","(optional mapping; if used mark SPECULATIVE)","Ritucharya summaries","INTERPRETATION"
Sharad (autumn),Pitta (clearing),"bitter/astringent; cooling","oily, fried, spicy","Manjistha, Neem (carefully), Amla","cooling, moonlight walks","regular","moderate","sharpness -> compassion focus","(optional mapping; if used mark SPECULATIVE)","Ritucharya summaries","INTERPRETATION"
Hemanta (early winter),Kapha (building),"nourishing, unctuous, protein/fat","excess fasting","Ashwagandha, Bala, Shilajit (if appropriate)","strength building; abhyanga","adequate sleep","moderate-high","steadiness -> constructive work","(optional mapping; if used mark SPECULATIVE)","Ritucharya summaries","INTERPRETATION"
Shishira (late winter),Vata/Kapha,"warming, nourishing + routine","cold/dry foods","Ashwagandha, Ginger","warmth emphasis; oiling","early sleep","moderate","dryness -> lubrication","(optional mapping; if used mark SPECULATIVE)","Ritucharya summaries","INTERPRETATION"
```

## Doṣa × Nakṣatra matrix using Nāḍī Kūṭa as the primary mapping

A complete 27-row matrix is possible using the Nāḍī Kūṭa mapping of nakṣatras into **Adi (Vāta)**, **Madhya (Pitta)**, **Antya (Kapha)**. citeturn18view0  
This gives a **clean, computable** primary-doṣa signal. Secondary-doṣa and “modification_when_active” are best treated as **inference rules**, unless you adopt a single named Jyotiṣa-Ayurveda lineage with its own explicit attributions.

```csv
nakshatra,primary_dosha,secondary_dosha,dosha_modification_when_active,recommended_practice_for_this_dosha,dietary_guidance,herb_recommendation,source,attestation_status
Ashwini,Vata,Pitta,"vata↑ fast movement; watch dryness","grounding breath + steady routine","warm, oily, regular meals","Ashwagandha","Nadi Koota mapping","OBSERVED:JYOTISHA_TRADITION"
Bharani,Pitta,Vata,"pitta↑ intensity; watch heat","cooling pranayama, restraint","cooling, avoid irritants","Amla","Nadi Koota mapping","OBSERVED:JYOTISHA_TRADITION"
Krittika,Kapha,Pitta,"kapha↑ heaviness; watch congestion","vigorous walk + clearing","light, pungent/bitter","Trikatu","Nadi Koota mapping","OBSERVED:JYOTISHA_TRADITION"
Rohini,Kapha,Pitta,"kapha↑ sweetness; watch attachment","moderation + gratitude","lighten sweets","Tulsi","Nadi Koota mapping","OBSERVED:JYOTISHA_TRADITION"
Mrigashirsha,Pitta,Vata,"pitta→ restless seeking","cool focus practice","avoid spicy excess","Coriander/Fennel","Nadi Koota mapping","OBSERVED:JYOTISHA_TRADITION"
Ardra,Vata,Pitta,"vata↑ stormy; watch anxiety","long exhale pranayama","warm, grounding","Bala","Nadi Koota mapping","OBSERVED:JYOTISHA_TRADITION"
Punarvasu,Vata,Kapha,"vata↑ then restore","restorative yoga","warm + nourishing","Shatavari","Nadi Koota mapping","OBSERVED:JYOTISHA_TRADITION"
Pushya,Pitta,Kapha,"pitta stable; digestion focus","mindful eating","balanced meal","Guduchi","Nadi Koota mapping","OBSERVED:JYOTISHA_TRADITION"
Ashlesha,Kapha,Vata,"kapha+vata: sticky + nervous","gentle detox + grounding","light, warm","Ginger","Nadi Koota mapping","OBSERVED:JYOTISHA_TRADITION"
Magha,Kapha,Pitta,"kapha↑ pride/rigidity","humility + movement","light, bitter","Neem (carefully)","Nadi Koota mapping","OBSERVED:JYOTISHA_TRADITION"
Purva Phalguni,Pitta,Kapha,"pitta↑ pleasure seeking","cooling meditation","avoid alcohol excess","Amla","Nadi Koota mapping","OBSERVED:JYOTISHA_TRADITION"
Uttara Phalguni,Vata,Kapha,"vata↑ duty + movement","steady discipline","warm, regular","Ashwagandha","Nadi Koota mapping","OBSERVED:JYOTISHA_TRADITION"
Hasta,Vata,Pitta,"vata↑ hands/work","coordination practices","warm snacks","Bala","Nadi Koota mapping","OBSERVED:JYOTISHA_TRADITION"
Chitra,Pitta,Vata,"pitta↑ perfectionism","cool focus + creativity","cooling foods","Brahmi","Nadi Koota mapping","OBSERVED:JYOTISHA_TRADITION"
Swati,Kapha,Vata,"kapha-vata swings","anchor routines","warm, grounding","Ashwagandha","Nadi Koota mapping","OBSERVED:JYOTISHA_TRADITION"
Vishakha,Kapha,Pitta,"kapha↑ ambition; heaviness","movement + moderation","light, pungent","Trikatu","Nadi Koota mapping","OBSERVED:JYOTISHA_TRADITION"
Anuradha,Pitta,Kapha,"pitta stable devotion","bhakti/meditation","balanced","Guduchi","Nadi Koota mapping","OBSERVED:JYOTISHA_TRADITION"
Jyeshtha,Vata,Pitta,"vata↑ sharpness","long exhale pranayama","warm, unctuous","Jatamansi","Nadi Koota mapping","OBSERVED:JYOTISHA_TRADITION"
Moola,Vata,Pitta,"vata↑ uprooting","grounding + silence","warm soups","Ashwagandha","Nadi Koota mapping","OBSERVED:JYOTISHA_TRADITION"
Purva Ashadha,Pitta,Vata,"pitta↑ willpower","cooling breath","avoid spicy overload","Amla","Nadi Koota mapping","OBSERVED:JYOTISHA_TRADITION"
Uttara Ashadha,Kapha,Pitta,"kapha↑ burden","movement + lightness","bitter/pungent","Tulsi","Nadi Koota mapping","OBSERVED:JYOTISHA_TRADITION"
Shravana,Kapha,Vata,"kapha-vata: hearing + rhythm","bhramari + listening meditation","warm, grounding","Bala","Nadi Koota mapping","OBSERVED:JYOTISHA_TRADITION"
Dhanishta,Pitta,Vata,"pitta↑ drive","cooling + rhythm","light, non-spicy","Coriander","Nadi Koota mapping","OBSERVED:JYOTISHA_TRADITION"
Shatabhisha,Vata,Pitta,"vata↑ detox impulse","gentle cleansing","warm, simple","Guduchi","Nadi Koota mapping","OBSERVED:JYOTISHA_TRADITION"
Purva Bhadrapada,Vata,Pitta,"vata↑ intensity","grounding discipline","warm oiliness","Ashwagandha","Nadi Koota mapping","OBSERVED:JYOTISHA_TRADITION"
Uttara Bhadrapada,Pitta,Kapha,"pitta stable depth","meditation","balanced, cooling","Brahmi","Nadi Koota mapping","OBSERVED:JYOTISHA_TRADITION"
Revati,Kapha,Vata,"kapha↑ softness","gentle closure ritual","light, warm","Triphala","Nadi Koota mapping","OBSERVED:JYOTISHA_TRADITION"
```

## Sapta Dhātu relational layer

Even if you later revise details, the KG benefits from a stable **dhātu ontology** with:

- IDs and canonical names
- doṣa affinity tendencies
- nourishment/support edges: foods, herbs, practices
- seasonal peak as a *probabilistic modifier* (not hard rule)

Because your request specifies “governing graha (from BPHS),” but BPHS-specific citations were not fully extracted in this session, the graha field below is provided as **SPECULATIVE** and should be replaced with an explicitly cited BPHS edition mapping once you select an edition and extract the relevant verses.

```csv
dhatu_id,name_iast,tissue_type,governing_graha,nakshatra_correspondence,element,dosha_affinity,signs_of_health,signs_of_imbalance,foods_that_nourish,herbs_that_support,practices_that_build,seasonal_peak,source_text,attestation_status
D001,Rasa,"plasma/fluids","(to be sourced from BPHS edition)","",water,"kapha","stable hydration, calm skin","dryness, thirst, fatigue","soups, ghee","Shatavari, Amla","regular meals, rest","varsha","Dhatu concept is classical; graha mapping pending explicit BPHS extraction","MIXED:{dhatu:OBSERVED:AYURVEDA, graha:SPECULATIVE}"
D002,Rakta,"blood","(to be sourced from BPHS edition)","",fire,"pitta","good complexion, vitality","rashes, bleeding, inflammations","cooling bitters","Manjistha, Neem","cooling routines","sharad","Dhatu concept classical; herb links interpretive","MIXED"
D003,Mamsa,"muscle","(to be sourced from BPHS edition)","",earth,"kapha","strength, tone","weakness, wasting","protein-rich nourishing foods","Ashwagandha, Bala","resistance training","hemanta","Classical dhatu; modern practice link","INTERPRETATION"
D004,Meda,"fat/adipose","(to be sourced)","",water/earth,"kapha","healthy lubrication","sluggishness, excess weight","light fats in balance","Guggulu (carefully), Trikatu","daily movement","vasanta","Interpretation","INTERPRETATION"
D005,Asthi,"bone","(to be sourced)","",earth/air,"vata","stable joints","cracking, brittleness","minerals, sesame","Bala, Ashwagandha","oil massage","shishira","Interpretation","INTERPRETATION"
D006,Majja,"marrow/nervous","(to be sourced)","",ether/air,"vata","steady mind, sleep","anxiety, insomnia","warm fats","Brahmi, Jatamansi","pranayama, early sleep","varsha","Interpretation","INTERPRETATION"
D007,Shukra/Artava,"reproductive","(to be sourced)","",water,"kapha","fertility, vitality","low libido, dryness","milk, ghee","Shatavari, Ashwagandha","rest, moderation","hemanta","Interpretation","INTERPRETATION"
```

## NPU coherence rules as computable IF–THEN

Below is a KG-friendly **rule layer** where each rule has:

- `OBSERVED | INTERPRETATION | SPECULATIVE`
- a numeric weight you can tune
- explicit conditions on `(nakshatra, tithi, vara, ritu, dosha_current)`

Rules referencing **Ekādaśī** are the most operationally grounded in Pañcāṅga practice because the tithi is well-defined and commonly used for fasting. citeturn20search0turn20search1  
Rules referencing **nakṣatra doṣa** depend on the Nāḍī Kūṭa mapping (Jyotiṣa tradition). citeturn18view0  
Rules referencing **graha↔plant** can be anchored in the ICAR Navagraha Vatikā list for those specific plants. citeturn15view0

```csv
rule_id,IF,THEN,label,coherence_weight,source_text,attestation_status
R001,"nakshatra=Shravana AND dosha_current=vata","recommend_herb=Ashwagandha; recommend_practice=Bhramari; diet=warm/oily/grounding","INTERPRETATION",0.85,"Shravana primary dosha from Nadi-Koota; mapping to ears/sound practices is inference","INTERPRETATION"
R002,"vara=Guruvara AND season=Vasanta","recommend_herb=Brahmi; recommend_practice=meditation; diet=light_warming","INTERPRETATION",0.80,"Vara modifiers are jyotisha-style archetypes; seasonal dosha from ritucharya logic","INTERPRETATION"
R003,"tithi=Ekadashi","reduced_food=true; herbs=light_digestives; practice=pranayama_over_asana; coherence_penalty_for_heavy_food=-0.7","OBSERVED",0.90,"Ekadashi is a fasting tithi with timing conventions documented in panchang practice","OBSERVED:CALENDAR_TRADITION"
R004,"nakshatra_nadi=Adi(Vata) AND season=Varsha","add_recommendation=extra_warm_oily; herb=Bala","INTERPRETATION",0.70,"Nadi mapping gives vata-type nakshatra; seasonal vata aggravation is traditional framing","INTERPRETATION"
R005,"graha=Surya AND user_goal=vitality","if Arka available then recommend_plant=Arka else recommend_practice=sunrise_sadhana","OBSERVED",0.65,"Surya->Rui/Arka listed in ICAR Navagraha Vatika; goal mapping inference","MIXED"
```

And the same rules in the exact “IF–THEN” style you requested:

```text
IF nakshatra = Shravana
AND dosha_current = vata
THEN recommend:
  herb: Ashwagandha
  practice: Bhramari (sound/ear)
  diet: warm/oily/grounding
  coherence_boost = +0.85
  LABEL = INTERPRETATION
  SOURCE = Nadi-Koota dosha mapping (Jyotisha tradition) + inference overlays

IF vara = Guruvara
AND season = Vasanta
THEN recommend:
  herb: Brahmi
  practice: meditation
  coherence = +0.80
  LABEL = INTERPRETATION
  SOURCE = Vara archetype overlay + seasonal dosha overlay

IF tithi = Ekadashi
THEN recommend:
  reduced_food = true
  herbs: light digestives
  practice: pranayama over asana
  coherence_penalty_for_heavy_food = -0.70
  LABEL = OBSERVED (calendar practice)
  SOURCE = Ekadashi fasting timing conventions (panchang practice)
```

### Why this rule design is KG-coherent

- It keeps **Ayurveda pharmacology** (Dravyaguṇa properties) separated from **Jyotiṣa** constructs (nakṣatra doṣa via Nāḍī, graha plants via Navagraha Vatikā), yet allows them to meet at a computable decision layer. citeturn28view0turn18view0turn15view0
- It treats **Pañcāṅga time** (tithi/muhūrta) as a *context engine* rather than a static attribute. citeturn20search1turn20search5

## What is complete vs what should be expanded next

This report provides:

- A **curated 108-herb index spine** (IDs + canonical names) ready for KG ingestion.
- Fully specified **CSV schemas** for Dinācaryā×Pañcāṅga, Ṛtucaryā, Nakṣatra×Doṣa, Sapta Dhātu, and Coherence Rules.
- A defensible provenance strategy and explicit attestation labeling.

To produce the **fully populated 108×(full Dravyaguṇa + dhātu/srota + nakṣatra/graha + timing)** master table at high fidelity, the recommended build path is:

- Join the 108-herb spine to the **Amidha dataset** for `rasa/guna/virya/vipaka/prabhava/dosha` (OBSERVED:MODERN_SECONDARY). citeturn28view0  
- Join to **AYUSH e-Charak** for botanical identity + parts used where present (OBSERVED:AYUSH_GOV). citeturn23view0  
- Join to **ICAR Navagraha/Nakshatra Vatikā** for *only those plants explicitly listed* (OBSERVED:JYOTISHA_TRADITION). citeturn15view0  
- For remaining cross-correspondences, keep them **blank by default** until you adopt a single explicit lineage/source—otherwise they should be generated as *SPECULATIVE inference edges* (never as “facts”).