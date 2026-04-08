# Coherence Atlas — Visual Standards

---

## Background: Shyama

```css
--bg:   #0a0d1a    /* shyama — deep blue-black */
--bg2:  #0d1020    /* slightly lighter surface */
--bg3:  #111428    /* panel background */
```

The background is shyama — Krishna's dark blue complexion.
Not black. Not navy. The color of a rain cloud holding inner light.

This is not a design choice. It is cosmological ground.
All content appears on this ground.
Never use pure black (#000000) or pure dark grey.

The observe panel sits on --bg2 (#0d1020).
Nothing darker than shyama.

---

## Colors come from cosmological tradition, not UI convention

Never invent a color. Derive from dataset.

### Graha colors (canonical)

| Graha   | Hex     | Luminosity | Meaning |
|---------|---------|------------|---------|
| Surya   | #FFB300 | bright     | gold of sovereignty and self-illumination |
| Chandra | #E8E8FF | bright     | silver-white of reflected consciousness |
| Mangala | #CC2200 | bright     | deep crimson of transformative heat |
| Budha   | #00AA44 | earth      | forest green of budding intelligence |
| Guru    | #FFDD44 | bright     | warm yellow of expansive wisdom |
| Shukra  | #FFAADD | bright     | rose-pink of beauty and attraction |
| Shani   | #445566 | dim        | slate blue-grey of endurance and time |
| Rahu    | #6600AA | dim        | deep violet of obsession and illusion |
| Ketu    | #887755 | dim        | smoky ochre of renunciation and moksha |

Source: `datasets/cosmology/graha_master.csv`

### Nakshatra colors

Each nakshatra inherits its ruling graha's color, modulated by guna:

- **Sattva** — brighten 15% (clarity lifts the color)
- **Rajas** — saturate 20% (activity intensifies)
- **Tamas** — darken 20%, desaturate (inertia dampens)

Source: `datasets/cosmology/nakshatra_master.csv` (color_hex column)

### Devi colors (Tantraraja tradition)

Each Nitya Devi has a canonical color from tantric tradition.
These are stored in `datasets/cosmology/nitya_devi_master.csv` (color_hex)
and `datasets/nitya_devi_mapping.csv` (color_hex, color_meaning).

---

## Luminosity = field activity level

- **Bright** — actively coherent in current field moment. Entity is resonant with the panchanga NOW.
- **Earth tone** — stable background presence. Entity exists in the graph but is not currently activated.
- **Dim** — low coherence. Entity is distant from the current field state.

Luminosity is not decoration. It is the coherence score made visible.

When the field changes (new tithi, new nakshatra), the colors that glow
shift — because the cosmos has moved and different entities are now resonant.

---

## Text legibility

All zone text is white (#ffffff). Color is in the backgrounds only.

- All data values: #ffffff, minimum 14px
- Labels: rgba(255,255,255,0.7), 11px mono uppercase
- Zone deity tags: #6a8090, 9px mono caps
- Entity names (hero): #ffffff, 22px italic Cormorant
- Observe panel values: #ffffff, minimum 14px on #141828
- Center nakshatra: #f0c040 (gold) — only colored text exception

See `npu_engine/mandala_schema.py` CONTENT_TYPES for canonical rules.

---

## The three surfaces

1. **Shyama ground** (#0a0d1a) — the mandala, the cosmos, the field
2. **Observe surface** (#0d1020) — the reading panel, entity portraits, data
3. **Warm reading** (#1a1208) — only for focused text study (codex reading mode)

Each surface is a cosmological context, not a UI layer.
