# CUSTOMER

| Source file | Type | Path |
|---|---|---|
| `customer.dbf` | Table in `tastrade.dbc` | `data/tastrade.dc2` (table block `CUSTOMER`) |

**Purpose:** The customers who place orders, with their credit terms: a minimum and maximum order amount and a standard discount.

**Used by:**
- [[../../04-forms/customer.md]] (`frmcustomers`) maintains it
- [[../../04-forms/custadd.md]] (`frmaddcustomer`) adds a customer from order entry
- [[../../04-forms/ordentry.md]] and [[../../04-forms/ordhist.md]] open it in their DataEnvironment
- `findcustomer` class in [[../../05-classes/tsgen.md]]
- Stored procedures `RemainingCredit()` and `ValOrder()` read `max_order_amt` and `min_order_amt`
- Views `CUSTOMER LISTING` ([[../../06-reports/listcust.md]]), `ORDERS VIEW` ([[../../06-reports/orders.md]]), `ORDER HISTORY`, `TOP25CUST` ([[../../06-reports/topcust.md]])

**Related docs:** [[../README.md]] (container, stored procedures, views)

Row count in the sample data: 92. DBC comment: "Customer Information".

## Schema

| # | Field | Type | Width | Dec | Null | Default | Field-valid expr | Comment |
|---|---|---|---|---|---|---|---|---|
| 1 | `customer_id` | Character (C) | 6 | 0 | no |  | `.NOT.EMPTY(customer_id)` → "Customer ID cannot be empty." | Customer ID |
| 2 | `company_name` | Character (C) | 40 | 0 | no |  | `.NOT.EMPTY(company_name)` → "Company name cannot be empty." | Company name (e.g. MJR Associates) |
| 3 | `contact_name` | Character (C) | 30 | 0 | no |  |  | Contact name (e.g. Bill Scott) |
| 4 | `contact_title` | Character (C) | 40 | 0 | no |  |  | Customer contact's title (e.g. President) |
| 5 | `address` | Character (C) | 60 | 0 | no |  |  | Customer's address (e.g. 1060 Main Street) |
| 6 | `city` | Character (C) | 15 | 0 | no |  |  | Customer's city (e.g. Bloomingdale) |
| 7 | `region` | Character (C) | 15 | 0 | no |  |  | Customer's region/state (e.g. CA) |
| 8 | `postal_code` | Character (C) | 10 | 0 | no |  |  | Customer's postal (zip) code |
| 9 | `country` | Character (C) | 15 | 0 | no |  |  | Customer Country |
| 10 | `phone` | Character (C) | 24 | 0 | no |  |  | Customer's phone number |
| 11 | `fax` | Character (C) | 24 | 0 | no |  |  | Customer's fax number |
| 12 | `max_order_amt` | Currency (Y) | 8 | 4 | no |  | `max_order_amt=>min_order_amt` → "Maximum order amount must be greater than or equal to minimum order amount." | Customer's maximum allowed order amount |
| 13 | `min_order_amt` | Currency (Y) | 8 | 4 | no |  | `min_order_amt<=max_order_amt` → "Minimum order amount must be less than or equal to maximum order amount." | Customer's minimum allowed order amount |
| 14 | `discount` | Numeric (N) | 2 | 0 | no | `0` |  | Customer's normal discount |
| 15 | `sales_region` | Character (C) | 4 | 0 | no |  |  | Customer's sales region |

## Triggers (from table header)

- Insert: none
- Update: `__ri_update_customer()`
- Delete: `__ri_delete_customer()`
- Table valid: none

The `__ri_*` triggers are generated referential-integrity code (see the container README). They enforce the relations listed below and contain no business rules.

## Indexes (.cdx tags)

| Tag | Type | Expression | For | Order |
|---|---|---|---|---|
| `company_na` | regular | `UPPER(COMPANY_NAME)` |  | asc |
| `customer_i` | primary | `CUSTOMER_ID` |  | asc |

Primary key tag: `customer_i`.

## Stored procedure references

- None from defaults or rules.

## Relations

- **Parent of** [[orders.md]] via child tag `customer_i`. RI: update cascade, delete restrict, insert restrict.

## Used by

See the header. Forms open this table through their DataEnvironment; reports reach it through the DBC views named above.

## Sample / notable rows

First 5 of 92 rows:

| customer_id | company_name | max_order_amt | min_order_amt | discount |
|---|---|---|---|---|
| ALFKI | Alfreds Futterkiste | 6300 | 2600 | 2 |
| ANATR | Ana Trujillo Emparedados y helados | 3500 | 1900 | 5 |
| ANTON | Antonio Moreno Taquería | 8500 | 1700 | 6 |
| AROUT | Around the Horn | 17100 | 0 | 1 |
| BERGS | Berglunds snabbköp | 28600 | 4900 | 0 |

## Notes

- `max_order_amt` and `min_order_amt` validate against **each other**. Either rule can fail when only one field is edited, and a rebuild must validate the pair together.
- `discount` is `N(2)` holding a whole-number percent. Every order total formula multiplies it by `.01`.
- `customer_id` has no default and its rule only requires non-empty. Sample IDs are five-letter Northwind codes such as `ALFKI`; the field is six wide.
- The credit check in `RemainingCredit()` sums **unpaid** orders and compares against `max_order_amt`. So `max_order_amt` is a credit limit, not a per-order maximum, despite the comment.
