"""Generate docs/04-forms/{customer,employee,product,supplier,category,shipper}.md and update the index."""
import os, re, sys, textwrap
sys.path.insert(0, os.environ.get("VFP_TOOLKIT_TOOLS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "vfp-documentation-toolkit", "tools")))
import foxparse as fp

ROOT = os.environ.get("TASTRADE_ROOT", os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))
OUT = os.path.join(ROOT, "docs", "04-forms")

def load(name):
    r = fp.parse_sc2(os.path.join(ROOT, "forms", name + ".sc2"))
    r["text"] = fp.read(os.path.join(ROOT, "forms", name + ".sc2"))
    # List-page grid columns from the PropValue block
    cols = {}
    for m in re.finditer(r"pageframe1\.page2\.grdlist\.Column(\d+)\.(ControlSource|ColumnOrder|InputMask|CurrentControl)\s*=\s*(.+)$", r["text"], re.M | re.I):
        cols.setdefault(int(m.group(1)), {})[m.group(2).lower()] = m.group(3).strip().strip('"')
    r["gridcols"] = cols
    m = re.search(r"pageframe1\.page2\.grdlist\.ColumnCount\s*=\s*(\d+)", r["text"], re.I)
    r["gridcolcount"] = int(m.group(1)) if m else len(cols)
    # header captions by column name
    r["headers"] = {}
    for m in re.finditer(r"ADD OBJECT 'pageframe1\.page2\.grdlist\.(grc\w+)\.grh\w+' AS header WITH ;(.*?)\*< END OBJECT", r["text"], re.S | re.I):
        cm = re.search(r'Caption = "([^"]*)"', m.group(2))
        r["headers"][m.group(1).lower()] = cm.group(1) if cm else ""
    # column names in definition order (Column1.. -> grcX via ObjPath order)
    r["colnames"] = re.findall(r"ObjPath=\"pageframe1\.page2\.grdlist\.(grc\w+)\.grh\w+\"", r["text"])
    return r

def body(r, method):
    for k in r["methods"]:
        if k.lower() == method.lower():
            return textwrap.dedent(r["methods"][k]).strip("\n")
    raise KeyError(method)

def fence(code): return "```foxpro\n" + code + "\n```"
def unq(v):
    v = (v or "").strip(); return v[1:-1] if len(v) >= 2 and v[0] == v[-1] == '"' else v

def method_section(r, method, explain):
    L = ["#### `%s`" % method, ""]
    if explain: L += [explain, ""]
    return L + [fence(body(r, method)), ""]

def de_table(r):
    L = ["| Cursor | Alias | Source | Order | Filter |", "|---|---|---|---|---|"]
    for c in r["cursors"]:
        L.append("| `%s` | `%s` | `%s` | %s | %s |" % (c["object"], c["alias"], c["table"], ("`%s`" % c["order"]) if c["order"] else "", c["filter"] or ""))
    return L + [""]

def control_rows(r, extra, skip_grid_internals=True):
    L = ["| Container path | Class | Bound to / key properties | Role |", "|---|---|---|---|"]
    n_skipped = 0
    for c in r["controls"]:
        path = c["path"]
        if skip_grid_internals and ".grdlist." in path.lower():
            n_skipped += 1; continue
        p = c["props"]; bits = []
        if p.get("caption"): bits.append("caption %s" % p["caption"])
        if p.get("controlsource"): bits.append("→ `%s`" % unq(p["controlsource"]))
        if p.get("rowsource"): bits.append("rows `%s`" % unq(p["rowsource"]))
        if p.get("value") and "Employee." in p.get("value", ""): bits.append("value `%s`" % p["value"])
        if p.get("enabled") == ".F.": bits.append("disabled")
        if p.get("readonly") == ".T.": bits.append("read-only")
        cls = c["class"] + ("" if c["class"].lower() == c["baseclass"].lower() else " (%s)" % c["baseclass"])
        L.append("| `%s` | `%s` | %s | %s |" % (path, cls, "; ".join(bits), extra.get(path.lower(), "")))
    L.append("")
    if n_skipped:
        L.append("The List page's grid headers and cells (%d objects under `pageframe1.page2.grdlist`) are "
                 "listed as columns below rather than one row each." % n_skipped)
        L.append("")
    return L

def grid_table(r):
    L = ["| Order | Column | Header | ControlSource | Notes |", "|---|---|---|---|---|"]
    rows = []
    for i in range(1, r["gridcolcount"] + 1):
        c = r["gridcols"].get(i, {})
        name = r["colnames"][i - 1] if i - 1 < len(r["colnames"]) else "Column%d" % i
        order = int(c.get("columnorder", i))
        notes = []
        if c.get("inputmask"): notes.append("mask `%s`" % c["inputmask"])
        if c.get("currentcontrol"): notes.append("current control `%s`" % c["currentcontrol"])
        rows.append((order, name, r["headers"].get(name.lower(), ""), c.get("controlsource", ""), "; ".join(notes)))
    for order, name, hdr, src, notes in sorted(rows):
        L.append("| %d | `%s` | %s | `%s` | %s |" % (order, name, hdr, src, notes))
    return L + [""]

def header(r, scx, purpose, used_by, related):
    return ["# %s (%s.scx)" % (r["name"], scx), "", "| Source file | Type | Path |", "|---|---|---|",
            "| `%s.scx` | Form | `forms/%s.sc2` |" % (scx, scx), "", "**Purpose:** " + purpose, "",
            "**Used by:**"] + ["- " + u for u in used_by] + ["", "**Related docs:** " + related, ""]

def pattern_para():
    return ["This is one of the six `tsmaintform` forms. The pattern, documented once in "
            "[[../05-classes/tsbase.md]]: a two-page pageframe (**Data Entry** with bound controls, **List** "
            "with a read-only `tsgrid` over the same cursor), the shared navigation toolbar for "
            "First/Prior/Next/Last/New/Save/Restore/Close, optimistic table buffering committed by "
            "`TABLEUPDATE`, and an `Error` method that turns DBC rule and trigger failures into messages. "
            "Each form adds only its bindings, a focus target for `AddNew`, the field-rule-to-control "
            "mapping in `Error`, and the trigger-failure message text in `Init`.", ""]

def menu_line(prompt, formname):
    return ("The Maintenance menu ([[../07-menus/main.md]]) bar \"%s\": `oApp.DoForm(\"%s\")`, "
            "`SKIP FOR WEXIST(\"%s\")` so only one instance opens." % (prompt, formname.lower(), formname))

def metadata(r, caption, icon, session, extra=None):
    L = ["## Form metadata", "",
         "- Base class / parent: `tsmaintform` of `..\\libs\\tsbase.vcx` → `tsbaseform` → `form`",
         "- Caption: \"%s\"; icon `..\\bitmaps\\%s`" % (caption, icon),
         "- Modal: no. MDI child with the navigation toolbar; new/edit/delete allowed (inherited defaults)",
         "- Data session: %s; `AutoCenter = .F.` (INI position); `ScaleMode = 3` (pixels)" % session]
    if extra: L += ["- " + e for e in extra]
    return L + [""]

# ----------------------------------------------------------------- docs
def gen_shipper():
    r = load("shipper")
    L = header(r, "shipper", "Maintain the three shipping companies. The simplest form in the application: one bound text box and a one-column list.",
        [menu_line("Shippers", "frmShippers"), "[[ordentry.md]] reads the same table through its shipper combo."],
        "[[../03-data-model/tables/shippers.md]], [[../05-classes/tsbase.md]] (`tsmaintform`), [[README.md]].")
    L += pattern_para()
    L += metadata(r, "Shippers", "shpprs1.ico", "**default (shared)**, the only maintenance form without `DataSession = 2`", ["`WindowState = 0`"])
    L += ["## DataEnvironment", ""] + de_table(r) + ["`InitialSelectedAlias = \"Shippers\"`, ordered by company name.", ""]
    L += ["## Controls (depth-first)", ""] + control_rows(r, {"pageframe1.page1.txtcompany_name": "The only editable field", "pageframe1.page1.tslabel1": "\"Company\""})
    L += ["List page grid (`ColumnCount = 1`):", ""] + grid_table(r)
    L += ["## Form methods", ""]
    L += method_section(r, "Init", "Delete-trigger failures show `DELSHIPPER_LOC`: \"Shipper exists on orders. Cannot delete!\"")
    L += method_section(r, "addnew", "Focus the company name after the base appends the record.")
    L += method_section(r, "Error", "Field rule 1582 on `COMPANY_NAME` (the DBC's not-empty rule) refocuses the text box after the base shows the rule text.")
    L += ["## Tables read / written", "", "| Table | Access | How |", "|---|---|---|",
          "| `SHIPPERS` | both | DataEnvironment; `newid()` default fills `shipper_id` on append |", "",
          "## Inter-form navigation", "", "- **← Maintenance menu** only. Opens nothing.", "",
          "## Notes", "",
          "- **Shared data session.** Unlike its five siblings this form runs in the default session, so its `Shippers` alias is the same one the order entry form's combo cursor is built from. Probably an oversight; harmless because both are read-mostly.",
          "- `shipper_id` is never shown; the ID is invisible to the user.", ""]
    return "\n".join(L)

def gen_category():
    r = load("category")
    L = header(r, "category", "Maintain the eight product categories: name, description, and a picture stored both as a file name and as an OLE General field.",
        [menu_line("Categories", "frmCategory"), "[[product.md]] reads the table through its category combo; view `CATEGORY LISTING` feeds [[../06-reports/listcat.md]]."],
        "[[../03-data-model/tables/category.md]], [[../05-classes/tsbase.md]] (`tsmaintform`), [[README.md]].")
    L += pattern_para()
    L += metadata(r, "Categories", "catgry.ico", "private (`DataSession = 2`)")
    L += ["## DataEnvironment", ""] + de_table(r) + ["`InitialSelectedAlias = \"Category\"`, ordered by upper-cased name.", ""]
    L += ["## Controls (depth-first)", ""] + control_rows(r, {
        "pageframe1.page1.txtcategory_name": "Name; the DBC rule requires it non-empty",
        "pageframe1.page1.edtdescription": "Memo",
        "pageframe1.page1.cmdpicture": "Caption switches between \"Add Picture\" and \"Change Picture\"",
        "pageframe1.page1.imgpicture": "Shows `picture_file`; `Stretch = 2` (stretch to fit)",
        "pageframe1.page1.tslabel1": "\"Name\"", "pageframe1.page1.tslabel2": "\"Description\""})
    L += ["List page grid (`ColumnCount = 2`):", ""] + grid_table(r)
    L += ["The description column shows `LEFT(Category.description, 60)`, an expression rather than a field, so the memo is truncated in the list.", "",
          "### Events with code", ""]
    L += method_section(r, "pageframe1.page1.cmdPicture.Click",
        "`GETFILE(\"BMP\")` picks a bitmap; the path goes into `picture_file` **and** the bitmap is loaded into the General field `picture` with `APPEND GENERAL`. "
        "**NOTE:** the General field copy is never read by this form (`refreshform` displays the file), so the OLE object is dead weight; and the stored path is absolute to the machine the file was picked on.")
    L += method_section(r, "pageframe1.page1.cmdPicture.Refresh", None)
    L += ["## Form methods", ""]
    L += method_section(r, "Init", "Calls `tsBaseForm::Init` directly, skipping `tsmaintform` (which has no `Init`, so no difference). Delete-trigger message `DELCATEGORY_LOC`: \"Products belong to this category. Cannot delete!\"")
    L += method_section(r, "addnew", None)
    L += method_section(r, "Error", "Field rule on `CATEGORY_NAME` refocuses the name.")
    L += method_section(r, "refreshform", "Overrides the base to load the picture from `picture_file` (blank if the file is missing) before the normal refresh.")
    L += ["## Tables read / written", "", "| Table | Access | How |", "|---|---|---|",
          "| `CATEGORY` | both | DataEnvironment; `picture_file` and General `picture` written by the picture button |", "",
          "## Inter-form navigation", "", "- **← Maintenance menu** only. Opens the `GETFILE` dialog.", "",
          "## Notes", "",
          "- **Two copies of the picture**, file path and OLE object, and only the path is used. A rebuild keeps the file.",
          "- **Absolute paths in data**: `picture_file` holds whatever `GETFILE` returned.",
          "- `category_id` is never shown.", ""]
    return "\n".join(L)

def gen_supplier():
    r = load("supplier")
    L = header(r, "supplier", "Maintain suppliers: company, contact, address, and phone details. Nine bound text boxes and a ten-column list.",
        [menu_line("Suppliers", "frmSuppliers"), "[[product.md]] reads the table through its supplier combo; view `SUPPLIER LISTING` feeds [[../06-reports/listsupp.md]]."],
        "[[../03-data-model/tables/supplier.md]], [[../05-classes/tsbase.md]] (`tsmaintform`), [[README.md]].")
    L += pattern_para()
    L += metadata(r, "Suppliers", "spplrs.ico", "private (`DataSession = 2`)")
    L += ["## DataEnvironment", ""] + de_table(r) + ["`InitialSelectedAlias = \"Supplier\"`, ordered by upper-cased company name.", ""]
    L += ["## Controls (depth-first)", ""] + control_rows(r, {"pageframe1.page1.txtcompany_name": "Required by the DBC rule"})
    L += ["List page grid (`ColumnCount = 10`):", ""] + grid_table(r)
    L += ["## Form methods", ""]
    L += method_section(r, "Init", "Delete-trigger message `DELSUPPLIER_LOC`: \"Products are supplied by this supplier. Cannot delete!\"")
    L += method_section(r, "addnew", None)
    L += method_section(r, "Error", "Field rule on `COMPANY_NAME` refocuses the company name.")
    L += ["## Tables read / written", "", "| Table | Access | How |", "|---|---|---|",
          "| `SUPPLIER` | both | DataEnvironment; `newid()` default fills `supplier_id` |", "",
          "## Inter-form navigation", "", "- **← Maintenance menu** only.", "",
          "## Notes", "",
          "- Identical in structure to [[customer.md]] minus the credit fields, but the customer form uses the shared `customerinfo` container while this one lays its text boxes out directly. Two ways of doing the same thing in one sample.",
          "- `supplier_id` is never shown.", ""]
    return "\n".join(L)

def gen_customer():
    r = load("customer")
    L = header(r, "customer", "Maintain customers. The Data Entry page is the shared `customerinfo` container (company, contact, address, credit terms); the List page is a fourteen-column grid.",
        [menu_line("Customers", "frmCustomers"),
         "[[custadd.md]] uses the same `customerinfo` container to add a customer from order entry.",
         "[[ordhist.md]], opened while this form is on top, starts on this form's current customer by reading its data session.",
         "View `CUSTOMER LISTING` feeds [[../06-reports/listcust.md]]."],
        "[[../03-data-model/tables/customer.md]], [[../05-classes/tsgen.md]] (`customerinfo`, where the bound controls, the `Error` handler, and the min/max validation live), [[../05-classes/tsbase.md]] (`tsmaintform`), [[README.md]].")
    L += pattern_para()
    L += metadata(r, "Customers", "cust.ico", "private (`DataSession = 2`)")
    L += ["## DataEnvironment", ""] + de_table(r) + ["`InitialSelectedAlias = \"Customer\"`, ordered by **customer ID**, unlike the other maintenance forms which order by name.", ""]
    L += ["## Controls (depth-first)", ""] + control_rows(r, {"pageframe1.page1.cntcustomerinfo": "The whole Data Entry page; its fourteen bound text boxes are documented under `customerinfo` in [[../05-classes/tsgen.md]]"})
    L += ["List page grid (`ColumnCount = 14`, displayed in `ColumnOrder`):", ""] + grid_table(r)
    L += ["`ColumnOrder` reorders the columns so contact name and title follow the company name although they were added last.", "",
          "### Events with code", ""]
    L += method_section(r, "pageframe1.page1.cntCustomerInfo.txtCustomer_ID.Refresh",
        "The customer ID is the primary key and is typed by the user (no `newid()` default on this table), so it is editable only on a new record. The `ISNULL` guard handles a refresh before any record exists.")
    L += ["## Form methods", ""]
    L += method_section(r, "Init", "Delete-trigger message `DELCUSTOMER_LOC`: \"Customer has orders. Cannot delete!\"")
    L += method_section(r, "addnew", "Focus goes to the ID inside the container.")
    L += method_section(r, "Error", "Primary-key (1884) and field-rule (1582) errors are delegated to the container's `Error`, which knows which text box to focus; everything else goes to the base.")
    L += ["## Tables read / written", "", "| Table | Access | How |", "|---|---|---|",
          "| `CUSTOMER` | both | DataEnvironment; ID typed by the user |", "",
          "## Inter-form navigation", "", "- **← Maintenance menu**.", "- **→ [[ordhist.md]]** indirectly: Order History opened from the menu while this form is active picks up its customer.", "",
          "## Notes", "",
          "- **User-typed primary key**, upper-cased by the container's `K!` format; duplicates surface as error 1884 at save.",
          "- **The grid shows credit limits and discount** with masks `$$9,999,999,999.99` and `99.99%`; the discount mask shows two decimals for an integer percent.",
          "- **The form itself has almost no code**; the behaviour is in `customerinfo` and `tsmaintform`.", ""]
    return "\n".join(L)

def gen_product():
    r = load("product")
    L = header(r, "product", "Maintain the product catalogue: names, packaging, price and cost, stock counts, discontinued flag, and the supplier and category each product belongs to.",
        [menu_line("Products", "frmProducts"), "[[ordentry.md]] reads the table through its product combo and copies `unit_price` onto order lines; view `PRODUCT LISTING` feeds [[../06-reports/listprod.md]]."],
        "[[../03-data-model/tables/products.md]], [[../03-data-model/tables/supplier.md]], [[../03-data-model/tables/category.md]], [[../05-classes/tsbase.md]] (`tsmaintform`), [[README.md]].")
    L += pattern_para()
    L += metadata(r, "Products", "prod1.ico", "private (`DataSession = 2`)")
    L += ["## DataEnvironment", ""] + de_table(r) + [
        "`InitialSelectedAlias = \"Products\"`, ordered by upper-cased product name. Two relations, `Products` → `Supplier` on `supplier_id` and `Products` → `Category` on `category_id`, let the List grid show the supplier and category **names** from the related cursors. `BeforeOpenTables` sets `TALK OFF`, `EXCLUSIVE OFF`, `DELETED ON`, `SET DATABASE TO TASTRADE` for the private session:", "",
        fence("SET TALK OFF\nSET EXCLUSIVE OFF\nSET DELETED ON\nSET DATABASE TO TASTRADE"), ""]
    L += ["## Controls (depth-first)", ""] + control_rows(r, {
        "pageframe1.page1.txtproduct_name": "Required by the DBC rule",
        "pageframe1.page1.cbosupply_id": "Supplier drop-down, `BoundColumn = 2`; its `Init` re-assigns the same binding and row source",
        "pageframe1.page1.cbocategory_id": "Category drop-down, `BoundColumn = 2`",
        "pageframe1.page1.chkdiscontinued": "\"Discontinued\"",
        "pageframe1.page1.txtunit_price": "Currency", "pageframe1.page1.txtunit_cost": "Currency",
        "pageframe1.page1.txtunits_in_stock": "N(12,3)", "pageframe1.page1.txtunits_on_order": "N(12,3)", "pageframe1.page1.txtreorder_level": "N(12,3)"})
    L += ["List page grid (`ColumnCount = 11`, displayed in `ColumnOrder`):", ""] + grid_table(r)
    L += ["Columns 10 and 11 are bound to `Supplier.company_name` and `Category.category_name` through the DataEnvironment relations. Column 9 (`discontinued`) has `Sparse = .F.` and a `tscheckbox` (`Tscheckbox1`) placed in the column but `CurrentControl = \"Text1\"`, so the checkbox is present but not the displayed control. **NOTE:** likely a half-finished change; the list shows `.T.`/`.F.` text.", "",
          "### Events with code", ""]
    L += method_section(r, "pageframe1.page1.cboSupply_ID.Init", "Sets `ControlSource` and `RowSource` to the values the designer already stored; redundant.")
    L += method_section(r, "pageframe1.page1.cboSupply_ID.Destroy", None)
    L += method_section(r, "pageframe1.page1.cboCategory_ID.Destroy", None)
    L += ["## Form methods", ""]
    L += method_section(r, "Init", "Two trigger messages: delete `DELPRODUCT_LOC` \"Product exists on order line items. Cannot delete!\" and insert `INSPRODUCT_LOC` \"All products must be assigned a supplier and a category.\" The insert message is what the user sees when the RI insert trigger refuses a product with a missing supplier or category.")
    L += method_section(r, "addnew", None)
    L += method_section(r, "Destroy", "Drops the relations on `products` before the base closes the tables.")
    L += method_section(r, "Error", "Field rule on `PRODUCT_NAME` refocuses the name.")
    L += ["## Tables read / written", "", "| Table | Access | How |", "|---|---|---|",
          "| `PRODUCTS` | both | DataEnvironment; `newid()` default fills `product_id` |",
          "| `SUPPLIER` | read | DataEnvironment (related) and combo cursor `cSupplier` |",
          "| `CATEGORY` | read | DataEnvironment (related) and combo cursor `cCategory` |", "",
          "## Inter-form navigation", "", "- **← Maintenance menu** only.", "",
          "## Notes", "",
          "- **Stock is edited by hand.** `units_in_stock` and `units_on_order` are plain text boxes; nothing in the application adjusts them when orders are saved (confirmed in [[ordentry.md]]). Inventory is decorative in this sample.",
          "- **Fractional stock**: the three quantity fields are `N(12,3)` with no mask.",
          "- **Unit price changes do not touch existing orders**; order lines keep the price copied at entry time.", ""]
    return "\n".join(L)

def gen_employee():
    r = load("employee")
    L = header(r, "employee", "Maintain employees: name, title, dates, address, phone, security group, and on a third page the notes and photo. Also the table the login dialog authenticates against.",
        [menu_line("Employees", "frmEmployee"),
         "[[../05-classes/login.md]] authenticates against the same table; [[chngpswd.md]] changes `password`; view `EMPLOYEE LISTING` feeds [[../06-reports/listempl.md]]."],
        "[[../03-data-model/tables/employee.md]], [[../03-data-model/tables/user_level.md]], [[../05-classes/tsbase.md]] (`tsmaintform`), [[../05-classes/main.md]] (`GetEmployeeID`), [[README.md]].")
    L += pattern_para()
    L += metadata(r, "Employees", "emply.ico", "private (`DataSession = 2`)", ["`pageframe1.PageCount = 3`: a third page \"Additional Information\" with notes, photo, and the employee's name"])
    L += ["## DataEnvironment", ""] + de_table(r) + ["`InitialSelectedAlias = \"Employee\"`, ordered by upper-cased last name. One relation, `Employee` → `User_Level` on `group_id`, so the List grid can show the group description.", ""]
    L += ["## Controls (depth-first)", ""] + control_rows(r, {
        "pageframe1.page1.txtlast_name": "Required by the DBC rule",
        "pageframe1.page1.cbogroup_id": "Security group drop-down over `USER_LEVEL`, `BoundColumn = 2`",
        "pageframe1.page1.hiredate": "→ `Employee.hire_date`; name lacks the `txt` prefix",
        "pageframe1.page1.extension": "→ `Employee.extension`; name lacks the `txt` prefix",
        "pageframe1.page3.edtnotes": "Memo",
        "pageframe1.page3.imgphoto": "Shows `photo_file`; `Stretch = 2`",
        "pageframe1.page3.cmdpicture": "\"Add Picture\" / \"Change Picture\"",
        "pageframe1.page3.txtemployeename": "Unbound, read-only; first and last name joined by `Page3.Refresh`"})
    L += ["List page grid (`ColumnCount = 14`, displayed in `ColumnOrder`):", ""] + grid_table(r)
    L += ["**NOTE:** column 13 shows `Employee.password` in clear text in the List page. Combined with the login dialog's \"Hint\" box ([[../05-classes/login.md]]), every password in the system is visible from two places in the UI. Column 14 shows the user level description from the related cursor.", "",
          "### Events with code", ""]
    L += method_section(r, "pageframe1.Page3.Activate", "Same alias re-selection as the base page-activate handlers, then a refresh so the photo loads.")
    L += method_section(r, "pageframe1.Page3.Refresh", None)
    L += method_section(r, "pageframe1.Page3.cmdPicture.Click", "Like the category form's picture button but stores only the file name; no General field copy here.")
    L += method_section(r, "pageframe1.Page3.cmdPicture.Refresh", None)
    L += method_section(r, "pageframe1.page1.cboGroup_ID.Destroy", None)
    L += ["## Form methods", ""]
    L += method_section(r, "Init", "Trigger messages: delete `DELEMPLOYEE_LOC` \"Employee exists on orders. Cannot delete!\" and insert `INSEMPLOYEE_LOC` \"All employees must be assigned to a group.\"")
    L += method_section(r, "addnew", None)
    L += method_section(r, "Refresh",
        "Prevents deleting the employee who is logged in by clearing `lAllowDelete` when the current record is `oApp.GetEmployeeID()`. **NOTE:** in this build `GetEmployeeID()` is always empty (`DEBUGMODE`, see [[../05-classes/main.md]]), so the guard never fires. Overriding `Refresh` rather than `RefreshForm` means it also runs on the base class's `LockScreen`-wrapped refresh.")
    L += method_section(r, "refreshform", "Loads the photo from `photo_file` (blank if missing) before the normal refresh.")
    L += method_section(r, "Destroy", None)
    L += method_section(r, "Error", "Field rule on `LAST_NAME` refocuses the last name.")
    L += ["## Tables read / written", "", "| Table | Access | How |", "|---|---|---|",
          "| `EMPLOYEE` | both | DataEnvironment; `newid()` default fills `employee_id`; `password` defaults to `\"Tastrade\"` and is **not** editable here (no control), only via [[chngpswd.md]] |",
          "| `USER_LEVEL` | read | DataEnvironment (related) and combo cursor `cUserLevels` |", "",
          "## Inter-form navigation", "", "- **← Maintenance menu** only.", "",
          "## Notes", "",
          "- **Password visible in the list grid.**",
          "- **No control for `password`, `sales_region`, `photo`** (the General field) on the entry pages; `sales_region` has no UI anywhere.",
          "- **Logged-in-employee delete guard is dead** under `DEBUGMODE`.",
          "- **Inconsistent control names** (`hiredate`, `extension` without the `txt` prefix).",
          "- **Photo path is absolute** to the machine it was chosen on, as in the category form.", ""]
    return "\n".join(L)

def update_readme():
    p = os.path.join(OUT, "README.md"); s = open(p, encoding="utf-8").read()
    for scx in ("customer", "employee", "product", "supplier", "category", "shipper"):
        s = re.sub(r"(\| `forms/%s\.scx` \|[^\n]*\| )pending \|" % scx, r"\1[[%s.md]] |" % scx, s)
    s = s.replace("Seventeen forms in `forms/*.scx`.", "Seventeen forms in `forms/*.scx`. The six maintenance forms share the `tsmaintform` pattern described in [[../05-classes/tsbase.md]].")
    open(p, "w", encoding="utf-8", newline="\n").write(s)

for fn, gen in (("shipper.md", gen_shipper), ("category.md", gen_category), ("supplier.md", gen_supplier),
                ("customer.md", gen_customer), ("product.md", gen_product), ("employee.md", gen_employee)):
    with open(os.path.join(OUT, fn), "w", encoding="utf-8", newline="\n") as f:
        f.write(gen())
    print("wrote", fn)
update_readme(); print("README updated")
