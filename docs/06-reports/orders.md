# Invoices (orders.frx)

| Source file | Type | Path |
|---|---|---|
| `orders.frx` | Report | `reports/orders.fr2` |

**Purpose:** Prints one invoice per order for a date range: ship-to and bill-to blocks, line items, subtotal, freight, discount, and total, from the `ORDERS VIEW` view after the `getinv` dialog supplies the range.

**Used by:**
- The report picker [[../04-forms/reports.md]] (`frmreports`, from the File menu's "Print Reports ..."), row `ORDERS` / "Invoices" of type `REPO` in `data/repolist.dbf`.

**Related docs:** [[../04-forms/getinv.md]] (the parameter dialog), [[../03-data-model/README.md]] (`ORDERS VIEW`), [[../03-data-model/tables/orders.md]], [[../03-data-model/tables/order_line_items.md]], [[../04-forms/reports.md]], [[../04-forms/ordentry.md]] (the same total on screen), [[README.md]].

The most elaborate report in the sample: a data environment with code, a group with a page break, two report variables, and 66 records. The page header is empty; everything a page needs sits in the group header, so each order starts a new page with its own heading.

## DataEnvironment

| Cursor | Alias | Source | Database | Filter |
|---|---|---|---|---|
| `Cursor1` | `orders_view` | `orders view` | `..\data\tastrade.dbc` |  |

Properties: `AutoOpenTables = .F.`, `AutoCloseTables = .F.`, `InitialSelectedAlias = "orders_view"`.

The `fontface` attribute of the data environment record holds the VFP 9 compiler's include-file table (`..\include\tastrade.h`, `foxpro.h`, `strings.h`) with an absolute path into the VFP install: build noise from the 2026 rebuild, not source.

DataEnvironment `Init`:

Runs the date dialog `LINKED` (so it is released with the object), reads the result, and copies the dates into `dDateFrom` and `dDateTo`. Those are not `LOCAL`, on purpose: they are private variables that the view's `?dDateFrom` and `?dDateTo` parameters read when `OpenTables()` runs. **NOTE:** `WEXIST("Project Manager")` switches to `HOME() + "Samples\Tastrade\"`. The `#INCLUDE` here is why the message constants resolve; [[listempl.md]] lacks it.

```foxpro
#DEFINE C_TASTRADEDIR_LOC	"Samples\Tastrade\"		&& Location of Tastrade, off of HOME()
#INCLUDE "INCLUDE\TASTRADE.H"

LOCAL loGetInvoice, ;
      llContinue
IF WEXIST("Project Manager")
*-- ... 20 more lines of Microsoft's Tastrade source omitted; see `DataEnvironment` in your own copy of Tastrade.
```

DataEnvironment `Destroy`:

```foxpro
This.CloseTables
```

## Bands & content

The wordmark, logo, and Page / Date objects are in the group header, not the page header, so they print once per invoice.

### Page Header (0.00 in)

Empty.

### Group Header 1 (2.82 in)

Band flags: group on `Order_number`; new page for each group.

| Kind | Top, left (in) | Size w×h (in) | Content | Format | Font | Options |
|---|---|---|---|---|---|---|
| label | 0.01, 7.03 | 0.85×0.26 | "INVOICE" |  | Arial 16 bold |  |
| picture | 0.02, 0.25 | 0.86×0.92 | picture `..\bitmaps\ttradesm.bmp` |  |  | file; clip; comment "(c) Microsoft Corporation 1995" |
| field | 0.41, 7.08 | 0.82×0.22 | `order_number` | `@J` | Arial 12 bold |  |
| label | 0.42, 5.86 | 1.12×0.21 | "Order Number" |  | Arial 12 bold |  |
| label | 0.43, 1.15 | 0.21×0.40 | "T" |  | Arial 24 bold, RGB(0,0,255) |  |
| label | 0.43, 2.76 | 0.21×0.40 | "T" |  | Arial 24 bold, RGB(0,0,255) |  |
| label | 0.48, 1.31 | 1.33×0.34 | "asmanian" |  | Arial 20 bold |  |
| label | 0.48, 2.93 | 0.88×0.34 | "raders\n" |  | Arial 20 bold |  |
| label | 0.67, 5.86 | 1.05×0.21 | "Date Ordered" |  | Arial 12 bold |  |
| field | 0.67, 7.08 | 0.82×0.22 | `order_date` |  | Arial 12 bold |  |
| line | 0.96, 0.01 | 8.12×0.01 | line |  |  |  |
| rectangle | 1.01, 0.10 | 0.84×0.22 | grey fill |  |  |  |
| rectangle | 1.01, 4.65 | 0.74×0.22 | grey fill |  |  |  |
| label | 1.02, 0.16 | 0.61×0.21 | "Ship To" |  | Arial 12 bold |  |
| label | 1.02, 4.74 | 0.50×0.21 | "Bill To" |  | Arial 12 bold |  |
| field | 1.29, 0.10 | 2.98×0.21 | `ship_to_name` |  | Arial 12 |  |
| field | 1.29, 4.64 | 3.24×0.21 | `company_name_a` |  | Arial 12 |  |
| field | 1.51, 0.10 | 2.98×0.21 | `ship_to_address` |  | Arial 12 |  |
| field | 1.51, 4.64 | 3.23×0.21 | `address` |  | Arial 12 |  |
| field | 1.73, 0.10 | 2.98×0.21 | `ALLTRIM(ship_to_city) + ", " + ALLTRIM(ship_to_region) + " " + ship_to_postal_code` |  | Arial 12 |  |
| field | 1.73, 4.64 | 3.19×0.21 | `ALLTRIM(city) + ", " + ALLTRIM(region) + postal_code` |  | Arial 12 |  |
| field | 1.95, 0.10 | 2.03×0.21 | `ship_to_country` |  | Arial 12 |  |
| field | 1.95, 4.64 | 2.03×0.21 | `country` |  | Arial 12 |  |
| rectangle | 2.22, 0.10 | 0.84×0.22 | grey fill |  |  |  |
| field | 2.23, 1.04 | 2.25×0.21 | `company_name_b` |  | Arial 12 |  |
| label | 2.24, 0.16 | 0.66×0.21 | "Ship Via" |  | Arial 12 bold |  |
| rectangle | 2.59, 0.00 | 7.93×0.23 | grey fill |  |  |  |
| label | 2.60, 0.10 | 1.14×0.21 | "Product Name" |  | Arial 12 bold |  |
| label | 2.60, 4.65 | 0.67×0.21 | "Quantity" |  | Arial 12 bold |  |
| label | 2.60, 5.82 | 0.77×0.21 | "Unit Price" |  | Arial 12 bold |  |
| label | 2.60, 6.98 | 0.80×0.21 | "Extension" |  | Arial 12 bold |  |

### Detail (0.23 in)

| Kind | Top, left (in) | Size w×h (in) | Content | Format | Font | Options |
|---|---|---|---|---|---|---|
| field | 0.00, 0.10 | 4.04×0.21 | `product_name` |  | Arial 12 |  |
| field | 0.00, 4.19 | 1.17×0.21 | `quantity` | `999999999.99` | Arial 12 | right-aligned |
| field | 0.00, 5.45 | 1.15×0.21 | `unit_price` | `99999.99` | Arial 12 | right-aligned |
| field | 0.00, 6.66 | 1.24×0.21 | `quantity * unit_price` | `9999999.99` | Arial 12 | right-aligned |

### Group Footer 1 (1.39 in)

Band flags: new page for each group.

| Kind | Top, left (in) | Size w×h (in) | Content | Format | Font | Options |
|---|---|---|---|---|---|---|
| rectangle | 0.35, 5.21 | 1.31×1.04 | grey fill |  |  |  |
| label | 0.39, 5.71 | 0.76×0.21 | "Sub Total" |  | Arial 12 bold |  |
| field | 0.39, 6.64 | 1.26×0.21 | `vsubtotal` | `999999999.99` | Arial 12 | right-aligned |
| label | 0.65, 5.89 | 0.56×0.21 | "Freight" |  | Arial 12 bold |  |
| field | 0.65, 6.64 | 1.26×0.21 | `freight` | `99999.99` | Arial 12 | right-aligned |
| field | 0.90, 5.31 | 0.23×0.21 | `discount` |  | Arial 12 | right-aligned |
| label | 0.91, 5.56 | 0.17×0.21 | "%" |  | Arial 12 bold |  |
| label | 0.91, 5.77 | 0.72×0.21 | "Discount" |  | Arial 12 bold |  |
| field | 0.91, 6.64 | 1.26×0.21 | `vDiscount` | `9999999.99` | Arial 12 | right-aligned |
| label | 1.17, 6.04 | 0.40×0.21 | "Total" |  | Arial 12 bold |  |
| field | 1.17, 6.64 | 1.26×0.21 | `vSubTotal + freight - vDisCount` | `999999999.99` | Arial 12 | right-aligned |

### Page Footer (0.93 in)

| Kind | Top, left (in) | Size w×h (in) | Content | Format | Font | Options |
|---|---|---|---|---|---|---|
| line | 0.31, 0.00 | 8.15×0.01 | line |  |  |  |
| label | 0.37, 0.36 | 3.23×0.20 | "We thank you for your patronage" |  | Courier New 12 bold italic, RGB(0,128,128) |  |

## Report variables

| Name | Value to store | Initial value | Calculate | Reset | Release after report |
|---|---|---|---|---|---|
| `vSubTotal` | `quantity * MTON(unit_price)` | `0` | Sum | Group 1 | yes |
| `vDisCount` | `iif(discount > 0, vSubTotal * (discount / 100), 0)` | `0` | nothing | End of report | yes |

The invoice arithmetic, quoted from the variables and the total field:

```foxpro
vSubTotal = quantity * MTON(unit_price)        && Calculate: Sum, reset per order group
vDisCount = iif(discount > 0, vSubTotal * (discount / 100), 0)
Total     = vSubTotal + freight - vDisCount
```

Subtotal is the sum of extended line prices for the order; discount is a percentage of that subtotal; total adds freight. This is the **seventh copy of the order total formula** in the sample (two stored procedures, two views, one stored procedure with freight, the order entry screen, and this report). It agrees with the `ORDERTOTAL` view and the order entry screen.

## Page setup

- Orientation: not stored (`ORIENTATION=0`, printer default)
- Paper size: 1 (Letter); copies: 1; duplex 1
- Print quality: 600 dpi
- Saved printer environment: driver `winspool`, device `\\RED-PRN-16\CORP0007 44E/MC3 172.30.168.9`, output `Ne00:`

**NOTE:** the saved environment names `\\RED-PRN-16\CORP0007`, a Microsoft print server (IP 172.30.168.9) captured when the report was last saved in 2001. VFP tries it first on every run.

## Triggered from

- `forms/reports.sc2` `cmdRun.Click`: `REPORT FORM (lcSeleRepo) PREVIEW`, or `TO PRINTER NOCONSOLE` after `PRINTSTATUS()`, or `TO FILE <stem>.TXT ASCII`, where `lcSeleRepo` is `REPORTS\ORDERS.FRX`.
- The ASCII output drops lines, boxes, and pictures.

## Notes

- **Bill To city line has no space before the postal code**: `ALLTRIM(city) + ", " + ALLTRIM(region) + postal_code`, while the Ship To line has `+ " " + ship_to_postal_code`.
- **Column names are VFP's automatic ones.** `company_name_a` (customer) and `company_name_b` (shipper) exist because `ORDERS VIEW` selects two `company_name` columns; a rebuilt view must keep those names or the report breaks.
- **`MTON()` in the variable, not in the field.** The subtotal variable converts the currency unit price to numeric; the Extension field prints `quantity * unit_price` directly.
- **`vDisCount` resets at end of report** but has no calculation, so it is simply re-evaluated on every record from the running subtotal; the reset setting is moot.
- **`order_number` uses format `@J`** (right-justify); money fields use `99999.99` to `999999999.99` masks.
- **Page footer** prints "We thank you for your patronage" in Courier New bold italic, teal, under a rule.
- **Empty page header (0 in)** with `pagebreak` on both the group header and footer.
- **The Escape key confirms** in the date dialog, see [[../04-forms/getinv.md]].
