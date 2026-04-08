# Shakti Pitha Geographic Body Map

## Objective
Map the 51 Shakti Pithas to anatomical body regions, creating a geographic-somatic correspondence layer for Atlas S4/S5 integration.

## Research Questions
1. What are the canonical 51 Shakti Pithas and their associated body parts (from Devi Bhagavata / Kalika Purana)?
2. How do the geographic coordinates of each pitha correlate with the body-part mapping?
3. Can we derive a spatial projection that maps the Indian subcontinent onto a human figure (as in the Purusha Sukta cosmography)?
4. Which pithas correspond to existing marma points in our marma dataset?

## Sources to Consult
- Devi Bhagavata Purana, Skandha 7
- Kalika Purana (body part assignments)
- D.C. Sircar, "The Sakta Pithas" (1948, revised 1973)
- Existing: `datasets/marma/body_region_marma.csv`
- Existing: `datasets/tantra/` (check for pitha references)

## Output Format
CSV: `pitha_name, body_part, latitude, longitude, marma_id (if mapped), element, devi_form`
Plus a narrative summary linking the geographic body to the Atlas torus topology.

## Atlas Integration
- S4 (Geometry): torus projection of geographic coordinates
- S5 (Nature): marma/body correspondences
- S1 (Archetype): Devi forms at each pitha

## Priority
High — foundational for body-cosmology layer

## Field Optimal
Guruvara (Thursday) + Pushya nakshatra — Jupiter-ruled, auspicious for sacred geography
