---
title: Writing Custom Wordlists and Rules
date: 2025-12-04 01:55:58

categories:
  - Active Directory
  - Enumeration
  - Users & Passwords Enumeration
  - Writing Custom Wordlists and Rules

tags:
  - Creds
  - CeWL
  - Cupp
  - Hashcat Rules

cover: /img/wordlist.png
top_img: /img/bg-img.jpg
description: Writing Custom Wordlists and Rules
---


# Default Credential 

### Creds

Installation 

```bash
pip3 install defaultcreds-cheat-sheet
```

Example :

```bash
creds search tomcat
```

```bash
creds search mysql
```


# CeWL

>- Depth to spider (`-d`)
>- The minimum length of the word (`-m`)
>- The storage of the found words in lowercase (`--lowercase`)
>- The file where we want to store the results (`-w`)

```bash
cewl https://website -d 4 -m 6 --lowercase -w wordlist.txt
```


# Cupp

> We can perform OSINT gathering and feed the collected information into `cupp` to generate a personalized wordlist.

```bash
cupp -i
```



# Hashcat Rules

### Predefined Rules

```bash
➜ ls /usr/share/hashcat/rules/

best64.rule
dive.rule
generated2.rule
rockyou-30000.rule
hob0rules
```

### Writing Custom Rules

>`:`      Do nothing
>`l`      Lowercase all letters
>`u`      Uppercase all letters                        
>`c`      Capitalize the first letter and lowercase others
>`sXY`   Replace all instances of X with Y                
>`$!`     Add the exclamation character at the end


```bash
cat custom.rule

:
c
so0
c so0
sa@
c sa@
c sa@ so0
$!
$! c
$! so0
$! sa@
$! c so0
$! c sa@
$! so0 sa@
$! c so0 sa@
```

### Applying Hashcat Rules to a Wordlist

```bash
hashcat --force our-wordlist -r custom.rule --stdout | sort -u > mut_password.list
```