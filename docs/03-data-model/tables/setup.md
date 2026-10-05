# SETUP

| Source file | Type | Path |
|---|---|---|
| `setup.dbf` | Table in `tastrade.dbc` | `data/tastrade.dc2` (table block `SETUP`) |

**Purpose:** The primary-key generator. One row per table (or counter) holding the next key value, consumed by `NewID()`.

**Used by:**
- Stored procedure `NewID()` only. No form opens it directly

**Related docs:** [[../README.md]] (container, stored procedures, views)

Row count in the sample data: 7. DBC comment: "Holds unique keys".

## Schema

| # | Field | Type | Width | Dec | Null | Default | Field-valid expr | Comment |
|---|---|---|---|---|---|---|---|---|
| 1 | `key_name` | Character (C) | 20 | 0 | no |  |  | Name of table's primary key |
| 2 | `value` | Character (C) | 6 | 0 | no |  |  | The next unique key |

## Triggers (from table header)

- Insert: none
- Update: none
- Delete: none
- Table valid: none

## Indexes (.cdx tags)

| Tag | Type | Expression | For | Order |
|---|---|---|---|---|
| `key_name` | regular | `KEY_NAME` |  | asc |

## Stored procedure references

- None from defaults or rules.

## Relations

- None. This table is not in any persistent relation.

## Used by

See the header. Forms open this table through their DataEnvironment; reports reach it through the DBC views named above.

## Sample / notable rows

All 7 rows:

| key_name | value |
|---|---|
| SUPPLIER | 30 |
| PRODUCTS | 78 |
| EMPLOYEE | 16 |
| CATEGORY | 9 |
| SHIPPERS | 4 |
| ORDERS | 1138 |
| ORDER_NUMBER | 1138 |

## Notes

- `value` is `C(6)`, so keys are zero-padded strings and the counter tops out at 999999. `NewID()` increments with `STR(VAL(...) + 1, LEN(setup.value))`.
- **NOTE:** `NewID()` sets `SET REPROCESS TO AUTOMATIC` and `RLOCK()`s the row, so every insert into any keyed table serializes on this one record. Under load this is the contention point.
- The rows named after tables use the DBC long name (`ORDERS`, not `orditems`). `NewID()` looks up `UPPER(ALIAS())`, so calling it from an alias that differs from the DBC name returns an empty ID.
- Not part of any relation; no triggers.
