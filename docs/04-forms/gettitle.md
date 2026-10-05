# frmgettitle (gettitle.scx)

| Source file | Type | Path |
|---|---|---|
| `gettitle.scx` | Form | `forms/gettitle.sc2` |

**Purpose:** The employee listing report's parameter dialog: pick one employee title from a distinct list, or all titles. Returns the title (or `"ALL"`, or empty for Cancel) as the form's return value.

**Used by:**
- `reports/listempl.frx`'s data environment `Init` ([[../06-reports/listempl.md]]): `DO FORM forms\gettitle TO cTitle`, then `RETURN .F.` if empty, and `cTitle = ""` when it is `"ALL"` so the `EMPLOYEE LISTING` view parameter `?cTitle` matches everything.

**Related docs:** [[../03-data-model/README.md]] (`EMPLOYEE LISTING` view), [[../03-data-model/tables/employee.md]], [[README.md]].

The second form with **no framework base**. Uses a plain `combobox`, `checkbox`, and `label` alongside two `tscommandbutton`s, and returns its value through `Unload`'s `RETURN`, the classic VFP `DO FORM ... TO` protocol rather than the framework's `uRetVal`.

## Form metadata

- Base class / parent: `form`; class name `frmGetTitle`
- Caption: "Report Parameters"; `ControlBox = .F.`
- Modal (`WindowType = 1`), private data session (`DataSession = 2`), `AutoCenter`

**Custom properties:**

| Property | Description |
|---|---|
| `ctitle` | Stores the selected title |

## DataEnvironment

| Cursor | Alias | Source | Order |
|---|---|---|---|
| `Cursor1` | `Employee` | `Employee` |  |

Opens `Employee` so the combo's SQL can run in the private session.

DataEnvironment `BeforeOpenTables`:

```foxpro
SET TALK OFF
SET EXCLUSIVE OFF
```

## Controls (depth-first)

| Container path | Class | Bound to / key properties | Role |
|---|---|---|---|
| `cboTitle` | `combobox (commandbutton)` | rows `SELECT DISTINCT Employee.Title FROM Employee ORDER BY 1 INTO CURSOR cTitles`; disabled | Distinct titles via `SELECT DISTINCT Employee.Title ... INTO CURSOR cTitles`; disabled until "All Titles" is unchecked |
| `chkAllTitles` | `checkbox (commandbutton)` | caption "All Titles" | Checked by default |
| `cmdCancel` | `tscommandbutton (commandbutton)` | caption "\<Cancel" | Cancel |
| `cmdOK` | `tscommandbutton (commandbutton)` | caption "\<OK" | Default |
| `label1` | `label ()` | caption "What employee title would you like to print?" | "What employee title would you like to print?" |

### Events with code

#### `chkAllTitles.InteractiveChange`

```foxpro
IF this.Value
  thisform.cboTitle.Enabled = .F.
  thisform.cTitle = "ALL"
ELSE
  thisform.cboTitle.Enabled = .T.
  thisform.cTitle = thisform.cboTitle.Value
ENDIF
```

#### `cboTitle.InteractiveChange`

```foxpro
thisform.cTitle = this.Value
```

#### `cboTitle.Destroy`

```foxpro
IF USED("cTitles")
  USE IN cTitles
ENDIF
```

#### `cmdOK.Click`

```foxpro
RELEASE thisform
```

#### `cmdCancel.Click`

Empty title signals Cancel to the report.

```foxpro
thisform.cTitle = ""
RELEASE thisform
```

## Form methods

#### `Init`

```foxpro
*-- (c) Microsoft Corporation 1995

thisform.cboTitle.ListIndex = 1
```

#### `Unload`

The return value of `Unload` is what `DO FORM ... TO` receives.

```foxpro
SET MESSAGE TO
RETURN thisform.cTitle
```

#### `Activate`

```foxpro
SET MESSAGE TO thisform.Caption
```

## Tables read / written

| Table | Access | How |
|---|---|---|
| `EMPLOYEE` | read | DataEnvironment; `SELECT DISTINCT title` for the combo |

## Inter-form navigation

- **← [[../06-reports/listempl.md]]** only.

## Notes

- **Two return conventions in one app**: this form and [[getinv.md]] use `DO FORM ... TO` / `NAME ... LINKED`; the framework dialogs use `uRetVal`.
- **`ctitle` defaults to `"ALL"`** and the checkbox to checked, so OK without touching anything prints everyone.
- **The distinct title list is case- and space-sensitive** to whatever was typed in the employee form.
