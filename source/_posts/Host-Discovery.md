---
title: Host Discovery
date: 2026-07-04 18:16:52

categories:
  - Active Directory
  - Exploitation
  - Enumeration 
  - Host Discovery

tags:
  - Active-Directory
  - Host-Discovery
  - Network-Discovery
  - Passive-Reconnaissance
  - Active-Reconnaissance
  - ARP
  - mDNS
  - Responder
  - Wireshark
  - tcpdump
  - pktmon
  - fping
  - Nmap
  - ICMP
  - Ping-Sweep

cover: /img/host-discovery.png
top_img: /img/bg-img.jpg
description: Learn how to discover live hosts on an internal network using passive traffic analysis and active host discovery techniques with Linux and Windows tools.
---


## Passive

#### Linux

> ➜ Sniff ARP and MDNS to reveal live hosts and hostnames without sending anything.


> Wireshark

```bash
sudo -E wireshark
```

> tcpdump

```bash
sudo tcpdump -i <iface>
```

> Responder (Analyze)

> Analyze mode logs hosts requesting name resolution without poisoning.

```bash
sudo responder -I <iface> -A
```


#### Windows

> pktmon 

```cmd
pktmon start --capture
```

## Active 

> FPing Sweep

> Sweep the subnet and write alive hosts to a list.

```bash
fping -asgq 172.16.5.0/23
```

> Nmap

```bash
nmap -sn -iL hosts.txt -oG -
```




## Living Off the Land - Local Host & Network Awareness

> ➜ Once on a foothold, these built-ins map the local host and the networks it can reach, revealing pivot points without any tooling.

#### ARP Cache

> ➜ List hosts this machine has recently communicated with

```powershell
arp -a
```

#### Routing Table

> ➜ Display the routing table to reveal reachable networks.

```powershell
route print
```

#### IP Configuration

> ➜ Built-in. Show the full network configuration, including DNS servers and domain.

```powershell
ipconfig /all
```