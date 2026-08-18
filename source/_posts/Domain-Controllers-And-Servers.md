---
title: Domain Controllers And Servers
date: 2026-07-04 23:57:29

categories:
  - Active Directory
  - Exploitation
  - Enumeration 
  - Domain Controllers And Servers

tags:
  - Windows
  - Active-Directory
  - Computer-Enumeration
  - Domain-Controllers
  - Domain-Computers
  - PowerView
  - ActiveDirectory-Module
  - Get-DomainComputer
  - Get-DomainController
  - Get-ADComputer
  - Test-AdminAccess
  - Get-NetSession
  - dsquery
  - net-view
  - net-group
  - Living-Off-The-Land
  - Local-Administrator
  - User-Sessions
  - Delegation

cover: /img/computer-enumeration.png
top_img: /img/bg-img.jpg
description: Learn how to enumerate Active Directory computer objects, Domain Controllers, user sessions, local administrator access, and computer accounts using PowerView, the Active Directory module, and built-in Windows commands.
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