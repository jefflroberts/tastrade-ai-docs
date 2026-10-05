# Menus

Five menus in `menus/*.mnx`, all documented from their FoxBin2PRG twins with every pad, bar, shortcut, `SKIP FOR` condition, action, procedure, and the setup and cleanup code. `foxparse.py` gained a `.mn2` parser for this step; its pad, bar, popup, and procedure counts match a raw grep of every twin, and the three 2001 `.mpr` programs match their twins statement for statement.

| File | Title | Pads | Location | Run by | `.mpr` in repo | Doc |
|---|---|---|---|---|---|---|
| `menus/main.mnx` | Main menu | File, Edit, Orders, Administration, Utilities, Help | `REPLACE` | `tastrade.Do`; again from the Login bar | yes | [[main.md]] |
| `menus/intro.mnx` | Intro menu | File, Help | `REPLACE` | `tastrade.Init`, before the intro form | yes | [[intro.md]] |
| `menus/navigate.mnx` | Navigation menu | Navigation (`_msm_edit`) | `AFTER _MFILE` | `application.ShowNavToolBar`, first form | no | [[navigate.md]] |
| `menus/ordentry.mnx` | Items menu | Items | `AFTER _MEDIT` | `frmorderentry.Activate`, every activation | yes | [[ordentry.md]] |
| `menus/window.mnx` | Window menu | Window (empty) | `AFTER _MFILE` | `tsbaseform.AddToMenu`, first form | no | [[window.md]] |

## Lifecycle

`application.Init` ([[../05-classes/tsgen.md]]) pushes the VFP system menu. `tastrade.Init` runs the intro menu and shows the intro form; `tastrade.Do` replaces it with the main menu and starts `READ EVENTS`. The first framework form to open adds the Window pad and then the Navigation pad; the order entry form adds and removes the Items pad on every activation; the last form to close removes Navigation and Window. Return to Visual FoxPro does `CLEAR EVENTS`, and `Cleanup2` pops the system menu back. Re-logging in as a different user level re-runs the main menu so its cleanup code can re-apply the gating.

## Placement by system names

Three pads reuse VFP system pad names as a placement trick, and the designer comments in the twins say so: Administration is `_msm_file` so that Navigation and Window (`AFTER _MFILE`) land after it; Navigation is `_msm_edit` so that Items (`AFTER _MEDIT`) lands after it; Help is `_msm_systm` so its system bars open the help file. A rebuilder should not look for File or Edit commands behind those names. The resulting bar order, by the sequence of the code, is File, Edit, Orders, Administration, Navigation, [Items], Window, Utilities, Help; not run here.

## Findings

- **Privilege gating is four lines of cleanup code in the main menu, and half of it misses.** Non-developers lose the Utilities pad; the lines meant to remove Login and Change Password for lower levels address a popup named `Administration` that does not exist (the popup is `_qx713dsus`), so those bars stay for everyone. Under `DEBUGMODE` none of it runs and every user gets the Utilities pad with the Command window.
- **Two About boxes.** The intro menu hard-codes version 1.0, a 1994 copyright, and a bitmap that is not in the repo; the main menu uses the include-file constants (1.1, 1996) and a bitmap that is.
- **The menus are keyboard fronts for the toolbar.** File and Navigation bars call toolbar button `Click` methods and mirror their `Enabled` state in `SKIP FOR`; only Delete, Print Setup, Login, About, and the form launches have code of their own.
- **Two menus have no `.mpr`** (`navigate`, `window`); the build generated them and the EXE contains their strings. The three that do have `.mpr` files date them to October 2000.
- **The copyright notice is stored as each menu's `ON SELECTION MENU` command**, a comment that does nothing.
- **Dead code in the intro menu**: a popup-level dispatcher with a `New`-to-`AddNew` workaround for a VFP bug, unreachable because the only bar has its own handler.
- **FoxBin2PRG emits an empty cascading popup for every separator bar** (five in `main`, one in `intro`); the `.mpr` files have none. Twin artifact, not source.
- Menu prompts and status messages are plain English in the `.mnx`, not `_LOC` constants; the forms' strings are localized through `strings.h`, the menus' are not.
