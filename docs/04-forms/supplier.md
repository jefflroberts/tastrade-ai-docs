# frmsuppliers (supplier.scx)

| Source file | Type | Path |
|---|---|---|
| `supplier.scx` | Form | `forms/supplier.sc2` |

**Purpose:** Maintain suppliers: company, contact, address, and phone details. Nine bound text boxes and a ten-column list.

**Used by:**
- The Maintenance menu ([[../07-menus/main.md]]) bar "Suppliers": `oApp.DoForm("frmsuppliers")`, `SKIP FOR WEXIST("frmSuppliers")` so only one instance opens.
- [[product.md]] reads the table through its supplier combo; view `SUPPLIER LISTING` feeds [[../06-reports/listsupp.md]].

**Related docs:** [[../03-data-model/tables/supplier.md]], [[../05-classes/tsbase.md]] (`tsmaintform`), [[README.md]].

This is one of the six `tsmaintform` forms. The pattern, documented once in [[../05-classes/tsbase.md]]: a two-page pageframe (**Data Entry** with bound controls, **List** with a read-only `tsgrid` over the same cursor), the shared navigation toolbar for First/Prior/Next/Last/New/Save/Restore/Close, optimistic table buffering committed by `TABLEUPDATE`, and an `Error` method that turns DBC rule and trigger failures into messages. Each form adds only its bindings, a focus target for `AddNew`, the field-rule-to-control mapping in `Error`, and the trigger-failure message text in `Init`.

## Form metadata

- Base class / parent: `tsmaintform` of `..\libs\tsbase.vcx` → `tsbaseform` → `form`
- Caption: "Suppliers"; icon `..\bitmaps\spplrs.ico`
- Modal: no. MDI child with the navigation toolbar; new/edit/delete allowed (inherited defaults)
- Data session: private (`DataSession = 2`); `AutoCenter = .F.` (INI position); `ScaleMode = 3` (pixels)

## DataEnvironment

| Cursor | Alias | Source | Order | Filter |
|---|---|---|---|---|
| `cursor1` | `Supplier` | `Supplier` | `company_na` |  |

`InitialSelectedAlias = "Supplier"`, ordered by upper-cased company name.

## Controls (depth-first)

| Container path | Class | Bound to / key properties | Role |
|---|---|---|---|
| `pageframe1.page1.Tslabel1` | `tslabel (label)` | caption "Company" |  |
| `pageframe1.page1.Tslabel10` | `tslabel (label)` | caption "Fax" |  |
| `pageframe1.page1.Tslabel2` | `tslabel (label)` | caption "Contact" |  |
| `pageframe1.page1.Tslabel3` | `tslabel (label)` | caption "Title" |  |
| `pageframe1.page1.Tslabel4` | `tslabel (label)` | caption "Address" |  |
| `pageframe1.page1.Tslabel5` | `tslabel (label)` | caption "City" |  |
| `pageframe1.page1.Tslabel6` | `tslabel (label)` | caption "Region" |  |
| `pageframe1.page1.Tslabel7` | `tslabel (label)` | caption "Postal Code" |  |
| `pageframe1.page1.Tslabel8` | `tslabel (label)` | caption "Country" |  |
| `pageframe1.page1.Tslabel9` | `tslabel (label)` | caption "Phone" |  |
| `pageframe1.page1.txtAddress` | `tstextbox (textbox)` | → `supplier.address` |  |
| `pageframe1.page1.txtCity` | `tstextbox (textbox)` | → `supplier.city` |  |
| `pageframe1.page1.txtCompany_Name` | `tstextbox (textbox)` | → `supplier.company_name` | Required by the DBC rule |
| `pageframe1.page1.txtContact_Name` | `tstextbox (textbox)` | → `supplier.contact_name` |  |
| `pageframe1.page1.txtContact_Title` | `tstextbox (textbox)` | → `supplier.contact_title` |  |
| `pageframe1.page1.txtCountry` | `tstextbox (textbox)` | → `supplier.country` |  |
| `pageframe1.page1.txtFax` | `tstextbox (textbox)` | → `supplier.fax` |  |
| `pageframe1.page1.txtPhone` | `tstextbox (textbox)` | → `supplier.phone` |  |
| `pageframe1.page1.txtPostal_Code` | `tstextbox (textbox)` | → `supplier.postal_code` |  |
| `pageframe1.page1.txtRegion` | `tstextbox (textbox)` | → `supplier.region` |  |

The List page's grid headers and cells (20 objects under `pageframe1.page2.grdlist`) are listed as columns below rather than one row each.

List page grid (`ColumnCount = 10`):

| Order | Column | Header | ControlSource | Notes |
|---|---|---|---|---|
| 1 | `grcName` | Name | `Supplier.company_name` |  |
| 2 | `grcAddress` | Address | `Supplier.address` |  |
| 3 | `grcCity` | City | `Supplier.city` |  |
| 4 | `grcRegion` | Region | `Supplier.region` |  |
| 5 | `grcContactName` | Contact Name | `Supplier.contact_name` |  |
| 6 | `grcContactTitle` | Contact Title | `Supplier.contact_title` |  |
| 7 | `grcPostalCode` | Postal Code | `Supplier.postal_code` |  |
| 8 | `grcCountry` | Country | `Supplier.country` |  |
| 9 | `grcPhone` | Phone | `Supplier.phone` |  |
| 10 | `grcFax` | Fax | `Supplier.fax` |  |

## Form methods

#### `Init`

Delete-trigger message `DELSUPPLIER_LOC`: "Products are supplied by this supplier. Cannot delete!"

```foxpro
*-- (c) Microsoft Corporation 1995

tsBaseForm::Init()
this.aErrorMsg[DELETETRIG] = DELSUPPLIER_LOC
```

#### `addnew`

```foxpro
tsMaintForm::AddNew()
thisform.pageframe1.page1.txtCompany_Name.SetFocus()
```

#### `Error`

Field rule on `COMPANY_NAME` refocuses the company name.

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
| `SUPPLIER` | both | DataEnvironment; `newid()` default fills `supplier_id` |

## Inter-form navigation

- **← Maintenance menu** only.

## Notes

- Identical in structure to [[customer.md]] minus the credit fields, but the customer form uses the shared `customerinfo` container while this one lays its text boxes out directly. Two ways of doing the same thing in one sample.
- `supplier_id` is never shown.
