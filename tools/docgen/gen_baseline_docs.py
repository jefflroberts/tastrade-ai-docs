"""Generate docs/10-baseline/README.md, the index of the screenshot baseline in
baseline/ (Step 8).

Everything in the page comes from the capture run's own records:
baseline/CAPTURE-LOG.csv (one row per capture, written by
tools/baseline/capture.prg), baseline/dialogs.csv (every Win32 message box the
runner saw, tools/baseline/run_capture.ps1), baseline/capture.log (timings and
errors), and the PNG headers for pixel sizes. The prose is hand-written and
held here. Rerun after every capture; never hand-edit the output.
"""
import os, csv, struct, re, collections

ROOT = os.environ.get("TASTRADE_ROOT", os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))
BASE = os.path.join(ROOT, "baseline")
OUT = os.path.join(ROOT, "docs", "10-baseline")
REL = "../../baseline/"

# Where each captured thing is documented.
FORM_DOC = {  # .scx forms -> docs/04-forms
    "customer": "customer", "employee": "employee", "product": "product", "supplier": "supplier",
    "category": "category", "shipper": "shipper", "ordentry": "ordentry", "ordhist": "ordhist",
    "behindsc": "behindsc", "viewcode": "viewcode", "reports": "reports", "chngpswd": "chngpswd",
    "rebuild": "rebuild", "custadd": "custadd", "casestdy": "casestdy", "getinv": "getinv",
    "gettitle": "gettitle",
}
CLASS_DOC = {  # class-based forms -> docs/05-classes
    "introform": ("tsgen", "introform"), "loginpicture": ("login", "loginpicture"),
    "findcustomer": ("tsgen", "findcustomer"), "findorder": ("tsgen", "findorder"),
    "about": ("about", "aboutbox"), "toolbar": ("tsbase", "tstoolbar"),
}
REPORT_TITLE = {
    "listcat": "Category Listing", "listcust": "Customer Listing", "listempl": "Employee Listing",
    "listprod": "Product Listing", "listship": "Shipper Listing", "listsupp": "Supplier Listing",
    "orders": "Invoices", "salesdet": "Sales Detail", "salessum": "Sales Summary",
    "topcust": "Top 25 Customers", "behindsc": "Behind the Scenes", "casestdy": "Case Study",
    "viewcode": "Code Report",
}


def png_size(path):
    with open(path, "rb") as f:
        head = f.read(24)
    assert head[:8] == b"\x89PNG\r\n\x1a\n", path
    w, h = struct.unpack(">II", head[16:24])
    return w, h


def md(s):
    return str(s).replace("|", "\\|").replace("\r\n", " ").replace("\n", " ").strip()


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def base_id(cid):
    return re.sub(r"-(page\d+|listings)$", "", cid)


def doc_link(cid):
    b = base_id(cid)
    if b in FORM_DOC:
        return "[[../04-forms/%s.md]]" % FORM_DOC[b]
    if b in CLASS_DOC:
        lib, cls = CLASS_DOC[b]
        return "[[../05-classes/%s.md]] (`%s`)" % (lib, cls)
    return ""


def load(base):
    """Rows of one capture run, with the runner's form captures folded in."""
    rows = read_csv(os.path.join(base, "CAPTURE-LOG.csv"))
    dialogs = read_csv(os.path.join(base, "dialogs.csv"))
    # The runner, not the harness, captures the two report parameter dialogs
    # (it presses Enter from outside VFP); its rows carry a forms/ file.
    runner_forms = [d for d in dialogs if d["file"].replace("\\", "/").startswith("forms/")]
    dialogs = [d for d in dialogs if d not in runner_forms]
    for d in runner_forms:
        fid = os.path.splitext(os.path.basename(d["file"]))[0]
        rows.append({"seq": d["seq"], "kind": "form", "id": fid,
                     "form_name": {"getinv": "Form1", "gettitle": "frmGetTitle"}[fid],
                     "form_class": "form", "caption": "Report Parameters",
                     "how": "opened by the report's data environment Init during REPORT FORM; run_capture.ps1 pressed Enter (OK is the default button)",
                     "file": d["file"].replace("\\", "/"), "pages": "0", "status": "ok", "note": d["text"]})
    log = open(os.path.join(base, "capture.log"), encoding="latin-1").read().splitlines()
    for r in rows:
        if r["file"] and r["status"] == "ok":
            r["w"], r["h"] = png_size(os.path.join(base, r["file"].replace("/", os.sep)))
    return rows, dialogs, log


def main():
    rows, dialogs, log = load(BASE)
    first, last = log[0][:19], log[-1][:19]
    engine = re.search(r"ENGINEBEHAVIOR (\d+)", "\n".join(log)).group(1)
    hidden = [l.split("now hidden: ", 1)[1] for l in log if "now hidden: " in l]
    errors = [l for l in log if " ERROR " in l]
    forms = [r for r in rows if r["kind"] == "form"]
    screens = [r for r in rows if r["kind"] == "screen"]
    reports = [r for r in rows if r["kind"] == "report"]
    drivers = {r["id"]: r for r in rows if r["kind"] == "driver"}
    err_rows = [r for r in rows if r["kind"] == "error"]

    report_pngs = collections.defaultdict(list)
    for name in sorted(os.listdir(os.path.join(BASE, "reports"))):
        m = re.match(r"(\w+)-p(\d+)\.png$", name)
        if m:
            report_pngs[m.group(1)].append((int(m.group(2)), name))

    def img(rel, alt):
        return "![%s](%s%s)" % (alt, REL, rel)

    L = ["# Screenshot baseline", ""]
    L += ["What the VFP 9 build of Tastrade shows on screen and prints, captured from the running `tastrade.exe` on %s "
          "so a rebuild can be compared against it. The images are in `baseline/` at the repo root; this page is the index. "
          "Every row below was written by the capture run itself (`baseline/CAPTURE-LOG.csv`, `baseline/dialogs.csv`, `baseline/capture.log`); "
          "nothing here is described from memory." % first[:10], ""]
    L += ["**Related docs:** [[data-entry.md]] (the second pass, refused edits), [[save.md]] (the third pass, successful saves), [[../04-forms/README.md]], [[../06-reports/README.md]], [[../05-classes/README.md]], [[../01-architecture/startup.md]], [[../README.md]].", ""]
    L += ["## How it was captured", ""]
    L += ["- `tools/baseline/run_capture.ps1` starts a visible VFP 9 with `tools/baseline/capture.fpw`, whose `COMMAND` runs `tools/baseline/capture.prg`. "
          "The harness does `DO tastrade.exe`, so the code that runs is the compiled EXE's own (`progs/main.prg`, the class libraries, the forms and reports inside it); "
          "VFP is the host only. Differences from a standalone run: the harness sizes the main window to 1024 by 700 client pixels, the VFP status bar is on, "
          "and `_VFP.StartMode` is the IDE's (nothing in the source reads it).",
          "- Two timers on `_SCREEN` drive the application while its `READ EVENTS` is live. One opens each form the way the main menu does (`oApp.DoForm(...)`), "
          "snapshots the form window and the main window, and releases it. The other fires inside every modal `Show()`, snapshots the modal form, and presses the button that closes it "
          "(Continue on the intro form, Cancel or Close elsewhere), so the run needs no hand. The two report parameter dialogs open while `REPORT FORM` runs, when VFP does not fire timers; "
          "the runner outside VFP snapshots them and presses Enter, which is OK.",
          "- Snapshots are `PrintWindow` by HWND from `tools/baseline/snap.ps1`, taken with a DPI-unaware thread so a 1990s form is stored at its own pixel size on a 200% desktop.",
          "- Reports are rendered the way the picker runs them, a cold `REPORT FORM x.frx`, into a VFP 9 `ReportListener` (`ListenerType` 3) whose pages are written as EMF and rasterised at twice 96 dpi (`tools/baseline/emf2png.ps1`). "
          "The first three pages of each report are kept; the page count is recorded for all of them. The EXE itself previews with the legacy engine (`SET REPORTBEHAVIOR 80`), "
          "so the listener's rendering is the object-assisted engine's; layout and data are the same, glyph placement can differ by a pixel.",
          "- `SET ENGINEBEHAVIOR` was %s, VFP 9's default, as in the EXE. VFP windows visible when the harness started and hidden by it, because the runtime has none: %s." % (engine, "; ".join(h.strip("; ") for h in hidden) or "none"),
          "- The runner watches the VFP process for Win32 message boxes, snapshots each, logs its text and buttons to `baseline/dialogs.csv`, and presses Ignore, OK, No, or Cancel, in that order of preference.",
          "- Started %s, finished %s. `tastrade.ini` is reset to the committed file before and after the run because the application writes window positions into it as forms close." % (first[11:19], last[11:19]),
          ""]

    L += ["## Forms", ""]
    L += ["%d images. `page2`, `page3`: the other pages of a form's page frame. `listings`: the report picker with Listings selected. Sizes are the window including its border and title bar." % len(forms), ""]
    L += ["| Image | Form (`Name`, class) | Caption | Launched as | Size | Doc |", "|---|---|---|---|---|---|"]
    for r in forms:
        if r["status"] != "ok" or not r["file"]:
            L.append("| (none) | `%s` | | `%s` | **%s**: %s | %s |" % (
                r["id"], md(r["how"]), r["status"], md(r["note"]), doc_link(r["id"])))
            continue
        L.append("| [`%s`](%s%s) | `%s` (`%s`) | %s | `%s` | %s×%s | %s |" % (
            r["file"].split("/")[-1], REL, r["file"], md(r["form_name"]), md(r["form_class"]), md(r["caption"]),
            md(r["how"]), r["w"], r["h"], doc_link(r["id"])))
    L.append("")
    L += ["### Main window", ""]
    L += ["`_SCREEN` with the menu and, once a framework form is open, the navigation toolbar. %d images." % len(screens), ""]
    L += ["| Image | State | Size |", "|---|---|---|"]
    for r in screens:
        size = "%s×%s" % (r["w"], r["h"]) if r["status"] == "ok" else r["status"]
        L.append("| [`%s`](%s%s) | %s | %s |" % (r["file"].split("/")[-1], REL, r["file"], md(r["note"]), size))
    L.append("")

    L += ["## Reports", ""]
    L += ["| Report | Pages | Kept | Run as | Result | Doc |", "|---|---|---|---|---|---|"]
    for r in reports:
        kept = ", ".join("[p%d](%sreports/%s)" % (n, REL, f) for n, f in report_pngs.get(r["id"], []))
        result = r["status"] + (": " + md(r["note"]) if r["note"] else "")
        L.append("| `%s.frx` %s | %s | %s | %s | %s | [[../06-reports/%s.md]] |" % (
            r["id"], REPORT_TITLE.get(r["id"], ""), r["pages"], kept or "none", md(r["how"]), result, r["id"]))
    L.append("")

    L += ["## Message boxes", ""]
    if dialogs:
        L += ["Every Win32 message box the run produced, in order, with what the runner pressed. These are the application's own texts (`include/strings.h`) or VFP's.", ""]
        L += ["| # | Time | Title | Text | Buttons | Pressed | Image |", "|---|---|---|---|---|---|---|"]
        for d in dialogs:
            L.append("| %s | %s | %s | %s | %s | %s | [`%s`](%s%s) |" % (
                d["seq"], d["time"], md(d["title"]), md(d["text"]), md(d["buttons"]), md(d["pressed"]),
                d["file"].split("\\")[-1], REL, d["file"].replace("\\", "/")))
        L.append("")
    else:
        L += ["None. No message box appeared during the run.", ""]

    L += ["## Errors during the run", ""]
    if err_rows or errors:
        L += ["| Where | What |", "|---|---|"]
        for r in err_rows:
            L.append("| `%s` | %s |" % (md(r["id"]), md(r["note"])))
        L.append("")
    else:
        L += ["None. The harness's `ON ERROR` handler and every report's `TRY` block stayed silent.", ""]

    L += comparison(rows)
    L += ["## Findings", ""]
    L += FINDINGS
    L += ["", "## Files", ""]
    L += ["| Path | What |", "|---|---|",
          "| `baseline/forms/*.png` | One image per form window, plus page and state variants |",
          "| `baseline/screen/*.png` | The main window in each state |",
          "| `baseline/reports/<report>-pN.png` | Rendered report pages |",
          "| `baseline/dialogs/*.png` | Message boxes |",
          "| `baseline/CAPTURE-LOG.csv` | One row per capture with form name, class, caption, launch statement, file, page count, status |",
          "| `baseline/dialogs.csv` | One row per message box with title, text, buttons, and what was pressed |",
          "| `baseline/capture.log` | Timestamped narrative of the run, including every error |",
          "| `tools/baseline/` | The harness: `run_capture.ps1`, `capture.fpw`, `capture.prg`, `snap.ps1` |",
          ""]

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "README.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L))
    print("wrote", os.path.join(OUT, "README.md"), len(forms), "forms", len(screens), "screens", len(reports), "reports", len(dialogs), "dialogs")


def comparison(rows90):
    """The same run with the harness forcing SET ENGINEBEHAVIOR 70 (baseline-eb70/)."""
    base70 = os.path.join(ROOT, "baseline-eb70")
    if not os.path.exists(os.path.join(base70, "CAPTURE-LOG.csv")):
        return []
    rows70, dialogs70, log70 = load(base70)
    L = ["## The same run under `SET ENGINEBEHAVIOR 70`", ""]
    L += ["`tools/baseline/run_capture.ps1 -Engine 70 -OutDir baseline-eb70` repeats the capture with the harness forcing VFP 7's query rules before the EXE starts; "
          "the EXE itself sets nothing. The images are in `baseline-eb70/`, same layout. What changes:", ""]
    L += ["| Item | Default (90) | Forced 70 |", "|---|---|---|"]
    def by(rows, kind):
        return {r["id"]: r for r in rows if r["kind"] == kind}
    f90, f70 = by(rows90, "form"), by(rows70, "form")
    r90, r70 = by(rows90, "report"), by(rows70, "report")
    for fid in ("ordentry", "ordhist"):
        a = f90.get(fid, {}).get("status", "not captured")
        b = f70.get(fid, {}).get("status", "not captured")
        L.append("| Form `%s` | %s | %s |" % (fid, a, b))
    for rid in sorted(set(r90) | set(r70)):
        a, b = r90.get(rid), r70.get(rid)
        pa = "%s pages (%s)" % (a["pages"], a["status"]) if a else "not run"
        pb = "%s pages (%s)" % (b["pages"], b["status"]) if b else "not run"
        if pa != pb:
            L.append("| Report `%s.frx` | %s | %s |" % (rid, pa, pb))
    d90 = [d for d in read_csv(os.path.join(BASE, "dialogs.csv")) if not d["file"].replace("\\", "/").startswith("forms/")]
    d70 = [d for d in dialogs70 if not d["file"].replace("\\", "/").startswith("forms/")]
    L.append("| Message boxes | %d | %d |" % (len(d90), len(d70)))
    e90 = [r for r in rows90 if r["kind"] == "error" and r["id"] != "CAPTURE"]
    e70 = [r for r in rows70 if r["kind"] == "error" and r["id"] != "CAPTURE"]
    L.append("| Errors caught by the harness's `ON ERROR` (outside the harness itself) | %d | %d |" % (len(e90), len(e70)))
    L.append("")
    for fid in ("ordentry", "ordhist"):
        if f70.get(fid, {}).get("status") == "ok" and f90.get(fid, {}).get("status") == "ok":
            L.append("- `%s` under 70: [`%s`](../../baseline-eb70/%s)" % (fid, os.path.basename(f70[fid]["file"]), f70[fid]["file"]))
        elif f70.get(fid, {}).get("status") == "ok":
            L.append("- `%s` opens under 70: [`%s`](../../baseline-eb70/%s)" % (fid, os.path.basename(f70[fid]["file"]), f70[fid]["file"]))
    for rid in ("topcust",):
        if r70.get(rid, {}).get("status") == "ok":
            L.append("- `%s.frx` renders under 70: [`p1`](../../baseline-eb70/reports/%s-p1.png)" % (rid, rid))
    L.append("")
    return L


FINDINGS = [
    "- **The VFP 9 build cannot open Order Entry or Order History cleanly, and cannot print Top 25 Customers.** Under VFP 9's default `SET ENGINEBEHAVIOR 90`, "
    "a `GROUP BY` must name every non-aggregated column. The stored procedure `RemainingCredit` (`data/tastrade.dc2`, `GROUP BY a.order_id` with `a.freight` outside an aggregate) "
    "raises error 1807 when Order Entry opens, then three follow-on errors as it continues past the failed query; the form shows an available credit of 999,999,999.99. "
    "The `order history` view (`GROUP BY Orditems.order_id`, selecting `order_date`, `deliver_by`, `paid`) fails in the form's data environment and the form never loads "
    "(error 2005, its grid's `ControlSource` alias `cItems` missing). The `top25cust` view (`GROUP BY ordertotal.customer_id`, selecting `company_name`, `country`) fails inside "
    "`REPORT FORM` without any error reaching the harness: no pages, no message. Nothing in the source says so; the VFP 7 twins and the VFP 9 twins are the same text. "
    "See the comparison section: with the harness forcing `SET ENGINEBEHAVIOR 70` all three work.",
    "- **Two more `GROUP BY` queries of the same shape did not fail because nothing in the run reached them**: the `ordertotal` view (read only by `top25cust`) and the sales views, "
    "which group by the columns they select. `docs/09-business-logic/README.md` R-rules quote the queries; this run is the evidence of which ones VFP 9 rejects.",
    "- **The invoice prints Quantity as asterisks.** `reports/orders.frx` gives the `quantity` field the format mask `999999999.99` in a 1.17-inch box at Arial 12, which cannot hold twelve characters, so every line of every invoice shows `**********` "
    "where the quantity should be (`baseline/reports/orders-p1.png`). The layout doc lists the field and its width; only a run shows the overflow.",
    "- **The report Date field is too narrow for its own value.** The `DATE()` field in every page header is 0.68 inches wide at Arial 12, less than `09/09/26` needs, "
    "so VFP 9's engine prints `09/09…` on every page (`baseline/reports/listcat-p1.png`). The application sets no `SET CENTURY`; this is the 1990s box, not a four-digit year.",
    "- **Case Study prints nothing because no row matches its filter.** `casestdy.frx` filters `behindsc.dbf` on `screen_id = \"*Case Study\"`; none of the 65 rows has that value, "
    "so the dead report is also empty. Its form (`casestdy.scx`, launched by nothing) opens and shows the text of a `behindsc` topic (`baseline/forms/casestdy.png`).",
    "- **The Employee Listing's dialog defaults to the first title, not all.** Pressing OK on `gettitle` as opened prints the first title in the combo box (3 pages); "
    "the All Titles path was not exercised in this run.",
    "- **The run rewrites two table headers.** After every run `data/customer.dbf` and `data/orders.dbf` differ from the committed files in exactly three bytes, "
    "the header's last-update date (bytes 1 to 3, `96-05-11` and `96-06-21` to today); no record changes. Which form does it was not isolated. The runner reports it and the files are restored before commit.",
    "- **Order Entry opens on order 1 whose Ship To country is Italy for a London address** (`baseline/forms/ordentry.png`, `orders-p1.png`); the sample data, not the code.",
    "- **What the run added to the reading.** Every earlier doc softened unrun behaviour to \"errors or does nothing\". The run resolves those: the employee listing's missing `#INCLUDE` path was not reached "
    "(its dialog answered with a real title); the printer environments in the reports did not stop the listener (the saved devices do not exist here, and every report that had data rendered); "
    "the intro form, login dialog, About box, find dialogs, and every maintenance form open and close as the docs describe.",
]

if __name__ == "__main__":
    main()
