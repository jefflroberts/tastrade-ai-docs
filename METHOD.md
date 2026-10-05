# Method: what this experiment shows about documenting VFP with AI

`JOURNAL.md` is the step-by-step record and `HANDOFF.md` the operational
state. This page is the synthesis for the paper: what the process was, what
it produced, where the AI was right, where it was wrong and how that was
caught, and what a person still had to supply. Every claim here points at
the journal entry or commit that holds the evidence. The Tastrade findings
themselves are the demonstration, not the subject; they are listed at the
end of `HANDOFF.md` under "Sample findings".

## 1. The pipeline

Five stages, each repeated per artifact type.

1. **Binaries to text.** FoxBin2PRG converts every VFP container (`.scx`,
   `.vcx`, `.frx`, `.mnx`, `.dbc`, `.pjx`) to a text twin. It is driven
   in-process through the VFP COM server (`tools/bin2prg_sweep.ps1`),
   because the executable returns before it finishes. 43 of 43 converted,
   twice: once from the VFP 7 binaries and once after a VFP 9 rebuild
   (Steps 1 and 3).
2. **Text to structure.** `foxparse.py` in the toolkit turns each twin into
   a dict: controls, methods, cursors, bands, objects, pads, bars, members.
   Its counts are compared with a raw `grep` of the twin before anything is
   trusted (Step 4a onward).
3. **Reading.** The twin is read in full, with layout properties filtered
   out. Nothing is sampled. For each claim the docs will make about usage,
   the rest of the application is grepped: who launches this, who calls
   that, which constant carries this message.
4. **Generation.** A script under `tools/docgen/` merges the parsed
   structure (schema, code bodies, coordinates, tables of constants, quoted
   verbatim) with hand-written prose (purpose, callers, notes). The output
   is never edited by hand; a correction is a change to the script and a
   rerun.
5. **Verification and record.** A checker counts fences, empty cells, rows
   per section against the parser, and unresolved `[[links]]` across all of
   `docs/`. Then a journal entry, a commit whose message carries the
   findings, and a push.

The AI's part: writing and fixing the parser, writing the generators and
checkers, reading the twins, drafting the prose, running the greps, writing
the journal. The person's part is in section 6.

## 2. What it produced

| Measure | Value |
|---|---|
| Source | Microsoft's Tastrade sample, VFP 7 release: 43 binaries, 2 programs, 2 include files, 10 tables |
| Documentation | 11,926 lines of markdown in 8 folders: data model, forms, classes, reports, menus, programs, architecture, inventory |
| Coverage | Every artifact: 1 DBC with 10 tables and 13 views, 31 classes in 6 libraries, 17 forms, 13 reports, 5 menus, 2 programs, 2 include files, the project |
| Generators | 10 scripts, 4,169 lines, all preserved in `tools/docgen/` |
| Toolkit changes | 6 commits: made app-agnostic, four parser fixes, one new parser, one template |
| Casebook commits | 23 over two days (2026-09-08 and 09), 10 of them documentation steps, the rest baseline, sweeps, toolkit setup, and handoff updates |
| Cross-links | 0 unresolved across `docs/`, checked by script at the end of each step from 4j |
| Verbatim code | Every method body, report expression, menu action, stored procedure, and constant quoted from the twin through the parser, not transcribed |

## 3. Failure mode one: the parser is plausibly wrong

The parser and the skill that drives it had been used on two applications
before this one. On the third they were wrong five times, and never with an
error. Each time the numbers returned were the kind a reader accepts.

| Step | What the parser said | What was true | How it was caught |
|---|---|---|---|
| 4a | 0 classes in every class library | 31 classes; every `DEFINE CLASS` had a trailing `&&` comment | "0 classes" was implausible for a class library |
| 4a | The DBC twin is `.db2` | `.dc2`; `.db2` is a free table | The file on disk had the other extension |
| 4c | 72 methods in the two framework libraries | 116; `PROTECTED PROCEDURE` and trailing comments dropped 44 | A raw `grep -c PROCEDURE` disagreed |
| 4h | Every three-band report was Title / Detail / Summary; no report has cursors | Page Header / Detail / Page Footer; 12 of 13 declare cursors | An empty half-inch "Summary" band made no sense; a report with no data source made no sense |
| 4k | 31 of 78 project members "unknown", two free tables "databases" | Type codes are case-sensitive: `d` container, `D` table, `x` image | Reading the twin's `Type="..."` values |

Two of the five passed the count check. What caught them was reading the
twin and noticing a fact that contradicted what the parser implied. The
rule that came out of it (`HANDOFF.md`, "How the documentation was
produced", item 2): compare the parser with a raw grep first, and treat
agreement as necessary, not sufficient.

The same shape appeared in the generators: one rendered every grid header
caption blank (4f, caught by counting empty cells), one tripled a sentence
in an index on every rerun (4g, caught two steps later), one first counted a
constant as used because of the word "tab" in a comment (4j, caught by
making the count case-sensitive).

## 4. Failure mode two: prose from memory is wrong about one time in five

The parser gives exact structure. The prose is where the errors are. At
every step some claims drafted before grepping turned out wrong:

- 4b: three usage claims checked, two wrong (who runs the startup action,
  whether `CalcOrdTotal` is called).
- 4c: three checked, three wrong (where the About box loads its library,
  which method logs in, which header defines a constant).
- 4g: four launch points missed because the first grep looked for
  `oApp.DoForm` and the menu uses `DO FORM`.
- 4j: `IsTag()` attributed to the base form; the caller is a combo box class.
- 4k: "five modal dialogs" on a base class; the inheritance diagram says four.

None reached a commit. The discipline is two greps per claim: one before
drafting (who calls this, where is that string) and one after (does the
sentence I wrote match the line I quoted). The journal's "Verification"
paragraphs record what was checked each time. The cost is small: a grep
takes seconds, and the twins are text.

## 5. Failure mode three: asserting VFP behaviour that was not run

The model knows a great deal of VFP and will state run-time behaviour with
confidence. Some of it is uncertain at the level of detail the docs need:
what `FILE()` does with an extension-less name (4d), what `Move` does with
no arguments (4g), whether a deactivated window satisfies `WEXIST` (4j),
what `RELEASE BAR` does to a popup that does not exist (4i). The rule
adopted at 4d, and applied since: do not assert VFP behaviour you have not
run. Soften to "errors or does nothing" when the documented conclusion
holds either way, and say "not run here" when it does not. One commit
(`7b3eaae`) exists only to take back such an assertion.

Where behaviour mattered, the evidence was found rather than asserted: the
compiled memo of a report proved its constants were never resolved (4h),
the built EXE proved two menus with no generated program were still
compiled in (4i), VFP's own `_frxcursor.h` supplied the band-bar offset
that makes report coordinates come out right (4h), and the 2001 GENMENU
output was diffed against the menu twins statement by statement (4i).

Step 8 ran the application and settled the rule's other half: what
reading cannot find. The built EXE was driven from inside a VFP 9
session by two timers, every form opened and snapshotted, every report
rendered, every message box logged (`docs/10-baseline/`). The first
thing it found was in none of the 11 thousand lines of docs: VFP 9's
default `SET ENGINEBEHAVIOR 90` rejects the sample's `GROUP BY` queries,
so Order Entry opens through four error dialogs, Order History does not
open at all, and the Top 25 Customers report prints nothing and raises
nothing. The twins are the same text under VFP 7 and VFP 9 (Step 3 counted
two lines of difference), the queries were quoted in the business-logic
page, and the docs said nothing, because nothing in the source says it.
The same capture with the harness forcing `SET ENGINEBEHAVIOR 70` shows
all three working. Two more defects were visible only on paper: the
invoice prints every quantity as asterisks (a format mask wider than its
box), and every report's Date field ends in an ellipsis for a four-digit
year. Of the statements softened to "errors or does nothing", the run
resolved the ones it reached and left the rest marked as not reached.

## 6. What the person supplied

- The subject and the framing: a sample everyone can check, and a paper
  about the method rather than the sample (this page exists because that
  framing was restated on the second day).
- The two hand steps: building the project in the VFP 9 IDE, and closing it
  when the sweep failed with "file access is denied" on the open `.pjx`.
- The operating rules that the AI then applied without being reminded:
  `ON ERROR` and `FFLUSH` in anything run through the hidden COM server,
  after a two-minute hang on an invisible error dialog (4b); only stop a
  `vfp9.exe` you started; `git pull --rebase` before touching the shared
  toolkit, after two sessions parameterized the same tool on the same day
  (4a).
- Continuity. Each session began by reading `HANDOFF.md`, the last two
  journal entries, and `docs/PROJECT.md`, and ended by updating them. The
  handoff is what let the fourth session start on reports with no
  re-derivation.
- Scope decisions: which artifact type next, and that the method page comes
  before the domain synthesis.

## 7. Techniques that carried the work

- **Twins are enough, mostly.** Every doc came from the text twins, the two
  programs, and the include files. The exceptions: field types and index
  expressions, which the DBC twin does not hold, came from a 60-line VFP
  program run headlessly (4b); one report's compiled memo and the EXE's
  strings settled two questions (4h, 4i).
- **Independent sources for cross-checks.** The DBC twin against a live
  `AFIELDS()` dump; menu twins against the 2001 `.mpr`; the project twin
  against the files on disk; parser counts against grep; the VFP 7 twins
  against the VFP 9 twins (two lines differ across 43 files, both
  environment paths).
- **Censuses instead of claims.** "Which constants are unused", "which
  bitmaps does anything reference", "who calls each utility function" were
  answered by scripts that grep everything, with the answer tabulated in
  the doc, rather than by reading and remembering. Two of these had to
  learn to separate design-time metadata (class icons) from run-time
  references.
- **Generators over hand editing.** A fact corrected in a script
  regenerates everywhere it appears; the docgen README says so, and the
  one time a doc was patched by rerunning an old generator (4h), the
  regenerated files were byte-identical except for the fix.
- **The toolkit grows by one parser or template per artifact type.** Reports
  gained band assignment and cursors, menus a parser, include files a
  template, the project a corrected type table. Each fix is a commit with
  the evidence in its message, and the skill copy in the casebook names the
  toolkit commit it came from.
- **Per-step journal with commit hashes.** Method notes, findings, and
  verification are written at the step, when the evidence is at hand, not
  reconstructed later.

## 8. Friction worth reporting

- A hidden VFP COM instance plus a runtime error is a hang, and low-level
  output is lost until flushed (4b).
- `foxbin2prg.exe` on the command line returns before finishing; an earlier
  sweep on another app logged 1,599 "errors" for that reason (Step 1).
- Python patch scripts fed through a shell heredoc lose backslashes; it
  happened in earlier sessions and twice more on the second day before the
  rule "write the script to a file" held (`HANDOFF.md` gotchas).
- FoxBin2PRG adds artifacts of its own: an empty cascading popup per menu
  separator, the compiler's include-file table in a report record after a
  VFP 9 build, generated procedure names. Each had to be recognised as
  tool output, not source (Step 3, 4h, 4i).
- Small housekeeping slips: a `__pycache__` committed and then ignored, a
  wording slip in the handoff, a duplicated phrase. All are in the history.
- Driving a GUI from outside is a run-fail-fix loop of its own (Step 8):
  six capture runs before a clean pair. The stalls were a message box the
  runner could not see (`FindWindowEx` finds no `#32770` on this Windows
  build; `EnumWindows` does), a report dialog VFP's timers do not reach
  while `REPORT FORM` runs, a helper object the application's `CLEAR ALL`
  released on shutdown, and a snapshot error on stderr that PowerShell 5.1
  turned into a terminating error and a killed VFP. Each is one line in
  the toolkit's methodology now; none could have been known from reading.

## 9. What transfers to a customer application, and what may not

The disciplines transfer: parser-versus-grep, grep-before-write, no
unrun assertions, generators not hand edits, per-step records. The
specific parsers and templates transfer with the toolkit, and the record
here says that on a third application they still broke five times in two
days; a fourth application will break them again in new places, and the
method's value is that the breakage is caught at the count or the read,
not in the delivered doc.

What may not transfer: Tastrade is small (43 binaries, 11 thousand lines
of documentation), its code is 1995 to 1998 Microsoft sample code with
comments and consistent naming, and it has no external components, no
SQL pass-through, no COM servers, no third-party controls. A customer
application will be larger, less regular, and will hold behaviour that
only running it reveals. The baseline capture (Step 8) shows the size of
that gap on even this sample: three of its screens and prints fail under
the VFP 9 defaults, and the docs written from the source alone had no way
to say so.

## 10. Open questions for the paper

- **Cost.** Two calendar days and 23 commits for 43 binaries (plus a third
  day for the free tables and the baseline) is a
  measure of the record, not of effort; token and wall-clock accounting
  were not kept. A second run on another sample, with timing, would let
  the paper give a rate.
- **Reader validation.** The docs have been checked against the source by
  the method above but not yet read by a VFP developer who knows Tastrade.
  That review is the test the choice of subject was meant to enable.
- **Rebuild fidelity.** The docs claim to be enough to rebuild each
  artifact. Nothing has been rebuilt from them.
- **Running the application.** Done in Step 8 for what a click-through
  reaches (every form, every report, no data entry). Paths that need data
  or a choice (the employee listing's "nothing to print" branch, Save with
  a rule violation, the credit check on a new order) are still unrun; a
  second harness that fills forms would reach them.
