# frmcasestudy (casestdy.scx)

| Source file | Type | Path |
|---|---|---|
| `casestdy.scx` | Form | `forms/casestdy.sc2` |

**Purpose:** A read-only viewer for the "Case Study" text stored in `behindsc.dbf` under `screen_id = "*Case Study"`, with a Print button that runs the `casestdy` report.

**Used by:**
- **Nothing.** No menu, form, class, or program in the source runs this form. It is in the project (`Case Study Form`) and builds into the EXE, but it is reachable only by `DO FORM casestdy` from the Command window.

**Related docs:** [[../05-classes/tsbase.md]] (`tstextform`), [[../06-reports/casestdy.md]], [[behindsc.md]] (the same table), [[README.md]].

## Form metadata

- Base class / parent: `tstextform` → `tsbaseform` → `form`
- Caption: "Case Study"
- Modal (`WindowType = 1`), private data session, no toolbar, no buffering (`BufferMode = 0`), new/edit/delete off
- `edtText.ControlSource = "behindsc.desc"`, white background

## DataEnvironment

| Cursor | Alias | Source | Order |
|---|---|---|---|
| `Cursor1` | `behindsc` | `..\data\behindsc.dbf` |  |

Free table `behindsc.dbf`; `Load` positions on the `*Case Study` row via `SEEKVALUE_LOC`.

DataEnvironment `BeforeOpenTables`:

```foxpro
SET TALK OFF
SET EXCLUSIVE OFF
```

## Controls (depth-first)

No controls of its own; `edtText`, `cmdClose`, `cmdPrint` come from `tstextform`.

### Events with code

#### `cmdPrint.Click`

The `tstextform` base leaves `cmdPrint.Click` empty; this form supplies it: confirm, hourglass, `PRINTSTATUS()`, `REPORT FORM casestdy TO PRINTER NOCONSOLE`.

```foxpro
LOCAL lnAnswer
lnAnswer = MESSAGEBOX(VIEWCSDTYPRINT_LOC, ;
                      MB_ICONQUESTION + MB_YESNO, ;
                      TASTRADE_LOC)
IF lnAnswer = IDYES
  thisform.WaitMode(.T.)
*-- ... 9 more lines of Microsoft's Tastrade source omitted; see `cmdPrint.Click` in your own copy of Tastrade.
```

## Form methods

#### `Load`

`SEEK("*Case Study", ALIAS(), "screen_id")`. The `screen_id` rows starting with `*` are excluded from the Behind the Scenes list by its `screen_id <> "*"` filter, which is how the two forms share one table.

```foxpro
*-- (c) Microsoft Corporation 1995

=SEEK(SEEKVALUE_LOC, ALIAS(), "screen_id")	&&"*Case Study"
```

## Tables read / written

| Table | Access | How |
|---|---|---|
| `behindsc.dbf` (free) | read | one row |

## Inter-form navigation

- **← nothing.**

## Notes

- **Unreachable in the shipped application.** Either a menu item was removed or it was only ever run by hand.
- **Print confirmation text** `VIEWCSDTYPRINT_LOC` is identical to `VIEWCODEPRINT_LOC`.
