#import "../_shared/preamble.typ": compendium-preamble, title-page

#compendium-preamble(
  title: "Svarodaya and the Breath Clock",
  subtitle: "Field Dive",
  version: "1.0 — converted from markdown",
)

#title-page(
  title: "Svarodaya and the Breath Clock",
  subtitle: "Nadi, element, and svara rules for temporal breath",
  volume: "COHERENCE ATLAS · FIELD DIVE",
  version: "1.0 · April 2026",
)

#v(0.6in)
#align(center)[#text(size: 11pt, weight: "semibold")[Status]]
#v(0.4em)

_Converted from `research/research_svara_shastra.md`. Content-lossless conversion._

#pagebreak()

#outline(
  title: [#text(size: 12pt, weight: "semibold")[Contents]],
  indent: 1.8em,
  depth: 2,
)

#pagebreak()

// ─── CONVERTED CONTENT ──────────────────────────────────

= Svara Shastra Structured Dataset for an NPU Knowledge Graph


== Corpus, scope, and attestation model


=== Primary-text scope used for extraction

The structured data below is grounded primarily in _Śiva Svarodaya / Shiva Svarodaya_ (a tantric text framed as a dialogue between Shiva and Parvati) and secondarily cross-checked with _Gorakṣaśataka / Goraksha Shataka_ for nadi metadata. citeturn21search0turn17view2

The working “primary” source in this build is an openly hosted OCR text of _Shiva Svarodaya with an English translation_, which includes _(a) translated verses_ and _(b) an extended “Introduction”/prefatory material_ containing practical tables and rules (including cycle durations, tithi-from-sunrise schedules, and health notes). Because those two layers are not equally authoritative, they are separated in the dataset via _attestation_status_ and (when needed) _variant_id_. citeturn8view0turn20view0turn12view0

=== Attestation vocabulary implemented in the data

Each row in the CSVs has _attestation_status_ and _knowledge_status_, designed to fit your requested _OBSERVED / INTERPRETATION / SPECULATIVE_ labeling.

_knowledge_status_
- _OBSERVED_: directly asserted in the cited passages (verse text or clearly marked instruction in the translation’s prefatory layer).
- _INTERPRETATION_: synthesized (e.g., combining a nadi-activity rule with an element-activity rule), or resolving conflicts via a documented “variant”.
- _SPECULATIVE_: added to make the NPU usable (e.g., numeric coherence scores), or modern extrapolations not explicitly stated in the primary passages.

_attestation_status_
- Flags whether a row is based on translated verse content, translation-introduction tables, cross-text corroboration (e.g., Goraksha Shataka), or inference.

This is necessary because (for example) _element-cycle durations_ and _element-order sequences_ occur in _multiple conflicting forms_ across layers of the source. The dataset preserves both where defensible rather than forcing a single truth. citeturn10view0turn8view0turn20view0

== Nadi system schema and extracted assertions


=== Core nadi definitions mapped into the schema

Shiva Svarodaya’s translation layer explicitly defines:
- _Ida = left nostril flow_, also termed _Moon-svara_
- _Pingala = right nostril flow_, also termed _Sun-svara_
- _Sushumna = both nostrils simultaneously or erratic alternation_ citeturn8view0

The text also states that the _Moon is the controller/resident of the left nadi (Ida)_ and the _Sun is controller/resident of the right nadi (Pingala)_. citeturn10view0

Goraksha Shataka (in the consulted translation) states that _Ida, Pingala, and Sushumna_ have presiding deities _Moon, Sun, and Fire (Agni)_ respectively, and explicitly places _Ida left / Pingala right / Sushumna middle_. citeturn17view2

Because “Sushumna = fire” is explicitly stated in Goraksha Shataka but not uniformly in the Shiva Swarodaya passages used here, _sushumna.graha_correspondence_ is represented as a multi-tradition field in `nadis.csv` (with attestation marking). citeturn17view2turn8view0

=== Activity polarity by nadi

Shiva Swarodaya provides strong categorical guidance:
- _Ida (Moon/left)_ is associated with _good/amiable/auspicious works_. citeturn10view0turn19view0
- _Pingala (Sun/right)_ is associated with _cruel/daring/moving works_, and a long list including travel/hunting/war-like actions; the same source layer also explicitly lists _eating, increasing digestive fire, and sleeping_ as “best” under Pingala. citeturn10view0turn19view0
- _Sushumna_ is repeatedly treated as _unsafe/inauspicious for ordinary works_ (worldly works become infructuous), while _yogic practice/dhyana/remembrance of the Supreme_ is recommended. citeturn19view0turn20view0

These are encoded in `nadis.csv` fields:
`activities_favored`, `activities_avoid`, and `health_indications` (with `knowledge_status` showing which parts are direct vs inferred).

=== Day–night yogic discipline rule

A key discipline rule appears in the Shiva Swarodaya passages consulted: _avoid Moon-svara at night and avoid Sun-svara in the day_ (framed as a yogic practice standard). citeturn23view0turn16view0
This is stored under `time_of_dominance` and `activities_avoid` (Ida/Pingala) with direct attestation.

== Five-element system and detection rules


=== Element detection signals extracted

Shiva Swarodaya provides multiple _how_to_detect_ modalities for the five elements, including:
- _nostril-region test_ (central = earth; lower = water; top = fire; side/oblique = air; rotating = ether) citeturn20view0turn23view2
- _mirror-condensation “haze” shape_ (square/half-moon/triangular/dotted patterns) citeturn20view0
- _color associations_ (water white, earth yellow, fire red, air blue; ether cloud-like/mixed) citeturn20view0
- _taste associations_ (earth sweet; water saline; fire bitter; air sour; ether pungent) citeturn20view0turn18view0
- _“reach/length” of exhalation_ in finger-widths (water ~16, earth ~12, air ~8, fire ~4) citeturn20view0turn18view0

All of these are encoded into `elements.csv.how_to_detect`, using short paraphrases to avoid long quotations (and to stay within reproducible KG-friendly strings). citeturn20view0turn18view0

=== Element outcome rules (auspiciousness + activity types)

The extracted Shiva Swarodaya passages strongly differentiate element outcomes:
- _Earth and Water_ are called _auspicious_ in multiple places, with Earth frequently linked to fixed/stationary and prosperity-oriented undertakings. citeturn18view0turn20view0
- _Fire_ is repeatedly tied to _cruel/daring_ actions and is also described as dangerous in some passages (e.g., “death from Fire element” appears in one place). citeturn20view0turn18view0
- _Air/Wind_ is linked to _movement/roving activity_ in one passage, while another passage frames air-conditions as destructive/loss-inducing; both are preserved as “ambiguous” at the narrative level and encoded as conservative recommendations in the activity matrix. citeturn20view0turn18view0
- _Ether (Akasa)_ is repeatedly described as making worldly actions _infructuous/blank_, while explicitly allowing _yoga-sadhana_ during its dominance. citeturn20view0turn18view0

These become the backbone of the `activity_matrix.csv` synthesis rules and are directly recorded per element row in `elements.csv`. citeturn20view0turn18view0

=== Preserving conflicting cycle orders and durations

Your prompt specifies the common _20/16/12/8/4_ minute pattern (Earth/Water/Fire/Air/Ether). This appears in the consulted Shiva Swarodaya translation’s _introductory_ tables and is included as the variant `cycle_var_20_16_12_8_4`. citeturn6view0turn8view0

However, another Shiva Swarodaya passage states an element order _Air → Fire → Earth → Water → Ether_ and also says elements rule _for half a ghaṭī_ within a _2.5 ghaṭī_ segment, which implies an _equal-duration_ reading in that verse-context. This is preserved as the separate variant `cycle_var_equal_12_order_air_fire_earth_water_ether` in `element_cycles.csv`. citeturn10view0turn23view0

This “multiple-variants” approach is intended to be KG-safe: your graph can either (a) select one variant globally for an experiment, or (b) keep both and resolve at query-time.

== Swara across tithi and vara


=== Tithi × swara

The consulted Shiva Swarodaya material contains two kinds of tithi-related content:

The translation-introduction schedule states that, _from sunrise onward in the bright fortnight_, specific tithis should begin with _left_ (1–3, 7–9, 13–15) and others with _right_ (4–6, 10–12), and then asserts the “same schedule” for the dark fortnight. citeturn8view0turn7view0

Separately, a Shiva Swarodaya verse-context passage states:
- _bright fortnight begins with Moon-svara (left)_
- _dark fortnight begins with Sun-svara (right)_
and treats reversal as inauspicious. citeturn10view0turn23view0

Because these can be read as tension between “same schedule” vs “opposite starts,” `tithi_rules.csv` includes _two variants_:
- `tithi_intro_same_both_paksha` (OBSERVED from the schedule statement)
- `tithi_inferred_invert_dark_paksha` (INTERPRETATION: inverting dark-fortnight sunrise mapping to respect the “dark begins with Sun-svara” statement)

For “wrong nadi active,” the material explicitly associates:
- bright-fortnight day 1 wrong-sided start with heat-type disease/strife/loss up to full moon, and
- dark-fortnight day 1 wrong-sided start with cold-type disease/loss/distress. citeturn12view0turn10view0

=== Vara × swara

Shiva Swarodaya states that _left-nadi is auspicious on Monday, Wednesday, Thursday, and Friday_, and that _right-nadi is favorable for roving business on Sunday, Tuesday, and Saturday_ (with paksha modifiers). citeturn10view0turn23view2

Because your prompt requests a complete _Sunday→Pingala, Monday→Ida…_ mapping, the dataset treats the above as the governing partition and assigns each weekday an expected nadi in `vara_rules.csv` (with `knowledge_status=INTERPRETATION` because the text is explicit for the partition, but not phrased as a sunrise-only rule for all activities). citeturn10view0turn7view1

For deviations, the text describes “adverse svara since morning” as producing escalating harms (anxiety → wealth loss → unwanted travel → etc.). This is used as the deviation interpretation in `vara_rules.csv.deviation_indicates`. citeturn11view0turn7view1

== Activity recommendation matrix


=== How the matrix was constructed

Shiva Swarodaya explicitly classifies works into _three svara categories_ (left/right/sushumna) and also gives _elemental success/failure heuristics_. citeturn19view0turn20view0

The requested full matrix `activity × nadi × element → recommendation` is therefore built by:
- anchoring each _activity_ to text-supported _nadi polarity_ when possible (e.g., eating/sleep under pingala; meditation under sushumna), citeturn19view0turn10view0
- anchoring _element suitability_ using the Earth/Water auspiciousness, Fire/Air risk, Ether “blank except yoga” constraints, citeturn20view0turn18view0
- marking the final row as OBSERVED only when the combination is explicitly supported (e.g., meditation under sushumna), and otherwise as INTERPRETATION or SPECULATIVE depending on distance from the text.

This yields `activity_matrix.csv` with _210 rows_ (14 activities × 3 nadis × 5 elements). Many entries are intentionally conservative because the source material does not enumerate a full Cartesian product. citeturn19view0turn20view0

=== Notable directly supported anchors

- _Meditation / dhyāna under sushumna_ is directly recommended in the consulted introduction list. citeturn19view0turn20view0
- _Eating + sleep under pingala_ is directly asserted. citeturn19view0
- _No worldly work under ether (akasa)_; yoga-sadhana allowed. citeturn20view0turn18view0

These are flagged as higher-confidence anchors in the matrix’s `knowledge_status`.

== Health diagnosis patterns and swara-switching techniques


=== Health-diagnostic claims extracted

The dataset includes explicit Shiva Swarodaya claims such as:
- diseases arising when svara timing/day patterns do not adhere to the fixed rules (and cure via correction), citeturn15view0
- element-imbalance linkages (e.g., earth disturbance linked to jaundice-like diseases and phobia-like mental disturbances; air disturbance linked to asthma), citeturn8view0turn15view0
- “adverse svara since morning” escalation outcomes, citeturn11view0turn7view1
- omen-style death forecasts (e.g., single-nostril dominance through the night; pingala dominance for consecutive nights; etc.). citeturn16view0turn23view1

These appear in `health_diagnosis.csv` as _traditional diagnostic/omen statements_; they are not clinical claims. (The dataset labels them as OBSERVED only in the sense “attested in text.”) citeturn16view0turn15view0

=== Dosha mapping layer

Your request includes “dosha imbalances.” The Shiva Swarodaya passages used here discuss element disturbances and diseases but do not consistently use Ayurveda’s _tridosha_ vocabulary. Therefore, the dosha relationships are encoded explicitly as a _mapping layer_ drawn from Ayurveda references (e.g., Vata = air+ether; Pitta = fire+water; Kapha = earth+water), and the dataset labels that mapping as _INTERPRETATION_ (not primary-text). citeturn21search14turn21search7

=== Swara switching techniques extracted

Shiva Swarodaya’s translation-introduction gives explicit behavioral methods:
- _side-lying to change active nostril_ (to induce the opposite nostril), citeturn8view0turn14view0
- _stopping a nostril_ by side-lying and/or _soft cotton in the nostril_ (therapeutic framing), citeturn15view0turn15view2
- “practice frequent switching” as a longevity/youth claim. citeturn15view1

Goraksha Shataka also contains a pranayama-style instruction consistent with _alternate nostril practice_, and claims that nadi cleansing yields health benefits. citeturn17view0turn17view2

These are encoded in `swara_switching_techniques.csv` with evidence levels and attestation tags.

== NPU coherence rules and deliverable files


=== Coherence rules

The required “NPU coherence rules” are implemented in `npu_coherence_rules.csv` with:
- rule-like IF conditions written as KG-friendly logical strings,
- numerical _coherence_ values (explicitly marked _SPECULATIVE_ because the texts do not provide numbers),
- recommended actions (e.g., switch_to_ida) derived from the source’s preference rules. citeturn10view0turn20view0

Examples in the file include weekday–nadi alignment (vara) and a peak meditation rule combining _sushumna + ether_ (qualitative support in Shiva Swarodaya; numeric score is modeling). citeturn19view0turn20view0

=== Output

[Download the CSV bundle](sandbox:/mnt/data/svara_shastra_npu_knowledge_graph_csv.zip)

The ZIP contains:
- `sources.csv`
- `nadis.csv`
- `elements.csv`
- `element_cycles.csv`
- `tithi_rules.csv`
- `vara_rules.csv`
- `activity_matrix.csv`
- `health_diagnosis.csv`
- `swara_switching_techniques.csv`
- `npu_coherence_rules.csv`

The _Schema fields you requested_ are present in the relevant tables (notably `nadis.csv` and `elements.csv`), and each row includes `source_text`, `attestation_status`, and a KG-ready `knowledge_status` label.
