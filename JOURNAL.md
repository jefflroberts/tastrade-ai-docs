# Experiment journal

Working notes for the paper and presentation on using AI with Visual FoxPro.
One entry per step. Each entry records what was done, the exact command or
action, the result, and anything surprising. Commits are referenced by subject.

## Environment

- Windows 11 Pro
- Visual FoxPro 9 SP2 installed at `C:\Program Files (x86)\Microsoft Visual FoxPro 9`
- FoxBin2PRG via Thor: `C:\fox\Thor\Thor\Tools\Components\FoxBin2PRG\foxbin2prg.exe`
- VFP documentation toolkit: `C:\fox\vfp-migration-toolkit`
- AI assistant: Claude Code (Claude Fable 5.1)

## 2026-09-08 Step 0: choose the subject and baseline it

**Why Tastrade.** It is Microsoft sample code, so nothing proprietary is
exposed. VFP developers recognize it, so readers can judge the generated
documentation against their own memory. It contains every VFP artifact type
(forms, class libraries, reports, menus, DBC, project, programs, headers)
at a size that can be documented completely.

**Version check.** The VFP 9 install's `Samples\Tastrade` folder contains only
`Bitmaps` and `Data` (117 files). The copy at `C:\fox\tastrade` is complete
(214 files): project dated 2001-02-05, `tastrade.app` built 2001-06-14, which
places it at VFP 7.

**Baseline commit.** `git init`, added a `.gitattributes` that marks every
VFP container as binary and disables line-ending normalization so the source
stays byte-exact, then committed everything as
"Pristine Tastrade sample as shipped with Visual FoxPro 7".

**Expectation going in.** FoxBin2PRG is expected to fail on some of the
older-format binaries. That failure, and how it is diagnosed and worked
around, is part of what the paper is about, so it will be recorded rather
than avoided.

## 2026-09-08 Step 1: FoxBin2PRG sweep of the pristine VFP 7 binaries

**Expectation.** FoxBin2PRG would fail on some of the older-format binaries,
most likely reports and menus, because the tool is written against VFP 9
table structures and its twin headers say "Only for VFP 9 binaries".

**Result.** Every one of the 43 binaries converted, return code 0, no error
log produced. The expectation was wrong, at least for VFP 7 era files.

| Type | Files | Twin | Notes |
|---|---|---|---|
| Forms `.scx` | 17 | `.sc2` | Method bodies present (order entry form has 33) |
| Class libs `.vcx` | 6 | `.vc2` | `tsbase.vc2` is the largest at 54 KB |
| Reports `.frx` | 13 | `.fr2` | Includes printer environment and all bands |
| Menus `.mnx` | 5 | `.mn2` | Emitted as generated menu code with setup and cleanup |
| Database `.dbc` | 1 | `.dc2` | 168 KB; includes 21 stored procedures and the RI code |
| Project `.pjx` | 1 | `.pj2` | Author metadata and full file list |

Total 43 twins, 1.2 MB of text. Sweep time about 3 seconds.

**How it was run.** Not with `foxbin2prg.exe` on the command line. That
executable is a GUI-subsystem program and returns before it finishes, so a
script cannot tell success from failure per file. An earlier sweep on another app
logged 1599 "errors" for that reason while actually converting almost
everything. Instead `tools/bin2prg_sweep.ps1` drives FoxBin2PRG in-process
through the `VisualFoxPro.Application.9` COM server, the way the tool's own
`convert_vfp9_bin_2_prg.vbs` does:

1. `SET PROCEDURE TO foxbin2prg.exe` inside the hidden VFP instance.
2. `CREATEOBJECT('c_foxbin2prg')`.
3. For each binary, `execute(file, 'BIN2PRG', ...)` with error dialogs off,
   progress bar off, recompile off, and timestamps blanked so the twins are
   deterministic.
4. Record the return code, whether the twin exists, its size, and elapsed time.
5. After the run, `git status` confirms no tracked binary changed.

**Things to note for the paper.**

- The tool arguments were undocumented in the folder. The meaning of the `4`
  the old script passed came from reading the tool's VBScript: it is a bit
  flag set (1 log, 2 dry run, 4 no error dialogs, 8 end message, 16 blank
  timestamps). Reading the tool's source, in Spanish, to recover its
  `execute()` parameter list was itself an AI-assisted step.
- A VFP 9 IDE instance was open on the machine during the sweep. The COM
  server starts a separate hidden instance, so that did not interfere.
- The `.gitattributes` from Step 0 disables line-ending normalization, so
  the twins are committed exactly as FoxBin2PRG wrote them.

**Open question for Step 3.** VFP 7 report and menu tables have fewer
fields than VFP 9 ones. The twins converted cleanly, but the VFP 9 rebuild
and second sweep will show which attributes were absent or defaulted.

## 2026-09-08 Step 3: open and rebuild in Visual FoxPro 9, then sweep again

**What was done (by hand, in the VFP 9 IDE).** Opened `tastrade.pjx`. VFP 9
asked whether to make `C:\fox\tastrade` the project's new home directory;
accepted. Chose Build, Win32 executable / COM server, with "Recompile All
Files" and "Display Errors" checked. It built `tastrade.exe` with no errors.
No conversion prompt appeared.

**What changed on disk.** `git status` afterwards:

- Every form, class library, and report binary was rewritten, plus the DBC.
  The menus were not touched.
- The `.pjx` table itself is byte-identical. Only its memo file `.pjt` changed,
  for the new home directory.
- `tastrade.app` (the 2001 VFP 7 build) disappeared and `tastrade.exe`
  appeared. The build target was the EXE; whether VFP removed the `.app` or it
  was replaced by the build is not established. The original stays in the
  first commit.

**Structure did not change, only object code.** Reading the DBF headers of
the old and new binaries: identical field counts, record counts, and record
lengths. Reports have 76 fields before and after; forms and classes 24; the
DBC 9. VFP 9 did not upgrade the table layouts. It refreshed the compiled
object code in the memo files, which is why the `.sct`, `.vct`, and `.dct`
grew by 46 to 384 bytes each while the `.scx`, `.vcx`, `.frx`, and `.dbc`
tables did not change size at all. The header date bytes of the pristine
binaries show 37 of 43 were last written in 1997 or 1998, including the
project file. One form, `category.scx`, was written in 2001, and the five
menus carry no date at all. The file-system dates all say 2001-02-05, which
is just when the VFP 7 release copied them. So the sample is VFP 6 era
code that shipped essentially unchanged with VFP 7.

**Second sweep.** 42 of 43 converted. The one failure was `tastrade.pjx`,
return code 1705 ("file access is denied"), because the project was still
open in the IDE, which holds it exclusively. Repeated after closing the
project; see below.

**Diff of the twins, VFP 7 versus VFP 9.** 41 of 42 twins are byte-identical.
FoxBin2PRG omits object code, and object code is all VFP 9 changed. The one
difference is in `reports/orders.fr2`. Two reports have code in their data
environment `Init`, this one and `listempl.fr2`, but only the orders report
has an `#INCLUDE "INCLUDE\TASTRADE.H"` line in that code. In its data
environment record, the `fontface` attribute now contains the compiler's
include-file table:
`..\include\tastrade.h`, `..\include\strings.h`, and an absolute path to
`foxpro.h` under `C:\Program Files (x86)\Microsoft Visual FoxPro 9`. VFP 7 did
not store this, and VFP 9 stores it only when the compiled code used
`#INCLUDE`, which is why the employee list report's twin did not change. Two consequences worth stating in the paper:

1. The twin now embeds a machine-specific path, so the same source compiled
   on two machines produces different text. That is noise for diffing and
   for source control, and FoxBin2PRG's configuration may be able to
   suppress it.
2. It is a reminder that VFP binaries mix source, compiled code, and
   build-environment metadata in one table, and the boundary between them
   is not where a reader would expect.

**Conclusion.** For this app, "upgrade to VFP 9" was a recompile, not a
format migration. FoxBin2PRG did not need it. The genuine reason to do it
is to have an executable that runs under the VFP 9 runtime for the
baseline capture in a later step.

**Project file, after closing the IDE.** `tastrade.pjx` converted on retry
with return code 0. Its twin differs from the VFP 7 twin by exactly one line:
the home directory changed from `c:\vfp\tastrade` to `c:\fox\tastrade`. So the
VFP 9 "conversion" of this project consisted of accepting a new home
directory and nothing else. The complete VFP 7 versus VFP 9 twin diff is
therefore two lines across 43 files, and both are environment paths rather
than source.

## 2026-09-08 Step 4a: parameterize the documentation toolkit for Tastrade

**Goal.** Run the `vfp-migration-toolkit` against Tastrade. The toolkit was
harvested from one customer job and its README admitted the debt: the
documentation skill named that app throughout, and two tools carried
hardcoded paths.

**What was found when the tools first touched Tastrade.**

- `foxparse.py` returned **zero classes for every class library**. Every
  `DEFINE CLASS` line in the Microsoft sample carries a trailing
  `&& description` comment, and the parser's regex required the line to end
  after the parent class. Neither previous app had that habit. One regex
  change; all 31 classes across 6 libraries now parse.
- `foxparse.py` has no `.mn2` parser. Menu twins are generated menu code and
  are readable as-is, so this is noted rather than fixed.
- The skill's dispatch table said the DBC twin is `.db2`. FoxBin2PRG writes
  `.dc2` for the container and `.db2` for free tables.
- The remote toolkit repo already had a newer commit from another session
  that parameterized `extract_frx.py` and `dbfscan.py`. My duplicate rewrite
  of those two files was dropped in favour of upstream during the rebase.

**What changed in the toolkit** (commit `8498186`, pushed):

- The skill and its seven reference templates are now app-agnostic. All
  app-specific facts move to a `docs/PROJECT.md` in the app's casebook,
  with a template in `references/project-md-template.md`. The skill reads
  it as step 0 and refuses to guess paths if it is missing.
- `foxparse.py`: regex fix above, plus a command line
  (`foxparse.py <twin|dir> [--summary] [--json out]`).
- `conventions.md` and README genericized; the README's "Known limitations"
  records what was paid down.

**What was added to this repo.**

- `docs/PROJECT.md`: the Tastrade config. Twelve gotchas came straight out
  of the parser output, for example that two forms bypass the framework base
  class, that the DBC's long table names differ from the 8.3 file names, and
  that `orders.frx` embeds a Microsoft print server from 2001.
- `.claude/skills/document-vfp-artifact/`: a copy of the generic skill so
  Claude Code finds it in this repo, with `SOURCE.md` naming the toolkit
  commit it came from.
- `docs/README.md`: the docs folder map.
- `docs/00-inventory/`: generated census. 38 twins parsed with no failures;
  12 tables, 4,210 rows, the largest being `orditems` at 2,821.

**For the paper.** A tool that "works" on two apps still broke on the third
in the first minute, on a formatting habit nobody had seen. The fix was
trivial; finding it required running the parser and noticing that "0
classes" was wrong rather than accepting it. Also: two people parameterizing
the same tool on the same day in different sessions is what the rebase
conflict was. Version control caught it.

**Not done yet.** The three free tables (`behindsc`, `repolist`, `ttrade`)
have no `.db2` twins; the sweep script converts only source containers.
Add `*.dbf` to the sweep for those before documenting the data model.

## 2026-09-08 Step 4b: document the DBC

**Output.** `docs/03-data-model/README.md` (container: tables, relations with
RI rules, 13 views with SQL, the six hand-written stored procedures quoted and
explained, the generated RI code described, free-table schemas) and ten
table docs under `docs/03-data-model/tables/`. About 1,200 lines.

**What the twin could not tell us.** The `.dc2` twin records what the DBC
stores: table names, comments, field defaults, rules, triggers, views, and
the stored procedure source. It does not hold field types and widths (those
are in the DBF headers) or index expressions (in the CDX). Rather than parse
those binaries, a 60-line VFP program run through the COM server dumped
`AFIELDS()`, `TAG()`/`KEY()`, and `ADBOBJECTS("RELATION")` for every table.
The table docs' schema and index sections come from that dump, so they are
read from the live tables, not transcribed.

**A hang, and its lesson.** The first run of that program hung for two
minutes. The cause was a one-character mistake (`ALINES()` given a logical
where VFP 9 wants a numeric flag). The runtime error opened a modal dialog
inside the hidden COM instance, which nobody could see or dismiss, and
low-level `FPUTS` output is buffered until `FCLOSE`, so the output file was
empty. Fix: an `ON ERROR` handler that writes the error and cancels, plus
`FFLUSH` after each table. Any VFP code driven headlessly needs both.

**Findings worth the paper.**

- The order total formula is written five times in the container (two
  stored procedures without freight, one with, two views with). One of the
  two duplicates, `CalcOrdTotal()`, is referenced by nothing at all.
- The `SALES SUMMARY` and `SALES DETAIL` views sum unit price without
  quantity, so the sales reports cannot reconcile with the order totals.
- The `ORDERS` table rule `ValOrder()` shows message boxes and inspects the
  active form's name. UI decisions inside a data-layer rule.
- `ORDER_LINE_ITEMS` has no primary or candidate key.
- Every key comes from one `SETUP` row locked with `SET REPROCESS TO
  AUTOMATIC`, so all inserts serialize on it.
- `employee.password` is eight plain characters with a default of
  `"Tastrade"`.
- `user_level.startup_action` is VFP code stored in data, looked up by the
  level's description text rather than its ID.
- The `.dc2` and the dump disagree on nothing. The parser's `sc2` output was
  used to build the "Used by" lists, then three of my usage claims were
  checked against the twins by grep and two were wrong (who runs the
  startup action, and whether `CalcOrdTotal` is called). Corrected before
  commit. Generated prose needs the same verification as hand-written prose.

**Method note.** The docs were produced by a generator script that merges
the verified dump with hand-written purpose, usage, and notes per table.
The schema tables are therefore exact; the prose is where errors can hide,
and that is where the verification pass went.

## 2026-09-09 Step 4c: document the tsbase and tsgen class libraries

**Output.** `docs/05-classes/tsbase.md` (17 classes, about 1,700 lines),
`docs/05-classes/tsgen.md` (8 classes, about 1,100 lines), and a
`docs/05-classes/README.md` index with the cross-library inheritance map and
a six-step run-time walkthrough. Every method body is quoted verbatim from
the twin through the parser, so 107 code fences carry no transcription;
the prose is hand-written per class and per method.

**Second parser bug, same shape as the first.** The method regex required
`PROCEDURE name` alone on its line. Tastrade declares 44 of the 116 methods
in these two libraries as `PROTECTED PROCEDURE` or with a trailing
`&& description`, and the parser dropped all of them without an error. The
census had also under-counted the order entry form by 7 methods. A tool that
had passed on two apps was wrong on the third in a way that produced
plausible numbers. Fixed in the toolkit (commit `9355a36`), census
regenerated. Lesson repeated from Step 4a: check parser output against a
raw `grep` count before trusting it.

**Findings worth the paper.**

- The startup action stored in `USER_LEVEL` is executed by `tastrade.Do`
  only when `DEBUGMODE` is off, and `DEBUGMODE` is `.T.` in the shipped
  header. So the sample's most-cited "code in data" feature never runs as
  built. Found only by reading the concrete subclass after documenting the
  abstract one; the DBC doc has been corrected to say so.
- Two probable defects in code that has shipped with VFP for years:
  `tstoolbar.savewindowpos` uses `thisform` inside a toolbar, and
  `tsifcombo.KeyPress` has `INLIST( 2, 26)` with its first argument missing,
  so the guard is always false.
- The splitter's handle shape still records
  `c:\fox30\nwind\beta1\mainsamp\libs\nwbasobj.vcx` as its class library: a
  FoxPro 3.0 beta path, and the Northwind name. Tastrade is a descendant of
  the Northwind sample, which is also why the customer IDs are `ALFKI` and
  friends.
- The framework's contract is small and clean: a form exposes
  `First/Prior/Next/Last/AddNew/Save/Restore/QueryUnload` returning four
  `FILE_*` codes, and one shared toolbar drives whichever form is active.
  Everything else is glue around `oApp`, `gTTrade`, and `_screen.ActiveForm`.
- Error handling is layered: DBC rule and trigger failures bubble up as VFP
  errors 1582, 1583, 1539 into `tsbaseform.Error`, and `customerinfo.Error`
  maps rule text back to the right text box by matching the first words of
  the message.

**Verification pass.** Three claims were checked by grep after drafting and
all three needed correction: where the About box gets its class library
(the menu loads it on demand), which method shows the intro form and logs
in (`tastrade.Init`, not `Do`), and which header defines `MOUSE_HOURGLASS`
(VFP's own `FOXPRO.H`). Same pattern as Step 4b: the prose is where the
errors are, and grep is cheap.

## 2026-09-09 Step 4d: document the main, login, about, and orders libraries

**Output.** `docs/05-classes/main.md`, `login.md`, `about.md`, `orders.md`
(about 1,150 lines together, every method body quoted verbatim) and the
index updated. All 31 classes in six libraries are now documented.

**The finding of the day.** `tastrade.Init` skips the login dialog entirely
when `DEBUGMODE` is `.T.`, sets the employee ID to empty and the user level
to "APPLICATIONS DEVELOPER", and `tastrade.Do` skips the startup action
under the same flag. `DEBUGMODE` is `.T.` in the shipped header. So the
sample as built has no login, no logged-in employee (every new order gets
the first employee on file via `DefaultEmployee()`), and no per-level
startup. Yesterday's note about the startup action was the half of it.

**Others.**

- The login dialog the app uses, `loginpicture`, displays the selected
  employee's password in a text box labelled "Hint", and the bad-password
  message says "(See Hint textbox)". Sample-grade security, documented as
  such.
- `orderentry` is half a form: it references a grid and a customer combo
  that only the subclass form defines, and every data binding is set in the
  form. Its description says the order history form derives from it, but
  the shipped `frmordhistory` derives from `tsbaseform` instead, so the
  `"HISTORY" $ thisform.Name` branches, the `ordtextbox.Init` disabling
  logic, and the window-position overrides are dead code.
- `orderentry.save` is the application's only explicit transaction, and it
  forces the `ORDERS` table rule to fire with `SETFLDSTATE(2, 2)`, which
  hard-codes the field position of `customer_id`.
- The on-screen total in `orderentry` is the sixth copy of the order total
  formula.
- `aboutbox.Init` branches on `OS()` returning "WINDOWS NT" or "WINDOWS 4";
  modern Windows matches neither, so the About box on this machine falls to
  the `WIN.INI` path and shows blank owner lines.
- The class icon paths record `h:\allisonk\sampapp\` in `login.vcx`, a third
  trace of the original authors' machines after `c:\fox30\nwind\beta1` and
  `..\..\..\..\backup\mainsamp`.

**Verification.** Before writing: the inheritance of the order history form,
where the order entry bindings live, which constant holds the developer
user level (it is in `tastrade.h`, not `strings.h`), the About box's call
site, and who calls which login. After writing: the subtotal really does
come from the grid's `ncolumnsum`, and the customer combo really does seek
the customer alias before `refreshcustomerinfo` runs. One claim about how
`FILE()` treats an extension-less name was softened rather than asserted.

## 2026-09-09 Step 4e: document the order entry and order history forms

**Output.** `docs/04-forms/ordentry.md` and `ordhist.md` (about 1,050 lines
together) and a `docs/04-forms/README.md` index of all seventeen forms with
their base classes. The control tables are generated depth-first from the
parser's control records (path, class, base class, bindings), so container
paths and `ControlSource`s are not transcribed; the role column, the
explanations, and the notes are hand-written. Every method body is quoted.

**What the two forms are.** Order entry is the `orderentry` class plus a
customer search combo, a line-item grid, a credit display, and the links to
add-customer, find-order, and order history. Order history is a two-grid
browser over two parameterised DBC views that, when opened from order
entry, becomes an item picker: it inserts the checked lines into the other
form's buffered cursor by switching data sessions, and the two forms lock
each other while linked.

**Findings worth the paper.**

- The cross-session insert (`SET DATASESSION TO` the other form's session,
  `INSERT INTO order_line_items`, switch back) is the most fragile technique
  in the app. The mutual locking (`Closable`, `lAllowEdits`, `lAllowNew`,
  `ClearLink`) exists to make it safe.
- The Tag checkbox in the history grid is bound to a literal `.F.` column
  in a view (`SELECT .F., ...`), edited in the buffer and reverted. It works
  only because the view never sends updates.
- `frmordhistory.datachanged` reverts the view and returns `.F.`, so the
  base form never prompts; the discard prompt is then re-implemented three
  times.
- Available credit is recomputed by `RemainingCredit()` on every grid
  refresh, which runs a grouped `SELECT` over the customer's unpaid orders
  each time.
- `chkPaid.Refresh` forces `lAllowEdits = .T.` on every refresh, fighting
  the class's delivery-date rule. Which wins depends on refresh order.
- Toggling Paid in the history grid saves immediately, outside any
  transaction, on a path the DBC rule deliberately exempts from the credit
  checks.
- Two undocumented magic values, `CHR(12)` and `CHR(200)`, guard the
  add-customer prompt.
- The stand-alone history form finds its customer by inspecting whichever
  of the order entry or customer form is on top, reaching into the customer
  form's data session to read the ID.

**Verification.** The custadd return contract (`lRetVal` returned from
`Unload`), the menu skip conditions (order entry single-instance, order
history not), that the customer form does not itself open order history,
and the string constants behind every prompt were all checked by grep
before writing. Parser control counts (18 and 32) match the twins.

## 2026-09-09 Step 4f: document the six maintenance forms

**Output.** `docs/04-forms/customer.md`, `employee.md`, `product.md`,
`supplier.md`, `category.md`, `shipper.md` (about 980 lines together) and
the index updated: 8 of 17 forms documented.

**Method.** The six forms share the `tsmaintform` pattern, so each doc
states the pattern once in a paragraph that points to the class doc, then
records only what the form adds: DataEnvironment cursors and relations,
the Data Entry page's bindings (from the parser's control records), the
List page's grid columns (extracted from the twin's property block, with
`ColumnOrder` applied and header captions matched to columns), and every
method body quoted. A first pass rendered every header caption blank
because the extraction assumed `Caption` was the first property after the
header's `WITH`; fixed by matching inside the whole object block. Checked
by counting empty header cells across all six files: zero.

**Findings.**

- The employee List page shows `Employee.password` in clear text as
  column 13. With the login dialog's "Hint" box that makes two places in
  the UI where every password is visible.
- The category form stores each picture twice, as a file path and as an
  OLE General field via `APPEND GENERAL`, and only ever reads the path.
  The employee form stores only the path. Both store the absolute path
  `GETFILE()` returned.
- The product form's stock fields are plain text boxes; nothing in the
  application adjusts them when orders are saved. Inventory is decorative.
- The product List grid has a checkbox placed in the Discontinued column
  but `CurrentControl` still set to the text box: a half-finished change.
- The customer form orders by ID while its five siblings order by name;
  the shipper form is the only one in the default data session.
- The employee form's guard against deleting the logged-in employee reads
  `oApp.GetEmployeeID()`, which is always empty under `DEBUGMODE`, so it
  never fires. Third feature found dead behind that flag.
- The customer form has almost no code of its own; its Data Entry page is
  the shared `customerinfo` container from `tsgen.vcx`, while the
  structurally identical supplier form lays its text boxes out directly.
  Two ways of doing the same thing in one sample.

**Verification.** Menu launch points and their single-instance `SKIP FOR`
conditions, the six trigger-failure strings, and the parser's control and
cursor counts were checked before writing. The `ColumnN` to `grcName`
mapping was verified by hand against the customer grid, whose columns were
added out of display order.

## 2026-09-09 Step 4g: document the remaining nine forms

**Output.** `docs/04-forms/getinv.md`, `gettitle.md`, `custadd.md`,
`chngpswd.md`, `reports.md`, `rebuild.md`, `behindsc.md`, `casestdy.md`,
`viewcode.md` (about 1,860 lines). All 17 forms are documented; the index
is complete. With the DBC and all six class libraries done earlier, the
remaining undocumented artifacts are the 13 reports, 5 menus, 2 programs,
2 include files, and the project.

**Findings.**

- **The case study form is unreachable.** `casestdy.scx` is in the
  project and compiles into the EXE, but no menu, form, class, or program
  runs it. Found by grepping every twin for its name; the only hits are
  the project manifest and the form itself.
- **Behind the Scenes is a source extractor inside the app.** Its
  `showcode` method opens `.scx` and `.vcx` files as tables, finds the
  object by `objname`, and splits the `methods` memo on `PROCEDURE`. It is
  FoxBin2PRG's technique, written in 1995 into the application it
  documents. The instruction data has drifted: one topic points at a class
  `tspasswordtextbox` that does not exist.
- **The splitter is dead.** The three objects it is meant to move override
  `Move` with empty bodies, so dragging the bar repositions nothing; the
  splitter swallows whatever error results.
- **Change Password edits the wrong employee in this build.** It seeks
  `oApp.GetEmployeeID()`, which is empty under `DEBUGMODE`, so it sits on
  the first record. Fourth feature found dead or wrong behind that flag.
  It also displays the current password as a "Hint".
- **The invoice parameter dialog's OK button is also its Cancel button**
  (`Default` and `Cancel` both `.T.` on `cmdOK`), so Escape confirms.
- **Two return conventions.** The two plain-`form` dialogs use
  `DO FORM ... TO` and `NAME ... LINKED`; the framework dialogs use
  `uRetVal`.
- **Reindex in a shared app**: the rebuild form does `CLOSE TABLES` and
  `USE ... EXCLUSIVE` per table in the default session.
- **FoxPro 2.x leftovers**: `ReleaseErase`, `TerminateRead`, `ReadSize`
  on the report picker's controls, inert properties from a screen
  conversion.

**Method notes.** Launch points for four forms were missed by the first
grep because the menu runs them with `DO FORM` rather than
`oApp.DoForm`; a case-insensitive second pass found them. One claim about
VFP's behaviour when `Move` is called with no arguments was softened to
"errors or does nothing" rather than asserted, since the documented
conclusion (nothing is repositioned) holds either way.

## 2026-09-09 Step 4h: document the thirteen reports

**Output.** `docs/06-reports/` (13 report docs and an index, about 1,240
lines) from `tools/docgen/gen_report_docs.py`. Every band, every object
with band-relative coordinates, every expression, cursor, data environment
method, report variable, and the saved printer environment, from the twins
alone. The cross-links other docs made to `../06-reports/*.md` now resolve.

**Method.** The `.fr2` twin is a flat list of FRX records with a 90-attribute
header each; filtered to non-default attributes, all thirteen fit in a few
screens. Cross-checking `foxparse.py` against a raw grep matched on record,
field, label, and band counts and still hid two problems, both of the
"plausible answer" kind:

- The parser's band table was off by one. FRX band `objcode` 0 is Title and
  1 is Page Header, so the parser called every three-band listing
  Title/Detail/Summary. Found because a listing with a "Summary" band 0.5
  inches tall and nothing in it made no sense; VFP always writes Page
  Header, Detail, and Page Footer, and those are 1/4/7.
- The parser's docstring said reports never declare cursors, and skipped
  the records that do. Twelve of the thirteen declare one; `topcust`
  declares four.

Two more things the twins do not say outright. Objects are not tagged with
a band; their `vpos` is a designer coordinate that includes one band bar
after each band (2083.333 units, 20 pixels, from VFP's own
`ffc/_frxcursor.h`), and one file (`viewcode.frx`) was saved with a 19-pixel
bar, so assignment goes by "below the previous band's content" rather than
exact ranges. And the `picture` attribute on a field is its format mask,
which the parser had been counting as an image. All fixed in toolkit commit
`c578f09`, with the format reference rewritten; the skill copy here is
refreshed.

`tools/extract_frx.py` needed `reportlab` installed; its coordinate
reconstruction agreed with the twins and was not otherwise needed.

**Findings.**

- **Every report carries a saved printer environment**, four devices in all:
  `\MSPRINT32\2/1MC PRIVJ 157.56.32.242` in seven, `LaserNT` in three, an
  HP LaserJet 4Si on `\msprint32\privj`, and the `\RED-PRN-16\CORP0007`
  already known. The printer record is stored twice (text and binary
  DEVNAMES) and in `casestdy.frx` the two halves name different printers.
- **The invoice is the seventh copy of the order total formula**: two
  report variables and a total field compute subtotal, discount percent,
  and freight again, in agreement with `ORDERTOTAL` and the order entry
  screen.
- **The employee listing has a latent runtime error.** Its data environment
  `Init` uses `NOTHINGTOPRINT_LOC`, `TASTRADE_LOC`, and
  `MB_ICONEXCLAMATION` with no `#INCLUDE`; the invoice's `Init` has one.
  The compiled code in `listempl.frt` carries the names, not the strings
  (`orders.frt` carries "Nothing to print."), so choosing a title with no
  employees errors instead of showing the message.
- **The three sales reports do not reconcile.** Sales Summary and Sales
  Detail label `SUM(unit_price)` as "Sales"; Top 25 Customers uses the full
  order total through `ORDERTOTAL`.
- **Three dead cursors** in `topcust` (`customer`, `orders`,
  `order_line_items`, opened and never referenced) and **one dead report**,
  `casestdy`, printable only from the form nothing launches.
- **Two reports depend on VFP's automatic column names** (`exp_1`,
  `sum_unit_price`, `company_name_a`, `company_name_b`); a rebuilt view must
  reproduce them.
- View parameters are passed by leaving private variables in scope:
  `DO FORM ... TO cTitle` and un-`LOCAL` date assignments feed `?cTitle`,
  `?dDateFrom`, `?dDateTo` when `OpenTables()` runs.
- The Behind the Scenes print relies on `AutoOpenTables = .F.` to reuse the
  form's open alias for `NEXT 1`; the Case Study print opens the table
  itself with a stored filter.
- Smaller: cost printed beside price on the product listing; the invoice's
  Bill To line lacks a space before the postal code; `unit_cost` and
  `unit_price` share a `99999.99` mask; fifteen blank records in
  `salesdet.frx`; the wordmark is four labels with blue 24-point T's.

**Verification.** Object rows per band in every doc equal the parser's
count; no empty content cells; every `[[link]]` resolves; fence counts
even. Launch points come from a case-insensitive grep for `REPORT FORM`
(three forms, plus the picker over `repolist.dbf`'s ten rows) and from the
project manifest. Printing is gated by no user-level check anywhere
(grepped). A generator bug from Step 4g was found on the way: the forms
index sentence had been appended on each rerun and stood three times;
`gen_rest_docs.py` is now idempotent and the index regenerated.

## 2026-09-09 Step 4i: document the five menus

**Output.** `docs/07-menus/` (five menu docs and an index, about 510 lines)
from `tools/docgen/gen_menu_docs.py`. Every pad, bar, shortcut, `SKIP FOR`
condition, action, procedure, and the setup and cleanup code, with the
code that runs and removes each menu traced through the class libraries
and forms. The eighteen forward links to `../07-menus/main.md` from the
form and class docs now resolve.

**Method.** `foxparse.py` had no `.mn2` parser, so this step added one
(toolkit commit `9a716a0`) rather than read the twins by hand and
hope: `parse_mn2` returns pads, bars, popups, procedures, and the setup
and cleanup blocks, and its counts match a raw grep of every twin. The
twins were then diffed against the three GENMENU `.mpr` programs shipped
in 2001 (dated 10/12/00): they match statement for statement apart from
formatting, procedure names, the `SET SYSMENU` pair a `REPLACE` menu
generates, and one artifact, an empty cascading popup that FoxBin2PRG
emits for every separator bar and the `.mpr` does not have. Six of them
across the five menus; the docs say so instead of documenting phantom
submenus. For the two menus with no `.mpr` (`navigate`, `window`), the
built EXE was grepped for their status text to confirm the build
generated them.

Every launch and release point was grepped: `DO main.mpr` through
`cMainMenu`, `DO menus\intro.mpr` in `tastrade.Init`, `DO navigate.mpr` in
`ShowNavToolBar`, `DO menus\window.mpr` in `AddToMenu`, `DO
menus\ordentry.mpr` in the order entry form's `Activate`, and the
`RELEASE PAD` / `RELEASE POPUP` lines that undo them. The order in which
`tsbaseform.Init` calls `AddToMenu` and `ShowNavToolBar` fixes the pad
order the placement trick produces; the docs give that order and say it
was not run.

**Findings.**

- **Privilege gating is four lines of cleanup code in the main menu, and
  half of it misses.** Non-developers lose the Utilities pad. The three
  lines meant to remove Login and Change Password for lower levels do
  `RELEASE BAR n OF ADMINBAR_LOC`, and `ADMINBAR_LOC` is "Administration",
  but the Administration popup was never named in the designer: it is
  `_qx713dsus` in the twin and in the 2001 `.mpr`. They error or do
  nothing; the bars stay. Under `DEBUGMODE` none of it runs, so the shipped
  build shows every user the Utilities pad with the Command window
  (Ctrl+F2), Debug, Trace, Suspend, and Cancel. Fifth feature found dead
  or wrong behind that flag.
- **Three pads reuse VFP system pad names as a placement trick**, and the
  designer comments in the twins say so: Administration is `_msm_file` so
  Navigation and Window (`AFTER _MFILE`) land after it; Navigation is
  `_msm_edit` so Items (`AFTER _MEDIT`) lands after it; Help is
  `_msm_systm` so its system bars open the help file.
- **Two About boxes.** The intro menu hard-codes version 1.0, a 1994
  copyright, and `BITMAPS\SMSWIRLT.BMP`, which is not in the repo; the
  main menu uses the include-file constants (1.1, 1996) and
  `TTRADESM.BMP`, which is.
- **The menus are keyboard fronts for the toolbar.** File and Navigation
  bars call toolbar button `Click` methods and mirror `Enabled` in their
  `SKIP FOR`; only Delete, Print Setup, Login, About, and the form launches
  have code of their own.
- **Dead code in the intro menu**: a popup-level dispatcher calling
  `_screen.activeform.<prompt>` with a `New`-to-`AddNew` workaround whose
  comment records a VFP bug from the sample's first release; unreachable
  because the only bar has its own handler.
- **The copyright notice is each menu's `ON SELECTION MENU` command**, a
  comment, so a no-op, in all five.
- Menu prompts and status text are plain English, not `_LOC` constants; the
  forms are localized through `strings.h`, the menus are not. Order History
  is the only multi-instance form on the menu; the six maintenance forms,
  order entry, and Behind the Scenes are single-instance by `WEXIST`.

**Verification.** Bar rows per pad in every doc equal the parser's bar
count; every `[[link]]` resolves except the forward links to
`../08-programs/`, which is next; fence counts even.

## 2026-09-09 Step 4j: document the programs and include files

**Output.** `docs/08-programs/` (`main.md`, `utility.md`, `tastrade.h.md`,
`strings.h.md`, and an index, about 590 lines) from
`tools/docgen/gen_program_docs.py`. With these, every forward link in the
docs resolves: a link check over all of `docs/` finds none missing.

**Method.** The programs and include files are native text, so there is
no twin and no parser to cross-check; the generator parses routines,
`DECLARE` blocks, and `#DEFINE` lines itself and its counts were compared
with a raw grep (1 and 6 routines, 6 declarations, 34 and 86 constants).
The new element is the constant census: for each of the 120 `#DEFINE`s a
case-sensitive whole-word grep over every twin, `.mpr`, `.prg`, and the
DBC twin lists the files that use it. A first, case-insensitive pass
counted `TAB` as used by `orders.vc2` because of the word "tab" in a
comment; the case-sensitive pass is what the docs carry. Every caller of
the six utility functions and every consumer of the six API declarations
and six globals was grepped the same way. The skill gained a dispatch
entry for `.h` files and a template section for them (toolkit `e46e61a`).

**Findings.**

- **`DEBUGMODE = .T.` is compiled in at five sites**: the startup action
  and the login in `tastrade`, two branches of `tsbaseform.Error`
  (a `WAIT WINDOW` on table-rule failure, `SUSPEND` on Abort), and
  `SET ESCAPE ON` in `environment.Set`. The dead delete guard, the
  wrong-record Change Password, and the missing menu gating all follow
  from the login site. There is no `#IF`; flipping it is a full rebuild.
- **Thirteen constants are defined and never used** (`CURRENCY`,
  `KEY_WIN4_MSINFO`, `DOLLAR_FORMAT1_LOC`, three `SYS2011_*` lock strings;
  `BADNAME_LOC`, `BADUPDATE_LOC`, `ASKDELETE_LOC`, `NORECSMATCHED_LOC`,
  `AVAILABLECREDIT_LOC`, `CUSTFIRSTORDER_LOC`, `CUSTNOORD_LOC`), and one
  function, `NotYet()` ("Under Construction"), is called by nothing.
- **Localizable strings are split across two files.** Eleven `_LOC`
  constants live in `tastrade.h`, not in `strings.h`, whose header says it
  is the file to localize; menu text is in neither.
- **`USER_APPDEV_LOC` and `USER_OPSMGR_LOC` must match `user_level`
  rows upper-cased.** Translate one without the other and the menu gating
  silently disappears.
- **The environment hides VFP's toolbars by their English window titles**
  (`TB_*` constants), a dependency on the IDE's language.
- **`main.prg` declares six Win32 API functions and calls none.** INI
  read/write serve the intro flag and window positions; three registry
  calls and a `win.ini` lookup serve the About box.
- **`main.prg` hides the Project Manager window; the reports assume it is
  closed.** Whether a deactivated window still satisfies `WEXIST` was not
  run.
- **`SetPath()` has no `RETURN`**, so `IF SetPath()` passes on VFP's
  default `.T.`. `gTTrade` and `oApp` outlive the comment that says all
  publics are released.
- Smaller: "maximimun" shipped in a message; two constants with identical
  text; `lnTagNum` leaks as a private in `IsTag`; `PARAMETER` instead of
  `LPARAMETERS` in `ToolBarEnabled`; `HKEY_LOCAL_MACHINE` written as a
  signed 32-bit integer; three spellings of the path to `tastrade.h`.

**Verification.** Fence counts even; every `[[link]]` resolves; the
computed unused lists match the names the prose cites; caller lists were
checked with the method name (`IsTag` is called from `tsifcombo.Init`, not
the base form, which the class doc had right and a first draft here had
wrong).

## 2026-09-09 Step 4k: document the project file and write the architecture pages

**Output.** `docs/01-architecture/` (`projects.md`, `startup.md`,
`framework.md`, and an index, about 420 lines) from
`tools/docgen/gen_project_docs.py`. The manifest page is generated from
the `.pj2` twin plus a census of the working tree; the start-up and
framework pages are synthesis, written from the finished per-artifact
docs with their counts computed. Every artifact type in the sample now
has its doc, and a link check over `docs/` finds nothing unresolved. The
inventory census in `docs/00-inventory/` was regenerated with the parser
as it now stands (43 lines, menus and project included).

**Method.** The parser cross-check found the fourth parser problem, of
the familiar kind: `parse_pj2` reported 78 members, the right number, and
called 31 of them "unknown" while labelling the two free tables as
databases. VFP's project type codes are case-sensitive (lowercase `d` is
the container, uppercase `D` a table, `x` an image or other file); the
parser had `D` as "database" and knew neither of the others. Fixed in
toolkit `fc295b9`, which also reads descriptions, exclusions, the
main file, dev info, and properties; 63 descriptions, 5 exclusions, and 2
text overrides match a raw grep.

The census went beyond the twin. For each of the 83 files in `bitmaps/`
the script asked three questions: is it a project member, does any twin,
program, or include file name it, and does a row of `category.dbf` or
`employee.dbf` name it. Reference lines that are only `ClassIcon`
metadata were separated from run-time references; without that split the
Class Browser icons would have looked like run-time dependencies. The
same pass listed everything on disk that the project does not know about.

**Findings.**

- **The EXE has no version resource.** Product name, description,
  copyright, and version are empty in the project; the versions the
  application shows (1.1 and 1.0) come from an include file and a menu.
- **Of 83 bitmaps, 30 are in the project and 19 are used at run time.**
  Eight `.msk` masks ride along with their buttons; `bhind.ico` and the
  two "splitter marker" bitmaps the project describes are referenced by
  nothing. 23 more are category pictures and employee photos named only
  by data rows, as relative `bitmaps\` paths, outside the project; 15 are
  Class Browser icons (two through the original authors' paths); 15 are
  referenced by nothing at all, including `splash.bmp`.
- **The project's home directory is the one line the VFP 9 rebuild
  changed** in this twin: `c:\vfp\tastrade` became `c:\fox\tastrade`, the
  fourth location the sample is known to have been built from.
- **What is outside the project**: the ten contained tables (only the
  container and the two free tables are members), the help file and its
  source table, the INI file, and the template's `notes.txt`.
- **Debug information is on and encryption off**, so the EXE carries
  line numbers; the base form's error handler shows them.
- The four undescribed members (two menus, two reports) are the four
  with `Cpid = 1252`, the late additions found in earlier steps.

**Verification.** Member, description, exclusion, and type counts against
grep; every `[[link]]` across `docs/` resolves; fence counts even. The
framework page's counts (21 saved settings, 17 forms by base class, 13
views, 8 relations, 21 stored procedures) were taken from the docs that
counted them, not retyped from memory; one draft said "five modal
dialogs" for `tsformretval` and the inheritance diagram says four.

## 2026-09-09 Step 5: method synthesis, and a correction of aim

**Correction.** The paper is about using AI to document Visual FoxPro
applications, not about Tastrade. The journal's "Method" and
"Verification" paragraphs had been recording the right evidence all
along, but the summaries, the commit messages, and the handoff's
"Findings so far, for the paper" section had been treating the sample's
defects as the result. They are the demonstration.

**Output.** `METHOD.md` at the root: the pipeline in five stages, what it
produced in numbers, the three failure modes with the table of parser
errors and how each was caught, what the person supplied, the techniques
that carried the work, the friction, what transfers to a customer
application, and the open questions (cost, reader validation, rebuild
fidelity, running the application). `HANDOFF.md`'s findings section is
split into "Method findings, for the paper" and "Sample findings (the
demonstration, not the subject)". The root README points at both.

**Numbers gathered for it.** 11,926 lines of docs in 8 folders; 10
generators, 4,169 lines; 23 casebook commits over two days, 10 of them
documentation steps; 6 toolkit commits during the experiment; parser or
skill wrong five times on this third application, two of them past a
count check; every step with at least one prose claim overturned by grep
before commit; four VFP behaviour assertions softened and one retracted
by its own commit.

**Verification.** Each number was recomputed from `git log`, `wc`, and the
journal rather than recalled; the commit count of documentation steps was
corrected once (12 written, 10 counted).

## 2026-09-09 Step 6: domain and business-logic synthesis

**Output.** `docs/02-domain/README.md` (the business in plain language,
with the sample's own help and Behind the Scenes text quoted and the
places where the code parts from it) and `docs/09-business-logic/README.md`
(fourteen numbered rules, R1 to R14, each quoted from source and
explained, with the seven copies of the order total side by side), from
`tools/docgen/gen_synthesis_docs.py`. Every folder in the docs map now
exists.

**Method.** Synthesis pages are where a documentation effort is most
tempted to write from memory, so the generator was built to refuse it:
every quoted rule is pulled through the parser at generation time (stored
procedures by name from the DBC twin's procedure block, field defaults
and rules from its table records, view SQL by name, method bodies from
the class and form twins, the invoice variables from the report twin, the
menu cleanup code from the menu twin), and the domain page's numbers come
from profiling the DBF data (order dates, paid counts, discount
distribution, shipper split, counters, passwords). Two independent
accounts were read first: the help table's introduction and the Behind
the Scenes topics, which are the authors' own description of the rules.
Where their text and the code disagree, both are given.

Method observations from this step:

- **The authors' description was wrong three times about their own
  rules.** Behind the Scenes says credit sums all the customer's orders
  (the code sums unpaid ones), that a failed order condition stops
  validation (the code asks Yes/No and lets the user override), and the
  help says user levels control table access (only menu pads). Reading
  the code beats reading the comments, even the authors'.
- **The parser did not carry everything.** The DBC twin lists relations
  but not their RI rule codes, which came from the live dump in Step 4b;
  the generator says so beside the table rather than leaving the reader
  to guess the source.
- **A rule that looks like data is data.** The order-ID counter stood
  59 above the number of orders on file; a draft said "issued and not
  kept" with a computed count until the ID range (1 to 1126, 47 gaps)
  showed the counter could not have started at 1. The sentence now
  states the two numbers and the mechanism, not a subtraction.
- **Two claims corrected by grep before commit**: the order history
  "Balance" is the sum of unpaid totals, not remaining credit; the login
  check lives in the base `login` class and the subclass the app shows
  only wraps it.
- Checks: every fence closed, every `[[link]]` in `docs/` resolves,
  fourteen `## R` sections, every stored procedure and method the page
  quotes was found by name at generation time (an assertion, not a
  hope).

**Sample findings.** The sample's one transaction is an order; credit is
recomputed, never stored; prices and discounts are copied at the moment
of choice; an order freezes when its deliver-by date passes; paying
bypasses every check; discontinued products stay orderable; inventory,
sales regions, and notes are stored and read by nothing; 95% of the
sample orders are paid; every sample employee has changed the default
password, and the login screen shows it anyway.

## 2026-09-09 Step 7: the three free tables

**Output.** `.db2` twins for `data/behindsc.dbf`, `data/repolist.dbf`, and
`help/ttrade.dbf` (`tools/bin2prg_free_tables.ps1`, 3 of 3, log beside
it), and `docs/03-data-model/tables/behindsc.md`, `repolist.md`,
`ttrade.md` from `tools/docgen/gen_free_table_docs.py`. The DBC README
links to them; the inventory census now has 46 lines. Every source
artifact in the sample, containers and tables alike, has a twin and a
doc.

**Method.** The sweep script converts source containers only, so a
sibling script names the three tables and drives FoxBin2PRG the same way
(in-process through the COM server, headless flags, its own hidden VFP
instance; the user's IDE instance, running since 09-03, was left alone).
The twin is structure only: fields, code page, file type, and the
structural CDX tags. The generator asserts at run time that the twin's
fields and tags equal the live `AFIELDS()`/`TAG()` dump from Step 4b,
so the two independent sources are compared on every rerun, not once.

Fifth parser gap, of the quiet kind: `parse_db2` returned fields and
nothing else, so the twin's three index tags were invisible to it and
its summary looked complete. Fixed in toolkit `61e579f`; the parser now
returns tags, file type, and the table-level entries.

The behindsc doc measures the drift of the sample's self-documentation
instead of asserting it. Each `code_to_sh` instruction (`file, object,
method`, 74 lines in 53 rows) is resolved against the twins the way the
form resolves it at run time: file by name, object by class name or
object path, method by `PROCEDURE`. 68 resolve; 6 do not, and each of
the six was confirmed by an independent grep: a class that does not
exist (`tspasswordtextbox`), a button that does not exist
(`cmdavailablecredit`, twice), a library named `order.vcx` for
`orders.vcx`, a button `cmdconfirm` for `cmdAddToCurrentOrder`, and a
form class `frmcustomer` for `frmcustomers`. Three resolved
instructions were spot-checked by grep as well, since a resolver that
never says no is as useless as one that always does.

Two smaller method notes. Rerunning the Step 4b DBC generator to change
one paragraph also rewrote `user_level.md` with different line endings
and no other change; the file was restored and the generator left alone,
but a rebuild of the docs on another machine would show the same noise.
And `ttrade.dbf` turned out not to be the source of the CHM, as the DBC
README had said: its three columns and widths are VFP's own DBF-format
help file, usable with `SET HELP TO`, kept beside the HTML Help file the
application actually opens. The README wording is corrected.

**Sample findings.** Behind the Scenes drifts at 6 of 74 instructions;
two of its topics have code but no text; the help table's "Overview"
topic is empty; the help introduction promises per-level table access
the code does not have and tells the user the password is shown "in
this sample application"; `repolist` lists ten of thirteen reports and
validates nothing.

## 2026-09-09 Step 8: baseline capture from the running EXE

**Output.** `baseline/`: 30 form images (17 `.scx` forms less the one
that does not open, the intro, login, find-customer, find-order and About
dialogs, the toolbar, and the page and state variants), 10 main-window
images, the first three pages of every report that printed (11 of 13; 24
page images at 1632 by 2112), 5 message boxes, and three records of the
run: `CAPTURE-LOG.csv` (one row per capture with the launch statement,
form name, class, caption, file, page count, and status), `dialogs.csv`
(every message box with its text and the button pressed), and
`capture.log`. `baseline-eb70/` is the same capture with the harness
forcing `SET ENGINEBEHAVIOR 70` (31 forms, 25 pages, no message box).
`docs/10-baseline/README.md` indexes both, generated by
`tools/docgen/gen_baseline_docs.py` from those records and the PNG
headers. The harness is `tools/baseline/`: `run_capture.ps1` (starts
VFP, watches for message boxes, answers the two report dialogs from
outside, watchdog), `capture.prg` (runs inside VFP), `snap.ps1`,
`emf2png.ps1`. Toolkit `cb074de` carries the reusable parts.

**Method.** The EXE is run inside a visible VFP 9 session (`DO
tastrade.exe` from a `.prg` named by the config file's `COMMAND`), so the
code that runs is the compiled EXE's, and two timers on `_SCREEN` drive
it during its `READ EVENTS`: one opens each form the way the menu does
(`oApp.DoForm(...)`), snapshots the form and the main window, and
releases it; the other fires inside every modal `Show()`, snapshots the
modal form, and presses the button that closes it. Reports are run cold
as the picker runs them, into a `ReportListener` that renders every page;
pages are written as EMF and rasterised. Message boxes are handled from
outside VFP by the runner. Nothing in the application was edited, and
the two `.dbf` headers the application stamps on opening (`customer`,
`orders`: three bytes, the last-update date) were restored before
commit.

Six runs before a clean pair, each stall a fact about the environment
that reading could not supply: the runner's `FindWindowEx(NULL, ...,
"#32770")` found no message box on this Windows build (`EnumWindows`
does); VFP's timers do not fire inside a modal form a report's data
environment opens while `REPORT FORM` runs, so the two report dialogs
are answered with Enter from outside; the application's closing `CLEAR
ALL` released the helper object held in a `_SCREEN` property, so nothing
after the EXE returns may use it; a snapshot error on stderr became a
terminating error in PowerShell 5.1 and the cleanup killed VFP
mid-report; `ReportListener.OutputPage` to PNG returned a half-size,
clipped bitmap on this 200% desktop, EMF the whole page; and
`_SCREEN.HWnd` is the MDI client, so the main window's frame, menu, and
toolbar need `GetAncestor(GA_ROOT)`. Each is a line in the toolkit's
methodology (section 12) and a helper in `tools/baseline-capture/`
(`Snap-Window.ps1 -Root`, `Render-EmfPage.ps1`, `Watch-Dialogs.ps1`).
Two harness bugs of the ordinary kind as well: a numeric `SET()` value
concatenated as text, and a protected property probed from outside.

The one-in-five rule held for the findings page too: the draft said the
case study form "shows an empty text box"; the image shows a Behind the
Scenes topic. A second draft claim, that the report Date field is too
narrow for a four-digit year, fell to the twin: the box is 0.68 inches
at Arial 12, narrower than `09/09/26`, and the application sets no
`SET CENTURY`.

**What running found that reading had not.** VFP 9's default `SET
ENGINEBEHAVIOR 90` requires every non-aggregated column in a `GROUP BY`.
The stored procedure `RemainingCredit` and the views `order history` and
`top25cust` were written for VFP 7's rule and are quoted in
`docs/09-business-logic/`, where nothing says they fail. Under the
defaults, Order Entry opens through four error dialogs (1807, then 12,
13, 107 as the procedure runs on past the failed query) and shows an
available credit of 999,999,999.99; Order History raises the same 1807
in its data environment and then does not load (2005, its grid's
`ControlSource` alias missing); Top 25 Customers renders no pages and
raises no error that reaches the harness. `baseline-eb70/` shows all
three working under 70. The VFP 7 and VFP 9 twins differ by two lines
(Step 3), so no static comparison could have found this. Two defects are
visible only on the printed page: the invoice's quantity prints as
asterisks (format mask `999999999.99` in a 1.17-inch box), and every
page-header Date ends in an ellipsis. The Case Study report's filter
matches none of the 65 `behindsc` rows, so the dead report is also
empty.

Of the docs' "errors or does nothing" statements, the run reached and
resolved the ones on the click-through path (every form opens and closes
as described, the saved printer environments in the reports do not stop
the listener, the login and find dialogs and About box show); the paths
that need data or a choice (the employee listing's "nothing to print"
branch, a rule violation on save, the credit check on a new order) are
recorded as not reached rather than asserted.

**Sample findings.** Three of the sample's screens and prints fail under
the VFP 9 defaults with no change to the source; the invoice never
printed a legible quantity under this engine; the page-header Date box
is narrower than its value; the dead case-study report has no data
either; the employee title dialog defaults to the first title, not all;
the run stamps two table headers (`customer`, `orders`).

## 2026-09-09 Step 9: data-entry capture pass

**Output.** `baseline-entry/` and `baseline-entry-eb70/`: the same harness
run with `-Pass entry`, under VFP 9's default engine and under
`SET ENGINEBEHAVIOR 70`. Eight scenarios drive the forms through what a
click-through cannot reach: a field rule violated on Save (Customers), a
delete the referential-integrity trigger refuses (Shippers), a new order
refused four times (no line item, below the customer's minimum, over the
credit limit for a customer already over it, no shipper), Add Customer
with an empty ID, Change Password with a mismatched confirmation and
with nothing entered, Login with a wrong password, and the Employee
Listing's title dialog. 25 and 27 form images, 3 report pages each, 98
and 12 message boxes. `docs/10-baseline/data-entry.md` indexes both,
generated by `tools/docgen/gen_entry_docs.py` from the runs' records.
Nothing was saved: after each run the data files differ from the
committed ones by five header stamps and the order-number counter, and
were restored.

**Method.** Scenarios reuse the harness: set a control's `Value` with
focus on it and call the form's own `Save()`, so the application's
`WriteBuffer`, the DBC rule, and the form's `Error` method run as they
would for a user; do what a form's own code would do to its tables
through `SET DATASESSION TO` the form's session and `EXECSCRIPT`; write
an answer file before an action whose dialog needs a specific button
(Yes on the delete confirmation) or keystrokes in the report dialog, and
let the runner consume it. Every scenario ends in a refusal or a
`Restore()`, and the data is diffed byte by byte afterwards.

Two harness rounds. The first skipped the empty-password scenario
because `SET EXACT OFF` made `"chngpswd-empty" = "chngpswd"` true in the
dispatch (`==` now), never reached the over-credit prompt because the
credit check counts saved orders only (a customer already over the
limit was found in the data), and lost the engine-70 run to the title
dialog staying open after its keystrokes (the runner now presses Enter
again if the window is still up after six seconds). The second round
ran clean under both engines. One draft claim fell before the page was
written: "the All Titles checkbox has the first tab stop, so Space then
Enter selects all titles" was true of the tab order in the twin and
false of the run; the page says what the twin shows (`cTitle` defaults
to `ALL` and is set only by an interactive change) and what each run
printed, and calls the keystroke path non-deterministic.

**What running found.** Every abandoned new order consumes an order
number (`newid()` increments the counter in `setup.dbf` at once), which
is the mechanism behind the counter standing 59 above the order count
noted in Step 6. The customer rule fires and the message shows, yet
`Save()` returns `.T.`, because the refused value never reaches the
buffer and the form then sees nothing to save. The credit check cannot
be tripped by the order being saved; only 2 of 92 customers are already
over their limit, and only they get the prompt. Under the default
engine the order rule degrades with every attempt: `RemainingCredit`
fails, `ValOrder` errors four more times on the undefined result and
leaves an alias open, and four saves produced 98 message boxes against
12 under engine 70; among them the form's own mis-call of `Error` with
the message text where the method name belongs. Setting the customer
through the combo leaves the previous customer's ship-to address. The
Employee Listing prints every title unless the combo is changed
interactively, and its "nothing to print" branch, the one with the
missing `#INCLUDE`, is unreachable through the interface because the
combo lists only titles that employees have. The login's wrong-password
box carries VFP's default caption; the credit prompt misspells maximum.

**Sample findings.** Order numbers leak on every abandoned order; a
refused edit reports success; the credit limit is checked against
history, not the order in hand; the VFP 9 build's order rule cascades
into dozens of error dialogs per save; a programmatic customer change
keeps the old ship-to; the employee listing ignores its own title box
unless touched; one message box has the wrong caption and one a typo.

## 2026-09-09 Step 10: successful-save capture pass

**Output.** `baseline-save/` and `baseline-save-eb70/`: the harness run
with `-Pass save`, under VFP 9's default engine and under
`SET ENGINEBEHAVIOR 70`. Six paths that write: a customer edit (ALFKI's
Contact Title), a new customer (BASEL), a new order (ALFKI, Chai times
150, above the minimum), an order filled from Order History through the
Last Order button and Add to Current Order, a password change and the
login that then uses it, and a delete (BASEL, which has no orders). Each
run's `data-diff.txt` is a record-level diff of `data/` against the
committed files, taken before the data was restored from git;
`docs/10-baseline/save.md` indexes both, generated by
`tools/docgen/gen_save_docs.py` from the records and the diffs. 15 and
19 form images.

**Method.** Same harness: set a control's `Value` with focus on it and
call the form's own `Save()`; a customer, order line, and shipper set
through `SET DATASESSION TO` the form's session and `EXECSCRIPT`; an
answer file for the delete confirmation. The scenarios were sized to the
rules: Chai at 18.00 times 150 is 2,700, less ALFKI's 2% discount 2,646,
above the 2,600 minimum; BASEL's maximum 5,000 and minimum 0 pass the
pair rule; the delete target is a customer with no orders. The diff was
made a record-level tool this step (`dbfdiff.py` now names the changed
fields with old and new values), because the point of the pass is what
reaches disk. Two rounds: the first login scenario typed the password
for whatever employee the combo showed (the first name, Brid), not the
one Change Password had edited (record 1, Buchanan); the scenario now
picks Buchanan by name, and the round trip closed.

**What the data shows.** Under engine 70 all six saved and the diff is
exactly the intended rows and nothing else: ALFKI's title changed, BASEL
appended, orders 1138 and 1139 appended with their Chai lines, employee
1's password `Buck` to `baseline`, BASEL marked deleted, plus the header
stamps and the counter. This is the run in which the schema and rules the
docs describe behave as an application, not a defect list.

Under the default engine the order save is the one that does not hold.
`orderentry.save` returned `.F.`, yet `orders.dbf` gained a fully
populated order 1138 with no matching line item in `orditems.dbf`: the
`GROUP BY` cascade in `RemainingCredit` and `ValOrder` leaves the header
committed inside the transaction that was meant to roll back, and the
lines uncommitted. A dangling order the application believes it did not
create. The below-minimum prompt in that run named $500.00 for a
customer whose minimum is 2,600, the calculation running on the state
the errors left. The other five paths saved under the default engine
too.

Three findings the save confirms against the data rather than the
source. Change Password edits employee record 1 under `DEBUGMODE` (no
login chose anyone), the password changed, and the later login as
Buchanan with the new password succeeded, so the whole round trip holds.
Every `AddNew` advances the ID counter whatever the outcome (1138 to
1139 for the one order under 90, 1138 to 1140 for two under 70), the
mechanism Step 6 inferred and Step 9 saw from abandoned orders, here from
saved ones. Delete marks the record in place: BASEL is still in
`customer.dbf` with its deletion flag set after a successful delete. And
the order just saved appears in Order History at once, its line copyable
to a new order at the stored price, not the current one.

**Sample findings.** Under the VFP 9 default engine a refused order save
leaves a headerless-line order on disk; the below-minimum message names
the wrong amount there; every started order burns an order number;
Change Password with no login edits the first employee and the change is
real; a delete marks but does not remove the row. Under engine 70 the
application saves cleanly and the data moves exactly as the rules say.
