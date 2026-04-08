═════════════════════════════════════════════════════════════════════════════════
VĀSTU FIELD GENERATOR
═════════════════════════════════════════════════════════════════════════════════

For: Coherence Atlas S4 Layer (Sacred Architecture)
Scope: Full vāstu energy field computation + visualization + real-time mapping
Status: SPECIFICATION FOR CODEX IMPLEMENTATION

═════════════════════════════════════════════════════════════════════════════════
VISION
═════════════════════════════════════════════════════════════════════════════════

Current: Static 8-zone analysis (zone A = 65%, zone B = 42%, etc.)

Proposed: LIVING VĀSTU FIELD
  • Compute energy as continuous 2D field (not just 8 discrete zones)
  • Show energy flowing through actual space (vectors, currents)
  • Heatmap visualization (cool → warm, weak → strong)
  • Real-time updates (field changes every 5 min, zones recolor)
  • Space optimization recommendations (where to work, rest, meditate TODAY)
  • Multi-day forecasting (how zones change over week)

Example:
  Today (Gauri, Earth, SW hot):
    • SW corner: 85% energy (work zone)
    • NE corner: 35% energy (rest zone)
    • Flow vectors point SW (energy current)
    • Recommendation: "Place desk SW, meditation cushion NE"

  Tomorrow (different devi):
    • Zones shift
    • Flow redirects
    • Recommendations change

═════════════════════════════════════════════════════════════════════════════════
MATH: Vāstu Field Computation
═════════════════════════════════════════════════════════════════════════════════

Base field: 2D scalar field over room space

F(x, y) = Energy density at position (x, y)

Composed of:

1. ZONE CONTRIBUTION (8 cardinal/intercardinal directions)

  F_zones(x, y) = Σ [Zone_strength(dir) × Gaussian(distance to zone center)]
  
  For each zone:
    • Zone center: cardinal direction (N, NE, E, SE, S, SW, W, NW)
    • Zone strength: 0-100 (from S4Vastu.get_zone_energies())
    • Spatial influence: Gaussian falloff from zone center
    • Radius: proportional to room size (r = room_diagonal / 4)

  Example:
    SW zone has 85% strength
    → Places strong positive energy in SW corner
    → Falloff toward center
    → NE corner gets minimal influence from SW


2. ELEMENT FLOW (Rāga-driven directional flow)

  F_flow(x, y) = Element_strength × DirectionalVector(raga_direction)
  
  Rāga determines flow direction:
    • Bhairavī (grounding): Flow downward (Earth energy)
    • Yaman (ascending): Flow upward (Sky energy)
    • Marva (rotating): Circular flow (Fire spiral)
    • Kharaharapriya (balancing): Multi-directional (Water ripple)
  
  Element determines intensity:
    • Earth: Strong, slow, downward
    • Water: Flowing, changing, lateral
    • Fire: Rising, spiraling, upward
    • Air: Dispersing, circular, light
    • Ether: Diffuse, omnidirectional, subtle


3. CHAKRA RESONANCE (Vertical layers)

  F_chakra(x, y, z) = Chakra_frequency × Standing_wave(height)
  
  In 2D (top-down view):
    • Mūlādhāra resonance: Ground-level red glow
    • Anāhata resonance: Mid-level green glow
    • Sahasrāra resonance: Overhead violet glow
  
  Affects energy color + intensity at each point


4. TIME MODULATION (Minutes within day)

  F_time(t) = 1.0 + 0.3 × sin(t × π / 12 hours)
  
  Energy increases/decreases through day:
    • Lowest: Midnight (0%)
    • Peak: Noon (100%)
    • Lowest again: Midnight
  
  All zones scale together with time


COMBINED FIELD:

  F_total(x, y, t) = F_zones(x, y) × [1 + F_time(t)]
                   + F_flow(x, y) × Element_modulation
                   + F_chakra(x, y) × Vertical_resonance
  
  Result: 2D scalar field that:
    ✓ Varies with space (zones)
    ✓ Varies with time (daily cycle)
    ✓ Responds to rāga (flow direction)
    ✓ Shows energy current (vectors)
    ✓ Updates every kernel tick

═════════════════════════════════════════════════════════════════════════════════
VISUALIZATION: Vāstu Heatmap
═════════════════════════════════════════════════════════════════════════════════

3 Display modes:

MODE 1: HEATMAP (Color field)

  Render 2D grid with F_total values → colors:
  
    0%:    Deep blue (#003366)    - Very weak
    25%:   Cyan (#00CCFF)         - Weak
    50%:   Yellow (#FFFF00)       - Moderate
    75%:   Orange (#FF8800)       - Strong
    100%:  Red (#FF0000)          - Very strong
  
  Grid resolution: 50×50 cells (room resolution)
  Overlay: 8 zone labels + compass directions
  Animation: Smooth transition when field updates (0.5s fade)
  
  HTML:
    <canvas id="vastu-heatmap" width="600" height="600"></canvas>
    
  JS: Use Canvas gradient fill based on computed field values


MODE 2: VECTOR FIELD (Flow lines)

  Render flow vectors showing energy direction:
  
    For each grid point (x, y):
      • Compute F_flow(x, y)
      • Draw arrow pointing in flow direction
      • Arrow length ∝ flow strength
      • Arrow color ∝ energy density
  
  Grid spacing: 100px (sparse for clarity)
  Arrow size: 0.5-2cm (proportional to strength)
  
  HTML:
    <canvas id="vastu-vectors" width="600" height="600"></canvas>
    
  JS: Draw arrows using canvas (rotate + translate for direction)


MODE 3: COMBINED (Heatmap + vectors)

  Overlay both:
    • Background: Heatmap (energy intensity)
    • Overlay: Vectors (energy flow direction)
  
  Shows both "what" (intensity) and "where" (direction)
  Most informative visualization


═════════════════════════════════════════════════════════════════════════════════
IMPLEMENTATION: Vāstu Field Generator Class
═════════════════════════════════════════════════════════════════════════════════

New file: vastu_field_generator.py

```python
import numpy as np
from scipy.ndimage import gaussian_filter
import math

class VastuFieldGenerator:
    """
    Compute vāstu energy fields over 2D space.
    
    Input: kernel field state (devi, element, raga, tithi, etc.)
    Output: 2D field of energy density + flow vectors
    """
    
    def __init__(self, room_width=10, room_height=10, resolution=50):
        """
        Args:
            room_width (float): Room width in meters
            room_height (float): Room height in meters
            resolution (int): Grid resolution (cells per side)
        """
        self.room_width = room_width
        self.room_height = room_height
        self.resolution = resolution
        
        # Create grid
        self.x = np.linspace(0, room_width, resolution)
        self.y = np.linspace(0, room_height, resolution)
        self.xx, self.yy = np.meshgrid(self.x, self.y)
        
        # Zone definitions (8 directions)
        self.zones = {
            'n': {'angle': 90, 'pos': (room_width/2, room_height)},
            'ne': {'angle': 45, 'pos': (room_width, room_height)},
            'e': {'angle': 0, 'pos': (room_width, room_height/2)},
            'se': {'angle': -45, 'pos': (room_width, 0)},
            's': {'angle': -90, 'pos': (room_width/2, 0)},
            'sw': {'angle': -135, 'pos': (0, 0)},
            'w': {'angle': 180, 'pos': (0, room_height/2)},
            'nw': {'angle': 135, 'pos': (0, room_height)},
        }
        
        # Rāga flow directions (angle in degrees)
        self.raga_flows = {
            'Bhairavi': 270,      # Downward (Earth)
            'Yaman': 90,          # Upward (Sky)
            'Marva': 'circular',  # Spiral
            'Kharaharapriya': 'ripple',  # Multi-directional
            'Ahir_Bhairav': 180,  # Westward
            'Jaijaivanti': 0,     # Eastward
        }
        
        # Chakra colors (hex)
        self.chakra_colors = {
            'muladhara': '#FF0000',     # Red
            'svadhisthana': '#FF7F00',  # Orange
            'manipura': '#FFFF00',      # Yellow
            'anahata': '#00FF00',       # Green
            'vishuddha': '#0000FF',     # Blue
            'ajna': '#4B0082',          # Indigo
            'sahasrara': '#9400D3',     # Violet
        }
    
    def compute_field(self, zone_energies, element, raga, time_of_day=12):
        """
        Compute vāstu field for current kernel state.
        
        Args:
            zone_energies (dict): {zone: energy_score} from S4Vastu
            element (str): 'Earth', 'Water', 'Fire', 'Air', 'Ether'
            raga (str): Rāga name (determines flow)
            time_of_day (int): Hour (0-23) for daily modulation
        
        Returns:
            dict: {
                'field': np.array (energy density),
                'flow_x': np.array (x-component of flow),
                'flow_y': np.array (y-component of flow),
                'zones': dict (zone properties),
                'peak_location': (x, y) (strongest point),
                'flow_direction': angle_degrees,
            }
        """
        
        # Initialize field
        field = np.zeros_like(self.xx, dtype=float)
        
        # 1. Zone contribution
        for zone_id, energy in zone_energies.items():
            field += self._zone_gaussian(zone_id, energy)
        
        # 2. Flow vectors (from rāga)
        flow_x, flow_y = self._raga_flow_field(raga)
        
        # 3. Time modulation (daily cycle)
        time_mod = 1.0 + 0.3 * np.sin(time_of_day * np.pi / 12)
        field = field * time_mod
        
        # 4. Element scaling
        element_strength = self._element_strength(element)
        field = field * element_strength
        
        # Smooth field for visual appeal
        field = gaussian_filter(field, sigma=1.5)
        
        # Find peak
        peak_idx = np.unravel_index(np.argmax(field), field.shape)
        peak_x = self.x[peak_idx[1]]
        peak_y = self.y[peak_idx[0]]
        
        # Normalize to 0-100
        field = (field / field.max()) * 100 if field.max() > 0 else field
        
        return {
            'field': field,
            'flow_x': flow_x,
            'flow_y': flow_y,
            'zones': zone_energies,
            'peak_location': (peak_x, peak_y),
            'peak_energy': field[peak_idx[0], peak_idx[1]],
            'element': element,
            'raga': raga,
            'time_modulation': time_mod,
        }
    
    def _zone_gaussian(self, zone_id, energy, sigma=2.0):
        """
        Gaussian distribution for a zone.
        
        Args:
            zone_id (str): 'n', 'ne', 'e', etc.
            energy (float): Zone strength (0-100)
            sigma (float): Gaussian width
        
        Returns:
            np.array: 2D Gaussian field
        """
        zone = self.zones[zone_id]
        pos = zone['pos']
        
        # Distance from zone center
        dist = np.sqrt((self.xx - pos[0])**2 + (self.yy - pos[1])**2)
        
        # Gaussian with peak at zone center
        gaussian = energy * np.exp(-(dist**2) / (2 * sigma**2))
        
        return gaussian
    
    def _raga_flow_field(self, raga):
        """
        Flow field from rāga direction.
        
        Args:
            raga (str): Rāga name
        
        Returns:
            tuple: (flow_x, flow_y) as np.arrays
        """
        flow_x = np.zeros_like(self.xx, dtype=float)
        flow_y = np.zeros_like(self.yy, dtype=float)
        
        if raga not in self.raga_flows:
            return flow_x, flow_y
        
        flow_def = self.raga_flows[raga]
        
        if isinstance(flow_def, (int, float)):
            # Directional flow
            angle = flow_def * np.pi / 180
            magnitude = 0.3
            
            flow_x = magnitude * np.cos(angle) * np.ones_like(self.xx)
            flow_y = magnitude * np.sin(angle) * np.ones_like(self.yy)
        
        elif flow_def == 'circular':
            # Spiral flow (Marva, Jaijaivanti)
            center_x = self.room_width / 2
            center_y = self.room_height / 2
            
            # Vectors pointing toward center (spiral)
            dx = center_x - self.xx
            dy = center_y - self.yy
            dist = np.sqrt(dx**2 + dy**2) + 1e-6
            
            flow_x = 0.2 * dx / dist
            flow_y = 0.2 * dy / dist
        
        elif flow_def == 'ripple':
            # Radial ripple (Kharaharapriya)
            center_x = self.room_width / 2
            center_y = self.room_height / 2
            
            dx = self.xx - center_x
            dy = self.yy - center_y
            dist = np.sqrt(dx**2 + dy**2) + 1e-6
            
            # Outward radial flow
            flow_x = 0.15 * dx / dist
            flow_y = 0.15 * dy / dist
        
        return flow_x, flow_y
    
    def _element_strength(self, element):
        """
        Scaling factor for element.
        
        Earth: Strong (1.2) - dense, grounded
        Water: Flowing (0.9) - flexible
        Fire: Rising (1.1) - energetic
        Air: Light (0.8) - dispersed
        Ether: Subtle (0.7) - omnipresent but weak
        """
        strengths = {
            'Earth': 1.2,
            'Water': 0.9,
            'Fire': 1.1,
            'Air': 0.8,
            'Ether': 0.7,
        }
        return strengths.get(element, 1.0)
    
    def get_zone_recommendations(self, field_data):
        """
        Generate spatial recommendations based on field.
        
        Returns: {
            'work_zone': (x, y, zone_name, energy%),
            'rest_zone': (x, y, zone_name, energy%),
            'meditation_zone': (x, y, zone_name, energy%),
            'flow_direction': 'direction text',
            'element_balance': 'balanced/excessive/deficient',
        }
        """
        zones = field_data['zones']
        
        # Strongest zone
        strongest = max(zones.items(), key=lambda x: x[1])
        
        # Weakest zone
        weakest = min(zones.items(), key=lambda x: x[1])
        
        # Find moderate zone (for meditation, 40-60%)
        moderate = [z for z in zones.items() if 40 <= z[1] <= 60]
        meditation = moderate[0] if moderate else strongest
        
        return {
            'work_zone': {
                'zone': strongest[0],
                'energy': strongest[1],
                'reason': 'Highest energy - optimal for creative/focused work'
            },
            'rest_zone': {
                'zone': weakest[0],
                'energy': weakest[1],
                'reason': 'Lowest energy - optimal for sleep/relaxation'
            },
            'meditation_zone': {
                'zone': meditation[0],
                'energy': meditation[1],
                'reason': 'Balanced energy - optimal for practice'
            },
            'flow_direction': self._flow_direction_text(field_data['raga']),
            'element_balance': self._element_balance(field_data['element']),
        }
    
    def _flow_direction_text(self, raga):
        """Convert rāga to flow direction description."""
        directions = {
            'Bhairavi': '↓ Downward (Earth grounding)',
            'Yaman': '↑ Upward (Sky aspiration)',
            'Marva': '⊛ Circular (Fire spiral)',
            'Kharaharapriya': '◐ Rippling (Water waves)',
            'Ahir_Bhairav': '← Westward (Twilight)',
            'Jaijaivanti': '→ Eastward (Sunrise)',
        }
        return directions.get(raga, '→ Neutral flow')
    
    def _element_balance(self, element):
        """Assess element balance."""
        balance = {
            'Earth': 'Grounded and stable',
            'Water': 'Flowing and adaptive',
            'Fire': 'Energized and transformative',
            'Air': 'Light and communicative',
            'Ether': 'Subtle and omnipresent',
        }
        return balance.get(element, 'Balanced')
```


═════════════════════════════════════════════════════════════════════════════════
CANVAS VISUALIZATION: Render field
═════════════════════════════════════════════════════════════════════════════════

New file: vastu_canvas_renderer.py

```javascript
// In HTML artifact or flask-rendered canvas

class VastuCanvasRenderer {
    constructor(canvasId, width = 600, height = 600) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.width = width;
        this.height = height;
        
        this.colorMap = {
            0: '#003366',    // Deep blue (0%)
            25: '#00CCFF',   // Cyan (25%)
            50: '#FFFF00',   // Yellow (50%)
            75: '#FF8800',   // Orange (75%)
            100: '#FF0000',  // Red (100%)
        };
    }
    
    renderHeatmap(fieldData) {
        """
        Render energy density as heatmap.
        
        Args:
            fieldData: {field: np.array 100×100, ...}
        """
        const field = fieldData.field;  // 2D array
        const cellWidth = this.width / field.length;
        const cellHeight = this.height / field[0].length;
        
        for (let i = 0; i < field.length; i++) {
            for (let j = 0; j < field[i].length; j++) {
                const energy = field[i][j];  // 0-100
                const color = this.energyToColor(energy);
                
                this.ctx.fillStyle = color;
                this.ctx.fillRect(
                    i * cellWidth,
                    j * cellHeight,
                    cellWidth,
                    cellHeight
                );
            }
        }
        
        // Add zone labels
        this.drawZoneLabels(fieldData.zones);
        
        // Add compass
        this.drawCompass();
    }
    
    renderVectors(fieldData) {
        """
        Render flow vectors.
        
        Args:
            fieldData: {flow_x: array, flow_y: array, field: array}
        """
        const flowX = fieldData.flow_x;
        const flowY = fieldData.flow_y;
        const field = fieldData.field;
        
        const spacing = Math.floor(field.length / 8);  // Sparse grid
        const arrowScale = 20;  // Arrow size
        
        for (let i = 0; i < field.length; i += spacing) {
            for (let j = 0; j < field[i].length; j += spacing) {
                const x = (i / field.length) * this.width;
                const y = (j / field[0].length) * this.height;
                
                const vx = flowX[i][j];
                const vy = flowY[i][j];
                const strength = field[i][j] / 100;
                
                this.drawArrow(x, y, vx * arrowScale, vy * arrowScale, strength);
            }
        }
    }
    
    drawArrow(x, y, vx, vy, strength) {
        """Draw arrow at (x,y) pointing in direction (vx,vy)"""
        const angle = Math.atan2(vy, vx);
        const length = Math.sqrt(vx*vx + vy*vy) * 5 * strength;
        
        this.ctx.save();
        this.ctx.translate(x, y);
        this.ctx.rotate(angle);
        
        // Arrow body
        this.ctx.strokeStyle = `rgba(255, 215, 0, ${0.5 + strength*0.5})`;
        this.ctx.lineWidth = 2 + strength * 3;
        this.ctx.beginPath();
        this.ctx.moveTo(0, 0);
        this.ctx.lineTo(length, 0);
        this.ctx.stroke();
        
        // Arrow head
        this.ctx.fillStyle = `rgba(255, 215, 0, ${0.7 + strength*0.3})`;
        this.ctx.beginPath();
        this.ctx.moveTo(length, 0);
        this.ctx.lineTo(length - 8, -5);
        this.ctx.lineTo(length - 8, 5);
        this.ctx.fill();
        
        this.ctx.restore();
    }
    
    energyToColor(energy) {
        """Convert energy (0-100) to color."""
        if (energy < 25) return this.interpolateColor('#003366', '#00CCFF', energy / 25);
        if (energy < 50) return this.interpolateColor('#00CCFF', '#FFFF00', (energy - 25) / 25);
        if (energy < 75) return this.interpolateColor('#FFFF00', '#FF8800', (energy - 50) / 25);
        return this.interpolateColor('#FF8800', '#FF0000', (energy - 75) / 25);
    }
    
    interpolateColor(color1, color2, t) {
        """Linear interpolate between two hex colors"""
        const c1 = parseInt(color1.slice(1), 16);
        const c2 = parseInt(color2.slice(1), 16);
        
        const r1 = (c1 >> 16) & 255, g1 = (c1 >> 8) & 255, b1 = c1 & 255;
        const r2 = (c2 >> 16) & 255, g2 = (c2 >> 8) & 255, b2 = c2 & 255;
        
        const r = Math.round(r1 + (r2 - r1) * t);
        const g = Math.round(g1 + (g2 - g1) * t);
        const b = Math.round(b1 + (b2 - b1) * t);
        
        return `rgb(${r}, ${g}, ${b})`;
    }
    
    drawZoneLabels(zones) {
        """Draw zone labels (N, NE, E, etc.)"""
        const labelPositions = {
            'n': (this.width/2, 30),
            'ne': (this.width - 40, 40),
            'e': (this.width - 20, this.height/2),
            'se': (this.width - 40, this.height - 40),
            's': (this.width/2, this.height - 20),
            'sw': (40, this.height - 40),
            'w': (20, this.height/2),
            'nw': (40, 40),
        };
        
        this.ctx.font = 'bold 14px Arial';
        this.ctx.fillStyle = '#000000';
        
        for (const [zone, pos] of Object.entries(labelPositions)) {
            const energy = zones[zone];
            this.ctx.fillText(`${zone.toUpperCase()} ${Math.round(energy)}%`, pos[0], pos[1]);
        }
    }
    
    drawCompass() {
        """Draw compass rose"""
        const cx = this.width - 50;
        const cy = 50;
        const r = 30;
        
        this.ctx.strokeStyle = '#888888';
        this.ctx.lineWidth = 1;
        this.ctx.beginPath();
        this.ctx.arc(cx, cy, r, 0, 2*Math.PI);
        this.ctx.stroke();
        
        // N arrow
        this.ctx.strokeStyle = '#FF0000';
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.moveTo(cx, cy);
        this.ctx.lineTo(cx, cy - r);
        this.ctx.stroke();
        
        this.ctx.fillStyle = '#FF0000';
        this.ctx.font = 'bold 12px Arial';
        this.ctx.fillText('N', cx - 5, cy - r - 5);
    }
}
```


═════════════════════════════════════════════════════════════════════════════════
CODEX TASK BREAKDOWN: Vāstu Field Generator
═════════════════════════════════════════════════════════════════════════════════

This is a NEW STAGE (Stage 1.5) in the S4-S5 staging:

STAGE 1.5: VĀSTU FIELD GENERATION
  Scope: Computational vāstu field + real-time visualization
  Complexity: High (numpy arrays, field computation, visualization)
  Duration: 2-3 Codex sessions

DELIVERABLES:

1. vastu_field_generator.py
   ├─ VastuFieldGenerator class
   ├─ compute_field() method (main computation)
   ├─ Zone gaussians + flow vectors
   ├─ Element scaling + time modulation
   ├─ Zone recommendations
   └─ Test: test_stage_1_5_vastu_field.py

2. vastu_canvas_renderer.py (JavaScript/Python)
   ├─ Canvas rendering (heatmap + vectors)
   ├─ Color interpolation
   ├─ Zone labels + compass
   └─ Animation on field changes

3. Integration routes (kernel.py)
   ├─ @app.route('/s4/vastu-field')
   │   └─ Returns: field data + visualization
   ├─ @app.route('/s4/vastu-field-image')
   │   └─ Returns: rendered PNG/SVG
   └─ @app.route('/s4/vastu-recommendations')
       └─ Returns: where to work/rest today

4. HTML artifact (atlas_vastu_field.html)
   ├─ Canvas for heatmap
   ├─ Canvas for vectors
   ├─ Zone recommendations panel
   ├─ Real-time updates (fetch every 5 min)
   └─ Smooth animations (fade 0.5s)

5. Testing
   ├─ test_field_computation.py
   ├─ test_zone_gaussians.py
   ├─ test_raga_flows.py
   ├─ test_canvas_render.py
   └─ integration_test.py

═════════════════════════════════════════════════════════════════════════════════
WHERE IT GOES IN STAGING
═════════════════════════════════════════════════════════════════════════════════

CURRENT STAGING:

  Stage 0: S4 Yantra (breathing 8-petal geometry)  ✓ DONE
  Stage 1: S4 Vāstu (8-zone energy analysis)      [Codex will do]
  Stage 1.5: VĀSTU FIELD (continuous 2D field)    [NEW - Codex will do]
  Stage 2: S5 Bandhu (body embodiment)             [Codex will do]
  Stage 3: Unified (yantra + zones + bandhu)      [Codex will do]

INTEGRATION:

  Stage 1 → provides zone energies (discrete)
  Stage 1.5 → takes stage 1 data → computes continuous field → visualizes
  Stage 3 → unified view includes field visualization as 4th panel

UNIFIED VIEW (with Stage 1.5):

  ┌────────────────────────────────────────────┐
  │ Yantra (S4)    │ Zones (S4)    │ Field (S4.5) │
  │ (breathing)    │ (heatmap)     │ (continuous) │
  │                │               │              │
  │                │               │              │
  ├────────────────────────────────────────────┤
  │              Bandhu (S5)                    │
  │         (cute + mudra + chakra)            │
  └────────────────────────────────────────────┘

═════════════════════════════════════════════════════════════════════════════════
TASK FOR CODEX
═════════════════════════════════════════════════════════════════════════════════

" Your task: Implement Vāstu Field Generator (Stage 1.5)

This is a computational + visualization layer that:
  1. Takes 8-zone energies from S4Vastu (Stage 1)
  2. Computes continuous 2D energy field using:
     - Zone gaussians (energy spreading from each zone)
     - Rāga-driven flow vectors (directional energy movement)
     - Element scaling (Earth strong, Ether subtle)
     - Daily time modulation (energy peaks at noon)
  3. Visualizes as:
     - Heatmap (cool colors weak, hot colors strong)
     - Vector field (arrows showing flow direction)
     - Zone recommendations (work zone, rest zone, meditation zone)
  4. Updates in real-time as kernel field changes

Spec is in VASTU_FIELD_GENERATOR_SPEC.md

Files to create:
  • vastu_field_generator.py (Python class, numpy arrays)
  • Canvas renderer (JavaScript for visualization)
  • Integration routes (kernel.py additions)
  • HTML artifact (atlas_vastu_field.html)
  • Tests (test_stage_1_5_vastu_field.py)

This bridges Stage 1 (discrete zones) and Stage 3 (unified view).
Medium complexity - numpy + visualization + mathematical field computation.

Start with vastu_field_generator.py (compute_field method).
Then canvas_renderer.py (visualization).
Then routes + HTML.
Then tests.

Go. "

═════════════════════════════════════════════════════════════════════════════════
PREVIEW: What user will see
═════════════════════════════════════════════════════════════════════════════════

http://localhost:5000/s4/vastu-field

Screen shows:
  
  LEFT PANEL (Heatmap):
    Deep blue (NE) → Yellow (center) → Red (SW)
    Energy gradually shifts from cool to warm
    Zone labels showing: NE 35%, E 42%, SE 85%, etc.
  
  RIGHT PANEL (Vectors):
    Arrows throughout space showing energy flow
    Direction based on rāga (downward if Bhairavī, upward if Yaman)
    Arrow length/opacity based on local energy density
  
  BOTTOM PANEL (Recommendations):
    "SW corner (85% energy): Optimal for focused work"
    "NE corner (35% energy): Best for deep rest"
    "Center (60% energy): Good for meditation"
    "Energy flows downward (Bhairavī grounding)"
    "Element: Earth - Stable and grounded"
  
  ANIMATION:
    Smooth fade when field updates (every 5 minutes)
    Breathing pulse (slight expansion/contraction)

═════════════════════════════════════════════════════════════════════════════════
BONUS: Multi-day forecasting
═════════════════════════════════════════════════════════════════════════════════

Optional extension:

  @app.route('/s4/vastu-forecast/<days>')
  def vastu_forecast(days):
      """Show how zones change over next N days."""
      
      forecast = []
      for day_offset in range(int(days)):
          # Predict field for each day
          # Based on known lunar/tithi cycles
          
          forecast.append({
              'date': tomorrow + day_offset,
              'zones': predicted_zones,
              'best_work': zone_name,
              'best_rest': zone_name,
          })
      
      return jsonify(forecast)

Users could see: "SW is hot Mon-Wed, but NE peaks Thu-Fri"

═════════════════════════════════════════════════════════════════════════════════
