# frmchangepassword (chngpswd.scx)

| Source file | Type | Path |
|---|---|---|
| `chngpswd.scx` | Form | `forms/chngpswd.sc2` |

**Purpose:** Change the logged-in employee's password: old password unlocks the new and confirm boxes, and OK writes the confirmed value. A "Hint" box shows the current password.

**Used by:**
- The File menu ([[../07-menus/main.md]]) bar "Change Password": `DO FORM chngpswd`, `SKIP FOR !EMPTY(WONTOP())` so it is only available when no form is active.

**Related docs:** [[../03-data-model/tables/employee.md]] (`password`), [[../05-classes/main.md]] (`GetEmployeeID`, empty in this build), [[../05-classes/login.md]] (the other place the password is displayed), [[README.md]].

## Form metadata

- Base class / parent: `tsbaseform` → `form`
- Caption: "Change Password"; `ControlBox = .F.`
- Modal, private data session, no toolbar, `lallowedits = .F.`, `lallownew = .F.`

**Custom properties:**

| Property | Description |
|---|---|
| `coldpassword` | The employee's old password. |

**Custom methods:**

| Method | Description |
|---|---|
| `validate` | Validates all entries made in this form. |

## DataEnvironment

| Cursor | Alias | Source | Order |
|---|---|---|---|
| `Cursor1` | `Employee` | `Employee` | `employee_i` |

`Employee` ordered by `employee_i` so `Load` can `SEEK` the logged-in employee.

DataEnvironment `BeforeOpenTables`:

```foxpro
SET TALK OFF
SET EXCLUSIVE OFF
```

## Controls (depth-first)

| Container path | Class | Bound to / key properties | Role |
|---|---|---|---|
| `cmdBehindSC` | `tscommandbutton (commandbutton)` | caption "\<Behind the Scenes" | Behind the Scenes, modal |
| `cmdCancel` | `tscommandbutton (commandbutton)` | caption "\<Cancel" | Cancel; `TABLEREVERT` |
| `cmdOK` | `tscommandbutton (commandbutton)` | caption "\<OK" | Default; validates then saves |
| `Tslabel1` | `tslabel (label)` | caption "Old Password" |  |
| `Tslabel2` | `tslabel (label)` | caption "New Password" |  |
| `Tslabel3` | `tslabel (label)` | caption "Confirm New Password" |  |
| `Tslabel4` | `tslabel (label)` | caption "User Name" |  |
| `Tslabel5` | `tslabel (label)` | caption "Hint" | "Hint" |
| `txtConfirm` | `tstextbox (textbox)` | disabled | Masked; disabled until the old password matches |
| `txtHint` | `tstextbox (textbox)` | → `Employee.password`; disabled | **Shows the current password in clear text**, bound to `Employee.password` |
| `txtNewPassword` | `tstextbox (textbox)` | disabled | Masked; disabled until the old password matches |
| `txtOldPassword` | `tstextbox (textbox)` |  | Masked; typing the correct old password enables the next two |
| `txtUserName` | `tstextbox (textbox)` | disabled | First and last name, set in `Init` |

### Events with code

#### `txtOldPassword.InteractiveChange`

Compares on every keystroke; the new-password boxes light up the moment the old one matches. Trimmed, case-sensitive.

```foxpro
LOCAL llEnabled

llEnabled = (ALLT(thisform.cOldPassword) == ALLT(this.Value)) 
thisform.txtNewPassword.Enabled = llEnabled
thisform.txtConfirm.Enabled = llEnabled
```

#### `cmdOK.Click`

`REPLACE` then `TABLEUPDATE()`, no transaction, no error check on the update.

```foxpro
IF thisform.Validate()
  REPLACE employee.password WITH thisform.txtConfirm.Value
  =TABLEUPDATE()
  RELEASE thisform
ENDIF
```

#### `cmdCancel.Click`

```foxpro
=TABLEREVERT()
RELEASE thisform
```

#### `cmdBehindSC.Click`

```foxpro
*-- Since this form is modal, we need to make
*-- 'Behind the Scenes' modal as well
DO FORM behindsc WITH .T.
this.Enabled = .F.
```

## Form methods

#### `Load`

Positions on `oApp.GetEmployeeID()`. **NOTE:** in this build the ID is empty (`DEBUGMODE`, [[../05-classes/main.md]]), the `SEEK` fails, and the form sits on the **first employee record**, so the password changed is Steven Buchanan's, not the user's.

```foxpro
*-- (c) Microsoft Corporation 1995

=SEEK(oApp.GetEmployeeID(), "employee", "employee_i")
thisform.cOldPassword = employee.password
```

#### `Init`

```foxpro
thisform.txtUserName.Value = ALLT(employee.first_name) + " " + employee.last_name
```

#### `validate`

Three checks: old password never entered (offer to abandon), new password empty, confirm mismatch. Returns `.F.` on any of them; the implicit `.T.` otherwise.

```foxpro
IF !thisform.txtNewPassword.Enabled
  IF MESSAGEBOX(NOPSWDENTERED_LOC, ;
              MB_ICONQUESTION + MB_YESNO, ;
              TASTRADE_LOC) = IDNO
    =TABLEREVERT()
    RELEASE thisform
*-- ... 24 more lines of Microsoft's Tastrade source omitted; see `validate` in your own copy of Tastrade.
```

#### `Activate`

```foxpro
tsBaseForm::Activate()
*-- Disable command button if Behind the Scenes is
*-- already active
thisform.cmdBehindSC.Enabled = !WEXIST("frmBehindSC")
SELECT employee
```

## Tables read / written

| Table | Access | How |
|---|---|---|
| `EMPLOYEE` | write (`password`) | `REPLACE` on the positioned row, `TABLEUPDATE` |

## Inter-form navigation

- **← File menu**.
- **→ [[behindsc.md]]** modally.

## Notes

- **The password is displayed** while the user is asked to prove they know it.
- **Wrong employee under `DEBUGMODE`**: with no logged-in ID the form edits the first employee.
- **No strength or length rules**; `password` is `C(8)`, so anything longer is silently truncated by the field width.
- **`ControlBox = .F.`** with a Cancel button as the only way out.
