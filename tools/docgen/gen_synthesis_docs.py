"""Generate docs/02-domain/README.md (what the business does, in plain language)
and docs/09-business-logic/README.md (every rule and formula, quoted from source).

Structure comes from the parsers: field defaults and rules and the view SQL from
the DBC twin, stored procedure bodies from its procedure block, method bodies
from the class and form twins, report variables from the invoice twin, the
menu cleanup code from the main menu twin, and row counts and value profiles
from the DBF data. Prose is hand-written and was checked against a grep of the
twins. Rerun after editing; never hand-edit the output.
"""
import os, re, sys, collections, textwrap
sys.path.insert(0, os.environ.get("VFP_TOOLKIT_TOOLS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "vfp-documentation-toolkit", "tools")))
import foxparse as fp
import dbf

ROOT = os.environ.get("TASTRADE_ROOT", os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))


def out_dir(name):
    d = os.path.join(ROOT, "docs", name)
    os.makedirs(d, exist_ok=True)
    return d


def fence(code, lang="foxpro"):
    return "```%s\n%s\n```" % (lang, textwrap.dedent(code).strip("\n"))


def rows(table):
    fields, data = dbf.read_table(os.path.join(ROOT, table))
    return [f[0] for f in fields], data


# ------------------------------------------------------------------ sources
DBC = fp.parse_dc2(os.path.join(ROOT, "data", "tastrade.dc2"))
SP_TEXT = DBC["stored_procedures"]


def stored_proc(name):
    m = re.search(r"^\s*FUNCTION\s+%s\b.*?^\s*ENDFUNC" % name, SP_TEXT, re.S | re.M | re.I)
    assert m, name
    return m.group(0)


def view_sql(name):
    for v in DBC["views"]:
        if v["name"].upper() == name.upper():
            return v["sql"]
    raise KeyError(name)


def field_rules():
    out = []
    for t in DBC["tables"]:
        for f in t["fields"]:
            if f["rule"] or f["default"]:
                out.append((t["name"], f["name"], f["default"], f["rule"], f["rule_text"]))
    return out


ORDERS_CLS = next(c for c in fp.parse_vc2(os.path.join(ROOT, "libs", "orders.vc2"))["classes"] if c["name"].lower() == "orderentry")
ORDENTRY = fp.parse_sc2(os.path.join(ROOT, "forms", "ordentry.sc2"))
ORDHIST = fp.parse_sc2(os.path.join(ROOT, "forms", "ordhist.sc2"))
LOGIN = next(c for c in fp.parse_vc2(os.path.join(ROOT, "libs", "login.vc2"))["classes"] if c["name"].lower() == "login")
MAINMENU = fp.parse_mn2(os.path.join(ROOT, "menus", "main.mn2"))
INVOICE = fp.parse_fr2(os.path.join(ROOT, "reports", "orders.fr2"))


def method(obj, name):
    for k, v in obj["methods"].items():
        if k.lower() == name.lower():
            return v
    raise KeyError(name)


# ------------------------------------------------------------------ data profile
def profile():
    P = {}
    n, o = rows("data/orders.dbf")
    P["orders"] = len(o)
    dates = sorted(r["order_date"] for r in o if r["order_date"])
    iso = lambda v: "%s-%s-%s" % (str(v)[:4], str(v)[4:6], str(v)[6:8]) if re.fullmatch(r"\d{8}", str(v)) else str(v)
    P["first_order"], P["last_order"] = iso(dates[0]), iso(dates[-1])
    P["paid"] = sum(1 for r in o if r["paid"]); P["unpaid"] = len(o) - P["paid"]
    P["discounts"] = collections.Counter(int(r["discount"]) for r in o).most_common()
    P["freight_zero"] = sum(1 for r in o if not r["freight"])
    P["customers_with_orders"] = len({str(r["customer_i"]) for r in o})
    P["employees_on_orders"] = len({str(r["employee_i"]) for r in o})
    P["shipper_split"] = collections.Counter(str(r["shipper_id"]).strip() for r in o)
    P["max_order_id"] = max(int(str(r["order_id"]).strip()) for r in o)
    n, li = rows("data/orditems.dbf")
    P["lines"] = len(li); P["lines_per_order"] = len(li) / len(o)
    P["fractional_qty"] = sum(1 for r in li if float(r["quantity"]) % 1)
    n, c = rows("data/customer.dbf")
    mx = next(k for k in n if k.startswith("max")); mn = next(k for k in n if k.startswith("min"))
    P["customers"] = len(c)
    P["countries"] = collections.Counter(str(r["country"]).strip() for r in c)
    P["cust_min_set"] = sum(1 for r in c if r[mn]); P["cust_max_set"] = sum(1 for r in c if r[mx]); P["cust_discount_set"] = sum(1 for r in c if r["discount"])
    n, p = rows("data/products.dbf")
    P["products"] = len(p); P["discontinued"] = sum(1 for r in p if r["discontinu"])
    n, cat = rows("data/category.dbf"); P["categories"] = [str(r["category_n"]).strip() for r in cat]
    n, sh = rows("data/shippers.dbf"); P["shippers"] = [(str(r["shipper_id"]).strip(), str(r["company_na"]).strip()) for r in sh]
    n, su = rows("data/supplier.dbf"); P["suppliers"] = len(su)
    n, e = rows("data/employee.dbf"); P["employees"] = len(e)
    P["titles"] = collections.Counter(str(r["title"]).strip() for r in e)
    P["groups"] = collections.Counter(str(r["group_id"]).strip() for r in e)
    P["default_passwords"] = sum(1 for r in e if str(r["password"]).strip() == "Tastrade")
    n, s = rows("data/setup.dbf"); P["setup"] = [(str(r["key_name"]).strip(), str(r["value"]).strip()) for r in s]
    n, u = rows("data/user_lev.dbf"); P["levels"] = [tuple(str(r[k]).strip() for k in n) for r in u]
    return P


# ------------------------------------------------------------------ 02-domain
def gen_domain(P):
    setup = dict(P["setup"])
    L = ["# The business, in plain language", "",
         "What Tasmanian Traders does, read out of the data model, the forms, the rules, and the sample's own help and \"Behind the Scenes\" text. Every statement points at the doc that carries the source. Where the sample's description and its code disagree, both are given.", "",
         "**Related docs:** [[../03-data-model/README.md]], [[../09-business-logic/README.md]] (the rules, quoted), [[../04-forms/README.md]], [[../06-reports/README.md]], [[../01-architecture/framework.md]].", "",
         "## What the sample says it is", "",
         "The help file's own introduction (`help/ttrade.dbf`, topic \"Introducing Tasmanian Traders\"):", "",
         "> Welcome to the Tasmanian Traders database! The Tasmanian Traders database stores information about customers, orders, shippers, suppliers, employees, and products. When you log in, your user level is identified as one of the following: Customer Service Representative, Operations Manager, Sales Manager, Application Developer. Depending on your user level, you have access to different tables.", "",
         "Tastrade is a descendant of the Northwind sample: the customer IDs are Northwind's five-letter codes (`ALFKI`, `ANATR`, ...), the splitter class still records a `nwind` path, and the product catalogue is Northwind's (beverages, condiments, seafood). It is a wholesale importer of food and drink that sells to trade customers on account, with a minimum and a maximum order size per customer.", "",
         "## The actors", "",
         "| Who | How the sample models them | Count in the data |", "|---|---|---|",
         "| Customers | `CUSTOMER`: company, contact, address, phone and fax, a normal discount, a minimum and a maximum order amount (the credit line), a sales region | %d, in %d countries; %d have a minimum order set, all %d a maximum, %d a discount |" % (P["customers"], len(P["countries"]), P["cust_min_set"], P["cust_max_set"], P["cust_discount_set"]),
         "| Employees | `EMPLOYEE`: name, title, dates, address, a user-level group, a sales region, a password, a photo | %d, in %d job titles from Sales Representative to Mail Clerk; per user level %s |" % (P["employees"], len(P["titles"]), ", ".join("%s: %d" % kv for kv in sorted(P["groups"].items()))),
         "| Products | `PRODUCTS`: name, English name, quantity per unit, price and cost, stock and reorder figures, a discontinued flag; each in one category from one supplier | %d products, %d categories (%s), %d suppliers, %d discontinued |" % (P["products"], len(P["categories"]), ", ".join(P["categories"]), P["suppliers"], P["discontinued"]),
         "| Shippers | `SHIPPERS`: an ID and a name, nothing else | %d (%s) |" % (len(P["shippers"]), ", ".join(n for i, n in P["shippers"])),
         "| User levels | `USER_LEVEL`: four groups, each with an optional startup action | %s |" % "; ".join("%s %s%s" % (g, d, (" (runs `%s`)" % a) if a else "") for g, d, a in P["levels"]),
         "", "There are no payments, invoices as records, price lists, stock movements, currencies, or taxes. An order is the only transaction.", ""]
    L += ["## The one transaction: an order", "",
          "An order (`ORDERS`) belongs to one customer, is taken by one employee, ships by one shipper to a ship-to address copied from the customer, and has one or more lines (`ORDER_LINE_ITEMS`), each a product, a quantity, and the unit price copied from the product at the moment it is chosen. The header carries an order date, a deliver-by date, a discount percentage (copied from the customer, editable), a freight charge, a paid flag, and notes.", "",
          "Its life, as the forms and rules implement it ([[../04-forms/ordentry.md]], [[../05-classes/orders.md]], [[../09-business-logic/README.md]]):", "",
          "1. **Take it.** The clerk picks a customer (or types a new one and is offered the add-customer dialog), the ship-to block and discount fill from the customer, a due date defaults to a week out, the employee defaults to whoever is logged in, and the order number is drawn from the `SETUP` counter. Lines are added from a product list that does not hide discontinued products; the product's current price is copied onto the line. The screen shows subtotal, discount, freight, total, and the customer's available credit as lines change.",
          "2. **Save it.** One transaction writes the header and all lines. The `ORDERS` table rule then insists on at least one line, warns if the customer's credit line would be exceeded, and warns if the order is under the customer's minimum; both warnings can be overridden with Yes.",
          "3. **Change it.** An order stays editable until its deliver-by date has passed; after that it is read-only and cannot be deleted. The only later change the sample expects is marking it paid, from order entry or from the order history grid, which bypasses the credit and minimum checks.",
          "4. **Reuse it.** From order entry, \"Last Order\" opens the customer's history; tagged lines from an old order are copied into the new one at their historical prices.",
          "5. **Print it.** Invoices for a date range, one page per order, recomputing the total from the lines ([[../06-reports/orders.md]]).", "",
          "Credit is not a balance kept anywhere. It is recomputed on demand as the customer's maximum order amount minus the total of every unpaid order, so paying an order frees credit and nothing else does.", ""]
    L += ["## Master data", "",
          "Six maintenance forms ([[../04-forms/README.md]]) add, edit, and delete customers, employees, products, suppliers, shippers, and categories, all on the same two-page pattern. Referential integrity refuses to delete anything that is in use (a customer with orders, a product on a line, a supplier or category with products, a shipper or employee on orders) and cascades key changes downward; only an order takes its lines with it when deleted. Keys for everything but customers come from the `SETUP` counters; customers type their own five-letter ID.", "",
          "Categories and employees carry pictures, stored as file paths into `bitmaps\\` (and, for categories, a second copy in a General field nobody reads).", ""]
    L += ["## Who may do what", "",
          "The help text says user levels \"have access to different tables\". The code does less: the user level decides which menu pads and bars exist (developers keep the Utilities pad; Operations Managers and above keep Login and Change Password) and which form opens at startup (a Customer Service Rep lands in order entry). No form, rule, or table checks the level. In the shipped build `DEBUGMODE` removes the login, so everyone is an Applications Developer and every user sees everything ([[../07-menus/main.md]], [[../08-programs/tastrade.h.md]]).", "",
          "Passwords are eight plain characters, default `\"Tastrade\"`, compared case-sensitively; in the data every employee has changed theirs (%d still hold the default), and the login screen shows the selected employee's password in a \"Hint\" box ([[../05-classes/login.md]])." % P["default_passwords"], ""]
    L += ["## Reporting", "",
          "Six listings of master data; invoices; two \"sales by month\" reports that sum unit prices without quantity, discount, or freight; a Top 25 Customers report that uses the full order total. The three sales reports therefore do not agree with each other or with the order screens ([[../06-reports/README.md]]).", ""]
    L += ["## What the data says", "",
          "| Fact | Value |", "|---|---|",
          "| Orders | %d, dated %s to %s, %.1f lines each on average (%d lines) |" % (P["orders"], P["first_order"], P["last_order"], P["lines_per_order"], P["lines"]),
          "| Paid | %d paid, %d unpaid |" % (P["paid"], P["unpaid"]),
          "| Discounts on orders | %s |" % ", ".join("%d%% on %d" % (d, n) for d, n in P["discounts"]),
          "| Freight | charged on all but %d orders |" % P["freight_zero"],
          "| Customers with orders | %d of %d |" % (P["customers_with_orders"], P["customers"]),
          "| Employees on orders | %d of %d |" % (P["employees_on_orders"], P["employees"]),
          "| Shippers | orders split %s |" % ", ".join("%s: %d" % (dict(P["shippers"]).get(k, k), v) for k, v in sorted(P["shipper_split"].items())),
          "| Quantities | whole numbers throughout, though the column allows three decimals (%d fractional) |" % P["fractional_qty"],
          "| Key counters (`SETUP`) | %s |" % ", ".join("%s=%s" % kv for kv in P["setup"]),
          "", "Order IDs run from 1 to %d with %d numbers missing, and the `ORDERS` counter already stands at %s: numbers were issued and not kept, as `NewID()` gives them out before the order is saved. Discontinued products can still be ordered, and nothing in the application changes `units_in_stock` or `units_on_order`; the inventory columns are maintained by hand on the product form and read by nothing ([[../04-forms/product.md]])." % (P["max_order_id"], P["max_order_id"] - P["orders"], setup.get("ORDERS")), ""]
    L += ["## Where the description and the code part", "",
          "- **\"Access to different tables\"** by user level is menu gating only, and is off in the shipped build.",
          "- **\"Checking Available Credit\"** (Behind the Scenes) says all the customer's orders are summed; the code sums only unpaid ones ([[../09-business-logic/README.md]], R7).",
          "- **\"Validating an Order\"** lists three conditions and says a failed condition stops the rest; the code asks Yes/No on the credit and minimum conditions and lets the user save anyway.",
          "- **The intro screen and the help** describe a login the shipped build never shows.",
          "- **Inventory fields** exist on the product form and in the help's picture of a product, but no transaction moves them.", ""]
    return "\n".join(L)


# ------------------------------------------------------------------ 09-business-logic
def gen_rules(P):
    L = ["# Business logic, quoted", "",
         "Every rule and formula the application enforces, each quoted from its source through the parser and then explained, with where it is enforced and which other places repeat it. Numbered R1 to R14 so other docs can cite them. The plain-language account is [[../02-domain/README.md]].", "",
         "**Related docs:** [[../03-data-model/README.md]] (the stored procedures in full), [[../05-classes/orders.md]], [[../04-forms/ordentry.md]], [[../04-forms/ordhist.md]], [[../05-classes/login.md]], [[../07-menus/main.md]], [[../06-reports/orders.md]], [[../08-programs/tastrade.h.md]].", "",
         "## Where the rules live", "",
         "| Layer | Rules |", "|---|---|",
         "| DBC field defaults and rules | R1 keys, R2 default employee, R3 field rules |",
         "| DBC table rule | R4 order validation |",
         "| DBC relations (RI Builder triggers) | R5 referential integrity |",
         "| Stored procedures called by code | R7 credit |",
         "| Views | R8 order total (two of seven copies), R12 sales figures |",
         "| Class and form code | R4 duplicates, R6 delete guards, R8 (screen), R9 price and discount copy, R10 editability, R11 login, R13 paid |",
         "| Menu cleanup code and `USER_LEVEL` rows | R14 user levels |",
         "| Report variables | R8 (invoice) |", ""]
    # R1
    L += ["## R1. Keys come from the `SETUP` counters", "",
          "Every table but `CUSTOMER` and `ORDER_LINE_ITEMS` takes its primary key from `NewID()`, the default expression of the key field; `orders.order_number` takes a second counter by name. `SETUP` holds one row per counter (%s). The customer ID is typed by the user and only required to be non-empty (R3); the primary index refuses duplicates and the `customerinfo` container turns error 1884 into \"Customer ID already exists\" ([[../05-classes/tsgen.md]])." % ", ".join("`%s`=%s" % kv for kv in P["setup"]), "",
          "Defaults, from the DBC twin:", "",
          "| Table | Field | Default |", "|---|---|---|"]
    for t, f, d, r, rt in field_rules():
        if d and "newid" in d.lower() or (d and "employee" in d.lower()):
            L.append("| `%s` | `%s` | `%s` |" % (t, f, d))
    L += ["", fence(stored_proc("NewID")), "",
          "Locks the counter row, waiting without limit (`SET REPROCESS TO AUTOMATIC`), returns the old value and stores the incremented one at the same width. **NOTE:** a missing counter name or a failed lock returns an empty key, and no caller checks. `ORDER_LINE_ITEMS` has no key at all ([[../03-data-model/tables/order_line_items.md]]).", ""]
    # R2
    L += ["## R2. A new order belongs to the logged-in employee", "", fence(stored_proc("DefaultEmployee")), "",
          "Default of `orders.employee_id`. **NOTE:** under `DEBUGMODE` the logged-in ID is empty, so every new order in the shipped build goes to the first employee on file ([[../05-classes/main.md]]).", ""]
    # R3
    L += ["## R3. Field rules and defaults", "", "From the DBC twin (`data/tastrade.dc2`); the message is what the user sees when the rule fails.", "",
          "| Table | Field | Default | Rule | Message |", "|---|---|---|---|---|"]
    for t, f, d, r, rt in field_rules():
        if r or (d and "newid" not in d.lower() and "employee" not in d.lower()):
            L.append("| `%s` | `%s` | %s | %s | %s |" % (t, f, ("`%s`" % d) if d else "", ("`%s`" % r) if r else "", rt.strip('"')))
    L += ["",
          "- `max_order_amt` and `min_order_amt` validate against each other; editing one can fail on the other ([[../03-data-model/tables/customer.md]]).",
          "- `deliver_by` defaults to a week out and may not precede the order date; the order form is stricter (R10).",
          "- `password` defaults to `\"Tastrade\"` for every new employee; the sample's own text says \"You must log in as the new employee to change the password.\"", ""]
    # R4
    L += ["## R4. An order must have a line, fit the customer's credit, and meet the minimum", "",
          "The `ORDERS` table rule, `ValOrder()`, runs on every `TABLEUPDATE` of an order. In order: nothing if the row is deleted; at least one line with a product, else refuse; unless the only change is the paid flag or the order history form is on top, compute remaining credit (R7) and ask whether to save anyway if it is negative; then ask again if the order is under the customer's minimum. The user's Yes is the rule's return value.", "",
          fence(stored_proc("ValOrder")), "",
          "The amount compared with the minimum is `CalcMinOrdAmount()`, the total after discount **without freight**:", "", fence(stored_proc("CalcMinOrdAmount")), "",
          "**NOTE:** a data-layer rule that shows dialogs and reads `_screen.ActiveForm.Name`. **NOTE:** `CalcOrdTotal()` is a second copy of the same function, called by nothing ([[../03-data-model/README.md]]). **NOTE:** the sample's Behind the Scenes text says a failed condition stops validation; the code lets the user override the last two.", "",
          "The order entry class forces the rule to fire even when only lines changed, by marking the customer field edited before `TABLEUPDATE`, inside the application's only transaction ([[../05-classes/orders.md]] `save`):", "",
          fence(method(ORDERS_CLS, "save")), ""]
    # R5
    L += ["## R5. Referential integrity", "",
          "Eight relations with RI Builder rules: key changes cascade to children; a parent in use cannot be deleted, except an order, whose lines go with it; a child cannot point at a missing parent. The generated triggers are named in [[../03-data-model/README.md]] and are not business logic. The forms translate the trigger failures into six messages (R6).", "",
          "| Child | Parent | Update | Delete | Insert |", "|---|---|---|---|---|"]
    ri = {("ORDER_LINE_ITEMS", "ORDERS"): ("cascade", "cascade", "restrict")}
    for r in DBC["relations"]:
        u, d, i = ri.get((r["child"], r["parent"]), ("cascade", "restrict", "restrict"))
        L.append("| `%s` | `%s` | %s | %s | %s |" % (r["child"], r["parent"], u, d, i))
    L += ["", "The rule codes come from the live DBC dump behind [[../03-data-model/README.md]]; the twin lists the relations but not the codes.", ""]
    # R6
    L += ["## R6. What may not be deleted, in the user's words", "",
          "Each maintenance form loads the message for its table's delete trigger into `aErrorMsg[DELETETRIG]`; `tsbaseform.Error` shows it on error 1539. The strings are in `include/strings.h` ([[../08-programs/strings.h.md]]).", "",
          "| Form | Message |", "|---|---|",
          "| Category | Products belong to this category. Cannot delete! |",
          "| Customer | Customer has orders. Cannot delete! |",
          "| Employee | Employee exists on orders. Cannot delete! |",
          "| Product | Product exists on order line items. Cannot delete! |",
          "| Supplier | Products are supplied by this supplier. Cannot delete! |",
          "| Shipper | Shipper exists on orders. Cannot delete! |", "",
          "Two more guards are in code, not triggers: the employee form clears `lAllowDelete` when the current record is the logged-in employee (dead under `DEBUGMODE`, [[../04-forms/employee.md]]), and the order form clears it once the deliver-by date has passed (R10).", ""]
    # R7
    L += ["## R7. Credit is the maximum order amount minus unpaid orders", "", fence(stored_proc("RemainingCredit")), "",
          "Called by `ValOrder()` (R4) and by the order entry form whenever the customer changes or the paid flag is toggled, to show \"Available Credit\" ([[../04-forms/ordentry.md]]); the order history form shows the other half of it, the sum of the customer's unpaid order totals, as \"Balance\". The per-order total here includes freight and is computed for **unpaid** orders only. **NOTE:** the sample's Behind the Scenes text says all the customer's orders are summed. `ValOrder()` adds the current order's own amount back when it is marked paid: `RemainingCredit(orders.customer_id) + IIF(orders.paid, lyOrderAmount, 0)`.", ""]
    # R8
    L += ["## R8. The order total, written seven times", "",
          "`subtotal = sum(unit_price * quantity)`; `discount = subtotal * discount% / 100`; `total = subtotal - discount + freight`. Each copy, verbatim:", "",
          "| # | Where | Freight | Source |", "|---|---|---|---|",
          "| 1 | `CalcMinOrdAmount()` (R4) | no | `SUM (unit_price * quantity) - (orders.discount * .01) * (unit_price * quantity) FOR order_id = tcOrderID` |",
          "| 2 | `CalcOrdTotal()` (dead) | no | same |",
          "| 3 | `RemainingCredit()` (R7) | yes | `SUM((b.unit_price * b.quantity) - (a.discount * .01) * (b.unit_price * b.quantity)) + a.freight` per unpaid order |",
          "| 4 | View `ORDER HISTORY` | yes | see below |",
          "| 5 | View `ORDERTOTAL` (feeds Top 25) | yes | see below |",
          "| 6 | Order entry screen | yes | `txtSubTotal` from the grid's `ncolumnsum` of `quantity * unit_price`, then the chain below |",
          "| 7 | Invoice report | yes | `vSubTotal` sums `quantity * MTON(unit_price)` per order; `vDisCount = iif(discount > 0, vSubTotal * (discount / 100), 0)`; total field `vSubTotal + freight - vDisCount` |", "",
          "View `ORDER HISTORY`:", "", fence(view_sql("ORDER HISTORY"), "sql"), "",
          "View `ORDERTOTAL`:", "", fence(view_sql("ORDERTOTAL"), "sql"), "",
          "The screen chain ([[../05-classes/orders.md]]):", "",
          fence(method(ORDERS_CLS, "txtSubTotal.ProgrammaticChange")), "", fence(method(ORDERS_CLS, "txtDiscount.ProgrammaticChange")), "",
          "The invoice variables ([[../06-reports/orders.md]]):", "",
          "| Variable | Value to store | Calculate | Reset |", "|---|---|---|---|"]
    for v in INVOICE["variables"]:
        L.append("| `%s` | `%s` | %s | %s |" % (v["name"], v["expr"], v["calculate"] or "nothing", v["reset"]))
    L += ["", "All seven agree on the arithmetic; they differ on freight (copies 1 and 2 leave it out, which is right for the minimum-order check and wrong for anything else) and on rounding, which none of them does. A rebuild implements it once, with freight as a parameter.", ""]
    # R9
    L += ["## R9. Prices and discounts are copied at the moment of choice", "",
          "Choosing a product on a line copies the product's current price onto the line; the line keeps that price if the product's price later changes ([[../04-forms/ordentry.md]]):", "",
          fence(method(ORDENTRY, "grdLineItems.grcProduct.cboProduct.InteractiveChange")), "",
          "Choosing a customer copies the customer's normal discount and address block onto the order; the clerk may then change the discount ([[../05-classes/orders.md]] `refreshcustomerinfo`). Copying tagged history lines into a new order carries their historical unit price ([[../04-forms/ordhist.md]]). Nothing stops ordering a discontinued product: the product list is `select product_name, product_id from products order by product_name`.", ""]
    # R10
    L += ["## R10. An order is editable until its deliver-by date passes", "", fence(method(ORDERS_CLS, "txtDeliver_By.Refresh")), "",
          "A new record is always editable; an existing one only while `deliver_by` is after today, and deletable under the same condition. The date itself must be today or later on entry, stricter than the DBC rule (R3):", "", fence(method(ORDERS_CLS, "txtDeliver_By.Valid")), ""]
    # R11
    L += ["## R11. Login", "", "`login.cmdOk.Click`; the `loginpicture` subclass the application shows calls it and then returns `employee_id + \",\" + thisform.GetUserLevel()`:", "", fence(method(LOGIN, "cmdOk.Click")), "",
          "The stored password must equal the typed one after trimming, case-sensitively, in plain text. The dialog returns `employee_id,user level`; the user level is what the menu gates on (R14). Under `DEBUGMODE` none of this runs ([[../05-classes/login.md]], [[../08-programs/tastrade.h.md]]). Changing a password requires the old one, a non-empty new one, and a matching confirmation ([[../04-forms/chngpswd.md]]).", ""]
    # R12
    L += ["## R12. What the sales reports call sales", "", fence(view_sql("SALES SUMMARY"), "sql"), "",
          "`SUM(unit_price)` per month: unit prices added up without quantity, discount, or freight. `SALES DETAIL` does the same per day. `TOP25CUST` sums `ORDERTOTAL` (R8 copy 5) per customer. **NOTE:** the three sales reports use two different definitions of a sale, and neither the reports nor the views say so ([[../06-reports/README.md]]).", ""]
    # R13
    L += ["## R13. Paid", "",
          "`orders.paid` has no default (new orders are unpaid). Marking an order paid excludes it from the credit calculation (R7). It is set from the order entry form's checkbox, which recomputes credit, or from the order history grid, which writes through and saves at once ([[../04-forms/ordhist.md]]):", "",
          fence(method(ORDHIST, "grdOrdHistory.Column5.chkPaid.Click")), "",
          "`ValOrder()` skips its credit and minimum checks when the paid flag is the only change or the history form is on top (R4), so paying never asks a question. **NOTE:** this save is outside any transaction.", ""]
    # R14
    cleanup = MAINMENU["cleanup_code"]
    L += ["## R14. User levels", "",
          "| Group | Description | Startup action |", "|---|---|---|"] + ["| %s | %s | %s |" % (g, d, ("`%s`" % a) if a else "") for g, d, a in P["levels"]] + ["",
          "Two things depend on the level. `tastrade.Do` runs the level's startup action after the menu (skipped under `DEBUGMODE`, [[../05-classes/main.md]]). The main menu's cleanup code removes pads and bars ([[../07-menus/main.md]]):", "", fence(cleanup), "",
          "`USER_APPDEV_LOC` and `USER_OPSMGR_LOC` are `\"APPLICATIONS DEVELOPER\"` and `\"OPERATIONS MANAGER\"` in `include/tastrade.h` and must equal the descriptions above upper-cased. **NOTE:** `ADMINBAR_LOC` is `\"Administration\"` but the popup is `_qx713dsus`, so the three `RELEASE BAR` lines do nothing useful; Login and Change Password stay for every level. **NOTE:** in the shipped build the level is always Applications Developer. No table, rule, or form checks the level.", ""]
    L += ["## What is not a rule", "",
          "- Inventory: `units_in_stock`, `units_on_order`, `reorder_level` are edited on the product form and read by nothing.",
          "- Sales regions on customers and employees: stored, never compared.",
          "- Discontinued products: flagged, still orderable, still listed.",
          "- Order notes: a memo nothing else reads.",
          "- Rounding: no copy of the total rounds; the currency fields hold four decimals and the report masks show two.", ""]
    return "\n".join(L)


if __name__ == "__main__":
    P = profile()
    with open(os.path.join(out_dir("02-domain"), "README.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(gen_domain(P))
    print("wrote 02-domain/README.md")
    with open(os.path.join(out_dir("09-business-logic"), "README.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(gen_rules(P))
    print("wrote 09-business-logic/README.md")
