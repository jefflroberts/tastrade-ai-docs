# Behind the Scenes (behindsc.frx)

| Source file | Type | Path |
|---|---|---|
| `behindsc.frx` | Report | `reports/behindsc.fr2` |

**Purpose:** Prints the explanation text (`behindsc.desc`) of the topic currently selected in the Behind the Scenes form.

**Used by:**
- [[../04-forms/behindsc.md]] `cmdPrint.Click`: `REPORT FORM behindsc NEXT 1 TO PRINTER NOCONSOLE`.

**Related docs:** [[../04-forms/behindsc.md]], [[../03-data-model/README.md]] (`behindsc.dbf` schema), [[casestdy.md]] (same layout), [[README.md]].

## DataEnvironment

| Cursor | Alias | Source | Database | Filter |
|---|---|---|---|---|
| `Cursor1` | `behindsc` | `..\data\behindsc.dbf` |  |  |

Properties: `AutoOpenTables = .F.`, `AutoCloseTables = .F.`, `InitialSelectedAlias = "behindsc"`.

`AutoOpenTables` is off and there is no code, so the cursor is never opened by the report: it prints against the `behindsc` alias the form already has open in its data session, which is what `NEXT 1` (the current record only) needs.

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
| label | 1.09, 1.83 | 1.50×0.21 | "Behind the Scenes" |  | Arial 12 bold |  |

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
- Paper size: 1 (Letter); copies: 1
- Print quality: 300 dpi
- Saved printer environment: driver `winspool`, device `LaserNT`, output `Ne00:`

**NOTE:** the saved environment names `LaserNT`, a printer on the original author's machine; VFP tries it first when the report runs.

## Triggered from

- The form's Print button, printer only (no preview), after `PRINTSTATUS()`.

## Notes

- **Same layout as [[casestdy.md]]** with the title label "Behind the Scenes"; the two differ only in the title, the cursor filter, and whether the cursor auto-opens.
- **`behindsc.desc`** is a memo printed in Arial 10 with `stretch` in a 0.71 in detail band.
