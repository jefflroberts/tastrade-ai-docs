# frmaddcustomer (custadd.scx)

| Source file | Type | Path |
|---|---|---|
| `custadd.scx` | Form | `forms/custadd.sc2` |

**Purpose:** Add one customer from inside order entry. A modal wrapper around the shared `customerinfo` container: appends a blank customer, pre-fills the company name the user typed, and commits on OK.

**Used by:**
- [[ordentry.md]] `cboCustomer_ID.Valid`: `DO FORM custadd WITH this.DisplayValue TO llAdded` when a typed customer does not exist; `.T.` on OK.

**Related docs:** [[../05-classes/tsgen.md]] (`customerinfo`, which supplies every bound control and the error-to-control mapping), [[customer.md]] (the maintenance form built on the same container), [[../03-data-model/tables/customer.md]], [[README.md]].

## Form metadata

- Base class / parent: `tsbaseform` → `form`
- Caption: "Add Customer"
- Modal (`WindowType = 1`), private data session, no toolbar (`ctoolbar` empty), `lallownew = .F.`
- Returns `lretval` from `Unload`

**Custom properties:**

| Property | Description |
|---|---|
| `lretval` | Return value for this form. If OK is selected, lRetVal will = .T. |

## DataEnvironment

| Cursor | Alias | Source | Order |
|---|---|---|---|
| `Cursor1` | `Customer` | `Customer` |  |

`InitialSelectedAlias = "Customer"`; optimistic table buffering inherited from the base form.

## Controls (depth-first)

| Container path | Class | Bound to / key properties | Role |
|---|---|---|---|
| `cmdBehindSC` | `tscommandbutton (commandbutton)` | caption "\<Behind the Scenes" | Opens Behind the Scenes modally; disabled if it is already open |
| `cmdCancel` | `tscommandbutton (commandbutton)` | caption "\<Cancel" | Cancel; `TABLEREVERT` |
| `cmdOK` | `tscommandbutton (commandbutton)` | caption "\<OK" | Default; `TABLEUPDATE` |
| `cntCustomerInfo` | `customerinfo ()` |  | The whole entry area; fourteen bound text boxes documented under `customerinfo` |

### Events with code

#### `cmdOK.Click`

Commits the buffered new row. Failures (duplicate ID 1884, field rule 1582) go to the form's `Error`, which forwards to the container so the right text box gets focus. **NOTE:** `llError` and `laError` are not declared `LOCAL`.

```foxpro
llError = !TABLEUPDATE(.T.)
IF llError
  IF AERROR(laError) > 0
    thisform.Error(laError[1])
  ENDIF
ELSE
*-- ... 3 more lines of Microsoft's Tastrade source omitted; see `cmdOK.Click` in your own copy of Tastrade.
```

#### `cmdCancel.Click`

```foxpro
thisform.lRetVal = .F.
=TABLEREVERT()
RELEASE thisform
```

#### `cmdBehindSC.Click`

Runs Behind the Scenes modally because this form is modal, then disables the button for the rest of the dialog.

```foxpro
*-- Since this form is modal, we need to make
*-- 'Behind the Scenes' modal as well
DO FORM behindsc WITH .T.
SELECT customer
this.Enabled = .F.
```

## Form methods

#### `Init`

Appends the blank row (firing the DBC defaults) and seeds the company name from the parameter.

```foxpro
*-- (c) Microsoft Corporation 1995

LPARAMETERS tcCompanyName
tsBaseForm::Init()

APPEND BLANK
*-- ... 3 more lines of Microsoft's Tastrade source omitted; see `Init` in your own copy of Tastrade.
```

#### `Unload`

```foxpro
RETURN thisform.lRetVal
```

#### `Destroy`

Closing from the title bar (`ReleaseType = 1`) counts as Cancel.

```foxpro
tsBaseForm::Destroy()
IF thisform.ReleaseType = 1    && Form closed from close box
  thisform.lRetVal = .F.
  =TABLEREVERT()
ENDIF
```

#### `Error`

```foxpro
LPARAMETERS nError, cMethod, nLine
DO CASE
  CASE nError = 1884    && Primary key violated
    thisform.cntCustomerInfo.Error(nError, cMethod, nLine)
  CASE nError = 1582    && Field rule violated
    thisform.cntCustomerInfo.Error(nError, cMethod, nLine)
*-- ... 3 more lines of Microsoft's Tastrade source omitted; see `Error` in your own copy of Tastrade.
```

#### `Activate`

```foxpro
*-- Disable command button if Behind the Scenes is
*-- already active
thisform.cmdBehindSC.Enabled = !WEXIST("frmBehindSC")
```

## Tables read / written

| Table | Access | How |
|---|---|---|
| `CUSTOMER` | write | One appended row, committed by OK; the user types the primary key |

## Inter-form navigation

- **← [[ordentry.md]]** only.
- **→ [[behindsc.md]]** modally.

## Notes

- **`lretval` defaults to `.T.`**; Cancel and the close box clear it. Any other exit reports success.
- **Same container, different form base**: [[customer.md]] uses `tsmaintform` with the toolbar; this uses `tsbaseform` modally with its own OK/Cancel. The container's `Error` works in both because it only touches its own controls.
