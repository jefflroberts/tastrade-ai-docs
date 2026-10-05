"""Generate docs/10-baseline/data-entry.md, the index of the data-entry capture
pass in baseline-entry/ (VFP 9 defaults) and baseline-entry-eb70/ (the harness
forcing SET ENGINEBEHAVIOR 70). Step 9.

Everything comes from the runs' own records (CAPTURE-LOG.csv, dialogs.csv,
capture.log, written by tools/baseline/run_capture.ps1 -Pass entry) and the
PNG headers; the scenario descriptions and findings are hand-written strings
here. Rerun after every capture; never hand-edit the output.
"""
import os, csv, re
import gen_baseline_docs as gb

ROOT = gb.ROOT
OUT = os.path.join(ROOT, "docs", "10-baseline")
RUNS = [("baseline-entry", "VFP 9 default (`SET ENGINEBEHAVIOR 90`)"),
        ("baseline-entry-eb70", "harness forcing `SET ENGINEBEHAVIOR 70`")]

# Scenario id -> (title, what the harness did, docs)
SCENARIOS = [
    ("customer", "Customer rule violation",
     "Open Customers (record ALFKI, minimum 2,600, maximum 6,300), put focus in Min Order Amount, set its value to 999,999 (the box still paints the stored value until it loses focus), call the form's `Save` as the toolbar does, then `Restore`.",
     "[[../04-forms/customer.md]], [[../03-data-model/tables/customer.md]] (the rule `min_order_amt <= max_order_amt`)"),
    ("shipper", "Delete refused by referential integrity",
     "Open Shippers, press Delete and answer Yes to the confirmation. Every shipper has orders and the orders-to-shippers delete rule is restrict, so the trigger refuses.",
     "[[../04-forms/shipper.md]], [[../03-data-model/README.md]] (RI rules)"),
    ("ordentry", "A new order that the rules refuse",
     "Open Order Entry, New, Save with no customer and no line (`ValOrder`: an order must have at least one line item); set customer ALFKI through the combo's `Value` (its `ProgrammaticChange` runs the same code as a pick), add the first product with quantity 1 as the product combo does, Save (below the customer's minimum of 2,600, \"Save anyway?\" answered No); under engine 70 only, customer CACTU, whose saved unpaid orders already exceed its maximum, Save (over the credit limit, answered No); then customer ALFKI with quantity 100,000 and no shipper, Save (the orders-to-shippers insert trigger refuses); Restore.",
     "[[../04-forms/ordentry.md]], [[../05-classes/orders.md]], [[../09-business-logic/README.md]] (`ValOrder`, `RemainingCredit`)"),
    ("custadd", "Add Customer with an empty ID",
     "Open Add Customer with the company name filled as Order Entry does, press OK with the Customer ID empty (the DBC rule `NOT EMPTY(customer_id)`), then Cancel.",
     "[[../04-forms/custadd.md]]"),
    ("chngpswd", "Change Password: correct old password, mismatched confirmation",
     "Type the old password (copied from the form's own Hint box, which shows it), a new password and a different confirmation, press OK, then Cancel.",
     "[[../04-forms/chngpswd.md]]"),
    ("chngpswd-empty", "Change Password: OK with nothing entered",
     "Press OK with every box empty; the form asks whether to abandon; No closes it.",
     "[[../04-forms/chngpswd.md]]"),
    ("loginpicture", "Login with a wrong password",
     "Type a wrong password for the first employee and press OK. (The shipped build never shows this form: `DEBUGMODE` skips the login.)",
     "[[../05-classes/login.md]]"),
    ("listempl", "Employee Listing: the title dialog",
     "Run the report; in its title dialog the runner presses Down, then Enter. The click-through pass pressed Enter alone.",
     "[[../06-reports/listempl.md]], [[../04-forms/gettitle.md]]"),
]


def rel(run, f):
    return "../../%s/%s" % (run, f.replace("\\", "/"))


def main():
    runs = {}
    for run, label in RUNS:
        base = os.path.join(ROOT, run)
        if not os.path.exists(os.path.join(base, "CAPTURE-LOG.csv")):
            continue
        rows, dialogs, log = gb.load(base)
        runs[run] = (label, rows, dialogs, log)
    if not runs:
        raise SystemExit("no entry runs found")

    L = ["# Data-entry capture", ""]
    first_run = next(iter(runs.values()))
    L += ["The second capture pass (Step 9): the same harness as [[README.md]], run with `-Pass entry`, drives the forms through the paths a click-through cannot reach: "
          "a field rule violated on Save, a delete the referential-integrity trigger refuses, a new order refused four times, an Add Customer with no ID, "
          "Change Password twice, a wrong login password, and the employee listing's title dialog. Nothing is saved: every path ends in a refusal or a Restore, and the data files were checked "
          "against the committed ones afterwards. Run on %s; images in `baseline-entry/` and `baseline-entry-eb70/`." % first_run[3][0][:10], ""]
    L += ["**Related docs:** [[README.md]] (the click-through baseline), [[save.md]] (the successful-save pass), [[../04-forms/README.md]], [[../09-business-logic/README.md]], [[../01-architecture/startup.md]].", ""]
    L += ["## Runs", "", "| Folder | Engine | Form images | Report pages | Message boxes | Errors caught by `ON ERROR` |", "|---|---|---|---|---|---|"]
    for run, (label, rows, dialogs, log) in runs.items():
        forms = [r for r in rows if r["kind"] == "form" and r["status"] == "ok"]
        pages = len([n for n in os.listdir(os.path.join(ROOT, run, "reports")) if n.endswith(".png")])
        mb = [d for d in dialogs if not d["file"].replace("\\", "/").startswith("forms/")]
        errs = [r for r in rows if r["kind"] == "error" and r["id"] != "CAPTURE"]
        L.append("| `%s/` | %s | %d | %d | %d | %d |" % (run, label, len(forms), pages, len(mb), len(errs)))
    L.append("")

    for sid, title, what, docs in SCENARIOS:
        L += ["## %s" % title, "", what, "", "Docs: %s." % docs, ""]
        for run, (label, rows, dialogs, log) in runs.items():
            L += ["### %s" % label, ""]
            mine = [r for r in rows if r["kind"] in ("form", "driver") and gb.base_id(r["id"]).split("-")[0] == sid.split("-")[0]
                    and (r["id"] == sid or r["id"].startswith(sid + "-"))]
            if sid == "chngpswd":
                mine = [r for r in mine if not r["id"].startswith("chngpswd-empty")]
            reps = [r for r in rows if r["kind"] == "report" and r["id"] == sid]
            if not mine and not reps:
                L += ["Not run.", ""]
                continue
            L += ["| Image | State | Size |", "|---|---|---|"]
            for r in mine:
                if r["kind"] == "driver":
                    L.append("| (none) | %s | %s |" % (gb.md(r["note"]), r["status"]))
                elif r["status"] != "ok" or not r["file"]:
                    L.append("| (none) | %s | %s: %s |" % (gb.md(r["how"]), r["status"], gb.md(r["note"])))
                else:
                    L.append("| [`%s`](%s) | %s | %s×%s |" % (r["file"].split("/")[-1], rel(run, r["file"]), gb.md(r["how"]), r["w"], r["h"]))
            for r in reps:
                pngs = sorted(n for n in os.listdir(os.path.join(ROOT, run, "reports")) if n.startswith(sid + "-p"))
                kept = ", ".join("[%s](%s)" % (n.split("-")[-1][:-4], rel(run, "reports/" + n)) for n in pngs)
                L.append("| %s | %s pages, %s | %s |" % (kept or "(none)", r["pages"], r["status"], gb.md(r["note"]) or gb.md(r["how"])))
            L.append("")
            # message boxes between this scenario's first and last log time
            times = [t for t in (r.get("seq") for r in mine + reps)]
            L += dialog_rows(run, dialogs, log, sid)

    L += ["## Findings", ""]
    L += FINDINGS
    L.append("")
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "data-entry.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L))
    print("wrote data-entry.md for", list(runs))


def dialog_rows(run, dialogs, log, sid):
    """Message boxes that appeared while the scenario's step was running, by log time."""
    # step boundaries from capture.log: "step N kind id" lines
    steps = [(l[:19], l) for l in log if re.search(r" step \d+ ", l)]
    start = end = None
    for i, (t, l) in enumerate(steps):
        if re.search(r" step \d+ \S+ %s$" % re.escape(sid), l):
            start = t[11:19]
            end = steps[i + 1][0][11:19] if i + 1 < len(steps) else "99:99:99"
            break
    if start is None:
        return []
    mine = [d for d in dialogs if start <= d["time"] < end]
    if not mine:
        return ["No message box.", ""]
    L = ["| # | Time | Title | Text | Buttons | Pressed | Image |", "|---|---|---|---|---|---|---|"]
    for d in mine:
        L.append("| %s | %s | %s | %s | %s | %s | [`%s`](%s) |" % (
            d["seq"], d["time"], gb.md(d["title"]), gb.md(d["text"]), gb.md(d["buttons"]), gb.md(d["pressed"]),
            d["file"].split("\\")[-1], rel(run, d["file"])))
    L.append("")
    return L


FINDINGS = [
    "- **Every rule and trigger the scenarios aimed at refused the change, and nothing was saved.** After each run the only bytes that differ from the committed data are the "
    "header stamps of five tables and the order-number counter in `setup.dbf` (see below); the runner reports them and they are restored before commit.",
    "- **The customer rule fires, the message shows, and `Save()` still returns `.T.`** The form's `WriteBuffer` `REPLACE`s the typed value, the DBC rule "
    "(`min_order_amt <= max_order_amt`) raises 1582, the form's `Error` shows the rule text, and the field keeps its old value; `Save` then finds nothing changed and reports success "
    "(`capture.log`: `Save() returned .T.`). A caller cannot tell a refused edit from a saved one.",
    "- **Every abandoned new order consumes an order number.** `AddNew` fires the DBC default `newid()`, which increments the counter in `setup.dbf` at once and permanently: "
    "the counter went from 1138 to 1139 in each run although the order was reverted. This is the mechanism behind the counter standing 59 above the number of orders "
    "([[../02-domain/README.md]]): 59 orders were started and not saved.",
    "- **The credit check counts saved unpaid orders only.** `RemainingCredit` reads `orders` through a second alias, so the order being saved is not in the sum; a first order of any size passes. "
    "The over-credit prompt appears only for a customer already over the limit before the order: 2 of 92 are (CACTU by 12,228.34; ANTON by 1,777,500), and CACTU produced it under engine 70 "
    "(`baseline-entry-eb70/dialogs/06.png`). The prompt's text misspells maximum (`CUSTOVERMAX_LOC` in `include/strings.h`).",
    "- **Under VFP 9's default engine the order rule degrades with every attempt.** Each `Save` runs `ValOrder`, which calls `RemainingCredit`; its `GROUP BY` fails (1807), the procedure "
    "runs on into three more errors, `ValOrder` itself then errors four times on the undefined result (lines 138 to 146), and the alias `_orders` it opened is left open, so the next call "
    "fails with `Alias name is already in use` and later with `Alias '_ORDERS' is not found`. The order scenario's three saves produced 90 of the run's 97 message boxes; its four saves under engine 70 produced 4 of 11. "
    "The below-minimum prompt alone appeared ten times under 90 and once under 70.",
    "- **The order form calls its `Error` method with the message where the method name belongs.** `orderentry.save` passes `Error(laError[1], laError[2], 0)`; the dialog reads "
    "`Method: Operator/operand type mismatch. Line: 0` (`baseline-entry/dialogs/35.png`). Only a failing save shows it, so only the engine-90 run has it.",
    "- **Setting the customer through the combo's `Value` leaves the previous customer's ship-to address.** `ProgrammaticChange` and `InteractiveChange` run the same two lines "
    "(credit, `RefreshCustomerInfo`), and `RefreshCustomerInfo` copies from the `customer` alias wherever it is positioned; after CACTU was set, the form showed Cactus Comidas with "
    "Alfreds Futterkiste's address (`baseline-entry-eb70/forms/ordentry-filled-over.png`). A user's pick from the list was not exercised; whether the base combo repositions the alias on that path is not shown here.",
    "- **The Employee Listing prints every title unless the combo is changed interactively.** The dialog's `cTitle` defaults to `ALL` and is set only by the combo's `InteractiveChange` "
    "or the checkbox; `Init` selects the first title programmatically, so the box shows one title while OK prints all (3 pages, every run: Enter alone in the click-through pass, "
    "Down then Enter here). One earlier run's Space then Enter printed a single title and a repeat of the same keys left the dialog open; the keystroke path is not deterministic from outside, "
    "and the finding rests on the twin (`forms/gettitle.sc2`, `ctitle = ALL`, `cboTitle.ListIndex = 1` in `Init`).",
    "- **The employee listing's \"nothing to print\" branch, the one with the missing `#INCLUDE`, is unreachable through the interface.** The combo lists only titles that employees have, "
    "so a title with no employees cannot be chosen; the latent error documented in [[../06-reports/listempl.md]] needs a data change to reach.",
    "- **The login's wrong-password box has no title of its own**: `MESSAGEBOX(BADPASSWORD_LOC, MB_ICONEXCLAMATION)` shows `Microsoft Visual FoxPro` as the caption where every other message shows `Tasmanian Traders` (`baseline-entry/dialogs/97.png`).",
    "- **Add Customer with an empty ID, the mismatched password confirmation, the empty password dialog, and the refused shipper delete all behave as their docs say**, with the "
    "texts `Customer ID cannot be empty.`, `Cannot confirm new password. Please try again.`, `You have not yet entered the old password. Do you want to continue?`, and "
    "`Shipper exists on orders. Cannot delete!` (`aErrorMsg` from the RI delete trigger).",
]

if __name__ == "__main__":
    main()
