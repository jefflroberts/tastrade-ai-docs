# login.vcx — login dialogs

| Source file | Type | Path |
|---|---|---|
| `login.vcx` | Class library | `libs/login.vc2` |

**Purpose:** Two modal dialogs that authenticate an employee against the `EMPLOYEE` table: `login` (name combo and password) and `loginpicture`, the one the application actually uses, which adds the employee's title, notes, photo, user level, and, under a label reading "Hint", the password itself.

**Used by:**
- `tastrade.Login` ([[main.md]]) runs `loginpicture` through `DoFormRetVal` and parses the returned `employee_id,user level` string. Only when `DEBUGMODE` is off.
- `application.Login` ([[tsgen.md]]) runs the plain `login`, but `tastrade` overrides it, so the plain class is not used by the shipped application.
- The File menu's Login item ([[../07-menus/main.md]]) calls `oApp.Login()` to switch users.

**Related docs:** [[main.md]], [[tsgen.md]] (`tsformretval` base, via [[tsbase.md]]), [[../03-data-model/tables/employee.md]] (`password`, `group_id`, `photo_file`), [[../03-data-model/tables/user_level.md]].

## Classes in this library

### login (extends tsformretval OF tsbase.vcx)

**Purpose:** Base login container. Allows entry of name and password. A modal form in its own data session (`DataSession = 2`) with a drop-down of employees (`cboName`, SQL row source, `BoundColumn = 2` so the value is the `employee_id`), a masked password box (`txtPassword`, `PasswordChar = "*"`), OK and Cancel. The table, field, and tag names are properties, so the class could authenticate against another table; the shipped values are `employee`, `last_name, employee_id`, `password`, `employee_i`. `HelpContextID = 10` links it to the help file. The class icon path in `CLASSDATA` is `h:\allisonk\sampapp\login_s.bmp`, another trace of the original author's machine.

**Custom properties:**

| Property | Protected | Description |
|---|---|---|
| `cfieldname` |  | Name of field that holds user name. |
| `cpassword` |  | Name of field that hold user password. |
| `ctable` |  | Name of table that hold user information. |
| `ctagname` |  | Tag name used to search the employee table for the user name. |

#### Methods

#### `Load`

Opens the employee table directly from the relative path `DATA\employee` if it is not already open in this session. **NOTE:** direct `USE` on a path relative to the current directory, outside any DataEnvironment and without the `tastrade!` prefix; also `FILE("DATA\employee")` tests for a name with no extension, so whether the table is opened here or later by the SQL in `Init` depends on how `FILE()` treats it. Either way the dialog works because the SQL opens `employee` itself.

```foxpro
IF FILE("DATA\" + this.cTable)
	IF !USED(this.cTable)
	  USE ("DATA\" + this.cTable) IN 0
	ENDIF
	SELECT (this.cTable)
ENDIF
```

#### `Init`

Guarded by `gTTrade`. Builds the combo's SQL from the property names (`SELECT last_name, employee_id FROM employee ORDER BY last_name, employee_id INTO CURSOR cNames`), requeries, and selects the first employee. No employees means the dialog refuses to open. **NOTE:** the combo lists employees by last name only, so two employees with the same last name are indistinguishable.

```foxpro
*-- (c) Microsoft Corporation 1995

*- this class can't be used independent of the application
IF TYPE("m.gTTrade") # 'L' OR !m.gTTrade
	=MESSAGEBOX(CLASSBROWERR_LOC)
	RETURN .F.
*-- ... 18 more lines of Microsoft's Tastrade source omitted; see `Init` in your own copy of Tastrade.
```

#### `Refresh`

Positions the employee table on the selected employee with `LOOKUP()` on the `employee_i` tag, so `cmdOk.Click` and the subclass can read that record's fields. Uses `&lcFldName` macro substitution for a field name that is a literal in the line above it.

```foxpro
*-- Set up our workareas
LOCAL lnOldSelect, lcFldName, lcUserID
lnOldSelect = SELECT()
SELECT (thisform.cTable)
lcFldName = "employee_id"
lcUserID = thisform.cboName.Value
*-- ... 5 more lines of Microsoft's Tastrade source omitted; see `Refresh` in your own copy of Tastrade.
```

#### `Unload`

Closes the names cursor and the employee table.

```foxpro
tsFormRetVal::Unload()
IF USED("cNames")
  USE IN cNames
ENDIF

IF USED(this.cTable)
  USE IN (this.cTable)
ENDIF
```

#### `cboName.InteractiveChange`

```foxpro
thisform.Refresh()
```

#### `cmdOk.Click`

The whole authentication: the trimmed stored password must equal the trimmed typed password, compared with `==` after `ALLTRIM` so trailing spaces do not matter. **Case-sensitive**, plain text. Failure shows `BADPASSWORD_LOC`, which reads "Password is invalid. (See Hint textbox)", clears the box, and stays on the form.

```foxpro
*-- Now check the password
IF ALLTRIM(EVAL(this.parent.cPassword)) == ALLTRIM(this.parent.txtPassword.Value)
  thisform.Hide()
ELSE
  =MESSAGEBOX(BADPASSWORD_LOC, MB_ICONEXCLAMATION)
  this.parent.txtPassword.Value = ""
  this.parent.txtPassword.SetFocus()
ENDIF
```

#### `cmdCancel.Click`

Cancel sets `uRetVal = .F.`; the subclass overrides this to return an empty string.

```foxpro
thisform.uRetVal = .F.
thisform.Hide()
```

### loginpicture (extends login)

**Purpose:** Allows entry of name and password, and also displays picture and description of employee. The dialog the application shows. Adds read-only `txtTitle`, `edtDescription` (the employee's notes), `imgPhoto` (from `photo_file`, `Stretch = 1`), `txtUserLevel` (looked up from `USER_LEVEL`), and `txtDispPswd` under the label **"Hint"**, which displays the selected employee's password. Returns `employee_id + "," + user level description` in `uRetVal`, or an empty string on Cancel.

**NOTE:** the password is shown on the login screen. The sample's `behindsc` topic "Hiding Login Passwords" and the `PasswordChar` mask on the entry box are undone by the hint box next to it. Intentional for a demo where every password is `Tastrade`; never to be copied.

**Custom methods:**

| Method | Protected | Description |
|---|---|---|
| `getuserlevel` |  | Returns the user level description from the user_level table. |

#### Methods

#### `Init`

Runs the base `Init` (which fills the combo) and then `Refresh` so the picture and details show for the first employee.

```foxpro
*-- (c) Microsoft Corporation 1995

IF login::Init()
	thisform.Refresh()
ELSE
	RETURN .F.
ENDIF
```

#### `Refresh`

After the base positions the employee record, copies `title`, `notes`, `password`, the photo (only if the file in `photo_file` exists), and the user level into the display controls. The `ELSE` branch's `STORE "" TO` list is broken across two statements by a missing continuation, so `thisform.txtUserLevel.Value` on its own line is a no-op expression rather than part of the store. Harmless because the base `Refresh` has no `RETURN` value and the `ELSE` never runs. **NOTE:** `IF login::Refresh()` tests the return of a method that returns nothing, which VFP evaluates as `.T.`.

```foxpro
IF login::Refresh()
  thisform.txtTitle.Value = title
  thisform.edtDescription.Value = Notes
  IF FILE(photo_file)
	  thisform.imgPhoto.Picture = photo_file
	ELSE
*-- ... 12 more lines of Microsoft's Tastrade source omitted; see `Refresh` in your own copy of Tastrade.
```

#### `getuserlevel`

Looks up the `USER_LEVEL` description for the employee's `group_id` through the `group_id` tag. `SET DATABASE TO TASTRADE` first because the form runs in a private data session. Direct `USE user_level` if needed.

```foxpro
LOCAL llCloseUserLevel, ;
      lcUserLevel

SET DATABASE TO TASTRADE

*-- Look up the group information
*-- ... 15 more lines of Microsoft's Tastrade source omitted; see `getuserlevel` in your own copy of Tastrade.
```

#### `cmdok.Click`

Runs the base password check, then sets `uRetVal` regardless of whether it passed. On a wrong password the base does not hide the form, so `Show()` does not return and the stale `uRetVal` is not seen unless the user then cancels, which overwrites it with an empty string. Works, by accident of ordering.

```foxpro
LOCAL llCloseUserLevel
login.cmdOk::Click()
thisform.uRetVal = employee_id + "," + thisform.GetUserLevel()
```

#### `cmdcancel.Click`

```foxpro
login.cmdCancel::Click()
thisform.uRetVal = ""
```

## Notes

- **Never shown in this build.** `DEBUGMODE` is `.T.`, so `tastrade.Init` skips `Login`; see [[main.md]]. The dialog only appears from the File menu's Login item.
- **Plain-text, case-sensitive, displayed password.** Three separate reasons a rebuild replaces this outright.
- **Direct table access** in `Load` and `getuserlevel` (`USE` by relative path, no DataEnvironment).
- **Macro substitution** in `login.Refresh`.
- **Hard-coded English** in `BADPASSWORD_LOC`, `NOEMPLOYEES_LOC`, and the Hint/Title/User Level labels.
