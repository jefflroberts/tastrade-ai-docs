# orders.vcx — the order entry form class

| Source file | Type | Path |
|---|---|---|
| `orders.vcx` | Class library | `libs/orders.vc2` |

**Purpose:** The order header as a reusable form class: the ship-to block, shipper combo, dates, discount, freight, and totals, with a `Save` that commits the order and its line items in one transaction and a set of overrides that keep the base form's navigation working when a grid of line items has focus. `ordtextbox` is the text box variant whose enabled state follows the form's `lAllowEdits`.

**Used by:**
- [[../04-forms/ordentry.md]] (`frmorderentry`) extends `orderentry`, adds the customer combo, the line-item grid (`grdLineItems`, a `tsgrid` summing `quantity * unit_price`), the DataEnvironment (`Orders`, `Customer`, `Shippers`, `Order_Line_Items`, `Products`), and the `ControlSource` bindings for every text box defined here.
- The order history form (`frmordhistory`, [[../04-forms/ordhist.md]]) does **not** extend this class despite the class description; it extends `tsbaseform` directly and uses no `ordtextbox`. The `"HISTORY" $ thisform.Name` branches in this library are therefore dead in the shipped app.

**Related docs:** [[tsbase.md]] (`tsbaseform`, `tstextbox`, `tsgrid`), [[../03-data-model/tables/orders.md]] and [[../03-data-model/tables/order_line_items.md]] (the tables `Save` commits; the `ValOrder()` rule that fires), [[../03-data-model/README.md]] (the order-total formula, of which this form holds a sixth copy), [[README.md]].

## Classes in this library

### orderentry (extends tsbaseform OF tsbase.vcx)

**Purpose:** The main order entry class, from which the order entry and order history forms will be based on. Caption "Order Entry". Holds the layout and the logic; the subclass form supplies data binding. `ashippers[]` is declared but nothing in this class or the form uses it.

**Custom properties:**

| Property | Protected | Description |
|---|---|---|
| `ashippers[1,0]` |  | Array of shippers |

**Custom methods:**

| Method | Protected | Description |
|---|---|---|
| `moveoffgrid` |  | Sets focus away from the grid when navigating the table. |
| `refreshcustomerinfo` |  | Refreshes the customer ship to address, city, etc. Called when selecting a new customer. |

**Controls defined here** (bindings shown are set by the `frmorderentry` subclass, not this class):

| Control | Class | Bound to (in the form) | Notes |
|---|---|---|---|
| `txtOrder_Number` | `ordtextbox` | `orders.order_number` | disabled, `ldynamicenable = .F.` |
| `txtOrder_Date` | `ordtextbox` | `orders.order_date` | disabled, `ldynamicenable = .F.` |
| `txtDeliver_By` | `ordtextbox` | `orders.deliver_by` | `Valid` enforces today or later; `Refresh` decides editability |
| `cboShipper_ID` | `tscombobox` | `Orders.shipper_id`; row source `select company_name, shipper_id from shippers ... into cursor cShipperList` | `BoundColumn = 2`, drop-down list |
| `txtShip_To_Name`, `_Address`, `_City`, `_Region`, `_Postal_Code`, `txtCountry` | `ordtextbox` | `orders.ship_to_*` | filled from the customer by `refreshcustomerinfo` |
| `txtSubTotal` | `ordtextbox` | unbound | disabled; set by the form from the grid's `ncolumnsum` |
| `txtDiscountPerc` | `ordtextbox` | `orders.discount` | mask `99` |
| `txtDiscount` | `ordtextbox` | unbound | disabled; computed amount |
| `txtFreight` | `ordtextbox` | `orders.freight` | mask `$99,999,999.99` |
| `txtTotal` | `ordtextbox` | unbound | disabled; computed |
| `edtNotes` | `tseditbox` | `orders.notes` | |
| `cmdFocusControl` | `commandbutton` | | parked off-screen; a focus sink |

**Referenced but defined in the subclass form:** `grdLineItems`, `cboCustomer_ID`. This class cannot be instantiated on its own; `addnew` and `refreshcustomerinfo` would fail.

#### The on-screen total

Four `ProgrammaticChange` handlers form a small dependency chain, triggered whenever the form assigns a value in code (the form sets `txtSubTotal.Value` from the grid sum):

```
txtSubTotal  --> txtDiscount = SubTotal * DiscountPerc/100
txtDiscountPerc (LostFocus) --> same
txtDiscount  --> txtTotal = SubTotal - Discount + Freight
txtFreight (LostFocus) --> txtTotal = SubTotal - Discount + Freight
```

This is the order-total formula again, `sum(price*qty) - discount% + freight`, computed on the screen from the grid's `ncolumnsum`, independently of the DBC's `CalcMinOrdAmount()` and the views ([[../03-data-model/README.md]]). The DBC rule `ValOrder()` recomputes it at save time.

#### Methods

#### `addnew`

Selects `orders`, turns editing on (a new order is always editable), refreshes the toolbar, runs the base `AddNew` (which appends the header and fires the DBC defaults for `order_id`, `order_number`, `order_date`, `deliver_by`, `employee_id`), then inserts one blank line item carrying the new `order_id` so the grid has a row to tab into, and puts focus on the customer combo.

```foxpro
IF ALIAS() <> "ORDERS"
  SELECT orders
ENDIF

thisform.lAllowEdits = .T.
thisform.lAllowDelete = .T.
*-- ... 13 more lines of Microsoft's Tastrade source omitted; see `addnew` in your own copy of Tastrade.
```

#### `save`

The one transactional save in the application. After settling the active control: `BEGIN TRANSACTION`; if `orders` shows no field changes, force one (`SETFLDSTATE(2, 2)` marks field 2, `customer_id`, as edited) so `TABLEUPDATE` sends the row and the table rule `ValOrder()` runs; update `orders` (current row only), then `order_line_items` (all rows); `END TRANSACTION` on success, `ROLLBACK` and route the first `AERROR()` to the form's `Error` on failure. **NOTE:** `SETFLDSTATE(2, 2)` hard-codes the field **position** of `customer_id`; reordering the table's fields silently breaks the forced rule check. **NOTE:** `TXNLEVEL() = 0` after `BEGIN TRANSACTION` is treated as an error (transaction could not start).

```foxpro
*-- (c) Microsoft Corporation 1995

LOCAL llError, ;
      laError[AERRORARRAY]

thisform.MoveOffGrid()
*-- ... 39 more lines of Microsoft's Tastrade source omitted; see `save` in your own copy of Tastrade.
```

#### `restore`

Reverts all line items and the current order row, steps back if that left `orders` at end of file, refreshes. Unlike the base `Restore` it does not re-enable the New button or refresh the menu.

```foxpro
thisform.MoveOffGrid()
=TABLEREVERT(.T., "Order_Line_Items")
=TABLEREVERT(.F., "Orders")

IF EOF("orders") AND !BOF("orders")
  SKIP -1 IN ORDERS
*-- ... 3 more lines of Microsoft's Tastrade source omitted; see `restore` in your own copy of Tastrade.
```

#### `datachanged`

A change to any buffered line item (`GETNEXTMODIFIED`) counts as well as a change to the header.

```foxpro
LOCAL llRetVal

SELECT orders
llRetVal = tsBaseForm::DataChanged()
IF !llRetVal
  *-- Check if any line items have changed
*-- ... 4 more lines of Microsoft's Tastrade source omitted; see `datachanged` in your own copy of Tastrade.
```

#### `delete`

Moves focus off the grid and selects `orders` before the base `Delete`, so the header is what gets deleted; the RI cascade removes the lines.

```foxpro
thisform.MoveOffGrid()
IF ALIAS() <> "ORDERS"
  SELECT orders
ENDIF

tsBaseForm::Delete()
```

#### `first`

The four navigation overrides just move focus off the grid first; see `moveoffgrid`.

```foxpro
thisform.MoveOffGrid()
RETURN tsBaseForm::First()
```

#### `prior`

```foxpro
thisform.MoveOffGrid()
RETURN tsBaseForm::Prior()
```

#### `next`

```foxpro
thisform.MoveOffGrid()
RETURN tsBaseForm::Next()
```

#### `last`

```foxpro
thisform.MoveOffGrid()
RETURN tsBaseForm::Last()
```

#### `moveoffgrid` (protected)

Parks focus on the invisible `cmdFocusControl` when the grid has it, so the grid's `SumColumn` is not run twice (once from `Refresh`, once from `BeforeRowColChange`). `cmdFocusControl.GotFocus` immediately forwards focus to the customer combo or ship-to name, so the user never sees it.

```foxpro
*-- To prevent the SumColumn method of grdLineItems from being called
*-- twice, once from the Refresh() method, and once from the BeforeRowColChange
*-- method, we set focus away from the grid
IF TYPE("this.ActiveControl") == "O" AND ;
    UPPER(this.ActiveControl.BaseClass) = "GRID"
  thisform.cmdFocusControl.SetFocus()
ENDIF
```

#### `refreshcustomerinfo`

Copies the customer's address block and discount into the ship-to fields and `txtDiscountPerc` when a customer is chosen, or blanks them. Assumes the `customer` alias is positioned on the chosen customer, which the form's customer combo arranges. The values go into control `Value`s, and reach the `orders` fields through the bindings.

```foxpro
*-- Update customer information
IF !EMPTY(thisform.cboCustomer_ID.Value)
  thisform.txtShip_To_Name.Value = customer.company_name
  thisform.txtShip_To_Address.Value = customer.address
  thisform.txtShip_To_City.Value = customer.city
  thisform.txtShip_To_Region.Value = customer.region
*-- ... 14 more lines of Microsoft's Tastrade source omitted; see `refreshcustomerinfo` in your own copy of Tastrade.
```

#### `restorewindowpos`

Because the order history form was designed to be multi-instance with a dynamic caption, its INI entry is fixed at "Order History". Dead branch here; see the note on `frmordhistory` above.

```foxpro
*-- Since the caption and name properties of 
*-- the Order History form are dynamic, we specify
*-- the name of the entry to make in the INI file.
IF "HISTORY" $ UPPER(thisform.Name)
  tsBaseForm::RestoreWindowPos("Order History")
ELSE
  tsBaseForm::RestoreWindowPos()
ENDIF
```

#### `savewindowpos`

```foxpro
*-- Since the caption and name properties of 
*-- the Order History form are dynamic, we specify
*-- the name of the entry to make in the INI file.
IF "HISTORY" $ UPPER(thisform.Name)
  tsBaseForm::SaveWindowPos("Order History")
ELSE
  tsBaseForm::SaveWindowPos()
ENDIF
```

#### `txtDeliver_By.Refresh`

Decides whether the order is editable: a new record always is; an existing order is editable only while its `deliver_by` date is in the future, and deletable under the same condition. Calls the native `textbox::Refresh` and then `OrdTextBox::Refresh` explicitly, so the enabled state it just computed is applied to this control too.

```foxpro
textbox::Refresh()
IF !("HISTORY" $ UPPER(thisform.Name))
  IF "3" $ GETFLDSTATE(-1) OR "4" $ GETFLDSTATE(-1)
    thisform.lAllowEdits = .T.
  ELSE
    thisform.lAllowEdits = this.Value > DATE()
*-- ... 4 more lines of Microsoft's Tastrade source omitted; see `txtDeliver_By.Refresh` in your own copy of Tastrade.
```

#### `txtDeliver_By.Valid`

Client-side copy of the DBC rule `deliver_by => order_date`, stricter: today or later.

```foxpro
*-- The deliver by date must be today or later
IF this.Value < DATE()
  =MessageBox(TODAYORLATER_LOC, ;
              MB_ICONEXCLAMATION, ;
              TASTRADE_LOC)
  this.Value = DATE()
*-- ... 3 more lines of Microsoft's Tastrade source omitted; see `txtDeliver_By.Valid` in your own copy of Tastrade.
```

#### `txtSubTotal.ProgrammaticChange`

```foxpro
*-- Calculate discount
IF thisform.txtDiscountPerc.Value > 0
  thisform.txtDiscount.Value = ;
    thisform.txtSubTotal.Value * ;
    (thisform.txtDiscountPerc.Value / 100)
ELSE
  thisform.txtDiscount.Value = 0
ENDIF
```

#### `txtDiscountPerc.ProgrammaticChange`

```foxpro
*-- Calculate the discount value based on discount percent
LOCAL lnTemp

IF this.Value > 0
  lnTemp = ;
    thisform.txtSubTotal.Value * ;
*-- ... 5 more lines of Microsoft's Tastrade source omitted; see `txtDiscountPerc.ProgrammaticChange` in your own copy of Tastrade.
```

#### `txtDiscountPerc.LostFocus`

```foxpro
*-- Force the totals to be updated
this.ProgrammaticChange()
```

#### `txtDiscount.ProgrammaticChange`

```foxpro
*-- Calculate the total order amount
thisform.txtTotal.Value = ;
  thisform.txtSubtotal.Value - ;
  this.Value + ;
  thisform.txtFreight.Value
```

#### `txtFreight.ProgrammaticChange`

```foxpro
*-- Calculate the total order amount
thisform.txtTotal.Value = ;
  thisform.txtSubtotal.Value - ;
  thisform.txtDiscount.Value + ;
  this.value
```

#### `txtFreight.LostFocus`

```foxpro
*-- Force the totals to be updated
this.ProgrammaticChange()
```

#### `cboShipper_ID.Refresh`

```foxpro
this.Enabled = thisform.lAllowEdits
```

#### `cboShipper_ID.Destroy`

Closes the shipper cursor the form's row source created.

```foxpro
IF USED("cShipperList")
  USE IN cShipperList
ENDIF
```

#### `edtNotes.Refresh`

```foxpro
this.Enabled = thisform.lAllowEdits
```

#### `cmdFocusControl.Init`

Moves the button ten pixels past the form's right edge.

```foxpro
*-- Move control out of site
this.Left = thisform.Width + 10
```

#### `cmdFocusControl.GotFocus`

```foxpro
*-- If user is tabbing around the form , don't stop here!
IF thisform.cboCustomer_ID.Enabled
  thisform.cboCustomer_ID.SetFocus()
ELSE
  IF thisform.txtShip_To_Name.Enabled
    thisform.txtShip_To_Name.SetFocus()
  ENDIF
ENDIF
```

#### `cmdFocusControl.Refresh`

```foxpro
*-- As user is scrolling through the orders, if 
*-- an order is displayed that is editable, we need
*-- to shift the focus
this.GotFocus()
```

### ordtextbox (extends tstextbox OF tsbase.vcx)

**Purpose:** Order entry text box used exclusively in the order entry class. It is based on tsTextBox, and is designed specifically to work in both the Order Entry and Order History forms. A `tstextbox` whose `Enabled` follows the form's `lAllowEdits` on every `Refresh`, unless `ldynamicenable` is `.F.` (the permanently disabled order number, date, and computed amounts).

**Custom properties:**

| Property | Protected | Description |
|---|---|---|
| `ldynamicenable` |  | False if control is permanently enabled or disabled. |

#### Methods

#### `Init`

After the base `Init` (auto input mask), disables itself permanently when the host form's name contains "HISTORY". Dead in the shipped app.

```foxpro
tsTextBox::Init()
*-- Disable all text boxes if we are running the Order History
*-- form and the text box isn't already disabled.
IF this.Enabled
  this.Enabled = !("HISTORY" $ UPPER(thisform.name))
  IF !this.Enabled
*-- ... 5 more lines of Microsoft's Tastrade source omitted; see `Init` in your own copy of Tastrade.
```

#### `Refresh`

```foxpro
IF this.lDynamicEnable
  this.Enabled = thisform.lAllowEdits
ENDIF
```

## Notes

- **Stale design.** The class description, the `HISTORY` branches, `restorewindowpos`, and `ordtextbox.Init` all serve an order history form built on this class. The shipped `frmordhistory` is built on `tsbaseform` instead. Roughly a fifth of this library is dead code.
- **Half a form.** The class references `grdLineItems` and `cboCustomer_ID` that only the subclass form defines, and every data binding lives in the form. Read [[../04-forms/ordentry.md]] with this page.
- **The only explicit transaction** in the application is `save`; the base form relies on `TABLEUPDATE` alone.
- **Field position hard-coded** in `SETFLDSTATE(2, 2)`.
- **Sixth copy of the order total**, this one on screen.
- **Editability by date.** Orders become read-only the day after their delivery date; there is no status field.
