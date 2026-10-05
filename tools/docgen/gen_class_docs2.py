"""Generate docs/05-classes/{main,login,about,orders}.md for Tastrade and update the index.
Method bodies are quoted verbatim from the twins via foxparse; prose is hand-written."""
import os, re, sys, textwrap
sys.path.insert(0, os.environ.get("VFP_TOOLKIT_TOOLS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "vfp-documentation-toolkit", "tools")))
import foxparse as fp

ROOT = os.environ.get("TASTRADE_ROOT", os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))
OUT = os.path.join(ROOT, "docs", "05-classes")

def load(lib):
    r = fp.parse_vc2(os.path.join(ROOT, "libs", lib))
    text = fp.read(os.path.join(ROOT, "libs", lib))
    classes = {c["name"]: c for c in r["classes"]}
    for name, parent, clib, body in fp._split_classes(text):
        c = classes[name]
        c["members"] = re.findall(r"^\s*\*([mpa]):\s*(\S+)\s*(?:&&\s*(.*))?$", body, re.M)
        m = re.search(r"DEFINE CLASS %s\b[^\n]*?&&\s*(.*)$" % re.escape(name), text, re.M)
        c["desc"] = (m.group(1).strip() if m else "")
        prot = re.search(r"^\s*PROTECTED\s+([^\n]+)$", body, re.M)
        c["protected"] = [p.strip() for p in prot.group(1).split(",")] if prot else []
    return classes

def body(c, method):
    for k in c["methods"]:
        if k.lower() == method.lower():
            return textwrap.dedent(c["methods"][k]).strip("\n")
    raise KeyError("%s.%s" % (c["name"], method))

def fence(code): return "```foxpro\n" + code + "\n```"
def is_trivial(code): return all(l.strip().startswith("*") for l in code.splitlines() if l.strip())

def header(title, srcfile, twin, purpose, used_by, related):
    L = ["# %s" % title, "", "| Source file | Type | Path |", "|---|---|---|",
         "| `%s` | Class library | `%s` |" % (srcfile, twin), "", "**Purpose:** " + purpose, "", "**Used by:**"]
    L += ["- " + u for u in used_by]
    L += ["", "**Related docs:** " + related, ""]
    return L

def members_table(c):
    L = []
    props = [(k, n, d) for k, n, d in c["members"] if k in ("p", "a")]
    meths = [(k, n, d) for k, n, d in c["members"] if k == "m"]
    prot = [p.lower() for p in c["protected"]]
    if props:
        L += ["**Custom properties:**", "", "| Property | Protected | Description |", "|---|---|---|"]
        L += ["| `%s` | %s | %s |" % (n, "yes" if n.split("[")[0].lower() in prot else "", d or "") for k, n, d in props]
        L.append("")
    if meths:
        L += ["**Custom methods:**", "", "| Method | Protected | Description |", "|---|---|---|"]
        L += ["| `%s` | %s | %s |" % (n, "yes" if n.lower() in prot else "", d or "") for k, n, d in meths]
        L.append("")
    return L

def method_section(c, method, explain, protected=False):
    code = body(c, method)
    L = ["#### `%s`%s" % (method, " (protected)" if protected else ""), ""]
    if explain: L += [explain, ""]
    L += (["Body holds only a copyright comment; no code.", ""] if is_trivial(code) else [fence(code), ""])
    return L

# ================================================================= main
def gen_main():
    C = load("main.vc2"); c = C["tastrade"]
    L = header("main.vcx — the tastrade application object", "main.vcx", "libs/main.vc2",
        "The one concrete class of the application: `tastrade` extends the framework's `application` "
        "([[tsgen.md]]) and fills in what that class leaves abstract: the database to open, the window "
        "caption, the intro screen, login, the logged-in employee and user level, and the user level's "
        "startup action.",
        ["`progs/main.prg` ([[../08-programs/main.md]]) creates it: `oApp = CREATEOBJECT(\"TasTrade\")`, then "
         "calls `oApp.Do()`. Every other class and form reaches it as the global `oApp`.",
         "`menus/main.mn2` ([[../07-menus/main.md]]) calls `oApp.Login()`, `oApp.GetUserLevel()`, "
         "`oApp.DoMenu()`, `oApp.DoForm()`; `SKIP FOR` conditions on menu bars test `oApp.GetUserLevel()`.",
         "The DBC stored procedure `DefaultEmployee()` ([[../03-data-model/README.md]]) calls "
         "`oApp.GetEmployeeID()` to stamp new orders."],
        "[[tsgen.md]] (`application`, whose `Init`, `Do`, and `Login` this class overrides), [[login.md]] "
        "(`loginpicture`, the dialog `Login` runs), [[../03-data-model/tables/user_level.md]] "
        "(`startup_action`), [[../08-programs/main.md]], [[README.md]].")
    L += ["## Classes in this library", "", "### tastrade (extends application OF tsgen.vcx)", "",
          "**Purpose:** " + c["desc"] + " Sets `cdatabase = DATA\\TASTRADE` and `cMainWindCaption = TASTRADE_LOC` "
          "(\"Tasmanian Traders\"). Declares `ainstances`, `cemployeeid`, `cmainwindcaption`, `cuserlevel` as "
          "`PROTECTED`, so the rest of the app must go through `GetEmployeeID()` and `GetUserLevel()`.", ""]
    L += members_table(c)
    L += ["#### Start-up sequence", "",
          "```mermaid", "flowchart TD",
          "    A[main.prg: oApp = CREATEOBJECT] --> B[tastrade.Init]",
          "    B --> C[application::Init<br/>environment, OPEN DATABASE, hide toolbars]",
          "    C --> D[DO menus\\intro.mpr]",
          "    D --> E{INI ShowIntroForm?}",
          "    E -- yes --> F[DoFormRetVal introform]",
          "    E -- no --> G[lnRetVal = 1]",
          "    F --> H{1 Continue / 2 Exit}",
          "    G --> H",
          "    H -- 2 --> X[Cleanup, Cleanup2, RETURN .F.]",
          "    H -- 1 --> I{DEBUGMODE?}",
          "    I -- .T. --> J[cEmployeeID = '' <br/> cUserLevel = APPLICATIONS DEVELOPER]",
          "    I -- .F. --> K[Login -> loginpicture]",
          "    J --> L[main.prg: oApp.Do]",
          "    K --> L",
          "    L --> M[DO MAIN.MPR]",
          "    M --> N{DEBUGMODE?}",
          "    N -- .F. --> O[&lcAction from user_level.startup_action]",
          "    N -- .T. --> P[READ EVENTS loop]",
          "    O --> P",
          "```", "",
          "**NOTE:** `DEBUGMODE` is `.T.` in `include/tastrade.h`. In this build the login dialog never "
          "appears, the employee ID is empty, the user level is hard-set to `USER_APPDEV_LOC` "
          "(\"APPLICATIONS DEVELOPER\", the level with no startup action), and the startup action is never "
          "executed. The security and personalisation features described in the sample's own \"Behind the "
          "Scenes\" text only work in a build with `DEBUGMODE` off. `DefaultEmployee()` in the DBC then falls "
          "back to the first employee record for every new order.", "",
          "#### Methods", ""]
    L += method_section(c, "Init",
        "Overrides `application.Init`. After the base initialisation succeeds, runs the intro menu, reads "
        "`[Defaults] ShowIntroForm` from `tastrade.ini` (default: show), and shows `introform` "
        "([[tsgen.md]]) as a return-value form. Continue leads to login, or to the debug shortcut; Exit, or "
        "a failed login, runs `Cleanup`/`Cleanup2` and returns `.F.`, which makes `CREATEOBJECT` in "
        "`main.prg` yield no object so the app never starts its event loop.")
    L += method_section(c, "do",
        "Overrides `application.Do` rather than calling it: runs the main menu, executes the user level's "
        "startup action by macro substitution (`&lcAction`) when not in debug mode, then the same "
        "`READ EVENTS` / `Cleanup` loop as the base. The comment explains why cleanup is here and not in "
        "the menu: windows cannot be released from menu code while a grid has focus.")
    L += method_section(c, "login",
        "Runs `loginpicture` ([[login.md]]) and parses its return string `employee_id,user level`. An empty "
        "user level (Cancel or a failed login) restores the previous values, so the Login menu item can be "
        "cancelled without logging the current user out. Returns whether a user level is set. "
        "**NOTE:** `lcLoginString` is not declared `LOCAL`.")
    L += method_section(c, "getstartupaction",
        "Looks up `startup_action` in `USER_LEVEL` by matching `cUserLevel` against the `description` "
        "column through the `DESCRIPTIO` tag, so the user level is carried around as its **description "
        "text**, upper-cased, not its `group_id`. Opens `user_level` directly if it is not already open. "
        "The value is a VFP command string; see [[../03-data-model/tables/user_level.md]].", protected=True)
    L += method_section(c, "getemployeeid", None)
    L += method_section(c, "getuserlevel", None)
    L += ["## Notes", "",
          "- **Two debug gates.** `DEBUGMODE` short-circuits both login and the startup action. Anyone "
          "evaluating the sample's security should set it to `.F.` and rebuild first.",
          "- **User level by description.** The menu, the login dialog, and this class all pass the user level "
          "as the description string (`\"APPLICATIONS DEVELOPER\"`, `\"OPERATIONS MANAGER\"`, defined as "
          "`USER_*_LOC` in `tastrade.h`), matched case-insensitively. Renaming a group in the table breaks "
          "menu security silently.",
          "- **Login can be repeated** from the File menu; a change of user level re-runs `DoMenu()` so the "
          "`SKIP FOR` conditions are re-evaluated.",
          "- **Direct `USE user_level`** in `getstartupaction`, outside any DataEnvironment.", ""]
    return "\n".join(L)

# ================================================================= login
def gen_login():
    C = load("login.vc2")
    L = header("login.vcx — login dialogs", "login.vcx", "libs/login.vc2",
        "Two modal dialogs that authenticate an employee against the `EMPLOYEE` table: `login` (name combo "
        "and password) and `loginpicture`, the one the application actually uses, which adds the employee's "
        "title, notes, photo, user level, and, under a label reading \"Hint\", the password itself.",
        ["`tastrade.Login` ([[main.md]]) runs `loginpicture` through `DoFormRetVal` and parses the returned "
         "`employee_id,user level` string. Only when `DEBUGMODE` is off.",
         "`application.Login` ([[tsgen.md]]) runs the plain `login`, but `tastrade` overrides it, so the "
         "plain class is not used by the shipped application.",
         "The File menu's Login item ([[../07-menus/main.md]]) calls `oApp.Login()` to switch users."],
        "[[main.md]], [[tsgen.md]] (`tsformretval` base, via [[tsbase.md]]), "
        "[[../03-data-model/tables/employee.md]] (`password`, `group_id`, `photo_file`), "
        "[[../03-data-model/tables/user_level.md]].")
    L += ["## Classes in this library", ""]
    c = C["login"]
    L += ["### login (extends tsformretval OF tsbase.vcx)", "",
          "**Purpose:** " + c["desc"] + " A modal form in its own data session (`DataSession = 2`) with a "
          "drop-down of employees (`cboName`, SQL row source, `BoundColumn = 2` so the value is the "
          "`employee_id`), a masked password box (`txtPassword`, `PasswordChar = \"*\"`), OK and Cancel. "
          "The table, field, and tag names are properties, so the class could authenticate against another "
          "table; the shipped values are `employee`, `last_name, employee_id`, `password`, `employee_i`. "
          "`HelpContextID = 10` links it to the help file. The class icon path in `CLASSDATA` is "
          "`h:\\allisonk\\sampapp\\login_s.bmp`, another trace of the original author's machine.", ""]
    L += members_table(c)
    L += ["#### Methods", ""]
    L += method_section(c, "Load",
        "Opens the employee table directly from the relative path `DATA\\employee` if it is not already open "
        "in this session. **NOTE:** direct `USE` on a path relative to the current directory, outside any "
        "DataEnvironment and without the `tastrade!` prefix; also `FILE(\"DATA\\employee\")` tests for a name "
        "with no extension, so whether the table is opened here or later by the SQL in `Init` depends on "
        "how `FILE()` treats it. Either way the dialog works because the SQL opens `employee` itself.")
    L += method_section(c, "Init",
        "Guarded by `gTTrade`. Builds the combo's SQL from the property names (`SELECT last_name, employee_id "
        "FROM employee ORDER BY last_name, employee_id INTO CURSOR cNames`), requeries, and selects the "
        "first employee. No employees means the dialog refuses to open. **NOTE:** the combo lists employees "
        "by last name only, so two employees with the same last name are indistinguishable.")
    L += method_section(c, "Refresh",
        "Positions the employee table on the selected employee with `LOOKUP()` on the `employee_i` tag, so "
        "`cmdOk.Click` and the subclass can read that record's fields. Uses `&lcFldName` macro substitution "
        "for a field name that is a literal in the line above it.")
    L += method_section(c, "Unload", "Closes the names cursor and the employee table.")
    L += method_section(c, "cboName.InteractiveChange", None)
    L += method_section(c, "cmdOk.Click",
        "The whole authentication: the trimmed stored password must equal the trimmed typed password, "
        "compared with `==` after `ALLTRIM` so trailing spaces do not matter. **Case-sensitive**, plain text. "
        "Failure shows `BADPASSWORD_LOC`, which reads \"Password is invalid. (See Hint textbox)\", clears the "
        "box, and stays on the form.")
    L += method_section(c, "cmdCancel.Click", "Cancel sets `uRetVal = .F.`; the subclass overrides this to return an empty string.")

    c = C["loginpicture"]
    L += ["### loginpicture (extends login)", "",
          "**Purpose:** " + c["desc"] + " The dialog the application shows. Adds read-only `txtTitle`, "
          "`edtDescription` (the employee's notes), `imgPhoto` (from `photo_file`, `Stretch = 1`), "
          "`txtUserLevel` (looked up from `USER_LEVEL`), and `txtDispPswd` under the label **\"Hint\"**, "
          "which displays the selected employee's password. Returns `employee_id + \",\" + user level "
          "description` in `uRetVal`, or an empty string on Cancel.", "",
          "**NOTE:** the password is shown on the login screen. The sample's `behindsc` topic \"Hiding Login "
          "Passwords\" and the `PasswordChar` mask on the entry box are undone by the hint box next to it. "
          "Intentional for a demo where every password is `Tastrade`; never to be copied.", ""]
    L += members_table(c)
    L += ["#### Methods", ""]
    L += method_section(c, "Init", "Runs the base `Init` (which fills the combo) and then `Refresh` so the picture and details show for the first employee.")
    L += method_section(c, "Refresh",
        "After the base positions the employee record, copies `title`, `notes`, `password`, the photo (only if "
        "the file in `photo_file` exists), and the user level into the display controls. The `ELSE` branch's "
        "`STORE \"\" TO` list is broken across two statements by a missing continuation, so "
        "`thisform.txtUserLevel.Value` on its own line is a no-op expression rather than part of the store. "
        "Harmless because the base `Refresh` has no `RETURN` value and the `ELSE` never runs. **NOTE:** "
        "`IF login::Refresh()` tests the return of a method that returns nothing, which VFP evaluates as `.T.`.")
    L += method_section(c, "getuserlevel",
        "Looks up the `USER_LEVEL` description for the employee's `group_id` through the `group_id` tag. "
        "`SET DATABASE TO TASTRADE` first because the form runs in a private data session. Direct `USE "
        "user_level` if needed.")
    L += method_section(c, "cmdok.Click",
        "Runs the base password check, then sets `uRetVal` regardless of whether it passed. On a wrong "
        "password the base does not hide the form, so `Show()` does not return and the stale `uRetVal` is "
        "not seen unless the user then cancels, which overwrites it with an empty string. Works, by accident "
        "of ordering.")
    L += method_section(c, "cmdcancel.Click", None)
    L += ["## Notes", "",
          "- **Never shown in this build.** `DEBUGMODE` is `.T.`, so `tastrade.Init` skips `Login`; see "
          "[[main.md]]. The dialog only appears from the File menu's Login item.",
          "- **Plain-text, case-sensitive, displayed password.** Three separate reasons a rebuild replaces "
          "this outright.",
          "- **Direct table access** in `Load` and `getuserlevel` (`USE` by relative path, no DataEnvironment).",
          "- **Macro substitution** in `login.Refresh`.",
          "- **Hard-coded English** in `BADPASSWORD_LOC`, `NOEMPLOYEES_LOC`, and the Hint/Title/User Level labels.", ""]
    return "\n".join(L)

# ================================================================= about
def gen_about():
    C = load("about.vc2"); c = C["aboutbox"]
    L = header("about.vcx — the About box", "about.vcx", "libs/about.vc2",
        "A generic, parameterised About dialog: application name, version, copyright, trademark, and logo "
        "come in as `Init` parameters; the registered owner and organisation come from the Windows registry "
        "(or `WIN.INI` on Windows 3.x); and a System Info button launches `MSINFO.EXE` if the registry says "
        "where it is.",
        ["The Help menu's About item ([[../07-menus/main.md]]) does `SET CLASSLIB TO about ADDITIVE`, creates "
         "`AboutBox` with `TASTRADE_LOC`, `VERSION_LOC` (\"1.1\"), `COPYRIGHT_LOC` (\"Copyright 1996 Microsoft "
         "Corporation\"), `RIGHTSRSRVD_LOC`, and `BITMAPS\\TTRADESM.BMP`, shows it, then releases the library. "
         "This is the only class library not loaded by `environment.Set` ([[tsgen.md]])."],
        "[[tsbase.md]] (`tsbaseform`, which it extends but largely disables), [[../08-programs/main.md]] "
        "(the `RegOpenKeyEx`, `RegQueryValueEx`, `RegCloseKey`, and `GetProStr` Win32 declarations it calls), "
        "[[../07-menus/main.md]], [[README.md]].")
    L += ["## Classes in this library", "", "### aboutbox (extends tsbaseform OF tsbase.vcx)", "",
          "**Purpose:** " + c["desc"] + " Although it extends `tsbaseform`, it turns the base behaviour off: "
          "`ctoolbar` empty, `lallownew/lallowedits/lallowdelete = .F.`, `WindowType = 1` (modal), "
          "`AlwaysOnTop = .T.`, and `addtomenu`, `removefrommenu`, `restorewindowpos`, `savewindowpos` "
          "declared `PROTECTED`. So the base form's `Init` still runs (`gTTrade` guard, window position) but "
          "there is no toolbar, no menu entry, and no data. Its controls are native VFP classes "
          "(`commandbutton`, `label`, `image`, `line`, `shape`), not the `ts*` subclasses, and the default "
          "captions are placeholders (\"Your application name\", \"Version #\", \"UserName\", \"UserCorp\") that "
          "`Init` replaces. The `CLASSDATA` icon paths are the bare `..\\`, meaning the designer icon was never set.", ""]
    L += members_table(c)
    L += ["**Controls:** `imgLogo` (image, stretched), `lblAppName`, `lblVersion`, `lblCopyright`, "
          "`lblTrademark`, `lblLicense` (\"This product is licensed to:\"), `lblUserName`, `lblUserCorp`, "
          "`cmdOK` (default), `cmdSysInfo` (\"\\<System Info...\"), plus a shape and two lines drawing the "
          "3-D frame.", "", "#### Methods", ""]
    L += method_section(c, "Init",
        "Takes five optional parameters and applies each only if it is a string. Then branches on `OS()`: on "
        "Windows NT or Windows 4.x (95/98) it opens `HKLM\\Software\\Microsoft\\Shared Tools\\MSInfo` to find "
        "`MSINFO.EXE` and `HKLM\\Software\\Microsoft\\Windows [NT]\\CurrentVersion` to read `RegisteredOwner` and "
        "`RegisteredOrganization`, through the Win32 declarations in `main.prg` and the key constants in "
        "`tastrade.h`; otherwise it reads `WIN.INI` sections `[MS USER INFO]` and `[MICROSOFT SYSTEM INFO]`. "
        "If no `MSINFO.EXE` was found the System Info button is disabled and the form shortened. "
        "**NOTE:** `OS()` on modern Windows returns `\"Windows 6.02\"` or similar, which matches neither "
        "branch, so on this machine the code falls to the `WIN.INI` path, finds nothing, and the About box "
        "shows blank owner lines with System Info disabled. **NOTE:** `RegCloseKey(lnResult)` after the "
        "second open runs even if that open failed. **NOTE:** the buffer is 128 bytes; a longer registered "
        "organisation is truncated.")
    L += method_section(c, "Activate", None)
    L += method_section(c, "Unload", None)
    L += method_section(c, "cmdOK.Click", None)
    L += method_section(c, "cmdSysInfo.Click",
        "`RUN /N1` launches the program through the shell in a normal window. **NOTE:** `&lcMSInfoWinDir` "
        "macro substitution of a registry value into a `RUN` command; a path with spaces would need quoting.")
    L += ["## Notes", "",
          "- **Era-specific.** The whole `Init` is a 1995 Windows version switch. A rebuild keeps the "
          "parameters and drops the registry and `WIN.INI` code.",
          "- **Version string** `\"1.1\"` and **copyright** `\"1996\"` come from `strings.h`, one year after the "
          "1995 copyright in the code.",
          "- **Reuses `tsbaseform` for its window-position memory only**, which means the About box's "
          "position is saved to `tastrade.ini` under its caption.", ""]
    return "\n".join(L)

# ================================================================= orders
def gen_orders():
    C = load("orders.vc2")
    L = header("orders.vcx — the order entry form class", "orders.vcx", "libs/orders.vc2",
        "The order header as a reusable form class: the ship-to block, shipper combo, dates, discount, "
        "freight, and totals, with a `Save` that commits the order and its line items in one transaction "
        "and a set of overrides that keep the base form's navigation working when a grid of line items has "
        "focus. `ordtextbox` is the text box variant whose enabled state follows the form's `lAllowEdits`.",
        ["[[../04-forms/ordentry.md]] (`frmorderentry`) extends `orderentry`, adds the customer combo, the "
         "line-item grid (`grdLineItems`, a `tsgrid` summing `quantity * unit_price`), the DataEnvironment "
         "(`Orders`, `Customer`, `Shippers`, `Order_Line_Items`, `Products`), and the `ControlSource` "
         "bindings for every text box defined here.",
         "The order history form (`frmordhistory`, [[../04-forms/ordhist.md]]) does **not** extend this class "
         "despite the class description; it extends `tsbaseform` directly and uses no `ordtextbox`. The "
         "`\"HISTORY\" $ thisform.Name` branches in this library are therefore dead in the shipped app."],
        "[[tsbase.md]] (`tsbaseform`, `tstextbox`, `tsgrid`), [[../03-data-model/tables/orders.md]] and "
        "[[../03-data-model/tables/order_line_items.md]] (the tables `Save` commits; the `ValOrder()` rule "
        "that fires), [[../03-data-model/README.md]] (the order-total formula, of which this form holds a "
        "sixth copy), [[README.md]].")
    L += ["## Classes in this library", ""]
    c = C["orderentry"]
    L += ["### orderentry (extends tsbaseform OF tsbase.vcx)", "",
          "**Purpose:** " + c["desc"] + " Caption \"Order Entry\". Holds the layout and the logic; the "
          "subclass form supplies data binding. `ashippers[]` is declared but nothing in this class or the "
          "form uses it.", ""]
    L += members_table(c)
    L += ["**Controls defined here** (bindings shown are set by the `frmorderentry` subclass, not this class):", "",
          "| Control | Class | Bound to (in the form) | Notes |", "|---|---|---|---|",
          "| `txtOrder_Number` | `ordtextbox` | `orders.order_number` | disabled, `ldynamicenable = .F.` |",
          "| `txtOrder_Date` | `ordtextbox` | `orders.order_date` | disabled, `ldynamicenable = .F.` |",
          "| `txtDeliver_By` | `ordtextbox` | `orders.deliver_by` | `Valid` enforces today or later; `Refresh` decides editability |",
          "| `cboShipper_ID` | `tscombobox` | `Orders.shipper_id`; row source `select company_name, shipper_id from shippers ... into cursor cShipperList` | `BoundColumn = 2`, drop-down list |",
          "| `txtShip_To_Name`, `_Address`, `_City`, `_Region`, `_Postal_Code`, `txtCountry` | `ordtextbox` | `orders.ship_to_*` | filled from the customer by `refreshcustomerinfo` |",
          "| `txtSubTotal` | `ordtextbox` | unbound | disabled; set by the form from the grid's `ncolumnsum` |",
          "| `txtDiscountPerc` | `ordtextbox` | `orders.discount` | mask `99` |",
          "| `txtDiscount` | `ordtextbox` | unbound | disabled; computed amount |",
          "| `txtFreight` | `ordtextbox` | `orders.freight` | mask `$99,999,999.99` |",
          "| `txtTotal` | `ordtextbox` | unbound | disabled; computed |",
          "| `edtNotes` | `tseditbox` | `orders.notes` | |",
          "| `cmdFocusControl` | `commandbutton` | | parked off-screen; a focus sink |", "",
          "**Referenced but defined in the subclass form:** `grdLineItems`, `cboCustomer_ID`. This class "
          "cannot be instantiated on its own; `addnew` and `refreshcustomerinfo` would fail.", "",
          "#### The on-screen total", "",
          "Four `ProgrammaticChange` handlers form a small dependency chain, triggered whenever the form "
          "assigns a value in code (the form sets `txtSubTotal.Value` from the grid sum):", "",
          "```", "txtSubTotal  --> txtDiscount = SubTotal * DiscountPerc/100",
          "txtDiscountPerc (LostFocus) --> same",
          "txtDiscount  --> txtTotal = SubTotal - Discount + Freight",
          "txtFreight (LostFocus) --> txtTotal = SubTotal - Discount + Freight", "```", "",
          "This is the order-total formula again, `sum(price*qty) - discount% + freight`, computed on the "
          "screen from the grid's `ncolumnsum`, independently of the DBC's `CalcMinOrdAmount()` and the views "
          "([[../03-data-model/README.md]]). The DBC rule `ValOrder()` recomputes it at save time.", "",
          "#### Methods", ""]
    L += method_section(c, "addnew",
        "Selects `orders`, turns editing on (a new order is always editable), refreshes the toolbar, runs the "
        "base `AddNew` (which appends the header and fires the DBC defaults for `order_id`, `order_number`, "
        "`order_date`, `deliver_by`, `employee_id`), then inserts one blank line item carrying the new "
        "`order_id` so the grid has a row to tab into, and puts focus on the customer combo.")
    L += method_section(c, "save",
        "The one transactional save in the application. After settling the active control: `BEGIN TRANSACTION`; "
        "if `orders` shows no field changes, force one (`SETFLDSTATE(2, 2)` marks field 2, `customer_id`, as "
        "edited) so `TABLEUPDATE` sends the row and the table rule `ValOrder()` runs; update `orders` (current "
        "row only), then `order_line_items` (all rows); `END TRANSACTION` on success, `ROLLBACK` and route the "
        "first `AERROR()` to the form's `Error` on failure. **NOTE:** `SETFLDSTATE(2, 2)` hard-codes the field "
        "**position** of `customer_id`; reordering the table's fields silently breaks the forced rule check. "
        "**NOTE:** `TXNLEVEL() = 0` after `BEGIN TRANSACTION` is treated as an error (transaction could not start).")
    L += method_section(c, "restore",
        "Reverts all line items and the current order row, steps back if that left `orders` at end of file, "
        "refreshes. Unlike the base `Restore` it does not re-enable the New button or refresh the menu.")
    L += method_section(c, "datachanged", "A change to any buffered line item (`GETNEXTMODIFIED`) counts as well as a change to the header.")
    L += method_section(c, "delete", "Moves focus off the grid and selects `orders` before the base `Delete`, so the header is what gets deleted; the RI cascade removes the lines.")
    L += method_section(c, "first", "The four navigation overrides just move focus off the grid first; see `moveoffgrid`.")
    L += method_section(c, "prior", None)
    L += method_section(c, "next", None)
    L += method_section(c, "last", None)
    L += method_section(c, "moveoffgrid",
        "Parks focus on the invisible `cmdFocusControl` when the grid has it, so the grid's `SumColumn` is "
        "not run twice (once from `Refresh`, once from `BeforeRowColChange`). `cmdFocusControl.GotFocus` "
        "immediately forwards focus to the customer combo or ship-to name, so the user never sees it.",
        protected=True)
    L += method_section(c, "refreshcustomerinfo",
        "Copies the customer's address block and discount into the ship-to fields and `txtDiscountPerc` when "
        "a customer is chosen, or blanks them. Assumes the `customer` alias is positioned on the chosen "
        "customer, which the form's customer combo arranges. The values go into control `Value`s, and reach "
        "the `orders` fields through the bindings.")
    L += method_section(c, "restorewindowpos",
        "Because the order history form was designed to be multi-instance with a dynamic caption, its INI "
        "entry is fixed at \"Order History\". Dead branch here; see the note on `frmordhistory` above.")
    L += method_section(c, "savewindowpos", None)
    L += method_section(c, "txtDeliver_By.Refresh",
        "Decides whether the order is editable: a new record always is; an existing order is editable only "
        "while its `deliver_by` date is in the future, and deletable under the same condition. Calls the "
        "native `textbox::Refresh` and then `OrdTextBox::Refresh` explicitly, so the enabled state it just "
        "computed is applied to this control too.")
    L += method_section(c, "txtDeliver_By.Valid", "Client-side copy of the DBC rule `deliver_by => order_date`, stricter: today or later.")
    L += method_section(c, "txtSubTotal.ProgrammaticChange", None)
    L += method_section(c, "txtDiscountPerc.ProgrammaticChange", None)
    L += method_section(c, "txtDiscountPerc.LostFocus", None)
    L += method_section(c, "txtDiscount.ProgrammaticChange", None)
    L += method_section(c, "txtFreight.ProgrammaticChange", None)
    L += method_section(c, "txtFreight.LostFocus", None)
    L += method_section(c, "cboShipper_ID.Refresh", None)
    L += method_section(c, "cboShipper_ID.Destroy", "Closes the shipper cursor the form's row source created.")
    L += method_section(c, "edtNotes.Refresh", None)
    L += method_section(c, "cmdFocusControl.Init", "Moves the button ten pixels past the form's right edge.")
    L += method_section(c, "cmdFocusControl.GotFocus", None)
    L += method_section(c, "cmdFocusControl.Refresh", None)

    c = C["ordtextbox"]
    L += ["### ordtextbox (extends tstextbox OF tsbase.vcx)", "",
          "**Purpose:** " + c["desc"] + " A `tstextbox` whose `Enabled` follows the form's `lAllowEdits` on "
          "every `Refresh`, unless `ldynamicenable` is `.F.` (the permanently disabled order number, date, "
          "and computed amounts).", ""]
    L += members_table(c)
    L += ["#### Methods", ""]
    L += method_section(c, "Init", "After the base `Init` (auto input mask), disables itself permanently when the host form's name contains \"HISTORY\". Dead in the shipped app.")
    L += method_section(c, "Refresh", None)
    L += ["## Notes", "",
          "- **Stale design.** The class description, the `HISTORY` branches, `restorewindowpos`, and "
          "`ordtextbox.Init` all serve an order history form built on this class. The shipped "
          "`frmordhistory` is built on `tsbaseform` instead. Roughly a fifth of this library is dead code.",
          "- **Half a form.** The class references `grdLineItems` and `cboCustomer_ID` that only the "
          "subclass form defines, and every data binding lives in the form. Read [[../04-forms/ordentry.md]] "
          "with this page.",
          "- **The only explicit transaction** in the application is `save`; the base form relies on "
          "`TABLEUPDATE` alone.",
          "- **Field position hard-coded** in `SETFLDSTATE(2, 2)`.",
          "- **Sixth copy of the order total**, this one on screen.",
          "- **Editability by date.** Orders become read-only the day after their delivery date; there is no "
          "status field.", ""]
    return "\n".join(L)

def update_readme():
    p = os.path.join(OUT, "README.md"); s = open(p, encoding="utf-8").read()
    s = s.replace("Six `.vcx` libraries hold 31 classes. The two framework libraries are documented; the four "
                  "application-specific ones are next.", "Six `.vcx` libraries hold 31 classes.")
    s = s.replace("| main.md (pending) |", "| [[main.md]] |").replace("| login.md (pending) |", "| [[login.md]] |")
    s = s.replace("| about.md (pending) |", "| [[about.md]] |").replace("| orders.md (pending) |", "| [[orders.md]] |")
    s = s.replace("`login` dialog and its picture variant", "`login` dialog and `loginpicture`, the variant the app uses")
    s = s.replace("`orderentry` form class and `ordtextbox`", "`orderentry` form class (half of the order entry form) and `ordtextbox`")
    open(p, "w", encoding="utf-8", newline="\n").write(s)

for fn, gen in (("main.md", gen_main), ("login.md", gen_login), ("about.md", gen_about), ("orders.md", gen_orders)):
    with open(os.path.join(OUT, fn), "w", encoding="utf-8", newline="\n") as f:
        f.write(gen())
    print("wrote", fn)
update_readme(); print("README updated")
