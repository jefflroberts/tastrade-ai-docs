# ORDER_LINE_ITEMS

| Source file | Type | Path |
|---|---|---|
| `orditems.dbf` | Table in `tastrade.dbc` | `data/tastrade.dc2` (table block `ORDER_LINE_ITEMS`) |

**Purpose:** One row per product on an order, with the quantity and the unit price captured at order time.

**Used by:**
- [[../../04-forms/ordentry.md]] (`frmorderentry`) edits it in a grid
- [[../../04-forms/ordhist.md]] (`frmordhistory`) reads it
- Stored procedures `ValOrder()`, `CalcMinOrdAmount()`, `CalcOrdTotal()`, `RemainingCredit()`
- Views `ORDER HISTORY LINE ITEMS`, `ORDERS VIEW`, `ORDER HISTORY`, `ORDERTOTAL`, `SALES SUMMARY`, `SALES DETAIL`

**Related docs:** [[../README.md]] (container, stored procedures, views)

Row count in the sample data: 2821. DBC comment: "Order Line Item Information".

## Schema

| # | Field | Type | Width | Dec | Null | Default | Field-valid expr | Comment |
|---|---|---|---|---|---|---|---|---|
| 1 | `order_id` | Character (C) | 6 | 0 | no |  |  | Internal order ID |
| 2 | `product_id` | Character (C) | 6 | 0 | no |  |  | Internal product ID |
| 3 | `unit_price` | Currency (Y) | 8 | 4 | no |  |  | Unit price of product |
| 4 | `quantity` | Numeric (N) | 12 | 3 | no | `1` |  | Quantity |

## Triggers (from table header)

- Insert: `__ri_insert_order_line_items()`
- Update: `__ri_update_order_line_items()`
- Delete: none
- Table valid: none

The `__ri_*` triggers are generated referential-integrity code (see the container README). They enforce the relations listed below and contain no business rules.

## Indexes (.cdx tags)

| Tag | Type | Expression | For | Order |
|---|---|---|---|---|
| `product_id` | regular | `PRODUCT_ID` |  | asc |
| `order_id` | regular | `ORDER_ID` |  | asc |

## Stored procedure references

- None from defaults or rules.

## Relations

- **Child of** [[products.md]] on `product_id` → parent tag `product_id`. RI: update cascade, delete restrict, insert restrict.
- **Child of** [[orders.md]] on `order_id` → parent tag `order_id`. RI: update cascade, delete cascade, insert restrict.

## Used by

See the header. Forms open this table through their DataEnvironment; reports reach it through the DBC views named above.

## Notes

- **NOTE:** No primary key and no candidate key. The same product can appear twice on one order and nothing in the DBC prevents it. Only the two foreign-key tags exist.
- `unit_price` is copied from `products.unit_price` when the line is entered (see the order entry form), so later price changes do not alter historical orders.
- `quantity` is `N(12,3)`, allowing fractional quantities, with default 1.
- There is no delete trigger; deletes are only ever caused by the cascade from ORDERS.
- The DBF is `orditems.dbf`; the DBC long name is `ORDER_LINE_ITEMS`. Code uses both spellings.
