# Items menu (ordentry.mnx)

| Source file | Type | Path |
|---|---|---|
| `ordentry.mnx` | Menu | `menus/ordentry.mn2` |

**Purpose:** One pad, Items, with Add Line Item (Ctrl+Ins) and Remove Line Item (Ctrl+Del) for the order entry form's grid; present only while that form is active.

**Used by:**
- `frmorderentry.Activate` in [[../04-forms/ordentry.md]]: `DO menus\ordentry.mpr` on every activation; `Deactivate` and `Destroy` both do `RELEASE PAD orderentry OF _msysmenu`. A `*-DO menus\ordentry.mpr` in `Load` is commented out.

**Related docs:** [[../04-forms/ordentry.md]] (`GridAddItem`, `GridRemoveItem`, and the right-click popup that offers the same two actions), [[../05-classes/orders.md]], [[navigate.md]] (the pad this one is placed after), [[main.md]], [[README.md]].

## Menu structure

Menu type 1, location `AFTER _MEDIT`.

### Pad: Items  (`orderentry`)

hot key ALT+I; `SKIP FOR !WONTOP("frmorderentry")`; status text "Add and delete line items for the Order Entry form"; popup `Items`.

The pad itself is skipped unless the order entry form is the top window, and each bar checks the form's `lAllowEdits` / `lAllowDelete`; Remove also requires the active control to be a grid, so it cannot fire while the cursor is in a header field.

| Bar | Prompt | Shortcut | Skip For | Action |
|---|---|---|---|---|
| `1` | Add Line Item | Ctrl+Ins | `!FormIsObject() OR !_screen.Activeform.lAllowEdits` | `_screen.Activeform.GridAddItem()` |
| `2` | Remove Line Item | Ctrl+Del | `!FormIsObject() OR !_screen.Activeform.lAllowDelete OR TYPE("_screen.Activeform.Activecontrol") <> "O" OR UPPER(_screen.Activeform.Activecontrol.BaseClass) <> "GRID"` | `_screen.Activeform.GridRemoveItem()` |

Menu-level handler: `ON SELECTION MENU _MSYSMENU *-- (c) Microsoft Corporation 1995` (a comment, so a no-op; the same line closes every menu in the sample).

## Setup / cleanup code

No setup code.

No cleanup code.

## What it launches

- `_screen.Activeform.GridAddItem()` and `GridRemoveItem()`: methods of the `orderentry` class in [[../05-classes/orders.md]], the same ones the grid's shortcut popup calls.

## Notes

- **Twin versus `.mpr`.** The twin is FoxBin2PRG's rendering of the `.mnx`; `menus/ordentry.mpr` is GENMENU's output dated 10/12/00. They match statement for statement apart from formatting, the generated procedure names (`_07y0s8...` there, `BAR_n_OF_popup_FB2P` here), the `AFTER _MEDIT` clause, which the `.mpr` writes on the `DEFINE PAD` and the twin keeps in its `MenuLocation` header, and the empty cascading popup the twin emits for each separator, which the `.mpr` does not have.
- **Redefined on every activation.** The pad is added each time the form becomes active and released each time it deactivates, so switching between forms rebuilds it; the `.mpr` is small enough that this costs nothing visible.
- **Placement.** `AFTER _MEDIT` resolves to the Navigation pad, which is named `_msm_edit` for exactly this purpose ([[navigate.md]]).
- **Two ways to reach the same two actions**: this pad with keyboard shortcuts, and the grid's right-click popup built in code ([[../04-forms/ordentry.md]]).
- **The copyright line is the menu's `ON SELECTION MENU` command**, as in every menu of the sample.
