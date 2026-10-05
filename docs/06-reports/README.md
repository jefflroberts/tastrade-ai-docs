# Reports

Thirteen reports in `reports/*.frx`, all documented from their FoxBin2PRG twins with every band, object, expression, cursor, and the saved printer environment. Ten are run from the report picker [[../04-forms/reports.md]] by the rows of `data/repolist.dbf`; three are printed by the self-documentation forms. There are no labels (`.lbx`).

| File | Title | Data | Run from | Doc |
|---|---|---|---|---|
| `reports/listcat.frx` | Category Listing | `CATEGORY LISTING` view | picker (LIST) | [[listcat.md]] |
| `reports/listcust.frx` | Customer Listing | `CUSTOMER LISTING` view | picker (LIST) | [[listcust.md]] |
| `reports/listempl.frx` | Employee Listing | `EMPLOYEE LISTING` view, `?cTitle` from `gettitle` | picker (LIST) | [[listempl.md]] |
| `reports/listprod.frx` | Product Listing | `PRODUCT LISTING` view | picker (LIST) | [[listprod.md]] |
| `reports/listship.frx` | Shipper Listing | `SHIPPER LISTING` view | picker (LIST) | [[listship.md]] |
| `reports/listsupp.frx` | Supplier Listing | `SUPPLIER LISTING` view | picker (LIST) | [[listsupp.md]] |
| `reports/orders.frx` | Invoices | `ORDERS VIEW` view, dates from `getinv` | picker (REPO) | [[orders.md]] |
| `reports/salesdet.frx` | Sales Detail | `SALES DETAIL` view | picker (REPO) | [[salesdet.md]] |
| `reports/salessum.frx` | Sales Summary | `SALES SUMMARY` view | picker (REPO) | [[salessum.md]] |
| `reports/topcust.frx` | Top 25 Customers | `TOP25CUST` view (+3 unused cursors) | picker (REPO) | [[topcust.md]] |
| `reports/behindsc.frx` | Behind the Scenes | form's `behindsc` alias, current record | `frmbehindsc` Print | [[behindsc.md]] |
| `reports/casestdy.frx` | Case Study | `behindsc.dbf`, filter `*Case Study` | `frmcasestudy` Print (unreachable) | [[casestdy.md]] |
| `reports/viewcode.frx` | Code Report | `viewcode` cursor made by `frmbehindsc` | `frmviewcode` Print | [[viewcode.md]] |

## How the reports get their data

Twelve of the thirteen declare a cursor in their data environment; the listings and sales reports open a DBC view, the two self-documentation prints open or reuse the free table `behindsc.dbf`, and `viewcode` has no cursor and reads a cursor its calling form creates. Two reports (`listempl`, `orders`) turn `AutoOpenTables` off and run a parameter dialog from the data environment's `Init` before opening the view, passing the values as private variables that the view's `?parameters` pick up. The invoice's `Init` has `#INCLUDE "INCLUDE\TASTRADE.H"`; the employee listing's does not, so its "Nothing to print" message box refers to undefined names and errors instead.

Cursor sources are stored relative to the `reports\` folder (`..\data\tastrade.dbc`); `progs/main.prg` sets the default directory to the application root and `SET PATH TO ... DATA ...`, which is how they resolve at run time.

## Layout conventions

Every report is on Letter paper (orientation left to the printer) in Arial 12 with a page header carrying the "Tasmanian Traders" wordmark (a blue 24-point "T" before "asmanian" and "raders"), the logo `bitmaps/ttradesm.bmp`, a rule, and Page / Date fields; `salesdet` omits the logo and page fields, and the invoice puts all of it in the group header so it repeats per order. In the listings, column headings sit in a grey box at the bottom of the page header. Coordinates in the docs are inches from the top-left of the band; the twins store 1/10000 inch in designer space, where each band is followed by a 20-pixel band bar.

## Findings

- **Every report carries a saved printer environment.** Four devices: `\\MSPRINT32\2/1MC PRIVJ 157.56.32.242` (seven reports), `LaserNT` (three, plus the text half of `casestdy`), an HP LaserJet 4Si on `\\msprint32\privj` (`viewcode`, and the binary half of `casestdy`), and `\\RED-PRN-16\CORP0007` (`orders`). VFP tries the saved device first on every run.
- **The invoice is the seventh copy of the order total formula** (subtotal, minus discount percent, plus freight), see [[orders.md]].
- **The three sales reports do not reconcile**: `salessum` and `salesdet` sum unit prices without quantity; `topcust` uses the full total through `ORDERTOTAL`.
- **Three dead cursors** in `topcust`; **one dead report**, `casestdy`, reachable only from a form nothing runs.
- **Two reports depend on VFP's automatic column names** (`exp_1`, `sum_unit_price`, `company_name_a`, `company_name_b`).
- **A latent runtime error** in the employee listing when the chosen title has no employees (missing `#INCLUDE`).
- **Cost printed beside price** on the product listing, with no user-level check.
- **Bill To postal code has no separating space** on the invoice.
- The FoxBin2PRG twins expose everything above; nothing needed the binary `.frx`, though `tools/extract_frx.py` reproduces the coordinates from it.
