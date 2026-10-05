# Tastrade documentation

Reverse-engineering docs for the Tastrade sample, generated with the
`document-vfp-artifact` skill from the FoxBin2PRG text twins in this repo.
Start with [`PROJECT.md`](PROJECT.md), which the skill reads first and which
records everything app-specific.

| Folder | Contents |
|---|---|
| `00-inventory/` | Generated census of artifacts and tables (not hand-edited) |
| `01-architecture/` | Project manifest, startup sequence, framework overview |
| `02-domain/` | What the business does, in plain language |
| `03-data-model/` | The DBC: `README.md` for the container, `tables/` one file per table |
| `04-forms/` | One file per form |
| `05-classes/` | One file per class library |
| `06-reports/` | One file per report |
| `07-menus/` | One file per menu |
| `08-programs/` | One file per `.prg` and per include file (`.h`) |
| `09-business-logic/` | Rules and formulas recovered from stored procedures and code |
| `10-baseline/` | Index of the screenshot baseline in `baseline/` (forms, main window, report pages, message boxes), captured from the running EXE |

Conventions come from the toolkit's `methodology/conventions.md`; the skill in
`.claude/skills/document-vfp-artifact/` applies them.
