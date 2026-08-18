---
title: Making a Target User List
date: 2025-12-03 22:05:36
categories:
  - Active Directory
  - Enumeration
  - "Users & Passwords Enumeration"
  - Making a Target User List
tags:
  - netexec
  - windapsearch
  - rpcclient
  - ldapsearch
  - enum4linux-ng
---

## SMB NULL Session

```bash
kerbrute userenum --dc dc-ip -d Domain wordlist.txt
```

```bash
enum4linux -U dc-ip  | grep "user:" | cut -f2 -d"[" | cut -f1 -d"]"
```

```bash
rpcclient -U "" -N dc-ip

rpcclient> enumdomusers
```

```bash
nxc smb dc-ip -u '' -p '' --users
```

## LDAP Anonymous

```bash
# Step 1: Get Base DN

ldapsearch -x -H ldap://<DC_IP> -s base namingcontexts

# Step 2: Use Base DN to retrieve list of users

ldapsearch -h dc-ip -x -b "<BASE_DN>" -s sub "(&(objectclass=user))"  | grep sAMAccountName: | cut -f2 -d" "
```

```bash
./windapsearch.py --dc-ip <DC_IP> -u "" -U
```
