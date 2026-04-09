# Astrobotany Timing Signals for an NPU Knowledge Graph

## Evidence framework and key takeaways

This research request spans three epistemic layers that often get conflated: (a) **measured biophysical rhythms** in plants and trees (chronobiology / ecophysiology), (b) **agricultural timing systems** (biodynamic calendars; regional farming almanacs), and (c) **Jyotiṣa-based muhurta rules** (nakṣatra/tithi/vāra classifications and auspiciousness). For an NPU Knowledge Graph, the most robust path is to store **all three as distinct claim types** and connect them only through explicitly labeled inference edges (INTERPRETATION or SPECULATIVE), rather than treating traditional timing rules as “validated biology.”

A few high-load findings shape everything else:

Peer-reviewed tree ecophysiology shows **rhythmic tree-stem diameter variation** that can correlate with the **lunisolar tidal acceleration** (i.e., the diurnal/semidiurnal gravitational cycle), including in controlled conditions without daily light cues. citeturn27search0turn26view0turn27search14

This “tidal signature” is **not the same claim** as “full moon makes sap rise” (a synodic phase claim). Lunar **phases are monthly**; lunisolar tides have strong **~12.4 h and ~24.8 h components**, and only modest spring-tide amplification near new/full moons. citeturn25view0turn26view0turn27search0

A critical review in agronomy/plant-science education argues there is **no reliable science-based evidence** (in mainstream textbooks or peer-reviewed plant physiology) to justify **agricultural tasks conditioned by lunar phases** (as commonly taught in popular tradition). citeturn25view0  
**Important nuance for NPU:** this conclusion is best read as “no reliable evidence for *phase-based prescriptions* in common agronomic practice,” not “no lunar-linked biological rhythms exist at all,” because other peer-reviewed chronobiology papers do report lunar/tidal correlations in certain plant signals. citeturn26view0turn27search0turn28view0

Classical Jyotiṣa sources (via Varāhamihira’s **Bṛhat Saṁhitā**, in a modern English translation) explicitly codify **nakṣatra categories** (e.g., Dhruva/Fixed; Tikṣṇa/Dreadful; Ugra/Fierce) and give “fit for” rules; for example, the Bṛhat Saṁhitā states that **Rohiṇī and the three Uttaras** are “Dhruva/Fixed” and suitable for planting trees, sowing seeds, foundations, and other long-lasting undertakings. citeturn15view0turn8view1  
This is a strong **TRADITIONAL attestation**, but it is not a biological mechanism claim.

Florida Zone 9b agriculture is dominated by **heat/humidity and frost windows**, making timing systems most useful when used as **fine-tuning within UF/IFAS-appropriate seasonal windows**, not as replacements for climate-based agronomy. citeturn24search6turn24search2

## Lunar rhythms and plant biology

### Sap flow and lunar phase

Peer-reviewed evidence exists for **tree water-status surrogates** (especially stem-diameter fluctuations) showing correlation with lunisolar tidal acceleration. A well-cited Nature correspondence reported stem diameter fluctuations and a “strong correlation” with tides, interpreted as implicating lunar influence on internal water movement. citeturn27search0 A later peer-reviewed synthesis/analysis across multiple datasets argued that stem diameter time series track the turning points of the **lunisolar tidal profile** and concluded the lunisolar tide can regulate stem diameter dilations under the described conditions. citeturn26view0turn27search14

What this does **not** directly establish:

It does not straightforwardly validate the common agricultural claim “sap flow is higher at full moon and/or new moon.” The best-supported periodicities in these tree measurements are **daily (~24–25 h) and semidiurnal (~12 h) tidal components**, while “full vs new” is a **synodic (~29.5 d) phase framing**. citeturn25view0turn26view0turn27search0

It does not automatically convert to actionable yield improvements for crop sowing or transplanting. The magnitude and agricultural relevance remain uncertain, and major agronomy education-focused reviews argue phase-based prescriptions lack reliable support in plant physiology literature. citeturn25view0

Where “full/new moon” does appear in peer-reviewed discussion is often in relation to **bioelectrical stem potentials** or amplitude modulation in some reported time series (e.g., cited in chronobiology discussions), but those claims are not yet a general agronomic lever. citeturn26view0turn28view0

**NPU modeling implication:** store “tide-linked diurnal/semidiurnal rhythmicity in tree stem signals” as a PEER_REVIEWED biological phenomenon; store “full/new moon sap surge” as TRADITIONAL unless tied to a specific study and phenotype.

### Germination rates by lunar phase

The chronobiology literature contains claims of lunar-linked signals in seeds (e.g., water uptake or metabolic oscillations) and reports that some species show maxima at certain moon times; a peer-reviewed review in *Earth, Moon, and Planets* summarizes reports such as **bean seeds resorbing water** with maxima at intervals related to new/full moon and quadratures, and also notes reports of better germination shortly before new moon in some experiments. citeturn28view0

However, a plant-science education review concludes that **there is no reliable science-based evidence** in mainstream plant physiology textbooks or peer-reviewed plant biology supporting the widespread practice of scheduling agricultural tasks by lunar phases. citeturn25view0

Biodynamic-community reporting (ANECTODAL/OBSERVED rather than mainstream agronomy) describes multi-year trials and claims patterns such as winter rye germinating better when seeded before full moon, yet also reports that later growth can compensate and yields may not differ; it further reports that results generally did **not confirm** the *Working with the Stars* (Maria Thun) calendar recommendations in those comparisons. citeturn35view0

**Practical synthesis for your knowledge graph:**

“Which phase favors germination?” cannot be answered as a universal law. The best-supported stance is: **effects, if present, are species- and context-dependent** and may be small compared with temperature, soil moisture, seed viability, and pathogen pressure. citeturn25view0turn35view0

Claims like “waxing favors leaf; waning favors root” are primarily **TRADITIONAL/ANECTODAL** in the sources reviewed here, and should be encoded with low certainty unless you run local experiments. citeturn29view0turn25view0

### Water uptake and “gravitational” mechanisms in plants

A common traditional mechanism narrative is “Moon gravity pulls water upward in plants.” The Agronomy review argues the Moon’s gravitational acceleration at Earth’s surface is tiny relative to Earth’s gravity and that a phase-based “sap rise” logic is physically inconsistent with the fact that tides have two highs and two lows each day; therefore, if gravity were driving plant water movement in a simple way, the strongest pattern should be **semidiurnal**, not monthly-phasic. citeturn25view0

At the same time, peer-reviewed chronobiology/ecophysiology does report that certain plant/tree signals can synchronize with the lunisolar tidal acceleration profile (again, typically treated as a continuously varying diurnal driver rather than a monthly phase switch). citeturn26view0turn27search0turn27search14

**NPU modeling implication:** distinguish (a) “phase-based” lunar folklore from (b) “continuous tidal acceleration” chronobiology; do not merge them into a single “Moon effect” node.

### Moisture in wood and “moon timber” traditions

“Moon wood” traditions claim that felling at certain lunar phases changes wood moisture and stability. Peer-reviewed work is mixed:

A field experiment on Norway spruce and sweet chestnut drying behavior reported **slight but significant variations with lunar periodicities** (synodic and sidereal) alongside seasonal trends, raising questions about rhythmic wood–water relations. citeturn34view0

A forestry products analysis of 60 oaks felled across the four lunar phases during one lunar period reported **no significant differences** in humidity, specific weight, or shrinkage (as summarized in an accessible abstract record). citeturn32search9

**NPU stance:** encode “moon wood quality” as a contested domain: PEER_REVIEWED studies exist both suggesting small effects and suggesting null results; local species, felling season, and drying/storage conditions are likely dominant confounders. citeturn34view0turn32search9

## Biodynamic calendars and the four “root/leaf/flower/fruit” categories

### What biodynamic calendars claim

Modern biodynamic calendars commonly map the Moon’s passage through zodiac constellations (earth/water/air/fire elements) to plant organ emphasis: **earth→root, water→leaf, air→flower, fire→fruit/seed**. A widely used biodynamic calendar publication describes this mapping and attributes its development to Maria Thun’s mid-20th-century observations, claiming “enhanced root growth” when sowing with Moon in earth constellations, etc. citeturn29view0

This same biodynamic calendar source also repeats the more general tradition that full moon enhances germination and that plant metabolism and water absorption peak around full moon—claims it presents as “confirmed by scientific studies,” though without presenting the underlying peer-reviewed citations in that usage guide. citeturn29view0

### What is scientifically supported vs tradition

A critical review of lunar influence claims in agriculture concludes that popular “task-by-lunar-phase” practices and many biodynamic lunar claims have **no scientific backing** in plant-physiology texts or peer-reviewed plant science, and argues physics does not support a causal phase→plant response relationship in the simplified way commonly taught. citeturn25view0

In contrast, peer-reviewed chronobiology/ecophysiology papers do support that plants/trees can show synchrony with lunisolar tidal signals under some conditions, but this does not validate the biodynamic calendar’s specific **zodiac element→plant organ** prescriptions as an agronomic rule. citeturn26view0turn27search0turn25view0

Biodynamic-community reporting acknowledges that controlled multi-year experiments often detect strong responses to **primary growth factors** (warmth, moisture, day length) and that lunar-rhythm effects may only appear after statistical detrending; it also reports that findings generally did not confirm Thun calendar advice in those trials, while still suggesting “different crops respond differently.” citeturn35view0

### Kolisko and Thun

In the biodynamic literature stream, Lilly (Lili) Kolisko is frequently cited as having run experiments suggesting better yields/quality when sowing before full moon than before new moon; later biodynamic reporting also claims Thun observed repeating “root/leaf/flower/fruit” types when sowing radishes across a sidereal lunar month. citeturn35view0

From an NPU perspective, treat “Kolisko/Thun findings” as **ANECTODAL/OBSERVED** unless you can link to their original experimental records and independently evaluate design/replication and statistical handling. The sources accessed here contain secondary summaries and explicit notes that many subsequent investigations did not verify calendar claims straightforwardly. citeturn35view0turn25view0

### Bridging biodynamic categories to Vedic nakshatra agriculture

Biodynamic categories depend on the Moon in **zodiac constellations/signs** (element mapping), while Jyotiṣa agriculture often depends on **nakṣatra categories** (Dhruva/Mṛdu/Cara/Kṣipra/Ugra/Tikṣṇa etc.) plus tithi and weekday. The Bṛhat Saṁhitā provides explicit nakṣatra classifications and use-cases (e.g., Dhruva suited for sowing and planting trees). citeturn15view0turn8view1

A workable NPU bridge (INTERPRETATION) is:

derive a nakṣatra’s **dominant zodiac element** from its ecliptic segment (to compare with biodynamic element categories), while separately tracking its **muhurta quality class** (Dhruva/Mṛdu/…); treat agreement as “coherence,” not validation.

## Nakshatra-based agricultural timing from attested sources

### Strong textual anchor: Bṛhat Saṁhitā on nakshatra properties

In the accessible English translation of Varāhamihira’s Bṛhat Saṁhitā (M. Ramakrishna Bhat), Chapter XCVIII (“Functions and Properties of the Asterisms”) lists presiding deities and then classifies nakṣatras into functional groups, including:

Dhruva/Fixed: Rohiṇī + the three Uttaras; suited for “planting of trees,” laying foundations, sowing seeds, and other permanent things. citeturn15view0

Tikṣṇa/Dāruṇa (Dreadful): Mūla, Ārdrā, Jyeṣṭhā, Āśleṣā; suited for aggressive/destructive acts (attacks, imprisoning, etc.). citeturn15view0

Ugra/Fierce: Bharaṇī, Maghā, and the three Pūrvās; similarly oriented to destructive aims. citeturn15view0

Kṣipra/Swift: Hasta, Aśvinī, Puṣya (and Abhijit); suited for quick activities including travel and medical treatment. citeturn15view0

Cara/Temporary: Śravaṇa, Dhaniṣṭhā, Śatabhiṣaj, Punarvasu, Svātī; suited for ephemeral things. citeturn15view0

The same translation also contains, in its tree-treatment section, a direct enumeration of nakṣatras recommended “by seers” for **planting trees**: the three Uttaras, Rohiṇī, Anurādhā, Citrā, Mṛgaśīrṣā, Revatī, Mūla, Viśākhā, Puṣya, Śravaṇa, Aśvinī, Hasta. citeturn8view1

For NPU, these two passages are unusually actionable because they are (a) explicit, and (b) already structured as categories and lists.

### How to represent “element” and “deity” without overclaiming biology

The Bṛhat Saṁhitā provides the **presiding deities** list for the nakṣatras in the same chapter as the functional groupings. citeturn15view0 That is sufficient for “nakshatra_deity” fields and for rule logic that references deity families (e.g., “Bṛhaspati family”).

The “element of each nakshatra” is not standardized in the same way across traditions; the most consistent bridge to biodynamic categories is **derived from the zodiac element** (fire/earth/air/water) corresponding to the Moon’s location along the ecliptic. This mapping should be stored as **INTERPRETATION/DERIVED**, not “attested.” citeturn21search2turn29view0

### Attribute quality classes to farming actions

Because Bṛhat Saṁhitā’s functions are not strictly agricultural (they are general muhurta), an NPU system can define a mapping layer:

Dhruva → high coherence for “long-term establishment” tasks (orchard planting, perennials, timber trees, major grafts)

Mṛdu/Gentle → high coherence for “gentle growth” tasks (transplanting, ornamentals, medicinal herbs)

Cara/Temporary and Kṣipra/Swift → coherence for “short-cycle” tasks (greens, mowing/harvest, quick successions)

Ugra/Tikṣṇa → coherence for “disruptive” tasks (clearing, pruning hard, pest removal, turning compost, heavy earthworks), and low coherence for sowing/transplanting

This is an INTERPRETATION layer sitting on top of attested categories. citeturn15view0turn8view1

## Graha–plant correspondences with modern phytochemistry parallels

### Status of the “Navagraha plant list”

A widely repeated Navagraha plant set in modern practice associates: Surya–Arka (*Calotropis*), Chandra–Palāśa (*Butea monosperma*), Mangala–Khadira (*Acacia catechu*), Budha–Apāmārga (*Achyranthes aspera*), Guru–Aśvattha (*Ficus religiosa*), Śukra–Udumbara (*Ficus racemosa*), Śani–Śamī (*Prosopis cineraria*), Rāhu–Dūrvā (*Cynodon dactylon*), Ketu–Darbha (*Imperata cylindrica*). citeturn22search4

In the sources reviewed here, this list is best treated as **TRADITIONAL (widely attested in modern “vatika” practice)** unless a primary classical textual anchor is identified for each pairing.

### Modern research parallels: what is reasonably supported

Surya → Arka (*Calotropis procera* / *C. gigantea*). Modern phytochemistry reviews describe *Calotropis procera* as rich in diverse compounds including **cardenolides** (a class that includes **cardiac glycosides**) along with other phytochemicals. This provides a plausible modern parallel to “heart/circulation potency” narratives, but also flags toxicity risk. citeturn36search0

Guru (Jupiter) → Aśvattha (*Ficus religiosa*). An Elsevier ethnopharmacology review synthesizes traditional uses, phytochemistry, and pharmacology for *F. religiosa*, supporting that it has documented bioactivities (with the usual caveat: activity evidence ranges from in vitro to in vivo and is not identical to clinical proof). citeturn37search0

Śukra (Venus) → Udumbara (*Ficus racemosa*). Reviews discuss phytochemical constituents and pharmacological activities for *F. racemosa*, supporting at least a modern “bioactive plant” parallel (again, not necessarily clinical confirmation of the astrological body-system assignment). citeturn37search9

Ketu → Darbha (*Imperata cylindrica*). A peer-reviewed MDPI review in *Molecules* surveys phytochemistry and pharmacology of *I. cylindrica*, supporting that it contains bioactives and is studied for diverse activities. citeturn38search0

Rāhu → Dūrvā (*Cynodon dactylon*). A systematic review summarizes pharmacognosy/phytochemistry/pharmacology of *C. dactylon*; quality of evidence varies by endpoint, but it supports the existence of multiple studied bioactivities. citeturn37search3

For Mangala/ Budha/ Śani plants, accessible reviews exist but often in variable-quality venues; treat “active compounds” as “known from phytochemistry literature,” and treat “body system governed” as TRADITIONAL unless you attach a classical Ayurvedic/Jyotiṣa source.

## Permaculture integration and Florida Zone 9b implementation notes

### Integrating “Vedic timing” with permaculture zones without breaking agronomy

Permaculture zone design (Zone 0–5) is primarily about **frequency of access and intensity of management** (Zone 1 close to the home; Zone 5 wild). citeturn24search1turn24search30turn24search24 Vedic timing can be integrated as a **scheduling overlay**:

Zone 1 (daily/near-home): use nakṣatra classes to time quick tasks (Kṣipra/Cara) and avoid overfitting; examples: salad greens successions, harvesting herbs for immediate use.

Zone 2 (orchard/food forest): reserve Dhruva and gentle nakṣatras for planting/transplanting trees and long-lived perennials, consistent with Bṛhat Saṁhitā’s “planting trees” emphasis for Dhruva and the enumerated planting list. citeturn15view0turn8view1

Zones 3–4: use Ugra/Tikṣṇa for disruptive maintenance tasks that permaculture already bundles periodically (copicing, clearing, major pruning, earth shaping), treating “coherence” as a cultural-ecological workflow tool rather than biology. citeturn15view0

### Soil building and lunar/nakṣatra timing

Because Florida gardening success hinges on seasonality, prioritize UF/IFAS seasonal guidance (what can be planted when) and then choose “high coherence” days inside that window. UF/IFAS notes vegetables can be grown year-round in Florida with attention to planting dates, and provides detailed guides by region. citeturn24search6turn24search2

Practical Zone 9b rhythm (Central Florida as proxy):

Fall (roughly Sep–Nov): prime for cool-season beds; UF/IFAS county guidance emphasizes soil prep and compost incorporation in fall garden start-up. citeturn24search18

Winter (Dec–Feb): cool-season crops; protect warm-season transplants from cold snaps. citeturn24search2

Spring (Feb–Apr): long productive planting window before high heat; UF/IFAS notes tomatoes can be planted early to “beat the heat,” but require protection during cold snaps. citeturn24search2

Summer (May–Aug): heat/humidity/pests dominate; focus on heat-tolerant crops, mulching, irrigation management, and soil cover rather than heavy transplanting of cool-season plants. citeturn24search6

### South Asian “food forest” parallels

Classical South Asian agriculture texts are typically not framed as “food forest permaculture” in modern terms, but they do include **tree-planting timing, orchard/garden management, and “treatment of trees”** (vṛkṣāyurveda-like material) within broader civilizational planning. The Bṛhat Saṁhitā translation explicitly discusses tree treatment and gives nakṣatra timing for planting trees. citeturn8view1turn14view3

For NPU, the most defensible mapping is: treat “food forest traditions” as “orchard + agroforestry + sacred grove (vana) practices,” and represent them as TRADITIONAL design patterns rather than claiming a direct one-to-one with modern permaculture doctrine.

## CSV outputs and NPU coherence rules

### Source handles used inside CSVs

The `source` columns below use short handles; this paragraph binds them to cited sources:

BS_Bhat_P2_XCVIII_Deities_And_Nakshatra_Types → Bṛhat Saṁhitā Part II, Chapter XCVIII lines giving deities and category definitions. citeturn15view0  
BS_Bhat_P1_LV_TreePlanting_NakshatraList → Bṛhat Saṁhitā Part I tree-treatment section enumerating nakṣatras suitable for planting trees. citeturn8view1  
BD_StellaNatura_RootLeafFlowerFruit → biodynamic calendar explanation of element→plant-part mapping and claims of Thun’s findings. citeturn29view0  
BD_Spiess_2000_LunarRhythmsAndPlants → biodynamic journal article summarizing experiments and reporting mixed/weak confirmation of Thun-type claims. citeturn35view0  
SCI_Mayoral_2020_AgronomyReview → Agronomy (MDPI) review concluding no reliable evidence for lunar-phase-conditioned plant physiology/agronomy practice. citeturn25view0  
SCI_Zuercher_1998_Nature_StemTides → Nature correspondence on stem diameter correlation with tides. citeturn27search0  
SCI_Fisahn_2018_AoB_TidesWithinTrees → Annals of Botany viewpoint synthesizing and re-evaluating stem diameter vs tidal acceleration. citeturn26view0  
SCI_Barlow_2010_Protoplasma_StemTides → Protoplasma article abstract on stem diameter fluctuations with lunar tides. citeturn27search14  
SCI_Zuercher_2010_Trees_MoonWood → Trees (Springer) abstract reporting slight but significant lunar periodicities in wood drying behavior. citeturn34view0  
SCI_OakFelling_LunarPhase_Null → abstract record indicating no significant phase effect on oak wood humidity/weight/shrinkage. citeturn32search9  
TRAD_NakshatraTrees_IndiaBiodiversity → “Trees representing 27 Astrological star (birth stars)” list with Sanskrit names and botanical names. citeturn11view0  
SCI_Nakshatravan_Review_2022_SAJB → South African Journal of Botany review of nakshatravan trees, compounds and medicinal properties. citeturn23view0  
FL_UFIFAS_VegGuide → UF/IFAS Florida Vegetable Gardening Guide. citeturn24search6  
FL_UFIFAS_CentralCalendar → UF/IFAS Central Florida Gardening Calendar PDF. citeturn24search2  
PERMA_Zones_OregonState + PERMA_Assoc_Zoning → permaculture zone explanations. citeturn24search1turn24search30  
PHYT_Calotropis_Review_SAJB_2025 → review on *Calotropis procera* phytochemistry/pharmacology. citeturn36search0  
PHYT_FicusReligiosa_Review_JEthno_2011 → review on *Ficus religiosa* phytochemistry/pharmacology. citeturn37search0  
PHYT_FicusRacemosa_Review_TandF_2020 → review on *Ficus racemosa* constituents and activities. citeturn37search9  
PHYT_Imperata_Review_Molecules_2021 → MDPI Molecules review on *Imperata cylindrica*. citeturn38search0  
PHYT_Cynodon_Review_2014 → systematic review on *Cynodon dactylon*. citeturn37search3  
PHYT_Prosopis_Study_SciDirect_2023 → study on *Prosopis cineraria* phyto-constituents and bioactivity models. citeturn37search10  
TRAD_NavagrahaPlantList_Modern → modern traditional Navagraha plant list. citeturn22search4  

### Lunar and plant biology evidence CSV

```csv
claim_id,topic,organism_or_material,measured_variable,periodicity_reported,key_result_short,evidence_label,attestation_status,source
LUN001,Stem water-status rhythms,Picea abies (spruce),stem diameter fluctuations,tidal-linked daily rhythms,"Stem diameters fluctuate and correlate with timing/strength of tides; interpreted as lunar influence on internal water flow",PEER_REVIEWED,ATTESTED_IN_JOURNAL,SCI_Zuercher_1998_Nature_StemTides
LUN002,Stem water-status rhythms,multiple tree species (meta-analysis),stem diameter time series vs lunisolar tidal acceleration,~24–25h turning-point synchrony,"Re-evaluation indicates synchrony between turning points of tidal acceleration and stem diameter extension turning points",PEER_REVIEWED,ATTESTED_IN_JOURNAL,SCI_Fisahn_2018_AoB_TidesWithinTrees
LUN003,Stem water-status rhythms,multiple tree datasets,stem diameter vs tidal acceleration,~24.8h lunar-day signal,"Article reports stem diameter fluctuations with lunar tides across datasets; also suggests possible geomagnetic co-variation",PEER_REVIEWED,ATTESTED_IN_JOURNAL,SCI_Barlow_2010_Protoplasma_StemTides
LUN004,Phase-based lunar agriculture claims,General agriculture (review),literature survey,NA,"Review concludes no reliable science-based evidence for lunar-phase-conditioned plant physiology/agronomy tasks; physics also does not support a simple phase→plant causal chain",PEER_REVIEWED,ATTESTED_IN_JOURNAL,SCI_Mayoral_2020_AgronomyReview
LUN005,Seed/seedling lunar periodicity (reported),multiple plants incl. beans,seed water uptake / metabolism,reported synodic/semilunar links,"Review summarizes reports of bean seed water uptake maxima near new/full/quadrature and other lunar-linked metabolic oscillations; stresses exo-endo rhythm complexity",PEER_REVIEWED_REVIEW,ATTESTED_IN_JOURNAL,SCI_Schad_2001_LunarInfluenceOnPlants
LUN006,Wood quality vs lunar felling,Norway spruce + sweet chestnut,water loss,shrinkage,relative density,synodic+sidereal periodicities reported,"Large field experiment reports slight but significant lunar periodicities in drying behavior alongside seasonal trends",PEER_REVIEWED,ATTESTED_IN_JOURNAL,SCI_Zuercher_2010_Trees_MoonWood
LUN007,Wood quality vs lunar felling (null),Quercus humilis (oak),humidity,specific weight,shrinkage,NA,"60 oaks felled across four lunar phases: no significant differences in tested properties (one-lunar-period sample)",PEER_REVIEWED_ABSTRACT_ONLY,ATTESTED_IN_JOURNAL,SCI_OakFelling_LunarPhase_Null
LUN008,Biodynamic phase and calendar claims (mixed results),field crops (rye, carrots, etc.),germination,yield,storage quality,full/new,perigee/high-low (reported),NA,"Biodynamic report describes multi-year trials where lunar effects were small and often required detrending; results generally did not confirm Thun calendar advice",ANECDOTAL_OBSERVED,SECONDARY_SUMMARY,BD_Spiess_2000_LunarRhythmsAndPlants
```

### Nakshatra × biology bridge CSV

Notes for this CSV:

`element_from_rasi` is **DERIVED** (INTERPRETATION) from the standard sidereal zodiac element mapping used in biodynamic calendars (earth/water/air/fire). citeturn29view0turn21search2  
`planting_quality` is mapped from Bṛhat Saṁhitā nakṣatra classes (ATTESTED) into gardening actions (INTERPRETATION). citeturn15view0turn8view1  

```csv
nakshatra_id,name_iast,name_sanskrit,presiding_deity,mūhurta_class_from_brihat_samhita,element_from_rasi,biodynamic_equivalent,planting_quality,best_for,avoid_for,traditional_reasoning,scientific_parallel,claim_label,attestation_status,source,florida_zone_9b_notes
1,Aśvinī,अश्विनी,Divine Physicians (Aśvinī-kumāras),KSHIPRA_SWIFT,fire,FRUIT_SEED,good,quick sowings; medicinal herb harvest; graft quick-start,major pruning for removal,"Swift nakshatra suited for quick works; also included in tree-planting nakshatra list",No direct plant-biology match; treat as scheduling heuristic,INTERPRETATION,ATTESTED_IN_BS,BS_Bhat_P2_XCVIII_Deities_And_Nakshatra_Types;BS_Bhat_P1_LV_TreePlanting_NakshatraList,"Use inside UF/IFAS planting windows; good for quick salad successions in fall/spring"
2,Bharaṇī,भरणी,Yama (God of Death),UGRA_FIERCE,fire,FRUIT_SEED,avoid,clearing; pest removal; compost turning,sowing/transplanting,"Fierce nakshatra; used for destructive/forceful acts",No direct plant-biology match; coherence via workflow only,INTERPRETATION,ATTESTED_IN_BS,BS_Bhat_P2_XCVIII_Deities_And_Nakshatra_Types,"Best used for bed clearing before fall planting (late Aug/Sep) rather than sowing"
3,Kṛttikā,कृत्तिका,Agni (Fire),MIXED,fire/EARTH,FRUIT_SEED (mixed),neutral,balanced tasks; avoid over-optimization,high-sensitivity transplants,"Mixed results per Brihat Samhita category",No direct plant-biology match,INTERPRETATION,ATTESTED_IN_BS,BS_Bhat_P2_XCVIII_Deities_And_Nakshatra_Types,"Use as flexible day when weather forces action (rain/frost)"
4,Rohiṇī,रोहिणी,Brahmā / Creator,DHRUVA_FIXED,earth,ROOT,excellent,tree planting; perennial establishment; seed saving,destructive earthworks,"Dhruva/fixed: suitable for planting trees and sowing seeds; explicitly stated",If modeling “long-term establishment,” this is high-confidence tradition; exclude mechanistic claims,TRADITIONAL,ATTESTED_IN_BS,BS_Bhat_P2_XCVIII_Deities_And_Nakshatra_Types;BS_Bhat_P1_LV_TreePlanting_NakshatraList,"Ideal for fruit tree planting in winter (Dec–Feb) when UF/IFAS recommends deciduous fruit planting"
5,Mṛgaśīrṣā,मृगशीर्ष,Chandra/Soma (Moon),MRIDU_GENTLE,earth,ROOT,good,transplanting; nursery work; gentle prunes,heavy clearing,"Gentle class in Brihat Samhita scheme; also in tree-planting list",No direct plant-biology match,INTERPRETATION,ATTESTED_IN_BS,BS_Bhat_P2_XCVIII_Deities_And_Nakshatra_Types;BS_Bhat_P1_LV_TreePlanting_NakshatraList,"Good for transplanting lettuce/brassicas in fall/winter"
6,Ārdrā,आर्द्रा,Rudra,TIKSHNA_DREADFUL,air,FLOWER,avoid,hard pruning; breaking pest cycles;sowing/transplanting,"Tikshna/dreadful: suited for harsh acts",No direct plant-biology match,INTERPRETATION,ATTESTED_IN_BS,BS_Bhat_P2_XCVIII_Deities_And_Nakshatra_Types,"Use for removing diseased plants during humid season"
7,Punarvasu,पुनर्वसु,Aditi,CARA_TEMPORARY,air,FLOWER,good,short-cycle crops; light cultivation,orchard planting,"Chara/temporary: beneficial for ephemeral things",No direct plant-biology match,INTERPRETATION,ATTESTED_IN_BS,BS_Bhat_P2_XCVIII_Deities_And_Nakshatra_Types,"Good for succession sowing greens/herbs in shoulder seasons"
8,Puṣya,पुष्य,Jupiter (Bṛhaspati),KSHIPRA_SWIFT,water,LEAF,good,medicinal herbs; leafy crops; quick starts,major removals,"Swift; also sacred to Guru; in tree-planting list",No direct plant-biology match,INTERPRETATION,ATTESTED_IN_BS,BS_Bhat_P2_XCVIII_Deities_And_Nakshatra_Types;BS_Bhat_P1_LV_TreePlanting_NakshatraList,"Good for compost tea application / foliar sprays in cool season"
9,Āśleṣā,आश्लेषा,Serpent (Nāga),TIKSHNA_DREADFUL,water,LEAF,avoid,pest suppression; invasive removal,sowing/transplanting,"Tikshna/dreadful",No direct plant-biology match,INTERPRETATION,ATTESTED_IN_BS,BS_Bhat_P2_XCVIII_Deities_And_Nakshatra_Types,"Time deep sanitation (remove pest habitat) before spring planting"
10,Maghā,मघा,Pitṛs (Ancestors),UGRA_FIERCE,fire,FRUIT_SEED,avoid,clearing/coppice; heavy earthwork,sowing/transplanting,"Ugra/fierce",No direct plant-biology match,INTERPRETATION,ATTESTED_IN_BS,BS_Bhat_P2_XCVIII_Deities_And_Nakshatra_Types,"Use for tree pruning/coppice in dormant season"
11,Pūrvaphālgunī,पूर्वाफाल्गुनी,Bhaga,UGRA_FIERCE,fire,FRUIT_SEED,avoid,hard pruning; removal,planting new orchards,"Ugra/fierce",No direct plant-biology match,INTERPRETATION,ATTESTED_IN_BS,BS_Bhat_P2_XCVIII_Deities_And_Nakshatra_Types,"Use for removing spent summer crops"
12,Uttaraphālgunī,उत्तराफाल्गुनी,Aryaman,DHRUVA_FIXED,earth,ROOT,excellent,orchard planting; perennial beds; seed storage,clear-and-burn style clearing,"Dhruva/fixed",As tradition, aligns with “long-term establishment”,TRADITIONAL,ATTESTED_IN_BS,BS_Bhat_P2_XCVIII_Deities_And_Nakshatra_Types;BS_Bhat_P1_LV_TreePlanting_NakshatraList,"Excellent for planting perennial greens in fall"
13,Hasta,हस्त,Savitar (Sun aspect),KSHIPRA_SWIFT,earth,ROOT,good,quick transplants; tool work; harvesting,starting long-lived trees if possible,"Swift; also listed for tree planting",No direct plant-biology match,INTERPRETATION,ATTESTED_IN_BS,BS_Bhat_P2_XCVIII_Deities_And_Nakshatra_Types;BS_Bhat_P1_LV_TreePlanting_NakshatraList,"Good for rapid bed turnover in spring"
14,Citrā,चित्रा,Tvaṣṭṛ,MRIDU_GENTLE,air,FLOWER,good,ornamentals; flower crops; gentle transplants,major clearing,"Gentle class; also listed for tree planting",No direct plant-biology match,INTERPRETATION,ATTESTED_IN_BS,BS_Bhat_P2_XCVIII_Deities_And_Nakshatra_Types;BS_Bhat_P1_LV_TreePlanting_NakshatraList,"Useful for pollinator plantings during warm season"
15,Svātī,स्वाती,Vāyu,CARA_TEMPORARY,air,FLOWER,good,short-cycle; ventilation/wind-oriented tasks,long-lived planting,"Temporary/ephemeral",No direct plant-biology match,INTERPRETATION,ATTESTED_IN_BS,BS_Bhat_P2_XCVIII_Deities_And_Nakshatra_Types,"Time trellising and airflow improvements before summer humidity"
16,Viśākhā,विशाखा,Indra-Agni,MIXED,fire,FRUIT_SEED,neutral,balanced; avoid major decisions,high-sensitivity sowing,"Mixed results category",No direct plant-biology match,INTERPRETATION,ATTESTED_IN_BS,BS_Bhat_P2_XCVIII_Deities_And_Nakshatra_Types,"Use as buffer day"
17,Anurādhā,अनुराधा,Mitra,MRIDU_GENTLE,water,LEAF,good,transplanting; social/guild planting; tree planting support,hard clearing,"Gentle; also listed for tree planting",No direct plant-biology match,INTERPRETATION,ATTESTED_IN_BS,BS_Bhat_P2_XCVIII_Deities_And_Nakshatra_Types;BS_Bhat_P1_LV_TreePlanting_NakshatraList,"Good for establishing understory layers in food forest"
18,Jyeṣṭhā,ज्येष्ठा,Indra,TIKSHNA_DREADFUL,water,LEAF,avoid,pest/disease interventions,sowing/transplanting,"Tikshna/dreadful",No direct plant-biology match,INTERPRETATION,ATTESTED_IN_BS,BS_Bhat_P2_XCVIII_Deities_And_Nakshatra_Types,"Good for disease cleanup after heavy rains"
19,Mūla,मूल,Nirṛti,TIKSHNA_DREADFUL,fire,FRUIT_SEED,avoid,uprooting; deep clearing; bed reset,sowing/transplanting,"Tikshna/dreadful; uprooting resonance matches semantics",No direct plant-biology match,INTERPRETATION,ATTESTED_IN_BS,BS_Bhat_P2_XCVIII_Deities_And_Nakshatra_Types,"Use for removing invasive roots in Zone 3–4"
20,Pūrvāṣāḍhā,पूर्वाषाढा,Āpas (Waters),UGRA_FIERCE,fire,FRUIT_SEED,avoid,heavy interventions,planting trees,"Ugra/fierce",No direct plant-biology match,INTERPRETATION,ATTESTED_IN_BS,BS_Bhat_P2_XCVIII_Deities_And_Nakshatra_Types,"Schedule major bed overhauls"
21,Uttarāṣāḍhā,उत्तराषाढा,Viśve-devas,DHRUVA_FIXED,fire,FRUIT_SEED,excellent,long-term plantings; seed saving,unnecessary disruption,"Dhruva/fixed",Tradition aligns with “durable result” planning,TRADITIONAL,ATTESTED_IN_BS,BS_Bhat_P2_XCVIII_Deities_And_Nakshatra_Types,"Good for planting long-season fruiting crops early spring"
22,Śravaṇa,श्रवण,Viṣṇu,CARA_TEMPORARY,earth,ROOT,good,routine maintenance; short-cycle,permanent orchard installation,"Temporary/ephemeral",No direct plant-biology match,INTERPRETATION,ATTESTED_IN_BS,BS_Bhat_P2_XCVIII_Deities_And_Nakshatra_Types,"Good for routine mulching and irrigation tuning"
23,Dhaniṣṭhā,धनिष्ठा,Vasus,CARA_TEMPORARY,earth,ROOT,good,harvest/storage tasks; compost distribution,planting trees,"Temporary/ephemeral",No direct plant-biology match,INTERPRETATION,ATTESTED_IN_BS,BS_Bhat_P2_XCVIII_Deities_And_Nakshatra_Types,"Useful for distributing mulch before heat spikes"
24,Śatabhiṣaj,शतभिषज्,Varuṇa,CARA_TEMPORARY,water,LEAF,good,water management; irrigation; wetland plants,perennial transplantation in soggy soils,"Temporary/ephemeral; Varuna water resonance",No direct plant-biology match,INTERPRETATION,ATTESTED_IN_BS,BS_Bhat_P2_XCVIII_Deities_And_Nakshatra_Types,"Good for irrigation audits and rainwater capture tweaks"
25,Pūrvabhādrapadā,पूर्वभाद्रपदा,Ajaikapād,UGRA_FIERCE,air,FLOWER,avoid,clearing; strong pruning,sowing/transplanting,"Ugra/fierce",No direct plant-biology match,INTERPRETATION,ATTESTED_IN_BS,BS_Bhat_P2_XCVIII_Deities_And_Nakshatra_Types,"Use for storm-prep pruning before hurricane season"
26,Uttarabhādrapadā,उत्तरभाद्रपदा,Ahirbudhnya,DHRUVA_FIXED,air,FLOWER,excellent,perennial establishment; long-term projects,destructive interventions,"Dhruva/fixed",Tradition aligns with stable establishment,TRADITIONAL,ATTESTED_IN_BS,BS_Bhat_P2_XCVIII_Deities_And_Nakshatra_Types,"Good for planting windbreak/support species"
27,Revatī,रेवती,Pūṣan,MRIDU_GENTLE,water,LEAF,good,transplanting; finishing; gentle harvest,major clearing,"Gentle; also listed for tree planting",No direct plant-biology match,INTERPRETATION,ATTESTED_IN_BS,BS_Bhat_P2_XCVIII_Deities_And_Nakshatra_Types;BS_Bhat_P1_LV_TreePlanting_NakshatraList,"Good for transplanting in cooler parts of day; avoid heat stress"
```

### Graha × plant correspondences CSV

```csv
graha_id,graha_name,primary_plant_sanskrit,primary_plant_common,primary_plant_latin,secondary_plants,element_correspondence_traditional,body_system_governed_traditional,active_compounds_known,traditional_use,modern_research_parallel,attestation_status,claim_labels,source
1,Surya (Sun),Arka,Milkweed/Calotropis,Calotropis procera,"Calotropis gigantea (variant by region)",fire,"heart/vitality (traditional astro-herbalism framing)","cardenolides (cardiac glycosides class) + diverse phytochemicals","used in traditional medicine; also ritual plant in some traditions","Modern review reports cardenolides and other compounds; cardiac-glycoside class provides plausible mechanistic parallel (with toxicity caveat)",TRADITIONAL_LIST_PLUS_PEER_REVIEWED_PHYTOCHEM,TRADITIONAL|PEER_REVIEWED,TRAD_NavagrahaPlantList_Modern;PHYT_Calotropis_Review_SAJB_2025
2,Chandra (Moon),Palāśa,Flame-of-the-forest,Butea monosperma,"—",water,"fertility/nourishment (traditional framing)","flavonoids (e.g., butein/butrin reported in reviews)","traditional multi-use medicinal tree; ritual importance","Modern reviews summarize phytochemistry and pharmacology (venue quality varies); treat as indicative not clinical proof",TRADITIONAL_LIST_PLUS_SECONDARY_REVIEWS,TRADITIONAL|OBSERVED,TRAD_NavagrahaPlantList_Modern;turn10search1;turn36search1
3,Mangala (Mars),Khadira,Catechu/Khair,Acacia catechu,"—",fire,"blood/heat/inflammation (traditional framing)","catechin/epicatechin and other polyphenols reported","astringent; oral/skin uses in traditional medicine","Reviews list major polyphenols; plausible anti-inflammatory/antioxidant parallels",TRADITIONAL_LIST_PLUS_SECONDARY_REVIEWS,TRADITIONAL|OBSERVED,TRAD_NavagrahaPlantList_Modern;turn36search2
4,Budha (Mercury),Apāmārga,Prickly chaff flower,Achyranthes aspera,"—",air,"nervous system/speech (traditional framing)","ecdysterone, oleanolic acid and other constituents reported in reviews","used in diverse folk/Ayurvedic contexts","Review summarizes phytochemistry and uses; evidence strength variable",TRADITIONAL_LIST_PLUS_SECONDARY_REVIEWS,TRADITIONAL|OBSERVED,TRAD_NavagrahaPlantList_Modern;turn36search3
5,Guru (Jupiter),Aśvattha,Peepal/Sacred fig,Ficus religiosa,"—",ether/air,"respiratory/metabolic (traditional framing)","multiple phytochemicals summarized in ethnopharmacology review","widely venerated; traditional medicinal uses","Elsevier review synthesizes phytochemistry/pharmacology and traditional uses",TRADITIONAL_LIST_PLUS_PEER_REVIEWED_REVIEW,TRADITIONAL|PEER_REVIEWED,TRAD_NavagrahaPlantList_Modern;PHYT_FicusReligiosa_Review_JEthno_2011
6,Shukra (Venus),Udumbara,Cluster fig,Ficus racemosa,"—",water,"reproductive/urinary (traditional framing)","diverse phytochemicals summarized in reviews","traditional uses across systems","Review literature summarizes constituents and activities (evidence varies by endpoint)",TRADITIONAL_LIST_PLUS_SECONDARY_REVIEW,TRADITIONAL|OBSERVED,TRAD_NavagrahaPlantList_Modern;PHYT_FicusRacemosa_Review_TandF_2020
7,Shani (Saturn),Śamī,Khejri/Prosopis,Prosopis cineraria,"—",air/earth,"bones/structure/constraint (traditional framing)","bioactive profiling and pharmacology endpoints reported in studies","agroforestry + traditional medicine uses","Study-level evidence exists on constituents and bioactivity models",TRADITIONAL_LIST_PLUS_PEER_REVIEWED_STUDY,TRADITIONAL|PEER_REVIEWED,TRAD_NavagrahaPlantList_Modern;PHYT_Prosopis_Study_SciDirect_2023
8,Rahu,Dūrvā,Bermuda grass,Cynodon dactylon,"—",air,"toxins/obscuration (traditional framing)","summarized multi-compound phytochemistry in review","ritual grass; folk uses","Systematic review summarizes phytochemistry and pharmacology",TRADITIONAL_LIST_PLUS_SECONDARY_REVIEW,TRADITIONAL|OBSERVED,TRAD_NavagrahaPlantList_Modern;PHYT_Cynodon_Review_2014
9,Ketu,Darbha,Cogon grass/Imperata,Imperata cylindrica,"Kusha/Desmostachya bipinnata sometimes used regionally",earth,"detachment/clearing (traditional framing)","review summarizes phytochemistry and pharmacology","ritual grass; traditional medicinal uses","MDPI review summarizes botanical/phytochemical/pharmacological studies",TRADITIONAL_LIST_PLUS_PEER_REVIEWED_REVIEW,TRADITIONAL|PEER_REVIEWED,TRAD_NavagrahaPlantList_Modern;PHYT_Imperata_Review_Molecules_2021
```

### Sacred plant database CSV

This dataset uses the IndiaBiodiversity list as the baseline for the **27 nakshatra-associated plants** and flags where that source itself lists regional alternates. citeturn11view0 The South African Journal of Botany review supports the broader notion of a 27-tree “nakshatravan” set with many documented medicinal properties and numerous reported compounds, but species-by-species details vary by tradition and region. citeturn23view0

```csv
nakshatra,plant_name_sanskrit,plant_name_iast,plant_name_common,plant_name_latin,plant_type,sacred_use,medicinal_use,ayurvedic_action,compounds_known,where_grows,conservation_status,ritual_use,source_text,attestation_status,source
Ashvinī,Kucchilā,Kucchilā,Poison nut / Strychnine tree,Strychnos nux-vomica,tree,nakshatra tree association,traditional medicinal use (caution: toxicity),UNKNOWN,"alkaloids (strychnine class)","tropical/subtropical; prefers well-drained soils",UNKNOWN,birth-star tree worship,TRADITIONAL_LIST,TRADITIONAL,TRAD_NakshatraTrees_IndiaBiodiversity
Bharaṇī,Āmalakī,Āmalakī,Indian gooseberry,Amla,Phyllanthus emblica,tree,nakshatra tree association,rasayana fruit,UNKNOWN,"polyphenols (general)","tropical/subtropical; hardy",UNKNOWN,birth-star tree worship,TRADITIONAL_LIST,TRADITIONAL,TRAD_NakshatraTrees_IndiaBiodiversity
Kṛttikā,Udumbara,Udumbara,Cluster fig,Ficus racemosa,tree,nakshatra tree association,traditional uses in multiple systems,UNKNOWN,"diverse phytochemicals summarized in reviews",tropical/subtropical; tolerates varied soils,UNKNOWN,birth-star tree worship,TRADITIONAL_LIST,TRADITIONAL,TRAD_NakshatraTrees_IndiaBiodiversity
Rohiṇī,Jambu,Jambu,Jamun/Java plum,Syzygium cumini,tree,nakshatra tree association,metabolic support in folk practice,UNKNOWN,UNKNOWN,tropical/subtropical; moist to seasonally dry,UNKNOWN,birth-star tree worship,TRADITIONAL_LIST,TRADITIONAL,TRAD_NakshatraTrees_IndiaBiodiversity
Mṛgaśīrsha,Khadira,Khadira,Cutch tree / Catechu,Acacia catechu,tree,nakshatra tree association,astringent uses,UNKNOWN,"catechin/epicatechin polyphenols reported",tropical/subtropical; dry forests,UNKNOWN,birth-star tree worship,TRADITIONAL_LIST,TRADITIONAL,TRAD_NakshatraTrees_IndiaBiodiversity
Ārdrā,Aguru,Aguru,Agarwood (regional variants),Aquilaria agallocha,tree,nakshatra tree association,aromatic/resin uses,UNKNOWN,UNKNOWN,tropical forests,UNKNOWN,birth-star tree worship,TRADITIONAL_LIST_WITH_ALTERNATES,TRADITIONAL,TRAD_NakshatraTrees_IndiaBiodiversity
Punarvasu,Vaṃśa,Vaṃśa,Bamboo,Bambusa arundinacea,grass/woody,nakshatra plant association,multiple practical uses,UNKNOWN,UNKNOWN,tropical/subtropical; wide habitat,UNKNOWN,birth-star plant association,TRADITIONAL_LIST,TRADITIONAL,TRAD_NakshatraTrees_IndiaBiodiversity
Puṣya,Aśvattha,Aśvattha,Peepal/Sacred fig,Ficus religiosa,tree,sacred worship tree,ethnomedicinal uses summarized in review,UNKNOWN,phytochemicals summarized in ethnopharmacology review,tropical/subtropical; hardy,UNKNOWN,worship/temple tree,TRADITIONAL_LIST_PLUS_REVIEW,TRADITIONAL,TRAD_NakshatraTrees_IndiaBiodiversity;SCI_Nakshatravan_Review_2022_SAJB
Āśleṣā,Nāgapuṣpa,Nāgapuṣpa,Alexandrian laurel / (regional alternates),Calophyllum inophyllum,tree,nakshatra tree association,traditional uses vary,UNKNOWN,UNKNOWN,coastal/tropical; sandy soils common,UNKNOWN,birth-star tree worship,TRADITIONAL_LIST_WITH_ALTERNATES,TRADITIONAL,TRAD_NakshatraTrees_IndiaBiodiversity
Maghā,Vaṭa,Vaṭa,Banyan,Ficus benghalensis,tree,major sacred tree,ethnomedicinal uses,UNKNOWN,UNKNOWN,tropical/subtropical; hardy,UNKNOWN,worship/temple tree,TRADITIONAL_LIST,TRADITIONAL,TRAD_NakshatraTrees_IndiaBiodiversity
Pūrvaphālgunī,Palāśa,Palāśa,Flame-of-the-forest,Butea monosperma,tree,ritual tree (yajna uses),traditional medicinal uses,UNKNOWN,flavonoids reported in reviews,tropical/subtropical; dry deciduous,UNKNOWN,ritual implements,TRADITIONAL_LIST,TRADITIONAL,TRAD_NakshatraTrees_IndiaBiodiversity
Uttaraphālgunī,Kāravīra,Kāravīra,Indian oleander,Nerium oleander,shrub,association varies by list,traditional use (toxicity caution),UNKNOWN,cardiac glycosides class (general),tropical/subtropical ornamental,UNKNOWN,ritual association varies,TRADITIONAL_LIST_WITH_ALTERNATE,TRADITIONAL,TRAD_NakshatraTrees_IndiaBiodiversity
Hasta,Jātī,Jātī,Royal jasmine,Jasminum grandiflorum,shrub/climber,flower sacred uses,traditional aromatic/medicinal uses,UNKNOWN,UNKNOWN,tropical/subtropical; well-drained,UNKNOWN,garlands,TRADITIONAL_LIST_WITH_ALTERNATE,TRADITIONAL,TRAD_NakshatraTrees_IndiaBiodiversity
Citrā,Bilva,Bilva,Bael,Aegle marmelos,tree,sacred to Shiva,traditional medicinal uses,UNKNOWN,UNKNOWN,tropical/subtropical; dry tolerant,UNKNOWN,leaf offerings,TRADITIONAL_LIST,TRADITIONAL,TRAD_NakshatraTrees_IndiaBiodiversity
Svātī,Arjuna,Arjuna,Arjun tree,Terminalia arjuna,tree,sacred/medicinal tree,cardio-related traditional uses (Ayurveda),UNKNOWN,UNKNOWN,subtropical/tropical; riverine,UNKNOWN,ritual association varies,TRADITIONAL_LIST,TRADITIONAL,TRAD_NakshatraTrees_IndiaBiodiversity
Viśākhā,Kapittha,Kapittha,Wood apple,Feronia elephantum,tree,association varies by region,traditional uses,UNKNOWN,UNKNOWN,tropical/subtropical,UNKNOWN,birth-star tree worship,TRADITIONAL_LIST,TRADITIONAL,TRAD_NakshatraTrees_IndiaBiodiversity
Anurādhā,Bakula,Bakula,Bullet wood,Mimusops elengi,tree,sacred/fragrant,traditional uses,UNKNOWN,UNKNOWN,tropical/subtropical,UNKNOWN,garlands,TRADITIONAL_LIST,TRADITIONAL,TRAD_NakshatraTrees_IndiaBiodiversity
Jyeṣṭhā,Śālmalī,Śālmalī,Silk cotton tree,Bombax ceiba,tree,association varies by list,traditional uses,UNKNOWN,UNKNOWN,tropical/subtropical,UNKNOWN,ritual association varies,TRADITIONAL_LIST_WITH_ALTERNATE,TRADITIONAL,TRAD_NakshatraTrees_IndiaBiodiversity
Mūla,Āmra,Āmra,Mango,Mangifera indica,tree,major sacred fruit tree,traditional medicinal uses,UNKNOWN,UNKNOWN,tropical/subtropical; warm,UNKNOWN,offerings,TRADITIONAL_LIST_WITH_ALTERNATE,TRADITIONAL,TRAD_NakshatraTrees_IndiaBiodiversity
Pūrvāṣāḍhā,Vetasa,Vetasa,Rattan (regional variants),Calamus rotang,climber,association varies by list,traditional uses,UNKNOWN,UNKNOWN,tropical; humid forests,UNKNOWN,ritual association varies,TRADITIONAL_LIST_WITH_ALTERNATES,TRADITIONAL,TRAD_NakshatraTrees_IndiaBiodiversity
Uttarāṣāḍhā,Panasa,Panasa,Jackfruit,Artocarpus heterophyllus,tree,fruit tree; abundance symbolism,traditional uses,UNKNOWN,UNKNOWN,tropical/subtropical; warm,UNKNOWN,offerings,TRADITIONAL_LIST,TRADITIONAL,TRAD_NakshatraTrees_IndiaBiodiversity
Śravaṇa,Arka,Arka,Crown flower,Calotropis gigantea,shrub,ritual plant,traditional uses (toxicity caution),UNKNOWN,cardenolides class (Calotropis genus),tropical/subtropical; dry tolerant,UNKNOWN,ritual offerings,TRADITIONAL_LIST,TRADITIONAL,TRAD_NakshatraTrees_IndiaBiodiversity
Dhaniṣṭhā,Śamī,Śamī,Khejri/Prosopis,Prosopis spicigera (syn. P. cineraria),tree,sacred in some regions,ethnomedicinal/agroforestry value,UNKNOWN,studied bioactives in literature,arid/semi-arid; drought tolerant,UNKNOWN,ritual association varies,TRADITIONAL_LIST,TRADITIONAL,TRAD_NakshatraTrees_IndiaBiodiversity
Śatabhiṣaj,Kadamba,Kadamba,Kadam tree,Anthocephalus cadamba (syn. Neolamarckia cadamba),tree,sacred grove tree,traditional uses,UNKNOWN,volatile compounds noted in nakshatravan review,tropical/subtropical; moist,UNKNOWN,temple groves,TRADITIONAL_LIST,TRADITIONAL,TRAD_NakshatraTrees_IndiaBiodiversity;SCI_Nakshatravan_Review_2022_SAJB
Pūrvabhādrapadā,Āmra,Āmra,Mango,Mangifera indica,tree,association varies in lists,traditional uses,UNKNOWN,UNKNOWN,tropical/subtropical,UNKNOWN,offerings,TRADITIONAL_LIST_WITH_DUPLICATION,TRADITIONAL,TRAD_NakshatraTrees_IndiaBiodiversity
Uttarabhādrapadā,Nimba,Nimba,Neem,Azadirachta indica,tree,major sacred medicinal tree,wide traditional medicinal uses,UNKNOWN,limonoids (general neem chemistry),tropical/subtropical; hardy,UNKNOWN,ritual and medicinal,TRADITIONAL_LIST,TRADITIONAL,TRAD_NakshatraTrees_IndiaBiodiversity
Revatī,Madhūka,Madhūka,Mahua,Madhuca longifolia,tree,sacred/ritual tree,traditional uses,UNKNOWN,UNKNOWN,tropical/subtropical,UNKNOWN,ritual offerings,TRADITIONAL_LIST,TRADITIONAL,TRAD_NakshatraTrees_IndiaBiodiversity
```

### Coherence rules as IF–THEN

The rules below combine: (a) nakṣatra element (derived), (b) Bṛhat Saṁhitā nakṣatra muhurta class (attested), (c) biodynamic plant-part category logic (traditional), and (d) Florida Zone 9b “season window” logic (agronomic). They should be tagged in your KG as **INTERPRETATION** unless the rule is directly quoted from a text (which these are not).

```text
IF nakshatra_muhurta_class = DHRUVA_FIXED
AND activity IN (plant_tree, establish_perennial_bed, sow_seed_for_long_term, save_seed)
THEN coherence = 0.92
AND evidence = TRADITIONAL

IF nakshatra_muhurta_class = MRIDU_GENTLE
AND activity IN (transplant_seedlings, plant_medicinal_herbs, graft_light, layer_plants)
THEN coherence = 0.80
AND evidence = TRADITIONAL

IF nakshatra_muhurta_class = CARA_TEMPORARY
AND crop_cycle_days <= 45
THEN coherence = 0.78
AND evidence = TRADITIONAL

IF nakshatra_muhurta_class = KSHIPRA_SWIFT
AND activity IN (quick_sowing, harvest_for_immediate_use, apply_foliar_spray)
THEN coherence = 0.75
AND evidence = TRADITIONAL

IF nakshatra_muhurta_class IN (UGRA_FIERCE, TIKSHNA_DREADFUL)
AND activity IN (sow_seed, transplant_seedlings, establish_perennial_bed)
THEN coherence = 0.25
AND evidence = TRADITIONAL

IF nakshatra_muhurta_class IN (UGRA_FIERCE, TIKSHNA_DREADFUL)
AND activity IN (heavy_earthwork, uproot_invasive, hard_prune, pest_removal, compost_turning)
THEN coherence = 0.85
AND evidence = TRADITIONAL

IF nakshatra_element = water
AND lunar_phase = waxing
THEN leaf_crops_coherence = 0.90
AND root_crops_coherence = 0.30
AND evidence = INTERPRETATION

IF nakshatra_element = earth
AND lunar_phase = waning
THEN root_crops_coherence = 0.88
AND leaf_crops_coherence = 0.55
AND evidence = INTERPRETATION

IF nakshatra = Rohini
AND tithi IN (3,5,7,10,11,13)
THEN planting_all_crops = 0.95
AND evidence = TRADITIONAL

IF vara = Guruvara
AND nakshatra_deity IN (Jupiter, Brihaspati_family_or_guru_affiliated)
THEN medicinal_herb_harvest_potency = 0.90
AND evidence = SPECULATIVE

IF florida_zone = 9b
AND month IN (May,Jun,Jul,Aug)
AND activity = transplant_cool_season_crops
THEN coherence = 0.10
AND override_reason = "heat/humidity stress risk"
AND evidence = PEER_REVIEWED_AGRONOMY

IF florida_zone = 9b
AND month IN (Sep,Oct,Nov)
AND activity IN (prepare_beds, add_compost, start_cool_season_seedlings)
THEN coherence = 0.90
AND evidence = PEER_REVIEWED_AGRONOMY

IF florida_zone = 9b
AND month IN (Dec,Jan,Feb)
AND activity = plant_deciduous_fruit_tree
AND nakshatra_muhurta_class = DHRUVA_FIXED
THEN coherence = 0.95
AND evidence = INTERPRETATION_PLUS_TRADITIONAL

IF scientific_claim_type = "sap_flow_peaks_at_full_moon"
THEN claim_status = "unsupported_generalization"
AND recommended_label = TRADITIONAL
AND evidence = PEER_REVIEWED_REVIEW_CONTRADICTS
```

### Implementation notes for the NPU Knowledge Graph

Store at least four distinct node families:

1) **Textual rules** (TRADITIONAL; with `source_text`, `verse/chapter`, and `translation_line_refs`)  
2) **Empirical bio-rhythms** (PEER_REVIEWED; with phenotype, species, periodicity, study design)  
3) **Calendar overlays** (biodynamic, panchang) as *tools* (TRADITIONAL/ANECTODAL)  
4) **Coherence inferences** (INTERPRETATION/SPECULATIVE; with tunable weights)

This separation is what allows your system to integrate Vedic timing with modern plant biology without collapsing them into a single evidence category.