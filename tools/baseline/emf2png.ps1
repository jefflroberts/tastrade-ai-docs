param(
    [Parameter(Mandatory = $true)] [string] $InFile,
    [Parameter(Mandatory = $true)] [string] $OutFile,
    [double] $Scale = 2.0
)
# Render an EMF page written by ReportListener.OutputPage(n, file, 100) to a
# PNG at Scale times its 96-dpi size (2.0 = 1632 by 2112 for Letter).
#
# Why not OutputPage's own PNG (device type 104): on this 200% desktop it
# returns a 408 by 528 bitmap with the page drawn at full size and clipped,
# whatever nWidth/nHeight are passed; the EMF (device type 100) is the whole
# page as vectors, so the raster is made here instead.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$emf = [System.Drawing.Imaging.Metafile]::new($InFile)
$w = [int][Math]::Round($emf.Width * $Scale)
$h = [int][Math]::Round($emf.Height * $Scale)
$bmp = New-Object System.Drawing.Bitmap $w, $h, ([System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.Clear([System.Drawing.Color]::White)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
$g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
$g.DrawImage($emf, (New-Object System.Drawing.Rectangle 0, 0, $w, $h))
$bmp.Save($OutFile, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose(); $emf.Dispose()
Write-Output "$w $h"
