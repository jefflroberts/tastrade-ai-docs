# frmreports (reports.scx)

| Source file | Type | Path |
|---|---|---|
| `reports.scx` | Form | `forms/reports.sc2` |

**Purpose:** The report picker: choose Reports or Listings, pick one from the list held in the free table `repolist.dbf`, and send it to preview, printer, or an ASCII text file.

**Used by:**
- The File menu ([[../07-menus/main.md]]) bar "Print Reports ...": `DO FORM Reports`.

**Related docs:** [[../03-data-model/README.md]] (`repolist.dbf` schema and rows), [[../06-reports/README.md]] (the ten reports it can run), [[README.md]].

## Form metadata

- Base class / parent: `tsbaseform` → `form`
- Caption: "Print"
- Modal, **default data session**, no toolbar, `lallowedits = .F.`, `lallownew = .F.`

**Custom properties:**

| Property | Description |
|---|---|
| `nsaveselect` | Saves the selected workarea. |

## DataEnvironment

| Cursor | Alias | Source | Order |
|---|---|---|---|
| `cursor1` | `repolist` | `..\data\repolist.dbf` |  |

`repolist.dbf` is a free table (not in the DBC) with `cdosname`, `cfullname`, `ctype` (`REPO` or `LIST`); ten rows listing the reports by display name.

## Controls (depth-first)

| Container path | Class | Bound to / key properties | Role |
|---|---|---|---|
| `cmdClose` | `tscommandbutton (commandbutton)` | caption "\<Close" | Cancel |
| `cmdRun` | `tscommandbutton (commandbutton)` | caption "\<Run" | Default |
| `lstReport` | `listbox ()` | rows `cfullname, cdosname` | `RowSourceType = 6` over `cfullname, cdosname`, `BoundColumn = 2` so `Value` is the file stem |
| `opgOutput` | `optiongroup ()` |  | `optScreen` (preview, default) / `optPrinter` / `optFile` |
| `opgOutputType` | `optiongroup (shape)` |  | `optReports` / `optListings`; drives the filter on `repolist` |
| `Ts3dshape1` | `ts3dshape (shape)` |  |  |
| `Tslabel1` | `tslabel (label)` | caption "Output Type" | "Output Type" |

### Events with code

#### `cmdRun.Click`

Builds `REPORTS\<stem>.FRX`, checks it exists, then `REPORT FORM` with `PREVIEW`, `TO PRINTER NOCONSOLE` (after `PRINTSTATUS()`), or `TO FILE <stem>.TXT ASCII`. **NOTE:** the text file lands in the current directory and `lcTextFile` is not `LOCAL`. **NOTE:** reports whose data environment runs a dialog (invoices, employee listing) show that dialog from here; the rest open the DBC views themselves.

```foxpro
LOCAL lcSeleRepo

lcSeleRepo = "REPORTS\" + ALLTRIM(repoList.cdosname) + ".FRX"

IF NOT FILE(lcSeleRepo)
  =MESSAGEBOX(REPORTNOTFOUND_LOC, MB_ICONEXCLAMATION)
*-- ... 20 more lines of Microsoft's Tastrade source omitted; see `cmdRun.Click` in your own copy of Tastrade.
```

#### `opgOutputType.Click`

```foxpro
thisform.Refresh()
thisform.lstReport.ListIndex = 1
thisform.lstReport.SetFocus()
```

#### `lstReport.DblClick`

```foxpro
thisform.cmdRun.Click()
```

#### `lstReport.KeyPress`

Enter would fire both the list's `DblClick` and the default button's `Click`, running the report twice; the handler swallows Enter and calls `DblClick` once.

```foxpro
LPARAMETERS nKeyCode, nShiftAltCtrl

*-- We want to provide the user with a visual clue that the
*-- Run command button is the default button.(By setting it's
*-- Default property.  However, if we don't trap for the
*-- Enter key being pressed, the DblClick() method will be
*-- ... 8 more lines of Microsoft's Tastrade source omitted; see `lstReport.KeyPress` in your own copy of Tastrade.
```

#### `lstReport.Init`

Refuses to instantiate the list if the table is empty, which VFP treats as an error.

```foxpro
IF RECCOUNT("RepoList") = 0
  RETURN .F.
ENDIF
```

## Form methods

#### `Refresh`

Filters `repolist` to `REPO` or `LIST` by macro-substituted `SET FILTER` and requeries the list.

```foxpro
LOCAL lcFilter
SELECT repolist

lcFilter = "ctype = '" + IIF(thisform.opgOutputType.optReports.Value = 1, ;
                            "REPO", ;
                            "LIST") + "'"
*-- ... 4 more lines of Microsoft's Tastrade source omitted; see `Refresh` in your own copy of Tastrade.
```

#### `Init`

```foxpro
*-- (c) Microsoft Corporation 1995

tsBaseForm::Init()
thisform.Refresh()
this.nSaveSelect = SELECT()

*-- ... 3 more lines of Microsoft's Tastrade source omitted; see `Init` in your own copy of Tastrade.
```

#### `Destroy`

Restores the work area that was selected before the form opened.

```foxpro
tsBaseForm::Destroy()
SELECT (this.nSaveSelect)
```

#### `cmdClose.Click`

```foxpro
RELEASE thisform
```

## Tables read / written

| Table | Access | How |
|---|---|---|
| `repolist.dbf` (free) | read | DataEnvironment, filtered by type |
| everything the chosen report reads | read | through the report's own data environment or the DBC views |

## Inter-form navigation

- **← File menu**.
- **→ every report** in `reports/*.frx` by name from `repolist`; the invoice and employee reports open [[getinv.md]] and [[gettitle.md]] from their data environments.

## Notes

- **Report list is data**, so a report can be added or hidden by editing `repolist.dbf`; a stem with no matching `.frx` shows "Report file not found."
- **`&lcFilter` macro** in `Refresh`.
- **`ReleaseErase`, `TerminateRead`, `ReadSize`** are FoxPro 2.x screen-conversion properties left on the controls; inert in VFP.
