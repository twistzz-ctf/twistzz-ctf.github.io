---
title: "Enumerating & Retrieving Password Policies"
date: 2025-12-03 03:33:31
categories:
  - Active Directory
  - Enumeration
  - "Users & Passwords Enumeration"
  - "Enumerating & Retrieving Password Policies"
tags:
  - netexec
  - rpcclient
  - ldapsearch
  - enum4linux-ng
---

# Linux

### Using Valid Domain Credential

```bash
nxc smb dc-ip -u username -p password --pass-pol
```

### Using SMB NULL Sessions

```bash
nxc smb dc-ip -u guest -p '' --pass-pol
```

```bash
rpcclient $> getdompwinfo
```

```bash
enum4linux-ng -P dc-ip
```

```bash
# Step 1: Get Base DN

ldapsearch -x -H ldap://<DC_IP> -s base namingcontexts

# Step 2: Use Base DN to retrieve password policy attributes

ldapsearch -x -H ldap://<DC_IP> -b "<BASE_DN>" -s sub "*" | grep -m 1 -B 10 pwdHistoryLength
```

# Windows

### Using SMB NULL Sessions

#### net.exe : Built-in Tool

```plaintext
C:\htb> net accounts
```

#### PowerView

```powershell
PS C:\htb> import-module .\PowerView.ps1
PS C:\htb> Get-DomainPolicy
```
