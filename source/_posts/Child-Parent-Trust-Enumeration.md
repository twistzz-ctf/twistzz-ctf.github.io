---
title: Child-Parent Trust Enumeration
date: 2026-07-06 14:42:32
categories:
  - Active Directory
  - Exploitation
  - Enumeration
  - Child-Parent Trust Enumeration
tags:
  - PowerView
  - Forest-Trusts
  - Windows
  - Active-Directory
  - Domain-Trusts
  - Trust-Enumeration
  - Trust-Mapping
  - Parent-Child-Trusts
  - External-Trusts
  - Realm-Trusts
  - ActiveDirectory-Module
  - Get-DomainTrust
  - Get-DomainTrustMapping
  - Get-ADTrust
  - netdom
  - nltest
  - Living-Off-The-Land

cover: /img/domain-trust-enumeration.png
top_img: /img/bg-img.jpg
description: Learn how to enumerate Active Directory domain, forest, parent-child, and external trusts using PowerView, the Active Directory module, and built-in Windows tools to identify potential cross-domain…
---

> ➜ Before attacking a trust, first confirm it exists and learn its type (parent/child, external, forest) and direction (one-way or bidirectional).

## Checking For Existing Trusts

#### AD Module : Get-ADTrust

```powershell
Import-Module ActiveDirectory
Get-ADTrust -Filter *
```

```
Direction               : BiDirectional
DistinguishedName       : CN=LOGISTICS.INLANEFREIGHT.LOCAL,CN=System,DC=INLANEFREIGHT,DC=LOCAL
ForestTransitive        : False
IntraForest             : True
Name                    : LOGISTICS.INLANEFREIGHT.LOCAL
SIDFilteringForestAware : False
SIDFilteringQuarantined : False
Source                  : DC=INLANEFREIGHT,DC=LOCAL
Target                  : LOGISTICS.INLANEFREIGHT.LOCAL
TrustAttributes         : 32
TrustType               : Uplevel

Direction               : BiDirectional
DistinguishedName       : CN=FREIGHTLOGISTICS.LOCAL,CN=System,DC=INLANEFREIGHT,DC=LOCAL
ForestTransitive        : True
IntraForest             : False
Name                    : FREIGHTLOGISTICS.LOCAL
SIDFilteringForestAware : False
SIDFilteringQuarantined : False
Source                  : DC=INLANEFREIGHT,DC=LOCAL
Target                  : FREIGHTLOGISTICS.LOCAL
TrustAttributes         : 8
TrustType               : Uplevel
```

> ➜ If `SIDFilteringForestAware`/`SIDFilteringQuarantined` are both `False`, SID filtering isn't enforced, so the trust may be vulnerable to an ExtraSids attack (SID History abuse).

#### PowerView

> ➜ Same information, PowerView's own format.

```powershell
Import-Module .\PowerView.ps1
Get-DomainTrust
```

```
SourceName      : INLANEFREIGHT.LOCAL
TargetName      : LOGISTICS.INLANEFREIGHT.LOCAL
TrustAttributes : WITHIN_FOREST
TrustDirection  : Bidirectional

SourceName      : INLANEFREIGHT.LOCAL
TargetName      : FREIGHTLOGISTICS.LOCAL
TrustAttributes : FOREST_TRANSITIVE
TrustDirection  : Bidirectional
```

> ➜ `Get-DomainTrustMapping` walks every reachable domain and maps trusts recursively, revealing type (parent/child, external, forest) and direction in one pass.

```powershell
Get-DomainTrustMapping
```

#### BloodHound

> ➜ The `Map Domain Trusts` pre-built query visualizes every trust relationship and its direction at a glance.

## Enumerating Without PowerView (LOTL)

#### netdom

```cmd
netdom query /domain:<DOMAIN> trust
```

```
Direction Trusted\Trusting domain                         Trust type
========= =======================                         ==========
<->       LOGISTICS.INLANEFREIGHT.LOCAL                    Direct
<->       FREIGHTLOGISTICS.LOCAL                            Direct
```

> ➜ List the domain controllers of a (child/trusted) domain.

```cmd
netdom query /domain:<DOMAIN> dc
```

> ➜ List workstations and servers joined to a (child/trusted) domain.

```cmd
netdom query /domain:<DOMAIN> workstation
```

#### nltest

> ➜ List every trust the current domain has, including transitive ones.

```cmd
nltest /domain_trusts /all_trusts
```

#### wmic

> ➜ Show the current domain, its forest, and any trusted domain in one line each, with no credentials required beyond a domain session.

```cmd
wmic ntdomain get Caption,Description,DnsForestName,DomainName,DomainControllerAddress
```

```
Caption          Description      DnsForestName           DomainControllerAddress  DomainName
INLANEFREIGHT    INLANEFREIGHT    INLANEFREIGHT.LOCAL     \\172.16.5.5             INLANEFREIGHT
LOGISTICS        LOGISTICS        INLANEFREIGHT.LOCAL     \\172.16.5.240           LOGISTICS
FREIGHTLOGISTIC  FREIGHTLOGISTIC  FREIGHTLOGISTICS.LOCAL  \\172.16.5.238           FREIGHTLOGISTIC
```


