---
title: Security Controls
date: 2026-07-04 23:42:03
categories:
  - Active Directory
  - Exploitation
  - Enumeration
  - Security Controls
tags:
  - PowerView
  - Windows
  - Active-Directory
  - Living-Off-The-Land
  - LAPS
  - Microsoft-Defender
  - AppLocker
  - Security-Controls
  - LOLBAS
  - Constrained-Language-Mode
  - Execution-Policy
  - Windows-Firewall
  - Defensive-Enumeration
  - Environment-Enumeration
  - Post-Exploitation
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
