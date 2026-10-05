# Product Listing (listprod.frx)

| Source file | Type | Path |
|---|---|---|
| `listprod.frx` | Report | `reports/listprod.fr2` |

**Purpose:** Prints product name, quantity per unit, unit price, and unit cost for every product, from the `PRODUCT LISTING` view (ordered by name then quantity).

**Used by:**
- The report picker [[../04-forms/reports.md]] (`frmreports`, from the File menu's "Print Reports ..."), row `LISTPROD` / "Product Listing" of type `LIST` in `data/repolist.dbf`.

**Related docs:** [[../03-data-model/README.md]] (`PRODUCT LISTING` view), [[../03-data-model/tables/products.md]], [[../04-forms/reports.md]], [[README.md]].

## DataEnvironment

| Cursor | Alias | Source | Database | Filter |
|---|---|---|---|---|
| `cursor1` | `product_listing` | `product listing` | `..\data\tastrade.dbc` |  |

## Bands & content

The page header carries the sample's wordmark (four labels: a blue 24-point "T" before "asmanian" and before "raders"), the logo bitmap `bitmaps/ttradesm.bmp` (present in the repo), and Page / Date fields.

### Page Header (2.22 in)

| Kind | Top, left (in) | Size w×h (in) | Content | Format | Font | Options |
|---|---|---|---|---|---|---|
| label | 0.32, 6.84 | 0.41×0.21 | "Page" |  | Arial 12 bold |  |
| field | 0.32, 7.51 | 0.51×0.21 | `_PAGENO` |  | Arial 12 | right-aligned |
| picture | 0.38, 0.74 | 0.86×0.92 | picture `..\bitmaps\ttradesm.bmp` |  |  | file; clip; comment "(c) Microsoft Corporation 1995" |
| label | 0.61, 6.84 | 0.36×0.21 | "Date" |  | Arial 12 bold |  |
| field | 0.61, 7.34 | 0.68×0.21 | `DATE()` |  | Arial 12 |  |
| label | 0.97, 1.80 | 0.21×0.40 | "T" |  | Arial 24 bold, RGB(0,0,255) |  |
| label | 0.97, 3.42 | 0.21×0.40 | "T" |  | Arial 24 bold, RGB(0,0,255) |  |
| label | 1.02, 1.97 | 1.33×0.34 | "asmanian" |  | Arial 20 bold |  |
| label | 1.02, 3.58 | 0.88×0.34 | "raders\n" |  | Arial 20 bold |  |
| line | 1.38, 0.00 | 7.98×0.01 | line |  |  |  |
| label | 1.47, 1.88 | 1.22×0.21 | "Product Listing" |  | Arial 12 bold |  |
| rectangle | 1.83, 0.00 | 8.03×0.39 | grey fill |  |  |  |
| label | 1.94, 0.10 | 1.14×0.21 | "Product Name" |  | Arial 12 bold | float |
| label | 1.94, 3.42 | 1.22×0.21 | "Quantity In Unit" |  | Arial 12 bold | float |
| label | 1.94, 5.92 | 0.77×0.21 | "Unit Price" |  | Arial 12 bold | float |
| label | 1.94, 7.04 | 0.74×0.21 | "Unit Cost" |  | Arial 12 bold | float |

### Detail (0.27 in)

| Kind | Top, left (in) | Size w×h (in) | Content | Format | Font | Options |
|---|---|---|---|---|---|---|
| field | 0.00, 0.10 | 3.24×0.21 | `product_name` |  | Arial 12 | stretch; float |
| field | 0.00, 3.41 | 2.36×0.21 | `quantity_in_unit` |  | Arial 12 | stretch; float |
| field | 0.00, 5.91 | 0.96×0.21 | `unit_price` | `99999.99` | Arial 12 | float |
| field | 0.00, 7.03 | 0.96×0.21 | `unit_cost` | `99999.99` | Arial 12 | float |

### Page Footer (0.16 in)

Empty.

## Report variables

None.

## Page setup

- Orientation: not stored (`ORIENTATION=0`, printer default)
- Paper size: 1 (Letter); copies: 1; duplex 1
- Saved printer environment: driver `winspool`, device `\\MSPRINT32\2/1MC PRIVJ 157.56.32.242`, output `Ne02:`

**NOTE:** the saved environment names `\\MSPRINT32`, a Microsoft print server from the 1990s, with an IP address in the 157.56 range. VFP tries the saved printer first when the report runs.

## Triggered from

- `forms/reports.sc2` `cmdRun.Click`: `REPORT FORM (lcSeleRepo) PREVIEW`, or `TO PRINTER NOCONSOLE` after `PRINTSTATUS()`, or `TO FILE <stem>.TXT ASCII`, where `lcSeleRepo` is `REPORTS\LISTPROD.FRX`.
- The ASCII output drops lines, boxes, and pictures.

## Notes

- **Prints cost next to price.** `unit_cost` is on the same listing as `unit_price`; there is no user-level check on the picker, so anyone who can print can see margins.
- **Currency masks `99999.99`** on both money columns, so values of 100,000 or more cannot display in full.
