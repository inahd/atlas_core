# Carnatic Tala System Deep Research and Computational Derivation Schema

## Classical foundations of tāla as measured time

Indian musicological literature treats **tāla primarily as measured time**, articulated through actions and organized into cyclical structures. In Bharata’s *Nāṭyaśāstra* (as translated by Manomohan Ghosh), the chapter “On the Time-measure” defines tāla in relation to **kāla (time units), laya (tempo), and structured division**; it also distinguishes the “kāla arising from tāla” from other popular time units, and relates tempo (laya) to quick/medium/slow categories. citeturn22view0

Later scholarship summarizing Śārṅgadeva (*Saṅgītaratnākara*, 13th c.) emphasizes two points that matter directly for a computational engine:

1) **tāla as a foundation for vocal, instrumental music, and dance** (the “basis” idea), and  
2) **time units defined via syllabic utterance**, notably: a mātrā as the time to pronounce **five short syllables**, and proportional units such as laghu/guru/pluta in mātrā counts. citeturn25view0turn33view2

A crucial historical clarification for knowledge-graph “attestation hygiene” is that **many familiar South Indian rhythm-theory terms are not stable across centuries**. For example, Arati Rao’s study of Vijayanagara-period musicological works argues that the *grouping* of ten “tāla-prāṇa” elements (the “tāla-daśa-prāṇa” concept) is first explicit in a Vijayanagara text (*Tāladīpikā*, c. 15th c.), and that some terms (notably **Aṅga** and **Jāti** as part of “daśa-prāṇa”) are not presented as such in pre‑Vijayanagara treatises. citeturn33view0turn33view1

Complementing that, N. Ramanathan’s Music Academy paper highlights that terms like **kriyā** and **aṅga** have complicated histories and that present-day textbook usage can diverge from earlier systems (e.g., Gandharva vs. later deśī and modern pedagogical frameworks). citeturn35view0turn35view2

## The core performance grammar of the three angas and kriyā

### What modern Carnatic pedagogy counts as “the three angas”
In the **Suladi/Sapta-tāla** teaching system (the one your `CarnataticTalaEngine` encodes), the working building blocks are three angas:

- **Laghu (L)**: variable length determined by **jāti** (3, 4, 5, 7, 9)  
- **Drutam (D)**: fixed length **2**  
- **Anudrutam (U)**: fixed length **1**

This is the specific “L/D/U” system described widely in modern Carnatic instruction and is explicitly framed as “only three kriyās are used nowadays” in David P. Nelson’s *Solkattu Manual* excerpt, which also defines kriyā gestures and finger-count practice. citeturn24view0

### Physical gestures used in performance
A consistent modern description (valuable for an NPU knowledge graph because it pins down *observable* behavior) is:

- **tattu**: audible clap (hand-to-hand or hand-to-thigh)  
- **viccu**: wave/turning gesture (often a “back of hand” motion)  
- **finger counts**: begin from the **little finger** (pinky) and proceed in a conventional order citeturn24view0turn35view0

From these, the three angas are manifested as:

- **Laghu (L)** = one tattu (clap) + *(jāti − 1)* finger counts  
- **Drutam (D)** = one tattu (clap) + one viccu (wave/turn)  
- **Anudrutam (U)** = one tattu (single clap)

Nelson’s excerpt states the modern triad of gestures (tattu/viccu/finger counts) and treats them as the practical substrate of tāla counting; Ramanathan independently lists tattu, viccu, and finger movements as the three contemporary kriyā types. citeturn24view0turn35view0

### Why “jāti” is mathematically central in this system
In the Suladi framework, **jāti** means **the laghu’s cardinality**, not the tāla family. Thus the five jāti-laghu values are: **tisra 3, catusra 4, khaṇḍa 5, miśra 7, saṅkīrṇa 9**—a set explicitly presented as “laghu variables” generating 35 tālas from 7 parents (7×5). citeturn23search13turn35view1

For an engine, this gives a clean formalism:

\[
\text{beats per cycle} = \sum_{\text{anga} \in \text{sequence}} 
\begin{cases}
J & \text{if anga = L}\\
2 & \text{if anga = D}\\
1 & \text{if anga = U}
\end{cases}
\]

where \(J \in \{3,4,5,7,9\}\) is the laghu jāti.

## Suladi Sapta Tāla system as a computable matrix of 35 tālas

### The seven tāla families and their anga sequences
The **Suladi Sapta Tāla** system enumerates seven “parent” tālas (families), each defined by an **anga sequence** built from L/D/U:

- Dhruva: L D L L  
- Matya: L D L  
- Rupaka: D L  
- Jhampa: L U D  
- Triputa: L D D  
- Ata: L L D D  
- Eka: L citeturn23search13turn13search10

Ramesh Shotham’s overview presents the 7 parents and the 5 laghu variants (tisra/catusra/khanda/misra/sankirna), explicitly stating the “7×5 = 35” structure and using the same L/D/U abstraction. citeturn23search13

### The 35 tālas
Combining each family with each jāti yields **35 distinct tālas** (often called the “35 tālas” scheme). This is exactly what your class encodes with `TALA_ANGAS` × `JATI_AKSHARAS`.

Two practical points matter for accurate knowledge-graph representation:

1) **Common concert names frequently refer to a specific family+jāti default**, not the entire family. For example, **Ādi tāla** is commonly identified as **caturasra-jāti tripuṭa** (8 akṣaras). citeturn28search3  
2) Many of the 35 exist primarily as **pedagogical possibilities** (alankāra exercises, rhythmic training) rather than being equally represented in mainstream kriti/varṇam repertoire. Shotham’s “7×5” presentation frames 35 as systematic outcomes; repertoire distribution is a separate cultural layer. citeturn23search13

### Traditional usage contexts and examples (high-attestation cases)
Some tala-use claims can be grounded with better-than-blog evidence:

- **Varṇams are commonly in Ādi and Āṭa tālas** (with other tālas also used). citeturn28search0turn28search14  
- In Muttusvāmi Dīkṣitar’s **Navagraha** corpus, multiple sources list specific graha-kritis with specific tālas (and several are Suladi talas). For example:  
  - “candram bhaja mānasa” lists **c/maṭya** on karnatik.com citeturn26search2  
  - “śrī śukra bhagavantam” lists **k/aṭa** (khanda aṭa) on karnatik.com citeturn26search3  
  - “aṅgārakam āśrayāmyaham” lists **rūpaka** on karnatik.com citeturn37search1  
  - Wikipedia’s summary list (tertiary, but explicit) also enumerates these tāla assignments. citeturn37search8

These examples are especially useful for your “cosmology hooks,” because they show an **existing, musically prestigious** repertoire that *connects* planets/deities and certain tālas—though it still does **not** establish a universal rule that weekdays must map to specific tāla families.

## Sollukattu and stroke-language as symbolic computation

### A practical definition of solkattu in modern sources
Nelson defines *solkattu* as combining spoken rhythmic syllables into phrases and synchronizing them with a stable tāla; once synchronized, phrases can be transformed via processes (speed changes, expansions/contractions, internal pulse regrouping). citeturn24view0

### Canonical syllable groups that matter for your engine
Nelson’s excerpt gives a compact, high-utility list of **example phrases of length 1–9**, including 3,4,5,7,8,9 syllable groups. citeturn24view0

For the specific *jāti* lengths your code uses (3/4/5/7/9), widely used pedagogical realizations include:

- 3 (tisra): **ta ki ta** citeturn24view0  
- 4 (catusra): **ta ka di mi** citeturn24view0  
- 5 (khanda): **ta ka ta ki ta** (one of the common five-syllable options) citeturn24view0turn36search11  
- 7 (misra): common realizations vary. One documented teaching variant is **tha ki ta tha ka di mi** (7), explicitly labeled “most common phrase used” for miśra/nadai in a Raga Surabhi lesson page. citeturn27search3  
- 9 (sankirna): a common realization is **ta ka dhi mi ta ka ta ki ta** (9), shown in dance-oriented tala system instruction. citeturn27search4turn36search11

This variability is critical for your NPU graph: “misra = ta ki ta ta ka di mi” is a **valid and widely used** 3+4 segmentation, but it is **not the only canonical** 7-syllable solkattu; Nelson’s excerpt also provides multiple alternative 7-syllable examples. citeturn24view0turn27search3

### How Carnatic solkattu differs from Hindustani bol/thekā
A minimal but accurate cross-system distinction:

- Carnatic solkattu is often taught as **flexible syllabic grouping** that can represent rhythmic density and subdivision, and can be recited by musicians and dancers even before fixing drum-stroke-specific realizations. citeturn24view0turn23search17  
- Hindustani bols/thekā are strongly tied to **tabla stroke vocabularies** and the **characteristic thekā patterns** of each tāl (e.g., formalized sequences for jhaptāl, tīntāl, etc.). An NCERT text excerpt provides explicit bol patterns for Hindustani tālas like jhaptāl and rūpak. citeturn36search1

Your engine’s `generate_bols()` function sits between these worlds: it uses Carnatic-style syllabic groups for laghu (3/4/5/7/9), then assigns fixed two- and one-syllable cells to drutam/anudrutam. That is a coherent **computational design**, but the attestation strength differs by component (laghu phrases are strongly attested; drutam/anudrutam “bol assignment” is more school-dependent and may be better treated as a configurable layer).

## Gati, nadai, kālai, and gati-bhedam as rule-based transformations

### Terminology alignment for a knowledge graph
Modern Carnatic usage typically separates:

- **gati / nadai**: subdivision count *within* a beat (akṣara)  
- **kālai (kāla)**: “speed level” / tempo scaling across a cycle (e.g., first speed vs. doubled)  
- **laya**: the general tempo/flow concept (with slow/medium/fast categories in older and modern texts)

Nelson’s excerpt explicitly frames “three speeds” (trikāla) as doubling and redoubling within the same tāla frame, and emphasizes that beats are assumed to contain an internal pulse structure that may change. citeturn24view0  
Ramanathan’s Music Academy paper further situates laya historically and highlights conceptual drift in later usage. citeturn35view1turn35view2

### The “pancha gati” set
A modern scholarly snippet (Taylor & Francis chapter preview) states the beat may be divided into five gatis: **tisra, catusra, khanda, misra, sankirna**, matching your engine’s `JATI_AKSHARAS` set and the common South Indian rhythmic framework. citeturn23search17

A useful formal identity for your NPU graph:

\[
\text{subpulses per cycle} = (\text{beats per cycle}) \times (\text{gati subdivisions per beat})
\]

### Gati-bhedam in computation terms
Within the solkattu framework, “internal pulse grouping of beats may temporarily change” (Nelson), which is effectively a statement that **gati can change while the higher-level tāla cycle remains stable**. citeturn24view0

In a knowledge-graph-friendly rule form:

- Fixed *cycle* (tāla family + jāti) → fixed akṣara count \(B\)  
- Variable *subdivision* (gati/nadai) → pulse multiplier \(G\)  
- Any gati-bhedam passage must preserve alignment to cycle boundaries by ensuring the total pulse counts reconcile at the intended resolution points.

This maps well to your engine’s `beats` and `gati_count` model.

## Korvai and kanakku as cadence mathematics

### A high-attestation minimal definition
The karnatik.com glossary defines **kōrvai** as “a rhythmic phrase of several tāla cycles,” usually featuring **a repetition of 3 within it**, and used as a performed rhythmic design. citeturn13search6

Nelson’s excerpt provides two additional knowledge-graph primitives relevant to your `compute_korvai()`:

- **kanakku** (“calculation”) as rhythmic designs that create tension within tāla citeturn24view0  
- **gopucca** (“cow’s tail”) patterning as long-to-short design types commonly used in Karnatak rhythm citeturn24view0

### Mathematical landing rule
Your code encodes the core cadential constraint correctly:

- A korvai (or any resolving cadence) must land on **samam / beat 1 alignment** of a cycle boundary.  
- The “3× repeated phrase” is the most common template, but real practice includes offsets (eduppu), inter-phrase gaps (karvais), and multi-cycle solutions.

Given the glossary’s explicit “usually repetition of 3,” your “3×” default is defensible as a **canonical** rule, but the “phrase_len = beats/3 else spread” logic should be tagged as **simplified pedagogy**, not as a complete korvai science.

### Where “srotovaha / sama / viṣama” belong
In classical and modern rhythm theory discourse, **srotogata/srotovaha, gopucca, sama, viṣama** are most consistently framed as **yati/design shapes** or “manner of change” in flow rather than a single fixed korvai taxonomy. Ramanathan’s paper explicitly discusses yati categories like **srotogata** and **gopucca** and notes later expansions of yati types. citeturn35view1turn35view2

For your NPU graph, the clean approach is:

- Keep **korvai** as “cadential composition that resolves” (often 3×)  
- Represent **yati** as a separate design-constraint node that can parameterize korvai shape (sama, srotogata, gopucca, etc.)

## Cosmological mappings and audit of the `CarnataticTalaEngine` derivation rules

### What is strongly attested vs. what is interpretive
Your engine combines three mappings:

- `element → jati`  
- `vara_lord (planet/day) → tala_family`  
- `guna → gati`

From the standpoint of classical Carnatic rhythm theory sources collected here:

- The **jāti laghu counts (3/4/5/7/9)** and the **sapta tāla families** are strongly attested as a modern Carnatic system (and computable without lookup tables). citeturn23search13turn24view0  
- The **existence of weekday → planet (vara → graha)** is a jyotiṣa convention (outside musicology proper) and is widely reported in explanations of navagraha/weekday naming conventions. citeturn31search7  
- A repertoire-based “planet ↔ tāla” linkage exists prominently in Dīkṣitar’s **Navagraha** kritis (e.g., Shukra kriti in Khanda Aṭa; Angāraka in Rūpaka; Chandra in Maṭya). This supports an **evidence-backed artistic association**, but does **not** establish a universal cosmological law that “Venus day implies Aṭa family” in general Carnatic theory. citeturn26search3turn26search2turn37search1turn37search8  
- No collected classical/standard Carnatic theory source here provides a canonical mapping of **pañca-bhūta elements → jāti counts** or **triguṇa → gati counts**. These should therefore be represented in your knowledge graph as **interpretive model assumptions** with explicit provenance.

### Validating today’s field example in your engine’s math
Your “today” state:

- AIR → miśra jāti → laghu = 7  
- Shukra (Venus) → aṭa family → anga sequence L L D D  
- tamas → khanda gati → subdivision = 5  

Beat computation:

\[
L(7) + L(7) + D(2) + D(2) = 18 \text{ beats}
\]

Pulse computation in khanda gati:

\[
18 \times 5 = 90 \text{ subpulses}
\]

This is exactly the computation implied by the standard Suladi anga arithmetic and the modern subdivision model used in solkattu pedagogy. citeturn23search13turn24view0

The only critical “attestation note” is that the *cosmological* step “Air ⇒ miśra” and “tamas ⇒ khanda” should be tagged as **system-internal derivation choices**, unless you later add external textual evidence.

## CSV deliverables for the NPU knowledge graph

[Download tala_angas_kriya.csv](sandbox:/mnt/data/tala_angas_kriya.csv)  
[Download suladi_sapta_tala_families.csv](sandbox:/mnt/data/suladi_sapta_tala_families.csv)  
[Download suladi_35_talas_matrix.csv](sandbox:/mnt/data/suladi_35_talas_matrix.csv)  
[Download solkattu_basic_phrases_1_to_9.csv](sandbox:/mnt/data/solkattu_basic_phrases_1_to_9.csv)  
[Download pancha_jati_canonical_phrases.csv](sandbox:/mnt/data/pancha_jati_canonical_phrases.csv)  
[Download pancha_gati_nadai.csv](sandbox:/mnt/data/pancha_gati_nadai.csv)  
[Download npu_derivation_rules_attestation.csv](sandbox:/mnt/data/npu_derivation_rules_attestation.csv)

Each CSV row includes an `attestation_status` and a `source_key`. The `source_key` strings correspond to the following evidence anchors used in this report:

- `NELSON2014_EXCERPT`: David P. Nelson, *Solkattu Manual* excerpt (phrases 1–9; kriyā gestures; trikāla; etc.). citeturn24view0  
- `MUSIC_ACAD_RAMANATHAN_2003_2005`: N. Ramanathan, Music Academy paper on tāla-daśa-prāṇa and concept drift (kriyā/aṅga/jāti/yati discussions). citeturn35view0turn35view1turn35view2  
- `SHOTHAM_SULADI`: Ramesh Shotham overview of South Indian tāla system (7 parents × 5 jāti = 35). citeturn23search13  
- `KARNATIK_TALA_TABLE`: karnatik.com “Tala Table” page (35-tāla tabulation reference). citeturn13search10  
- `RAGASURABHI_MISHRA_NADAI`: Raga Surabhi “Miśra nadai” lesson statement about the commonly used 7-syllable phrase. citeturn27search3  
- `ONLINEBHARATANATYAM_TALA_SYSTEM`: Online Bharatanatyam tala system page (jāti phrases and L/D/U framing). citeturn27search4turn36search11  
- `REINA_TAYLORFRANCIS_SNIPPET`: Rafael Reina (Taylor & Francis chapter preview) mentioning five gatis and defining solkattu usage. citeturn23search17  
- `NAVAGRAHA_KRITIS_LIST` / `KARNATIK_SRI_SHUKRA`: Navagraha kriti tala assignments (karnatik.com pages; summary list). citeturn26search3turn37search8  
- `PANCHA_BHUTA_GENERAL`: general pañca-bhūta background (used only to note that “elements → jati” is not evidenced in Carnatic theory sources collected here). citeturn12search14turn12search10  
- `TRIGUNA_GENERAL`: *no dedicated classical Carnatic mapping source in this collection*; rows are explicitly marked “Interpretation / system design.”

