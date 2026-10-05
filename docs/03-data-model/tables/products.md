# PRODUCTS

| Source file | Type | Path |
|---|---|---|
| `products.dbf` | Table in `tastrade.dbc` | `data/tastrade.dc2` (table block `PRODUCTS`) |

**Purpose:** The product catalogue with pricing, cost, stock levels, and links to the supplier and category.

**Used by:**
- [[../../04-forms/product.md]] (`frmproducts`) maintains it
- [[../../04-forms/ordentry.md]] and [[../../04-forms/ordhist.md]] open it as a lookup
- Views `PRODUCT LISTING` ([[../../06-reports/listprod.md]]), `ORDER HISTORY LINE ITEMS`, `ORDERS VIEW`

**Related docs:** [[../README.md]] (container, stored procedures, views)

Row count in the sample data: 77. DBC comment: "Product Inventory Information".

## Schema

| # | Field | Type | Width | Dec | Null | Default | Field-valid expr | Comment |
|---|---|---|---|---|---|---|---|---|
| 1 | `product_id` | Character (C) | 6 | 0 | no | `newid()` |  | Internal product ID |
| 2 | `supplier_id` | Character (C) | 6 | 0 | no |  |  | ID of supplier of this product |
| 3 | `category_id` | Character (C) | 6 | 0 | no |  |  | ID of category to which this product belongs |
| 4 | `product_name` | Character (C) | 40 | 0 | no |  | `.NOT.EMPTY(product_name)` → "Product name cannot be empty." | Full name of product |
| 5 | `english_name` | Character (C) | 50 | 0 | no |  |  | English name of product |
| 6 | `quantity_in_unit` | Character (C) | 20 | 0 | no |  |  | Quantity in each unit  |
| 7 | `unit_price` | Currency (Y) | 8 | 4 | no |  |  | Unit price |
| 8 | `unit_cost` | Currency (Y) | 8 | 4 | no |  |  | Unit cost |
| 9 | `units_in_stock` | Numeric (N) | 12 | 3 | no | `0` |  | Number of units in stock |
| 10 | `units_on_order` | Numeric (N) | 12 | 3 | no | `0` |  | Number of units on order |
| 11 | `reorder_level` | Numeric (N) | 12 | 3 | no | `0` |  | Reorder level |
| 12 | `discontinued` | Logical (L) | 1 | 0 | no |  |  | True if product has been discontinued |

## Triggers (from table header)

- Insert: `__ri_insert_products()`
- Update: `__ri_update_products()`
- Delete: `__ri_delete_products()`
- Table valid: none

The `__ri_*` triggers are generated referential-integrity code (see the container README). They enforce the relations listed below and contain no business rules.

## Indexes (.cdx tags)

| Tag | Type | Expression | For | Order |
|---|---|---|---|---|
| `category_i` | regular | `CATEGORY_ID` |  | asc |
| `supplier_i` | regular | `SUPPLIER_ID` |  | asc |
| `product_na` | regular | `UPPER(PRODUCT_NAME)` |  | asc |
| `product_id` | primary | `PRODUCT_ID` |  | asc |

Primary key tag: `product_id`.

## Stored procedure references

- `NewID()` — default of `product_id`. Quoted and explained in [[../README.md]].

## Relations

- **Parent of** [[order_line_items.md]] via child tag `product_id`. RI: update cascade, delete restrict, insert restrict.
- **Child of** [[category.md]] on `category_i` → parent tag `category_i`. RI: update cascade, delete restrict, insert restrict.
- **Child of** [[supplier.md]] on `supplier_i` → parent tag `supplier_i`. RI: update cascade, delete restrict, insert restrict.

## Used by

See the header. Forms open this table through their DataEnvironment; reports reach it through the DBC views named above.

## Notes

- `units_in_stock`, `units_on_order`, and `reorder_level` are `N(12,3)`: stock is tracked in fractional units. Nothing in the DBC adjusts stock when an order is saved; check the order entry form before assuming inventory is maintained.
- `unit_price` and `unit_cost` are Currency (`Y`). `unit_price` is the value copied onto order lines.
- The insert trigger is RI only: `supplier_id` and `category_id` must exist.
- `english_name` exists because the sample product names are in several languages.
