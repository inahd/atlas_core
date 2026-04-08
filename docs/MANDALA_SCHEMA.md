# Atlas Mandala Schema
# Complete vastu directional map for all layers and sub-mandalas
# This is the relational layout law — not a design choice

---

## Directional Archetypes (canonical, never changes)

| Direction | Deity    | Element | Domain              | Governs                          |
|-----------|----------|---------|---------------------|----------------------------------|
| NE        | Ishana   | ether   | sacred knowledge    | deity, mantra, scripture, devi   |
| N         | Kubera   | water   | time, rhythm        | tithi, nakshatra, tala, calendar |
| NW        | Vayu     | air     | sound, breath       | raga, svara, prana, transmission |
| W         | Varuna   | water   | depth, ecology      | plant, herb, dissolution, ocean  |
| C         | Brahma   | all     | source, field       | bindu, integration, now          |
| E         | Indra    | fire    | perception, study   | codex, text, eye, cognition      |
| SW        | Nirriti  | earth   | ancestor, history   | seed, root, archaeology, past    |
| S         | Yama     | earth   | body, law, form     | marma, anatomy, dharma, boundary |
| SE        | Agni     | fire    | action, practice    | ritual, craft, transformation    |

---

## MAIN MANDALA — S0-S6 Layer Selector

Center: field state now (nakshatra, tithi, devi, raga)
Grid breathes with vastu_engine.zone_weights

| Zone | Content                        | App Portal        |
|------|-------------------------------|-------------------|
| NE   | current devi + yantra mini    | archana, tarot    |
| N    | nakshatra + tithi + tala dots | agriculture cal   |
| NW   | raga ring + raga name         | talachakra        |
| W    | element + dosha + ecology     | plant wheel       |
| C    | FIELD — nakshatra hero        | —                 |
| E    | codex passage for today       | codex, bandhu     |
| SW   | nakshatra plant + history     | guild, wiki       |
| S    | body region + marma           | ecology practice  |
| SE   | practice + muhurta arc        | yantra, brahmanda |

Bottom bar: S0 · S1 · S2 · S3 · S4 · S5 · S6 layer selectors

---

## S0 SUB-MANDALA — Metaphysical Source

Center: bindu · paksha phase · yuga position
Zone weights: uniform — all zones equally present at S0

| Zone | Content                              | 
|------|--------------------------------------|
| NE   | Gaudiya calendar — ashtakala now     |
| N    | Yuga position — Kali arc             |
| NW   | OM — bija of all sound               |
| W    | Akasha — pure space signal           |
| C    | Paksha phase + element signal        |
| E    | Vedic passage — Rigveda cosmology    |
| SW   | Manvantara — deep time               |
| S    | Earth position — seasonal arc        |
| SE   | Pralaya/Srishti arc                  |

---

## S1 SUB-MANDALA — Archetype / Deity

Center: current devi portrait (devanagari, yantra, bija)
Zone weights: NE heavy (Ishana/ether = sacred knowledge center of S1)

| Zone | Content                              | App Portal        |
|------|--------------------------------------|-------------------|
| NE   | Full devi portrait — name, yantra,   | archana, tarot    |
|      | bija, mantra, weapons, vahana        |                   |
| N    | Tithi deity — who presides today     | —                 |
| NW   | Devi's raga — her musical expression | talachakra        |
| W    | Devi's plant — her sacred herb       | plant wheel       |
| C    | DEVI — devanagari large, yantra SVG  | —                 |
| E    | Bhagavatam passage mentioning her    | codex             |
| SW   | Nakshatra deity — Savitar etc        | wiki              |
| S    | Her body correspondence / marma      | ecology           |
| SE   | Her worship — puja, offering, ritual | —                 |

---

## S2 SUB-MANDALA — Sound / Gandharva

Center: raga name + scale ring SVG + current note playing
Zone weights: NW heavy (Vayu/air = sound transmission)

| Zone | Content                              | App Portal        |
|------|--------------------------------------|-------------------|
| NE   | Mantra — bija + deity mantra now     | —                 |
| N    | Tala — full bol cycle ring           | talachakra        |
| NW   | Raga — full scale ring, aroha/avar   | talachakra        |
| W    | Shruti — tuning, element frequency   | —                 |
| C    | RAGA — name large + scale ring       | talachakra        |
| E    | Raga description — rasa, time, mood  | codex             |
| SW   | Gandharva passage — Sangita Ratnak.  | wiki              |
| S    | Therapeutic raga — dosha target      | ecology           |
| SE   | Current phrase — note queue arc      | —                 |

---

## S3 SUB-MANDALA — Rhythm / Panchanga

Center: nakshatra + tithi + vara prominent
Zone weights: N heavy (Kubera/water = time/rhythm)

| Zone | Content                              | App Portal        |
|------|--------------------------------------|-------------------|
| NE   | Devi of this tithi                   | archana           |
| N    | Full tithi info — paksha, deity      | —                 |
| NW   | Vara — day lord, glyph, muhurta      | —                 |
| W    | Dasha — current period, sub-lord     | —                 |
| C    | NAKSHATRA — large + pada + lord      | —                 |
| E    | Nakshatra passage — Taittiriya       | codex             |
| SW   | Historical — who was born here       | wiki              |
| S    | Body — nakshatra body region         | ecology           |
| SE   | Muhurta — auspicious timing now      | —                 |

---

## S4 SUB-MANDALA — Geometry / Vastu

Center: vastu mandala grid SVG — active zones lit
Zone weights: derived from vastu_engine zone_weights directly

| Zone | Content                              | App Portal        |
|------|--------------------------------------|-------------------|
| NE   | Yantra for current deity             | yantra app        |
| N    | Mandala — current formation          | —                 |
| NW   | Temple geometry — shikhara           | vastu analyzer    |
| W    | Vastu analyzer — floor plan          | vastu app         |
| C    | GRID — 8x8 manduka with entities     | —                 |
| E    | Mayamata passage — temple law        | codex             |
| SW   | Brihat Samhita — vastu text          | wiki              |
| S    | Compass — cardinal alignment now     | —                 |
| SE   | Sacred geometry — active formation   | yantra app        |

---

## S5 SUB-MANDALA — Ecology / Nature

Center: today's nakshatra plant + bio-activity indicator
Zone weights: SW heavy (Nirriti/earth = plants/growth foundation)

| Zone | Content                              | App Portal        |
|------|--------------------------------------|-------------------|
| NE   | Sacred plants — ritual, mantra       | —                 |
| N    | Agricultural calendar — planting     | agriculture       |
| NW   | Herb study — search, properties      | guild search      |
| W    | Plant wheel — 27 nakshatra plants    | plant wheel       |
| C    | TODAY — canonical plant + body +     | —                 |
|      | dosha + element + bio-activity       |                   |
| E    | PFAF database — 8504 plants          | guild/PFAF        |
| SW   | Guild mandala — companion planting   | guild generator   |
| S    | Body-plant — marma + herb pairings   | ecology/practice  |
| SE   | Dinacharya — daily practice now      | ecology           |

---

## S6 SUB-MANDALA — Lila / Human Experience

Center: companion (Bandhu) + practice for today
Zone weights: E heavy (Indra/fire = perception/codex/study)

| Zone | Content                              | App Portal        |
|------|--------------------------------------|-------------------|
| NE   | Codex — sacred study, manuscripts   | codex             |
| N    | Wiki — entity browser                | wiki              |
| NW   | Journal — seed capture               | command layer     |
| W    | Bandhu — companion chat              | bandhu            |
| C    | PRACTICE — what to do now            | —                 |
| E    | Research — query + synthesis         | research          |
| SW   | Lila — coherence game                | lila              |
| S    | Art — music, dance, craft            | talachakra        |
| SE   | Offering — what to give now          | archana           |

---

## Grid Sizing Rules

Zone weight → CSS fr unit (from vastu_engine.zone_weights):

  cols: W_weight : Center_weight : E_weight  
  rows: N_weight : Center_weight : S_weight

Center always minimum 1.5fr, maximum 3fr
Outer zones: minimum 0.5fr, maximum 1.5fr

Smooth transition: 1.2s ease when field updates

---

## Color Rules (from VISUAL_STANDARDS)

Zone backgrounds keyed to direction element:
  NE ether/Ishana:  #1a0d28  border #aa77dd
  N  water/Kubera:  #0d1828  border #8899bb
  NW air/Vayu:      #0d2818  border #5cb87a
  W  water/Varuna:  #0d2020  border #4da8a0
  C  all/Brahma:    #0d1428  border #f0c040
  E  fire/Indra:    #280d0d  border #d44040
  SW earth/Nirriti: #0d2010  border #5cb87a
  S  earth/Yama:    #1a1408  border #a09070
  SE fire/Agni:     #281808  border #f0b060

All text: #ffffff minimum 14px
Labels: direction color, 9px mono caps
No opacity anywhere — solid hex only

---

## Navigation (canonical — shell implements exactly this)

```
primary:    ← → arrow keys cycle S0-S6
enter:      ↑ arrow enters sub-mandala for current layer
back:       ↓ arrow or Escape goes up one level
jump:       number keys 0-6 jump directly to that layer
s0_special: S0 shows all layers symbolically — no sub-mandala
observe:    click entity name → observe panel slides in
portal:     click ✦ app link → iframe overlay opens
stack_max:  2 (main → sub-mandala only, no deeper)
```

Bottom bar always shows: S0 S1 S2 S3 S4 S5 S6
Active layer highlighted in its graha color

---

## Content Types (from mandala_schema.py CONTENT_TYPES)

Every piece of text in every zone has a named type with fixed rules:

| Type      | Min Size | Color Rule              | Description                     |
|-----------|----------|-------------------------|---------------------------------|
| hero      | 22px     | #ffffff                 | Primary entity name, large      |
| label     | 11px     | rgba(255,255,255,0.7)   | Field label (graha, deity etc)  |
| value     | 14px     | #ffffff                 | Data value (Hasta, fire etc)    |
| deity_tag | 9px      | #6a8090                 | Zone guardian deity name        |
| zone_title| 22px     | #ffffff                 | Zone domain name                |
| portal    | 11px     | #ffffff                 | App link (✦ talachakra etc)     |
| passage   | 14px     | rgba(255,255,255,0.7)   | Text corpus excerpt             |
| signal    | 14px     | #ffffff                 | S0 field signal text            |
| cosmic    | 11px     | #6a8090                 | Yuga/manvantara context         |
| row       | 14px     | #ffffff                 | Key-value data row              |

---

## Zone Visuals (from mandala_schema.py ZONE_VISUALS)

Fixed SVG visual per direction — shell renders these, never invents new types:

| Direction | Visual Type  | Description                                    |
|-----------|-------------|------------------------------------------------|
| NW        | raga_ring   | 12 semitone ring, active notes green            |
| N         | tala_cycle  | Beat dots in circle, sam gold, bol labels       |
| NE        | devi_yantra | Square + gates + circle + triangle + bindu      |
| W         | (none)      | Data only                                       |
| C         | moon_phase  | Waxing/waning arc from tidx                     |
| E         | (none)      | Data only                                       |
| SW        | plant_form  | Botanical leaf SVG, earth tones                 |
| S         | body_region | Human outline, active region highlighted        |
| SE        | vara_arc    | Planetary glyph + time-of-day arc               |

---

## Zone Content Order (from mandala_schema.py ZONE_CONTENT_ORDER)

Shell renders content in this exact sequence per zone:

```
NW: deity_tag → zone_title → visual → row → portal
N:  deity_tag → zone_title → visual → row → portal
NE: deity_tag → zone_title → visual → row → portal
W:  deity_tag → zone_title → row → portal
C:  deity_tag → hero → row → visual
E:  deity_tag → zone_title → row → portal
SW: deity_tag → zone_title → visual → row → portal
S:  deity_tag → zone_title → visual → row → portal
SE: deity_tag → zone_title → visual → row → portal
```

---

## Declarative Shell Contract

The /shell/state response includes for each zone:
- `visual_type`: which SVG to render (or null)
- `content_order`: exact rendering sequence
- `data`: key-value pairs for row content

The shell reads this and renders. No decisions.
Pure rendering of what the schema provides.
