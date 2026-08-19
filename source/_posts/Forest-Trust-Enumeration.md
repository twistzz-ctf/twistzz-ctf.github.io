---
title: Forest Trust Enumeration
date: 2026-07-06 15:00:25
categories:
  - Active Directory
  - Exploitation
  - Enumeration
  - Forest Trust Enumeration
tags:
  - PowerView
  - Forest-Trusts
  - Cross-Forest
  - Cross-Domain
  - Get-DomainForeignGroupMember
  - Windows
  - Active-Directory
  - Domain-Trusts
  - Trust-Enumeration
  - Foreign-Security-Principals
  - Foreign-Users
  - Foreign-Group-Members
  - Get-ForestTrust
  - Get-DomainForeignUser

cover: /img/cross-domain-enumeration.png
top_img: /img/bg-img.jpg
description: Learn how to enumerate Active Directory forest trusts, foreign users, and foreign group members using PowerView to identify cross-domain and cross-forest access relationships.
---

### PowerView

```powershell
Import-Module .\PowerView.ps1
```

> ➜ Return the trust relationships of the current forest.

```powershell
Get-ForestTrust
```

> ➜ Return users from another domain who are members of groups in ours.

```powershell
Get-DomainForeignUser
```

> ➜ Return principals from other domains placed into groups in this domain (cross-trust access).

```powershell
Get-DomainForeignGroupMember
```
