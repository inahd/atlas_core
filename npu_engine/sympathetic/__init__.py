"""
npu_engine.sympathetic — Relational sympathetic string resonance engine.

In Indian classical music, the sitar and sarangi have sympathetic strings
(taraf) that vibrate when specific notes are played. These strings are
tuned to the raga — they resonate with what's being played and add a
shimmering halo to every note.

This engine models that relationship:
  - 13 sympathetic strings tuned to the current raga's scale
  - Each string resonates when a nearby frequency is played
  - Resonance decays naturally (Karplus-Strong in SC)
  - Raga change = retune all strings
  - The strings are the raga made physical — they ARE the scale
"""
