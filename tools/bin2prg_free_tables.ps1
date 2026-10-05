# FoxBin2PRG conversion of the three free tables (structure only, to .db2 twins).
#
# The main sweep (bin2prg_sweep.ps1) converts source containers only; the
# tables inside tastrade.dbc are described by the .dc2 twin, but the three free
# tables outside it have no twin until this runs. Same in-process COM technique
# as the sweep, same argument list, same headless flags. Direction BIN2PRG only.
#
# Usage:  powershell -ExecutionPolicy Bypass -File tools\bin2prg_free_tables.ps1
# Output: .db2 beside each .dbf, and tools\bin2prg_free_tables.log

$ErrorActionPreference = 'Stop'
$exe  = 'C:\fox\Thor\Thor\Tools\Components\FoxBin2PRG\foxbin2prg.exe'
$root = Split-Path $PSScriptRoot -Parent
$log  = Join-Path $PSScriptRoot 'bin2prg_free_tables.log'
$targets = @('data\behindsc.dbf', 'data\repolist.dbf', 'help\ttrade.dbf') | ForEach-Object { Get-Item (Join-Path $root $_) }

$errLog = Join-Path $env:TEMP 'FoxBin2Prg_Error.LOG'
if (Test-Path $errLog) { Remove-Item $errLog -Force }
"free-table sweep start $(Get-Date -Format s)  root=$root  targets=$($targets.Count)" | Set-Content $log

$vfp = New-Object -ComObject 'VisualFoxPro.Application.9'
$vfp.Visible = $false
$vfp.DoCmd("SET PROCEDURE TO '$exe'")
$vfp.DoCmd("PUBLIC oFoxBin2prg")
$vfp.DoCmd("oFoxBin2prg = CREATEOBJECT('c_foxbin2prg')")
Add-Content $log "FoxBin2PRG version: $($vfp.Eval('oFoxBin2prg.c_FB2PRG_EXE_Version'))"

$ok = 0; $fail = 0
foreach ($f in $targets) {
    $rel = $f.FullName.Substring($root.Length + 1)
    $t   = [System.IO.Path]::ChangeExtension($f.FullName, '.db2')
    if (Test-Path $t) { Remove-Item $t -Force }
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
}
$hadErr = $vfp.Eval("oFoxBin2prg.l_Error")
try { $vfp.DoCmd("oFoxBin2prg.writeErrorLog_Flush()") } catch {}
$vfp.DoCmd("RELEASE oFoxBin2prg")
$vfp.Quit()
if (Test-Path $errLog) { Copy-Item $errLog (Join-Path $PSScriptRoot 'FoxBin2Prg_Error_free_tables.LOG') -Force }
Add-Content $log "free-table sweep done $(Get-Date -Format s)  ok=$ok fail=$fail  tool_reported_error=$hadErr"
Write-Host "ok=$ok fail=$fail  (log: $log)"
