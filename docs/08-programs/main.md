# main.prg

| Source file | Type | Path |
|---|---|---|
| `main.prg` | Program | `progs/main.prg` |

**Purpose:** The application's entry point: declares the Win32 API functions the framework uses, saves the environment it is about to change, sets the path and class libraries, creates the `tastrade` application object, runs it, and cleans up.

**Used by:**
- The project's main file: `tastrade.pj2` has `.SetMain(lcCurdir + 'progs\main.prg')`, so `tastrade.exe` starts here. Nothing else calls it; running `progs\main.prg` from the IDE is the other way in, and `SetPath()` allows for it.

**Related docs:** [[../05-classes/main.md]] (`tastrade`, the object this program creates), [[../05-classes/tsgen.md]] (`application.Init`/`Do`, and `environment`, which consumes the globals saved here), [[../05-classes/login.md]], [[tastrade.h.md]] (the include file), [[utility.md]] (loaded by `environment.Set`), [[../07-menus/README.md]] (the menus `Do` runs), [[README.md]].

## Role

**Runtime entry point.** It is the project's main program and the only `.prg` on the call graph besides the procedure library. Nothing to flag for deletion.

## What it does

1. `#INCLUDE`s [[tastrade.h.md]] (which pulls in `FOXPRO.H` and [[strings.h.md]]); no constant from it is used in this file, but the project compiles it in.
2. Declares six Win32 API functions (table below). Declarations are process-wide in VFP, so this is where the INI and registry access used by the classes is wired up.
3. `CLEAR`s the screen and `DEACTIVATE WINDOW "Project Manager"` so a hot key sent with `KEYBOARD` cannot land in the IDE's project window.
4. Turns `SET TALK` off, remembering the old value, and saves `SET ESCAPE`, the current directory, `SET PATH`, and `SET CLASSLIB` into public `gcOld*` variables; sets the public flag `gTTrade` to `.T.`.
5. `SetPath()` changes directory to the application root and sets the search path and the two class libraries needed to instantiate the application object.
6. `CREATEOBJECT("TasTrade")`. `application.Init` copies the `gcOld*` values into its `environment` member and applies the application's own settings ([[../05-classes/tsgen.md]]); `tastrade.Init` then runs the intro menu, the intro form, and the login ([[../05-classes/main.md]]).
7. If the object came back, releases the five `gcOld*` variables (their values now live in `environment`) and calls `oApp.Do()`, which puts up the main menu and sits in `READ EVENTS` until Return to Visual FoxPro.
8. On the way out: `CLEAR DLLS`, `RELEASE ALL EXTENDED`, `CLEAR ALL`. Releasing `oApp` fires `application.Destroy`, and `environment.Destroy` restores every setting saved in step 4 and in `environment.Init`.

The top-level code, verbatim:

```foxpro
*-- (c) Microsoft Corporation 1995

#INCLUDE "INCLUDE\TASTRADE.H"

*-- DECLARE DLL statements for reading/writing to private INI files
DECLARE INTEGER GetPrivateProfileString IN Win32API  AS GetPrivStr ;
*-- ... 63 more lines of Microsoft's Tastrade source omitted; see `What it does` in your own copy of Tastrade.
```

## Key routines

#### `FUNCTION SetPath()`

Works out where the program is running from with `SYS(16)` (the running program's name with its path), takes the text from the drive letter on, and changes to that folder. Run as `MAIN.FXP` from `progs\`, it goes up one level so the relative folders in `SET PATH` resolve; run from the EXE, `SYS(16)` already names the root. Then it sets the search path over every application folder (`OTHER` holds only `notes.txt`, a placeholder) and the two class libraries that `CREATEOBJECT("TasTrade")` needs. It has no `RETURN`, so it returns VFP's default `.T.` and the `IF SetPath()` in the caller always passes.

```foxpro
FUNCTION SetPath()
  LOCAL lcSys16, ;
        lcProgram

  lcSys16 = SYS(16)
  lcProgram = SUBSTR(lcSys16, AT(":", lcSys16) - 1)
*-- ... 13 more lines of Microsoft's Tastrade source omitted; see `FUNCTION SetPath()` in your own copy of Tastrade.
```

## Inputs / outputs / side effects

**Win32 API declarations** (all `IN Win32API`):

| Declared as | Alias | Used by |
|---|---|---|
| `INTEGER GetPrivateProfileString(String cSection, String cKey, String cDefault, String @cBuffer, Integer nBufferSize, String cINIFile)` | `GetPrivStr` | [[../05-classes/main.md]] `tastrade.Init` reads `ShowIntroForm`; [[../05-classes/tsbase.md]] `tsbaseform.RestoreWindowPos` reads window positions |
| `INTEGER WritePrivateProfileString(String cSection, String cKey, String cValue, String cINIFile)` | `WritePrivStr` | [[../05-classes/tsgen.md]] `introform` writes `ShowIntroForm`; [[../05-classes/tsbase.md]] `tsbaseform.SaveWindowPos` writes window positions |
| `Integer RegOpenKeyEx(Integer nKey, String @cSubKey, Integer nReserved, Integer nAccessMask, Integer @nResult)` | `RegOpenKeyEx` | [[../05-classes/about.md]] `aboutbox` locates the System Info program |
| `Integer RegQueryValueEx(Integer nKey, String cValueName, Integer nReserved, Integer @nType, String @cBuffer, Integer @nBufferSize)` | `RegQueryValueEx` | [[../05-classes/about.md]] |
| `Integer RegCloseKey(Integer nKey)` | `RegCloseKey` | [[../05-classes/about.md]] |
| `INTEGER GetProfileString(String cSection, String cKey, String cDefault, String @cBuffer, Integer nBufferSize)` | `GetProStr` | [[../05-classes/about.md]] (Windows 3.1 `win.ini` lookup, the About box's fallback) |

`main.prg` itself calls none of them; it declares for the classes. `CLEAR DLLS` at the end drops all six.

**Public variables created here:**

| Variable | Value | Consumer |
|---|---|---|
| `gcOldTalk` | `'ON'` or `'OFF'` | `environment.Init` (`cOldTalk`), restored by `environment.Reset` |
| `gcOldEscape` | `SET('ESCAPE')` | same (`cOldEscape`) |
| `gcOldDir` | `FULLPATH(CURDIR())` | same (`cOldDir`); `Reset` does `CD` back to it |
| `gcOldPath` | `SET('PATH')` | same (`cOldPath`) |
| `gcOldClassLib` | `SET('CLASSLIB')` | same (`cOldClassLib`) |
| `gTTrade` | `.T.` | The guard `IF TYPE("m.gTTrade") # 'L' OR !m.gTTrade` in the `Init` of `application`, `environment`, `tastrade`, `tsbaseform`, `tstoolbar`, `login`, `aboutbox`, and others: nine sites across the libraries. It is never released by this program; `RELEASE ALL EXTENDED` at the end takes it. |
| `oApp` | the `tastrade` object | Every form, menu, and class; the application's only global object |

**Files and settings:** reads nothing itself; the INI file (`tastrade.ini`, `INIFILE` in [[tastrade.h.md]], one key `ShowIntroForm=1` in the repo copy) and the registry are touched by the classes through the declarations above. Changes the current directory, `SET TALK`, `SET PATH`, `SET CLASSLIB`; `environment.Set` then changes another fourteen settings and `ON SHUTDOWN` ([[../05-classes/tsgen.md]]), all restored on exit.

## Called from / calls

- **Called from:** the EXE (project main file), or `DO progs\main.prg` in the IDE.
- **Calls:** `SetPath()` (local), `CREATEOBJECT("TasTrade")` ([[../05-classes/main.md]]), `oApp.Do()`. Everything else in the application hangs off `Do`: the main menu ([[../07-menus/main.md]]), the forms, the reports.

## Notes

- **The comment about public variables is half true.** "All public vars will be released as soon as the application object is created" holds for the five `gcOld*` variables; `gTTrade` and `oApp` stay public for the life of the application, on purpose: `gTTrade` is what stops the classes being used outside Tastrade.
- **No error handler of its own.** `ON ERROR` is never set by this program or by `environment.Set`; form errors go to `tsbaseform.Error` ([[../05-classes/tsbase.md]]), and anything before `oApp` exists gets VFP's default error dialog.
- **`DEACTIVATE WINDOW "Project Manager"` hides the IDE's project window; it does not close it.** The report data environments ([[../06-reports/orders.md]], [[../06-reports/listempl.md]]) test `WEXIST("Project Manager")` on the assumption that "TasTrade closes the Project Manager window". Whether a deactivated window still satisfies `WEXIST` was not run here; if it does, running the reports from inside the IDE with the project open takes the `HOME() + "Samples\Tastrade\"` branch.
- **Two class-library lists.** `SetPath` sets `MAIN, TSGEN`, just enough to create the object; `environment.Set` immediately replaces that with `MAIN, TSBASE, TSGEN, LOGIN, ORDERS`. `ABOUT` is loaded on demand by the Help menu.
- **`SET TALK` is handled before the environment object exists** because `SET TALK ON` would echo everything that follows; the value is passed along as text rather than read with `SET('TALK')` a second time.
- **`RIGHT(lcProgram, 3) = "FXP"`** is how the program tells IDE from EXE: only a compiled `.prg` run directly reports its own `.FXP` name.
- **The 1995 copyright line** is the first line, as in every source file of the sample.
