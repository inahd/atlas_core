# Sound System

SuperCollider receives OSC from `bridge.py` and kernel `/sound/*` endpoints.

## SC Port

`127.0.0.1:57121` — set in `bridge.py` and `kernel.py`

## SynthDefs (19)

| Synth | Type | Description |
|-------|------|-------------|
| `\atlasTanpura` | Drone | 6-string tonic drone |
| `\atlasBass` | Percussion | Bayan (left tabla) |
| `\atlasMid` | Percussion | Dayan mid pitch |
| `\atlasBright` | Percussion | Dayan high ring |
| `\atlasNote` | Melody | Raga note with gamaka |
| `\atlasPad` | Ambient | FM synthesis deity-colored pad |
| `\atlasElectronic` | Texture | Filtered noise + shimmer |
| `\atlasKonnakol` | Rhythm | Voiced buzz konnakol |
| `\atlasBol` | Rhythm | Tabla bol syllable |
| `\atlasMantraDrone` | Vocal | AUM with morphing formants |
| `\atlasBijaSyllable` | Vocal | Sacred syllable with meend |
| `\atlasVocalPad` | Vocal | Guna-colored vowel bed |
| `\atlasVocalLine` | Vocal | Main vocal with gamaka/bhava |
| `\atlasSympString` | String | Sympathetic string with decay |
| `\atlasSarod` | String | 15 sympathetic strings |
| `\atlasSarangi` | String | Bowed with 18 chromatic strings |
| `\atlasMaster` | Mix | Global guna-based filter |

## OSC Routes (41 handlers)

### Core Field
- `/atlas/field` — sa, bpm, guna_idx, deity_idx, graha_ratio, time_match
- `/atlas/raga` — aroha(8), avaroha(8), vadi, samvadi, gamak(3), tala_sym
- `/atlas/rasa` — rasa_idx, arc_phase
- `/atlas/tala` — tala_name, beat_count, bols[]
- `/atlas/npu` — energy, density, tension, release, tempo

### Rhythm
- `/atlas/rhythm/beat`, `/atlas/rhythm/sam`, `/atlas/rhythm/bol`
- `/atlas/rhythm/layakari`, `/atlas/rhythm/tihai`, `/atlas/rhythm/fill`

### Voice
- `/atlas/vocal`, `/atlas/vocal/bhava`, `/atlas/vocal/gamaka`
- `/atlas/vocal/phoneme`, `/atlas/vocal/svara`

### Mix (11 layers)
- `/atlas/mix/layers` — [tanpura, mantra_drone, vocal_pad, tabla, konnakol, bol, melody, vocal_line, pad, electronic, bija]
- `/atlas/mix/global` — brightness, reverb, decay, sub
- `/atlas/mix/sam_event`, `/atlas/mix/khali_event`

### Sympathetic Strings
- `/atlas/sympathetic/tune`, `/atlas/sympathetic/excite`, `/atlas/sympathetic/damp`

### Kernel HTTP Sound Endpoints
- `POST /sound/raga` — send raga + semitones to SC
- `POST /sound/play_note` — play single note via SC
- `POST /sound/voice` — konnakol or bol syllable
- `POST /sound/mantra` — start/stop AUM drone
- `POST /sound/bols` — full bol sequence
- `GET  /sound/mix/state` — current 11-layer mix weights
