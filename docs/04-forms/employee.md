# frmemployee (employee.scx)

| Source file | Type | Path |
|---|---|---|
| `employee.scx` | Form | `forms/employee.sc2` |

**Purpose:** Maintain employees: name, title, dates, address, phone, security group, and on a third page the notes and photo. Also the table the login dialog authenticates against.

**Used by:**
- The Maintenance menu ([[../07-menus/main.md]]) bar "Employees": `oApp.DoForm("frmemployee")`, `SKIP FOR WEXIST("frmEmployee")` so only one instance opens.
- [[../05-classes/login.md]] authenticates against the same table; [[chngpswd.md]] changes `password`; view `EMPLOYEE LISTING` feeds [[../06-reports/listempl.md]].

**Related docs:** [[../03-data-model/tables/employee.md]], [[../03-data-model/tables/user_level.md]], [[../05-classes/tsbase.md]] (`tsmaintform`), [[../05-classes/main.md]] (`GetEmployeeID`), [[README.md]].

This is one of the six `tsmaintform` forms. The pattern, documented once in [[../05-classes/tsbase.md]]: a two-page pageframe (**Data Entry** with bound controls, **List** with a read-only `tsgrid` over the same cursor), the shared navigation toolbar for First/Prior/Next/Last/New/Save/Restore/Close, optimistic table buffering committed by `TABLEUPDATE`, and an `Error` method that turns DBC rule and trigger failures into messages. Each form adds only its bindings, a focus target for `AddNew`, the field-rule-to-control mapping in `Error`, and the trigger-failure message text in `Init`.

## Form metadata

- Base class / parent: `tsmaintform` of `..\libs\tsbase.vcx` → `tsbaseform` → `form`
- Caption: "Employees"; icon `..\bitmaps\emply.ico`
- Modal: no. MDI child with the navigation toolbar; new/edit/delete allowed (inherited defaults)
- Data session: private (`DataSession = 2`); `AutoCenter = .F.` (INI position); `ScaleMode = 3` (pixels)
- `pageframe1.PageCount = 3`: a third page "Additional Information" with notes, photo, and the employee's name

## DataEnvironment

| Cursor | Alias | Source | Order | Filter |
|---|---|---|---|---|
| `Cursor1` | `Employee` | `Employee` | `last_name` |  |
| `Cursor2` | `User_Level` | `User_Level` |  |  |

`InitialSelectedAlias = "Employee"`, ordered by upper-cased last name. One relation, `Employee` → `User_Level` on `group_id`, so the List grid can show the group description.

## Controls (depth-first)

| Container path | Class | Bound to / key properties | Role |
|---|---|---|---|
| `pageframe1.page1.cboGroup_ID` | `tscombobox (combobox)` | → `Employee.group_id`; rows `select description, group_id from user_level order by description into cursor cUserLevels` | Security group drop-down over `USER_LEVEL`, `BoundColumn = 2` |
| `pageframe1.page1.extension` | `tstextbox (textbox)` | → `Employee.extension` | → `Employee.extension`; name lacks the `txt` prefix |
| `pageframe1.page1.hiredate` | `tstextbox (textbox)` | → `Employee.hire_date` | → `Employee.hire_date`; name lacks the `txt` prefix |
| `pageframe1.page1.lblGroup` | `tslabel (label)` | caption "\<Group" |  |
| `pageframe1.page1.Tslabel1` | `tslabel (label)` | caption "Last Name" |  |
| `pageframe1.page1.Tslabel10` | `tslabel (label)` | caption "Country" |  |
| `pageframe1.page1.Tslabel11` | `tslabel (label)` | caption "Home Phone" |  |
| `pageframe1.page1.Tslabel12` | `tslabel (label)` | caption "Extension" |  |
| `pageframe1.page1.Tslabel2` | `tslabel (label)` | caption "First Name" |  |
| `pageframe1.page1.Tslabel3` | `tslabel (label)` | caption "Title" |  |
| `pageframe1.page1.Tslabel4` | `tslabel (label)` | caption "Birth Date" |  |
| `pageframe1.page1.Tslabel5` | `tslabel (label)` | caption "Hire Date" |  |
| `pageframe1.page1.Tslabel6` | `tslabel (label)` | caption "Address" |  |
| `pageframe1.page1.Tslabel7` | `tslabel (label)` | caption "City" |  |
| `pageframe1.page1.Tslabel8` | `tslabel (label)` | caption "Region" |  |
| `pageframe1.page1.Tslabel9` | `tslabel (label)` | caption "Postal Code" |  |
| `pageframe1.page1.txtAddress` | `tstextbox (textbox)` | → `Employee.address` |  |
| `pageframe1.page1.txtBirth_Date` | `tstextbox (textbox)` | → `Employee.birth_date` |  |
| `pageframe1.page1.txtCity` | `tstextbox (textbox)` | → `Employee.city` |  |
| `pageframe1.page1.txtCountry` | `tstextbox (textbox)` | → `Employee.country` |  |
| `pageframe1.page1.txtFirst_Name` | `tstextbox (textbox)` | → `Employee.first_name` |  |
| `pageframe1.page1.txtHome_Phone` | `tstextbox (textbox)` | → `Employee.home_phone` |  |
| `pageframe1.page1.txtLast_Name` | `tstextbox (textbox)` | → `Employee.last_name` | Required by the DBC rule |
| `pageframe1.page1.txtPostal_Code` | `tstextbox (textbox)` | → `Employee.postal_code` |  |
| `pageframe1.page1.txtRegion` | `tstextbox (textbox)` | → `Employee.region` |  |
| `pageframe1.page1.txtTitle` | `tstextbox (textbox)` | → `Employee.title` |  |
| `pageframe1.Page3.cmdPicture` | `tscommandbutton (commandbutton)` | caption "Change Picture" | "Add Picture" / "Change Picture" |
| `pageframe1.Page3.edtNotes` | `tseditbox (editbox)` | → `Employee.notes` | Memo |
| `pageframe1.Page3.imgPhoto` | `image (textbox)` |  | Shows `photo_file`; `Stretch = 2` |
| `pageframe1.Page3.txtEmployeeName` | `tstextbox (textbox)` | value `(ALLTRIM( Employee.first_name) + " " +  Employee.last_name)`; disabled; read-only | Unbound, read-only; first and last name joined by `Page3.Refresh` |

The List page's grid headers and cells (28 objects under `pageframe1.page2.grdlist`) are listed as columns below rather than one row each.

List page grid (`ColumnCount = 14`, displayed in `ColumnOrder`):

| Order | Column | Header | ControlSource | Notes |
|---|---|---|---|---|
| 1 | `grcLastName` | Last Name | `Employee.last_name` |  |
| 2 | `grcFirstName` | First Name | `Employee.first_name` |  |
| 3 | `grcTitle` | Title | `Employee.title` |  |
| 4 | `grcAddress` | Address | `Employee.address` |  |
| 5 | `grcCity` | City | `Employee.city` |  |
| 6 | `grcBirthDate` | Birth Date | `Employee.birth_date` |  |
| 7 | `grcHireDate` | Hire Date | `Employee.hire_date` |  |
| 8 | `grcRegion` | Region | `Employee.region` |  |
| 9 | `grcPostalCode` | Postal Code | `Employee.postal_code` |  |
| 10 | `grcCountry` | Country | `Employee.country` |  |
| 11 | `grcHomePhone` | Home Phone | `Employee.home_phone` |  |
| 12 | `grcExtension` | Extension | `Employee.extension` |  |
| 13 | `grcPassword` | Password | `Employee.password` |  |
| 14 | `grcUserLevel` | User Level | `User_Level.description` |  |

**NOTE:** column 13 shows `Employee.password` in clear text in the List page. Combined with the login dialog's "Hint" box ([[../05-classes/login.md]]), every password in the system is visible from two places in the UI. Column 14 shows the user level description from the related cursor.

### Events with code

#### `pageframe1.Page3.Activate`

Same alias re-selection as the base page-activate handlers, then a refresh so the photo loads.

```foxpro
LOCAL lcAlias
lcAlias = thisform.DataEnvironment.InitialSelectedAlias
IF !EMPTY(lcAlias)
  SELECT (lcAlias)
ENDIF
thisform.RefreshForm()
```

#### `pageframe1.Page3.Refresh`

```foxpro
this.txtEmployeeName.Value = ALLT( Employee.first_name) + ;
                              " " +  Employee.last_name
```

#### `pageframe1.Page3.cmdPicture.Click`

Like the category form's picture button but stores only the file name; no General field copy here.

```foxpro
LOCAL lcFileName

lcFileName = GETFILE("BMP", ;
                    this.Caption, ;
                    SELECTBUTTON_LOC)

*-- ... 5 more lines of Microsoft's Tastrade source omitted; see `pageframe1.Page3.cmdPicture.Click` in your own copy of Tastrade.
```

#### `pageframe1.Page3.cmdPicture.Refresh`

```foxpro
IF "3" $ GETFLDSTATE(-1) OR "4" $ GETFLDSTATE(-1)
  this.Caption = ADDPICTURE_LOC
ELSE
  this.Caption = CHANGEPICTURE_LOC
ENDIF
```

#### `pageframe1.page1.cboGroup_ID.Destroy`

```foxpro
IF USED("cUserLevels")
  USE IN cUserLevels
ENDIF
```

## Form methods

#### `Init`

Trigger messages: delete `DELEMPLOYEE_LOC` "Employee exists on orders. Cannot delete!" and insert `INSEMPLOYEE_LOC` "All employees must be assigned to a group."

```foxpro
*-- (c) Microsoft Corporation 1995

tsBaseForm::Init()
this.aErrorMsg[DELETETRIG] = DELEMPLOYEE_LOC
this.aErrorMsg[INSERTTRIG] = INSEMPLOYEE_LOC
```

#### `addnew`

```foxpro
tsMaintForm::AddNew()
thisform.pageframe1.page1.txtLast_Name.SetFocus()
```

#### `Refresh`

Prevents deleting the employee who is logged in by clearing `lAllowDelete` when the current record is `oApp.GetEmployeeID()`. **NOTE:** in this build `GetEmployeeID()` is always empty (`DEBUGMODE`, see [[../05-classes/main.md]]), so the guard never fires. Overriding `Refresh` rather than `RefreshForm` means it also runs on the base class's `LockScreen`-wrapped refresh.

```foxpro
LOCAL lcEmployeeID
lcEmployeeID = ""
IF TYPE("oApp") == "O"
  lcEmployeeID = oApp.GetEmployeeID()
ENDIF

*-- ... 7 more lines of Microsoft's Tastrade source omitted; see `Refresh` in your own copy of Tastrade.
```

#### `refreshform`

Loads the photo from `photo_file` (blank if missing) before the normal refresh.

```foxpro
LOCAL lcFile

IF FILE(employee.photo_file)
	lcFile = employee.photo_file
ELSE
	lcFile = ''
*-- ... 4 more lines of Microsoft's Tastrade source omitted; see `refreshform` in your own copy of Tastrade.
```

#### `Destroy`

```foxpro
tsMaintForm::Destroy()
IF USED("employee")
  SELECT employee
  SET RELATION TO
ENDIF
```

#### `Error`

Field rule on `LAST_NAME` refocuses the last name.

```foxpro
LPARAMETERS nError, cMethod, nLine

LOCAL laError[AERRORARRAY], ;
      lcMessage
=AERROR(laError)

*-- ... 13 more lines of Microsoft's Tastrade source omitted; see `Error` in your own copy of Tastrade.
```

## Tables read / written

| Table | Access | How |
|---|---|---|
| `EMPLOYEE` | both | DataEnvironment; `newid()` default fills `employee_id`; `password` defaults to `"Tastrade"` and is **not** editable here (no control), only via [[chngpswd.md]] |
| `USER_LEVEL` | read | DataEnvironment (related) and combo cursor `cUserLevels` |

## Inter-form navigation

- **← Maintenance menu** only.

## Notes

- **Password visible in the list grid.**
- **No control for `password`, `sales_region`, `photo`** (the General field) on the entry pages; `sales_region` has no UI anywhere.
- **Logged-in-employee delete guard is dead** under `DEBUGMODE`.
- **Inconsistent control names** (`hiredate`, `extension` without the `txt` prefix).
- **Photo path is absolute** to the machine it was chosen on, as in the category form.
