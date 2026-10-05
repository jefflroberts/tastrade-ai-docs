# tastrade-ai-docs

What happened when AI tooling was used to convert, read, and document a legacy Visual FoxPro
application. The subject is Microsoft's own **Tasmanian Traders (Tastrade)** sample, chosen so
that no customer code or data is involved.

This is the **docs-only edition**. It holds the documentation, the experiment journal, the
method write-up, and the scripts that produced them. It does **not** contain Tastrade itself:
the sample is Microsoft's copyrighted code, and the Visual FoxPro license does not allow
redistributing it.

## What's here

| Path | Contents |
|---|---|
| [`METHOD.md`](METHOD.md) | The synthesis: what the experiment showed about documenting VFP with AI, with pointers into the journal. Start here. |
| [`JOURNAL.md`](JOURNAL.md) | The step-by-step record of every pass, in order, with what worked and what didn't. |
| [`HANDOFF.md`](HANDOFF.md) | The working state between sessions: the documentation recipe, gotchas, method findings, and sample findings. |
| [`docs/`](docs/) | One document per form, class library, report, menu, table, and program, plus architecture, domain, data-model, business-logic, and baseline pages. Start at [`docs/README.md`](docs/README.md). |
| [`tools/docgen/`](tools/docgen/) | The scripts that generated most of `docs/` from the FoxBin2PRG text files. |
| [`tools/baseline/`](tools/baseline/) | The capture harness that drove the running app to record every form and report. |
| `tools/*.ps1` | The FoxBin2PRG conversion sweeps, with their logs. |
| `baseline*/` | Capture logs and indexes from each baseline run. The screenshots themselves are not included. |

## How this edition differs from the working repo

- **No Tastrade source, data, help file, bitmaps, or executables.**
- **Quoted code is trimmed.** Where the docs quoted Microsoft's source at length, each block keeps
  its first few lines and a note naming the method the rest is in. Short quotes are unchanged.
- **No screenshots.** The baseline pages still list every capture with its form, caption, and
  size; the image names are kept so you can match them to your own capture run.
- **Commit hashes in the journal refer to the private working repo**, whose history starts with
  the pristine Microsoft source and so can't be published. They show the order of the work but
  don't resolve here.
- **The toolkit has since been renamed.** The journal's `vfp-migration-toolkit` is today's
  [`vfp-documentation-toolkit`](https://github.com/jefflroberts/vfp-documentation-toolkit).

## Reproducing the work

You need your own copy of Tastrade. The complete source shipped as a sample with **Visual FoxPro
5, 6, and 7** (`Samples\Tastrade\`); the edition documented here is the VFP 7 source, with project
files dated 2001-02-05. Visual FoxPro 9 ships only Tastrade's `Data` and `Bitmaps` folders, which
is not enough.

1. Clone this repo and the toolkit side by side:
   ```sh
   git clone https://github.com/jefflroberts/tastrade-ai-docs.git
   git clone https://github.com/jefflroberts/vfp-documentation-toolkit.git
   ```
2. Copy the contents of your `Samples\Tastrade\` folder into the root of `tastrade-ai-docs`
   (`forms/`, `libs/`, `data/`, `tastrade.pjx`, and so on). `.gitignore` keeps all of it out of git.
3. Convert the binaries with [FoxBin2PRG](https://github.com/fdbozzo/foxbin2prg), using
   `tools/bin2prg_sweep.ps1` and `tools/bin2prg_free_tables.ps1`.
4. Regenerate the docs with the scripts in [`tools/docgen/`](tools/docgen/). They find the toolkit
   and the source on their own when the two repos sit side by side; otherwise set
   `VFP_TOOLKIT_TOOLS` and `TASTRADE_ROOT`. Regenerated docs carry the full method bodies from your
   copy.
5. Capture the baseline with `tools/baseline/run_capture.ps1` (needs Visual FoxPro 9).

## License

The documentation, journal, method write-up, and scripts are © 2026 Jeff Roberts, released under
the [MIT License](LICENSE).

Tastrade (Tasmanian Traders) is © Microsoft Corporation. The short excerpts of its source quoted
in `docs/` are included for reference and commentary; they are Microsoft's, not covered by this
repo's license, and are not a license to the sample. This project is not affiliated with or
endorsed by Microsoft.
