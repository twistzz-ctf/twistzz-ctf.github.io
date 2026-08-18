---
title: Shares
date: 2026-07-04 23:54:02

categories:
  - Active Directory
  - Exploitation
  - Enumeration 
  - Shares

tags:
  - SMB-Shares
  - File-Shares
  - Snaffler
  - PowerView
  - Find-DomainShare
  - Get-NetShare
  - Get-DomainFileServer
  - DFS
  - Get-DomainDFSShare
  - Living-Off-The-Land

cover: /img/smb-share-enumeration.png
top_img: /img/bg-img.jpg
description: Learn how to enumerate SMB shares from Linux and Windows using NetExec, SMBMap, Snaffler, PowerView, and built-in Windows commands to identify accessible file shares and sensitive data.
---



# Linux
#### Share Access 

> ➜ List shares and our permissions on each one 

```bash
nxc smb <DC_IP> -u <user> -p <pass> --shares
```

#### Spider Shares

> ➜ Recursively list readable files across shares.

```bash
nxc smb <DC_IP> -u <user> -p <pass> -M spider_plus
```

#### SMBMap

> ➜ Map share access.

```bash
smbmap -u <user> -p <pass> -d <DOMAIN> -H <DC_IP>
```

> ➜ Recursively list a share's contents.

```bash
smbmap -u <user> -p <pass> -d <DOMAIN> -H <DC_IP> -R
```

# Windows

#### Snaffler

> ➜ Sweep shares for credentials and interesting files.

```powershell
.\Snaffler.exe -d <DOMAIN> -s -v data
```

### PowerView 

```powershell
Import-Module .\PowerView.ps1
```

> ➜ Find domain shares the current user can access.

```powershell
Find-DomainShare -CheckShareAccess
```

> ➜ Return the open shares on a target host.

```powershell
Get-NetShare -ComputerName <host>
```

> ➜ Identify likely file servers (high-value loot targets).

```powershell
Get-DomainFileServer
```

> ➜ Return all Distributed File System (DFS) shares.

```powershell
Get-DomainDFSShare
```

### Living Off the Land - Built-in


> ➜ List the shared folders exposed by a specific host.

```cmd
net view \\<host> /ALL
```


> ➜ Show the shares currently published by the local host.

```cmd
net share
```