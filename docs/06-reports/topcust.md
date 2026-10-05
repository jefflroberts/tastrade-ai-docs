# Top 25 Customers (topcust.frx)

| Source file | Type | Path |
|---|---|---|
| `topcust.frx` | Report | `reports/topcust.fr2` |

**Purpose:** Prints the 25 customers with the highest order totals, ranked, with country and total, from the `TOP25CUST` view.

**Used by:**
- The report picker [[../04-forms/reports.md]] (`frmreports`, from the File menu's "Print Reports ..."), row `TOPCUST` / "Top 25 Customers" of type `REPO` in `data/repolist.dbf`.

**Related docs:** [[../03-data-model/README.md]] (`TOP25CUST` and `ORDERTOTAL` views), [[../03-data-model/tables/customer.md]], [[salessum.md]], [[../04-forms/reports.md]], [[README.md]].

## DataEnvironment

| Cursor | Alias | Source | Database | Filter |
|---|---|---|---|---|
| `Cursor2` | `customer` | `customer` | `..\data\tastrade.dbc` |  |
| `Cursor3` | `orders` | `orders` | `..\data\tastrade.dbc` |  |
| `Cursor4` | `order_line_items` | `order_line_items` | `..\data\tastrade.dbc` |  |
| `Cursor1` | `top25cust` | `top25cust` | `..\data\tastrade.dbc` |  |

Properties: `InitialSelectedAlias = "top25cust"`.

**NOTE:** four cursors, three of them dead. `customer`, `orders`, and `order_line_items` are opened by the data environment but no field expression, variable, or group refers to them; the `TOP25CUST` view already joins them through `ORDERTOTAL`. Probably left from a draft that queried the tables directly.

## Bands & content

The page header carries the sample's wordmark (four labels: a blue 24-point "T" before "asmanian" and before "raders"), the logo bitmap `bitmaps/ttradesm.bmp` (present in the repo), and Page / Date fields.

### Page Header (1.99 in)

| Kind | Top, left (in) | Size w×h (in) | Content | Format | Font | Options |
|---|---|---|---|---|---|---|
| picture | 0.12, 0.36 | 0.86×0.92 | picture `..\bitmaps\ttradesm.bmp` |  |  | file; clip; comment "(c) Microsoft Corporation 1995" |
| label | 0.26, 6.72 | 0.41×0.21 | "Page" |  | Arial 12 bold |  |
| field | 0.26, 7.39 | 0.51×0.21 | `_PAGENO` |  | Arial 12 | right-aligned |
| label | 0.55, 6.72 | 0.36×0.21 | "Date" |  | Arial 12 bold |  |
| field | 0.55, 7.22 | 0.68×0.21 | `DATE()` |  | Arial 12 |  |
| label | 0.59, 1.43 | 0.21×0.40 | "T" |  | Arial 24 bold, RGB(0,0,255) |  |
| label | 0.59, 3.04 | 0.21×0.40 | "T" |  | Arial 24 bold, RGB(0,0,255) |  |
| label | 0.65, 1.59 | 1.33×0.34 | "asmanian" |  | Arial 20 bold |  |
| label | 0.65, 3.21 | 0.88×0.34 | "raders\n" |  | Arial 20 bold |  |
| line | 1.12, 0.00 | 8.14×0.01 | line |  |  |  |
| label | 1.22, 1.45 | 1.46×0.21 | "Top 25 Customers" |  | Arial 12 bold |  |
| rectangle | 1.64, 0.00 | 7.93×0.35 | grey fill |  |  |  |
| label | 1.72, 0.23 | 0.42×0.21 | "Rank" |  | Arial 12 bold | float |
| label | 1.72, 0.85 | 1.27×0.21 | "Company Name" |  | Arial 12 bold | float |
| label | 1.72, 4.17 | 0.65×0.21 | "Country" |  | Arial 12 bold | float |
| label | 1.72, 7.28 | 0.44×0.21 | "Sales" |  | Arial 12 bold | float |

### Detail (0.29 in)

| Kind | Top, left (in) | Size w×h (in) | Content | Format | Font | Options |
|---|---|---|---|---|---|---|
| field | 0.00, 0.07 | 0.58×0.21 | `STR(RECNO(),2) + '.'` |  | Arial 12 | stretch; float; right-aligned |
| field | 0.00, 0.85 | 3.26×0.21 | `company_name` |  | Arial 12 | stretch; float |
| field | 0.00, 4.17 | 2.08×0.21 | `top25cust.country` |  | Arial 12 | stretch; float |
| field | 0.00, 6.31 | 1.55×0.21 | `top25cust.custtotal` | `$9,999,999.99` | Arial 12 | stretch; float; right-aligned |

### Page Footer (0.00 in)

Empty.

## Report variables

None.

## Page setup

- Orientation: not stored (`ORIENTATION=0`, printer default)
- Paper size: 1 (Letter); copies: 1
- Print quality: 300 dpi
- Saved printer environment: driver `winspool`, device `LaserNT`, output `Ne00:`

**NOTE:** the saved environment names `LaserNT`, a printer on the original author's machine; VFP tries it first when the report runs.

## Triggered from

- `forms/reports.sc2` `cmdRun.Click`: `REPORT FORM (lcSeleRepo) PREVIEW`, or `TO PRINTER NOCONSOLE` after `PRINTSTATUS()`, or `TO FILE <stem>.TXT ASCII`, where `lcSeleRepo` is `REPORTS\TOPCUST.FRX`.
- The ASCII output drops lines, boxes, and pictures.

## Notes

- **Rank is `STR(RECNO(),2) + '.'`**, the record number in the view cursor, which is ordered `custtotal DESC` by the view's SQL.
- **`company_name` is unqualified** while `customer` is also open with a `company_name` column; it resolves through `InitialSelectedAlias = "top25cust"`. The other two columns are qualified `top25cust.`.
- **Uses the real order total.** `ORDERTOTAL` applies quantity, discount, and freight, so this report's figures are order totals; [[salessum.md]] and [[salesdet.md]] sum unit prices. The three sales reports do not reconcile.
- One of two reports (with `behindsc.frx`) that have no description entry in `tastrade.pj2`; the same two are the only ones with a code page recorded (`Cpid="1252"`), so both were probably added or re-saved later than the rest.
- Money mask `$9,999,999.99`.
