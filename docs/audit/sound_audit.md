# Sound Engine Audit

Date: 2026-04-10

## Sound Engine Files: 27

### `npu_engine/bija_synth.py` (247 lines)
- Functions: _bandpass, _glottal_source, _noise_source, _synth_varna, _envelope, _crossfade

### `npu_engine/engines/sound_engine.py` (32 lines)
- Functions: 

### `npu_engine/field_to_sound.py` (428 lines)
- Functions: _slugify, get_devi_from_tithi, get_vastu_from_field, get_treatment_vector, element_to_sa, guna_to_character

### `npu_engine/mix/authority_mix.py` (30 lines)
- Functions: get_confidence_scale

### `npu_engine/mix/deity_mix.py` (18 lines)
- Functions: get_deity_bias

### `npu_engine/mix/guna_mix.py` (14 lines)
- Functions: get_guna_character

### `npu_engine/mix/mix_history.py` (65 lines)
- Functions: 

### `npu_engine/mix/mix_kernel.py` (151 lines)
- Functions: 

### `npu_engine/mix/mix_osc.py` (62 lines)
- Functions: 

### `npu_engine/mix/nakshatra_mix.py` (14 lines)
- Functions: get_nakshatra_bias

### `npu_engine/mix/sam_mix.py` (38 lines)
- Functions: get_sam_event, get_khali_event

### `npu_engine/phrase_engine.py` (392 lines)
- Functions: arc_to_mode

### `npu_engine/rhythm/rhythm_osc.py` (71 lines)
- Functions: 

### `npu_engine/sarangi_voice.py` (377 lines)
- Functions: 

### `npu_engine/sound/bija_synth.py` (1 lines)
- Functions: 

### `npu_engine/sound/field_to_sound.py` (1 lines)
- Functions: 

### `npu_engine/sound/osc_bridge.py` (57 lines)
- Functions: _get_client, send_sound_spec

### `npu_engine/sound/phrase_engine.py` (1 lines)
- Functions: 

### `npu_engine/sound/sarangi_voice.py` (1 lines)
- Functions: 

### `npu_engine/sound/sound_engine.py` (373 lines)
- Functions: _resolve_sound_params, _resolve_observance, _compute_layers, _compute_master, _build_osc_messages, _clamp

### `npu_engine/sound/tanpura_engine.py` (1 lines)
- Functions: 

### `npu_engine/sound/tanpura_field.py` (1 lines)
- Functions: 

### `npu_engine/sympathetic/sympathetic_osc.py` (68 lines)
- Functions: 

### `npu_engine/tanpura_engine.py` (558 lines)
- Functions: _load_string_defs, _load_graha_energy, _graha_jivari, _graha_decay, _build_lookups, _fallback_render

### `npu_engine/tanpura_field.py` (242 lines)
- Functions: tithi_string_weights, derive_tanpura_params

### `npu_engine/vocal/vocal_osc.py` (110 lines)
- Functions: 

### `npu_engine/zones/sound.py` (1 lines)
- Functions: 

## SuperCollider Files: 2
- `sc/atlas_mix.scd`
- `sc/atlas_synth.scd`
