"""Generate docs/04-forms/ordentry.md, ordhist.md and README.md for Tastrade.
Control tree, cursors, and method bodies come from the FoxBin2PRG twins via foxparse;
explanations and notes are hand-written."""
import os, re, sys, textwrap
sys.path.insert(0, os.environ.get("VFP_TOOLKIT_TOOLS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "vfp-documentation-toolkit", "tools")))
import foxparse as fp

ROOT = os.environ.get("TASTRADE_ROOT", os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))
OUT = os.path.join(ROOT, "docs", "04-forms")
os.makedirs(OUT, exist_ok=True)

def load(name):
    r = fp.parse_sc2(os.path.join(ROOT, "forms", name + ".sc2"))
    r["text"] = fp.read(os.path.join(ROOT, "forms", name + ".sc2"))
    r["members"] = re.findall(r"^\s*\*([mpa]):\s*(\S+)\s*(?:&&\s*(.*))?$", r["text"], re.M)
    return r

def body(r, method):
    for k in r["methods"]:
        if k.lower() == method.lower():
            return textwrap.dedent(r["methods"][k]).strip("\n")
    raise KeyError(method)

def fence(code): return "```foxpro\n" + code + "\n```"

def unq(v):
    v = (v or "").strip()
    return v[1:-1] if len(v) >= 2 and v[0] == v[-1] == '"' else v

def method_section(r, method, explain):
    L = ["#### `%s`" % method, ""]
    if explain: L += [explain, ""]
    L += [fence(body(r, method)), ""]
    return L

def members_table(r):
    L = []
    props = [(k, n, d) for k, n, d in r["members"] if k in ("p", "a")]
    meths = [(k, n, d) for k, n, d in r["members"] if k == "m"]
    if props:
        L += ["**Custom properties:**", "", "| Property | Description |", "|---|---|"]
        L += ["| `%s` | %s |" % (n, d or "") for k, n, d in props] + [""]
    if meths:
        L += ["**Custom methods:**", "", "| Method | Description |", "|---|---|"]
        L += ["| `%s` | %s |" % (n, d or "") for k, n, d in meths] + [""]
    return L

def de_table(r, notes):
    L = ["| Cursor | Alias | Source | Database | Order | Filter |", "|---|---|---|---|---|---|"]
    for c in r["cursors"]:
        L.append("| `%s` | `%s` | `%s` | `%s` | %s | %s |" % (c["object"], c["alias"], c["table"],
                 os.path.basename(c["database"]), ("`%s`" % c["order"]) if c["order"] else "", c["filter"] or ""))
    L.append("")
    L += notes
    return L

def control_rows(r, extra):
    """Depth-first control table from the parser, with hand-written role text per control."""
    L = ["| Container path | Class | Bound to / key properties | Role |", "|---|---|---|---|"]
    for c in r["controls"]:
        p = c["props"]
        bits = []
        if p.get("caption"): bits.append("caption %s" % p["caption"])
        if p.get("controlsource"): bits.append("→ `%s`" % unq(p["controlsource"]))
        if p.get("rowsource"): bits.append("rows `%s`" % unq(p["rowsource"])[:70] + ("…" if len(unq(p["rowsource"])) > 70 else ""))
        if p.get("recordsource"): bits.append("RecordSource `%s`" % unq(p["recordsource"]))
        if p.get("picture"): bits.append("picture `%s`" % unq(p["picture"]))
        if p.get("enabled") == ".F.": bits.append("disabled")
        if p.get("readonly") == ".T.": bits.append("read-only")
        cls = c["class"] + ("" if c["class"].lower() == c["baseclass"].lower() else " (%s)" % c["baseclass"])
        L.append("| `%s` | `%s` | %s | %s |" % (c["path"], cls, "; ".join(bits), extra.get(c["path"], extra.get(c["path"].lower(), ""))))
    L.append("")
    return L

# ================================================================= ordentry
def gen_ordentry():
    r = load("ordentry")
    L = ["# frmorderentry (ordentry.scx)", "",
         "| Source file | Type | Path |", "|---|---|---|",
         "| `ordentry.scx` | Form | `forms/ordentry.sc2` |", "",
         "**Purpose:** The order entry screen. Creates and edits an order header (customer, ship-to, "
         "shipper, dates, discount, freight, paid) and its line items in a grid, shows the customer's "
         "remaining credit as lines are added, and can open the customer's order history to copy items "
         "from a previous order.", "",
         "**Used by:**",
         "- The Orders menu ([[../07-menus/main.md]]): `oApp.DoForm(\"ordentry\")`, skipped while an instance "
         "is open (`SKIP FOR WEXIST(\"frmOrderEntry\")`), so at most one order entry form exists.",
         "- `USER_LEVEL.startup_action` for group 1, Customer Service Rep, is `oApp.DoForm(\"ordentry\")` "
         "([[../03-data-model/tables/user_level.md]]), inert in this build.",
         "- Opens [[custadd.md]] (`DO FORM custadd ... TO llAdded`) and [[ordhist.md]] "
         "(`oApp.DoForm(\"ordhist\", thisform)`), and the `findorder` picker ([[../05-classes/tsgen.md]]).", "",
         "**Related docs:** [[../05-classes/orders.md]] (`orderentry`, the class that defines most of the "
         "controls, the on-screen total, and the transactional `Save`), [[../05-classes/tsbase.md]] "
         "(`tsbaseform`, `tsifcombo`, `tsgrid`), [[../03-data-model/tables/orders.md]], "
         "[[../03-data-model/tables/order_line_items.md]], [[../03-data-model/README.md]] (`RemainingCredit()`, "
         "`ValOrder()`), [[../07-menus/ordentry.md]] (the Items menu pad this form activates), [[README.md]].", "",
         "This page documents what the `.scx` adds. Half the form, including every ship-to text box, the "
         "totals, `Save`, `Restore`, `AddNew`, and the navigation overrides, lives in the `orderentry` class "
         "and is documented in [[../05-classes/orders.md]]. Read both.", "",
         "## Form metadata", "",
         "- Base class / parent: `orderentry` of `..\\libs\\orders.vcx` → `tsbaseform` → `form`",
         "- Caption: \"Order Entry\" (inherited)",
         "- Modal: no. MDI child with the shared navigation toolbar (`ctoolbar = tstoolbar`, inherited)",
         "- Icon `..\\bitmaps\\orders.ico`; `HelpContextID = 11`; `AutoCenter = .F.` so the INI position wins",
         "- Data session: default (shared). The order history form it opens runs in its own session and "
         "switches into this one to insert lines.", ""]
    L += members_table(r)
    L += ["## DataEnvironment", ""]
    L += de_table(r, ["`InitialSelectedAlias = \"Orders\"`, `AutoCloseTables = .F.`. Three relations:", "",
        "| Parent | Child | Expression | Child order |", "|---|---|---|---|",
        "| `Orders` | `Shippers` | `shipper_id` | `shipper_id` |",
        "| `Orders` | `Order_Line_Items` | `order_id` | `order_id` |",
        "| `Order_Line_Items` | `Products` | `product_id` | `product_id` |", "",
        "The `Orders` → `Order_Line_Items` relation is what the grid's `LinkMaster`/`ChildOrder` uses, and "
        "the `Order_Line_Items` → `Products` relation is what makes `products.product_name` and "
        "`products.unit_price` follow the current line. Buffering is optimistic table buffering on every "
        "cursor, inherited from the form's `BufferMode = 2`. The form class's `Save` commits `Orders` and "
        "`Order_Line_Items` in one transaction. `AutoCloseTables = .F.` with `Destroy` doing its own "
        "`TABLEREVERT` and `SET RELATION TO` cleanup.", ""])
    L += ["## Controls (depth-first)", "",
          "Only the controls this form adds. The ship-to block, shipper combo, dates, discount, freight, "
          "totals, notes, and the off-screen `cmdFocusControl` come from the class; the form sets their "
          "`ControlSource`s (listed in [[../05-classes/orders.md]]) and gives `txtsubtotal`, `txtdiscount`, "
          "`txtfreight` the mask `99,999,999.99`.", ""]
    L += control_rows(r, {
        "cboCustomer_ID": "Incremental-search customer picker (`llimittolist = .F.` so a new name can be typed); enabled only for a new order",
        "chkPaid": "Toggles `orders.paid`; recomputes available credit",
        "cmdFind": "Opens the `findorder` picker and jumps to that order; enabled only for existing orders",
        "cmdHelp": "`HELP`",
        "cmdLastOrder": "Opens order history linked to this form; enabled only for a new order",
        "grdLineItems": "Line items; `cfieldtosum = quantity * unit_price` feeds the subtotal; `LinkMaster = Orders`, `ChildOrder = order_id`",
        "grdLineItems.grcExtension.grhExtension": "",
        "grdLineItems.grcExtension.Text1": "Column 4, unbound: `order_line_items.quantity * order_line_items.unit_price`, read-only grey",
        "grdLineItems.grcProduct.cboProduct": "Column 1's current control: product drop-down, `BoundColumn = 2` → `Order_line_items.product_id`; column is `Bound = .F.` and shows `products.product_name`",
        "grdLineItems.grcProduct.grhProduct": "",
        "grdLineItems.grcProduct.Text1": "",
        "grdLineItems.grcQuantity.grhQuantity": "",
        "grdLineItems.grcQuantity.Text1": "Column 2 → `Order_Line_Items.quantity`; `DynamicBackColor` grey when disabled",
        "grdLineItems.grcUnitPrice.grhUnitPrice": "",
        "grdLineItems.grcUnitPrice.Text1": "Column 3 → `Order_Line_Items.unit_price`, read-only; set by code when a product is picked",
        "Tslabel1": "\"Available Credit:\"",
        "tsLabelRightClick": "\"Right click on grid for menu\"; visible only when the grid is enabled",
        "txtAvailCredit": "Unbound, disabled; `RemainingCredit(customer_id)` from the DBC",
    })
    L += ["Grid column bindings, from the grid's definition:", "",
          "| Column | Name | ControlSource | Current control | Editable |", "|---|---|---|---|---|",
          "| 1 | `grcProduct` | `products.product_name` (unbound) | `cboProduct` | yes, via the combo |",
          "| 2 | `grcQuantity` | `Order_Line_Items.quantity` | text | yes |",
          "| 3 | `grcUnitPrice` | `Order_Line_Items.unit_price` | text | no |",
          "| 4 | `grcExtension` | `order_line_items.quantity * order_line_items.unit_price` (unbound) | text | no |", "",
          "### Events with code", ""]
    L += method_section(r, "cboCustomer_ID.Init", "Runs the search-combo `Init`, blanks the display, and reverts the buffer so that populating the combo does not count as a data change.")
    L += method_section(r, "cboCustomer_ID.Refresh", "A customer can only be chosen on a **new** order (record state 3 or 4). Existing orders show the customer read-only.")
    L += method_section(r, "cboCustomer_ID.InteractiveChange", "Picking a customer recomputes available credit through the DBC's `RemainingCredit()` and fills the ship-to block from the customer record (`refreshcustomerinfo` in the class).")
    L += method_section(r, "cboCustomer_ID.ProgrammaticChange", None)
    L += method_section(r, "cboCustomer_ID.Valid",
        "The add-a-customer path. If the user typed a name that matched nothing (`Value` empty, `DisplayValue` "
        "not), offer to add it; run [[custadd.md]] with the typed name and get back `.T.` on OK; then requery "
        "the combo, restore the typed name, position `customer`, and recompute credit and ship-to. Declining or "
        "cancelling returns `.F.` to keep focus. **NOTE:** the `CHR(12)` and `CHR(200)` guards filter two "
        "characters the combo can report as `DisplayValue` after keyboard navigation; undocumented magic values.")
    L += method_section(r, "cboCustomer_ID.Destroy", None)
    L += method_section(r, "chkPaid.InteractiveChange", "Paid orders no longer count against credit, so recompute it and refresh.")
    L += method_section(r, "chkPaid.Refresh", "**NOTE:** forces `lAllowEdits` on during every refresh so Save stays enabled for the paid flag, which overrides the delivery-date rule in `txtDeliver_By.Refresh` ([[../05-classes/orders.md]]) whenever this control refreshes after it.")
    L += method_section(r, "cmdFind.Click",
        "Runs the `findorder` picker; on a choice, calls `First()` to settle any pending edit, then seeks the "
        "order. The `#IF 0` block is a compiled-out earlier version that found by customer instead.")
    L += method_section(r, "cmdFind.Refresh", None)
    L += method_section(r, "cmdHelp.Click", None)
    L += method_section(r, "cmdLastOrder.Click",
        "Requires a customer, then counts that customer's orders in a second alias of `orders` "
        "(`USE ... AGAIN ALIAS orders_temp`), and if any exist locks this form down (not closable, no edits, "
        "no new, customer fixed) and opens [[ordhist.md]] passing `thisform`. The history form's `ClearLink` "
        "call undoes the lock-down when it closes. **NOTE:** a `USE ... AGAIN` and `COUNT FOR` over the whole "
        "orders table for a yes/no answer; the `cust_ord` index would do.")
    L += method_section(r, "cmdLastOrder.Refresh", None)
    L += method_section(r, "grdLineItems.Refresh",
        "After the base grid sums `quantity * unit_price`, pushes the sum into `txtSubTotal` (which cascades "
        "through the class's `ProgrammaticChange` chain to the total), recomputes available credit, and "
        "enables the grid and the right-click hint from `lAllowEdits`.")
    L += method_section(r, "grdLineItems.RightClick",
        "Builds a two-item shortcut popup (Add Item / Remove Item) at the mouse and routes the choice to "
        "`GridPop`. The `Items` menu pad offers the same two actions with Ctrl+Ins and Ctrl+Del.")
    L += method_section(r, "grdLineItems.grcProduct.cboProduct.InteractiveChange",
        "Choosing a product writes `product_id`, re-reads the row so the relation to `products` repositions, "
        "then copies `products.unit_price` into the line. This is where the historical unit price on a line "
        "comes from ([[../03-data-model/tables/order_line_items.md]]).")
    L += method_section(r, "grdLineItems.grcQuantity.Text1.LostFocus", "Leaving the quantity cell re-sums the grid, guarded against running during shutdown.")
    L += ["The four `RightClick` handlers on the column text boxes and the product combo all forward to "
          "`grdLineItems.RightClick`:", "", fence(body(r, "grdLineItems.grcProduct.cboProduct.RightClick")), "",
          "## Form methods", ""]
    L += method_section(r, "Init", "After the class `Init`, replaces the generic insert-trigger message with `INSORDER_LOC` (\"All orders must have a customer and a shipper.(Delivery Info)\"), the message shown when the RI insert trigger on `ORDERS` refuses a row.")
    L += method_section(r, "Load", None)
    L += method_section(r, "Activate", "Adds the Items menu pad ([[../07-menus/ordentry.md]]) each time the form becomes active.")
    L += method_section(r, "Deactivate", "Removes it again.")
    L += method_section(r, "Destroy", "Closes the product cursor, drops the relations, reverts any uncommitted line items, removes the pad.")
    L += method_section(r, "clearlink", "Called by the linked order history form when it closes: re-enables what `cmdLastOrder.Click` locked.")
    L += method_section(r, "getcustomerid", "The three getters exist for the order history form, which reads the current customer and order through them.")
    L += method_section(r, "getcustomername", None)
    L += method_section(r, "getordernumber", None)
    L += method_section(r, "gridadditem", "Deletes any product-less lines, appends a new line for this order, and puts the cursor in the product column.")
    L += method_section(r, "gridremoveitem", "Confirms and deletes the current line in the buffer; the delete is committed by `Save`.")
    L += method_section(r, "gridpop", None)
    L += ["## Tables read / written", "",
          "| Table | Access | How |", "|---|---|---|",
          "| `ORDERS` | both | DataEnvironment; header fields bound to controls; `Save` in the class |",
          "| `ORDER_LINE_ITEMS` | both | DataEnvironment; grid; `INSERT INTO` in `AddNew`, `APPEND BLANK` in `gridadditem`, `DELETE` in `gridremoveitem` |",
          "| `CUSTOMER` | read | DataEnvironment; combo row source cursor `cCustomerList`; `SEEK` after adding; `RemainingCredit()` reads it again |",
          "| `SHIPPERS` | read | DataEnvironment; combo row source cursor `cShipperList` |",
          "| `PRODUCTS` | read | DataEnvironment; combo row source cursor `cProducts`; `unit_price` copied to lines |",
          "| `SETUP` | write | indirectly, through the `newid()` defaults when a header is appended |", "",
          "## Inter-form navigation", "",
          "- **→ [[custadd.md]]** from `cboCustomer_ID.Valid` when a typed customer does not exist; modal, returns `.T.` on OK.",
          "- **→ [[ordhist.md]]** from `cmdLastOrder.Click`, passing `thisform`; the history form locks this form "
          "until it closes and can insert checked items into this form's `order_line_items` by switching data sessions.",
          "- **→ `findorder`** ([[../05-classes/tsgen.md]]) from `cmdFind.Click`.",
          "- **← Orders menu** and, in a non-debug build, the Customer Service Rep startup action.",
          "- **Items menu pad** (`menus\\ordentry.mpr`) is added on `Activate` and removed on `Deactivate`.", "",
          "## Notes", "",
          "- **Credit is recomputed on every grid refresh** by `RemainingCredit()`, which runs a `SELECT ... GROUP BY` over the customer's unpaid orders each time. Fine at 1,079 orders; a scaling concern.",
          "- **`chkPaid.Refresh` forces `lAllowEdits = .T.`**, fighting the delivery-date rule in the class. Which wins depends on refresh order.",
          "- **Undocumented magic values** `CHR(12)` and `CHR(200)` in `cboCustomer_ID.Valid`.",
          "- **`USE ... AGAIN` + `COUNT`** in `cmdLastOrder.Click` for an existence check.",
          "- **Menu pad per form** (`DO menus\\ordentry.mpr` on every `Activate`): the pad is redefined each activation.",
          "- **Hard-coded English** through `_LOC` constants; \"Right click on grid for menu\" is a literal caption.",
          "- **Direct table access**: `USE ORDERS IN 0 AGAIN ALIAS orders_temp` in `cmdLastOrder.Click`; everything else goes through the DataEnvironment.", ""]
    return "\n".join(L)

# ================================================================= ordhist
def gen_ordhist():
    r = load("ordhist")
    L = ["# frmordhistory (ordhist.scx)", "",
         "| Source file | Type | Path |", "|---|---|---|",
         "| `ordhist.scx` | Form | `forms/ordhist.sc2` |", "",
         "**Purpose:** A customer's order history: one grid of the customer's orders with totals and a "
         "Paid checkbox, one grid of the selected order's line items, and the customer's outstanding "
         "balance. Opened on its own it is a browser that can toggle Paid; opened from order entry it "
         "becomes a picker whose checked line items are copied into the order being entered.", "",
         "**Used by:**",
         "- The Orders menu ([[../07-menus/main.md]]): `oApp.DoForm(\"ordhist\")`, no skip condition, so "
         "several instances can be open; each gets a numbered name and caption.",
         "- [[ordentry.md]] `cmdLastOrder.Click`: `oApp.DoForm(\"ordhist\", thisform)`, one linked instance.",
         "- Opens the `findcustomer` picker ([[../05-classes/tsgen.md]]).", "",
         "**Related docs:** [[../05-classes/tsbase.md]] (`tsbaseform`, `tsgrid`), [[../05-classes/tsgen.md]] "
         "(`application.AddInstance`/`RemoveInstance`), [[../03-data-model/README.md]] (views `ORDER HISTORY` "
         "and `ORDER HISTORY LINE ITEMS`, which are this form's data), [[../03-data-model/tables/orders.md]], "
         "[[ordentry.md]], [[README.md]].", "",
         "Despite the `orderentry` class description in [[../05-classes/orders.md]], this form extends "
         "`tsbaseform` directly and shares no code with the order entry form beyond the base.", "",
         "## Form metadata", "",
         "- Base class / parent: `tsbaseform` of `..\\libs\\tsbase.vcx` → `form`",
         "- Caption: \"Order History\", suffixed at run time with `:n` (instance number) or ` for <customer>` (linked)",
         "- Modal: no. MDI child with the navigation toolbar, but `lallownew`, `lallowedits`, `lallowdelete` all `.F.`, so the toolbar's New/Save/Restore are disabled and navigation moves through **customers**",
         "- `DataSession = 2` (private); `AutoCenter = .F.`; `restorewindowpos`/`savewindowpos` overridden to do nothing", ""]
    L += members_table(r)
    L += ["## DataEnvironment", ""]
    L += de_table(r, ["`InitialSelectedAlias = \"customer\"`, so the navigation toolbar steps through customers and "
        "each step refreshes the two grids. Two of the six cursors are **parameterised views** from the DBC:", "",
        "| View | Parameter | Supplies |", "|---|---|---|",
        "| `ORDER HISTORY` (alias `history`) | `?customer.customer_id` | the customer's orders with `ord_total` computed in SQL and `paid` |",
        "| `ORDER HISTORY LINE ITEMS` (alias `citems`) | `?orders.order_id` | the selected order's lines with `extension` and a literal `.F.` first column, `exp_1`, used as the Tag checkbox |", "",
        "Both are requeried by code (`REQUERY(\"history\")`, `REQUERY(\"citems\")`) after the parent alias is "
        "positioned. One relation, `products` → `order_line_items` on `product_id`, is defined but the grids "
        "read the views, not the base tables. `BeforeOpenTables` sets `TALK OFF`, `EXCLUSIVE OFF`, `DELETED ON` "
        "and `SET DATABASE TO tastrade` because the private session starts with no current database.", "",
        fence(body(r, "dataenvironment.BeforeOpenTables") if "dataenvironment.BeforeOpenTables" in r["methods"] else "SET TALK OFF\nSET EXCLUSIVE OFF\nSET DELETED ON\nSET DATABASE TO tastrade"), ""])
    L += ["## Controls (depth-first)", ""]
    L += control_rows(r, {
        "cmdAddToCurrentOrder": "Copies checked lines into the linked order entry form; enabled only when linked",
        "cmdCancel": "\"Close\"; offers to discard checked items first",
        "cmdFind": "Opens `findcustomer` and repositions; enabled only when not linked",
        "grdLineItems": "Lines of the selected order from view `citems`; `cfieldtosum = extension`",
        "grdLineItems.grcTag.chkItemTag": "Column 1's current control: the Tag checkbox bound to the view's literal `exp_1` column; enabled only when linked",
        "grdLineItems.grcTag.grhTag": "", "grdLineItems.grcTag.Text1": "",
        "grdLineItems.grcProduct.grhProduct": "", "grdLineItems.grcProduct.Text1": "→ `citems.product_name`",
        "grdLineItems.grcQuantity.grhQuantity": "", "grdLineItems.grcQuantity.Text1": "→ `citems.quantity`",
        "grdLineItems.grcUnitPrice.grhUnitPrice": "", "grdLineItems.grcUnitPrice.Text1": "→ `citems.unit_price`",
        "grdLineItems.grcExtension.grhExtension": "", "grdLineItems.grcExtension.Text1": "→ `citems.extension`",
        "grdOrdHistory": "The customer's orders from view `history`; `HighlightRow`, `RecordMark`",
        "grdOrdHistory.Column1.Header1": "\"Order ID\"", "grdOrdHistory.Column1.Text1": "→ `history.order_id`",
        "grdOrdHistory.Column2.Header1": "\"Order date\"", "grdOrdHistory.Column2.Text1": "→ `history.order_date`",
        "grdOrdHistory.Column3.Header1": "\"Deliver On\"", "grdOrdHistory.Column3.Text1": "→ `history.deliver_by`",
        "grdOrdHistory.Column4.Header1": "\"Order Amt\"", "grdOrdHistory.Column4.Text1": "→ `history.ord_total` (computed in the view, with freight)",
        "grdOrdHistory.Column5.Header1": "\"Paid\"", "grdOrdHistory.Column5.Text1": "",
        "grdOrdHistory.Column5.chkPaid": "Column 5's current control → `history.paid`; `Click` writes through to `orders.paid` and saves",
        "Tslabel1": "\"Orders For:\"", "Tslabel2": "\"Current Balance:\"",
        "txtBalance": "Unbound, disabled; sum of unpaid `ord_total`",
        "txtCustID": "→ `customer.customer_id`, disabled",
        "txtCustomer": "→ `customer.company_name`, disabled",
    })
    L += ["### Events with code", ""]
    L += method_section(r, "grdOrdHistory.AfterRowColChange",
        "Moving to another order: if any line items are tagged, offer to discard them (No returns to the previous "
        "order); then position `orders` on the chosen order, requery the line-item view, refresh the lower grid, "
        "and remember the row. Column changes within the same row are ignored via `nOrderRec`.")
    L += method_section(r, "grdOrdHistory.Column5.chkPaid.Click",
        "The one write this form performs: positions `orders` on the history row, replaces `paid`, and calls the "
        "base `Save` (`TABLEUPDATE`), then recomputes the balance. This is the path the DBC rule `ValOrder()` "
        "special-cases: when `paid` is the only changed field, or the active form is `frmordhistory`, the credit "
        "and minimum checks are skipped ([[../03-data-model/README.md]]).")
    L += method_section(r, "grdLineItems.Refresh", "Always enabled so the user can scroll; only the Tag checkbox follows the linked state.")
    L += method_section(r, "cmdAddToCurrentOrder.Click",
        "The cross-session copy. For every tagged line in `citems`, switch to the order entry form's data "
        "session, `INSERT INTO order_line_items` a row for the order being entered with the historical "
        "`unit_price` and `quantity`, switch back. Then revert the tags, delete any blank line the order entry "
        "form had appended, unlock that form through `ClearLink`, hide, refresh it, and release. "
        "**NOTE:** `lcProductID`, `lnUnitPrice`, `lnQuantity` are not declared `LOCAL`. **NOTE:** copies the "
        "old unit price, not the current product price, so a re-ordered item is priced as it was.")
    L += method_section(r, "cmdCancel.Click", "Close with a discard prompt if any line is tagged. `TSBaseForm::DataChanged()` on the `cItems` view detects the tag edits, which is why the form's own `datachanged` returns `.F.` unconditionally elsewhere.")
    L += method_section(r, "cmdFind.Click", "Same discard prompt, then the `findcustomer` picker and a `SEEK` on `customer`; `refreshform` requeries both views.")
    L += ["## Form methods", ""]
    L += method_section(r, "Init",
        "Two modes. **Stand-alone** (no parameter): register with `oApp.AddInstance`, suffix the name and caption "
        "with the instance number so several can coexist, then look for an order entry or customer form on top "
        "and start on its customer (reading the customer form's `customer_id` by temporarily switching to its "
        "data session). **Linked** (order entry form passed): keep the name, caption \" for <customer>\", enable "
        "the Add button, start on that form's customer via `GetCustomerID()`. **NOTE:** `TYPE(\"toOrdEntryForm \")` "
        "has a trailing space inside the string; VFP tolerates it. **NOTE:** the loop assigns `toOrdEntryForm` "
        "(a parameter) as a side channel for the found form.")
    L += method_section(r, "refreshform",
        "Overrides the base `RefreshForm` (which just calls `Refresh`): disables the Paid checkbox and enables "
        "Find only when not linked, requeries the orders view for the current customer, positions `orders` on "
        "the first order, requeries the line items, refreshes, recomputes the balance, and leaves `customer` "
        "selected for the toolbar.")
    L += method_section(r, "calcbalance", "Sum of `ord_total` over unpaid rows of the `history` view, restoring the record pointer.")
    L += method_section(r, "datachanged", "**NOTE:** reverts the line-item view and reports no change, so the base form's navigation and `QueryUnload` never prompt. The discard prompt is implemented separately in three places (`cmdCancel`, `cmdFind`, `AfterRowColChange`).")
    L += method_section(r, "QueryUnload", "Always closable; combined with `datachanged` above, the toolbar's Close never prompts.")
    L += method_section(r, "Activate", None)
    L += method_section(r, "Destroy", "Unlocks the linked order entry form, removes the menu entry under the original caption, deregisters the instance, reverts the view.")
    L += method_section(r, "restorewindowpos", "Empty overrides: instance staggering is done by `AddInstance`, and the INI position is not used.")
    L += method_section(r, "savewindowpos", None)
    L += ["## Tables read / written", "",
          "| Table / view | Access | How |", "|---|---|---|",
          "| `CUSTOMER` | read | DataEnvironment; the navigation alias; `SEEK` by ID |",
          "| view `ORDER HISTORY` → `history` | read | requeried per customer; drives the top grid and the balance |",
          "| view `ORDER HISTORY LINE ITEMS` → `citems` | read (+ tag edits reverted) | requeried per order; `exp_1` edited in the buffer as the Tag, then `TABLEREVERT` |",
          "| `ORDERS` | write (`paid` only) | `chkPaid.Click` via `Save` |",
          "| `ORDER_LINE_ITEMS` | write, in **another form's session** | `cmdAddToCurrentOrder.Click` `INSERT INTO` under the order entry form's `DataSessionID` |",
          "| `PRODUCTS` | read | DataEnvironment relation; not referenced by the grids |", "",
          "## Inter-form navigation", "",
          "- **← [[ordentry.md]]** passes itself in; this form calls back `GetCustomerID()`, `GetCustomerName()`, `ClearLink()`, `RefreshForm()`, and writes into its data session.",
          "- **← Orders menu**, stand-alone; picks up the customer from whichever of `frmorderentry` or `frmcustomers` is on top.",
          "- **→ `findcustomer`** from `cmdFind.Click`.",
          "- **Multiple instances** by name suffix, tracked in `oApp.aInstances`.", "",
          "## Notes", "",
          "- **Cross-session write.** Inserting into another form's buffered cursor by `SET DATASESSION` is the "
          "most fragile technique in the application and the reason the two forms lock each other.",
          "- **Toggling Paid saves immediately**, outside any transaction, and bypasses the credit rules by design of `ValOrder()`.",
          "- **The tag column is a view expression** (`SELECT .F., ...`), edited in the buffer and reverted; a "
          "trick that only works because the view is never sent updates.",
          "- **Three copies of the discard prompt** and a `datachanged` that lies to the base class.",
          "- **Undeclared variables** in `cmdAddToCurrentOrder.Click`.",
          "- **Balance and order total come from the views**, so this form agrees with `RemainingCredit()` and "
          "disagrees with the sales reports ([[../03-data-model/README.md]]).", ""]
    return "\n".join(L)

def gen_readme():
    forms = [("ordentry", "frmorderentry", "orderentry (orders.vcx)", "Order entry", "[[ordentry.md]]"),
             ("ordhist", "frmordhistory", "tsbaseform", "Order history and item copy", "[[ordhist.md]]"),
             ("customer", "frmcustomers", "tsmaintform", "Customer maintenance", "pending"),
             ("custadd", "frmaddcustomer", "tsbaseform", "Add a customer from order entry", "pending"),
             ("employee", "frmemployee", "tsmaintform", "Employee maintenance", "pending"),
             ("product", "frmproducts", "tsmaintform", "Product maintenance", "pending"),
             ("supplier", "frmsuppliers", "tsmaintform", "Supplier maintenance", "pending"),
             ("category", "frmcategory", "tsmaintform", "Category maintenance", "pending"),
             ("shipper", "frmshippers", "tsmaintform", "Shipper maintenance", "pending"),
             ("chngpswd", "frmchangepassword", "tsbaseform", "Change password", "pending"),
             ("reports", "frmreports", "tsbaseform", "Report picker", "pending"),
             ("getinv", "form1", "form", "Invoice date-range dialog (run by orders.frx)", "pending"),
             ("gettitle", "frmgettitle", "form", "Employee title dialog (run by listempl.frx)", "pending"),
             ("rebuild", "frmdatabaseutils", "tsbaseform", "Database utilities (reindex)", "pending"),
             ("behindsc", "frmbehindsc", "tsbaseform", "Behind the Scenes", "pending"),
             ("casestdy", "frmcasestudy", "tstextform", "Case study viewer", "pending"),
             ("viewcode", "frmviewcode", "tstextform", "View code", "pending")]
    L = ["# Forms", "", "Seventeen forms in `forms/*.scx`. Each is documented from its FoxBin2PRG twin with the "
         "control tree, DataEnvironment, and every method body. What a form inherits is in [[../05-classes/README.md]].", "",
         "| File | Form class | Extends | Role | Doc |", "|---|---|---|---|---|"]
    L += ["| `forms/%s.scx` | `%s` | `%s` | %s | %s |" % f for f in forms]
    L += ["", "Two forms are plain VFP forms with no framework base (`getinv`, `gettitle`); they are report "
          "parameter dialogs run from report data environments, see [[../03-data-model/README.md]].", ""]
    return "\n".join(L)

for fn, gen in (("ordentry.md", gen_ordentry), ("ordhist.md", gen_ordhist), ("README.md", gen_readme)):
    with open(os.path.join(OUT, fn), "w", encoding="utf-8", newline="\n") as f:
        f.write(gen())
    print("wrote", fn)
