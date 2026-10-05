# Data-entry capture

The second capture pass (Step 9): the same harness as [[README.md]], run with `-Pass entry`, drives the forms through the paths a click-through cannot reach: a field rule violated on Save, a delete the referential-integrity trigger refuses, a new order refused four times, an Add Customer with no ID, Change Password twice, a wrong login password, and the employee listing's title dialog. Nothing is saved: every path ends in a refusal or a Restore, and the data files were checked against the committed ones afterwards. Run on 2026-09-09; images in `baseline-entry/` and `baseline-entry-eb70/`.

**Related docs:** [[README.md]] (the click-through baseline), [[save.md]] (the successful-save pass), [[../04-forms/README.md]], [[../09-business-logic/README.md]], [[../01-architecture/startup.md]].

## Runs

| Folder | Engine | Form images | Report pages | Message boxes | Errors caught by `ON ERROR` |
|---|---|---|---|---|---|
| `baseline-entry/` | VFP 9 default (`SET ENGINEBEHAVIOR 90`) | 25 | 3 | 97 | 68 |
| `baseline-entry-eb70/` | harness forcing `SET ENGINEBEHAVIOR 70` | 27 | 3 | 11 | 0 |

## Customer rule violation

Open Customers (record ALFKI, minimum 2,600, maximum 6,300), put focus in Min Order Amount, set its value to 999,999 (the box still paints the stored value until it loses focus), call the form's `Save` as the toolbar does, then `Restore`.

Docs: [[../04-forms/customer.md]], [[../03-data-model/tables/customer.md]] (the rule `min_order_amt <= max_order_amt`).

### VFP 9 default (`SET ENGINEBEHAVIOR 90`)

| Image | State | Size |
|---|---|---|
| `customer-before.png` | oApp.DoForm("customer"); Min Order Amount set above the maximum; Save; Restore | 610×381 |
| `customer-typed.png` | Min Order Amount typed as 999999, above the maximum | 610×381 |
| `customer-rule.png` | after Save() with the rule min_order_amt <= max_order_amt violated | 610×381 |
| `customer-restored.png` | after Restore() | 610×381 |

| # | Time | Title | Text | Buttons | Pressed | Image |
|---|---|---|---|---|---|---|
| 1 | 17:25:16 | Tasmanian Traders | Minimum order amount must be less than or equal to maximum order amount. | OK | OK | `01.png` |

### harness forcing `SET ENGINEBEHAVIOR 70`

| Image | State | Size |
|---|---|---|
| `customer-before.png` | oApp.DoForm("customer"); Min Order Amount set above the maximum; Save; Restore | 610×381 |
| `customer-typed.png` | Min Order Amount typed as 999999, above the maximum | 610×381 |
| `customer-rule.png` | after Save() with the rule min_order_amt <= max_order_amt violated | 610×381 |
| `customer-restored.png` | after Restore() | 610×381 |

| # | Time | Title | Text | Buttons | Pressed | Image |
|---|---|---|---|---|---|---|
| 1 | 17:30:11 | Tasmanian Traders | Minimum order amount must be less than or equal to maximum order amount. | OK | OK | `01.png` |

## Delete refused by referential integrity

Open Shippers, press Delete and answer Yes to the confirmation. Every shipper has orders and the orders-to-shippers delete rule is restrict, so the trigger refuses.

Docs: [[../04-forms/shipper.md]], [[../03-data-model/README.md]] (RI rules).

### VFP 9 default (`SET ENGINEBEHAVIOR 90`)

| Image | State | Size |
|---|---|---|
| `shipper-before.png` | oApp.DoForm("shipper"); Delete answered Yes (every shipper has orders; RI delete rule is restrict) | 526×150 |
| `shipper-delete-refused.png` | after Delete() confirmed Yes: the RI delete trigger (restrict) refused it | 526×150 |

| # | Time | Title | Text | Buttons | Pressed | Image |
|---|---|---|---|---|---|---|
| 2 | 17:25:31 | Delete Warning | Are you sure you want to delete this record? | Yes/No | Yes | `02.png` |
| 3 | 17:25:32 | Tasmanian Traders | Shipper exists on orders. Cannot delete! | OK | OK | `03.png` |

### harness forcing `SET ENGINEBEHAVIOR 70`

| Image | State | Size |
|---|---|---|
| `shipper-before.png` | oApp.DoForm("shipper"); Delete answered Yes (every shipper has orders; RI delete rule is restrict) | 526×150 |
| `shipper-delete-refused.png` | after Delete() confirmed Yes: the RI delete trigger (restrict) refused it | 526×150 |

| # | Time | Title | Text | Buttons | Pressed | Image |
|---|---|---|---|---|---|---|
| 2 | 17:30:26 | Delete Warning | Are you sure you want to delete this record? | Yes/No | Yes | `02.png` |
| 3 | 17:30:28 | Tasmanian Traders | Shipper exists on orders. Cannot delete! | OK | OK | `03.png` |

## A new order that the rules refuse

Open Order Entry, New, Save with no customer and no line (`ValOrder`: an order must have at least one line item); set customer ALFKI through the combo's `Value` (its `ProgrammaticChange` runs the same code as a pick), add the first product with quantity 1 as the product combo does, Save (below the customer's minimum of 2,600, "Save anyway?" answered No); under engine 70 only, customer CACTU, whose saved unpaid orders already exceed its maximum, Save (over the credit limit, answered No); then customer ALFKI with quantity 100,000 and no shipper, Save (the orders-to-shippers insert trigger refuses); Restore.

Docs: [[../04-forms/ordentry.md]], [[../05-classes/orders.md]], [[../09-business-logic/README.md]] (`ValOrder`, `RemainingCredit`).

### VFP 9 default (`SET ENGINEBEHAVIOR 90`)

| Image | State | Size |
|---|---|---|
| `ordentry-before.png` | oApp.DoForm("ordentry"); AddNew; Save with no item; customer ALFKI and one line, quantity 1, Save (below minimum, No); Restore | 613×383 |
| `ordentry-new.png` | after AddNew(): blank order, DBC defaults for id, number, dates, employee | 613×383 |
| `ordentry-noitems.png` | after Save() with no customer and no line item (ValOrder) | 613×383 |
| `ordentry-filled.png` | customer ALFKI (minimum order 2,600) and one line, quantity 1 | 613×383 |
| `ordentry-belowmin.png` | after Save() below the customer minimum: "Save anyway?" answered No | 613×383 |
| (none) | under ENGINEBEHAVIOR 90 the credit check itself errors (RemainingCredit), so an over-credit save could go through; run with -Engine 70 | skipped |
| `ordentry-filled-noshipper.png` | customer ALFKI, quantity 100000 (above the minimum), no shipper | 613×383 |
| `ordentry-noshipper.png` | after Save() with no shipper: the RI insert trigger refused it | 613×383 |
| `ordentry-restored.png` | after Restore(): the new order and its line reverted | 613×383 |

| # | Time | Title | Text | Buttons | Pressed | Image |
|---|---|---|---|---|---|---|
| 4 | 17:25:39 | An error has occurred | SQL: GROUP BY clause is missing or invalid.Method: remainingcreditLine: 75 | Abort/Retry/Ignore | Ignore | `04.png` |
| 5 | 17:25:40 | An error has occurred | Variable 'TOTALORDER' is not found.Method: remainingcreditLine: 77 | Abort/Retry/Ignore | Ignore | `05.png` |
| 6 | 17:25:42 | An error has occurred | Alias 'ORDERAMOUNTS' is not found.Method: remainingcreditLine: 80 | Abort/Retry/Ignore | Ignore | `06.png` |
| 7 | 17:25:44 | An error has occurred | Operator/operand type mismatch.Method: remainingcreditLine: 84 | Abort/Retry/Ignore | Ignore | `07.png` |
| 8 | 17:25:53 | Tasmanian Traders | An order must have at least one line item. | OK | OK | `08.png` |
| 9 | 17:25:58 | Tasmanian Traders | An order must have at least one line item. | OK | OK | `09.png` |
| 10 | 17:26:00 | Tasmanian Traders | Customer order total must be at least $2600.00Save anyway? | Yes/No | No | `10.png` |
| 11 | 17:26:02 | Tasmanian Traders | Customer order total must be at least $2600.00Save anyway? | Yes/No | No | `11.png` |
| 12 | 17:26:07 | An error has occurred | SQL: GROUP BY clause is missing or invalid.Method: remainingcreditLine: 75 | Abort/Retry/Ignore | Ignore | `12.png` |
| 13 | 17:26:09 | An error has occurred | Variable 'TOTALORDER' is not found.Method: remainingcreditLine: 77 | Abort/Retry/Ignore | Ignore | `13.png` |
| 14 | 17:26:10 | An error has occurred | Alias 'ORDERAMOUNTS' is not found.Method: remainingcreditLine: 80 | Abort/Retry/Ignore | Ignore | `14.png` |
| 15 | 17:26:12 | An error has occurred | Operator/operand type mismatch.Method: remainingcreditLine: 84 | Abort/Retry/Ignore | Ignore | `15.png` |
| 16 | 17:26:14 | An error has occurred | Operator/operand type mismatch.Method: valorderLine: 138 | Abort/Retry/Ignore | Ignore | `16.png` |
| 17 | 17:26:16 | An error has occurred | Operator/operand type mismatch.Method: valorderLine: 139 | Abort/Retry/Ignore | Ignore | `17.png` |
| 18 | 17:26:17 | An error has occurred | Function argument value, type, or count is invalid.Method: valorderLine: 145 | Abort/Retry/Ignore | Ignore | `18.png` |
| 19 | 17:26:19 | An error has occurred | Operator/operand type mismatch.Method: valorderLine: 146 | Abort/Retry/Ignore | Ignore | `19.png` |
| 20 | 17:26:21 | Tasmanian Traders | Customer order total must be at least $2600.00Save anyway? | Yes/No | No | `20.png` |
| 21 | 17:26:22 | An error has occurred | SQL: GROUP BY clause is missing or invalid.Method: remainingcreditLine: 75 | Abort/Retry/Ignore | Ignore | `21.png` |
| 22 | 17:26:24 | An error has occurred | Alias name is already in use.Method: remainingcreditLine: 66 | Abort/Retry/Ignore | Ignore | `22.png` |
| 23 | 17:26:26 | An error has occurred | SQL: GROUP BY clause is missing or invalid.Method: remainingcreditLine: 75 | Abort/Retry/Ignore | Ignore | `23.png` |
| 24 | 17:26:28 | An error has occurred | Variable 'TOTALORDER' is not found.Method: remainingcreditLine: 77 | Abort/Retry/Ignore | Ignore | `24.png` |
| 25 | 17:26:29 | An error has occurred | Alias 'ORDERAMOUNTS' is not found.Method: remainingcreditLine: 80 | Abort/Retry/Ignore | Ignore | `25.png` |
| 26 | 17:26:31 | An error has occurred | Operator/operand type mismatch.Method: remainingcreditLine: 84 | Abort/Retry/Ignore | Ignore | `26.png` |
| 27 | 17:26:33 | An error has occurred | Operator/operand type mismatch.Method: valorderLine: 138 | Abort/Retry/Ignore | Ignore | `27.png` |
| 28 | 17:26:34 | An error has occurred | Operator/operand type mismatch.Method: valorderLine: 139 | Abort/Retry/Ignore | Ignore | `28.png` |
| 29 | 17:26:36 | An error has occurred | Function argument value, type, or count is invalid.Method: valorderLine: 145 | Abort/Retry/Ignore | Ignore | `29.png` |
| 30 | 17:26:38 | An error has occurred | Operator/operand type mismatch.Method: valorderLine: 146 | Abort/Retry/Ignore | Ignore | `30.png` |
| 31 | 17:26:40 | Tasmanian Traders | Customer order total must be at least $2600.00Save anyway? | Yes/No | No | `31.png` |
| 32 | 17:26:41 | An error has occurred | Alias '_ORDERS' is not found.Method: remainingcreditLine: 79 | Abort/Retry/Ignore | Ignore | `32.png` |
| 33 | 17:26:43 | An error has occurred | Alias 'ORDERAMOUNTS' is not found.Method: remainingcreditLine: 80 | Abort/Retry/Ignore | Ignore | `33.png` |
| 34 | 17:26:45 | An error has occurred | Operator/operand type mismatch.Method: remainingcreditLine: 84 | Abort/Retry/Ignore | Ignore | `34.png` |
| 35 | 17:26:46 | An error has occurred | Operator/operand type mismatch.Method: Operator/operand type mismatch.Line: 0 | Abort/Retry/Ignore | Ignore | `35.png` |
| 36 | 17:26:48 | An error has occurred | SQL: GROUP BY clause is missing or invalid.Method: remainingcreditLine: 75 | Abort/Retry/Ignore | Ignore | `36.png` |
| 37 | 17:26:50 | An error has occurred | Alias name is already in use.Method: remainingcreditLine: 66 | Abort/Retry/Ignore | Ignore | `37.png` |
| 38 | 17:26:52 | An error has occurred | SQL: GROUP BY clause is missing or invalid.Method: remainingcreditLine: 75 | Abort/Retry/Ignore | Ignore | `38.png` |
| 39 | 17:26:53 | An error has occurred | Variable 'TOTALORDER' is not found.Method: remainingcreditLine: 77 | Abort/Retry/Ignore | Ignore | `39.png` |
| 40 | 17:26:55 | An error has occurred | Alias 'ORDERAMOUNTS' is not found.Method: remainingcreditLine: 80 | Abort/Retry/Ignore | Ignore | `40.png` |
| 41 | 17:26:57 | An error has occurred | Operator/operand type mismatch.Method: remainingcreditLine: 84 | Abort/Retry/Ignore | Ignore | `41.png` |
| 42 | 17:26:59 | An error has occurred | Operator/operand type mismatch.Method: valorderLine: 138 | Abort/Retry/Ignore | Ignore | `42.png` |
| 43 | 17:27:00 | An error has occurred | Operator/operand type mismatch.Method: valorderLine: 139 | Abort/Retry/Ignore | Ignore | `43.png` |
| 44 | 17:27:02 | An error has occurred | Function argument value, type, or count is invalid.Method: valorderLine: 145 | Abort/Retry/Ignore | Ignore | `44.png` |
| 45 | 17:27:04 | An error has occurred | Operator/operand type mismatch.Method: valorderLine: 146 | Abort/Retry/Ignore | Ignore | `45.png` |
| 46 | 17:27:05 | Tasmanian Traders | Customer order total must be at least $2600.00Save anyway? | Yes/No | No | `46.png` |
| 47 | 17:27:07 | An error has occurred | Alias '_ORDERS' is not found.Method: remainingcreditLine: 79 | Abort/Retry/Ignore | Ignore | `47.png` |
| 48 | 17:27:09 | An error has occurred | Alias 'ORDERAMOUNTS' is not found.Method: remainingcreditLine: 80 | Abort/Retry/Ignore | Ignore | `48.png` |
| 49 | 17:27:11 | An error has occurred | Operator/operand type mismatch.Method: remainingcreditLine: 84 | Abort/Retry/Ignore | Ignore | `49.png` |
| 50 | 17:27:16 | Tasmanian Traders | Customer order total must be at least $2600.00Save anyway? | Yes/No | No | `50.png` |
| 51 | 17:27:18 | Tasmanian Traders | Customer order total must be at least $2600.00Save anyway? | Yes/No | No | `51.png` |
| 52 | 17:27:23 | An error has occurred | SQL: GROUP BY clause is missing or invalid.Method: remainingcreditLine: 75 | Abort/Retry/Ignore | Ignore | `52.png` |
| 53 | 17:27:25 | An error has occurred | Variable 'TOTALORDER' is not found.Method: remainingcreditLine: 77 | Abort/Retry/Ignore | Ignore | `53.png` |
| 54 | 17:27:26 | An error has occurred | Alias 'ORDERAMOUNTS' is not found.Method: remainingcreditLine: 80 | Abort/Retry/Ignore | Ignore | `54.png` |
| 55 | 17:27:28 | An error has occurred | Operator/operand type mismatch.Method: remainingcreditLine: 84 | Abort/Retry/Ignore | Ignore | `55.png` |
| 56 | 17:27:30 | An error has occurred | Operator/operand type mismatch.Method: valorderLine: 138 | Abort/Retry/Ignore | Ignore | `56.png` |
| 57 | 17:27:31 | An error has occurred | Operator/operand type mismatch.Method: valorderLine: 139 | Abort/Retry/Ignore | Ignore | `57.png` |
| 58 | 17:27:33 | An error has occurred | Function argument value, type, or count is invalid.Method: valorderLine: 145 | Abort/Retry/Ignore | Ignore | `58.png` |
| 59 | 17:27:35 | An error has occurred | Operator/operand type mismatch.Method: valorderLine: 146 | Abort/Retry/Ignore | Ignore | `59.png` |
| 60 | 17:27:37 | Tasmanian Traders | Customer order total must be at least $2600.00Save anyway? | Yes/No | No | `60.png` |
| 61 | 17:27:38 | An error has occurred | SQL: GROUP BY clause is missing or invalid.Method: remainingcreditLine: 75 | Abort/Retry/Ignore | Ignore | `61.png` |
| 62 | 17:27:40 | An error has occurred | Alias name is already in use.Method: remainingcreditLine: 66 | Abort/Retry/Ignore | Ignore | `62.png` |
| 63 | 17:27:42 | An error has occurred | SQL: GROUP BY clause is missing or invalid.Method: remainingcreditLine: 75 | Abort/Retry/Ignore | Ignore | `63.png` |
| 64 | 17:27:43 | An error has occurred | Variable 'TOTALORDER' is not found.Method: remainingcreditLine: 77 | Abort/Retry/Ignore | Ignore | `64.png` |
| 65 | 17:27:45 | An error has occurred | Alias 'ORDERAMOUNTS' is not found.Method: remainingcreditLine: 80 | Abort/Retry/Ignore | Ignore | `65.png` |
| 66 | 17:27:47 | An error has occurred | Operator/operand type mismatch.Method: remainingcreditLine: 84 | Abort/Retry/Ignore | Ignore | `66.png` |
| 67 | 17:27:49 | An error has occurred | Operator/operand type mismatch.Method: valorderLine: 138 | Abort/Retry/Ignore | Ignore | `67.png` |
| 68 | 17:27:50 | An error has occurred | Operator/operand type mismatch.Method: valorderLine: 139 | Abort/Retry/Ignore | Ignore | `68.png` |
| 69 | 17:27:52 | An error has occurred | Function argument value, type, or count is invalid.Method: valorderLine: 145 | Abort/Retry/Ignore | Ignore | `69.png` |
| 70 | 17:27:54 | An error has occurred | Operator/operand type mismatch.Method: valorderLine: 146 | Abort/Retry/Ignore | Ignore | `70.png` |
| 71 | 17:27:55 | Tasmanian Traders | Customer order total must be at least $2600.00Save anyway? | Yes/No | No | `71.png` |
| 72 | 17:27:57 | An error has occurred | Alias '_ORDERS' is not found.Method: remainingcreditLine: 79 | Abort/Retry/Ignore | Ignore | `72.png` |
| 73 | 17:27:59 | An error has occurred | Alias 'ORDERAMOUNTS' is not found.Method: remainingcreditLine: 80 | Abort/Retry/Ignore | Ignore | `73.png` |
| 74 | 17:28:01 | An error has occurred | Operator/operand type mismatch.Method: remainingcreditLine: 84 | Abort/Retry/Ignore | Ignore | `74.png` |
| 75 | 17:28:02 | An error has occurred | Operator/operand type mismatch.Method: Operator/operand type mismatch.Line: 0 | Abort/Retry/Ignore | Ignore | `75.png` |
| 76 | 17:28:04 | An error has occurred | SQL: GROUP BY clause is missing or invalid.Method: remainingcreditLine: 75 | Abort/Retry/Ignore | Ignore | `76.png` |
| 77 | 17:28:06 | An error has occurred | Alias name is already in use.Method: remainingcreditLine: 66 | Abort/Retry/Ignore | Ignore | `77.png` |
| 78 | 17:28:07 | An error has occurred | SQL: GROUP BY clause is missing or invalid.Method: remainingcreditLine: 75 | Abort/Retry/Ignore | Ignore | `78.png` |
| 79 | 17:28:09 | An error has occurred | Variable 'TOTALORDER' is not found.Method: remainingcreditLine: 77 | Abort/Retry/Ignore | Ignore | `79.png` |
| 80 | 17:28:11 | An error has occurred | Alias 'ORDERAMOUNTS' is not found.Method: remainingcreditLine: 80 | Abort/Retry/Ignore | Ignore | `80.png` |
| 81 | 17:28:13 | An error has occurred | Operator/operand type mismatch.Method: remainingcreditLine: 84 | Abort/Retry/Ignore | Ignore | `81.png` |
| 82 | 17:28:14 | An error has occurred | Operator/operand type mismatch.Method: valorderLine: 138 | Abort/Retry/Ignore | Ignore | `82.png` |
| 83 | 17:28:16 | An error has occurred | Operator/operand type mismatch.Method: valorderLine: 139 | Abort/Retry/Ignore | Ignore | `83.png` |
| 84 | 17:28:18 | An error has occurred | Function argument value, type, or count is invalid.Method: valorderLine: 145 | Abort/Retry/Ignore | Ignore | `84.png` |
| 85 | 17:28:19 | An error has occurred | Operator/operand type mismatch.Method: valorderLine: 146 | Abort/Retry/Ignore | Ignore | `85.png` |
| 86 | 17:28:21 | Tasmanian Traders | Customer order total must be at least $2600.00Save anyway? | Yes/No | No | `86.png` |
| 87 | 17:28:23 | An error has occurred | Alias '_ORDERS' is not found.Method: remainingcreditLine: 79 | Abort/Retry/Ignore | Ignore | `87.png` |
| 88 | 17:28:25 | An error has occurred | Alias 'ORDERAMOUNTS' is not found.Method: remainingcreditLine: 80 | Abort/Retry/Ignore | Ignore | `88.png` |
| 89 | 17:28:26 | An error has occurred | Operator/operand type mismatch.Method: remainingcreditLine: 84 | Abort/Retry/Ignore | Ignore | `89.png` |
| 90 | 17:28:32 | An error has occurred | SQL: GROUP BY clause is missing or invalid.Method: remainingcreditLine: 75 | Abort/Retry/Ignore | Ignore | `90.png` |
| 91 | 17:28:33 | An error has occurred | Variable 'TOTALORDER' is not found.Method: remainingcreditLine: 77 | Abort/Retry/Ignore | Ignore | `91.png` |
| 92 | 17:28:35 | An error has occurred | Alias 'ORDERAMOUNTS' is not found.Method: remainingcreditLine: 80 | Abort/Retry/Ignore | Ignore | `92.png` |
| 93 | 17:28:37 | An error has occurred | Operator/operand type mismatch.Method: remainingcreditLine: 84 | Abort/Retry/Ignore | Ignore | `93.png` |

### harness forcing `SET ENGINEBEHAVIOR 70`

| Image | State | Size |
|---|---|---|
| `ordentry-before.png` | oApp.DoForm("ordentry"); AddNew; Save with no item; customer ALFKI and one line, quantity 1, Save (below minimum, No); Restore | 613×383 |
| `ordentry-new.png` | after AddNew(): blank order, DBC defaults for id, number, dates, employee | 613×383 |
| `ordentry-noitems.png` | after Save() with no customer and no line item (ValOrder) | 613×383 |
| `ordentry-filled.png` | customer ALFKI (minimum order 2,600) and one line, quantity 1 | 613×383 |
| `ordentry-belowmin.png` | after Save() below the customer minimum: "Save anyway?" answered No | 613×383 |
| `ordentry-filled-over.png` | customer CACTU, already over its maximum by 12,228 on saved unpaid orders | 613×383 |
| `ordentry-overcredit.png` | after Save() with the customer over the limit: "Save anyway?" answered No | 613×383 |
| `ordentry-filled-noshipper.png` | customer ALFKI, quantity 100000 (above the minimum), no shipper | 613×383 |
| `ordentry-noshipper.png` | after Save() with no shipper: the RI insert trigger refused it | 613×383 |
| `ordentry-restored.png` | after Restore(): the new order and its line reverted | 613×383 |

| # | Time | Title | Text | Buttons | Pressed | Image |
|---|---|---|---|---|---|---|
| 4 | 17:30:41 | Tasmanian Traders | An order must have at least one line item. | OK | OK | `04.png` |
| 5 | 17:30:50 | Tasmanian Traders | Customer order total must be at least $2600.00Save anyway? | Yes/No | No | `05.png` |
| 6 | 17:30:59 | Tasmanian Traders | Customer is over their maximimun order amount by $12228.34Save anyway? | Yes/No | No | `06.png` |
| 7 | 17:31:08 | Tasmanian Traders | All orders must have a customer and a shipper.(Delivery Info) | OK | OK | `07.png` |

## Add Customer with an empty ID

Open Add Customer with the company name filled as Order Entry does, press OK with the Customer ID empty (the DBC rule `NOT EMPTY(customer_id)`), then Cancel.

Docs: [[../04-forms/custadd.md]].

### VFP 9 default (`SET ENGINEBEHAVIOR 90`)

| Image | State | Size |
|---|---|---|
| `custadd.png` | modal, see driver row | 605×383 |
| `custadd-rule.png` | cmdOK with an empty Customer ID (rule on customer_id) | 605×383 |
| (none) |  | returned |

| # | Time | Title | Text | Buttons | Pressed | Image |
|---|---|---|---|---|---|---|
| 94 | 17:28:46 | Tasmanian Traders | Customer ID cannot be empty. | OK | OK | `94.png` |

### harness forcing `SET ENGINEBEHAVIOR 70`

| Image | State | Size |
|---|---|---|
| `custadd.png` | modal, see driver row | 605×383 |
| `custadd-rule.png` | cmdOK with an empty Customer ID (rule on customer_id) | 605×383 |
| (none) |  | returned |

| # | Time | Title | Text | Buttons | Pressed | Image |
|---|---|---|---|---|---|---|
| 8 | 17:31:20 | Tasmanian Traders | Customer ID cannot be empty. | OK | OK | `08.png` |

## Change Password: correct old password, mismatched confirmation

Type the old password (copied from the form's own Hint box, which shows it), a new password and a different confirmation, press OK, then Cancel.

Docs: [[../04-forms/chngpswd.md]].

### VFP 9 default (`SET ENGINEBEHAVIOR 90`)

| Image | State | Size |
|---|---|---|
| `chngpswd.png` | modal, see driver row | 432×197 |
| `chngpswd-filled.png` | old password typed (from the Hint box), new and confirm differ | 432×197 |
| `chngpswd-mismatch.png` | after cmdOK with new and confirm differing | 432×197 |
| (none) |  | returned |

| # | Time | Title | Text | Buttons | Pressed | Image |
|---|---|---|---|---|---|---|
| 95 | 17:28:59 | Tasmanian Traders | Cannot confirm new password. Please try again. | OK | OK | `95.png` |

### harness forcing `SET ENGINEBEHAVIOR 70`

| Image | State | Size |
|---|---|---|
| `chngpswd.png` | modal, see driver row | 432×197 |
| `chngpswd-filled.png` | old password typed (from the Hint box), new and confirm differ | 432×197 |
| `chngpswd-mismatch.png` | after cmdOK with new and confirm differing | 432×197 |
| (none) |  | returned |

| # | Time | Title | Text | Buttons | Pressed | Image |
|---|---|---|---|---|---|---|
| 9 | 17:31:32 | Tasmanian Traders | Cannot confirm new password. Please try again. | OK | OK | `09.png` |

## Change Password: OK with nothing entered

Press OK with every box empty; the form asks whether to abandon; No closes it.

Docs: [[../04-forms/chngpswd.md]].

### VFP 9 default (`SET ENGINEBEHAVIOR 90`)

| Image | State | Size |
|---|---|---|
| `chngpswd-empty.png` | modal, see driver row | 432×197 |
| (none) |  | returned |

| # | Time | Title | Text | Buttons | Pressed | Image |
|---|---|---|---|---|---|---|
| 96 | 17:29:08 | Tasmanian Traders | You have not yet entered the old password. Do you want to continue? | Yes/No | No | `96.png` |

### harness forcing `SET ENGINEBEHAVIOR 70`

| Image | State | Size |
|---|---|---|
| `chngpswd-empty.png` | modal, see driver row | 432×197 |
| (none) |  | returned |

| # | Time | Title | Text | Buttons | Pressed | Image |
|---|---|---|---|---|---|---|
| 10 | 17:31:42 | Tasmanian Traders | You have not yet entered the old password. Do you want to continue? | Yes/No | No | `10.png` |

## Login with a wrong password

Type a wrong password for the first employee and press OK. (The shipped build never shows this form: `DEBUGMODE` skips the login.)

Docs: [[../05-classes/login.md]].

### VFP 9 default (`SET ENGINEBEHAVIOR 90`)

| Image | State | Size |
|---|---|---|
| `loginpicture.png` | modal, see driver row | 443×345 |
| `loginpicture-filled.png` | password box holds a wrong password | 443×345 |
| `loginpicture-badpassword.png` | after cmdOk with a wrong password | 443×345 |
| (none) | uRetVal | returned |

| # | Time | Title | Text | Buttons | Pressed | Image |
|---|---|---|---|---|---|---|
| 97 | 17:29:18 | Microsoft Visual FoxPro | Password is invalid. (See Hint textbox) | OK | OK | `97.png` |

### harness forcing `SET ENGINEBEHAVIOR 70`

| Image | State | Size |
|---|---|---|
| `loginpicture.png` | modal, see driver row | 443×345 |
| `loginpicture-filled.png` | password box holds a wrong password | 443×345 |
| `loginpicture-badpassword.png` | after cmdOk with a wrong password | 443×345 |
| (none) | uRetVal | returned |

| # | Time | Title | Text | Buttons | Pressed | Image |
|---|---|---|---|---|---|---|
| 11 | 17:31:52 | Microsoft Visual FoxPro | Password is invalid. (See Hint textbox) | OK | OK | `11.png` |

## Employee Listing: the title dialog

Run the report; in its title dialog the runner presses Down, then Enter. The click-through pass pressed Enter alone.

Docs: [[../06-reports/listempl.md]], [[../04-forms/gettitle.md]].

### VFP 9 default (`SET ENGINEBEHAVIOR 90`)

| Image | State | Size |
|---|---|---|
| p1, p2, p3 | 3 pages, ok | REPORT FORM reports\listempl.frx OBJECT ReportListener (ListenerType 3, pages as EMF), as the picker runs it |

No message box.

### harness forcing `SET ENGINEBEHAVIOR 70`

| Image | State | Size |
|---|---|---|
| p1, p2, p3 | 3 pages, ok | REPORT FORM reports\listempl.frx OBJECT ReportListener (ListenerType 3, pages as EMF), as the picker runs it |

No message box.

## Findings

- **Every rule and trigger the scenarios aimed at refused the change, and nothing was saved.** After each run the only bytes that differ from the committed data are the header stamps of five tables and the order-number counter in `setup.dbf` (see below); the runner reports them and they are restored before commit.
- **The customer rule fires, the message shows, and `Save()` still returns `.T.`** The form's `WriteBuffer` `REPLACE`s the typed value, the DBC rule (`min_order_amt <= max_order_amt`) raises 1582, the form's `Error` shows the rule text, and the field keeps its old value; `Save` then finds nothing changed and reports success (`capture.log`: `Save() returned .T.`). A caller cannot tell a refused edit from a saved one.
- **Every abandoned new order consumes an order number.** `AddNew` fires the DBC default `newid()`, which increments the counter in `setup.dbf` at once and permanently: the counter went from 1138 to 1139 in each run although the order was reverted. This is the mechanism behind the counter standing 59 above the number of orders ([[../02-domain/README.md]]): 59 orders were started and not saved.
- **The credit check counts saved unpaid orders only.** `RemainingCredit` reads `orders` through a second alias, so the order being saved is not in the sum; a first order of any size passes. The over-credit prompt appears only for a customer already over the limit before the order: 2 of 92 are (CACTU by 12,228.34; ANTON by 1,777,500), and CACTU produced it under engine 70 (`baseline-entry-eb70/dialogs/06.png`). The prompt's text misspells maximum (`CUSTOVERMAX_LOC` in `include/strings.h`).
- **Under VFP 9's default engine the order rule degrades with every attempt.** Each `Save` runs `ValOrder`, which calls `RemainingCredit`; its `GROUP BY` fails (1807), the procedure runs on into three more errors, `ValOrder` itself then errors four times on the undefined result (lines 138 to 146), and the alias `_orders` it opened is left open, so the next call fails with `Alias name is already in use` and later with `Alias '_ORDERS' is not found`. The order scenario's three saves produced 90 of the run's 97 message boxes; its four saves under engine 70 produced 4 of 11. The below-minimum prompt alone appeared ten times under 90 and once under 70.
- **The order form calls its `Error` method with the message where the method name belongs.** `orderentry.save` passes `Error(laError[1], laError[2], 0)`; the dialog reads `Method: Operator/operand type mismatch. Line: 0` (`baseline-entry/dialogs/35.png`). Only a failing save shows it, so only the engine-90 run has it.
- **Setting the customer through the combo's `Value` leaves the previous customer's ship-to address.** `ProgrammaticChange` and `InteractiveChange` run the same two lines (credit, `RefreshCustomerInfo`), and `RefreshCustomerInfo` copies from the `customer` alias wherever it is positioned; after CACTU was set, the form showed Cactus Comidas with Alfreds Futterkiste's address (`baseline-entry-eb70/forms/ordentry-filled-over.png`). A user's pick from the list was not exercised; whether the base combo repositions the alias on that path is not shown here.
- **The Employee Listing prints every title unless the combo is changed interactively.** The dialog's `cTitle` defaults to `ALL` and is set only by the combo's `InteractiveChange` or the checkbox; `Init` selects the first title programmatically, so the box shows one title while OK prints all (3 pages, every run: Enter alone in the click-through pass, Down then Enter here). One earlier run's Space then Enter printed a single title and a repeat of the same keys left the dialog open; the keystroke path is not deterministic from outside, and the finding rests on the twin (`forms/gettitle.sc2`, `ctitle = ALL`, `cboTitle.ListIndex = 1` in `Init`).
- **The employee listing's "nothing to print" branch, the one with the missing `#INCLUDE`, is unreachable through the interface.** The combo lists only titles that employees have, so a title with no employees cannot be chosen; the latent error documented in [[../06-reports/listempl.md]] needs a data change to reach.
- **The login's wrong-password box has no title of its own**: `MESSAGEBOX(BADPASSWORD_LOC, MB_ICONEXCLAMATION)` shows `Microsoft Visual FoxPro` as the caption where every other message shows `Tasmanian Traders` (`baseline-entry/dialogs/97.png`).
- **Add Customer with an empty ID, the mismatched password confirmation, the empty password dialog, and the refused shipper delete all behave as their docs say**, with the texts `Customer ID cannot be empty.`, `Cannot confirm new password. Please try again.`, `You have not yet entered the old password. Do you want to continue?`, and `Shipper exists on orders. Cannot delete!` (`aErrorMsg` from the RI delete trigger).
