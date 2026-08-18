---
title: External Reconnaissance
date: 2026-07-04 18:02:42
categories:
  - Active Directory
  - Exploitation
  - Enumeration
  - External Enumeration
tags:
  - OSINT
  - Passive-Reconnaissance
  - External-Enumeration
  - WHOIS
  - ASN
  - BGP
  - DNS
  - NSLookup
  - dig
  - MX
  - NS
  - TXT
  - SPF
  - DKIM
  - Google-Dorking
  - Metadata
  - Public-Files
  - Email-Harvesting
  - Username-Enumeration
  - linkedin2username
  - DeHashed
  - Breach-Data
  - Credential-Hunting
---

> ➜ Passive footprinting from outside the network ASN/IP space, domains, DNS, public files, emails, usernames, and breach data.

### ASN & IP Space

> ➜ Web GUI `bgp.he.net` we enter the target domain to get its ASN, netblocks, IP, mail server, and nameservers.

### WHOIS & Registrar Data

> ➜ Pull registrar, organisation, and contact data for the domain.

```bash
whois <target-domain>
```

### DNS Records

> ➜ Resolve the host (A) record.

```bash
nslookup <target-domain>
```

> ➜ Enumerate the mail servers (MX).

```bash
nslookup -type=MX <target-domain>
```

> ➜ Enumerate the name servers (NS).

```bash
nslookup -type=NS <target-domain>
```

> ➜ Enumerate TXT records (SPF, DKIM, third-party services).

```bash
nslookup -type=TXT <target-domain>
```

> ➜ Pull every record at once with dig.

```bash
dig <target-domain> ANY +noall +answer
```

> ➜ Cross-validate a record against a public resolver.

```bash
dig <target-domain> @8.8.8.8 +short
```

### Public File Discovery

> ➜ Google dorks : Find indexed documents whose metadata leaks usernames and software versions.

```text
filetype:pdf inurl:<target-domain>
```

### E-mail Address Harvesting

> ➜ Surface pages exposing employee emails (reveals the AD username format).

```text
intext:"@<target-domain>" inurl:<target-domain>
```

### Username Generation

> ➜ Scrape LinkedIn to build username list for spraying.

```bash
linkedin2username -c "<Company Name>" -n <target-domain>
```

### Breach & Credential Hunting

> ➜ Search breach data for cleartext credentials and hashes tied to the target.

```bash
sudo python3 dehashed.py -q <target-domain> -p
```
