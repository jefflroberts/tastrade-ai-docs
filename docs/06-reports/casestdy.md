# Case Study (casestdy.frx)

| Source file | Type | Path |
|---|---|---|
| `casestdy.frx` | Report | `reports/casestdy.fr2` |

**Purpose:** Prints every "Case Study" row of `behindsc.dbf` (`screen_id = "*Case Study"`), the text the case study form displays.

**Used by:**
- [[../04-forms/casestdy.md]] `cmdPrint.Click`: `REPORT FORM casestdy TO PRINTER NOCONSOLE`, after a Yes/No confirmation.

**Related docs:** [[../04-forms/casestdy.md]], [[behindsc.md]] (same layout), [[../03-data-model/README.md]] (`behindsc.dbf`), [[README.md]].

**Dead report.** The only thing that runs it is the case study form, and nothing in the source runs that form (see [[../04-forms/casestdy.md]]). It compiles into the EXE and is unreachable.

## DataEnvironment

| Cursor | Alias | Source | Database | Filter |
|---|---|---|---|---|
| `Cursor1` | `behindsc` | `..\data\behindsc.dbf` |  | `'SCREEN_ID = "*Case Study"'` |

`AutoOpenTables` is left on, so the report opens `behindsc.dbf` itself with the filter above, in the calling form's data session where the form has the same alias open already; not run here.

## Bands & content

The page header carries the sample's wordmark (four labels: a blue 24-point "T" before "asmanian" and before "raders"), the logo bitmap `bitmaps/ttradesm.bmp` (present in the repo), and Page / Date fields.

### Page Header (1.34 in)

| Kind | Top, left (in) | Size w×h (in) | Content | Format | Font | Options |
|---|---|---|---|---|---|---|
| picture | 0.03, 0.62 | 0.86×0.92 | picture `..\bitmaps\ttradesm.bmp` |  |  | file; clip; comment "(c) Microsoft Corporation 1995" |
| label | 0.15, 6.83 | 0.41×0.21 | "Page" |  | Arial 12 bold |  |
| field | 0.15, 7.50 | 0.51×0.21 | `_PAGENO` |  | Arial 12 | right-aligned |
| label | 0.44, 6.83 | 0.36×0.21 | "Date" |  | Arial 12 bold |  |
| field | 0.44, 7.33 | 0.68×0.21 | `DATE()` |  | Arial 12 |  |
| label | 0.62, 1.80 | 0.21×0.40 | "T" |  | Arial 24 bold, RGB(0,0,255) |  |
| label | 0.62, 3.42 | 0.21×0.40 | "T" |  | Arial 24 bold, RGB(0,0,255) |  |
| label | 0.68, 1.97 | 1.33×0.34 | "asmanian" |  | Arial 20 bold |  |
| label | 0.68, 3.58 | 0.88×0.34 | "raders\n" |  | Arial 20 bold |  |
| line | 1.03, 0.00 | 8.03×0.01 | line |  |  |  |
| label | 1.09, 1.88 | 0.92×0.21 | "Case Study" |  | Arial 12 bold |  |

### Detail (0.71 in)

| Kind | Top, left (in) | Size w×h (in) | Content | Format | Font | Options |
|---|---|---|---|---|---|---|
| field | 0.00, 0.10 | 7.82×0.69 | `behindsc.desc` |  | Arial 10 | stretch |

### Page Footer (0.50 in)

Empty.

## Report variables

None.

## Page setup

- Orientation: not stored (`ORIENTATION=0`, printer default)
- Paper size: 1 (Letter); copies: 1; duplex 1
- Print quality: 600 dpi
- Saved printer environment: driver `winspool`, device `LaserNT`, output `Ne00:`
- The binary DEVNAMES block disagrees: driver `WINSPOOL`, device `HP LaserJet 4Si/4SiMX PS`, output `\\msprint32\privj`

**NOTE:** the text environment names `LaserNT` but the binary DEVNAMES block names an HP LaserJet 4Si on `\\msprint32\privj`; the report was saved on two different machines and the two halves of the printer record were not updated together.

## Triggered from

- The case study form's Print button only.

## Notes

- **Filter stored on the cursor**: `SCREEN_ID = "*Case Study"`, the same value the form seeks (`SEEKVALUE_LOC`).
- **Printer environment records disagree**, see Page setup.
- The FRX has `Cpid="0"` in the project; layout identical to [[behindsc.md]].
