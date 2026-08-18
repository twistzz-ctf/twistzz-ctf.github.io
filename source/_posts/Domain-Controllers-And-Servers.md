---
title: Domain Controllers And Servers
date: 2026-07-04 23:57:29
categories:
  - Active Directory
  - Exploitation
  - Enumeration
  - Domain Controllers And Servers
tags:
  - PowerView
  - Windows
  - Active-Directory
  - ActiveDirectory-Module
  - Living-Off-The-Land
  - Computer-Enumeration
  - Domain-Controllers
  - Domain-Computers
  - Get-DomainComputer
  - Get-DomainController
  - Get-ADComputer
  - Test-AdminAccess
  - Get-NetSession
  - dsquery
  - net-view
  - net-group
  - Local-Administrator
  - User-Sessions
  - Delegation
---

> ➜ Enumerate computer objects : Domain Controllers, servers, delegation, sessions, and where we hold local admin.

### PowerView

```powershell
Import-Module .\PowerView.ps1
```

> ➜ Return all computers with their DNS name and account flags

```powershell
Get-DomainComputer | select dnshostname,useraccountcontrol
```

> ➜ Return the DCs with OS, IP, and Global Catalog status

```powershell
Get-DomainController
```

> ➜ Test whether the current user is local admin on a target host

```powershell
Test-AdminAccess -ComputerName <host>
```

> ➜ Show who is connected to a host

```powershell
Get-NetSession -ComputerName <host>
```

> ➜ Enumerate computer objects.

```powershell
Get-ADComputer -Filter * -Properties OperatingSystem | select Name,OperatingSystem
```

## Living Off the Land - Built-in

> ➜ Enumerate computers via dsquery, and find DCs by the userAccountControl bit.

```cmd
dsquery * -filter "(userAccountControl:1.2.840.113556.1.4.803:=8192)" -attr sAMAccountName
```

> ➜ List the computers visible in the domain.

```cmd
net view /domain
```

> ➜ List the computer accounts that belong to the domain.

```cmd
net group "Domain Computers" /domain
```
