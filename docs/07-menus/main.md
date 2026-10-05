# Main menu (main.mnx)

| Source file | Type | Path |
|---|---|---|
| `main.mnx` | Menu | `menus/main.mn2` |

**Purpose:** The application's menu bar: File (record actions, reports, exit), Edit, Orders, Administration (login and the six maintenance forms), Utilities (VFP debugging windows and reindex), and Help. It replaces the VFP system menu for the life of the application.

**Used by:**
- `tastrade.Do` in [[../05-classes/main.md]]: `DO (this.cMainMenu)` with `cmainmenu = MAIN.MPR` inherited from `application` in [[../05-classes/tsgen.md]], right after `Init` has shown the intro form and logged the user in.
- The Login bar's own procedure, through `oApp.DoMenu()`, whenever a re-login changes the user level: the menu is defined again and its cleanup code re-applies the privilege gating.

**Related docs:** [[../05-classes/tsgen.md]] (`application`: `Init` pushes the system menu, `Cleanup2` pops it), [[../05-classes/main.md]], [[../05-classes/tsbase.md]] (`tstoolbar`, whose buttons the File bars click), [[../08-programs/utility.md]] (`FormIsObject()`, `ToolBarEnabled()`), [[navigate.md]], [[ordentry.md]], [[window.md]], [[intro.md]], [[README.md]].

This is the primary navigation. `application.Init` does `PUSH MENU _MSYSMENU` before any menu runs and `Cleanup2` does `POP MENU _MSYSMENU TO MASTER`, so the VFP menu comes back when the application ends. Between those, this menu is defined with location `REPLACE`, which the 2001 `.mpr` renders as `SET SYSMENU TO` and `SET SYSMENU AUTOMATIC`.

## Menu structure

Menu type 1, location `REPLACE`.

### Pad: File  (`Pad`)

hot key ALT+F; status text "Create, save, delete, and restore records, close forms, print reports, or quit Tastrade"; popup `File`.

Every record action calls the corresponding button of the shared navigation toolbar ([[../05-classes/tsbase.md]] `tstoolbar`) and is skipped unless a form is active and that button is enabled, so the menu is a keyboard front for the toolbar. Delete is the exception: it calls the form's `delete` method directly and checks the form's `lAllowDelete`.

| Bar | Prompt | Shortcut | Skip For | Action |
|---|---|---|---|---|
| `1` | New | Ctrl+N | `!FormIsObject() OR !ToolBarEnabled("cmdNew")` | `oApp.oToolbar.cmdNew.Click()` |
| `2` | Close |  | `!FormIsObject() OR !ToolBarEnabled("cmdClose")` | `oApp.oToolbar.cmdClose.Click()` |
| `3` | (separator) |  |  | empty cascading popup `_qx713oqj4` in the twin only |
| `4` | Save | Ctrl+S | `!FormIsObject()  OR !ToolBarEnabled("cmdSave")` | `oApp.oToolbar.cmdSave.Click()` |
| `5` | Restore | Ctrl+E | `!FormIsObject()  OR !ToolBarEnabled("cmdRestore")` | `oApp.oToolbar.cmdRestore.Click()` |
| `6` | Delete |  | `!FormIsObject()  OR TYPE("oApp.oToolBar") # "O" OR !_screen.activeform.lAllowDelete` | `_screen.activeform.delete()` |
| `7` | (separator) |  |  | empty cascading popup `_qx713bhn6` in the twin only |
| `8` | Print Reports ... | Ctrl+P |  | `DO FORM Reports` |
| `9` | Print Setup |  |  | `DO BAR_9_OF_File_FB2P` |
| `10` | (separator) |  |  | empty cascading popup `_qx713bhn7` in the twin only |
| `11` | Return to Visual FoxPro |  |  | `DO BAR_11_OF_File_FB2P` |

### Pad: Edit  (`Edit`)

hot key ALT+E; status text "Edits text or current selection"; popup `Edit`.

Every bar is a VFP system bar (`_med_*`), so undo, cut, copy, paste, and select-all are VFP's own with no code in the sample.

| Bar | Prompt | Shortcut | Skip For | Action |
|---|---|---|---|---|
| `_med_undo` | Undo | Ctrl+Z |  | VFP system bar |
| `_med_redo` | Redo | Ctrl+R |  | VFP system bar |
| `3` | (separator) |  |  |  |
| `_med_cut` | Cut | Ctrl+X |  | VFP system bar |
| `_med_copy` | Copy | Ctrl+C |  | VFP system bar |
| `_med_paste` | Paste | Ctrl+V |  | VFP system bar |
| `7` | (separator) |  |  |  |
| `_med_slcta` | Select All | Ctrl+A |  | VFP system bar |

### Pad: Orders  (`Orders`)

hot key ALT+O; status text "Access to Order Entry and Order History forms"; popup `_qx713dax1`.

Order Entry is single-instance (`WEXIST` of the form's name); Order History has no skip condition and opens as many instances as asked, see [[../04-forms/ordhist.md]].

| Bar | Prompt | Shortcut | Skip For | Action |
|---|---|---|---|---|
| `1` | Order Entry |  | `WEXIST("frmOrderEntry")` | `oApp.DoForm("ordentry")` |
| `2` | Order History |  |  | `oApp.DoForm("ordhist")` |

### Pad: Administration  (`_msm_file`)

hot key ALT+A; status text "Login, change password, and access to all maintenance forms"; popup `_qx713dsus`; designer comment `*- pad is named _msm_file to simplify positioning Navigation menu`.

The pad is named `_msm_file`, the VFP system name for the File pad, so that the Navigation and Window pads, which the designer placed `AFTER _MFILE`, land after Administration ([[navigate.md]], [[window.md]]). Login and Change Password are skipped while any window is on top; each maintenance form is single-instance by `WEXIST` of its class name.

| Bar | Prompt | Shortcut | Skip For | Action |
|---|---|---|---|---|
| `1` | Login |  | `!EMPTY(WONTOP())` | `DO BAR_1_OF__qx713dsus_FB2P` |
| `2` | Change Password |  | `!EMPTY(WONTOP())` | `DO FORM chngpswd` |
| `3` | (separator) |  |  | empty cascading popup `_qx713j5wk` in the twin only |
| `4` | Customers |  | `WEXIST("frmCustomers")` | `oApp.DoForm("customer")` |
| `5` | Categories |  | `WEXIST("frmCategory")` | `oApp.DoForm("category")` |
| `6` | Employees |  | `WEXIST("frmEmployee")` | `oApp.DoForm("employee")` |
| `7` | Shippers |  | `WEXIST("frmShippers")` | `oApp.DoForm("shipper")` |
| `8` | Suppliers |  | `WEXIST("frmSuppliers")` | `oApp.DoForm("supplier")` |
| `9` | Products |  | `WEXIST("frmProducts")` | `oApp.DoForm("product")` |
| `10` | (separator) |  |  |  |
| `11` | Behind the Scenes |  | `WEXIST("frmBehindSC")` | `oApp.DoForm("behindsc")` |

### Pad: Utilities  (`Utilities`)

hot key ALT+U; status text "Trace, debug, and view windows, suspend, resume, and cancel programs"; popup `Utilities`.

Trace, Debug, View, Command, Resume, and Cancel are VFP system bars (`_MWI_*`, `_MPR_*`); Suspend runs the `SUSPEND` command. The whole pad is meant for developers only: the cleanup code below removes it for every other user level.

| Bar | Prompt | Shortcut | Skip For | Action |
|---|---|---|---|---|
| `_MWI_TRACE` | Trace |  |  | VFP system bar |
| `_MWI_DEBUG` | Debug |  |  | VFP system bar |
| `_MWI_VIEW` | View |  |  | VFP system bar |
| `_MWI_CMD` | Command | Ctrl+F2 |  | VFP system bar |
| `5` | (separator) |  |  |  |
| `6` | Suspend |  |  | `suspend` |
| `_MPR_RESUM` | Resume |  |  | VFP system bar |
| `_MPR_CANCL` | Cancel |  |  | VFP system bar |
| `9` | (separator) |  |  |  |
| `10` | Rebuild DBC/Reindex |  | `!EMPTY(WONTOP())` | `DO FORM rebuild` |

### Pad: Help  (`_msm_systm`)

hot key ALT+H; status text "Displays help on Tastrade"; popup `Help`.

The pad is named `_msm_systm`, VFP's system Help pad, and Contents / Search are the system bars `_mst_help` / `_mst_hpsch`, so they open the help file that `environment.Set` selects with `SET HELP TO HELP\TASTRADE.CHM` ([[../05-classes/tsgen.md]]).

| Bar | Prompt | Shortcut | Skip For | Action |
|---|---|---|---|---|
| `_mst_help` | Contents |  |  | VFP system bar |
| `_mst_hpsch` | Search for Help on... |  |  | VFP system bar |
| `3` | (separator) |  |  | empty cascading popup `_qvj0k3u8p` in the twin only |
| `4` | About Tasmanian Traders... |  |  | `DO BAR_4_OF_Help_FB2P` |

Menu-level handler: `ON SELECTION MENU _MSYSMENU *-- (c) Microsoft Corporation 1995` (a comment, so a no-op; the same line closes every menu in the sample).

## Setup / cleanup code

Setup code:

```foxpro
#INCLUDE "INCLUDE\TASTRADE.H"
```

The include file supplies `USER_APPDEV_LOC`, `USER_OPSMGR_LOC`, `ADMINBAR_LOC` (from `include/tastrade.h`) and the About box strings (from `include/strings.h`).

Procedure `BAR_9_OF_File_FB2P`:

Print Setup: VFP's page setup dialog, `SYS(1037)`, with every error suppressed by `ON ERROR *` and the previous handler restored by macro. **NOTE:** `&lcOldError` macro substitution.

```foxpro
LOCAL lcOldError
lcOldError = ON('ERROR')
ON ERROR *
=SYS(1037)
ON ERROR &lcOldError
```

Procedure `BAR_11_OF_File_FB2P`:

Return to Visual FoxPro: `CLEAR EVENTS` ends the `READ EVENTS` loop in `application.Do`, whose next lines call `Cleanup` and `Cleanup2`.

```foxpro
*- cleanup will be done in the oApp object's Do method
CLEAR EVENTS
```

Procedure `BAR_1_OF__qx713dsus_FB2P`:

Login: runs the login dialog again through `oApp.Login()` ([[../05-classes/main.md]], which shows `loginpicture` from [[../05-classes/login.md]]) and, if the user level changed, re-runs this whole menu so the cleanup code can re-apply the gating.

```foxpro
LOCAL lcUserLevel

lcUserLevel = oApp.GetUserLevel()
=oApp.Login()

IF oApp.GetUserLevel() <> lcUserLevel
  oApp.DoMenu()
ENDIF
```

Procedure `BAR_4_OF_Help_FB2P`:

About: loads `about.vcx`, builds the box from the `_LOC` constants ("Tasmanian Traders", "1.1", "Copyright 1996 Microsoft Corporation", "All rights reserved") and `BITMAPS\TTRADESM.BMP`, then releases the library ([[../05-classes/about.md]]).

```foxpro
LOCAL loAboutBox


SET CLASSLIB TO about ADDITIVE
loAboutBox = CREATEOBJECT("AboutBox", ;
              TASTRADE_LOC, ;
*-- ... 7 more lines of Microsoft's Tastrade source omitted; see `Setup / cleanup code` in your own copy of Tastrade.
```

Cleanup code (runs after the definitions):

This is the application's only privilege gating. Non-developers lose the Utilities pad. Users below Operations Manager are meant to lose Login, Change Password, and the separator. **NOTE:** `ADMINBAR_LOC` is `"Administration"`, but the Administration popup was never named in the designer and is `_qx713dsus` in both this twin and the 2001 `.mpr`, so the three `RELEASE BAR` lines address a popup that does not exist; they error or do nothing, and either way the bars stay. **NOTE:** under `DEBUGMODE` ([[../05-classes/main.md]] `Init` sets the level to Applications Developer without a login) neither branch runs, so the shipped build shows every user the Utilities pad, including the Command window (Ctrl+F2), Debug, Trace, Suspend, and Cancel.

```foxpro
*-RELEASE BAR 1 OF Window

IF UPPER(oApp.GetUserLevel()) <> USER_APPDEV_LOC
  RELEASE PAD Utilities OF _MSYSMENU
ENDIF

*-- ... 5 more lines of Microsoft's Tastrade source omitted; see `Setup / cleanup code` in your own copy of Tastrade.
```

## What it launches

- Print Reports: `DO FORM Reports`, [[../04-forms/reports.md]] (the only route to the ten picker reports in [[../06-reports/README.md]]).
- Order Entry / Order History: [[../04-forms/ordentry.md]], [[../04-forms/ordhist.md]].
- Change Password: [[../04-forms/chngpswd.md]]. Login: [[../05-classes/login.md]] via `oApp.Login()`.
- Customers, Categories, Employees, Shippers, Suppliers, Products: [[../04-forms/customer.md]], [[../04-forms/category.md]], [[../04-forms/employee.md]], [[../04-forms/shipper.md]], [[../04-forms/supplier.md]], [[../04-forms/product.md]], all through `oApp.DoForm`.
- Behind the Scenes: [[../04-forms/behindsc.md]] (`oApp.DoForm("behindsc")`, without the `.T.` parameter the intro form passes).
- Rebuild DBC/Reindex: [[../04-forms/rebuild.md]].
- About: [[../05-classes/about.md]]. Help Contents / Search: `help/tastrade.chm` through VFP's system bars.

## Notes

- **Twin versus `.mpr`.** The twin is FoxBin2PRG's rendering of the `.mnx`; `menus/main.mpr` is GENMENU's output dated 10/12/00. They match statement for statement apart from formatting, the generated procedure names (`_07y0s8...` there, `BAR_n_OF_popup_FB2P` here), the `SET SYSMENU` pair that the `REPLACE` location generates, and the empty cascading popup the twin emits for each separator, which the `.mpr` does not have.
- **Daily use versus administration.** File, Edit, Orders, and the maintenance half of Administration are the working menu; Login, Change Password, Utilities, and Rebuild are administrative and are the only items the cleanup code gates.
- **Keyboard map.** Pads Alt+F/E/O/A/U/H; New Ctrl+N, Save Ctrl+S, Restore Ctrl+E, Print Reports Ctrl+P; Edit Ctrl+Z/R/X/C/V/A; Command window Ctrl+F2. First/Prior/Next/Last shortcuts live in [[navigate.md]].
- **Status-bar text** for every pad and bar is in the `MESSAGE` clauses above; there are no `_LOC` constants for prompts or messages, so the menu is not localized the way the forms' strings are.
- **`*-RELEASE BAR 1 OF Window`** at the top of the cleanup code is a commented-out remnant of the placeholder trick now done in [[window.md]].
- **The copyright line is the menu's `ON SELECTION MENU` command**: `ON SELECTION MENU _MSYSMENU *-- (c) Microsoft Corporation 1995`. Because the command is a comment it does nothing; it is where the sample keeps its copyright notice in every menu.
- **Behind the Scenes lives under Administration** and is gated by nothing, unlike Utilities.
