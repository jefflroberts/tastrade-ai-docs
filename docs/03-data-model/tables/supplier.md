# SUPPLIER

| Source file | Type | Path |
|---|---|---|
| `supplier.dbf` | Table in `tastrade.dbc` | `data/tastrade.dc2` (table block `SUPPLIER`) |

**Purpose:** The companies that supply products.

**Used by:**
- [[../../04-forms/supplier.md]] (`frmsuppliers`) maintains it
- [[../../04-forms/product.md]] opens it as a lookup
- View `SUPPLIER LISTING`, printed by [[../../06-reports/listsupp.md]]

**Related docs:** [[../README.md]] (container, stored procedures, views)

Row count in the sample data: 29. DBC comment: "Inventory Supplier Information".

## Schema

| # | Field | Type | Width | Dec | Null | Default | Field-valid expr | Comment |
|---|---|---|---|---|---|---|---|---|
| 1 | `supplier_id` | Character (C) | 6 | 0 | no | `newid()` |  | Internal supplier ID |
| 2 | `company_name` | Character (C) | 40 | 0 | no |  | `.NOT.EMPTY(company_name)` → "Company name cannot be empty." | Supplier's company name |
| 3 | `contact_name` | Character (C) | 30 | 0 | no |  |  | Contact's name |
| 4 | `contact_title` | Character (C) | 40 | 0 | no |  |  | Contact's title |
| 5 | `address` | Character (C) | 60 | 0 | no |  |  | Supplier's address |
| 6 | `city` | Character (C) | 15 | 0 | no |  |  | Supplier's city |
| 7 | `region` | Character (C) | 15 | 0 | no |  |  | Supplier region |
| 8 | `postal_code` | Character (C) | 10 | 0 | no |  |  | Supplier's postal (zip) code |
| 9 | `country` | Character (C) | 15 | 0 | no |  |  | Supplier's country |
| 10 | `phone` | Character (C) | 24 | 0 | no |  |  | Supplier's phone number |
| 11 | `fax` | Character (C) | 24 | 0 | no |  |  | Supplier's fax number |

## Triggers (from table header)

- Insert: none
- Update: `__ri_update_supplier()`
- Delete: `__ri_delete_supplier()`
- Table valid: none

The `__ri_*` triggers are generated referential-integrity code (see the container README). They enforce the relations listed below and contain no business rules.

## Indexes (.cdx tags)

| Tag | Type | Expression | For | Order |
|---|---|---|---|---|
| `contact_na` | regular | `CONTACT_NAME` |  | asc |
| `company_na` | regular | `UPPER(COMPANY_NAME)` |  | asc |
| `supplier_i` | primary | `SUPPLIER_ID` |  | asc |

Primary key tag: `supplier_i`.

## Stored procedure references

- `NewID()` — default of `supplier_id`. Quoted and explained in [[../README.md]].

## Relations

- **Parent of** [[products.md]] via child tag `supplier_i`. RI: update cascade, delete restrict, insert restrict.

## Used by

See the header. Forms open this table through their DataEnvironment; reports reach it through the DBC views named above.

## Notes

- `contact_na` is the only name index in the DBC that is **not** wrapped in `UPPER()`; seeks on it are case-sensitive.
