# Programs and include files

Two programs in `progs/` and two include files in `include/`, all native VFP text read directly (no twin, no parser); routine, declaration, and `#DEFINE` counts were checked against a raw grep, and every constant's users were found with a case-sensitive whole-word grep over the twins, the `.mpr` files, the programs, and the DBC twin.

| File | Role | Doc |
|---|---|---|
| `progs/main.prg` | Runtime entry point (project main file): API declarations, environment save, `SetPath()`, `CREATEOBJECT("TasTrade")`, `oApp.Do()`, cleanup | [[main.md]] |
| `progs/utility.prg` | Runtime library (`SET PROCEDURE`): `IsTag`, `NotYet` (dead), `FileSize`, `FormIsObject`, `ToolBarEnabled`, `OnShutdown` | [[utility.md]] |
| `include/tastrade.h` | Main include file: `FOXPRO.H` + `STRINGS.H`, `DEBUGMODE`, INI name, status and trigger codes, registry keys, user-level names | [[tastrade.h.md]] |
| `include/strings.h` | Localizable strings, 86 `_LOC` constants | [[strings.h.md]] |

## Startup sequence

`tastrade.exe` → `progs/main.prg` → `SetPath()` → `CREATEOBJECT("TasTrade")` ([[../05-classes/main.md]]) → `application.Init` (adds `environment`, whose `Set` loads `utility.prg`, the five class libraries, and the help file; opens the DBC; hides VFP's toolbars; pushes the system menu) → `tastrade.Init` (intro menu, intro form, login or the `DEBUGMODE` bypass) → `oApp.Do()` (main menu, optional startup action, `READ EVENTS`) → Return to Visual FoxPro (`CLEAR EVENTS`) → `Cleanup`, `Cleanup2` → back in `main.prg`: `CLEAR DLLS`, `RELEASE ALL EXTENDED`, `CLEAR ALL` → `environment.Destroy` restores every setting. The full picture with the menus is in [[../07-menus/README.md]]; the architecture page will draw it.

## Include chain

`FOXPRO.H` (VFP's) → `strings.h` → `tastrade.h` → every form, class library, code-bearing menu, program, the stored procedures, and one of the two reports with data environment code. The other report, `listempl.frx`, forgot it ([[../06-reports/listempl.md]]). `DEBUGMODE` is compiled into all of them, so changing it is a full rebuild.

## Findings

- **`DEBUGMODE = .T.` is compiled in at five sites** and shipped on: no login, no startup action, developer user level for everyone, `SET ESCAPE ON`, and `SUSPEND` on Abort. The dead delete guard, the wrong-record Change Password, and the missing menu gating all follow from the second site.
- **13 constants are defined and never used** (6 in `tastrade.h`, 7 in `strings.h`), and one function, `NotYet()`, is called by nothing.
- **Localizable strings are split across two files**, and the menus' text is in neither.
- **The environment hides VFP's toolbars by their English window titles**, a dependency on the IDE's language, not the application's.
- **`main.prg` declares six Win32 API functions for the classes** (INI read/write for the intro flag and window positions; three registry calls and a `win.ini` lookup for the About box) and calls none itself.
- **`main.prg` hides the Project Manager window while the reports assume it is closed**; the two disagree on the same window.
- One typo ("maximimun"), one duplicated message, one leaked private variable, one old-style `PARAMETER`.
