# Forms

Seventeen forms in `forms/*.scx`. All seventeen are documented. The six maintenance forms share the `tsmaintform` pattern described in [[../05-classes/tsbase.md]]; `casestdy` is launched by nothing in the source. Each is documented from its FoxBin2PRG twin with the control tree, DataEnvironment, and every method body. What a form inherits is in [[../05-classes/README.md]].

| File | Form class | Extends | Role | Doc |
|---|---|---|---|---|
| `forms/ordentry.scx` | `frmorderentry` | `orderentry (orders.vcx)` | Order entry | [[ordentry.md]] |
| `forms/ordhist.scx` | `frmordhistory` | `tsbaseform` | Order history and item copy | [[ordhist.md]] |
| `forms/customer.scx` | `frmcustomers` | `tsmaintform` | Customer maintenance | [[customer.md]] |
| `forms/custadd.scx` | `frmaddcustomer` | `tsbaseform` | Add a customer from order entry | [[custadd.md]] |
| `forms/employee.scx` | `frmemployee` | `tsmaintform` | Employee maintenance | [[employee.md]] |
| `forms/product.scx` | `frmproducts` | `tsmaintform` | Product maintenance | [[product.md]] |
| `forms/supplier.scx` | `frmsuppliers` | `tsmaintform` | Supplier maintenance | [[supplier.md]] |
| `forms/category.scx` | `frmcategory` | `tsmaintform` | Category maintenance | [[category.md]] |
| `forms/shipper.scx` | `frmshippers` | `tsmaintform` | Shipper maintenance | [[shipper.md]] |
| `forms/chngpswd.scx` | `frmchangepassword` | `tsbaseform` | Change password | [[chngpswd.md]] |
| `forms/reports.scx` | `frmreports` | `tsbaseform` | Report picker | [[reports.md]] |
| `forms/getinv.scx` | `form1` | `form` | Invoice date-range dialog (run by orders.frx) | [[getinv.md]] |
| `forms/gettitle.scx` | `frmgettitle` | `form` | Employee title dialog (run by listempl.frx) | [[gettitle.md]] |
| `forms/rebuild.scx` | `frmdatabaseutils` | `tsbaseform` | Database utilities (reindex) | [[rebuild.md]] |
| `forms/behindsc.scx` | `frmbehindsc` | `tsbaseform` | Behind the Scenes | [[behindsc.md]] |
| `forms/casestdy.scx` | `frmcasestudy` | `tstextform` | Case study viewer | [[casestdy.md]] |
| `forms/viewcode.scx` | `frmviewcode` | `tstextform` | View code | [[viewcode.md]] |

Two forms are plain VFP forms with no framework base (`getinv`, `gettitle`); they are report parameter dialogs run from report data environments, see [[../03-data-model/README.md]].
