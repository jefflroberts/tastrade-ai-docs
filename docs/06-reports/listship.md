# Shipper Listing (listship.frx)

| Source file | Type | Path |
|---|---|---|
| `listship.frx` | Report | `reports/listship.fr2` |

**Purpose:** Prints the company name of every shipper, from the `SHIPPER LISTING` view (ordered by name).

**Used by:**
- The report picker [[../04-forms/reports.md]] (`frmreports`, from the File menu's "Print Reports ..."), row `LISTSHIP` / "Shipper Listing" of type `LIST` in `data/repolist.dbf`.

**Related docs:** [[../03-data-model/README.md]] (`SHIPPER LISTING` view), [[../03-data-model/tables/shippers.md]], [[../04-forms/reports.md]], [[README.md]].

## DataEnvironment

| Cursor | Alias | Source | Database | Filter |
|---|---|---|---|---|
| `cursor1` | `shipper_listing` | `shipper listing` | `..\data\tastrade.dbc` |  |

## Bands & content

The page header carries the sample's wordmark (four labels: a blue 24-point "T" before "asmanian" and before "raders"), the logo bitmap `bitmaps/ttradesm.bmp` (present in the repo), and Page / Date fields.

### Page Header (2.26 in)

| Kind | Top, left (in) | Size w×h (in) | Content | Format | Font | Options |
|---|---|---|---|---|---|---|
| picture | 0.25, 0.49 | 0.86×0.92 | picture `..\bitmaps\ttradesm.bmp` |  |  | file; clip; comment "(c) Microsoft Corporation 1995" |
| label | 0.30, 6.83 | 0.41×0.21 | "Page" |  | Arial 12 bold |  |
| field | 0.30, 7.50 | 0.51×0.21 | `_PAGENO` |  | Arial 12 | right-aligned |
| label | 0.59, 6.83 | 0.36×0.21 | "Date" |  | Arial 12 bold |  |
| field | 0.59, 7.33 | 0.68×0.21 | `DATE()` |  | Arial 12 |  |
| label | 0.84, 1.68 | 0.21×0.40 | "T" |  | Arial 24 bold, RGB(0,0,255) |  |
| label | 0.84, 3.29 | 0.21×0.40 | "T" |  | Arial 24 bold, RGB(0,0,255) |  |
| label | 0.90, 1.84 | 1.33×0.34 | "asmanian" |  | Arial 20 bold |  |
| label | 0.90, 3.46 | 0.88×0.34 | "raders\n" |  | Arial 20 bold |  |
| line | 1.25, 0.00 | 7.98×0.01 | line |  |  |  |
| label | 1.34, 1.75 | 1.21×0.21 | "Shipper Listing" |  | Arial 12 bold |  |
| rectangle | 1.88, 0.00 | 4.76×0.39 | grey fill |  |  |  |
| label | 1.97, 0.12 | 1.27×0.21 | "Company Name" |  | Arial 12 bold | float |

### Detail (0.22 in)

| Kind | Top, left (in) | Size w×h (in) | Content | Format | Font | Options |
|---|---|---|---|---|---|---|
| field | 0.00, 0.11 | 4.67×0.21 | `company_name` |  | Arial 12 |  |

### Page Footer (0.50 in)

Empty.

## Report variables

None.

## Page setup

- Orientation: not stored (`ORIENTATION=0`, printer default)
- Paper size: 1 (Letter); copies: 1; duplex 1
- Saved printer environment: driver `winspool`, device `\\MSPRINT32\2/1MC PRIVJ 157.56.32.242`, output `Ne02:`

**NOTE:** the saved environment names `\\MSPRINT32`, a Microsoft print server from the 1990s, with an IP address in the 157.56 range. VFP tries the saved printer first when the report runs.

## Triggered from

- `forms/reports.sc2` `cmdRun.Click`: `REPORT FORM (lcSeleRepo) PREVIEW`, or `TO PRINTER NOCONSOLE` after `PRINTSTATUS()`, or `TO FILE <stem>.TXT ASCII`, where `lcSeleRepo` is `REPORTS\LISTSHIP.FRX`.
- The ASCII output drops lines, boxes, and pictures.

## Notes

- **One column.** The smallest report in the sample: a page header, a single 4.67 in field, and an empty 0.50 in page footer.
- The detail field neither floats nor stretches; every other listing's columns at least `float`.
