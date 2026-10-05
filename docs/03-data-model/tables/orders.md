# ORDERS

| Source file | Type | Path |
|---|---|---|
| `orders.dbf` | Table in `tastrade.dbc` | `data/tastrade.dc2` (table block `ORDERS`) |

**Purpose:** The order header: who ordered, who ships it, where it ships to, discount, freight, and whether it is paid.

**Used by:**
- [[../../04-forms/ordentry.md]] (`frmorderentry`) creates and edits orders
- [[../../04-forms/ordhist.md]] (`frmordhistory`) lists a customer's orders and toggles `paid`
- `findorder` class in [[../../05-classes/tsgen.md]]
- Every hand-written stored procedure except `NewID()` and `DefaultEmployee()`
- Views `ORDERS VIEW` ([[../../06-reports/orders.md]]), `ORDER HISTORY`, `ORDERTOTAL`, `SALES SUMMARY` ([[../../06-reports/salessum.md]]), `SALES DETAIL` ([[../../06-reports/salesdet.md]])

**Related docs:** [[../README.md]] (container, stored procedures, views)

Row count in the sample data: 1079. DBC comment: "Order Information".

## Schema

| # | Field | Type | Width | Dec | Null | Default | Field-valid expr | Comment |
|---|---|---|---|---|---|---|---|---|
| 1 | `order_id` | Character (C) | 6 | 0 | no | `newid()` |  | Unique ID of this order |
| 2 | `customer_id` | Character (C) | 6 | 0 | no |  |  | ID of customer who placed order |
| 3 | `shipper_id` | Character (C) | 6 | 0 | no |  |  | Shipper ID |
| 4 | `order_number` | Character (C) | 6 | 0 | no | `newid("order_number")` |  | Order number (automatically generated) |
| 5 | `order_date` | Date (D) | 8 | 0 | no | `DATE()` |  | Order date |
| 6 | `ship_to_name` | Character (C) | 40 | 0 | no |  |  | Ship to name |
| 7 | `ship_to_address` | Character (C) | 60 | 0 | no |  |  | Ship to address |
| 8 | `ship_to_city` | Character (C) | 15 | 0 | no |  |  | Ship to city |
| 9 | `ship_to_region` | Character (C) | 15 | 0 | no |  |  | Ship to region |
| 10 | `ship_to_postal_code` | Character (C) | 10 | 0 | no |  |  | Ship to postal (zip) code |
| 11 | `ship_to_country` | Character (C) | 15 | 0 | no |  |  | Ship to country |
| 12 | `discount` | Numeric (N) | 2 | 0 | no | `0` |  | Order discount percent |
| 13 | `freight` | Currency (Y) | 8 | 4 | no |  |  | Total freight charges |
| 14 | `paid` | Logical (L) | 1 | 0 | no |  |  |  |
| 15 | `deliver_by` | Date (D) | 8 | 0 | no | `DATE()+7` | `deliver_by=>order_date` → "Cannot be earlier than Order Date" | Date order must be delivered |
| 16 | `notes` | Memo (M) | 4 | 0 | no |  |  | Miscellaneous notes |
| 17 | `employee_id` | Character (C) | 6 | 0 | no | `defaultemployee()` |  | Employee ID |

## Triggers (from table header)

- Insert: `__ri_insert_orders()`
- Update: `__ri_update_orders()`
- Delete: `__ri_delete_orders()`
- Table valid: `valorder()`

The `__ri_*` triggers are generated referential-integrity code (see the container README). They enforce the relations listed below and contain no business rules.

## Indexes (.cdx tags)

| Tag | Type | Expression | For | Order |
|---|---|---|---|---|
| `shipper_id` | regular | `SHIPPER_ID` |  | asc |
| `customer_i` | regular | `CUSTOMER_ID` |  | asc |
| `employee_i` | regular | `EMPLOYEE_ID` |  | asc |
| `order_numb` | regular | `ORDER_NUMBER` |  | asc |
| `order_id` | primary | `ORDER_ID` |  | asc |
| `cust_ord` | candidate | `CUSTOMER_ID+ORDER_ID` |  | asc |

Primary key tag: `order_id`.

## Stored procedure references

- `DefaultEmployee()` — default of `employee_id`. Quoted and explained in [[../README.md]].
- `NewID()` — default of `order_id`. Quoted and explained in [[../README.md]].
- `NewID()` — default of `order_number`. Quoted and explained in [[../README.md]].
- `ValOrder()` — table rule. Quoted and explained in [[../README.md]].

## Relations

- **Child of** [[customer.md]] on `customer_i` → parent tag `customer_i`. RI: update cascade, delete restrict, insert restrict.
- **Parent of** [[order_line_items.md]] via child tag `order_id`. RI: update cascade, delete cascade, insert restrict.
- **Child of** [[shippers.md]] on `shipper_id` → parent tag `shipper_id`. RI: update cascade, delete restrict, insert restrict.
- **Child of** [[employee.md]] on `employee_i` → parent tag `employee_i`. RI: update cascade, delete restrict, insert restrict.

## Used by

See the header. Forms open this table through their DataEnvironment; reports reach it through the DBC views named above.

## Notes

- Two independent counters: `order_id` defaults to `newid()` (counter `ORDERS`) and `order_number` to `newid("order_number")` (counter `ORDER_NUMBER`). They happen to be equal in the sample data (both at 1138) but nothing keeps them so.
- **NOTE:** The table rule `valorder()` shows `MESSAGEBOX` dialogs and inspects `_screen.ActiveForm.Name` for `frmordhistory`. The data layer knows about the UI. A rebuild has to move that decision out of the rule.
- `deliver_by` must be on or after `order_date` and defaults to a week out.
- `employee_id` defaults to `defaultemployee()`, which asks the running application object for the logged-in employee.
- `paid` has no comment and no default. `ORDER HISTORY` lets the user toggle it, and `ValOrder()` skips the credit check when `paid` is the only changed field.
- `cust_ord` is a candidate key on `customer_id + order_id`, redundant with the primary key but used for seeking a customer's orders.
