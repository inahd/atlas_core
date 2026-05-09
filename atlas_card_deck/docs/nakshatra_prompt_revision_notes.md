# Nakshatra Card Prompts — v1 to v2 Revision Notes

**Date**: 2026-04-23

---

## What changed

| Area | v1 | v2 |
|------|----|----|
| Style anchor | "Vedic infographic tarot card" (no training signal) | "Rajput miniature painting, Mewar school" (strong signal in all generators) |
| Deity description | "standing or seated in composed posture" (generic, same for all 27) | Per-deity canonical iconography (27 unique descriptions) |
| Plant integration | "leaves or flowers woven into border" (identical for all 27) | Per-plant visual cues with species-specific features |
| Yoni animal | "appears at base or flanking" (uniform placement) | Role-based: vahana / companion / ambient / emblematic |
| Color language | Hex codes (#8d784f) — ignored by generators | Natural language ("warm bronze-brown") |
| Negative prompt | 8 terms | 14 terms — added RWS, anime, Disney, digital painting, devanagari script |

---

## Deity iconography lookup (27 entries)

| Nakshatra | Deity | Iconographic description | Variant choice note |
|-----------|-------|------------------------|---------------------|
| Ashwini | Ashwini Kumaras | Twin horse-headed physicians, healing vessels | Standard twin form. Not the later human-faced variant. |
| Bharani | Yama | Dark-skinned, buffalo vahana, noose + staff, red | Standard dharmaraja form. Not the wrathful Tibetan variant. |
| Krittika | Agni | Red-skinned, seven flame-tongues, ram vahana, ghee ladle | Vedic fire-god form. Not the two-headed post-Puranic form. |
| Rohini | Brahma | Four-headed, four-armed, lotus seat, Vedas + kamandalu | Standard Prajapati form. Chose seated (calmer) over standing. |
| Mrigashira | Soma | Cool-blue, amrita chalice, crescent moon, antelope | Lunar Soma, not the plant. Antelope is his traditional seat. |
| Ardra | Rudra | Three-eyed, tiger-skin, trident + damaru, ash-smeared | Pre-Puranic Rudra (fierce ascetic), not the benevolent Shiva-Nataraja. |
| Punarvasu | Aditi | Maternal cosmic mother, twelve-sun halo | Vedic Aditi (boundless mother). No standard iconographic form exists; this is synthesis from textual descriptions. |
| Pushya | Brihaspati | Golden, chin-beard, danda + rosary, lotus seat | Guru of devas form. Not the graha-Brihaspati (Jupiter planet). |
| Ashlesha | Nagas | Multi-hooded serpent deities, jeweled hoods | Collective Naga form. Not Shesha or Vasuki specifically. |
| Magha | Pitris | Three elder ancestors, white garments, offerings | Collective ancestor form. No single standard iconography; composed from shraddha ritual descriptions. |
| Purva Phalguni | Bhaga | Red-gold, lotus, dawn light | Aditya form. Bhaga has minimal independent iconography; adapted from Vedic hymns (RV 7.41). |
| Uttara Phalguni | Aryaman | Golden, chariot, contract scroll | Aditya form. Aryaman has minimal independent iconography; "friend-god on chariot" from RV descriptions. |
| Hasta | Savitar | Solar-golden, two right hands in blessing | Vedic Savitar (impeller). Distinct from Surya — Savitar specifically associated with hand gestures (RV 5.81). |
| Chitra | Tvashtar | Architect-artisan, hammer + compass, mandala | Vedic Tvashtar (craftsman of the gods). Chose artisan form over father-of-Vritra variant. |
| Swati | Vayu | Blue-green, striding, banner, wind-swept | Standard wind-god form. Not the Hanuman father aspect. |
| Vishakha | Indra-Agni | Dual figure — Indra with vajra (right) + Agni with flame (left) | Composite deity; no single standard image. Designed as split-throne composition. |
| Anuradha | Mitra | Solar, golden, lotus + sun disc, chariot | Aditya form. Mitra has minimal independent iconography; composed from Vedic paired-with-Varuna descriptions. |
| Jyeshtha | Indra | Crowned, vajra, white elephant Airavata | Standard king-of-devas form. Chose regal seated (not warrior charging). |
| Mula | Nirriti | Dark fierce goddess, dog/crow, roots + skull | Chose goddess form (shakti tradition) over the male Nirrti variant. Southwest directional guardian. |
| Purva Ashadha | Apas | Three water nymphs, conch + lotus, turquoise | Collective water-deity form. "Apas" is plural; rendered as three figures. |
| Uttara Ashadha | Vishvadevas | Ten devas assembled, sunburst | Collective form. No standard unified iconography; designed as assembly composition. |
| Shravana | Vishnu | Dark-blue, four-armed, conch/discus/mace/lotus | Standard chaturbhuja Vishnu. Chose standing (sthanaka) over reclining (anantashayana). |
| Dhanishta | Vasus | Eight elemental deities in circle, instruments | Collective form. Vasus rarely depicted as group; designed from textual listing of eight. |
| Shatabhisha | Varuna | Blue-black, noose, makara vahana, oceanic | Standard ocean-lord form. Post-Vedic (Puranic) variant with makara. |
| Purva Bhadrapada | Aja Ekapada | One-footed goat-headed, fire, lightning | Rare deity with minimal standard iconography. Composed from name etymology (aja=goat, ekapada=one-footed). |
| Uttara Bhadrapada | Ahirbudhnya | Great serpent, coiled, oceanic depths | Name means "serpent of the deep." No standard visual form; composed from textual description. |
| Revati | Pushan | Golden nourisher, goad, pastoral | Vedic Pushan (path-guardian, cattle-herder). Chose pastoral over the toothless-old-man variant in later texts. |

---

## Plant cue lookup (27 entries)

| Nakshatra | Plant | Visual cue |
|-----------|-------|-----------|
| Ashwini | Ashwagandha | Low shrub, small red-orange berries, oval green leaves |
| Bharani | Amla | Round ribbed green gooseberries, feathery pinnate leaves |
| Krittika | Fig | Round figs clustered on trunk/branches, broad lobed leaves |
| Rohini | Jasmine | White five-petaled star flowers, deep green leaves |
| Mrigashira | Khadira | Thorny acacia, small yellow pom-pom flowers, pinnate leaves |
| Ardra | Agarwood | Dark resinous wood fragments, small white flowers |
| Punarvasu | Bamboo | Tall segmented green culms, narrow leaves |
| Pushya | Peepal | Heart-shaped leaves with drip-tips, fluttering |
| Ashlesha | Nagakesara | Waxy white four-petaled flowers, golden stamen clusters |
| Magha | Banyan | Broad canopy, descending aerial roots, oval leaves |
| Purva Phalguni | Palasha | Brilliant orange-red flowers on bare branches, trifoliate leaves |
| Uttara Phalguni | Rudraksha | Blue-brown ridged berries, elliptic leaves |
| Hasta | Soapnut | Round brown fruits, pinnate compound leaves |
| Chitra | Bael | Trifoliate bilva leaves (three pointed leaflets), yellow-green fruit |
| Swati | Arjuna | Bark strips, small pale flower clusters |
| Vishakha | Wood Apple | Hard round fruit, compound leaves |
| Anuradha | Tulsi | Small dark-green aromatic leaves, purple stems, tiny flower spikes |
| Jyeshtha | Silk Cotton | Red flowers on thorny trunk, kapok pods splitting |
| Mula | Sal | Broad leaves, small cream-yellow flowers |
| Purva Ashadha | Lotus | Open pink blooms, round floating leaves |
| Uttara Ashadha | Jackfruit | Large oblong spiny fruit, broad dark leaves |
| Shravana | Arka | Waxy purple-white five-petaled blooms, thick round leaves |
| Dhanishta | Shami | Tiny bipinnate leaves, small yellow flower clusters |
| Shatabhisha | Kadamba | Spherical orange flower-balls, broad round leaves |
| Purva Bhadrapada | Mango | Lance-shaped leaves in red-green new-growth, small fruit |
| Uttara Bhadrapada | Neem | Pinnate compound leaves, small white flower sprays |
| Revati | Mahua | Fleshy cream-yellow flowers dropping from branches |

---

## Yoni role assignments (27 entries)

| Nakshatra | Yoni animal | Role | Reasoning |
|-----------|-------------|------|-----------|
| Ashwini | Horse (m) | companion | Horses flank twin physicians — both are equine-natured |
| Bharani | Elephant (m) | vahana | Yama rides buffalo (his vahana); elephant as separate guardian at base |
| Krittika | Sheep (m) | vahana | Agni rides ram — ram IS the sheep yoni; double duty |
| Rohini | Serpent (m) | ambient | Brahma on lotus; serpent in jasmine vines below — not foregrounded |
| Mrigashira | Serpent (f) | ambient | Soma on deer; serpent subtle in grass; deer-head symbol at top resolves deer/serpent |
| Ardra | Dog (f) | companion | Rudra's dog (Sarama's progeny tradition); loyal at side in storm |
| Punarvasu | Cat (m) | ambient | Aditi has no animal association; cat rests in bamboo — subtle |
| Pushya | Sheep (f) | ambient | Brihaspati on lotus; sheep grazes beneath peepal — pastoral |
| Ashlesha | Cat (f) | emblematic | Nagas ARE serpents (deity=symbol); cat as separate yoni marker at base |
| Magha | Mouse (m) | ambient | Ancestral throne scene; mouse near offerings — Ganesha resonance |
| Purva Phalguni | Mouse (f) | ambient | Hammock scene; tiny mouse nestled in folds — whimsical |
| Uttara Phalguni | Cow (m) | companion | Bull beside Aryaman's chariot — dharmic pair |
| Hasta | Buffalo (m) | ambient | Savitar is solar/aerial; buffalo in field behind — grounded contrast |
| Chitra | Tiger (m) | companion | Tiger at Tvashtar's workbench — Mars-ruled power beside craft |
| Swati | Buffalo (f) | ambient | Vayu is wind/motion; buffalo as grounded silhouette — contrast |
| Vishakha | Tiger (f) | ambient | Tigress prowling under arch — ambition stalking toward goal |
| Anuradha | Hare (m) | companion | Gentle hare beside gentle Mitra — friendship pair |
| Jyeshtha | Hare (f) | ambient | Hare crouched at base of Indra's elephant — small/large contrast |
| Mula | Dog (m) | companion | Nirriti traditionally associated with dogs; dog at side in roots |
| Purva Ashadha | Monkey (m) | ambient | Monkey on branch above water nymphs — playful elevation |
| Uttara Ashadha | Mongoose (f) | ambient | Mongoose among rocks at assembly base — serpent-enemy subtlety |
| Shravana | Monkey (f) | ambient | Monkey in listening pose — echoes Vishnu's teaching |
| Dhanishta | Lion (m) | companion | Lion among eight Vasus — Mars-ruled regality |
| Shatabhisha | Horse (f) | ambient | Mare at ocean shore behind Varuna — horse meets water |
| Purva Bhadrapada | Lion (f) | companion | Lioness at base of fire deity — fierce guardianship |
| Uttara Bhadrapada | Cow (f) | ambient | Cow resting on shore above ocean depths — Saturn patience |
| Revati | Elephant (f) | companion | Elephant walking beside Pushan — gentle giant on the path |

---

## Deities with iconographic variant decisions

| Deity | Chosen variant | Rejected variant | Reason |
|-------|---------------|------------------|--------|
| Agni | Vedic fire-god (seven tongues, ram) | Two-headed post-Puranic | Vedic form is more distinctive; two-headed rarely depicted in miniature tradition |
| Rudra | Pre-Puranic fierce ascetic | Benevolent Shiva-Nataraja | Ardra = storm/destruction; Rudra's fierce form matches the nakshatra's character |
| Soma | Lunar deity (blue, amrita, moon) | Soma plant | Deity form is visually generative; plant form is abstract |
| Nirriti | Goddess form (shakti tradition) | Male Nirrti | Goddess form is more visually distinct and matches the fierce dissolution theme |
| Indra (Jyeshtha) | Regal seated king | Warrior charging on elephant | Elder authority (Jyeshtha = eldest) matches seated composure better than battle |
| Vishnu (Shravana) | Standing (sthanaka) | Reclining (anantashayana) | Vertical card format suits standing; listening theme suits alert upright pose |
| Pushan | Pastoral nourisher | Toothless old man (later Puranic) | Pastoral form matches Revati's gentle prosperity; old-man form is less visually useful |
| Aditi | Maternal with twelve-sun halo | Abstract cosmic mother | Halo gives visual concreteness; pure abstraction produces generic output |
| Aja Ekapada | Goat-headed one-footed fire deity | Abstract cosmic pillar | Name etymology gives workable visual; abstract form is unrenderable |
| Ahirbudhnya | Great coiled serpent in ocean depths | Abstract cosmic serpent-principle | Coiled-in-ocean is paintable; abstract principle is not |
