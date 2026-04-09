# Chandas for Knowledge Graph and Generative Text Engine

## Knowledge graph schema and evidence labels

### What is stable enough to store as structured data

Vedic and Classical prosody can be represented cleanly as a graph of **Forms** (metres and prose styles) linked to **Constraints** (syllable/mātrā counts, laghu/guru patterns, caesura), **Contexts** (Vedic ritual moments, literary genres), and **Bandhu-style correspondences** (cosmic mappings). The hard boundary is that **metre is primarily syllable-counted with a regulated cadence**, and (in Vedic) the quantitative rhythm is **not governed by musical accent**. Macdonell emphasizes that Vedic metre is measured by syllable count, and is “more or less regulated by a quantitative rhythm (unaffected by the musical accent),” with the cadence (last 4–5 syllables) being more rigidly regulated. citeturn22view0

From a knowledge-graph perspective, this supports a split into:
- **Observed constraint nodes**: syllables-per-pāda, stanza structure, cadence tendencies, caesura positions.
- **Observed usage nodes**: where a metre is used (e.g., Vedic Soma-pressing associations or epic narrative dominance).
- **Interpretive mappings**: metre ↔ rasa, metre ↔ element/graha, metre ↔ time-of-day heuristics.
- **Speculative mappings**: metre ↔ particular nakṣatras or detailed pañcāṅga rules (usually not textually fixed).

### Evidence labels you requested

This report uses:
- **OBSERVED**: explicitly stated in primary/standard secondary sources (Brāhmaṇa passages; standard prosody treatises; well-attested literary usage).
- **INTERPRETATION**: inferred from conventional usage patterns, genre practice, or later scholastic/poetic tradition, but not a single canonical mapping across traditions.
- **SPECULATIVE**: proposed generator heuristics where no strong traditional mapping is widely attested.

## Vedic chandas structures, patterns, and attested correspondences

### Core mechanical facts of Vedic metre that matter for an engine

Macdonell’s summary is highly implementable:
- Vedic metres are defined by **syllable count per pāda**, most commonly 8, 11, 12. citeturn22view0
- **Cadence** (last 4–5 syllables) is more strictly regulated than the opening. citeturn22view0
- 11- and 12-syllable verses are characterized by **cadence + caesura after the 4th or 5th syllable**. citeturn22view0turn23view4
- The **8-syllable verse** tends to have an iambic cadence pattern in the last 4 syllables, with flexibility at the beginning. citeturn22view0

For structured data, it is best to store (a) stanza syllable structures, (b) a *canonical* cadence model per line-type (8/11/12), and (c) a “variance model” allowing known Vedic freedoms (anceps positions, limited resolution).

### The seven primary Vedic metres as a structured set

Many traditional sources treat these seven as a canonical set in ritual and mythic explanations. For example, a discussion of morning recitation and sacrifice in the “Chandas as Vedanga” source explicitly lists the seven metres as the configuration of ritual mantra-recitation. citeturn30search0

A highly concrete **Brāhmaṇa bandhu** (Śatapatha 8.3.1.12) maps several metres to directions/regions (east/south/west/north/upper), explicitly naming Gāyatrī, Triṣṭubh, Jagatī, Anuṣṭubh, Paṅkti. citeturn30search2  
This is important because it is a rare *explicit* “metre ↔ cosmos” mapping you can store as OBSERVED (directional bandhu), distinct from later astrological overlays.

Another important Brāhmaṇa bandhu (Śatapatha X.3.1.1 as cited in the same source) maps the seven metres to **limbs/functions** (mouth/eye/voice/mind/ear/breath functions). citeturn30search0

### Accent and “tone_quality” field

Your requested field “tone_quality (grave/acute/circumflex pattern)” cannot be a fixed per-metre template in the way L/H cadence is. A key reason: Vedic accent (udātta/anudātta/svarita) is not what defines chandas; metrical rhythm is based on syllable quantity and is described as *unaffected by the musical accent*. citeturn22view0  
So the correct structured-data approach is:
- `tone_quality = "Accent is lexical; not determined by metre. Store accent at token level if generating Vedic-accented output."` (OBSERVED, per metrical descriptions) citeturn22view0

### Downloadable CSV with all requested fields

You asked for full structured data as CSV. Two machine-ready files were created:

- [Download metres_and_forms.csv](sandbox:/mnt/data/metres_and_forms.csv)
- [Download metre_correspondence_matrix.csv](sandbox:/mnt/data/metre_correspondence_matrix.csv)

The first includes the seven Vedic metres plus Classical metres, vernacular forms, and prose styles as “forms,” with the key fields you specified (syllables, padas, L/H pattern, cadence, Vedic usage notes, deity and other correspondences with evidence labels).

The second is the requested **metre × rasa × deity × purpose × time/panchanga** matrix as weighted edges.

## Classical Sanskrit metres and mixed forms

### The authoritative pattern source for classical vṛttas

For classical syllable-counting metres (vṛtta), a standard primary source is **Kedārabhaṭṭa’s Vṛttaratnākara**, which encodes metres by gaṇa sequences and final laghu/guru. In the text, it defines and exemplifies many of the metres you listed, including vasantatilakā, mālinī, śikhariṇī, mandākrāntā, and śārdūlavikrīḍita via mnemonic definition-verses that are themselves valid examples. citeturn18view0

### A practical implementation note: use “definition-verses” as example-lines

Because the Vṛttaratnākara definition-lines are short and metrically guaranteed, they are ideal for your “Example verse (1 line with scansion)” requirement. The CSV therefore stores, for each classical metre, one definition-line plus a gaṇa-based scansion template (H/L per syllable group) derived from the gaṇa formula. citeturn18view0

### Caesura positions you can store with high confidence

Some classical metres have strongly conventional internal breaks (yati):
- Śārdūlavikrīḍita is widely described as 19 syllables per pāda and often divided **12 + 7**. citeturn42search2
- Mālinī is often described with an obligatory **word break after the 8th syllable** by later authorities (important for generation quality). citeturn41search10
- Mandākrāntā’s traditional mnemonic marks yati by “jaladhi-ṣaṭ” (4 + 6) before the remaining pattern, i.e., an internal pause after 4 and 10 syllables (a standard interpretation of the mnemonic line in the metre tradition). citeturn18view0

### Jāti (mātrā-based) metres: Āryā and Vaitālīya

Macdonell notes that Āryā and Vaitālīya are measured not by syllables but by **morae (mātrās)**, which is crucial for your generator backend. citeturn22view0  
Vṛttaratnākara explicitly treats **vaitālīya** in its jāti/metre section. citeturn18view0

### Campū as a macro-form

The campū form is explicitly described as **mixed prose and verse**, with “powerful picturesque descriptions” expressed in verse while the narrative continues mainly in prose—exactly the “prose for movement, verse for peaks” architecture you want for generation modes. citeturn43search3

## Metre × meaning matrices and coherence rules for generation

### Metre × rasa

Some metre–rasa associations are strongly supported by literary tradition:
- Mandākrāntā is widely treated as the “gently stepping” metre suited to **love-in-separation**, and this is explicitly discussed in modern scholarship on Meghadūta, noting its suitability for “love in separation” and its pairing with landscape/seasonal aesthetics. citeturn42search3
- Triṣṭubh is explicitly described as a symbol of “might and vigour” and is associated with Indra in Vedic discussions—supporting a high-confidence **vīra** mapping. citeturn38view0
- Vedic 12-syllable verse (basis of jagatī) is described as extending triṣṭubh to shift its cadence toward an iambic character; that “flow” supports your interpretive mapping of jagatī toward expansive/cosmological affect. citeturn25view3

In the matrix CSV, these are implemented as weighted edges (OBSERVED where the tradition directly states suitability/association; otherwise INTERPRETATION).

### Metre × deity

Some deity associations are explicit enough to store as OBSERVED:
- Triṣṭubh ↔ Indra is explicit in the “Chandas as Vedanga” source: “The Ṛgveda associates Triṣṭubh metre with Indra,” and it’s linked to vigour and force (vajra imagery). citeturn38view0
- Jagatī is “allotted to Ādityas and Viśvedevas during the third pressing of Soma” in an Aitareya Brāhmaṇa context, which supports a strong jagatī ↔ solar/Āditya association in ritual framing. citeturn39view4
- Gāyatrī has strong Sāvitr/Sūrya association through the canonical Gāyatrī (RV 3.62.10), which is explicitly dedicated to Savitṛ and used widely in later practice. citeturn29search8

For the seven metres as “Sun’s horses,” a Purāṇic attestation explicitly names the seven horses yoked to the Sun-god’s chariot as the seven metres (Gayatri, Brhati, Usnik, Jagati, Tristup, Anustup, Pankti), and cites this as coming from Viṣṇu Purāṇa. This is a useful *cosmological trope* for your engine, but it should be tagged as later textual tradition rather than early Vedic. citeturn40search2

### Metre × purpose

This is where your generator can be most reliable, because purposes correspond to genre practice:
- Sutra-style is explicitly defined in modern reference works as an aphoristic, condensed manual genre of short rules. citeturn43search0turn43search4
- Bhāṣya is a commentary/exposition genre that explains terse root texts and typically includes interpretive expansions and citations. citeturn43search9turn43search5
- Campū is explicitly mixed prose–verse with verse for high-description intensity. citeturn43search3

### Metre × time of day and Soma-pressing bandhu

A robust Vedic anchor for time-of-day mapping is the Soma ritual mythos where metres are linked to **morning/midday/evening pressings** (prātaḥ/mādhyandina/sāyam savana). The “Chandas as Vedanga” source narrates this in its Soma-bringing myth discussion, explicitly connecting Gāyatrī with morning pressing, Triṣṭubh with the process after it, and Jagatī with later aspects. citeturn38view3  
For many modern users, Gāyatrī recitation is also centered on the three sandhyās (dawn, midday, dusk), which can be used as a practical alignment layer in generation. citeturn36search4turn36search0

### Coherence rules as IF–THEN with weights

The matrix CSV already stores these as edges; below is a compact rule layer in the form you requested (weights are tunable; evidence labels shown):

```text
IF deity = Sūrya/Savitṛ AND time_of_day = dawn
THEN prefer metre = VED_GAYATRI coherence = 0.95  [OBSERVED: Sāvitrī-gāyatrī + sandhyā practice]

IF rasa = vīra AND purpose IN {praise, heroic proclamation}
THEN prefer metre = VED_TRISTUBH coherence = 0.85  [OBSERVED/INTERPRETATION: Indra + might/vigour]

IF purpose = cosmology OR purpose = expansive-world-description
THEN prefer metre = VED_JAGATI coherence = 0.80  [INTERPRETATION: 12-syll flowing cadence; “all-encompassing” ritual praise]

IF mood = longing OR rasa = śṛṅgāra(vipralambha) AND time_of_day = evening
THEN prefer metre = CLS_MANDAKRANTA coherence = 0.85  [OBSERVED: Meghadūta / love-in-separation suitability]

IF purpose = teaching AND tradition IN {Vedānta, Yoga-darśana, śāstra}
THEN prefer form = PROSE_SUTRA coherence = 0.85  [OBSERVED: aphoristic sūtra genre]
AND prefer metre = CLS_ANUSTUBH_SLOKA coherence = 0.75  [INTERPRETATION: didactic śloka usage]

IF purpose = commentary OR mode = archaeology
THEN prefer prose = PROSE_BHASHYA coherence = 0.85  [OBSERVED: bhāṣya genre as exposition of terse text]

IF mode = fiction AND target_register IN {Purāṇic, epic}
THEN prefer macroform = PROSE_PURANIC with verse_peaks = CLS_CAMPU coherence = 0.85  [INTERPRETATION + OBSERVED campū definition]

IF mode = vastu OR ritual_instruction = true
THEN prefer prose = PROSE_AGAMIC coherence = 0.90  [OBSERVED: āgama texts describe worship/temple/ritual practice]
```

## Prose styles and register calibration

### Sutra style

A sutra is classically defined as a condensed, aphoristic rule-text, a “theorem distilled into few words,” designed so teachings can be “woven” around it. citeturn43search0turn43search4  
For generation: use short nominal clauses, minimal connectives, high compound density, and predictable topic-markers (e.g., “atha,” “iti”).

### Bhāṣya style

A bhāṣya is a genre of commentary/exposition that explains terse root texts; descriptions emphasize word-meaning explanation, interpretive expansion, and engagement with prior views. citeturn43search9turn43search5  
For generation: implement a canonical argument loop (quotation → gloss → inference → objection → resolution).

### Purāṇic narrative prose

For your engine, treat “Purāṇic” less as a single prose grammar and more as a **macro-style**: frame narration, embedded tales, genealogical expansions, and formulaic transitions (“atha,” “tataḥ,” “iti ha sma”). A minimal observed anchor is that Itihāsa–Purāṇa literature is explicitly characterized by embedded tale structures and narrative authority traditions. citeturn43search6  
The detailed stylistic features (heavy epithets, deliberate repetition) should be tagged INTERPRETATION unless you attach them to a specific corpus analysis.

### Āgamic technical prose

Āgama texts are described as including deity worship procedures, mantras, temple construction, and practice instructions across Śaiva, Vaiṣṇava, and Śākta traditions. citeturn44search6  
For generation: the distinctive feature is procedural sequencing (step-by-step), which you can implement as a graph walk producing imperative/optative instruction clauses.

### Modern Sanskrit prose

Modern Sanskrit literature includes a wide range of forms (poems, dramas, novels, travelogues, biographies, scientific works, magazines, online publications), and twentieth-century production is highlighted as especially prolific in at least one modern teaching module. citeturn45search0  
For a research-backed modern framing, recent scholarship also emphasizes modern Sanskrit writers’ engagement with contemporary issues and experimentation with genres. citeturn45search8

### Register levels as generator control

A practical “register ladder” you requested:
- **Vedic register (most sacred/archaic):** strict syllable counts, controlled compounding, avoid later philosophical vocabulary; optionally store lexical accent separately because metre is not defined by it. citeturn22view0  
- **Classical kāvya register:** vṛtta metres with gaṇas; dense imagery; alaṃkāra-heavy.
- **Epic/Purāṇic register:** simpler syntax than kāvya; narrative continuity; formulaic transitions.
- **Vernacular devotional register:** direct address, emotionally warm, refrain-friendly.
- **Modern English + Sanskrit terms:** treat Sanskrit words as semantic anchors; keep cadence via English prosody or constraint-lite stanza templates.

## Vernacular devotional forms and integration patterns

### Hindi/Braj: Chaupāī and Dohā in devotional epics

A standard description of **chaupāī** identifies it as a quatrain with a 16/16 count (counted in mātrā units), and notes its importance in medieval Hindi poetry including Tulsidas and Hanuman Chalisa traditions. citeturn32search2  
Academic discussion of Rāmcaritmānas structure describes it as primarily chaupāī, separated by dohā (and occasional other metres). citeturn32search9

For **dोहā**, there is a common Hindi prosody rule of 13+11 mātrās (not 24+26). Because your spec requested “24+26,” the CSV records:
- the **standard pattern** as OBSERVED for Hindi teaching practice,
- “24+26” as a **nonstandard claim** to be stored (if needed) with a lower confidence flag and only enabled if your project’s internal tradition requires it.

### Tamil: Veṇpā and the couplet engine

Veṇpā is a classical Tamil prosody form governed by formal metric rules; a major corpus example is that all 1330 Tirukkuṟaḷ couplets are in a veṇpā subtype (“kural veṇpā”). citeturn31search2  
If you want this in a generator, do not shoehorn it into Sanskrit laghu/guru; treat it as a separate constraint grammar (ner/nirai, seer endings).

### Telugu: Kṛti/Kīrtana as a performance-first form

A conventional Carnatic **kṛti** is structurally segmented into pallavi (refrain), anupallavi, and caraṇam, and this structure is stable enough to store as a macro-form schema for generation. citeturn31search3  
This can be paired with rāga/time-of-day mapping if you later add music constraints.

---

## Included deliverables

- [Download metres_and_forms.csv](sandbox:/mnt/data/metres_and_forms.csv)  
  Contains: Vedic 7 + major Classical metres + vernacular forms + prose styles, with L/H patterns, cadences, caesura, usage notes, and OBSERVED/INTERPRETATION/SPECULATIVE labels.

- [Download metre_correspondence_matrix.csv](sandbox:/mnt/data/metre_correspondence_matrix.csv)  
  Contains: weighted edges for metre × rasa × deity × purpose × time/panchanga hints (as rules-ready structured data).

