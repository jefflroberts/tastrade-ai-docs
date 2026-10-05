"""Generate docs/10-baseline/save.md, the index of the successful-save capture
pass in baseline-save/ (VFP 9 defaults) and baseline-save-eb70/ (the harness
forcing SET ENGINEBEHAVIOR 70). Step 10.

Everything comes from the runs' own records (CAPTURE-LOG.csv, dialogs.csv,
capture.log, written by tools/baseline/run_capture.ps1 -Pass save), the PNG
headers, and data-diff.txt (a byte-level diff of data/ against the committed
files, written before the data was restored). Scenario descriptions and
findings are hand-written strings here. Rerun after every capture; never
hand-edit the output.
"""
import os
import gen_baseline_docs as gb
import gen_entry_docs as ge

ROOT = gb.ROOT
OUT = os.path.join(ROOT, "docs", "10-baseline")
RUNS = [("baseline-save", "VFP 9 default (`SET ENGINEBEHAVIOR 90`)"),
        ("baseline-save-eb70", "harness forcing `SET ENGINEBEHAVIOR 70`")]

SCENARIOS = [
    ("customer", "A customer edit saved",
     "Open Customers (ALFKI), put focus in Contact Title, set it to Baseline Reviewer, call the form's `Save` as the toolbar does.",
     "[[../04-forms/customer.md]], [[../05-classes/tsbase.md]] (`save`)"),
    ("custadd", "A new customer saved",
     "Open Add Customer with the company name filled as Order Entry does, set the ID to BASEL, a contact, maximum 5,000 and minimum 0, press OK (`TABLEUPDATE`, then the form releases itself).",
     "[[../04-forms/custadd.md]]"),
    ("ordentry", "A new order saved, and one filled from Order History",
     "Open Order Entry, New, customer ALFKI (maximum 6,300, minimum 2,600, no unpaid orders), one line of Chai at 18.00 times 150 (2,646 after the 2% discount), shipper 1, Save. "
     "Under engine 70 only: New again, ALFKI, Last Order (which opens Order History linked to this form), tag the first line of the order shown, Add to Current Order, shipper 1, Save; Restore if refused.",
     "[[../04-forms/ordentry.md]], [[../04-forms/ordhist.md]], [[../05-classes/orders.md]], [[../09-business-logic/README.md]]"),
    ("ordhist", "Order History linked from Order Entry",
     "Opened by the Last Order button of the scenario above (engine 70 only; the form does not open under the default engine).",
     "[[../04-forms/ordhist.md]]"),
    ("chngpswd", "A password changed",
     "Type the old password (from the form's own Hint box), the same new password and confirmation (baseline), press OK (`REPLACE`, `TABLEUPDATE`, release).",
     "[[../04-forms/chngpswd.md]]"),
    ("loginpicture", "A login that succeeds",
     "Type the password just set and press OK; the form hides and `DoFormRetVal` returns the employee id and user level. (The shipped build never shows this form: `DEBUGMODE` skips the login.)",
     "[[../05-classes/login.md]]"),
    ("customer-delete", "A customer deleted",
     "Open Customers, position on BASEL (added above; it has no orders, so the referential rule allows the delete), press Delete and answer Yes.",
     "[[../04-forms/customer.md]], [[../03-data-model/README.md]] (RI rules)"),
]


def main():
    runs = {}
    for run, label in RUNS:
        base = os.path.join(ROOT, run)
        if not os.path.exists(os.path.join(base, "CAPTURE-LOG.csv")):
            continue
        rows, dialogs, log = gb.load(base)
        diff = ""
        dp = os.path.join(base, "data-diff.txt")
        if os.path.exists(dp):
            diff = open(dp, encoding="utf-8-sig").read().strip()
        runs[run] = (label, rows, dialogs, log, diff)
    if not runs:
        raise SystemExit("no save runs found")

    first = next(iter(runs.values()))
    L = ["# Successful-save capture", ""]
    L += ["The third capture pass (Step 10): the same harness as [[README.md]] and [[data-entry.md]], run with `-Pass save`, takes the paths that write: "
          "a customer edit, a new customer, a new order, an order filled from Order History, a password change and the login that uses it, and a delete. "
          "The data was diffed byte by byte against the committed files after each run (`data-diff.txt` in each folder, quoted below) and then restored from git. "
          "Run on %s; images in `baseline-save/` and `baseline-save-eb70/`." % first[3][0][:10], ""]
    L += ["**Related docs:** [[README.md]], [[data-entry.md]], [[../04-forms/README.md]], [[../09-business-logic/README.md]], [[../02-domain/README.md]].", ""]
    L += ["## Runs", "", "| Folder | Engine | Form images | Message boxes | Errors caught by `ON ERROR` |", "|---|---|---|---|---|"]
    for run, (label, rows, dialogs, log, diff) in runs.items():
        forms = [r for r in rows if r["kind"] == "form" and r["status"] == "ok"]
        mb = [d for d in dialogs if not d["file"].replace("\\", "/").startswith("forms/")]
        errs = [r for r in rows if r["kind"] == "error" and r["id"] != "CAPTURE"]
        L.append("| `%s/` | %s | %d | %d | %d |" % (run, label, len(forms), len(mb), len(errs)))
    L.append("")

    L += ["## What the data files show afterwards", ""]
    L += ["`dbfdiff` over `data/` against the committed files, before the restore. Three differing bytes at the start of a file are the header's last-update stamp; "
          "a record count that grew is a saved row; a record's bytes are the edit.", ""]
    for run, (label, rows, dialogs, log, diff) in runs.items():
        L += ["### %s" % label, "", "```", diff or "(no data-diff.txt)", "```", ""]

    for sid, title, what, docs in SCENARIOS:
        L += ["## %s" % title, "", what, "", "Docs: %s." % docs, ""]
        for run, (label, rows, dialogs, log, diff) in runs.items():
            L += ["### %s" % label, ""]
            if sid == "customer-delete":
                mine = [r for r in rows if r["kind"] == "form" and r["id"] in ("customer-positioned", "customer-deleted")]
            elif sid == "customer":
                mine = [r for r in rows if r["kind"] == "form" and r["id"] in ("customer-before", "customer-saved")]
            else:
                mine = [r for r in rows if r["kind"] in ("form", "driver") and (r["id"] == sid or r["id"].startswith(sid + "-"))]
            if not mine:
                L += ["Not run.", ""]
                continue
            L += ["| Image | State | Size |", "|---|---|---|"]
            for r in mine:
                if r["kind"] == "driver":
                    L.append("| (none) | %s | %s |" % (gb.md(r["note"]), r["status"]))
                elif r["status"] != "ok" or not r["file"]:
                    L.append("| (none) | %s | %s: %s |" % (gb.md(r["how"]), r["status"], gb.md(r["note"])))
                else:
                    L.append("| [`%s`](%s) | %s | %s×%s |" % (r["file"].split("/")[-1], ge.rel(run, r["file"]), gb.md(r["how"]), r["w"], r["h"]))
            L.append("")
            L += ge.dialog_rows(run, dialogs, log, sid.split("-")[0] if sid != "customer-delete" else "customer")
            # log lines with the save results for this scenario
            key = {"customer": "customer:", "ordentry": "order:", "customer-delete": "customer: Delete", "loginpicture": "driver loginpicture"}.get(sid)
            if key:
                hits = [l[20:] for l in log if key in l]
                if hits:
                    L += ["Log:", ""] + ["- `%s`" % gb.md(h) for h in hits] + [""]

    L += ["## Findings", ""]
    L += FINDINGS
    L.append("")
    with open(os.path.join(OUT, "save.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L))
    print("wrote save.md for", list(runs))


FINDINGS = [
    "- **Under `SET ENGINEBEHAVIOR 70` every one of the six paths saved, and the data files show exactly the intended rows and nothing else.** The Contact Title of ALFKI "
    "changed (`customer.dbf` record 1); a new customer BASEL was appended (record 93, maximum 5,000); order 1138 was appended (`orders.dbf`) with its one Chai line "
    "(`orditems.dbf`, unit price 18.00, quantity 150); the order copied through Order History was appended as order 1139 with the same historical line; employee 1's "
    "password changed from `Buck` to `baseline` (`employee.dbf`); and BASEL was marked deleted. Apart from those, only the header stamps and the ID counter moved. "
    "This is the run that shows the documentation's schema and rules describing a working application, not a broken one.",
    "- **Under VFP 9's default engine a refused order save still writes the order header.** `orderentry.save` returned `.F.` (the order was reported not saved, and the "
    "below-minimum prompt was answered No), yet `orders.dbf` gained a fully populated order 1138 (customer ALFKI, shipper, ship-to block) with **no** matching line item in "
    "`orditems.dbf`. The save runs inside `BEGIN TRANSACTION ... ROLLBACK`, but the `GROUP BY` errors in `RemainingCredit` and `ValOrder` (the same cascade as [[data-entry.md]]) "
    "leave the header committed and the lines not: a dangling order the application believes it did not create. The other five paths saved under the default engine as well; "
    "only the order is affected, because only its rule runs the failing query.",
    "- **The below-minimum prompt under the default engine names the wrong amount.** For ALFKI (minimum 2,600) it read \"Customer order total must be at least $500.00\" "
    "(`baseline-save/dialogs`), because the minimum is computed on the state the erroring `RemainingCredit`/`ValOrder` left behind. Under engine 70 the same order does not "
    "trip the prompt at all (2,646 clears the 2,600 minimum) and saves.",
    "- **Change Password edits the first employee, and the change is real.** With the shipped `DEBUGMODE` there is no login, so no employee is chosen; Change Password wrote "
    "employee record 1 (Buchanan), whose password went from `Buck` to `baseline`. The login scenario then chose Buchanan and signed in with `baseline` and succeeded "
    "(`DoFormRetVal` returned the id and level), so the whole password round trip is confirmed against the data, not just asserted from [[../04-forms/chngpswd.md]].",
    "- **Every new order consumes an ID counter step whatever the outcome.** The counter in `setup.dbf` went 1138 to 1139 under the default engine (one order, not cleanly saved) "
    "and 1138 to 1140 under engine 70 (two orders saved); the order number equals the counter at `AddNew`, so the sequence is contiguous only when no order is ever abandoned. "
    "This is the same mechanism [[data-entry.md]] found from the abandoned orders, seen here from saved ones.",
    "- **Delete marks the record in place.** After `Delete()` of BASEL succeeded, `customer.dbf` still holds record 93 with its deletion flag set to `*`; the row is hidden and its "
    "space reusable, not removed, until a pack. The form moved to the next customer (`baseline-save/forms/customer-deleted.png`).",
    "- **The just-saved order appears in Order History at once, and the copy keeps the old price.** Opening Order History from Last Order showed order 1138 already in the grid with a "
    "current balance of 2,646; tagging its line and Add to Current Order copied the line into order 1139 at the stored unit price of 18.00, not a re-read of the current product price, "
    "as [[../04-forms/ordhist.md]] describes. Order History opens only under engine 70; under the default engine its view is one of the three that fail.",
]

if __name__ == "__main__":
    main()
