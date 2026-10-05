# repolist

| Source file | Type | Path |
|---|---|---|
| `repolist.dbf` | Free table (outside `tastrade.dbc`) | `data/repolist.db2` |

**Purpose:** The report picker's list: one row per report the user may run, with its file stem, display name, and whether it is a report or a listing.

**Used by:**
- [[../../04-forms/reports.md]] (`frmreports`): DataEnvironment cursor, `SET FILTER TO ctype = 'REPO'` or `'LIST'` by the option group, list box rows from `cfullname, cdosname`, and `REPORT FORM REPORTS\<cdosname>.FRX`.

**Related docs:** [[../README.md]], [[../../06-reports/README.md]] (the ten reports it names and the three it does not), [[behindsc.md]], [[ttrade.md]].

Row count in the sample data: 10. No database container, so no long field names, comments, defaults, rules, or triggers; what follows is all there is.

## Schema

| # | Field | Type | Width | Dec | Null |
|---|---|---|---|---|---|
| 1 | `cdosname` | Character (C) | 8 | 0 | no |
| 2 | `cfullname` | Character (C) | 30 | 0 | no |
| 3 | `ctype` | Character (C) | 4 | 0 | no |

## Triggers (from table header)

- None: no insert, update, or delete trigger, no table rule. Free tables cannot carry them.

## Indexes (.cdx tags)

| Tag | Type | Expression | For | Order |
|---|---|---|---|---|
| `cdosname` | regular | `CDOSNAME` |  | asc |
| `cfullname` | regular | `CFULLNAME` |  | asc |
| `ctype` | regular | `CTYPE` |  | asc |

## Stored procedure references

- None.

## Relations

- None. Free tables take part in no persistent relation.

## Used by

See the header. Read-only; the sample's own note says the table "is considered metadata, and does not pertain to the data maintained by Tasmanian Traders", which is why it is outside the DBC.

## Sample / notable rows

All 10 rows:

| cdosname | cfullname | ctype | Report doc |
|---|---|---|---|
| SALESSUM | Sales Summary | REPO | [[../../06-reports/salessum.md]] |
| SALESDET | Sales Detail | REPO | [[../../06-reports/salesdet.md]] |
| ORDERS | Invoices | REPO | [[../../06-reports/orders.md]] |
| LISTCAT | Category Listing | LIST | [[../../06-reports/listcat.md]] |
| LISTCUST | Customer Listing | LIST | [[../../06-reports/listcust.md]] |
| LISTEMPL | Employee Listing | LIST | [[../../06-reports/listempl.md]] |
| LISTPROD | Product Listing | LIST | [[../../06-reports/listprod.md]] |
| LISTSHIP | Shipper Listing | LIST | [[../../06-reports/listship.md]] |
| LISTSUPP | Supplier Listing | LIST | [[../../06-reports/listsupp.md]] |
| TOPCUST | Top 25 Customers | REPO | [[../../06-reports/topcust.md]] |

## Notes

- **The picker is data-driven**: a report is added or hidden by editing this table; a stem with no `.frx` shows "Report file not found." No row is validated against the `reports/` folder.
- **Three reports are not listed** (`behindsc.frx`, `casestdy.frx`, `viewcode.frx`): the self-documentation prints, run only from their forms ([[../../06-reports/README.md]]).
- **Three tags**, one per column, though the form filters and lists without setting an order.
- **`cdosname` is 8 characters**: an 8.3 file-name assumption from 1995, still true of every report stem.
