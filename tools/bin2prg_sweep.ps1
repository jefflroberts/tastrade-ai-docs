# FoxBin2PRG sweep: convert every VFP source binary in this repo to its text twin.
#
# Drives FoxBin2PRG in-process through the Visual FoxPro 9 COM server, the same way
# the tool's own convert_vfp9_bin_2_prg.vbs does. This gives a synchronous return
# code per file, unlike foxbin2prg.exe, which is a GUI-subsystem program that returns
# before it finishes.
#
# Direction is BIN2PRG only. The binaries are never written; the sweep verifies that
# with `git status` afterwards.
#
# Usage:  powershell -ExecutionPolicy Bypass -File tools\bin2prg_sweep.ps1
# Output: <ext>2 twin beside each binary, tools\bin2prg_sweep.log, and a copy of
#         FoxBin2PRG's own error log at tools\FoxBin2Prg_Error.LOG when one is produced.

$ErrorActionPreference = 'Stop'
$exe  = 'C:\fox\Thor\Thor\Tools\Components\FoxBin2PRG\foxbin2prg.exe'
$root = Split-Path $PSScriptRoot -Parent
$log  = Join-Path $PSScriptRoot 'bin2prg_sweep.log'
$twin = @{ '.scx'='.sc2'; '.vcx'='.vc2'; '.frx'='.fr2'; '.mnx'='.mn2'; '.pjx'='.pj2'; '.dbc'='.dc2'; '.lbx'='.lb2' }

$targets = Get-ChildItem $root -Recurse -Include *.scx,*.vcx,*.frx,*.mnx,*.pjx,*.dbc,*.lbx -File |
           Sort-Object FullName

$errLog = Join-Path $env:TEMP 'FoxBin2Prg_Error.LOG'
if (Test-Path $errLog) { Remove-Item $errLog -Force }

"sweep start $(Get-Date -Format s)  root=$root  targets=$($targets.Count)  tool=$exe" | Set-Content $log

$vfp = New-Object -ComObject 'VisualFoxPro.Application.9'
$vfp.Visible = $false
$vfp.DoCmd("SET PROCEDURE TO '$exe'")
$vfp.DoCmd("PUBLIC oFoxBin2prg")
$vfp.DoCmd("oFoxBin2prg = CREATEOBJECT('c_foxbin2prg')")
$ver = $vfp.Eval("oFoxBin2prg.c_FB2PRG_EXE_Version")
Add-Content $log "FoxBin2PRG version: $ver"

$ok = 0; $fail = 0; $rows = @()
foreach ($f in $targets) {
    $rel = $f.FullName.Substring($root.Length + 1)
    $t   = [System.IO.Path]::ChangeExtension($f.FullName, $twin[$f.Extension.ToLower()])
    if (Test-Path $t) { Remove-Item $t -Force }

    # execute(tc_InputFile, tcType, tcTextName, tlGenText, tcDontShowErrors, tcDebug,
    #         tcDontShowProgress, toModulo, toEx, tlRelanzarError, tcOriginalFileName,
    #         tcRecompile, tcNoTimestamps)
    # '1' for DontShowErrors keeps it headless; '1' for NoTimestamps makes twins deterministic;
    # '0' for Recompile so nothing is regenerated or compiled.
    $cmd = "oFoxBin2prg.execute(""$($f.FullName)"",'BIN2PRG','0','0','1','0','1','','',.F.,'','0','1')"
    $sw  = [System.Diagnostics.Stopwatch]::StartNew()
    try   { $rc = $vfp.Eval($cmd) } catch { $rc = "EXC: $($_.Exception.Message)" }
    $sw.Stop()

    $made = Test-Path $t
    $size = if ($made) { (Get-Item $t).Length } else { 0 }
    $status = if ($made -and $rc -eq 0) { 'OK' } else { 'FAIL' }
    if ($status -eq 'OK') { $ok++ } else { $fail++ }
    $line = "{0,-4} rc={1,-4} twin={2,-5} bytes={3,-7} ms={4,-6} {5}" -f $status, $rc, $made, $size, $sw.ElapsedMilliseconds, $rel
    Add-Content $log $line
    Write-Host $line
    $rows += [pscustomobject]@{ status=$status; rc=$rc; twin=$made; bytes=$size; file=$rel }
}

$hadErr = $vfp.Eval("oFoxBin2prg.l_Error")
try { $vfp.DoCmd("oFoxBin2prg.writeErrorLog_Flush()") } catch {}
$vfp.DoCmd("RELEASE oFoxBin2prg")
$vfp.Quit()

if (Test-Path $errLog) {
    Copy-Item $errLog (Join-Path $PSScriptRoot 'FoxBin2Prg_Error.LOG') -Force
    Add-Content $log "FoxBin2PRG error log copied to tools\FoxBin2Prg_Error.LOG"
}
Add-Content $log "sweep done $(Get-Date -Format s)  ok=$ok fail=$fail  tool_reported_error=$hadErr"
Write-Host "`nok=$ok fail=$fail  (log: $log)"
