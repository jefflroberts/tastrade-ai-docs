# Code Report (viewcode.frx)

| Source file | Type | Path |
|---|---|---|
| `viewcode.frx` | Report | `reports/viewcode.fr2` |

**Purpose:** Prints the method code the Behind the Scenes form extracted, from the `viewcode` cursor the form creates.

**Used by:**
- [[../04-forms/viewcode.md]] `cmdPrint.Click`: `REPORT FORM viewcode TO PRINTER NOCONSOLE`, after a Yes/No confirmation.

**Related docs:** [[../04-forms/viewcode.md]], [[../04-forms/behindsc.md]] (creates the cursor), [[README.md]].

## DataEnvironment

No cursors.

The only report with no cursor at all. `frmbehindsc.showcode` runs `CREATE CURSOR viewcode (code M)`, fills it, and opens the viewer form in the same data session; the report's single field reads `viewcode.code` from that cursor.

## Bands & content

The page header carries the sample's wordmark (four labels: a blue 24-point "T" before "asmanian" and before "raders"), the logo bitmap `bitmaps/ttradesm.bmp` (present in the repo), and Page / Date fields.

### Page Header (1.41 in)

| Kind | Top, left (in) | Size w×h (in) | Content | Format | Font | Options |
|---|---|---|---|---|---|---|
| picture | 0.03, 0.61 | 0.86×0.92 | picture `..\bitmaps\ttradesm.bmp` |  |  | file; clip; comment "(c) Microsoft Corporation 1995" |
| label | 0.21, 6.83 | 0.41×0.21 | "Page" |  | Arial 12 bold |  |
| field | 0.21, 7.50 | 0.51×0.21 | `_PAGENO` |  | Arial 12 | right-aligned |
| label | 0.50, 6.83 | 0.36×0.21 | "Date" |  | Arial 12 bold |  |
| field | 0.50, 7.33 | 0.68×0.21 | `DATE()` |  | Arial 12 |  |
| label | 0.62, 1.80 | 0.21×0.40 | "T" |  | Arial 24 bold, RGB(0,0,255) |  |
| label | 0.62, 3.42 | 0.21×0.40 | "T" |  | Arial 24 bold, RGB(0,0,255) |  |
| label | 0.68, 1.97 | 1.33×0.34 | "asmanian" |  | Arial 20 bold |  |
| label | 0.68, 3.58 | 0.88×0.34 | "raders\n" |  | Arial 20 bold |  |
| line | 1.03, 0.00 | 8.01×0.01 | line |  |  |  |
| label | 1.09, 1.88 | 1.01×0.21 | "Code Report" |  | Arial 12 bold |  |

### Detail (0.50 in)

| Kind | Top, left (in) | Size w×h (in) | Content | Format | Font | Options |
|---|---|---|---|---|---|---|
| field | -0.01, 0.51 | 7.50×0.52 | `viewcode.code` |  | Courier New 10 | stretch |

### Page Footer (0.50 in)

Empty.

## Report variables

None.

## Page setup

- Orientation: not stored (`ORIENTATION=0`, printer default)
- Paper size: 1 (Letter); copies: 1; duplex 1
- Print quality: 600 dpi
- Saved printer environment: driver `WINSPOOL`, device `HP LaserJet 4Si/4SiMX PS`, output `\\msprint32\privj`

**NOTE:** the saved environment names an `HP LaserJet 4Si/4SiMX PS` on `\\msprint32\privj`, a Microsoft print server; VFP tries it first.

## Triggered from

- The View Code form's Print button only.

## Notes

- **Code prints in Courier New 10** with `stretch`, the only monospaced field in the reports.
- **Band bar height differs.** The detail field sits 19 designer pixels below the page header, not 20 like every other report: this FRX was last saved by a different VFP version's designer.
- **Not in `repolist.dbf`**, like the other two self-documentation prints; it can only be printed from its form.
