# ttrade

| Source file | Type | Path |
|---|---|---|
| `ttrade.dbf` | Free table (outside `tastrade.dbc`) | `help/ttrade.db2` |

**Purpose:** A help file in Visual FoxPro's own DBF help format (`contextid`, `topic`, `details`): sixteen topics introducing the application, its login and order entry, and each menu.

**Used by:**
- **Nothing at run time.** `environment.Set` does `SET HELP TO HELP\TASTRADE.CHM` ([[../../05-classes/tsgen.md]]), the HTML Help file, and no twin or program names `ttrade.dbf`. The two `HelpContextID` values in the source (10 on login.vc2; 11 on ordentry.sc2) match rows here and, presumably, the CHM's map.
- The project does not include it or the CHM ([[../../01-architecture/projects.md]]).

**Related docs:** [[../README.md]], [[behindsc.md]], [[repolist.md]], [[../../07-menus/README.md]] (the menus the topics describe).

Row count in the sample data: 16. No database container, so no long field names, comments, defaults, rules, or triggers; what follows is all there is.

## Schema

| # | Field | Type | Width | Dec | Null |
|---|---|---|---|---|---|
| 1 | `contextid` | Numeric (N) | 10 | 0 | no |
| 2 | `topic` | Character (C) | 70 | 0 | no |
| 3 | `details` | Memo (M) | 4 | 0 | no |

## Triggers (from table header)

- None: no insert, update, or delete trigger, no table rule. Free tables cannot carry them.

## Indexes (.cdx tags)

None. The table has no `.cdx`; the help engine reads it by `contextid` sequentially.

## Stored procedure references

- None.

## Relations

- None. Free tables take part in no persistent relation.

## Used by

See the header: not read by the application. The columns and widths (`contextid N(10)`, `topic C(70)`, `details M`) are exactly the structure VFP's `SET HELP TO <table>` expects, so it is the pre-HTML-Help help file, kept beside the CHM.

## Sample / notable rows

All 16 rows, in table order; `details` lengths in characters.

| # | contextid | topic | details |
|---|---|---|---|
| 1 | 0 | ***** Before You Begin ***** | 28 chars |
| 2 | 12 | Overview | **empty** |
| 3 | 0 | Introducing Tasmanian Traders | 1029 chars |
| 4 | 0 | ***** Using Tasmanian Traders ***** | 35 chars |
| 5 | 10 | Login Dialog Box | 689 chars |
| 6 | 11 | Order Entry Form | 1553 chars |
| 7 | 0 | ***** Menu Commands ***** | 25 chars |
| 8 | 0 | File Menu | 813 chars |
| 9 | 0 | Edit Menu | 325 chars |
| 10 | 0 | Orders Menu | 247 chars |
| 11 | 0 | Administration Menu | 851 chars |
| 12 | 0 | Navigation Menu | 317 chars |
| 13 | 0 | Utilities Menu | 532 chars |
| 14 | 0 | Items Menu | 392 chars |
| 15 | 0 | Window Menu | 245 chars |
| 16 | 0 | Help Menu | 335 chars |

## Notes

- **1 of 16 topics has no text**: "Overview". The `***** ... *****` rows are section headings with a line of text each; "Overview", which has context ID 12, is simply empty.
- **The introduction promises more than the code does**: "Depending on your user level, you have access to different tables" describes menu gating that the shipped build turns off ([[../../02-domain/README.md]]).
- **The Login topic says the password is shown in the Hint box** "in this sample application", so the authors knew.
- **No index**, no `.fpt` in the project; the text lives in `ttrade.fpt` beside the table.
