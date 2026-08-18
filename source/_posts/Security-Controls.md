---
title: Security Controls
date: 2026-07-04 23:42:03

categories:
  - Active Directory
  - Exploitation
  - Enumeration 
  - Security Controls

tags:
  - Windows
  - Active-Directory
  - Security-Controls
  - Microsoft-Defender
  - AppLocker
  - Constrained-Language-Mode
  - Execution-Policy
  - Windows-Firewall
  - LAPS
  - PowerView
  - Living-Off-The-Land
  - LOLBAS
  - Defensive-Enumeration
  - Environment-Enumeration
  - Post-Exploitation

cover: /img/security-controls-enumeration.png
top_img: /img/bg-img.jpg
description: Learn how to enumerate Windows security controls, including Microsoft Defender, AppLocker, PowerShell restrictions, LAPS, Windows Firewall, and execution policies to assess which offensive techniques are likely to succeed.
---


### Windows Defender Status

> ➜ Check whether Defender and real-time protection are enabled.

```powershell
Get-MpComputerStatus
```

### AppLocker Policy

> ➜ Review the effective AppLocker rules to see what binaries are blocked.

```powershell
Get-AppLockerPolicy -Effective | select -ExpandProperty RuleCollections
```

### PowerShell Language Mode

> ➜ Check the language mode : `ConstrainedLanguage restricts most offensive tools`

```powershell
$ExecutionContext.SessionState.LanguageMode
```

### LAPS - Delegated Groups

> ➜ Find groups delegated rights to read LAPS passwords.

```powershell
Find-LAPSDelegatedGroups
```

### LAPS - Extended Rights

> ➜ Find principals with extended rights to read LAPS passwords.

```powershell
Find-AdmPwdExtendedRights
```

### LAPS - Readable Computers

> ➜ List computers whose LAPS password the current user can read.

```powershell
Get-LAPSComputers
```

## Living Off the Land - Built-in Checks

### Windows Firewall Profiles

> ➜ Shows whether the firewall is turned **on or off** for each profile (Domain, Private, Public) and its default inbound/outbound rules.

```powershell
netsh advfirewall show allprofiles
```

### PowerShell Execution Policy

> ➜ Check the execution policy across all scopes.

```powershell
Get-ExecutionPolicy -List
```
