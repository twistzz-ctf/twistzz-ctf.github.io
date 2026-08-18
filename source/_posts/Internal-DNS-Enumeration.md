---
title: Internal DNS Enumeration
date: 2026-07-04 18:07:52
categories:
  - Active Directory
  - Exploitation
  - Enumeration
  - Internal DNS Enumeration
tags:
  - Active-Directory
  - Domain-Controllers
  - DNS
  - dig
  - Internal-DNS
  - DNS-Enumeration
  - Zone-Transfer
  - AXFR
  - dnsrecon
  - nslookup
  - adidnsdump
---

> ➜ From inside the network, DNS gives up the domain’s structure for free, the DC publishes its own roles as SRV records, and AD-integrated zones can often be dumped.

### Locate AD Roles via SRV Records

> ➜ Find the Domain Controllers.

```bash
nslookup -type=SRV _ldap._tcp.dc._msdcs.<DOMAIN>
```

> ➜ Find the KDC (Kerberos).

```bash
nslookup -type=SRV _kerberos._tcp.<DOMAIN>
```

### Zone Transfer

> ➜ Attempt a full zone transfer

```bash
dig axfr <DOMAIN> @<DC_IP>
```

> Or

```bash
dnsrecon -d <DOMAIN> -t axfr
```

### Dump AD-Integrated DNS

```bash
pipx install adidnsdump
```

> ➜ Dump every record in the AD-integrated zone with a valid domain account.

```bash
adidnsdump -u <DOMAIN>\<user> ldap://<DC_IP>
```

> ➜ Re-run with the resolve flag to reveal records hidden on the first pass.

```bash
adidnsdump -u <DOMAIN>\<user> ldap://<DC_IP> -r
```
