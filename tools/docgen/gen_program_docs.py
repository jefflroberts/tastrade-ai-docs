"""Generate docs/08-programs/*.md (two programs, two include files) and its index.

Programs and include files are native VFP text, so this script parses them
itself: routines, DECLARE blocks, #INCLUDE lines, #DEFINE tables. Constant
usage is counted by a case-sensitive whole-word grep over every twin, .mpr,
.prg and the DBC twin (the include files themselves excluded). Purpose,
callers, and notes are hand-written strings below, each checked against a
grep. Rerun after editing; never hand-edit the output.
"""
import os, re, glob, sys

ROOT = os.environ.get("TASTRADE_ROOT", os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))
OUT = os.path.join(ROOT, "docs", "08-programs")
os.makedirs(OUT, exist_ok=True)


def rd(p):
    return open(os.path.join(ROOT, p), encoding="cp1252", errors="replace").read()


def fence(code):
    return "```foxpro\n" + code.strip("\r\n") + "\n```"


# ------------------------------------------------------------------ parsing
def parse_prg(rel):
    t = rd(rel)
    lines = t.splitlines()
    # join ';' continuations for DECLARE / #INCLUDE scanning
    joined, buf = [], ""
    for l in lines:
        if l.rstrip().endswith(";"):
            buf += l.rstrip()[:-1] + " "
        else:
            joined.append((buf + l).strip()); buf = ""
    includes = [l for l in joined if l.upper().startswith("#INCLUDE")]
    declares = []
    for l in joined:
        m = re.match(r"DECLARE\s+(\w+)\s+(\w+)\s+IN\s+(\w+)(?:\s+AS\s+(\w+))?\s*(.*)", l, re.I)
        if m:
            declares.append({"ret": m.group(1), "name": m.group(2), "lib": m.group(3), "alias": m.group(4) or "",
                             "params": re.sub(r"\s+", " ", m.group(5)).strip()})
    # routines
    idx = [i for i, l in enumerate(lines) if re.match(r"^(FUNCTION|PROCEDURE)\s+\w+", l, re.I)]
    routines = []
    for n, i in enumerate(idx):
        end = idx[n + 1] if n + 1 < len(idx) else len(lines)
        m = re.match(r"^(FUNCTION|PROCEDURE)\s+(\w+)\s*(\(.*?\))?", lines[i], re.I)
        body = "\n".join(lines[i:end]).rstrip()
        body = re.sub(r"\n(ENDFUNC|ENDPROC)\s*$", r"\n\1", body)
        routines.append({"kind": m.group(1).upper(), "name": m.group(2), "params": (m.group(3) or "").strip("()"), "body": body})
    top = "\n".join(lines[:idx[0]]).rstrip() if idx else t
    return {"file": rel, "text": t, "includes": includes, "declares": declares, "routines": routines, "top": top,
            "line_count": len(lines)}


SCAN = [f for pat in ("forms/*.sc2", "libs/*.vc2", "menus/*.mn2", "menus/*.mpr", "reports/*.fr2", "data/*.dc2", "progs/*.prg")
        for f in glob.glob(os.path.join(ROOT, pat))]
SCAN_TEXT = {os.path.basename(f): open(f, encoding="cp1252", errors="replace").read() for f in SCAN}


def users_of(name):
    out = []
    for fn, t in SCAN_TEXT.items():
        n = len(re.findall(r"\b%s\b" % re.escape(name), t))
        if n:
            out.append((fn, n))
    return out


def parse_h(rel):
    t = rd(rel)
    defines, section = [], ""
    for l in t.splitlines():
        s = l.strip()
        m = re.match(r"#DEFINE\s+(\w+)\s+(.*?)\s*(?:&&\s*(.*))?$", s)
        if m:
            defines.append({"name": m.group(1), "value": m.group(2), "comment": (m.group(3) or "").strip(),
                            "section": section, "users": users_of(m.group(1))})
        elif s.startswith("*--") and not s.startswith("*-- (c)"):
            section = s[3:].strip()
        elif not s:
            pass
    includes = [l.strip() for l in t.splitlines() if l.strip().upper().startswith("#INCLUDE")]
    return {"file": rel, "text": t, "defines": defines, "includes": includes, "line_count": len(t.splitlines())}


def users_cell(users):
    if not users:
        return "**unused**"
    return ", ".join("`%s`%s" % (fn, "" if n == 1 else " (%d)" % n) for fn, n in users)


# ------------------------------------------------------------------ pieces
def head(fname, kind, title, purpose, used_by, related):
    return ["# %s" % title, "", "| Source file | Type | Path |", "|---|---|---|",
            "| `%s` | %s | `%s` |" % (os.path.basename(fname), kind, fname), "", "**Purpose:** " + purpose, "",
            "**Used by:**"] + ["- " + u for u in used_by] + ["", "**Related docs:** " + related, ""]


def notes(items):
    return ["## Notes", ""] + ["- " + i for i in items] + [""]


# ------------------------------------------------------------------ main.prg
def gen_main():
    r = parse_prg("progs/main.prg")
    L = head("progs/main.prg", "Program", "main.prg",
             "The application's entry point: declares the Win32 API functions the framework uses, saves the environment it is about to change, sets the path and class libraries, creates the `tastrade` application object, runs it, and cleans up.",
             ["The project's main file: `tastrade.pj2` has `.SetMain(lcCurdir + 'progs\\main.prg')`, so `tastrade.exe` starts here. Nothing else calls it; running `progs\\main.prg` from the IDE is the other way in, and `SetPath()` allows for it."],
             "[[../05-classes/main.md]] (`tastrade`, the object this program creates), [[../05-classes/tsgen.md]] (`application.Init`/`Do`, and `environment`, which consumes the globals saved here), [[../05-classes/login.md]], [[tastrade.h.md]] (the include file), [[utility.md]] (loaded by `environment.Set`), [[../07-menus/README.md]] (the menus `Do` runs), [[README.md]].")
    L += ["## Role", "",
          "**Runtime entry point.** It is the project's main program and the only `.prg` on the call graph besides the procedure library. Nothing to flag for deletion.", ""]
    L += ["## What it does", "",
          "1. `#INCLUDE`s [[tastrade.h.md]] (which pulls in `FOXPRO.H` and [[strings.h.md]]); no constant from it is used in this file, but the project compiles it in.",
          "2. Declares six Win32 API functions (table below). Declarations are process-wide in VFP, so this is where the INI and registry access used by the classes is wired up.",
          "3. `CLEAR`s the screen and `DEACTIVATE WINDOW \"Project Manager\"` so a hot key sent with `KEYBOARD` cannot land in the IDE's project window.",
          "4. Turns `SET TALK` off, remembering the old value, and saves `SET ESCAPE`, the current directory, `SET PATH`, and `SET CLASSLIB` into public `gcOld*` variables; sets the public flag `gTTrade` to `.T.`.",
          "5. `SetPath()` changes directory to the application root and sets the search path and the two class libraries needed to instantiate the application object.",
          "6. `CREATEOBJECT(\"TasTrade\")`. `application.Init` copies the `gcOld*` values into its `environment` member and applies the application's own settings ([[../05-classes/tsgen.md]]); `tastrade.Init` then runs the intro menu, the intro form, and the login ([[../05-classes/main.md]]).",
          "7. If the object came back, releases the five `gcOld*` variables (their values now live in `environment`) and calls `oApp.Do()`, which puts up the main menu and sits in `READ EVENTS` until Return to Visual FoxPro.",
          "8. On the way out: `CLEAR DLLS`, `RELEASE ALL EXTENDED`, `CLEAR ALL`. Releasing `oApp` fires `application.Destroy`, and `environment.Destroy` restores every setting saved in step 4 and in `environment.Init`.", ""]
    L += ["The top-level code, verbatim:", "", fence(r["top"]), ""]
    L += ["## Key routines", ""]
    for rt in r["routines"]:
        L += ["#### `%s %s(%s)`" % (rt["kind"], rt["name"], rt["params"]), "",
              "Works out where the program is running from with `SYS(16)` (the running program's name with its path), takes the text from the drive letter on, and changes to that folder. Run as `MAIN.FXP` from `progs\\`, it goes up one level so the relative folders in `SET PATH` resolve; run from the EXE, `SYS(16)` already names the root. Then it sets the search path over every application folder (`OTHER` holds only `notes.txt`, a placeholder) and the two class libraries that `CREATEOBJECT(\"TasTrade\")` needs. It has no `RETURN`, so it returns VFP's default `.T.` and the `IF SetPath()` in the caller always passes.", "",
              fence(rt["body"]), ""]
    L += ["## Inputs / outputs / side effects", "",
          "**Win32 API declarations** (all `IN Win32API`):", "",
          "| Declared as | Alias | Used by |", "|---|---|---|"]
    use = {"GetPrivateProfileString": "[[../05-classes/main.md]] `tastrade.Init` reads `ShowIntroForm`; [[../05-classes/tsbase.md]] `tsbaseform.RestoreWindowPos` reads window positions",
           "WritePrivateProfileString": "[[../05-classes/tsgen.md]] `introform` writes `ShowIntroForm`; [[../05-classes/tsbase.md]] `tsbaseform.SaveWindowPos` writes window positions",
           "RegOpenKeyEx": "[[../05-classes/about.md]] `aboutbox` locates the System Info program",
           "RegQueryValueEx": "[[../05-classes/about.md]]", "RegCloseKey": "[[../05-classes/about.md]]",
           "GetProfileString": "[[../05-classes/about.md]] (Windows 3.1 `win.ini` lookup, the About box's fallback)"}
    for d in r["declares"]:
        L.append("| `%s %s(%s)` | `%s` | %s |" % (d["ret"], d["name"], d["params"], d["alias"] or d["name"], use.get(d["name"], "")))
    L += ["",
          "`main.prg` itself calls none of them; it declares for the classes. `CLEAR DLLS` at the end drops all six.", "",
          "**Public variables created here:**", "",
          "| Variable | Value | Consumer |", "|---|---|---|",
          "| `gcOldTalk` | `'ON'` or `'OFF'` | `environment.Init` (`cOldTalk`), restored by `environment.Reset` |",
          "| `gcOldEscape` | `SET('ESCAPE')` | same (`cOldEscape`) |",
          "| `gcOldDir` | `FULLPATH(CURDIR())` | same (`cOldDir`); `Reset` does `CD` back to it |",
          "| `gcOldPath` | `SET('PATH')` | same (`cOldPath`) |",
          "| `gcOldClassLib` | `SET('CLASSLIB')` | same (`cOldClassLib`) |",
          "| `gTTrade` | `.T.` | The guard `IF TYPE(\"m.gTTrade\") # 'L' OR !m.gTTrade` in the `Init` of `application`, `environment`, `tastrade`, `tsbaseform`, `tstoolbar`, `login`, `aboutbox`, and others: nine sites across the libraries. It is never released by this program; `RELEASE ALL EXTENDED` at the end takes it. |",
          "| `oApp` | the `tastrade` object | Every form, menu, and class; the application's only global object |", "",
          "**Files and settings:** reads nothing itself; the INI file (`tastrade.ini`, `INIFILE` in [[tastrade.h.md]], one key `ShowIntroForm=1` in the repo copy) and the registry are touched by the classes through the declarations above. Changes the current directory, `SET TALK`, `SET PATH`, `SET CLASSLIB`; `environment.Set` then changes another fourteen settings and `ON SHUTDOWN` ([[../05-classes/tsgen.md]]), all restored on exit.", ""]
    L += ["## Called from / calls", "",
          "- **Called from:** the EXE (project main file), or `DO progs\\main.prg` in the IDE.",
          "- **Calls:** `SetPath()` (local), `CREATEOBJECT(\"TasTrade\")` ([[../05-classes/main.md]]), `oApp.Do()`. Everything else in the application hangs off `Do`: the main menu ([[../07-menus/main.md]]), the forms, the reports.", ""]
    L += notes(["**The comment about public variables is half true.** \"All public vars will be released as soon as the application object is created\" holds for the five `gcOld*` variables; `gTTrade` and `oApp` stay public for the life of the application, on purpose: `gTTrade` is what stops the classes being used outside Tastrade.",
                "**No error handler of its own.** `ON ERROR` is never set by this program or by `environment.Set`; form errors go to `tsbaseform.Error` ([[../05-classes/tsbase.md]]), and anything before `oApp` exists gets VFP's default error dialog.",
                "**`DEACTIVATE WINDOW \"Project Manager\"` hides the IDE's project window; it does not close it.** The report data environments ([[../06-reports/orders.md]], [[../06-reports/listempl.md]]) test `WEXIST(\"Project Manager\")` on the assumption that \"TasTrade closes the Project Manager window\". Whether a deactivated window still satisfies `WEXIST` was not run here; if it does, running the reports from inside the IDE with the project open takes the `HOME() + \"Samples\\Tastrade\\\"` branch.",
                "**Two class-library lists.** `SetPath` sets `MAIN, TSGEN`, just enough to create the object; `environment.Set` immediately replaces that with `MAIN, TSBASE, TSGEN, LOGIN, ORDERS`. `ABOUT` is loaded on demand by the Help menu.",
                "**`SET TALK` is handled before the environment object exists** because `SET TALK ON` would echo everything that follows; the value is passed along as text rather than read with `SET('TALK')` a second time.",
                "**`RIGHT(lcProgram, 3) = \"FXP\"`** is how the program tells IDE from EXE: only a compiled `.prg` run directly reports its own `.FXP` name.",
                "**The 1995 copyright line** is the first line, as in every source file of the sample."])
    return "\n".join(L)


# ------------------------------------------------------------------ utility.prg
def gen_utility():
    r = parse_prg("progs/utility.prg")
    callers = {
        "IsTag": "[[../05-classes/tsbase.md]] `tsifcombo.Init`, to warn when the tag it derived from the `RowSource` does not exist (the comment there: \"SET('PROCEDURE') should include Utility.prg\").",
        "NotYet": "**Nothing.** Grepped every twin, menu, report, and the DBC: no caller. A construction-time placeholder (\"Under Construction\") left in the shipped library.",
        "FileSize": "[[../04-forms/behindsc.md]] `frmbehindsc.procstomem`, to size the file that `COPY PROCEDURES TO` wrote before reading it back with `FREAD`.",
        "FormIsObject": "[[../05-classes/tsbase.md]] `tstoolbar.oktosend`, `tstoolbar.Refresh`, `tstoolbar.cmdClose.Click`; [[../04-forms/behindsc.md]] `frmbehindsc.Load`; and the `SKIP FOR` conditions of the File, Navigation, and Items menus ([[../07-menus/main.md]], [[../07-menus/navigate.md]], [[../07-menus/ordentry.md]]).",
        "ToolBarEnabled": "The `SKIP FOR` conditions of New, Close, Save, and Restore on the File menu ([[../07-menus/main.md]]) only.",
        "OnShutdown": "`ON SHUTDOWN DO OnShutDown`, set by `environment.Set` ([[../05-classes/tsgen.md]]) and restored to the previous handler by `environment.Reset`.",
    }
    explain = {
        "IsTag": "Walks `TAG(n, alias)` until it runs out, comparing upper-cased trimmed names. **NOTE:** `lnTagNum` is not `LOCAL`, so it is created as a private variable visible to anything called below it. The `EMPTY(tcAlias)` check returns `.F.` rather than erroring when no table is open.",
        "NotYet": "Shows \"Under Construction\" (`NOTYET_LOC`). Dead, see above.",
        "FileSize": "`FSIZE()` returns a field's size unless `SET COMPATIBLE` is `ON`, so the function flips it on around the call and puts it back. **NOTE:** `&lcSetCompatible` macro substitution.",
        "FormIsObject": "True when `_screen.ActiveForm` is an object whose base class is a form; false for toolbars and for no window at all. The test every menu `SKIP FOR` and toolbar refresh starts with.",
        "ToolBarEnabled": "Builds the name `oApp.oToolBar.<button>.enabled` as text and evaluates it, returning `.F.` if the path does not resolve to a logical (no toolbar, no such button). Old-style `PARAMETER` rather than `LPARAMETERS`, so `oObject` is private; the body spells it `oobject`, which VFP does not mind.",
        "OnShutdown": "Shows \"Cannot quit Visual FoxPro within Tasmanian Traders.\" A shutdown handler that does not itself `QUIT` cancels the close, so this is what stops the user closing VFP with the application running; the only way out is the menu's Return to Visual FoxPro.",
    }
    L = head("progs/utility.prg", "Program", "utility.prg",
             "The procedure file: six standalone functions (index-tag test, a placeholder, file size, active-form test, toolbar-button test, shutdown guard) kept outside the classes, as its header says, \"for better performance and accessibility\".",
             ["`environment.Set` in [[../05-classes/tsgen.md]]: `SET PROCEDURE TO UTILITY.PRG`, found through the `PROGS` entry of `SET PATH`; `environment.Reset` restores the previous procedure file on exit. Individual callers are listed per function below."],
             "[[../05-classes/tsbase.md]] (`tsifcombo`, `tstoolbar`), [[../04-forms/behindsc.md]], [[../07-menus/main.md]] and [[../07-menus/navigate.md]] and [[../07-menus/ordentry.md]] (menus whose `SKIP FOR` conditions call in here), [[tastrade.h.md]], [[main.md]], [[README.md]].")
    L += ["## Role", "",
          "**Runtime library.** Loaded by `SET PROCEDURE` for the life of the application; five of its six functions have callers. `NotYet()` is dead and can go.", ""]
    L += ["## What it does", "",
          "Nothing at the top level beyond `#INCLUDE \"INCLUDE\\TASTRADE.H\"`, needed for `NOTYET_LOC`, `CANNOTQUIT_LOC`, `TASTRADE_LOC`, and the `MB_*` constants. The functions:", "",
          "| Function | Parameters | Returns | Called from |", "|---|---|---|---|"]
    for rt in r["routines"]:
        L.append("| `%s` | `%s` | %s | %s |" % (rt["name"], rt["params"] or "", {
            "IsTag": "`.T.` if the tag exists in the alias", "NotYet": "nothing", "FileSize": "bytes",
            "FormIsObject": "`.T.` if the active window is a form", "ToolBarEnabled": "the button's `Enabled`, or `.F.`",
            "OnShutdown": "nothing"}[rt["name"]], callers[rt["name"]]))
    L += ["", "## Key routines", ""]
    for rt in r["routines"]:
        L += ["#### `%s %s(%s)`" % (rt["kind"], rt["name"], rt["params"]), "", explain[rt["name"]], "", fence(rt["body"]), ""]
    L += ["## Inputs / outputs / side effects", "",
          "- Reads the open table's index tags (`IsTag`), a file on disk (`FileSize`, through `FSIZE()`), the active form and the global `oApp` (`FormIsObject`, `ToolBarEnabled`).",
          "- Writes nothing. `FileSize` toggles `SET COMPATIBLE` and puts it back; `NotYet` and `OnShutdown` show message boxes.",
          "- Expects `oApp` to be the application object ([[../05-classes/main.md]]) and `_screen.ActiveForm` to be meaningful; both are true only inside the running application.", ""]
    L += ["## Called from / calls", "",
          "- **Called from:** see the table above; the file is on the procedure chain, so any code in the application can call these by name.",
          "- **Calls:** VFP functions only (`TAG`, `FSIZE`, `TYPE`, `EVAL`, `MESSAGEBOX`); no other program, form, or class.", ""]
    L += notes(["**One dead function** (`NotYet`), whose string `NOTYET_LOC` is in turn used by nothing else ([[strings.h.md]]).",
                "**`FormIsObject` is the sample's most-called helper**: three toolbar methods, one form, and nine menu bars depend on it.",
                "**Private-variable leak** in `IsTag` (`lnTagNum`), and old-style `PARAMETER` in `ToolBarEnabled`; the rest of the sample uses `LOCAL` and `LPARAMETERS`.",
                "**`OnShutdown` is a guard, not a cleanup**: it blocks the close and tells the user to exit through the menu. With `DEBUGMODE` on, `SET ESCAPE` is also left on ([[tastrade.h.md]]), so Esc can still interrupt code.",
                "**Comment header** says the functions are \"independent of any classes\"; two of them read `oApp` and `_screen.ActiveForm`."])
    return "\n".join(L)


# ------------------------------------------------------------------ include files
def define_table(defs, value_col="Value"):
    L = ["| Constant | %s | Comment | Used by |" % value_col, "|---|---|---|---|"]
    for d in defs:
        L.append("| `%s` | `%s` | %s | %s |" % (d["name"], d["value"].replace("|", "\\|"), d["comment"].replace("|", "\\|"), users_cell(d["users"])))
    return L


def gen_tastrade_h():
    r = parse_h("include/tastrade.h")
    unused = [d["name"] for d in r["defines"] if not d["users"]]
    L = head("include/tastrade.h", "Include file", "tastrade.h",
             "The application's main include file: pulls in VFP's `FOXPRO.H` and the localizable strings of [[strings.h.md]], then defines the `DEBUGMODE` switch, the INI file name, whitespace constants, the record-status and trigger codes the base form uses, registry keys for the About box, the user-level names the menu gates on, and a few strings.",
             ["Every form (`#INCLUDE \"..\\include\\tastrade.h\"` in all 17 `.sc2`), every class library (in 5 of 6; `orders.vc2` once, `tsbase.vc2` and `tsgen.vc2` several times because each class carries its own line), the three menus with code ([[../07-menus/main.md]], [[../07-menus/navigate.md]], [[../07-menus/window.md]]), both programs ([[main.md]], [[utility.md]]), the DBC's stored procedures ([[../03-data-model/README.md]], `#INCLUDE INCLUDE\\TASTRADE.H`), and one report data environment ([[../06-reports/orders.md]]; [[../06-reports/listempl.md]] lacks it and errors for it).",
              "The project (`tastrade.pj2`) lists it as a text file, excluded from the build, described as \"The main include file for this application\"."],
             "[[strings.h.md]], [[main.md]], [[utility.md]], [[../05-classes/tsgen.md]] (`environment.Set`, the `DEBUGMODE` site that matters most), [[../05-classes/main.md]], [[../05-classes/tsbase.md]], [[../07-menus/main.md]] (`ADMINBAR_LOC`, `USER_*_LOC`), [[README.md]].")
    L += ["## Role", "", "**Runtime constants, compiled into every artifact that includes it.** Not a program; nothing runs. The `Used by` column below is a case-sensitive whole-word grep over every twin, `.mpr`, `.prg`, and the DBC twin; %d of the %d constants have no user." % (len(unused), len(r["defines"])), ""]
    L += ["## Includes", "", fence("\n".join(r["includes"])), "",
          "`FOXPRO.H` is VFP's own header (the `MB_*` message-box constants, `IDYES`/`IDABORT`, `COLOR_*`, and the rest), resolved from the VFP home directory at compile time. `STRINGS.H` is [[strings.h.md]], resolved relative to this file. Three spellings of the path to this file exist in the sources: `..\\include\\tastrade.h` in forms and classes, `INCLUDE\\TASTRADE.H` in programs, menus, and the invoice report, and `INCLUDE\\TASTRADE.H` unquoted in the stored procedures.", ""]
    L += ["## Constants", ""] + define_table(r["defines"]) + [""]
    sites = ["`tastrade.Do` ([[../05-classes/main.md]]): `IF !DEBUGMODE` around the startup action from `user_level.startup_action`, so the Customer Service Rep's automatic order entry form never opens.",
             "`tastrade.Init` ([[../05-classes/main.md]]): `IF !DEBUGMODE` around `this.Login()`; the debug branch sets `cEmployeeID` to empty and `cUserLevel` to `USER_APPDEV_LOC`. Consequences: no login, an empty employee ID that defeats the delete guard in [[../04-forms/employee.md]] and puts [[../04-forms/chngpswd.md]] on the first record, and the developer level that keeps every menu pad ([[../07-menus/main.md]]).",
             "`tsbaseform.Error` ([[../05-classes/tsbase.md]]), twice: a `WAIT WINDOW` when a table rule fails (error 1583), and `SUSPEND` instead of `oApp.Cleanup` / `CANCEL` when the user picks Abort on an unhandled error.",
             "`environment.Set` ([[../05-classes/tsgen.md]]): `SET ESCAPE ON` instead of `OFF`, so Esc interrupts running code."]
    L += ["## `DEBUGMODE`", "",
          "Shipped as `.T.`. Five `#IF`-style sites read it (`IF DEBUGMODE` / `IF !DEBUGMODE`; the value is compiled in, so flipping it means rebuilding everything that includes this file):", ""] + ["%d. %s" % (i + 1, s) for i, s in enumerate(sites)] + ["",
          "There is no `#IF DEBUGMODE` anywhere: the switch is always evaluated at run time from a compiled-in literal.", ""]
    L += notes(["**Unused constants:** %s. `CURRENCY` and the `SYS2011_*` lock-status strings look like abandoned features; `KEY_WIN4_MSINFO` is a registry path the About box never reads (it reads `KEY_SHARED_TOOLS_LOCATION`, `KEY_NTCURRENTVERSION`, and `KEY_WIN4CURRENTVERSION`); `DOLLAR_FORMAT1_LOC` is the odd one out of three." % ", ".join("`%s`" % u for u in unused),
                "**Localizable strings in the wrong file.** `ADMINBAR_LOC`, `ALL_LOC`, `USER_APPDEV_LOC`, `USER_OPSMGR_LOC`, `DOLLAR_FORMAT*_LOC`, `SEEKVALUE_LOC`, and the `SYS2011_*_LOC` names carry the `_LOC` suffix that marks translatable text, but live here rather than in [[strings.h.md]], whose header says it is the file to localize.",
                "**`USER_APPDEV_LOC` and `USER_OPSMGR_LOC` must match `user_level.description` upper-cased** ([[../03-data-model/tables/user_level.md]]: \"Applications Developer\", \"Operations Manager\"); the menu compares `UPPER(oApp.GetUserLevel())` against them. Translating the strings without changing the data, or the reverse, silently removes the gating.",
                "**`ADMINBAR_LOC` names a popup that does not exist** (the Administration popup is `_qx713dsus`), see [[../07-menus/main.md]].",
                "**`SEEKVALUE_LOC` (`\"*Case Study\"`) duplicates the filter literal** stored in `reports/casestdy.frx`'s cursor ([[../06-reports/casestdy.md]]); the form uses the constant, the report the literal.",
                "**`HKEY_LOCAL_MACHINE` as `-2147483646`** is `0x80000002` written as a signed 32-bit integer, which is what the `RegOpenKeyEx` declaration in [[main.md]] takes.",
                "**`I_SHPMIN` / `I_SHPMAX`** are the pixel limits of the Behind the Scenes splitter ([[../05-classes/tsgen.md]] `splitter`); layout numbers in an include file.",
                "**`AERRORARRAY 7`** is the column count of `AERROR()`'s array, used to `DIMENSION` it before the call in eight places."])
    return "\n".join(L)


def gen_strings_h():
    r = parse_h("include/strings.h")
    unused = [d["name"] for d in r["defines"] if not d["users"]]
    L = head("include/strings.h", "Include file", "strings.h",
             "Every user-visible string of the application as a `_LOC` constant, \"for localization purposes\": message-box titles and texts, the names of VFP's toolbar windows, trigger-failure messages, button captions, and the version and copyright shown in the About box.",
             ["[[tastrade.h.md]] (`#INCLUDE \"STRINGS.H\"`), and through it everything that includes that file. No source includes this file directly.",
              "The project lists it as a text file, excluded from the build, described as \"Strings used in app (for localization)\"."],
             "[[tastrade.h.md]], [[../05-classes/tsgen.md]] (`releasetoolbars`, which hides VFP's toolbars by the `TB_*` names), [[../05-classes/tsbase.md]] (`tsbaseform.Error`, the trigger messages), [[../03-data-model/README.md]] (stored procedures use the credit-limit strings), [[../07-menus/main.md]] and [[../07-menus/intro.md]] (the About boxes), [[README.md]].")
    L += ["## Role", "", "**Runtime constants.** Nothing runs. %d constants in %d sections; the `Used by` column is a case-sensitive whole-word grep over every twin, `.mpr`, `.prg`, and the DBC twin, and %d constants have no user." % (len(r["defines"]), len({d["section"] for d in r["defines"]}), len(unused)), ""]
    L += ["## Constants", ""]
    cur = None
    for d in r["defines"]:
        if d["section"] != cur:
            cur = d["section"]
            L += ["", "### %s" % (cur or "(no section)"), "", "| Constant | Text | Comment | Used by |", "|---|---|---|---|"]
        L.append("| `%s` | %s | %s | %s |" % (d["name"], d["value"].replace("|", "\\|"), d["comment"].replace("|", "\\|"), users_cell(d["users"])))
    L += [""]
    L += notes(["**Unused constants:** %s. `ASKDELETE_LOC` and `DELETEREC_LOC` say the same thing; only the second is used. `AVAILABLECREDIT_LOC` and `CUSTNOORD_LOC` belong to features the order entry form does differently now." % ", ".join("`%s`" % u for u in unused),
                "**The toolbar names are a hidden dependency on an English VFP.** `environment.ReleaseToolBars` ([[../05-classes/tsgen.md]]) hides the IDE's toolbars by window title (\"Form Designer\", \"Standard\", ..., \"Command\"); on a localized VFP the titles differ and nothing is hidden. Localizing this file would not fix that, since the strings must match VFP's, not the user's language.",
                "**Typo shipped:** `CUSTOVERMAX_LOC` reads \"maximimun\".",
                "**Two constants, one text:** `VIEWCODEPRINT_LOC` and `VIEWCSDTYPRINT_LOC` are both \"This report may be lengthy. Do you want to continue?\", used by the code viewer and the case study / Behind the Scenes prints respectively.",
                "**Version and copyright** (`VERSION_LOC` \"1.1\", `COPYRIGHT_LOC` \"Copyright 1996 Microsoft Corporation\") are read only by the main menu's About box; the intro menu's About box hard-codes \"1.0\" and 1994 ([[../07-menus/intro.md]]). The project's own header says 1995.",
                "**Not everything is here.** Menu prompts and status text ([[../07-menus/README.md]]), the intro menu's About strings, form captions, and grid headers are literals in the `.mnx`, `.scx`, and `.vcx` files; the file localizes messages, not the UI.",
                "**Credit-limit messages are assembled in the stored procedures** (`CUSTOVERMAX_LOC`, `CUSTUNDERMIN_LOC`, `SAVEANYWAY_LOC` with the `DOLLAR_FORMAT*` constants from [[tastrade.h.md]]), so the DBC, not just the forms, depends on this file at compile time."])
    return "\n".join(L)


# ------------------------------------------------------------------ index
def gen_readme():
    nt = len([d for d in parse_h("include/tastrade.h")["defines"] if not d["users"]])
    ns = len([d for d in parse_h("include/strings.h")["defines"] if not d["users"]])
    L = ["# Programs and include files", "",
         "Two programs in `progs/` and two include files in `include/`, all native VFP text read directly (no twin, no parser); routine, declaration, and `#DEFINE` counts were checked against a raw grep, and every constant's users were found with a case-sensitive whole-word grep over the twins, the `.mpr` files, the programs, and the DBC twin.", "",
         "| File | Role | Doc |", "|---|---|---|",
         "| `progs/main.prg` | Runtime entry point (project main file): API declarations, environment save, `SetPath()`, `CREATEOBJECT(\"TasTrade\")`, `oApp.Do()`, cleanup | [[main.md]] |",
         "| `progs/utility.prg` | Runtime library (`SET PROCEDURE`): `IsTag`, `NotYet` (dead), `FileSize`, `FormIsObject`, `ToolBarEnabled`, `OnShutdown` | [[utility.md]] |",
         "| `include/tastrade.h` | Main include file: `FOXPRO.H` + `STRINGS.H`, `DEBUGMODE`, INI name, status and trigger codes, registry keys, user-level names | [[tastrade.h.md]] |",
         "| `include/strings.h` | Localizable strings, 86 `_LOC` constants | [[strings.h.md]] |", "",
         "## Startup sequence", "",
         "`tastrade.exe` → `progs/main.prg` → `SetPath()` → `CREATEOBJECT(\"TasTrade\")` ([[../05-classes/main.md]]) → `application.Init` (adds `environment`, whose `Set` loads `utility.prg`, the five class libraries, and the help file; opens the DBC; hides VFP's toolbars; pushes the system menu) → `tastrade.Init` (intro menu, intro form, login or the `DEBUGMODE` bypass) → `oApp.Do()` (main menu, optional startup action, `READ EVENTS`) → Return to Visual FoxPro (`CLEAR EVENTS`) → `Cleanup`, `Cleanup2` → back in `main.prg`: `CLEAR DLLS`, `RELEASE ALL EXTENDED`, `CLEAR ALL` → `environment.Destroy` restores every setting. The full picture with the menus is in [[../07-menus/README.md]]; the architecture page will draw it.", "",
         "## Include chain", "",
         "`FOXPRO.H` (VFP's) → `strings.h` → `tastrade.h` → every form, class library, code-bearing menu, program, the stored procedures, and one of the two reports with data environment code. The other report, `listempl.frx`, forgot it ([[../06-reports/listempl.md]]). `DEBUGMODE` is compiled into all of them, so changing it is a full rebuild.", "",
         "## Findings", "",
         "- **`DEBUGMODE = .T.` is compiled in at five sites** and shipped on: no login, no startup action, developer user level for everyone, `SET ESCAPE ON`, and `SUSPEND` on Abort. The dead delete guard, the wrong-record Change Password, and the missing menu gating all follow from the second site.",
         "- **%d constants are defined and never used** (%d in `tastrade.h`, %d in `strings.h`), and one function, `NotYet()`, is called by nothing." % (nt + ns, nt, ns),
         "- **Localizable strings are split across two files**, and the menus' text is in neither.",
         "- **The environment hides VFP's toolbars by their English window titles**, a dependency on the IDE's language, not the application's.",
         "- **`main.prg` declares six Win32 API functions for the classes** (INI read/write for the intro flag and window positions; three registry calls and a `win.ini` lookup for the About box) and calls none itself.",
         "- **`main.prg` hides the Project Manager window while the reports assume it is closed**; the two disagree on the same window.",
         "- One typo (\"maximimun\"), one duplicated message, one leaked private variable, one old-style `PARAMETER`.",
         ""]
    return "\n".join(L)


GENERATORS = (("main.md", gen_main), ("utility.md", gen_utility), ("tastrade.h.md", gen_tastrade_h),
              ("strings.h.md", gen_strings_h), ("README.md", gen_readme))

if __name__ == "__main__":
    for fn, gen in GENERATORS:
        with open(os.path.join(OUT, fn), "w", encoding="utf-8", newline="\n") as f:
            f.write(gen())
        print("wrote", fn)
