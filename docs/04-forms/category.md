# frmcategory (category.scx)

| Source file | Type | Path |
|---|---|---|
| `category.scx` | Form | `forms/category.sc2` |

**Purpose:** Maintain the eight product categories: name, description, and a picture stored both as a file name and as an OLE General field.

**Used by:**
- The Maintenance menu ([[../07-menus/main.md]]) bar "Categories": `oApp.DoForm("frmcategory")`, `SKIP FOR WEXIST("frmCategory")` so only one instance opens.
- [[product.md]] reads the table through its category combo; view `CATEGORY LISTING` feeds [[../06-reports/listcat.md]].

**Related docs:** [[../03-data-model/tables/category.md]], [[../05-classes/tsbase.md]] (`tsmaintform`), [[README.md]].

This is one of the six `tsmaintform` forms. The pattern, documented once in [[../05-classes/tsbase.md]]: a two-page pageframe (**Data Entry** with bound controls, **List** with a read-only `tsgrid` over the same cursor), the shared navigation toolbar for First/Prior/Next/Last/New/Save/Restore/Close, optimistic table buffering committed by `TABLEUPDATE`, and an `Error` method that turns DBC rule and trigger failures into messages. Each form adds only its bindings, a focus target for `AddNew`, the field-rule-to-control mapping in `Error`, and the trigger-failure message text in `Init`.

## Form metadata

- Base class / parent: `tsmaintform` of `..\libs\tsbase.vcx` → `tsbaseform` → `form`
- Caption: "Categories"; icon `..\bitmaps\catgry.ico`
- Modal: no. MDI child with the navigation toolbar; new/edit/delete allowed (inherited defaults)
- Data session: private (`DataSession = 2`); `AutoCenter = .F.` (INI position); `ScaleMode = 3` (pixels)

## DataEnvironment

| Cursor | Alias | Source | Order | Filter |
|---|---|---|---|---|
| `Cursor1` | `Category` | `Category` | `category_n` |  |

`InitialSelectedAlias = "Category"`, ordered by upper-cased name.

## Controls (depth-first)

| Container path | Class | Bound to / key properties | Role |
|---|---|---|---|
| `pageframe1.page1.cmdPicture` | `tscommandbutton (commandbutton)` | caption "Change Picture" | Caption switches between "Add Picture" and "Change Picture" |
| `pageframe1.page1.edtDescription` | `tseditbox (editbox)` | → `Category.description` | Memo |
| `pageframe1.page1.imgPicture` | `image (label)` |  | Shows `picture_file`; `Stretch = 2` (stretch to fit) |
| `pageframe1.page1.Tslabel1` | `tslabel (label)` | caption "Name" | "Name" |
| `pageframe1.page1.Tslabel2` | `tslabel (label)` | caption "Description" | "Description" |
| `pageframe1.page1.txtCategory_Name` | `tstextbox (textbox)` | → `Category.category_name` | Name; the DBC rule requires it non-empty |

The List page's grid headers and cells (4 objects under `pageframe1.page2.grdlist`) are listed as columns below rather than one row each.

List page grid (`ColumnCount = 2`):

| Order | Column | Header | ControlSource | Notes |
|---|---|---|---|---|
| 1 | `grcName` | Name | `Category.category_name` |  |
| 2 | `grcDescription` | Description | `LEFT(Category.description, 60)` |  |

The description column shows `LEFT(Category.description, 60)`, an expression rather than a field, so the memo is truncated in the list.

### Events with code

#### `pageframe1.page1.cmdPicture.Click`

`GETFILE("BMP")` picks a bitmap; the path goes into `picture_file` **and** the bitmap is loaded into the General field `picture` with `APPEND GENERAL`. **NOTE:** the General field copy is never read by this form (`refreshform` displays the file), so the OLE object is dead weight; and the stored path is absolute to the machine the file was picked on.

```foxpro
LOCAL lcFileName

lcFileName = GETFILE("BMP", ;
                    this.Caption, ;
                    SELECTBUTTON_LOC)

*-- ... 6 more lines of Microsoft's Tastrade source omitted; see `pageframe1.page1.cmdPicture.Click` in your own copy of Tastrade.
```

#### `pageframe1.page1.cmdPicture.Refresh`

```foxpro
IF "3" $ GETFLDSTATE(-1, "category") OR "4" $ GETFLDSTATE(-1, "category")
  this.Caption = ADDPICTURE_LOC
ELSE
  this.Caption = CHANGEPICTURE_LOC
ENDIF
```

## Form methods

#### `Init`

Calls `tsBaseForm::Init` directly, skipping `tsmaintform` (which has no `Init`, so no difference). Delete-trigger message `DELCATEGORY_LOC`: "Products belong to this category. Cannot delete!"

```foxpro
tsBaseForm::Init()
this.aErrorMsg[DELETETRIG] = DELCATEGORY_LOC
```

#### `addnew`

```foxpro
*-- (c) Microsoft Corporation 1995

tsMaintForm::AddNew()
this.pageframe1.page1.txtCategory_Name.SetFocus()
```

#### `Error`

Field rule on `CATEGORY_NAME` refocuses the name.

```foxpro
LPARAMETERS nError, cMethod, nLine

LOCAL laError[AERRORARRAY], ;
      lcMessage
=AERROR(laError)

*-- ... 13 more lines of Microsoft's Tastrade source omitted; see `Error` in your own copy of Tastrade.
```

#### `refreshform`

Overrides the base to load the picture from `picture_file` (blank if the file is missing) before the normal refresh.

```foxpro
LOCAL lcFile

IF FILE(category.picture_file)
	lcFile = category.picture_file
ELSE
	lcFile = ''
*-- ... 4 more lines of Microsoft's Tastrade source omitted; see `refreshform` in your own copy of Tastrade.
```

## Tables read / written

| Table | Access | How |
|---|---|---|
| `CATEGORY` | both | DataEnvironment; `picture_file` and General `picture` written by the picture button |

## Inter-form navigation

- **← Maintenance menu** only. Opens the `GETFILE` dialog.

## Notes

- **Two copies of the picture**, file path and OLE object, and only the path is used. A rebuild keeps the file.
- **Absolute paths in data**: `picture_file` holds whatever `GETFILE` returned.
- `category_id` is never shown.
