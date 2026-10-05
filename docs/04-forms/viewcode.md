# frmviewcode (viewcode.scx)

| Source file | Type | Path |
|---|---|---|
| `viewcode.scx` | Form | `forms/viewcode.sc2` |

**Purpose:** The code window Behind the Scenes opens to display extracted source. A `tstextform` bound at run time to the `code` memo of a cursor named `viewcode` in the caller's data session.

**Used by:**
- [[behindsc.md]] `showcode`: `DO FORM viewcode WITH thisform.DataSessionID` after creating `CREATE CURSOR viewcode (code M)` and loading `SNIPPETS.TXT` into it.

**Related docs:** [[../05-classes/tsbase.md]] (`tstextform`), [[../06-reports/viewcode.md]], [[README.md]].

## Form metadata

- Base class / parent: `tstextform` → `tsbaseform` → `form`
- Caption: "Code Window"; `MaxButton = .F.`
- Inherits `tstextform`'s modal `WindowType = 1` and `DataSession = 2`, but `Init` immediately switches `DataSessionID` to the caller's session, which is the only way it can see the caller's cursor
- `edtText.ColorSource = 0`, `ControlSource` cleared in the designer and set in `Init`

## DataEnvironment

No cursors. The `viewcode` cursor belongs to the caller.

## Controls (depth-first)

No controls of its own.

### Events with code

#### `cmdPrint.Click`

Prints the extracted code with `REPORT FORM viewcode`, whose single field expression is `viewcode.code`.

```foxpro
LOCAL lnAnswer
lnAnswer = MESSAGEBOX(VIEWCODEPRINT_LOC, ;
                      MB_ICONQUESTION + MB_YESNO, ;
                      TASTRADE_LOC)
IF lnAnswer = IDYES
  thisform.WaitMode(.T.)
*-- ... 9 more lines of Microsoft's Tastrade source omitted; see `cmdPrint.Click` in your own copy of Tastrade.
```

## Form methods

#### `Init`

**NOTE:** `LPARAMETER` (singular) works but is unusual; the data session switch is the whole point of the method.

```foxpro
*-- (c) Microsoft Corporation 1995

LPARAMETER tnCallingFormDataSessionID
this.DataSessionID = tnCallingFormDataSessionID
thisform.edtText.ControlSource = "viewcode.code"
thisform.edtText.Refresh()
```

## Tables read / written

| Table | Access | How |
|---|---|---|
| cursor `viewcode` | read | in the caller's session |

## Inter-form navigation

- **← [[behindsc.md]]** only.

## Notes

- **Adopts the caller's data session** rather than receiving data; the reverse of the order history form, which pushes rows into another session.
- **Same print pattern** as the case study form, copy-pasted with a different report name.
