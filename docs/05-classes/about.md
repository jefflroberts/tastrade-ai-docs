# about.vcx — the About box

| Source file | Type | Path |
|---|---|---|
| `about.vcx` | Class library | `libs/about.vc2` |

**Purpose:** A generic, parameterised About dialog: application name, version, copyright, trademark, and logo come in as `Init` parameters; the registered owner and organisation come from the Windows registry (or `WIN.INI` on Windows 3.x); and a System Info button launches `MSINFO.EXE` if the registry says where it is.

**Used by:**
- The Help menu's About item ([[../07-menus/main.md]]) does `SET CLASSLIB TO about ADDITIVE`, creates `AboutBox` with `TASTRADE_LOC`, `VERSION_LOC` ("1.1"), `COPYRIGHT_LOC` ("Copyright 1996 Microsoft Corporation"), `RIGHTSRSRVD_LOC`, and `BITMAPS\TTRADESM.BMP`, shows it, then releases the library. This is the only class library not loaded by `environment.Set` ([[tsgen.md]]).

**Related docs:** [[tsbase.md]] (`tsbaseform`, which it extends but largely disables), [[../08-programs/main.md]] (the `RegOpenKeyEx`, `RegQueryValueEx`, `RegCloseKey`, and `GetProStr` Win32 declarations it calls), [[../07-menus/main.md]], [[README.md]].

## Classes in this library

### aboutbox (extends tsbaseform OF tsbase.vcx)

**Purpose:** This class displays an About Application that the user can customize. Although it extends `tsbaseform`, it turns the base behaviour off: `ctoolbar` empty, `lallownew/lallowedits/lallowdelete = .F.`, `WindowType = 1` (modal), `AlwaysOnTop = .T.`, and `addtomenu`, `removefrommenu`, `restorewindowpos`, `savewindowpos` declared `PROTECTED`. So the base form's `Init` still runs (`gTTrade` guard, window position) but there is no toolbar, no menu entry, and no data. Its controls are native VFP classes (`commandbutton`, `label`, `image`, `line`, `shape`), not the `ts*` subclasses, and the default captions are placeholders ("Your application name", "Version #", "UserName", "UserCorp") that `Init` replaces. The `CLASSDATA` icon paths are the bare `..\`, meaning the designer icon was never set.

**Custom properties:**

| Property | Protected | Description |
|---|---|---|
| `cmsinfodir` |  | Holds the path of the MSINFO.EXE program. |

**Controls:** `imgLogo` (image, stretched), `lblAppName`, `lblVersion`, `lblCopyright`, `lblTrademark`, `lblLicense` ("This product is licensed to:"), `lblUserName`, `lblUserCorp`, `cmdOK` (default), `cmdSysInfo` ("\<System Info..."), plus a shape and two lines drawing the 3-D frame.

#### Methods

#### `Init`

Takes five optional parameters and applies each only if it is a string. Then branches on `OS()`: on Windows NT or Windows 4.x (95/98) it opens `HKLM\Software\Microsoft\Shared Tools\MSInfo` to find `MSINFO.EXE` and `HKLM\Software\Microsoft\Windows [NT]\CurrentVersion` to read `RegisteredOwner` and `RegisteredOrganization`, through the Win32 declarations in `main.prg` and the key constants in `tastrade.h`; otherwise it reads `WIN.INI` sections `[MS USER INFO]` and `[MICROSOFT SYSTEM INFO]`. If no `MSINFO.EXE` was found the System Info button is disabled and the form shortened. **NOTE:** `OS()` on modern Windows returns `"Windows 6.02"` or similar, which matches neither branch, so on this machine the code falls to the `WIN.INI` path, finds nothing, and the About box shows blank owner lines with System Info disabled. **NOTE:** `RegCloseKey(lnResult)` after the second open runs even if that open failed. **NOTE:** the buffer is 128 bytes; a longer registered organisation is truncated.

```foxpro
*-- (c) Microsoft Corporation 1995
LPARAMETERS tcAppName, tcVersion, tcCopyright, tcTrademark, tcLogoBMP

LOCAL lcBuffer, ;
      lnBufferSize, ;
      lcRetVal, ;
*-- ... 126 more lines of Microsoft's Tastrade source omitted; see `Init` in your own copy of Tastrade.
```

#### `Activate`

```foxpro
SET MESSAGE TO thisform.Caption
```

#### `Unload`

```foxpro
SET MESSAGE TO
```

#### `cmdOK.Click`

```foxpro
RELEASE thisform
```

#### `cmdSysInfo.Click`

`RUN /N1` launches the program through the shell in a normal window. **NOTE:** `&lcMSInfoWinDir` macro substitution of a registry value into a `RUN` command; a path with spaces would need quoting.

```foxpro
LOCAL lcMSInfoWinDir
lcMSInfoWinDir= thisform.cMSInfoDir
RUN/N1 &lcMSInfoWinDir
```

## Notes

- **Era-specific.** The whole `Init` is a 1995 Windows version switch. A rebuild keeps the parameters and drops the registry and `WIN.INI` code.
- **Version string** `"1.1"` and **copyright** `"1996"` come from `strings.h`, one year after the 1995 copyright in the code.
- **Reuses `tsbaseform` for its window-position memory only**, which means the About box's position is saved to `tastrade.ini` under its caption.
