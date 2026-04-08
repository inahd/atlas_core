"""Backward-compatibility re-exports for npu_engine restructure.

Old import paths still work via these re-exports.
Remove this file once all imports are updated to new paths.

Mapping:
  npu_engine.graph_engine    → npu_engine.core.graph_engine
  npu_engine.datasets        → npu_engine.core.datasets
  npu_engine.toroidal_field  → npu_engine.core.toroidal_field
  npu_engine.field_state     → npu_engine.core.field_state
  npu_engine.build_field_state → npu_engine.core.build
  npu_engine.coherence_engine_v2 → npu_engine.core.coherence
  npu_engine.vector_store    → npu_engine.core.vector_store
  npu_engine.vastu_engine    → npu_engine.geometry.vastu_engine
  npu_engine.igpu            → npu_engine.geometry.igpu
  ... etc for all moved files
"""
# This file is imported by npu_engine/__init__.py to maintain
# backward compatibility during the transition period.
# It does NOT need to be imported directly.
