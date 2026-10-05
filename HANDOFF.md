# Handoff

State of the tastrade-ai experiment as of 2026-09-09 (after Step 10), for
resuming in a new session. `JOURNAL.md` is the narrative record for the paper; this file is the
operational one.

## What this is

An experiment in using AI tooling (Claude Code) to convert, read, and document
a legacy Visual FoxPro application, using Microsoft's Tastrade sample so no
customer code is involved. Output feeds a paper and a presentation on AI with
VFP. Every step is a commit here and an entry in `JOURNAL.md`.

## Repos and paths

| What | Where |
|---|---|
| This repo (casebook) | the published docs-only edition; the Tastrade source is supplied by the reader (see README) |
| Toolkit (shared spine) | [`jefflroberts/vfp-documentation-toolkit`](https://github.com/jefflroberts/vfp-documentation-toolkit), cloned next to this repo |
| VFP 9 SP2 | `C:\Program Files (x86)\Microsoft Visual FoxPro 9`; COM server `VisualFoxPro.Application.9` |
| FoxBin2PRG 1.21.04 | installed through Thor (`Thor\Tools\Components\FoxBin2PRG\foxbin2prg.exe`) |
| Parser | the toolkit's `tools/foxparse.py` (`--summary`, `--json`) |
| Skill | `.claude/skills/document-vfp-artifact/` (copy of the toolkit's; `SOURCE.md` names the commit) |
| App config for the skill | `docs/PROJECT.md` (read this before documenting anything) |
| Doc generators | `tools/docgen/` (see its README; edit the script, rerun, never hand-edit generated docs) |
| Method synthesis | `METHOD.md` (what the experiment shows about the method; the paper's subject) |
| FoxBin2PRG sweep | `tools/bin2prg_sweep.ps1` (drives the tool through the VFP COM server; log beside it); `tools/bin2prg_free_tables.ps1` for the three free tables |
| Baseline capture | `tools/baseline/run_capture.ps1` (visible VFP 9, `DO tastrade.exe`, timers; `-Engine 70 -OutDir baseline-eb70` for the comparison run; `-Pass entry -OutDir baseline-entry[-eb70]` for the data-entry scenarios); output `baseline*/`, indexes `docs/10-baseline/README.md` and `data-entry.md` from `tools/docgen/gen_baseline_docs.py` and `gen_entry_docs.py`. Restore `data/` after an entry run (`git checkout -- data`) |

Both repos were clean and pushed at handoff. The toolkit's last commit here
was `9e5f466` (answer file in `Watch-Dialogs.ps1`, scenario-pass notes; `cb074de` baseline-capture helpers and methodology section 12; `61e579f` free-table tags; `fc295b9` project type codes; `e46e61a` skill
include files; `9a716a0` menu parser; `c578f09` report fixes);
another session may push to it independently, so `git pull --rebase` before
committing there. `tools/extract_frx.py` needs `pip install reportlab`.

## Done

| Step | Result | Commit |
|---|---|---|
| 0 | Pristine VFP 7 source committed untouched, with `.gitattributes` for byte-exact binaries | `e7ac5a1` |
| 1 | FoxBin2PRG sweep: 43 of 43 binaries converted (expected failures did not happen) | `79a154d` |
| 3 | Rebuilt in VFP 9; twins differ by two lines across 43 files (both environment paths) | `3511659` |
| 4a | Toolkit made app-agnostic; `docs/PROJECT.md`; two parser bugs fixed (`&&` on `DEFINE CLASS`, `PROTECTED PROCEDURE` / `&&` on methods) | `7376209`, toolkit `8498186`, `9355a36` |
| 4b | DBC documented: `docs/03-data-model/` (container + 10 tables) | `e91aab8` |
| 4c–4d | All 6 class libraries, 31 classes: `docs/05-classes/` | `f902917`, `a24eee2`, `7b3eaae` |
| 4e–4g | All 17 forms: `docs/04-forms/` | `298dce8`, `f6d4ffb`, `911dcd6` |
| 4h | All 13 reports: `docs/06-reports/` (third parser bug fixed, toolkit `c578f09`) | `bd942b7` |
| 4i | All 5 menus: `docs/07-menus/` (`.mn2` parser added, toolkit `9a716a0`) | `58d653e` |
| 4j | Both programs and both include files: `docs/08-programs/`; every `[[link]]` in `docs/` resolves | `ca43842` |
| 4k | Project manifest and architecture pages: `docs/01-architecture/` (fourth parser fix, toolkit `fc295b9`); inventory regenerated | `34b87c6` |
| 5 | `METHOD.md`, the synthesis for the paper; HANDOFF findings split into method and sample | `cf342cd` |
| 6 | Domain and business-logic synthesis: `docs/02-domain/`, `docs/09-business-logic/` (R1 to R14, quoted through the parser) | `db3f4f6` |
| 7 | Free tables: `.db2` twins and `docs/03-data-model/tables/behindsc.md`, `repolist.md`, `ttrade.md`; fifth parser gap (toolkit `61e579f`) | `a6c6397` |
| 8 | Baseline capture from the running EXE: `baseline/` (30 forms, 10 main-window states, 24 report pages, 5 message boxes), `baseline-eb70/` (same under `SET ENGINEBEHAVIOR 70`), `docs/10-baseline/`; toolkit `cb074de` | `06d1dab` |
| 9 | Data-entry pass: `baseline-entry/`, `baseline-entry-eb70/` (eight scenarios, every one refused, nothing saved), `docs/10-baseline/data-entry.md` | `10e1728` |
| 10 | Successful-save pass: `baseline-save/`, `baseline-save-eb70/` (six write paths, record-level diffs, data restored), `docs/10-baseline/save.md` | `3ec4a09` |

## Not done

In the intended order:

1. **Paths still unrun** after the three capture passes: the employee
   listing's "nothing to print" branch (unreachable through the interface:
   the combo lists only titles that exist), a user's interactive pick from
   the order form's customer combo list (the harness set `Value`, which
   runs the programmatic path), and the reindex the database-utilities form
   offers. None is likely to change the method argument; the successful
   save (Step 10) was the last one worth its own pass.
2. **Cross-links**: all resolve (1,007 checked with an inline script at the
   end of Step 8, `[[...]]` and the `../../baseline` image links). Every
   folder in the docs map exists and every source artifact has a twin and
   a doc.
3. **For the paper** (`METHOD.md`, section 10): cost accounting on a second
   run, review of the docs by a VFP developer, a rebuild from the docs.
   The run is done; the comparison with `SET ENGINEBEHAVIOR 70` is the
   paper's example of what reading cannot find.

## How the documentation was produced (repeat this)

1. Read `docs/PROJECT.md`, then read the twin(s) in full. Filtering layout
   properties out with `grep -vE` keeps the read manageable; never sample.
2. Run `foxparse.py` on the twin and compare its counts against a raw grep
   (`DEFINE CLASS`, `PROCEDURE`, `objtype=`, `.ADD(`, `<INDEX>`) before
   trusting it. All five parser bugs so far produced plausible numbers
   rather than errors; the third (report band names off by one, cursor records skipped)
   and the fourth (project type codes: `D` is a table, `d` the database,
   `x` an image) passed the count check and were caught only by reading
   the twin.
3. Grep the rest of the app for every claim about usage: who launches the
   form (`oApp.DoForm` **and** `DO FORM`, case-insensitive), who calls the
   method, which string constant a message uses. Roughly one claim in five
   drafted from memory was wrong before this pass.
4. Write a generator under `tools/docgen/` that quotes method bodies from
   the parser and merges hand-written prose. Schema and code are exact;
   prose is where errors hide.
5. Verify the output (counts of fences, empty table cells), then journal,
   commit, push. Commit messages carry the findings.

## Gotchas learned

- **Hidden VFP COM instance + runtime error = hang.** Always `ON ERROR` in
  any `.prg` run through COM, and `FFLUSH` low-level writes. The user's own
  IDE instance may be running; only kill the PID you started.
- **`foxbin2prg.exe` returns before it finishes**; drive it in-process
  through the COM server (`tools/bin2prg_sweep.ps1`) for real return codes.
  A `.pjx` open in the IDE fails with 1705; ask the user to close it.
- **Bash heredocs with Python string patches** mangled backslash escapes
  several times; patch by line index or use the Write tool for whole files.
- **DBF field names are 10 characters**; long names live only in the DBC.
  `tools/dbf.py` returns rows keyed by the short names.
- **Do not assert VFP behaviour you have not run.** Soften to "errors or
  does nothing" when the conclusion holds either way.
- **FRX objects carry no band tag.** Their `vpos` includes one designer
  band bar per preceding band (20 pixels; 19 in `viewcode.frx`), so band
  membership is "below the previous band's content", which `parse_fr2` now
  does. A `picture` attribute on a field is its format mask, not an image.
- **Report printer records are stored twice** (text `expr`, binary DEVNAMES
  `tag`) and can disagree; check both.
- **Menu twins add an empty cascading popup to every separator bar**; the
  `.mpr` has none. Diff the twin against the `.mpr` when one exists, and
  grep the EXE for status text when one does not.
- **Class-icon metadata looks like a bitmap reference.** `ProjectClassIcon`
  and `ClassIcon` in `*< CLASSDATA` lines name bitmaps the Class Browser
  shows; separate them from run-time references before calling a file
  used. Picture paths also live in data rows (`category.picture_file`,
  `employee.photo_file`), not only in code.
- **Driving the running app**: see `vfp-ui-capture-gotchas` in memory and
  the toolkit methodology section 12. Short form: timers on `_SCREEN`
  reach ordinary modal forms but not a report's parameter dialog (answer
  it with Enter from outside); message boxes need `EnumWindows`, not
  `FindWindowEx`; press Ignore, never Abort (`DEBUGMODE` `SUSPEND`s);
  the app's closing `CLEAR ALL` releases what the harness put on
  `_SCREEN`; `ReportListener` PNG output is half-size here, use EMF;
  `_SCREEN.HWnd` is the MDI client; a PowerShell 5.1 native command
  writing to stderr under `-ErrorAction Stop` is a terminating error.
  The app stamps `customer.dbf` and `orders.dbf` headers on open, and an
  entry run stamps three more and advances the order counter in
  `setup.dbf`; restore them (`git checkout -- data`) before committing.
  Scenario dispatch must compare with `==` (`SET EXACT OFF`); a rule
  message and `Save()` returning `.T.` can coexist; the credit check reads
  saved rows only, so pick a customer already over the limit. For a save
  pass, size the values to the rules (an order above the customer minimum,
  a new customer whose min/max pair is valid, a delete target with no
  child rows) and diff `data/` at the record level (`tools/.../dbfdiff.py`)
  before restoring; Change Password edits employee record 1 under
  `DEBUGMODE`, so log in as that employee, not the combo's default.
- **Python patch scripts with backslashes go through the Write tool**, never
  a Bash heredoc: a doubled backslash in the heredoc reached Python as a
  single one again this session (the HANDOFF update failed once with
  "truncated \xXX escape" on `reports\x.frx`).

## Method findings, for the paper

The paper is about using AI to document VFP applications, not about
Tastrade. `METHOD.md` is the synthesis; the short form:

- **The parser is plausibly wrong, never loudly wrong.** Five times on this
  third application (class regex, DBC extension, method regex, report bands
  and cursors, project type codes); two passed a count check and were caught
  only by reading the twin. Compare with a raw grep first; treat agreement
  as necessary, not sufficient.
- **Prose from memory is wrong about one time in five.** Every step had
  usage claims that a grep overturned before commit. Grep before drafting
  and after; the twins are text and the greps are cheap.
- **Do not assert VFP behaviour you have not run.** Four assertions were
  softened; one commit exists only to retract one. Where behaviour
  mattered, evidence was found instead: a compiled memo, the EXE's strings,
  VFP's own header files, the 2001 generated menu code.
- **Generators, not hand edits**, so a corrected fact regenerates
  everywhere; **censuses, not claims**, for anything that is a list (unused
  constants, bitmap referrers, callers).
- **The toolkit grows one parser or template per artifact type**, and each
  fix is a commit whose message carries the evidence.
- **The person supplied** the subject, the framing, the two hand steps in
  the IDE, the operating rules learned from hangs and conflicts, the
  continuity files, and the scope decisions.
- **Friction to report**: hidden-COM hangs, a converter that returns early,
  heredoc backslash loss, converter artifacts that look like source.
- **Open**: cost accounting, review by a VFP developer, rebuild fidelity,
  and a capture pass that enters data.
- **Running the application found what reading could not.** VFP 9's
  default `SET ENGINEBEHAVIOR 90` rejects three of the sample's `GROUP BY`
  queries: Order Entry opens through four error dialogs, Order History
  does not open, Top 25 Customers prints nothing and raises nothing. The
  twins are the same text under VFP 7 and 9, the queries were quoted in
  the business-logic page, and the docs had no way to say so. The same
  capture under 70 shows all three working (`baseline-eb70/`). Two more
  defects exist only on paper (invoice quantity as asterisks, page-header
  Date truncated). Six harness runs to a clean pair; every stall was an
  environment fact, now a line in the toolkit methodology.
- **The image is a source too.** One findings-page claim ("empty text
  box") fell to the screenshot, one ("four-digit year") to the twin; the
  one-in-five rule applies to observations as much as to code.
- **Data entry finds the mechanisms.** Step 9's refused saves explained
  the order-counter gap (every abandoned order consumes a number), showed
  that a refused edit reports success, that the credit check reads
  history only, and that the VFP 9 order rule cascades into dozens of
  dialogs per save (98 against 12 under engine 70). Each scenario was
  chosen to end in a refusal, and the data was diffed byte by byte after
  every run; a draft claim about the title dialog's tab order fell to the
  run and the page now rests on the twin.
- **The successful save is the control.** Step 10 saved the six write
  paths and diffed the data at the record level: under engine 70 exactly
  the intended rows moved, which is the evidence that the documented
  schema and rules describe a working application. The same order save
  under the default engine returned `.F.` yet left an order header on disk
  with no line items, so the `GROUP BY` defect is not only noisy but
  corrupts: a diff of what reached disk, not an inference. The pass also
  confirmed Change Password edits the first employee (the password round
  trip closed) and that a delete marks the row in place.
- **Measure drift, do not assert it.** The self-documentation table's 74
  code instructions were resolved against the twins by a script (68 hold,
  6 do not), each miss confirmed by grep and three hits spot-checked, so
  the finding is a count with a table behind it.
- **Synthesis pages must be generated too.** Step 6 pulled every quoted
  rule through the parser at generation time and profiled the data for
  the numbers; the authors' own descriptions of their rules were wrong
  three times, and two draft claims were overturned by grep.

## Sample findings (the demonstration, not the subject)

- `DEBUGMODE = .T.` in the shipped header disables login, the startup
  action, the logged-in-employee delete guard, the menu's privilege gating,
  and makes Change Password edit the first employee. The sample as built
  has no security, and every user gets the Utilities pad with the Command
  window. The gating itself is half broken: its `RELEASE BAR` lines name
  a popup (`Administration`) that does not exist.
- Passwords are plain text, default `"Tastrade"`, and displayed in three
  places (login hint, employee list grid, change-password hint).
- The order total formula is written seven times (2 stored procedures, 2
  views, 1 stored procedure with freight, the order entry screen, the
  invoice report's variables). One copy, `CalcOrdTotal()`, is called by
  nothing.
- The sales views sum unit price without quantity, and the two sales reports
  print that as "Sales"; the Top 25 Customers report uses the full total, so
  the three reports do not reconcile.
- Three parser bugs, one dead form (`casestdy`) and its dead report, one
  dead splitter, three dead cursors in `topcust.frx`, one dead class
  reference in the self-documentation data, saved printer environments in
  all 13 reports (four devices, three of them Microsoft network printers),
  three original-author paths (`c:\fox30\nwind\beta1`, `h:\allisonk\sampapp`, `..\backup\mainsamp`).
- Behind the Scenes reads `.scx`/`.vcx` as tables to show method code: an
  in-app FoxBin2PRG from 1995.
- The VFP 7 → VFP 9 "upgrade" changed two lines of source-level text.
- The employee listing's data environment code uses include-file constants
  with no `#INCLUDE`; the compiled `.frt` proves they were not resolved, so
  its "nothing to print" path is a runtime error.
- Two reports depend on VFP's automatic view column names (`exp_1`,
  `sum_unit_price`, `company_name_a`/`_b`).
- Three menu pads reuse VFP system pad names (`_msm_file`, `_msm_edit`,
  `_msm_systm`) as a placement trick; two About boxes with different
  versions and copyrights; menu text is not localized while form text is.
- Thirteen `#DEFINE`s are unused and eleven `_LOC` strings sit outside
  `strings.h`; the user-level names in `tastrade.h` must match table rows
  upper-cased or the gating vanishes; VFP's toolbars are hidden by their
  English window titles; `main.prg` declares six API functions for the
  classes and calls none.
- Under VFP 9's defaults the sample cannot open Order Entry cleanly or Order
  History at all and cannot print Top 25 Customers (`GROUP BY` rule, Step 8);
  the invoice prints every quantity as asterisks; every page-header Date is
  truncated; the case-study report has no matching data; the run stamps
  two table headers (`customer`, `orders`).
- Every abandoned new order consumes an order number; a refused customer
  edit shows its rule and `Save()` returns `.T.`; the credit limit is checked
  against saved unpaid orders only (2 of 92 customers can trip it); the
  order rule under VFP 9 defaults cascades into error dialogs and the form
  mis-calls `Error` with the message as the method name; a programmatic
  customer change keeps the old ship-to; the employee listing prints every
  title unless its combo is touched, and its latent "nothing to print"
  error is unreachable; the login's error box has VFP's caption; the credit
  prompt misspells maximum (Step 9).
- Under the VFP 9 default engine a refused order save leaves an order
  header on disk with no line items (a dangling order), and the
  below-minimum message names the wrong amount; under engine 70 the six
  write paths save cleanly and the data moves exactly as the rules say.
  Change Password with no login edits employee record 1 and the change
  persists (login with the new password succeeds); a delete marks the row
  in place rather than removing it (Step 10).
- The EXE has no version resource; of 83 bitmaps 30 are in the project and
  19 used at run time, 23 are named only by data rows as relative paths,
  15 are Class Browser icons, 15 are dead; the project's home directory
  (`c:\vfp\tastrade`) is a fourth build location; four undescribed project
  members are the four late additions with `Cpid = 1252`.
