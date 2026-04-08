"""
codex_engine.py — Relational generation engine for Atlas Codex v2.

All outputs are:
  - grounded in field_state
  - derived from canonical relations
  - constrained by truth layer
  - traceable (provenance appended)

Pipeline: field_state → entity selection → relation selection → artifact

No freeform prompts. No generation without entities + relations.
No invention of relations not present in graph.
"""

from typing import Any, Dict, List, Optional

from .codex_modes import MODES


# ── Config ────────────────────────────────────────────────

DEFAULT_CONFIG = {
    "top_n": 5,
    "depth": 1,
    "truth_layer": "canonical",
}


# ── Selection ─────────────────────────────────────────────

def select_entities(state: Dict[str, Any],
                    config: Dict[str, Any]) -> List[Dict]:
    """Select top entities from field_state by composite score."""
    top_n = config.get("top_n", 5)
    return (state.get("entities") or [])[:top_n]


def select_relations(state: Dict[str, Any],
                     entities: List[Dict],
                     config: Dict[str, Any]) -> List[Dict]:
    """Select active relations touching the selected entities."""
    entity_ids = {e.get("entity_id", "") for e in entities}
    all_rels = state.get("active_relations") or []

    rels = [
        r for r in all_rels
        if r.get("from_id") in entity_ids or r.get("to_id") in entity_ids
    ]
    return rels[:20]


# ── Main entry point ─────────────────────────────────────

def generate(field_state: Dict[str, Any],
             mode: str = "brief",
             config: Optional[Dict[str, Any]] = None) -> str:
    """Generate a Codex artifact from field_state.

    Args:
        field_state: dict from /spine or query_field_state()
        mode: one of MODES
        config: optional overrides for top_n, depth, etc.

    Returns:
        Formatted artifact string with provenance block.

    Raises:
        ValueError: if mode is unknown or field_state has no entities.
    """
    if mode not in MODES:
        raise ValueError(f"Unknown codex mode: {mode}. Valid: {MODES}")

    cfg = {**DEFAULT_CONFIG, **(config or {})}

    entities = select_entities(field_state, cfg)
    if not entities:
        return "CODEX: No entities in field_state. Cannot generate without data.\n"

    relations = select_relations(field_state, entities, cfg)

    # Dispatch to artifact generator
    generators = {
        "brief": _generate_brief,
        "practice": _generate_practice,
        "study": _generate_study,
        "commentary": _generate_commentary,
        "cluster": _generate_cluster,
    }

    body = generators[mode](entities, relations, field_state)
    return _add_provenance(body, entities, relations, mode)


# ── Artifact generators ───────────────────────────────────

def _generate_brief(entities: List[Dict],
                    relations: List[Dict],
                    state: Dict) -> str:
    """Field summary: top entities + key relations + lifecycle."""
    p = state.get("panchanga", {})
    lc = state.get("lifecycle", {})
    psi = state.get("psi", {})
    ss = state.get("sound_state", {})

    lines = ["FIELD BRIEF", ""]

    # Panchanga context
    nak = p.get("nakshatra", "?")
    tithi = f"{p.get('paksha', '')} {p.get('tithi', '')}".strip() or "?"
    devi = (p.get("devi") or [""])[0]
    lines.append(f"  {nak} · {tithi} · {devi}")
    if ss:
        lines.append(f"  {ss.get('raga', '?')} · {ss.get('rasa_primary', '?')} · {ss.get('tala', '?')} {ss.get('tala_beats', '')} · {ss.get('bpm', '?')}bpm")
    lines.append(f"  Phase: {lc.get('phase', '?')} · intensity {lc.get('intensity', 0):.2f} · stability {lc.get('stability', 0):.2f}")
    lines.append("")

    # Top entities
    lines.append("COHERENT ENTITIES:")
    for e in entities:
        comp = e.get("composite_score", e.get("score", 0))
        geo = e.get("geometric_score", 0)
        rel = e.get("relational_score", 0)
        att = e.get("attestation", "?")
        name = _name(e)
        lines.append(f"  {comp:.3f}  {name:30s}  geo={geo:.3f} rel={rel:.3f}  [{att}]")
    lines.append("")

    # Key relations (prioritized)
    from .path_engine import prioritize_relations, detect_flows
    pri = prioritize_relations(relations, {e.get("entity_id", ""): e.get("composite_score", 0) for e in entities})

    if pri["primary_deity"] or pri["ruling_graha"] or pri["element"]:
        lines.append("KEY RELATIONS:")
        for r in pri["primary_deity"]:
            lines.append(f"  deity   {_short(r['to_id']):20s}  [{r.get('attestation','?')}]")
        for r in pri["ruling_graha"]:
            lines.append(f"  graha   {_short(r['to_id']):20s}  [{r.get('attestation','?')}]")
        for r in pri["element"]:
            lines.append(f"  quality {_short(r['to_id']):20s}  [{r.get('attestation','?')}]")
        if pri["secondary"]:
            lines.append(f"  + {len(pri['secondary'])} secondary relations")
    elif relations:
        lines.append("KEY RELATIONS:")
        for r in relations[:5]:
            att = r.get("attestation", "?")
            lines.append(f"  {_short(r['from_id']):20s} → {r['relation']:18s} → {_short(r['to_id']):20s}  [{att}]")
    else:
        lines.append("KEY RELATIONS: none active")
    lines.append("")

    # Flows (2-step chains showing movement)
    anchor_id = entities[0]["entity_id"] if entities else ""
    if anchor_id:
        all_rels = state.get("active_relations") or relations
        flows = detect_flows(all_rels, anchor_id,
                             {e.get("entity_id", ""): e.get("composite_score", 0) for e in entities})
        if flows:
            lines.append("FLOW:")
            for f in flows:
                d1 = f["domains"][0] or ""
                d2 = f["domains"][1] or ""
                domain_hint = f" ({d1} → {d2})" if d1 or d2 else ""
                lines.append(f"  {f['text']}{domain_hint}")
        lines.append("")

    # Formations
    formations = state.get("formations", [])
    if formations:
        lines.append("FORMATIONS:")
        for fm in formations[:5]:
            fm_type = fm.get("type", "?")
            fm_name = fm.get("name", "?").replace("_", " ")
            fm_count = fm.get("count", 0)
            fm_desc = fm.get("description", "")
            lines.append(f"  {fm_type:8s} {fm_name:25s} ({fm_count})  {fm_desc}")

    return "\n".join(lines)


def _generate_practice(entities: List[Dict],
                       relations: List[Dict],
                       state: Dict) -> str:
    """Executable practice protocol from field state."""
    p = state.get("panchanga", {})
    nd = p.get("nak_data", {}) or {}
    lc = state.get("lifecycle", {})
    psi = state.get("psi", {})
    ss = state.get("sound_state", {})

    top = entities[0] if entities else {}
    element = (nd.get("element") or top.get("element") or "ether").lower()
    guna = (nd.get("guna") or top.get("guna") or "sattva").lower()
    raga = ss.get("raga", "current rāga")
    phase = lc.get("phase", "unknown")

    # Element → breath
    breath = {
        "earth": "Square breath (4:4:4:4) — grounding, prthivī",
        "water": "Cooling breath (4:8 exhale) — lunar, soma",
        "fire": "Kapālabhāti 27 rounds — agni, purification",
        "air": "Nāḍī śodhana — alternate nostril, balance",
        "ether": "Khecarī awareness — silent presence, ākāśa",
    }.get(element, "12 breaths, settle")

    # Guna → quality
    guna_note = {
        "sattva": "Receptive. Let the field compose. Minimal effort.",
        "rajas": "Directed. Channel into structured repetition.",
        "tamas": "Still. Offer presence before action. Do not force.",
    }.get(guna, "Observe quality of attention.")

    # Relational chain for practice focus
    chain = ""
    if relations:
        r = relations[0]
        chain = f"\n  Relational anchor: {_short(r['from_id'])} → {r['relation']} → {_short(r['to_id'])}"

    lines = [
        "PRACTICE PROTOCOL",
        "",
        f"  Focus: {_name(top)}",
        f"  Element: {element} · Guṇa: {guna}",
        f"  Phase: {phase} · ψ stability: {psi.get('stability', 0):.2f}",
        "",
        f"  1. BREATH: {breath}",
        f"  2. NĀDA: Drone in {raga}, vādī note first, then ārōha",
        f"     BPM: {ss.get('bpm', '?')} · Tāla: {ss.get('tala', 'free')}",
        f"  3. GUṆA: {guna_note}",
        f"  4. TITHI: {p.get('paksha', '')} {p.get('tithi', '')}",
        f"     Observe. Log before interpreting.",
        chain,
    ]

    return "\n".join(lines)


def _generate_study(entities: List[Dict],
                    relations: List[Dict],
                    state: Dict) -> str:
    """Relational study path with grouped interpretation."""
    lines = ["STUDY PATH", ""]

    anchor = entities[0] if entities else {}
    anchor_name = _name(anchor)
    anchor_id = anchor.get("entity_id", "")

    # ── Group relations by semantic category ──────────────
    groups = {
        "governance": [],    # deity, ruling graha
        "elemental": [],     # element, dosha, guna
        "sonic": [],         # raga, tala, sound
        "structural": [],    # pada, formation, vastu
        "other": [],
    }

    GOVERNANCE_RELS = {"nakshatra_associated_deity", "nakshatra_ruling_graha",
                       "ruled_by", "deity", "associated_graha"}
    ELEMENTAL_RELS = {"element", "dosha", "guna", "balances", "opposes"}
    SONIC_RELS = {"raga", "therapeutic", "tala", "sound"}

    # Filter out structural noise
    NOISE = {"nakshatra_has_pada", "nakshatra_pada_entity",
             "tithi_in_paksha", "tithi_index_in_paksha", "identity_bridge"}

    meaningful_rels = [r for r in relations if r.get("relation", "") not in NOISE]

    for r in meaningful_rels:
        rel = r.get("relation", "")
        if rel in GOVERNANCE_RELS:
            groups["governance"].append(r)
        elif rel in ELEMENTAL_RELS:
            groups["elemental"].append(r)
        elif rel in SONIC_RELS:
            groups["sonic"].append(r)
        elif "pada" in rel or "vastu" in rel or "index" in rel:
            groups["structural"].append(r)
        else:
            groups["other"].append(r)

    # ── Anchor entity ─────────────────────────────────────
    comp = anchor.get("composite_score", anchor.get("score", 0))
    lines.append(f"● {anchor_name}  ({comp:.3f})  [{anchor.get('attestation', '?')}]")
    lines.append(f"  Element: {anchor.get('element', '?')} · Guṇa: {anchor.get('guna', '?')}")
    lines.append("")

    # ── Grouped relations with interpretation ─────────────
    _INTERPRETATIONS = {
        "nakshatra_associated_deity": lambda to: f"Governed by {to} — the presiding intelligence of this lunar station.",
        "nakshatra_ruling_graha": lambda to: f"Ruled by {to} — planetary lord shaping temporal character.",
        "ruled_by": lambda to: f"Under the authority of {to}.",
        "deity": lambda to: f"Associated with {to} — the mythic layer that gives form to this position.",
        "associated_graha": lambda to: f"Planetary connection to {to} — shared domain of influence.",
        "element": lambda to: f"Element: {to} — the qualitative ground.",
        "dosha": lambda to: f"Dosha affinity: {to} — constitutional resonance.",
        "guna": lambda to: f"Guṇa: {to} — the quality of being.",
        "balances": lambda to: f"In balance with {to} — complementary force.",
        "opposes": lambda to: f"In tension with {to} — productive opposition.",
        "raga": lambda to: f"Musical expression through {to}.",
        "therapeutic": lambda to: f"Therapeutic application via {to}.",
    }

    for group_name, group_rels in groups.items():
        if not group_rels:
            continue

        label = group_name.upper()
        lines.append(f"  ┄┄ {label} ┄┄")

        for r in group_rels[:6]:
            rel = r.get("relation", "")
            to_id = r.get("to_id", "")
            to_name = _short(to_id)
            att = r.get("attestation", "?")

            # Relation line
            lines.append(f"    → {to_name}  ({rel.replace('_', ' ')})  [{att}]")

            # Interpretation (only for known meaningful relations)
            interp_fn = _INTERPRETATIONS.get(rel)
            if interp_fn and (r.get("from_id") == anchor_id or r.get("to_id") == anchor_id):
                lines.append(f"      {interp_fn(to_name)}")

        lines.append("")

    # ── Other entities in the study set ───────────────────
    if len(entities) > 1:
        lines.append("  RELATED ENTITIES:")
        for e in entities[1:]:
            comp = e.get("composite_score", e.get("score", 0))
            lines.append(f"    {_name(e):25s}  {comp:.3f}  {e.get('element', '?')} [{e.get('attestation', '?')}]")
        lines.append("")

    # ── Flows (2-step meaningful chains) ────────────────────
    from .path_engine import detect_flows
    if anchor_id:
        all_rels = state.get("active_relations") or relations
        flows = detect_flows(all_rels, anchor_id,
                             {e.get("entity_id", ""): e.get("composite_score", 0) for e in entities})
        if flows:
            lines.append("  ┄┄ FLOW ┄┄")
            for f in flows:
                d1 = f["domains"][0] or ""
                d2 = f["domains"][1] or ""
                hint = f" ({d1} → {d2})" if d1 or d2 else ""
                lines.append(f"    {f['text']}{hint}")
            lines.append("")

    # ── Formations ─────────────────────────────────────────
    formations = state.get("formations", [])
    if formations:
        lines.append("  ┄┄ FORMATIONS ┄┄")
        for fm in formations[:4]:
            fm_name = fm.get("name", "?").replace("_", " ")
            fm_count = fm.get("count", 0)
            members = fm.get("members", [])
            # Check if anchor is a member
            anchor_in = anchor_id in members
            tag = " ◆" if anchor_in else ""
            lines.append(f"    {fm_name} ({fm_count}){tag}")
            if fm.get("description"):
                lines.append(f"      {fm['description']}")
        lines.append("")

    # ── Study order ───────────────────────────────────────
    if len(entities) > 1:
        lines.append("SUGGESTED ORDER:")
        lines.append("  " + " → ".join(_short(e["entity_id"]) for e in entities))

    return "\n".join(lines)


def _generate_commentary(entities: List[Dict],
                         relations: List[Dict],
                         state: Dict) -> str:
    """Structured analysis of why the top entity is coherent."""
    top = entities[0] if entities else {}
    lc = state.get("lifecycle", {})
    psi = state.get("psi", {})
    p = state.get("panchanga", {})

    eid = top.get("entity_id", "none")
    name = _name(top)
    geo = top.get("geometric_score", 0)
    rel = top.get("relational_score", 0)
    auth = top.get("authority_weight", 0)
    comp = top.get("composite_score", 0)
    att = top.get("attestation", "?")
    elem = top.get("element", "?")
    guna = top.get("guna", "?")

    # Why is it coherent?
    reasons = []
    if geo > 0.9:
        reasons.append(f"Toroidal proximity is very high ({geo:.3f}) — the entity's θ/φ position is near the current panchanga moment.")
    elif geo > 0.7:
        reasons.append(f"Moderate toroidal proximity ({geo:.3f}).")

    if rel > 0.3:
        reasons.append(f"Relational support ({rel:.3f}) — connected to other coherent entities via canonical graph edges.")
    else:
        reasons.append(f"No significant relational support in current field ({rel:.3f}).")

    if auth > 0.8:
        reasons.append(f"High authority ({auth:.2f}) — sourced from canonical/master datasets.")
    elif auth > 0.5:
        reasons.append(f"Moderate authority ({auth:.2f}) — attested but not primary canonical source.")

    # Connected relations
    connected = [r for r in relations if r.get("from_id") == eid or r.get("to_id") == eid]

    lines = [
        "COMMENTARY",
        "",
        f"  Entity: {name}",
        f"  Score:  {comp:.3f}  (geo={geo:.3f} rel={rel:.3f} auth={auth:.2f})",
        f"  Attestation: {att}",
        f"  Element: {elem} · Guṇa: {guna}",
        "",
        "  WHY COHERENT:",
    ]
    for r in reasons:
        lines.append(f"    • {r}")

    if connected:
        lines.append("")
        lines.append("  ACTIVE RELATIONS:")
        for r in connected[:6]:
            r_att = r.get("attestation", "?")
            other = r["to_id"] if r["from_id"] == eid else r["from_id"]
            lines.append(f"    {r['relation']:20s} → {_short(other)}  [{r_att}]")

    lines.append("")
    lines.append(f"  FIELD CONTEXT:")
    lines.append(f"    Nakshatra: {p.get('nakshatra', '?')}")
    lines.append(f"    Phase: {lc.get('phase', '?')} · ψ intensity={psi.get('intensity', 0):.2f}")

    return "\n".join(lines)


def _generate_cluster(entities: List[Dict],
                      relations: List[Dict],
                      state: Dict) -> str:
    """Formation / cluster geometry report."""
    formations = state.get("formations", [])
    lc = state.get("lifecycle", {})
    psi = state.get("psi", {})

    lines = ["CLUSTER REPORT", ""]

    if not formations:
        # No sacred geometry detected — report the coherence cluster instead
        lines.append("  No geometric formation detected.")
        lines.append("")
        lines.append("  COHERENCE CLUSTER (top entities by composite score):")
        lines.append("")

        # Group by element
        by_elem = {}
        for e in entities:
            elem = e.get("element", "ether")
            by_elem.setdefault(elem, []).append(e)

        for elem, group in sorted(by_elem.items(), key=lambda x: -len(x[1])):
            lines.append(f"  {elem} ({len(group)}):")
            for e in group[:3]:
                lines.append(f"    {_name(e):25s}  {e.get('composite_score', 0):.3f}  [{e.get('attestation', '?')}]")
        lines.append("")

        # Mutual relations
        mutual = [r for r in relations if r.get("mutual")]
        if mutual:
            lines.append("  MUTUAL RELATIONS (both endpoints coherent):")
            for r in mutual[:6]:
                lines.append(f"    {_short(r['from_id'])} ⟷ {_short(r['to_id'])}  ({r['relation']})  [{r.get('attestation', '?')}]")
    else:
        for f in formations:
            sym = f.get("symmetry_score", 0)
            name = f.get("name", "unknown")
            count = f.get("count", 0)
            members = f.get("members", [])

            lines.append(f"  FORMATION: {name}")
            lines.append(f"  Count: {count} · Symmetry: {sym:.3f}")
            if members:
                lines.append(f"  Members:")
                for m in members[:12]:
                    lines.append(f"    {_short(m)}")
            lines.append("")

    lines.append(f"  Lifecycle: {lc.get('phase', '?')} · intensity {lc.get('intensity', 0):.2f}")
    lines.append(f"  ψ: intensity={psi.get('intensity', 0):.2f} focus={psi.get('focus', 0):.2f} stability={psi.get('stability', 0):.2f}")

    return "\n".join(lines)


# ── Provenance ────────────────────────────────────────────

def _add_provenance(body: str, entities: List[Dict],
                    relations: List[Dict], mode: str) -> str:
    """Append provenance block. Every output must show its sources."""
    lines = [
        body, "",
        "───────────────────────────────────",
        f"PROVENANCE (codex:{mode})",
        "  Entities:",
    ]
    for e in entities:
        att = e.get("attestation", "?")
        lines.append(f"    {e.get('entity_id', '?')}  [{att}]")

    if relations:
        lines.append("  Relations:")
        for r in relations[:8]:
            att = r.get("attestation", "?")
            lines.append(f"    {r.get('from_id', '?')} → {r.get('to_id', '?')}  ({r.get('relation', '?')})  [{att}]")

    lines.append(f"  Truth layer: canonical graph + toroidal coherence")
    lines.append(f"  Generated from field_state, not freeform prompt")

    return "\n".join(lines)


# ── Helpers ───────────────────────────────────────────────

def _name(entity: Dict) -> str:
    """Human-readable name for an entity."""
    return (entity.get("name") or entity.get("entity_id", "?")).replace("_", " ")


def _short(entity_id: str) -> str:
    """Shortened entity_id for display."""
    parts = entity_id.split("_", 1)
    return parts[1].replace("_", " ") if len(parts) > 1 else entity_id
