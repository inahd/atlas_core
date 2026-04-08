# ATLAS ONTOLOGY SCHEMA

## Purpose

This document defines the core entities and relations used by the Atlas knowledge graph.

The ontology organizes traditional cosmological knowledge into a relational structure suitable for research, visualization, and symbolic interfaces.

---

# Universal Field

Every entity in Atlas carries the `path` coordinate:

```
path: float (0.0–1.0) — bheda-abheda axis

  0.0 = pure non-difference (abheda, Advaita, unity)
  0.5 = neutral / bindu / field state (acintya-bheda-abheda)
  1.0 = pure difference (bheda, Dvaita, devotional distinction)
```

The path value encodes where an entity sits on the axis between
unity-consciousness and relational-devotion. This is the fourth
axis — the one that holds the other three (θ, φ, S-layer).

See docs/reference/specs/atlas_axes.md for full specification.

---

# Core Entity Types

## Cosmology

### Nakshatra

Fields:

id  
name  
ruler_graha  
deity  
symbol  
shakti  
guna  
animal  
element  
path  

Relations:

nakshatra → ruled_by → graha  
nakshatra → deity → deity  
nakshatra → element → mahabhuta  
nakshatra → guna → guna  
nakshatra → sound → mantra  

---

### Graha

Fields:

id  
name  
element  
guna  
metal  
color  
direction  
deity  
path  

Relations:

graha → element → mahabhuta  
graha → governs → rashi  
graha → influences → nakshatra  
graha → associated_deity → deity  

---

### Rashi

Fields:

id  
name  
element  
mode  
ruler_graha  
body_part  

Relations:

rashi → ruled_by → graha  
rashi → element → mahabhuta  
rashi → contains → nakshatra  

---

### Tithi

Fields:

id  
name  
deity  
nature  
ritual_use  

Relations:

tithi → deity → deity  
tithi → lunar_phase → time_cycle  
tithi → favorable_for → ritual  

---

# Fundamental Principles

### Mahabhutas

ether  
air  
fire  
water  
earth  

Fields:

id  
name  
qualities  
sense  
organ  
path  

Relations:

element → influences → dosha  
element → associated_with → chakra  
element → associated_with → graha  

---

### Gunas

sattva  
rajas  
tamas  

Fields:

id  
name  
qualities  

Relations:

guna → influences → graha  
guna → influences → nakshatra  
guna → influences → mind_state  

---

# Embodiment

### Doshas

vata  
pitta  
kapha  

Fields:

id  
name  
elements  
qualities  
body_systems  

Relations:

dosha → composed_of → element  
dosha → influences → body_system  
dosha → influenced_by → graha  
dosha → influenced_by → nakshatra  
dosha → balanced_by → practice  

---

### Chakras

Fields:

id  
name  
location  
element  
bija_mantra  
petals  

Relations:

chakra → element → mahabhuta  
chakra → associated_mantra → mantra  
chakra → body_region → marma  

---

### Marma Points

Fields:

id  
name  
location  
organ_relation  
chakra_relation  

Relations:

marma → associated_with → chakra  
marma → influenced_by → dosha  

---

# Spiritual and Symbolic Entities

### Deities

Fields:

id  
name  
domain  
associated_graha  
associated_nakshatra  

Relations:

deity → associated_with → graha  
deity → associated_with → nakshatra  
deity → associated_with → mantra  

---

### Mantra / Sound

Fields:

id  
syllable  
deity  
element  
chakra  

Relations:

mantra → associated_deity → deity  
mantra → resonates_with → chakra  
mantra → resonates_with → element  

---

# Music and Sound

### Raga

Fields:

id  
name  
time_of_day  
season  
rasa  
associated_deity  

Relations:

raga → evokes → rasa  
raga → associated_with → time_cycle  
raga → associated_with → deity  

---

### Tala

Fields:

id  
name  
beats  
structure  
ritual_use  

Relations:

tala → associated_with → ritual  
tala → used_in → mantra_chanting  

---

### Rasa

Fields:

id  
name  
emotion  
associated_deity  
color  

Relations:

rasa → expressed_in → raga  
rasa → associated_with → deity  

---

# Time

### Time Cycles

Fields:

id  
name  
length  
category  

Examples:

muhurta  
tithi  
paksha  
masa  
ritu  
ayana  
yuga  

Relations:

time_cycle → contains → tithi  
time_cycle → governs → ritual  

---

# Geometry

### Yantra

Fields:

id  
name  
geometry_type  
associated_deity  
associated_element  

Relations:

yantra → represents → deity  
yantra → associated_with → element  
yantra → associated_with → mantra  

---

# Guiding Principles

Atlas ontology prioritizes:

clarity  
traceability  
canonical grounding  
relational coherence  

The goal is not maximal data accumulation but harmonized cosmological structure.

