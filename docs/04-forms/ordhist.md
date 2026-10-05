# frmordhistory (ordhist.scx)

| Source file | Type | Path |
|---|---|---|
| `ordhist.scx` | Form | `forms/ordhist.sc2` |

**Purpose:** A customer's order history: one grid of the customer's orders with totals and a Paid checkbox, one grid of the selected order's line items, and the customer's outstanding balance. Opened on its own it is a browser that can toggle Paid; opened from order entry it becomes a picker whose checked line items are copied into the order being entered.

**Used by:**
- The Orders menu ([[../07-menus/main.md]]): `oApp.DoForm("ordhist")`, no skip condition, so several instances can be open; each gets a numbered name and caption.
- [[ordentry.md]] `cmdLastOrder.Click`: `oApp.DoForm("ordhist", thisform)`, one linked instance.
- Opens the `findcustomer` picker ([[../05-classes/tsgen.md]]).

**Related docs:** [[../05-classes/tsbase.md]] (`tsbaseform`, `tsgrid`), [[../05-classes/tsgen.md]] (`application.AddInstance`/`RemoveInstance`), [[../03-data-model/README.md]] (views `ORDER HISTORY` and `ORDER HISTORY LINE ITEMS`, which are this form's data), [[../03-data-model/tables/orders.md]], [[ordentry.md]], [[README.md]].

Despite the `orderentry` class description in [[../05-classes/orders.md]], this form extends `tsbaseform` directly and shares no code with the order entry form beyond the base.

## Form metadata

- Base class / parent: `tsbaseform` of `..\libs\tsbase.vcx` → `form`
- Caption: "Order History", suffixed at run time with `:n` (instance number) or ` for <customer>` (linked)
- Modal: no. MDI child with the navigation toolbar, but `lallownew`, `lallowedits`, `lallowdelete` all `.F.`, so the toolbar's New/Save/Restore are disabled and navigation moves through **customers**
- `DataSession = 2` (private); `AutoCenter = .F.`; `restorewindowpos`/`savewindowpos` overridden to do nothing

**Custom properties:**

| Property | Description |
|---|---|
| `coriginalformcaption` |  |
| `coriginalformname` |  |
| `norderrec` | Record number of current order |
| `oordentryform` |  |

**Custom methods:**

| Method | Description |
|---|---|
| `calcbalance` | Calcularte balance due for customer |

## DataEnvironment

| Cursor | Alias | Source | Database | Order | Filter |
|---|---|---|---|---|---|
| `Cursor1` | `orders` | `orders` | `tastrade.dbc` |  |  |
| `Cursor2` | `products` | `products` | `tastrade.dbc` |  |  |
| `Cursor3` | `order_line_items` | `order_line_items` | `tastrade.dbc` |  |  |
| `Cursor4` | `customer` | `customer` | `tastrade.dbc` |  |  |
| `Cursor5` | `citems` | `order history line items` | `tastrade.dbc` |  |  |
| `Cursor6` | `history` | `order history` | `tastrade.dbc` |  |  |

`InitialSelectedAlias = "customer"`, so the navigation toolbar steps through customers and each step refreshes the two grids. Two of the six cursors are **parameterised views** from the DBC:

| View | Parameter | Supplies |
|---|---|---|
| `ORDER HISTORY` (alias `history`) | `?customer.customer_id` | the customer's orders with `ord_total` computed in SQL and `paid` |
| `ORDER HISTORY LINE ITEMS` (alias `citems`) | `?orders.order_id` | the selected order's lines with `extension` and a literal `.F.` first column, `exp_1`, used as the Tag checkbox |

Both are requeried by code (`REQUERY("history")`, `REQUERY("citems")`) after the parent alias is positioned. One relation, `products` → `order_line_items` on `product_id`, is defined but the grids read the views, not the base tables. `BeforeOpenTables` sets `TALK OFF`, `EXCLUSIVE OFF`, `DELETED ON` and `SET DATABASE TO tastrade` because the private session starts with no current database.

```foxpro
SET TALK OFF
SET EXCLUSIVE OFF
SET DELETED ON
SET DATABASE TO tastrade
```

## Controls (depth-first)

| Container path | Class | Bound to / key properties | Role |
|---|---|---|---|
| `cmdAddToCurrentOrder` | `tscommandbutton (commandbutton)` | caption "\<Add checked items to current order" | Copies checked lines into the linked order entry form; enabled only when linked |
| `cmdCancel` | `tscommandbutton (commandbutton)` | caption "Close" | "Close"; offers to discard checked items first |
| `cmdFind` | `tscommandbutton (commandbutton)` | caption ""; picture `..\bitmaps\locate.bmp` | Opens `findcustomer` and repositions; enabled only when not linked |
| `grdLineItems` | `tsgrid (grid)` | RecordSource `cItems` | Lines of the selected order from view `citems`; `cfieldtosum = extension` |
| `grdLineItems.grcExtension.grhExtension` | `header ()` | caption "Extension" |  |
| `grdLineItems.grcExtension.Text1` | `textbox (checkbox)` | disabled; read-only | → `citems.extension` |
| `grdLineItems.grcProduct.grhProduct` | `header (checkbox)` | caption "Product" |  |
| `grdLineItems.grcProduct.Text1` | `textbox (checkbox)` | disabled; read-only | → `citems.product_name` |
| `grdLineItems.grcQuantity.grhQuantity` | `header (checkbox)` | caption "Quantity" |  |
| `grdLineItems.grcQuantity.Text1` | `textbox (checkbox)` | disabled; read-only | → `citems.quantity` |
| `grdLineItems.grcTag.chkItemTag` | `tscheckbox (checkbox)` | caption "" | Column 1's current control: the Tag checkbox bound to the view's literal `exp_1` column; enabled only when linked |
| `grdLineItems.grcTag.grhTag` | `header ()` | caption "Tag" |  |
| `grdLineItems.grcTag.Text1` | `textbox ()` |  |  |
| `grdLineItems.grcUnitPrice.grhUnitPrice` | `header (grid)` | caption "Unit Price" |  |
| `grdLineItems.grcUnitPrice.Text1` | `textbox (grid)` | disabled; read-only | → `citems.unit_price` |
| `grdOrdHistory` | `tsgrid (grid)` | RecordSource `history` | The customer's orders from view `history`; `HighlightRow`, `RecordMark` |
| `grdOrdHistory.Column1.Header1` | `header ()` | caption "Order ID" | "Order ID" |
| `grdOrdHistory.Column1.Text1` | `textbox ()` | read-only | → `history.order_id` |
| `grdOrdHistory.Column2.Header1` | `header (checkbox)` | caption "Order date" | "Order date" |
| `grdOrdHistory.Column2.Text1` | `textbox (checkbox)` | read-only | → `history.order_date` |
| `grdOrdHistory.Column3.Header1` | `header (checkbox)` | caption "Deliver On" | "Deliver On" |
| `grdOrdHistory.Column3.Text1` | `textbox (checkbox)` | read-only | → `history.deliver_by` |
| `grdOrdHistory.Column4.Header1` | `header (checkbox)` | caption "Order Amt" | "Order Amt" |
| `grdOrdHistory.Column4.Text1` | `textbox (checkbox)` | read-only | → `history.ord_total` (computed in the view, with freight) |
| `grdOrdHistory.Column5.chkPaid` | `tscheckbox (checkbox)` | caption "" | Column 5's current control → `history.paid`; `Click` writes through to `orders.paid` and saves |
| `grdOrdHistory.Column5.Header1` | `header (label)` | caption "Paid" | "Paid" |
| `grdOrdHistory.Column5.Text1` | `textbox (label)` |  |  |
| `Tslabel1` | `tslabel (label)` | caption "Orders For:" | "Orders For:" |
| `Tslabel2` | `tslabel (label)` | caption "Current Balance:" | "Current Balance:" |
| `txtBalance` | `tstextbox (textbox)` | disabled | Unbound, disabled; sum of unpaid `ord_total` |
| `txtCustID` | `tstextbox (textbox)` | → `customer.customer_id`; disabled | → `customer.customer_id`, disabled |
| `txtCustomer` | `tstextbox (textbox)` | → `customer.company_name`; disabled | → `customer.company_name`, disabled |

### Events with code

#### `grdOrdHistory.AfterRowColChange`

Moving to another order: if any line items are tagged, offer to discard them (No returns to the previous order); then position `orders` on the chosen order, requery the line-item view, refresh the lower grid, and remember the row. Column changes within the same row are ignored via `nOrderRec`.

```foxpro
LPARAMETERS nColIndex

IF RECNO("history") == THISFORM.nOrderRec
	*- the user hasn't moved off of this record -- only changed columns, so ignore
	RETURN
ENDIF
*-- ... 27 more lines of Microsoft's Tastrade source omitted; see `grdOrdHistory.AfterRowColChange` in your own copy of Tastrade.
```

#### `grdOrdHistory.Column5.chkPaid.Click`

The one write this form performs: positions `orders` on the history row, replaces `paid`, and calls the base `Save` (`TABLEUPDATE`), then recomputes the balance. This is the path the DBC rule `ValOrder()` special-cases: when `paid` is the only changed field, or the active form is `frmordhistory`, the credit and minimum checks are skipped ([[../03-data-model/README.md]]).

```foxpro
IF SEEK(history.order_id,"orders","order_id")
	REPLACE orders.paid WITH THIS.value
	THISFORM.Save
	THISFORM.txtBalance.Value = THISFORM.CalcBalance()
ENDIF
```

#### `grdLineItems.Refresh`

Always enabled so the user can scroll; only the Tag checkbox follows the linked state.

```foxpro
tsGrid::Refresh()
this.Enabled = .t.		&& !IsNull(thisform.oOrdEntryForm)
*- disable tag checkbox in grid if items can't be added to current order
THIS.grcTag.chkItemTag.Enabled = THISFORM.cmdAddToCurrentOrder.Enabled
SELECT customer
```

#### `cmdAddToCurrentOrder.Click`

The cross-session copy. For every tagged line in `citems`, switch to the order entry form's data session, `INSERT INTO order_line_items` a row for the order being entered with the historical `unit_price` and `quantity`, switch back. Then revert the tags, delete any blank line the order entry form had appended, unlock that form through `ClearLink`, hide, refresh it, and release. **NOTE:** `lcProductID`, `lnUnitPrice`, `lnQuantity` are not declared `LOCAL`. **NOTE:** copies the old unit price, not the current product price, so a re-ordered item is priced as it was.

```foxpro
LOCAL lcAlias, ;
      loGrid, ;
      lnOldArea, ;
      lnNumItemsAdded

lnNumItemsAdded = 0
*-- ... 57 more lines of Microsoft's Tastrade source omitted; see `cmdAddToCurrentOrder.Click` in your own copy of Tastrade.
```

#### `cmdCancel.Click`

Close with a discard prompt if any line is tagged. `TSBaseForm::DataChanged()` on the `cItems` view detects the tag edits, which is why the form's own `datachanged` returns `.F.` unconditionally elsewhere.

```foxpro
tsCommandButton::Click

*- if they checked a row in the items grid, give the
*- user the option to save items first
SELECT cItems
IF TSBaseForm::DataChanged()
*-- ... 14 more lines of Microsoft's Tastrade source omitted; see `cmdCancel.Click` in your own copy of Tastrade.
```

#### `cmdFind.Click`

Same discard prompt, then the `findcustomer` picker and a `SEEK` on `customer`; `refreshform` requeries both views.

```foxpro
LOCAL lcCustomer_id

*- if they checked a row in the items grid, give the
*- user the option to save items first
SELECT cItems
IF TSBaseForm::DataChanged()
*-- ... 19 more lines of Microsoft's Tastrade source omitted; see `cmdFind.Click` in your own copy of Tastrade.
```

## Form methods

#### `Init`

Two modes. **Stand-alone** (no parameter): register with `oApp.AddInstance`, suffix the name and caption with the instance number so several can coexist, then look for an order entry or customer form on top and start on its customer (reading the customer form's `customer_id` by temporarily switching to its data session). **Linked** (order entry form passed): keep the name, caption " for <customer>", enable the Add button, start on that form's customer via `GetCustomerID()`. **NOTE:** `TYPE("toOrdEntryForm ")` has a trailing space inside the string; VFP tolerates it. **NOTE:** the loop assigns `toOrdEntryForm` (a parameter) as a side channel for the found form.

```foxpro
*-- (c) Microsoft Corporation 1995

LPARAMETERS toOrdEntryForm
LOCAL lnNumParms, ;
      lcFilter, i, ;
      loCustomerForm, ;
*-- ... 70 more lines of Microsoft's Tastrade source omitted; see `Init` in your own copy of Tastrade.
```

#### `refreshform`

Overrides the base `RefreshForm` (which just calls `Refresh`): disables the Paid checkbox and enables Find only when not linked, requeries the orders view for the current customer, positions `orders` on the first order, requeries the line items, refreshes, recomputes the balance, and leaves `customer` selected for the toolbar.

```foxpro
thisform.LockScreen = .T.
*- disable Paid checkbox if adding a new order
THISFORM.grdOrdHistory.column5.chkPaid.Enabled = !THISFORM.cmdAddToCurrentOrder.Enabled
*- enable Find button only if not adding a new order
THISFORM.cmdFind.Enabled = !(THISFORM.cmdAddToCurrentOrder.Enabled)
=REQUERY("history")
*-- ... 11 more lines of Microsoft's Tastrade source omitted; see `refreshform` in your own copy of Tastrade.
```

#### `calcbalance`

Sum of `ord_total` over unpaid rows of the `history` view, restoring the record pointer.

```foxpro
LOCAL lnBalance, liSelect, liRecno

liSelect = SELECT()

SELECT history
liRecno = IIF(EOF(),0,RECNO())
*-- ... 7 more lines of Microsoft's Tastrade source omitted; see `calcbalance` in your own copy of Tastrade.
```

#### `datachanged`

**NOTE:** reverts the line-item view and reports no change, so the base form's navigation and `QueryUnload` never prompt. The discard prompt is implemented separately in three places (`cmdCancel`, `cmdFind`, `AfterRowColChange`).

```foxpro
=TABLEREVERT(.T., 'citems')
RETURN .F.
```

#### `QueryUnload`

Always closable; combined with `datachanged` above, the toolbar's Close never prompts.

```foxpro
RETURN .T.
```

#### `Activate`

```foxpro
tsBaseForm::Activate
THISFORM.RefreshForm
```

#### `Destroy`

Unlocks the linked order entry form, removes the menu entry under the original caption, deregisters the instance, reverts the view.

```foxpro
tsBaseForm::Destroy()

*-- If this form is linked to an Order Entry form, 
*-- reset any properties that may have changed on
*-- that form by calling its ClearLink() method
IF TYPE("thisform.oOrdEntryForm") = "O" AND ;
*-- ... 15 more lines of Microsoft's Tastrade source omitted; see `Destroy` in your own copy of Tastrade.
```

#### `restorewindowpos`

Empty overrides: instance staggering is done by `AddInstance`, and the INI position is not used.

```foxpro
*-- Override for multiple instance staggering logic
```

#### `savewindowpos`

```foxpro
*-- Override for multiple instance staggering logic
```

## Tables read / written

| Table / view | Access | How |
|---|---|---|
| `CUSTOMER` | read | DataEnvironment; the navigation alias; `SEEK` by ID |
| view `ORDER HISTORY` → `history` | read | requeried per customer; drives the top grid and the balance |
| view `ORDER HISTORY LINE ITEMS` → `citems` | read (+ tag edits reverted) | requeried per order; `exp_1` edited in the buffer as the Tag, then `TABLEREVERT` |
| `ORDERS` | write (`paid` only) | `chkPaid.Click` via `Save` |
| `ORDER_LINE_ITEMS` | write, in **another form's session** | `cmdAddToCurrentOrder.Click` `INSERT INTO` under the order entry form's `DataSessionID` |
| `PRODUCTS` | read | DataEnvironment relation; not referenced by the grids |

## Inter-form navigation

- **← [[ordentry.md]]** passes itself in; this form calls back `GetCustomerID()`, `GetCustomerName()`, `ClearLink()`, `RefreshForm()`, and writes into its data session.
- **← Orders menu**, stand-alone; picks up the customer from whichever of `frmorderentry` or `frmcustomers` is on top.
- **→ `findcustomer`** from `cmdFind.Click`.
- **Multiple instances** by name suffix, tracked in `oApp.aInstances`.

## Notes

- **Cross-session write.** Inserting into another form's buffered cursor by `SET DATASESSION` is the most fragile technique in the application and the reason the two forms lock each other.
- **Toggling Paid saves immediately**, outside any transaction, and bypasses the credit rules by design of `ValOrder()`.
- **The tag column is a view expression** (`SELECT .F., ...`), edited in the buffer and reverted; a trick that only works because the view is never sent updates.
- **Three copies of the discard prompt** and a `datachanged` that lies to the base class.
- **Undeclared variables** in `cmdAddToCurrentOrder.Click`.
- **Balance and order total come from the views**, so this form agrees with `RemainingCredit()` and disagrees with the sales reports ([[../03-data-model/README.md]]).
