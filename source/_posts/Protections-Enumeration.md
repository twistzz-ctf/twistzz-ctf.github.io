---
title: Protections Enumeration
date: 2026-06-09 21:54:38

categories:
  - Active Directory
  - Windows
  - Post-Exploitation
  - Windows Privesc
  - Windows Enumeration
tags:
  - systeminfo
  - whoami
  - tasklist
  - netstat
  - ipconfig
  - Get-HotFix
  - Get-Process
  - Get-MpComputerStatus
  - Get-AppLockerPolicy
  - wmic
  - Windows-Defender
  - EDR
  - AppLocker
  - CrowdStrike
  - SentinelOne
  - LOLBAS
cover: /img/defender.png
top_img: /img/bg-img.jpg
description: Enumerate a Windows system for privilege escalation vectors including Defender status, EDR detection, AppLocker rules, and bypass paths.
---




### Checking Windows Defender status

```powershell
PS> Get-MpComputerStatus

AMServiceEnabled        : True
AntivirusEnabled        : True
RealTimeProtectionEnabled : False   <-- Disabled! Safe to use standard tools
BehaviorMonitorEnabled  : False
IoavProtectionEnabled   : False
```

>- `RealTimeProtectionEnabled: False` → Defender scanning is off, use tools normally
>- `RealTimeProtectionEnabled: True` → need obfuscated or in-memory techniques
>- `BehaviorMonitorEnabled` → catches Potato-style attacks even when signature scanning is bypassed

### Identifying third-party EDR products

> Enterprise environments almost always have an EDR beyond basic Defender :

| EDR Product          | Process to look for     |
| -------------------- | ----------------------- |
| CrowdStrike Falcon   | CSFalconService.exe     |
| Carbon Black         | cb.exe, CarbonBlack.exe |
| Cylance              | CylanceSvc.exe          |
| SentinelOne          | SentinelAgent.exe       |
| Windows Defender ATP | MsSense.exe             |

```cmd
C:\> tasklist | findstr /i "carbon\|cylance\|sentinel\|crowdstrike\|MsSense\|csfalcon"
```

## AppLocker : Application Whitelisting

### Understanding AppLocker rules

> AppLocker is Microsoft's application whitelisting solution, It can block execution of specific files, entire file types, or anything not from a trusted publisher.

```powershell
PS> Get-AppLockerPolicy -Effective | select -ExpandProperty RuleCollections
```

> Test if cmd.exe is blocked

```powershell
PS> Get-AppLockerPolicy -Local | Test-AppLockerPolicy -path C:\Windows\System32\cmd.exe -User Everyone

FilePath                          PolicyDecision  MatchingRule
--------                          --------------  ------------
C:\Windows\System32\cmd.exe       Denied          c:\windows\system32\cmd.exe
```

### Common AppLocker bypass paths

> Even when AppLocker is enabled, several paths are almost always allowed, we can place our tools in these locations:

```
C:\Windows\Temp\         <-- BUILTIN\Users always has write access here
C:\Windows\System32\     <-- Default allowed (can't write, but LOLBAS binaries here work)
C:\Program Files\        <-- Usually allowed for execution
%APPDATA%\               <-- Sometimes allowed, user-writable
```
