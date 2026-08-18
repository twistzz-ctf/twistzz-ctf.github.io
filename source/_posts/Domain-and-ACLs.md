---
title: Domain and ACLs
date: 2026-07-06 13:24:06
categories:
  - Active Directory
  - Exploitation
  - Enumeration
  - Domain and ACLs
tags:
  - PowerView
  - Windows
  - Active-Directory
  - NetExec
  - ActiveDirectory-Module
  - Living-Off-The-Land
  - Domain-Enumeration
  - Linux
  - Domain-Information
  - Password-Policy
  - ACL
  - Active-Directory-ACL
  - Access-Control-Lists
  - Security-Descriptors
  - rpcclient
  - net-accounts
  - Get-ADDomain
  - Get-Domain
  - Find-InterestingDomainAcl
  - Get-DomainObjectACL
  - Convert-NameToSid
  - Get-ADObject
---

> ➜ Enumerate the domain itself (info + password policy) and the Access Control Lists that reveal who can act on whom.

## Domain Information

#### AD Module

```powershell
Import-Module ActiveDirectory
```

> ➜ Pull domain details

```powershell
Get-ADDomain
```

### PowerView

> ➜ Pull the domain objects

```powershell
Get-Domain
```

### LOTL

> ➜ Read the domain the host is joined to.

```cmd
wmic ntdomain get
```

## Password Policy

#### NetExec

> ➜ Pull the password policy with a credential.

```bash
nxc smb <DC_IP> -u <user> -p <pass> --pass-pol
```

#### rpcclient

> ➜ Read the policy over a null session.

```bash
rpcclient -U "" -N <DC_IP> -c "getdompwinfo"
```

### net accounts

> ➜ Read the policy from a domain host.

```cmd
net accounts /domain
```

## ACL Enumeration

#### PowerView

```powershell
Import-Module .\PowerView.ps1
```

> ➜ Find Interesting ACLs

```powershell
Find-InterestingDomainAcl
```

> ➜ Convert an account name to its SID to match against object ACLs.

```powershell
$sid = Convert-NameToSid <target-user>
```

> ➜ Return every object the target has rights over, with GUIDs resolved to names.

```powershell
Get-DomainObjectACL -ResolveGUIDs -Identity * | ? {$_.SecurityIdentifier -eq $sid}
```

> ➜ Look up an ExtendedRight GUID (e.g. User-Force-Change-Password) in the schema.

```powershell
Get-ADObject -SearchBase "CN=Extended-Rights,$((Get-ADRootDSE).ConfigurationNamingContext)" -Filter {ObjectClass -like 'ControlAccessRight'} -Properties * | Select Name,DisplayName,rightsGuid | ?{$_.rightsGuid -eq "00299570-246d-11d0-a768-00aa006e0529"} | fl
```

#### Built-In Alternative : Check ACLs

> ➜ Loop each user’s ACL, keeping only entries where our controlled account has rights.

```powershell
foreach($line in [System.IO.File]::ReadLines(".\ad_users.txt")) {get-acl "AD:\$(Get-ADUser $line)" | Select-Object Path -ExpandProperty Access | Where-Object {$_.IdentityReference -match '<DOMAIN>\<target-user>'}}
```
