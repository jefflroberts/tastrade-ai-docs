"""Generate docs/06-reports/*.md and its index from the thirteen .fr2 twins.

Structure (bands, objects, coordinates, expressions, cursors, DE code, printer
environment) comes from foxparse.parse_fr2; purpose, notes, and launch points
are hand-written strings below, each checked against a grep of the twins.
Rerun after editing; never hand-edit the output.
"""
import os, sys, textwrap
sys.path.insert(0, os.environ.get("VFP_TOOLKIT_TOOLS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "vfp-documentation-toolkit", "tools")))
import foxparse as fp

ROOT = os.environ.get("TASTRADE_ROOT", os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))
OUT = os.path.join(ROOT, "docs", "06-reports")
os.makedirs(OUT, exist_ok=True)


def inch(v):
    v = float(v) / 10000
    return "%.2f" % (0.0 if abs(v) < 0.005 else v)


def fence(code):
    return "```foxpro\n" + code + "\n```"


def unq(v):
    v = (v or "").strip()
    return v[1:-1] if len(v) >= 2 and v[0] == v[-1] == '"' else v


def font(r):
    p = r["props"]
    face = p.get("fontface", "")
    if not face:
        return ""
    style = int(p.get("fontstyle", 0) or 0)
    bits = [n for b, n in ((1, "bold"), (2, "italic"), (4, "underline")) if style & b]
    s = "%s %s" % (face, p.get("fontsize", ""))
    if bits:
        s += " " + " ".join(bits)
    rgb = (int(r["penred"] or 0), int(p.get("pengreen", 0) or 0), int(p.get("penblue", 0) or 0))
    if rgb not in ((0, 0, 0), (-1, -1, -1)) and -1 not in rgb:
        s += ", RGB(%d,%d,%d)" % rgb
    return s


def options(r):
    p = r["props"]; o = []
    ot = r["objtype"]
    if p.get("stretch") == ".T.":
        o.append("stretch")
    if p.get("float") == ".T.":
        o.append("float")
    if ot in (5, 8) and p.get("offset") == "1":
        o.append("right-aligned")
    if ot in (5, 8) and p.get("offset") == "2":
        o.append("centred")
    if ot == 8:
        tt = int(p.get("totaltype", 0) or 0)
        rt = int(p.get("resettotal", 0) or 0)
        if tt:
            o.append("calculate %s, reset %s" % (fp.TOTALTYPE[tt].lower(), fp.reset_name(rt).lower()))
        if p.get("norepeat") == ".T.":
            o.append("no repeated values")
        if p.get("supvalchng") == ".T.":
            o.append("print-when flags changed (`supvalchng`)")
    if ot == 17:
        o.append({"0": "file", "1": "General field", "2": "expression"}.get(p.get("offset", "0"), ""))
        o.append({"0": "clip", "1": "scale, keep shape", "2": "scale, stretch"}.get(p.get("general", "0"), ""))
    if r["supexpr"]:
        o.append("print when `%s`" % r["supexpr"])
    if r["comment"] and r["comment"].strip():
        o.append("comment \"%s\"" % r["comment"].strip())
    return "; ".join(x for x in o if x)


def content(r):
    ot = r["objtype"]
    if ot == 5:
        return '"%s"' % unq(r["expr"]).replace("\n", "\\n")
    if ot == 8:
        return "`%s`" % r["expr"]
    if ot == 17:
        return ("picture `%s`" % unq(r["picture"])) if r["picture"] else ("picture from field `%s`" % r["name"])
    if ot == 6:
        return "line"
    if ot == 7:
        p = r["props"]
        fill = "grey fill" if p.get("fillpat", "0") != "0" and p.get("fillred") == "192" else "box"
        return fill if fill != "box" else "box"
    return r["kind"]


def fmt(r):
    if r["objtype"] == 8 and r["picture"]:
        return "`%s`" % unq(r["picture"])
    return ""


def band_section(b):
    L = []
    title = "### %s (%s in)" % (b["band"], inch(b["height"]))
    L += [title, ""]
    flags = []
    if b["group_expr"]:
        flags.append("group on `%s`" % b["group_expr"])
    for k, n in (("pagebreak", "new page for each group"), ("colbreak", "`colbreak`"), ("resetpage", "page number reset per group"),
                 ("norepeat", "`norepeat`"), ("swapheader", "`swapheader`"), ("swapfooter", "`swapfooter`"),
                 ("ejectbefor", "eject before"), ("ejectafter", "eject after")):
        if b["props"].get(k) == ".T.":
            flags.append(n)
    if flags:
        L += ["Band flags: " + "; ".join(flags) + ".", ""]
    if not b["objects"]:
        L += ["Empty.", ""]
        return L
    L += ["| Kind | Top, left (in) | Size w×h (in) | Content | Format | Font | Options |", "|---|---|---|---|---|---|---|"]
    for r in b["objects"]:
        L.append("| %s | %s, %s | %s×%s | %s | %s | %s | %s |" % (
            r["kind"].replace(" expression", ""), inch(r["vpos"] - b["start"]), inch(r["hpos"]),
            inch(r["width"]), inch(r["height"]), content(r), fmt(r), font(r), options(r)))
    L.append("")
    return L


def head(stem, title, purpose, used_by, related):
    return ["# %s (%s.frx)" % (title, stem), "", "| Source file | Type | Path |", "|---|---|---|",
            "| `%s.frx` | Report | `reports/%s.fr2` |" % (stem, stem), "", "**Purpose:** " + purpose, "",
            "**Used by:**"] + ["- " + u for u in used_by] + ["", "**Related docs:** " + related, ""]


def de_section(r, extra, explain):
    L = ["## DataEnvironment", ""]
    p = r["de_props"]
    bits = []
    if p.get("autoopentables", "").upper() == ".F.":
        bits.append("`AutoOpenTables = .F.`")
    if p.get("autoclosetables", "").upper() == ".F.":
        bits.append("`AutoCloseTables = .F.`")
    if p.get("initialselectedalias"):
        bits.append("`InitialSelectedAlias = \"%s\"`" % p["initialselectedalias"])
    if r["cursors"]:
        L += ["| Cursor | Alias | Source | Database | Filter |", "|---|---|---|---|---|"]
        for c in r["cursors"]:
            L.append("| `%s` | `%s` | `%s` | %s | %s |" % (c["object"], c["alias"], c["table"],
                                                          ("`%s`" % c["database"]) if c["database"] else "",
                                                          ("`%s`" % c["filter"]) if c["filter"] else ""))
        L.append("")
    else:
        L += ["No cursors.", ""]
    if bits:
        L += ["Properties: " + ", ".join(bits) + ".", ""]
    if extra:
        L += [extra, ""]
    for name, body in r["de_methods"].items():
        L += ["DataEnvironment `%s`:" % name, ""]
        if explain.get(name):
            L += [explain[name], ""]
        L += [fence(textwrap.dedent(body).strip("\n")), ""]
    return L


def variables_section(r):
    L = ["## Report variables", ""]
    if not r["variables"]:
        return L + ["None.", ""]
    L += ["| Name | Value to store | Initial value | Calculate | Reset | Release after report |", "|---|---|---|---|---|---|"]
    for v in r["variables"]:
        L.append("| `%s` | `%s` | `%s` | %s | %s | %s |" % (v["name"], v["expr"], v["initial"], v["calculate"] or "nothing",
                                                          v["reset"], "yes" if v["release_after_report"] else "no"))
    return L + [""]


PAPER = {"1": "1 (Letter)", "9": "9 (A4)"}


def page_section(r, note):
    P = r["printer"]
    L = ["## Page setup", ""]
    L.append("- Orientation: %s" % ({"1": "portrait", "2": "landscape"}.get(P.get("ORIENTATION"), "not stored (`ORIENTATION=0`, printer default)")))
    L.append("- Paper size: %s; copies: %s%s" % (PAPER.get(P.get("PAPERSIZE"), P.get("PAPERSIZE")), P.get("COPIES", "?"),
                                                 ("; duplex %s" % P["DUPLEX"]) if "DUPLEX" in P else ""))
    if "PRINTQUALITY" in P:
        L.append("- Print quality: %s dpi" % P["PRINTQUALITY"])
    L.append("- Saved printer environment: driver `%s`, device `%s`, output `%s`" % (P.get("DRIVER"), P.get("DEVICE"), P.get("OUTPUT")))
    dn = P.get("DEVNAMES")
    if dn and (dn["device"] != P.get("DEVICE") or dn["output"] != P.get("OUTPUT")):
        L.append("- The binary DEVNAMES block disagrees: driver `%s`, device `%s`, output `%s`" % (dn["driver"], dn["device"], dn["output"]))
    L += ["", note, ""]
    return L


def notes(items):
    return ["## Notes", ""] + ["- " + i for i in items] + [""]


PICKER = "The report picker [[../04-forms/reports.md]] (`frmreports`, from the File menu's \"Print Reports ...\"), row `%s` / \"%s\" of type `%s` in `data/repolist.dbf`."
PICKER_TRIG = ["`forms/reports.sc2` `cmdRun.Click`: `REPORT FORM (lcSeleRepo) PREVIEW`, or `TO PRINTER NOCONSOLE` after `PRINTSTATUS()`, or `TO FILE <stem>.TXT ASCII`, where `lcSeleRepo` is `REPORTS\\%s.FRX`.",
               "The ASCII output drops lines, boxes, and pictures."]
PRN_MS = "**NOTE:** the saved environment names `\\\\MSPRINT32`, a Microsoft print server from the 1990s, with an IP address in the 157.56 range. VFP tries the saved printer first when the report runs."
PRN_LOCAL = "**NOTE:** the saved environment names `LaserNT`, a printer on the original author's machine; VFP tries it first when the report runs."
LOGO = "The page header carries the sample's wordmark (four labels: a blue 24-point \"T\" before \"asmanian\" and before \"raders\"), the logo bitmap `bitmaps/ttradesm.bmp` (present in the repo), and Page / Date fields."
UNITPRICE = "**NOTE:** `sum_unit_price` is the view's `SUM(unit_price)`: unit price summed without quantity, discount, or freight (see the view note in [[../03-data-model/README.md]]). The figures this report labels \"Sales\" are not order totals; [[topcust.md]] uses the full formula, so the two disagree."


def load(stem):
    return fp.parse_fr2(os.path.join(ROOT, "reports", stem + ".fr2"))


def listing(stem, title, view, view_doc_note, purpose, extra_notes, de_extra="", trig=None):
    r = load(stem)
    L = head(stem, title, purpose,
             [PICKER % (stem.upper(), title, "LIST")],
             "[[../03-data-model/README.md]] (`%s` view), %s[[../04-forms/reports.md]], [[README.md]]." % (view, view_doc_note))
    L += de_section(r, de_extra, {})
    L += ["## Bands & content", "", LOGO, ""]
    for b in r["bands"]:
        L += band_section(b)
    L += variables_section(r)
    L += page_section(r, PRN_MS)
    L += ["## Triggered from", ""] + ["- " + (t % stem.upper() if "%s" in t else t) for t in (trig or PICKER_TRIG)] + [""]
    L += notes(extra_notes)
    return "\n".join(L)


# ------------------------------------------------------------------ listings
def gen_listcat():
    return listing("listcat", "Category Listing", "CATEGORY LISTING", "[[../03-data-model/tables/category.md]], ",
                   "Prints every product category with its description and picture, from the `CATEGORY LISTING` view.",
                   ["**Only listing with a picture.** The detail band is 1.94 in tall to hold the picture object, whose source is the view's `picture` General field (`offset = 1`), scaled to keep its shape. The picker's \"To File\" ASCII option cannot print it.",
                    "**`Description` does not stretch**: a 3.55 × 1.71 in box with `float` but no `stretch`, so a long memo is clipped. `category_name` does stretch.",
                    "The view carries no `ORDER BY`, so categories print in table order."])


def gen_listcust():
    return listing("listcust", "Customer Listing", "CUSTOMER LISTING", "[[../03-data-model/tables/customer.md]], ",
                   "Prints company name, contact name, and phone for every customer, from the `CUSTOMER LISTING` view (ordered by company then contact).",
                   ["**Twin of [[listsupp.md]]**: same bands, fonts, and columns; the supplier version places its columns a little differently and has a 0.18 in page footer instead of none.",
                    "All three columns `float` and `stretch`."])


def gen_listsupp():
    return listing("listsupp", "Supplier Listing", "SUPPLIER LISTING", "[[../03-data-model/tables/supplier.md]], ",
                   "Prints company name, contact name, and phone for every supplier, from the `SUPPLIER LISTING` view (ordered by company then contact).",
                   ["**Twin of [[listcust.md]]**, see the note there."])


def gen_listship():
    return listing("listship", "Shipper Listing", "SHIPPER LISTING", "[[../03-data-model/tables/shippers.md]], ",
                   "Prints the company name of every shipper, from the `SHIPPER LISTING` view (ordered by name).",
                   ["**One column.** The smallest report in the sample: a page header, a single 4.67 in field, and an empty 0.50 in page footer.",
                    "The detail field neither floats nor stretches; every other listing's columns at least `float`."])


def gen_listprod():
    return listing("listprod", "Product Listing", "PRODUCT LISTING", "[[../03-data-model/tables/products.md]], ",
                   "Prints product name, quantity per unit, unit price, and unit cost for every product, from the `PRODUCT LISTING` view (ordered by name then quantity).",
                   ["**Prints cost next to price.** `unit_cost` is on the same listing as `unit_price`; there is no user-level check on the picker, so anyone who can print can see margins.",
                    "**Currency masks `99999.99`** on both money columns, so values of 100,000 or more cannot display in full."])


def gen_listempl():
    r = load("listempl")
    L = head("listempl", "Employee Listing",
             "Prints employees grouped by title (name, extension, notes) from the `EMPLOYEE LISTING` view, after asking which title to print through the `gettitle` dialog.",
             [PICKER % ("LISTEMPL", "Employee Listing", "LIST")],
             "[[../04-forms/gettitle.md]] (the parameter dialog), [[../03-data-model/README.md]] (`EMPLOYEE LISTING` view), [[../03-data-model/tables/employee.md]], [[../04-forms/reports.md]], [[README.md]].")
    L += ["One of two reports whose data environment runs a form before opening its tables (the other is [[orders.md]]). `AutoOpenTables` is off so `Init` can collect the parameter first; the view's `?cTitle` is then satisfied by the private variable that `DO FORM ... TO cTitle` created.", ""]
    L += de_section(r, "", {
        "Init": "Runs the title dialog, maps \"ALL\" to an empty string (which matches every title under the default `SET ANSI OFF` comparison), opens the view, and refuses to print when it returns no rows. **NOTE:** `NOTHINGTOPRINT_LOC`, `TASTRADE_LOC`, and `MB_ICONEXCLAMATION` are `#DEFINE`s from `include/tastrade.h`, but this code has no `#INCLUDE` (compare [[orders.md]], which has one). The compiled code in `reports/listempl.frt` still carries the three names and not the strings, so the message box line refers to three undefined variables: when no employee has the chosen title the report errors instead of saying \"Nothing to print.\" **NOTE:** `WEXIST(\"Project Manager\")` switches to `HOME() + \"Samples\\Tastrade\\\"`, a path that assumes the sample sits under the VFP install folder.",
        "Destroy": ""})
    L += ["## Bands & content", "", LOGO, ""]
    for b in r["bands"]:
        L += band_section(b)
    L += variables_section(r)
    L += page_section(r, PRN_MS)
    L += ["## Triggered from", ""] + ["- " + (t % "LISTEMPL" if "%s" in t else t) for t in PICKER_TRIG] + [""]
    L += notes(["**Group header prints `Title`** in navy bold; the group footer has zero height. The view orders by title, so the grouping works.",
                "**Detail name expression** `trim(last_name)+', ' + first_name`; `notes` is a memo printed with `stretch`.",
                "**The Cancel path** returns `.F.` from `Init`, which cancels the report silently; the picker shows nothing.",
                "`*=REQUERY()` is a commented-out leftover.",
                "`DEFAULTSOURCE=265` in the printer environment (a driver-specific paper tray) versus 7 in the other listings."])
    return "\n".join(L)


# ------------------------------------------------------------------ invoices
def gen_orders():
    r = load("orders")
    L = head("orders", "Invoices",
             "Prints one invoice per order for a date range: ship-to and bill-to blocks, line items, subtotal, freight, discount, and total, from the `ORDERS VIEW` view after the `getinv` dialog supplies the range.",
             [PICKER % ("ORDERS", "Invoices", "REPO")],
             "[[../04-forms/getinv.md]] (the parameter dialog), [[../03-data-model/README.md]] (`ORDERS VIEW`), [[../03-data-model/tables/orders.md]], [[../03-data-model/tables/order_line_items.md]], [[../04-forms/reports.md]], [[../04-forms/ordentry.md]] (the same total on screen), [[README.md]].")
    L += ["The most elaborate report in the sample: a data environment with code, a group with a page break, two report variables, and 66 records. The page header is empty; everything a page needs sits in the group header, so each order starts a new page with its own heading.", ""]
    L += de_section(r, "The `fontface` attribute of the data environment record holds the VFP 9 compiler's include-file table (`..\\include\\tastrade.h`, `foxpro.h`, `strings.h`) with an absolute path into the VFP install: build noise from the 2026 rebuild, not source.", {
        "Init": "Runs the date dialog `LINKED` (so it is released with the object), reads the result, and copies the dates into `dDateFrom` and `dDateTo`. Those are not `LOCAL`, on purpose: they are private variables that the view's `?dDateFrom` and `?dDateTo` parameters read when `OpenTables()` runs. **NOTE:** `WEXIST(\"Project Manager\")` switches to `HOME() + \"Samples\\Tastrade\\\"`. The `#INCLUDE` here is why the message constants resolve; [[listempl.md]] lacks it.",
        "Destroy": ""})
    L += ["## Bands & content", "", "The wordmark, logo, and Page / Date objects are in the group header, not the page header, so they print once per invoice.", ""]
    for b in r["bands"]:
        L += band_section(b)
    L += variables_section(r)
    L += ["The invoice arithmetic, quoted from the variables and the total field:", "",
          fence("vSubTotal = quantity * MTON(unit_price)        && Calculate: Sum, reset per order group\nvDisCount = iif(discount > 0, vSubTotal * (discount / 100), 0)\nTotal     = vSubTotal + freight - vDisCount"), "",
          "Subtotal is the sum of extended line prices for the order; discount is a percentage of that subtotal; total adds freight. This is the **seventh copy of the order total formula** in the sample (two stored procedures, two views, one stored procedure with freight, the order entry screen, and this report). It agrees with the `ORDERTOTAL` view and the order entry screen.", ""]
    L += page_section(r, "**NOTE:** the saved environment names `\\\\RED-PRN-16\\CORP0007`, a Microsoft print server (IP 172.30.168.9) captured when the report was last saved in 2001. VFP tries it first on every run.")
    L += ["## Triggered from", ""] + ["- " + (t % "ORDERS" if "%s" in t else t) for t in PICKER_TRIG] + [""]
    L += notes(["**Bill To city line has no space before the postal code**: `ALLTRIM(city) + \", \" + ALLTRIM(region) + postal_code`, while the Ship To line has `+ \" \" + ship_to_postal_code`.",
                "**Column names are VFP's automatic ones.** `company_name_a` (customer) and `company_name_b` (shipper) exist because `ORDERS VIEW` selects two `company_name` columns; a rebuilt view must keep those names or the report breaks.",
                "**`MTON()` in the variable, not in the field.** The subtotal variable converts the currency unit price to numeric; the Extension field prints `quantity * unit_price` directly.",
                "**`vDisCount` resets at end of report** but has no calculation, so it is simply re-evaluated on every record from the running subtotal; the reset setting is moot.",
                "**`order_number` uses format `@J`** (right-justify); money fields use `99999.99` to `999999999.99` masks.",
                "**Page footer** prints \"We thank you for your patronage\" in Courier New bold italic, teal, under a rule.",
                "**Empty page header (0 in)** with `pagebreak` on both the group header and footer.",
                "**The Escape key confirms** in the date dialog, see [[../04-forms/getinv.md]]."])
    return "\n".join(L)


# ------------------------------------------------------------------ sales
def gen_salesdet():
    r = load("salesdet")
    L = head("salesdet", "Sales Detail",
             "Prints daily sales figures grouped by month, with a total and average per month and a grand total, from the `SALES DETAIL` view.",
             [PICKER % ("SALESDET", "Sales Detail", "REPO")],
             "[[../03-data-model/README.md]] (`SALES DETAIL` view and its unit-price note), [[salessum.md]] (the summary version), [[topcust.md]], [[../04-forms/reports.md]], [[README.md]].")
    L += de_section(r, "", {})
    L += ["## Bands & content", "", "The wordmark labels are present but this is the only report without the logo bitmap and without Page / Date fields.", ""]
    for b in r["bands"]:
        L += band_section(b)
    L += variables_section(r)
    L += page_section(r, PRN_MS)
    L += ["## Triggered from", ""] + ["- " + (t % "SALESDET" if "%s" in t else t) for t in PICKER_TRIG] + [""]
    L += notes([UNITPRICE,
                "**One month per page**: the group on `exp_1` has `pagebreak` set on both header and footer.",
                "**Column names are VFP's automatic ones.** `exp_1` is the unnamed first column `STR(YEAR(...),4)+STR(MONTH(...),2)` and `sum_unit_price` the unnamed `SUM(...)`; a rebuilt view must keep them.",
                "**Month/Year prints as `RIGHT(exp_1, 2) + \"/\" + LEFT(exp_1, 4)`**, so single-digit months come out space-padded (\" 7/1996\"). That detail field has its print-when flags changed (`supvalchng`), which in the designer corresponds to printing only when the value changes; not run here.",
                "**Average is the average of daily sums** within the month (calculate Average, reset Group 1), not of orders.",
                "**Fifteen empty records** (objtype 0) sit between the layout objects and the data environment record; they are not deleted rows, and VFP ignores them."])
    return "\n".join(L)


def gen_salessum():
    r = load("salessum")
    L = head("salessum", "Sales Summary",
             "Prints one line per month with the month's sales figure and a grand total, from the `SALES SUMMARY` view.",
             [PICKER % ("SALESSUM", "Sales Summary", "REPO")],
             "[[../03-data-model/README.md]] (`SALES SUMMARY` view), [[salesdet.md]] (the detail version), [[topcust.md]], [[../04-forms/reports.md]], [[README.md]].")
    L += de_section(r, "", {})
    L += ["## Bands & content", "", LOGO, ""]
    for b in r["bands"]:
        L += band_section(b)
    L += variables_section(r)
    L += page_section(r, PRN_LOCAL)
    L += ["## Triggered from", ""] + ["- " + (t % "SALESSUM" if "%s" in t else t) for t in PICKER_TRIG] + [""]
    L += notes([UNITPRICE,
                "**Depends on the automatic column name `exp_1`** for the month key; `sum_unit_price` is named in the view's SQL.",
                "**Grand total** is a Sum of `MTON(sum_unit_price)` reset at end of report, in a 0.50 in summary band whose record has `norepeat` and `colbreak` set."])
    return "\n".join(L)


def gen_topcust():
    r = load("topcust")
    L = head("topcust", "Top 25 Customers",
             "Prints the 25 customers with the highest order totals, ranked, with country and total, from the `TOP25CUST` view.",
             [PICKER % ("TOPCUST", "Top 25 Customers", "REPO")],
             "[[../03-data-model/README.md]] (`TOP25CUST` and `ORDERTOTAL` views), [[../03-data-model/tables/customer.md]], [[salessum.md]], [[../04-forms/reports.md]], [[README.md]].")
    L += de_section(r, "**NOTE:** four cursors, three of them dead. `customer`, `orders`, and `order_line_items` are opened by the data environment but no field expression, variable, or group refers to them; the `TOP25CUST` view already joins them through `ORDERTOTAL`. Probably left from a draft that queried the tables directly.", {})
    L += ["## Bands & content", "", LOGO, ""]
    for b in r["bands"]:
        L += band_section(b)
    L += variables_section(r)
    L += page_section(r, PRN_LOCAL)
    L += ["## Triggered from", ""] + ["- " + (t % "TOPCUST" if "%s" in t else t) for t in PICKER_TRIG] + [""]
    L += notes(["**Rank is `STR(RECNO(),2) + '.'`**, the record number in the view cursor, which is ordered `custtotal DESC` by the view's SQL.",
                "**`company_name` is unqualified** while `customer` is also open with a `company_name` column; it resolves through `InitialSelectedAlias = \"top25cust\"`. The other two columns are qualified `top25cust.`.",
                "**Uses the real order total.** `ORDERTOTAL` applies quantity, discount, and freight, so this report's figures are order totals; [[salessum.md]] and [[salesdet.md]] sum unit prices. The three sales reports do not reconcile.",
                "One of two reports (with `behindsc.frx`) that have no description entry in `tastrade.pj2`; the same two are the only ones with a code page recorded (`Cpid=\"1252\"`), so both were probably added or re-saved later than the rest.",
                "Money mask `$9,999,999.99`."])
    return "\n".join(L)


# ------------------------------------------------------------------ self-documentation
def gen_behindsc():
    r = load("behindsc")
    L = head("behindsc", "Behind the Scenes",
             "Prints the explanation text (`behindsc.desc`) of the topic currently selected in the Behind the Scenes form.",
             ["[[../04-forms/behindsc.md]] `cmdPrint.Click`: `REPORT FORM behindsc NEXT 1 TO PRINTER NOCONSOLE`."],
             "[[../04-forms/behindsc.md]], [[../03-data-model/README.md]] (`behindsc.dbf` schema), [[casestdy.md]] (same layout), [[README.md]].")
    L += de_section(r, "`AutoOpenTables` is off and there is no code, so the cursor is never opened by the report: it prints against the `behindsc` alias the form already has open in its data session, which is what `NEXT 1` (the current record only) needs.", {})
    L += ["## Bands & content", "", LOGO, ""]
    for b in r["bands"]:
        L += band_section(b)
    L += variables_section(r)
    L += page_section(r, PRN_LOCAL)
    L += ["## Triggered from", "", "- The form's Print button, printer only (no preview), after `PRINTSTATUS()`.", ""]
    L += notes(["**Same layout as [[casestdy.md]]** with the title label \"Behind the Scenes\"; the two differ only in the title, the cursor filter, and whether the cursor auto-opens.",
                "**`behindsc.desc`** is a memo printed in Arial 10 with `stretch` in a 0.71 in detail band."])
    return "\n".join(L)


def gen_casestdy():
    r = load("casestdy")
    L = head("casestdy", "Case Study",
             "Prints every \"Case Study\" row of `behindsc.dbf` (`screen_id = \"*Case Study\"`), the text the case study form displays.",
             ["[[../04-forms/casestdy.md]] `cmdPrint.Click`: `REPORT FORM casestdy TO PRINTER NOCONSOLE`, after a Yes/No confirmation."],
             "[[../04-forms/casestdy.md]], [[behindsc.md]] (same layout), [[../03-data-model/README.md]] (`behindsc.dbf`), [[README.md]].")
    L += ["**Dead report.** The only thing that runs it is the case study form, and nothing in the source runs that form (see [[../04-forms/casestdy.md]]). It compiles into the EXE and is unreachable.", ""]
    L += de_section(r, "`AutoOpenTables` is left on, so the report opens `behindsc.dbf` itself with the filter above, in the calling form's data session where the form has the same alias open already; not run here.", {})
    L += ["## Bands & content", "", LOGO, ""]
    for b in r["bands"]:
        L += band_section(b)
    L += variables_section(r)
    L += page_section(r, "**NOTE:** the text environment names `LaserNT` but the binary DEVNAMES block names an HP LaserJet 4Si on `\\\\msprint32\\privj`; the report was saved on two different machines and the two halves of the printer record were not updated together.")
    L += ["## Triggered from", "", "- The case study form's Print button only.", ""]
    L += notes(["**Filter stored on the cursor**: `SCREEN_ID = \"*Case Study\"`, the same value the form seeks (`SEEKVALUE_LOC`).",
                "**Printer environment records disagree**, see Page setup.",
                "The FRX has `Cpid=\"0\"` in the project; layout identical to [[behindsc.md]]."])
    return "\n".join(L)


def gen_viewcode():
    r = load("viewcode")
    L = head("viewcode", "Code Report",
             "Prints the method code the Behind the Scenes form extracted, from the `viewcode` cursor the form creates.",
             ["[[../04-forms/viewcode.md]] `cmdPrint.Click`: `REPORT FORM viewcode TO PRINTER NOCONSOLE`, after a Yes/No confirmation."],
             "[[../04-forms/viewcode.md]], [[../04-forms/behindsc.md]] (creates the cursor), [[README.md]].")
    L += de_section(r, "The only report with no cursor at all. `frmbehindsc.showcode` runs `CREATE CURSOR viewcode (code M)`, fills it, and opens the viewer form in the same data session; the report's single field reads `viewcode.code` from that cursor.", {})
    L += ["## Bands & content", "", LOGO, ""]
    for b in r["bands"]:
        L += band_section(b)
    L += variables_section(r)
    L += page_section(r, "**NOTE:** the saved environment names an `HP LaserJet 4Si/4SiMX PS` on `\\\\msprint32\\privj`, a Microsoft print server; VFP tries it first.")
    L += ["## Triggered from", "", "- The View Code form's Print button only.", ""]
    L += notes(["**Code prints in Courier New 10** with `stretch`, the only monospaced field in the reports.",
                "**Band bar height differs.** The detail field sits 19 designer pixels below the page header, not 20 like every other report: this FRX was last saved by a different VFP version's designer.",
                "**Not in `repolist.dbf`**, like the other two self-documentation prints; it can only be printed from its form."])
    return "\n".join(L)


# ------------------------------------------------------------------ index
def gen_readme():
    rows = [
        ("listcat", "Category Listing", "`CATEGORY LISTING` view", "picker (LIST)"),
        ("listcust", "Customer Listing", "`CUSTOMER LISTING` view", "picker (LIST)"),
        ("listempl", "Employee Listing", "`EMPLOYEE LISTING` view, `?cTitle` from `gettitle`", "picker (LIST)"),
        ("listprod", "Product Listing", "`PRODUCT LISTING` view", "picker (LIST)"),
        ("listship", "Shipper Listing", "`SHIPPER LISTING` view", "picker (LIST)"),
        ("listsupp", "Supplier Listing", "`SUPPLIER LISTING` view", "picker (LIST)"),
        ("orders", "Invoices", "`ORDERS VIEW` view, dates from `getinv`", "picker (REPO)"),
        ("salesdet", "Sales Detail", "`SALES DETAIL` view", "picker (REPO)"),
        ("salessum", "Sales Summary", "`SALES SUMMARY` view", "picker (REPO)"),
        ("topcust", "Top 25 Customers", "`TOP25CUST` view (+3 unused cursors)", "picker (REPO)"),
        ("behindsc", "Behind the Scenes", "form's `behindsc` alias, current record", "`frmbehindsc` Print"),
        ("casestdy", "Case Study", "`behindsc.dbf`, filter `*Case Study`", "`frmcasestudy` Print (unreachable)"),
        ("viewcode", "Code Report", "`viewcode` cursor made by `frmbehindsc`", "`frmviewcode` Print"),
    ]
    L = ["# Reports", "",
         "Thirteen reports in `reports/*.frx`, all documented from their FoxBin2PRG twins with every band, object, expression, cursor, and the saved printer environment. Ten are run from the report picker [[../04-forms/reports.md]] by the rows of `data/repolist.dbf`; three are printed by the self-documentation forms. There are no labels (`.lbx`).", "",
         "| File | Title | Data | Run from | Doc |", "|---|---|---|---|---|"]
    for stem, title, data, run in rows:
        L.append("| `reports/%s.frx` | %s | %s | %s | [[%s.md]] |" % (stem, title, data, run, stem))
    L += ["",
          "## How the reports get their data", "",
          "Twelve of the thirteen declare a cursor in their data environment; the listings and sales reports open a DBC view, the two self-documentation prints open or reuse the free table `behindsc.dbf`, and `viewcode` has no cursor and reads a cursor its calling form creates. Two reports (`listempl`, `orders`) turn `AutoOpenTables` off and run a parameter dialog from the data environment's `Init` before opening the view, passing the values as private variables that the view's `?parameters` pick up. The invoice's `Init` has `#INCLUDE \"INCLUDE\\TASTRADE.H\"`; the employee listing's does not, so its \"Nothing to print\" message box refers to undefined names and errors instead.", "",
          "Cursor sources are stored relative to the `reports\\` folder (`..\\data\\tastrade.dbc`); `progs/main.prg` sets the default directory to the application root and `SET PATH TO ... DATA ...`, which is how they resolve at run time.", "",
          "## Layout conventions", "",
          "Every report is on Letter paper (orientation left to the printer) in Arial 12 with a page header carrying the \"Tasmanian Traders\" wordmark (a blue 24-point \"T\" before \"asmanian\" and \"raders\"), the logo `bitmaps/ttradesm.bmp`, a rule, and Page / Date fields; `salesdet` omits the logo and page fields, and the invoice puts all of it in the group header so it repeats per order. In the listings, column headings sit in a grey box at the bottom of the page header. Coordinates in the docs are inches from the top-left of the band; the twins store 1/10000 inch in designer space, where each band is followed by a 20-pixel band bar.", "",
          "## Findings", "",
          "- **Every report carries a saved printer environment.** Four devices: `\\\\MSPRINT32\\2/1MC PRIVJ 157.56.32.242` (seven reports), `LaserNT` (three, plus the text half of `casestdy`), an HP LaserJet 4Si on `\\\\msprint32\\privj` (`viewcode`, and the binary half of `casestdy`), and `\\\\RED-PRN-16\\CORP0007` (`orders`). VFP tries the saved device first on every run.",
          "- **The invoice is the seventh copy of the order total formula** (subtotal, minus discount percent, plus freight), see [[orders.md]].",
          "- **The three sales reports do not reconcile**: `salessum` and `salesdet` sum unit prices without quantity; `topcust` uses the full total through `ORDERTOTAL`.",
          "- **Three dead cursors** in `topcust`; **one dead report**, `casestdy`, reachable only from a form nothing runs.",
          "- **Two reports depend on VFP's automatic column names** (`exp_1`, `sum_unit_price`, `company_name_a`, `company_name_b`).",
          "- **A latent runtime error** in the employee listing when the chosen title has no employees (missing `#INCLUDE`).",
          "- **Cost printed beside price** on the product listing, with no user-level check.",
          "- **Bill To postal code has no separating space** on the invoice.",
          "- The FoxBin2PRG twins expose everything above; nothing needed the binary `.frx`, though `tools/extract_frx.py` reproduces the coordinates from it.",
          ""]
    return "\n".join(L)


GENERATORS = (("listcat.md", gen_listcat), ("listcust.md", gen_listcust), ("listempl.md", gen_listempl),
              ("listprod.md", gen_listprod), ("listship.md", gen_listship), ("listsupp.md", gen_listsupp),
              ("orders.md", gen_orders), ("salesdet.md", gen_salesdet), ("salessum.md", gen_salessum),
              ("topcust.md", gen_topcust), ("behindsc.md", gen_behindsc), ("casestdy.md", gen_casestdy),
              ("viewcode.md", gen_viewcode), ("README.md", gen_readme))

if __name__ == "__main__":
    for fn, gen in GENERATORS:
        with open(os.path.join(OUT, fn), "w", encoding="utf-8", newline="\n") as f:
            f.write(gen())
        print("wrote", fn)
