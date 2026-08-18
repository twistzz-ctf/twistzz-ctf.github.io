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
  - DNS
  - Internal-DNS
  - DNS-Enumeration
  - Domain-Controllers
  - Zone-Transfer
  - AXFR
  - dig
  - dnsrecon
  - nslookup
  - adidnsdump


cover: /img/internal-dns-enumeration.png
top_img: /img/bg-img.jpg
description: Learn how to enumerate Active Directory DNS infrastructure by discovering Domain Controllers, Kerberos services, testing zone transfers, and dumping AD-integrated DNS records.
---



> ➜ From inside the network, DNS gives up the domain's structure for free, the DC publishes its own roles as SRV records, and AD-integrated zones can often be dumped.

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