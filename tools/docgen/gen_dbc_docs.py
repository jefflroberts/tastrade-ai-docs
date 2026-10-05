"""Generate docs/03-data-model/ for Tastrade from the VFP schema dump and the .dc2 twin."""
import os, re, sys
sys.path.insert(0, os.environ.get("VFP_TOOLKIT_TOOLS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "vfp-documentation-toolkit", "tools")))
from dbf import read_table

ROOT = os.environ.get("TASTRADE_ROOT", os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))
DUMP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dbcdump.txt")  # produced by dbcdump.prg
DC2 = os.path.join(ROOT, "data", "tastrade.dc2")
OUT = os.path.join(ROOT, "docs", "03-data-model")
TOUT = os.path.join(OUT, "tables")
os.makedirs(TOUT, exist_ok=True)

# ---------------------------------------------------------------- parse dump
tables, free, views, rels = {}, {}, [], []
cur = None
for line in open(DUMP, encoding="latin-1"):
    p = line.rstrip("\r\n").split("|")
    k = p[0]
    if k == "TABLE":
        cur = {"name": p[1], "dbf": os.path.basename(p[2]).lower(), "rows": int(p[3]),
               "comment": p[4], "rule": p[5], "rule_text": p[6], "ins": p[7], "upd": p[8],
               "del": p[9], "pk": p[10], "fields": [], "tags": []}
        tables[p[1]] = cur
    elif k == "FREETABLE":
        cur = {"name": p[1], "dbf": os.path.basename(p[2]).lower(), "rows": int(p[3]),
               "fields": [], "tags": []}
        free[p[1]] = cur
    elif k == "FIELD":
        f = {"name": p[1], "type": p[2], "width": p[3], "dec": p[4], "null": p[5]}
        if len(p) > 6:
            f.update({"rule": p[6], "rule_text": p[7], "default": p[8], "comment": p[9],
                      "caption": p[10], "mask": p[11], "format": p[12]})
        else:
            f.update({"rule": "", "rule_text": "", "default": "", "comment": "", "caption": "",
                      "mask": "", "format": ""})
        cur["fields"].append(f)
    elif k == "TAG":
        cur["tags"].append({"name": p[1], "key": p[2], "for": p[3], "kind": p[4], "dir": p[5]})
    elif k == "VIEW":
        views.append({"name": p[1], "sql": p[2].strip(), "upd": p[3], "comment": p[4]})
    elif k == "RELATION":
        rels.append({"child": p[1], "parent": p[2], "child_tag": p[3], "parent_tag": p[4],
                     "ri": p[5].strip()})

RI = {"C": "cascade", "R": "restrict", "I": "ignore"}
def ri_words(code):
    return {"update": RI[code[0]], "delete": RI[code[1]], "insert": RI[code[2]]}

TYPE = {"C": "Character", "N": "Numeric", "Y": "Currency", "D": "Date", "L": "Logical",
        "M": "Memo", "G": "General"}

# ------------------------------------------------------- stored procedures
dc2 = open(DC2, encoding="latin-1").read()
sp_start = dc2.index("<STOREDPROCEDURES><![CDATA[") + len("<STOREDPROCEDURES><![CDATA[")
sp_end = dc2.index("]]></STOREDPROCEDURES>") if "]]></STOREDPROCEDURES>" in dc2 else dc2.index("**__RI_HEADER!@")
sp_text = dc2[sp_start:sp_end]
hand_end = sp_text.index("**__RI_HEADER!@")
hand = sp_text[:hand_end]
def func_block(name):
    m = re.search(r"^FUNCTION %s\b.*?^ENDFUNC\s*$" % re.escape(name), hand, re.S | re.M)
    return m.group(0).rstrip()
HAND_FUNCS = ["NewID", "RemainingCredit", "ValOrder", "CalcMinOrdAmount", "CalcOrdTotal", "DefaultEmployee"]
ri_procs = re.findall(r"^\s*(?:PROCEDURE|procedure)\s+(\S+)", sp_text[hand_end:], re.M)

# ------------------------------------------------------------- usage map
# From the forms' DataEnvironments (foxparse cursors), report/view wiring, and class code.
USED_BY = {
    "CATEGORY": ["[[../../04-forms/category.md]] (`frmcategory`) maintains it",
                 "[[../../04-forms/product.md]] (`frmproducts`) opens it as a lookup",
                 "View `CATEGORY LISTING`, printed by [[../../06-reports/listcat.md]]"],
    "CUSTOMER": ["[[../../04-forms/customer.md]] (`frmcustomers`) maintains it",
                 "[[../../04-forms/custadd.md]] (`frmaddcustomer`) adds a customer from order entry",
                 "[[../../04-forms/ordentry.md]] and [[../../04-forms/ordhist.md]] open it in their DataEnvironment",
                 "`findcustomer` class in [[../../05-classes/tsgen.md]]",
                 "Stored procedures `RemainingCredit()` and `ValOrder()` read `max_order_amt` and `min_order_amt`",
                 "Views `CUSTOMER LISTING` ([[../../06-reports/listcust.md]]), `ORDERS VIEW` ([[../../06-reports/orders.md]]), `ORDER HISTORY`, `TOP25CUST` ([[../../06-reports/topcust.md]])"],
    "EMPLOYEE": ["[[../../04-forms/employee.md]] (`frmemployee`) maintains it",
                 "[[../../04-forms/chngpswd.md]] (`frmchangepassword`) updates `password`",
                 "[[../../04-forms/gettitle.md]] lists distinct titles for the employee report",
                 "`login` class in [[../../05-classes/login.md]] authenticates against it",
                 "Stored procedure `DefaultEmployee()` falls back to its first record",
                 "View `EMPLOYEE LISTING`, printed by [[../../06-reports/listempl.md]]"],
    "ORDER_LINE_ITEMS": ["[[../../04-forms/ordentry.md]] (`frmorderentry`) edits it in a grid",
                         "[[../../04-forms/ordhist.md]] (`frmordhistory`) reads it",
                         "Stored procedures `ValOrder()`, `CalcMinOrdAmount()`, `CalcOrdTotal()`, `RemainingCredit()`",
                         "Views `ORDER HISTORY LINE ITEMS`, `ORDERS VIEW`, `ORDER HISTORY`, `ORDERTOTAL`, `SALES SUMMARY`, `SALES DETAIL`"],
    "ORDERS": ["[[../../04-forms/ordentry.md]] (`frmorderentry`) creates and edits orders",
               "[[../../04-forms/ordhist.md]] (`frmordhistory`) lists a customer's orders and toggles `paid`",
               "`findorder` class in [[../../05-classes/tsgen.md]]",
               "Every hand-written stored procedure except `NewID()` and `DefaultEmployee()`",
               "Views `ORDERS VIEW` ([[../../06-reports/orders.md]]), `ORDER HISTORY`, `ORDERTOTAL`, `SALES SUMMARY` ([[../../06-reports/salessum.md]]), `SALES DETAIL` ([[../../06-reports/salesdet.md]])"],
    "PRODUCTS": ["[[../../04-forms/product.md]] (`frmproducts`) maintains it",
                 "[[../../04-forms/ordentry.md]] and [[../../04-forms/ordhist.md]] open it as a lookup",
                 "Views `PRODUCT LISTING` ([[../../06-reports/listprod.md]]), `ORDER HISTORY LINE ITEMS`, `ORDERS VIEW`"],
    "SETUP": ["Stored procedure `NewID()` only. No form opens it directly"],
    "SHIPPERS": ["[[../../04-forms/shipper.md]] (`frmshippers`) maintains it",
                 "[[../../04-forms/ordentry.md]] opens it as a lookup",
                 "Views `SHIPPER LISTING` ([[../../06-reports/listship.md]]), `ORDERS VIEW`"],
    "SUPPLIER": ["[[../../04-forms/supplier.md]] (`frmsuppliers`) maintains it",
                 "[[../../04-forms/product.md]] opens it as a lookup",
                 "View `SUPPLIER LISTING`, printed by [[../../06-reports/listsupp.md]]"],
    "USER_LEVEL": ["[[../../04-forms/employee.md]] (`frmemployee`) opens it as a lookup for `group_id`",
                   "`tastrade` application class in [[../../05-classes/main.md]] (`getstartupaction`) looks up `startup_action` by the user level's `description` after login and returns it to be run as a VFP command"],
}

PURPOSE = {
    "CATEGORY": "Lookup table of the eight product categories (Beverages, Condiments, ...) that every product belongs to.",
    "CUSTOMER": "The customers who place orders, with their credit terms: a minimum and maximum order amount and a standard discount.",
    "EMPLOYEE": "Employees of the company. Doubles as the login table: `password` and `group_id` drive authentication and the user level.",
    "ORDER_LINE_ITEMS": "One row per product on an order, with the quantity and the unit price captured at order time.",
    "ORDERS": "The order header: who ordered, who ships it, where it ships to, discount, freight, and whether it is paid.",
    "PRODUCTS": "The product catalogue with pricing, cost, stock levels, and links to the supplier and category.",
    "SETUP": "The primary-key generator. One row per table (or counter) holding the next key value, consumed by `NewID()`.",
    "SHIPPERS": "Lookup table of the three shipping companies an order can be sent by.",
    "SUPPLIER": "The companies that supply products.",
    "USER_LEVEL": "Security groups. Each employee belongs to one; the group's `startup_action` is code the application runs at login.",
}

NOTES = {
    "CATEGORY": [
        "`picture` is a **General** (OLE) field and `picture_file` a memo holding the file name it was loaded from. General fields have no equivalent outside VFP; a rebuild must store the image file instead.",
        "`category_name` carries the only field **Caption** in the whole DBC (`Name:`). Nothing else uses captions.",
        "`category_id` defaults to `newid()`, so the stored procedure runs on every APPEND, even outside the application.",
    ],
    "CUSTOMER": [
        "`max_order_amt` and `min_order_amt` validate against **each other**. Either rule can fail when only one field is edited, and a rebuild must validate the pair together.",
        "`discount` is `N(2)` holding a whole-number percent. Every order total formula multiplies it by `.01`.",
        "`customer_id` has no default and its rule only requires non-empty. Sample IDs are five-letter Northwind codes such as `ALFKI`; the field is six wide.",
        "The credit check in `RemainingCredit()` sums **unpaid** orders and compares against `max_order_amt`. So `max_order_amt` is a credit limit, not a per-order maximum, despite the comment.",
    ],
    "EMPLOYEE": [
        "**NOTE:** `password` is `C(8)` plain text with default `\"Tastrade\"`. Every sample employee can log in with the default. A rebuild must not carry this forward.",
        "`photo` is a **General** field and `photo_file` its source file name; see the category note.",
        "The insert trigger is RI only: an employee cannot be added with a `group_id` that is not in USER_LEVEL.",
        "`sales_region` is `C(4)` and matches `customer.sales_region`, but no relation or rule enforces it.",
        "The `extension` comment misspells \"Employee\"; the data is a phone extension, not a home phone.",
    ],
    "ORDER_LINE_ITEMS": [
        "**NOTE:** No primary key and no candidate key. The same product can appear twice on one order and nothing in the DBC prevents it. Only the two foreign-key tags exist.",
        "`unit_price` is copied from `products.unit_price` when the line is entered (see the order entry form), so later price changes do not alter historical orders.",
        "`quantity` is `N(12,3)`, allowing fractional quantities, with default 1.",
        "There is no delete trigger; deletes are only ever caused by the cascade from ORDERS.",
        "The DBF is `orditems.dbf`; the DBC long name is `ORDER_LINE_ITEMS`. Code uses both spellings.",
    ],
    "ORDERS": [
        "Two independent counters: `order_id` defaults to `newid()` (counter `ORDERS`) and `order_number` to `newid(\"order_number\")` (counter `ORDER_NUMBER`). They happen to be equal in the sample data (both at 1138) but nothing keeps them so.",
        "**NOTE:** The table rule `valorder()` shows `MESSAGEBOX` dialogs and inspects `_screen.ActiveForm.Name` for `frmordhistory`. The data layer knows about the UI. A rebuild has to move that decision out of the rule.",
        "`deliver_by` must be on or after `order_date` and defaults to a week out.",
        "`employee_id` defaults to `defaultemployee()`, which asks the running application object for the logged-in employee.",
        "`paid` has no comment and no default. `ORDER HISTORY` lets the user toggle it, and `ValOrder()` skips the credit check when `paid` is the only changed field.",
        "`cust_ord` is a candidate key on `customer_id + order_id`, redundant with the primary key but used for seeking a customer's orders.",
    ],
    "PRODUCTS": [
        "`units_in_stock`, `units_on_order`, and `reorder_level` are `N(12,3)`: stock is tracked in fractional units. Nothing in the DBC adjusts stock when an order is saved; check the order entry form before assuming inventory is maintained.",
        "`unit_price` and `unit_cost` are Currency (`Y`). `unit_price` is the value copied onto order lines.",
        "The insert trigger is RI only: `supplier_id` and `category_id` must exist.",
        "`english_name` exists because the sample product names are in several languages.",
    ],
    "SETUP": [
        "`value` is `C(6)`, so keys are zero-padded strings and the counter tops out at 999999. `NewID()` increments with `STR(VAL(...) + 1, LEN(setup.value))`.",
        "**NOTE:** `NewID()` sets `SET REPROCESS TO AUTOMATIC` and `RLOCK()`s the row, so every insert into any keyed table serializes on this one record. Under load this is the contention point.",
        "The rows named after tables use the DBC long name (`ORDERS`, not `orditems`). `NewID()` looks up `UPPER(ALIAS())`, so calling it from an alias that differs from the DBC name returns an empty ID.",
        "Not part of any relation; no triggers.",
    ],
    "SHIPPERS": ["Both tags exist so the order entry combo can sort by name while the relation seeks by ID."],
    "SUPPLIER": ["`contact_na` is the only name index in the DBC that is **not** wrapped in `UPPER()`; seeks on it are case-sensitive."],
    "USER_LEVEL": [
        "**NOTE:** `startup_action` holds executable VFP code (`oApp.DoForm(\"ordentry\")` for group 1). The application object's `getstartupaction` method fetches it with `LOOKUP()` on the `descriptio` tag, matching the user level by **description text**, not by `group_id`, and the caller executes the string as a command. Code stored in data; a rebuild needs a lookup of allowed actions instead.",
        "The DBF is `user_lev.dbf`; the DBC long name is `USER_LEVEL`.",
        "No trigger stops an employee from being left with a `group_id` that is later deleted: the delete trigger on this table restricts, so the group cannot go while employees reference it.",
    ],
}

SAMPLE = {
    "CATEGORY": ("data/category.dbf", ["category_i", "category_n"], ["category_id", "category_name"], 8),
    "SHIPPERS": ("data/shippers.dbf", ["shipper_id", "company_na"], ["shipper_id", "company_name"], 3),
    "USER_LEVEL": ("data/user_lev.dbf", ["group_id", "descriptio", "startup_ac"], ["group_id", "description", "startup_action"], 4),
    "SETUP": ("data/setup.dbf", ["key_name", "value"], ["key_name", "value"], 7),
    "EMPLOYEE": ("data/employee.dbf", ["last_name", "first_name", "title", "group_id"], ["last_name", "first_name", "title", "group_id"], 15),
    "CUSTOMER": ("data/customer.dbf", ["customer_i", "company_na", "max_order_", "min_order_", "discount"], ["customer_id", "company_name", "max_order_amt", "min_order_amt", "discount"], 5),
}

def md_escape(s):
    return s.replace("|", "\\|")

def fmt_val(v):
    if v is None:
        return ""
    if isinstance(v, float):
        return ("%.2f" % v).rstrip("0").rstrip(".")
    return str(v).strip()

def sample_rows(tname):
    if tname not in SAMPLE:
        return ""
    path, cols, heads, n = SAMPLE[tname]
    _, rows = read_table(os.path.join(ROOT, path))
    out = ["## Sample / notable rows", ""]
    if n >= len(rows):
        out.append("All %d rows:" % len(rows))
    else:
        out.append("First %d of %d rows:" % (n, len(rows)))
    out.append("")
    out.append("| " + " | ".join(heads) + " |")
    out.append("|" + "---|" * len(heads))
    for r in rows[:n]:
        out.append("| " + " | ".join(md_escape(fmt_val(r.get(c))) for c in cols) + " |")
    out.append("")
    return "\n".join(out)

def rel_lines(tname):
    out = []
    for r in rels:
        w = ri_words(r["ri"])
        if r["child"] == tname:
            out.append("- **Child of** [[%s.md]] on `%s` → parent tag `%s`. RI: update %s, delete %s, insert %s."
                       % (r["parent"].lower(), r["child_tag"].lower(), r["parent_tag"].lower(), w["update"], w["delete"], w["insert"]))
        if r["parent"] == tname:
            out.append("- **Parent of** [[%s.md]] via child tag `%s`. RI: update %s, delete %s, insert %s."
                       % (r["child"].lower(), r["child_tag"].lower(), w["update"], w["delete"], w["insert"]))
    return out or ["- None. This table is not in any persistent relation."]

def table_doc(t):
    name = t["name"]
    L = []
    L.append("# %s" % name)
    L.append("")
    L.append("| Source file | Type | Path |")
    L.append("|---|---|---|")
    L.append("| `%s` | Table in `tastrade.dbc` | `data/tastrade.dc2` (table block `%s`) |" % (t["dbf"], name))
    L.append("")
    L.append("**Purpose:** %s" % PURPOSE[name])
    L.append("")
    L.append("**Used by:**")
    for u in USED_BY[name]:
        L.append("- " + u)
    L.append("")
    L.append("**Related docs:** [[../README.md]] (container, stored procedures, views)")
    L.append("")
    L.append("Row count in the sample data: %d. DBC comment: \"%s\"." % (t["rows"], t["comment"]))
    L.append("")
    L.append("## Schema")
    L.append("")
    L.append("| # | Field | Type | Width | Dec | Null | Default | Field-valid expr | Comment |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for i, f in enumerate(t["fields"], 1):
        rule = ("`%s`" % f["rule"]) if f["rule"] else ""
        if f["rule_text"]:
            rule += " → %s" % md_escape(f["rule_text"])
        dflt = ("`%s`" % f["default"]) if f["default"] else ""
        comment = md_escape(f["comment"])
        if f["caption"]:
            comment += " (caption `%s`)" % f["caption"]
        L.append("| %d | `%s` | %s (%s) | %s | %s | %s | %s | %s | %s |"
                 % (i, f["name"].lower(), TYPE.get(f["type"], f["type"]), f["type"], f["width"], f["dec"],
                    "yes" if f["null"] == "Y" else "no", dflt, rule, comment))
    L.append("")
    L.append("## Triggers (from table header)")
    L.append("")
    L.append("- Insert: %s" % ("`%s`" % t["ins"] if t["ins"] else "none"))
    L.append("- Update: %s" % ("`%s`" % t["upd"] if t["upd"] else "none"))
    L.append("- Delete: %s" % ("`%s`" % t["del"] if t["del"] else "none"))
    if t["rule"]:
        L.append("- Table valid: `%s`%s" % (t["rule"], (" — " + t["rule_text"]) if t["rule_text"] else ""))
    else:
        L.append("- Table valid: none")
    L.append("")
    if t["ins"] or t["upd"] or t["del"]:
        L.append("The `__ri_*` triggers are generated referential-integrity code (see the container README). "
                 "They enforce the relations listed below and contain no business rules.")
        L.append("")
    L.append("## Indexes (.cdx tags)")
    L.append("")
    L.append("| Tag | Type | Expression | For | Order |")
    L.append("|---|---|---|---|---|")
    for g in t["tags"]:
        L.append("| `%s` | %s | `%s` | %s | %s |" % (g["name"].lower(), g["kind"].lower(), g["key"],
                                                    ("`%s`" % g["for"]) if g["for"] else "", g["dir"].lower()))
    L.append("")
    if t["pk"]:
        L.append("Primary key tag: `%s`." % t["pk"].lower())
        L.append("")
    L.append("## Stored procedure references")
    L.append("")
    refs = set()
    for f in t["fields"]:
        for fn in HAND_FUNCS:
            if fn.lower() in (f["default"] + f["rule"]).lower():
                refs.add((fn, "default of `%s`" % f["name"].lower() if fn.lower() in f["default"].lower() else "rule of `%s`" % f["name"].lower()))
    if t["rule"]:
        for fn in HAND_FUNCS:
            if fn.lower() in t["rule"].lower():
                refs.add((fn, "table rule"))
    if refs:
        for fn, where in sorted(refs):
            L.append("- `%s()` — %s. Quoted and explained in [[../README.md]]." % (fn, where))
    else:
        L.append("- None from defaults or rules.")
    L.append("")
    L.append("## Relations")
    L.append("")
    L.extend(rel_lines(name))
    L.append("")
    L.append("## Used by")
    L.append("")
    L.append("See the header. Forms open this table through their DataEnvironment; reports reach it through the DBC views named above.")
    L.append("")
    s = sample_rows(name)
    if s:
        L.append(s)
    L.append("## Notes")
    L.append("")
    for n in NOTES[name]:
        L.append("- " + n)
    L.append("")
    return "\n".join(L)

# ----------------------------------------------------------------- README
def readme():
    L = []
    L.append("# Data model: `tastrade.dbc`")
    L.append("")
    L.append("| Source file | Type | Path |")
    L.append("|---|---|---|")
    L.append("| `tastrade.dbc` | Database container | `data/tastrade.dc2` |")
    L.append("")
    L.append("**Purpose:** The single database of the Tastrade sample: ten tables for customers, orders, "
             "products, and the people who sell them, plus the key generator and the security groups. "
             "It holds the business rules as stored procedures wired to defaults, validation rules, and triggers.")
    L.append("")
    L.append("**Used by:** Every form opens its tables from this container through its DataEnvironment "
             "(`tastrade!table`). The list and sales reports print the container's views. "
             "`progs/main.prg` never opens it directly; the `tastrade` application object does.")
    L.append("")
    L.append("**Related docs:** one file per table under [`tables/`](tables/); [[../PROJECT.md]] for naming rules.")
    L.append("")
    L.append("## Tables")
    L.append("")
    L.append("| Table (DBC name) | File | Rows | Primary key | Triggers | Table rule | Doc |")
    L.append("|---|---|---|---|---|---|---|")
    for name in sorted(tables):
        t = tables[name]
        trig = ", ".join(x for x, v in (("insert", t["ins"]), ("update", t["upd"]), ("delete", t["del"])) if v) or "none"
        L.append("| `%s` | `%s` | %d | %s | %s | %s | [[tables/%s.md]] |"
                 % (name, t["dbf"], t["rows"], ("`%s`" % t["pk"].lower()) if t["pk"] else "**none**",
                    trig, ("`%s`" % t["rule"]) if t["rule"] else "", name.lower()))
    L.append("")
    L.append("Three more tables ship with the sample but are **free tables outside the DBC**: "
             "`data/behindsc.dbf` (the \"behind the scenes\" explanations, 65 rows), "
             "`data/repolist.dbf` (the report picker list, 10 rows), and `help/ttrade.dbf` "
             "(help topics, 16 rows). Each has its own doc: [[tables/behindsc.md]], [[tables/repolist.md]], "
             "[[tables/ttrade.md]]; their schemas are summarised at the end of this page.")
    L.append("")
    L.append("Long table names are DBC properties. The DBF headers truncate field names to ten characters "
             "(`customer_i`, `category_n`), and two DBFs have different names from their tables "
             "(`orditems.dbf` is `ORDER_LINE_ITEMS`, `user_lev.dbf` is `USER_LEVEL`). "
             "Code that opens the DBF directly, bypassing the container, sees the short names.")
    L.append("")
    L.append("## Relations and referential integrity")
    L.append("")
    L.append("Eight persistent relations, all with RI rules generated by VFP's RI Builder. "
             "Codes are Update / Delete / Insert; C cascade, R restrict.")
    L.append("")
    L.append("| Child | Child tag | Parent | Parent tag | Update | Delete | Insert |")
    L.append("|---|---|---|---|---|---|---|")
    for r in sorted(rels, key=lambda x: (x["child"], x["parent"])):
        w = ri_words(r["ri"])
        L.append("| [[tables/%s.md]] | `%s` | [[tables/%s.md]] | `%s` | %s | %s | %s |"
                 % (r["child"].lower(), r["child_tag"].lower(), r["parent"].lower(), r["parent_tag"].lower(),
                    w["update"], w["delete"], w["insert"]))
    L.append("")
    L.append("Read as: a parent key change cascades to children; a parent cannot be deleted while children "
             "exist, except an order, whose line items are deleted with it; a child cannot be inserted "
             "with a key that has no parent. `SETUP` is in no relation.")
    L.append("")
    L.append("```mermaid")
    L.append("erDiagram")
    L.append("    USER_LEVEL ||--o{ EMPLOYEE : group_id")
    L.append("    CUSTOMER ||--o{ ORDERS : customer_id")
    L.append("    EMPLOYEE ||--o{ ORDERS : employee_id")
    L.append("    SHIPPERS ||--o{ ORDERS : shipper_id")
    L.append("    ORDERS ||--o{ ORDER_LINE_ITEMS : order_id")
    L.append("    PRODUCTS ||--o{ ORDER_LINE_ITEMS : product_id")
    L.append("    SUPPLIER ||--o{ PRODUCTS : supplier_id")
    L.append("    CATEGORY ||--o{ PRODUCTS : category_id")
    L.append("```")
    L.append("")
    L.append("## Views")
    L.append("")
    L.append("Thirteen local views, all read-only (`SendUpdates` off). The `LISTING` views feed the six "
             "list reports; the rest feed the sales reports and the order history form. Views with `?name` "
             "parameters are opened by code that supplies the value.")
    L.append("")
    L.append("| View | Parameters | Feeds | SQL |")
    L.append("|---|---|---|---|")
    FEEDS = {
        "CATEGORY LISTING": "[[../06-reports/listcat.md]]", "CUSTOMER LISTING": "[[../06-reports/listcust.md]]",
        "EMPLOYEE LISTING": "[[../06-reports/listempl.md]]", "PRODUCT LISTING": "[[../06-reports/listprod.md]]",
        "SHIPPER LISTING": "[[../06-reports/listship.md]]", "SUPPLIER LISTING": "[[../06-reports/listsupp.md]]",
        "SALES SUMMARY": "[[../06-reports/salessum.md]]", "SALES DETAIL": "[[../06-reports/salesdet.md]]",
        "ORDERS VIEW": "[[../06-reports/orders.md]] (invoices)", "TOP25CUST": "[[../06-reports/topcust.md]]",
        "ORDERTOTAL": "`TOP25CUST` (view on a view)", "ORDER HISTORY": "[[../04-forms/ordhist.md]]",
        "ORDER HISTORY LINE ITEMS": "[[../04-forms/ordhist.md]]",
    }
    for v in sorted(views, key=lambda x: x["name"]):
        params = ", ".join("`%s`" % p for p in re.findall(r"\?([A-Za-z_][\w.]*)", v["sql"])) or ""
        sql = re.sub(r"\s+", " ", v["sql"])
        L.append("| `%s` | %s | %s | `%s` |" % (v["name"], params, FEEDS.get(v["name"], ""), md_escape(sql)))
    L.append("")
    L.append("Things to know about the views:")
    L.append("")
    L.append("- **NOTE:** `SALES SUMMARY` and `SALES DETAIL` sum `unit_price` alone, not `unit_price * quantity`, "
             "and ignore discount and freight. The sales reports therefore do not agree with the order totals "
             "shown elsewhere. This looks like a sample-data simplification rather than intent; a rebuild should decide which is right.")
    L.append("- `ORDER HISTORY` and `ORDERTOTAL` carry the order total formula in SQL: "
             "`SUM(unit_price*quantity) - discount% of that + freight`. The same formula appears in the stored procedures below, "
             "twice without freight and once with it.")
    L.append("- `ORDER HISTORY LINE ITEMS` selects a literal `.F.` as its first column, a placeholder for a grid checkbox.")
    L.append("- `TOP25CUST` uses `SELECT TOP 25 ... ORDER BY custtotal DESC` over the `ORDERTOTAL` view.")
    L.append("- View parameters `?orders.order_id` and `?customer.customer_id` are field references, so those views "
             "can only be opened while the parent alias is open and positioned.")
    L.append("")
    L.append("## Stored procedures")
    L.append("")
    L.append("The container holds %d procedures: six hand-written business functions and %d generated by the "
             "RI Builder. The block starts with `#INCLUDE INCLUDE\\TASTRADE.H`, so the procedures use the "
             "`_LOC` string constants and `MB_*` values from the include files." % (len(HAND_FUNCS) + len(ri_procs), len(ri_procs)))
    L.append("")
    L.append("### Where each one is wired")
    L.append("")
    L.append("| Function | Called from |")
    L.append("|---|---|")
    L.append("| `NewID()` | Default of `category_id`, `supplier_id`, `shipper_id`, `product_id`, `order_id`, `employee_id`; `NewID(\"order_number\")` default of `orders.order_number` |")
    L.append("| `DefaultEmployee()` | Default of `orders.employee_id` |")
    L.append("| `ValOrder()` | Table validation rule of `ORDERS` |")
    L.append("| `CalcMinOrdAmount()` | `ValOrder()` |")
    L.append("| `CalcOrdTotal()` | **Nothing.** Not referenced by any form, class, program, view, rule, or default. Dead duplicate of `CalcMinOrdAmount()` |")
    L.append("| `RemainingCredit()` | `ValOrder()`; also the order entry form |")
    L.append("")
    explain = {
        "NewID": "Returns the next key for a table and advances the counter in `SETUP`. Uses the DBC long name of "
                 "the current alias (or the name passed in) as the lookup key, locks the `SETUP` row with "
                 "`SET REPROCESS TO AUTOMATIC` so it waits indefinitely for the lock, increments the value as a "
                 "zero-padded string of the same width, and returns the **old** value. Returns an empty string if "
                 "the key name is not in `SETUP` or the lock fails, and nothing downstream checks for that.",
        "RemainingCredit": "Credit available to a customer: `max_order_amt` minus the total of all **unpaid** orders. "
                           "Opens `customer` and `orders` again under temporary aliases so it can run from inside a "
                           "trigger on `orders` without an \"illegal recursion\" error. The per-order total is "
                           "`sum(price*qty) - discount% * sum(price*qty) + freight`, the only place in the stored "
                           "procedures where freight is included.",
        "ValOrder": "The `ORDERS` table rule, run on every save. In order: skip if the record is being deleted; "
                    "require at least one line item with a product (message `ORDHASITEMS_LOC`); unless the only "
                    "change is the `paid` flag or the active form is the order history form, check that the "
                    "customer's remaining credit is not negative and, if it is, ask whether to save anyway "
                    "(`CUSTOVERMAX_LOC`); then check the order meets the customer's `min_order_amt` and again ask "
                    "(`CUSTUNDERMIN_LOC`). Returns the user's answer. **NOTE:** a table rule that shows dialogs "
                    "and reads `_screen.ActiveForm.Name`.",
        "CalcMinOrdAmount": "Order total after discount, **without freight**, for the order whose ID is passed, "
                            "summed from `order_line_items` with a `FOR` scan. Assumes `orders` is open and "
                            "positioned so that `orders.discount` is the right row.",
        "CalcOrdTotal": "Identical to `CalcMinOrdAmount()` except that it restores the selected work area. "
                        "Two copies of the same formula under two names, and this one is never called: no form, "
                        "class, program, or DBC object references it. **NOTE:** dead code.",
        "DefaultEmployee": "The employee to stamp on a new order: the logged-in employee from the application "
                           "object `oApp` if it exists, otherwise the first record of `employee`. The fallback "
                           "exists so the table can be edited in the IDE without the app running.",
    }
    for fn in HAND_FUNCS:
        L.append("### `%s`" % fn)
        L.append("")
        L.append(explain[fn])
        L.append("")
        L.append("```foxpro")
        L.append(func_block(fn))
        L.append("```")
        L.append("")
    L.append("### Generated referential-integrity code")
    L.append("")
    L.append("Everything after the line `**__RI_HEADER!@ Do NOT REMOVE or MODIFY this line!!!! @!__RI_HEADER**` "
             "is emitted by VFP's RI Builder from the relation rules above and is regenerated whenever the "
             "builder runs. It is not business logic and is not quoted here. It consists of:")
    L.append("")
    L.append("- Six shared helpers: `RIDELETE`, `RIUPDATE`, `rierror`, `riopen`, `riend`, `rireuse`. They "
             "open the related tables again under `__ri` aliases, wrap the whole trigger in a transaction, "
             "collect errors into the array `gaErrors`, and restore `SET` state on exit.")
    L.append("- One `__RI_INSERT_*`, `__RI_UPDATE_*`, or `__RI_DELETE_*` procedure per table and direction, "
             "named in the trigger columns of the table list above: %s." % ", ".join("`%s`" % p for p in ri_procs if p.upper().startswith("__RI")))
    L.append("")
    L.append("The `__RI_UPDATE_*` triggers cascade key changes to children; the `__RI_DELETE_*` triggers refuse "
             "while children exist (or cascade, for `ORDERS`); the `__RI_INSERT_*` triggers refuse a child whose "
             "parent key is missing. A rebuild replaces all of this with foreign-key constraints.")
    L.append("")
    L.append("## The order total, in one place")
    L.append("")
    L.append("The same calculation is written five times in this container. A rebuild should implement it once.")
    L.append("")
    L.append("| Where | Formula | Freight |")
    L.append("|---|---|---|")
    L.append("| `CalcMinOrdAmount()` | `SUM((unit_price*quantity) - (orders.discount*.01)*(unit_price*quantity))` | no |")
    L.append("| `CalcOrdTotal()` | same | no |")
    L.append("| `RemainingCredit()` | same, `+ a.freight`, per unpaid order | yes |")
    L.append("| View `ORDER HISTORY` | `SUM(p*q) - discount*0.01*SUM(p*q) + freight` | yes |")
    L.append("| View `ORDERTOTAL` | `SUM(p*q - 0.01*discount*p*q) + freight` | yes |")
    L.append("")
    L.append("## Free tables outside the DBC")
    L.append("")
    for name in ("behindsc", "repolist", "ttrade"):
        t = free[name]
        L.append("### `%s` (%d rows), see [[tables/%s.md]]" % (t["dbf"], t["rows"], name))
        L.append("")
        L.append("| Field | Type | Width | Dec |")
        L.append("|---|---|---|---|")
        for f in t["fields"]:
            L.append("| `%s` | %s | %s | %s |" % (f["name"].lower(), f["type"], f["width"], f["dec"]))
        if t["tags"]:
            L.append("")
            L.append("Tags: " + ", ".join("`%s` on `%s`" % (g["name"].lower(), g["key"]) for g in t["tags"]) + ".")
        L.append("")
    L.append("`behindsc` pairs a form name with explanatory text and code snippets for the \"Behind the Scenes\" "
             "form; `repolist` maps report file names to display names and a type (`REPO` or `LIST`) for the "
             "report picker; `ttrade` is a VFP DBF-format help file, the form VFP used before HTML Help, "
             "kept beside the compiled `tastrade.chm` the application actually opens.")
    L.append("")
    L.append("## Notes")
    L.append("")
    L.append("- The DBC is opened `SHARED`; nothing in it requires exclusive access.")
    L.append("- The only field caption in the container is on `category.category_name`. Captions were not used.")
    L.append("- No table has an auto-increment field; all keys come from `NewID()` and `SETUP`.")
    L.append("- Two General fields (`category.picture`, `employee.photo`) hold OLE objects. Everything else is plain data.")
    L.append("- Schema, tags, and RI rules on this page were read from the live tables through VFP 9 "
             "(`AFIELDS()`, `TAG()`/`KEY()`, `ADBOBJECTS()`), because the `.dc2` twin records only what the "
             "container stores: names, comments, defaults, rules, and triggers. Field types and index expressions "
             "live in the DBF and CDX headers.")
    L.append("")
    return "\n".join(L)

with open(os.path.join(OUT, "README.md"), "w", encoding="utf-8", newline="\n") as f:
    f.write(readme())
for name, t in tables.items():
    with open(os.path.join(TOUT, name.lower() + ".md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(table_doc(t))
print("wrote README + %d table docs" % len(tables))
