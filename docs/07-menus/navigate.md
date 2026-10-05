# Navigation menu (navigate.mnx)

| Source file | Type | Path |
|---|---|---|
| `navigate.mnx` | Menu | `menus/navigate.mn2` |

**Purpose:** One pad, Navigation, with First / Prior / Next / Last and their Ctrl+Home / PgUp / PgDn / End shortcuts; each bar clicks the matching button of the shared navigation toolbar.

**Used by:**
- `application.ShowNavToolBar` in [[../05-classes/tsgen.md]]: `DO navigate.mpr` after creating and showing the toolbar, for the first `tsbaseform` instance only (the call comes from `tsbaseform.Init` in [[../05-classes/tsbase.md]] when the form has a `cToolBar`).
- Removed by `application.ReleaseNavToolBar` when the last such form closes: `RELEASE POPUP navigation EXTENDED` and `RELEASE PAD _msm_edit OF _msysmenu`.

**Related docs:** [[../05-classes/tsgen.md]], [[../05-classes/tsbase.md]] (`tstoolbar`), [[main.md]] (the bar it is inserted into), [[ordentry.md]] (the pad placed after this one), [[window.md]], [[README.md]].

## Menu structure

Menu type 1, location `AFTER _MFILE`.

### Pad: Navigation  (`_msm_edit`)

hot key ALT+N; status text "Commands to navigate through records on the active form"; popup `Navigation`; designer comment `*-- Pad name is "_msm_edit" for better placement of the "Items" menu pad for the Order Entry form.`.

Each bar is skipped unless a form is active, the toolbar object exists, and the matching button is enabled, so the menu mirrors the toolbar's state. The pad is named `_msm_edit` (VFP's system name for the Edit pad) for the reason the designer comment gives: the order entry form's Items pad is placed `AFTER _MEDIT`, and this name makes it land here rather than after the main menu's Edit pad, which is named `Edit`.

| Bar | Prompt | Shortcut | Skip For | Action |
|---|---|---|---|---|
| `1` | First | Ctrl+Home | `!FormIsObject()  OR TYPE("oApp.oToolBar") <> "O"  OR !oApp.oToolBar.cmdFirst.Enabled` | `oApp.oToolbar.cmdFirst.Click()` |
| `2` | Prior | Ctrl+PgUp | `!FormIsObject()  OR TYPE("oApp.oToolBar") <> "O"  OR !oApp.oToolBar.cmdPrior.Enabled` | `oApp.oToolbar.cmdPrior.Click()` |
| `3` | Next | Ctrl+PgDn | `!FormIsObject()  OR TYPE("oApp.oToolBar") <> "O"  OR !oApp.oToolBar.cmdNext.Enabled` | `oApp.oToolbar.cmdNext.Click()` |
| `4` | Last | Ctrl+End | `!FormIsObject()  OR TYPE("oApp.oToolBar") <> "O"  OR !oApp.oToolBar.cmdLast.Enabled` | `oApp.oToolbar.cmdLast.Click()` |

Menu-level handler: `ON SELECTION MENU _MSYSMENU *-- (c) Microsoft Corporation 1995` (a comment, so a no-op; the same line closes every menu in the sample).

## Setup / cleanup code

Setup code:

```foxpro
#INCLUDE "INCLUDE\TASTRADE.H"
```

The include file is not used by anything in this menu.

No cleanup code.

## What it launches

- `oApp.oToolbar.cmdFirst/cmdPrior/cmdNext/cmdLast.Click()`: the `tstoolbar` buttons in [[../05-classes/tsbase.md]], which act on `_screen.ActiveForm` through the base form's navigation methods.

## Notes

- **No `.mpr` in the repo.** `navigate.mnx` and `window.mnx` have no generated program beside them, unlike the other three; the built `tastrade.exe` contains this menu's status text, so the VFP build generated the code itself. The `.pj2` has descriptions for the other three menus and none for these two.
- **Placement by system names.** Location `AFTER _MFILE` puts the pad after the pad VFP knows as the File pad, and the main menu gave that name, `_msm_file`, to its Administration pad ([[main.md]]). Read together with `tsbaseform.Init`, which adds the Window pad (also `AFTER _MFILE`) before it shows the toolbar, the resulting bar is File, Edit, Orders, Administration, Navigation, Window, Utilities, Help, with Items after Navigation while order entry is active. Not run here.
- **Keyboard map.** Ctrl+Home, Ctrl+PgUp, Ctrl+PgDn, Ctrl+End; pad Alt+N.
- **Twin only**: with no `.mpr` there is nothing to cross-check the twin against except the EXE's strings. It has no cascading-popup artifacts because it has no separators.
- **The copyright line is the menu's `ON SELECTION MENU` command**, as in every menu of the sample.
