# EMPLOYEE

| Source file | Type | Path |
|---|---|---|
| `employee.dbf` | Table in `tastrade.dbc` | `data/tastrade.dc2` (table block `EMPLOYEE`) |

**Purpose:** Employees of the company. Doubles as the login table: `password` and `group_id` drive authentication and the user level.

**Used by:**
- [[../../04-forms/employee.md]] (`frmemployee`) maintains it
- [[../../04-forms/chngpswd.md]] (`frmchangepassword`) updates `password`
- [[../../04-forms/gettitle.md]] lists distinct titles for the employee report
- `login` class in [[../../05-classes/login.md]] authenticates against it
- Stored procedure `DefaultEmployee()` falls back to its first record
- View `EMPLOYEE LISTING`, printed by [[../../06-reports/listempl.md]]

**Related docs:** [[../README.md]] (container, stored procedures, views)

Row count in the sample data: 15. DBC comment: "Employee Information".

## Schema

| # | Field | Type | Width | Dec | Null | Default | Field-valid expr | Comment |
|---|---|---|---|---|---|---|---|---|
| 1 | `employee_id` | Character (C) | 6 | 0 | no | `newid()` |  | Internal employee ID |
| 2 | `last_name` | Character (C) | 20 | 0 | no |  | `.NOT.EMPTY(last_name)` → "Last name cannot be empty." | Employee's last name |
| 3 | `first_name` | Character (C) | 10 | 0 | no |  |  | Employee's first name |
| 4 | `title` | Character (C) | 30 | 0 | no |  |  | Employee's job title |
| 5 | `birth_date` | Date (D) | 8 | 0 | no |  |  | Employee's birth date  |
| 6 | `hire_date` | Date (D) | 8 | 0 | no |  |  | Date employee was hired |
| 7 | `address` | Character (C) | 60 | 0 | no |  |  | Employee's address |
| 8 | `city` | Character (C) | 15 | 0 | no |  |  | Employee's city |
| 9 | `region` | Character (C) | 15 | 0 | no |  |  | Employee's region (e.g., TX) |
| 10 | `postal_code` | Character (C) | 10 | 0 | no |  |  | Employee's postal (zip) code |
| 11 | `country` | Character (C) | 15 | 0 | no |  |  | Employee country |
| 12 | `home_phone` | Character (C) | 24 | 0 | no |  |  | Employee's home phone number |
| 13 | `extension` | Character (C) | 4 | 0 | no |  |  | Emploee's home phone number extension |
| 14 | `group_id` | Character (C) | 6 | 0 | no |  |  | Internal group id of employee |
| 15 | `sales_region` | Character (C) | 4 | 0 | no |  |  | Sales region employee is responsibile for |
| 16 | `password` | Character (C) | 8 | 0 | no | `"Tastrade"` |  | Employee's password |
| 17 | `photo_file` | Memo (M) | 4 | 0 | no |  |  |  |
| 18 | `notes` | Memo (M) | 4 | 0 | no |  |  | Notes about employee |
| 19 | `photo` | General (G) | 4 | 0 | no |  |  | Employee's photo |

## Triggers (from table header)

- Insert: `__ri_insert_employee()`
- Update: `__ri_update_employee()`
- Delete: `__ri_delete_employee()`
- Table valid: none

The `__ri_*` triggers are generated referential-integrity code (see the container README). They enforce the relations listed below and contain no business rules.

## Indexes (.cdx tags)

| Tag | Type | Expression | For | Order |
|---|---|---|---|---|
| `group_id` | regular | `GROUP_ID` |  | asc |
| `last_name` | regular | `UPPER(LAST_NAME)` |  | asc |
| `employee_i` | primary | `EMPLOYEE_ID` |  | asc |

Primary key tag: `employee_i`.

## Stored procedure references

- `NewID()` — default of `employee_id`. Quoted and explained in [[../README.md]].

## Relations

- **Child of** [[user_level.md]] on `group_id` → parent tag `group_id`. RI: update cascade, delete restrict, insert restrict.
- **Parent of** [[orders.md]] via child tag `employee_i`. RI: update cascade, delete restrict, insert restrict.

## Used by

See the header. Forms open this table through their DataEnvironment; reports reach it through the DBC views named above.

## Sample / notable rows

All 15 rows:

| last_name | first_name | title | group_id |
|---|---|---|---|
| Buchanan | Steven | Sales Manager | 1 |
| Suyama | Michael | Sales Representative | 4 |
| King | Robert | Sales Representative | 3 |
| Callahan | Laura | Inside Sales Coordinator | 4 |
| Dodsworth | Anne | Sales Representative | 2 |
| Hellstern | Albert | Business Manager | 3 |
| Smith | Tim | Mail Clerk | 1 |
| Patterson | Caroline | Receptionist | 4 |
| Brid | Justin | Marketing Director | 3 |
| Martin | Xavier | Marketing Associate | 4 |
| Pereira | Laurent | Advertising Specialist | 2 |
| Davolio | Nancy | Applications Developer | 2 |
| Fuller | Andrew | Entry Clerk | 1 |
| Leverling | Janet | Applications Developer | 2 |
| Peacock | Margaret | Sales Manager | 3 |

## Notes

- **NOTE:** `password` is `C(8)` plain text with default `"Tastrade"`. Every sample employee can log in with the default. A rebuild must not carry this forward.
- `photo` is a **General** field and `photo_file` its source file name; see the category note.
- The insert trigger is RI only: an employee cannot be added with a `group_id` that is not in USER_LEVEL.
- `sales_region` is `C(4)` and matches `customer.sales_region`, but no relation or rule enforces it.
- The `extension` comment misspells "Employee"; the data is a phone extension, not a home phone.
