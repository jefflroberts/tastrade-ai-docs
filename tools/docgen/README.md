# Doc generators

The scripts that produced `docs/03-data-model/`, `docs/05-classes/`,
`docs/04-forms/`, `docs/06-reports/`, `docs/07-menus/`, `docs/08-programs/`,
`docs/01-architecture/`, `docs/02-domain/`, and `docs/09-business-logic/`. Each merges structure read from the FoxBin2PRG twins through
`foxparse.py` (control trees, cursors, method bodies quoted verbatim) with
hand-written purpose, explanations, and notes held as strings inside the script.
To correct a doc, edit the script and rerun it; do not hand-edit the generated
markdown, or the next run overwrites the change.

Each script finds the toolkit's `tools/` folder through the `VFP_TOOLKIT_TOOLS`
environment variable, defaulting to a `vfp-documentation-toolkit` clone next to
this repo, and the Tastrade source through `TASTRADE_ROOT`, defaulting to this
repo's root. The source is not in this repo; see the top-level README.
Rerunning a script rewrites its docs with the full method bodies from your copy
of the source, where the published docs carry short excerpts.

| Script | Produces | Input |
|---|---|---|
| `dbcdump.prg` | `dbcdump.txt` | Run through the VFP 9 COM server against `data\tastrade.dbc`; dumps `AFIELDS()`, tags, views, relations, and the three free tables. Has an `ON ERROR` handler that writes the error and cancels, because a runtime error in a hidden COM instance otherwise hangs on a modal dialog |
| `gen_dbc_docs.py` | `docs/03-data-model/README.md` and `tables/*.md` | `dbcdump.txt` and `data/tastrade.dc2` |
| `gen_class_docs.py` | `docs/05-classes/tsbase.md`, `tsgen.md`, `README.md` | `libs/tsbase.vc2`, `libs/tsgen.vc2` |
| `gen_class_docs2.py` | `docs/05-classes/main.md`, `login.md`, `about.md`, `orders.md`; updates the index | `libs/*.vc2` |
| `gen_form_docs.py` | `docs/04-forms/ordentry.md`, `ordhist.md`, `README.md` | `forms/*.sc2` |
| `gen_maint_docs.py` | the six `tsmaintform` form docs; updates the index | `forms/*.sc2` |
| `gen_rest_docs.py` | the remaining nine form docs; updates the index | `forms/*.sc2` |
| `gen_report_docs.py` | all thirteen `docs/06-reports/*.md` and the index | `reports/*.fr2` through `foxparse.parse_fr2` (bands, objects with band-relative coordinates, cursors, DE code, variables, printer environment) |
| `gen_menu_docs.py` | all five `docs/07-menus/*.md` and the index | `menus/*.mn2` through `foxparse.parse_mn2` (pads, bars, keys, `SKIP FOR`, actions, procedures, setup and cleanup code) |
| `gen_program_docs.py` | `docs/08-programs/main.md`, `utility.md`, `tastrade.h.md`, `strings.h.md`, and the index | `progs/*.prg` and `include/*.h` read directly (no twin); parses routines, `DECLARE`s, and `#DEFINE`s itself and greps every twin for each constant's users |
| `gen_project_docs.py` | `docs/01-architecture/projects.md`, `startup.md`, `framework.md`, and the index | `tastrade.pj2` through `foxparse.parse_pj2`, plus a census of the working tree against the project (bitmaps by referrer, files outside the project); the two overview pages are synthesis prose with computed counts |
| `gen_synthesis_docs.py` | `docs/02-domain/README.md` and `docs/09-business-logic/README.md` | stored procedures, field rules, and view SQL from `data/tastrade.dc2`; method bodies from `libs/orders.vc2`, `libs/login.vc2`, `forms/ordentry.sc2`, `forms/ordhist.sc2`; invoice variables from `reports/orders.fr2`; menu cleanup from `menus/main.mn2`; data profile from the DBFs |
| `gen_free_table_docs.py` | `docs/03-data-model/tables/behindsc.md`, `repolist.md`, `ttrade.md` | the `.db2` twins through `foxparse.parse_db2`, asserted equal to the live dump in `dbcdump.txt`; rows from the DBFs; every `code_to_sh` instruction in `behindsc.dbf` resolved against the twins |
| `gen_baseline_docs.py` | `docs/10-baseline/README.md` | `baseline/CAPTURE-LOG.csv`, `baseline/dialogs.csv`, `baseline/capture.log`, and the PNG headers, all written by `tools/baseline/run_capture.ps1`; the findings paragraphs are hand-written strings in the script |

Run order matters only for the forms index: `gen_form_docs.py` creates it,
the other two update rows in it.

Invoking the DBC dump from PowerShell:

```powershell
$vfp = New-Object -ComObject 'VisualFoxPro.Application.9'; $vfp.Visible = $false
$vfp.DoCmd('SET DEFAULT TO C:\fox\tastrade\data')
$vfp.DoCmd("DO ('C:\fox\tastrade\tools\docgen\dbcdump.prg') WITH 'C:\fox\tastrade\data\tastrade.dbc','C:\fox\tastrade\tools\docgen\dbcdump.txt','C:\fox\tastrade\data\behindsc.dbf,C:\fox\tastrade\data\repolist.dbf,C:\fox\tastrade\help\ttrade.dbf'")
$vfp.Quit()
```
