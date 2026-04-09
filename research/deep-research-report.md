iturn15image8turn16image0turn16image1turn15image5

# Extracting Cosmological Entities from Vedic and Puranic Literature

## Executive summary

Vedic cosmology (especially in the Rigveda and Atharvaveda) most consistently encodes a **three-tier world** (earth–midspace/atmosphere–heaven) and supporting principles such as a **cosmic “pillar/foundation” (Skambha)** and **a primordial “golden embryo” (Hiraṇyagarbha)** that “holds up” earth and heaven. The Atharvaveda’s Skambha hymn explicitly frames Skambha as stabilizing **earth and heaven**, maintaining the “ample air between them,” and pervading the whole world. citeturn27view2turn22view0 The Rigveda’s Hiraṇyagarbha hymn likewise states that the primordial Hiraṇyagarbha “fixed and holds up” earth and heaven. citeturn28search1turn28search2

The major Purāṇas systematize this into a far more **explicit ontology**: a layered **Brahmāṇḍa** (“cosmic egg”) containing **Lokas** (often “14 worlds”: 7 upper + earth + 7 nether worlds), an axis-centered **cosmography around Mount Meru**, and a intertwined **cyclical time system** (Yugas → Mahāyuga/Caturyuga → Manvantara → Kalpa “day of Brahmā”), with large canonical durations. The Viṣṇu Purāṇa’s geography chapter lists the **seven dvīpas** and their **seven encircling oceans** (salt water, sugarcane juice, wine, ghee, curds, milk, fresh water) and places **Meru** at the center of Jambūdvīpa, “like the seed-cup of the lotus of the earth.” citeturn48view0 The Viṣṇu Purāṇa also enumerates the **seven upper spheres** (Bhūr, Bhuvar, Svar, Mahar, Jana, Tapo, Satya) and describes the **envelopes of the cosmic egg** and its containment within Pradhāna/Prakṛti. citeturn29view0 The Brahmāṇḍa Purāṇa preserves an explicit “fourteen worlds arranged vertically.” citeturn49view0

Across the corpus, “the same” entity may appear with **variant names, ordering, or placement** (e.g., names and order of nether worlds vary between Viṣṇu Purāṇa vs Bhāgavata/Padma; “higher-than-Satya” lokas appear in sectarian recensions like Vaikuṇṭha/Goloka/Kailāsa). Viṣṇu Purāṇa’s own editorial notes highlight sectarian expansions and cross-Purāṇic differences. citeturn29view0turn48view0turn47view1 Modern scholarship on Purāṇic textual transmission further emphasizes **multiple recensions** with “minor variant readings” up to “inclusion or exclusion of entire chapters,” which structurally explains cosmological inconsistencies across manuscripts and editions. citeturn37view0turn37view1

The dataset below operationalizes extraction as an **entity–relation schema** with explicit “unknown = unspecified” handling, producing a **CSV-ready consolidated table** and a **Mermaid nesting diagram** for the Yuga/Kalpa hierarchy.

## Corpus, scope, and extraction method

This report focuses on **primary passages** in (a) Vedic Saṃhitās and (b) major Purāṇas, using widely cited, stable digital editions and classic translations.

For Vedic primary citations, the Atharvaveda Saunaka recension is cited from a **GRETIL-accented reference text** (line-addressable by book/hymn/verse), which preserves verse identifiers like AVŚ_10,7.35. citeturn26view0turn27view2 English translation for the same hymn is from **R. T. H. Griffith’s Atharvaveda translation** (as hosted by Sacred Texts). citeturn22view0 Rigvedic citations use stable verse pages providing Sanskrit and English (e.g., Rigveda-online, Sacred Texts). citeturn28search1turn34search0turn34search4

For Purāṇic citations, the **Viṣṇu Purāṇa** passages use **H. H. Wilson’s translation** hosted by Sacred Texts (for cosmography, lokas, and egg-envelopes) and a Wilson-based online text for Pātāla regions (Book II Chapter V). citeturn29view0turn48view0turn47view1 The **Bhāgavata Purāṇa** yuga structure is cited in Sanskrit at 3.11.18–19. citeturn32view0turn30view0 The **Brahmāṇḍa Purāṇa** fourteen-world schema is cited from G. V. Tagare’s translation notes (Wisdom Library) explicitly referencing Brahmāṇḍa-purāṇa 1.2.20. citeturn49view0 The **Matsya Purāṇa** is cited from an Internet Archive public-domain English translation (chapter 273) because it explicitly states Kali-yuga duration and supplies a worked **divine-year ↔ human-year conversion**. citeturn46view0

Extraction approach (conceptual, not sectarian):  
Entity candidates are identified by (1) **named cosmological places** (lokas, dvīpas, oceans, Meru), (2) **time units** (yugas, mahāyuga, kalpa), (3) **cosmic containers/principles** (brahmāṇḍa; Skambha/Hiraṇyagarbha as Vedic precursors), and (4) **agents/regents** (deities as “governors” of processes or directions). Entities are normalized to **IAST-like romanization** when possible, but the dataset keeps common English spellings as synonyms in definitions. Where sources disagree or omit a field, the relation table marks **“unspecified.”**

## Primary-source entity inventory

### Lokas

**Vedic baseline: “three worlds.”**  
While later Purāṇic cosmologies elaborate 14 worlds, Vedic hymns repeatedly presuppose a cosmos in which earth and heaven are stabilized and separated by “midspace.” Atharvaveda 10.7.35 explicitly states: Skambha fixed earth and heaven, maintained the “ample air between them,” and established the six regions—pervading the whole world. citeturn27view2turn22view0 Rigveda 10.121.1 similarly states that Hiraṇyagarbha “fixed and holdeth up this earth and heaven.” citeturn28search1turn28search2 This triadic frame coheres with later labels Bhūr/Bhuvar/Svar as the “three spheres” in Purāṇic systematization. citeturn29view0

**Purāṇic system: “seven spheres + Pātālas,” and often “fourteen worlds.”**  
Viṣṇu Purāṇa Book II Chapter VII defines a **seven-sphere vertical stack** starting with the earth sphere (Bhūr-loka), then Bhuvar-loka (sky/atmosphere), Svar-loka (planetary/heavenly sphere), then Mahar-loka, Jana-loka, Tapo-loka, Satya-loka, and explicitly states these “seven spheres, together with the Pātālas, form the extent of the whole world.” citeturn29view0 The Brahmāṇḍa Purāṇa’s fourteen-world note arranges them as: Satya, Tapo, Jana, Mahar, Svar, Bhuvar, **Earth (middle)**, then Atala…Pātāla (lower). citeturn49view0

**Named lokas and brief definitions (cross-text normalized)**  
Definitions here are deliberately short, designed for extraction/ontology building, not exhaustive theological description.

Upper/middle worlds (largely stable across Viṣṇu Purāṇa and Brahmāṇḍa Purāṇa):
- **Satya-loka (Brahma-loka)**: “sphere of truth,” highest of the seven upper spheres; its inhabitants “never again know death” in Viṣṇu Purāṇa’s account. citeturn29view0turn49view0  
- **Tapo-loka**: “sphere of penance,” above Jana-loka. citeturn29view0turn49view0  
- **Jana-loka**: sphere where Sanandana and other mind-born sons of Brahmā reside (Viṣṇu Purāṇa). citeturn29view0turn49view0  
- **Mahar-loka**: sphere of “saints”; its inhabitants endure “throughout a Kalpa” in Viṣṇu Purāṇa’s account (i.e., through a “day of Brahmā”). citeturn29view0turn49view0  
- **Svar-loka (Svarga; “heavenly/planetary sphere”)**: included among the three lower “transitory” spheres; placed between sun and Dhruva as “heavenly sphere” in Viṣṇu Purāṇa’s planetary-distance framing. citeturn29view0turn49view0  
- **Bhuvar-loka**: “atmospheric sphere,” between earth and the solar region; in Viṣṇu Purāṇa it spreads above earth up to the planetary sphere. citeturn29view0turn49view0  
- **Bhūr-loka (Earth sphere)**: terrestrial sphere “comprehending its oceans, mountains, and rivers,” as far as illuminated by sun and moon rays in Viṣṇu Purāṇa. citeturn29view0turn49view0  
- **Earth (Pṛthivī; “middle region” in fourteen-world scheme)**: explicitly singled out as the middle region in the Brahmāṇḍa Purāṇa note. citeturn49view0

Nether worlds / “Pātālas” (high-variance across Purāṇas):
- **Atala, Vitala, Sutala, Talātala, Mahātala, Rasātala, Pātāla**: the Brahmāṇḍa Purāṇa note gives this familiar sevenfold sequence (with Rasātala and Mahātala ordering shown). citeturn49view0turn47view1  
- **Variant names in Viṣṇu Purāṇa Book II Chapter V**: Viṣṇu Purāṇa lists seven regions as **Atala, Vitala, Nitala, Gabhastimat, Mahātala, Sutala, Pātāla**, each 10,000 yojanas deep. citeturn47view1  
- **Bhāgavata/Padma naming (reported in Viṣṇu Purāṇa footnote)**: Atala, Vitala, Sutala, Talātala, Mahātala, Rasātala, Pātāla. citeturn47view1  

### Brahmāṇḍa

**Definition (Purāṇic):** the universe is modeled as a **cosmic “egg” (aṇḍa)** with a “shell,” surrounded by successive **envelopes** (water, fire, air, etc.). In Viṣṇu Purāṇa Book II Chapter VII, this egg is said to be encompassed “like the seed of the wood-apple… invested by its rind,” and then wrapped by water, fire, air, mind, ahaṅkāra, intellect, and finally Pradhāna (Prakṛti) as the illimitable cause. citeturn29view0 The same passage asserts a plurality of “mundane eggs… thousands and tens of thousands… millions,” i.e., many brahmāṇḍas. citeturn29view0 The Brahmāṇḍa Purāṇa note explicitly uses “Cosmic Egg” language as the container for the fourteen worlds. citeturn49view0

### Yuga cycles, Mahāyuga, and Kalpa

**Four yugas as a structured cycle.**  
Bhāgavata Purāṇa 3.11.18 defines the **caturyuga** as Kṛta, Tretā, Dvāpara, Kali and states it is set out as **twelve “divine years.”** citeturn32view0 Bhāgavata Purāṇa 3.11.19 supplies the canonical ratio structure (4:3:2:1 thousands, with “twofold hundreds”) that yields the standard (sandhyā + sandhyāṃśa included) totals for each yuga. citeturn30view0

**Kali-yuga duration and conversion (worked example).**  
Matsya Purāṇa (in this translation, chapter 273) states Kali-yuga duration as **400,000 years**, plus **32,000** years for the “twilights,” equaling **432,000 human years**, and explicitly equates this to **1200 divine years × 360 = 432,000**. citeturn46view0 This is valuable for extraction because it encodes both the **duration** and its **unit conversion rule** in one place.

**Kalpa.**  
In Viṣṇu Purāṇa Book II Chapter VII, lokas above earth are tied explicitly to a **Kalpa “day of Brahmā”**: Mahar-loka inhabitants dwell “throughout a Kalpa,” and the seven-sphere system is narrated in terms of what is consumed/deserted at kalpa-end. citeturn29view0

### Cosmic structures: Mount Meru, dvīpas, oceans

**Mount Meru as axis/center.**  
Viṣṇu Purāṇa Book II Chapter II places Jambūdvīpa “in the centre” and states: “in the centre of this continent is the golden mountain Meru.” citeturn48view0 It gives Meru’s dimensions and explicitly compares its form to “the seed-cup of the lotus of the earth.” citeturn48view0 It further situates a “vast city of Brahmā” on Meru’s summit and “stately cities of Indra and the other regents of the spheres” around it. citeturn48view0turn47view0

**Seven dvīpas and seven oceans (concentric cosmography).**  
Viṣṇu Purāṇa Book II Chapter II enumerates the seven “insular continents” (dvīpas) and seven encircling seas (salt water, sugarcane juice, wine, clarified butter, curds, milk, fresh water). citeturn48view0 This forms the canonical “ring” model used in many Purāṇas and is the backbone for extracting “located_in” relations, e.g., Meru ∈ Jambūdvīpa; Jambūdvīpa ∈ Bhūr-loka. citeturn48view0turn29view0

**Modern diagrams referenced in this report.**  
The included diagrams are modern reconstructions (not canonical ancient plates) that visually encode the concentric dvīpa–ocean rings and the vertical loka stack as described in Purāṇic prose. The “three-layered planetary systems / fourteen worlds” and “Jambudvipa” reconstructions in the carousel derive from ISKCON-affiliated explanatory pages. citeturn15image8turn15image5turn20search5 A vertical Meru diagram is drawn from a modern explanatory blog post. citeturn16image0 A concentric dvīpa graphic is hosted in a commercial/archival context. citeturn16image1

### Deities governing cosmic processes and cosmic order

The extraction challenge is that “governance” is expressed in multiple idioms: (a) **cosmic causality** (creation/sustenance/dissolution), (b) **directional or spatial regency** (lokapālas), and (c) **moral/cosmic law** (ṛta/dharma) or **mortuary sovereignty**.

**Brahmā as (re-)creator in Purāṇic cosmogony.**  
In Brahmāṇḍa Purāṇa (Tagare translation, chapter 4 context), a primordial Lord bears the appellation “Brahmā,” becomes “the evolver,” and “creates the worlds once again.” citeturn19view0 This supports extracting a “governs → creation” relation for Brahmā in a non-sectarian ontology (while noting that different Purāṇas elevate different deities). citeturn37view2

**Viṣṇu as cosmic cause and pervader.**  
Viṣṇu Purāṇa Book II Chapter II states “Hari pervades all places… supporter of all things.” citeturn48view0 Viṣṇu Purāṇa Book II Chapter VII states: “This Viṣṇu is the supreme spirit… from whence all this world proceeds… by whom the world subsists, and in whom it will be resolved.” citeturn29view0 These lines strongly license governance relations of **creation / sustenance / resolution** (often later differentiated as Brahmā–Viṣṇu–Rudra in sectarian systems, but in this text asserted as Viṣṇu’s supremacy). citeturn29view0turn37view2

**Rudra/Śiva as dissolution/fire at kalpa-end.**  
Viṣṇu Purāṇa Book II Chapter V states that from Śeṣa’s mouths “at the end of the Kalpa” issues “venomed fire,” “impersonated as Rudra,” which “devours the three worlds.” citeturn47view1 This provides a direct primary-text anchor for extracting **Rudra → dissolution (kalpa-end)**.

**Lokapālas: Indra, Yama, Varuṇa, etc.**  
Viṣṇu Purāṇa Book II Chapter II situates on Meru’s summit the city of Brahmā, and around it the cities of Indra and other regents. citeturn48view0 Wilson’s note enumerates eight lokapālas: **Indra, Yama, Varuṇa, Kubera, Vivasvat, Soma, Agni, Vāyu.** citeturn47view0turn48view0

**Vedic depictions of governance domains.**  
Rigveda 1.25.1 frames Varuṇa as a deity of *vrata* (law/observance) repeatedly violated by humans, supporting “Varuṇa → cosmic/moral order.” citeturn34search0 Rigveda 10.14 (Yama hymn) calls Yama “King” and depicts him as gathering men and showing the path, supporting “Yama → mortuary sovereignty / ancestral realm.” citeturn34search4turn34search1

## Variant accounts and cosmological inconsistencies across texts

Purāṇic cosmology is simultaneously “systematic” and **textually unstable** because Purāṇas were transmitted in **multiple recensions** and often expanded sectarianly. Rocher explicitly notes that printed Purāṇa editions can differ from “minor variant readings” to inclusion/exclusion of “entire chapters or sections,” giving Padma Purāṇa as an example with distinct North vs South recensions. citeturn37view0turn37view1 This has direct consequences for entity extraction: an “entity list” may be edition-specific unless you normalize across recensions.

Key cross-text inconsistencies relevant to cosmological entities:

Nether-world naming and ordering varies. Viṣṇu Purāṇa Book II Chapter V lists **Atala, Vitala, Nitala, Gabhastimat, Mahātala, Sutala, Pātāla**, while its own note says Bhāgavata/Padma instead use **Atala, Vitala, Sutala, Talātala, Mahātala, Rasātala, Pātāla**, and Vāyu offers yet another pattern. citeturn47view1 The Brahmāṇḍa Purāṇa note presents the familiar seven nether worlds but orders Rasātala/Mahātala differently than some modern re-tellings. citeturn49view0 For extraction, this means “Talātala” may map to “Gabhastimat/Nitala” depending on source.

Lokas “above Satya” appear as sectarian expansions. Viṣṇu Purāṇa’s editorial discussion notes that “sectarial” Purāṇas add other/higher worlds (e.g., identifying Brahmā-loka with Viṣṇu-loka; adding Rudra-loka; substituting Vaikuṇṭha and Kailāsa; or positing Goloka above all). citeturn29view0 A neutral dataset should model these as **optional / tradition-specific nodes** rather than core nodes.

Cosmographic “sub-details” diverge even when the high-level schema matches. Viṣṇu Purāṇa notes that the seven dvīpas/seas and Meru scheme are broadly shared, but that Bhāgavata differs “in its nomenclature of the subordinate details.” citeturn48view0 Planetary-distance schemata also vary subtly across Purāṇas. citeturn29view0

Time-cycle structure is mostly consistent, but texts differ in what they foreground. Bhāgavata emphasizes caturyuga as 12 divine years and gives the numeric ratio structure in compact verse form. citeturn32view0turn30view0 Matsya (ch. 273) emphasizes Kali-yuga’s human-year duration and explicitly shows the “twilight” increment and 360× conversion. citeturn46view0 Extraction pipelines should therefore store (a) the **canonical value**, (b) **unit**, and (c) whether **sandhyā/sandhyāṃśa** are included.

## Relations table for extracted entities

The table schema requested is:

**Entity | governs | Domain | located_in | Loka | symbolized_by | Symbol | cycle_duration | Time**

A compact preview is shown first, followed by the full CSV-ready dataset.

| Entity | governs | Domain | located_in | Loka | symbolized_by | Symbol | cycle_duration | Time |
|---|---|---|---|---|---|---|---|---|
| Bhūr-loka | unspecified | Earth sphere; oceans/mountains/rivers; illuminated by sun & moon rays | Brahmāṇḍa | Bhūr-loka | unspecified | unspecified | unspecified | unspecified |
| Bhuvar-loka | unspecified | Atmospheric/sky sphere above earth (up to planetary sphere) | Brahmāṇḍa | Bhuvar-loka | unspecified | unspecified | unspecified | unspecified |
| Svar-loka | unspecified | Heavenly/planetary sphere (region of “consequences of works”) | Brahmāṇḍa | Svar-loka | unspecified | unspecified | unspecified | unspecified |
| Satya-loka | unspecified | Highest sphere; “sphere of truth”; inhabitants “never again know death” | Brahmāṇḍa | Satya-loka | unspecified | unspecified | unspecified | unspecified |
| Brahmāṇḍa | unspecified | Cosmic egg/universe; multiple envelopes; many world-eggs | encompassed by Pradhāna/Prakṛti | unspecified | egg/seed | aṇḍa | unspecified | unspecified |
| Mount Meru | unspecified | Central golden mountain of Jambūdvīpa; axis-like; lotus seed-cup simile | Jambūdvīpa (Ilāvṛta) | Bhūr-loka | seed-cup of lotus | lotus seed-cup | unspecified | unspecified |
| Caturyuga / Mahāyuga | governs (time structure) | Four-yuga cycle | Brahmāṇḍa time | unspecified | unspecified | unspecified | 4 yugas in order | 12,000 divine years (4,320,000 human years) |
| Kali-yuga | governs (time structure) | Fourth yuga; “iron age” in some accounts; begins when Kṛṣṇa departs (Matsya) | Brahmāṇḍa time | unspecified | unspecified | unspecified | yuga + twilights | 1200 divine years = 432,000 human years |
| Viṣṇu (Hari) | cosmic causality | world proceeds from him; world subsists in him; resolved in him; pervades all | Brahmāṇḍa | unspecified | unspecified | unspecified | unspecified | unspecified |
| Rudra | dissolution | “venomed fire” at kalpa-end devours the three worlds | end-of-kalpa function | unspecified | unspecified | unspecified | kalpa-end | unspecified |

Primary passages underlying these preview entries include Viṣṇu Purāṇa Book II ch. VII (spheres + egg-envelopes + viṣṇu as cosmic cause), Viṣṇu Purāṇa Book II ch. II (dvīpas, oceans, Meru), Viṣṇu Purāṇa Book II ch. V (nether worlds and Rudra at kalpa-end), Bhāgavata Purāṇa 3.11 (yuga structure), and Matsya Purāṇa ch. 273 (Kali duration + conversion). citeturn29view0turn48view0turn47view1turn32view0turn30view0turn46view0

## Consolidated CSV-ready dataset and Mermaid nesting chart

### CSV-ready consolidated table

```csv
Entity,governs,Domain,located_in,Loka,symbolized_by,Symbol,cycle_duration,Time
Skambha,unspecified,"Cosmic pillar/support: stabilizes earth, heaven, midspace; pervades world","universe","unspecified","pillar/support","skambha","unspecified","unspecified"
Hiraṇyagarbha,unspecified,"Primordial golden embryo; holds up earth and heaven","universe","unspecified","golden embryo/seed","hiraṇyagarbha","unspecified","unspecified"
Brahmāṇḍa,unspecified,"Cosmic egg/universe with shell and envelopes; many world-eggs implied","encompassed by Pradhāna/Prakṛti","unspecified","egg/seed","aṇḍa","unspecified","unspecified"
Bhūr-loka,unspecified,"Earth sphere; oceans/mountains/rivers; lit by sun & moon rays","Brahmāṇḍa","Bhūr-loka","unspecified","unspecified","unspecified","unspecified"
Bhuvar-loka,unspecified,"Atmospheric/sky sphere above earth (up to planetary sphere)","Brahmāṇḍa","Bhuvar-loka","unspecified","unspecified","unspecified","unspecified"
Svar-loka,unspecified,"Heavenly/planetary sphere (region of consequences of works)","Brahmāṇḍa","Svar-loka","unspecified","unspecified","unspecified","unspecified"
Mahar-loka,unspecified,"Sphere of saints; inhabitants endure throughout a Kalpa","Brahmāṇḍa","Mahar-loka","unspecified","unspecified","unspecified","unspecified"
Jana-loka,unspecified,"Sphere where mind-born sons of Brahmā (e.g., Sanandana) reside","Brahmāṇḍa","Jana-loka","unspecified","unspecified","unspecified","unspecified"
Tapo-loka,unspecified,"Sphere of penance","Brahmāṇḍa","Tapo-loka","unspecified","unspecified","unspecified","unspecified"
Satya-loka (Brahma-loka),unspecified,"Highest sphere; sphere of truth; inhabitants never again know death","Brahmāṇḍa","Satya-loka","unspecified","unspecified","unspecified","unspecified"
Earth (middle region),unspecified,"Middle region in 14-world vertical schema","Brahmāṇḍa","Bhūr-loka","unspecified","unspecified","unspecified","unspecified"
Atala,unspecified,"Nether world (one of Pātālas)","Brahmāṇḍa","Pātāla (nether)","unspecified","unspecified","unspecified","unspecified"
Vitala,unspecified,"Nether world (one of Pātālas)","Brahmāṇḍa","Pātāla (nether)","unspecified","unspecified","unspecified","unspecified"
Sutala,unspecified,"Nether world (one of Pātālas)","Brahmāṇḍa","Pātāla (nether)","unspecified","unspecified","unspecified","unspecified"
Talātala,unspecified,"Nether world (one of Pātālas)","Brahmāṇḍa","Pātāla (nether)","unspecified","unspecified","unspecified","unspecified"
Mahātala,unspecified,"Nether world (one of Pātālas)","Brahmāṇḍa","Pātāla (nether)","unspecified","unspecified","unspecified","unspecified"
Rasātala,unspecified,"Nether world (one of Pātālas)","Brahmāṇḍa","Pātāla (nether)","unspecified","unspecified","unspecified","unspecified"
Pātāla,unspecified,"Lowest nether world (one of Pātālas)","Brahmāṇḍa","Pātāla (nether)","unspecified","unspecified","unspecified","unspecified"
Nitala,unspecified,"Variant nether world name (Viṣṇu Purāṇa sequence)","Brahmāṇḍa","Pātāla (nether)","unspecified","unspecified","unspecified","unspecified"
Gabhastimat,unspecified,"Variant nether world name (Viṣṇu Purāṇa sequence)","Brahmāṇḍa","Pātāla (nether)","unspecified","unspecified","unspecified","unspecified"
Mount Meru,unspecified,"Central golden mountain of Jambūdvīpa; axis-like; lotus seed-cup simile","Jambūdvīpa (Ilāvṛta)","Bhūr-loka","seed-cup of lotus","lotus seed-cup","unspecified","unspecified"
Jambūdvīpa,unspecified,"Central dvīpa/continent; contains Meru","Bhūr-loka","Bhūr-loka","unspecified","unspecified","unspecified","unspecified"
Plakṣadvīpa,unspecified,"Dvīpa/continent","Bhūr-loka","Bhūr-loka","unspecified","unspecified","unspecified","unspecified"
Śālmali-dvīpa,unspecified,"Dvīpa/continent","Bhūr-loka","Bhūr-loka","unspecified","unspecified","unspecified","unspecified"
Kuśa-dvīpa,unspecified,"Dvīpa/continent","Bhūr-loka","Bhūr-loka","unspecified","unspecified","unspecified","unspecified"
Krauñca-dvīpa,unspecified,"Dvīpa/continent","Bhūr-loka","Bhūr-loka","unspecified","unspecified","unspecified","unspecified"
Śāka-dvīpa,unspecified,"Dvīpa/continent","Bhūr-loka","Bhūr-loka","unspecified","unspecified","unspecified","unspecified"
Puṣkara-dvīpa,unspecified,"Dvīpa/continent","Bhūr-loka","Bhūr-loka","unspecified","unspecified","unspecified","unspecified"
Lavaṇa (salt-water ocean),unspecified,"Ocean encircling a dvīpa (salt water)","Bhūr-loka","Bhūr-loka","unspecified","unspecified","unspecified","unspecified"
Ikṣu (sugarcane-juice ocean),unspecified,"Ocean encircling a dvīpa (sugarcane juice)","Bhūr-loka","Bhūr-loka","unspecified","unspecified","unspecified","unspecified"
Surā (wine ocean),unspecified,"Ocean encircling a dvīpa (wine)","Bhūr-loka","Bhūr-loka","unspecified","unspecified","unspecified","unspecified"
Sarpi (ghee ocean),unspecified,"Ocean encircling a dvīpa (clarified butter/ghee)","Bhūr-loka","Bhūr-loka","unspecified","unspecified","unspecified","unspecified"
Dadhi (curds ocean),unspecified,"Ocean encircling a dvīpa (curds)","Bhūr-loka","Bhūr-loka","unspecified","unspecified","unspecified","unspecified"
Dugdha (milk ocean),unspecified,"Ocean encircling a dvīpa (milk)","Bhūr-loka","Bhūr-loka","unspecified","unspecified","unspecified","unspecified"
Jala (fresh-water ocean),unspecified,"Ocean encircling a dvīpa (fresh water)","Bhūr-loka","Bhūr-loka","unspecified","unspecified","unspecified","unspecified"
Kṛta/Satya-yuga,governs,"First yuga in a caturyuga","Brahmāṇḍa time","unspecified","unspecified","unspecified","yuga incl. sandhyā/sandhyāṃśa","4,800 divine years (1,728,000 human years)"
Tretā-yuga,governs,"Second yuga in a caturyuga","Brahmāṇḍa time","unspecified","unspecified","unspecified","yuga incl. sandhyā/sandhyāṃśa","3,600 divine years (1,296,000 human years)"
Dvāpara-yuga,governs,"Third yuga in a caturyuga","Brahmāṇḍa time","unspecified","unspecified","unspecified","yuga incl. sandhyā/sandhyāṃśa","2,400 divine years (864,000 human years)"
Kali-yuga,governs,"Fourth yuga in a caturyuga; arrives when Kṛṣṇa departs (Matsya ch. 273)","Brahmāṇḍa time","unspecified","unspecified","unspecified","yuga incl. twilights","1,200 divine years = 432,000 human years"
Caturyuga / Mahāyuga,governs,"Four-yuga cycle (Kṛta–Tretā–Dvāpara–Kali)","Brahmāṇḍa time","unspecified","unspecified","unspecified","4 yugas (12,000 divine years)","4,320,000 human years"
Manvantara,governs,"Rule-period of a Manu (often 71 caturyugas)","Brahmāṇḍa time","unspecified","unspecified","unspecified","71 caturyugas (base)","306,720,000 human years (excluding additional junctions)"
Kalpa,governs,"One 'day of Brahmā' (time-cycle context for loka endurance and dissolution)","Brahmāṇḍa time","unspecified","unspecified","unspecified","1,000 caturyugas","4,320,000,000 human years"
Brahmā,governs,"Creation/evolution of worlds (re-creation)","Brahmāṇḍa","Satya-loka","unspecified","unspecified","unspecified","unspecified"
Viṣṇu (Hari),governs,"Cosmic causality: world proceeds from him, subsists in him, resolves in him; pervades all","Brahmāṇḍa","unspecified","unspecified","unspecified","unspecified","unspecified"
Rudra (Śiva),governs,"Dissolution at kalpa-end: destructive fire devours the three worlds","Brahmāṇḍa","unspecified","unspecified","unspecified","kalpa-end","unspecified"
Indra,governs,"Lokapāla/regent; city around Brahmā’s city on Meru; Vedic storm/war deity","Bhūr-loka / Meru-region","Svar-loka (often)","unspecified","unspecified","unspecified","unspecified"
Varuṇa,governs,"Lokapāla/regent; also Vedic deity of law/vrata and cosmic/moral order","Bhūr-loka / Meru-region","unspecified","unspecified","unspecified","unspecified","unspecified"
Yama,governs,"Lokapāla/regent; Vedic 'King' associated with the dead/ancestors","Bhūr-loka / Meru-region","unspecified","unspecified","unspecified","unspecified","unspecified"
Agni,governs,"Lokapāla/regent (as listed) and Vedic fire principle","Bhūr-loka / Meru-region","unspecified","unspecified","unspecified","unspecified","unspecified"
Vāyu,governs,"Lokapāla/regent and Vedic wind/breath principle","Bhūr-loka / Meru-region","unspecified","unspecified","unspecified","unspecified","unspecified"
Soma (Candra),governs,"Lokapāla/regent (as listed) and lunar principle","Bhūr-loka / Meru-region","unspecified","unspecified","unspecified","unspecified","unspecified"
Sūrya,governs,"Solar principle (orbital marker in loka-distance schema)","Svar-loka system","unspecified","unspecified","unspecified","unspecified","unspecified"
Śeṣa (Ananta),governs,"Support/foundation: bears the world; foundation for Pātālas; kalpa-end fire context","Below Pātālas","unspecified","unspecified","unspecified","unspecified","unspecified"
```

Dataset provenance (for verification):  
Lokas and brahmāṇḍa-envelope structure are grounded in Viṣṇu Purāṇa Book II ch. VII and Brahmāṇḍa Purāṇa 1.2.20 note. citeturn29view0turn49view0 Dvīpas, seas, and Meru are grounded in Viṣṇu Purāṇa Book II ch. II. citeturn48view0 Nether-world variants are grounded in Viṣṇu Purāṇa Book II ch. V and its footnote. citeturn47view1 Yuga structure is grounded in Bhāgavata Purāṇa 3.11.18–19 and Kali conversion in Matsya Purāṇa ch. 273. citeturn32view0turn30view0turn46view0

### Mermaid nesting chart for Yuga/Kalpa cycles

```mermaid
flowchart TD
  A[Brahmāṇḍa\n(cosmic egg / universe)] --> B[Kalpa\n(1 day of Brahmā)\n= 1000 Caturyugas\n= 4.32 billion human years]
  B --> C[Caturyuga / Mahāyuga\n= 12,000 divine years\n= 4,320,000 human years]
  C --> D1[Satya/Kṛta-yuga\n4,800 divine years\n= 1,728,000 human years]
  D1 --> D2[Tretā-yuga\n3,600 divine years\n= 1,296,000 human years]
  D2 --> D3[Dvāpara-yuga\n2,400 divine years\n= 864,000 human years]
  D3 --> D4[Kali-yuga\n1,200 divine years\n= 432,000 human years]
  B -. "Contextual subdivision\n(often)" .-> M[Manvantara\n(71 Caturyugas base)\n= 306,720,000 human years\n(+ junctions vary by text)]
```

Durations shown here follow Bhāgavata Purāṇa’s caturyuga definition and ratio formula, with Matsya Purāṇa’s explicit Kali-yuga conversion providing a worked “divine years × 360” rule. citeturn32view0turn30view0turn46view0