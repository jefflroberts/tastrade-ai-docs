# SHIPPERS

| Source file | Type | Path |
|---|---|---|
| `shippers.dbf` | Table in `tastrade.dbc` | `data/tastrade.dc2` (table block `SHIPPERS`) |

**Purpose:** Lookup table of the three shipping companies an order can be sent by.

**Used by:**
- [[../../04-forms/shipper.md]] (`frmshippers`) maintains it
- [[../../04-forms/ordentry.md]] opens it as a lookup
- Views `SHIPPER LISTING` ([[../../06-reports/listship.md]]), `ORDERS VIEW`

**Related docs:** [[../README.md]] (container, stored procedures, views)

Row count in the sample data: 3. DBC comment: "Shipper Lookup Table".

## Schema

| # | Field | Type | Width | Dec | Null | Default | Field-valid expr | Comment |
|---|---|---|---|---|---|---|---|---|
| 1 | `shipper_id` | Character (C) | 6 | 0 | no | `newid()` |  | Internal shipper ID |
| 2 | `company_name` | Character (C) | 40 | 0 | no |  | `.NOT.EMPTY(company_name)` → "Company name cannot be empty." | Shipper company name |

## Triggers (from table header)

- Insert: none
- Update: `__ri_update_shippers()`
- Delete: `__ri_delete_shippers()`
- Table valid: none

The `__ri_*` triggers are generated referential-integrity code (see the container README). They enforce the relations listed below and contain no business rules.

## Indexes (.cdx tags)

| Tag | Type | Expression | For | Order |
|---|---|---|---|---|
| `company_na` | regular | `COMPANY_NAME` |  | asc |
| `shipper_id` | primary | `SHIPPER_ID` |  | asc |

Primary key tag: `shipper_id`.

## Stored procedure references

- `NewID()` — default of `shipper_id`. Quoted and explained in [[../README.md]].

## Relations

- **Parent of** [[orders.md]] via child tag `shipper_id`. RI: update cascade, delete restrict, insert restrict.

## Used by

See the header. Forms open this table through their DataEnvironment; reports reach it through the DBC views named above.

## Sample / notable rows

All 3 rows:

| shipper_id | company_name |
|---|---|
| 1 | Speedy Express |
| 2 | United Package |
| 3 | Federal Shipping |

## Notes

- Both tags exist so the order entry combo can sort by name while the relation seeks by ID.
