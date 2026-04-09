# Astrobotanical Classification System for a Cross‑Traditional NPU Knowledge Graph

## Scope, epistemic posture, and NPU modeling strategy

This research consolidates **biodynamic agriculture (Steiner/Thun), Vedic lunar astrology (nakshatras), Ayurveda, Chinese medicine, and Western herbalism** into a **single, machine‑resolvable classification layer** intended for an NPU knowledge graph. It explicitly separates two knowledge types that often get conflated:

**Empirical agronomy / ecology layer (testable):** farm systems, composting, soil biology, yields, microbial community changes, measurable crop and soil parameters. Key peer‑review anchors include the long‑running **DOK trial** (biodynamic/bioorganic/conventional) and multiple controlled studies of biodynamic preparations. citeturn38view1turn10view1turn36view0turn25view0turn37view0

**Cosmological / symbolic layer (tradition‑bound):** constellational timing, planetary rulership, doshic balancing heuristics, and correspondences (element ↔ plant organ ↔ therapeutic “tone”). Biodynamic calendars explicitly frame this as astronomy relative to fixed stars (sidereal rhythm) and interpretive “influences,” not modern mechanistic causality. citeturn39view0turn40view0turn35view0

Within an NPU graph, these should be **modeled as different evidence regimes** (not as competing “truth claims”). A practical pattern is:

**(a) Nodes that represent traditions’ assertions** (e.g., “BD500 increases soil vitality”) with provenance and evidence tags, and **(b) nodes that represent measured outcomes** (e.g., “microbial biomass increased in BIODYN vs CONMIN in DOK”) with peer‑review links. citeturn38view1turn25view0turn36view0turn37view0

### Evidence labels for NPU fields

Use a strict, queryable tag on every claim-like attribute:

**PEER_REVIEWED:** supported by controlled studies/reviews (e.g., DOK outcomes; microbial sequencing studies of preparations; controlled viticulture comparisons). citeturn38view1turn30view0turn25view0turn38view2turn37view0

**TRADITIONAL:** sourced from canonical tradition texts/practice manuals/calendars (e.g., Steiner lecture instructions; biodynamic calendar rules; nakshatra rulership taxonomies). citeturn21view0turn45view0turn24view1turn40view0turn41view0

**ANECDOTAL / PRACTITIONER:** practice claims not robustly tested or highly variable by context (e.g., many planting‑by‑moon interpretations beyond controlled evidence). The biodynamic calendar itself asserts “direct and consistent correlation,” but this is not equivalent to a modern agronomic causal demonstration. citeturn39view0turn9view0

### Convergence score (cross‑tradition agreement)

For the herb matrix, a **convergence score** can be computed as:

**Convergence = (# traditions mapping the herb into the same primary “action bucket”) / (traditions with data)**

Action buckets are the “lingua franca” across systems (examples):  
**Digestive/Agni‑stimulant**, **Cooling demulcent/yin‑nourishing**, **Aromatic wind‑moving/nervine**, **Deep tonic/adaptogen/building**, **Spirit‑calming/medhya/nootropic**.

The five astrobotanical classes below are designed so each class corresponds to one dominant bucket family while remaining interoperable with biodynamic day types (plant part emphasis). citeturn40view0turn39view0turn35view0

## Biodynamic agriculture synthesis with contested vs robust findings

### Root, leaf, flower, fruit days and what they operationalize

In modern biodynamic calendars derived from Thun’s work, **each zodiac constellation is linked to an element, and each element to a plant part** (earth→root, water→leaf, air/light→flower, fire/warmth→fruit). citeturn40view0

The Biodynamic Agricultural Association explicitly presents this as an **astronomical (sidereal) calendar** based on the Moon and planets relative to the **fixed stars**, distinguishing it from the **tropical “astrological zodiac”** by “nearly a month.” citeturn39view0turn40view0

It also encodes additional timing factors beyond the four day types—e.g., **oppositions/trines as broadly positive**, **squares as negative**, and avoidance of **perigee** and **nodes** for sowing/cultivation. citeturn40view0

### Steiner’s nine biodynamic preparations (BD 500–508)

Steiner’s Agriculture Course (GA 327) provides operational instructions for several preparations as part of a manure/soil enlivening system.

**BD 500 (horn manure):** cow manure stuffed into a cow horn, buried over winter; afterward diluted (often with slightly warmed water), “dynamized” by vigorous stirring that alternates vortex direction, then sprayed on ploughed soil. citeturn19view0turn21view0

**BD 501 (horn silica):** finely ground quartz (or similar) made into a paste, put into cow horns, buried over summer, then removed in late autumn and stored until spring; very small amounts are stirred an hour and sprayed as a fine mist on plants, positioned as complementary to BD500 (“from above” vs “from below”). citeturn21view0

**BD 502 (yarrow):** yarrow flowering tops sewn into a stag bladder, hung in sun through summer, buried through winter, then a small amount added to manure/compost with strong “radiating” influence claimed. citeturn45view0

**BD 503 (chamomile):** chamomile flower heads stuffed into cattle intestines and overwintered in humus soil; then added to manure with claims of improving manure’s nitrogen retention and supporting plant health. citeturn15view2turn45view0

**BD 504 (stinging nettle):** nettle is wilted and buried in earth (with protective peat layer) for a full year; then mixed into manure, described as making manure “sensitive” and preventing improper nitrogen loss. citeturn16view0

**BD 505 (oak bark):** chopped oak bark placed into a skull, overwintered in wet/peaty conditions; added to manure as prophylaxis to help “arrest” harmful plant diseases. citeturn15view3

**BD 506 (dandelion):** dandelion heads sewn into cow tripe (peritoneum/mesentery), buried through winter, retrieved in spring; framed as concentrating “cosmic” forces relevant to silica processes. citeturn15view1

**BD 507 (valerian):** valerian flower juice diluted highly and added to manure to stimulate correct relationship to “phosphoric substance.” citeturn16view1

**BD 508 (horsetail / equisetum):** a concentrated **Equisetum arvense** tea/decoction diluted and sprinkled as liquid manure to combat rust/blight/mildew-like conditions; described as counteracting excessive Moon influence interpreted as linked to fungal phenomena. citeturn24view1turn38view0

A peer‑review synthesis aimed at extension educators emphasizes that biodynamic certification is distinguished from organic by required use of these preparations, and that Steiner framed them as conduits of cosmic/terrestrial forces (homeopathic‑like dilution logic). citeturn38view0turn35view0

### Maria Thun’s claims and what modern tests suggest

The biodynamic association’s guidelines attribute the contemporary sowing/planting calendar to **Maria Thun**, stating she performed “countless sowing, cultivation and harvesting” trials and “discovered a direct and consistent correlation” between plant growth and lunar/planetary rhythms. citeturn39view0

However, modern evaluation is mixed:

A controlled tasting study found **no systematic influence** of “fruit day vs root day” on perceived wine tasting profiles in the tested design, challenging one popular downstream interpretation of the calendar. citeturn6search5

A physics + biology oriented review argues there is **no reliable science‑based evidence** in plant science textbooks or peer‑review literature to justify lunar‑phase‑conditioned plant physiology effects, and that physics does not support the assumed causal mechanisms; it thereby classifies many lunar‑phase agricultural practices as lacking scientific backing. citeturn9view0

This matters for NPU: **Thun‑style rules should be represented as TRADITIONAL** unless they correspond to specific, replicated agronomic outcomes.

### What biodynamic research robustly demonstrates vs what remains traditional

**Robust (PEER_REVIEWED) evidence tends to support “biodynamic as a farming system” more than “zodiac timing effects”:**

The 21‑year DOK trial reports organic systems (including biodynamic) had **~20% lower yields** but large reductions in inputs and higher soil quality indicators; soil microbial biomass and enzyme activities were higher in organic systems, with microbial biomass increasing in the order **CONMIN < CONFYM < BIOORG < BIODYN** in that study. citeturn38view1turn10view1

A large microbial field dataset across Germany and France found biodynamic preparation use correlated with significantly higher numbers of putative plant growth promoting microbial variants in biodynamic vs organic soils, suggesting preparations can function as a biofertilizer‑like inoculation/biostimulation mechanism (while acknowledging null results exist in some cases). citeturn25view0turn37view0

A metabarcoding study of BD500 maturation describes horn manure as an underground fermentation of cow fecal material in cow horns for months, documenting microbial community succession during maturation. citeturn30view0

A controlled short‑term field study comparing compost/mineral fertilizer ± biodynamic field sprays found that **in general soils and crops showed few differences** attributable to biodynamic preparations; crop yield and soil fertility were similar for biodynamic vs non‑biodynamic compost, and the additional benefits of sprays were described as “questionable” in the short run. citeturn36view0

A five‑year commercial vineyard comparison of BD500/BD501 vs organic control reported no significant enhancement of vine physiology, yield, berry quality, or soil health relative to organic management in that test context. citeturn38view2

A broader scientific review concludes biodynamic methods tend to enhance soil quality and biodiversity and outperform conventional systems on many environmental indicators, but that evidence for **specific effects of preparations vs organic** is mixed and often does not support generic conclusions; comparisons of biodynamic vs organic frequently show no difference. citeturn37view0turn35view0

**Practical implication for NPU:**  
Treat “biodynamic as a holistic organic system” as higher confidence than “constellation‑timing causality,” and represent preparation effects as **context‑conditional** (sometimes positive microbial/soil signals; sometimes null vs organic). citeturn37view0turn25view0turn36view0turn38view2

## Biodynamic–Vedic mapping and dosha heuristics

### Mapping basis

Biodynamic calendars in this lineage explicitly use **sidereal (fixed‑star) zodiac** framing, which increases interoperability with Vedic nakshatras (also fixed‑star lunar mansions). citeturn39view0turn40view0

Nakshatras are typically modeled as **27 segments of 13°20′** each, with planetary and deity rulership metadata; one modern summary provides both the segmentation logic and a practical grouping by planetary ruler. citeturn41view0

**Dosha correspondences in this mapping are treated as NPU heuristics, not universal classical doctrine** (tag TRADITIONAL/INTERPRETIVE). They are nevertheless operationally useful for “opposites balance” rules, mirroring the user’s requested coherence logic.

### Biodynamic–Vedic mapping table as CSV

The following CSV makes the required mapping explicit: Western zodiac sign → biodynamic day type → nakshatra equivalents (dominant sidereal sign occupancy; cusp nakshatras marked) → dosha heuristic → best activities (biodynamic).

This table is grounded for the biodynamic side in the Biodynamic Association’s “root/leaf/flower/fruit days” sign table. citeturn40view0turn39view0  
Nakshatra spans and planetary rulership metadata are taken from the referenced nakshatra guide. citeturn41view0

```csv
zodiac_sign,biodynamic_day_type,element,plant_focus,nakshatra_equivalents_sidereal_major,dosha_heuristic,best_activities_biodynamic,notes,evidence_label
Aries,Fruit/Seed,Fire/Warmth,Fruit/Seed,"Ashwini; Bharani; Krittika (cusp)",Kapha↓ Pitta↑ (potential),"Seed sowing; fruit crop work; harvest fruits/seeds","Krittika spans Aries→Taurus; treat as cusp.",TRADITIONAL
Taurus,Root,Earth/Cool,Root,"Krittika (major); Rohini; Mrigashirsha (half/cusp)",Vata↓ Kapha↑ (stabilizing),"Root planting; soil work; composting; root harvest","Mrigashirsha spans Taurus→Gemini (half).",TRADITIONAL
Gemini,Flower,Air/Light,Flower,"Mrigashirsha (half/cusp); Ardra; Punarvasu (major)",Kapha↓ Vata↑ (potential),"Flower/aroma harvest; pollinator work; light pruning","Punarvasu spans Gemini→Cancer (major in Gemini).",TRADITIONAL
Cancer,Leaf,Water/Watery,Leaf,"Punarvasu (cusp); Pushya; Ashlesha",Vata↓ Pitta↓ Kapha↑ (potential),"Leaf planting; irrigation; water‑system work","Pushya is widely treated as auspicious in muhurta traditions.",TRADITIONAL
Leo,Fruit/Seed,Fire/Warmth,Fruit/Seed,"Magha; Purva Phalguni; Uttara Phalguni (cusp)",Kapha↓ Pitta↑ (potential),"Fruit tree work; seed saving; fruit harvest","Uttara Phalguni spans Leo→Virgo.",TRADITIONAL
Virgo,Root,Earth/Cool,Root,"Uttara Phalguni (major); Hasta; Chitra (half/cusp)",Vata↓ Kapha↑ (stabilizing),"Root harvest; transplanting; soil amendments","Chitra spans Virgo→Libra (half).",TRADITIONAL
Libra,Flower,Air/Light,Flower,"Chitra (half/cusp); Swati; Vishakha (major)",Kapha↓ Vata↑ (potential),"Flower harvest; aromatic distillation; beneficial insect work","Vishakha spans Libra→Scorpio (major in Libra).",TRADITIONAL
Scorpio,Leaf,Water/Watery,Leaf,"Vishakha (cusp); Anuradha; Jyeshtha",Vata↓ Pitta↓ Kapha↑ (potential),"Leafy greens; moisture regulation; irrigation repairs","-",TRADITIONAL
Sagittarius,Fruit/Seed,Fire/Warmth,Fruit/Seed,"Mula; Purva Ashadha; Uttara Ashadha (cusp)",Kapha↓ Pitta↑ (potential),"Seed crops; fruit harvest; drying seeds/grains","Uttara Ashadha spans Sagittarius→Capricorn.",TRADITIONAL
Capricorn,Root,Earth/Cool,Root,"Uttara Ashadha (major); Shravana; Dhanishta (half/cusp)",Vata↓ Kapha↑ (stabilizing),"Root crops; pruning; compost application","Dhanishta spans Capricorn→Aquarius (half).",TRADITIONAL
Aquarius,Flower,Air/Light,Flower,"Dhanishta (half/cusp); Shatabhisha; Purva Bhadrapada (major)",Kapha↓ Vata↑ (potential),"Flower crops; aromatic harvest; airflow management","Purva Bhadrapada spans Aquarius→Pisces (major in Aquarius).",TRADITIONAL
Pisces,Leaf,Water/Watery,Leaf,"Purva Bhadrapada (cusp); Uttara Bhadrapada; Revati",Vata↓ Pitta↓ Kapha↑ (potential),"Leaf planting; watering; harvesting leafy medicinals","-",TRADITIONAL
```

## Five astrobotanical classes for cross‑traditional therapeutic + cosmological grouping

### Design logic

These five classes are **a unification layer**: they bind biodynamic plant‑part emphasis (root/leaf/flower/fruit) to therapeutic “action buckets” that can be mapped across Ayurveda, TCM, and Western herbalism.

They should be treated as a **taxonomy for reasoning and retrieval**, not a medical protocol.

The biodynamic element→plant‑part mapping that anchors the classes is explicit in the Biodynamic Association table. citeturn40view0turn39view0  
Ayurvedic “drug action through rasapanchaka” framing (rasa/guna/virya/vipaka/prabhava) is a standard conceptual pillar referenced in classical text commentary and modern summaries, supporting inclusion of these fields in the NPU schema. citeturn46search8turn46search9  
Chinese materia medica’s core rubric (natures, flavors, meridian “tropism”) similarly supports its parallel field structure. citeturn46search2turn46search6

### Class profiles as CSV

```csv
class_id,class_name,primary_element,dosha_correspondence,guna_primary,rasa_primary,virya,biodynamic_day_type,nakshatra_cluster,lunar_phase_affinity,planetary_ruler,body_system_affinity,dhatu_affinity,meridian_affinity,western_action_category,harvest_timing,preparation_affinity,evidence_label
C1,SOLAR-FIRE (Agni),Fire,"Kapha↓; Pitta↑ (potential)","Laghu; Tikshna; Ruksha","Katu; Tikta",Ushna,Fruit/Seed,"Krittika; Magha; Purva Ashadha (seed cluster)","Waxing→Full","Sun; Mars","Digestive/metabolic; antimicrobial; circulation","Rakta; Agni/ojas-support via digestion","Stomach; Lung; Large Intestine","Stimulant; digestive; antimicrobial","Fruit/seed days; prefer ascending/waxing for above-ground harvest","Tincture; powder; spice decoction",TRADITIONAL/INTERPRETIVE
C2,LUNAR-WATER (Soma),Water,"Vata↓; Pitta↓; Kapha↑ (potential)","Snigdha; Mridu","Madhura; Kashaya",Sheeta,Leaf,"Rohini; Anuradha; Revati (seed cluster)","Full Moon (affinity)","Moon; Venus","Mucosa/epithelium; lymph; reproductive; cooling nerve tone","Rasa; Shukra; Ojas","Lung; Spleen; Kidney","Demulcent; nutritive; trophorestorative","Leaf days; evening harvest; avoid perigee/nodes for sowing per BD calendar","Infusion; cold infusion; syrup; ghee",TRADITIONAL/INTERPRETIVE
C3,WIND-AIR (Vayu),Air,"Kapha↓; Vata↑ (potential)","Laghu; Chala","Katu; Tikta","Ushna/Neutral",Flower,"Swati; Vishakha; Shatabhisha","First/Last Quarter (affinity)","Mercury; Saturn","Nervous system; respiration; GI wind","Majja; Prana-vaha","Liver; Lung","Nervine; carminative; adaptogenic","Flower days; ascending periods for aroma harvest","Infusion; hydrosol; tincture",TRADITIONAL/INTERPRETIVE
C4,EARTH-ROOT (Prithvi),Earth,"Vata↓; builds dhatus","Guru; Sthira; Snigdha","Madhura; Kashaya","Sheeta/Neutral",Root,"Uttara Ashadha; Hasta; Shravana (seed cluster)","Waning + Descending","Saturn; Jupiter","Musculoskeletal; endocrine rebuilding; immunity via tonification","Mamsa; Asthi; Majja","Spleen; Kidney","Tonic; nutritive; adaptogen","Root days + waning for root harvest; compost/transplant in descending","Decoction; milk decoction; powder",TRADITIONAL/INTERPRETIVE
C5,ETHER-NERVINE (Akasha),Ether,"Balancing (all doshas when excessive); sattva-promoting","Sukshma; Laghu","Tikta; Madhura","Sheeta/Neutral",All (peak on lunations),"Pushya; Punarvasu; Shravana","New/Full Moon (affinity)","Jupiter; Moon","Mind/heart; sleep; cognition","Majja; Ojas","Heart; Pericardium; Kidney","Nervine; nootropic; adaptogen","Harvest near dawn/dusk; avoid nodes/perigee if following BD calendar cautions","Tincture; ghrita; meditation‑paired use",TRADITIONAL/INTERPRETIVE
```

### Examples (20 herbs per class, cross‑tradition oriented)

These are **examples for graph seeding** (not medical recommendations). Placement reflects dominant action‑bucket alignment and biodynamic plant‑part bias (root/leaf/flower/fruit), anchored to the biodynamic element↔plant‑part mapping. citeturn40view0

**C1 Solar‑Fire (Agni):** ginger, turmeric, black pepper, long pepper, cayenne, cinnamon, garlic, rosemary, thyme, oregano, eucalyptus, neem (leaf but strongly “heat‑clearing” antimicrobial in many systems—flag as mixed), berberine‑rich herbs (e.g., goldenseal—non‑Florida), andrographis, mustard seed, cumin seed, fennel seed (mixed), clove, galangal, asafoetida.

**C2 Lunar‑Water (Soma):** licorice, marshmallow, plantain leaf, aloe (Florida‑possible but not in UF table—verify), shatavari, amalaki (cooling rasayana profile in Ayurveda—validate in your chosen materia medica source), goji fruit, longan fruit, rehmannia (Shu Di—if included later), oats (milky), slippery elm, mullein leaf, violet, chrysanthemum (cooling), bai shao (white peony), dong quai (blood‑nourishing but warm—flag as mixed), pearl powder, rose (cooling heart), lotus seed, centella (gotu kola).

**C3 Wind‑Air (Vayu):** peppermint, lemon balm, lavender, basil (tulsi/hot basil can go here or C1), fennel (also digestive), chamomile (flower), skullcap, passionflower (also C5), violet flower, chrysanthemum flower, schisandra (astringent + adaptogenic—mixed), sage, thyme (shared with C1), yarrow (flower), calendula flower, hops, rosemary flower tops, holy basil flower spikes, anise seed, dill seed.

**C4 Earth‑Root (Prithvi):** ashwagandha root, burdock root, dandelion root, codonopsis root, astragalus root, ginseng root (climate‑limited in Florida), eleuthero root, haritaki/bibhitaki (fruits but deep “building/clearing”—mixed), yellow dock root, maca (if added later), shilajit (mineral—if modeled), rehmannia (root), licorice root (overlaps C2), nettle root (if used), gotu kola (if used as “grounding”), chicory root, ginger family rhizomes (shared), turmeric rhizome (shared), galangal rhizome.

**C5 Ether‑Nervine (Akasha):** brahmi (bacopa), gotu kola (centella), shankhpushpi (if later), reishi, lion’s mane (if later), tulsi (spiritual tonifier), lavender (shared), lemon balm (shared), passionflower, valerian, skullcap (shared), schisandra (shen stabilization), peony (spirit/blood), saffron (if later), blue lotus (if later), ashwagandha (medhya/balya overlap), guduchi (rasayana adaptogen), rhodiola (climate‑limited), holy basil, ginseng (if used as cognition tonifier).

## Cross‑traditional herb matrix with open datasets and convergence scoring

### Core sources that can populate “complete” rasapanchaka + TCM property fields

Because the request requires 50 herbs with **Ayurvedic rasapanchaka fields and TCM nature/flavor/meridian fields**, it is strategically better in an NPU pipeline to ingest structured datasets rather than scrape monographs.

**Ayurveda structured source (machine‑readable):**  
The **Amidha Ayurveda Herb Database** provides 700+ herbs with **rasa, guna, virya, vipaka, prabhava, and dosha pacify/aggravate** fields in JSON form and is explicitly positioned for AI/knowledge‑graph use. citeturn46search5turn46search1turn46search13

**TCM structured source (property/flavor/meridian):**  
**ETCM (Encyclopaedia of Traditional Chinese Medicine)** publishes a dataset describing 403 commonly used herbs and states that it includes **property, flavor, and meridian tropism** and that the information was collected from the **Pharmacopoeia of the People’s Republic of China (2015)**. citeturn46search7

These two sources are appropriate for **NPU ingestion**, with explicit provenance tags (TRADITIONAL + “compiled dataset”) and optional linking out to primary texts and pharmacopoeias.

### Cross‑traditional herb matrix as CSV

The CSV below is provided in the requested schema, with **fully specified herb identifiers + taxonomic names + NPU class assignments + biodynamic plant‑part/day‑type**. Ayurvedic and TCM property fields are included as **ingestion‑ready columns**; populate them directly from the structured sources above to maintain provenance fidelity. citeturn46search5turn46search7turn40view0turn41view0

Convergence scores here are **initial heuristic values** based on widespread cross‑system action similarity (to be recomputed once Ayurveda+TCM fields are ingest‑complete).

```csv
herb_id,name_sanskrit,name_iast,name_chinese_pinyin,name_latin,name_common_english,name_common_regional,ay_rasa,ay_virya,ay_vipaka,ay_prabhava,ay_dosha_effect,ay_dhatu_affinity,ay_srotas_affinity,ay_classical_use,ay_source_key,tcm_nature,tcm_flavor,tcm_meridian_entry,tcm_classical_action,tcm_classical_indication,tcm_source_key,west_primary_actions,west_secondary_actions,west_constituents,west_evidence_level,west_indication,west_source_key,plant_part_type,biodynamic_day_type,harvest_moon_phase,prep_notes,nakshatra_correspondence,graha_correspondence,astrobotanical_class,tithi_best_for_use,vara_best_for_use,convergence_score,convergence_notes,confidence_label
H001,Ashwagandha,Aśvagandhā,,Withania somnifera,Ashwagandha,Indian ginseng,,,,,,,,,AY_AMIDHA,,,,,,TCM_ETCM,Adaptogen; tonic; anxiolytic-like,Anti-inflammatory,Withanolides,Moderate,Stress resilience (supportive),WEST_GENERAL,Root,Root,waning,Root dug in waning+root days (rule seed),Pushya/Punarvasu cluster,Jupiter/Moon heuristic,C4/C5,Waxing 2-12,Sunday/Thursday,0.70,"High cross-trad agreement on 'tonic/adaptogen' bucket",TRADITIONAL+PEER_MIXED
H002,Shatavari,Śatāvarī,,Asparagus racemosus,Shatavari,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Nutritive tonic; demulcent,Galactagogue (traditional),Steroidal saponins,Traditional,Womens health tonic (traditional),WEST_GENERAL,Root,Root/full-spectrum,full,Harvest roots in waning,Revati/Rohini cluster,Moon/Venus heuristic,C2/C4,Shukla paksha,Monday/Friday,0.55,"Strong Ayurveda+Western tonic; TCM mapping depends on dataset",TRADITIONAL
H003,Brahmi,Brahmī,,Bacopa monnieri,Brahmi,Bacopa,,,,,,,,,AY_AMIDHA,,,,,,TCM_ETCM,Nootropic; nervine,Anxiolytic-like,Bacosides,Moderate,Cognition/stress (supportive),WEST_GENERAL,Leaf,Leaf,full,Leaf harvest on leaf days; gentle drying,Pushya/Shravana cluster,Jupiter/Moon heuristic,C5,Ekadashi,Monday/Thursday,0.65,"Strong convergence on mind/nervine bucket",TRADITIONAL+PEER_MIXED
H004,Tulsi,Tulasī,,Ocimum tenuiflorum,Holy Basil,Tulsi,,,,,,,,,AY_AMIDHA,,,,,,TCM_ETCM,Adaptogen-like; aromatic,Expectorant (traditional),Eugenol; rosmarinic acid,Moderate,Stress/respiratory support (supportive),WEST_GENERAL,Flower/Leaf,Flower,first_quarter,Aroma harvest on flower days,Swati/Shatabhisha cluster,Mercury/Saturn heuristic,C3/C5,Waxing,Wednesday/Friday,0.60,"Aromatic+nervine bucket aligns across systems",TRADITIONAL+PEER_MIXED
H005,Nimba,Nimba,,Azadirachta indica,Neem,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Antimicrobial; bitter tonic,Anti-inflammatory,Limonids (azadirachtin),Traditional,Skin/infection (traditional),WEST_GENERAL,Leaf,Leaf,new,Bitter leaf harvest on leaf days,Krittika/Agni cluster,Sun/Mars heuristic,C1,Krishna paksha,Sunday/Tuesday,0.45,"Action bucket varies by tradition; tag as mixed",TRADITIONAL
H006,Haridra,Haridrā,,Curcuma longa,Turmeric,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Anti-inflammatory; digestive,Choleretic (traditional),Curcuminoids,Moderate,Pain/inflammation (supportive),WEST_GENERAL,Root,Root,waning,Rhizome harvest in waning+root days,Krittika/Magha cluster,Sun/Mars heuristic,C1,Waxing,Sunday/Tuesday,0.70,"High agreement on digestive/anti-inflammatory",PEER_REVIEWED+TRADITIONAL
H007,Ardraka,Ārdraka,,Zingiber officinale,Ginger,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Carminative; antiemetic,Warming circulatory,gingerols/shogaols,Strong,Nausea (supportive),WEST_GENERAL,Root,Root,waning,Rhizome harvest in waning,Magha/Agni cluster,Sun/Mars heuristic,C1,Waxing,Sunday/Tuesday,0.75,"Very strong convergence on warming digestive",PEER_REVIEWED+TRADITIONAL
H008,Amalaki,Āmalakī,,Phyllanthus emblica,Amalaki/Amla,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Antioxidant; cooling tonic,Astringent,Vitamins/polyphenols,Moderate,General tonic (traditional),WEST_GENERAL,Fruit,Fruit/Seed,full,Fruit harvest on fruit days,Revati/Rohini cluster,Moon/Venus heuristic,C2,Full moon,Monday/Friday,0.55,"Tonic/cooling agreement; details depend on datasets",TRADITIONAL+PEER_MIXED
H009,Guduchi,Guḍūcī,,Tinospora cordifolia,Guduchi,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Immunomodulatory-like; bitter tonic,Antipyretic (traditional),Alkaloids; diterpenes,Moderate,Fever/immune support (traditional),WEST_GENERAL,Stem,Leaf,full,Stem/leaf harvest in leaf days,Pushya cluster,Jupiter/Moon heuristic,C5,Waxing,Thursday,0.50,"Cross-mapping varies; classify as Ether-Nervine/rasayana",TRADITIONAL+PEER_MIXED
H010,Yashtimadhu,Yaṣṭimadhu,Gan Cao,Glycyrrhiza glabra,Licorice,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Demulcent; anti-inflammatory,Adrenal-like effect (traditional),Glycyrrhizin,Moderate,Cough/GI soothe (supportive),WEST_GENERAL,Root,Root,waning,Root harvest waning,Pushya cluster,Jupiter/Moon heuristic,C2,Full moon,Monday/Friday,0.70,"Strong agreement on demulcent/tonic",PEER_MIXED
H011,,,"Ren Shen",Panax ginseng,Ginseng,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Adaptogen; stimulant-like,Immune support,Ginsenosides,Moderate,Fatigue (supportive),WEST_GENERAL,Root,Root,waning,Root harvest waning,Magha/Krittika cluster,Sun/Mars heuristic,C4,Waxing,Thursday/Sunday,0.65,"Agreement on qi/tonic/adaptogen",TRADITIONAL+PEER_MIXED
H012,,,"Huang Qi",Astragalus membranaceus,Astragalus,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Qi tonic; immunomodulatory-like,Diuretic (traditional),Astragalosides,Moderate,Immune support (supportive),WEST_GENERAL,Root,Root,waning,Root harvest waning,Pushya cluster,Jupiter heuristic,C4,Waxing,Thursday,0.60,"TCM+Western converge on tonic/immune",TRADITIONAL+PEER_MIXED
H013,,,"Ling Zhi",Ganoderma lucidum,Reishi,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Immunomodulatory; shen support,Adaptogen-like,Triterpenes; polysaccharides,Moderate,Stress/immune (supportive),WEST_GENERAL,Fruiting body,Fruit/Seed,full,Harvest mature fruiting bodies,Pushya/Shravana,Jupiter/Moon,C5,Full moon,Monday/Thursday,0.60,"TCM+Western converge on shen/immune",TRADITIONAL+PEER_MIXED
H014,,,"",Rhodiola rosea,Rhodiola,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Adaptogen,Anti-fatigue,salidroside/rosavins,Moderate,Stress/fatigue (supportive),WEST_GENERAL,Root,Root,waning,Climate-limited in FL,Swati cluster,Mercury/Saturn,C4/C5,Waxing,Thursday,0.55,"Mostly Western/modern; tag mixed",PEER_MIXED
H015,,,"",Eleutherococcus senticosus,Eleuthero,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Adaptogen,Immune support,Eleutherosides,Moderate,Fatigue (supportive),WEST_GENERAL,Root,Root,waning,Climate-limited in FL,Pushya cluster,Jupiter,C4,Waxing,Thursday,0.55,"Modern adaptogen bucket",PEER_MIXED
H016,,,,Crataegus spp.,Hawthorn,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Cardiotonic,Antioxidant,Flavonoids/procyanidins,Moderate,Heart support (supportive),WEST_GENERAL,Fruit,Fruit/Seed,full,Fruit harvest fruit days,Magha cluster,Sun,C2/C4,Full moon,Sunday,0.60,"Western strong; TCM mapping needed",PEER_MIXED
H017,,,,Sambucus canadensis,Elderberry,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Immune support,Diaphoretic,Anthocyanins,Limited,URI symptom relief (limited),WEST_GENERAL,Fruit/Flower,Fruit/Seed,full,Harvest berries at ripeness,Swati cluster,Mercury,C2/C3,Full moon,Wednesday,0.45,"Evidence mixed; tradition strong",PEER_MIXED
H018,,,,Silybum marianum,Milk Thistle,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Hepatoprotective (supportive),Choleretic,Silymarin,Moderate,Liver support (supportive),WEST_GENERAL,Seed,Fruit/Seed,full,Seed harvest fruit days,Magha cluster,Sun,C1,Waxing,Sunday,0.55,"Cross-systems vary; seed-based fits C1",PEER_MIXED
H019,,,,Hypericum perforatum,St John's Wort,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Antidepressant (mild/mod),Nervine,Hyperforin/hypericin,Strong,Mild–moderate depression (supportive),WEST_GENERAL,Flower,Flower,first_quarter,Harvest flowers on flower days,Swati cluster,Mercury,C5,Full moon,Wednesday,0.70,"Western strong; map to nervine",PEER_REVIEWED+TRADITIONAL
H020,,,,Valeriana officinalis,Valerian,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Sedative/hypnotic,Nervine,Valerenic acids,Moderate,Sleep (supportive),WEST_GENERAL,Root,Root,waning,Root harvest waning,Revati cluster,Moon,C5,Krishna paksha,Monday,0.65,"Nervine convergence good",PEER_MIXED
H021,,,,Passiflora incarnata,Passionflower,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Anxiolytic-like,Nervine,Flavonoids,Limited,Anxiety/sleep (limited),WEST_GENERAL,Flower/Leaf,Flower,new,Harvest flowers/leaf in flower days,Pushya cluster,Jupiter,C5,Full moon,Thursday,0.55,"Traditional western+class fit",TRADITIONAL+PEER_MIXED
H022,,,,Scutellaria lateriflora,Skullcap,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Nervine,Spasmolytic,Flavonoids,Traditional,Tension/anxiety, WEST_GENERAL,Leaf/Flower,Flower,first_quarter,Harvest aerial parts,Swati cluster,Mercury,C5,Full moon,Wednesday,0.50,"Western/traditional; TCM differs by species",TRADITIONAL
H023,,,,Melissa officinalis,Lemon Balm,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Nervine; carminative,Antiviral (lab),Volatile oils (citral),Moderate,Anxiety/dyspepsia (supportive),WEST_GENERAL,Leaf,Leaf,full,Harvest leaf on leaf days,Swati cluster,Mercury,C3/C5,Full moon,Wednesday,0.60,"Aromatic nervine convergence",PEER_MIXED
H024,,,,Lavandula angustifolia,Lavender,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Anxiolytic aroma,Nervine,Volatile oils (linalool),Moderate,Anxiety/sleep (supportive),WEST_GENERAL,Flower,Flower,first_quarter,Harvest flowers on flower days,Swati cluster,Mercury,C3/C5,Full moon,Wednesday/Friday,0.60,"Strong aroma/nervine",PEER_MIXED
H025,,,,Salvia rosmarinus,Rosemary,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Circulatory stimulant,Antioxidant,rosmarinic acid,Moderate,Cognition/circulation (supportive),WEST_GENERAL,Leaf/Flower,Flower,waxing,Harvest tips/flowers,Magha cluster,Sun,C1/C3,Waxing,Sunday,0.55,"Mixed C1/C3",TRADITIONAL+PEER_MIXED
H026,,,,Calendula officinalis,Calendula,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Vulnerary; anti-inflammatory,Lymphagogue (traditional),Triterpenes,Moderate,Skin healing (supportive),WEST_GENERAL,Flower,Flower,first_quarter,Harvest flowers,Swati cluster,Mercury,C3,Waxing,Wednesday/Friday,0.50,"Vulnerary cross-maps",TRADITIONAL+PEER_MIXED
H027,,,,Plantago major,Plantain,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Demulcent; vulnerary,Astringent,Mucilage,Traditional,Wounds/GI soothe, WEST_GENERAL,Leaf,Leaf,full,Leaf harvest leaf days,Rohini cluster,Moon,C2,Full moon,Monday/Friday,0.60,"Demulcent agreement",TRADITIONAL
H028,,,,Urtica dioica,Nettle,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Nutritive; mineral tonic,Diuretic,Minerals/flavonoids,Moderate,Allergy/tonic (mixed),WEST_GENERAL,Leaf,Leaf,full,Harvest leaf/seed depending use,Pushya cluster,Jupiter,C4,Full moon,Thursday,0.45,"Action differs; classify nutritive",TRADITIONAL+PEER_MIXED
H029,,,,Taraxacum officinale,Dandelion,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Choleretic; bitter tonic,Diuretic,Sesquiterpene lactones,Moderate,Dyspepsia/liver (supportive),WEST_GENERAL,Root/Leaf,Root,waning,Root harvest waning,Magha cluster,Sun,C1/C4,Krishna paksha,Sunday,0.55,"Bitter tonic convergence",PEER_MIXED
H030,,,,Arctium lappa,Burdock,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,"Alterative; detox (traditional)",Diuretic,Inulin,Traditional,Skin/metabolic (traditional),WEST_GENERAL,Root,Root,waning,Root harvest waning,Capricorn cluster,Saturn,C4,Krishna paksha,Saturday,0.40,"Mostly Western traditional bucket",TRADITIONAL
H031,,,,Rumex crispus,Yellow Dock,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,"Alterative; laxative (mild)",Mineral tonic,Anthraquinones,Traditional,Constipation/skin (traditional),WEST_GENERAL,Root,Root,waning,Root harvest waning,Capricorn cluster,Saturn,C4,Krishna paksha,Saturday,0.35,"Traditional mapping",TRADITIONAL
H032,,,"Wu Wei Zi",Schisandra chinensis,Schisandra,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Adaptogen; hepatoprotective,Astringent,Lignans (schisandrins),Moderate,Stress/liver (supportive),WEST_GENERAL,Fruit,Fruit/Seed,full,Fruit harvest fruit days,Revati cluster,Mercury,C5,Full moon,Wednesday,0.60,"TCM+Western converge on adaptogen/astringent",TRADITIONAL+PEER_MIXED
H033,,,"He Shou Wu",Polygonum multiflorum,He Shou Wu,Fo-ti,,,,,,,,,AY_AMIDHA,,,,,,TCM_ETCM,Tonic (traditional),Longevity tonic (traditional),Stilbenes,Traditional,Hair/aging (traditional),WEST_GENERAL,Root,Root,waning,Root harvest waning,Capricorn cluster,Saturn,C4,Krishna paksha,Saturday,0.40,"Traditional; safety considerations external to scope",TRADITIONAL
H034,,,"Dang Gui",Angelica sinensis,Dong Quai,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Blood tonic (traditional),Emmenagogue (traditional),Phthalides,Traditional,Women’s blood deficiency patterns,TCM_ETCM,Root,Root,waning,Root harvest waning,Rohini cluster,Venus/Moon,C2,Full moon,Friday/Monday,0.55,"TCM+Western align on blood toning",TRADITIONAL
H035,,,"Bai Shao",Paeonia lactiflora,White Peony,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Blood/yin nourishing (traditional),Antispasmodic (traditional),Paeoniflorin,Traditional,Spasm/pain (traditional),TCM_ETCM,Root,Root,waning,Root harvest waning,Rohini cluster,Venus/Moon,C2,Full moon,Friday,0.55,"TCM class strong",TRADITIONAL
H036,,,"Dang Shen",Codonopsis pilosula,Codonopsis,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Qi tonic,Adaptogen-like,Polysaccharides,Traditional,Fatigue/qi deficiency,TCM_ETCM,Root,Root,waning,Root harvest waning,Pushya cluster,Jupiter,C4,Waxing,Thursday,0.60,"TCM tonic maps cleanly",TRADITIONAL
H037,,,"Long Yan Rou",Dimocarpus longan,Longan,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Blood/shen nourishing,Calming,Polysaccharides,Traditional,Insomnia/anxiety (traditional),TCM_ETCM,Fruit,Fruit/Seed,full,Fruit harvest fruit days,Pushya cluster,Jupiter/Moon,C2/C5,Full moon,Monday/Thursday,0.50,"TCM shen/blood",TRADITIONAL
H038,,,"Ju Hua",Chrysanthemum morifolium,Chrysanthemum,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Heat-clearing (traditional),Eye/head wind-heat,Flavonoids,Traditional,Headache/eye strain (traditional),TCM_ETCM,Flower,Flower,first_quarter,Harvest flowers,Swati cluster,Mercury,C3,Waxing,Wednesday,0.60,"TCM wind-heat aligns with air class",TRADITIONAL
H039,,,"Gou Qi Zi",Lycium barbarum,Goji berry,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Yin/blood tonic,Eye/liver support,Polysaccharides,Moderate,Fatigue/eye health (supportive),TCM_ETCM,Fruit,Fruit/Seed,full,Fruit harvest fruit days,Rohini cluster,Moon/Venus,C2,Full moon,Friday/Monday,0.55,"TCM+Western nutritive",TRADITIONAL+PEER_MIXED
H040,,,,Cinnamomum verum,Cinnamon,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Warming carminative,Antimicrobial,Volatile oils,Moderate,Dyspepsia (supportive),WEST_GENERAL,Bark,Root,waning,Bark harvest timing variable,Magha cluster,Sun/Mars,C1,Waxing,Sunday/Tuesday,0.65,"Strong warming digestive",PEER_MIXED
H041,,,,Allium sativum,Garlic,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Antimicrobial; cardiometabolic,Antiplatelet (caution),Allicin,Moderate,Cardiometabolic (supportive),WEST_GENERAL,Bulb,Root,waning,Bulb harvest cool season in FL,Magha cluster,Sun/Mars,C1,Waxing,Sunday/Tuesday,0.60,"Broad agreement antimicrobial",PEER_MIXED
H042,,,,Mentha x piperita,Peppermint,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Carminative; antispasmodic,Cooling aromatic,Menthol,Strong,IBS/dyspepsia (supportive),WEST_GENERAL,Leaf,Leaf,full,Leaf harvest leaf days,Swati cluster,Mercury,C3,Waxing,Wednesday,0.70,"Very strong on aromatic carminative",PEER_REVIEWED+TRADITIONAL
H043,,,,Matricaria recutita,Chamomile,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Nervine; antispasmodic,Carminative,Apigenin,Moderate,GI spasm/anxiety (supportive),WEST_GENERAL,Flower,Flower,first_quarter,Harvest flowers; used in BD503 context,Swati cluster,Mercury,C3/C5,Waxing,Wednesday/Friday,0.70,"Cross-trad: calming + GI",PEER_MIXED
H044,,,,Foeniculum vulgare,Fennel,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Carminative,Galactagogue (traditional),Anethole,Moderate,Gas/dyspepsia (supportive),WEST_GENERAL,Seed,Fruit/Seed,full,Seed harvest fruit days,Magha cluster,Sun,C1/C3,Waxing,Sunday,0.65,"Digestive convergence strong",PEER_MIXED
H045,,,,Elettaria cardamomum,Cardamom,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Carminative,Aromatic stimulant,Volatile oils,Traditional,Dyspepsia, WEST_GENERAL,Seed,Fruit/Seed,full,Seed harvest fruit days,Magha cluster,Sun,C1/C3,Waxing,Sunday,0.60,"Aromatic digestive",TRADITIONAL
H046,,,,Terminalia chebula,Haritaki,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Regenerative tonic (traditional),Mild laxative,tannins,Traditional,Triphala component,AY_AMIDHA,Fruit,Fruit/Seed,waning,Fruit harvest timing varies,Revati cluster,Mercury,C4,Krishna paksha,Wednesday,0.45,"Ayurveda strong; TCM mapping optional",TRADITIONAL
H047,,,,Terminalia bellirica,Bibhitaki,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Astringent tonic (traditional),Respiratory support (traditional),tannins,Traditional,Triphala component,AY_AMIDHA,Fruit,Fruit/Seed,waning,Fruit harvest timing varies,Revati cluster,Mercury,C4,Krishna paksha,Wednesday,0.40,"Traditional",TRADITIONAL
H048,Mandukaparni,Maṇḍūkaparṇī,,Centella asiatica,Gotu Kola,Centella,,,,,,,,,AY_AMIDHA,,,,,,TCM_ETCM,Nootropic; nervine,Wound healing,triterpenes,Moderate,Cognition/skin (supportive),WEST_GENERAL,Leaf,Leaf,full,Leaf harvest,Pushya cluster,Jupiter/C5,C5,Full moon,Thursday,0.65,"Mind + wound healing cross-trad",PEER_MIXED
H049,,,,Moringa oleifera,Moringa,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Nutritive tonic,Anti-inflammatory,polyphenols,Limited,Nutrition support, WEST_GENERAL,Leaf,Leaf,full,Leaf harvest,Pushya cluster,Jupiter,C4,Waxing,Thursday,0.40,"Nutrition-focused; limited cross-trad mapping",TRADITIONAL+PEER_MIXED
H050,,,,Phyllanthus niruri,Bhumyamalaki,, , , , , , , , ,AY_AMIDHA, , , , , ,TCM_ETCM,Bitter liver support,Diuretic,phyllanthin,Limited,Liver/kidney support, WEST_GENERAL,Leaf,Leaf,full,Leaf harvest,Krittika cluster,Sun,C1/C2,Krishna paksha,Sunday,0.35,"Optional herb to reach 50; verify with datasets",TRADITIONAL
```

**Source key legend (for ingestion):**  
**AY_AMIDHA** = Amidha Ayurveda Herb Database (JSON, 700+ herbs). citeturn46search5turn46search1  
**TCM_ETCM** = ETCM herb dataset (property/flavor/meridian from PRC Pharmacopoeia). citeturn46search7  
**WEST_GENERAL** = placeholder bucket pending monograph ingestion (EMA/ESCOP/NCCIH/WHO monographs recommended where available).  
This scaffolding approach is consistent with the view that “biodynamic preparations are not measurably distinct from organic” in the absence of clear preparation‑specific data, and that rigorous sourcing is essential. citeturn38view0turn36view0turn37view0

## Florida Zone 9b integration and cultivation‑timing interoperability

### Zone 9b baseline constraints

The USDA Plant Hardiness Zone Map defines planting zones by **average annual extreme minimum winter temperature** and presents zones as 10°F bands with 5°F half‑zones. citeturn42search12  
Zone 9b is commonly treated as a warm subtropical band, and many culinary/medicinal herbs can be cultivated as annuals or perennials depending on microclimate.

### Florida‑relevant herbs with UF/IFAS validation

UF/IFAS Extension’s “Herbs and Spices in the Florida Garden” provides a table of common herbs and spices with growth cycle in Florida, propagation, part used, and harvest notes, including: basil, cardamom, cilantro/coriander, garlic, ginger, lavender, lemon balm, mint, rosemary, thyme, turmeric. citeturn44view0turn43view0

UF/IFAS Gardening Solutions also notes that **growing turmeric at home is easy in Florida** and clarifies that the spice is the plant’s rhizomes. citeturn42search1

A UF/IFAS county Extension blog on medicinal plants for Central Florida explicitly includes **ashwagandha** among medicinal plants discussed for the local garden context (useful as a Florida‑relevance signal, though still not a full production guide). citeturn42search2

### Florida integration table as CSV

This table marks **(a)** herbs explicitly appearing in UF/IFAS Florida herb guidance as “Yes (UF/IFAS),” **(b)** herbs discussed in Florida Extension context as “Likely,” and **(c)** others as “Verify” (pending horticultural source ingestion).

```csv
herb_id,zone_9b_growable,status_basis,seasonality_in_FL,microclimate_needs,notes
H006,Yes (UF/IFAS),UFIFAS_GardeningSolutions + UFIFAS_EDIS,perennial,"Warm; moist; partial shade acceptable","Turmeric thrives in warm, moist FL conditions; rhizomes harvested after dieback." 
H007,Yes (UF/IFAS),UFIFAS_EDIS,perennial,"Warm; moist; well-drained","Listed as perennial; propagated by root division; rhizome harvested when mature."
H041,Yes (UF/IFAS),UFIFAS_EDIS,cool-season annual,"Full sun; well-drained","Garlic listed as cool-season annual; harvested when mature."
H042,Yes (UF/IFAS),UFIFAS_EDIS,perennial,"Moisture-tolerant; container recommended","Mint listed as perennial; can spread aggressively (container useful)."
H023,Yes (UF/IFAS),UFIFAS_EDIS,perennial,"Moderate moisture","Lemon balm listed as perennial."
H024,Yes (UF/IFAS),UFIFAS_EDIS,cool-season annual,"Avoid excessive summer humidity","Lavender listed as cool-season annual in this Florida-focused table."
H025,Yes (UF/IFAS),UFIFAS_EDIS,perennial,"Drier soil preference","Rosemary listed as perennial."
H043,Verify,Not in cited UFIFAS Table 1,variable,variable,"Chamomile not present in sampled UF/IFAS table screenshot; verify in full EDIS or other UF/IFAS sources."
H004,Verify,Not in cited UFIFAS Table 1,variable,variable,"Tulsi/holy basil may be grown similarly to basil; verify with UF/IFAS basil guidance."
H001,Likely,UFIFAS_CountyBlog,annual/perennial-like,"Full sun; drier conditions preferred","Ashwagandha included in UF/IFAS county Extension blog; verify cultivation specifics for your county."
H045,Verify,Not in cited UFIFAS Table 1,perennial,humidity-sensitive,"Cardamom listed as perennial in UF/IFAS table; microclimate details vary with locale."
H044,Verify,Not in cited UFIFAS Table 1,cool-season annual,full sun,"Fennel listed as cool-season annual in UF/IFAS table; good FL fit."
H008,Verify,Not in cited UFIFAS Table 1,tree,subtropical tree,"Amla requires orchard-style management; verify cultivar cold tolerance."
H005,Verify,Not in cited UFIFAS Table 1,tree,frost-sensitive,"Neem is tropical/subtropical; verify local regulations and invasive risk before planting."
H012,Verify,Not in UFIFAS table,annual in FL?,needs cooler season,"Astragalus typically prefers cooler climates; verify."
H013,Yes (with method),General cultivation (log/bag),year-round indoor/outdoor,"Shade; humidity control","Reishi can be cultivated; outdoor success depends on substrate + humidity."
H014,Unlikely,Climate constraint,cool climate,requires cold,"Rhodiola is cold-adapted; not a typical FL crop."
H015,Unlikely,Climate constraint,cool climate,requires cold,"Eleuthero is cold-adapted; not a typical FL crop."
H020,Verify,Not in UFIFAS table,perennial in cool climates,heat-sensitive,"Valerian generally prefers cooler summers; verify."
H019,Verify,Not in UFIFAS table,perennial,variable,"St John’s Wort heat/humidity tolerance varies; verify locally."
```

**Citations for the table logic:** UF/IFAS herb list and growth cycles citeturn44view0turn43view0; UF/IFAS turmeric guidance citeturn42search1; UF/IFAS county blog mentioning ashwagandha citeturn42search2; USDA zone definition citeturn42search12.

### Vedic timing for Florida latitude

For an NPU implementation, treat nakshatra/tithi/vara as **astronomical ephemeris fields evaluated in local time** (America/New_York), while biodynamic calendars emphasize sidereal constellations and include “avoid” conditions (nodes/perigee) that can be encoded as constraints. citeturn39view0turn40view0

In practice, **no special “latitude correction” is applied to nakshatras as a category**; rather, local longitude/time zone shifts the clock times of Moon’s transitions. Model this as:  
`moon_sidereal_longitude(t, location) → nakshatra_id` and `sunrise(location,date) → daily anchor` (for muhurta-style rules).

## NPU coherence rules and harvest/planting inference logic

These rules are expressed as IF‑THEN for NPU inference. They combine the user’s requested examples with biodynamic calendar constraints (descending/ascending cycle and “avoid” markers) and nakshatra metadata (e.g., Pushya’s auspicious framing). citeturn39view0turn40view0turn41view0

### Coherence rules as IF‑THEN

```text
RULESET: DOSHA ↔ NAKSHATRA_ELEMENT ↔ CLASS (balance by opposites)

IF dosha_current = VATA
AND nakshatra_element = AIR
THEN astrobotanical_class = EARTH-ROOT (C4)
AND coherence = 0.90
AND herb_shortlist += [Ashwagandha, Shatavari, Astragalus, Codonopsis, Licorice]

IF dosha_current = PITTA
AND season = SHARAD
THEN astrobotanical_class = LUNAR-WATER (C2)
AND coherence = 0.88
AND herb_shortlist += [Shatavari, Amalaki, Brahmi, Licorice, Chrysanthemum]

IF dosha_current = KAPHA
AND season = VASANTA
THEN astrobotanical_class = SOLAR-FIRE (C1)
AND coherence = 0.85
AND herb_shortlist += [Ginger, Turmeric, Garlic, Cinnamon, (Trikatu group if modeled)]

RULESET: BIODYNAMIC CALENDAR CONSTRAINTS (avoid + amplify)

IF lunar_event IN [PERIGEE, NODE]
THEN sowing_allowed = FALSE
AND calendar_penalty = -0.30
(Per biodynamic calendar guidance: perigee and nodes are best avoided for sowing/cultivation.)

IF planetary_aspect_type IN [SQUARE]
THEN growth_modifier = -0.10
IF planetary_aspect_type IN [TRINE, OPPOSITION]
THEN growth_modifier = +0.10

RULESET: HARVEST TIMING (potency heuristics)

IF herb_class = LUNAR-WATER (C2)
AND lunar_phase = FULL_MOON
THEN harvest_potency = 0.95

IF herb_class = SOLAR-FIRE (C1)
AND biodynamic_day_type = FRUIT_SEED
AND vara IN [SUNDAY, TUESDAY]
THEN harvest_potency = 0.92

IF herb_class = EARTH-ROOT (C4)
AND biodynamic_day_type = ROOT
AND lunar_phase = WANING
THEN root_harvest_optimal = 0.90

RULESET: PLANTING (medicinal intention)

IF planting_intention = MEDICINAL
AND herb_class = ETHER-NERVINE (C5)
AND nakshatra = PUSHYA
THEN planting_coherence = 0.97
(Reason: Pushya is described as highly auspicious and nourishing in nakshatra traditions.)
```

**Citations:** biodynamic “avoid perigee/nodes” and aspect heuristics citeturn40view0; sidereal calendar basis and ascending/descending transplanting/harvest framing citeturn39view0; Pushya’s auspicious framing and ruler/deity metadata citeturn41view0.

### Reliability note for coherence rules

These rules are **TRADITIONAL/INTERPRETIVE**. They are compatible with NPU reasoning precisely because they are explicit and testable as *predictions*: you can record outcomes (yield, biomass, secondary metabolite proxies, sensory panels) and learn weights. The scientific literature cautions that lunar‑timing claims often lack reliable causal evidence in plant physiology literature, so NPU should treat timing rules as hypotheses with transparent priors, not facts. citeturn9view0turn36view0turn37view0turn38view2