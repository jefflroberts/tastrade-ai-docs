# form1 (getinv.scx)

| Source file | Type | Path |
|---|---|---|
| `getinv.scx` | Form | `forms/getinv.sc2` |

**Purpose:** The invoice report's parameter dialog: an order date range, returned to the report's data environment which feeds it to the `ORDERS VIEW` parameters `?dDateFrom` and `?dDateTo`.

**Used by:**
- `reports/orders.frx`'s data environment `Init` ([[../06-reports/orders.md]]): `DO FORM forms\getinv NAME loGetInvoice LINKED`, then reads `lRetVal`, `dDateFrom`, `dDateTo` from the object.

**Related docs:** [[../05-classes/tsgen.md]] (`daterange`), [[../03-data-model/README.md]] (`ORDERS VIEW`), [[README.md]].

One of two forms with **no framework base**: the form class is the VFP `form`, named `form1` (the designer default), and its DataEnvironment is empty. It runs inside a report's data environment, so it must not depend on `oApp` or the toolbar. The `daterange` control and the `ts*` buttons are the only framework pieces it uses.

## Form metadata

- Base class / parent: `form` (no framework base); class name `form1`
- Caption: "Report Parameters"
- Modal: yes (`WindowType = 1`), `AutoCenter`, no Min/Max buttons
- Run `LINKED` and `NAME`d by the caller, which reads the properties after `Show` returns

**Custom properties:**

| Property | Description |
|---|---|
| `ddatefrom` | Holds the beginning date for the report. |
| `ddateto` | Holds the ending date for the report. |
| `lretval` | Returns .T. if OK was clicked, otherwise returns .F. |

## DataEnvironment

No cursors. The caller (the report) owns the data.

## Controls (depth-first)

| Container path | Class | Bound to / key properties | Role |
|---|---|---|---|
| `cmdCancel` | `tscommandbutton (commandbutton)` | caption "\<Cancel" | Sets `lRetVal = .F.` |
| `cmdOK` | `tscommandbutton (commandbutton)` | caption "\<OK" | Default; also `Cancel = .T.`, see note |
| `ctlDateRange` | `daterange (control)` |  | From/To dates; `GetDateFrom()` and `GetDateTo()` (empty To = far future) |
| `Ts3dshape1` | `ts3dshape (shape)` |  |  |
| `Tslabel1` | `tslabel (label)` | caption "Order date range:" | "Order date range:" |

### Events with code

#### `cmdOK.Click`

Copies the range into the form properties and hides; hiding returns control to the report's `Init`.

```foxpro
thisform.dDateFrom = thisform.ctlDateRange.GetDateFrom()
thisform.dDateTo = thisform.ctlDateRange.GetDateTo()
thisform.Hide()
```

#### `cmdCancel.Click`

```foxpro
thisform.lRetVal = .F.
thisform.Hide()
```

## Form methods

#### `Activate`

```foxpro
SET MESSAGE TO thisform.Caption
```

#### `Unload`

```foxpro
*-- (c) Microsoft Corporation 1995

SET MESSAGE TO
```

## Tables read / written

| Table | Access | How |
|---|---|---|
| none |  |  |

## Inter-form navigation

- **← [[../06-reports/orders.md]]** only.
- `lretval` defaults to `.T.`; only Cancel clears it. Closing the dialog any other way counts as OK.

## Notes

- **`cmdOK` has both `Default = .T.` and `Cancel = .T.`**, so Escape triggers OK, not Cancel. `cmdCancel` has neither `Cancel` nor `Default`. Probably a designer slip; the visible captions say the opposite.
- **No validation on OK** beyond what `daterange.txtDateTo.Valid` did; an empty From date is allowed and means no lower bound.
- **Hides rather than releases**, because the caller still needs to read the properties; the caller's `LINKED` clause releases it.
