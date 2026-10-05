"""Generate docs for the remaining nine forms and finish the forms index."""
import os, re, sys, textwrap
sys.path.insert(0, os.environ.get("VFP_TOOLKIT_TOOLS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "vfp-documentation-toolkit", "tools")))
import foxparse as fp

ROOT = os.environ.get("TASTRADE_ROOT", os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))
OUT = os.path.join(ROOT, "docs", "04-forms")

def load(name):
    r = fp.parse_sc2(os.path.join(ROOT, "forms", name + ".sc2"))
    r["text"] = fp.read(os.path.join(ROOT, "forms", name + ".sc2"))
    r["members"] = re.findall(r"^\s*\*([mpa]):\s*(\S+)\s*(?:&&\s*(.*))?$", r["text"], re.M)
    r["de_methods"] = {}
    m = re.search(r"DEFINE CLASS dataenvironment.*?ENDDEFINE", r["text"], re.S)
    if m:
        for pm in re.finditer(r"^\s*PROCEDURE (\w+)\s*$(.*?)^\s*ENDPROC", m.group(0), re.S | re.M):
            r["de_methods"][pm.group(1)] = textwrap.dedent(pm.group(2)).strip("\n")
    return r

def body(r, method):
    for k in r["methods"]:
        if k.lower() == method.lower():
            return textwrap.dedent(r["methods"][k]).strip("\n")
    raise KeyError(method)

def fence(code): return "```foxpro\n" + code + "\n```"
def unq(v):
    v = (v or "").strip(); return v[1:-1] if len(v) >= 2 and v[0] == v[-1] == '"' else v

def ms(r, method, explain=None):
    L = ["#### `%s`" % method, ""]
    if explain: L += [explain, ""]
    return L + [fence(body(r, method)), ""]

def members(r):
    L = []
    props = [(k, n, d) for k, n, d in r["members"] if k in ("p", "a")]
    meths = [(k, n, d) for k, n, d in r["members"] if k == "m"]
    if props:
        L += ["**Custom properties:**", "", "| Property | Description |", "|---|---|"] + ["| `%s` | %s |" % (n, d or "") for k, n, d in props] + [""]
    if meths:
        L += ["**Custom methods:**", "", "| Method | Description |", "|---|---|"] + ["| `%s` | %s |" % (n, d or "") for k, n, d in meths] + [""]
    return L

def de(r, extra=""):
    if not r["cursors"]:
        L = ["No cursors. " + extra, ""]
    else:
        L = ["| Cursor | Alias | Source | Order |", "|---|---|---|---|"]
        for c in r["cursors"]:
            L.append("| `%s` | `%s` | `%s` | %s |" % (c["object"], c["alias"], c["table"], ("`%s`" % c["order"]) if c["order"] else ""))
        L += ["", extra, ""] if extra else [""]
    for name, code in r["de_methods"].items():
        L += ["DataEnvironment `%s`:" % name, "", fence(code), ""]
    return L

def controls(r, roles):
    L = ["| Container path | Class | Bound to / key properties | Role |", "|---|---|---|---|"]
    for c in r["controls"]:
        p = c["props"]; bits = []
        if p.get("caption"): bits.append("caption %s" % p["caption"])
        if p.get("controlsource") and unq(p["controlsource"]): bits.append("→ `%s`" % unq(p["controlsource"]))
        if p.get("rowsource") and unq(p["rowsource"]): bits.append("rows `%s`" % unq(p["rowsource"]))
        if p.get("enabled") == ".F.": bits.append("disabled")
        if p.get("readonly") == ".T.": bits.append("read-only")
        cls = c["class"] + ("" if c["class"].lower() == c["baseclass"].lower() else " (%s)" % c["baseclass"])
        L.append("| `%s` | `%s` | %s | %s |" % (c["path"], cls, "; ".join(bits), roles.get(c["path"].lower(), "")))
    return L + [""]

def head(r, scx, purpose, used_by, related):
    return ["# %s (%s.scx)" % (r["name"], scx), "", "| Source file | Type | Path |", "|---|---|---|",
            "| `%s.scx` | Form | `forms/%s.sc2` |" % (scx, scx), "", "**Purpose:** " + purpose, "",
            "**Used by:**"] + ["- " + u for u in used_by] + ["", "**Related docs:** " + related, ""]

def meta(lines):
    return ["## Form metadata", ""] + ["- " + l for l in lines] + [""]

def tables(rows):
    return ["## Tables read / written", "", "| Table | Access | How |", "|---|---|---|"] + ["| %s | %s | %s |" % t for t in rows] + [""]

def nav(items): return ["## Inter-form navigation", ""] + ["- " + i for i in items] + [""]
def notes(items): return ["## Notes", ""] + ["- " + i for i in items] + [""]

# ---------------------------------------------------------------- getinv
def gen_getinv():
    r = load("getinv")
    L = head(r, "getinv", "The invoice report's parameter dialog: an order date range, returned to the report's data environment which feeds it to the `ORDERS VIEW` parameters `?dDateFrom` and `?dDateTo`.",
        ["`reports/orders.frx`'s data environment `Init` ([[../06-reports/orders.md]]): `DO FORM forms\\getinv NAME loGetInvoice LINKED`, then reads `lRetVal`, `dDateFrom`, `dDateTo` from the object."],
        "[[../05-classes/tsgen.md]] (`daterange`), [[../03-data-model/README.md]] (`ORDERS VIEW`), [[README.md]].")
    L += ["One of two forms with **no framework base**: the form class is the VFP `form`, named `form1` (the designer default), and its DataEnvironment is empty. It runs inside a report's data environment, so it must not depend on `oApp` or the toolbar. The `daterange` control and the `ts*` buttons are the only framework pieces it uses.", ""]
    L += meta(["Base class / parent: `form` (no framework base); class name `form1`", "Caption: \"Report Parameters\"", "Modal: yes (`WindowType = 1`), `AutoCenter`, no Min/Max buttons", "Run `LINKED` and `NAME`d by the caller, which reads the properties after `Show` returns"])
    L += members(r)
    L += ["## DataEnvironment", ""] + de(r, "The caller (the report) owns the data.")
    L += ["## Controls (depth-first)", ""] + controls(r, {"ctldaterange": "From/To dates; `GetDateFrom()` and `GetDateTo()` (empty To = far future)", "cmdok": "Default; also `Cancel = .T.`, see note", "cmdcancel": "Sets `lRetVal = .F.`", "tslabel1": "\"Order date range:\""})
    L += ["### Events with code", ""] + ms(r, "cmdOK.Click", "Copies the range into the form properties and hides; hiding returns control to the report's `Init`.") + ms(r, "cmdCancel.Click")
    L += ["## Form methods", ""] + ms(r, "Activate") + ms(r, "Unload")
    L += tables([("none", "", "")])
    L += nav(["**← [[../06-reports/orders.md]]** only.", "`lretval` defaults to `.T.`; only Cancel clears it. Closing the dialog any other way counts as OK."])
    L += notes(["**`cmdOK` has both `Default = .T.` and `Cancel = .T.`**, so Escape triggers OK, not Cancel. `cmdCancel` has neither `Cancel` nor `Default`. Probably a designer slip; the visible captions say the opposite.",
                "**No validation on OK** beyond what `daterange.txtDateTo.Valid` did; an empty From date is allowed and means no lower bound.",
                "**Hides rather than releases**, because the caller still needs to read the properties; the caller's `LINKED` clause releases it."])
    return "\n".join(L)

# ---------------------------------------------------------------- gettitle
def gen_gettitle():
    r = load("gettitle")
    L = head(r, "gettitle", "The employee listing report's parameter dialog: pick one employee title from a distinct list, or all titles. Returns the title (or `\"ALL\"`, or empty for Cancel) as the form's return value.",
        ["`reports/listempl.frx`'s data environment `Init` ([[../06-reports/listempl.md]]): `DO FORM forms\\gettitle TO cTitle`, then `RETURN .F.` if empty, and `cTitle = \"\"` when it is `\"ALL\"` so the `EMPLOYEE LISTING` view parameter `?cTitle` matches everything."],
        "[[../03-data-model/README.md]] (`EMPLOYEE LISTING` view), [[../03-data-model/tables/employee.md]], [[README.md]].")
    L += ["The second form with **no framework base**. Uses a plain `combobox`, `checkbox`, and `label` alongside two `tscommandbutton`s, and returns its value through `Unload`'s `RETURN`, the classic VFP `DO FORM ... TO` protocol rather than the framework's `uRetVal`.", ""]
    L += meta(["Base class / parent: `form`; class name `frmGetTitle`", "Caption: \"Report Parameters\"; `ControlBox = .F.`", "Modal (`WindowType = 1`), private data session (`DataSession = 2`), `AutoCenter`"])
    L += members(r)
    L += ["## DataEnvironment", ""] + de(r, "Opens `Employee` so the combo's SQL can run in the private session.")
    L += ["## Controls (depth-first)", ""] + controls(r, {"cbotitle": "Distinct titles via `SELECT DISTINCT Employee.Title ... INTO CURSOR cTitles`; disabled until \"All Titles\" is unchecked", "chkalltitles": "Checked by default", "cmdok": "Default", "cmdcancel": "Cancel", "label1": "\"What employee title would you like to print?\""})
    L += ["### Events with code", ""] + ms(r, "chkAllTitles.InteractiveChange") + ms(r, "cboTitle.InteractiveChange") + ms(r, "cboTitle.Destroy") + ms(r, "cmdOK.Click") + ms(r, "cmdCancel.Click", "Empty title signals Cancel to the report.")
    L += ["## Form methods", ""] + ms(r, "Init") + ms(r, "Unload", "The return value of `Unload` is what `DO FORM ... TO` receives.") + ms(r, "Activate")
    L += tables([("`EMPLOYEE`", "read", "DataEnvironment; `SELECT DISTINCT title` for the combo")])
    L += nav(["**← [[../06-reports/listempl.md]]** only."])
    L += notes(["**Two return conventions in one app**: this form and [[getinv.md]] use `DO FORM ... TO` / `NAME ... LINKED`; the framework dialogs use `uRetVal`.",
                "**`ctitle` defaults to `\"ALL\"`** and the checkbox to checked, so OK without touching anything prints everyone.",
                "**The distinct title list is case- and space-sensitive** to whatever was typed in the employee form."])
    return "\n".join(L)

# ---------------------------------------------------------------- custadd
def gen_custadd():
    r = load("custadd")
    L = head(r, "custadd", "Add one customer from inside order entry. A modal wrapper around the shared `customerinfo` container: appends a blank customer, pre-fills the company name the user typed, and commits on OK.",
        ["[[ordentry.md]] `cboCustomer_ID.Valid`: `DO FORM custadd WITH this.DisplayValue TO llAdded` when a typed customer does not exist; `.T.` on OK."],
        "[[../05-classes/tsgen.md]] (`customerinfo`, which supplies every bound control and the error-to-control mapping), [[customer.md]] (the maintenance form built on the same container), [[../03-data-model/tables/customer.md]], [[README.md]].")
    L += meta(["Base class / parent: `tsbaseform` → `form`", "Caption: \"Add Customer\"", "Modal (`WindowType = 1`), private data session, no toolbar (`ctoolbar` empty), `lallownew = .F.`", "Returns `lretval` from `Unload`"])
    L += members(r)
    L += ["## DataEnvironment", ""] + de(r, "`InitialSelectedAlias = \"Customer\"`; optimistic table buffering inherited from the base form.")
    L += ["## Controls (depth-first)", ""] + controls(r, {"cntcustomerinfo": "The whole entry area; fourteen bound text boxes documented under `customerinfo`", "cmdok": "Default; `TABLEUPDATE`", "cmdcancel": "Cancel; `TABLEREVERT`", "cmdbehindsc": "Opens Behind the Scenes modally; disabled if it is already open"})
    L += ["### Events with code", ""]
    L += ms(r, "cmdOK.Click", "Commits the buffered new row. Failures (duplicate ID 1884, field rule 1582) go to the form's `Error`, which forwards to the container so the right text box gets focus. **NOTE:** `llError` and `laError` are not declared `LOCAL`.")
    L += ms(r, "cmdCancel.Click") + ms(r, "cmdBehindSC.Click", "Runs Behind the Scenes modally because this form is modal, then disables the button for the rest of the dialog.")
    L += ["## Form methods", ""]
    L += ms(r, "Init", "Appends the blank row (firing the DBC defaults) and seeds the company name from the parameter.")
    L += ms(r, "Unload") + ms(r, "Destroy", "Closing from the title bar (`ReleaseType = 1`) counts as Cancel.") + ms(r, "Error") + ms(r, "Activate")
    L += tables([("`CUSTOMER`", "write", "One appended row, committed by OK; the user types the primary key")])
    L += nav(["**← [[ordentry.md]]** only.", "**→ [[behindsc.md]]** modally."])
    L += notes(["**`lretval` defaults to `.T.`**; Cancel and the close box clear it. Any other exit reports success.",
                "**Same container, different form base**: [[customer.md]] uses `tsmaintform` with the toolbar; this uses `tsbaseform` modally with its own OK/Cancel. The container's `Error` works in both because it only touches its own controls."])
    return "\n".join(L)

# ---------------------------------------------------------------- chngpswd
def gen_chngpswd():
    r = load("chngpswd")
    L = head(r, "chngpswd", "Change the logged-in employee's password: old password unlocks the new and confirm boxes, and OK writes the confirmed value. A \"Hint\" box shows the current password.",
        ["The File menu ([[../07-menus/main.md]]) bar \"Change Password\": `DO FORM chngpswd`, `SKIP FOR !EMPTY(WONTOP())` so it is only available when no form is active."],
        "[[../03-data-model/tables/employee.md]] (`password`), [[../05-classes/main.md]] (`GetEmployeeID`, empty in this build), [[../05-classes/login.md]] (the other place the password is displayed), [[README.md]].")
    L += meta(["Base class / parent: `tsbaseform` → `form`", "Caption: \"Change Password\"; `ControlBox = .F.`", "Modal, private data session, no toolbar, `lallowedits = .F.`, `lallownew = .F.`"])
    L += members(r)
    L += ["## DataEnvironment", ""] + de(r, "`Employee` ordered by `employee_i` so `Load` can `SEEK` the logged-in employee.")
    L += ["## Controls (depth-first)", ""] + controls(r, {"txtoldpassword": "Masked; typing the correct old password enables the next two", "txtnewpassword": "Masked; disabled until the old password matches", "txtconfirm": "Masked; disabled until the old password matches", "txthint": "**Shows the current password in clear text**, bound to `Employee.password`", "txtusername": "First and last name, set in `Init`", "cmdok": "Default; validates then saves", "cmdcancel": "Cancel; `TABLEREVERT`", "cmdbehindsc": "Behind the Scenes, modal", "tslabel5": "\"Hint\""})
    L += ["### Events with code", ""]
    L += ms(r, "txtOldPassword.InteractiveChange", "Compares on every keystroke; the new-password boxes light up the moment the old one matches. Trimmed, case-sensitive.")
    L += ms(r, "cmdOK.Click", "`REPLACE` then `TABLEUPDATE()`, no transaction, no error check on the update.") + ms(r, "cmdCancel.Click") + ms(r, "cmdBehindSC.Click")
    L += ["## Form methods", ""]
    L += ms(r, "Load", "Positions on `oApp.GetEmployeeID()`. **NOTE:** in this build the ID is empty (`DEBUGMODE`, [[../05-classes/main.md]]), the `SEEK` fails, and the form sits on the **first employee record**, so the password changed is Steven Buchanan's, not the user's.")
    L += ms(r, "Init") + ms(r, "validate", "Three checks: old password never entered (offer to abandon), new password empty, confirm mismatch. Returns `.F.` on any of them; the implicit `.T.` otherwise.")
    L += ms(r, "Activate")
    L += tables([("`EMPLOYEE`", "write (`password`)", "`REPLACE` on the positioned row, `TABLEUPDATE`")])
    L += nav(["**← File menu**.", "**→ [[behindsc.md]]** modally."])
    L += notes(["**The password is displayed** while the user is asked to prove they know it.",
                "**Wrong employee under `DEBUGMODE`**: with no logged-in ID the form edits the first employee.",
                "**No strength or length rules**; `password` is `C(8)`, so anything longer is silently truncated by the field width.",
                "**`ControlBox = .F.`** with a Cancel button as the only way out."])
    return "\n".join(L)

# ---------------------------------------------------------------- reports
def gen_reports():
    r = load("reports")
    L = head(r, "reports", "The report picker: choose Reports or Listings, pick one from the list held in the free table `repolist.dbf`, and send it to preview, printer, or an ASCII text file.",
        ["The File menu ([[../07-menus/main.md]]) bar \"Print Reports ...\": `DO FORM Reports`."],
        "[[../03-data-model/README.md]] (`repolist.dbf` schema and rows), [[../06-reports/README.md]] (the ten reports it can run), [[README.md]].")
    L += meta(["Base class / parent: `tsbaseform` → `form`", "Caption: \"Print\"", "Modal, **default data session**, no toolbar, `lallowedits = .F.`, `lallownew = .F.`"])
    L += members(r)
    L += ["## DataEnvironment", ""] + de(r, "`repolist.dbf` is a free table (not in the DBC) with `cdosname`, `cfullname`, `ctype` (`REPO` or `LIST`); ten rows listing the reports by display name.")
    L += ["## Controls (depth-first)", ""] + controls(r, {"opgoutputtype": "`optReports` / `optListings`; drives the filter on `repolist`", "lstreport": "`RowSourceType = 6` over `cfullname, cdosname`, `BoundColumn = 2` so `Value` is the file stem", "opgoutput": "`optScreen` (preview, default) / `optPrinter` / `optFile`", "cmdrun": "Default", "cmdclose": "Cancel", "tslabel1": "\"Output Type\""})
    L += ["### Events with code", ""]
    L += ms(r, "cmdRun.Click", "Builds `REPORTS\\<stem>.FRX`, checks it exists, then `REPORT FORM` with `PREVIEW`, `TO PRINTER NOCONSOLE` (after `PRINTSTATUS()`), or `TO FILE <stem>.TXT ASCII`. **NOTE:** the text file lands in the current directory and `lcTextFile` is not `LOCAL`. **NOTE:** reports whose data environment runs a dialog (invoices, employee listing) show that dialog from here; the rest open the DBC views themselves.")
    L += ms(r, "opgOutputType.Click") + ms(r, "lstReport.DblClick") + ms(r, "lstReport.KeyPress", "Enter would fire both the list's `DblClick` and the default button's `Click`, running the report twice; the handler swallows Enter and calls `DblClick` once.") + ms(r, "lstReport.Init", "Refuses to instantiate the list if the table is empty, which VFP treats as an error.")
    L += ["## Form methods", ""]
    L += ms(r, "Refresh", "Filters `repolist` to `REPO` or `LIST` by macro-substituted `SET FILTER` and requeries the list.") + ms(r, "Init") + ms(r, "Destroy", "Restores the work area that was selected before the form opened.") + ms(r, "cmdClose.Click")
    L += tables([("`repolist.dbf` (free)", "read", "DataEnvironment, filtered by type"), ("everything the chosen report reads", "read", "through the report's own data environment or the DBC views")])
    L += nav(["**← File menu**.", "**→ every report** in `reports/*.frx` by name from `repolist`; the invoice and employee reports open [[getinv.md]] and [[gettitle.md]] from their data environments."])
    L += notes(["**Report list is data**, so a report can be added or hidden by editing `repolist.dbf`; a stem with no matching `.frx` shows \"Report file not found.\"",
                "**`&lcFilter` macro** in `Refresh`.",
                "**`ReleaseErase`, `TerminateRead`, `ReadSize`** are FoxPro 2.x screen-conversion properties left on the controls; inert in VFP."])
    return "\n".join(L)

# ---------------------------------------------------------------- rebuild
def gen_rebuild():
    r = load("rebuild")
    L = head(r, "rebuild", "Database utilities: reindex every table in the DBC and/or validate the DBC, writing the validation output to a temporary file that is shown read-only.",
        ["The Utilities menu ([[../07-menus/main.md]]) bar \"Rebuild DBC/Reindex\": `DO FORM rebuild`, `SKIP FOR !EMPTY(WONTOP())`."],
        "[[../03-data-model/README.md]], [[README.md]].")
    L += meta(["Base class / parent: `tsbaseform` → `form`", "Caption: \"Database Utilities\"", "Modal, **`DataSession = 1`** (the default session, set explicitly), no toolbar, new/edit/delete off", "Empty DataEnvironment; it works on whatever database is current"])
    L += members(r)
    L += ["## DataEnvironment", ""] + de(r, "Operates on `DBC()` of the default session, which the application opened at start-up.")
    L += ["## Controls (depth-first)", ""] + controls(r, {"chkrebuild": "\"Rebuild Indexes\"", "chkvalidate": "\"Validate DBC\"", "cmdok": "Default; disabled until a box is checked", "cmdcancel": "Cancel"})
    L += ["### Events with code", ""] + ms(r, "cmdOK.Click") + ms(r, "chkRebuild.Click") + ms(r, "chkValidate.Click") + ms(r, "cmdCancel.Click")
    L += ["## Form methods", ""]
    L += ms(r, "rebuildindexes", "`CLOSE TABLES`, then for each table in the DBC, `USE ... EXCLUSIVE` and `REINDEX`. **NOTE:** `CLOSE TABLES` in the default session closes the tables other open forms' shared cursors may depend on, and any table another user has open makes the exclusive `USE` fail with an error the base `Error` handler shows. Meant for a single user with everything closed, which the menu's `SKIP FOR !EMPTY(WONTOP())` half-enforces.")
    L += ms(r, "validatedbc", "`VALIDATE DATABASE TO FILE` into `valdbc.txt` in the current directory, shown with `MODIFY FILE ... NOMODIFY`, then deleted. The `#DEFINE OUTFILE` inside a method is a compile-time constant local to that method's compilation.")
    L += tables([("every table in `tastrade.dbc`", "reindex (exclusive)", "`ADBOBJECTS` loop"), ("`valdbc.txt`", "write, then delete", "validation output")])
    L += nav(["**← Utilities menu** only."])
    L += notes(["**Exclusive access in a shared app**; the sample's `SET EXCLUSIVE OFF` elsewhere is overridden here per table.",
                "**Does not touch the three free tables** (`behindsc`, `repolist`, `ttrade`), which are not in the DBC.",
                "**`WAIT WINDOW` progress** and `MODIFY FILE` are IDE-style UI; a runtime EXE shows them too, as plain windows."])
    return "\n".join(L)

# ---------------------------------------------------------------- behindsc
def gen_behindsc():
    r = load("behindsc")
    L = head(r, "behindsc", "The sample's self-documentation: a list of design topics per form, read from the free table `behindsc.dbf`, with an explanation pane and a **Code** button that extracts the referenced methods, properties, programs, or stored procedures from the live `.scx`, `.vcx`, `.prg`, and `.dbc` files and shows them in a viewer.",
        ["The Maintenance menu ([[../07-menus/main.md]]) bar \"Behind the Scenes\": `oApp.DoForm(\"behindsc\")`, `SKIP FOR WEXIST(\"frmBehindSC\")`.",
         "The navigation toolbar's `cmdBehindSC` ([[../05-classes/tsbase.md]]): `oApp.DoForm(\"behindsc\")`.",
         "`introform` ([[../05-classes/tsgen.md]]), [[custadd.md]], and [[chngpswd.md]]: `DO FORM behindsc WITH .T.` (modal, because those callers are modal)."],
        "[[viewcode.md]] (the viewer it opens), [[../03-data-model/README.md]] (`behindsc.dbf` schema), [[../05-classes/tsgen.md]] (`splitter`), [[../06-reports/behindsc.md]] (the print), [[README.md]].")
    L += ["This form is the reason the sample calls itself \"discoverable\". Its `showcode` method opens `.scx` and `.vcx` files **as tables** (`USE ... ALIAS showmeth NOUPDATE`), locates the object record by `objname`, and pulls text out of the `methods` and `properties` memo fields, which is exactly what FoxBin2PRG does for this documentation, written in 1995 inside the application it documents.", ""]
    L += meta(["Base class / parent: `tsbaseform` → `form`", "Caption: \"Behind the Scenes\"", "Modal or not depending on the `tlModal` parameter (`WindowType` set in `Init`); default data session; no toolbar; `BufferMode = 0`; new/edit/delete off", "Filters itself to the form that was active when it opened (`ccurrentform` from `_screen.ActiveForm.Caption`)"])
    L += members(r)
    L += ["## DataEnvironment", ""] + de(r, "`behindsc.dbf` is a free table: `screen_id` (form name), `topic`, `desc` (memo, the explanation), `code_to_sh` (memo, extraction instructions). 65 rows over 21 screens, 53 with code instructions. Order `screen_top` is `screen_id + topic`.")
    L += ["## Controls (depth-first)", ""] + controls(r, {"cboforms": "Form filter; row source is the `aForms` array (\"All\" plus every distinct `screen_id`)", "lstfeatures": "Topics in the current filter, `RowSourceType = 6` on `behindsc.topic`", "edtfeaturetext": "The explanation, read-only, bound to `behindsc.desc`", "cmdcode": "Runs `showcode`; enabled only when the topic has `code_to_sh`", "cmdprint": "Prints the current topic with `REPORT FORM behindsc NEXT 1`", "cmdclose": "Cancel", "ctlsplitter": "Drag bar between list and text (see note)", "lblselectfeature": "\"Design Feature\"", "lblhowitworks": "\"How It Works\""})
    L += ["### The `code_to_sh` instruction format", "",
          "Each line of the memo is `file, object, method` where object and method may be `*` (all), a single name, or a parenthesised comma list. Examples from the data:", "",
          "```", "ordentry.scx, cmdFind, click", "tsbase.vcx, tsgrid, (refresh, sumcolumn)", "behindsc.scx, cmdcode, click", "tastrade.dbc, newid,", "tsbase.vcx, tspasswordtextbox, *", "```", "",
          "The last example, under \"Hiding Login Passwords\", names a class `tspasswordtextbox` that does not exist in `tsbase.vcx` (see [[../05-classes/tsbase.md]]); the Code button for that topic reports the object was not found. The self-documentation has drifted from the code it documents.", "",
          "### Events with code", ""]
    L += ms(r, "cboForms.InteractiveChange", "Changing the form filter re-filters and re-orders the table (by topic when \"All\") with a macro-substituted `SET FILTER`.")
    L += ms(r, "cboForms.ProgrammaticChange") + ms(r, "lstFeatures.InteractiveChange") + ms(r, "lstFeatures.Requery") + ms(r, "cmdCode.Click") + ms(r, "cmdPrint.Click", "The confirmation prompt is commented out.") + ms(r, "cmdClose.Click")
    L += ["`lstFeatures.Move`, `edtFeatureText.Move`, and `lblHowItWorks.Move` are overridden with **empty bodies**:", "", fence(body(r, "lstFeatures.Move") or "* (empty)"), "",
          "**NOTE:** the splitter calls `Move()` with no arguments on each of these three objects. With the override empty and no `NODEFAULT`, the native `Move` runs with no coordinates, which either errors (swallowed by the splitter's `lSetErrorOff`) or does nothing. Either way no object is repositioned: dragging the splitter moves the bar and nothing else. The resize feature is dead, and was presumably left this way once the empty overrides stopped it crashing.", "",
          "## Form methods", ""]
    L += ms(r, "Load", "Captures the active form's caption as the starting filter, stripping the `:n` instance suffix and the \" for <customer>\" suffix the order history form adds.")
    L += ms(r, "Init", "Modal or modeless by parameter; disables the toolbar's Behind the Scenes button; builds the form list from `SELECT DISTINCT screen_id`, inserting \"All\" first; loads the three objects the splitter should move; filters to the current form.")
    L += ms(r, "Destroy", "Removes the menu entry, the code window and its temp file, re-enables the toolbar button, nulls the object references.")
    L += ms(r, "refreshfeatures") + ms(r, "refreshform")
    L += ms(r, "showcode", "The extractor. For each instruction line: resolve the file type from its extension; programs are copied whole from `PROGS\\`; stored procedures are pulled from the DBC via `COPY PROCEDURES TO` a temp file and searched for `FUNCTION name` ... `ENDFUNC`; forms and classes are opened as tables, the object located by `objname`, and the `properties` memo dumped plus the `methods` memo searched for `PROCEDURE name` ... `ENDPROC`. Everything is written to `SNIPPETS.TXT`, loaded into a one-row cursor `viewcode`, and shown by [[viewcode.md]] in this form's data session. **NOTE:** `USE (lcFileName) AGAIN ... NOUPDATE` opens the running application's own `.scx`/`.vcx` files; works in the IDE and from an EXE as long as the source files are present beside it.")
    for m in ("extractmethod", "extractallmethods", "extractmultimethods", "extractallproperties", "extractprg", "extractstoredproc", "extractmultistoredprocs", "extractallstoredprocs", "procstomem", "getfilename", "getobject", "getmethod"):
        L += ms(r, m)
    L += tables([("`behindsc.dbf` (free)", "read", "DataEnvironment; filtered and reordered by code"), ("`forms/*.scx`, `libs/*.vcx`", "read as tables", "`showcode`, alias `showmeth`, `NOUPDATE`"), ("`progs/*.prg`", "read", "low-level file I/O"), ("`tastrade.dbc` stored procedures", "read", "`COPY PROCEDURES TO`"), ("`SNIPPETS.TXT`, `sproc.txt`", "write, then delete", "temp files in the current directory")])
    L += nav(["**← Maintenance menu, toolbar, intro form, add-customer, change-password.**", "**→ [[viewcode.md]]** with this form's `DataSessionID` so the viewer can bind to the `viewcode` cursor."])
    L += notes(["**A source extractor inside the app.** Reading `.scx`/`.vcx` as DBF tables and splitting the `methods` memo on `PROCEDURE` is the same technique this documentation's tool chain uses. `extractmethod`'s search for `PROCEDURE name` would also match `PROCEDURE namexyz`; the sample gets away with it.",
                "**The splitter is dead** (see above).",
                "**Stale instructions in the data**: `tspasswordtextbox` does not exist.",
                "**Macro-substituted `SET FILTER`** in two places; **undeclared `lnMethEndPos`** in `extractmethod`; `tnFileHandle` assigned but unused in `extractallstoredprocs` (the `@` by-reference call is the intent).",
                "**Temp files in the current directory** and a `RELEASE WINDOW \"SNIPPETS.TXT\"` for a window that is never created by this code."])
    return "\n".join(L)

# ---------------------------------------------------------------- casestdy
def gen_casestdy():
    r = load("casestdy")
    L = head(r, "casestdy", "A read-only viewer for the \"Case Study\" text stored in `behindsc.dbf` under `screen_id = \"*Case Study\"`, with a Print button that runs the `casestdy` report.",
        ["**Nothing.** No menu, form, class, or program in the source runs this form. It is in the project (`Case Study Form`) and builds into the EXE, but it is reachable only by `DO FORM casestdy` from the Command window."],
        "[[../05-classes/tsbase.md]] (`tstextform`), [[../06-reports/casestdy.md]], [[behindsc.md]] (the same table), [[README.md]].")
    L += meta(["Base class / parent: `tstextform` → `tsbaseform` → `form`", "Caption: \"Case Study\"", "Modal (`WindowType = 1`), private data session, no toolbar, no buffering (`BufferMode = 0`), new/edit/delete off", "`edtText.ControlSource = \"behindsc.desc\"`, white background"])
    L += ["## DataEnvironment", ""] + de(r, "Free table `behindsc.dbf`; `Load` positions on the `*Case Study` row via `SEEKVALUE_LOC`.")
    L += ["## Controls (depth-first)", "", "No controls of its own; `edtText`, `cmdClose`, `cmdPrint` come from `tstextform`.", "", "### Events with code", ""]
    L += ms(r, "cmdPrint.Click", "The `tstextform` base leaves `cmdPrint.Click` empty; this form supplies it: confirm, hourglass, `PRINTSTATUS()`, `REPORT FORM casestdy TO PRINTER NOCONSOLE`.")
    L += ["## Form methods", ""] + ms(r, "Load", "`SEEK(\"*Case Study\", ALIAS(), \"screen_id\")`. The `screen_id` rows starting with `*` are excluded from the Behind the Scenes list by its `screen_id <> \"*\"` filter, which is how the two forms share one table.")
    L += tables([("`behindsc.dbf` (free)", "read", "one row")])
    L += nav(["**← nothing.**"])
    L += notes(["**Unreachable in the shipped application.** Either a menu item was removed or it was only ever run by hand.",
                "**Print confirmation text** `VIEWCSDTYPRINT_LOC` is identical to `VIEWCODEPRINT_LOC`."])
    return "\n".join(L)

# ---------------------------------------------------------------- viewcode
def gen_viewcode():
    r = load("viewcode")
    L = head(r, "viewcode", "The code window Behind the Scenes opens to display extracted source. A `tstextform` bound at run time to the `code` memo of a cursor named `viewcode` in the caller's data session.",
        ["[[behindsc.md]] `showcode`: `DO FORM viewcode WITH thisform.DataSessionID` after creating `CREATE CURSOR viewcode (code M)` and loading `SNIPPETS.TXT` into it."],
        "[[../05-classes/tsbase.md]] (`tstextform`), [[../06-reports/viewcode.md]], [[README.md]].")
    L += meta(["Base class / parent: `tstextform` → `tsbaseform` → `form`", "Caption: \"Code Window\"; `MaxButton = .F.`", "Inherits `tstextform`'s modal `WindowType = 1` and `DataSession = 2`, but `Init` immediately switches `DataSessionID` to the caller's session, which is the only way it can see the caller's cursor", "`edtText.ColorSource = 0`, `ControlSource` cleared in the designer and set in `Init`"])
    L += ["## DataEnvironment", ""] + de(r, "The `viewcode` cursor belongs to the caller.")
    L += ["## Controls (depth-first)", "", "No controls of its own.", "", "### Events with code", ""]
    L += ms(r, "cmdPrint.Click", "Prints the extracted code with `REPORT FORM viewcode`, whose single field expression is `viewcode.code`.")
    L += ["## Form methods", ""] + ms(r, "Init", "**NOTE:** `LPARAMETER` (singular) works but is unusual; the data session switch is the whole point of the method.")
    L += tables([("cursor `viewcode`", "read", "in the caller's session")])
    L += nav(["**← [[behindsc.md]]** only."])
    L += notes(["**Adopts the caller's data session** rather than receiving data; the reverse of the order history form, which pushes rows into another session.",
                "**Same print pattern** as the case study form, copy-pasted with a different report name."])
    return "\n".join(L)

def update_readme():
    p = os.path.join(OUT, "README.md"); s = open(p, encoding="utf-8").read()
    for scx in ("getinv", "gettitle", "custadd", "chngpswd", "reports", "rebuild", "behindsc", "casestdy", "viewcode"):
        s = re.sub(r"(\| `forms/%s\.scx` \|[^\n]*\| )pending \|" % scx, r"\1[[%s.md]] |" % scx, s)
    # idempotent: an earlier version re-applied this on every run and tripled the sentence
    s = re.sub(r"(All seventeen are documented\. The six maintenance forms share the `tsmaintform` pattern described in \[\[\.\./05-classes/tsbase\.md\]\]; `casestdy` is launched by nothing in the source\. ?)+",
               "All seventeen are documented. The six maintenance forms share the `tsmaintform` pattern described in [[../05-classes/tsbase.md]]; `casestdy` is launched by nothing in the source. ", s)
    if "All seventeen are documented" not in s:
        s = s.replace("The six maintenance forms share the `tsmaintform` pattern described in [[../05-classes/tsbase.md]].",
                      "All seventeen are documented. The six maintenance forms share the `tsmaintform` pattern described in [[../05-classes/tsbase.md]]; `casestdy` is launched by nothing in the source.")
    open(p, "w", encoding="utf-8", newline="\n").write(s)

for fn, gen in (("getinv.md", gen_getinv), ("gettitle.md", gen_gettitle), ("custadd.md", gen_custadd), ("chngpswd.md", gen_chngpswd),
                ("reports.md", gen_reports), ("rebuild.md", gen_rebuild), ("behindsc.md", gen_behindsc), ("casestdy.md", gen_casestdy), ("viewcode.md", gen_viewcode)):
    with open(os.path.join(OUT, fn), "w", encoding="utf-8", newline="\n") as f:
        f.write(gen())
    print("wrote", fn)
update_readme(); print("README updated")
