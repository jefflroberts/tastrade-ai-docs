# Supplier Listing (listsupp.frx)

| Source file | Type | Path |
|---|---|---|
| `listsupp.frx` | Report | `reports/listsupp.fr2` |

**Purpose:** Prints company name, contact name, and phone for every supplier, from the `SUPPLIER LISTING` view (ordered by company then contact).

**Used by:**
- The report picker [[../04-forms/reports.md]] (`frmreports`, from the File menu's "Print Reports ..."), row `LISTSUPP` / "Supplier Listing" of type `LIST` in `data/repolist.dbf`.

**Related docs:** [[../03-data-model/README.md]] (`SUPPLIER LISTING` view), [[../03-data-model/tables/supplier.md]], [[../04-forms/reports.md]], [[README.md]].

## DataEnvironment

| Cursor | Alias | Source | Database | Filter |
|---|---|---|---|---|
| `cursor1` | `supplier_listing` | `supplier listing` | `..\data\tastrade.dbc` |  |

## Bands & content

The page header carries the sample's wordmark (four labels: a blue 24-point "T" before "asmanian" and before "raders"), the logo bitmap `bitmaps/ttradesm.bmp` (present in the repo), and Page / Date fields.

### Page Header (1.99 in)

| Kind | Top, left (in) | Size w×h (in) | Content | Format | Font | Options |
|---|---|---|---|---|---|---|
| picture | 0.12, 0.49 | 0.86×0.92 | picture `..\bitmaps\ttradesm.bmp` |  |  | file; clip; comment "(c) Microsoft Corporation 1995" |
| label | 0.27, 6.84 | 0.41×0.21 | "Page" |  | Arial 12 bold |  |
| field | 0.27, 7.51 | 0.51×0.21 | `_PAGENO` |  | Arial 12 | right-aligned |
| label | 0.56, 6.84 | 0.36×0.21 | "Date" |  | Arial 12 bold |  |
| field | 0.56, 7.34 | 0.68×0.21 | `DATE()` |  | Arial 12 |  |
| label | 0.59, 1.43 | 0.21×0.40 | "T" |  | Arial 24 bold, RGB(0,0,255) |  |
| label | 0.59, 3.04 | 0.21×0.40 | "T" |  | Arial 24 bold, RGB(0,0,255) |  |
| label | 0.65, 1.59 | 1.33×0.34 | "asmanian" |  | Arial 20 bold |  |
| label | 0.65, 3.21 | 0.88×0.34 | "raders\n" |  | Arial 20 bold |  |
| line | 1.07, 0.00 | 8.03×0.01 | line |  |  |  |
| label | 1.09, 1.50 | 1.25×0.21 | "Supplier Listing" |  | Arial 12 bold |  |
| rectangle | 1.64, 0.00 | 8.03×0.35 | grey fill |  |  |  |
| label | 1.72, 0.10 | 1.27×0.21 | "Company Name" |  | Arial 12 bold | float |
| label | 1.72, 3.65 | 1.12×0.21 | "Contact Name" |  | Arial 12 bold | float |
| label | 1.72, 6.36 | 0.52×0.21 | "Phone" |  | Arial 12 bold | float |

### Detail (0.29 in)

| Kind | Top, left (in) | Size w×h (in) | Content | Format | Font | Options |
|---|---|---|---|---|---|---|
| field | 0.00, 0.10 | 3.45×0.21 | `company_name` |  | Arial 12 | stretch; float |
| field | 0.00, 3.65 | 2.61×0.21 | `contact_name` |  | Arial 12 | stretch; float |
| field | 0.00, 6.39 | 1.75×0.21 | `phone` |  | Arial 12 | stretch; float |

### Page Footer (0.18 in)

Empty.

## Report variables

None.

## Page setup

- Orientation: not stored (`ORIENTATION=0`, printer default)
- Paper size: 1 (Letter); copies: 1; duplex 1
- Saved printer environment: driver `winspool`, device `\\MSPRINT32\2/1MC PRIVJ 157.56.32.242`, output `Ne02:`

**NOTE:** the saved environment names `\\MSPRINT32`, a Microsoft print server from the 1990s, with an IP address in the 157.56 range. VFP tries the saved printer first when the report runs.

## Triggered from

- `forms/reports.sc2` `cmdRun.Click`: `REPORT FORM (lcSeleRepo) PREVIEW`, or `TO PRINTER NOCONSOLE` after `PRINTSTATUS()`, or `TO FILE <stem>.TXT ASCII`, where `lcSeleRepo` is `REPORTS\LISTSUPP.FRX`.
- The ASCII output drops lines, boxes, and pictures.

## Notes

- **Twin of [[listcust.md]]**, see the note there.
