# behindsc

| Source file | Type | Path |
|---|---|---|
| `behindsc.dbf` | Free table (outside `tastrade.dbc`) | `data/behindsc.db2` |

**Purpose:** The sample's self-documentation: one row per "Behind the Scenes" topic, holding the explanation the form displays and an instruction telling the form which file, object, and methods to open as tables and show as code.

**Used by:**
- [[../../04-forms/behindsc.md]] (`frmbehindsc`): DataEnvironment cursor, ordered by `screen_top`; `SEEK`s the current form's name in `screen_id`, lists the topics, shows `desc`, and follows `code_to_sh` in `showcode`.
- [[../../04-forms/casestdy.md]] (`frmcasestudy`): DataEnvironment cursor, positioned on `screen_id = "*Case Study"` (`SEEKVALUE_LOC`).
- [[../../06-reports/behindsc.md]] (the form's current row, `NEXT 1`) and [[../../06-reports/casestdy.md]] (all `*Case Study` rows).

**Related docs:** [[../README.md]] (container; this table is outside it), [[../../04-forms/behindsc.md]], [[repolist.md]], [[ttrade.md]].

Row count in the sample data: 65. No database container, so no long field names, comments, defaults, rules, or triggers; what follows is all there is.

## Schema

| # | Field | Type | Width | Dec | Null |
|---|---|---|---|---|---|
| 1 | `screen_id` | Character (C) | 20 | 0 | no |
| 2 | `topic` | Character (C) | 60 | 0 | no |
| 3 | `desc` | Memo (M) | 4 | 0 | no |
| 4 | `code_to_sh` | Memo (M) | 4 | 0 | no |

## Triggers (from table header)

- None: no insert, update, or delete trigger, no table rule. Free tables cannot carry them.

## Indexes (.cdx tags)

| Tag | Type | Expression | For | Order |
|---|---|---|---|---|
| `screen_id` | regular | `SCREEN_ID` |  | asc |
| `screen_top` | regular | `SCREEN_ID+TOPIC` |  | asc |
| `topic` | regular | `LTRIM(TOPIC)` |  | asc |

## Stored procedure references

- None.

## Relations

- None. Free tables take part in no persistent relation.

## Used by

See the header. The form opens it read-only from its DataEnvironment and never writes it; there is no maintenance form. Adding a topic means editing the DBF.

## Sample / notable rows

All 65 rows, grouped by `screen_id` (the form or subject the topic belongs to). `desc` is the text shown; `code_to_sh` is the instruction, `file, object, method` per line, `*` for every method, `(a, b)` for several.

| screen_id | topics | rows | with code instruction |
|---|---|---|---|
| `Login Class Library` | Hiding Login Passwords, Selecting an Employee | 2 | 2 |
| `Behind the Scenes` | Exposing Methods, Refreshing the Design Feature list | 2 | 2 |
| `Order Entry` | Finding an Order, Calculating Totals On Screen, Adding and Deleting Detail Lines, Generating Order Numbers, Order Entry Overview, Bringing Up the Last Order, Checking Available Credit, Getting Help, Disabling the Controls, Creating a Shortcut Menu | 10 | 7 |
| `Order History` | Managing Multiple Instances, The Tag Column in the Grid, Refreshing the Grid, Copying Tagged Items to an Order | 4 | 3 |
| `Introductory Form` | Creating an Intro Form, Show This Form at Startup | 2 | 2 |
| `Categories` | Category Overview, Changing the Picture | 2 | 2 |
| `Customers` | Customers Overview, Handling User Entered Primary Keys | 2 | 1 |
| `Employees` | Employees Overview, Changing the Picture | 2 | 1 |
| `Products` | Products Overview | 1 | 1 |
| `Suppliers` | Suppliers Overview | 1 | 1 |
| `Shippers` | Shippers Overview | 1 | 1 |
| `Stored Procedures` | NewID( ), RemainingCredit( ) | 2 | 2 |
| `Print` | Reports Overview, Repolist.dbf Structure, Filtering the Listbox, Running the Report or List | 4 | 2 |
| `tsGen Class Library` | DateRange Control | 1 | 1 |
| `About Class Library` | About Form | 1 | 1 |
| `Change Password` | Change Password Overview, Enabling the New and Confirm Textboxes, Bringing Up Behind the Scenes, Confirming the Entries, Initializing the Form | 5 | 4 |
| `Add Customer` | Add Customer Overview | 1 | 1 |
| `tsBaseForm` | Displaying the Toolbar, Refreshing the Menu, Saving the Window Position, Restoring the Window Position, Manipulating the Content of the Window Menu, Checking for Changes, Refreshing the Toolbar, Preventing a Form From Closing, Prompting to Save Changes, Saving the Contents of the Current Control, Changing the Mouse Cursor, Adding Records, Saving Records, Reverting Changes, Moving the Record Pointer | 15 | 14 |
| `Reports` | Creating User Criteria Screens | 1 | 0 |
| `Main Menu` | Closing the Application, Disabling the Menu Items, Running a Form, Removing Menus Based on User Level | 4 | 4 |
| `Rules` | Validating an Order with a Table Rule, Customer Table Field Rules | 2 | 1 |

## Do the instructions still point at code?

Each `code_to_sh` line was resolved against the twins the way `frmbehindsc` resolves it at run time (file by name, object by class name or object path, method by `PROCEDURE`). 74 instruction lines in 53 rows; 68 resolve; 6 do not:

| Topic | Instruction | What is wrong |
|---|---|---|
| Login Class Library / Hiding Login Passwords | `tsbase.vcx, tspasswordtextbox, *` | no such object or class |
| Stored Procedures / RemainingCredit( ) | `ordentry.scx, cmdavailablecredit, click` | no such object or class |
| Order Entry / Checking Available Credit | `ordentry.scx, cmdavailablecredit, click` | no such object or class |
| Order Entry / Disabling the Controls | `order.vcx, txtdeliver_by, refresh` | no such file |
| Order History / Copying Tagged Items to an Order | `ordhist.scx, cmdconfirm, click` | no such object or class |
| Rules / Customer Table Field Rules | `customer.scx, frmcustomer, error` | no such object or class |

The form reports "not found" for these when the Code button is pressed ([[../../04-forms/behindsc.md]]). The rest resolve, including the two that name the DBC's stored procedures and the two that name whole programs.

## Notes

- **The self-documentation has drifted from the code**: the table above is the measurement. It was last edited for a build whose library was named `order.vcx` and whose customer form was `frmcustomer`.
- **2 rows have an empty `desc`** ("Refreshing the Design Feature list", "Filtering the Listbox"): topics with a code instruction and no explanation.
- **`code_to_sh` is a tiny language**: `file, object, method`, one instruction per line, `*` for all methods, `(m1, m2)` for a list, a trailing comma and nothing for a stored procedure or a program. It is parsed by three methods of the form with `AT()` and `SUBSTR()` and has no validation.
- **The Case Study rows** share the table under `screen_id = "*Case Study"`; the leading asterisk sorts them first and keeps them out of the form-name lookups.
- **Three tags**, on `screen_id`, `screen_id + topic`, and `LTRIM(topic)`; the form uses `screen_top`.
- **Ships in the EXE's project as a member marked Exclude**, so it must be on disk beside the EXE like the DBC ([[../../01-architecture/projects.md]]).
