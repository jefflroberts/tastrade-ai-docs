# tastrade.h

| Source file | Type | Path |
|---|---|---|
| `tastrade.h` | Include file | `include/tastrade.h` |

**Purpose:** The application's main include file: pulls in VFP's `FOXPRO.H` and the localizable strings of [[strings.h.md]], then defines the `DEBUGMODE` switch, the INI file name, whitespace constants, the record-status and trigger codes the base form uses, registry keys for the About box, the user-level names the menu gates on, and a few strings.

**Used by:**
- Every form (`#INCLUDE "..\include\tastrade.h"` in all 17 `.sc2`), every class library (in 5 of 6; `orders.vc2` once, `tsbase.vc2` and `tsgen.vc2` several times because each class carries its own line), the three menus with code ([[../07-menus/main.md]], [[../07-menus/navigate.md]], [[../07-menus/window.md]]), both programs ([[main.md]], [[utility.md]]), the DBC's stored procedures ([[../03-data-model/README.md]], `#INCLUDE INCLUDE\TASTRADE.H`), and one report data environment ([[../06-reports/orders.md]]; [[../06-reports/listempl.md]] lacks it and errors for it).
- The project (`tastrade.pj2`) lists it as a text file, excluded from the build, described as "The main include file for this application".

**Related docs:** [[strings.h.md]], [[main.md]], [[utility.md]], [[../05-classes/tsgen.md]] (`environment.Set`, the `DEBUGMODE` site that matters most), [[../05-classes/main.md]], [[../05-classes/tsbase.md]], [[../07-menus/main.md]] (`ADMINBAR_LOC`, `USER_*_LOC`), [[README.md]].

## Role

**Runtime constants, compiled into every artifact that includes it.** Not a program; nothing runs. The `Used by` column below is a case-sensitive whole-word grep over every twin, `.mpr`, `.prg`, and the DBC twin; 6 of the 34 constants have no user.

## Includes

```foxpro
#INCLUDE "FOXPRO.H"
#INCLUDE "STRINGS.H"
```

`FOXPRO.H` is VFP's own header (the `MB_*` message-box constants, `IDYES`/`IDABORT`, `COLOR_*`, and the rest), resolved from the VFP home directory at compile time. `STRINGS.H` is [[strings.h.md]], resolved relative to this file. Three spellings of the path to this file exist in the sources: `..\include\tastrade.h` in forms and classes, `INCLUDE\TASTRADE.H` in programs, menus, and the invoice report, and `INCLUDE\TASTRADE.H` unquoted in the stored procedures.

## Constants

| Constant | Value | Comment | Used by |
|---|---|---|---|
| `DEBUGMODE` | `.T.` |  | `main.vc2` (2), `tsbase.vc2` (2), `tsgen.vc2` |
| `INIFILE` | `"TASTRADE.INI"` |  | `main.vc2`, `tsbase.vc2` (4), `tsgen.vc2` |
| `CRLF` | `CHR(13) + CHR(10)` |  | `behindsc.sc2` (8) |
| `CR` | `CHR(13)` |  | `tsbase.vc2` (2), `tastrade.dc2` (2) |
| `TAB` | `CHR(9)` |  | `behindsc.sc2` (6) |
| `CURRENCY` | `"$"` |  | **unused** |
| `AERRORARRAY` | `7` |  | `category.sc2`, `employee.sc2`, `product.sc2`, `shipper.sc2`, `supplier.sc2`, `orders.vc2`, `tsbase.vc2` (2), `tsgen.vc2` |
| `FILE_OK` | `0` |  | `tsbase.vc2` (4) |
| `FILE_BOF` | `1` |  | `tsbase.vc2` (5) |
| `FILE_EOF` | `2` |  | `tsbase.vc2` (6) |
| `FILE_CANCEL` | `3` |  | `tsbase.vc2` (12) |
| `INSERTTRIG` | `1` |  | `employee.sc2`, `ordentry.sc2`, `product.sc2`, `tsbase.vc2` |
| `UPDATETRIG` | `2` |  | `tsbase.vc2` |
| `DELETETRIG` | `3` |  | `category.sc2`, `customer.sc2`, `employee.sc2`, `product.sc2`, `shipper.sc2`, `supplier.sc2`, `tsbase.vc2` (2) |
| `HKEY_LOCAL_MACHINE` | `-2147483646` |  | `about.vc2` (2) |
| `KEY_SHARED_TOOLS_LOCATION` | `"Software\Microsoft\Shared Tools"` |  | `about.vc2` |
| `KEY_NTCURRENTVERSION` | `"Software\Microsoft\Windows NT\CurrentVersion"` |  | `about.vc2` |
| `KEY_WIN4CURRENTVERSION` | `"Software\Microsoft\Windows\CurrentVersion"` |  | `about.vc2` |
| `KEY_WIN4_MSINFO` | `"Software\Microsoft\Shared Tools\MSInfo"` |  | **unused** |
| `KEY_QUERY_VALUE` | `1` |  | `about.vc2` (2) |
| `ERROR_SUCCESS` | `0` |  | `about.vc2` (5) |
| `ADMINBAR_LOC` | `"Administration"` |  | `main.mn2` (3), `main.mpr` (3) |
| `ALL_LOC` | `"All"` |  | `behindsc.sc2` |
| `USER_APPDEV_LOC` | `"APPLICATIONS DEVELOPER"` |  | `main.vc2`, `main.mn2` (2), `main.mpr` (2) |
| `USER_OPSMGR_LOC` | `"OPERATIONS MANAGER"` |  | `main.mn2`, `main.mpr` |
| `DOLLAR_FORMAT1_LOC` | `": $"` |  | **unused** |
| `DOLLAR_FORMAT2_LOC` | `""` |  | `tastrade.dc2` (2) |
| `DOLLAR_FORMAT3_LOC` | `"$"` |  | `tastrade.dc2` (2) |
| `SEEKVALUE_LOC` | `"*Case Study"` |  | `casestdy.sc2` |
| `SYS2011_EXCLUSIVE_LOC` | `"EXCLUSIVE"` |  | **unused** |
| `SYS2011_RECLOCK_LOC` | `"RECORD LOCKED"` |  | **unused** |
| `SYS2011_RECUNLOCK_LOC` | `"RECORD UNLOCKED"` |  | **unused** |
| `I_SHPMIN` | `111` | how far left can the Behind the Scenes splitter go? | `tsgen.vc2` |
| `I_SHPMAX` | `303` | how far right can the Behind the Scenes splitter go? | `tsgen.vc2` |

## `DEBUGMODE`

Shipped as `.T.`. Five `#IF`-style sites read it (`IF DEBUGMODE` / `IF !DEBUGMODE`; the value is compiled in, so flipping it means rebuilding everything that includes this file):

1. `tastrade.Do` ([[../05-classes/main.md]]): `IF !DEBUGMODE` around the startup action from `user_level.startup_action`, so the Customer Service Rep's automatic order entry form never opens.
2. `tastrade.Init` ([[../05-classes/main.md]]): `IF !DEBUGMODE` around `this.Login()`; the debug branch sets `cEmployeeID` to empty and `cUserLevel` to `USER_APPDEV_LOC`. Consequences: no login, an empty employee ID that defeats the delete guard in [[../04-forms/employee.md]] and puts [[../04-forms/chngpswd.md]] on the first record, and the developer level that keeps every menu pad ([[../07-menus/main.md]]).
3. `tsbaseform.Error` ([[../05-classes/tsbase.md]]), twice: a `WAIT WINDOW` when a table rule fails (error 1583), and `SUSPEND` instead of `oApp.Cleanup` / `CANCEL` when the user picks Abort on an unhandled error.
4. `environment.Set` ([[../05-classes/tsgen.md]]): `SET ESCAPE ON` instead of `OFF`, so Esc interrupts running code.

There is no `#IF DEBUGMODE` anywhere: the switch is always evaluated at run time from a compiled-in literal.

## Notes

- **Unused constants:** `CURRENCY`, `KEY_WIN4_MSINFO`, `DOLLAR_FORMAT1_LOC`, `SYS2011_EXCLUSIVE_LOC`, `SYS2011_RECLOCK_LOC`, `SYS2011_RECUNLOCK_LOC`. `CURRENCY` and the `SYS2011_*` lock-status strings look like abandoned features; `KEY_WIN4_MSINFO` is a registry path the About box never reads (it reads `KEY_SHARED_TOOLS_LOCATION`, `KEY_NTCURRENTVERSION`, and `KEY_WIN4CURRENTVERSION`); `DOLLAR_FORMAT1_LOC` is the odd one out of three.
- **Localizable strings in the wrong file.** `ADMINBAR_LOC`, `ALL_LOC`, `USER_APPDEV_LOC`, `USER_OPSMGR_LOC`, `DOLLAR_FORMAT*_LOC`, `SEEKVALUE_LOC`, and the `SYS2011_*_LOC` names carry the `_LOC` suffix that marks translatable text, but live here rather than in [[strings.h.md]], whose header says it is the file to localize.
- **`USER_APPDEV_LOC` and `USER_OPSMGR_LOC` must match `user_level.description` upper-cased** ([[../03-data-model/tables/user_level.md]]: "Applications Developer", "Operations Manager"); the menu compares `UPPER(oApp.GetUserLevel())` against them. Translating the strings without changing the data, or the reverse, silently removes the gating.
- **`ADMINBAR_LOC` names a popup that does not exist** (the Administration popup is `_qx713dsus`), see [[../07-menus/main.md]].
- **`SEEKVALUE_LOC` (`"*Case Study"`) duplicates the filter literal** stored in `reports/casestdy.frx`'s cursor ([[../06-reports/casestdy.md]]); the form uses the constant, the report the literal.
- **`HKEY_LOCAL_MACHINE` as `-2147483646`** is `0x80000002` written as a signed 32-bit integer, which is what the `RegOpenKeyEx` declaration in [[main.md]] takes.
- **`I_SHPMIN` / `I_SHPMAX`** are the pixel limits of the Behind the Scenes splitter ([[../05-classes/tsgen.md]] `splitter`); layout numbers in an include file.
- **`AERRORARRAY 7`** is the column count of `AERROR()`'s array, used to `DIMENSION` it before the call in eight places.
