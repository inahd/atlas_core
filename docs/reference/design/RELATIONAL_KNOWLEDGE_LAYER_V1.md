# Relational Knowledge Layer V1

## One-line anchor

Compute which knowledge relations are
active now. Not what to study.
What is coherent to study.

## Stack

field_state → relational_knowledge_state → surface_state

## Inputs from field

nakshatra → primary entity + cross-links
tithi     → devī domain emphasis
vara      → planetary knowledge bias
element   → elemental relation cluster
guna      → depth vs breadth tendency
psi       → approach (ārta/jijñāsu/etc)
coherence_peaks → which entities are loud now

## Computed relations

### Active entity relations
  primary_entity (current nakshatra)
  ruled_by (graha)
  deity (devī/deva)
  body_region → marma → āsana
  element → herb → dosha
  All from datasets/ · attestation per claim

### Domain weights (0-1)
  How emphasized is each domain right now?
  Derived from field state.
  Attestation: SYNTHESIS

### Study path
  Which approach is coherent now?
  Depth or breadth?
  Which topic cluster is indicated?
  Attestation: INTERPRETATION

### Cross-link chains
  Entity clusters that are
  mutually coherent right now.
  Useful for wiki navigation.

## Consumers

  Wiki      → section ordering · link emphasis
  TUI       → :today · :related · detail panel
  Portal    → entity dot brightness
  Archana   → spread domain weighting
  Bandhu    → context without prompting
  Hypervisor → research task routing

## Authority

  field_state → READ ONLY
  relational_knowledge_state → COMPUTED (kernel)
  surface rendering → LOCAL (each surface)

## Attestation rules

  Entity relations from datasets: OBSERVED
  Domain weights:                 SYNTHESIS
  Study path:                     INTERPRETATION
  Cross-links:                    SYNTHESIS
  
  Never strip attestation.
  Never present SYNTHESIS as OBSERVED.
