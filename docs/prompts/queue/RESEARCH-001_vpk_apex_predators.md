RESEARCH-001: Extract 14 Missing Apex Predators VPK data

# Note: /mnt/skills not accessible — proceed with task directly

Source: ~/Downloads/Extending a Vedic Cosmological Knowledge Graph With VPK Inferences for Sixty Animals.docx

Extract VPK data for these 14 animals that were cut off in the original COR-012 run:
wolverine, jaguar, snow_leopard, orca, harpy_eagle,
saltwater_crocodile, cassowary, komodo_dragon, african_wild_dog,
mantis_shrimp, peregrine_falcon, tasmanian_devil,
african_savanna_elephant, galapagos_giant_tortoise

Steps:
1. Convert docx: pandoc "$SOURCE" -t plain 2>/dev/null
2. Find the CSV-Ready Rows section
3. Extract just these 14 rows
4. If not found in parsed text, create rows from the prose descriptions
   in the document using the same schema as datasets/species/vpk_global_inference.csv
5. Write to: datasets/species/vpk_apex_predators.csv

Schema: match existing vpk_global_inference.csv columns
Log completion to docs/ATLAS_CYCLE_LOG.md
