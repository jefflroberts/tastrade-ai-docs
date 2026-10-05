# frmproducts (product.scx)

| Source file | Type | Path |
|---|---|---|
| `product.scx` | Form | `forms/product.sc2` |

**Purpose:** Maintain the product catalogue: names, packaging, price and cost, stock counts, discontinued flag, and the supplier and category each product belongs to.

**Used by:**
- The Maintenance menu ([[../07-menus/main.md]]) bar "Products": `oApp.DoForm("frmproducts")`, `SKIP FOR WEXIST("frmProducts")` so only one instance opens.
- [[ordentry.md]] reads the table through its product combo and copies `unit_price` onto order lines; view `PRODUCT LISTING` feeds [[../06-reports/listprod.md]].

**Related docs:** [[../03-data-model/tables/products.md]], [[../03-data-model/tables/supplier.md]], [[../03-data-model/tables/category.md]], [[../05-classes/tsbase.md]] (`tsmaintform`), [[README.md]].

This is one of the six `tsmaintform` forms. The pattern, documented once in [[../05-classes/tsbase.md]]: a two-page pageframe (**Data Entry** with bound controls, **List** with a read-only `tsgrid` over the same cursor), the shared navigation toolbar for First/Prior/Next/Last/New/Save/Restore/Close, optimistic table buffering committed by `TABLEUPDATE`, and an `Error` method that turns DBC rule and trigger failures into messages. Each form adds only its bindings, a focus target for `AddNew`, the field-rule-to-control mapping in `Error`, and the trigger-failure message text in `Init`.

## Form metadata

- Base class / parent: `tsmaintform` of `..\libs\tsbase.vcx` → `tsbaseform` → `form`
- Caption: "Products"; icon `..\bitmaps\prod1.ico`
- Modal: no. MDI child with the navigation toolbar; new/edit/delete allowed (inherited defaults)
- Data session: private (`DataSession = 2`); `AutoCenter = .F.` (INI position); `ScaleMode = 3` (pixels)

## DataEnvironment

| Cursor | Alias | Source | Order | Filter |
|---|---|---|---|---|
| `Cursor1` | `Products` | `Products` | `product_na` |  |
| `Cursor2` | `Supplier` | `Supplier` |  |  |
| `Cursor3` | `Category` | `Category` |  |  |

`InitialSelectedAlias = "Products"`, ordered by upper-cased product name. Two relations, `Products` → `Supplier` on `supplier_id` and `Products` → `Category` on `category_id`, let the List grid show the supplier and category **names** from the related cursors. `BeforeOpenTables` sets `TALK OFF`, `EXCLUSIVE OFF`, `DELETED ON`, `SET DATABASE TO TASTRADE` for the private session:

```foxpro
SET TALK OFF
SET EXCLUSIVE OFF
SET DELETED ON
SET DATABASE TO TASTRADE
```

## Controls (depth-first)

| Container path | Class | Bound to / key properties | Role |
|---|---|---|---|
| `pageframe1.page1.cboCategory_ID` | `tscombobox (combobox)` | → `Products.category_id`; rows `select category_name, category_id from category order by category_name into cursor cCategory` | Category drop-down, `BoundColumn = 2` |
| `pageframe1.page1.cboSupply_ID` | `tscombobox (combobox)` | → `products.supplier_id`; rows `select company_name, supplier_id from supplier order by company_name into cursor cSupplier` | Supplier drop-down, `BoundColumn = 2`; its `Init` re-assigns the same binding and row source |
| `pageframe1.page1.chkDiscontinued` | `tscheckbox (checkbox)` | caption "\<Discontinued"; → `Products.discontinued` | "Discontinued" |
| `pageframe1.page1.Tslabel1` | `tslabel (label)` | caption "Product Name" |  |
| `pageframe1.page1.Tslabel10` | `tslabel (label)` | caption "In Stock" |  |
| `pageframe1.page1.Tslabel2` | `tslabel (label)` | caption "English Name" |  |
| `pageframe1.page1.Tslabel3` | `tslabel (label)` | caption "Number In Unit" |  |
| `pageframe1.page1.Tslabel4` | `tslabel (label)` | caption "Unit Price" |  |
| `pageframe1.page1.Tslabel5` | `tslabel (label)` | caption "Unit Cost" |  |
| `pageframe1.page1.Tslabel6` | `tslabel (label)` | caption "Supplier" |  |
| `pageframe1.page1.Tslabel7` | `tslabel (label)` | caption "Category" |  |
| `pageframe1.page1.Tslabel8` | `tslabel (label)` | caption "Reorder Level" |  |
| `pageframe1.page1.Tslabel9` | `tslabel (label)` | caption "On Order" |  |
| `pageframe1.page1.txtEnglish_Name` | `tstextbox (textbox)` | → `Products.english_name` |  |
| `pageframe1.page1.txtProduct_Name` | `tstextbox (textbox)` | → `Products.product_name` | Required by the DBC rule |
| `pageframe1.page1.txtQuantity_In_Unit` | `tstextbox (textbox)` | → `Products.quantity_in_unit` |  |
| `pageframe1.page1.txtReorder_Level` | `tstextbox (textbox)` | → `Products.reorder_level` | N(12,3) |
| `pageframe1.page1.txtUnit_Cost` | `tstextbox (textbox)` | → `Products.unit_cost` | Currency |
| `pageframe1.page1.txtUnit_Price` | `tstextbox (textbox)` | → `Products.unit_price` | Currency |
| `pageframe1.page1.txtUnits_In_Stock` | `tstextbox (textbox)` | → `Products.units_in_stock` | N(12,3) |
| `pageframe1.page1.txtUnits_On_Order` | `tstextbox (textbox)` | → `Products.units_on_order` | N(12,3) |

The List page's grid headers and cells (23 objects under `pageframe1.page2.grdlist`) are listed as columns below rather than one row each.

List page grid (`ColumnCount = 11`, displayed in `ColumnOrder`):

| Order | Column | Header | ControlSource | Notes |
|---|---|---|---|---|
| 1 | `grcProductName` | Product Name | `Products.product_name` |  |
| 2 | `grcEnglishName` | English Name | `Products.english_name` |  |
| 3 | `grcUnitCost` | Unit Cost | `Products.unit_cost` |  |
| 4 | `grcUnitPrice` | Unit Price | `Products.unit_price` |  |
| 5 | `grcQtyInUnit` | Qty In Unit | `Products.quantity_in_unit` |  |
| 6 | `grcUnitsInStock` | Units In Stock | `Products.units_in_stock` |  |
| 7 | `grcUnitsOnOrder` | Units On Order | `Products.units_on_order` |  |
| 8 | `grcReorderLevel` | Reorder Level | `Products.reorder_level` |  |
| 9 | `grcDiscontinued` | Discontinued | `Products.discontinued` | current control `Text1` |
| 10 | `grcSupplier` | Supplier | `Supplier.company_name` |  |
| 11 | `grcCategory` | Category | `Category.category_name` |  |

Columns 10 and 11 are bound to `Supplier.company_name` and `Category.category_name` through the DataEnvironment relations. Column 9 (`discontinued`) has `Sparse = .F.` and a `tscheckbox` (`Tscheckbox1`) placed in the column but `CurrentControl = "Text1"`, so the checkbox is present but not the displayed control. **NOTE:** likely a half-finished change; the list shows `.T.`/`.F.` text.

### Events with code

#### `pageframe1.page1.cboSupply_ID.Init`

Sets `ControlSource` and `RowSource` to the values the designer already stored; redundant.

```foxpro
THIS.ControlSource = "products.supplier_id"
THIS.RowSource = "select company_name, supplier_id from supplier order by company_name into cursor cSupplier"
```

#### `pageframe1.page1.cboSupply_ID.Destroy`

```foxpro
*-- Destroy the alias created in the RowSource property
IF USED("cSupplier")
  USE IN cSupplier
ENDIF
```

#### `pageframe1.page1.cboCategory_ID.Destroy`

```foxpro
*-- Destroy the alias created in the RowSource property
IF USED("cCategory")
  USE IN cCategory
ENDIF
```

## Form methods

#### `Init`

Two trigger messages: delete `DELPRODUCT_LOC` "Product exists on order line items. Cannot delete!" and insert `INSPRODUCT_LOC` "All products must be assigned a supplier and a category." The insert message is what the user sees when the RI insert trigger refuses a product with a missing supplier or category.

```foxpro
*-- (c) Microsoft Corporation 1995

tsBaseForm::Init()

this.aErrorMsg[DELETETRIG] = DELPRODUCT_LOC
this.aErrorMsg[INSERTTRIG] = INSPRODUCT_LOC
```

#### `addnew`

```foxpro
tsMaintForm::AddNew()
thisform.pageframe1.page1.txtProduct_Name.SetFocus()
```

#### `Destroy`

Drops the relations on `products` before the base closes the tables.

```foxpro
tsMaintForm::Destroy()
IF USED("products")
  SELECT products
  SET RELATION TO
ENDIF
```

#### `Error`

Field rule on `PRODUCT_NAME` refocuses the name.

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
| `PRODUCTS` | both | DataEnvironment; `newid()` default fills `product_id` |
| `SUPPLIER` | read | DataEnvironment (related) and combo cursor `cSupplier` |
| `CATEGORY` | read | DataEnvironment (related) and combo cursor `cCategory` |

## Inter-form navigation

- **← Maintenance menu** only.

## Notes

- **Stock is edited by hand.** `units_in_stock` and `units_on_order` are plain text boxes; nothing in the application adjusts them when orders are saved (confirmed in [[ordentry.md]]). Inventory is decorative in this sample.
- **Fractional stock**: the three quantity fields are `N(12,3)` with no mask.
- **Unit price changes do not touch existing orders**; order lines keep the price copied at entry time.
