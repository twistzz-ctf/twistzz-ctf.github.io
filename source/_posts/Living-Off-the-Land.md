---
title: Living Off the Land
date: 2026-06-29 23:56:56


categories:
  - Active Directory
  - Exploitation
  - Living Off the Land

tags:
  - Windows
  - Active-Directory
  - Living-Off-the-Land
  - LOLBAS
  - Enumeration
  - Native-Commands
  - whoami
  - net
  - net1
  - dsquery
  - WMIC
  - PowerShell
  - AppLocker
  - Constrained-Language-Mode
  - Microsoft-Defender
  - Host-Enumeration
  - User-Enumeration
  - Group-Enumeration
  - Share-Enumeration
  - Domain-Enumeration
  - Password-Policy
  - Execution-Policy
  - Environment-Variables
  - Firewall
  - Active-Sessions
  - Domain-Controllers

cover: /img/living-off-the-land.png
top_img: /img/bg-img.jpg
description: Learn how to enumerate Windows and Active Directory environments using only built-in Windows utilities when offensive tooling is restricted by AppLocker, Constrained Language Mode, or endpoint security solutions.
---

> ➜ In environments where offensive tooling cannot be executed due to AppLocker, Constrained Language Mode, or EDR, Windows built-in utilities can still be used to enumerate the Active Directory environment.

## Host and Session Information


#### Current User Information

> ➜ Display the current user along with its privileges and group memberships.

```powershell
whoami /all
```

#### Environment Variables

> ➜ List environment variables to reveal paths, the logon server, and the user's domain.

```powershell
Get-ChildItem Env: | ft Key,Value
```

#### System Information

> ➜ Print a full summary of the host: OS version, installed patches, and domain membership.

```cmd
systeminfo
```

#### Installed Patches (Hotfixes)

> ➜ List installed hotfixes to spot missing patches that may allow privilege escalation.

```cmd
wmic qfe get Caption,Description,HotFixID,InstalledOn
```

#### Loaded PowerShell Modules

> ➜ Show the modules currently loaded in the PowerShell session.

```powershell
Get-Module
```

#### Execution Policy

> ➜ Check the PowerShell execution policy across all scopes.

```powershell
Get-ExecutionPolicy -List
```

#### Antivirus / Defender Status

> ➜ Check whether Microsoft Defender and its real-time protection are enabled.

```powershell
Get-MpComputerStatus
```

#### Active Sessions

> ➜ List the active sessions on the host to see who else is logged on.

```powershell
qwinsta
```

#### ARP Cache

> ➜ List the hosts this machine has recently communicated with — potential pivots for lateral movement.

```powershell
arp -a
```

#### Routing Table

> ➜ Display the routing table to reveal which networks the host can reach.

```powershell
route print
```

#### IP Configuration

> ➜ Show the full network configuration, including IP address, DNS servers, and domain.

```powershell
ipconfig /all
```

#### Windows Firewall Profiles

> ➜ Display the configuration of all Windows Firewall profiles.

```powershell
netsh advfirewall show allprofiles
```

#### Downgrade to PowerShell v2

> ➜ Older environments may still support PowerShell v2, which does not include AMSI.

```powershell
powershell.exe -version 2
```

> ➜ Confirm the current PowerShell version after the downgrade.

```powershell
Get-Host
```

## Enumerating Domain Users

#### List All Domain Users

> ➜ List every user account in the domain.

```cmd
net user /domain
```

#### Information About a Specific User

> ➜ Display the group memberships and details of a single domain user.

```cmd
net user <ACCOUNT> /domain
```

#### Built-in LDAP User Enumeration

> ➜ Enumerate domain users through the built-in dsquery LDAP utility.

```cmd
dsquery user
```

## Enumerating Domain Groups

#### Members of a Group

> ➜ List the members of a specific privileged group such as Domain Admins.

```cmd
net group "Domain Admins" /domain
```

#### Domain Controllers Group

> ➜ List the members of the Domain Controllers group.

```cmd
net group "Domain Controllers" /domain
```

#### Domain Computers Group

> ➜ List the computer accounts that belong to the domain.

```cmd
net group "Domain Computers" /domain
```

#### Local Administrators

> ➜ List the users in the local Administrators group on this host.

```cmd
net localgroup administrators
```

#### Nested Group Membership

> ➜ Recursively resolve nested membership of a group using the LDAP matching-rule-in-chain OID.

```cmd
dsquery * -filter "(member:1.2.840.113556.1.4.1941:=<GROUP_DN>)"
```

## Host and Share Discovery

#### List Domain Computers

> ➜ Discover the computers visible in the domain.

```cmd
net view /domain
```

#### List Shares on a Host

> ➜ List the shared folders exposed by a specific computer.

```cmd
net view \\<COMPUTER> /ALL
```

#### Current Shares on This Host

> ➜ Show the shares currently published by the local host.

```cmd
net share
```

## Enumerating Password Policy

#### Domain Password Policy

> ➜ Display the domain password and account lockout policy.

```cmd
net accounts /domain
```

## Enumerating Domain Controllers

> ➜ The OID `1.2.840.113556.1.4.803` is a bitwise-AND match on `userAccountControl`, where `8192` flags a Domain Controller.

#### Identify Domain Controllers

> ➜ Query for accounts whose userAccountControl carries the Domain Controller flag.

```cmd
dsquery * -filter "(userAccountControl:1.2.840.113556.1.4.803:=8192)" -attr sAMAccountName
```

## Enumerating Accounts Without Password Requirements


> ➜ Query for user accounts carrying the PASSWD_NOTREQD flag (value 32), which may have no password set.

```cmd
dsquery * -filter "(&(objectCategory=person)(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=32))" -attr distinguishedName
```

## Enumerating Domain Information

#### Display Domain Information

> ➜ Display information about the domain the host is joined to.

```cmd
wmic ntdomain get
```

#### Current Computer's Domain

> ➜ Show the domain name of the current computer.

```cmd
wmic computersystem get domain
```

#### Enumerate User Accounts

> ➜ List the local and domain user accounts known to the host.

```cmd
wmic useraccount list /format:list
```

#### Enumerate Groups

> ➜ List the groups known to the host.

```cmd
wmic group list /format:list
```

#### Enumerate Service Accounts

> ➜ List the accounts used to run services on the host.

```cmd
wmic sysaccount list /format:list
```

#### List Running Processes

> ➜ List all running processes, which can reveal installed software and security agents.

```cmd
wmic process list /format:list
```

## Enumerating Local Groups

#### Enumerate Local Groups Using WMI

> ➜ Enumerate the local groups for the specified domain using WMI.

```powershell
Get-WmiObject -Class Win32_Group -Filter "Domain='<DOMAIN>'"
```

### net1

#### Bypass net Binary Restrictions

> ➜ `net1.exe` provides the same functionality as `net.exe` and can sometimes bypass simple application-control rules that block the `net` binary.

```cmd
net1 user /domain
```