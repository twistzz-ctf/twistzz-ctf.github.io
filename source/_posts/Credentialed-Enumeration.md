---
title: Credentialed Enumeration
date: 2026-06-29 21:37:57
categories:
  - Active Directory
  - Exploitation
  - Credentialed Enumeration
tags:
  - PowerView
  - Windows
  - Active-Directory
  - NetExec
  - Trust-Enumeration
  - ActiveDirectory-Module
  - Credentialed-Enumeration
  - SMBMap
  - Snaffler
  - SharpHound
  - bloodhound-python
  - windapsearch
  - LDAP
  - LAPS
  - Microsoft-Defender
  - AppLocker
  - PowerShell
  - Security-Controls
  - Domain-Enumeration
  - User-Enumeration
  - Group-Enumeration
  - Share-Enumeration
  - Kerberoasting
---

> ➜ Once valid domain credentials have been obtained, the next step is to enumerate the Active Directory environment, the objective is to identify users, groups, trusts, shares, security controls, and privilege escalation paths that can be leveraged during the engagement.

## Enumerating Security Controls

> ➜ Before executing offensive tooling, identify the security controls deployed in the environment, this helps determine which techniques are likely to be detected or blocked.

> Microsoft Defender

```powershell
Get-MpComputerStatus
```

> AppLocker Policy

```powershell
Get-AppLockerPolicy -Effective | Select-Object -ExpandProperty RuleCollections
```

> PowerShell Language Mode

```powershell
$ExecutionContext.SessionState.LanguageMode
```

> LAPS Delegated Groups

```powershell
Find-LAPSDelegatedGroups
```

> Find Users with LAPS Read Permissions

```powershell
Find-AdmPwdExtendedRights
```

> Enumerate Computers Managed by LAPS

```powershell
Get-LAPSComputers
```

## Enumerating Users - Groups And Domain Admins

> ➜ After identifying the security controls, enumerate users, groups, trusts, sessions and file shares to understand the domain structure and identify potential attack paths.

### Linux

> Users

```bash
nxc smb <DC_IP> -u <user> -p <pass> --users
```

> Groups

```bash
nxc smb <DC_IP> -u <user> -p <pass> --groups
```

> Logged On Users

```bash
nxc smb <HOST> -u <user> -p <pass> --loggedon-users
```

> Enumerate Privileged Users

```bash
python3 windapsearch.py --dc-ip <DC_IP> -u <DOMAIN>\<user> -p <pass> --da
python3 windapsearch.py --dc-ip <DC_IP> -u <DOMAIN>\<user> -p <pass> -PU
```

> Enumerate Domain Admins

```bash
python3 windapsearch.py --dc-ip <DC_IP> -u <DOMAIN>\<user> -p <pass> --da
python3 windapsearch.py --dc-ip <DC_IP> -u <DOMAIN>\<user> -p <pass> -PU
```

### Windows

##### Active Directory Module

```powershell
Import-Module ActiveDirectory
```

> Domain Information

```powershell
Get-ADDomain
```

> Domain Trusts

```powershell
Get-ADTrust -Filter *
```

> Group Members

```powershell
Get-ADGroupMember -Identity "Backup Operators"
```

> Kerberoastable Accounts (SPNs)

```powershell
Get-ADUser -Filter {ServicePrincipalName -ne "$null"} -Properties ServicePrincipalName
```

##### PowerView

```powershell
Import-Module .\PowerView.ps1
```

> User Information

```powershell
Get-DomainUser -Identity <user>
```

> Recursive Group Members

```powershell
Get-DomainGroupMember -Identity "Domain Admins" -Recurse
```

> Domain Trusts

```powershell
Get-DomainTrustMapping
```

> Kerberoastable Accounts (SPNs)

```powershell
Get-DomainUser -SPN
```

> Check Local Administrator Access (Current User)

```powershell
Test-AdminAccess -ComputerName <HOST>
```

## Enumerating SMB Shares

> ➜ Shared folders often contain credentials, scripts, configuration files, backups, and other sensitive information.

### Linux

> NetExec

```bash
nxc smb <DC_IP> -u <user> -p <pass> -M spider_plus
```

```bash
nxc smb <DC_IP> -u <user> -p <pass> --shares
```

> SMBMap

```bash
smbmap -u <user> -p <pass> -d <DOMAIN> -H <DC_IP>

smbmap -u <user> -p <pass> -d <DOMAIN> -H <DC_IP> -R
```

### Windows

> Snaffler

> ➜ Snaffler recursively scans accessible SMB shares and highlights files that are likely to contain credentials, secrets, certificates, configuration files, or other sensitive information.

```powershell
.\Snaffler.exe -d <DOMAIN> -s -v data
```

## BloodHound Collection

> ➜ BloodHound maps relationships between users, groups, computers and ACLs to identify privilege escalation and attack paths that are difficult to discover manually.

### Linux

> bloodhound-python

```bash
bloodhound-python -u <user> -p <pass> -d <DOMAIN> -ns <DC_IP> -c All
```

> NetExec

```bash
nxc ldap FQDN -u user -p password --bloodhound -c all --dns-tcp --dns-server IP
```

### Windows

```powershell
.\SharpHound.exe -c All --zipfilename BLOODHOUND
```

> After importing the collected data, useful starting queries include:
>
>   * Shortest Paths to Domain Admins
>   * Kerberoastable Accounts
>   * AS-REP Roastable Accounts
>   * Unconstrained Delegation
>   * Outbound Object Control
>   * Computers where Domain Users are Local Administrators
>

## Active Directory DNS Enumeration

> ➜ Authenticated users can often enumerate AD-integrated DNS, mapping internal hosts and services before lateral movement.

#### Linux

> Install adidnsdump

```bash
pipx install adidnsdump
```

> Dump DNS Records : Enumerate all DNS records in the AD-integrated zone with a valid domain account.

```bash
adidnsdump -u <DOMAIN>\<user> ldap://<DC_IP>
```

> Resolve Hidden Records : Re-run with the resolve flag to resolve records that were not displayed on the first pass.

```bash
adidnsdump -u <DOMAIN>\<user> ldap://<DC_IP> -r
```
