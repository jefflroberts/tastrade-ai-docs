# Inventory (generated)

Produced by the toolkit tools on 2026-09-08 against the twins from the VFP 9
rebuild. Regenerate rather than edit.

| File | Command | What it shows |
|---|---|---|
| `artifact-census.txt` | `python <toolkit>\tools\foxparse.py --summary forms libs reports menus data help tastrade.pj2` | One line per twin: controls, methods, cursors, tables, report bands and cursors, menu pads and bars, classes, free-table fields and tags, project members. 46 lines; regenerated 2026-09-09 after the parser gained menu, report, project, and free-table fields |
| `table-census.txt` / `.json` | `python <toolkit>\tools\dbf_header.py data --json ...` | Header-only census of the 12 tables in `data/`: rows, size, field count |
