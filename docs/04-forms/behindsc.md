# frmbehindsc (behindsc.scx)

| Source file | Type | Path |
|---|---|---|
| `behindsc.scx` | Form | `forms/behindsc.sc2` |

**Purpose:** The sample's self-documentation: a list of design topics per form, read from the free table `behindsc.dbf`, with an explanation pane and a **Code** button that extracts the referenced methods, properties, programs, or stored procedures from the live `.scx`, `.vcx`, `.prg`, and `.dbc` files and shows them in a viewer.

**Used by:**
- The Maintenance menu ([[../07-menus/main.md]]) bar "Behind the Scenes": `oApp.DoForm("behindsc")`, `SKIP FOR WEXIST("frmBehindSC")`.
- The navigation toolbar's `cmdBehindSC` ([[../05-classes/tsbase.md]]): `oApp.DoForm("behindsc")`.
- `introform` ([[../05-classes/tsgen.md]]), [[custadd.md]], and [[chngpswd.md]]: `DO FORM behindsc WITH .T.` (modal, because those callers are modal).

**Related docs:** [[viewcode.md]] (the viewer it opens), [[../03-data-model/README.md]] (`behindsc.dbf` schema), [[../05-classes/tsgen.md]] (`splitter`), [[../06-reports/behindsc.md]] (the print), [[README.md]].

This form is the reason the sample calls itself "discoverable". Its `showcode` method opens `.scx` and `.vcx` files **as tables** (`USE ... ALIAS showmeth NOUPDATE`), locates the object record by `objname`, and pulls text out of the `methods` and `properties` memo fields, which is exactly what FoxBin2PRG does for this documentation, written in 1995 inside the application it documents.

## Form metadata

- Base class / parent: `tsbaseform` → `form`
- Caption: "Behind the Scenes"
- Modal or not depending on the `tlModal` parameter (`WindowType` set in `Init`); default data session; no toolbar; `BufferMode = 0`; new/edit/delete off
- Filters itself to the form that was active when it opened (`ccurrentform` from `_screen.ActiveForm.Caption`)

**Custom properties:**

| Property | Description |
|---|---|
| `ccurrentform` | The name of the currently active form. |
| `isplitwidth` |  |
| `aforms[1,0]` | Array for forms to hold scope. |
| `aobjsplitmove[1,0]` | This array holds references to screen objects that will need to be referenced by the splitter object to be moved. |

**Custom methods:**

| Method | Description |
|---|---|
| `extractallmethods` | Extracts all methods from the METHODS memo field of an SCX or VCX file. |
| `extractallproperties` | Extracts all properties from the PROPERTIES memo field of an SCX or VCX file. |
| `extractallstoredprocs` | Extracts all storec procedures from a DBC file. |
| `extractmethod` | Extracts a method from the METHODS memo field of an SCX or VCX file. |
| `extractmultimethods` | Extracts multiple, but not all, methods from the METHODS memo field of an SCX or VCX file. |
| `extractmultistoredprocs` | Extracts multiple, but not all, stored procedures from a DBC file. |
| `extractprg` | Extracts the contents of a PRG and writes it to the output file. |
| `extractstoredproc` | Extracts a single stored procedure from a DBC file. |
| `getfilename` | Extracts the file name from 'show code' string in behindsc.code_to_sh. |
| `getmethod` | Extracts the method name from 'show code' string in behindsc.code_to_sh. |
| `getobject` | Extracts the object name from 'show code' string in behindsc.code_to_sh. |
| `procstomem` | Dumps the contents of all stored procedures to a memory variable. |
| `refreshfeatures` | Refreshes the edit box containing the feature text. |
| `showcode` | Creates a text file with code based on instructions stored in behindsc.code_to_sh. |

## DataEnvironment

| Cursor | Alias | Source | Order |
|---|---|---|---|
| `Cursor1` | `behindsc` | `..\data\behindsc.dbf` | `screen_top` |

`behindsc.dbf` is a free table: `screen_id` (form name), `topic`, `desc` (memo, the explanation), `code_to_sh` (memo, extraction instructions). 65 rows over 21 screens, 53 with code instructions. Order `screen_top` is `screen_id + topic`.

## Controls (depth-first)

| Container path | Class | Bound to / key properties | Role |
|---|---|---|---|
| `cboForms` | `tscombobox (combobox)` |  | Form filter; row source is the `aForms` array ("All" plus every distinct `screen_id`) |
| `cmdClose` | `tscommandbutton (commandbutton)` | caption "\<Close" | Cancel |
| `cmdCode` | `tscommandbutton (commandbutton)` | caption "Co\<de" | Runs `showcode`; enabled only when the topic has `code_to_sh` |
| `cmdPrint` | `tscommandbutton (commandbutton)` | caption "\<Print" | Prints the current topic with `REPORT FORM behindsc NEXT 1` |
| `ctlSplitter` | `splitter (control)` |  | Drag bar between list and text (see note) |
| `edtFeatureText` | `tseditbox (editbox)` | → `behindsc.desc`; read-only | The explanation, read-only, bound to `behindsc.desc` |
| `lblHowItWorks` | `tslabel (label)` | caption "How I\<t Works" | "How It Works" |
| `lblSelectFeature` | `tslabel (label)` | caption "Desi\<gn Feature" | "Design Feature" |
| `lstFeatures` | `tslistbox (listbox)` | rows `behindsc.topic` | Topics in the current filter, `RowSourceType = 6` on `behindsc.topic` |

### The `code_to_sh` instruction format

Each line of the memo is `file, object, method` where object and method may be `*` (all), a single name, or a parenthesised comma list. Examples from the data:

```
ordentry.scx, cmdFind, click
tsbase.vcx, tsgrid, (refresh, sumcolumn)
behindsc.scx, cmdcode, click
tastrade.dbc, newid,
tsbase.vcx, tspasswordtextbox, *
```

The last example, under "Hiding Login Passwords", names a class `tspasswordtextbox` that does not exist in `tsbase.vcx` (see [[../05-classes/tsbase.md]]); the Code button for that topic reports the object was not found. The self-documentation has drifted from the code it documents.

### Events with code

#### `cboForms.InteractiveChange`

Changing the form filter re-filters and re-orders the table (by topic when "All") with a macro-substituted `SET FILTER`.

```foxpro
LOCAL lcValue

DO CASE
  CASE this.Value <> 1            && 1 is the "All Screens" case
    SET ORDER TO screen_top        && Order: by Screen and Topic

*-- ... 21 more lines of Microsoft's Tastrade source omitted; see `cboForms.InteractiveChange` in your own copy of Tastrade.
```

#### `cboForms.ProgrammaticChange`

```foxpro
this.InterActiveChange()
```

#### `lstFeatures.InteractiveChange`

```foxpro
thisform.RefreshFeatures()
```

#### `lstFeatures.Requery`

```foxpro
TSListBox::Requery
this.ListIndex = 1
```

#### `cmdCode.Click`

```foxpro
thisform.WaitMode(.T.)
thisform.ShowCode()
thisform.WaitMode(.F.)
```

#### `cmdPrint.Click`

The confirmation prompt is commented out.

```foxpro
LOCAL lnAnswer
*-lnAnswer = MESSAGEBOX(VIEWCSDTYPRINT_LOC, ;
*-                      MB_ICONQUESTION + MB_YESNO, ;
*-                      TASTRADE_LOC)
*-IF lnAnswer = IDYES
  thisform.WaitMode(.T.)
*-- ... 9 more lines of Microsoft's Tastrade source omitted; see `cmdPrint.Click` in your own copy of Tastrade.
```

#### `cmdClose.Click`

```foxpro
IF WEXIST("ShowMeth")
   RELEASE WINDOW "ShowMeth"
ENDIF

RELEASE thisform
```

`lstFeatures.Move`, `edtFeatureText.Move`, and `lblHowItWorks.Move` are overridden with **empty bodies**:

```foxpro
this.Width = thisform.ctlSplitter.GetLeftEdge() - this.Left
```

**NOTE:** the splitter calls `Move()` with no arguments on each of these three objects. With the override empty and no `NODEFAULT`, the native `Move` runs with no coordinates, which either errors (swallowed by the splitter's `lSetErrorOff`) or does nothing. Either way no object is repositioned: dragging the splitter moves the bar and nothing else. The resize feature is dead, and was presumably left this way once the empty overrides stopped it crashing.

## Form methods

#### `Load`

Captures the active form's caption as the starting filter, stripping the `:n` instance suffix and the " for <customer>" suffix the order history form adds.

```foxpro
LOCAL lcForm
IF FormIsObject()
  lcForm = _screen.Activeform.Caption
  *-- Special handling for Order History and forms that
  *-- support multiple instances
  IF ":" $ lcForm
*-- ... 13 more lines of Microsoft's Tastrade source omitted; see `Load` in your own copy of Tastrade.
```

#### `Init`

Modal or modeless by parameter; disables the toolbar's Behind the Scenes button; builds the form list from `SELECT DISTINCT screen_id`, inserting "All" first; loads the three objects the splitter should move; filters to the current form.

```foxpro
*-- (c) Microsoft Corporation 1995

LPARAMETERS tlModal
thisform.WindowType = IIF(tlModal, 1, 0)

IF TYPE("oApp.oToolbar") == "O"
*-- ... 45 more lines of Microsoft's Tastrade source omitted; see `Init` in your own copy of Tastrade.
```

#### `Destroy`

Removes the menu entry, the code window and its temp file, re-enables the toolbar button, nulls the object references.

```foxpro
LOCAL i

tsBaseForm::Destroy()
thisform.RemoveFromMenu()

IF WEXIST("SNIPPETS.TXT")
*-- ... 18 more lines of Microsoft's Tastrade source omitted; see `Destroy` in your own copy of Tastrade.
```

#### `refreshfeatures`

```foxpro
thisform.LockScreen = .T.

*-- Display the explanation of the feature.
THISFORM.edtFeatureText.SelStart = 0
thisform.edtFeatureText.Refresh()

thisform.cmdCode.Enabled = !EMPTY(behindsc.code_to_sh)
thisform.LockScreen = .F.
```

#### `refreshform`

```foxpro
thisform.LockScreen = .T.
thisform.Refresh()
thisform.cmdCode.Enabled = !EMPTY(behindsc.code_to_sh)
thisform.LockScreen = .F.
```

#### `showcode`

The extractor. For each instruction line: resolve the file type from its extension; programs are copied whole from `PROGS\`; stored procedures are pulled from the DBC via `COPY PROCEDURES TO` a temp file and searched for `FUNCTION name` ... `ENDFUNC`; forms and classes are opened as tables, the object located by `objname`, and the `properties` memo dumped plus the `methods` memo searched for `PROCEDURE name` ... `ENDPROC`. Everything is written to `SNIPPETS.TXT`, loaded into a one-row cursor `viewcode`, and shown by [[viewcode.md]] in this form's data session. **NOTE:** `USE (lcFileName) AGAIN ... NOUPDATE` opens the running application's own `.scx`/`.vcx` files; works in the IDE and from an EXE as long as the source files are present beside it.

```foxpro
LOCAL lnOldArea, ;
      lnOldRec, ;
      lnNumSnips, ;
      lcTextFileName, ;
      lnFileHandle, ;
      lnCounter, ;
*-- ... 143 more lines of Microsoft's Tastrade source omitted; see `showcode` in your own copy of Tastrade.
```

#### `extractmethod`

```foxpro
LPARAMETER tnFileHandle, tcMethod

LOCAL lnMemoLength, ;
      lnMethStartPos, ;
      lcMethod, ;
      lnLine, ;
*-- ... 28 more lines of Microsoft's Tastrade source omitted; see `extractmethod` in your own copy of Tastrade.
```

#### `extractallmethods`

```foxpro
LPARAMETERS tnFileHandle
LOCAL lcMethods, ;
      lnNextMethod, ;
      lcThisMethod, ;
      lnLine, ;
      lcOutputString
*-- ... 27 more lines of Microsoft's Tastrade source omitted; see `extractallmethods` in your own copy of Tastrade.
```

#### `extractmultimethods`

```foxpro
LPARAMETERS tnFileHandle, tcMethods

LOCAL lcMethods, ;
      lcThisMethod, ;
      lnNextMethod

*-- ... 14 more lines of Microsoft's Tastrade source omitted; see `extractmultimethods` in your own copy of Tastrade.
```

#### `extractallproperties`

```foxpro
LPARAMETERS tnFileHandle
LOCAL lnLine

IF EMPTY(showmeth.properties)
  RETURN ""
ENDIF
*-- ... 4 more lines of Microsoft's Tastrade source omitted; see `extractallproperties` in your own copy of Tastrade.
```

#### `extractprg`

```foxpro
LPARAMETERS tnOutFileHandle, tcFileName

LOCAL lnFileHandle

tcFileName = "PROGS\" + tcFileName

*-- ... 12 more lines of Microsoft's Tastrade source omitted; see `extractprg` in your own copy of Tastrade.
```

#### `extractstoredproc`

```foxpro
LPARAMETER tnFileHandle, tcProcToShow, tcStoredProc

LOCAL lnProcLength, ;
      lnProcStartPos, ;
      lnProcEndPos, ;
      lcProc, ;
*-- ... 29 more lines of Microsoft's Tastrade source omitted; see `extractstoredproc` in your own copy of Tastrade.
```

#### `extractmultistoredprocs`

```foxpro
LPARAMETER tnFileHandle, tcProcs, tcStoredProc

LOCAL lcProcs, ;
      lcThisProc, ;
      lnNextProc

*-- ... 14 more lines of Microsoft's Tastrade source omitted; see `extractmultistoredprocs` in your own copy of Tastrade.
```

#### `extractallstoredprocs`

```foxpro
LPARAMETERS tnOutFileHandle, tcTextFileName

=FCLOSE(tnOutFileHandle)

*-- We assume the database is open
COPY PROCEDURES TO (tcTextFileName) ADDITIVE
*-- ... 3 more lines of Microsoft's Tastrade source omitted; see `extractallstoredprocs` in your own copy of Tastrade.
```

#### `procstomem`

```foxpro
LPARAMETERS tcStoredProcFileName
LOCAL lnFileHandle, ;
      lnFileSize, ;
      lcStoredProcs

COPY PROCEDURES TO (tcStoredProcFileName)
*-- ... 7 more lines of Microsoft's Tastrade source omitted; see `procstomem` in your own copy of Tastrade.
```

#### `getfilename`

```foxpro
*-- Extract file name
LPARAMETER tcString
RETURN LEFT(tcString, AT(",", tcString) - 1)
```

#### `getobject`

```foxpro
LPARAMETERS tcString
LOCAL lnStartWord, ;
      lnEndWord

lnStartWord = AT(",", tcString, 1) + 1
IF LEFT(LTRIM(SUBSTR(tcString, lnStartWord)), 1) = "("
*-- ... 7 more lines of Microsoft's Tastrade source omitted; see `getobject` in your own copy of Tastrade.
```

#### `getmethod`

```foxpro
*-- Extract method name
LPARAMETER tcString
LOCAL lcMethod
lcMethod = ALLT(SUBSTR(tcString, AT(",", tcString, 2) + 1))

IF LEFT(lcMethod, 1) = "("
*-- ... 5 more lines of Microsoft's Tastrade source omitted; see `getmethod` in your own copy of Tastrade.
```

## Tables read / written

| Table | Access | How |
|---|---|---|
| `behindsc.dbf` (free) | read | DataEnvironment; filtered and reordered by code |
| `forms/*.scx`, `libs/*.vcx` | read as tables | `showcode`, alias `showmeth`, `NOUPDATE` |
| `progs/*.prg` | read | low-level file I/O |
| `tastrade.dbc` stored procedures | read | `COPY PROCEDURES TO` |
| `SNIPPETS.TXT`, `sproc.txt` | write, then delete | temp files in the current directory |

## Inter-form navigation

- **← Maintenance menu, toolbar, intro form, add-customer, change-password.**
- **→ [[viewcode.md]]** with this form's `DataSessionID` so the viewer can bind to the `viewcode` cursor.

## Notes

- **A source extractor inside the app.** Reading `.scx`/`.vcx` as DBF tables and splitting the `methods` memo on `PROCEDURE` is the same technique this documentation's tool chain uses. `extractmethod`'s search for `PROCEDURE name` would also match `PROCEDURE namexyz`; the sample gets away with it.
- **The splitter is dead** (see above).
- **Stale instructions in the data**: `tspasswordtextbox` does not exist.
- **Macro-substituted `SET FILTER`** in two places; **undeclared `lnMethEndPos`** in `extractmethod`; `tnFileHandle` assigned but unused in `extractallstoredprocs` (the `@` by-reference call is the intent).
- **Temp files in the current directory** and a `RELEASE WINDOW "SNIPPETS.TXT"` for a window that is never created by this code.
