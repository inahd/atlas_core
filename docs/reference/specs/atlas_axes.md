# Coherence Atlas — Four Axes

The field has four axes. The first three encode position.
The fourth holds them.

---

## Axis 1: theta — Vertical (Time / Level)

**Encodes:** Level of manifestation
**Range:** S0 (unmanifest) to S6 (fully embodied)
**Toroid:** Major axis theta, 0 to 2pi

```
S0  Bindu     Source, pure potential
S1  Archetype Deity, yantra, first form
S2  Sound     Raga, tala, bija, nada
S3  Rhythm    Panchanga, dasha, muhurta
S4  Geometry  Vastu, yantra, mandala
S5  Nature    Ayurveda, plants, dosha, marma
S6  Lila      Practice, codex, altar, art
```

S6 wraps to S0. Lila IS Bindu experienced from within.

Defined in: TWO_AXIS_FIELD_SPEC.md (Bead 009)

---

## Axis 2: phi — Horizontal (Witness / Participant)

**Encodes:** Mode of engagement
**Range:** Pure witness (phi = 0) to pure participant (phi = 2pi)
**Toroid:** Minor axis phi, 0 to 2pi

```
FAR LEFT     Pure witness, Shiva, jnana, ether
LEFT         Witnessing with recognition, air
CENTER-LEFT  Contemplative engagement, water
CENTER       Union point, bindu of phi, Bherunda
CENTER-RIGHT Engaged action with awareness, fire
RIGHT        Full participant, earth
FAR RIGHT    Pure action, Shakti, karma (wraps to witness)
```

Shilpi lives LEFT (phi < pi). Bandhu lives RIGHT (phi > pi).

Defined in: TWO_AXIS_FIELD_SPEC.md (Bead 009)

---

## Axis 3: S-layer — Depth (Domain)

**Encodes:** Which ring of the cosmos an entity renders on
**Range:** S0 through S6 (discrete)
**Independence:** An entity's S-layer is independent of its theta and phi

Defined in: CLAUDE.md, S0-S6 Layer System

---

## Axis 4: path — Bheda-Abheda (Unity / Distinction)

**Encodes:** Position on the axis between non-difference and difference
**Range:** 0.0 to 1.0 (continuous float)
**Nature:** This axis holds the other three

```
0.0   Pure abheda (non-difference)
      Advaita. Unity. No separation between jiva and Brahman.
      The field before names.

0.1   Advaita zone
      Shankara. Nirguna Brahman. Maya as illusion.
      Entity: advaita

0.15  Rahu (shadow that dissolves boundaries)

0.2   --

0.25  Shakta zone
      The goddess as non-different power.
      Entity: shakta
      Graha: Chandra (mind reflecting source)

0.3   Shaiva zone / Water element
      Shiva as consciousness. Shakti as his power, not separate.
      Entity: shaiva
      Graha: Shukra (beauty as divine quality)
      Element: water

0.35  Vishishtadvaita zone
      Ramanuja. Qualified non-difference.
      Part and whole are real, part is dependent.
      Entity: vishishtadvaita
      Graha: Shani (form that serves the whole)

0.4   Earth element

0.5   BINDU — Acintya-bheda-abheda
      Gaudiya. Inconceivable simultaneous oneness and difference.
      Holds the ENTIRE axis without resolving it.
      The field state. The neutral coordinate.
      Entity: gaudiya
      Graha: Budha (Mercury — the messenger, holds both)
      Element: ether

0.6   Guru zone / Air element
      Jupiter. The teacher who distinguishes to illuminate.
      Graha: Guru
      Element: air

0.7   Fire element / Surya zone
      Illumination through distinction. Light that reveals form.
      Graha: Surya
      Element: fire

0.8   Dvaita zone
      Madhva. Pure difference. Jiva eternally distinct from Vishnu.
      The devotional relationship requires two.
      Entity: dvaita / madhva
      Graha: Mangala (Mars — the warrior who serves his Lord)

0.9   --

1.0   Pure bheda (difference)
      Maximum distinction. Pure devotional otherness.
      "You are You and I am I" — the rasa of separation.
```

### Why path holds the other three

Theta says WHEN (which level of manifestation).
Phi says HOW (witness or participant).
S-layer says WHERE (which domain ring).
Path says FROM WHAT STANCE the entity exists at all.

An entity at path=0.1 experiences S2-Sound as vibration
dissolving into silence — nada merging into Brahman.

The same entity type at path=0.8 experiences S2-Sound as
the flute of Krishna calling the gopis — irreducibly relational,
the beloved addressing the lover.

Both are real. Both are sound. The path coordinate determines
which sound.

Gaudiya (path=0.5) holds both simultaneously: the flute IS
the silence. Acintya-bheda-abheda. This is not a compromise
at the midpoint — it is the recognition that the axis itself
is a lila.

### Derivation for composite entities

For entities without an explicit path value, derive from components:

```
path = 0.6 * graha_path(ruler) + 0.4 * element_path(element)
```

Element path values:
```
ether  0.5   (neutral, holds space for both)
air    0.6   (carries, distinguishes subtly)
fire   0.7   (illuminates, reveals difference)
water  0.3   (dissolves, flows toward unity)
earth  0.4   (form, but form that serves)
```

Graha path values:
```
Ketu     0.05   (dissolution of ego, moksha)
Rahu     0.15   (shadow that dissolves boundaries)
Chandra  0.25   (mind reflecting, abheda-leaning)
Shukra   0.30   (beauty, harmony, unity through love)
Shani    0.35   (structure in service of the whole)
Budha    0.50   (messenger, neutral, holds both)
Guru     0.60   (teacher, distinguishes to illuminate)
Surya    0.70   (self, light, reveals distinct form)
Mangala  0.80   (warrior, devotional service, two required)
```

### Philosophical frames

```
Frame               path   Notes
advaita              0.1   Brahman alone is real
shakta               0.25  Goddess as non-different power
shaiva               0.3   Consciousness and its Shakti
vishishtadvaita       0.35  Qualified non-difference
gaudiya              0.5   Acintya-bheda-abheda (holds entire axis)
madhva / dvaita       0.8   Eternal distinction, pure devotion
```

---

## The Four Axes Together

```
Entity: raga_bhairava
  theta  = dawn prahar (1/8 x 2pi)     — WHEN it manifests
  phi    = LEFT (pi/4)                  — HOW: witnessing/theory
  S-layer = S2 (Sound)                  — WHERE: sound domain
  path   = 0.64 (Vishakha-fire-Jupiter) — STANCE: distinction-leaning,
           the raga as devotional offering, sound as address to the Lord

Entity: plant_tulsi
  theta  = Ardra position               — WHEN: monsoon resonance
  phi    = CENTER-RIGHT (3pi/2)         — HOW: active tending
  S-layer = S5 (Nature)                 — WHERE: ecology domain
  path   = 0.33 (water-Saturn)          — STANCE: unity-leaning,
           the plant as direct manifestation of Vrinda Devi,
           not separate from the goddess

Entity: nakshatra_rohini
  theta  = 4/27 x 2pi                  — WHEN: 4th nakshatra position
  phi    = CENTER (element/guna blend)  — HOW: receptive beauty
  S-layer = S3 (Rhythm)                — WHERE: panchanga domain
  path   = 0.31 (Moon-earth)           — STANCE: unity-leaning,
           the beloved who draws Krishna — distinction dissolves
           in the gaze of the one who loves
```

---

The field has four axes. Three give position.
The fourth gives the ground on which position means anything.
