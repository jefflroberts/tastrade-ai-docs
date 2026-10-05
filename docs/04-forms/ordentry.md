# frmorderentry (ordentry.scx)

| Source file | Type | Path |
|---|---|---|
| `ordentry.scx` | Form | `forms/ordentry.sc2` |

**Purpose:** The order entry screen. Creates and edits an order header (customer, ship-to, shipper, dates, discount, freight, paid) and its line items in a grid, shows the customer's remaining credit as lines are added, and can open the customer's order history to copy items from a previous order.

**Used by:**
- The Orders menu ([[../07-menus/main.md]]): `oApp.DoForm("ordentry")`, skipped while an instance is open (`SKIP FOR WEXIST("frmOrderEntry")`), so at most one order entry form exists.
- `USER_LEVEL.startup_action` for group 1, Customer Service Rep, is `oApp.DoForm("ordentry")` ([[../03-data-model/tables/user_level.md]]), inert in this build.
- Opens [[custadd.md]] (`DO FORM custadd ... TO llAdded`) and [[ordhist.md]] (`oApp.DoForm("ordhist", thisform)`), and the `findorder` picker ([[../05-classes/tsgen.md]]).

**Related docs:** [[../05-classes/orders.md]] (`orderentry`, the class that defines most of the controls, the on-screen total, and the transactional `Save`), [[../05-classes/tsbase.md]] (`tsbaseform`, `tsifcombo`, `tsgrid`), [[../03-data-model/tables/orders.md]], [[../03-data-model/tables/order_line_items.md]], [[../03-data-model/README.md]] (`RemainingCredit()`, `ValOrder()`), [[../07-menus/ordentry.md]] (the Items menu pad this form activates), [[README.md]].

This page documents what the `.scx` adds. Half the form, including every ship-to text box, the totals, `Save`, `Restore`, `AddNew`, and the navigation overrides, lives in the `orderentry` class and is documented in [[../05-classes/orders.md]]. Read both.

## Form metadata

- Base class / parent: `orderentry` of `..\libs\orders.vcx` → `tsbaseform` → `form`
- Caption: "Order Entry" (inherited)
- Modal: no. MDI child with the shared navigation toolbar (`ctoolbar = tstoolbar`, inherited)
- Icon `..\bitmaps\orders.ico`; `HelpContextID = 11`; `AutoCenter = .F.` so the INI position wins
- Data session: default (shared). The order history form it opens runs in its own session and switches into this one to insert lines.

**Custom methods:**

| Method | Description |
|---|---|
| `clearlink` | Resets the environment when the Order History form to which this form is "linked" is being destroyed. |
| `getcustomerid` | Returns the customer id for the current order. |
| `getcustomername` | Returns the customer name for the current order. |
| `getordernumber` | Returns the order number for the current order. |
| `gridadditem` | Adds items to the grid. |
| `gridpop` | Handles the popup selection made when right clicking in the grid. |
| `gridremoveitem` | Removes items from the grid. |

## DataEnvironment

| Cursor | Alias | Source | Database | Order | Filter |
|---|---|---|---|---|---|
| `Cursor1` | `Orders` | `Orders` | `tastrade.dbc` |  |  |
| `Cursor2` | `Customer` | `Customer` | `tastrade.dbc` |  |  |
| `Cursor3` | `Shippers` | `Shippers` | `tastrade.dbc` |  |  |
| `Cursor4` | `Order_Line_Items` | `Order_Line_Items` | `tastrade.dbc` |  |  |
| `Cursor5` | `Products` | `Products` | `tastrade.dbc` |  |  |

`InitialSelectedAlias = "Orders"`, `AutoCloseTables = .F.`. Three relations:

| Parent | Child | Expression | Child order |
|---|---|---|---|
| `Orders` | `Shippers` | `shipper_id` | `shipper_id` |
| `Orders` | `Order_Line_Items` | `order_id` | `order_id` |
| `Order_Line_Items` | `Products` | `product_id` | `product_id` |

The `Orders` → `Order_Line_Items` relation is what the grid's `LinkMaster`/`ChildOrder` uses, and the `Order_Line_Items` → `Products` relation is what makes `products.product_name` and `products.unit_price` follow the current line. Buffering is optimistic table buffering on every cursor, inherited from the form's `BufferMode = 2`. The form class's `Save` commits `Orders` and `Order_Line_Items` in one transaction. `AutoCloseTables = .F.` with `Destroy` doing its own `TABLEREVERT` and `SET RELATION TO` cleanup.

## Controls (depth-first)

Only the controls this form adds. The ship-to block, shipper combo, dates, discount, freight, totals, notes, and the off-screen `cmdFocusControl` come from the class; the form sets their `ControlSource`s (listed in [[../05-classes/orders.md]]) and gives `txtsubtotal`, `txtdiscount`, `txtfreight` the mask `99,999,999.99`.

| Container path | Class | Bound to / key properties | Role |
|---|---|---|---|
| `cboCustomer_ID` | `tsifcombo (combobox)` | → `Orders.customer_id`; rows `select company_name, customer_id from customer order by company_name i`…; disabled | Incremental-search customer picker (`llimittolist = .F.` so a new name can be typed); enabled only for a new order |
| `chkPaid` | `tscheckbox (checkbox)` | caption "Paid"; → `Orders.paid` | Toggles `orders.paid`; recomputes available credit |
| `cmdFind` | `tscommandbutton (commandbutton)` | caption ""; picture `..\bitmaps\locate.bmp` | Opens the `findorder` picker and jumps to that order; enabled only for existing orders |
| `cmdHelp` | `tscommandbutton (commandbutton)` | caption "Hel\<p" | `HELP` |
| `cmdLastOrder` | `tscommandbutton (commandbutton)` | caption "\<Last Order" | Opens order history linked to this form; enabled only for a new order |
| `grdLineItems` | `tsgrid (grid)` | RecordSource `Order_Line_Items` | Line items; `cfieldtosum = quantity * unit_price` feeds the subtotal; `LinkMaster = Orders`, `ChildOrder = order_id` |
| `grdLineItems.grcExtension.grhExtension` | `header (combobox)` | caption "Extension" |  |
| `grdLineItems.grcExtension.Text1` | `textbox (combobox)` | disabled; read-only | Column 4, unbound: `order_line_items.quantity * order_line_items.unit_price`, read-only grey |
| `grdLineItems.grcProduct.cboProduct` | `tscombobox (combobox)` | → `Order_line_items.product_id`; rows `select product_name, product_id from products order by product_name in`… | Column 1's current control: product drop-down, `BoundColumn = 2` → `Order_line_items.product_id`; column is `Bound = .F.` and shows `products.product_name` |
| `grdLineItems.grcProduct.grhProduct` | `header (label)` | caption "Product" |  |
| `grdLineItems.grcProduct.Text1` | `textbox (label)` |  |  |
| `grdLineItems.grcQuantity.grhQuantity` | `header (label)` | caption "Quantity" |  |
| `grdLineItems.grcQuantity.Text1` | `textbox (label)` |  | Column 2 → `Order_Line_Items.quantity`; `DynamicBackColor` grey when disabled |
| `grdLineItems.grcUnitPrice.grhUnitPrice` | `header (label)` | caption "Unit Price" |  |
| `grdLineItems.grcUnitPrice.Text1` | `textbox (label)` | disabled; read-only | Column 3 → `Order_Line_Items.unit_price`, read-only; set by code when a product is picked |
| `Tslabel1` | `tslabel (label)` | caption "Available Credit:" | "Available Credit:" |
| `tsLabelRightClick` | `tslabel (label)` | caption "Right click on grid for menu " | "Right click on grid for menu"; visible only when the grid is enabled |
| `txtAvailCredit` | `ordtextbox (textbox)` | disabled | Unbound, disabled; `RemainingCredit(customer_id)` from the DBC |

Grid column bindings, from the grid's definition:

| Column | Name | ControlSource | Current control | Editable |
|---|---|---|---|---|
| 1 | `grcProduct` | `products.product_name` (unbound) | `cboProduct` | yes, via the combo |
| 2 | `grcQuantity` | `Order_Line_Items.quantity` | text | yes |
| 3 | `grcUnitPrice` | `Order_Line_Items.unit_price` | text | no |
| 4 | `grcExtension` | `order_line_items.quantity * order_line_items.unit_price` (unbound) | text | no |

### Events with code

#### `cboCustomer_ID.Init`

Runs the search-combo `Init`, blanks the display, and reverts the buffer so that populating the combo does not count as a data change.

```foxpro
tsifCombo::Init
THIS.DisplayValue = ""
=TABLEREVERT(.T.)		&& prevent from thinking data has changed
```

#### `cboCustomer_ID.Refresh`

A customer can only be chosen on a **new** order (record state 3 or 4). Existing orders show the customer read-only.

```foxpro
*-- Only allow change of customer if we're adding a new record.
this.Enabled = ("3" $ GETFLDSTATE(-1, "orders") OR "4" $ GETFLDSTATE(-1, "orders"))
tsifCombo::Refresh()
```

#### `cboCustomer_ID.InteractiveChange`

Picking a customer recomputes available credit through the DBC's `RemainingCredit()` and fills the ship-to block from the customer record (`refreshcustomerinfo` in the class).

```foxpro
tsifCombo::InteractiveChange()
THISFORM.txtAvailCredit.Value = RemainingCredit(THIS.Value)
thisform.RefreshCustomerInfo()
```

#### `cboCustomer_ID.ProgrammaticChange`

```foxpro
tsifCombo::ProgrammaticChange()
THISFORM.txtAvailCredit.Value = RemainingCredit(THIS.Value)
thisform.RefreshCustomerInfo()
```

#### `cboCustomer_ID.Valid`

The add-a-customer path. If the user typed a name that matched nothing (`Value` empty, `DisplayValue` not), offer to add it; run [[custadd.md]] with the typed name and get back `.T.` on OK; then requery the combo, restore the typed name, position `customer`, and recompute credit and ship-to. Declining or cancelling returns `.F.` to keep focus. **NOTE:** the `CHR(12)` and `CHR(200)` guards filter two characters the combo can report as `DisplayValue` after keyboard navigation; undocumented magic values.

```foxpro
LOCAL llAdded, ;
      lcDisplayValue

IF tsifCombo::Valid() AND this.Enabled
  this.Refresh()
  IF EMPTY(this.Value) AND !EMPTY(this.DisplayValue) AND;
*-- ... 26 more lines of Microsoft's Tastrade source omitted; see `cboCustomer_ID.Valid` in your own copy of Tastrade.
```

#### `cboCustomer_ID.Destroy`

```foxpro
IF USED("cCustomerList")
  USE IN cCustomerList
ENDIF
```

#### `chkPaid.InteractiveChange`

Paid orders no longer count against credit, so recompute it and refresh.

```foxpro
THISFORM.txtAvailCredit.Value = RemainingCredit(THISFORM.cboCustomer_ID.Value)
THISFORM.RefreshForm
```

#### `chkPaid.Refresh`

**NOTE:** forces `lAllowEdits` on during every refresh so Save stays enabled for the paid flag, which overrides the delivery-date rule in `txtDeliver_By.Refresh` ([[../05-classes/orders.md]]) whenever this control refreshes after it.

```foxpro
thisform.lAllowEdits = .T.	&& make sure Save is active
```

#### `cmdFind.Click`

Runs the `findorder` picker; on a choice, calls `First()` to settle any pending edit, then seeks the order. The `#IF 0` block is a compiled-out earlier version that found by customer instead.

```foxpro
LOCAL lcCustomer_id, lcOrder_ID, liRecno

lcOrder_ID = oApp.DoFormRetVal("findOrder")
IF !EMPTY(lcOrder_id) AND !ISNULL(lcOrder_id)
	liRecno = RECNO("orders")
	THISFORM.lockscreen = .T.
*-- ... 17 more lines of Microsoft's Tastrade source omitted; see `cmdFind.Click` in your own copy of Tastrade.
```

#### `cmdFind.Refresh`

```foxpro
this.Enabled = !("3" $ GETFLDSTATE(-1, "orders") OR "4" $ GETFLDSTATE(-1, "orders"))
```

#### `cmdHelp.Click`

```foxpro
HELP
```

#### `cmdLastOrder.Click`

Requires a customer, then counts that customer's orders in a second alias of `orders` (`USE ... AGAIN ALIAS orders_temp`), and if any exist locks this form down (not closable, no edits, no new, customer fixed) and opens [[ordhist.md]] passing `thisform`. The history form's `ClearLink` call undoes the lock-down when it closes. **NOTE:** a `USE ... AGAIN` and `COUNT FOR` over the whole orders table for a yes/no answer; the `cust_ord` index would do.

```foxpro
LOCAL lcCustomerID, ;
      lnOldArea

IF EMPTY(thisform.cboCustomer_ID.Value) OR ;
    EMPTY(thisform.cboCustomer_ID.DisplayValue)
  =MESSAGEBOX(SELCUSTFIRST_LOC, ;
*-- ... 28 more lines of Microsoft's Tastrade source omitted; see `cmdLastOrder.Click` in your own copy of Tastrade.
```

#### `cmdLastOrder.Refresh`

```foxpro
*-- Only allow access to last order if we're adding a new record.
this.Enabled = ("3" $ GETFLDSTATE(-1, "orders") OR ;
      "4" $ GETFLDSTATE(-1, "orders"))
```

#### `grdLineItems.Refresh`

After the base grid sums `quantity * unit_price`, pushes the sum into `txtSubTotal` (which cascades through the class's `ProgrammaticChange` chain to the total), recomputes available credit, and enables the grid and the right-click hint from `lAllowEdits`.

```foxpro
tsGrid::Refresh()
thisform.txtSubTotal.Value = this.nColumnSum
thisform.txtAvailCredit.Value = RemainingCredit(orders.customer_id)
this.Enabled = thisform.lAllowEdits
THISFORM.tsLabelRightClick.Visible = this.Enabled	&& only show "Right click" message if the user can use it
```

#### `grdLineItems.RightClick`

Builds a two-item shortcut popup (Add Item / Remove Item) at the mouse and routes the choice to `GridPop`. The `Items` menu pad offers the same two actions with Ctrl+Ins and Ctrl+Del.

```foxpro
SET SHADOW ON

DEFINE POPUP GridPopup ;
  FROM MROW(), MCOL() ;
  MARGIN ;
  SHORTCUT		&& add shadow (jd 06/20/96)
*-- ... 7 more lines of Microsoft's Tastrade source omitted; see `grdLineItems.RightClick` in your own copy of Tastrade.
```

#### `grdLineItems.grcProduct.cboProduct.InteractiveChange`

Choosing a product writes `product_id`, re-reads the row so the relation to `products` repositions, then copies `products.unit_price` into the line. This is where the historical unit price on a line comes from ([[../03-data-model/tables/order_line_items.md]]).

```foxpro
*-- Force relation to product table to be updated  
REPLACE order_line_items.product_id WITH this.Value
GO recno() IN order_line_items
REPLACE order_line_items.unit_price WITH products.unit_price
thisform.grdLineItems.Refresh()
```

#### `grdLineItems.grcQuantity.Text1.LostFocus`

Leaving the quantity cell re-sums the grid, guarded against running during shutdown.

```foxpro
IF TYPE("oApp") == 'O' AND !ISNULL(oApp) AND !oApp.lQuitting
	thisform.grdLineItems.Refresh()
ENDIF
```

The four `RightClick` handlers on the column text boxes and the product combo all forward to `grdLineItems.RightClick`:

```foxpro
this.Parent.Parent.RightClick()
```

## Form methods

#### `Init`

After the class `Init`, replaces the generic insert-trigger message with `INSORDER_LOC` ("All orders must have a customer and a shipper.(Delivery Info)"), the message shown when the RI insert trigger on `ORDERS` refuses a row.

```foxpro
OrderEntry::Init()
*-- Load the error message array with the appropriate error message if a
*-- trigger fails
this.aErrorMsg[INSERTTRIG] = INSORDER_LOC
thisform.RefreshForm()
```

#### `Load`

```foxpro
*-- (c) Microsoft Corporation 1995
OrderEntry::Load()
*-DO menus\ordentry.mpr
```

#### `Activate`

Adds the Items menu pad ([[../07-menus/ordentry.md]]) each time the form becomes active.

```foxpro
*-- (c) Microsoft Corporation 1995
OrderEntry::Activate()
DO menus\ordentry.mpr
```

#### `Deactivate`

Removes it again.

```foxpro
OrderEntry::Deactivate()
RELEASE PAD orderentry OF _msysmenu
```

#### `Destroy`

Closes the product cursor, drops the relations, reverts any uncommitted line items, removes the pad.

```foxpro
Orderentry::Destroy()

IF USED("cProducts")
  USE IN cProducts
ENDIF

*-- ... 12 more lines of Microsoft's Tastrade source omitted; see `Destroy` in your own copy of Tastrade.
```

#### `clearlink`

Called by the linked order history form when it closes: re-enables what `cmdLastOrder.Click` locked.

```foxpro
*-- Called when the link between a customer in Order Entry
*-- and all past orders is being cleared
thisform.cboCustomer_ID.Enabled = .T.
thisform.cmdLastOrder.Enabled = .T.
thisform.Closable = .T.
thisform.lAllowEdits = .T.
thisform.lAllowNew = .T.
```

#### `getcustomerid`

The three getters exist for the order history form, which reads the current customer and order through them.

```foxpro
*-- Returns the cusomter ID for the current order
RETURN thisform.cboCustomer_ID.Value
```

#### `getcustomername`

```foxpro
*-- Returns the customer name for the current order
RETURN thisform.cboCustomer_id.DisplayValue
```

#### `getordernumber`

```foxpro
*-- Returns the current order number
RETURN RIGHT(thisform.txtOrder_Number.Value,6)
```

#### `gridadditem`

Deletes any product-less lines, appends a new line for this order, and puts the cursor in the product column.

```foxpro
SELECT Order_Line_Items
*-- Delete any empty line items
DELETE FOR EMPTY(product_id)

APPEND BLANK
REPLACE order_id WITH orders.order_id
*-- ... 4 more lines of Microsoft's Tastrade source omitted; see `gridadditem` in your own copy of Tastrade.
```

#### `gridremoveitem`

Confirms and deletes the current line in the buffer; the delete is committed by `Save`.

```foxpro
IF MessageBox(DELETEREC_LOC, ;
              MB_ICONQUESTION + MB_YESNO, ;
              DELETEWARN_LOC) = IDNO
  RETURN
ENDIF

DELETE IN Order_Line_Items
thisform.grdLineItems.Refresh()
```

#### `gridpop`

```foxpro
LPARAMETERS tnBar

DO CASE
  CASE tnBar = 1
    thisform.GridAddItem()
  CASE tnBar = 2
*-- ... 4 more lines of Microsoft's Tastrade source omitted; see `gridpop` in your own copy of Tastrade.
```

## Tables read / written

| Table | Access | How |
|---|---|---|
| `ORDERS` | both | DataEnvironment; header fields bound to controls; `Save` in the class |
| `ORDER_LINE_ITEMS` | both | DataEnvironment; grid; `INSERT INTO` in `AddNew`, `APPEND BLANK` in `gridadditem`, `DELETE` in `gridremoveitem` |
| `CUSTOMER` | read | DataEnvironment; combo row source cursor `cCustomerList`; `SEEK` after adding; `RemainingCredit()` reads it again |
| `SHIPPERS` | read | DataEnvironment; combo row source cursor `cShipperList` |
| `PRODUCTS` | read | DataEnvironment; combo row source cursor `cProducts`; `unit_price` copied to lines |
| `SETUP` | write | indirectly, through the `newid()` defaults when a header is appended |

## Inter-form navigation

- **→ [[custadd.md]]** from `cboCustomer_ID.Valid` when a typed customer does not exist; modal, returns `.T.` on OK.
- **→ [[ordhist.md]]** from `cmdLastOrder.Click`, passing `thisform`; the history form locks this form until it closes and can insert checked items into this form's `order_line_items` by switching data sessions.
- **→ `findorder`** ([[../05-classes/tsgen.md]]) from `cmdFind.Click`.
- **← Orders menu** and, in a non-debug build, the Customer Service Rep startup action.
- **Items menu pad** (`menus\ordentry.mpr`) is added on `Activate` and removed on `Deactivate`.

## Notes

- **Credit is recomputed on every grid refresh** by `RemainingCredit()`, which runs a `SELECT ... GROUP BY` over the customer's unpaid orders each time. Fine at 1,079 orders; a scaling concern.
- **`chkPaid.Refresh` forces `lAllowEdits = .T.`**, fighting the delivery-date rule in the class. Which wins depends on refresh order.
- **Undocumented magic values** `CHR(12)` and `CHR(200)` in `cboCustomer_ID.Valid`.
- **`USE ... AGAIN` + `COUNT`** in `cmdLastOrder.Click` for an existence check.
- **Menu pad per form** (`DO menus\ordentry.mpr` on every `Activate`): the pad is redefined each activation.
- **Hard-coded English** through `_LOC` constants; "Right click on grid for menu" is a literal caption.
- **Direct table access**: `USE ORDERS IN 0 AGAIN ALIAS orders_temp` in `cmdLastOrder.Click`; everything else goes through the DataEnvironment.
