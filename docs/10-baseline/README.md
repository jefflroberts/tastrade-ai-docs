# Screenshot baseline

What the VFP 9 build of Tastrade shows on screen and prints, captured from the running `tastrade.exe` on 2026-09-09 so a rebuild can be compared against it. The images are in `baseline/` at the repo root; this page is the index. Every row below was written by the capture run itself (`baseline/CAPTURE-LOG.csv`, `baseline/dialogs.csv`, `baseline/capture.log`); nothing here is described from memory.

**Related docs:** [[data-entry.md]] (the second pass, refused edits), [[save.md]] (the third pass, successful saves), [[../04-forms/README.md]], [[../06-reports/README.md]], [[../05-classes/README.md]], [[../01-architecture/startup.md]], [[../README.md]].

## How it was captured

- `tools/baseline/run_capture.ps1` starts a visible VFP 9 with `tools/baseline/capture.fpw`, whose `COMMAND` runs `tools/baseline/capture.prg`. The harness does `DO tastrade.exe`, so the code that runs is the compiled EXE's own (`progs/main.prg`, the class libraries, the forms and reports inside it); VFP is the host only. Differences from a standalone run: the harness sizes the main window to 1024 by 700 client pixels, the VFP status bar is on, and `_VFP.StartMode` is the IDE's (nothing in the source reads it).
- Two timers on `_SCREEN` drive the application while its `READ EVENTS` is live. One opens each form the way the main menu does (`oApp.DoForm(...)`), snapshots the form window and the main window, and releases it. The other fires inside every modal `Show()`, snapshots the modal form, and presses the button that closes it (Continue on the intro form, Cancel or Close elsewhere), so the run needs no hand. The two report parameter dialogs open while `REPORT FORM` runs, when VFP does not fire timers; the runner outside VFP snapshots them and presses Enter, which is OK.
- Snapshots are `PrintWindow` by HWND from `tools/baseline/snap.ps1`, taken with a DPI-unaware thread so a 1990s form is stored at its own pixel size on a 200% desktop.
- Reports are rendered the way the picker runs them, a cold `REPORT FORM x.frx`, into a VFP 9 `ReportListener` (`ListenerType` 3) whose pages are written as EMF and rasterised at twice 96 dpi (`tools/baseline/emf2png.ps1`). The first three pages of each report are kept; the page count is recorded for all of them. The EXE itself previews with the legacy engine (`SET REPORTBEHAVIOR 80`), so the listener's rendering is the object-assisted engine's; layout and data are the same, glyph placement can differ by a pixel.
- `SET ENGINEBEHAVIOR` was 90, VFP 9's default, as in the EXE. VFP windows visible when the harness started and hidden by it, because the runtime has none: Standard.
- The runner watches the VFP process for Win32 message boxes, snapshots each, logs its text and buttons to `baseline/dialogs.csv`, and presses Ignore, OK, No, or Cancel, in that order of preference.
- Started 16:35:22, finished 16:41:06. `tastrade.ini` is reset to the committed file before and after the run because the application writes window positions into it as forms close.

## Forms

31 images. `page2`, `page3`: the other pages of a form's page frame. `listings`: the report picker with Listings selected. Sizes are the window including its border and title bar.

| Image | Form (`Name`, class) | Caption | Launched as | Size | Doc |
|---|---|---|---|---|---|
| `introform.png` | `introform` (`Introform`) | Introductory Form | `appeared on its own` | 475×357 | [[../05-classes/tsgen.md]] (`introform`) |
| `customer.png` | `frmcustomers` (`Tsmaintform`) | Customers | `oApp.DoForm("customer")` | 610×381 | [[../04-forms/customer.md]] |
| `toolbar.png` | `tstoolbar` (`Tstoolbar`) | Navigation Tools | `oApp.ShowNavToolBar (first framework form)` | 234×33 | [[../05-classes/tsbase.md]] (`tstoolbar`) |
| `customer-page2.png` | `frmcustomers` (`Tsmaintform`) | Customers | `oApp.DoForm("customer") page 2` | 610×381 | [[../04-forms/customer.md]] |
| `employee.png` | `frmemployee` (`Tsmaintform`) | Employees | `oApp.DoForm("employee")` | 562×350 | [[../04-forms/employee.md]] |
| `employee-page2.png` | `frmemployee` (`Tsmaintform`) | Employees | `oApp.DoForm("employee") page 2` | 562×350 | [[../04-forms/employee.md]] |
| `employee-page3.png` | `frmemployee` (`Tsmaintform`) | Employees | `oApp.DoForm("employee") page 3` | 562×350 | [[../04-forms/employee.md]] |
| `product.png` | `frmproducts` (`Tsmaintform`) | Products | `oApp.DoForm("product")` | 587×265 | [[../04-forms/product.md]] |
| `product-page2.png` | `frmproducts` (`Tsmaintform`) | Products | `oApp.DoForm("product") page 2` | 587×265 | [[../04-forms/product.md]] |
| `supplier.png` | `frmsuppliers` (`Tsmaintform`) | Suppliers | `oApp.DoForm("supplier")` | 535×355 | [[../04-forms/supplier.md]] |
| `supplier-page2.png` | `frmsuppliers` (`Tsmaintform`) | Suppliers | `oApp.DoForm("supplier") page 2` | 535×355 | [[../04-forms/supplier.md]] |
| `category.png` | `frmcategory` (`Tsmaintform`) | Categories | `oApp.DoForm("category")` | 462×279 | [[../04-forms/category.md]] |
| `category-page2.png` | `frmcategory` (`Tsmaintform`) | Categories | `oApp.DoForm("category") page 2` | 462×279 | [[../04-forms/category.md]] |
| `shipper.png` | `frmshippers` (`Tsmaintform`) | Shippers | `oApp.DoForm("shipper")` | 526×150 | [[../04-forms/shipper.md]] |
| `shipper-page2.png` | `frmshippers` (`Tsmaintform`) | Shippers | `oApp.DoForm("shipper") page 2` | 526×150 | [[../04-forms/shipper.md]] |
| `ordentry.png` | `frmorderentry` (`Orderentry`) | Order Entry | `oApp.DoForm("ordentry")` | 613×383 | [[../04-forms/ordentry.md]] |
| (none) | `ordhist` | | `oApp.DoForm("ordhist")` | **no form**: no active form after DoForm | [[../04-forms/ordhist.md]] |
| `behindsc.png` | `frmbehindsc` (`Tsbaseform`) | Behind the Scenes | `oApp.DoForm("behindsc")` | 615×362 | [[../04-forms/behindsc.md]] |
| `viewcode.png` | `frmViewCode` (`Tstextform`) | Code Window | `modal, see driver row` | 594×380 | [[../04-forms/viewcode.md]] |
| `reports.png` | `frmreports` (`Tsbaseform`) | Print | `modal, see driver row` | 370×258 | [[../04-forms/reports.md]] |
| `reports-listings.png` | `frmreports` (`Tsbaseform`) | Print | `modal, see driver row` | 370×258 | [[../04-forms/reports.md]] |
| `chngpswd.png` | `frmChangePassword` (`Tsbaseform`) | Change Password | `modal, see driver row` | 432×197 | [[../04-forms/chngpswd.md]] |
| `rebuild.png` | `frmDatabaseUtils` (`Tsbaseform`) | Database Utilities | `modal, see driver row` | 258×159 | [[../04-forms/rebuild.md]] |
| `custadd.png` | `frmAddCustomer` (`Tsbaseform`) | Add Customer | `modal, see driver row` | 605×383 | [[../04-forms/custadd.md]] |
| `casestdy.png` | `frmcasestudy` (`Tstextform`) | Case Study | `modal, see driver row` | 594×380 | [[../04-forms/casestdy.md]] |
| `loginpicture.png` | `loginpicture` (`Loginpicture`) | Login | `modal, see driver row` | 443×345 | [[../05-classes/login.md]] (`loginpicture`) |
| `findcustomer.png` | `findcustomer` (`Findcustomer`) | Find Customer | `modal, see driver row` | 456×309 | [[../05-classes/tsgen.md]] (`findcustomer`) |
| `findorder.png` | `findorder` (`Findorder`) | Find Order | `modal, see driver row` | 456×309 | [[../05-classes/tsgen.md]] (`findorder`) |
| `about.png` | `aboutbox` (`Aboutbox`) | About Tasmanian Traders | `modal, see driver row` | 380×311 | [[../05-classes/about.md]] (`aboutbox`) |
| `gettitle.png` | `frmGetTitle` (`form`) | Report Parameters | `opened by the report's data environment Init during REPORT FORM; run_capture.ps1 pressed Enter (OK is the default button)` | 308×164 | [[../04-forms/gettitle.md]] |
| `getinv.png` | `Form1` (`form`) | Report Parameters | `opened by the report's data environment Init during REPORT FORM; run_capture.ps1 pressed Enter (OK is the default button)` | 267×186 | [[../04-forms/getinv.md]] |

### Main window

`_SCREEN` with the menu and, once a framework form is open, the navigation toolbar. 10 images.

| Image | State | Size |
|---|---|---|
| `main.png` | main window after start-up, no form open | 1040×783 |
| `customer.png` | main window with frmcustomers open | 1040×783 |
| `employee.png` | main window with frmemployee open | 1040×783 |
| `product.png` | main window with frmproducts open | 1040×783 |
| `supplier.png` | main window with frmsuppliers open | 1040×783 |
| `category.png` | main window with frmcategory open | 1040×783 |
| `shipper.png` | main window with frmshippers open | 1040×783 |
| `ordentry.png` | main window with frmorderentry open | 1040×783 |
| `behindsc.png` | main window with frmbehindsc open | 1040×783 |
| `end.png` | main window after every form was released | 1040×783 |

## Reports

| Report | Pages | Kept | Run as | Result | Doc |
|---|---|---|---|---|---|
| `listcat.frx` Category Listing | 2 | p1, p2 | REPORT FORM reports\listcat.frx OBJECT ReportListener (ListenerType 3, pages as EMF), as the picker runs it | ok | [[../06-reports/listcat.md]] |
| `listcust.frx` Customer Listing | 4 | p1, p2, p3 | REPORT FORM reports\listcust.frx OBJECT ReportListener (ListenerType 3, pages as EMF), as the picker runs it | ok | [[../06-reports/listcust.md]] |
| `listempl.frx` Employee Listing | 3 | p1, p2, p3 | REPORT FORM reports\listempl.frx OBJECT ReportListener (ListenerType 3, pages as EMF), as the picker runs it | ok | [[../06-reports/listempl.md]] |
| `listprod.frx` Product Listing | 3 | p1, p2, p3 | REPORT FORM reports\listprod.frx OBJECT ReportListener (ListenerType 3, pages as EMF), as the picker runs it | ok | [[../06-reports/listprod.md]] |
| `listship.frx` Shipper Listing | 1 | p1 | REPORT FORM reports\listship.frx OBJECT ReportListener (ListenerType 3, pages as EMF), as the picker runs it | ok | [[../06-reports/listship.md]] |
| `listsupp.frx` Supplier Listing | 1 | p1 | REPORT FORM reports\listsupp.frx OBJECT ReportListener (ListenerType 3, pages as EMF), as the picker runs it | ok | [[../06-reports/listsupp.md]] |
| `orders.frx` Invoices | 1080 | p1, p2, p3 | REPORT FORM reports\orders.frx OBJECT ReportListener (ListenerType 3, pages as EMF), as the picker runs it | ok | [[../06-reports/orders.md]] |
| `salesdet.frx` Sales Detail | 36 | p1, p2, p3 | REPORT FORM reports\salesdet.frx OBJECT ReportListener (ListenerType 3, pages as EMF), as the picker runs it | ok | [[../06-reports/salesdet.md]] |
| `salessum.frx` Sales Summary | 2 | p1, p2 | REPORT FORM reports\salessum.frx OBJECT ReportListener (ListenerType 3, pages as EMF), as the picker runs it | ok | [[../06-reports/salessum.md]] |
| `topcust.frx` Top 25 Customers | 0 | none | REPORT FORM reports\topcust.frx OBJECT ReportListener (ListenerType 3, pages as EMF), as the picker runs it | no pages | [[../06-reports/topcust.md]] |
| `behindsc.frx` Behind the Scenes | 1 | p1 | REPORT FORM behindsc NEXT 1 (as frmbehindsc.cmdPrint does) into a ReportListener | ok: harness opened data\behindsc.dbf, first record | [[../06-reports/behindsc.md]] |
| `casestdy.frx` Case Study | 0 | none | REPORT FORM reports\casestdy.frx OBJECT ReportListener (ListenerType 3, pages as EMF), as the picker runs it | no pages | [[../06-reports/casestdy.md]] |
| `viewcode.frx` Code Report | 2 | p1, p2 | REPORT FORM viewcode (as frmviewcode.cmdPrint does) into a ReportListener | ok: harness supplied cursor viewcode with progs\main.prg as its text | [[../06-reports/viewcode.md]] |

## Message boxes

Every Win32 message box the run produced, in order, with what the runner pressed. These are the application's own texts (`include/strings.h`) or VFP's.

| # | Time | Title | Text | Buttons | Pressed | Image |
|---|---|---|---|---|---|---|
| 1 | 16:36:36 | An error has occurred | SQL: GROUP BY clause is missing or invalid.Method: remainingcreditLine: 75 | Abort/Retry/Ignore | Ignore | `01.png` |
| 2 | 16:36:38 | An error has occurred | Variable 'TOTALORDER' is not found.Method: remainingcreditLine: 77 | Abort/Retry/Ignore | Ignore | `02.png` |
| 3 | 16:36:39 | An error has occurred | Alias 'ORDERAMOUNTS' is not found.Method: remainingcreditLine: 80 | Abort/Retry/Ignore | Ignore | `03.png` |
| 4 | 16:36:41 | An error has occurred | Operator/operand type mismatch.Method: remainingcreditLine: 84 | Abort/Retry/Ignore | Ignore | `04.png` |
| 5 | 16:36:51 | An error has occurred | SQL: GROUP BY clause is missing or invalid.Method: tsbaseform.dataenvironment.OpenTablesLine: 0 | Abort/Retry/Ignore | Ignore | `05.png` |

## Errors during the run

| Where | What |
|---|---|
| `REMAININGCREDIT` | 1807 SQL: GROUP BY clause is missing or invalid. line 75 |
| `REMAININGCREDIT` | 12 Variable 'TOTALORDER' is not found. line 77 |
| `REMAININGCREDIT` | 13 Alias 'ORDERAMOUNTS' is not found. line 80 |
| `REMAININGCREDIT` | 107 Operator/operand type mismatch. line 84 |
| `REMAININGCREDIT` | 1807 SQL: GROUP BY clause is missing or invalid. line 75 |
| `REMAININGCREDIT` | 12 Variable 'TOTALORDER' is not found. line 77 |
| `REMAININGCREDIT` | 13 Alias 'ORDERAMOUNTS' is not found. line 80 |
| `REMAININGCREDIT` | 107 Operator/operand type mismatch. line 84 |
| `TASTRADE.DOFORM` | 2005 Error loading file - record number 11.  grdLineItems <or one of its members>.  ControlSource : Alias 'CITEMS' is not found line 3 |

## The same run under `SET ENGINEBEHAVIOR 70`

`tools/baseline/run_capture.ps1 -Engine 70 -OutDir baseline-eb70` repeats the capture with the harness forcing VFP 7's query rules before the EXE starts; the EXE itself sets nothing. The images are in `baseline-eb70/`, same layout. What changes:

| Item | Default (90) | Forced 70 |
|---|---|---|
| Form `ordentry` | ok | ok |
| Form `ordhist` | no form | ok |
| Report `topcust.frx` | 0 pages (no pages) | 1 pages (ok) |
| Message boxes | 5 | 0 |
| Errors caught by the harness's `ON ERROR` (outside the harness itself) | 9 | 0 |

- `ordentry` under 70: `ordentry.png`
- `ordhist` opens under 70: `ordhist.png`
- `topcust.frx` renders under 70: `p1`

## Findings

- **The VFP 9 build cannot open Order Entry or Order History cleanly, and cannot print Top 25 Customers.** Under VFP 9's default `SET ENGINEBEHAVIOR 90`, a `GROUP BY` must name every non-aggregated column. The stored procedure `RemainingCredit` (`data/tastrade.dc2`, `GROUP BY a.order_id` with `a.freight` outside an aggregate) raises error 1807 when Order Entry opens, then three follow-on errors as it continues past the failed query; the form shows an available credit of 999,999,999.99. The `order history` view (`GROUP BY Orditems.order_id`, selecting `order_date`, `deliver_by`, `paid`) fails in the form's data environment and the form never loads (error 2005, its grid's `ControlSource` alias `cItems` missing). The `top25cust` view (`GROUP BY ordertotal.customer_id`, selecting `company_name`, `country`) fails inside `REPORT FORM` without any error reaching the harness: no pages, no message. Nothing in the source says so; the VFP 7 twins and the VFP 9 twins are the same text. See the comparison section: with the harness forcing `SET ENGINEBEHAVIOR 70` all three work.
- **Two more `GROUP BY` queries of the same shape did not fail because nothing in the run reached them**: the `ordertotal` view (read only by `top25cust`) and the sales views, which group by the columns they select. `docs/09-business-logic/README.md` R-rules quote the queries; this run is the evidence of which ones VFP 9 rejects.
- **The invoice prints Quantity as asterisks.** `reports/orders.frx` gives the `quantity` field the format mask `999999999.99` in a 1.17-inch box at Arial 12, which cannot hold twelve characters, so every line of every invoice shows `**********` where the quantity should be (`baseline/reports/orders-p1.png`). The layout doc lists the field and its width; only a run shows the overflow.
- **The report Date field is too narrow for its own value.** The `DATE()` field in every page header is 0.68 inches wide at Arial 12, less than `09/09/26` needs, so VFP 9's engine prints `09/09…` on every page (`baseline/reports/listcat-p1.png`). The application sets no `SET CENTURY`; this is the 1990s box, not a four-digit year.
- **Case Study prints nothing because no row matches its filter.** `casestdy.frx` filters `behindsc.dbf` on `screen_id = "*Case Study"`; none of the 65 rows has that value, so the dead report is also empty. Its form (`casestdy.scx`, launched by nothing) opens and shows the text of a `behindsc` topic (`baseline/forms/casestdy.png`).
- **The Employee Listing's dialog defaults to the first title, not all.** Pressing OK on `gettitle` as opened prints the first title in the combo box (3 pages); the All Titles path was not exercised in this run.
- **The run rewrites two table headers.** After every run `data/customer.dbf` and `data/orders.dbf` differ from the committed files in exactly three bytes, the header's last-update date (bytes 1 to 3, `96-05-11` and `96-06-21` to today); no record changes. Which form does it was not isolated. The runner reports it and the files are restored before commit.
- **Order Entry opens on order 1 whose Ship To country is Italy for a London address** (`baseline/forms/ordentry.png`, `orders-p1.png`); the sample data, not the code.
- **What the run added to the reading.** Every earlier doc softened unrun behaviour to "errors or does nothing". The run resolves those: the employee listing's missing `#INCLUDE` path was not reached (its dialog answered with a real title); the printer environments in the reports did not stop the listener (the saved devices do not exist here, and every report that had data rendered); the intro form, login dialog, About box, find dialogs, and every maintenance form open and close as the docs describe.

## Files

| Path | What |
|---|---|
| `baseline/forms/*.png` | One image per form window, plus page and state variants |
| `baseline/screen/*.png` | The main window in each state |
| `baseline/reports/<report>-pN.png` | Rendered report pages |
| `baseline/dialogs/*.png` | Message boxes |
| `baseline/CAPTURE-LOG.csv` | One row per capture with form name, class, caption, launch statement, file, page count, status |
| `baseline/dialogs.csv` | One row per message box with title, text, buttons, and what was pressed |
| `baseline/capture.log` | Timestamped narrative of the run, including every error |
| `tools/baseline/` | The harness: `run_capture.ps1`, `capture.fpw`, `capture.prg`, `snap.ps1` |
