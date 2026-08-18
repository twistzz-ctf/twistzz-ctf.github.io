---
title: Hyper-V Administrators
date: 2026-03-06 11:32:17

categories:
  - Active Directory
  - Windows
  - Post-Exploitation
  - Windows Privesc
  - Groups
tags:

cover: /img/privesc.png
top_img: /img/bg-img.jpg
description: Privilege escalation using the Hyper-V Administrators group.
---


> ➜ The `Hyper-V Administrators` group has full access to all [Hyper-V features](https://docs.microsoft.com/en-us/windows-server/manage/windows-admin-center/use/manage-virtual-machines). If Domain Controllers have been virtualized, then the virtualization admins should be considered Domain Admins. They could easily create a clone of the live Domain Controller and mount the virtual disk offline to obtain the NTDS.dit file and extract NTLM password hashes for all users in the domain.

> ➜ The `Hyper-V Administrators` group can manage virtual machines and their disk files (`.vhdx`). The Hyper-V service (`vmms.exe`), running as `NT AUTHORITY\SYSTEM`, automatically restores default permissions on these disk files during cleanup. An attacker can delete a legitimate `.vhdx` file and replace it with a hard link to a protected system file such as `SAM`. When `vmms.exe` restores permissions, it grants `Hyper-V Administrators` full control over the target file, allowing credential extraction and privilege escalation to SYSTEM.




### Initial State

Our target file is:

```text
K:\Twistzz\dc01.vhdx
```

We are members of:

```text
Hyper-V Administrators
```

However, we do not have direct access to protected files such as:

```text
C:\Windows\System32\config\SAM
```
  
### Remove the Legitimate Virtual Disk

Because members of `Hyper-V Administrators` have full control over VM disks, we can delete the original `.vhdx` file:

```powershell
del K:\Twistzz\dc01.vhdx
```

### Create a Hard Link to a Protected File

Next, we create a hard link using the same file name as the virtual disk `dc01.vhdx`, pointing to the `SAM` registry hive:

```powershell
fsutil hardlink create K:\Twistzz\dc01.vhdx C:\Windows\System32\config\SAM
```

- At the filesystem level, both paths now reference the same file object.

- Importantly, the `SAM` file permissions remain unchanged at this stage.

### Trigger Permission Restoration by Deleting the VM


When the virtual machine is deleted, `vmms.exe` restores permissions on `K:\Twistzz\dc01.vhdx`.

Since `K:\Twistzz\dc01.vhdx` is a hard link to the `SAM` hive, any permission changes applied to this file also affect the `SAM` file.

Because this operation is performed by `SYSTEM`, `vmms.exe` grants Full Control on `K:\Twistzz\dc01.vhdx` to members of `Hyper-V Administrators`, which effectively grants the same permissions on the `SAM` hive.

### Access the Protected System File

As members of `Hyper-V Administrators`, we now have sufficient permissions to access the `SAM` and `SYSTEM` registry hives

``` powershell
copy C:\Windows\System32\config\SAM C:\Temp\SAM_copy

copy C:\Windows\System32\config\SYSTEM C:\Temp\SYSTEM_copy
```
