# Sales Detail (salesdet.frx)

| Source file | Type | Path |
|---|---|---|
| `salesdet.frx` | Report | `reports/salesdet.fr2` |

**Purpose:** Prints daily sales figures grouped by month, with a total and average per month and a grand total, from the `SALES DETAIL` view.

**Used by:**
- The report picker [[../04-forms/reports.md]] (`frmreports`, from the File menu's "Print Reports ..."), row `SALESDET` / "Sales Detail" of type `REPO` in `data/repolist.dbf`.

**Related docs:** [[../03-data-model/README.md]] (`SALES DETAIL` view and its unit-price note), [[salessum.md]] (the summary version), [[topcust.md]], [[../04-forms/reports.md]], [[README.md]].

## DataEnvironment

| Cursor | Alias | Source | Database | Filter |
|---|---|---|---|---|
| `Cursor1` | `sales_detail` | `sales detail` | `..\data\tastrade.dbc` |  |

## Bands & content

The wordmark labels are present but this is the only report without the logo bitmap and without Page / Date fields.

### Page Header (1.44 in)

| Kind | Top, left (in) | Size w×h (in) | Content | Format | Font | Options |
|---|---|---|---|---|---|---|
| label | 0.42, 1.20 | 0.21×0.40 | "T" |  | Arial 24 bold, RGB(0,0,255) |  |
| label | 0.42, 2.81 | 0.21×0.40 | "T" |  | Arial 24 bold, RGB(0,0,255) |  |
| label | 0.47, 1.36 | 1.33×0.34 | "asmanian" |  | Arial 20 bold |  |
| label | 0.47, 2.98 | 0.88×0.34 | "raders\n" |  | Arial 20 bold |  |
| line | 0.98, 0.00 | 8.03×0.01 | line |  |  |  |
| label | 1.01, 1.25 | 2.24×0.21 | "Total Sales by Month - Detail" |  | Arial 12 bold |  |

### Group Header 1 (0.24 in)

Band flags: group on `exp_1`; new page for each group.

| Kind | Top, left (in) | Size w×h (in) | Content | Format | Font | Options |
|---|---|---|---|---|---|---|
| rectangle | 0.00, 0.47 | 4.12×0.22 | grey fill |  |  |  |
| label | 0.00, 0.52 | 0.90×0.21 | "Month/Year\n" |  | Arial 12 bold |  |
| label | 0.00, 1.84 | 0.36×0.21 | "Date\n" |  | Arial 12 bold |  |
| label | 0.00, 4.06 | 0.44×0.21 | "Sales" |  | Arial 12 bold |  |

### Detail (0.28 in)

| Kind | Top, left (in) | Size w×h (in) | Content | Format | Font | Options |
|---|---|---|---|---|---|---|
| field | 0.04, 0.47 | 0.82×0.21 | `RIGHT(exp_1, 2) + "/" + LEFT(exp_1, 4)` |  | Arial 12 | print-when flags changed (`supvalchng`) |
| field | 0.04, 1.82 | 0.93×0.21 | `order_date` |  | Arial 12 |  |
| field | 0.04, 3.14 | 1.41×0.21 | `sum_unit_price` | `999999999.99` | Arial 12 | right-aligned |

### Group Footer 1 (0.75 in)

Band flags: new page for each group.

| Kind | Top, left (in) | Size w×h (in) | Content | Format | Font | Options |
|---|---|---|---|---|---|---|
| line | 0.05, 0.00 | 8.03×0.01 | line |  |  |  |
| rectangle | 0.16, 2.45 | 2.18×0.52 | grey fill |  |  |  |
| field | 0.20, 3.25 | 1.29×0.22 | `MTON(sum_unit_price)` | `999999999.99` | Arial 12 bold | right-aligned; calculate sum, reset group 1 |
| label | 0.21, 2.50 | 0.40×0.21 | "Total" |  | Arial 12 bold |  |
| field | 0.42, 3.25 | 1.29×0.22 | `MTON(sum_unit_price)` | `999999999.99` | Arial 12 bold | right-aligned; calculate average, reset group 1 |
| label | 0.43, 2.50 | 0.66×0.21 | "Average" |  | Arial 12 bold |  |

### Page Footer (0.00 in)

Empty.

### Summary (0.71 in)

| Kind | Top, left (in) | Size w×h (in) | Content | Format | Font | Options |
|---|---|---|---|---|---|---|
| rectangle | 0.26, 1.97 | 2.66×0.27 | grey fill |  |  |  |
| label | 0.27, 2.03 | 1.15×0.24 | "Grand Total\n" |  | Arial 14 bold |  |
| field | 0.27, 3.45 | 1.09×0.25 | `MTON(sum_unit_price)` | `999999999.99` | Arial 14 bold, RGB(128,0,128) | right-aligned; calculate sum, reset end of report |

## Report variables

None.

## Page setup

- Orientation: not stored (`ORIENTATION=0`, printer default)
- Paper size: 1 (Letter); copies: 1; duplex 1
- Saved printer environment: driver `winspool`, device `\\MSPRINT32\2/1MC PRIVJ 157.56.32.242`, output `Ne02:`

**NOTE:** the saved environment names `\\MSPRINT32`, a Microsoft print server from the 1990s, with an IP address in the 157.56 range. VFP tries the saved printer first when the report runs.

## Triggered from

- `forms/reports.sc2` `cmdRun.Click`: `REPORT FORM (lcSeleRepo) PREVIEW`, or `TO PRINTER NOCONSOLE` after `PRINTSTATUS()`, or `TO FILE <stem>.TXT ASCII`, where `lcSeleRepo` is `REPORTS\SALESDET.FRX`.
- The ASCII output drops lines, boxes, and pictures.

## Notes

- **NOTE:** `sum_unit_price` is the view's `SUM(unit_price)`: unit price summed without quantity, discount, or freight (see the view note in [[../03-data-model/README.md]]). The figures this report labels "Sales" are not order totals; [[topcust.md]] uses the full formula, so the two disagree.
- **One month per page**: the group on `exp_1` has `pagebreak` set on both header and footer.
- **Column names are VFP's automatic ones.** `exp_1` is the unnamed first column `STR(YEAR(...),4)+STR(MONTH(...),2)` and `sum_unit_price` the unnamed `SUM(...)`; a rebuilt view must keep them.
- **Month/Year prints as `RIGHT(exp_1, 2) + "/" + LEFT(exp_1, 4)`**, so single-digit months come out space-padded (" 7/1996"). That detail field has its print-when flags changed (`supvalchng`), which in the designer corresponds to printing only when the value changes; not run here.
- **Average is the average of daily sums** within the month (calculate Average, reset Group 1), not of orders.
- **Fifteen empty records** (objtype 0) sit between the layout objects and the data environment record; they are not deleted rows, and VFP ignores them.
