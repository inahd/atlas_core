# Coherence Atlas — Core Architecture

Atlas is a cosmological research engine for organizing Vedic knowledge.

The system organizes knowledge using:

Entities
Relations
Authority
Stability
Visualization permissions

Atlas is designed to detect patterns, generate research questions,
and visualize cosmological structure.

---

## Core Data Model

ENTITY
    anything in cosmology

RELATION
    connection between entities

Examples

Ashwini → ruled_by → Ketu
Pitta → composed_of → Fire
Agni → element_of → Fire
Tuesday → ruled_by → Mars

---

## Three System Axes

Atlas uses three independent classification systems.

1. Stability Layer
2. Authority Source
3. Visualization Permission

These axes must remain independent.

---

## Stability Layer

STABLE
    canonical cosmological knowledge

WORKING
    validated synthesis

EXPERIMENTAL
    research hypothesis

Examples

27 Nakshatras → STABLE
Dosha–Element correspondences → WORKING
AI symmetry detection → EXPERIMENTAL

Purpose

System safety.

---

## Authority Axis

SHASTRA
    textual source

SADHU
    practitioner / community confirmation

GURU
    interpretation / synthesis

Example

Ashwini → healing

Shastra: strong
Sadhu: moderate
Guru: strong

Purpose

Epistemic provenance.

---

## Visualization Permission

RELATION
    graph only

ANALYTIC
    neutral geometry

SYMBOLIC
    mandala representation

CANONICAL
    sacred yantra

Example

5 Mahabhutas → symbolic pentagonal mandala

Purpose

Prevent decorative sacred geometry.

---

## Yantra Harmonizer

Pipeline

graph pattern
→ authority evaluation
→ stability layer check
→ visualization permission
→ geometry generation

This prevents misleading sacred diagrams.


---

# Graph Schema

Atlas ultimately operates on a simple model:

ENTITY
RELATION

Everything in the system reduces to these two primitives.

Entities represent cosmological objects.

Relations represent meaningful connections between them.

Example relations:

Ashwini → ruled_by → Ketu
Pitta → composed_of → Fire
Agni → element_of → Fire
Tuesday → ruled_by → Mars

---

# Entity Metadata

Every entity or relation may include metadata fields.

stability_layer
    stable
    working
    experimental

authority_source
    shastra
    sadhu
    guru
    secondary
    inferred

visualization_permission
    blocked
    relation
    analytic
    symbolic
    canonical

These metadata fields guide the Yantra Harmonizer and visualization system.

---

# Yantra Harmonizer Logic

The Yantra Harmonizer evaluates structural patterns before allowing visual elevation.

Pipeline:

graph pattern
→ authority evaluation
→ stability layer evaluation
→ visualization permission
→ geometry rendering

Example rule:

If:
    stability = stable
    authority = strong shastra

Then:
    canonical yantra allowed

If:
    stability = experimental

Then:
    analytic geometry only

---

# System Principle

Atlas may generate geometry freely.

Atlas may authorize sacred geometry only when supported
by authority and stability rules.


---

# Canonical Entity Registry

Atlas uses a controlled set of entity categories.

This prevents uncontrolled ontology growth.

Each entity in the graph must belong to a defined type.

Core entity categories include:

Deity
Graha
Nakshatra
Rashi
Mahabhuta
Guna
Dosha
Rasa
Direction
Tithi
Festival
Mantra
Yantra
Mandala
Ritual
Substance
Organ
Chakra
Time_Cycle
Loka
Text
Commentary
Teacher
Lineage

These entity types form the **core ontology skeleton** of Atlas.

New entity types should be added carefully to avoid fragmentation.


---

# Atlas Ingestion Engine

Script

scripts/atlas_ingest.py

Purpose

Convert datasets into structured Atlas entities.

Pipeline

datasets
→ entity normalization
→ entity type detection
→ authority metadata attachment
→ stability assignment
→ graph generation

Output

data/atlas_graph.json

This file becomes the base knowledge graph used by the Atlas engine.


---

# Convention Protocol

Atlas uses an explicit convention registry.

New conventions must be added as structured records.

Convention categories include:

entity_type
relation_type
authority_rule
visualization_rule
domain_rule
harmonizer_rule
ingestion_rule

Each convention must record:

name
category
description
status
source
introduced_by
date

This prevents silent architectural drift.

---

# Placeholder Node Protocol

Atlas allows intentional incomplete nodes.

A placeholder node is a valid graph object that represents
expected but not yet populated knowledge.

Placeholder nodes must include:

id
name
type
status
gap_state
required_fields

Gap states include:

unpopulated
partial
needs_review
needs_source
needs_relation
needs_authority
needs_promotion
complete

This allows Atlas to represent missing knowledge explicitly
and turn gaps into research tasks.

---

# Population Cycle

create placeholder
→ mark required fields
→ create research task
→ ingest evidence
→ populate fields
→ validate
→ promote or retain


---

# Gap Detection System

Atlas now includes automatic gap detection.

Script

scripts/atlas_gap_detector.py

Purpose

Scan the Atlas graph for incomplete entities and generate
placeholder nodes for missing information.

Pipeline

graph
→ gap detector
→ missing field detection
→ placeholder node creation
→ research queue candidate

Example

Entity missing authority metadata:

Agni

→ placeholder created

missing_fields_for_Agni

required_fields

authority
stability_layer
visualization_permission

This converts incomplete knowledge into structured research tasks.

---

# Atlas Research Loop

dataset ingestion
→ graph generation
→ gap detection
→ placeholder nodes
→ research tasks
→ population
→ validation
→ promotion

Atlas therefore represents both knowledge and missing knowledge.


---

# Canonical Cosmology Backbone

Atlas encodes finite cosmological structures as canonical datasets.

These structures form the immutable skeleton of the knowledge graph.

Examples include:

Nakshatras (27)
Grahas (9)
Mahabhutas (5)
Gunas (3)
Rashis (12)
Directions (8)

These lists should not expand.

Atlas can add attributes, relations, and interpretations around these
structures, but the core sets remain fixed.

This prevents ontology drift and provides a stable anchor for
research and visualization systems.

---

# Canonical Coverage

Each canonical system includes an expected_count value.

Atlas can use this to measure completion:

coverage = known_items / expected_count

Example:

Nakshatra coverage = 27 / 27 = 1.0

When coverage approaches 1.0 the system automatically reduces
canonical discovery tasks and shifts effort toward synthesis
and experimental discovery.


---

# Canonical Structure Loader

Script

scripts/atlas_load_canon.py

Purpose

Load canonical cosmological datasets and ensure the Atlas graph
contains the correct entities.

Pipeline

canonical datasets
→ canonical loader
→ entity verification
→ missing entity creation
→ canonical gap placeholder generation

Canonical entities are assigned:

stability_layer: stable  
authority: strong shastra  
visualization_permission: symbolic  

This ensures the backbone of Atlas remains structurally correct.

---

# Canonical Integrity

Each canonical dataset defines:

system  
expected_count  
items  

The loader checks:

actual_count vs expected_count

If items are missing a placeholder node is generated so the
research cycle can investigate the gap.


---

# Relation Engine

Script

scripts/atlas_build_relations.py

Purpose

Automatically generate relationships between entities using
structured mapping datasets.

Pipeline

mapping dataset
→ relation builder
→ entity lookup
→ relation creation
→ graph update

Example relation

Ashwini → rules → Ketu

Relations include metadata:

stability_layer
authority
visualization_permission

This allows relations to participate in the same promotion and
evaluation cycle as entities.


---

# Yantra Harmonizer Engine

Script

scripts/atlas_harmonizer.py

Purpose

Detect structural patterns in the Atlas graph that correspond
to sacred numerical geometries.

Pipeline

graph
→ cluster detection
→ sacred number evaluation
→ geometry assignment
→ yantra candidate generation

Example structures

3 nodes → triangle  
4 nodes → square  
5 nodes → pentagon  
6 nodes → hexagon  
8 nodes → vastu grid  
9 nodes → navagraha mandala  
12 nodes → zodiac wheel  
27 nodes → nakshatra wheel  

Important rule

Candidates begin as:

stability_layer: experimental  
visualization_permission: analytic  

They must be promoted through authority validation before
being rendered as symbolic or canonical yantras.


---

# Research Queue Engine

Script

scripts/atlas_build_research_queue.py

Purpose

Convert placeholder nodes and detected gaps into structured
research tasks.

Pipeline

placeholder nodes
→ task generation
→ priority scoring
→ research queue

Each task contains:

task_id  
target entity  
gap_state  
layer (stable / working / experimental)  
priority score  
status  

Priority reflects:

gap severity  
canonical importance  
relation dependency  

Tasks are sorted so Atlas works on the highest-value research first.


---

# Research Executor

Script

scripts/atlas_execute_research.py

Purpose

Attempt automated resolution of research tasks generated by the
research queue engine.

Pipeline

research_queue
→ task selection
→ automated analysis attempt
→ task status update

Possible outcomes

needs_manual_source
needs_relation_discovery
ai_analysis_candidate
unresolved

This allows Atlas to begin automatically triaging research work
between canonical sourcing, synthesis tasks, and AI discovery.


---

# Cosmic Map Explorer

Location

explorer/atlas_cosmic_map.html

Purpose

Provide a simple interactive visualization of the Atlas knowledge graph.

Features

Interactive node layout  
Graph relations  
Drag navigation  
Entity hover labels  

Pipeline

atlas_graph.json
→ D3 visualization
→ cosmic network map

This viewer allows developers to inspect the evolving cosmological graph
structure as Atlas grows.


---

# Entity Normalization System

Script

scripts/atlas_normalize_entities.py

Purpose

Ensure that entities in the Atlas graph maintain consistent identity.

Features

Alias resolution  
Canonical naming  
Duplicate detection  

Example

"Fire Deity"
→ normalized to
"Agni"

This prevents ontology fragmentation as the graph expands.


---

# Atlas Pipeline Runner

Script

scripts/atlas_run_pipeline.py

Purpose

Run the full Atlas research cycle automatically.

Steps executed

1 canonical loader  
2 ingestion engine  
3 relation builder  
4 entity normalization  
5 gap detection  
6 research queue generation  
7 research executor  
8 yantra harmonizer  

Usage

atlasenv  
python scripts/atlas_run_pipeline.py

This replaces running each subsystem manually.


---

# Coherence Engine

Script

scripts/atlas_compute_coherence.py

Purpose

Compute coherence scores for entities in the Atlas graph.

Signals used

relation density  
authority strength  

Higher coherence scores indicate stronger cosmological alignment
across the Atlas knowledge graph.

These scores may later influence:

research priority  
promotion decisions  
visualization strength  

