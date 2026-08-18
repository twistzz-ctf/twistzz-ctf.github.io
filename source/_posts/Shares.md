---
title: Shares
date: 2026-07-04 23:54:02
categories:
  - Active Directory
  - Exploitation
  - Enumeration
  - Shares
tags:
  - PowerView
  - Living-Off-The-Land
  - Snaffler
  - SMB-Shares
  - File-Shares
  - Find-DomainShare
  - Get-NetShare
  - Get-DomainFileServer
  - DFS
  - Get-DomainDFSShare
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

> ➜ Recursively list a share’s contents.

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
