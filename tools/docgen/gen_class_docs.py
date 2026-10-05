"""Generate docs/05-classes/tsbase.md, tsgen.md and README.md for Tastrade.
Method bodies are quoted verbatim from the FoxBin2PRG twins via foxparse;
purpose, explanations, and notes are hand-written below."""
import os, re, sys, textwrap
sys.path.insert(0, os.environ.get("VFP_TOOLKIT_TOOLS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "vfp-documentation-toolkit", "tools")))
import foxparse as fp

ROOT = os.environ.get("TASTRADE_ROOT", os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))
OUT = os.path.join(ROOT, "docs", "05-classes")
os.makedirs(OUT, exist_ok=True)

def load(lib):
    r = fp.parse_vc2(os.path.join(ROOT, "libs", lib))
    text = fp.read(os.path.join(ROOT, "libs", lib))
    classes = {c["name"]: c for c in r["classes"]}
    # custom members (*m: *p: *a:) with their designer descriptions, per class
    for name, parent, clib, body in fp._split_classes(text):
        c = classes[name]
        c["members"] = re.findall(r"^\s*\*([mpa]):\s*(\S+)\s*(?:&&\s*(.*))?$", body, re.M)
        m = re.search(r"DEFINE CLASS %s\b[^\n]*?&&\s*(.*)$" % re.escape(name), text, re.M)
        c["desc"] = (m.group(1).strip() if m else "")
        pm = re.search(r"\*<PropValue>(.*?)\*</PropValue>", body, re.S)
        c["propvalues"] = [l.strip() for l in (pm.group(1) if pm else "").splitlines() if "=" in l]
        prot = re.search(r"^\s*PROTECTED\s+([^\n]+)$", body, re.M)
        c["protected"] = [p.strip() for p in prot.group(1).split(",")] if prot else []
    return classes

def body(c, method):
    code = c["methods"].get(method)
    if code is None:
        for k in c["methods"]:
            if k.lower() == method.lower():
                code = c["methods"][k]; break
    assert code is not None, "%s.%s" % (c["name"], method)
    return textwrap.dedent(code).strip("\n")

def fence(code):
    return "```foxpro\n" + code + "\n```"

def is_trivial(code):
    lines = [l.strip() for l in code.splitlines() if l.strip()]
    return all(l.startswith("*") for l in lines)

def header(title, srcfile, twin, purpose, used_by, related):
    L = ["# %s" % title, "",
         "| Source file | Type | Path |", "|---|---|---|",
         "| `%s` | Class library | `%s` |" % (srcfile, twin), "",
         "**Purpose:** " + purpose, "",
         "**Used by:**"]
    L += ["- " + u for u in used_by]
    L += ["", "**Related docs:** " + related, ""]
    return L

def members_table(c):
    L = []
    props = [(k, n, d) for k, n, d in c["members"] if k in ("p", "a")]
    meths = [(k, n, d) for k, n, d in c["members"] if k == "m"]
    if props:
        L += ["**Custom properties:**", "", "| Property | Protected | Description |", "|---|---|---|"]
        for k, n, d in props:
            L.append("| `%s` | %s | %s |" % (n, "yes" if n.split("[")[0].lower() in [p.lower() for p in c["protected"]] else "", d or ""))
        L.append("")
    if meths:
        L += ["**Custom methods:**", "", "| Method | Protected | Description |", "|---|---|---|"]
        for k, n, d in meths:
            L.append("| `%s` | %s | %s |" % (n, "yes" if n.lower() in [p.lower() for p in c["protected"]] else "", d or ""))
        L.append("")
    return L

def method_section(c, method, explain, protected=False):
    code = body(c, method)
    L = ["#### `%s`%s" % (method, " (protected)" if protected else ""), ""]
    if explain:
        L += [explain, ""]
    if is_trivial(code):
        L += ["Body holds only a copyright comment; no code.", ""]
    else:
        L += [fence(code), ""]
    return L

# =============================================================== tsbase
def gen_tsbase():
    C = load("tsbase.vc2")
    L = header("tsbase.vcx — visual base classes", "tsbase.vcx", "libs/tsbase.vc2",
        "The visual foundation of the application: one subclass of every VFP control used, a base form "
        "that owns record navigation, table buffering, save/restore, error handling, and window-position "
        "memory, two specialised form bases (maintenance and text viewer), a return-value form base for "
        "modal dialogs, and the navigation toolbar that drives the base form.",
        ["Twelve of the seventeen forms inherit from a class here: `tsbaseform` directly for "
         "[[../04-forms/behindsc.md]], [[../04-forms/chngpswd.md]], [[../04-forms/custadd.md]], "
         "[[../04-forms/ordhist.md]], [[../04-forms/rebuild.md]], [[../04-forms/reports.md]]; "
         "`tsmaintform` for [[../04-forms/category.md]], [[../04-forms/customer.md]], "
         "[[../04-forms/employee.md]], [[../04-forms/product.md]], [[../04-forms/shipper.md]], "
         "[[../04-forms/supplier.md]]; `tstextform` for [[../04-forms/casestdy.md]] and "
         "[[../04-forms/viewcode.md]].",
         "[[orders.md]]: `orderentry` extends `tsbaseform`, `ordtextbox` extends `tstextbox`.",
         "[[about.md]]: `aboutbox` extends `tsbaseform`. [[login.md]]: `login` extends `tsformretval`.",
         "[[tsgen.md]]: `findcustomer`, `findorder`, and `introform` extend `tsformretval`; "
         "`customerinfo`, `daterange`, and `findcustomer` are built from the control subclasses here.",
         "`tstoolbar` is never named outside this library. `tsbaseform.ctoolbar` defaults to `tstoolbar` "
         "and the application object instantiates it by that name (`CREATEOBJECT(tcToolBar)` in "
         "[[tsgen.md]] `shownavtoolbar`).",
         "`tsifcombo` is used by [[../04-forms/ordentry.md]]; `tsgrid` by [[../04-forms/ordentry.md]] "
         "and [[../04-forms/ordhist.md]].",
         "Two forms do **not** inherit from here: [[../04-forms/getinv.md]] and [[../04-forms/gettitle.md]] "
         "are plain VFP `form`s (see [[../PROJECT.md]])."],
        "[[README.md]] (library index and inheritance map), [[tsgen.md]] (the application object the base "
        "form talks to through the global `oApp`), [[../03-data-model/README.md]] (the triggers and rules "
        "whose failures `tsbaseform.Error` handles), [[../08-programs/utility.md]] (`FormIsObject()`, "
        "`IsTag()`, `OnShutdown()` called from here).")

    L += ["## Inheritance map", "",
          "```mermaid", "classDiagram",
          "    form <|-- tsbaseform", "    tsbaseform <|-- tsmaintform", "    tsbaseform <|-- tstextform",
          "    form <|-- tsformretval", "    toolbar <|-- tstoolbar", "    commandbutton <|-- tstoolbarbutton",
          "    commandbutton <|-- tscommandbutton", "    textbox <|-- tstextbox", "    combobox <|-- tscombobox",
          "    combobox <|-- tsifcombo", "    grid <|-- tsgrid", "    editbox <|-- tseditbox", "    label <|-- tslabel",
          "    listbox <|-- tslistbox", "    checkbox <|-- tscheckbox", "    optiongroup <|-- tsoptiongroup",
          "    shape <|-- ts3dshape",
          "```", "",
          "Every class was designed in the Class Designer, so each carries a `*< CLASSDATA` line with its "
          "designer icon, and each `DEFINE CLASS` carries the designer's one-line description as a `&&` "
          "comment. Those descriptions are the **Purpose** lines below unless corrected.", "",
          "All classes include `..\\include\\tastrade.h`, which pulls in `strings.h`. Constants used here: "
          "`FILE_OK` 0, `FILE_BOF` 1, `FILE_EOF` 2, `FILE_CANCEL` 3 (navigation return codes); "
          "`INSERTTRIG` 1, `UPDATETRIG` 2, `DELETETRIG` 3 (index into `aErrorMsg`, matching element 5 of "
          "`AERROR()` for a trigger failure); `AERRORARRAY` 7; `INIFILE` `\"TASTRADE.INI\"`; `DEBUGMODE` `.T.`; "
          "every `*_LOC` string from `strings.h`; `MOUSE_HOURGLASS`, `MOUSE_DEFAULT`, `TOOL_TOP`, `MB_*`, `ID*` "
          "from VFP's own `FOXPRO.H`, which `tastrade.h` includes.", "",
          "## Classes in this library", ""]

    # ---- tsbaseform
    c = C["tsbaseform"]
    L += ["### tsbaseform (extends form)", "",
          "**Purpose:** The base of every data-entry form. Owns the contract between a form and the "
          "navigation toolbar: the toolbar calls `First/Prior/Next/Last/AddNew/Save/Restore/QueryUnload` on "
          "`_screen.ActiveForm`, and these methods return a `FILE_*` code the toolbar uses to enable its "
          "buttons. Also owns optimistic table buffering (`BufferMode = 2`), the prompt-to-save logic, the "
          "form-level `Error` handler for trigger and rule failures, the Window-menu entry, and the "
          "remembered window position in `tastrade.ini`.", ""]
    L += members_table(c)
    L += ["**Notable property values:** `BufferMode = 2` (optimistic table buffering; the DataEnvironment "
          "cursors inherit it), `MDIForm = .T.`, `AutoCenter = .T.`, `BorderStyle = 2` (fixed), no Min/Max "
          "buttons, `ctoolbar = tstoolbar`, `lallowdelete/lallowedits/lallownew = .T.`, `FontSize = 8`, "
          "grey `BackColor = 192,192,192`.", "",
          "**Coupling to watch:** every method assumes the global `oApp` (the application object) and the "
          "public `gTTrade` flag set by `progs/main.prg`. `Init` refuses to run without `gTTrade`, which is "
          "how the sample blocks the Class Browser from instantiating these classes.", "",
          "#### Method contract used by the toolbar", "",
          "| Method | Returns | Meaning |", "|---|---|---|",
          "| `First()`, `Last()`, `Next()`, `Prior()` | `FILE_OK`, `FILE_BOF`, `FILE_EOF`, `FILE_CANCEL` | Moved; hit the start; hit the end; did not move (save cancelled, or already there) |",
          "| `AddNew()` | `.F.` on cancel | Appends a blank record after settling the current one |",
          "| `Save()` | `.T.` on success | `TABLEUPDATE(.T.)` with errors routed to `Error` |",
          "| `Restore()` | | `TABLEREVERT(.T.)`, releases the form if the table is now empty |",
          "| `Delete()` | `.T.` on success | Confirms, deletes, moves off the record so the buffered delete happens |",
          "| `QueryUnload()` | `.F.` to veto | Writes the active control, then asks to save |",
          "| `DataChanged()`, `IsNewAndEmpty()`, `WriteBuffer()`, `AskToSave()` | | Helpers the above share |", "",
          "Every navigation method follows the same four steps: `WriteBuffer()` the active control; if the "
          "record is a new blank one, `Restore()` it away, otherwise `AskToSave()` when `DataChanged()`; "
          "move; if the pointer did not move return `FILE_CANCEL`; else `RefreshForm()`.", "",
          "#### Methods", ""]
    L += method_section(c, "Init",
        "Refuses to run outside the application (`gTTrade`), restores the window position from the INI file, "
        "adds the form to the Window menu and shows the navigation toolbar when `cToolBar` is set, and loads "
        "the three trigger-failure messages into `aErrorMsg`, indexed by `INSERTTRIG/UPDATETRIG/DELETETRIG`.")
    L += method_section(c, "Activate",
        "Selects the DataEnvironment's `InitialSelectedAlias` so the toolbar acts on the right cursor, "
        "refreshes the toolbar, re-activates the system menu so `SKIP FOR` conditions re-evaluate, sets the "
        "status-bar message, and if the table is empty switches straight into add mode after a message box.")
    L += method_section(c, "Destroy",
        "Hides the form first, removes its Window-menu entry, tells the application to release the "
        "navigation toolbar (reference-counted), and saves the window position.")
    L += method_section(c, "QueryUnload",
        "Forms with no toolbar are assumed read-only and close freely. Otherwise the active control is "
        "written to the buffer, and if the current alias is lost the code re-selects the DataEnvironment's "
        "initial alias in the form's own data session before the usual new-and-empty or ask-to-save checks. "
        "`NODEFAULT` vetoes the close.")
    L += method_section(c, "Unload", "Clears the status-bar message.")
    L += method_section(c, "Error",
        "The form-level error handler. `lSetErrorOff` lets a caller (the splitter in [[tsgen.md]]) suppress "
        "handling and just record `lHadError`. Three VFP errors are handled specially: **1539** trigger failed, "
        "which shows the `aErrorMsg` entry for the trigger that failed and restores the form after a failed "
        "delete; **1583** table rule failed, treated as already reported by the rule itself (see `ValOrder()` "
        "in [[../03-data-model/README.md]]) with a `WAIT WINDOW` in debug mode; **1582** field rule violated, "
        "which shows the field's `RuleText` from the DBC with its quotes stripped. Anything else gets an "
        "Abort/Retry/Ignore box; Abort suspends in debug mode or cleans up and cancels otherwise. "
        "**NOTE:** `RETRY` re-executes the failing line, and `SUSPEND` under `DEBUGMODE` drops into the "
        "debugger in a built executable.")
    L += method_section(c, "addnew",
        "Settles the current record, disables the toolbar's New button, appends a blank record, and refreshes. "
        "The DBC defaults (`newid()`, `DATE()`, `defaultemployee()`) fire on the `APPEND BLANK`.")
    L += method_section(c, "save",
        "Writes the active control, returns early if nothing changed, then `TABLEUPDATE(.T.)`. On failure the "
        "first `AERROR()` code is passed to the form's own `Error` method so trigger and rule failures show "
        "their messages. On success `GO (RECNO())` forces related cursors to refresh.")
    L += method_section(c, "restore",
        "`TABLEREVERT(.T.)` discards all buffered changes, including a new record. If that leaves the table "
        "empty the form is released. Re-enables the New button.")
    L += method_section(c, "delete",
        "Confirms with the user; a new unsaved record is simply reverted. Otherwise `DELETE` then `SKIP`, "
        "because under table buffering the delete is only sent when the pointer moves, and the RI delete "
        "trigger may refuse it. Landing on an empty table offers to add a record or closes the form. "
        "If the pointer did not move the delete is reported as failed.")
    L += method_section(c, "first", "Navigation. `LOCATE` with no condition goes to the first record.")
    L += method_section(c, "last", "Navigation. Tracks whether a new empty record was discarded so that landing on the same record number still counts as a move.")
    L += method_section(c, "next", "Navigation. Backs up one record when the move hits `EOF()`.")
    L += method_section(c, "prior", "Navigation.")
    L += method_section(c, "datachanged",
        "Uses `GETFLDSTATE(-1)` for the whole record: any field in state 2 (edited) or 4 (appended and edited) "
        "counts as changed.")
    L += method_section(c, "isnewandempty",
        "Every field in state 3 (appended, untouched) means a blank new record. The test builds a number of "
        "all 3s the same length as the state string and checks divisibility, which is a compact but obscure "
        "way to say \"every character is 3\". **NOTE:** relies on the state string being all `3`s; a record "
        "whose default values fire (`newid()`, `DATE()`) still reads as untouched because defaults do not "
        "change field state.")
    L += method_section(c, "writebuffer",
        "Pushes the active control's `Value` into its `ControlSource` when the user clicks the toolbar without "
        "leaving the field, since the control's own `Valid` has not fired. Grids are skipped because a grid "
        "can change work areas. Returns `.F.` if the `REPLACE` did not take, relying on the `Error` method "
        "having reverted the field.")
    L += method_section(c, "asktosave",
        "Yes/No/Cancel prompt. Yes saves (a failed save turns into Cancel), No restores, Cancel is returned "
        "to the caller so navigation can stop.")
    L += method_section(c, "refreshform",
        "Wraps `Refresh()` in `LockScreen` and gives subclasses one place to override (the order history form does).")
    L += method_section(c, "addtomenu",
        "Adds the form's caption as a bar on the Window popup, defining the popup from `menus\\window.mpr` on "
        "first use. **NOTE:** `&lcFormName` macro substitution builds the `ACTIVATE WINDOW` command, and "
        "`lcFormName` is not declared `LOCAL`, so it leaks as a private variable.")
    L += method_section(c, "removefrommenu",
        "Finds the bar whose prompt equals the caption and releases it; releases the popup and pad when the "
        "menu becomes empty. Matching by caption means two forms with the same caption collide.")
    L += method_section(c, "restorewindowpos",
        "Reads `[WindowPositions] <caption>=top,left` from `tastrade.ini` in the current directory through the "
        "`GetPrivStr` Win32 declaration made in `progs/main.prg`, with an `ON ERROR` guard around the parse. "
        "The INI key is the form **caption**, so a caption change loses the saved position.")
    L += method_section(c, "savewindowpos", "Writes the same key back with `WritePrivStr`, clamping negative positions to 0.")
    L += method_section(c, "waitmode",
        "Sets the hourglass on the form and, with `SetAll`, on every control. **NOTE:** `lnMousePointer` is not "
        "declared `LOCAL`.")
    L += ["**Not overridden here but relied on:** `Load` and `Refresh` are the VFP defaults; subclasses "
          "override `Refresh` freely because `RefreshForm` calls it.", ""]

    # ---- tsmaintform
    c = C["tsmaintform"]
    L += ["### tsmaintform (extends tsbaseform)", "",
          "**Purpose:** " + c["desc"] + " Adds a two-page pageframe, **Data Entry** and **List**, where the "
          "List page holds a read-only `tsgrid` that subclasses bind to the form's main cursor. Six lookup "
          "and master-file forms use it.", "",
          "**Members:** `pageframe1` (pageframe, 2 pages, `Page1.Caption = \"\\<Data Entry\"`, "
          "`Page2.Caption = \"\\<List\"`), `pageframe1.Page2.grdList` (`tsgrid`, `ReadOnly = .T.`, empty "
          "`RecordSource`).", "",
          "`addtomenu`, `removefrommenu`, `restorewindowpos`, `savewindowpos` are declared `PROTECTED` here, "
          "hiding them from callers outside the form.", "",
          "#### Methods", ""]
    L += method_section(c, "addnew", "Flips to the Data Entry page before delegating to the base `AddNew` with the `::` scope operator.")
    L += method_section(c, "pageframe1.Page1.Activate", "Refreshes the form when returning to Data Entry because the grid on the List page may have moved the record pointer.")
    L += method_section(c, "pageframe1.Page2.Activate",
        "Switching to the List page is treated like navigation: a blank new record is discarded and the grid "
        "repositioned; otherwise unsaved changes prompt, and Cancel bounces back to page 1. Explicitly sets the "
        "data session because page events can fire in the default session.")
    L += method_section(c, "pageframe1.Page2.grdList.Init", "Makes every column read-only at run time regardless of how the subclass configured it.")
    L += method_section(c, "pageframe1.Page2.Init", "Pins the grid to the page's top-left corner.")

    # ---- tstextform
    c = C["tstextform"]
    L += ["### tstextform (extends tsbaseform)", "",
          "**Purpose:** " + c["desc"] + " A resizable, non-modal viewer with a read-only edit box and Close "
          "and Print buttons. Used by the case study and view-code forms. Runs in a private data session "
          "(`DataSession = 2`), turns buffering off (`BufferMode = 0`), has **no toolbar** (`ctoolbar` empty), "
          "and disables new/edit/delete, so the base form's navigation and save logic is inert here.", "",
          "**Members:** `edtText` (`tseditbox`, `ReadOnly = .T.`, fills the form), `cmdClose` "
          "(`tscommandbutton`, `Cancel = .T.`), `cmdPrint` (`tscommandbutton`, **no Click code in this class**; "
          "subclasses supply it).", "",
          "#### Methods", ""]
    L += method_section(c, "QueryUnload", "Overrides the base with an empty body so closing never prompts to save.")
    L += method_section(c, "Resize", "Lays the edit box and the two buttons out proportionally each time the form is resized.")
    L += method_section(c, "cmdClose.Click", None)

    # ---- tsformretval
    c = C["tsformretval"]
    L += ["### tsformretval (extends form)", "",
          "**Purpose:** " + c["desc"] + " The base for modal dialogs that hand a value back: `WindowType = 1` "
          "(modal), no control box, and a `uretval` property the caller reads after `Show()` returns. "
          "`application.doformretval` in [[tsgen.md]] is the standard way to run one: `CREATEOBJECT`, `Show()`, "
          "read `uRetVal`. Subclasses: `login` ([[login.md]]), `findcustomer`, `findorder`, `introform` ([[tsgen.md]]).", ""]
    L += members_table(c)
    L += ["`lallowdelete` is declared but never read; it exists so the toolbar's `Refresh` can test "
          "`TYPE(\"_screen.ActiveForm.lAllowEdits\")` uniformly, but this class does not declare `lallowedits`, "
          "so the test fails and the toolbar leaves its buttons alone.", "",
          "#### Methods", ""]
    L += method_section(c, "Init", "Same `gTTrade` guard as `tsbaseform`.")
    L += method_section(c, "Activate", None)
    L += method_section(c, "Unload", None)

    # ---- tstoolbar
    c = C["tstoolbar"]
    L += ["### tstoolbar (extends toolbar)", "",
          "**Purpose:** " + c["desc"] + " The \"Navigation Tools\" toolbar: First, Prior, Next, Last, New, "
          "Save, Restore, Close, and Behind the Scenes. One instance is shared by all open forms; the "
          "application object creates it for the first form and releases it with the last "
          "(`shownavtoolbar`/`releasenavtoolbar` in [[tsgen.md]]). Every button acts on `_screen.ActiveForm` "
          "through the method contract described under `tsbaseform`, and the `navigate.mpr` menu "
          "([[../07-menus/navigate.md]]) exposes the same actions with keyboard shortcuts.", "",
          "**Buttons** (all `tstoolbarbutton`, 22 x 22, picture only):", "",
          "| Button | Picture | Tooltip | Calls on the active form |", "|---|---|---|---|",
          "| `cmdFirst` | `frsrec_s.bmp` | First (Ctrl+Home) | `First()` |",
          "| `cmdPrior` | `prvrec_s.bmp` | Prior (Ctrl+Page Up) | `Prior()` |",
          "| `cmdNext` | `nxtrec_s.bmp` | Next (Ctrl+Page Down) | `Next()` |",
          "| `cmdLast` | `lstrec_s.bmp` | Last (Ctrl+End) | `Last()` |",
          "| `cmdNew` | `new.bmp` | New (Ctrl+N) | `AddNew()` |",
          "| `cmdSave` | `save.bmp` | Save (Ctrl+S) | `Save()` |",
          "| `cmdRestore` | `undo.bmp` | Restore (Ctrl+E) | `Restore()` |",
          "| `cmdClose` | `close.bmp` | Close (Ctrl+F4) | `QueryUnload()` then `Release()` |",
          "| `cmdBehindSC` | `bhind_s.bmp` | Behind The Scenes | `oApp.DoForm(\"behindsc\")` |", "",
          "Three `separator`s divide the groups. The class icon path recorded in `CLASSDATA` is "
          "`..\\..\\..\\..\\backup\\mainsamp\\bitmaps\\toolbar.bmp`, a leftover from the original author's "
          "directory layout; harmless, but it shows the library predates this folder structure.", ""]
    L += members_table(c)
    L += ["#### Methods", ""]
    L += method_section(c, "Init", "Restores the last docked or floating position from the INI file; first run docks at the top (`TOOL_TOP`).")
    L += method_section(c, "Destroy", None)
    L += method_section(c, "Refresh",
        "Called by `tsbaseform.Activate` and after each navigation click, optionally with `\"BOF\"` or "
        "`\"EOF\"` when the form reported hitting an end. Enables the four navigation buttons from the "
        "BOF/EOF state (the truth table is in the dead code after `RETURN`), and New/Save/Restore from the "
        "active form's `lAllowNew`/`lAllowEdits` when it has them, Close from `Closable`.")
    L += method_section(c, "oktosend",
        "True when the active window is a form with a non-empty `cToolBar`. `FormIsObject()` is in "
        "[[../08-programs/utility.md]].")
    L += method_section(c, "restorewindowpos",
        "A stored value with a comma is `top,left` for a floating toolbar; without one it is a dock position "
        "passed to `Dock()`. Returns `.F.` when no entry exists so `Init` can apply the default.", protected=True)
    L += method_section(c, "savewindowpos",
        "**NOTE:** when the toolbar is floating this writes `thisform.Top` and `thisform.Left`. A toolbar is "
        "not a form and has no `thisform`, so undocking the toolbar and then closing the application should "
        "raise an error in `Destroy`. Docked, the code path is fine, which is presumably how it was always "
        "tested. Verify at run time before relying on it.", protected=True)
    for m, e in [("cmdFirst.Click", "Each navigation click passes the form's `FILE_*` return code to `Refresh` so the buttons update."),
                 ("cmdPrior.Click", None), ("cmdNext.Click", None), ("cmdLast.Click", None),
                 ("cmdNew.Click", None), ("cmdSave.Click", None), ("cmdRestore.Click", None),
                 ("cmdClose.Click", "Asks the form first; `QueryUnload` returning `.F.` cancels."),
                 ("cmdBehindSC.Click", None)]:
        L += method_section(c, m, e)

    # ---- tstoolbarbutton
    c = C["tstoolbarbutton"]
    L += ["### tstoolbarbutton (extends commandbutton)", "",
          "**Purpose:** " + c["desc"] + " Adds one behaviour: if the active window cannot receive toolbar "
          "messages (`Parent.OKToSend()` false), the button beeps and refuses to depress, so a click on the "
          "toolbar while, say, the intro form is active does nothing.", ""]
    L += members_table(c)
    L += ["#### Methods", ""]
    L += method_section(c, "MouseDown", "`NODEFAULT` here stops the visual press; `lCancelClick` remembers the decision for `MouseUp`.")
    L += method_section(c, "MouseUp", None)

    # ---- tsifcombo
    c = C["tsifcombo"]
    L += ["### tsifcombo (extends combobox)", "",
          "**Purpose:** " + c["desc"] + " A combo bound to a SQL `RowSource` that seeks the underlying "
          "table as the user types, so a long lookup list (products, customers) can be picked by prefix. "
          "Used by the order entry form's product column ([[../04-forms/ordentry.md]]).", ""]
    L += members_table(c)
    L += ["`RowSourceType = 3` (SQL statement) and `IncrementalSearch = .F.` because the class does its own. "
          "`calias`, `cfield`, `csearchstring`, `RowSourceType`, and `Style` are `PROTECTED`.", "",
          "#### Methods", ""]
    L += method_section(c, "Init",
        "Parses the alias out of the `FROM` clause and the first selected field out of the `SELECT` clause of "
        "the `RowSource`, derives a 10-character tag name from the field unless `cTag` was set, and warns with "
        "`IsTag()` ([[../08-programs/utility.md]]) if that tag does not exist. Re-assigning `RowSource` at the "
        "end forces the list to populate. **NOTE:** the parser is string arithmetic on the SQL text; a "
        "`RowSource` with a `JOIN`, a subquery, or a table alias breaks it.")
    L += method_section(c, "KeyPress",
        "Builds `cSearchString` from printable keys, `SEEK`s it (upper-cased) on the lookup alias, and sets "
        "`DisplayValue` from the found record or, if `lLimitToList` is off, from the typed text. Up and down "
        "arrows step through the alias. `NODEFAULT` stops the combo from also inserting the character. "
        "**NOTE:** the guard `INLIST( 2, 26)` is missing its first argument (`nKeyCode`); it compares 2 to 26 "
        "and is always false, so the Ctrl+B and Ctrl+Z exclusions never fire. Also uses `&lcField` style "
        "macro expansion in `InteractiveChange`.")
    L += method_section(c, "InteractiveChange", "When the user picks from the dropped list, positions the lookup alias on that row with `LOOKUP()` and resets the search string.")
    L += method_section(c, "LostFocus", None)
    L += method_section(c, "Valid", "Always valid; the class never rejects input.")

    # ---- tsgrid
    c = C["tsgrid"]
    L += ["### tsgrid (extends grid)", "",
          "**Purpose:** " + c["desc"] + " A grid that can total one column expression into `ncolumnsum` "
          "every time it refreshes. The order entry form sets `cfieldtosum = quantity * unit_price`; the "
          "order history form sets `cfieldtosum = extension`. `RecordMark` and `DeleteMark` are off, "
          "`Highlight` off, `RowHeight` 17.", ""]
    L += members_table(c)
    L += ["#### Methods", ""]
    L += method_section(c, "Refresh", None)
    L += method_section(c, "sumcolumn",
        "Selects the grid's `RecordSource`, and if it has a controlling index, `SEEK`s the current key and "
        "`SUM`s `WHILE` the key matches, which totals the current order's lines in a child cursor ordered by "
        "`order_id`. Without an index it sums the whole cursor, but only if the cursor is a view. Restores the "
        "record pointer and work area. **NOTE:** `&lcFieldToSum.` macro substitution; the property holds an "
        "expression, not a field name, and is expanded as code.")

    # ---- tstextbox
    c = C["tstextbox"]
    L += ["### tstextbox (extends textbox)", "",
          "**Purpose:** " + c["desc"] + " `Format = \"K\"` selects the contents on entry. `Init` derives an "
          "`InputMask` of `X`s from the width of the bound character field so users cannot type past the "
          "field, unless a mask was set in the designer.", "",
          "#### Methods", ""]
    L += method_section(c, "Init", "`FSIZE()` on the field name after the dot needs the alias to be the current work area; a control bound to another alias gets the wrong width or an error.")

    # ---- plain base controls
    L += ["### Plain control subclasses", "",
          "These eight classes exist so every control in the application shares one place to change fonts "
          "and colours. Each `Init` contains only the 1995 copyright comment. Their only content is designer "
          "defaults:", "",
          "| Class | Extends | Defaults |", "|---|---|---|"]
    for name, defaults in [
        ("ts3dshape", "`BackStyle = 0`, `SpecialEffect = 0` (3-D), 234 x 73"),
        ("tscheckbox", "`BackStyle = 0` (transparent), `FontSize = 8`"),
        ("tscombobox", "`FontSize = 8`, grey `DisabledBackColor`, 200 x 24"),
        ("tscommandbutton", "`FontBold = .T.`, `FontSize = 8`, 76 x 26"),
        ("tseditbox", "`ColorSource = 0`, `FontSize = 8`"),
        ("tslabel", "`Alignment = 1` (right), `BackStyle = 0`, `FontBold = .T.`, `FontSize = 8`"),
        ("tslistbox", "`FontSize = 8`, grey `DisabledBackColor`, 125 x 104"),
        ("tsoptiongroup", "`BackStyle = 0`, two options, `FontSize = 8`"),
    ]:
        L.append("| `%s` | `%s` | %s |" % (name, C[name]["parentclass"], defaults))
    L += ["", "## Notes", "",
          "- **Global coupling.** `oApp`, `gTTrade`, `_screen.ActiveForm`, and `FormIsObject()` tie every "
          "class here to the running application. None of these classes can be reused in another app "
          "without the same globals.",
          "- **INI file in the current directory.** Window positions go to `CURDIR() + \"TASTRADE.INI\"`, so "
          "starting the executable from another folder creates a second INI.",
          "- **Buffering model.** Optimistic table buffering per form, committed with `TABLEUPDATE(.T.)` and "
          "reverted with `TABLEREVERT(.T.)`. The DBC's triggers and rules fire at commit, which is why "
          "`Save` routes `AERROR()` into `Error`.",
          "- **Macro substitution** in `addtomenu` (`&lcFormName`), `tsgrid.sumcolumn` (`&lcFieldToSum.`), and "
          "`tsifcombo` (`&lcField`).",
          "- **Hard-coded English** in every `MESSAGEBOX`, though all strings come from `strings.h` `_LOC` "
          "constants, so localisation was planned.",
          "- **Suspected defects:** `tstoolbar.savewindowpos` uses `thisform` inside a toolbar; "
          "`tsifcombo.KeyPress` has the malformed `INLIST( 2, 26)`; `waitmode` and `addtomenu` leak "
          "undeclared variables.", ""]
    return "\n".join(L)

# =============================================================== tsgen
def gen_tsgen():
    C = load("tsgen.vc2")
    L = header("tsgen.vcx — application framework and composite classes", "tsgen.vcx", "libs/tsgen.vc2",
        "The non-visual half of the framework plus the reusable composites: the `application` object that "
        "owns the event loop, menu, database, toolbars, and form instances; the `environment` object that "
        "saves and restores every `SET` the app changes; a customer-details container, a date-range control, "
        "two modal record pickers, the intro screen, and the splitter used by the Behind the Scenes form.",
        ["[[main.md]]: `tastrade` extends `application` and is the object `progs/main.prg` creates as the "
         "global `oApp`. `application.Init` creates the `environment` object as `oApp.oEnvironment`.",
         "[[../04-forms/customer.md]] and [[../04-forms/custadd.md]] drop in `customerinfo`.",
         "[[../04-forms/getinv.md]] uses `daterange` for the invoice date range.",
         "[[../04-forms/ordentry.md]] opens `findcustomer` and `findorder`; [[../04-forms/ordhist.md]] opens "
         "`findcustomer`; both through `oApp.DoFormRetVal()`.",
         "[[main.md]] `tastrade.Init` shows `introform` through `DoFormRetVal` when the INI says to.",
         "[[../04-forms/behindsc.md]] hosts `splitter` and supplies the `aObjSplitMove` array it moves.",
         "Every `tsbaseform` descendant ([[tsbase.md]]) calls `oApp.ShowNavToolBar`, `oApp.ReleaseNavToolBar`, "
         "`oApp.DoForm`, and reads `oApp.oToolBar`."],
        "[[README.md]] (library index), [[tsbase.md]] (the form and toolbar classes this object manages), "
        "[[main.md]] (the concrete subclass), [[../08-programs/main.md]] (creates `oApp` and the globals "
        "`environment` reads), [[../07-menus/main.md]] and [[../07-menus/navigate.md]] (the menus this "
        "object runs).")
    L += ["## Inheritance map", "",
          "```mermaid", "classDiagram",
          "    custom <|-- application", "    application <|-- tastrade : main.vcx",
          "    custom <|-- environment", "    container <|-- customerinfo", "    control <|-- daterange",
          "    control <|-- splitter", "    tsformretval <|-- findcustomer : tsbase.vcx",
          "    findcustomer <|-- findorder", "    tsformretval <|-- introform",
          "```", "", "## Classes in this library", ""]

    # ---- application
    c = C["application"]
    L += ["### application (extends custom)", "",
          "**Purpose:** " + c["desc"] + " The framework's application object. `Init` prepares the "
          "environment and opens the database; `Do` runs the menu and the `READ EVENTS` loop; `Cleanup` and "
          "`Cleanup2` shut down; the rest manage the shared navigation toolbar, VFP's own toolbars, modal "
          "dialogs, and multiple instances of a form. It is abstract in practice: `cdatabase` and "
          "`cmainwindcaption` are empty and are filled in by the `tastrade` subclass in [[main.md]], which "
          "also overrides `Do`, `Init`, and `Login`. See the note at the end about which of them does what.", ""]
    L += members_table(c)
    L += ["`cmainmenu` defaults to `MAIN.MPR`. `atoolbars`, `cdatabase`, `cmainmenu`, `coldwindcaption`, "
          "`lisclean`, and `nforminstancecount` are `PROTECTED`. `lhaderror` and `lseterroroff` are declared "
          "but no method in this library reads them; the same pair on `tsbaseform` is what the splitter uses.", "",
          "#### Lifecycle", "",
          "```mermaid", "sequenceDiagram",
          "    participant M as main.prg", "    participant A as oApp (tastrade)", "    participant E as oEnvironment",
          "    M->>A: CREATEOBJECT(\"TasTrade\")", "    A->>E: AddObject + Set()  (SET commands, procedures, class libs)",
          "    A->>A: OPEN DATABASE cDataBase", "    A->>A: ReleaseToolBars(), PUSH MENU _MSYSMENU",
          "    M->>A: Do()", "    A->>A: DoMenu() -> DO MAIN.MPR", "    loop until Cleanup() succeeds",
          "        A->>A: READ EVENTS", "    end", "    A->>A: Cleanup2(): CLEAR EVENTS, POP MENU, ShowToolBars()",
          "    A->>E: Destroy -> Reset()", "```", "",
          "#### Methods", ""]
    L += method_section(c, "Init",
        "Guarded by `gTTrade`. Adds the `environment` member and applies its `Set`, swaps the main window "
        "caption, closes all data and opens `cDataBase` (fails with a message box if the DBC did not open), "
        "hides VFP's toolbars, and pushes the current system menu so `Cleanup2` can pop it back.")
    L += method_section(c, "do",
        "The main loop. `READ EVENTS` blocks until `CLEAR EVENTS`; the loop exists so that a `Cleanup` vetoed "
        "by a form's `QueryUnload` (unsaved changes, Cancel) re-enters `READ EVENTS` instead of exiting.")
    L += method_section(c, "cleanup",
        "Asks every open form to close through `QueryUnload`; the first refusal aborts the shutdown. "
        "`application.Forms` here is VFP's own `application` object (the IDE or runtime), not this class.")
    L += method_section(c, "cleanup2", "Restores the window caption and the pre-application menu, re-shows VFP toolbars, and ends the event loop.")
    L += method_section(c, "Destroy", "Safety net: if the object is released without `Cleanup` having run, run it now. Closes all tables either way.")
    L += method_section(c, "domenu", None)
    L += method_section(c, "doform", "Runs an `.scx` form by name with up to one parameter. Forms register their own toolbar needs in their `Init`.")
    L += method_section(c, "doformretval",
        "Runs a class-based modal form (a `tsformretval` descendant), waits for `Show()` to return, and hands "
        "back `uRetVal`. Because the form is a `LOCAL`, it is released when the method returns.")
    L += method_section(c, "login", "Runs the `login` class from [[login.md]] as a return-value form. Overridden in [[main.md]].")
    L += method_section(c, "shownavtoolbar",
        "Reference-counted creation of the navigation toolbar: the first `tsbaseform` to open creates it by "
        "class name, shows it, and runs `navigate.mpr` to add the Navigation menu pad; later forms only "
        "increment the count.")
    L += method_section(c, "releasenavtoolbar", "The mirror: when the last form closes, drop the toolbar reference (releasing it) and remove the Navigation popup and pad.")
    L += method_section(c, "releasetoolbars",
        "Hides the twelve VFP IDE toolbars and the Command window by their localised window names "
        "(`TB_*_LOC`, `WIN_COMMAND_LOC` in `strings.h`), remembering which were visible. Only meaningful when "
        "running inside the IDE; in the runtime none exist.", protected=True)
    L += method_section(c, "showtoolbars", None, protected=True)
    L += method_section(c, "addinstance",
        "Bookkeeping for running the same form more than once (the order history form does this). "
        "`aInstances` rows are `[form name, an instance reference, running count, next instance number]`; a "
        "second instance is offset 5 right and 23 down from the remembered one. **NOTE:** the two lines that "
        "store the form reference in column 2 are commented out, so column 2 is only set on the second "
        "instance by the `TYPE(...) # \"O\"` check. The dead-code comments show this was reworked.")
    L += method_section(c, "removeinstance", "Decrements the count and drops the row when it reaches zero, collapsing the array to `.F.` when it is the last row.")

    # ---- environment
    c = C["environment"]
    L += ["### environment (extends custom)", "",
          "**Purpose:** " + c["desc"] + " Captures the state of every `SET` and `ON` command the application "
          "changes, applies the application's settings, and restores the originals on `Destroy`. The first "
          "five values (`talk`, `path`, directory, class libraries, escape) are taken from the public "
          "variables `gcOldTalk`, `gcOldPath`, `gcOldDir`, `gcOldClassLib`, `gcOldEscape` that "
          "`progs/main.prg` fills in before creating the application object and releases afterwards.", ""]
    L += members_table(c)
    L += ["All `cold*` properties are `PROTECTED`.", "",
          "**What `Set` establishes:**", "",
          "| Setting | Value | Why |", "|---|---|---|",
          "| `SAFETY` | OFF | No overwrite prompts |",
          "| `PROCEDURE` | `UTILITY.PRG` | `IsTag`, `FormIsObject`, `OnShutdown`, etc. |",
          "| `CLASSLIB` | `MAIN, TSBASE, TSGEN, LOGIN, ORDERS` | All six libraries except `ABOUT` |",
          "| `MEMOWIDTH` | 120 | |",
          "| `MULTILOCKS` | ON | Required for table buffering |",
          "| `HELP` | `HELP\\TASTRADE.CHM` | |",
          "| `DELETED` | ON | Deleted rows hidden |",
          "| `EXCLUSIVE` | OFF | Shared tables |",
          "| `NOTIFY`, `BELL`, `NEAR`, `EXACT`, `INTENSITY` | OFF | |",
          "| `CONFIRM` | ON | Enter required to leave a full field |",
          "| `COMPATIBLE` | OFF | |",
          "| `ESCAPE` | ON when `DEBUGMODE`, else OFF | `DEBUGMODE` is `.T.` in `tastrade.h` |",
          "| `ON SHUTDOWN` | `DO OnShutDown` | Handler in `utility.prg` |", "",
          "`about.vcx` is not in the `SET CLASSLIB` list; the Help menu's About item does `SET CLASSLIB TO about "
          "ADDITIVE` and creates `AboutBox` itself ([[../07-menus/main.md]]). `SET HELP TO HELP\TASTRADE.CHM` "
          "is relative to the current directory. `Reset` restores through `&luTemp` macro substitution for every ON/OFF value.", "",
          "#### Methods", ""]
    L += method_section(c, "Init", "Guarded by `gTTrade`. Snapshots the settings listed above. `SET('HELP', 1)` returns the help file name.")
    L += method_section(c, "set", None)
    L += method_section(c, "reset", "Restores in roughly reverse order; `SET HELP` only if the old help file still exists.")
    L += method_section(c, "Destroy", None)

    # ---- customerinfo
    c = C["customerinfo"]
    L += ["### customerinfo (extends container)", "",
          "**Purpose:** " + c["desc"] + " The customer data-entry block, bound field by field to the "
          "`customer` alias, shared by the customer maintenance form and the add-customer dialog so the "
          "layout exists once. Includes its own `Error` handler that maps DBC rule failures to the offending "
          "text box.", "",
          "**Bound controls** (all `tstextbox`):", "",
          "| Control | ControlSource | Format / mask |", "|---|---|---|"]
    for name, src, fmt in [
        ("txtCustomer_ID", "Customer.customer_id", "`K!` (upper-case)"),
        ("txtCompany_Name", "Customer.company_name", ""),
        ("txtContact_Name", "customer.contact_name", ""), ("txtContact_Title", "customer.contact_title", ""),
        ("txtAddress", "customer.address", ""), ("txtCity", "customer.city", ""), ("txtRegion", "customer.region", ""),
        ("txtPostal_Code", "customer.postal_code", "right-aligned"), ("txtCountry", "customer.country", ""),
        ("txtPhone", "customer.phone", ""), ("txtFax", "customer.fax", ""),
        ("txtMax_Ord_Amt", "customer.max_order_amt", "`K$`, `999,999,999.99`"),
        ("txtMin_Ord_Amt", "customer.min_order_amt", "`K$`, `999,999,999.99`"),
        ("txtDiscount", "customer.discount", "`99`"),
    ]:
        L.append("| `%s` | `%s` | %s |" % (name, src, fmt))
    L += ["", "Plus fourteen `tslabel`s and a `ts3dshape` framing the three credit fields under the label "
          "\"Maximum\", \"Minimum\", \"Discount\". `sales_region` is **not** on the container; it has no UI.", "",
          "#### Methods", ""]
    L += method_section(c, "Init", "Guarded by `gTTrade`.")
    L += method_section(c, "Error",
        "Intercepts two DBC errors before the form's handler sees them. **1884** primary key violated: "
        "\"customer ID exists\" and focus the ID. **1582** field rule violated: show the rule text and pick the "
        "text box to focus by matching the **first words of the error message** (\"CUSTOMER ID\", "
        "\"COMPANY NAME\", \"MINIMUM\", \"MAXIMUM\"). **NOTE:** the rule texts live in the DBC; editing one "
        "silently breaks the focus mapping. Other errors go to the parent form's `Error` if it has one.")
    L += method_section(c, "txtMax_Ord_Amt.Valid",
        "Client-side copy of the DBC cross-field rule: if minimum exceeds maximum, revert the field to "
        "`OLDVAL()` and return 0 (keep focus). The DBC rule would also fire at commit; doing it here gives "
        "immediate feedback and avoids the pair-validation trap noted in [[../03-data-model/tables/customer.md]].")
    L += method_section(c, "txtMin_Ord_Amt.Valid", None)

    # ---- daterange
    c = C["daterange"]
    L += ["### daterange (extends control)", "",
          "**Purpose:** " + c["desc"] + " Two `tstextbox`es (`txtDateFrom`, `txtDateTo`, `Format = \"DK\"`) "
          "with From/To labels. The invoice dialog reads the two getters to supply `?dDateFrom` and "
          "`?dDateTo` to the `ORDERS VIEW` ([[../03-data-model/README.md]]).", ""]
    L += members_table(c)
    L += ["#### Methods", ""]
    L += method_section(c, "getdatefrom", None)
    L += method_section(c, "getdateto",
        "An empty To date means \"no upper bound\", returned as today plus 100,000 days (about 274 years). "
        "**NOTE:** a sentinel date rather than an open range; fine for the view parameter, surprising if displayed.")
    L += method_section(c, "validate", "To before From is rejected with a message box. An empty From is allowed.")
    L += method_section(c, "txtDateTo.Valid", "A failed validation clears the To date rather than refusing to leave the field.")

    # ---- findcustomer / findorder
    c = C["findcustomer"]
    L += ["### findcustomer (extends tsformretval)", "",
          "**Purpose:** " + c["desc"] + " A modal list of customers (ID, company, contact, city) sortable "
          "by ID or company through an option group; OK or double-click returns the `customer_id` in "
          "`uRetVal`, Cancel returns whatever `uRetVal` held (empty). Private data session (`DataSession = 2`). "
          "The list is `RowSourceType = 6` (fields) over the `customer` alias, so sorting is done by "
          "`SET ORDER` and `Requery`.", "",
          "**Members:** `lstCustomers` (`tslistbox`, 4 columns, widths `40,155,120,70`, `BoundTo = .T.`), "
          "`cmdOK` (default), `cmdCancel` (cancel), `Tsoptiongroup1` (Customer ID / Company), five labels.", "",
          "#### Methods", ""]
    L += method_section(c, "Load",
        "Opens `customer` directly with `USE ... ORDER TAG company_na` if it is not already open in this "
        "session. **NOTE:** direct `USE` outside any DataEnvironment, and without the `tastrade!` prefix, so "
        "it depends on the DBC being the current database. Flagged per the data-access convention in "
        "[[../PROJECT.md]].")
    L += method_section(c, "Unload", "Re-selects `orders` on the way out so the calling order form finds its alias current.")
    L += method_section(c, "cmdOK.Click", None)
    L += method_section(c, "cmdCancel.Click", None)
    L += method_section(c, "lstCustomers.DblClick", None)
    L += method_section(c, "Tsoptiongroup1.Option1.Click", None)
    L += method_section(c, "Tsoptiongroup1.Option2.Click", None)
    c = C["findorder"]
    L += ["### findorder (extends findcustomer)", "",
          "**Purpose:** " + c["desc"] + " The same dialog re-skinned for orders: the list shows "
          "`order_id, customer_id, ship_to_city, order_date`, the option group sorts by Order ID or Customer ID, "
          "and OK returns `orders.order_id`. Inherits the list control name `lstCustomers` unchanged.", "",
          "#### Methods", ""]
    L += method_section(c, "Load", "Same direct `USE` pattern on `orders`, ordered by `order_id`.")
    L += method_section(c, "cmdOK.Click", None)
    L += method_section(c, "Tsoptiongroup1.Option1.Click", None)
    L += method_section(c, "Tsoptiongroup1.Option2.Click", None)

    # ---- introform
    c = C["introform"]
    L += ["### introform (extends tsformretval)", "",
          "**Purpose:** " + c["desc"] + " The welcome screen with the Tasmanian Traders picture "
          "(`..\\bitmaps\\ttradelg.bmp`), three paragraphs of explanation, a \"Show This Form at Startup\" "
          "checkbox, and Continue / Behind the Scenes / Exit buttons. `uRetVal` is 1 for Continue and 2 "
          "for Exit; `tastrade.Init` in [[main.md]] reads the `[Defaults] ShowIntroForm` INI value to decide "
          "whether to show it and exits the application on 2. `Closable = .F.`, so the menu `intro.mpr` "
          "([[../07-menus/intro.md]]) calls `close` instead.", ""]
    L += members_table(c)
    L += ["#### Methods", ""]
    L += method_section(c, "close", None)
    L += method_section(c, "chkShowAtStartup.Click", "Writes `ShowIntroForm=0` or `1` to `tastrade.ini` immediately.")
    L += method_section(c, "cmdBehindSC.Click", "**NOTE:** runs the form directly with `DO FORM` rather than through `oApp.DoForm`, the only such call in the framework libraries.")
    L += method_section(c, "cmdContinue.Click", "Hiding the modal form is what makes `Show()` return to `doformretval`.")
    L += method_section(c, "cmdExit.Click", "`SET SYSMENU TO DEFAULT` restores VFP's menu before the application shuts down.")

    # ---- splitter
    c = C["splitter"]
    L += ["### splitter (extends control)", "",
          "**Purpose:** " + c["desc"] + " A grey bar with a draggable handle. Dragging moves the splitter "
          "between `I_SHPMIN` (111) and `I_SHPMIN + I_SHPMAX` (414) pixels, then calls `Move()` on every "
          "object in the **parent form's** `aObjSplitMove` array so the list and text panes resize. "
          "Only [[../04-forms/behindsc.md]] uses it, and it defines that array.", ""]
    L += members_table(c)
    L += ["**NOTE:** the handle shape carries `ClassLibrary = \"c:\\fox30\\nwind\\beta1\\mainsamp\\libs\\nwbasobj.vcx\"`, "
          "an absolute path into a **FoxPro 3.0 beta \"Northwind\" sample** on the original author's machine. "
          "It is inert (the shape is a native `shape`), but it dates the class to 1995 and shows Tastrade "
          "descends from the Northwind sample, which also explains the Northwind customer IDs in the data.", "",
          "#### Methods", ""]
    L += method_section(c, "Init", "Guarded by `gTTrade`.")
    L += method_section(c, "getleftedge", None)
    L += method_section(c, "getrightedge", None)
    L += method_section(c, "shpHandle.MouseDown",
        "A polling drag loop: `DO WHILE MDOWN()` reads `MCOL()` (a character column) and multiplies by the "
        "average character width to get pixels, moving the parent each pass. **NOTE:** busy loop tied to mouse "
        "state, and `PARAMETERS` rather than `LPARAMETERS`.")
    L += method_section(c, "updatecontrols",
        "Records the new edges, locks the active form, and moves each object in `this.Parent.aObjSplitMove`. "
        "Sets the form's `lSetErrorOff` around the moves so any error is swallowed into `lHadError` (see "
        "`tsbaseform.Error` in [[tsbase.md]]) and cleared afterwards. Reaches the form as both `THISFORM` and "
        "`_screen.ActiveForm`.")
    L += ["## Notes", "",
          "- **`application` is the only class here that is not tied to a specific form**, and even it assumes "
          "the `gTTrade` flag, the `_screen` caption, and menus named `navigation`, `_msm_edit`, and `Window`.",
          "- **The event loop lives in `application.Do`**; the concrete `tastrade.Do` in [[main.md]] re-implements it "
          "and adds the user level's startup action, executed by `&lcAction` macro, but **only when `DEBUGMODE` is "
          "off**. `DEBUGMODE` is `.T.` in `tastrade.h`, so in this build the startup action never runs. The intro "
          "form and login are in `tastrade.Init`. Read all three together.",
          "- **Direct table access** in `findcustomer.Load` and `findorder.Load` (`USE` without a "
          "DataEnvironment) is the only place in these two libraries that opens a table by hand.",
          "- **Two modal pickers and the intro form return through `uRetVal`**; nothing else in the framework "
          "returns values from forms.",
          "- **Hard-coded English** in `introform` captions and every message box, via `_LOC` constants.",
          "- **History:** the `c:\\fox30\\nwind\\beta1` path in `splitter`.", ""]
    return "\n".join(L)

def gen_readme():
    L = ["# Class libraries", "",
         "Six `.vcx` libraries hold 31 classes. The two framework libraries are documented; the four "
         "application-specific ones are next.", "",
         "| Library | Classes | Role | Doc |", "|---|---|---|---|",
         "| `libs/tsbase.vcx` | 17 | Visual base classes: base form, maintenance form, text form, return-value form, toolbar, one subclass per control | [[tsbase.md]] |",
         "| `libs/tsgen.vcx` | 8 | Application object, environment object, customer block, date range, record pickers, intro form, splitter | [[tsgen.md]] |",
         "| `libs/main.vcx` | 1 | `tastrade`, the concrete application object | main.md (pending) |",
         "| `libs/login.vcx` | 2 | `login` dialog and its picture variant | login.md (pending) |",
         "| `libs/about.vcx` | 1 | `aboutbox` | about.md (pending) |",
         "| `libs/orders.vcx` | 2 | `orderentry` form class and `ordtextbox` | orders.md (pending) |", "",
         "## Inheritance across libraries", "",
         "```mermaid", "classDiagram",
         "    form <|-- tsbaseform", "    tsbaseform <|-- tsmaintform", "    tsbaseform <|-- tstextform",
         "    tsbaseform <|-- orderentry : orders.vcx", "    tsbaseform <|-- aboutbox : about.vcx",
         "    form <|-- tsformretval", "    tsformretval <|-- login : login.vcx", "    login <|-- loginpicture : login.vcx",
         "    tsformretval <|-- findcustomer : tsgen.vcx", "    findcustomer <|-- findorder : tsgen.vcx",
         "    tsformretval <|-- introform : tsgen.vcx",
         "    custom <|-- application : tsgen.vcx", "    application <|-- tastrade : main.vcx",
         "    custom <|-- environment : tsgen.vcx",
         "    textbox <|-- tstextbox", "    tstextbox <|-- ordtextbox : orders.vcx",
         "    toolbar <|-- tstoolbar",
         "```", "",
         "Forms in `forms/*.scx` inherit as listed in [[tsbase.md]]; the two that do not (`getinv`, `gettitle`) "
         "are plain VFP forms.", "",
         "## How the pieces fit at run time", "",
         "1. `progs/main.prg` saves the environment into public variables, sets `gTTrade`, and creates "
         "`oApp = CREATEOBJECT(\"TasTrade\")` ([[main.md]] → `application` in [[tsgen.md]]).",
         "2. `application.Init` adds the `environment` object, opens `tastrade.dbc`, hides VFP toolbars.",
         "3. `tastrade.Init` shows `introform` when the INI says so and logs in (`login` in [[login.md]]); "
         "`tastrade.Do` runs `MAIN.MPR`, the user level's startup action (only when `DEBUGMODE` is off), "
         "and enters `READ EVENTS`.",
         "4. Menu items call `oApp.DoForm(\"...\")`. Each form inherits `tsbaseform` ([[tsbase.md]]); its `Init` "
         "asks `oApp.ShowNavToolBar` for the shared `tstoolbar`.",
         "5. The toolbar drives the active form through `First/Next/Save/...`; the form's buffering commits "
         "through the DBC rules and triggers ([[../03-data-model/README.md]]), and failures surface in "
         "`tsbaseform.Error`.",
         "6. Closing the last form releases the toolbar; Exit runs `Cleanup` → `Cleanup2` → `environment.Reset`.", ""]
    return "\n".join(L)

for fn, gen in (("tsbase.md", gen_tsbase), ("tsgen.md", gen_tsgen), ("README.md", gen_readme)):
    with open(os.path.join(OUT, fn), "w", encoding="utf-8", newline="\n") as f:
        f.write(gen())
    print("wrote", fn)
