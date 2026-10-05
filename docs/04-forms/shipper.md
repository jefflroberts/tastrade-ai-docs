# frmshippers (shipper.scx)

| Source file | Type | Path |
|---|---|---|
| `shipper.scx` | Form | `forms/shipper.sc2` |

**Purpose:** Maintain the three shipping companies. The simplest form in the application: one bound text box and a one-column list.

**Used by:**
- The Maintenance menu ([[../07-menus/main.md]]) bar "Shippers": `oApp.DoForm("frmshippers")`, `SKIP FOR WEXIST("frmShippers")` so only one instance opens.
- [[ordentry.md]] reads the same table through its shipper combo.

**Related docs:** [[../03-data-model/tables/shippers.md]], [[../05-classes/tsbase.md]] (`tsmaintform`), [[README.md]].

This is one of the six `tsmaintform` forms. The pattern, documented once in [[../05-classes/tsbase.md]]: a two-page pageframe (**Data Entry** with bound controls, **List** with a read-only `tsgrid` over the same cursor), the shared navigation toolbar for First/Prior/Next/Last/New/Save/Restore/Close, optimistic table buffering committed by `TABLEUPDATE`, and an `Error` method that turns DBC rule and trigger failures into messages. Each form adds only its bindings, a focus target for `AddNew`, the field-rule-to-control mapping in `Error`, and the trigger-failure message text in `Init`.

## Form metadata

- Base class / parent: `tsmaintform` of `..\libs\tsbase.vcx` → `tsbaseform` → `form`
- Caption: "Shippers"; icon `..\bitmaps\shpprs1.ico`
- Modal: no. MDI child with the navigation toolbar; new/edit/delete allowed (inherited defaults)
- Data session: **default (shared)**, the only maintenance form without `DataSession = 2`; `AutoCenter = .F.` (INI position); `ScaleMode = 3` (pixels)
- `WindowState = 0`

## DataEnvironment

| Cursor | Alias | Source | Order | Filter |
|---|---|---|---|---|
| `cursor1` | `Shippers` | `Shippers` | `company_na` |  |

`InitialSelectedAlias = "Shippers"`, ordered by company name.

## Controls (depth-first)

| Container path | Class | Bound to / key properties | Role |
|---|---|---|---|
| `pageframe1.page1.Tslabel1` | `tslabel (label)` | caption "Company" | "Company" |
| `pageframe1.page1.txtCompany_Name` | `tstextbox (textbox)` | → `shippers.company_name` | The only editable field |

The List page's grid headers and cells (2 objects under `pageframe1.page2.grdlist`) are listed as columns below rather than one row each.

List page grid (`ColumnCount = 1`):

| Order | Column | Header | ControlSource | Notes |
|---|---|---|---|---|
| 1 | `grcName` | Name | `Shippers.company_name` |  |

## Form methods

#### `Init`

Delete-trigger failures show `DELSHIPPER_LOC`: "Shipper exists on orders. Cannot delete!"

```foxpro
*-- (c) Microsoft Corporation 1995

tsBaseForm::Init()
this.aErrorMsg[DELETETRIG] = DELSHIPPER_LOC
```

#### `addnew`

Focus the company name after the base appends the record.

```foxpro
tsMaintForm::AddNew()
thisform.pageframe1.page1.txtCompany_Name.SetFocus()
```

#### `Error`

Field rule 1582 on `COMPANY_NAME` (the DBC's not-empty rule) refocuses the text box after the base shows the rule text.

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
| `SHIPPERS` | both | DataEnvironment; `newid()` default fills `shipper_id` on append |

## Inter-form navigation

- **← Maintenance menu** only. Opens nothing.

## Notes

- **Shared data session.** Unlike its five siblings this form runs in the default session, so its `Shippers` alias is the same one the order entry form's combo cursor is built from. Probably an oversight; harmless because both are read-mostly.
- `shipper_id` is never shown; the ID is invisible to the user.
