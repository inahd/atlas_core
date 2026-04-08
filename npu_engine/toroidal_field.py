"""
toroidal_field.py — Coherence Atlas NPU Engine
Bead 009 · coherence-atlas-009-npu

The toroidal field is the coherence space.
Every entity has a position (theta, phi) on the toroid surface.
Every moment in time has a position.
Coherence = proximity on the surface.

Toroid coordinate system:
  theta (θ) = major axis = TIME
    encodes: tithi, nakshatra, vara, muhurta
    range: 0 to 2π
    one full rotation = one lunar month (30 tithis)

  phi (φ) = minor axis = QUALITY
    encodes: element, guna, rasa, dosha
    range: 0 to 2π
    one full rotation = five elements cycling

Both axes wrap — no edges, no discontinuities.
Tithi 30 is adjacent to Tithi 1.
Nakshatra 27 wraps to Nakshatra 1.
This is why the toroid is the correct structure.
"""

import numpy as np
import math
from typing import Dict, List, Tuple, Optional

# ── OpenVINO NPU acceleration ────────────────────────────────
_ov_core = None
_OV_DEVICE = "NPU"

def _init_npu():
    global _ov_core
    try:
        from openvino.runtime import Core
        _ov_core = Core()
        if "NPU" not in _ov_core.available_devices:
            _ov_core = None
            return False
        print("  ✓ NPU available for toroidal coherence scoring")
        return True
    except Exception as e:
        print(f"  ⚠ NPU init failed: {e}")
        return False

_npu_ready = _init_npu()

try:
    from . import datasets as dataset_loader
except ImportError:
    import datasets as dataset_loader


# ══════════════════════════════════════════════
# CONSTANTS — encoded from canonical sources
# ══════════════════════════════════════════════

# Major axis (θ) — TIME encodings
# Tithi contribution: 0 to 2π over 30 tithis
TITHI_ANGLE = {i: (i / 30) * 2 * math.pi for i in range(1, 31)}

# Nakshatra contribution: 0 to 2π over 27 nakshatras
NAKSHATRA_ANGLE = {
    'Ashwini': 0/27, 'Bharani': 1/27, 'Krittika': 2/27,
    'Rohini': 3/27, 'Mrigashira': 4/27, 'Ardra': 5/27,
    'Punarvasu': 6/27, 'Pushya': 7/27, 'Ashlesha': 8/27,
    'Magha': 9/27, 'Purva Phalguni': 10/27, 'Uttara Phalguni': 11/27,
    'Hasta': 12/27, 'Chitra': 13/27, 'Swati': 14/27,
    'Vishakha': 15/27, 'Anuradha': 16/27, 'Jyeshtha': 17/27,
    'Mula': 18/27, 'Purva Ashadha': 19/27, 'Uttara Ashadha': 20/27,
    'Shravana': 21/27, 'Dhanishtha': 22/27, 'Shatabhisha': 23/27,
    'Purva Bhadrapada': 24/27, 'Uttara Bhadrapada': 25/27, 'Revati': 26/27,
}
NAKSHATRA_ANGLE = {k: v * 2 * math.pi for k, v in NAKSHATRA_ANGLE.items()}

# Vara (day of week) contribution to θ
VARA_ANGLE = {
    'Ravivara': 0/7,   # Sun — 0°
    'Somavara': 1/7,   # Moon
    'Mangalavara': 2/7, # Mars
    'Budhavara': 3/7,  # Mercury
    'Guruvara': 4/7,   # Jupiter
    'Shukravara': 5/7, # Venus
    'Shanivara': 6/7,  # Saturn
}
VARA_ANGLE = {k: v * 2 * math.pi for k, v in VARA_ANGLE.items()}

# Minor axis (φ) — QUALITY encodings
# Element: 5 elements equally spaced
ELEMENT_ANGLE = {
    'earth': 0/5 * 2 * math.pi,
    'water': 1/5 * 2 * math.pi,
    'fire':  2/5 * 2 * math.pi,
    'air':   3/5 * 2 * math.pi,
    'ether': 4/5 * 2 * math.pi,
}

# Guna: 3 gunas
GUNA_ANGLE = {
    'tamas':  0/3 * 2 * math.pi,
    'rajas':  1/3 * 2 * math.pi,
    'sattva': 2/3 * 2 * math.pi,
}

# Rasa: 9 rasas
RASA_ANGLE = {
    'shringara': 0/9 * 2 * math.pi,   # love/beauty
    'hasya':     1/9 * 2 * math.pi,   # humor
    'karuna':    2/9 * 2 * math.pi,   # compassion
    'raudra':    3/9 * 2 * math.pi,   # fury
    'vira':      4/9 * 2 * math.pi,   # heroism
    'bhayanaka': 5/9 * 2 * math.pi,   # terror
    'bibhatsa':  6/9 * 2 * math.pi,   # disgust
    'adbhuta':   7/9 * 2 * math.pi,   # wonder
    'shanta':    8/9 * 2 * math.pi,   # peace
}

# ── Bhakti-rasa depth signal ─────────────────────────────
# Not positions on φ axis — depth weights toward the source (S0).
# Eternal ontological layer, not material quality positions.
BHAKTI_RASA_DEPTH = {
    'shanta':   0.2,
    'dasya':    0.4,
    'sakhya':   0.6,
    'vatsalya': 0.8,
    'madhurya': 1.0,
}

# S0 entities are not placed on the toroid surface.
S0_PREFIXES = ('tattva_', 'parampara_', 'rasa_s')

# Toroid geometry — R and r determine the shape
# R = major radius (distance from center to tube center)
# r = minor radius (tube radius)
# R > r always for a proper toroid
TOROID_R = 3.0  # major radius
TOROID_r = 1.0  # minor radius


# ══════════════════════════════════════════════
# COORDINATE FUNCTIONS
# ══════════════════════════════════════════════

def toroid_3d(theta: float, phi: float,
              R: float = TOROID_R,
              r: float = TOROID_r) -> Tuple[float, float, float]:
    """
    Convert toroid surface coordinates (θ, φ) to 3D point (x, y, z).
    Used for visualization — maps directly to the brahmanda canvas.
    """
    x = (R + r * math.cos(phi)) * math.cos(theta)
    y = (R + r * math.cos(phi)) * math.sin(theta)
    z = r * math.sin(phi)
    return x, y, z


def toroidal_distance(theta1: float, phi1: float,
                      theta2: float, phi2: float,
                      R: float = TOROID_R,
                      r: float = TOROID_r) -> float:
    """
    Geodesic distance between two points on the toroid surface.
    Correctly wraps — distance from θ=0 to θ=2π is 0.

    This is the core metric. All coherence derives from this.
    """
    # Angular distances (wrapped to [0, π])
    d_theta = math.pi - abs(abs(theta1 - theta2) - math.pi)
    d_phi   = math.pi - abs(abs(phi1   - phi2)   - math.pi)

    # Arc lengths on the toroid surface
    arc_theta = d_theta * (R + r)  # approximate major arc
    arc_phi   = d_phi   * r        # minor arc

    return math.sqrt(arc_theta**2 + arc_phi**2)


def max_toroidal_distance(R: float = TOROID_R,
                          r: float = TOROID_r) -> float:
    """Maximum possible distance on this toroid (antipodal points)."""
    return math.sqrt((math.pi * (R + r))**2 + (math.pi * r)**2)


def coherence_from_distance(dist: float,
                             max_dist: Optional[float] = None) -> float:
    """
    Convert distance to coherence score 0.0–1.0.
    Close = coherent (1.0). Far = incoherent (0.0).
    Uses a gentle curve — not a hard threshold.
    """
    if max_dist is None:
        max_dist = max_toroidal_distance()
    # Cosine falloff — smooth, natural
    normalized = dist / max_dist  # 0.0 to 1.0
    return (math.cos(normalized * math.pi) + 1) / 2


# ══════════════════════════════════════════════
# PANCHANGA → TOROID COORDINATES
# ══════════════════════════════════════════════

def panchanga_to_coords(panchanga: Dict) -> Tuple[float, float]:
    """
    Convert a panchanga moment to toroid coordinates (θ, φ).

    Panchanga fields used:
      tithi_num   (1-30)
      nakshatra   (name string)
      vara        (day name)
      element     (earth/water/fire/air/ether)
      guna        (sattva/rajas/tamas)

    θ is a weighted blend of time signals.
    φ is a weighted blend of quality signals.
    """
    # ── θ (TIME axis) ──
    tithi_num = panchanga.get('tithi_num', 1)
    tithi_a = TITHI_ANGLE.get(tithi_num, 0)

    nak_name = panchanga.get('nakshatra', 'Ashwini')
    nak_a = NAKSHATRA_ANGLE.get(nak_name, 0)

    vara = panchanga.get('vara', 'Ravivara')
    vara_a = VARA_ANGLE.get(vara, 0)

    # Weighted blend — nakshatra is most specific
    theta = _circular_mean([
        (nak_a,   0.5),   # nakshatra dominates
        (tithi_a, 0.35),  # tithi significant
        (vara_a,  0.15),  # vara minor contribution
    ])

    # ── φ (QUALITY axis) ──
    element = panchanga.get('element', 'ether')
    elem_a = ELEMENT_ANGLE.get(element.lower(), 0)

    guna = panchanga.get('guna', 'sattva')
    guna_a = GUNA_ANGLE.get(guna.lower(), 0)

    phi = _circular_mean([
        (elem_a, 0.6),  # element dominates quality
        (guna_a, 0.4),  # guna secondary
    ])

    return theta, phi


def _circular_mean(angle_weight_pairs: List[Tuple[float, float]]) -> float:
    """
    Compute weighted circular mean of angles.
    Handles the wrapping problem correctly.
    """
    sin_sum = sum(w * math.sin(a) for a, w in angle_weight_pairs)
    cos_sum = sum(w * math.cos(a) for a, w in angle_weight_pairs)
    return math.atan2(sin_sum, cos_sum) % (2 * math.pi)


# ══════════════════════════════════════════════
# TOROIDAL FIELD — main class
# ══════════════════════════════════════════════

class ToroidalField:
    """
    The living toroidal coherence field.

    Holds all entity positions on the toroid surface.
    Computes coherence between any moment and any entity.
    The NPU accelerates batch queries.

    Usage:
        field = ToroidalField()
        moment_coords = field.moment_to_coords(panchanga)
        score = field.coherence(moment_coords, 'pranayama_bhramari')
        top = field.field_query(panchanga, top_n=10)
    """

    def __init__(self, R: float = TOROID_R, r: float = TOROID_r):
        self.R = R
        self.r = r
        self.max_dist = max_toroidal_distance(R, r)

        # Entity registry is dataset-backed, not hardcoded here.
        self.entities = dict(dataset_loader.load_all_entities())
        self.entity_metadata = dataset_loader.load_entity_metadata()
        self.relations = dataset_loader.load_relations()

        # S0 entities — eternal ground, not toroid participants
        self.s0_entities = {
            eid: meta
            for eid, meta in self.entity_metadata.items()
            if any(eid.startswith(p) for p in S0_PREFIXES)
        }

        # Build numpy arrays for batch operations
        self._build_arrays()

        # NPU compiled model
        self._ov_compiled = None
        self._ov_n = 0
        self._ov_dirty = True   # recompile on next query
        self._npu_call_count = 0
        if _npu_ready:
            self._compile_npu()

    def _build_arrays(self):
        """Build numpy arrays for vectorized coherence queries."""
        self.entity_ids = list(self.entities.keys())
        coords = np.array(list(self.entities.values()))  # (n, 2)
        self.entity_theta = coords[:, 0]  # (n,)
        self.entity_phi   = coords[:, 1]  # (n,)

    def register_entity(self, entity_id: str,
                        theta: float, phi: float):
        """Register a new entity on the toroid."""
        self.entities[entity_id] = (theta, phi)
        self._build_arrays()
        self._ov_dirty = True  # recompile NPU model with new entities

    def moment_to_coords(self, panchanga: Dict) -> Tuple[float, float]:
        """Convert panchanga to toroid coordinates."""
        return panchanga_to_coords(panchanga)

    def coherence(self, moment_coords: Tuple[float, float],
                  entity_id: str) -> float:
        """
        Coherence score between a moment and an entity.
        Returns 0.0 (incoherent) to 1.0 (fully coherent).
        """
        if entity_id not in self.entities:
            return 0.0

        theta1, phi1 = moment_coords
        theta2, phi2 = self.entities[entity_id]

        dist = toroidal_distance(theta1, phi1, theta2, phi2, self.R, self.r)
        return coherence_from_distance(dist, self.max_dist)

    def field_query(self, panchanga: Dict,
                    top_n: int = 10,
                    min_score: float = 0.0,
                    category: Optional[str] = None) -> List[Dict]:
        """
        Query the field — returns all entities sorted by coherence
        with the current moment.

        This is the NPU operation — batch distance query
        against all entities simultaneously.

        Args:
            panchanga: current field state
            top_n: number of results to return
            min_score: minimum coherence threshold
            category: filter by entity category
                      ('nakshatra', 'pranayama', 'raga', etc.)

        Returns:
            List of dicts: {entity_id, score, theta, phi, x, y, z}
        """
        theta1, phi1 = self.moment_to_coords(panchanga)

        # Vectorized distance computation — NPU or numpy fallback
        if _npu_ready:
            scores = self._npu_coherence_scores(theta1, phi1)
        else:
            d_theta = np.pi - np.abs(np.abs(self.entity_theta - theta1) - np.pi)
            d_phi   = np.pi - np.abs(np.abs(self.entity_phi   - phi1)   - np.pi)
            arc_theta = d_theta * (self.R + self.r)
            arc_phi   = d_phi   * self.r
            distances = np.sqrt(arc_theta**2 + arc_phi**2)
            normalized = distances / self.max_dist
            scores = (np.cos(normalized * np.pi) + 1) / 2

        # Build results
        results = []
        for i, entity_id in enumerate(self.entity_ids):
            score = float(scores[i])
            if score < min_score:
                continue
            if category and not entity_id.startswith(category):
                continue

            x, y, z = toroid_3d(
                float(self.entity_theta[i]),
                float(self.entity_phi[i]),
                self.R, self.r
            )

            results.append({
                'entity_id': entity_id,
                'score': round(score, 4),
                'theta': float(self.entity_theta[i]),
                'phi': float(self.entity_phi[i]),
                'x': round(x, 3),
                'y': round(y, 3),
                'z': round(z, 3),
            })

        # Category weights — boost cosmological, penalize herb catalogues
        _W = {
            "nakshatra": 1.5, "graha": 1.4, "deity": 1.4,
            "tithi": 1.3, "devi": 1.3, "vara": 1.2,
            "raga": 1.3, "tala": 1.2, "svara": 1.2, "bija": 1.2,
            "plant": 1.0, "dosha": 1.0, "element": 1.0, "marma": 0.9,
            "mythic": 0.6, "jyotish": 0.5, "amidha": 0.3, "herb": 0.3,
        }
        for r in results:
            eid = r['entity_id']
            if 'amidha_herb' in eid:
                w = 0.3
            elif 'herb_spine' in eid:
                w = 0.3
            else:
                p = eid.split('_')[0] if '_' in eid else eid
                w = _W.get(p, 0.8)
            r['score'] = round(r['score'] * w, 4)

        # ── S0 source-pull ──────────────────────────────────────
        # Bhakti-rasa tagged entities receive depth boost toward source.
        # Bounded — never pushes above 1.0. Axiomatic not geometric.
        for r in results:
            meta = self.entity_metadata.get(r['entity_id'], {})
            bhakti_rasa = meta.get('bhakti_rasa', '')
            if bhakti_rasa in BHAKTI_RASA_DEPTH:
                depth = BHAKTI_RASA_DEPTH[bhakti_rasa]
                r['score'] = round(min(1.0, r['score'] + depth * 0.15), 4)
                r['source_pull'] = depth

        # Sort by coherence descending
        results.sort(key=lambda r: r['score'], reverse=True)
        return results[:top_n]

    def _compile_npu(self):
        """Build and compile an OpenVINO model for toroidal coherence.

        Entity coords are baked in as CONSTANTS — only the moment
        position (theta1, phi1) is a runtime input. This means:
          - No entity data transfer on each inference call
          - NPU can optimize the constant arrays
          - Must recompile when entities change (_ov_dirty flag)

        Input:  moment (2,) float32  — [theta1, phi1]
        Output: scores (N,) float32  — coherence per entity

        Graph:
          d_theta = pi - |  |entity_theta - theta1| - pi  |
          d_phi   = pi - |  |entity_phi   - phi1  | - pi  |
          arc_theta = d_theta * (R + r)
          arc_phi   = d_phi * r
          dist = sqrt(arc_theta^2 + arc_phi^2)
          score = (cos(dist / max_dist * pi) + 1) / 2
        """
        try:
            import openvino.runtime.opset13 as ops
            from openvino.runtime import Model, Type, Shape

            n = len(self.entity_theta)
            self._ov_n = n

            # ── Single input: moment coords [theta1, phi1] ──
            moment = ops.parameter(Shape([2]), Type.f32, name="moment")

            # ── Entity coords baked as constants ──
            e_theta = ops.constant(self.entity_theta.astype(np.float32))  # (N,)
            e_phi = ops.constant(self.entity_phi.astype(np.float32))      # (N,)

            # ── Scalar constants ──
            pi_c = ops.constant(np.float32(np.pi))
            Rr_c = ops.constant(np.float32(self.R + self.r))
            r_c = ops.constant(np.float32(self.r))
            max_d_c = ops.constant(np.float32(self.max_dist))
            one_c = ops.constant(np.float32(1.0))
            two_c = ops.constant(np.float32(2.0))

            # ── Extract theta1, phi1 from moment input ──
            axis_0 = ops.constant(np.int64(0))
            m_theta = ops.gather(moment, ops.constant(np.int64(0)), axis_0)  # scalar
            m_phi = ops.gather(moment, ops.constant(np.int64(1)), axis_0)    # scalar

            # ── Circular distance on toroid ──
            # d = pi - abs(abs(a - b) - pi)  wraps correctly on [0, 2pi]
            d_theta = ops.subtract(pi_c,
                ops.abs(ops.subtract(ops.abs(ops.subtract(e_theta, m_theta)), pi_c)))
            d_phi = ops.subtract(pi_c,
                ops.abs(ops.subtract(ops.abs(ops.subtract(e_phi, m_phi)), pi_c)))

            # ── Arc lengths ──
            arc_theta = ops.multiply(d_theta, Rr_c)
            arc_phi = ops.multiply(d_phi, r_c)

            # ── Euclidean distance ──
            dist = ops.sqrt(ops.add(
                ops.multiply(arc_theta, arc_theta),
                ops.multiply(arc_phi, arc_phi)))

            # ── Coherence: (cos(dist/max_dist * pi) + 1) / 2 ──
            norm = ops.multiply(ops.divide(dist, max_d_c), pi_c)
            scores = ops.divide(ops.add(ops.cos(norm), one_c), two_c)

            result = ops.result(scores, name="scores")
            model = Model([result], [moment], "toroidal_coherence")

            self._ov_compiled = _ov_core.compile_model(model, _OV_DEVICE)
            self._ov_dirty = False
            print(f"  ✓ NPU compiled: {n} entities baked, device={_OV_DEVICE}")

        except Exception as e:
            print(f"  ⚠ NPU compile failed: {e} — numpy fallback")
            self._ov_compiled = None
            self._ov_dirty = False

    def _npu_coherence_scores(self, theta1: float, phi1: float) -> np.ndarray:
        """Run coherence scoring on NPU.

        Only the moment position is sent — entity coords are baked
        into the compiled model as constants.
        """
        import time as _time

        # Recompile if entities changed
        if self._ov_dirty:
            self._compile_npu()

        if self._ov_compiled is not None:
            try:
                t0 = _time.perf_counter()

                # Single input: [theta1, phi1]
                moment = np.array([theta1, phi1], dtype=np.float32)
                result = self._ov_compiled({"moment": moment})
                scores = next(iter(result.values())).flatten()

                self._npu_call_count += 1
                if self._npu_call_count % 100 == 0:
                    elapsed_ms = (_time.perf_counter() - t0) * 1000
                    print(f"  NPU inference: {self._ov_n} entities in {elapsed_ms:.1f}ms")

                return scores

            except Exception as e:
                # Runtime failure — fall through to numpy
                if self._npu_call_count == 0:
                    print(f"  ⚠ NPU runtime error: {e}")

        # Numpy fallback (silent)
        d_theta = np.pi - np.abs(np.abs(self.entity_theta - theta1) - np.pi)
        d_phi   = np.pi - np.abs(np.abs(self.entity_phi   - phi1)   - np.pi)
        arc_theta = d_theta * (self.R + self.r)
        arc_phi   = d_phi   * self.r
        distances = np.sqrt(arc_theta**2 + arc_phi**2)
        normalized = distances / self.max_dist
        return (np.cos(normalized * np.pi) + 1) / 2

    def moment_3d(self, panchanga: Dict) -> Tuple[float, float, float]:
        """Get the 3D position of the current moment on the toroid."""
        theta, phi = self.moment_to_coords(panchanga)
        return toroid_3d(theta, phi, self.R, self.r)

    def explain(self, panchanga: Dict, entity_id: str) -> Dict:
        """
        Explain why an entity has a given coherence score.
        Returns the contributing factors.
        """
        if entity_id not in self.entities:
            return {'error': f'entity {entity_id} not found'}

        moment_theta, moment_phi = self.moment_to_coords(panchanga)
        entity_theta, entity_phi = self.entities[entity_id]

        score = self.coherence((moment_theta, moment_phi), entity_id)

        d_theta = math.pi - abs(abs(moment_theta - entity_theta) - math.pi)
        d_phi   = math.pi - abs(abs(moment_phi   - entity_phi)   - math.pi)

        return {
            'entity_id': entity_id,
            'score': round(score, 4),
            'theta_distance': round(d_theta, 4),
            'phi_distance': round(d_phi, 4),
            'time_alignment': round(1 - d_theta / math.pi, 4),
            'quality_alignment': round(1 - d_phi / math.pi, 4),
            'moment': {
                'theta': round(moment_theta, 4),
                'phi': round(moment_phi, 4),
            },
            'entity': {
                'theta': round(entity_theta, 4),
                'phi': round(entity_phi, 4),
            },
        }

    def entity_count(self) -> int:
        return len(self.entities)

    def categories(self) -> List[str]:
        """List all entity categories registered."""
        cats = set()
        for eid in self.entity_ids:
            cats.add(eid.split('_')[0])
        return sorted(cats)


    def s0_ground(self) -> dict:
        """Return the S0 axiomatic ground — eternal entities that underlie
        the material field. Not coherence-scored. The source the field blooms from.
        """
        by_category = {}
        for eid, meta in self.s0_entities.items():
            cat = meta.get('category', 'other')
            by_category.setdefault(cat, []).append({
                'entity_id': eid,
                'name': meta.get('name_iast', eid),
                'description': meta.get('description', ''),
                'source': meta.get('source', ''),
                'layer': 'S0',
                'on_toroid': False,
            })
        return by_category


# ══════════════════════════════════════════════
# QUICK TEST
# ══════════════════════════════════════════════

if __name__ == '__main__':
    print("✦ Toroidal Field — Coherence Atlas bead 009")
    print()

    field = ToroidalField()
    print(f"Entities registered: {field.entity_count()}")
    print(f"Categories: {field.categories()}")
    print()

    # Test with today's field state
    test_panchanga = {
        'tithi_num': 4,          # Caturthī
        'nakshatra': 'Shravana', # ears
        'vara': 'Guruvara',      # Thursday
        'element': 'air',
        'guna': 'sattva',
    }

    print("Today's field: Kṛṣṇa Caturthī · Śravaṇa · Guruvāra")
    theta, phi = field.moment_to_coords(test_panchanga)
    x, y, z = field.moment_3d(test_panchanga)
    print(f"Toroid coords: θ={theta:.3f} φ={phi:.3f}")
    print(f"3D position:   x={x:.3f} y={y:.3f} z={z:.3f}")
    print()

    print("Top 10 coherent entities:")
    results = field.field_query(test_panchanga, top_n=10)
    for r in results:
        bar = '█' * int(r['score'] * 20)
        print(f"  {r['score']:.3f} {bar:<20} {r['entity_id']}")
    print()

    explain_id = results[0]['entity_id'] if results else 'nakshatra_shravana'
    print(f"Explain {explain_id} coherence:")
    exp = field.explain(test_panchanga, explain_id)
    print(f"  Score:             {exp['score']}")
    print(f"  Time alignment:    {exp['time_alignment']}")
    print(f"  Quality alignment: {exp['quality_alignment']}")
