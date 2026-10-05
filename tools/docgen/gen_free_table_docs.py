"""Generate docs/03-data-model/tables/{behindsc,repolist,ttrade}.md, the three free
tables outside tastrade.dbc.

Schema and tags come from the .db2 twins through foxparse.parse_db2 and are
cross-checked at run time against the live AFIELDS()/TAG() dump in dbcdump.txt
(Step 4b); rows come from the DBFs through tools/dbf.py. The behindsc doc also
resolves every "show code" instruction in the table against the twins, so the
drift between the sample's self-documentation and its code is measured, not
asserted. Prose is hand-written and grep-checked. Rerun after editing; never
hand-edit the output.
"""
import os, re, sys, collections
sys.path.insert(0, os.environ.get("VFP_TOOLKIT_TOOLS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "vfp-documentation-toolkit", "tools")))
import foxparse as fp
from dbf import read_table

ROOT = os.environ.get("TASTRADE_ROOT", os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))
OUT = os.path.join(ROOT, "docs", "03-data-model", "tables")
DUMP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dbcdump.txt")
TYPES = {"C": "Character (C)", "N": "Numeric (N)", "M": "Memo (M)", "D": "Date (D)", "L": "Logical (L)", "Y": "Currency (Y)", "G": "General (G)"}


def dump_free():
    free, cur = {}, None
    for line in open(DUMP, encoding="latin-1"):
        p = line.rstrip("\r\n").split("|")
        if p[0] == "FREETABLE":
            cur = {"name": p[1], "rows": int(p[3]), "fields": [], "tags": []}; free[p[1]] = cur
        elif p[0] == "TABLE":
            cur = None
        elif cur is not None and p[0] == "FIELD":
            cur["fields"].append((p[1], p[2], p[3], p[4]))
        elif cur is not None and p[0] == "TAG":
            cur["tags"].append((p[1], p[2], p[3], p[4], p[5]))
    return free


FREE = dump_free()


def twin(rel):
    r = fp.parse_db2(os.path.join(ROOT, rel))
    d = FREE[r["table"]]
    # cross-check: the twin and the live dump must agree on every field and tag
    tf = [(f["name"], f["type"], f["width"], f["decimals"]) for f in r["fields"]]
    assert tf == d["fields"], (rel, tf, d["fields"])
    tt = [(i["name"], i["key"]) for i in r["indexes"]]
    assert tt == [(t[0], t[1]) for t in d["tags"]], (rel, tt, d["tags"])
    return r, d


def md(s):
    return str(s).replace("|", "\\|").replace("\r\n", " ").replace("\n", " ").strip()


def head(dbf_rel, twin_rel, title, purpose, used_by, related, rows_n):
    return ["# %s" % title, "", "| Source file | Type | Path |", "|---|---|---|",
            "| `%s` | Free table (outside `tastrade.dbc`) | `%s` |" % (os.path.basename(dbf_rel), twin_rel), "",
            "**Purpose:** " + purpose, "", "**Used by:**"] + ["- " + u for u in used_by] + ["", "**Related docs:** " + related, "",
            "Row count in the sample data: %d. No database container, so no long field names, comments, defaults, rules, or triggers; what follows is all there is." % rows_n, ""]


def schema(r):
    L = ["## Schema", "", "| # | Field | Type | Width | Dec | Null |", "|---|---|---|---|---|---|"]
    for i, f in enumerate(r["fields"], 1):
        L.append("| %d | `%s` | %s | %s | %s | %s |" % (i, f["name"].lower(), TYPES.get(f["type"], f["type"]), f["width"], f["decimals"], "no" if f["null"] == ".F." else "yes"))
    L += ["", "## Triggers (from table header)", "", "- None: no insert, update, or delete trigger, no table rule. Free tables cannot carry them.", "",
          "## Indexes (.cdx tags)", ""]
    if r["indexes"]:
        L += ["| Tag | Type | Expression | For | Order |", "|---|---|---|---|---|"]
        for i in r["indexes"]:
            L.append("| `%s` | %s | `%s` | %s | %s |" % (i["name"].lower(), i["kind"], i["key"], i["filter"], "asc" if i["order"] == "ascending" else i["order"]))
    else:
        L.append("None. The table has no `.cdx`; the help engine reads it by `contextid` sequentially.")
    L += ["", "## Stored procedure references", "", "- None.", "", "## Relations", "", "- None. Free tables take part in no persistent relation.", ""]
    return L


# ------------------------------------------------------------------ instruction resolver (behindsc)
TWINS = {}
for pat, folder in (("*.sc2", "forms"), ("*.vc2", "libs"), ("*.prg", "progs"), ("*.dc2", "data")):
    import glob
    for f in glob.glob(os.path.join(ROOT, folder, pat)):
        TWINS[os.path.basename(f).lower()] = open(f, encoding="cp1252", errors="replace").read()


def resolve(instr):
    """'file, object, method' -> (file ok, object ok, methods ok/missing) following frmbehindsc's parsing."""
    parts = [x.strip() for x in instr.split(",", 2)]
    fname = parts[0].lower(); obj = parts[1].lower() if len(parts) > 1 else ""; meth = parts[2].strip() if len(parts) > 2 else ""
    if fname.startswith("("):
        obj = ""
    stem, ext = os.path.splitext(fname)
    twin_name = {".scx": stem + ".sc2", ".vcx": stem + ".vc2", ".dbc": stem + ".dc2", ".prg": stem + ".prg"}.get(ext, "")
    text = TWINS.get(twin_name)
    file_ok = text is not None
    if not file_ok:
        return file_ok, False, [], parts
    if ext == ".prg":
        return True, True, [], parts
    if ext == ".dbc":
        ok = re.search(r"^\s*FUNCTION\s+%s\b" % re.escape(obj), text, re.M | re.I) is not None
        return True, ok, [], parts
    low = text.lower()
    obj_ok = (re.search(r"^define class %s\b" % re.escape(obj), low, re.M) is not None
              or re.search(r'objpath="(?:[\w.]+\.)?%s"' % re.escape(obj), low) is not None
              or re.search(r"^\s*procedure (?:[\w.]+\.)?%s\." % re.escape(obj), low, re.M) is not None)
    meths = []
    if meth and meth != "*":
        names = [m.strip() for m in meth.strip("()").split(",") if m.strip()]
        for m in names:
            found = re.search(r"^\s*procedure (?:[\w.]+\.)?%s\.%s\s*$" % (re.escape(obj), re.escape(m.lower())), low, re.M) is not None \
                or (re.search(r"^define class %s\b" % re.escape(obj), low, re.M) is not None and
                    re.search(r"^define class %s\b.*?^\s*(?:protected |hidden )?procedure %s\b" % (re.escape(obj), re.escape(m.lower())), low, re.M | re.S) is not None)
            meths.append((m, found))
    return True, obj_ok, meths, parts


# ------------------------------------------------------------------ behindsc
def gen_behindsc():
    r, d = twin("data/behindsc.db2")
    names, rows = read_table(os.path.join(ROOT, "data", "behindsc.dbf"))
    L = head("data/behindsc.dbf", "data/behindsc.db2", "behindsc",
             "The sample's self-documentation: one row per \"Behind the Scenes\" topic, holding the explanation the form displays and an instruction telling the form which file, object, and methods to open as tables and show as code.",
             ["[[../../04-forms/behindsc.md]] (`frmbehindsc`): DataEnvironment cursor, ordered by `screen_top`; `SEEK`s the current form's name in `screen_id`, lists the topics, shows `desc`, and follows `code_to_sh` in `showcode`.",
              "[[../../04-forms/casestdy.md]] (`frmcasestudy`): DataEnvironment cursor, positioned on `screen_id = \"*Case Study\"` (`SEEKVALUE_LOC`).",
              "[[../../06-reports/behindsc.md]] (the form's current row, `NEXT 1`) and [[../../06-reports/casestdy.md]] (all `*Case Study` rows)."],
             "[[../README.md]] (container; this table is outside it), [[../../04-forms/behindsc.md]], [[repolist.md]], [[ttrade.md]].", len(rows))
    L += schema(r)
    # rows by screen
    by = collections.OrderedDict()
    for row in rows:
        by.setdefault(str(row["screen_id"]).strip(), []).append(row)
    L += ["## Used by", "", "See the header. The form opens it read-only from its DataEnvironment and never writes it; there is no maintenance form. Adding a topic means editing the DBF.", "",
          "## Sample / notable rows", "",
          "All %d rows, grouped by `screen_id` (the form or subject the topic belongs to). `desc` is the text shown; `code_to_sh` is the instruction, `file, object, method` per line, `*` for every method, `(a, b)` for several." % len(rows), "",
          "| screen_id | topics | rows | with code instruction |", "|---|---|---|---|"]
    for sid, rs in by.items():
        L.append("| `%s` | %s | %d | %d |" % (sid, ", ".join(md(str(x["topic"]).strip()) for x in rs), len(rs), sum(1 for x in rs if str(x.get("code_to_sh", "")).strip())))
    L += [""]
    # resolve instructions
    results = []
    for row in rows:
        c = str(row.get("code_to_sh", "")).strip()
        if not c:
            continue
        for line in c.replace("\r\n", "\n").split("\n"):
            line = line.strip()
            if line:
                file_ok, obj_ok, meths, parts = resolve(line)
                results.append((str(row["screen_id"]).strip(), str(row["topic"]).strip(), line, file_ok, obj_ok, meths))
    total = len(results)
    bad = [x for x in results if not x[3] or not x[4] or any(not ok for m, ok in x[5])]
    L += ["## Do the instructions still point at code?", "",
          "Each `code_to_sh` line was resolved against the twins the way `frmbehindsc` resolves it at run time (file by name, object by class name or object path, method by `PROCEDURE`). %d instruction lines in %d rows; %d resolve; %d do not:" % (total, sum(1 for row in rows if str(row.get("code_to_sh", "")).strip()), total - len(bad), len(bad)), "",
          "| Topic | Instruction | What is wrong |", "|---|---|---|"]
    for sid, topic, line, file_ok, obj_ok, meths in bad:
        why = []
        if not file_ok:
            why.append("no such file")
        elif not obj_ok:
            why.append("no such object or class")
        if obj_ok:
            why += ["no method `%s`" % m for m, ok in meths if not ok]
        L.append("| %s / %s | `%s` | %s |" % (md(sid), md(topic), md(line), "; ".join(why)))
    L += ["",
          "The form reports \"not found\" for these when the Code button is pressed ([[../../04-forms/behindsc.md]]). The rest resolve, including the two that name the DBC's stored procedures and the two that name whole programs.", ""]
    empties = [str(x["topic"]).strip() for x in rows if not str(x.get("desc", "")).strip()]
    L += ["## Notes", "",
          "- **The self-documentation has drifted from the code**: the table above is the measurement. It was last edited for a build whose library was named `order.vcx` and whose customer form was `frmcustomer`.",
          "- **%d rows have an empty `desc`** (%s): topics with a code instruction and no explanation." % (len(empties), ", ".join("\"%s\"" % e for e in empties)),
          "- **`code_to_sh` is a tiny language**: `file, object, method`, one instruction per line, `*` for all methods, `(m1, m2)` for a list, a trailing comma and nothing for a stored procedure or a program. It is parsed by three methods of the form with `AT()` and `SUBSTR()` and has no validation.",
          "- **The Case Study rows** share the table under `screen_id = \"*Case Study\"`; the leading asterisk sorts them first and keeps them out of the form-name lookups.",
          "- **Three tags**, on `screen_id`, `screen_id + topic`, and `LTRIM(topic)`; the form uses `screen_top`.",
          "- **Ships in the EXE's project as a member marked Exclude**, so it must be on disk beside the EXE like the DBC ([[../../01-architecture/projects.md]])."]
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ repolist
def gen_repolist():
    r, d = twin("data/repolist.db2")
    names, rows = read_table(os.path.join(ROOT, "data", "repolist.dbf"))
    L = head("data/repolist.dbf", "data/repolist.db2", "repolist",
             "The report picker's list: one row per report the user may run, with its file stem, display name, and whether it is a report or a listing.",
             ["[[../../04-forms/reports.md]] (`frmreports`): DataEnvironment cursor, `SET FILTER TO ctype = 'REPO'` or `'LIST'` by the option group, list box rows from `cfullname, cdosname`, and `REPORT FORM REPORTS\\<cdosname>.FRX`."],
             "[[../README.md]], [[../../06-reports/README.md]] (the ten reports it names and the three it does not), [[behindsc.md]], [[ttrade.md]].", len(rows))
    L += schema(r)
    L += ["## Used by", "", "See the header. Read-only; the sample's own note says the table \"is considered metadata, and does not pertain to the data maintained by Tasmanian Traders\", which is why it is outside the DBC.", "",
          "## Sample / notable rows", "", "All %d rows:" % len(rows), "", "| cdosname | cfullname | ctype | Report doc |", "|---|---|---|---|"]
    for row in rows:
        stem = str(row["cdosname"]).strip().lower()
        L.append("| %s | %s | %s | [[../../06-reports/%s.md]] |" % (str(row["cdosname"]).strip(), md(str(row["cfullname"]).strip()), str(row["ctype"]).strip(), stem))
    missing = [s for s in ("behindsc", "casestdy", "viewcode")]
    L += ["", "## Notes", "",
          "- **The picker is data-driven**: a report is added or hidden by editing this table; a stem with no `.frx` shows \"Report file not found.\" No row is validated against the `reports/` folder.",
          "- **Three reports are not listed** (%s): the self-documentation prints, run only from their forms ([[../../06-reports/README.md]])." % ", ".join("`%s.frx`" % s for s in missing),
          "- **Three tags**, one per column, though the form filters and lists without setting an order.",
          "- **`cdosname` is 8 characters**: an 8.3 file-name assumption from 1995, still true of every report stem."]
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ ttrade
def gen_ttrade():
    r, d = twin("help/ttrade.db2")
    names, rows = read_table(os.path.join(ROOT, "help", "ttrade.dbf"))
    ctx = {}
    for pat in ("forms/*.sc2", "libs/*.vc2"):
        for f in glob.glob(os.path.join(ROOT, pat)):
            for m in re.finditer(r"HelpContextID = (\d+)", open(f, encoding="cp1252", errors="replace").read()):
                if m.group(1) != "0":
                    ctx.setdefault(int(m.group(1)), []).append(os.path.basename(f))
    L = head("help/ttrade.dbf", "help/ttrade.db2", "ttrade",
             "A help file in Visual FoxPro's own DBF help format (`contextid`, `topic`, `details`): sixteen topics introducing the application, its login and order entry, and each menu.",
             ["**Nothing at run time.** `environment.Set` does `SET HELP TO HELP\\TASTRADE.CHM` ([[../../05-classes/tsgen.md]]), the HTML Help file, and no twin or program names `ttrade.dbf`. The two `HelpContextID` values in the source (%s) match rows here and, presumably, the CHM's map." % "; ".join("%d on %s" % (k, ", ".join(sorted(set(v)))) for k, v in sorted(ctx.items())),
              "The project does not include it or the CHM ([[../../01-architecture/projects.md]])."],
             "[[../README.md]], [[behindsc.md]], [[repolist.md]], [[../../07-menus/README.md]] (the menus the topics describe).", len(rows))
    L += schema(r)
    L += ["## Used by", "", "See the header: not read by the application. The columns and widths (`contextid N(10)`, `topic C(70)`, `details M`) are exactly the structure VFP's `SET HELP TO <table>` expects, so it is the pre-HTML-Help help file, kept beside the CHM.", "",
          "## Sample / notable rows", "", "All %d rows, in table order; `details` lengths in characters." % len(rows), "",
          "| # | contextid | topic | details |", "|---|---|---|---|"]
    for i, row in enumerate(rows, 1):
        det = str(row.get("details", "")).strip()
        L.append("| %d | %s | %s | %s |" % (i, int(row["contextid"]), md(str(row["topic"]).strip()), ("%d chars" % len(det)) if det else "**empty**"))
    empties = [str(x["topic"]).strip() for x in rows if not str(x.get("details", "")).strip()]
    L += ["", "## Notes", "",
          "- **%d of %d topics %s no text**: %s. The `***** ... *****` rows are section headings with a line of text each; \"Overview\", which has context ID 12, is simply empty." % (len(empties), len(rows), "has" if len(empties) == 1 else "have", ", ".join("\"%s\"" % e for e in empties)),
          "- **The introduction promises more than the code does**: \"Depending on your user level, you have access to different tables\" describes menu gating that the shipped build turns off ([[../../02-domain/README.md]]).",
          "- **The Login topic says the password is shown in the Hint box** \"in this sample application\", so the authors knew.",
          "- **No index**, no `.fpt` in the project; the text lives in `ttrade.fpt` beside the table."]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, gen in (("behindsc.md", gen_behindsc), ("repolist.md", gen_repolist), ("ttrade.md", gen_ttrade)):
        with open(os.path.join(OUT, fn), "w", encoding="utf-8", newline="\n") as f:
            f.write(gen())
        print("wrote", fn)
