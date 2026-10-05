# Business logic, quoted

Every rule and formula the application enforces, each quoted from its source through the parser and then explained, with where it is enforced and which other places repeat it. Numbered R1 to R14 so other docs can cite them. The plain-language account is [[../02-domain/README.md]].

**Related docs:** [[../03-data-model/README.md]] (the stored procedures in full), [[../05-classes/orders.md]], [[../04-forms/ordentry.md]], [[../04-forms/ordhist.md]], [[../05-classes/login.md]], [[../07-menus/main.md]], [[../06-reports/orders.md]], [[../08-programs/tastrade.h.md]].

## Where the rules live

| Layer | Rules |
|---|---|
| DBC field defaults and rules | R1 keys, R2 default employee, R3 field rules |
| DBC table rule | R4 order validation |
| DBC relations (RI Builder triggers) | R5 referential integrity |
| Stored procedures called by code | R7 credit |
| Views | R8 order total (two of seven copies), R12 sales figures |
| Class and form code | R4 duplicates, R6 delete guards, R8 (screen), R9 price and discount copy, R10 editability, R11 login, R13 paid |
| Menu cleanup code and `USER_LEVEL` rows | R14 user levels |
| Report variables | R8 (invoice) |

## R1. Keys come from the `SETUP` counters

Every table but `CUSTOMER` and `ORDER_LINE_ITEMS` takes its primary key from `NewID()`, the default expression of the key field; `orders.order_number` takes a second counter by name. `SETUP` holds one row per counter (`SUPPLIER`=30, `PRODUCTS`=78, `EMPLOYEE`=16, `CATEGORY`=9, `SHIPPERS`=4, `ORDERS`=1138, `ORDER_NUMBER`=1138). The customer ID is typed by the user and only required to be non-empty (R3); the primary index refuses duplicates and the `customerinfo` container turns error 1884 into "Customer ID already exists" ([[../05-classes/tsgen.md]]).

Defaults, from the DBC twin:

| Table | Field | Default |
|---|---|---|
| `CATEGORY` | `category_id` | `newid()` |
| `EMPLOYEE` | `employee_id` | `newid()` |
| `ORDERS` | `employee_id` | `defaultemployee()` |
| `ORDERS` | `order_id` | `newid()` |
| `ORDERS` | `order_number` | `newid("order_number")` |
| `PRODUCTS` | `product_id` | `newid()` |
| `SHIPPERS` | `shipper_id` | `newid()` |
| `SUPPLIER` | `supplier_id` | `newid()` |

```foxpro
FUNCTION NewID(tcAlias)
  LOCAL lcAlias, ;
        lcID, ;
        lcOldReprocess, ;
        lnOldArea

*-- ... 33 more lines of Microsoft's Tastrade source omitted; see `R1. Keys come from the `SETUP` counters` in your own copy of Tastrade.
```

Locks the counter row, waiting without limit (`SET REPROCESS TO AUTOMATIC`), returns the old value and stores the incremented one at the same width. **NOTE:** a missing counter name or a failed lock returns an empty key, and no caller checks. `ORDER_LINE_ITEMS` has no key at all ([[../03-data-model/tables/order_line_items.md]]).

## R2. A new order belongs to the logged-in employee

```foxpro
FUNCTION DefaultEmployee()
  LOCAL lcEmployeeID
  *-- An order must have an employee ID associated with it
  *-- For the purposes of this sample application, we will
  *-- attempt to use the employee ID for the currently logged in
  *-- employee. If the oApp object does not exist (i.e., we are not
*-- ... 14 more lines of Microsoft's Tastrade source omitted; see `R2. A new order belongs to the logged-in employee` in your own copy of Tastrade.
```

Default of `orders.employee_id`. **NOTE:** under `DEBUGMODE` the logged-in ID is empty, so every new order in the shipped build goes to the first employee on file ([[../05-classes/main.md]]).

## R3. Field rules and defaults

From the DBC twin (`data/tastrade.dc2`); the message is what the user sees when the rule fails.

| Table | Field | Default | Rule | Message |
|---|---|---|---|---|
| `CATEGORY` | `category_name` |  | `.NOT.EMPTY(category_name)` | Category name cannot be empty. |
| `CUSTOMER` | `company_name` |  | `.NOT.EMPTY(company_name)` | Company name cannot be empty. |
| `CUSTOMER` | `customer_id` |  | `.NOT.EMPTY(customer_id)` | Customer ID cannot be empty. |
| `CUSTOMER` | `discount` | `0` |  |  |
| `CUSTOMER` | `max_order_amt` |  | `max_order_amt=>min_order_amt` | Maximum order amount must be greater than or equal to minimum order amount. |
| `CUSTOMER` | `min_order_amt` |  | `min_order_amt<=max_order_amt` | Minimum order amount must be less than or equal to maximum order amount. |
| `EMPLOYEE` | `last_name` |  | `.NOT.EMPTY(last_name)` | Last name cannot be empty. |
| `EMPLOYEE` | `password` | `"Tastrade"` |  |  |
| `ORDER_LINE_ITEMS` | `quantity` | `1` |  |  |
| `ORDERS` | `deliver_by` | `DATE()+7` | `deliver_by=>order_date` | Cannot be earlier than Order Date |
| `ORDERS` | `discount` | `0` |  |  |
| `ORDERS` | `order_date` | `DATE()` |  |  |
| `PRODUCTS` | `product_name` |  | `.NOT.EMPTY(product_name)` | Product name cannot be empty. |
| `PRODUCTS` | `reorder_level` | `0` |  |  |
| `PRODUCTS` | `units_in_stock` | `0` |  |  |
| `PRODUCTS` | `units_on_order` | `0` |  |  |
| `SHIPPERS` | `company_name` |  | `.NOT.EMPTY(company_name)` | Company name cannot be empty. |
| `SUPPLIER` | `company_name` |  | `.NOT.EMPTY(company_name)` | Company name cannot be empty. |

- `max_order_amt` and `min_order_amt` validate against each other; editing one can fail on the other ([[../03-data-model/tables/customer.md]]).
- `deliver_by` defaults to a week out and may not precede the order date; the order form is stricter (R10).
- `password` defaults to `"Tastrade"` for every new employee; the sample's own text says "You must log in as the new employee to change the password."

## R4. An order must have a line, fit the customer's credit, and meet the minimum

The `ORDERS` table rule, `ValOrder()`, runs on every `TABLEUPDATE` of an order. In order: nothing if the row is deleted; at least one line with a product, else refuse; unless the only change is the paid flag or the order history form is on top, compute remaining credit (R7) and ask whether to save anyway if it is negative; then ask again if the order is under the customer's minimum. The user's Yes is the rule's return value.

```foxpro
FUNCTION ValOrder()
  LOCAL llRetVal, ;
        lnAnswer, ;
        llClose, ;
        lnOldRecNo, ;
        lnOrderTotal, ;
*-- ... 89 more lines of Microsoft's Tastrade source omitted; see `R4. An order must have a line, fit the customer's credit, and meet the minimum` in your own copy of Tastrade.
```

The amount compared with the minimum is `CalcMinOrdAmount()`, the total after discount **without freight**:

```foxpro
FUNCTION CalcMinOrdAmount(tcOrderID)
  *-- Returns order amount
  *-- Assumes orders table is open and positioned on desired record
  LOCAL lyOrderTotal, ;
        llClose

*-- ... 23 more lines of Microsoft's Tastrade source omitted; see `R4. An order must have a line, fit the customer's credit, and meet the minimum` in your own copy of Tastrade.
```

**NOTE:** a data-layer rule that shows dialogs and reads `_screen.ActiveForm.Name`. **NOTE:** `CalcOrdTotal()` is a second copy of the same function, called by nothing ([[../03-data-model/README.md]]). **NOTE:** the sample's Behind the Scenes text says a failed condition stops validation; the code lets the user override the last two.

The order entry class forces the rule to fire even when only lines changed, by marking the customer field edited before `TABLEUPDATE`, inside the application's only transaction ([[../05-classes/orders.md]] `save`):

```foxpro
*-- (c) Microsoft Corporation 1995

LOCAL llError, ;
      laError[AERRORARRAY]

thisform.MoveOffGrid()
*-- ... 39 more lines of Microsoft's Tastrade source omitted; see `R4. An order must have a line, fit the customer's credit, and meet the minimum` in your own copy of Tastrade.
```

## R5. Referential integrity

Eight relations with RI Builder rules: key changes cascade to children; a parent in use cannot be deleted, except an order, whose lines go with it; a child cannot point at a missing parent. The generated triggers are named in [[../03-data-model/README.md]] and are not business logic. The forms translate the trigger failures into six messages (R6).

| Child | Parent | Update | Delete | Insert |
|---|---|---|---|---|
| `EMPLOYEE` | `USER_LEVEL` | cascade | restrict | restrict |
| `ORDER_LINE_ITEMS` | `ORDERS` | cascade | cascade | restrict |
| `ORDER_LINE_ITEMS` | `PRODUCTS` | cascade | restrict | restrict |
| `ORDERS` | `CUSTOMER` | cascade | restrict | restrict |
| `ORDERS` | `EMPLOYEE` | cascade | restrict | restrict |
| `ORDERS` | `SHIPPERS` | cascade | restrict | restrict |
| `PRODUCTS` | `CATEGORY` | cascade | restrict | restrict |
| `PRODUCTS` | `SUPPLIER` | cascade | restrict | restrict |

The rule codes come from the live DBC dump behind [[../03-data-model/README.md]]; the twin lists the relations but not the codes.

## R6. What may not be deleted, in the user's words

Each maintenance form loads the message for its table's delete trigger into `aErrorMsg[DELETETRIG]`; `tsbaseform.Error` shows it on error 1539. The strings are in `include/strings.h` ([[../08-programs/strings.h.md]]).

| Form | Message |
|---|---|
| Category | Products belong to this category. Cannot delete! |
| Customer | Customer has orders. Cannot delete! |
| Employee | Employee exists on orders. Cannot delete! |
| Product | Product exists on order line items. Cannot delete! |
| Supplier | Products are supplied by this supplier. Cannot delete! |
| Shipper | Shipper exists on orders. Cannot delete! |

Two more guards are in code, not triggers: the employee form clears `lAllowDelete` when the current record is the logged-in employee (dead under `DEBUGMODE`, [[../04-forms/employee.md]]), and the order form clears it once the deliver-by date has passed (R10).

## R7. Credit is the maximum order amount minus unpaid orders

```foxpro
FUNCTION RemainingCredit(tcCustomerID)
  LOCAL lyMaxOrderAmount, ;
        lyTotalOrders, ;
        lcCustomerAlias, ;
        lnOldArea

*-- ... 36 more lines of Microsoft's Tastrade source omitted; see `R7. Credit is the maximum order amount minus unpaid orders` in your own copy of Tastrade.
```

Called by `ValOrder()` (R4) and by the order entry form whenever the customer changes or the paid flag is toggled, to show "Available Credit" ([[../04-forms/ordentry.md]]); the order history form shows the other half of it, the sum of the customer's unpaid order totals, as "Balance". The per-order total here includes freight and is computed for **unpaid** orders only. **NOTE:** the sample's Behind the Scenes text says all the customer's orders are summed. `ValOrder()` adds the current order's own amount back when it is marked paid: `RemainingCredit(orders.customer_id) + IIF(orders.paid, lyOrderAmount, 0)`.

## R8. The order total, written seven times

`subtotal = sum(unit_price * quantity)`; `discount = subtotal * discount% / 100`; `total = subtotal - discount + freight`. Each copy, verbatim:

| # | Where | Freight | Source |
|---|---|---|---|
| 1 | `CalcMinOrdAmount()` (R4) | no | `SUM (unit_price * quantity) - (orders.discount * .01) * (unit_price * quantity) FOR order_id = tcOrderID` |
| 2 | `CalcOrdTotal()` (dead) | no | same |
| 3 | `RemainingCredit()` (R7) | yes | `SUM((b.unit_price * b.quantity) - (a.discount * .01) * (b.unit_price * b.quantity)) + a.freight` per unpaid order |
| 4 | View `ORDER HISTORY` | yes | see below |
| 5 | View `ORDERTOTAL` (feeds Top 25) | yes | see below |
| 6 | Order entry screen | yes | `txtSubTotal` from the grid's `ncolumnsum` of `quantity * unit_price`, then the chain below |
| 7 | Invoice report | yes | `vSubTotal` sums `quantity * MTON(unit_price)` per order; `vDisCount = iif(discount > 0, vSubTotal * (discount / 100), 0)`; total field `vSubTotal + freight - vDisCount` |

View `ORDER HISTORY`:

```sql
SELECT Orders.order_id, Orders.order_date, Orders.deliver_by,  SUM(Orditems.unit_price*Orditems.quantity)-Orders.discount*0.01*SUM(Orditems.unit_price*Orditems.quantity)+Orders.freight AS ord_total,  Orders.paid FROM  tastrade!orders INNER JOIN tastrade!order_line_items Orditems    ON  Orders.order_id = Orditems.order_id WHERE Orders.customer_id = ?customer.customer_id GROUP BY Orditems.order_id ORDER BY Orders.order_date DESC
```

View `ORDERTOTAL`:

```sql
SELECT Orders.customer_id,   SUM(Orditems.unit_price*Orditems.quantity-(0.01*Orders.discount*Orditems.unit_price*Orditems.quantity))+Orders.freight AS ordertotal  FROM  tastrade!orders INNER JOIN tastrade!order_line_items Orditems     ON  Orders.order_id = Orditems.order_id   GROUP BY Orditems.order_id
```

The screen chain ([[../05-classes/orders.md]]):

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

```foxpro
*-- Calculate the total order amount
thisform.txtTotal.Value = ;
  thisform.txtSubtotal.Value - ;
  this.Value + ;
  thisform.txtFreight.Value
```

The invoice variables ([[../06-reports/orders.md]]):

| Variable | Value to store | Calculate | Reset |
|---|---|---|---|
| `vSubTotal` | `quantity * MTON(unit_price)` | Sum | Group 1 |
| `vDisCount` | `iif(discount > 0, vSubTotal * (discount / 100), 0)` | nothing | End of report |

All seven agree on the arithmetic; they differ on freight (copies 1 and 2 leave it out, which is right for the minimum-order check and wrong for anything else) and on rounding, which none of them does. A rebuild implements it once, with freight as a parameter.

## R9. Prices and discounts are copied at the moment of choice

Choosing a product on a line copies the product's current price onto the line; the line keeps that price if the product's price later changes ([[../04-forms/ordentry.md]]):

```foxpro
*-- Force relation to product table to be updated  
REPLACE order_line_items.product_id WITH this.Value
GO recno() IN order_line_items
REPLACE order_line_items.unit_price WITH products.unit_price
thisform.grdLineItems.Refresh()
```

Choosing a customer copies the customer's normal discount and address block onto the order; the clerk may then change the discount ([[../05-classes/orders.md]] `refreshcustomerinfo`). Copying tagged history lines into a new order carries their historical unit price ([[../04-forms/ordhist.md]]). Nothing stops ordering a discontinued product: the product list is `select product_name, product_id from products order by product_name`.

## R10. An order is editable until its deliver-by date passes

```foxpro
textbox::Refresh()
IF !("HISTORY" $ UPPER(thisform.Name))
  IF "3" $ GETFLDSTATE(-1) OR "4" $ GETFLDSTATE(-1)
    thisform.lAllowEdits = .T.
  ELSE
    thisform.lAllowEdits = this.Value > DATE()
*-- ... 4 more lines of Microsoft's Tastrade source omitted; see `R10. An order is editable until its deliver-by date passes` in your own copy of Tastrade.
```

A new record is always editable; an existing one only while `deliver_by` is after today, and deletable under the same condition. The date itself must be today or later on entry, stricter than the DBC rule (R3):

```foxpro
*-- The deliver by date must be today or later
IF this.Value < DATE()
  =MessageBox(TODAYORLATER_LOC, ;
              MB_ICONEXCLAMATION, ;
              TASTRADE_LOC)
  this.Value = DATE()
*-- ... 3 more lines of Microsoft's Tastrade source omitted; see `R10. An order is editable until its deliver-by date passes` in your own copy of Tastrade.
```

## R11. Login

`login.cmdOk.Click`; the `loginpicture` subclass the application shows calls it and then returns `employee_id + "," + thisform.GetUserLevel()`:

```foxpro
*-- Now check the password
IF ALLTRIM(EVAL(this.parent.cPassword)) == ALLTRIM(this.parent.txtPassword.Value)
  thisform.Hide()
ELSE
  =MESSAGEBOX(BADPASSWORD_LOC, MB_ICONEXCLAMATION)
  this.parent.txtPassword.Value = ""
  this.parent.txtPassword.SetFocus()
ENDIF
```

The stored password must equal the typed one after trimming, case-sensitively, in plain text. The dialog returns `employee_id,user level`; the user level is what the menu gates on (R14). Under `DEBUGMODE` none of this runs ([[../05-classes/login.md]], [[../08-programs/tastrade.h.md]]). Changing a password requires the old one, a non-empty new one, and a matching confirmation ([[../04-forms/chngpswd.md]]).

## R12. What the sales reports call sales

```sql
SELECT STR(YEAR(Orders.order_date), 4) + STR(MONTH(Orders.order_date), 2),  SUM(Order_line_items.unit_price) AS sum_unit_price FROM tastrade!Orders, tastrade!Order_Line_Items WHERE Orders.order_id = Order_line_items.order_id GROUP BY 1
```

`SUM(unit_price)` per month: unit prices added up without quantity, discount, or freight. `SALES DETAIL` does the same per day. `TOP25CUST` sums `ORDERTOTAL` (R8 copy 5) per customer. **NOTE:** the three sales reports use two different definitions of a sale, and neither the reports nor the views say so ([[../06-reports/README.md]]).

## R13. Paid

`orders.paid` has no default (new orders are unpaid). Marking an order paid excludes it from the credit calculation (R7). It is set from the order entry form's checkbox, which recomputes credit, or from the order history grid, which writes through and saves at once ([[../04-forms/ordhist.md]]):

```foxpro
IF SEEK(history.order_id,"orders","order_id")
	REPLACE orders.paid WITH THIS.value
	THISFORM.Save
	THISFORM.txtBalance.Value = THISFORM.CalcBalance()
ENDIF
```

`ValOrder()` skips its credit and minimum checks when the paid flag is the only change or the history form is on top (R4), so paying never asks a question. **NOTE:** this save is outside any transaction.

## R14. User levels

| Group | Description | Startup action |
|---|---|---|
| 1 | Customer Service Rep | `oApp.DoForm("ordentry")` |
| 2 | Applications Developer |  |
| 3 | Operations Manager |  |
| 4 | Sales Manager |  |

Two things depend on the level. `tastrade.Do` runs the level's startup action after the menu (skipped under `DEBUGMODE`, [[../05-classes/main.md]]). The main menu's cleanup code removes pads and bars ([[../07-menus/main.md]]):

```foxpro
*-RELEASE BAR 1 OF Window

IF UPPER(oApp.GetUserLevel()) <> USER_APPDEV_LOC
  RELEASE PAD Utilities OF _MSYSMENU
ENDIF

*-- ... 5 more lines of Microsoft's Tastrade source omitted; see `R14. User levels` in your own copy of Tastrade.
```

`USER_APPDEV_LOC` and `USER_OPSMGR_LOC` are `"APPLICATIONS DEVELOPER"` and `"OPERATIONS MANAGER"` in `include/tastrade.h` and must equal the descriptions above upper-cased. **NOTE:** `ADMINBAR_LOC` is `"Administration"` but the popup is `_qx713dsus`, so the three `RELEASE BAR` lines do nothing useful; Login and Change Password stay for every level. **NOTE:** in the shipped build the level is always Applications Developer. No table, rule, or form checks the level.

## What is not a rule

- Inventory: `units_in_stock`, `units_on_order`, `reorder_level` are edited on the product form and read by nothing.
- Sales regions on customers and employees: stored, never compared.
- Discontinued products: flagged, still orderable, still listed.
- Order notes: a memo nothing else reads.
- Rounding: no copy of the total rounds; the currency fields hold four decimals and the report masks show two.
