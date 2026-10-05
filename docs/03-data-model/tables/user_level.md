# USER_LEVEL

| Source file | Type | Path |
|---|---|---|
| `user_lev.dbf` | Table in `tastrade.dbc` | `data/tastrade.dc2` (table block `USER_LEVEL`) |

**Purpose:** Security groups. Each employee belongs to one; the group's `startup_action` is code the application runs at login.

**Used by:**
- [[../../04-forms/employee.md]] (`frmemployee`) opens it as a lookup for `group_id`
- `tastrade` application class in [[../../05-classes/main.md]] (`getstartupaction`) looks up `startup_action` by the user level's `description` after login and returns it to be run as a VFP command

**Related docs:** [[../README.md]] (container, stored procedures, views)

Row count in the sample data: 4. DBC comment: "User Level (Security) Information".

## Schema

| # | Field | Type | Width | Dec | Null | Default | Field-valid expr | Comment |
|---|---|---|---|---|---|---|---|---|
| 1 | `group_id` | Character (C) | 6 | 0 | no |  |  | Internal group ID |
| 2 | `description` | Character (C) | 35 | 0 | no |  |  | Description of group |
| 3 | `startup_action` | Memo (M) | 4 | 0 | no |  |  | Name of action to perform when logging in |

## Triggers (from table header)

- Insert: none
- Update: `__ri_update_user_level()`
- Delete: `__ri_delete_user_level()`
- Table valid: none

The `__ri_*` triggers are generated referential-integrity code (see the container README). They enforce the relations listed below and contain no business rules.

## Indexes (.cdx tags)

| Tag | Type | Expression | For | Order |
|---|---|---|---|---|
| `group_id` | primary | `GROUP_ID` |  | asc |
| `descriptio` | regular | `UPPER(DESCRIPTION)` |  | asc |

Primary key tag: `group_id`.

## Stored procedure references

- None from defaults or rules.

## Relations

- **Parent of** [[employee.md]] via child tag `group_id`. RI: update cascade, delete restrict, insert restrict.

## Used by

See the header. Forms open this table through their DataEnvironment; reports reach it through the DBC views named above.

## Sample / notable rows

All 4 rows:

| group_id | description | startup_action |
|---|---|---|
| 1 | Customer Service Rep | oApp.DoForm("ordentry") |
| 2 | Applications Developer |  |
| 3 | Operations Manager |  |
| 4 | Sales Manager |  |

## Notes

- **NOTE:** `startup_action` holds executable VFP code (`oApp.DoForm("ordentry")` for group 1). The application object's `getstartupaction` method fetches it with `LOOKUP()` on the `descriptio` tag, matching the user level by **description text**, not by `group_id`, and `tastrade.Do` ([[../../05-classes/main.md]]) executes the string with `&lcAction` macro substitution, but only when `DEBUGMODE` is off. `DEBUGMODE` is `.T.` in `include/tastrade.h`, so **in this build the startup action never runs**. Code stored in data; a rebuild needs a lookup of allowed actions instead.
- The DBF is `user_lev.dbf`; the DBC long name is `USER_LEVEL`.
- No trigger stops an employee from being left with a `group_id` that is later deleted: the delete trigger on this table restricts, so the group cannot go while employees reference it.
