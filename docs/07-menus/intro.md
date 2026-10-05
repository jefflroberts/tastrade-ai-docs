# Intro menu (intro.mnx)

| Source file | Type | Path |
|---|---|---|
| `intro.mnx` | Menu | `menus/intro.mn2` |

**Purpose:** The two-pad menu (File: Return to Visual FoxPro; Help) shown while the intro screen is up, before login.

**Used by:**
- `tastrade.Init` in [[../05-classes/main.md]]: `DO menus\intro.mpr` right after `application.Init` succeeds and before the intro form ([[../05-classes/tsgen.md]] `introform`) is shown. It runs whether or not the INI setting `ShowIntroForm` suppresses the form; `tastrade.Do` then replaces it with [[main.md]].

**Related docs:** [[../05-classes/tsgen.md]] (`introform`, whose `close` method the File bar calls), [[../05-classes/main.md]], [[../05-classes/about.md]], [[main.md]], [[README.md]].

## Menu structure

Menu type 1, location `REPLACE`.

### Pad: File  (`Pad`)

hot key ALT+F; popup `File`.

Return to Visual FoxPro calls `_screen.activeform.Close()`; `introform.close` is `thisform.cmdExit.Click()`, so it is the same as the intro form's Exit button. The popup-level handler below is dead: a bar with its own `ON SELECTION BAR` is not passed to `ON SELECTION POPUP`.

Popup-level handler: `ON SELECTION POPUP File DO File_FB2P`.

| Bar | Prompt | Shortcut | Skip For | Action |
|---|---|---|---|---|
| `1` | Return to Visual FoxPro |  |  | `_screen.activeform.Close()` |

### Pad: Help  (`Help`)

hot key ALT+H; popup `Help`.

Contents has F1 here (the main menu's does not). Contents and Search are VFP system bars.

| Bar | Prompt | Shortcut | Skip For | Action |
|---|---|---|---|---|
| `_mst_help` | Contents | F1 |  | VFP system bar |
| `_mst_hpsch` | Search for Help on... |  |  | VFP system bar |
| `3` | (separator) |  |  | empty cascading popup `_qvj0k3u8p` in the twin only |
| `4` | About Tasmanian Traders... |  |  | `DO BAR_4_OF_Help_FB2P` |

Menu-level handler: `ON SELECTION MENU _MSYSMENU *-- (c) Microsoft Corporation 1995` (a comment, so a no-op; the same line closes every menu in the sample).

## Setup / cleanup code

No setup code.

Procedure `File_FB2P`:

A generic dispatcher that calls a method of the active form named after the bar's prompt (`Prompt()`), with a special case renaming "New" to `AddNew`. Nothing reaches it: the only bar has its own handler. The comment records a VFP bug from the sample's first release that forced the `AddNew` rename, and the code shows this menu once had record-action bars like the main menu's. **NOTE:** `&lcCmd` macro substitution.

```foxpro
LOCAL lcCmd
lcCmd = Prompt()

*? There was a bug with adding a method called "New" to a form,
*? so we were forced to change it to AddNew at the last minute. 
IF UPPER(lcCmd) = "NEW"
*-- ... 5 more lines of Microsoft's Tastrade source omitted; see `Setup / cleanup code` in your own copy of Tastrade.
```

Procedure `BAR_4_OF_Help_FB2P`:

**NOTE:** a second About box with different facts from the main menu's: version "1.0" and "Copyright 1994 Microsoft Corporation" hard-coded here against `VERSION_LOC` "1.1" and `COPYRIGHT_LOC` "Copyright 1996 Microsoft Corporation" there, and the logo `BITMAPS\SMSWIRLT.BMP`, which is not in `bitmaps/` (the main menu uses `TTRADESM.BMP`, which is). `about.vcx` is loaded by path here and by name there. There is no setup code, so no include file could have supplied the constants.

```foxpro
LOCAL loAboutBox

SET CLASSLIB TO libs\about.vcx ADDITIVE
loAboutBox = CREATEOBJECT("AboutBox", ;
              "Tasmanian Traders", ;
              "1.0", ;
*-- ... 6 more lines of Microsoft's Tastrade source omitted; see `Setup / cleanup code` in your own copy of Tastrade.
```

No cleanup code.

## What it launches

- Return to Visual FoxPro: `introform.close` → `cmdExit.Click` ([[../05-classes/tsgen.md]]).
- About: [[../05-classes/about.md]] with the 1994 strings. Help: `help/tastrade.chm` through the system bars, once `environment.Set` has run.

## Notes

- **Twin versus `.mpr`.** The twin is FoxBin2PRG's rendering of the `.mnx`; `menus/intro.mpr` is GENMENU's output dated 10/12/00. They match statement for statement apart from formatting, the generated procedure names (`_07y0s8...` there, `BAR_n_OF_popup_FB2P` here), the `SET SYSMENU` pair that the `REPLACE` location generates, and the empty cascading popup the twin emits for each separator, which the `.mpr` does not have.
- **Nothing here is gated**; the user has not logged in yet.
- **The copyright line is the menu's `ON SELECTION MENU` command**, as in every menu of the sample.
