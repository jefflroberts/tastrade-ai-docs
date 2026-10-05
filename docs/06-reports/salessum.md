# Sales Summary (salessum.frx)

| Source file | Type | Path |
|---|---|---|
| `salessum.frx` | Report | `reports/salessum.fr2` |

**Purpose:** Prints one line per month with the month's sales figure and a grand total, from the `SALES SUMMARY` view.

**Used by:**
- The report picker [[../04-forms/reports.md]] (`frmreports`, from the File menu's "Print Reports ..."), row `SALESSUM` / "Sales Summary" of type `REPO` in `data/repolist.dbf`.

**Related docs:** [[../03-data-model/README.md]] (`SALES SUMMARY` view), [[salesdet.md]] (the detail version), [[topcust.md]], [[../04-forms/reports.md]], [[README.md]].

## DataEnvironment

| Cursor | Alias | Source | Database | Filter |
|---|---|---|---|---|
| `cursor1` | `sales_summary` | `sales summary` | `..\data\tastrade.dbc` |  |

## Bands & content

The page header carries the sample's wordmark (four labels: a blue 24-point "T" before "asmanian" and before "raders"), the logo bitmap `bitmaps/ttradesm.bmp` (present in the repo), and Page / Date fields.

### Page Header (1.84 in)

| Kind | Top, left (in) | Size w×h (in) | Content | Format | Font | Options |
|---|---|---|---|---|---|---|
| picture | 0.05, 0.30 | 0.86×0.92 | picture `..\bitmaps\ttradesm.bmp` |  |  | file; clip; comment "(c) Microsoft Corporation 1995" |
| label | 0.25, 6.83 | 0.41×0.21 | "Page" |  | Arial 12 bold |  |
| field | 0.25, 7.50 | 0.51×0.21 | `_PAGENO` |  | Arial 12 | right-aligned |
| label | 0.47, 1.30 | 0.21×0.40 | "T" |  | Arial 24 bold, RGB(0,0,255) |  |
| label | 0.47, 2.92 | 0.21×0.40 | "T" |  | Arial 24 bold, RGB(0,0,255) |  |
| label | 0.52, 1.47 | 1.33×0.34 | "asmanian" |  | Arial 20 bold |  |
| label | 0.52, 3.08 | 0.88×0.34 | "raders\n" |  | Arial 20 bold |  |
| label | 0.54, 6.83 | 0.36×0.21 | "Date" |  | Arial 12 bold |  |
| field | 0.54, 7.33 | 0.68×0.21 | `DATE()` |  | Arial 12 |  |
| line | 0.98, 0.00 | 8.03×0.01 | line |  |  |  |
| label | 1.01, 1.35 | 2.55×0.21 | "Total Sales by Month - Summary" |  | Arial 12 bold |  |
| rectangle | 1.61, 1.67 | 2.88×0.23 | grey fill |  |  |  |
| label | 1.64, 1.72 | 0.90×0.21 | "Month/Year\n" |  | Arial 12 bold |  |
| label | 1.64, 4.06 | 0.44×0.21 | "Sales" |  | Arial 12 bold |  |

### Detail (0.27 in)

| Kind | Top, left (in) | Size w×h (in) | Content | Format | Font | Options |
|---|---|---|---|---|---|---|
| field | 0.03, 1.60 | 0.82×0.21 | `RIGHT(exp_1, 2) + "/" + LEFT(exp_1, 4)` |  | Arial 12 |  |
| field | 0.03, 3.22 | 1.28×0.21 | `sum_unit_price` | `999999999.99` | Arial 12 | right-aligned |

### Page Footer (0.18 in)

Empty.

### Summary (0.50 in)

Band flags: `colbreak`; `norepeat`.

| Kind | Top, left (in) | Size w×h (in) | Content | Format | Font | Options |
|---|---|---|---|---|---|---|
| rectangle | 0.09, 1.94 | 2.60×0.27 | grey fill |  |  |  |
| label | 0.10, 2.08 | 1.15×0.24 | "Grand Total\n" |  | Arial 14 bold |  |
| field | 0.10, 3.39 | 1.09×0.25 | `MTON(sum_unit_price)` | `999999999.99` | Arial 14 bold, RGB(128,0,128) | right-aligned; calculate sum, reset end of report |

## Report variables

None.

## Page setup

- Orientation: not stored (`ORIENTATION=0`, printer default)
- Paper size: 1 (Letter); copies: 1
- Print quality: 300 dpi
- Saved printer environment: driver `winspool`, device `LaserNT`, output `Ne00:`

**NOTE:** the saved environment names `LaserNT`, a printer on the original author's machine; VFP tries it first when the report runs.

## Triggered from

- `forms/reports.sc2` `cmdRun.Click`: `REPORT FORM (lcSeleRepo) PREVIEW`, or `TO PRINTER NOCONSOLE` after `PRINTSTATUS()`, or `TO FILE <stem>.TXT ASCII`, where `lcSeleRepo` is `REPORTS\SALESSUM.FRX`.
- The ASCII output drops lines, boxes, and pictures.

## Notes

- **NOTE:** `sum_unit_price` is the view's `SUM(unit_price)`: unit price summed without quantity, discount, or freight (see the view note in [[../03-data-model/README.md]]). The figures this report labels "Sales" are not order totals; [[topcust.md]] uses the full formula, so the two disagree.
- **Depends on the automatic column name `exp_1`** for the month key; `sum_unit_price` is named in the view's SQL.
- **Grand total** is a Sum of `MTON(sum_unit_price)` reset at end of report, in a 0.50 in summary band whose record has `norepeat` and `colbreak` set.
