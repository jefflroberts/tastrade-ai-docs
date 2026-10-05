# Employee Listing (listempl.frx)

| Source file | Type | Path |
|---|---|---|
| `listempl.frx` | Report | `reports/listempl.fr2` |

**Purpose:** Prints employees grouped by title (name, extension, notes) from the `EMPLOYEE LISTING` view, after asking which title to print through the `gettitle` dialog.

**Used by:**
- The report picker [[../04-forms/reports.md]] (`frmreports`, from the File menu's "Print Reports ..."), row `LISTEMPL` / "Employee Listing" of type `LIST` in `data/repolist.dbf`.

**Related docs:** [[../04-forms/gettitle.md]] (the parameter dialog), [[../03-data-model/README.md]] (`EMPLOYEE LISTING` view), [[../03-data-model/tables/employee.md]], [[../04-forms/reports.md]], [[README.md]].

One of two reports whose data environment runs a form before opening its tables (the other is [[orders.md]]). `AutoOpenTables` is off so `Init` can collect the parameter first; the view's `?cTitle` is then satisfied by the private variable that `DO FORM ... TO cTitle` created.

## DataEnvironment

| Cursor | Alias | Source | Database | Filter |
|---|---|---|---|---|
| `Cursor1` | `employee_listing` | `employee listing` | `..\data\tastrade.dbc` |  |

Properties: `AutoOpenTables = .F.`, `AutoCloseTables = .F.`, `InitialSelectedAlias = "employee_listing"`.

DataEnvironment `Init`:

Runs the title dialog, maps "ALL" to an empty string (which matches every title under the default `SET ANSI OFF` comparison), opens the view, and refuses to print when it returns no rows. **NOTE:** `NOTHINGTOPRINT_LOC`, `TASTRADE_LOC`, and `MB_ICONEXCLAMATION` are `#DEFINE`s from `include/tastrade.h`, but this code has no `#INCLUDE` (compare [[orders.md]], which has one). The compiled code in `reports/listempl.frt` still carries the three names and not the strings, so the message box line refers to three undefined variables: when no employee has the chosen title the report errors instead of saying "Nothing to print." **NOTE:** `WEXIST("Project Manager")` switches to `HOME() + "Samples\Tastrade\"`, a path that assumes the sample sits under the VFP install folder.

```foxpro
#DEFINE C_TASTRADEDIR_LOC	"Samples\Tastrade\"		&& Location of Tastrade, off of HOME()

LOCAL llContinue

IF WEXIST("Project Manager")
	*- assume that TasTrade isn't running, since it closes the Project Manager window
*-- ... 23 more lines of Microsoft's Tastrade source omitted; see `DataEnvironment` in your own copy of Tastrade.
```

DataEnvironment `Destroy`:

```foxpro
THIS.CLOSETABLES()
```

## Bands & content

The page header carries the sample's wordmark (four labels: a blue 24-point "T" before "asmanian" and before "raders"), the logo bitmap `bitmaps/ttradesm.bmp` (present in the repo), and Page / Date fields.

### Page Header (2.09 in)

| Kind | Top, left (in) | Size w×h (in) | Content | Format | Font | Options |
|---|---|---|---|---|---|---|
| picture | 0.12, 0.49 | 0.86×0.92 | picture `..\bitmaps\ttradesm.bmp` |  |  | file; clip; comment "(c) Microsoft Corporation 1995" |
| label | 0.31, 6.82 | 0.41×0.21 | "Page" |  | Arial 12 bold |  |
| field | 0.31, 7.49 | 0.51×0.21 | `_PAGENO` |  | Arial 12 | right-aligned |
| label | 0.60, 6.82 | 0.36×0.21 | "Date" |  | Arial 12 bold |  |
| field | 0.60, 7.32 | 0.68×0.21 | `DATE()` |  | Arial 12 |  |
| label | 0.72, 1.55 | 0.21×0.40 | "T" |  | Arial 24 bold, RGB(0,0,255) |  |
| label | 0.72, 3.17 | 0.21×0.40 | "T" |  | Arial 24 bold, RGB(0,0,255) |  |
| label | 0.77, 1.72 | 1.33×0.34 | "asmanian" |  | Arial 20 bold |  |
| label | 0.77, 3.33 | 0.88×0.34 | "raders\n" |  | Arial 20 bold |  |
| line | 1.12, 0.00 | 8.03×0.01 | line |  |  |  |
| label | 1.22, 1.62 | 1.38×0.21 | "Employee Listing" |  | Arial 12 bold |  |
| rectangle | 1.75, 0.00 | 8.03×0.34 | grey fill |  |  |  |
| label | 1.84, 0.05 | 1.29×0.21 | "Employee Name" |  | Arial 12 bold | float |
| label | 1.84, 3.23 | 0.26×0.21 | "Ext" |  | Arial 12 bold | float |
| label | 1.84, 3.76 | 0.47×0.21 | "Notes" |  | Arial 12 bold | float |

### Group Header 1 (0.34 in)

Band flags: group on `Title`.

| Kind | Top, left (in) | Size w×h (in) | Content | Format | Font | Options |
|---|---|---|---|---|---|---|
| field | 0.12, 0.05 | 3.06×0.22 | `Title` |  | Arial 12 bold, RGB(0,0,128) |  |

### Detail (0.35 in)

| Kind | Top, left (in) | Size w×h (in) | Content | Format | Font | Options |
|---|---|---|---|---|---|---|
| field | 0.00, 0.26 | 2.90×0.21 | `trim(last_name)+', ' + first_name` |  | Arial 12 | stretch; float |
| field | 0.00, 3.23 | 0.41×0.21 | `extension` |  | Arial 12 | stretch; float |
| field | 0.00, 3.76 | 4.27×0.21 | `notes` |  | Arial 12 | stretch; float |

### Group Footer 1 (0.00 in)

Empty.

### Page Footer (0.11 in)

Empty.

## Report variables

None.

## Page setup

- Orientation: not stored (`ORIENTATION=0`, printer default)
- Paper size: 1 (Letter); copies: 1; duplex 1
- Saved printer environment: driver `winspool`, device `\\MSPRINT32\2/1MC PRIVJ 157.56.32.242`, output `Ne02:`

**NOTE:** the saved environment names `\\MSPRINT32`, a Microsoft print server from the 1990s, with an IP address in the 157.56 range. VFP tries the saved printer first when the report runs.

## Triggered from

- `forms/reports.sc2` `cmdRun.Click`: `REPORT FORM (lcSeleRepo) PREVIEW`, or `TO PRINTER NOCONSOLE` after `PRINTSTATUS()`, or `TO FILE <stem>.TXT ASCII`, where `lcSeleRepo` is `REPORTS\LISTEMPL.FRX`.
- The ASCII output drops lines, boxes, and pictures.

## Notes

- **Group header prints `Title`** in navy bold; the group footer has zero height. The view orders by title, so the grouping works.
- **Detail name expression** `trim(last_name)+', ' + first_name`; `notes` is a memo printed with `stretch`.
- **The Cancel path** returns `.F.` from `Init`, which cancels the report silently; the picker shows nothing.
- `*=REQUERY()` is a commented-out leftover.
- `DEFAULTSOURCE=265` in the printer environment (a driver-specific paper tray) versus 7 in the other listings.
