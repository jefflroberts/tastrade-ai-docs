# Category Listing (listcat.frx)

| Source file | Type | Path |
|---|---|---|
| `listcat.frx` | Report | `reports/listcat.fr2` |

**Purpose:** Prints every product category with its description and picture, from the `CATEGORY LISTING` view.

**Used by:**
- The report picker [[../04-forms/reports.md]] (`frmreports`, from the File menu's "Print Reports ..."), row `LISTCAT` / "Category Listing" of type `LIST` in `data/repolist.dbf`.

**Related docs:** [[../03-data-model/README.md]] (`CATEGORY LISTING` view), [[../03-data-model/tables/category.md]], [[../04-forms/reports.md]], [[README.md]].

## DataEnvironment

| Cursor | Alias | Source | Database | Filter |
|---|---|---|---|---|
| `cursor1` | `category_listing` | `category listing` | `..\data\tastrade.dbc` |  |

## Bands & content

The page header carries the sample's wordmark (four labels: a blue 24-point "T" before "asmanian" and before "raders"), the logo bitmap `bitmaps/ttradesm.bmp` (present in the repo), and Page / Date fields.

### Page Header (2.19 in)

| Kind | Top, left (in) | Size w×h (in) | Content | Format | Font | Options |
|---|---|---|---|---|---|---|
| picture | 0.12, 0.36 | 0.86×0.92 | picture `..\bitmaps\ttradesm.bmp` |  |  | file; clip; comment "(c) Microsoft Corporation 1995" |
| label | 0.31, 6.79 | 0.41×0.21 | "Page" |  | Arial 12 bold |  |
| field | 0.31, 7.46 | 0.51×0.21 | `_PAGENO` |  | Arial 12 | right-aligned |
| label | 0.60, 6.79 | 0.36×0.21 | "Date" |  | Arial 12 bold |  |
| field | 0.60, 7.29 | 0.68×0.21 | `DATE()` |  | Arial 12 |  |
| label | 0.72, 1.55 | 0.21×0.40 | "T" |  | Arial 24 bold, RGB(0,0,255) |  |
| label | 0.72, 3.17 | 0.21×0.40 | "T" |  | Arial 24 bold, RGB(0,0,255) |  |
| label | 0.77, 1.72 | 1.33×0.34 | "asmanian" |  | Arial 20 bold |  |
| label | 0.77, 3.33 | 0.88×0.34 | "raders\n" |  | Arial 20 bold |  |
| line | 1.12, 0.00 | 8.03×0.01 | line |  |  |  |
| label | 1.22, 1.62 | 1.31×0.21 | "Category Listing" |  | Arial 12 bold |  |
| rectangle | 1.75, 0.00 | 8.03×0.39 | grey fill |  |  |  |
| label | 1.84, 0.05 | 1.23×0.21 | "Category Name" |  | Arial 12 bold | float |
| label | 1.84, 1.82 | 0.92×0.21 | "Description" |  | Arial 12 bold | float |

### Detail (1.94 in)

| Kind | Top, left (in) | Size w×h (in) | Content | Format | Font | Options |
|---|---|---|---|---|---|---|
| field | 0.00, 0.05 | 1.74×0.21 | `category_name` |  | Arial 12 | stretch; float |
| field | 0.00, 1.82 | 3.55×1.71 | `Description` |  | Arial 12 | float |
| picture | 0.00, 5.43 | 2.60×1.89 | picture from field `Picture` |  |  | float; General field; scale, keep shape |

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

- `forms/reports.sc2` `cmdRun.Click`: `REPORT FORM (lcSeleRepo) PREVIEW`, or `TO PRINTER NOCONSOLE` after `PRINTSTATUS()`, or `TO FILE <stem>.TXT ASCII`, where `lcSeleRepo` is `REPORTS\LISTCAT.FRX`.
- The ASCII output drops lines, boxes, and pictures.

## Notes

- **Only listing with a picture.** The detail band is 1.94 in tall to hold the picture object, whose source is the view's `picture` General field (`offset = 1`), scaled to keep its shape. The picker's "To File" ASCII option cannot print it.
- **`Description` does not stretch**: a 3.55 × 1.71 in box with `float` but no `stretch`, so a long memo is clipped. `category_name` does stretch.
- The view carries no `ORDER BY`, so categories print in table order.
