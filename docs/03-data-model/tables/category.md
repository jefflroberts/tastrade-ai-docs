# CATEGORY

| Source file | Type | Path |
|---|---|---|
| `category.dbf` | Table in `tastrade.dbc` | `data/tastrade.dc2` (table block `CATEGORY`) |

**Purpose:** Lookup table of the eight product categories (Beverages, Condiments, ...) that every product belongs to.

**Used by:**
- [[../../04-forms/category.md]] (`frmcategory`) maintains it
- [[../../04-forms/product.md]] (`frmproducts`) opens it as a lookup
- View `CATEGORY LISTING`, printed by [[../../06-reports/listcat.md]]

**Related docs:** [[../README.md]] (container, stored procedures, views)

Row count in the sample data: 8. DBC comment: "Product Category Lookup Table".

## Schema

| # | Field | Type | Width | Dec | Null | Default | Field-valid expr | Comment |
|---|---|---|---|---|---|---|---|---|
| 1 | `category_id` | Character (C) | 6 | 0 | no | `newid()` |  | Internal category ID |
| 2 | `category_name` | Character (C) | 25 | 0 | no |  | `.NOT.EMPTY(category_name)` → "Category name cannot be empty." | Category name (caption `Name:`) |
| 3 | `description` | Memo (M) | 4 | 0 | no |  |  | Category description |
| 4 | `picture_file` | Memo (M) | 4 | 0 | no |  |  |  |
| 5 | `picture` | General (G) | 4 | 0 | no |  |  | Category picture |

## Triggers (from table header)

- Insert: none
- Update: `__ri_update_category()`
- Delete: `__ri_delete_category()`
- Table valid: none

The `__ri_*` triggers are generated referential-integrity code (see the container README). They enforce the relations listed below and contain no business rules.

## Indexes (.cdx tags)

| Tag | Type | Expression | For | Order |
|---|---|---|---|---|
| `category_i` | primary | `CATEGORY_ID` |  | asc |
| `category_n` | regular | `UPPER(CATEGORY_NAME)` |  | asc |

Primary key tag: `category_i`.

## Stored procedure references

- `NewID()` — default of `category_id`. Quoted and explained in [[../README.md]].

## Relations

- **Parent of** [[products.md]] via child tag `category_i`. RI: update cascade, delete restrict, insert restrict.

## Used by

See the header. Forms open this table through their DataEnvironment; reports reach it through the DBC views named above.

## Sample / notable rows

All 8 rows:

| category_id | category_name |
|---|---|
| 1 | Beverages |
| 2 | Condiments |
| 3 | Confections |
| 4 | Dairy Products |
| 5 | Grains/Cereals |
| 6 | Meat/Poultry |
| 7 | Produce |
| 8 | Seafood |

## Notes

- `picture` is a **General** (OLE) field and `picture_file` a memo holding the file name it was loaded from. General fields have no equivalent outside VFP; a rebuild must store the image file instead.
- `category_name` carries the only field **Caption** in the whole DBC (`Name:`). Nothing else uses captions.
- `category_id` defaults to `newid()`, so the stored procedure runs on every APPEND, even outside the application.
