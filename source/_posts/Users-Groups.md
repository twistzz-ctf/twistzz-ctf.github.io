---
title: "Users & Groups"
date: 2026-07-06 14:13:08
categories:
  - Active Directory
  - Exploitation
  - Enumeration
  - "Users & Groups"
tags:
  - PowerView
  - Windows
  - Active-Directory
  - NetExec
  - ActiveDirectory-Module
  - windapsearch
  - User-Enumeration
  - Group-Enumeration
  - dsquery
  - net-group
  - Linux
  - rpcclient
  - WMIC
  - Kerbrute
  - enum4linux
  - Domain-Users
  - Domain-Groups
  - Local-Groups
  - Local-Users
  - Domain-Admins
  - Privileged-Users
  - Logged-On-Users
  - Service-Accounts
  - Kerberoast
  - SPN
  - PASSWD_NOTREQD
  - RID-Cycling
  - net-user
  - Username-Anarchy
  - Find-DomainUserLocation

cover: /img/user-group-enumeration.png
top_img: /img/bg-img.jpg
description: Learn how to enumerate Active Directory users, groups, privileged accounts, logged-on users, service accounts, and Kerberoastable accounts using Linux, PowerView, the Active Directory module, and…
---

> ➜ Enumerate domain users and groups from the DC directly (null/anonymous) or credentialed

# Users

#### Username Wordlist

> ➜ Turn real names into username

```bash
./username-anarchy -i <names-file>
```

#### Kerbrute

> ➜ Validate usernames using Kerberos pre-auth (low-noise, no credential needed).

```bash
kerbrute userenum -d <DOMAIN> --dc <DC_IP> <wordlist>
```

#### RID Brute

> ➜ Enumerate users via RID cycling.

```bash
nxc smb <DC_IP> -u guest -p '' --rid-brute
```

#### List Domain Users

> ➜ List all domain users.

```bash
nxc smb <DC_IP> -u <user> -p <pass> --users
```

> List All Domain Users Via AD-Module

```powershell
Import-Module ActiveDirectory
```

```powershell
Get-ADUser -Filter * -Properties *
```

> ➜ Enumerate a user and its group memberships Via PowerView

```powershell
Import-Module .\PowerView.ps1
```

```powershell
Get-DomainUser -Identity <user> | Select-Object name,memberof
```

> ➜ List every user account in the domain via Built-in commands

```cmd
net user /domain
```

> ➜ Enumerate domain users via the dsquery LDAP utility via Built-in tool.

```cmd
dsquery user
```

#### Detail a Specific User (net)

> ➜ Show the group memberships and details of one domain user.

```cmd
net user <ACCOUNT> /domain
```

### User Accounts

> ➜ List local and domain user accounts known to the host.

```cmd
wmic useraccount list /format:list
```

### Service Accounts

> ➜ List the accounts used to run services.

```cmd
wmic sysaccount list /format:list
```

#### rpcclient

> ➜ Enumerate users

```bash
rpcclient -U "" -N <DC_IP> -c "enumdomusers"
```

#### enum4linux

> ➜ Pull the user list and filter it.

```bash
enum4linux -U <DC_IP>
```

#### Logged-On Users

> ➜ List users currently logged on to a target host.

```bash
nxc smb <host> -u <user> -p <pass> --loggedon-users
```

#### Privileged Users

> ➜ Enumerate privileged users and Domain Admins.

```bash
python3 windapsearch.py --dc-ip <DC_IP> -u <DOMAIN>\<user> -p <pass> --da
```

#### Kerberoastable Users

> ➜ Find users with a Service Principal Name set (Kerberoast candidates) Via AD-Module.

```powershell
Get-ADUser -Filter {ServicePrincipalName -ne "$null"} -Properties ServicePrincipalName
```

> ➜ Find users with a Service Principal Name set (Kerberoast candidates) Via PowerView.

```powershell
Get-DomainUser -SPN -Properties samaccountname,ServicePrincipalName
```

#### User Hunting

> ➜ Find machines where a target user is logged in Via PowerView.

```powershell
Find-DomainUserLocation -UserIdentity <target-user>
```

#### Accounts Without Password Requirement

> ➜ Find accounts carrying the PASSWD_NOTREQD flag (value 32) ( Built-in ) .

```cmd
dsquery * -filter "(&(objectCategory=person)(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=32))" -attr distinguishedName
```

# Groups

> ➜ List all domain groups.

```bash
nxc smb <DC_IP> -u <user> -p <pass> --groups
```

### AD Module - Group Members

> ➜ Enumerate members of a privileged group.

```powershell
Get-ADGroupMember -Identity "Domain Admins"
```

> ➜ Recursively enumerate members of a group.

```powershell
Get-DomainGroupMember -Identity "Domain Admins" -Recurse
```

> ➜ List the members of a privileged group such as Domain Admins.

```cmd
net group "Domain Admins" /domain
```

#### Local Administrators (net)

> ➜ List the users in the local Administrators group on this host.

```cmd
net localgroup administrators
```

#### Nested Group Membership

> ➜ Recursively resolve nested group membership with the matching-rule-in-chain OID.

```cmd
dsquery * -filter "(member:1.2.840.113556.1.4.1941:=<GROUP_DN>)"
```

#### List the groups known to the host

```cmd
wmic group list /format:list
```

### Local Groups

> ➜ Enumerate local groups for the domain via WMI.

```powershell
Get-WmiObject -Class Win32_Group -Filter "Domain='<DOMAIN>'"
```
