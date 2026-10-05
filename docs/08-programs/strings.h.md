# strings.h

| Source file | Type | Path |
|---|---|---|
| `strings.h` | Include file | `include/strings.h` |

**Purpose:** Every user-visible string of the application as a `_LOC` constant, "for localization purposes": message-box titles and texts, the names of VFP's toolbar windows, trigger-failure messages, button captions, and the version and copyright shown in the About box.

**Used by:**
- [[tastrade.h.md]] (`#INCLUDE "STRINGS.H"`), and through it everything that includes that file. No source includes this file directly.
- The project lists it as a text file, excluded from the build, described as "Strings used in app (for localization)".

**Related docs:** [[tastrade.h.md]], [[../05-classes/tsgen.md]] (`releasetoolbars`, which hides VFP's toolbars by the `TB_*` names), [[../05-classes/tsbase.md]] (`tsbaseform.Error`, the trigger messages), [[../03-data-model/README.md]] (stored procedures use the credit-limit strings), [[../07-menus/main.md]] and [[../07-menus/intro.md]] (the About boxes), [[README.md]].

## Role

**Runtime constants.** Nothing runs. 86 constants in 5 sections; the `Used by` column is a case-sensitive whole-word grep over every twin, `.mpr`, `.prg`, and the DBC twin, and 7 constants have no user.

## Constants


### Messagebox Titles

| Constant | Text | Comment | Used by |
|---|---|---|---|
| `ERRORTITLE_LOC` | "An error has occurred" |  | `tsbase.vc2`, `tsgen.vc2` |
| `TASTRADE_LOC` | "Tasmanian Traders" |  | `behindsc.sc2`, `casestdy.sc2`, `chngpswd.sc2` (3), `ordentry.sc2` (3), `ordhist.sc2` (3), `reports.sc2`, `viewcode.sc2`, `login.vc2`, `main.vc2`, `orders.vc2`, `tsbase.vc2` (5), `tsgen.vc2` (2), `main.mn2`, `main.mpr`, `listempl.fr2`, `orders.fr2`, `tastrade.dc2` (3), `utility.prg` |

### Toolbar names

| Constant | Text | Comment | Used by |
|---|---|---|---|
| `TB_FORMDESIGNER_LOC` | "Form Designer" |  | `tsgen.vc2` |
| `TB_STANDARD_LOC` | "Standard" |  | `tsgen.vc2` |
| `TB_LAYOUT_LOC` | "Layout" |  | `tsgen.vc2` |
| `TB_QUERY_LOC` | "Query Designer" |  | `tsgen.vc2` |
| `TB_VIEWDESIGNER_LOC` | "View Designer" |  | `tsgen.vc2` |
| `TB_COLORPALETTE_LOC` | "Color Palette" |  | `tsgen.vc2` |
| `TB_FORMCONTROLS_LOC` | "Form Controls" |  | `tsgen.vc2` |
| `TB_DATADESIGNER_LOC` | "Database Designer" |  | `tsgen.vc2` |
| `TB_REPODESIGNER_LOC` | "Report Designer" |  | `tsgen.vc2` |
| `TB_REPOCONTROLS_LOC` | "Report Controls" |  | `tsgen.vc2` |
| `TB_PRINTPREVIEW_LOC` | "Print Preview" |  | `tsgen.vc2` |
| `WIN_COMMAND_LOC` | "Command" | Command Window | `tsgen.vc2` |

### Messagebox Messages

| Constant | Text | Comment | Used by |
|---|---|---|---|
| `FILENOTEXIST_LOC` | "File does not exist: " |  | `tsgen.vc2` |
| `BADPASSWORD_LOC` | "Password is invalid. (See Hint textbox)" |  | `login.vc2` |
| `BADNAME_LOC` | "Name not found." |  | **unused** |
| `BADUPDATE_LOC` | "Could not update - reverting to original." |  | **unused** |
| `SAVECHANGES_LOC` | "Do you want to save your changes first?" |  | `tsbase.vc2` |
| `ASKDELETE_LOC` | "Are you sure you wish to delete this information?" |  | **unused** |
| `TAGNOTFOUND_LOC` | "Index tag not found." |  | `tsbase.vc2` |
| `REPORTNOTFOUND_LOC` | "Report file not found." |  | `reports.sc2` |
| `PRINTERNOTREADY_LOC` | "Printer not ready." |  | `behindsc.sc2`, `casestdy.sc2`, `reports.sc2`, `viewcode.sc2` |
| `NORECSMATCHED_LOC` | "No records matched criteria." |  | **unused** |
| `DELETEREC_LOC` | "Are you sure you want to delete this record?" |  | `ordentry.sc2`, `tsbase.vc2` |
| `DELETEWARN_LOC` | "Delete Warning" |  | `ordentry.sc2`, `tsbase.vc2` |
| `AVAILABLECREDIT_LOC` | "Available Credit" |  | **unused** |
| `NOTYET_LOC` | "Under Construction" |  | `utility.prg` |
| `CUSTIDEXISTS_LOC` | "Customer ID already exists. Please re-enter." |  | `tsgen.vc2` |
| `NOLASTORDER_LOC` | "Customer has no prior order." |  | `ordentry.sc2` |
| `CUSTFIRSTORDER_LOC` | "Customer's last order is current order." |  | **unused** |
| `TODAYORLATER_LOC` | "Date must be today or later." |  | `orders.vc2` |
| `DATERANGEERROR_LOC` | "'To' date cannot be less than 'From' date." |  | `tsgen.vc2` |
| `ADDCUSTOMER_LOC` | "Do you want to add this customer to the Customer master file?" |  | `ordentry.sc2` |
| `NOTHINGTOPRINT_LOC` | "Nothing to print." |  | `listempl.fr2`, `orders.fr2` |
| `PASSWORDEMPTY_LOC` | "New password cannot be empty." |  | `chngpswd.sc2` |
| `PSWDNOTCNFRM_LOC` | "Cannot confirm new password. Please try again." |  | `chngpswd.sc2` |
| `NOPSWDENTERED_LOC` | "You have not yet entered the old password. Do you want to continue?" |  | `chngpswd.sc2` |
| `FILESAVEDAS_LOC` | "File saved as " |  | `reports.sc2` |
| `ORDHASITEMS_LOC` | "An order must have at least one line item." |  | `tastrade.dc2` |
| `CUSTOVERMAX_LOC` | "Customer is over their maximimun order amount by " |  | `tastrade.dc2` |
| `CUSTUNDERMIN_LOC` | "Customer order total must be at least " |  | `tastrade.dc2` |
| `SAVEANYWAY_LOC` | "Save anyway?" |  | `tastrade.dc2` (2) |
| `VALIDATING_LOC` | "Validating ..." |  | `rebuild.sc2` |
| `PRINTING_LOC` | "Printing ..." |  | `behindsc.sc2`, `casestdy.sc2`, `viewcode.sc2` |
| `VIEWCODEPRINT_LOC` | "This report may be lengthy. Do you want to continue?" |  | `viewcode.sc2` |
| `VIEWCSDTYPRINT_LOC` | "This report may be lengthy. Do you want to continue?" |  | `behindsc.sc2`, `casestdy.sc2` |
| `METHOD_LOC` | "Method: " |  | `tsbase.vc2` |
| `LINENUM_LOC` | "Line: " |  | `tsbase.vc2` |
| `CUSTNOORD_LOC` | "Customer has no orders." |  | **unused** |
| `SELCUSTFIRST_LOC` | "Must select a customer first." |  | `ordentry.sc2` |
| `CANNOTQUIT_LOC` | "Cannot quit Visual FoxPro within Tasmanian Traders." |  | `utility.prg` |
| `ADDNEWREC_LOC` | "That was the last record. Do you want to add a new one?" |  | `tsbase.vc2` |
| `ENTERADDMODE_LOC` | "There are no records on file. You will be placed in 'Add' mode." |  | `tsbase.vc2` |
| `NOEMPLOYEES_LOC` | "There are no employees on file." |  | `login.vc2` |
| `INSEMPLOYEE_LOC` | "All employees must be assigned to a group." |  | `employee.sc2` |
| `INSPRODUCT_LOC` | "All products must be assigned a supplier and a category." |  | `product.sc2` |
| `INSORDER_LOC` | "All orders must have a customer and a shipper.(Delivery Info)" |  | `ordentry.sc2` |
| `TABLERULEFAIL_LOC` | "Table rule failed!" |  | `tsbase.vc2` |
| `ITEMNOTSAVED_LOC` | "The marked items have not been added to the order. Discard the marked items?" |  | `ordhist.sc2` (3) |
| `CLASSBROWERR_LOC` | "This class cannot be used outside of the Tastrade application." |  | `about.vc2`, `login.vc2`, `main.vc2`, `tsbase.vc2` (2), `tsgen.vc2` (4) |

### Trigger error messages

| Constant | Text | Comment | Used by |
|---|---|---|---|
| `INSERTTRIGFAIL_LOC` | "Insert trigger failed!" |  | `tsbase.vc2` |
| `UPDATETRIGFAIL_LOC` | "Update trigger failed!" |  | `tsbase.vc2` |
| `DELETETRIGFAIL_LOC` | "Delete trigger failed!" |  | `tsbase.vc2` |
| `DELCATEGORY_LOC` | "Products belong to this category. Cannot delete!" |  | `category.sc2` |
| `DELCUSTOMER_LOC` | "Customer has orders. Cannot delete!" |  | `customer.sc2` |
| `DELEMPLOYEE_LOC` | "Employee exists on orders. Cannot delete!" |  | `employee.sc2` |
| `DELPRODUCT_LOC` | "Product exists on order line items. Cannot delete!" |  | `product.sc2` |
| `DELSUPPLIER_LOC` | "Products are supplied by this supplier. Cannot delete!" |  | `supplier.sc2` |
| `DELSHIPPER_LOC` | "Shipper exists on orders. Cannot delete!" |  | `shipper.sc2` |

### Other strings

| Constant | Text | Comment | Used by |
|---|---|---|---|
| `ADDPICTURE_LOC` | "Add Picture" |  | `category.sc2`, `employee.sc2` |
| `CHANGEPICTURE_LOC` | "Change Picture" |  | `category.sc2`, `employee.sc2` |
| `SELECTBUTTON_LOC` | "Select" |  | `category.sc2`, `employee.sc2` |
| `VERSION_LOC` | "1.1" |  | `main.mn2`, `main.mpr` |
| `COPYRIGHT_LOC` | "Copyright 1996 Microsoft Corporation" |  | `main.mn2`, `main.mpr` |
| `RIGHTSRSRVD_LOC` | "All rights reserved" |  | `main.mn2`, `main.mpr` |
| `ADDITEM_LOC` | "Add Item" |  | `ordentry.sc2` |
| `REMOVEITEM_LOC` | "Remove Item" |  | `ordentry.sc2` |
| `INFSAVED_LOC` | "Information saved." |  | `custadd.sc2`, `tsbase.vc2` |
| `REINDEXING_LOC` | "Reindexing: " |  | `rebuild.sc2` |
| `DONE_LOC` | "Done" |  | `rebuild.sc2` |
| `LOWERNOTFOUND_LOC` | " not found." |  | `behindsc.sc2` |
| `ABOUT_LOC` | "About " |  | `about.vc2` |
| `VERSIONLABEL_LOC` | "Version " |  | `about.vc2` |
| `LOWERFOR_LOC` | " for " |  | `ordhist.sc2` |
| `UPDATEORDER_LOC` | "Updating Order" |  | `ordhist.sc2` |

## Notes

- **Unused constants:** `BADNAME_LOC`, `BADUPDATE_LOC`, `ASKDELETE_LOC`, `NORECSMATCHED_LOC`, `AVAILABLECREDIT_LOC`, `CUSTFIRSTORDER_LOC`, `CUSTNOORD_LOC`. `ASKDELETE_LOC` and `DELETEREC_LOC` say the same thing; only the second is used. `AVAILABLECREDIT_LOC` and `CUSTNOORD_LOC` belong to features the order entry form does differently now.
- **The toolbar names are a hidden dependency on an English VFP.** `environment.ReleaseToolBars` ([[../05-classes/tsgen.md]]) hides the IDE's toolbars by window title ("Form Designer", "Standard", ..., "Command"); on a localized VFP the titles differ and nothing is hidden. Localizing this file would not fix that, since the strings must match VFP's, not the user's language.
- **Typo shipped:** `CUSTOVERMAX_LOC` reads "maximimun".
- **Two constants, one text:** `VIEWCODEPRINT_LOC` and `VIEWCSDTYPRINT_LOC` are both "This report may be lengthy. Do you want to continue?", used by the code viewer and the case study / Behind the Scenes prints respectively.
- **Version and copyright** (`VERSION_LOC` "1.1", `COPYRIGHT_LOC` "Copyright 1996 Microsoft Corporation") are read only by the main menu's About box; the intro menu's About box hard-codes "1.0" and 1994 ([[../07-menus/intro.md]]). The project's own header says 1995.
- **Not everything is here.** Menu prompts and status text ([[../07-menus/README.md]]), the intro menu's About strings, form captions, and grid headers are literals in the `.mnx`, `.scx`, and `.vcx` files; the file localizes messages, not the UI.
- **Credit-limit messages are assembled in the stored procedures** (`CUSTOVERMAX_LOC`, `CUSTUNDERMIN_LOC`, `SAVEANYWAY_LOC` with the `DOLLAR_FORMAT*` constants from [[tastrade.h.md]]), so the DBC, not just the forms, depends on this file at compile time.
