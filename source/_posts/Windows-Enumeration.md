---
title: Windows Enumeration
date: 2026-06-09 20:23:00

categories:
  - Active Directory
  - Windows
  - Post-Exploitation
  - Windows Privesc
  - Windows Enumeration

tags:
  - systeminfo
  - whoami
  - tasklist
  - netstat
  - ipconfig
  - Get-HotFix
  - Get-Process
  - wmic
cover: /img/privesc.png
top_img: /img/bg-img.jpg
description: Enumerate a Windows system for privilege escalation vectors.
---





# System Information


> Operating system version and build


```
C:\> systeminfo | findstr /B /C:"OS Name" /C:"OS Version"
```


> Patch level 

```cmd
C:\> wmic qfe list brief
```

```PowerShell
PS> Get-HotFix | ft -AutoSize
```

> Environment variables

> If a writable directory appears early in `PATH` ( Example home directory ) we can plant a malicious binary or DLL that gets loaded by a privileged process like DLL hijacking or binary planting.


```cmd
C:\> set
```



```PowerShell
PS> Get-ChildItem Env:

➜ Check just the PATH

PS> $env:PATH
```

# Running Processes & Services


> Reading tasklist

> We should look for anything non-standard: database servers, backup agents, VPN clients, monitoring tools, and especially anything running as SYSTEM or a service account.


```cmd
C:\> tasklist /svc

Image Name          PID  Services
=================== ==== =====================================
FileZilla Server.exe 1140 FileZilla Server
inSyncCPHwnet64.exe  3324 inSyncCPHService      <-- Druva inSync 6.6.3 (vulnerable!)
MsMpEng.exe         2136 WinDefend
spoolsv.exe         1884 Spooler                <-- PrintNightmare target
```


```powershell
Get-Process
```

`If we see a process with "Session ID >= 1" and we are connecting with winrm this probably means there is another user logged in with us`


> Network connections 

> Services may be running on localhost-only ports (127.0.0.1) that are invisible to external scan and these are often less hardened because administrators assume `it's not accessible from the network.`.

```
C:\> netstat -ano

Proto  Local Address     Foreign Address  State      PID
TCP    0.0.0.0:445       0.0.0.0:0        LISTENING  4
TCP    0.0.0.0:3389      0.0.0.0:0        LISTENING  968
TCP    127.0.0.1:14147   0.0.0.0:0        LISTENING  1140  <-- FileZilla admin interface
TCP    127.0.0.1:6064    0.0.0.0:0        LISTENING  3324  <-- Druva inSync RPC
```


# User & Group Information


> It tells us three critical things: 
> - Our identity
> - Our group memberships
> - Our assigned token privileges

```cmd
C:\> whoami /all

USER INFORMATION
User Name          SID
================== =============================================
winlpe-srv01\htb-student  S-1-5-21-...-1002

GROUP INFORMATION
Group Name                           Type  Attributes
==================================== ===== ========================
BUILTIN\Backup Operators             Alias Mandatory group, Enabled  <-- JACKPOT

PRIVILEGES INFORMATION
Privilege Name                Description           State
============================= ===================== ========
SeImpersonatePrivilege        Impersonate a client  Enabled   <-- Potato attack
SeBackupPrivilege             Back up files         Disabled  <-- Can be enabled
```


> Group Memberships

|Group|Why it matters|Attack path|
|---|---|---|
|Backup Operators|Can read any file, log into DCs locally|Extract NTDS.dit → Domain Admin|
|Server Operators|Full control over all services on servers/DCs|Modify service binpath → SYSTEM|
|DnsAdmins|Can load DLL into DNS service (runs as SYSTEM on DC)|Malicious DLL → SYSTEM on DC|
|Print Operators|SeLoadDriverPrivilege (load kernel drivers)|Capcom.sys → SYSTEM|
|Hyper-V Administrators|Full Hyper-V access, can clone virtual DCs|Clone DC VHDX → extract NTDS.dit|
|Event Log Readers|Read security event logs including 4688 process creation|Find credentials in process command lines|


```
C:\> net localgroup administrators
C:\> net localgroup "Backup Operators"
C:\> net localgroup "Server Operators"
C:\> net localgroup "DnsAdmins"
C:\> net localgroup "Print Operators"
C:\> net localgroup "Hyper-V Administrators"
```


# Network Information : Identifying dual-homed machines


> IP Configuration

```cmd
C:\> ipconfig /all
# Look for multiple "Ethernet adapter" sections with different IP ranges

Ethernet adapter Ethernet0:   IPv4: 10.129.43.8    <-- External network
Ethernet adapter Ethernet1:   IPv4: 192.168.20.56  <-- Internal segment!
```

> ARP Table / ARP Cache

```cmd
C:\> arp -a          # Discover other hosts passively
```

> Routing Table

```cmd
C:\> route print     # See all reachable networks
```