param(
    [int] $TimeoutSec = 1200,
    [int] $Engine = 0,               # SET ENGINEBEHAVIOR to force; 0 = VFP 9 default (90)
    [string] $OutDir = 'baseline',   # output folder under the repo root
    [string] $Pass = 'click'         # 'click' (open and close everything) or 'entry' (data-entry scenarios)
)
# Runs the Tastrade baseline capture: starts a visible VFP 9 with a config file
# whose COMMAND DOes tools\baseline\capture.prg, then watches the VFP process for
# Win32 message boxes (#32770 dialogs). Each one is screenshotted to
# baseline\dialogs\, its title, text, and buttons are logged to
# baseline\dialogs.csv, and the button that lets the run continue is pressed
# (Ignore > OK > No > Cancel > Yes > first). A watchdog kills the VFP instance
# this script started, and only that one, if the harness has not finished in
# time.
#
# The harness's own outputs: baseline\forms, baseline\screen, baseline\reports,
# baseline\CAPTURE-LOG.csv, baseline\capture.log, and CAPTURED.txt when the
# sequence is complete (the harness then CLEAR EVENTS, the EXE shuts down, VFP quits).
$ErrorActionPreference = 'Stop'
$root  = 'C:\fox\tastrade'
$tools = "$root\tools\baseline"
$out   = "$root\$OutDir"
$vfp   = 'C:\Program Files (x86)\Microsoft Visual FoxPro 9\vfp9.exe'

$signature = @'
public delegate bool EnumProc(IntPtr hWnd, IntPtr lParam);
[DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr lParam);
[DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr parent, EnumProc cb, IntPtr lParam);
[DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern int GetClassName(IntPtr hWnd, System.Text.StringBuilder sb, int max);
[DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint pid);
[DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder sb, int max);
[DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
[DllImport("user32.dll")] public static extern bool IsWindow(IntPtr hWnd);
[DllImport("user32.dll")] public static extern int GetDlgCtrlID(IntPtr hWnd);
[DllImport("user32.dll")] public static extern bool PostMessage(IntPtr hWnd, uint msg, IntPtr wParam, IntPtr lParam);
[DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
[DllImport("user32.dll")] public static extern IntPtr GetAncestor(IntPtr hWnd, uint gaFlags);
[StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
[DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
'@
Add-Type -AssemblyName System.Windows.Forms
$u32 = Add-Type -MemberDefinition $signature -Name 'U32' -Namespace 'Cap' -PassThru

function Get-Text([IntPtr] $h) {
    $sb = New-Object System.Text.StringBuilder 4096
    [void][Cap.U32]::GetWindowText($h, $sb, $sb.Capacity)
    return $sb.ToString()
}
function Get-Class([IntPtr] $h) {
    $sb = New-Object System.Text.StringBuilder 256
    [void][Cap.U32]::GetClassName($h, $sb, $sb.Capacity)
    return $sb.ToString()
}
# EnumWindows/EnumChildWindows with callbacks: FindWindowEx(NULL, ..., '#32770')
# returned nothing for a MessageBox on this Windows 11 build, and FindWindowEx
# by child class stopped after the first Static.
function Get-TopWindows {
    $list = New-Object System.Collections.ArrayList
    $cb = [Cap.U32+EnumProc]{ param($h, $l); [void]$list.Add($h); $true }
    [void][Cap.U32]::EnumWindows($cb, [IntPtr]::Zero)
    return @($list)
}
function Get-Children([IntPtr] $parent, [string] $cls) {
    $list = New-Object System.Collections.ArrayList
    $cb = [Cap.U32+EnumProc]{ param($h, $l); if ((Get-Class $h) -eq $cls) { [void]$list.Add($h) }; $true }
    [void][Cap.U32]::EnumChildWindows($parent, $cb, [IntPtr]::Zero)
    return @($list)
}
function Get-Descendants([IntPtr] $parent) {
    $list = New-Object System.Collections.ArrayList
    $cb = [Cap.U32+EnumProc]{ param($h, $l); [void]$list.Add($h); $true }
    [void][Cap.U32]::EnumChildWindows($parent, $cb, [IntPtr]::Zero)
    return @($list)
}
function Csv-Quote($v) { return '"' + ([string]$v).Replace('"', '""') + '"' }
# The harness writes ANSWER.txt before an action whose dialog needs a specific
# button (e.g. "Yes" on a delete confirmation) or keystrokes in a VFP form
# ("KEYS:{TAB} {ENTER}"). One use, then the file is removed.
function Read-Answer {
    $p = "$out\ANSWER.txt"
    if (-not (Test-Path $p)) { return '' }
    $a = (Get-Content $p -Raw).Trim()
    Remove-Item $p -Force
    return $a
}
# A window can vanish between the check and the shot; snap.ps1 then writes an
# error to stderr, which PowerShell 5.1 under -ErrorAction Stop turns into a
# terminating error (run 4 ended that way, and the finally block killed VFP).
function Snap-Safe([long] $hwnd, [string] $file) {
    $ErrorActionPreference = 'Continue'
    try {
        $r = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$tools\snap.ps1" -Hwnd $hwnd -OutFile $file 2>&1
        if ($LASTEXITCODE -ne 0 -or -not (Test-Path $file)) { Write-Host "snap of $hwnd failed: $r"; return $false }
        return $true
    } catch { Write-Host "snap of $hwnd failed: $($_.Exception.Message)"; return $false }
}

# The config file VFP starts with: capture.fpw is the template, the COMMAND line
# gets this run's parameters.
$fpw = "$tools\capture-run.fpw"
$cmd = "COMMAND=DO $tools\capture.prg WITH $Engine, `"$OutDir`", `"$Pass`""
Set-Content -Path $fpw -Value @($cmd, 'RESOURCE=OFF', 'SCREEN=ON') -Encoding ascii

# Fresh output folders (the harness writes into them; nothing else lives here).
if (-not (Test-Path $out)) { New-Item -ItemType Directory -Force -Path $out | Out-Null }
foreach ($d in 'forms', 'screen', 'reports', 'dialogs') {
    $p = Join-Path $out $d
    if (Test-Path $p) { Remove-Item "$p\*" -Force }
    else { New-Item -ItemType Directory -Force -Path $p | Out-Null }
}
foreach ($f in 'CAPTURED.txt', 'ANSWER.txt', 'dialogs.csv', 'capture.log', 'CAPTURE-LOG.csv') {
    $p = Join-Path $out $f
    if (Test-Path $p) { Remove-Item $p -Force }
}
Set-Content -Path "$out\dialogs.csv" -Value 'seq,time,title,text,buttons,pressed,file' -Encoding utf8

# The application writes window positions into tastrade.ini as forms close;
# start from the committed file so the baseline does not depend on a prior run.
& git -C $root checkout -- tastrade.ini

$started = Get-Date
$p = Start-Process -FilePath $vfp -ArgumentList "-c`"$fpw`"" -WorkingDirectory $root -PassThru
Write-Host "vfp9.exe PID $($p.Id) started $($started.ToString('HH:mm:ss'))"

$seen = @{}
$seq = 0
$captured = $false
$formKeyed = @{}   # hwnd -> time the keys were sent; a second Enter if still up 6 s later
try {
    while ($true) {
        if ($p.HasExited) { Write-Host 'VFP exited.'; break }
        if (-not $captured -and (Test-Path "$out\CAPTURED.txt")) { $captured = $true; Write-Host 'Capture sequence complete; waiting for shutdown.' }
        if (((Get-Date) - $started).TotalSeconds -gt $TimeoutSec) {
            Write-Host "Watchdog: $TimeoutSec s elapsed, killing PID $($p.Id)."
            Stop-Process -Id $p.Id -Force
            break
        }
        if ($captured -and ((Get-Date) - $started).TotalSeconds -gt 0 -and (Test-Path "$out\CAPTURED.txt")) {
            $age = ((Get-Date) - (Get-Item "$out\CAPTURED.txt").LastWriteTime).TotalSeconds
            if ($age -gt 60) { Write-Host 'No shutdown 60 s after capture; killing our VFP.'; Stop-Process -Id $p.Id -Force; break }
        }

        # forget dialogs whose windows are gone
        foreach ($k in @($seen.Keys)) { if (-not [Cap.U32]::IsWindow([IntPtr][long]$k)) { $seen.Remove($k) } }

        foreach ($h in Get-TopWindows) {
            if ((Get-Class $h) -ne '#32770') { continue }
            $pid_ = [uint32]0
            [void][Cap.U32]::GetWindowThreadProcessId($h, [ref]$pid_)
            if ($pid_ -ne $p.Id) { continue }
            if (-not [Cap.U32]::IsWindowVisible($h)) { continue }
            $key = [string][long]$h
            if ($seen.ContainsKey($key)) { continue }
            $seen[$key] = $true

            Start-Sleep -Milliseconds 500
            $seq++
            $title = Get-Text $h
            $texts = @(Get-Children $h 'Static' | ForEach-Object { Get-Text $_ } | Where-Object { $_ -ne '' })
            $buttons = @(Get-Children $h 'Button')
            $captions = @($buttons | ForEach-Object { (Get-Text $_).Replace('&', '') })
            $file = "dialogs\{0:d2}.png" -f $seq
            [void](Snap-Safe ([long]$h) "$out\$file")

            $pick = -1
            $prefer = @('Ignore', 'OK', 'No', 'Cancel', 'Yes')
            $answer = Read-Answer
            if ($answer -and -not $answer.StartsWith('KEYS:')) { $prefer = @($answer) + $prefer }
            foreach ($want in $prefer) {
                $i = [array]::IndexOf($captions, $want)
                if ($i -ge 0) { $pick = $i; break }
            }
            if ($pick -lt 0 -and $buttons.Count -gt 0) { $pick = 0 }
            $pressed = ''
            if ($pick -ge 0) {
                $hb = $buttons[$pick]
                $id = [Cap.U32]::GetDlgCtrlID($hb)
                [void][Cap.U32]::PostMessage($h, 0x0111, [IntPtr]$id, $hb)   # WM_COMMAND, BN_CLICKED
                $pressed = $captions[$pick]
            }
            $line = ($seq, (Csv-Quote (Get-Date).ToString('HH:mm:ss')), (Csv-Quote $title), (Csv-Quote ($texts -join ' | ')), (Csv-Quote ($captions -join '/')), (Csv-Quote $pressed), (Csv-Quote $file)) -join ','
            Add-Content -Path "$out\dialogs.csv" -Value $line -Encoding utf8
            Write-Host "dialog $seq '$title': $($texts -join ' | ') [$($captions -join '/')] -> $pressed"
        }

        # The two report parameter dialogs (forms/getinv.scx, forms/gettitle.scx)
        # open from a report's data environment while REPORT FORM runs, and VFP
        # does not fire timers then, so the in-process sentinel never sees them.
        # They are child windows of the main window titled "Report Parameters";
        # OK is the default button on both, so Enter from outside accepts them.
        foreach ($top in Get-TopWindows) {
            $pid_ = [uint32]0
            [void][Cap.U32]::GetWindowThreadProcessId($top, [ref]$pid_)
            if ($pid_ -ne $p.Id) { continue }
            foreach ($h in Get-Descendants $top) {
                if (-not [Cap.U32]::IsWindowVisible($h)) { continue }
                if ((Get-Text $h) -ne 'Report Parameters') { continue }
                $key = [string][long]$h
                if ($seen.ContainsKey($key)) {
                    if ($formKeyed.ContainsKey($key) -and ((Get-Date) - $formKeyed[$key]).TotalSeconds -gt 6) {
                        Write-Host "form dialog $key still up 6 s after the keys; pressing Enter"
                        [void][Cap.U32]::SetForegroundWindow([Cap.U32]::GetAncestor($h, 2))
                        Start-Sleep -Milliseconds 200
                        [System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
                        $formKeyed[$key] = Get-Date
                    }
                    continue
                }
                $seen[$key] = $true
                Start-Sleep -Milliseconds 800
                if (-not ([Cap.U32]::IsWindow($h) -and [Cap.U32]::IsWindowVisible($h))) { continue }
                $r = New-Object Cap.U32+RECT
                [void][Cap.U32]::GetWindowRect($h, [ref]$r)
                $wid = $r.Right - $r.Left
                # getinv is 261 wide by design, gettitle 302; GetWindowRect here reports
                # 267 and 308 (run 3), so this thread sees the app's own pixels
                $id = if ($wid -lt 285) { 'getinv' } else { 'gettitle' }
                $file = "forms\$id.png"
                if (-not (Snap-Safe ([long]$h) "$out\$file")) { continue }
                if (-not ([Cap.U32]::IsWindow($h) -and [Cap.U32]::IsWindowVisible($h))) { continue }
                [void][Cap.U32]::SetForegroundWindow([Cap.U32]::GetAncestor($h, 2))
                Start-Sleep -Milliseconds 200
                $keys = '{ENTER}'
                $answer = Read-Answer
                if ($answer.StartsWith('KEYS:')) { $keys = $answer.Substring(5) }
                [System.Windows.Forms.SendKeys]::SendWait($keys)
                $formKeyed[$key] = Get-Date
                $seq++
                $line = ($seq, (Csv-Quote (Get-Date).ToString('HH:mm:ss')), (Csv-Quote 'Report Parameters'), (Csv-Quote "VFP form $id opened by a report data environment; width $wid px on screen"), (Csv-Quote 'OK (default)/Cancel'), (Csv-Quote $keys), (Csv-Quote $file)) -join ','
                Add-Content -Path "$out\dialogs.csv" -Value $line -Encoding utf8
                Write-Host "form dialog $seq 'Report Parameters' as $id -> Enter"
            }
        }
        Start-Sleep -Milliseconds 400
    }
} finally {
    if (-not $p.HasExited) {
        Write-Host 'Waiting up to 30 s for VFP to quit...'
        if (-not $p.WaitForExit(30000)) { Write-Host "Killing our VFP PID $($p.Id)."; Stop-Process -Id $p.Id -Force }
    }
    & git -C $root checkout -- tastrade.ini
    # The application stamps table headers (last-update date) when forms open
    # them for writing; report what changed under data\ so it can be restored
    # or examined before anything is committed.
    $changed = & git -C $root status --short -- data
    if ($changed) { Write-Host "Files under data\ changed by the run (git status):"; $changed | ForEach-Object { Write-Host "  $_" } }
}
$elapsed = [int]((Get-Date) - $started).TotalSeconds
Write-Host "Elapsed $elapsed s."
if (Test-Path "$out\capture.log") {
    Write-Host '--- capture.log (tail) ---'
    Get-Content "$out\capture.log" -Tail 40
}
