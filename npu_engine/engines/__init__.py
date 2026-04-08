"""
engines/ — Zone engine registry.

Each engine owns a vastu direction and its domain.
The center engine assembles from all of them.
"""

from .sound_engine import SoundEngine
from .rhythm_engine import RhythmEngine
from .archetype_engine import ArchetypeEngine
from .ecology_engine import EcologyEngine
from .codex_engine import CodexEngine
from .plant_engine import PlantEngine
from .body_engine import BodyEngine
from .action_engine import ActionEngine
from .center_engine import CenterEngine

ENGINES = [
    SoundEngine(),      # NW · Vayu · S2
    RhythmEngine(),     # N  · Kubera · S3
    ArchetypeEngine(),  # NE · Ishana · S1
    EcologyEngine(),    # W  · Varuna · S5
    CodexEngine(),      # E  · Indra · S6
    PlantEngine(),      # SW · Nirriti · S5
    BodyEngine(),       # S  · Yama · S5
    ActionEngine(),     # SE · Agni · S6
]

CENTER = CenterEngine(ENGINES)

# Map vastu position → engine for quick lookup
ENGINE_MAP = {e.vastu_position: e for e in ENGINES}
ENGINE_MAP["C"] = CENTER
