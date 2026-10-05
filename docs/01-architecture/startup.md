# Start-up and shutdown

How Tastrade goes from `tastrade.exe` to a working screen and back, assembled from the per-artifact docs. Every step names the doc that quotes the code.

**Related docs:** [[../08-programs/main.md]], [[../05-classes/main.md]] (`tastrade`, with its own start-up flowchart), [[../05-classes/tsgen.md]] (`application`, `environment`, `introform`), [[../05-classes/login.md]], [[../07-menus/README.md]] (menu lifecycle), [[../05-classes/tsbase.md]] (`tsbaseform`, `tstoolbar`), [[framework.md]], [[README.md]].

## Sequence

```mermaid
sequenceDiagram
    participant X as tastrade.exe
    participant M as main.prg
    participant A as oApp (tastrade : application)
    participant E as oEnvironment
    participant U as user
    participant F as forms
    X->>M: DO progs\main.prg (project main file)
    M->>M: DECLARE 6 Win32 API functions
    M->>M: save TALK, ESCAPE, CURDIR, PATH, CLASSLIB to gcOld*; gTTrade = .T.
    M->>M: SetPath(): CD to root, SET PATH, SET CLASSLIB TO MAIN, TSGEN
    M->>A: CREATEOBJECT("TasTrade")
    A->>E: AddObject("oEnvironment") -> Init saves 20 settings
    A->>E: Set(): SAFETY, PROCEDURE utility.prg, 5 class libs, HELP, ON SHUTDOWN, ESCAPE
    A->>A: OPEN DATABASE data\tastrade.dbc
    A->>A: ReleaseToolBars() (hide VFP's), PUSH MENU _MSYSMENU
    A->>A: tastrade.Init: DO menus\intro.mpr
    A->>U: introform (if tastrade.ini ShowIntroForm=1)
    U-->>A: Continue (1) or Exit (2)
    alt DEBUGMODE .F.
        A->>U: loginpicture dialog
        U-->>A: employee id + user level
    else DEBUGMODE .T. (shipped)
        A->>A: cEmployeeID = "", cUserLevel = "APPLICATIONS DEVELOPER"
    end
    M->>M: RELEASE gcOld*
    M->>A: Do()
    A->>A: DO MAIN.MPR (cleanup code gates pads by user level)
    A->>A: startup action from user_level (skipped under DEBUGMODE)
    loop READ EVENTS
        U->>A: menu bar -> oApp.DoForm(...)
        A->>F: DO FORM; tsbaseform.Init: AddToMenu (Window pad), ShowNavToolBar (toolbar + Navigation pad)
        F->>A: last form closes -> ReleaseNavToolBar, RemoveFromMenu
    end
    U->>A: File > Return to Visual FoxPro: CLEAR EVENTS
    A->>F: Cleanup(): QueryUnload + Release every form
    A->>A: Cleanup2(): caption back, POP MENU, ShowToolBars()
    A-->>M: Do() returns
    M->>M: CLEAR DLLS, RELEASE ALL EXTENDED, CLEAR ALL
    M->>E: (release oApp) Destroy -> Reset() restores every setting
```

## Step by step

1. **Entry.** `tastrade.exe` runs `progs/main.prg`, the project's main file ([[projects.md]]). It declares the INI and registry API functions the classes will use, saves five settings into public `gcOld*` variables, sets `gTTrade`, and `SetPath()` moves to the application root and sets the search path ([[../08-programs/main.md]]).
2. **Application object.** `CREATEOBJECT("TasTrade")` runs `application.Init` ([[../05-classes/tsgen.md]]): adds the `environment` object, whose `Init` records twenty-one settings and whose `Set` applies the application's own (procedure file [[../08-programs/utility.md]], the five class libraries, the help file, `ON SHUTDOWN`); opens the DBC; hides VFP's toolbars by their window titles; pushes the system menu.
3. **Intro and login.** `tastrade.Init` ([[../05-classes/main.md]]) runs the intro menu ([[../07-menus/intro.md]]), shows `introform` unless `tastrade.ini` says not to, then either shows the login dialog ([[../05-classes/login.md]]) or, under `DEBUGMODE`, sets an empty employee and the developer level ([[../08-programs/tastrade.h.md]]).
4. **Main menu and event loop.** `oApp.Do()` runs `main.mpr` ([[../07-menus/main.md]]); its cleanup code removes pads by user level. The user level's startup action (`user_level.startup_action`, [[../03-data-model/tables/user_level.md]]) would run here but is skipped under `DEBUGMODE`. `READ EVENTS` starts.
5. **Forms.** Menu bars call `oApp.DoForm`. Every framework form's `Init` ([[../05-classes/tsbase.md]]) adds its caption to the Window menu ([[../07-menus/window.md]]) and asks the application for the shared toolbar; the first form creates it and adds the Navigation pad ([[../07-menus/navigate.md]]). The order entry form adds the Items pad on every activation ([[../07-menus/ordentry.md]]). Forms open their tables through their data environments with optimistic table buffering; saves go through the DBC's rules and triggers ([[../03-data-model/README.md]]).
6. **Reports** run from the picker ([[../04-forms/reports.md]]) or the self-documentation forms; two open a parameter dialog from their data environment before opening the view ([[../06-reports/README.md]]).
7. **Shutdown.** Return to Visual FoxPro does `CLEAR EVENTS`. `application.Do` then calls `Cleanup` (every form's `QueryUnload`, so unsaved changes can stop the exit) and `Cleanup2` (caption, `POP MENU`, toolbars). Control returns to `main.prg`, which clears the DLL declarations and releases everything; releasing `oApp` runs `environment.Reset`, which puts back every setting, the procedure file, the class libraries, the directory, and the previous `ON SHUTDOWN` handler. Closing VFP from outside is refused while the application runs (`OnShutdown` in [[../08-programs/utility.md]]).

## What `DEBUGMODE` changes on this path

The shipped build has `DEBUGMODE = .T.` compiled in ([[../08-programs/tastrade.h.md]]): step 3 skips the login and grants the developer level, step 4 skips the startup action and keeps every menu pad including Utilities, the environment leaves `SET ESCAPE ON`, and the error handler `SUSPEND`s on Abort. The security and personalisation the sample describes exist only in a build with the flag off.

## Where things live while it runs

| Thing | Holder |
|---|---|
| The application object | public `oApp` (created in `main.prg`) |
| Guard against use outside the app | public `gTTrade` |
| Saved environment | `oApp.oEnvironment` (protected properties) |
| Logged-in employee and level | `oApp.cEmployeeID`, `oApp.cUserLevel` (empty and developer under `DEBUGMODE`) |
| Shared toolbar and its reference count | `oApp.oToolBar`, `oApp.nFormInstanceCount` |
| Multiple instances of a form | `oApp.aInstances` (used by order history) |
| Window positions and the intro flag | `tastrade.ini` beside the EXE |
| Menu state | the system menu, pushed in `Init`, popped in `Cleanup2` |
