# Window menu (window.mnx)

| Source file | Type | Path |
|---|---|---|
| `window.mnx` | Menu | `menus/window.mn2` |

**Purpose:** An empty Window pad that the base form class fills at run time with one bar per open form; selecting a bar activates that form's window.

**Used by:**
- `tsbaseform.AddToMenu` in [[../05-classes/tsbase.md]]: `DO menus\window.mpr` when no popup named `Window` exists yet, then `DEFINE BAR n OF Window PROMPT thisform.caption` and `ON SELECTION BAR n OF Window ACTIVATE WINDOW <form name>` (by macro). Called from `tsbaseform.Init` for forms with a `cToolBar`, and by [[../04-forms/behindsc.md]] directly.
- `tsbaseform.RemoveFromMenu` releases the form's bar and, when the popup is empty, `RELEASE POPUP window EXTENDED` and `RELEASE PAD window OF _MSYSMENU`; [[../04-forms/ordhist.md]] passes its original caption because it renames itself.

**Related docs:** [[../05-classes/tsbase.md]], [[main.md]], [[navigate.md]], [[README.md]].

## Menu structure

Menu type 1, location `AFTER _MFILE`.

### Pad: Window  (`Window`)

hot key ALT+W; status text "Window selection"; popup `Window`.

The designer needs a bar to save, so the menu carries one placeholder bar, "This bar will be removed", and the cleanup code removes it, leaving an empty popup for the forms to fill. The twin also shows an empty cascading popup `Thisbarwil` hanging off the placeholder; the placeholder and the popup are both gone once the cleanup code has run.

| Bar | Prompt | Shortcut | Skip For | Action |
|---|---|---|---|---|
| `1` | This bar will be removed |  |  | none; cascades to `Thisbarwil` |

Menu-level handler: `` (a comment, so a no-op; the same line closes every menu in the sample).

## Setup / cleanup code

Setup code:

```foxpro
#INCLUDE "INCLUDE\TASTRADE.H"
```

The include file is not used by anything in this menu.

Cleanup code (runs after the definitions):

Deletes the placeholder bar the moment the menu is defined.

```foxpro
RELEASE BAR 1 OF Window
```

## What it launches

- Nothing of its own. Each bar the forms add runs `ACTIVATE WINDOW <form name>`; the bar numbers come from `CNTBAR()` / `GETBAR()` so they stay unique as forms open and close.

## Notes

- **No `.mpr` in the repo**, as for [[navigate.md]]; the EXE contains "This bar will be removed", so the build generated it.
- **Placement.** `AFTER _MFILE`, which lands after the Administration pad ([[main.md]]) and, because `tsbaseform.Init` adds this pad before it shows the toolbar, ends up to the right of Navigation. Not run here.
- **Guarded by `TYPE("oApp") == "O"`** in both `AddToMenu` and `RemoveFromMenu`, so a form run outside the application skips the Window menu.
- **The copyright line is the menu's `ON SELECTION MENU` command**, as in every menu of the sample.
