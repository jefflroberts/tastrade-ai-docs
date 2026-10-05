# Project: tastrade.pjx

| Source file | Type | Path |
|---|---|---|
| `tastrade.pjx` | Project | `tastrade.pj2` |

**Purpose:** The manifest VFP builds `tastrade.exe` from: 78 members (30 others, 17 forms, 13 reports, 6 class libraries, 5 menus, 2 programs, 2 tables, 2 texts, 1 database), the main program, and the build settings. Nothing reads it at run time.

**Used by:**
- The VFP IDE and the `BUILD EXE` that produced `tastrade.exe` on 2026-09-08 (Step 3 in `JOURNAL.md`); the 2001 release shipped `tastrade.app` built from the same project.
- `.SetMain('progs\main.prg')` makes [[../08-programs/main.md]] the entry point.

**Related docs:** [[startup.md]], [[framework.md]], [[../00-inventory/README.md]] (the generated census), [[../08-programs/main.md]], [[../03-data-model/README.md]], [[README.md]].

## Build settings

| Setting | Value | Note |
|---|---|---|
| Main file | `progs\main.prg` | [[../08-programs/main.md]] |
| Home directory | `c:\fox\tastrade` | The VFP 9 rebuild changed it from `c:\vfp\tastrade`: the only line of the twin that differs between the 2001 and 2026 sweeps |
| Debug info | `.T.` | Compiled with debugging information |
| Encrypted | `.F.` | Source in the EXE is not encrypted |
| Project hook | none | `ProjectHookLibrary` and `ProjectHookClass` empty |
| Author / company | Microsoft Corporation, One Microsoft Way, Redmond WA 98052 | The only version-info fields filled in |
| Product name, description, copyright, version | empty | The EXE carries no product name, file description, legal copyright, or version number; `_AutoIncrement = 0` |

**NOTE:** the version and copyright the application shows come from `include/strings.h` ("1.1", 1996) and the intro menu ("1.0", 1994), not from here; the EXE's own version resource is blank.

## Members

| Type | Count | Compiled into the EXE |
|---|---|---|
| other | 30 | yes |
| form | 17 | yes |
| report | 13 | yes |
| class library | 6 | yes |
| menu | 5 | yes |
| program | 2 | yes |
| table | 2 | no (2 excluded) |
| text | 2 | no (2 excluded) |
| database | 1 | no (1 excluded) |

### Program (2)

| Path | Description in the project | Excluded | Doc |
|---|---|---|---|
| `progs/main.prg` | The main program of the system |  | [[../08-programs/main.md]] |
| `progs/utility.prg` | Contains common UDFs |  | [[../08-programs/utility.md]] |

### Class library (6)

| Path | Description in the project | Excluded | Doc |
|---|---|---|---|
| `libs/about.vcx` | Generic about box |  | [[../05-classes/about.md]] |
| `libs/login.vcx` | Login form classes |  | [[../05-classes/login.md]] |
| `libs/main.vcx` | *(none)* |  | [[../05-classes/main.md]] |
| `libs/orders.vcx` | Order entry classes |  | [[../05-classes/orders.md]] |
| `libs/tsbase.vcx` | Application base classes with desired look & feel |  | [[../05-classes/tsbase.md]] |
| `libs/tsgen.vcx` | General classes |  | [[../05-classes/tsgen.md]] |

### Form (17)

| Path | Description in the project | Excluded | Doc |
|---|---|---|---|
| `forms/behindsc.scx` | "Behind The Scenes" Form |  | [[../04-forms/behindsc.md]] |
| `forms/casestdy.scx` | Case Study Form |  | [[../04-forms/casestdy.md]] |
| `forms/category.scx` | Product Category Maintenance Form |  | [[../04-forms/category.md]] |
| `forms/chngpswd.scx` | Change Password Form |  | [[../04-forms/chngpswd.md]] |
| `forms/custadd.scx` | Add Customer Form |  | [[../04-forms/custadd.md]] |
| `forms/customer.scx` | Customer Maintenance Form |  | [[../04-forms/customer.md]] |
| `forms/employee.scx` | Employee Maintenance Form |  | [[../04-forms/employee.md]] |
| `forms/getinv.scx` | Invoice Report Parameters Form |  | [[../04-forms/getinv.md]] |
| `forms/gettitle.scx` | Employee Listing Report Parameters Form |  | [[../04-forms/gettitle.md]] |
| `forms/ordentry.scx` | Order Entry Form |  | [[../04-forms/ordentry.md]] |
| `forms/ordhist.scx` | *(none)* |  | [[../04-forms/ordhist.md]] |
| `forms/product.scx` | Product Maintenance Form |  | [[../04-forms/product.md]] |
| `forms/rebuild.scx` | Database Utilities Form |  | [[../04-forms/rebuild.md]] |
| `forms/reports.scx` | Report Selection Form |  | [[../04-forms/reports.md]] |
| `forms/shipper.scx` | Shipper Maintenance Form |  | [[../04-forms/shipper.md]] |
| `forms/supplier.scx` | Supplier Maintenance Form |  | [[../04-forms/supplier.md]] |
| `forms/viewcode.scx` | Behind the Scenes Code Window |  | [[../04-forms/viewcode.md]] |

### Menu (5)

| Path | Description in the project | Excluded | Doc |
|---|---|---|---|
| `menus/intro.mnx` | Menu displayed while the IntroForm is displaying |  | [[../07-menus/intro.md]] |
| `menus/main.mnx` | Main menu |  | [[../07-menus/main.md]] |
| `menus/navigate.mnx` | *(none)* |  | [[../07-menus/navigate.md]] |
| `menus/ordentry.mnx` | Order Entry menu |  | [[../07-menus/ordentry.md]] |
| `menus/window.mnx` | *(none)* |  | [[../07-menus/window.md]] |

### Report (13)

| Path | Description in the project | Excluded | Doc |
|---|---|---|---|
| `reports/behindsc.frx` | *(none)* |  | [[../06-reports/behindsc.md]] |
| `reports/casestdy.frx` | Case Study |  | [[../06-reports/casestdy.md]] |
| `reports/listcat.frx` | Product Category Listing |  | [[../06-reports/listcat.md]] |
| `reports/listcust.frx` | Customer Listing |  | [[../06-reports/listcust.md]] |
| `reports/listempl.frx` | Employee Listing |  | [[../06-reports/listempl.md]] |
| `reports/listprod.frx` | Product Listing |  | [[../06-reports/listprod.md]] |
| `reports/listship.frx` | Shipper Listing |  | [[../06-reports/listship.md]] |
| `reports/listsupp.frx` | Supplier Listing |  | [[../06-reports/listsupp.md]] |
| `reports/orders.frx` | Invoices |  | [[../06-reports/orders.md]] |
| `reports/salesdet.frx` | Detailed Sales Information |  | [[../06-reports/salesdet.md]] |
| `reports/salessum.frx` | Summary Sales Information |  | [[../06-reports/salessum.md]] |
| `reports/topcust.frx` | *(none)* |  | [[../06-reports/topcust.md]] |
| `reports/viewcode.frx` | Behind the Scenes Code Report |  | [[../06-reports/viewcode.md]] |

### Database (1)

| Path | Description in the project | Excluded | Doc |
|---|---|---|---|
| `data/tastrade.dbc` | Tasmanian Traders Database Container | yes | [[../03-data-model/README.md]] |

### Table (2)

| Path | Description in the project | Excluded | Doc |
|---|---|---|---|
| `data/behindsc.dbf` | Behind the Scenes Information | yes | [[../03-data-model/README.md]] (free table) |
| `data/repolist.dbf` | Information about Reports | yes | [[../03-data-model/README.md]] (free table) |

### Text (2)

| Path | Description in the project | Excluded | Doc |
|---|---|---|---|
| `include/strings.h` | Strings used in app (for localization) | yes | [[../08-programs/strings.h.md]] |
| `include/tastrade.h` | The main include file for this application | yes | [[../08-programs/tastrade.h.md]] |

### Other (30)

| Path | Description in the project | Excluded | Doc |
|---|---|---|---|
| `bitmaps/bhind.ico` | Behind the Scenes Icon |  |  |
| `bitmaps/bhind_s.bmp` | Behind the Scenes Bitmap |  |  |
| `bitmaps/bhind_s.msk` | *(none)* |  |  |
| `bitmaps/catgry.ico` | Category Form Icon |  |  |
| `bitmaps/close.bmp` | "Close" bitmap for toolbar |  |  |
| `bitmaps/close.msk` | *(none)* |  |  |
| `bitmaps/cust.ico` | Customer Form Icon |  |  |
| `bitmaps/emply.ico` | Employee Form Icon |  |  |
| `bitmaps/frsrec_s.bmp` | "First Record" bitmap for toolbar |  |  |
| `bitmaps/frsrec_s.msk` | *(none)* |  |  |
| `bitmaps/lfscroll.bmp` | Left scroll marker for splitter |  |  |
| `bitmaps/locate.bmp` | *(none)* |  |  |
| `bitmaps/locate.msk` | *(none)* |  |  |
| `bitmaps/lstrec_s.bmp` | "Last Record" bitmap for toolbar |  |  |
| `bitmaps/lstrec_s.msk` | *(none)* |  |  |
| `bitmaps/new.bmp` | "New" bitmap for toolbar |  |  |
| `bitmaps/new.msk` | *(none)* |  |  |
| `bitmaps/nxtrec_s.bmp` | "Next Record" bitmap for toolbar |  |  |
| `bitmaps/nxtrec_s.msk` | *(none)* |  |  |
| `bitmaps/orders.ico` | Order Form Icon |  |  |
| `bitmaps/prod1.ico` | Product Form Icon |  |  |
| `bitmaps/prvrec_s.bmp` | "Previous Record" bitmap for toolbar |  |  |
| `bitmaps/prvrec_s.msk` | *(none)* |  |  |
| `bitmaps/rtscroll.bmp` | Right scroll marker for splitter |  |  |
| `bitmaps/save.bmp` | "Save" bitmap for toolbar |  |  |
| `bitmaps/shpprs1.ico` | Shipper Form Icon |  |  |
| `bitmaps/spplrs.ico` | Supplier Form Icon |  |  |
| `bitmaps/ttradelg.bmp` | Tasmanian Traders large bitmap (used in intro form) |  |  |
| `bitmaps/ttradesm.bmp` | Tasmanian Traders large bitmap (used in reports) |  |  |
| `bitmaps/undo.bmp` | "Undo" bitmap for toolbar |  |  |

63 of 78 members carry a description. The undescribed ones outside the bitmaps are `forms/ordhist.scx`, `libs/main.vcx`, `menus/navigate.mnx`, `menus/window.mnx`, `reports/behindsc.frx`, `reports/topcust.frx`.

## Excluded from the EXE

Five members are marked `Exclude`: the database container, the two free tables, and the two include files. The EXE therefore expects `data\tastrade.dbc` and its tables, `data\behindsc.dbf`, and `data\repolist.dbf` on disk beside it, found through `SET PATH` ([[../08-programs/main.md]]); the include files matter only at compile time. Excluding data is the normal choice: tables inside an EXE would be read-only.

## On disk but not in the project

| File | Why it is outside |
|---|---|
| `data/category.dbf` | a table contained in `tastrade.dbc`; the project lists the container, not its tables |
| `data/customer.dbf` | a table contained in `tastrade.dbc`; the project lists the container, not its tables |
| `data/employee.dbf` | a table contained in `tastrade.dbc`; the project lists the container, not its tables |
| `data/orders.dbf` | a table contained in `tastrade.dbc`; the project lists the container, not its tables |
| `data/orditems.dbf` | a table contained in `tastrade.dbc`; the project lists the container, not its tables |
| `data/products.dbf` | a table contained in `tastrade.dbc`; the project lists the container, not its tables |
| `data/setup.dbf` | a table contained in `tastrade.dbc`; the project lists the container, not its tables |
| `data/shippers.dbf` | a table contained in `tastrade.dbc`; the project lists the container, not its tables |
| `data/supplier.dbf` | a table contained in `tastrade.dbc`; the project lists the container, not its tables |
| `data/user_lev.dbf` | a table contained in `tastrade.dbc`; the project lists the container, not its tables |
| `help/tastrade.chi` | the help file's index |
| `help/tastrade.chm` | the help file `environment.Set` selects with `SET HELP TO HELP\TASTRADE.CHM`; found by path, never bundled |
| `help/ttrade.bmp` | help artwork |
| `help/ttrade.dbf` | source table of the help file (16 topics) |
| `other/notes.txt` | the project template's placeholder ("Here's a place to keep notes on your project.") |
| `tastrade.exe` | the build output |
| `tastrade.ini` | run-time data: the intro-form flag and window positions, written by the application |

The ten contained tables appear under the database node in the Project Manager but are not members; the two free tables are. `data/setup.dbf` is the DBC's own configuration table ([[../03-data-model/tables/setup.md]]).

## Bitmaps: what is used, by whom

`bitmaps/` holds 83 files; the project includes 30. Every twin, the two programs, the include files, and the picture columns of `category.dbf` and `employee.dbf` were grepped for each file name:

| Group | Files | Names |
|---|---|---|
| in the project, referenced at run time | 19 | `bhind_s.bmp`, `catgry.ico`, `close.bmp`, `cust.ico`, `emply.ico`, `frsrec_s.bmp`, `locate.bmp`, `lstrec_s.bmp`, `new.bmp`, `nxtrec_s.bmp`, `orders.ico`, `prod1.ico`, `prvrec_s.bmp`, `save.bmp`, `shpprs1.ico`, `spplrs.ico`, `ttradelg.bmp`, `ttradesm.bmp`, `undo.bmp` |
| in the project, referenced by nothing | 11 | `bhind.ico`, `bhind_s.msk`, `close.msk`, `frsrec_s.msk`, `lfscroll.bmp`, `locate.msk`, `lstrec_s.msk`, `new.msk`, `nxtrec_s.msk`, `prvrec_s.msk`, `rtscroll.bmp` |
| not in the project, referenced only by data rows | 23 | `beverage.bmp`, `bridjust.bmp`, `buchstev.bmp`, `calllaur.bmp`, `condimen.bmp`, `confecti.bmp`, `dairypro.bmp`, `davonanc.bmp`, `dodsanne.bmp`, `fullandr.bmp`, `grainsce.bmp`, `hellalbe.bmp`, `kingrobe.bmp`, `levejane.bmp`, `martxavi.bmp`, `meatpoul.bmp`, `pattcaro.bmp`, `peacmarg.bmp`, `perelaur.bmp`, `produce.bmp`, `seafood.bmp`, `smittim.bmp`, `suyamich.bmp` |
| not in the project, class-icon metadata only | 15 | `box.bmp`, `checkbx.bmp`, `combo.bmp`, `datagrid.bmp`, `editbox.bmp`, `form.bmp`, `intell_s.bmp`, `label.bmp`, `listbox.bmp`, `login_s.bmp`, `loginp_s.bmp`, `pushb.bmp`, `shape.bmp`, `textbox.bmp`, `toolbar.bmp` |
| not in the project, referenced by nothing | 15 | `formpg.bmp`, `hvline.bmp`, `intell_b.bmp`, `library.bmp`, `line.bmp`, `lock.bmp`, `ohist.ico`, `ole.bmp`, `pointer.bmp`, `radiob.bmp`, `sep.bmp`, `spinner.bmp`, `splash.bmp`, `timer.bmp`, `wizard.bmp` |

Run-time references, by file:

| Bitmap | Referenced from |
|---|---|
| `bhind_s.bmp` | `tsbase.vc2` |
| `catgry.ico` | `category.sc2` |
| `close.bmp` | `tsbase.vc2` |
| `cust.ico` | `customer.sc2` |
| `emply.ico` | `employee.sc2` |
| `frsrec_s.bmp` | `tsbase.vc2` |
| `locate.bmp` | `ordentry.sc2`, `ordhist.sc2` |
| `lstrec_s.bmp` | `tsbase.vc2` |
| `new.bmp` | `tsbase.vc2` |
| `nxtrec_s.bmp` | `tsbase.vc2` |
| `orders.ico` | `ordentry.sc2` |
| `prod1.ico` | `product.sc2` |
| `prvrec_s.bmp` | `tsbase.vc2` |
| `save.bmp` | `tsbase.vc2` |
| `shpprs1.ico` | `shipper.sc2` |
| `spplrs.ico` | `supplier.sc2` |
| `ttradelg.bmp` | `tsgen.vc2` |
| `ttradesm.bmp` | `behindsc.fr2`, `casestdy.fr2`, `listcat.fr2`, `listcust.fr2`, `listempl.fr2`, `listprod.fr2`, `listship.fr2`, `listsupp.fr2`, `main.mn2`, `orders.fr2`, `salessum.fr2`, `topcust.fr2`, `viewcode.fr2` |
| `undo.bmp` | `tsbase.vc2` |

- **The 11 unreferenced project members** are 8 `.msk` mask files, which VFP pairs with the toolbar button bitmap of the same name without a reference in code, plus `bhind.ico`, `lfscroll.bmp`, `rtscroll.bmp`, which no twin names.
- **The 23 data-only bitmaps** are the category pictures and employee photos: `category.picture_file` and `employee.photo_file` hold relative paths such as `bitmaps\beverage.bmp`, resolved against the current directory at run time ([[../04-forms/category.md]], [[../04-forms/employee.md]]). They are not in the project, so a build on another machine ships without them unless the folder is copied.
- **The 15 class-icon bitmaps** appear only in the `ProjectClassIcon` / `ClassIcon` metadata of the class libraries (the icons the Class Browser shows), two of them through the original authors' paths `h:\allisonk\sampapp\` and `..\..\..\..\backup\mainsamp\`. Design-time only.
- **15 files are referenced by nothing at all** (`formpg.bmp`, `hvline.bmp`, `intell_b.bmp`, `library.bmp`, `line.bmp`, `lock.bmp`, `ohist.ico`, `ole.bmp`, `pointer.bmp`, `radiob.bmp`, `sep.bmp`, `spinner.bmp`, `splash.bmp`, `timer.bmp`, `wizard.bmp`): dead artwork, including `splash.bmp` and `ohist.ico`.

## Reading the twin

FoxBin2PRG renders the project as a program that would rebuild the `.pjx`: `BUILD PROJECT ... FROM '__newproject.f2b'`, an `.ADD()` per member with a `FileMetadata` comment (`Type`, `Cpid`, `ObjRev`), then descriptions, exclusions, text-file overrides, and properties. The `LPARAMETERS tcDir`, the temporary `__newproject.f2b`, and the commented `*ERASE` are the tool's scaffolding, not project data.

Type codes as VFP writes them: lowercase `d` for the database container, uppercase `D` for a table, `x` for images and other files, `K` form, `V` class library, `M` menu, `R` report, `P` program, `T` text. `foxparse.py` mislabelled `D` as "database" and knew neither `d` nor `x` until this step (toolkit commit noted in `JOURNAL.md`).

`ObjRev` is `544` on every form, class library, menu, program, and the DBC, and `0` on reports, tables, include files, and images; `Cpid` is `1252` on seven members (`locate.bmp`/`.msk`, `ordhist.scx`, `navigate.mnx`, `window.mnx`, `behindsc.frx`, `topcust.frx`) and `0` elsewhere, which marks the members touched last by a code-page-aware VFP.

## Notes

- **No version resource.** Product name, description, copyright, and version are empty in the project, so the EXE identifies itself only by its file name.
- **Debug information is on.** Line numbers survive into the EXE (`tsbaseform.Error` puts the `nLine` it receives into its message, [[../05-classes/tsbase.md]]), at the cost of size.
- **Two menus and two reports have no description**, the same four members that other steps found to be late additions (`Cpid = 1252`).
- **The 2001 `tastrade.app` and the 2026 `tastrade.exe`** were built from this same manifest; the app was 826,220 bytes, the EXE is 851,749 (the VFP 9 runtime stub and refreshed object code).
- **`c:\vfp\tastrade`** was the home directory in the shipped project, alongside the three original-author paths found in the class libraries; the sample has been built from at least four locations.
