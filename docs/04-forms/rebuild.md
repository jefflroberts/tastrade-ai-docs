# frmdatabaseutils (rebuild.scx)

| Source file | Type | Path |
|---|---|---|
| `rebuild.scx` | Form | `forms/rebuild.sc2` |

**Purpose:** Database utilities: reindex every table in the DBC and/or validate the DBC, writing the validation output to a temporary file that is shown read-only.

**Used by:**
- The Utilities menu ([[../07-menus/main.md]]) bar "Rebuild DBC/Reindex": `DO FORM rebuild`, `SKIP FOR !EMPTY(WONTOP())`.

**Related docs:** [[../03-data-model/README.md]], [[README.md]].

## Form metadata

- Base class / parent: `tsbaseform` → `form`
- Caption: "Database Utilities"
- Modal, **`DataSession = 1`** (the default session, set explicitly), no toolbar, new/edit/delete off
- Empty DataEnvironment; it works on whatever database is current

**Custom methods:**

| Method | Description |
|---|---|
| `rebuildindexes` | Rebuilds indexes for all tables in the current DBC. |
| `validatedbc` | Validates the current DBC. |

## DataEnvironment

No cursors. Operates on `DBC()` of the default session, which the application opened at start-up.

## Controls (depth-first)

| Container path | Class | Bound to / key properties | Role |
|---|---|---|---|
| `chkRebuild` | `tscheckbox (checkbox)` | caption "\<Rebuild Indexes" | "Rebuild Indexes" |
| `chkValidate` | `tscheckbox (checkbox)` | caption "\<Validate DBC" | "Validate DBC" |
| `cmdCancel` | `tscommandbutton (commandbutton)` | caption "\<Cancel" | Cancel |
| `cmdOK` | `tscommandbutton (commandbutton)` | caption "\<OK"; disabled | Default; disabled until a box is checked |

### Events with code

#### `cmdOK.Click`

```foxpro
IF thisform.chkValidate.Value
  thisform.ValidateDBC()
ENDIF

IF thisform.chkRebuild.Value
  thisform.RebuildIndexes()
*-- ... 3 more lines of Microsoft's Tastrade source omitted; see `cmdOK.Click` in your own copy of Tastrade.
```

#### `chkRebuild.Click`

```foxpro
thisform.cmdOK.Enabled = this.Value OR thisform.chkValidate.Value
```

#### `chkValidate.Click`

```foxpro
thisform.cmdOK.Enabled = this.Value OR thisform.chkRebuild.Value
```

#### `cmdCancel.Click`

```foxpro
RELEASE thisform
```

## Form methods

#### `rebuildindexes`

`CLOSE TABLES`, then for each table in the DBC, `USE ... EXCLUSIVE` and `REINDEX`. **NOTE:** `CLOSE TABLES` in the default session closes the tables other open forms' shared cursors may depend on, and any table another user has open makes the exclusive `USE` fail with an error the base `Error` handler shows. Meant for a single user with everything closed, which the menu's `SKIP FOR !EMPTY(WONTOP())` half-enforces.

```foxpro
*-- (c) Microsoft Corporation 1995

LOCAL laTables[1], ;
      i

CLOSE TABLES
*-- ... 12 more lines of Microsoft's Tastrade source omitted; see `rebuildindexes` in your own copy of Tastrade.
```

#### `validatedbc`

`VALIDATE DATABASE TO FILE` into `valdbc.txt` in the current directory, shown with `MODIFY FILE ... NOMODIFY`, then deleted. The `#DEFINE OUTFILE` inside a method is a compile-time constant local to that method's compilation.

```foxpro
#DEFINE OUTFILE  "valdbc.txt"
CLOSE TABLES

IF FILE(OUTFILE)
  DELETE FILE OUTFILE
ENDIF
*-- ... 10 more lines of Microsoft's Tastrade source omitted; see `validatedbc` in your own copy of Tastrade.
```

## Tables read / written

| Table | Access | How |
|---|---|---|
| every table in `tastrade.dbc` | reindex (exclusive) | `ADBOBJECTS` loop |
| `valdbc.txt` | write, then delete | validation output |

## Inter-form navigation

- **← Utilities menu** only.

## Notes

- **Exclusive access in a shared app**; the sample's `SET EXCLUSIVE OFF` elsewhere is overridden here per table.
- **Does not touch the three free tables** (`behindsc`, `repolist`, `ttrade`), which are not in the DBC.
- **`WAIT WINDOW` progress** and `MODIFY FILE` are IDE-style UI; a runtime EXE shows them too, as plain windows.
