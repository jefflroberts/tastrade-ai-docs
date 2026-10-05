"""Generate docs/01-architecture/: projects.md (the project manifest), startup.md
(start-up and shutdown sequence), framework.md (framework overview), README.md.

The manifest comes from foxparse.parse_pj2 plus a census of the working tree
(what is on disk but not in the project, which bitmaps are referenced by code,
by data rows, by class-icon metadata, or by nothing). The two overview pages
are synthesis: prose written from the finished per-artifact docs, with counts
computed here. Rerun after editing; never hand-edit the output.
"""
import os, re, glob, sys
sys.path.insert(0, os.environ.get("VFP_TOOLKIT_TOOLS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "vfp-documentation-toolkit", "tools")))
import foxparse as fp
import dbf

ROOT = os.environ.get("TASTRADE_ROOT", os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))
OUT = os.path.join(ROOT, "docs", "01-architecture")
os.makedirs(OUT, exist_ok=True)


def rel(p):
    return p.replace("\\", "/")


def fence(code, lang="foxpro"):
    return "```%s\n%s\n```" % (lang, code.strip("\n"))


# ------------------------------------------------------------------ census
DOC_FOR = {"form": "04-forms", "report": "06-reports", "menu": "07-menus", "class library": "05-classes",
           "program": "08-programs", "text": "08-programs"}


def doc_link(f):
    stem = os.path.splitext(os.path.basename(f["path"]))[0].lower()
    if f["type"] == "text":
        return "[[../08-programs/%s.h.md]]" % stem
    if f["type"] == "database":
        return "[[../03-data-model/README.md]]"
    if f["type"] == "table":
        return "[[../03-data-model/README.md]] (free table)"
    if f["type"] in DOC_FOR:
        return "[[../%s/%s.md]]" % (DOC_FOR[f["type"]], stem)
    return ""


def bitmap_census(proj_paths):
    scan = {}
    for pat in ("forms/*.sc2", "libs/*.vc2", "menus/*.mn2", "reports/*.fr2", "data/*.dc2", "progs/*.prg", "include/*.h"):
        for f in glob.glob(os.path.join(ROOT, pat)):
            scan[os.path.basename(f)] = open(f, encoding="cp1252", errors="replace").read()
    datarefs = {}
    for t, fld in (("data/category.dbf", "picture_fi"), ("data/employee.dbf", "photo_file")):
        fields, rows = dbf.read_table(os.path.join(ROOT, t))
        for r in rows:
            v = str(r.get(fld, "")).strip()
            if v:
                datarefs.setdefault(os.path.basename(v).lower(), []).append((t, fld, v))
    groups = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "bitmaps", "*"))):
        base = os.path.basename(p).lower()
        inproj = ("bitmaps\\" + base) in proj_paths
        code, icon = [], []
        for fn, t in scan.items():
            lines = [l for l in t.splitlines() if base in l.lower()]
            if not lines:
                continue
            if all("ClassIcon" in l for l in lines):
                icon.append(fn)
            else:
                code.append(fn)
        dref = base in datarefs
        if inproj:
            k = "in the project, referenced at run time" if code else "in the project, referenced by nothing"
        elif code:
            k = "not in the project, referenced at run time"
        elif dref:
            k = "not in the project, referenced only by data rows"
        elif icon:
            k = "not in the project, class-icon metadata only"
        else:
            k = "not in the project, referenced by nothing"
        groups.setdefault(k, []).append((base, sorted(code), sorted(icon), datarefs.get(base, [])))
    return groups


def disk_census(proj_paths):
    skip = ("docs/", "tools/", ".claude/", ".git", "HANDOFF.md", "JOURNAL.md", "README.md", "bitmaps/")
    twin_ext = (".sc2", ".vc2", ".fr2", ".mn2", ".dc2", ".pj2", ".sct", ".vct", ".frt", ".mnt", ".fpt", ".cdx",
                ".mpr", ".mpx", ".dcx", ".dct", ".pjt", ".pjx")
    out = []
    for p in sorted(glob.glob(os.path.join(ROOT, "**", "*"), recursive=True)):
        if not os.path.isfile(p):
            continue
        r = rel(os.path.relpath(p, ROOT))
        if r.startswith(skip) or r.lower().endswith(twin_ext):
            continue
        if r.replace("/", "\\").lower() not in proj_paths:
            out.append(r)
    return out


# ------------------------------------------------------------------ projects.md
def gen_projects():
    r = fp.parse_pj2(os.path.join(ROOT, "tastrade.pj2"))
    proj = {f["path"].lower() for f in r["files"]}
    files = r["files"]
    tc = r["type_counts"]
    L = ["# Project: tastrade.pjx", "",
         "| Source file | Type | Path |", "|---|---|---|",
         "| `tastrade.pjx` | Project | `tastrade.pj2` |", "",
         "**Purpose:** The manifest VFP builds `tastrade.exe` from: %d members (%s), the main program, and the build settings. Nothing reads it at run time." % (
             r["file_count"], ", ".join("%d %s" % (n, t if n == 1 else {"class library": "class libraries"}.get(t, t + "s")) for t, n in sorted(tc.items(), key=lambda kv: -kv[1]))), "",
         "**Used by:**",
         "- The VFP IDE and the `BUILD EXE` that produced `tastrade.exe` on 2026-09-08 (Step 3 in `JOURNAL.md`); the 2001 release shipped `tastrade.app` built from the same project.",
         "- `.SetMain('progs\\main.prg')` makes [[../08-programs/main.md]] the entry point.", "",
         "**Related docs:** [[startup.md]], [[framework.md]], [[../00-inventory/README.md]] (the generated census), [[../08-programs/main.md]], [[../03-data-model/README.md]], [[README.md]].", ""]
    L += ["## Build settings", "",
          "| Setting | Value | Note |", "|---|---|---|",
          "| Main file | `%s` | [[../08-programs/main.md]] |" % r["main_file"],
          "| Home directory | `%s` | The VFP 9 rebuild changed it from `c:\\vfp\\tastrade`: the only line of the twin that differs between the 2001 and 2026 sweeps |" % r["home_dir"],
          "| Debug info | `%s` | Compiled with debugging information |" % r["properties"].get("Debug"),
          "| Encrypted | `%s` | Source in the EXE is not encrypted |" % r["properties"].get("Encrypted"),
          "| Project hook | none | `ProjectHookLibrary` and `ProjectHookClass` empty |",
          "| Author / company | %s, %s, %s %s %s | The only version-info fields filled in |" % (r["dev_info"].get("Author"), r["dev_info"].get("Address"), r["dev_info"].get("City"), r["dev_info"].get("State"), r["dev_info"].get("PostalCode")),
          "| Product name, description, copyright, version | empty | The EXE carries no product name, file description, legal copyright, or version number; `_AutoIncrement = 0` |", "",
          "**NOTE:** the version and copyright the application shows come from `include/strings.h` (\"1.1\", 1996) and the intro menu (\"1.0\", 1994), not from here; the EXE's own version resource is blank.", ""]
    # members by type
    L += ["## Members", "", "| Type | Count | Compiled into the EXE |", "|---|---|---|"]
    for t, n in sorted(tc.items(), key=lambda kv: -kv[1]):
        exc = sum(1 for f in files if f["type"] == t and f["excluded"])
        L.append("| %s | %d | %s |" % (t, n, "no (%d excluded)" % exc if exc == n else ("%d of %d" % (n - exc, n) if exc else "yes")))
    L.append("")
    order = ["program", "class library", "form", "menu", "report", "database", "table", "text", "other"]
    for t in order:
        members = [f for f in files if f["type"] == t]
        if not members:
            continue
        L += ["### %s (%d)" % (t[0].upper() + t[1:], len(members)), "",
              "| Path | Description in the project | Excluded | Doc |", "|---|---|---|---|"]
        for f in members:
            L.append("| `%s` | %s | %s | %s |" % (rel(f["path"]), f["description"] or "*(none)*", "yes" if f["excluded"] else "", doc_link(f)))
        L.append("")
    undesc = [rel(f["path"]) for f in files if not f["description"] and f["type"] != "other"]
    L += ["%d of %d members carry a description. The undescribed ones outside the bitmaps are %s." % (
        sum(1 for f in files if f["description"]), len(files), ", ".join("`%s`" % u for u in undesc)), ""]
    # excluded
    L += ["## Excluded from the EXE", "",
          "Five members are marked `Exclude`: the database container, the two free tables, and the two include files. The EXE therefore expects `data\\tastrade.dbc` and its tables, `data\\behindsc.dbf`, and `data\\repolist.dbf` on disk beside it, found through `SET PATH` ([[../08-programs/main.md]]); the include files matter only at compile time. Excluding data is the normal choice: tables inside an EXE would be read-only.", ""]
    # on disk not in project
    disk = disk_census(proj)
    L += ["## On disk but not in the project", "",
          "| File | Why it is outside |", "|---|---|"]
    why = {"tastrade.exe": "the build output", "tastrade.ini": "run-time data: the intro-form flag and window positions, written by the application",
           "other/notes.txt": "the project template's placeholder (\"Here's a place to keep notes on your project.\")",
           "help/tastrade.chm": "the help file `environment.Set` selects with `SET HELP TO HELP\\TASTRADE.CHM`; found by path, never bundled",
           "help/tastrade.chi": "the help file's index", "help/ttrade.dbf": "source table of the help file (16 topics)", "help/ttrade.bmp": "help artwork"}
    for d in disk:
        L.append("| `%s` | %s |" % (d, why.get(d, "a table contained in `tastrade.dbc`; the project lists the container, not its tables" if d.startswith("data/") else "")))
    L += ["", "The ten contained tables appear under the database node in the Project Manager but are not members; the two free tables are. `data/setup.dbf` is the DBC's own configuration table ([[../03-data-model/tables/setup.md]]).", ""]
    # bitmaps
    groups = bitmap_census(proj)
    total = sum(len(v) for v in groups.values())
    L += ["## Bitmaps: what is used, by whom", "",
          "`bitmaps/` holds %d files; the project includes %d. Every twin, the two programs, the include files, and the picture columns of `category.dbf` and `employee.dbf` were grepped for each file name:" % (total, sum(len(v) for k, v in groups.items() if k.startswith("in the project"))), "",
          "| Group | Files | Names |", "|---|---|---|"]
    for k in ("in the project, referenced at run time", "in the project, referenced by nothing", "not in the project, referenced at run time",
              "not in the project, referenced only by data rows", "not in the project, class-icon metadata only", "not in the project, referenced by nothing"):
        if k in groups:
            L.append("| %s | %d | %s |" % (k, len(groups[k]), ", ".join("`%s`" % b for b, c, i, d in groups[k])))
    L += [""]
    runtime = groups.get("in the project, referenced at run time", [])
    L += ["Run-time references, by file:", "", "| Bitmap | Referenced from |", "|---|---|"]
    for b, c, i, d in runtime:
        L.append("| `%s` | %s |" % (b, ", ".join("`%s`" % x for x in c)))
    L += ["",
          "- **The %d unreferenced project members** are %d `.msk` mask files, which VFP pairs with the toolbar button bitmap of the same name without a reference in code, plus %s, which no twin names." % (
              len(groups.get("in the project, referenced by nothing", [])), sum(1 for b, c, i, d in groups.get("in the project, referenced by nothing", []) if b.endswith(".msk")),
              ", ".join("`%s`" % b for b, c, i, d in groups.get("in the project, referenced by nothing", []) if not b.endswith(".msk"))),
          "- **The %d data-only bitmaps** are the category pictures and employee photos: `category.picture_file` and `employee.photo_file` hold relative paths such as `bitmaps\\beverage.bmp`, resolved against the current directory at run time ([[../04-forms/category.md]], [[../04-forms/employee.md]]). They are not in the project, so a build on another machine ships without them unless the folder is copied." % len(groups.get("not in the project, referenced only by data rows", [])),
          "- **The %d class-icon bitmaps** appear only in the `ProjectClassIcon` / `ClassIcon` metadata of the class libraries (the icons the Class Browser shows), two of them through the original authors' paths `h:\\allisonk\\sampapp\\` and `..\\..\\..\\..\\backup\\mainsamp\\`. Design-time only." % len(groups.get("not in the project, class-icon metadata only", [])),
          "- **%d files are referenced by nothing at all** (`%s`): dead artwork, including `splash.bmp` and `ohist.ico`." % (
              len(groups.get("not in the project, referenced by nothing", [])), "`, `".join(b for b, c, i, d in groups.get("not in the project, referenced by nothing", []))), ""]
    # twin notes
    L += ["## Reading the twin", "",
          "FoxBin2PRG renders the project as a program that would rebuild the `.pjx`: `BUILD PROJECT ... FROM '__newproject.f2b'`, an `.ADD()` per member with a `FileMetadata` comment (`Type`, `Cpid`, `ObjRev`), then descriptions, exclusions, text-file overrides, and properties. The `LPARAMETERS tcDir`, the temporary `__newproject.f2b`, and the commented `*ERASE` are the tool's scaffolding, not project data.", "",
          "Type codes as VFP writes them: lowercase `d` for the database container, uppercase `D` for a table, `x` for images and other files, `K` form, `V` class library, `M` menu, `R` report, `P` program, `T` text. `foxparse.py` mislabelled `D` as \"database\" and knew neither `d` nor `x` until this step (toolkit commit noted in `JOURNAL.md`).", "",
          "`ObjRev` is `544` on every form, class library, menu, program, and the DBC, and `0` on reports, tables, include files, and images; `Cpid` is `1252` on seven members (`locate.bmp`/`.msk`, `ordhist.scx`, `navigate.mnx`, `window.mnx`, `behindsc.frx`, `topcust.frx`) and `0` elsewhere, which marks the members touched last by a code-page-aware VFP.", ""]
    L += ["## Notes", "",
          "- **No version resource.** Product name, description, copyright, and version are empty in the project, so the EXE identifies itself only by its file name.",
          "- **Debug information is on.** Line numbers survive into the EXE (`tsbaseform.Error` puts the `nLine` it receives into its message, [[../05-classes/tsbase.md]]), at the cost of size.",
          "- **Two menus and two reports have no description**, the same four members that other steps found to be late additions (`Cpid = 1252`).",
          "- **The 2001 `tastrade.app` and the 2026 `tastrade.exe`** were built from this same manifest; the app was 826,220 bytes, the EXE is 851,749 (the VFP 9 runtime stub and refreshed object code).",
          "- **`c:\\vfp\\tastrade`** was the home directory in the shipped project, alongside the three original-author paths found in the class libraries; the sample has been built from at least four locations."]
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ startup.md
def gen_startup():
    L = ["# Start-up and shutdown", "",
         "How Tastrade goes from `tastrade.exe` to a working screen and back, assembled from the per-artifact docs. Every step names the doc that quotes the code.", "",
         "**Related docs:** [[../08-programs/main.md]], [[../05-classes/main.md]] (`tastrade`, with its own start-up flowchart), [[../05-classes/tsgen.md]] (`application`, `environment`, `introform`), [[../05-classes/login.md]], [[../07-menus/README.md]] (menu lifecycle), [[../05-classes/tsbase.md]] (`tsbaseform`, `tstoolbar`), [[framework.md]], [[README.md]].", "",
         "## Sequence", "",
         fence("""sequenceDiagram
    participant X as tastrade.exe
    participant M as main.prg
    participant A as oApp (tastrade : application)
    participant E as oEnvironment
    participant U as user
    participant F as forms
    X->>M: DO progs\\main.prg (project main file)
    M->>M: DECLARE 6 Win32 API functions
    M->>M: save TALK, ESCAPE, CURDIR, PATH, CLASSLIB to gcOld*; gTTrade = .T.
    M->>M: SetPath(): CD to root, SET PATH, SET CLASSLIB TO MAIN, TSGEN
    M->>A: CREATEOBJECT("TasTrade")
    A->>E: AddObject("oEnvironment") -> Init saves 20 settings
    A->>E: Set(): SAFETY, PROCEDURE utility.prg, 5 class libs, HELP, ON SHUTDOWN, ESCAPE
    A->>A: OPEN DATABASE data\\tastrade.dbc
    A->>A: ReleaseToolBars() (hide VFP's), PUSH MENU _MSYSMENU
    A->>A: tastrade.Init: DO menus\\intro.mpr
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
    M->>E: (release oApp) Destroy -> Reset() restores every setting""", "mermaid"), "",
         "## Step by step", "",
         "1. **Entry.** `tastrade.exe` runs `progs/main.prg`, the project's main file ([[projects.md]]). It declares the INI and registry API functions the classes will use, saves five settings into public `gcOld*` variables, sets `gTTrade`, and `SetPath()` moves to the application root and sets the search path ([[../08-programs/main.md]]).",
         "2. **Application object.** `CREATEOBJECT(\"TasTrade\")` runs `application.Init` ([[../05-classes/tsgen.md]]): adds the `environment` object, whose `Init` records twenty-one settings and whose `Set` applies the application's own (procedure file [[../08-programs/utility.md]], the five class libraries, the help file, `ON SHUTDOWN`); opens the DBC; hides VFP's toolbars by their window titles; pushes the system menu.",
         "3. **Intro and login.** `tastrade.Init` ([[../05-classes/main.md]]) runs the intro menu ([[../07-menus/intro.md]]), shows `introform` unless `tastrade.ini` says not to, then either shows the login dialog ([[../05-classes/login.md]]) or, under `DEBUGMODE`, sets an empty employee and the developer level ([[../08-programs/tastrade.h.md]]).",
         "4. **Main menu and event loop.** `oApp.Do()` runs `main.mpr` ([[../07-menus/main.md]]); its cleanup code removes pads by user level. The user level's startup action (`user_level.startup_action`, [[../03-data-model/tables/user_level.md]]) would run here but is skipped under `DEBUGMODE`. `READ EVENTS` starts.",
         "5. **Forms.** Menu bars call `oApp.DoForm`. Every framework form's `Init` ([[../05-classes/tsbase.md]]) adds its caption to the Window menu ([[../07-menus/window.md]]) and asks the application for the shared toolbar; the first form creates it and adds the Navigation pad ([[../07-menus/navigate.md]]). The order entry form adds the Items pad on every activation ([[../07-menus/ordentry.md]]). Forms open their tables through their data environments with optimistic table buffering; saves go through the DBC's rules and triggers ([[../03-data-model/README.md]]).",
         "6. **Reports** run from the picker ([[../04-forms/reports.md]]) or the self-documentation forms; two open a parameter dialog from their data environment before opening the view ([[../06-reports/README.md]]).",
         "7. **Shutdown.** Return to Visual FoxPro does `CLEAR EVENTS`. `application.Do` then calls `Cleanup` (every form's `QueryUnload`, so unsaved changes can stop the exit) and `Cleanup2` (caption, `POP MENU`, toolbars). Control returns to `main.prg`, which clears the DLL declarations and releases everything; releasing `oApp` runs `environment.Reset`, which puts back every setting, the procedure file, the class libraries, the directory, and the previous `ON SHUTDOWN` handler. Closing VFP from outside is refused while the application runs (`OnShutdown` in [[../08-programs/utility.md]]).", "",
         "## What `DEBUGMODE` changes on this path", "",
         "The shipped build has `DEBUGMODE = .T.` compiled in ([[../08-programs/tastrade.h.md]]): step 3 skips the login and grants the developer level, step 4 skips the startup action and keeps every menu pad including Utilities, the environment leaves `SET ESCAPE ON`, and the error handler `SUSPEND`s on Abort. The security and personalisation the sample describes exist only in a build with the flag off.", "",
         "## Where things live while it runs", "",
         "| Thing | Holder |", "|---|---|",
         "| The application object | public `oApp` (created in `main.prg`) |",
         "| Guard against use outside the app | public `gTTrade` |",
         "| Saved environment | `oApp.oEnvironment` (protected properties) |",
         "| Logged-in employee and level | `oApp.cEmployeeID`, `oApp.cUserLevel` (empty and developer under `DEBUGMODE`) |",
         "| Shared toolbar and its reference count | `oApp.oToolBar`, `oApp.nFormInstanceCount` |",
         "| Multiple instances of a form | `oApp.aInstances` (used by order history) |",
         "| Window positions and the intro flag | `tastrade.ini` beside the EXE |",
         "| Menu state | the system menu, pushed in `Init`, popped in `Cleanup2` |", ""]
    return "\n".join(L)


# ------------------------------------------------------------------ framework.md
def gen_framework():
    L = ["# Framework overview", "",
         "Tastrade exists to show one way of building a VFP application: an application object that owns the event loop, an environment object that saves and restores settings, a base form class that talks to one shared toolbar, a database container that holds the business rules, and menus that are thin fronts for all of it. This page names the parts and the conventions; each part has its own doc.", "",
         "**Related docs:** [[startup.md]], [[projects.md]], [[../05-classes/README.md]] (inheritance diagram across the six libraries), [[../03-data-model/README.md]], [[../04-forms/README.md]], [[../06-reports/README.md]], [[../07-menus/README.md]], [[../08-programs/README.md]], [[README.md]].", "",
         "## Layers", "",
         fence("""flowchart TB
    subgraph entry [Entry and environment]
        MP[progs/main.prg] --> ENV[environment: 21 settings saved, applied, restored]
    end
    subgraph app [Application object]
        APP[application in tsgen.vcx] --> TT[tastrade in main.vcx]
    end
    subgraph ui [User interface]
        MENUS[5 menus] --> TB[tstoolbar, one shared instance]
        TB --> BF[tsbaseform contract: First/Prior/Next/Last/AddNew/Save/Restore/QueryUnload]
        BF --> MF[tsmaintform: 6 maintenance forms]
        BF --> TF[tstextform: 2 viewers]
        BF --> OE[orderentry: order entry]
        BF --> OTHER[6 other tsbaseform forms]
        RV[tsformretval: 5 modal dialogs]
    end
    subgraph data [Data]
        DBC[tastrade.dbc: 10 tables, 13 views, 8 relations, 21 stored procedures]
        RPT[13 reports, 10 on the views]
    end
    MP --> APP
    TT --> MENUS
    BF --> DBC
    RPT --> DBC""", "mermaid"), "",
         "### Entry and environment", "",
         "`main.prg` ([[../08-programs/main.md]]) is fifty lines: declare, save, path, create, run, release. Everything it changes is put back by `environment` ([[../05-classes/tsgen.md]]), which records twenty-one `SET` and `ON` values in `Init`, applies the application's in `Set`, and restores them in `Reset` from `Destroy`. The public variable `gTTrade` is the framework's only guard: every class `Init` refuses to run without it.", "",
         "### Application object", "",
         "`application` ([[../05-classes/tsgen.md]]) is abstract in practice: it owns the menu name, the event loop (`Do`), the two-stage shutdown (`Cleanup`, `Cleanup2`), the shared toolbar with its reference count, VFP's own toolbars, modal dialogs that return a value (`DoFormRetVal`), and the instance table for forms that may open more than once. `tastrade` ([[../05-classes/main.md]]) fills in the database name and caption, adds the intro screen and login, the employee id and user level, and the startup action per user level.", "",
         "### Base classes and the toolbar contract", "",
         "`tsbase.vcx` ([[../05-classes/tsbase.md]]) holds `tsbaseform` and one subclass per VFP control. The form owns optimistic table buffering (`BufferMode = 2`), the prompt-to-save logic, the form-level `Error` handler that turns trigger and rule failures into messages, its Window-menu entry, and its remembered window position. The single `tstoolbar` instance drives whichever form is active by calling `First`, `Prior`, `Next`, `Last`, `AddNew`, `Save`, `Restore`, and `QueryUnload` on `_screen.ActiveForm`, and reads the `FILE_*` codes they return to enable its buttons; the menus call the same buttons' `Click` methods and mirror their `Enabled` state in `SKIP FOR` conditions ([[../07-menus/README.md]]). Three properties, `lAllowEdits`, `lAllowNew`, `lAllowDelete`, are what a form sets to restrict itself.", "",
         "`tsmaintform` adds the two-page maintenance pattern (data entry page, list page with a grid) used by the six master-file forms; `tstextform` is the read-only text viewer used twice; `tsformretval` (a plain `form`, not a `tsbaseform`) is the base for the modal dialogs that hand back `uRetVal`: `login` and its `loginpicture` variant, the two record pickers, and the intro screen; the About box extends `tsbaseform`. Two forms bypass all of it ([[../04-forms/getinv.md]], [[../04-forms/gettitle.md]]).", "",
         "### Forms", "",
         "Seventeen forms ([[../04-forms/README.md]]): six maintenance forms on `tsmaintform`, the order entry form on `orderentry` ([[../05-classes/orders.md]]), order history, add-customer, change-password, report picker, reindex, and Behind the Scenes on `tsbaseform`, two viewers on `tstextform`, and the two report dialogs on `form`. Forms are single-instance by `WEXIST` of their class name in the menu, except order history, which registers with `oApp.AddInstance` and numbers its captions. Forms open tables through their data environments; the form docs flag the few places that do their own `USE` instead.", "",
         "### Data", "",
         "`tastrade.dbc` ([[../03-data-model/README.md]]) is where the business rules are: `NewID()` for keys, `ValOrder()` and `RemainingCredit()` for order validation, RI triggers on eight relations, field and table rules, and thirteen read-only views that feed the reports and the order history form. The order total is computed in seven places ([[../06-reports/orders.md]] lists them); the two sales views sum unit prices without quantity, and the Top 25 view uses the full formula, so the sales reports disagree with each other.", "",
         "### Reports and menus", "",
         "Reports ([[../06-reports/README.md]]) declare their own cursors on the DBC views; two run a parameter dialog from their data environment `Init` and pass the values as private variables. All thirteen carry saved printer environments naming Microsoft's 1990s printers. Menus ([[../07-menus/README.md]]) are five `.mnx` files; the main menu's cleanup code is the only privilege gating, three pads reuse VFP system pad names as a placement trick, and the Window and Items pads are created and destroyed at run time by the base form and the order entry form.", "",
         "### Self-documentation", "",
         "Behind the Scenes ([[../04-forms/behindsc.md]]) reads `behindsc.dbf` for explanations and opens `.scx`/`.vcx` files as tables to show method code; the case study viewer, its report, and the code report ([[../06-reports/README.md]]) belong to the same teaching layer. One of them, [[../04-forms/casestdy.md]], is reachable from nothing.", "",
         "## Conventions a rebuild must reproduce", "",
         "- **Strings** come from `include/strings.h` and `include/tastrade.h` ([[../08-programs/README.md]]); menu text does not.",
         "- **`DEBUGMODE`** is a compiled-in literal read at five sites ([[../08-programs/tastrade.h.md]]); the shipped build has it on, which removes login, the startup action, and the menu gating.",
         "- **User levels** are rows of `user_level` whose upper-cased descriptions must equal `USER_APPDEV_LOC` and `USER_OPSMGR_LOC`.",
         "- **Pictures** for categories and employees are relative paths in the data (`bitmaps\\name.bmp`), not project members ([[projects.md]]).",
         "- **Window positions and the intro flag** live in `tastrade.ini` through the Win32 profile API declared in `main.prg`.",
         "- **Exit** is only through the menu; `ON SHUTDOWN` refuses to close VFP while the application runs.",
         "- **The toolbar and the base form share a method contract** by name; a form that lacks one of the eight methods breaks the toolbar.",
         "- **Views depend on VFP's automatic column names** in two reports (`exp_1`, `sum_unit_price`, `company_name_a`/`_b`).", "",
         "## Where the framework leaks", "",
         "The framework promises separation and mostly keeps it, but the docs found the seams: the order total formula written seven times instead of one; a stored procedure (`CalcOrdTotal()`) nobody calls; four features behind `DEBUGMODE`; a privilege gate that names a popup that does not exist; a dead form, a dead report, three dead cursors, thirteen dead constants, a dead function, fifteen dead bitmaps; a splitter whose targets refuse to move; an include-file constant left out of one report's data environment so its error path errors; and a self-documentation topic that names a class that does not exist. Each is recorded in the doc of the artifact that carries it and summarised in `JOURNAL.md`.", ""]
    return "\n".join(L)


# ------------------------------------------------------------------ index
def gen_readme():
    L = ["# Architecture", "",
         "Three pages that sit above the per-artifact docs.", "",
         "| Page | What it holds |", "|---|---|",
         "| [[projects.md]] | The project manifest from `tastrade.pjx`: members by type with descriptions, exclusions, build settings, what is on disk but outside the project, and which of the 83 bitmaps anything uses |",
         "| [[startup.md]] | Start-up and shutdown sequence, as a diagram and step by step, with what `DEBUGMODE` changes |",
         "| [[framework.md]] | Framework overview: entry and environment, application object, base classes and the toolbar contract, forms, data, reports and menus, and the conventions a rebuild must reproduce |", "",
         "The per-artifact docs these draw on: [[../03-data-model/README.md]], [[../04-forms/README.md]], [[../05-classes/README.md]], [[../06-reports/README.md]], [[../07-menus/README.md]], [[../08-programs/README.md]]; the generated census is in [[../00-inventory/README.md]].", ""]
    return "\n".join(L)


GENERATORS = (("projects.md", gen_projects), ("startup.md", gen_startup), ("framework.md", gen_framework), ("README.md", gen_readme))

if __name__ == "__main__":
    for fn, gen in GENERATORS:
        with open(os.path.join(OUT, fn), "w", encoding="utf-8", newline="\n") as f:
            f.write(gen())
        print("wrote", fn)
