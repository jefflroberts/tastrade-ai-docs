*-- capture.prg: baseline capture harness for Tastrade.
*--
*-- Run by  vfp9.exe -c tools\baseline\capture.fpw  (COMMAND=DO ...\capture.prg),
*-- normally through tools\baseline\run_capture.ps1, which also watches for
*-- Win32 message boxes, screenshots them, and dismisses them.
*--
*-- The harness runs the built tastrade.exe inside this VFP session
*-- (DO tastrade.exe), so the code that runs is the compiled EXE's. Two timers
*-- on _SCREEN drive it while the application's READ EVENTS is live:
*--   capsentinel  captures and dismisses every modal form it sees (intro form,
*--                report dialogs, About box, modal forms the driver opens);
*--   capdriver    opens each form the way the menu does, captures the form and
*--                the main window, releases it; renders each report through a
*--                ReportListener to PNG pages; then CLEAR EVENTS.
*-- Everything logged: baseline\capture.log (text) and baseline\CAPTURE-LOG.csv,
*-- both flushed after every line (they are never closed: see the end of the
*-- main program).
*-- The window snapshot itself is tools\baseline\snap.ps1 (PrintWindow by HWND).

#DEFINE CAP_ROOT      "C:\fox\tastrade\"
#DEFINE CAP_TOOLS     "C:\fox\tastrade\tools\baseline\"
#DEFINE CAP_MAXPAGES  3
#DEFINE CAP_SCREEN_W  1024
#DEFINE CAP_SCREEN_H  700
#DEFINE CRLF          CHR(13) + CHR(10)
*-- Copied from include\strings.h: what menus\main.mpr passes to the About box.
#DEFINE TASTRADE_LOC     "Tasmanian Traders"
#DEFINE VERSION_LOC      "1.1"
#DEFINE COPYRIGHT_LOC    "Copyright 1996 Microsoft Corporation"
#DEFINE RIGHTSRSRVD_LOC  "All rights reserved"

*-- tnEngine: SET ENGINEBEHAVIOR value to force (0 = leave VFP 9's default);
*-- tcOutDir: output folder under the repo root (default "baseline");
*-- tcPass:   "click" opens and closes everything (the baseline), "entry" runs
*--           the data-entry scenarios (rule violations, refused delete, a new
*--           order, wrong password, all titles); nothing is saved. "save" runs
*--           the successful paths (a customer edit, a new customer, a new
*--           order, the item copy, a password change and login, a delete);
*--           the caller restores data\ from git afterwards.
LPARAMETERS tnEngine, tcOutDir, tcPass
LOCAL lcOut, lcVisible, lcName, i
IF VARTYPE(tnEngine) <> "N"
	tnEngine = 0
ENDIF
IF VARTYPE(tcOutDir) <> "C" OR EMPTY(tcOutDir)
	tcOutDir = "baseline"
ENDIF
IF VARTYPE(tcPass) <> "C" OR EMPTY(tcPass)
	tcPass = "click"
ENDIF
lcOut = CAP_ROOT + tcOutDir + "\"

SET SAFETY OFF
SET BELL OFF
SET TALK OFF
SET DEFAULT TO (CAP_ROOT)
IF tnEngine > 0
	SET ENGINEBEHAVIOR (tnEngine)
ENDIF

IF !DIRECTORY(lcOut)
	MKDIR (lcOut)
ENDIF
IF !DIRECTORY(lcOut + "forms")
	MKDIR (lcOut + "forms")
ENDIF
IF !DIRECTORY(lcOut + "screen")
	MKDIR (lcOut + "screen")
ENDIF
IF !DIRECTORY(lcOut + "reports")
	MKDIR (lcOut + "reports")
ENDIF

*-- Helper object and timers live on _SCREEN, which survives the application's
*-- CLEAR ALL and SET PROCEDURE/CLASSLIB changes. Their classes are defined in
*-- this program, which stays on the call stack for the whole run.
_SCREEN.AddProperty("oCap", CREATEOBJECT("capcore", lcOut))
_SCREEN.oCap.cPass = LOWER(tcPass)
_SCREEN.oCap.nEngine = IIF(tnEngine > 0, tnEngine, 90)
ON ERROR _SCREEN.oCap.OnError(ERROR(), MESSAGE(), PROGRAM(), LINENO())

*-- The runtime has no IDE windows. Record which of VFP's are visible here,
*-- then hide them; the application's own ReleaseToolBars runs later and
*-- found "Standard" not yet visible in the first runs (it appears after
*-- the config COMMAND starts).
lcVisible = ""
FOR i = 1 TO 12
	*-- a variable first: inside HIDE WINDOW (...) VFP read this_toolbar(i)
	*-- as an array subscript (error 31 in run 3)
	lcName = this_toolbar(i)
	IF WVISIBLE(lcName)
		lcVisible = lcVisible + lcName + "; "
		HIDE WINDOW (lcName)
	ENDIF
ENDFOR
_SCREEN.oCap.Log("VFP windows visible at harness start, now hidden: " + IIF(EMPTY(lcVisible), "none", lcVisible))
IF WEXIST("Command")
	HIDE WINDOW Command
ENDIF
_SCREEN.WindowState = 0
_SCREEN.Top = 0
_SCREEN.Left = 0
_SCREEN.Width = CAP_SCREEN_W
_SCREEN.Height = CAP_SCREEN_H

_SCREEN.oCap.Log("harness start; pass " + LOWER(tcPass) + "; VFP " + VERSION() + "; output " + lcOut + "; REPORTBEHAVIOR " + TRANSFORM(SET("REPORTBEHAVIOR")) ;
	+ "; ENGINEBEHAVIOR " + TRANSFORM(SET("ENGINEBEHAVIOR")) + IIF(tnEngine > 0, " (forced by the harness)", " (VFP 9 default)") ;
	+ "; screen " + TRANSFORM(_SCREEN.Width) + "x" + TRANSFORM(_SCREEN.Height) ;
	+ "; default printer " + SET("PRINTER", 2))

_SCREEN.AddObject("tmrSentinel", "capsentinel")
_SCREEN.AddObject("tmrDriver", "capdriver")
_SCREEN.tmrSentinel.Enabled = .T.
_SCREEN.tmrDriver.Enabled = .T.

_SCREEN.oCap.Log("DO " + CAP_ROOT + "tastrade.exe")
DO (CAP_ROOT + "tastrade.exe")
*-- main.prg ends with RELEASE ALL EXTENDED and CLEAR ALL. In run 3 that removed
*-- the _SCREEN property holding the helper ("Unknown member OCAP" on the next
*-- line) and it releases this program's variables too, so nothing below may
*-- use either. The driver wrote CAPTURED.txt before CLEAR EVENTS; the runner
*-- takes this process's exit as the end of the run.
ON ERROR
ON SHUTDOWN
QUIT


*-- The twelve window titles application.ReleaseToolBars hides (include\strings.h).
FUNCTION this_toolbar(tnIndex)
	LOCAL laNames[12]
	laNames[1] = "Form Designer"
	laNames[2] = "Standard"
	laNames[3] = "Layout"
	laNames[4] = "Query Designer"
	laNames[5] = "View Designer"
	laNames[6] = "Color Palette"
	laNames[7] = "Form Controls"
	laNames[8] = "Database Designer"
	laNames[9] = "Report Designer"
	laNames[10] = "Report Controls"
	laNames[11] = "Print Preview"
	laNames[12] = "Command"
	RETURN laNames[tnIndex]
ENDFUNC


*=====================================================================
DEFINE CLASS capcore AS custom
	cOut = ""
	cPass = "click"
	nEngine = 90
	nLog = 0
	nCsv = 0
	nSeq = 0
	cExpect = ""
	cHandled = ""
	lToolbarDone = .F.
	lDone = .F.

	PROCEDURE Init(tcOut)
		this.cOut = tcOut
		this.nLog = FCREATE(this.cOut + "capture.log")
		this.nCsv = FCREATE(this.cOut + "CAPTURE-LOG.csv")
		FPUTS(this.nCsv, "seq,kind,id,form_name,form_class,caption,how,file,pages,status,note")
		FFLUSH(this.nCsv, .T.)
	ENDPROC

	PROCEDURE Log(tcText)
		FPUTS(this.nLog, TTOC(DATETIME(), 3) + " " + TRANSFORM(tcText))
		FFLUSH(this.nLog, .T.)
	ENDPROC

	PROCEDURE Q(tuValue)
		RETURN '"' + STRTRAN(TRANSFORM(tuValue), '"', '""') + '"'
	ENDPROC

	PROCEDURE Csv(tcKind, tcId, tcFormName, tcFormClass, tcCaption, tcHow, tcFile, tnPages, tcStatus, tcNote)
		this.nSeq = this.nSeq + 1
		FPUTS(this.nCsv, TRANSFORM(this.nSeq) + "," + this.Q(tcKind) + "," + this.Q(tcId) + "," ;
			+ this.Q(tcFormName) + "," + this.Q(tcFormClass) + "," + this.Q(tcCaption) + "," ;
			+ this.Q(tcHow) + "," + this.Q(tcFile) + "," + TRANSFORM(tnPages) + "," ;
			+ this.Q(tcStatus) + "," + this.Q(tcNote))
		FFLUSH(this.nCsv, .T.)
		this.Log(tcKind + " " + tcId + " " + tcStatus + IIF(EMPTY(tcNote), "", " (" + tcNote + ")"))
	ENDPROC

	PROCEDURE OnError(tnError, tcMessage, tcProgram, tnLine)
		this.Log("ERROR " + TRANSFORM(tnError) + " " + tcMessage + " in " + tcProgram + " line " + TRANSFORM(tnLine))
		this.Csv("error", tcProgram, "", "", "", "", "", 0, "error", TRANSFORM(tnError) + " " + tcMessage + " line " + TRANSFORM(tnLine))
	ENDPROC

	*-- Let the event loop breathe: the sentinel timer fires inside this loop.
	PROCEDURE Wait(tnSeconds)
		LOCAL lnStart
		lnStart = SECONDS()
		DO WHILE SECONDS() - lnStart < tnSeconds
			DOEVENTS
		ENDDO
	ENDPROC

	*-- Snapshot a window by HWND through snap.ps1; returns .T. if the PNG exists.
	PROCEDURE Snap(tnHwnd, tcFile, tlRoot)
		LOCAL loShell, lcCmd, lnRet
		IF FILE(tcFile)
			ERASE (tcFile)
		ENDIF
		loShell = CREATEOBJECT("WScript.Shell")
		lcCmd = 'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "' + CAP_TOOLS + 'snap.ps1" ' ;
			+ '-Hwnd ' + TRANSFORM(tnHwnd) + ' -OutFile "' + tcFile + '"' + IIF(tlRoot, " -Root", "")
		lnRet = loShell.Run(lcCmd, 0, .T.)
		IF lnRet <> 0
			this.Log("snap.ps1 exit " + TRANSFORM(lnRet) + " for " + tcFile)
		ENDIF
		RETURN FILE(tcFile)
	ENDPROC

	*-- Rasterise an EMF report page through emf2png.ps1.
	PROCEDURE Emf2Png(tcEmf, tcPng)
		LOCAL loShell, lcCmd, lnRet
		loShell = CREATEOBJECT("WScript.Shell")
		lcCmd = 'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "' + CAP_TOOLS + 'emf2png.ps1" ' ;
			+ '-InFile "' + tcEmf + '" -OutFile "' + tcPng + '" -Scale 2'
		lnRet = loShell.Run(lcCmd, 0, .T.)
		IF lnRet <> 0
			this.Log("emf2png.ps1 exit " + TRANSFORM(lnRet) + " for " + tcPng)
		ENDIF
		RETURN FILE(tcPng)
	ENDPROC

	PROCEDURE CaptureForm(toForm, tcId, tcHow, tcSuffix)
		LOCAL lcFile, llOk, lcName, lcClass, lcCaption
		lcFile = this.cOut + "forms\" + tcId + IIF(EMPTY(tcSuffix), "", "-" + tcSuffix) + ".png"
		lcName = toForm.Name
		lcClass = toForm.Class
		lcCaption = toForm.Caption
		llOk = this.Snap(toForm.HWnd, lcFile)
		this.Csv("form", tcId + IIF(EMPTY(tcSuffix), "", "-" + tcSuffix), lcName, lcClass, lcCaption, tcHow, ;
			"forms/" + JUSTFNAME(lcFile), 0, IIF(llOk, "ok", "no file"), ;
			TRANSFORM(toForm.Width) + "x" + TRANSFORM(toForm.Height) + IIF(toForm.WindowType = 1, " modal", ""))
		RETURN llOk
	ENDPROC

	PROCEDURE CaptureScreen(tcId, tcNote)
		LOCAL lcFile, llOk
		lcFile = this.cOut + "screen\" + tcId + ".png"
		*-- _SCREEN.HWnd is the MDI client; -Root takes the frame with menu and toolbar
		llOk = this.Snap(_SCREEN.HWnd, lcFile, .T.)
		this.Csv("screen", tcId, "_SCREEN", "", _SCREEN.Caption, "", "screen/" + JUSTFNAME(lcFile), 0, ;
			IIF(llOk, "ok", "no file"), tcNote)
		RETURN llOk
	ENDPROC

	PROCEDURE CaptureToolbar
		IF this.lToolbarDone OR TYPE("oApp.oToolBar") <> "O" OR ISNULL(oApp.oToolBar)
			RETURN
		ENDIF
		this.lToolbarDone = .T.
		IF PEMSTATUS(oApp.oToolBar, "HWnd", 5)
			LOCAL lcFile, llOk
			lcFile = this.cOut + "forms\toolbar.png"
			llOk = this.Snap(oApp.oToolBar.HWnd, lcFile)
			this.Csv("form", "toolbar", oApp.oToolBar.Name, oApp.oToolBar.Class, oApp.oToolBar.Caption, ;
				"oApp.ShowNavToolBar (first framework form)", "forms/toolbar.png", 0, IIF(llOk, "ok", "no file"), "")
		ELSE
			this.Log("toolbar has no HWnd; captured only inside screen/*.png")
		ENDIF
	ENDPROC

	*-- Name the button (or KEYS:<SendKeys>) run_capture.ps1 should use on the
	*-- next dialog; the runner deletes the file after one use.
	PROCEDURE Answer(tcText)
		STRTOFILE(tcText, this.cOut + "ANSWER.txt")
		this.Log("answer for the next dialog: " + tcText)
	ENDPROC

	*-- Run a few lines of code in a form's private data session (the way the
	*-- form's own methods would see the tables), then come back.
	PROCEDURE InSession(toForm, tcCode)
		LOCAL lnOld
		lnOld = SET("DATASESSION")
		SET DATASESSION TO (toForm.DataSessionId)
		EXECSCRIPT(tcCode)
		SET DATASESSION TO (lnOld)
	ENDPROC

	*-- Data-entry pass: what to do with a modal form after its first capture.
	*-- Returns .T. when the scenario closed the form itself.
	PROCEDURE Scenario(toForm, tcId)
		LOCAL lcHow
		lcHow = "entry scenario, see the driver row"
		IF this.cPass == "save"
			RETURN this.ScenarioSave(toForm, tcId)
		ENDIF
		DO CASE
			CASE tcId == "custadd"
				*-- OK with the customer ID empty: the DBC rule NOT EMPTY(customer_id)
				toForm.cmdOK.Click()
				this.Wait(0.8)
				this.CaptureForm(toForm, tcId, "cmdOK with an empty Customer ID (rule on customer_id)", "rule")
			CASE tcId == "chngpswd"
				*-- correct old password (the Hint box shows it), then a mismatched confirmation
				toForm.txtOldPassword.Value = toForm.txtHint.Value
				toForm.txtOldPassword.InteractiveChange()
				toForm.txtNewPassword.Value = "baseline"
				toForm.txtConfirm.Value = "baselinX"
				this.Wait(0.4)
				this.CaptureForm(toForm, tcId, "old password typed (from the Hint box), new and confirm differ", "filled")
				toForm.cmdOK.Click()
				this.Wait(0.8)
				this.CaptureForm(toForm, tcId, "after cmdOK with new and confirm differing", "mismatch")
			CASE tcId == "chngpswd-empty"
				*-- OK with nothing entered: "no password entered, abandon?" answered No closes it
				toForm.cmdOK.Click()
				this.Wait(0.5)
				RETURN .T.
			CASE tcId == "loginpicture"
				toForm.txtPassword.Value = "wrong"
				this.Wait(0.3)
				this.CaptureForm(toForm, tcId, "password box holds a wrong password", "filled")
				toForm.cmdOk.Click()
				this.Wait(0.8)
				this.CaptureForm(toForm, tcId, "after cmdOk with a wrong password", "badpassword")
		ENDCASE
		RETURN .F.
	ENDPROC

	*-- Save pass: the successful paths through the modal forms.
	PROCEDURE ScenarioSave(toForm, tcId)
		DO CASE
			CASE tcId == "custadd"
				*-- a new customer BASEL; OK runs TABLEUPDATE and releases the form
				toForm.cntCustomerInfo.txtCustomer_ID.Value = "BASEL"
				toForm.cntCustomerInfo.txtContact_Name.Value = "Baseline Reviewer"
				toForm.cntCustomerInfo.txtMax_Ord_Amt.Value = 5000
				toForm.cntCustomerInfo.txtMin_Ord_Amt.Value = 0
				this.Wait(0.4)
				this.CaptureForm(toForm, tcId, "ID BASEL, contact, maximum 5000, minimum 0 typed", "filled")
				toForm.cmdOK.Click()
				this.Wait(0.8)
				RETURN .T.
			CASE tcId == "chngpswd"
				*-- old password from the Hint box, new and confirm equal: OK saves and releases
				toForm.txtOldPassword.Value = toForm.txtHint.Value
				toForm.txtOldPassword.InteractiveChange()
				toForm.txtNewPassword.Value = "baseline"
				toForm.txtConfirm.Value = "baseline"
				this.Wait(0.4)
				this.CaptureForm(toForm, tcId, "old password typed, new and confirm both baseline", "filled")
				toForm.cmdOK.Click()
				this.Wait(0.8)
				RETURN .T.
			CASE tcId == "loginpicture"
				*-- Change Password edited employee record 1 (Buchanan) under
				*-- DEBUGMODE; the combo lists employees by name and opens on the
				*-- first name (Brid), so pick Buchanan as a user would
				LOCAL i
				FOR i = 1 TO toForm.cboName.ListCount
					IF LEFT(toForm.cboName.List(i), 8) == "Buchanan"
						toForm.cboName.ListIndex = i
						toForm.cboName.InteractiveChange()
						EXIT
					ENDIF
				ENDFOR
				this.Log("login: combo shows '" + ALLTRIM(toForm.cboName.DisplayValue) + "', value '" + TRANSFORM(toForm.cboName.Value) + "'")
				toForm.txtPassword.Value = "baseline"
				this.Wait(0.3)
				this.CaptureForm(toForm, tcId, "Buchanan chosen, the password just set typed", "filled")
				toForm.cmdOk.Click()
				this.Wait(0.5)
				RETURN .T.
		ENDCASE
		RETURN .F.
	ENDPROC

	*-- Close a modal form the way its own buttons do. Returns what was pressed.
	PROCEDURE Dismiss(toForm)
		LOCAL lcClass, lcButton
		*-- an .scx form's Class is its parent class; its Name is its own
		lcClass = LOWER(toForm.Name)
		lcButton = ""
		DO CASE
			CASE lcClass = "introform"
				lcButton = "cmdContinue"
			CASE lcClass = "frmgettitle"
				toForm.chkAllTitles.Value = 1
				toForm.chkAllTitles.InteractiveChange()
				lcButton = "cmdOK"
			CASE lcClass = "form1" AND PEMSTATUS(toForm, "ctlDateRange", 5)
				lcButton = "cmdOK"      && getinv: empty range = every invoice
			CASE lcClass = "aboutbox"
				lcButton = "cmdOK"
			CASE PEMSTATUS(toForm, "cmdCancel", 5)
				lcButton = "cmdCancel"
			CASE PEMSTATUS(toForm, "cmdClose", 5)
				lcButton = "cmdClose"
			CASE PEMSTATUS(toForm, "cmdExit", 5)
				lcButton = "cmdExit"
			CASE PEMSTATUS(toForm, "cmdOK", 5)
				lcButton = "cmdOK"
		ENDCASE
		IF EMPTY(lcButton)
			toForm.Release()
			RETURN "Release()"
		ENDIF
		EVALUATE("toForm." + lcButton + ".Click()")
		RETURN lcButton + ".Click()"
	ENDPROC

	PROCEDURE Finish
		IF this.lDone
			RETURN
		ENDIF
		this.lDone = .T.
		this.Log("finish; " + TRANSFORM(this.nSeq) + " log rows")
		FCLOSE(this.nCsv)
		FCLOSE(this.nLog)
		STRTOFILE("done " + TTOC(DATETIME(), 3), this.cOut + "DONE.txt")
	ENDPROC
ENDDEFINE


*=====================================================================
*-- Fires during every modal Show(): captures the active modal form and
*-- presses the button that closes it.
DEFINE CLASS capsentinel AS timer
	Interval = 400
	Enabled = .F.
	lBusy = .F.

	PROCEDURE Timer
		LOCAL loForm, lcKey, lcId, lcHow, lcPressed, loCap
		IF this.lBusy
			RETURN
		ENDIF
		this.lBusy = .T.
		loCap = _SCREEN.oCap
		IF TYPE("_SCREEN.ActiveForm") = "O" AND !ISNULL(_SCREEN.ActiveForm)
			loForm = _SCREEN.ActiveForm
			*-- The two report parameter dialogs open while REPORT FORM runs;
			*-- timers reached one of them and not the other, so both are left
			*-- to run_capture.ps1, which snapshots them and presses Enter.
			IF PEMSTATUS(loForm, "WindowType", 5) AND loForm.WindowType = 1 ;
					AND loForm.Caption <> "Report Parameters"
				lcKey = "|" + TRANSFORM(loForm.HWnd) + "|"
				IF !(lcKey $ loCap.cHandled)
					loCap.cHandled = loCap.cHandled + lcKey
					lcId = IIF(EMPTY(loCap.cExpect), LOWER(loForm.Name), loCap.cExpect)
					lcHow = IIF(EMPTY(loCap.cExpect), "appeared on its own", "modal, see driver row")
					loCap.cExpect = ""
					loCap.Log("sentinel: modal " + loForm.Name + " (" + loForm.Class + ") '" + loForm.Caption + "' as " + lcId)
					loCap.Wait(0.8)
					loCap.CaptureForm(loForm, lcId, lcHow, "")
					IF LOWER(loForm.Name) = "frmreports"
						*-- second state of the picker: Listings
						loForm.opgOutputType.Value = 2
						loForm.opgOutputType.Click()
						loCap.Wait(0.5)
						loCap.CaptureForm(loForm, lcId, lcHow, "listings")
					ENDIF
					IF loCap.cPass <> "click" AND loCap.Scenario(loForm, lcId) AND TYPE("loForm.Name") <> "C"
						loCap.Log("sentinel: scenario closed " + lcId)
					ELSE
						*-- the scenario did not close it (a refused OK, a wrong password): close it as usual
						lcPressed = loCap.Dismiss(loForm)
						loCap.Log("sentinel: dismissed " + lcId + " with " + lcPressed)
					ENDIF
				ENDIF
			ENDIF
		ENDIF
		this.lBusy = .F.
	ENDPROC
ENDDEFINE


*=====================================================================
*-- Runs the capture sequence one step per tick once the application's
*-- READ EVENTS is live (public oApp exists and the intro form is gone).
DEFINE CLASS capdriver AS timer
	Interval = 800
	Enabled = .F.
	lBusy = .F.
	nStep = 0
	nSteps = 0
	DIMENSION aSteps[1, 3]

	PROCEDURE Init
		IF _SCREEN.oCap.cPass == "save"
			this.AddStep("save-customer", "customer", 'oApp.DoForm("customer"); Contact Title changed; Save')
			this.AddStep("modal", "custadd", 'oApp.DoForm("custadd", "Baseline Capture Co."); ID BASEL; OK saves')
			this.AddStep("save-order", "ordentry", 'oApp.DoForm("ordentry"); AddNew; ALFKI, Chai x 150, shipper 1; Save; then (engine 70) a second order filled by Last Order > Add to current order')
			this.AddStep("modal", "chngpswd", 'oApp.DoForm("chngpswd"); old from the Hint box, new = confirm = baseline; OK saves')
			this.AddStep("retval", "loginpicture", 'oApp.DoFormRetVal("loginpicture"); password baseline; OK')
			this.AddStep("save-delete", "customer", 'oApp.DoForm("customer"); positioned on BASEL; Delete answered Yes')
			this.AddStep("done", "", "")
			RETURN
		ENDIF
		IF _SCREEN.oCap.cPass == "entry"
			this.AddStep("entry-customer", "customer", 'oApp.DoForm("customer"); Min Order Amount set above the maximum; Save; Restore')
			this.AddStep("entry-shipper", "shipper", 'oApp.DoForm("shipper"); Delete answered Yes (every shipper has orders; RI delete rule is restrict)')
			this.AddStep("entry-order", "ordentry", 'oApp.DoForm("ordentry"); AddNew; Save with no item; customer ALFKI and one line, quantity 1, Save (below minimum, No); Restore')
			this.AddStep("modal", "custadd", 'oApp.DoForm("custadd", "Baseline Capture Co."); cmdOK with an empty ID; Cancel')
			this.AddStep("modal", "chngpswd", 'oApp.DoForm("chngpswd"); old password from the Hint box, mismatched confirmation, cmdOK; Cancel')
			this.AddStep("modal", "chngpswd-empty", 'oApp.DoForm("chngpswd"); cmdOK with nothing entered; "abandon?" answered No')
			this.AddStep("retval", "loginpicture", 'oApp.DoFormRetVal("loginpicture"); wrong password, cmdOk; Cancel')
			*-- listempl: the runner sends Down then Enter in the title dialog
			this.AddStep("report", "listempl", "")
			this.AddStep("done", "", "")
			RETURN
		ENDIF
		*-- Non-modal forms, launched as the main menu does (menus\main.mn2).
		this.AddStep("form", "customer", 'oApp.DoForm("customer")')
		this.AddStep("form", "employee", 'oApp.DoForm("employee")')
		this.AddStep("form", "product", 'oApp.DoForm("product")')
		this.AddStep("form", "supplier", 'oApp.DoForm("supplier")')
		this.AddStep("form", "category", 'oApp.DoForm("category")')
		this.AddStep("form", "shipper", 'oApp.DoForm("shipper")')
		this.AddStep("form", "ordentry", 'oApp.DoForm("ordentry")')
		this.AddStep("form", "ordhist", 'oApp.DoForm("ordhist")')
		this.AddStep("form", "behindsc", 'oApp.DoForm("behindsc")')
		*-- Modal forms (.scx), launched as the menu or the calling form does.
		this.AddStep("modal", "reports", 'oApp.DoForm("reports") (menu: DO FORM Reports)')
		this.AddStep("modal", "chngpswd", 'oApp.DoForm("chngpswd") (menu: DO FORM chngpswd)')
		this.AddStep("modal", "rebuild", 'oApp.DoForm("rebuild") (menu: DO FORM rebuild)')
		this.AddStep("modal", "custadd", 'oApp.DoForm("custadd", "Baseline Capture Co.") (ordentry: DO FORM custadd WITH name TO llAdded)')
		this.AddStep("modal", "casestdy", 'oApp.DoForm("casestdy") (launched by nothing in the source)')
		*-- Modal forms that are classes, not .scx files.
		this.AddStep("retval", "loginpicture", 'oApp.DoFormRetVal("loginpicture") (skipped by the shipped DEBUGMODE build)')
		this.AddStep("retval", "findcustomer", 'oApp.DoFormRetVal("findcustomer") (as ordentry and ordhist do)')
		this.AddStep("retval", "findorder", 'oApp.DoFormRetVal("findorder") (as ordentry does)')
		this.AddStep("about", "about", 'CREATEOBJECT("AboutBox", ...).Show() (as Help > About does)')
		*-- Reports: cold REPORT FORM as the picker does, through a ReportListener.
		this.AddStep("report", "listcat", "")
		this.AddStep("report", "listcust", "")
		this.AddStep("report", "listempl", "")
		this.AddStep("report", "listprod", "")
		this.AddStep("report", "listship", "")
		this.AddStep("report", "listsupp", "")
		this.AddStep("report", "orders", "")
		this.AddStep("report", "salesdet", "")
		this.AddStep("report", "salessum", "")
		this.AddStep("report", "topcust", "")
		this.AddStep("report", "behindsc", "")
		this.AddStep("report", "casestdy", "")
		this.AddStep("report", "viewcode", "")
		this.AddStep("done", "", "")
	ENDPROC

	PROCEDURE AddStep(tcKind, tcId, tcHow)
		this.nSteps = this.nSteps + 1
		DIMENSION this.aSteps[this.nSteps, 3]
		this.aSteps[this.nSteps, 1] = tcKind
		this.aSteps[this.nSteps, 2] = tcId
		this.aSteps[this.nSteps, 3] = tcHow
	ENDPROC

	PROCEDURE Timer
		LOCAL loCap
		IF this.lBusy
			RETURN
		ENDIF
		this.lBusy = .T.
		loCap = _SCREEN.oCap
		DO CASE
			CASE this.nStep = 0
				*-- oApp is assigned after its Init (and the intro form) returns;
				*-- cUserLevel is protected, so it cannot be read from here.
				IF TYPE("oApp") = "O" AND !ISNULL(oApp) AND _SCREEN.FormCount = 0
					loCap.Log("application ready: CURDIR " + CURDIR() ;
						+ ", PATH " + SET("PATH") + ", DBC " + DBC() + ", menu bars " + TRANSFORM(CNTBAR("_MSYSMENU")))
					loCap.Wait(1.0)
					loCap.CaptureScreen("main", "main window after start-up, no form open")
					this.nStep = 1
				ENDIF
			CASE this.nStep <= this.nSteps
				this.RunStep(this.nStep)
				this.nStep = this.nStep + 1
			OTHERWISE
				this.Enabled = .F.
		ENDCASE
		this.lBusy = .F.
	ENDPROC

	PROCEDURE RunStep(tnStep)
		LOCAL lcKind, lcId, lcHow, loCap, loForm, luRet, loAbout, lnPage
		lcKind = this.aSteps[tnStep, 1]
		lcId = this.aSteps[tnStep, 2]
		lcHow = this.aSteps[tnStep, 3]
		loCap = _SCREEN.oCap
		loCap.Log("step " + TRANSFORM(tnStep) + " " + lcKind + " " + lcId)
		DO CASE
			CASE lcKind = "form"
				oApp.DoForm(lcId)
				loCap.Wait(1.2)
				IF TYPE("_SCREEN.ActiveForm") <> "O" OR ISNULL(_SCREEN.ActiveForm)
					loCap.Csv("form", lcId, "", "", "", lcHow, "", 0, "no form", "no active form after DoForm")
					RETURN
				ENDIF
				loForm = _SCREEN.ActiveForm
				loCap.CaptureForm(loForm, lcId, lcHow, "")
				loCap.CaptureScreen(lcId, "main window with " + loForm.Name + " open")
				loCap.CaptureToolbar()
				IF PEMSTATUS(loForm, "pageframe1", 5)
					FOR lnPage = 2 TO loForm.pageframe1.PageCount
						loForm.pageframe1.ActivePage = lnPage
						loCap.Wait(0.6)
						loCap.CaptureForm(loForm, lcId, lcHow + " page " + TRANSFORM(lnPage), "page" + TRANSFORM(lnPage))
					ENDFOR
					loForm.pageframe1.ActivePage = 1
				ENDIF
				IF LOWER(loForm.Name) = "frmbehindsc"
					*-- Show Code opens the modal viewcode form; the sentinel captures it.
					loCap.cExpect = "viewcode"
					loForm.cmdCode.Click()
					loCap.Wait(0.3)
				ENDIF
				loForm.Release()
				loForm = NULL
				loCap.Wait(0.6)
			CASE lcKind = "modal"
				loCap.cExpect = lcId
				DO CASE
					CASE lcId = "custadd"
						oApp.DoForm("custadd", "Baseline Capture Co.")
					CASE lcId = "chngpswd-empty"
						oApp.DoForm("chngpswd")
					OTHERWISE
						oApp.DoForm(lcId)
				ENDCASE
				loCap.Csv("driver", lcId, "", "", "", lcHow, "", 0, "returned", "")
				loCap.Wait(0.4)
			CASE lcKind = "retval"
				loCap.cExpect = lcId
				luRet = oApp.DoFormRetVal(lcId)
				loCap.Csv("driver", lcId, "", "", "", lcHow, "", 0, "returned", "uRetVal " + TRANSFORM(luRet))
				loCap.Wait(0.4)
			CASE lcKind = "about"
				loCap.cExpect = "about"
				SET CLASSLIB TO about ADDITIVE
				loAbout = CREATEOBJECT("AboutBox", TASTRADE_LOC, VERSION_LOC, COPYRIGHT_LOC, RIGHTSRSRVD_LOC, "BITMAPS\TTRADESM.BMP")
				loAbout.Show()
				loAbout = NULL
				RELEASE CLASSLIB about.vcx
				loCap.Csv("driver", "about", "", "", "", lcHow, "", 0, "returned", "")
				loCap.Wait(0.4)
			CASE lcKind = "save-customer"
				this.SaveCustomer(lcId, lcHow)
			CASE lcKind = "save-order"
				this.SaveOrder(lcId, lcHow)
			CASE lcKind = "save-delete"
				this.SaveDelete(lcId, lcHow)
			CASE lcKind = "entry-customer"
				this.EntryCustomer(lcId, lcHow)
			CASE lcKind = "entry-shipper"
				this.EntryShipper(lcId, lcHow)
			CASE lcKind = "entry-order"
				this.EntryOrder(lcId, lcHow)
			CASE lcKind = "report"
				IF loCap.cPass = "entry" AND lcId = "listempl"
					*-- the title dialog: as opened, OK prints every title (cTitle is
					*-- set only by the combo's InteractiveChange; the click pass shows
					*-- that). Down changes the combo interactively, then Enter is OK.
					loCap.Answer("KEYS:{DOWN}{ENTER}")
				ENDIF
				this.RunReport(lcId)
			CASE lcKind = "done"
				loCap.CaptureScreen("end", "main window after every form was released")
				loCap.Log("CLEAR EVENTS; " + TRANSFORM(loCap.nSeq) + " log rows; the application's shutdown and QUIT follow")
				STRTOFILE("captured " + TTOC(DATETIME(), 3), loCap.cOut + "CAPTURED.txt")
				CLEAR EVENTS
		ENDCASE
	ENDPROC

	*-- Open a non-modal form and return it, or NULL (logged).
	PROCEDURE OpenForm(tcId, tcHow)
		LOCAL loCap, loForm
		loCap = _SCREEN.oCap
		oApp.DoForm(tcId)
		loCap.Wait(1.2)
		IF TYPE("_SCREEN.ActiveForm") <> "O" OR ISNULL(_SCREEN.ActiveForm)
			loCap.Csv("form", tcId, "", "", "", tcHow, "", 0, "no form", "no active form after DoForm")
			RETURN NULL
		ENDIF
		loForm = _SCREEN.ActiveForm
		loCap.CaptureForm(loForm, tcId, tcHow, "before")
		RETURN loForm
	ENDPROC

	*-- A customer edit that the rules accept: Contact Title on ALFKI.
	PROCEDURE SaveCustomer(tcId, tcHow)
		LOCAL loCap, loForm, loCtl
		loCap = _SCREEN.oCap
		loForm = this.OpenForm(tcId, tcHow)
		IF ISNULL(loForm)
			RETURN
		ENDIF
		loCtl = loForm.pageframe1.page1.cntCustomerInfo.txtContact_Title
		loCtl.SetFocus()
		loCap.Log("customer: contact title was '" + ALLTRIM(loCtl.Value) + "', set to 'Baseline Reviewer'")
		loCtl.Value = "Baseline Reviewer"
		loCap.Wait(0.3)
		loCap.Log("customer: Save() returned " + TRANSFORM(loForm.Save()))
		loCap.Wait(0.8)
		loCap.CaptureForm(loForm, tcId, "after Save() of the changed Contact Title", "saved")
		loForm.Release()
		loCap.Wait(0.6)
	ENDPROC

	*-- A new order the rules accept, then (engine 70) one filled from Order History.
	PROCEDURE SaveOrder(tcId, tcHow)
		LOCAL loCap, loForm, loHist
		loCap = _SCREEN.oCap
		loForm = this.OpenForm(tcId, tcHow)
		IF ISNULL(loForm)
			RETURN
		ENDIF
		loForm.AddNew()
		loCap.Wait(0.8)
		loForm.cboCustomer_ID.Value = "ALFKI"
		loCap.Wait(0.8)
		*-- Chai at 18.00 times 150 = 2,700, less the 2% discount = 2,646, above the 2,600 minimum
		loCap.InSession(loForm, "SELECT products" + CHR(13) + "GO TOP" + CHR(13) ;
			+ "SELECT order_line_items" + CHR(13) ;
			+ "REPLACE product_id WITH products.product_id, unit_price WITH products.unit_price, quantity WITH 150" + CHR(13) ;
			+ "SELECT orders" + CHR(13) + "REPLACE shipper_id WITH '     1'")
		loForm.grdLineItems.Refresh()
		loForm.Refresh()
		loCap.Wait(0.6)
		loCap.CaptureForm(loForm, tcId, "new order: ALFKI, Chai x 150, shipper 1", "filled")
		loCap.Log("order: Save() returned " + TRANSFORM(loForm.Save()))
		loCap.Wait(0.8)
		loCap.CaptureForm(loForm, tcId, "after Save(): the order and its line committed", "saved")
		IF loCap.nEngine = 70
			*-- second order: Last Order opens Order History linked to this form;
			*-- tag its first history line and Add to Current Order
			loForm.AddNew()
			loCap.Wait(0.8)
			loForm.cboCustomer_ID.Value = "ALFKI"
			loCap.Wait(0.8)
			loForm.cmdLastOrder.Click()
			loCap.Wait(1.5)
			IF TYPE("_SCREEN.ActiveForm") = "O" AND !ISNULL(_SCREEN.ActiveForm) AND LOWER(_SCREEN.ActiveForm.Name) = "frmordhistory"
				loHist = _SCREEN.ActiveForm
				loCap.CaptureForm(loHist, "ordhist", "Last Order from Order Entry: Order History linked to the new order", "linked")
				loCap.InSession(loHist, "SELECT citems" + CHR(13) + "GO TOP" + CHR(13) + "REPLACE exp_1 WITH .T.")
				loHist.grdLineItems.Refresh()
				loCap.Wait(0.5)
				loCap.CaptureForm(loHist, "ordhist", "first line of the shown order tagged", "tagged")
				loHist.cmdAddToCurrentOrder.Click()
				loCap.Wait(1.0)
				loCap.CaptureForm(loForm, tcId, "after Add to Current Order: the historical line copied in", "copied")
				loCap.InSession(loForm, "SELECT orders" + CHR(13) + "REPLACE shipper_id WITH '     1'")
				loForm.Refresh()
				loCap.Log("order: Save() of the copied order returned " + TRANSFORM(loForm.Save()))
				loCap.Wait(0.8)
				loCap.CaptureForm(loForm, tcId, "after Save() of the copied order (refused if below the minimum, answered No)", "copied-saved")
				loForm.Restore()
				loCap.Wait(0.5)
			ELSE
				loCap.Csv("driver", "ordhist", "", "", "", "cmdLastOrder.Click()", "", 0, "no form", "Order History did not become the active form")
				loForm.Restore()
			ENDIF
		ELSE
			loCap.Csv("driver", "ordhist", "", "", "", "skipped", "", 0, "skipped", "Order History does not open under ENGINEBEHAVIOR 90 (its view fails); the item copy runs with -Engine 70")
		ENDIF
		loForm.Release()
		loCap.Wait(0.6)
	ENDPROC

	*-- Delete the customer BASEL added earlier (no orders, so the RI rule allows it).
	PROCEDURE SaveDelete(tcId, tcHow)
		LOCAL loCap, loForm
		loCap = _SCREEN.oCap
		loForm = this.OpenForm(tcId, tcHow)
		IF ISNULL(loForm)
			RETURN
		ENDIF
		loCap.InSession(loForm, "SELECT customer" + CHR(13) + "SEEK 'BASEL'")
		loForm.RefreshForm()
		loCap.Wait(0.6)
		loCap.CaptureForm(loForm, tcId, "positioned on BASEL, the customer added in this run", "positioned")
		loCap.Answer("Yes")
		loCap.Log("customer: Delete() of BASEL returned " + TRANSFORM(loForm.Delete()))
		loCap.Wait(1.0)
		loCap.CaptureForm(loForm, tcId, "after Delete() confirmed Yes: BASEL gone, next record shown", "deleted")
		loForm.Release()
		loCap.Wait(0.6)
	ENDPROC

	*-- Field rule: min_order_amt <= max_order_amt on the customer table.
	PROCEDURE EntryCustomer(tcId, tcHow)
		LOCAL loCap, loForm, loCtl
		loCap = _SCREEN.oCap
		loForm = this.OpenForm(tcId, tcHow)
		IF ISNULL(loForm)
			RETURN
		ENDIF
		loCtl = loForm.pageframe1.page1.cntCustomerInfo.txtMin_Ord_Amt
		loCtl.SetFocus()
		loCap.Log("customer: max " + TRANSFORM(loForm.pageframe1.page1.cntCustomerInfo.txtMax_Ord_Amt.Value) ;
			+ ", min was " + TRANSFORM(loCtl.Value) + ", set to 999999")
		loCtl.Value = 999999
		loCap.Wait(0.3)
		loCap.CaptureForm(loForm, tcId, "Min Order Amount typed as 999999, above the maximum", "typed")
		loCap.Log("customer: Save() returned " + TRANSFORM(loForm.Save()))
		loCap.Wait(0.8)
		loCap.CaptureForm(loForm, tcId, "after Save() with the rule min_order_amt <= max_order_amt violated", "rule")
		loForm.Restore()
		loCap.Wait(0.6)
		loCap.CaptureForm(loForm, tcId, "after Restore()", "restored")
		loForm.Release()
		loCap.Wait(0.6)
	ENDPROC

	*-- Referential integrity: deleting a shipper that has orders is refused.
	PROCEDURE EntryShipper(tcId, tcHow)
		LOCAL loCap, loForm
		loCap = _SCREEN.oCap
		loForm = this.OpenForm(tcId, tcHow)
		IF ISNULL(loForm)
			RETURN
		ENDIF
		loCap.Answer("Yes")
		loCap.Log("shipper: Delete() returned " + TRANSFORM(loForm.Delete()))
		loCap.Wait(1.0)
		loCap.CaptureForm(loForm, tcId, "after Delete() confirmed Yes: the RI delete trigger (restrict) refused it", "delete-refused")
		loForm.Release()
		loCap.Wait(0.6)
	ENDPROC

	*-- A new order: saved empty (no line item), then with one line below the
	*-- customer's minimum, then (engine 70 only) far over the credit limit.
	PROCEDURE EntryOrder(tcId, tcHow)
		LOCAL loCap, loForm
		loCap = _SCREEN.oCap
		loForm = this.OpenForm(tcId, tcHow)
		IF ISNULL(loForm)
			RETURN
		ENDIF
		loForm.AddNew()
		loCap.Wait(0.8)
		loCap.CaptureForm(loForm, tcId, "after AddNew(): blank order, DBC defaults for id, number, dates, employee", "new")
		loCap.Log("order: Save() with no item returned " + TRANSFORM(loForm.Save()))
		loCap.Wait(0.8)
		loCap.CaptureForm(loForm, tcId, "after Save() with no customer and no line item (ValOrder)", "noitems")
		*-- customer through the combo (its ProgrammaticChange runs, as the app's does)
		loForm.cboCustomer_ID.Value = "ALFKI"
		loCap.Wait(0.8)
		*-- one line, the first product, quantity 1 (what cboProduct.InteractiveChange does)
		loCap.InSession(loForm, "SELECT products" + CHR(13) + "GO TOP" + CHR(13) ;
			+ "SELECT order_line_items" + CHR(13) ;
			+ "REPLACE product_id WITH products.product_id, unit_price WITH products.unit_price, quantity WITH 1" + CHR(13) ;
			+ "SELECT orders")
		loForm.grdLineItems.Refresh()
		loForm.Refresh()
		loCap.Wait(0.6)
		loCap.CaptureForm(loForm, tcId, "customer ALFKI (minimum order 2,600) and one line, quantity 1", "filled")
		loCap.Log("order: Save() below the minimum returned " + TRANSFORM(loForm.Save()))
		loCap.Wait(0.8)
		loCap.CaptureForm(loForm, tcId, 'after Save() below the customer minimum: "Save anyway?" answered No', "belowmin")
		IF loCap.nEngine = 70
			*-- RemainingCredit counts saved unpaid orders only, so a new order of
			*-- any size passes unless the customer is already over: CACTU is
			*-- (maximum 5,800, unpaid orders 18,028, minimum 0)
			loForm.cboCustomer_ID.Value = "CACTU"
			loCap.Wait(0.8)
			loForm.Refresh()
			loCap.Wait(0.4)
			loCap.CaptureForm(loForm, tcId, "customer CACTU, already over its maximum by 12,228 on saved unpaid orders", "filled-over")
			loCap.Log("order: Save() for a customer over the credit limit returned " + TRANSFORM(loForm.Save()))
			loCap.Wait(0.8)
			loCap.CaptureForm(loForm, tcId, 'after Save() with the customer over the limit: "Save anyway?" answered No', "overcredit")
			loForm.cboCustomer_ID.Value = "ALFKI"
			loCap.Wait(0.8)
		ELSE
			loCap.Log("order: over-credit step skipped under ENGINEBEHAVIOR " + TRANSFORM(loCap.nEngine) ;
				+ ": RemainingCredit errors inside ValOrder, so the refusal is not certain and the order could be saved")
			loCap.Csv("driver", "ordentry-overcredit", "", "", "", "skipped", "", 0, "skipped", ;
				"under ENGINEBEHAVIOR 90 the credit check itself errors (RemainingCredit), so an over-credit save could go through; run with -Engine 70")
		ENDIF
		*-- quantity 100000 passes the minimum; the order has no shipper, so the
		*-- orders-to-shippers insert trigger (restrict) refuses it under both engines
		loCap.InSession(loForm, "SELECT order_line_items" + CHR(13) + "REPLACE quantity WITH 100000" + CHR(13) + "SELECT orders")
		loForm.grdLineItems.Refresh()
		loForm.Refresh()
		loCap.Wait(0.6)
		loCap.CaptureForm(loForm, tcId, "customer ALFKI, quantity 100000 (above the minimum), no shipper", "filled-noshipper")
		loCap.Log("order: Save() with no shipper returned " + TRANSFORM(loForm.Save()))
		loCap.Wait(0.8)
		loCap.CaptureForm(loForm, tcId, "after Save() with no shipper: the RI insert trigger refused it", "noshipper")
		loForm.Restore()
		loCap.Wait(0.6)
		loCap.CaptureForm(loForm, tcId, "after Restore(): the new order and its line reverted", "restored")
		loForm.Release()
		loCap.Wait(0.6)
	ENDPROC

	*-- Cold REPORT FORM, as the picker's cmdRun does, into a page-rendering
	*-- listener; first CAP_MAXPAGES pages go to reports\<id>-pN.png.
	PROCEDURE RunReport(tcId)
		LOCAL loCap, loListener, lcFrx, lnPages, lnPage, lcFile, lcEmf, lcNote, lcStatus, loEx, lcClause
		LOCAL laBefore[1], laAfter[1], lnBefore, lnAfter, i, j, llFound, lcHow
		loCap = _SCREEN.oCap
		lcFrx = CAP_ROOT + "reports\" + tcId + ".frx"
		lcNote = ""
		lcClause = ""
		lcHow = "REPORT FORM reports\" + tcId + ".frx OBJECT ReportListener (ListenerType 3, pages as EMF), as the picker runs it"
		lnBefore = AUSED(laBefore)
		DO CASE
			CASE tcId = "behindsc"
				*-- frmbehindsc prints NEXT 1 from its behindsc alias
				USE (CAP_ROOT + "data\behindsc.dbf") ALIAS behindsc IN 0 SHARED
				SELECT behindsc
				GO TOP
				lcClause = "NEXT 1"
				lcHow = "REPORT FORM behindsc NEXT 1 (as frmbehindsc.cmdPrint does) into a ReportListener"
				lcNote = "harness opened data\behindsc.dbf, first record"
			CASE tcId = "viewcode"
				*-- frmviewcode prints the one-row cursor frmbehindsc builds
				CREATE CURSOR viewcode (code M)
				APPEND BLANK
				REPLACE code WITH FILETOSTR(CAP_ROOT + "progs\main.prg")
				lcHow = "REPORT FORM viewcode (as frmviewcode.cmdPrint does) into a ReportListener"
				lcNote = "harness supplied cursor viewcode with progs\main.prg as its text"
			CASE tcId = "orders"
				loCap.cExpect = "getinv"
			CASE tcId = "listempl"
				loCap.cExpect = "gettitle"
		ENDCASE
		loListener = CREATEOBJECT("ReportListener")
		loListener.ListenerType = 3
		loListener.QuietMode = .T.
		lnPages = 0
		lcStatus = "ok"
		TRY
			IF EMPTY(lcClause)
				REPORT FORM (lcFrx) OBJECT loListener
			ELSE
				REPORT FORM (lcFrx) NEXT 1 OBJECT loListener
			ENDIF
			lnPages = loListener.PageTotal
			FOR lnPage = 1 TO MIN(lnPages, CAP_MAXPAGES)
				lcFile = loCap.cOut + "reports\" + tcId + "-p" + TRANSFORM(lnPage) + ".png"
				IF FILE(lcFile)
					ERASE (lcFile)
				ENDIF
				*-- EMF (device type 100) is the whole page as vectors; the PNG
				*-- device type came back half-size and clipped on this desktop.
				*-- emf2png.ps1 rasterises it at 2x (1632 by 2112 for Letter).
				lcEmf = FORCEEXT(lcFile, "emf")
				IF FILE(lcEmf)
					ERASE (lcEmf)
				ENDIF
				loListener.OutputPage(lnPage, lcEmf, 100)
				IF FILE(lcEmf)
					loCap.Emf2Png(lcEmf, lcFile)
					ERASE (lcEmf)
				ENDIF
				IF !FILE(lcFile)
					lcStatus = "page missing"
				ENDIF
			ENDFOR
			IF lnPages = 0
				lcStatus = "no pages"
			ENDIF
		CATCH TO loEx
			lcStatus = "error"
			lcNote = lcNote + IIF(EMPTY(lcNote), "", "; ") + TRANSFORM(loEx.ErrorNo) + " " + loEx.Message ;
				+ " (" + loEx.Procedure + " line " + TRANSFORM(loEx.LineNo) + ")"
		ENDTRY
		loCap.cExpect = ""
		loListener = NULL
		loCap.Csv("report", tcId, "", "", "", lcHow, ;
			IIF(lnPages > 0, "reports/" + tcId + "-p1.png", ""), lnPages, lcStatus, lcNote)
		*-- close whatever the report opened in this data session
		lnAfter = AUSED(laAfter)
		FOR i = 1 TO lnAfter
			llFound = .F.
			FOR j = 1 TO lnBefore
				IF laAfter[i, 1] == laBefore[j, 1]
					llFound = .T.
					EXIT
				ENDIF
			ENDFOR
			IF !llFound AND USED(laAfter[i, 1])
				USE IN (laAfter[i, 1])
			ENDIF
		ENDFOR
		loCap.Wait(0.3)
	ENDPROC
ENDDEFINE
