---
title: Legacy OS
date: 2026-06-26 17:10:35
categories:
  - Active Directory
  - Windows
  - Post-Exploitation
  - Windows Privesc
  - Old Systems
tags:
  - Privilege-Escalation
  - Windows
  - CVE
  - Legacy-Systems
  - Watson
  - Sherlock
  - Windows-Exploit-Suggester
  - Metasploit
  - Patch-Enumeration
  - Local-Exploit-Suggester
  - Windows-Updates
  - HotFix
---

### Enumeration

> Enumerate the installed Windows updates.

```powershell
wmic qfe list brief

or

Get-HotFix
```

### Windows Exploit Suggester

> Save the system information for offline analysis.

```cmd
systeminfo > sysinfo.txt
```

> Transfer the systeminfo output to our machine and analyze it with `windows-exploit-suggester`

```bash
python windows-exploit-suggester.py --update

python windows-exploit-suggester.py --database <database>.xlsx --systeminfo sysinfo.txt
```

### Watson

> Run Watson to identify missing privilege escalation patches on modern Windows systems.

```powershell
.\Watson.exe
```

### Sherlock

> Run Sherlock to identify missing privilege escalation patches on legacy Windows systems.

```powershell
Import-Module .\Sherlock.ps1

Find-AllVulns
```

### Metasploit Local Exploit Suggester

> If we have a Meterpreter session we can enumerate applicable local privilege escalation exploits.

```text
msf6 > use post/multi/recon/local_exploit_suggester

msf6 > set SESSION <id>

msf6 > run
```
