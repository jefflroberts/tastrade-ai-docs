"""Generate docs/07-menus/*.md and its index from the five .mn2 twins.

Structure (pads, bars, keys, SKIP FOR, actions, procedures, setup and cleanup
code) comes from foxparse.parse_mn2; purpose, launch points, and notes are
hand-written strings below, each checked against a grep of the twins and the
code that runs the menus. Rerun after editing; never hand-edit the output.
"""
import os, sys, textwrap
sys.path.insert(0, os.environ.get("VFP_TOOLKIT_TOOLS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "vfp-documentation-toolkit", "tools")))
import foxparse as fp

ROOT = os.environ.get("TASTRADE_ROOT", os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))
OUT = os.path.join(ROOT, "docs", "07-menus")
os.makedirs(OUT, exist_ok=True)


def fence(code):
    return "```foxpro\n" + textwrap.dedent(code).strip("\n") + "\n```"


def prompt(p):
    return p.replace("\\<", "")


def key(k):
    # KEY CTRL+N, "Ctrl+N"  ->  Ctrl+N
    if "," in k:
        k = k.split(",", 1)[1].strip()
    return k.strip('"')


def load(stem):
    return fp.parse_mn2(os.path.join(ROOT, "menus", stem + ".mn2"))


def head(stem, title, purpose, used_by, related):
    return ["# %s (%s.mnx)" % (title, stem), "", "| Source file | Type | Path |", "|---|---|---|",
            "| `%s.mnx` | Menu | `menus/%s.mn2` |" % (stem, stem), "", "**Purpose:** " + purpose, "",
            "**Used by:**"] + ["- " + u for u in used_by] + ["", "**Related docs:** " + related, ""]


def structure(r, pad_notes):
    L = ["## Menu structure", "",
         "Menu type %s, location `%s`." % (r["menu_type"], r["location"]), ""]
    for p in r["pads"]:
        L += ["### Pad: %s  (`%s`)" % (prompt(p["prompt"]), p["name"]), ""]
        bits = []
        if p["key"]:
            bits.append("hot key %s" % key(p["key"]))
        if p["skip_for"]:
            bits.append("`SKIP FOR %s`" % p["skip_for"])
        if p["message"]:
            bits.append("status text \"%s\"" % p["message"])
        if p["popup"]:
            bits.append("popup `%s`" % p["popup"])
        if p["comment"]:
            bits.append("designer comment `%s`" % p["comment"])
        if bits:
            L += ["; ".join(bits) + ".", ""]
        if pad_notes.get(p["name"].lower()):
            L += [pad_notes[p["name"].lower()], ""]
        if p.get("popup_on_selection"):
            L += ["Popup-level handler: `ON SELECTION POPUP %s %s`." % (p["popup"], p["popup_on_selection"]), ""]
        L += ["| Bar | Prompt | Shortcut | Skip For | Action |", "|---|---|---|---|---|"]
        for b in p["bars"]:
            if b["separator"]:
                L.append("| `%s` | (separator) |  |  | %s |" % (b["id"], ("empty cascading popup `%s` in the twin only" % b["submenu"]) if b["submenu"] else ""))
                continue
            act = ("`%s`" % b["action"]) if b["action"] else ("VFP system bar" if b["system"] else "none")
            if b["submenu"]:
                act += "; cascades to `%s`" % b["submenu"]
            L.append("| `%s` | %s | %s | %s | %s |" % (b["id"], prompt(b["prompt"]), key(b["key"]),
                                                      ("`%s`" % b["skip_for"]) if b["skip_for"] else "", act))
        L.append("")
    L += ["Menu-level handler: `%s` (a comment, so a no-op; the same line closes every menu in the sample)." % r["on_selection_menu"], ""]
    return L


def code_section(r, explain):
    L = ["## Setup / cleanup code", ""]
    if r["setup_code"]:
        L += ["Setup code:", "", fence(r["setup_code"]), ""]
        if explain.get("setup"):
            L += [explain["setup"], ""]
    else:
        L += ["No setup code.", ""]
    for name, body in r["procedures"].items():
        L += ["Procedure `%s`:" % name, ""]
        if explain.get(name):
            L += [explain[name], ""]
        L += [fence(body), ""]
    if r["cleanup_code"]:
        L += ["Cleanup code (runs after the definitions):", ""]
        if explain.get("cleanup"):
            L += [explain["cleanup"], ""]
        L += [fence(r["cleanup_code"]), ""]
    else:
        L += ["No cleanup code.", ""]
    return L


def launches(items):
    return ["## What it launches", ""] + ["- " + i for i in items] + [""]


def notes(items):
    return ["## Notes", ""] + ["- " + i for i in items] + [""]


TWIN_NOTE = "**Twin versus `.mpr`.** The twin is FoxBin2PRG's rendering of the `.mnx`; `menus/%s.mpr` is GENMENU's output dated 10/12/00. They match statement for statement apart from formatting, the generated procedure names (`_07y0s8...` there, `BAR_n_OF_popup_FB2P` here), %s and the empty cascading popup the twin emits for each separator, which the `.mpr` does not have."


# ------------------------------------------------------------------ main
def gen_main():
    r = load("main")
    L = head("main", "Main menu",
             "The application's menu bar: File (record actions, reports, exit), Edit, Orders, Administration (login and the six maintenance forms), Utilities (VFP debugging windows and reindex), and Help. It replaces the VFP system menu for the life of the application.",
             ["`tastrade.Do` in [[../05-classes/main.md]]: `DO (this.cMainMenu)` with `cmainmenu = MAIN.MPR` inherited from `application` in [[../05-classes/tsgen.md]], right after `Init` has shown the intro form and logged the user in.",
              "The Login bar's own procedure, through `oApp.DoMenu()`, whenever a re-login changes the user level: the menu is defined again and its cleanup code re-applies the privilege gating."],
             "[[../05-classes/tsgen.md]] (`application`: `Init` pushes the system menu, `Cleanup2` pops it), [[../05-classes/main.md]], [[../05-classes/tsbase.md]] (`tstoolbar`, whose buttons the File bars click), [[../08-programs/utility.md]] (`FormIsObject()`, `ToolBarEnabled()`), [[navigate.md]], [[ordentry.md]], [[window.md]], [[intro.md]], [[README.md]].")
    L += ["This is the primary navigation. `application.Init` does `PUSH MENU _MSYSMENU` before any menu runs and `Cleanup2` does `POP MENU _MSYSMENU TO MASTER`, so the VFP menu comes back when the application ends. Between those, this menu is defined with location `REPLACE`, which the 2001 `.mpr` renders as `SET SYSMENU TO` and `SET SYSMENU AUTOMATIC`.", ""]
    L += structure(r, {
        "pad": "Every record action calls the corresponding button of the shared navigation toolbar ([[../05-classes/tsbase.md]] `tstoolbar`) and is skipped unless a form is active and that button is enabled, so the menu is a keyboard front for the toolbar. Delete is the exception: it calls the form's `delete` method directly and checks the form's `lAllowDelete`.",
        "edit": "Every bar is a VFP system bar (`_med_*`), so undo, cut, copy, paste, and select-all are VFP's own with no code in the sample.",
        "orders": "Order Entry is single-instance (`WEXIST` of the form's name); Order History has no skip condition and opens as many instances as asked, see [[../04-forms/ordhist.md]].",
        "_msm_file": "The pad is named `_msm_file`, the VFP system name for the File pad, so that the Navigation and Window pads, which the designer placed `AFTER _MFILE`, land after Administration ([[navigate.md]], [[window.md]]). Login and Change Password are skipped while any window is on top; each maintenance form is single-instance by `WEXIST` of its class name.",
        "utilities": "Trace, Debug, View, Command, Resume, and Cancel are VFP system bars (`_MWI_*`, `_MPR_*`); Suspend runs the `SUSPEND` command. The whole pad is meant for developers only: the cleanup code below removes it for every other user level.",
        "_msm_systm": "The pad is named `_msm_systm`, VFP's system Help pad, and Contents / Search are the system bars `_mst_help` / `_mst_hpsch`, so they open the help file that `environment.Set` selects with `SET HELP TO HELP\\TASTRADE.CHM` ([[../05-classes/tsgen.md]]).",
    })
    L += code_section(r, {
        "setup": "The include file supplies `USER_APPDEV_LOC`, `USER_OPSMGR_LOC`, `ADMINBAR_LOC` (from `include/tastrade.h`) and the About box strings (from `include/strings.h`).",
        "BAR_9_OF_File_FB2P": "Print Setup: VFP's page setup dialog, `SYS(1037)`, with every error suppressed by `ON ERROR *` and the previous handler restored by macro. **NOTE:** `&lcOldError` macro substitution.",
        "BAR_11_OF_File_FB2P": "Return to Visual FoxPro: `CLEAR EVENTS` ends the `READ EVENTS` loop in `application.Do`, whose next lines call `Cleanup` and `Cleanup2`.",
        "BAR_1_OF__qx713dsus_FB2P": "Login: runs the login dialog again through `oApp.Login()` ([[../05-classes/main.md]], which shows `loginpicture` from [[../05-classes/login.md]]) and, if the user level changed, re-runs this whole menu so the cleanup code can re-apply the gating.",
        "BAR_4_OF_Help_FB2P": "About: loads `about.vcx`, builds the box from the `_LOC` constants (\"Tasmanian Traders\", \"1.1\", \"Copyright 1996 Microsoft Corporation\", \"All rights reserved\") and `BITMAPS\\TTRADESM.BMP`, then releases the library ([[../05-classes/about.md]]).",
        "cleanup": "This is the application's only privilege gating. Non-developers lose the Utilities pad. Users below Operations Manager are meant to lose Login, Change Password, and the separator. **NOTE:** `ADMINBAR_LOC` is `\"Administration\"`, but the Administration popup was never named in the designer and is `_qx713dsus` in both this twin and the 2001 `.mpr`, so the three `RELEASE BAR` lines address a popup that does not exist; they error or do nothing, and either way the bars stay. **NOTE:** under `DEBUGMODE` ([[../05-classes/main.md]] `Init` sets the level to Applications Developer without a login) neither branch runs, so the shipped build shows every user the Utilities pad, including the Command window (Ctrl+F2), Debug, Trace, Suspend, and Cancel.",
    })
    L += launches(["Print Reports: `DO FORM Reports`, [[../04-forms/reports.md]] (the only route to the ten picker reports in [[../06-reports/README.md]]).",
                   "Order Entry / Order History: [[../04-forms/ordentry.md]], [[../04-forms/ordhist.md]].",
                   "Change Password: [[../04-forms/chngpswd.md]]. Login: [[../05-classes/login.md]] via `oApp.Login()`.",
                   "Customers, Categories, Employees, Shippers, Suppliers, Products: [[../04-forms/customer.md]], [[../04-forms/category.md]], [[../04-forms/employee.md]], [[../04-forms/shipper.md]], [[../04-forms/supplier.md]], [[../04-forms/product.md]], all through `oApp.DoForm`.",
                   "Behind the Scenes: [[../04-forms/behindsc.md]] (`oApp.DoForm(\"behindsc\")`, without the `.T.` parameter the intro form passes).",
                   "Rebuild DBC/Reindex: [[../04-forms/rebuild.md]].",
                   "About: [[../05-classes/about.md]]. Help Contents / Search: `help/tastrade.chm` through VFP's system bars."])
    L += notes([TWIN_NOTE % ("main", "the `SET SYSMENU` pair that the `REPLACE` location generates,"),
                "**Daily use versus administration.** File, Edit, Orders, and the maintenance half of Administration are the working menu; Login, Change Password, Utilities, and Rebuild are administrative and are the only items the cleanup code gates.",
                "**Keyboard map.** Pads Alt+F/E/O/A/U/H; New Ctrl+N, Save Ctrl+S, Restore Ctrl+E, Print Reports Ctrl+P; Edit Ctrl+Z/R/X/C/V/A; Command window Ctrl+F2. First/Prior/Next/Last shortcuts live in [[navigate.md]].",
                "**Status-bar text** for every pad and bar is in the `MESSAGE` clauses above; there are no `_LOC` constants for prompts or messages, so the menu is not localized the way the forms' strings are.",
                "**`*-RELEASE BAR 1 OF Window`** at the top of the cleanup code is a commented-out remnant of the placeholder trick now done in [[window.md]].",
                "**The copyright line is the menu's `ON SELECTION MENU` command**: `ON SELECTION MENU _MSYSMENU *-- (c) Microsoft Corporation 1995`. Because the command is a comment it does nothing; it is where the sample keeps its copyright notice in every menu.",
                "**Behind the Scenes lives under Administration** and is gated by nothing, unlike Utilities."])
    return "\n".join(L)


# ------------------------------------------------------------------ intro
def gen_intro():
    r = load("intro")
    L = head("intro", "Intro menu",
             "The two-pad menu (File: Return to Visual FoxPro; Help) shown while the intro screen is up, before login.",
             ["`tastrade.Init` in [[../05-classes/main.md]]: `DO menus\\intro.mpr` right after `application.Init` succeeds and before the intro form ([[../05-classes/tsgen.md]] `introform`) is shown. It runs whether or not the INI setting `ShowIntroForm` suppresses the form; `tastrade.Do` then replaces it with [[main.md]]."],
             "[[../05-classes/tsgen.md]] (`introform`, whose `close` method the File bar calls), [[../05-classes/main.md]], [[../05-classes/about.md]], [[main.md]], [[README.md]].")
    L += structure(r, {
        "pad": "Return to Visual FoxPro calls `_screen.activeform.Close()`; `introform.close` is `thisform.cmdExit.Click()`, so it is the same as the intro form's Exit button. The popup-level handler below is dead: a bar with its own `ON SELECTION BAR` is not passed to `ON SELECTION POPUP`.",
        "help": "Contents has F1 here (the main menu's does not). Contents and Search are VFP system bars.",
    })
    L += code_section(r, {
        "File_FB2P": "A generic dispatcher that calls a method of the active form named after the bar's prompt (`Prompt()`), with a special case renaming \"New\" to `AddNew`. Nothing reaches it: the only bar has its own handler. The comment records a VFP bug from the sample's first release that forced the `AddNew` rename, and the code shows this menu once had record-action bars like the main menu's. **NOTE:** `&lcCmd` macro substitution.",
        "BAR_4_OF_Help_FB2P": "**NOTE:** a second About box with different facts from the main menu's: version \"1.0\" and \"Copyright 1994 Microsoft Corporation\" hard-coded here against `VERSION_LOC` \"1.1\" and `COPYRIGHT_LOC` \"Copyright 1996 Microsoft Corporation\" there, and the logo `BITMAPS\\SMSWIRLT.BMP`, which is not in `bitmaps/` (the main menu uses `TTRADESM.BMP`, which is). `about.vcx` is loaded by path here and by name there. There is no setup code, so no include file could have supplied the constants.",
    })
    L += launches(["Return to Visual FoxPro: `introform.close` → `cmdExit.Click` ([[../05-classes/tsgen.md]]).",
                   "About: [[../05-classes/about.md]] with the 1994 strings. Help: `help/tastrade.chm` through the system bars, once `environment.Set` has run."])
    L += notes([TWIN_NOTE % ("intro", "the `SET SYSMENU` pair that the `REPLACE` location generates,"),
                "**Nothing here is gated**; the user has not logged in yet.",
                "**The copyright line is the menu's `ON SELECTION MENU` command**, as in every menu of the sample."])
    return "\n".join(L)


# ------------------------------------------------------------------ navigate
def gen_navigate():
    r = load("navigate")
    L = head("navigate", "Navigation menu",
             "One pad, Navigation, with First / Prior / Next / Last and their Ctrl+Home / PgUp / PgDn / End shortcuts; each bar clicks the matching button of the shared navigation toolbar.",
             ["`application.ShowNavToolBar` in [[../05-classes/tsgen.md]]: `DO navigate.mpr` after creating and showing the toolbar, for the first `tsbaseform` instance only (the call comes from `tsbaseform.Init` in [[../05-classes/tsbase.md]] when the form has a `cToolBar`).",
              "Removed by `application.ReleaseNavToolBar` when the last such form closes: `RELEASE POPUP navigation EXTENDED` and `RELEASE PAD _msm_edit OF _msysmenu`."],
             "[[../05-classes/tsgen.md]], [[../05-classes/tsbase.md]] (`tstoolbar`), [[main.md]] (the bar it is inserted into), [[ordentry.md]] (the pad placed after this one), [[window.md]], [[README.md]].")
    L += structure(r, {
        "_msm_edit": "Each bar is skipped unless a form is active, the toolbar object exists, and the matching button is enabled, so the menu mirrors the toolbar's state. The pad is named `_msm_edit` (VFP's system name for the Edit pad) for the reason the designer comment gives: the order entry form's Items pad is placed `AFTER _MEDIT`, and this name makes it land here rather than after the main menu's Edit pad, which is named `Edit`.",
    })
    L += code_section(r, {"setup": "The include file is not used by anything in this menu."})
    L += launches(["`oApp.oToolbar.cmdFirst/cmdPrior/cmdNext/cmdLast.Click()`: the `tstoolbar` buttons in [[../05-classes/tsbase.md]], which act on `_screen.ActiveForm` through the base form's navigation methods."])
    L += notes(["**No `.mpr` in the repo.** `navigate.mnx` and `window.mnx` have no generated program beside them, unlike the other three; the built `tastrade.exe` contains this menu's status text, so the VFP build generated the code itself. The `.pj2` has descriptions for the other three menus and none for these two.",
                "**Placement by system names.** Location `AFTER _MFILE` puts the pad after the pad VFP knows as the File pad, and the main menu gave that name, `_msm_file`, to its Administration pad ([[main.md]]). Read together with `tsbaseform.Init`, which adds the Window pad (also `AFTER _MFILE`) before it shows the toolbar, the resulting bar is File, Edit, Orders, Administration, Navigation, Window, Utilities, Help, with Items after Navigation while order entry is active. Not run here.",
                "**Keyboard map.** Ctrl+Home, Ctrl+PgUp, Ctrl+PgDn, Ctrl+End; pad Alt+N.",
                "**Twin only**: with no `.mpr` there is nothing to cross-check the twin against except the EXE's strings. It has no cascading-popup artifacts because it has no separators.",
                "**The copyright line is the menu's `ON SELECTION MENU` command**, as in every menu of the sample."])
    return "\n".join(L)


# ------------------------------------------------------------------ ordentry
def gen_ordentry():
    r = load("ordentry")
    L = head("ordentry", "Items menu",
             "One pad, Items, with Add Line Item (Ctrl+Ins) and Remove Line Item (Ctrl+Del) for the order entry form's grid; present only while that form is active.",
             ["`frmorderentry.Activate` in [[../04-forms/ordentry.md]]: `DO menus\\ordentry.mpr` on every activation; `Deactivate` and `Destroy` both do `RELEASE PAD orderentry OF _msysmenu`. A `*-DO menus\\ordentry.mpr` in `Load` is commented out."],
             "[[../04-forms/ordentry.md]] (`GridAddItem`, `GridRemoveItem`, and the right-click popup that offers the same two actions), [[../05-classes/orders.md]], [[navigate.md]] (the pad this one is placed after), [[main.md]], [[README.md]].")
    L += structure(r, {
        "orderentry": "The pad itself is skipped unless the order entry form is the top window, and each bar checks the form's `lAllowEdits` / `lAllowDelete`; Remove also requires the active control to be a grid, so it cannot fire while the cursor is in a header field.",
    })
    L += code_section(r, {})
    L += launches(["`_screen.Activeform.GridAddItem()` and `GridRemoveItem()`: methods of the `orderentry` class in [[../05-classes/orders.md]], the same ones the grid's shortcut popup calls."])
    L += notes([TWIN_NOTE % ("ordentry", "the `AFTER _MEDIT` clause, which the `.mpr` writes on the `DEFINE PAD` and the twin keeps in its `MenuLocation` header,"),
                "**Redefined on every activation.** The pad is added each time the form becomes active and released each time it deactivates, so switching between forms rebuilds it; the `.mpr` is small enough that this costs nothing visible.",
                "**Placement.** `AFTER _MEDIT` resolves to the Navigation pad, which is named `_msm_edit` for exactly this purpose ([[navigate.md]]).",
                "**Two ways to reach the same two actions**: this pad with keyboard shortcuts, and the grid's right-click popup built in code ([[../04-forms/ordentry.md]]).",
                "**The copyright line is the menu's `ON SELECTION MENU` command**, as in every menu of the sample."])
    return "\n".join(L)


# ------------------------------------------------------------------ window
def gen_window():
    r = load("window")
    L = head("window", "Window menu",
             "An empty Window pad that the base form class fills at run time with one bar per open form; selecting a bar activates that form's window.",
             ["`tsbaseform.AddToMenu` in [[../05-classes/tsbase.md]]: `DO menus\\window.mpr` when no popup named `Window` exists yet, then `DEFINE BAR n OF Window PROMPT thisform.caption` and `ON SELECTION BAR n OF Window ACTIVATE WINDOW <form name>` (by macro). Called from `tsbaseform.Init` for forms with a `cToolBar`, and by [[../04-forms/behindsc.md]] directly.",
              "`tsbaseform.RemoveFromMenu` releases the form's bar and, when the popup is empty, `RELEASE POPUP window EXTENDED` and `RELEASE PAD window OF _MSYSMENU`; [[../04-forms/ordhist.md]] passes its original caption because it renames itself."],
             "[[../05-classes/tsbase.md]], [[main.md]], [[navigate.md]], [[README.md]].")
    L += structure(r, {
        "window": "The designer needs a bar to save, so the menu carries one placeholder bar, \"This bar will be removed\", and the cleanup code removes it, leaving an empty popup for the forms to fill. The twin also shows an empty cascading popup `Thisbarwil` hanging off the placeholder; the placeholder and the popup are both gone once the cleanup code has run.",
    })
    L += code_section(r, {"setup": "The include file is not used by anything in this menu.",
                          "cleanup": "Deletes the placeholder bar the moment the menu is defined."})
    L += launches(["Nothing of its own. Each bar the forms add runs `ACTIVATE WINDOW <form name>`; the bar numbers come from `CNTBAR()` / `GETBAR()` so they stay unique as forms open and close."])
    L += notes(["**No `.mpr` in the repo**, as for [[navigate.md]]; the EXE contains \"This bar will be removed\", so the build generated it.",
                "**Placement.** `AFTER _MFILE`, which lands after the Administration pad ([[main.md]]) and, because `tsbaseform.Init` adds this pad before it shows the toolbar, ends up to the right of Navigation. Not run here.",
                "**Guarded by `TYPE(\"oApp\") == \"O\"`** in both `AddToMenu` and `RemoveFromMenu`, so a form run outside the application skips the Window menu.",
                "**The copyright line is the menu's `ON SELECTION MENU` command**, as in every menu of the sample."])
    return "\n".join(L)


# ------------------------------------------------------------------ index
def gen_readme():
    rows = [("main", "Main menu", "File, Edit, Orders, Administration, Utilities, Help", "`REPLACE`", "`tastrade.Do`; again from the Login bar", "yes"),
            ("intro", "Intro menu", "File, Help", "`REPLACE`", "`tastrade.Init`, before the intro form", "yes"),
            ("navigate", "Navigation menu", "Navigation (`_msm_edit`)", "`AFTER _MFILE`", "`application.ShowNavToolBar`, first form", "no"),
            ("ordentry", "Items menu", "Items", "`AFTER _MEDIT`", "`frmorderentry.Activate`, every activation", "yes"),
            ("window", "Window menu", "Window (empty)", "`AFTER _MFILE`", "`tsbaseform.AddToMenu`, first form", "no")]
    L = ["# Menus", "",
         "Five menus in `menus/*.mnx`, all documented from their FoxBin2PRG twins with every pad, bar, shortcut, `SKIP FOR` condition, action, procedure, and the setup and cleanup code. `foxparse.py` gained a `.mn2` parser for this step; its pad, bar, popup, and procedure counts match a raw grep of every twin, and the three 2001 `.mpr` programs match their twins statement for statement.", "",
         "| File | Title | Pads | Location | Run by | `.mpr` in repo | Doc |", "|---|---|---|---|---|---|---|"]
    for stem, title, pads, loc, run, mpr in rows:
        L.append("| `menus/%s.mnx` | %s | %s | %s | %s | %s | [[%s.md]] |" % (stem, title, pads, loc, run, mpr, stem))
    L += ["",
          "## Lifecycle", "",
          "`application.Init` ([[../05-classes/tsgen.md]]) pushes the VFP system menu. `tastrade.Init` runs the intro menu and shows the intro form; `tastrade.Do` replaces it with the main menu and starts `READ EVENTS`. The first framework form to open adds the Window pad and then the Navigation pad; the order entry form adds and removes the Items pad on every activation; the last form to close removes Navigation and Window. Return to Visual FoxPro does `CLEAR EVENTS`, and `Cleanup2` pops the system menu back. Re-logging in as a different user level re-runs the main menu so its cleanup code can re-apply the gating.", "",
          "## Placement by system names", "",
          "Three pads reuse VFP system pad names as a placement trick, and the designer comments in the twins say so: Administration is `_msm_file` so that Navigation and Window (`AFTER _MFILE`) land after it; Navigation is `_msm_edit` so that Items (`AFTER _MEDIT`) lands after it; Help is `_msm_systm` so its system bars open the help file. A rebuilder should not look for File or Edit commands behind those names. The resulting bar order, by the sequence of the code, is File, Edit, Orders, Administration, Navigation, [Items], Window, Utilities, Help; not run here.", "",
          "## Findings", "",
          "- **Privilege gating is four lines of cleanup code in the main menu, and half of it misses.** Non-developers lose the Utilities pad; the lines meant to remove Login and Change Password for lower levels address a popup named `Administration` that does not exist (the popup is `_qx713dsus`), so those bars stay for everyone. Under `DEBUGMODE` none of it runs and every user gets the Utilities pad with the Command window.",
          "- **Two About boxes.** The intro menu hard-codes version 1.0, a 1994 copyright, and a bitmap that is not in the repo; the main menu uses the include-file constants (1.1, 1996) and a bitmap that is.",
          "- **The menus are keyboard fronts for the toolbar.** File and Navigation bars call toolbar button `Click` methods and mirror their `Enabled` state in `SKIP FOR`; only Delete, Print Setup, Login, About, and the form launches have code of their own.",
          "- **Two menus have no `.mpr`** (`navigate`, `window`); the build generated them and the EXE contains their strings. The three that do have `.mpr` files date them to October 2000.",
          "- **The copyright notice is stored as each menu's `ON SELECTION MENU` command**, a comment that does nothing.",
          "- **Dead code in the intro menu**: a popup-level dispatcher with a `New`-to-`AddNew` workaround for a VFP bug, unreachable because the only bar has its own handler.",
          "- **FoxBin2PRG emits an empty cascading popup for every separator bar** (five in `main`, one in `intro`); the `.mpr` files have none. Twin artifact, not source.",
          "- Menu prompts and status messages are plain English in the `.mnx`, not `_LOC` constants; the forms' strings are localized through `strings.h`, the menus' are not.",
          ""]
    return "\n".join(L)


GENERATORS = (("main.md", gen_main), ("intro.md", gen_intro), ("navigate.md", gen_navigate),
              ("ordentry.md", gen_ordentry), ("window.md", gen_window), ("README.md", gen_readme))

if __name__ == "__main__":
    for fn, gen in GENERATORS:
        with open(os.path.join(OUT, fn), "w", encoding="utf-8", newline="\n") as f:
            f.write(gen())
        print("wrote", fn)
