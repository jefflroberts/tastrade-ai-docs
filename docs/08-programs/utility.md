# utility.prg

| Source file | Type | Path |
|---|---|---|
| `utility.prg` | Program | `progs/utility.prg` |

**Purpose:** The procedure file: six standalone functions (index-tag test, a placeholder, file size, active-form test, toolbar-button test, shutdown guard) kept outside the classes, as its header says, "for better performance and accessibility".

**Used by:**
- `environment.Set` in [[../05-classes/tsgen.md]]: `SET PROCEDURE TO UTILITY.PRG`, found through the `PROGS` entry of `SET PATH`; `environment.Reset` restores the previous procedure file on exit. Individual callers are listed per function below.

**Related docs:** [[../05-classes/tsbase.md]] (`tsifcombo`, `tstoolbar`), [[../04-forms/behindsc.md]], [[../07-menus/main.md]] and [[../07-menus/navigate.md]] and [[../07-menus/ordentry.md]] (menus whose `SKIP FOR` conditions call in here), [[tastrade.h.md]], [[main.md]], [[README.md]].

## Role

**Runtime library.** Loaded by `SET PROCEDURE` for the life of the application; five of its six functions have callers. `NotYet()` is dead and can go.

## What it does

Nothing at the top level beyond `#INCLUDE "INCLUDE\TASTRADE.H"`, needed for `NOTYET_LOC`, `CANNOTQUIT_LOC`, `TASTRADE_LOC`, and the `MB_*` constants. The functions:

| Function | Parameters | Returns | Called from |
|---|---|---|---|
| `IsTag` | `tcTagName, tcAlias` | `.T.` if the tag exists in the alias | [[../05-classes/tsbase.md]] `tsifcombo.Init`, to warn when the tag it derived from the `RowSource` does not exist (the comment there: "SET('PROCEDURE') should include Utility.prg"). |
| `NotYet` | `` | nothing | **Nothing.** Grepped every twin, menu, report, and the DBC: no caller. A construction-time placeholder ("Under Construction") left in the shipped library. |
| `FileSize` | `tcFileName` | bytes | [[../04-forms/behindsc.md]] `frmbehindsc.procstomem`, to size the file that `COPY PROCEDURES TO` wrote before reading it back with `FREAD`. |
| `FormIsObject` | `` | `.T.` if the active window is a form | [[../05-classes/tsbase.md]] `tstoolbar.oktosend`, `tstoolbar.Refresh`, `tstoolbar.cmdClose.Click`; [[../04-forms/behindsc.md]] `frmbehindsc.Load`; and the `SKIP FOR` conditions of the File, Navigation, and Items menus ([[../07-menus/main.md]], [[../07-menus/navigate.md]], [[../07-menus/ordentry.md]]). |
| `ToolBarEnabled` | `` | the button's `Enabled`, or `.F.` | The `SKIP FOR` conditions of New, Close, Save, and Restore on the File menu ([[../07-menus/main.md]]) only. |
| `OnShutdown` | `` | nothing | `ON SHUTDOWN DO OnShutDown`, set by `environment.Set` ([[../05-classes/tsgen.md]]) and restored to the previous handler by `environment.Reset`. |

## Key routines

#### `FUNCTION IsTag(tcTagName, tcAlias)`

Walks `TAG(n, alias)` until it runs out, comparing upper-cased trimmed names. **NOTE:** `lnTagNum` is not `LOCAL`, so it is created as a private variable visible to anything called below it. The `EMPTY(tcAlias)` check returns `.F.` rather than erroring when no table is open.

```foxpro
FUNCTION IsTag (tcTagName, tcAlias)
  *-- Receives a tag name and an alias (which is optional) as
  *-- parameters and returns .T. if the tag name exists in the
  *-- alias. If no alias is passed, the current alias is assumed.
  LOCAL llIsTag, ;
        lcTagFound
*-- ... 25 more lines of Microsoft's Tastrade source omitted; see `FUNCTION IsTag(tcTagName, tcAlias)` in your own copy of Tastrade.
```

#### `FUNCTION NotYet()`

Shows "Under Construction" (`NOTYET_LOC`). Dead, see above.

```foxpro
FUNCTION NotYet()
  *-- Used during construction of Tastrade to indicate those
  *-- parts of the application that were not yet completed.
  =MESSAGEBOX(NOTYET_LOC, MB_ICONINFORMATION)
  RETURN
ENDFUNC
```

#### `FUNCTION FileSize(tcFileName)`

`FSIZE()` returns a field's size unless `SET COMPATIBLE` is `ON`, so the function flips it on around the call and puts it back. **NOTE:** `&lcSetCompatible` macro substitution.

```foxpro
FUNCTION FileSize(tcFileName)
  *-- Returns the size of a file. SET COMPATIBLE must be ON for
  *-- FSIZE() to return the size of a file. Otherwise, it returns
  *-- the size of a field.
  LOCAL lcSetCompatible, lnFileSize

*-- ... 6 more lines of Microsoft's Tastrade source omitted; see `FUNCTION FileSize(tcFileName)` in your own copy of Tastrade.
```

#### `FUNCTION FormIsObject()`

True when `_screen.ActiveForm` is an object whose base class is a form; false for toolbars and for no window at all. The test every menu `SKIP FOR` and toolbar refresh starts with.

```foxpro
FUNCTION FormIsObject()
  *-- Return .T. if the active form is of type "O" and its baseclass
  *-- is "Form". 
  RETURN (TYPE("_screen.activeform") == "O" AND ;
          UPPER(_screen.ActiveForm.BaseClass) = "FORM")
ENDFUNC
```

#### `FUNCTION ToolBarEnabled()`

Builds the name `oApp.oToolBar.<button>.enabled` as text and evaluates it, returning `.F.` if the path does not resolve to a logical (no toolbar, no such button). Old-style `PARAMETER` rather than `LPARAMETERS`, so `oObject` is private; the body spells it `oobject`, which VFP does not mind.

```foxpro
FUNCTION ToolBarEnabled
  *- Return value of Toolbar object
  PARAMETER oObject
  LOCAL oToolObj
  oToolObj = "oApp.oToolBar." + oobject + ".enabled"
  IF TYPE(oToolObj) # "L"
*-- ... 5 more lines of Microsoft's Tastrade source omitted; see `FUNCTION ToolBarEnabled()` in your own copy of Tastrade.
```

#### `FUNCTION OnShutdown()`

Shows "Cannot quit Visual FoxPro within Tasmanian Traders." A shutdown handler that does not itself `QUIT` cancels the close, so this is what stops the user closing VFP with the application running; the only way out is the menu's Return to Visual FoxPro.

```foxpro
FUNCTION OnShutdown()
  *-- Custom message called via the ON SHUTDOWN command to indicate
  *-- that the user must exit Tastrade before exiting Visual Foxpro.
  =MESSAGEBOX(CANNOTQUIT_LOC, ;
              MB_ICONEXCLAMATION, ;
              TASTRADE_LOC)
ENDFUNC
```

## Inputs / outputs / side effects

- Reads the open table's index tags (`IsTag`), a file on disk (`FileSize`, through `FSIZE()`), the active form and the global `oApp` (`FormIsObject`, `ToolBarEnabled`).
- Writes nothing. `FileSize` toggles `SET COMPATIBLE` and puts it back; `NotYet` and `OnShutdown` show message boxes.
- Expects `oApp` to be the application object ([[../05-classes/main.md]]) and `_screen.ActiveForm` to be meaningful; both are true only inside the running application.

## Called from / calls

- **Called from:** see the table above; the file is on the procedure chain, so any code in the application can call these by name.
- **Calls:** VFP functions only (`TAG`, `FSIZE`, `TYPE`, `EVAL`, `MESSAGEBOX`); no other program, form, or class.

## Notes

- **One dead function** (`NotYet`), whose string `NOTYET_LOC` is in turn used by nothing else ([[strings.h.md]]).
- **`FormIsObject` is the sample's most-called helper**: three toolbar methods, one form, and nine menu bars depend on it.
- **Private-variable leak** in `IsTag` (`lnTagNum`), and old-style `PARAMETER` in `ToolBarEnabled`; the rest of the sample uses `LOCAL` and `LPARAMETERS`.
- **`OnShutdown` is a guard, not a cleanup**: it blocks the close and tells the user to exit through the menu. With `DEBUGMODE` on, `SET ESCAPE` is also left on ([[tastrade.h.md]]), so Esc can still interrupt code.
- **Comment header** says the functions are "independent of any classes"; two of them read `oApp` and `_screen.ActiveForm`.
