"""
codex_modes.py — The 5 canonical Codex artifact modes.

Each mode is a structured output type grounded in field_state.
No freeform prompts. No generation without entities + relations.
"""

MODES = ["brief", "practice", "study", "commentary", "cluster"]

MODE_DESCRIPTIONS = {
    "brief":      "Field summary with top entities + key relations",
    "practice":   "Executable field-informed protocol",
    "study":      "Relational study path from entity through graph",
    "commentary": "Structured analysis of why an entity is coherent",
    "cluster":    "Formation / cluster geometry report",
}
