# frmcustomers (customer.scx)

| Source file | Type | Path |
|---|---|---|
| `customer.scx` | Form | `forms/customer.sc2` |

**Purpose:** Maintain customers. The Data Entry page is the shared `customerinfo` container (company, contact, address, credit terms); the List page is a fourteen-column grid.

**Used by:**
- The Maintenance menu ([[../07-menus/main.md]]) bar "Customers": `oApp.DoForm("frmcustomers")`, `SKIP FOR WEXIST("frmCustomers")` so only one instance opens.
- [[custadd.md]] uses the same `customerinfo` container to add a customer from order entry.
- [[ordhist.md]], opened while this form is on top, starts on this form's current customer by reading its data session.
- View `CUSTOMER LISTING` feeds [[../06-reports/listcust.md]].

**Related docs:** [[../03-data-model/tables/customer.md]], [[../05-classes/tsgen.md]] (`customerinfo`, where the bound controls, the `Error` handler, and the min/max validation live), [[../05-classes/tsbase.md]] (`tsmaintform`), [[README.md]].

This is one of the six `tsmaintform` forms. The pattern, documented once in [[../05-classes/tsbase.md]]: a two-page pageframe (**Data Entry** with bound controls, **List** with a read-only `tsgrid` over the same cursor), the shared navigation toolbar for First/Prior/Next/Last/New/Save/Restore/Close, optimistic table buffering committed by `TABLEUPDATE`, and an `Error` method that turns DBC rule and trigger failures into messages. Each form adds only its bindings, a focus target for `AddNew`, the field-rule-to-control mapping in `Error`, and the trigger-failure message text in `Init`.

## Form metadata

- Base class / parent: `tsmaintform` of `..\libs\tsbase.vcx` → `tsbaseform` → `form`
- Caption: "Customers"; icon `..\bitmaps\cust.ico`
- Modal: no. MDI child with the navigation toolbar; new/edit/delete allowed (inherited defaults)
- Data session: private (`DataSession = 2`); `AutoCenter = .F.` (INI position); `ScaleMode = 3` (pixels)

## DataEnvironment

| Cursor | Alias | Source | Order | Filter |
|---|---|---|---|---|
| `cursor1` | `Customer` | `Customer` | `customer_i` |  |

`InitialSelectedAlias = "Customer"`, ordered by **customer ID**, unlike the other maintenance forms which order by name.

## Controls (depth-first)

| Container path | Class | Bound to / key properties | Role |
|---|---|---|---|
| `pageframe1.page1.cntCustomerInfo` | `customerinfo ()` |  | The whole Data Entry page; its fourteen bound text boxes are documented under `customerinfo` in [[../05-classes/tsgen.md]] |

The List page's grid headers and cells (28 objects under `pageframe1.page2.grdlist`) are listed as columns below rather than one row each.

List page grid (`ColumnCount = 14`, displayed in `ColumnOrder`):

| Order | Column | Header | ControlSource | Notes |
|---|---|---|---|---|
| 1 | `grcID` | ID | `Customer.customer_id` |  |
| 2 | `grcName` | Name | `Customer.company_name` |  |
| 3 | `grcContactName` | Contact Name | `Customer.contact_name` |  |
| 4 | `grcContactTitle` | Contact Title | `Customer.contact_title` |  |
| 5 | `grcAddress` | Address | `Customer.address` |  |
| 6 | `grcCity` | City | `Customer.city` |  |
| 7 | `grcRegion` | Region | `Customer.region` |  |
| 8 | `grcPostalCode` | Postal Code | `Customer.postal_code` |  |
| 9 | `grcCountry` | Country | `Customer.country` |  |
| 10 | `grcPhone` | Phone | `Customer.phone` |  |
| 11 | `grcFax` | Fax | `Customer.fax` |  |
| 12 | `grcMaxOrderAmt` | Max Order Amt | `Customer.max_order_amt` | mask `$$9,999,999,999.99` |
| 13 | `grcMinOrderAmt` | Min Order Amt | `Customer.min_order_amt` | mask `$$9,999,999,999.99` |
| 14 | `grcDiscount` | Discount | `Customer.discount` | mask `99.99%` |

`ColumnOrder` reorders the columns so contact name and title follow the company name although they were added last.

### Events with code

#### `pageframe1.page1.cntCustomerInfo.txtCustomer_ID.Refresh`

The customer ID is the primary key and is typed by the user (no `newid()` default on this table), so it is editable only on a new record. The `ISNULL` guard handles a refresh before any record exists.

```foxpro
*-- Only allow change to customer ID if we're adding a new record.
this.Enabled = IIF(ISNULL(GETFLDSTATE(-1, "customer")),.F.,("3" $ GETFLDSTATE(-1, "customer") OR "4" $ GETFLDSTATE(-1, "customer")))
```

## Form methods

#### `Init`

Delete-trigger message `DELCUSTOMER_LOC`: "Customer has orders. Cannot delete!"

```foxpro
*-- (c) Microsoft Corporation 1995

tsBaseForm::Init()
this.aErrorMsg[DELETETRIG] = DELCUSTOMER_LOC
```

#### `addnew`

Focus goes to the ID inside the container.

```foxpro
tsMaintForm::AddNew()
thisform.pageframe1.page1.cntCustomerInfo.txtCustomer_ID.SetFocus()
```

#### `Error`

Primary-key (1884) and field-rule (1582) errors are delegated to the container's `Error`, which knows which text box to focus; everything else goes to the base.

```foxpro
LPARAMETERS nError, cMethod, nLine
DO CASE
  CASE nError = 1884    && Primary key violated
    thisform.pageframe1.page1.cntCustomerInfo.Error(nError, cMethod, nLine)
  CASE nError = 1582    && Field rule violated
    thisform.pageframe1.page1.cntCustomerInfo.Error(nError, cMethod, nLine)
*-- ... 3 more lines of Microsoft's Tastrade source omitted; see `Error` in your own copy of Tastrade.
```

## Tables read / written

| Table | Access | How |
|---|---|---|
| `CUSTOMER` | both | DataEnvironment; ID typed by the user |

## Inter-form navigation

- **← Maintenance menu**.
- **→ [[ordhist.md]]** indirectly: Order History opened from the menu while this form is active picks up its customer.

## Notes

- **User-typed primary key**, upper-cased by the container's `K!` format; duplicates surface as error 1884 at save.
- **The grid shows credit limits and discount** with masks `$$9,999,999,999.99` and `99.99%`; the discount mask shows two decimals for an integer percent.
- **The form itself has almost no code**; the behaviour is in `customerinfo` and `tsmaintform`.
