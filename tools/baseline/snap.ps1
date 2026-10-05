param(
    [Parameter(Mandatory = $true)] [long]   $Hwnd,
    [Parameter(Mandatory = $true)] [string] $OutFile,
    [switch] $Root
)
# Screenshot one window (by HWND) to a PNG at the window's own pixel size.
#
# Derived from the toolkit's tools/baseline-capture/Snap-Window.ps1 with two
# changes learned on Tastrade:
#   1. The calling thread is made DPI-unaware before any window call, so a
#      DPI-unaware target (VFP 9) is measured and printed at its native pixel
#      size instead of the DWM-scaled size (this desktop runs at 200%).
#   2. No SetForegroundWindow/ShowWindow: the harness inside VFP already has
#      the window it wants on top, and activating a child form from outside
#      fires the app's Activate code a second time.
#   3. -Root captures the top-level window that owns the HWND, because VFP's
#      _SCREEN.HWnd is the MDI client and leaves out the frame, menu, and
#      docked toolbar.
# PrintWindow with PW_RENDERFULLCONTENT first; if that comes back a single
# flat colour, fall back to copying the window's screen rectangle.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

$signature = @'
[StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
[DllImport("user32.dll", SetLastError = true)] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
[DllImport("user32.dll")] public static extern bool IsWindow(IntPtr hWnd);
[DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint nFlags);
[DllImport("user32.dll")] public static extern IntPtr SetThreadDpiAwarenessContext(IntPtr dpiContext);
[DllImport("user32.dll")] public static extern IntPtr GetAncestor(IntPtr hWnd, uint gaFlags);
'@
$u32 = Add-Type -MemberDefinition $signature -Name 'U32' -Namespace 'Snap' -PassThru

# DPI_AWARENESS_CONTEXT_UNAWARE = -1 (Windows 10 1607+)
try { [void][Snap.U32]::SetThreadDpiAwarenessContext([IntPtr](-1)) } catch { }

$h = [IntPtr]$Hwnd
if (-not [Snap.U32]::IsWindow($h)) { Write-Error "HWND $Hwnd is not a valid window." }
if ($Root) {
    # -Root: the top-level window that owns this one (frame, title bar, menu,
    # docked toolbars). VFP's _SCREEN.HWnd is the MDI client inside the frame.
    $h = [Snap.U32]::GetAncestor($h, 2)   # GA_ROOT
}

$rect = New-Object Snap.U32+RECT
[void][Snap.U32]::GetWindowRect($h, [ref]$rect)
$w  = [int]($rect.Right  - $rect.Left)
$ht = [int]($rect.Bottom - $rect.Top)
if ($w -le 0 -or $ht -le 0) { Write-Error "Window $Hwnd has zero size." }

$bmp = New-Object System.Drawing.Bitmap $w, $ht, ([System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
$gfx = [System.Drawing.Graphics]::FromImage($bmp)
$gfx.Clear([System.Drawing.Color]::White)
$hdc = $gfx.GetHdc()
$ok = $false
try {
    $ok = [Snap.U32]::PrintWindow($h, $hdc, 2)   # PW_RENDERFULLCONTENT
} finally {
    $gfx.ReleaseHdc($hdc)
}

# Flat-colour test on a coarse grid: a blank PrintWindow result is one colour.
$flat = $true
if ($ok) {
    $first = $bmp.GetPixel(0, 0)
    for ($y = 0; $y -lt $ht -and $flat; $y += [Math]::Max(1, [int]($ht / 12))) {
        for ($x = 0; $x -lt $w; $x += [Math]::Max(1, [int]($w / 12))) {
            if ($bmp.GetPixel($x, $y) -ne $first) { $flat = $false; break }
        }
    }
}
$method = 'PrintWindow'
if (-not $ok -or $flat) {
    $gfx.CopyFromScreen($rect.Left, $rect.Top, 0, 0, (New-Object System.Drawing.Size($w, $ht)))
    $method = 'CopyFromScreen'
}

$dir = Split-Path -Path $OutFile -Parent
if ($dir -and -not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
$bmp.Save($OutFile, [System.Drawing.Imaging.ImageFormat]::Png)
$gfx.Dispose(); $bmp.Dispose()
Write-Output "$w $ht $method"
