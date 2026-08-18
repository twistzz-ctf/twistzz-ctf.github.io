---
title: Linux Credential Hunting
date: 2025-11-27 09:55:02
categories:
  - Active Directory
  - Linux
  - Post Exploitation
  - Credential Hunting
tags:
  - config-files
  - history-file
  - db-files
  - cronjobs-enumeration
---

# Linux Credential Hunting

### Enumerating history files

```bash
tail -n10 /home/*/.bash*
```

### Searching for configuration files

```bash
for l in $(echo ".conf .config .cnf");do echo -e "\nFile extension: " $l; find / -name *$l 2>/dev/null | grep -v "lib\|fonts\|share\|core" ;done
```

### Searching for Passwords in Configuration Files

```bash
for i in $(find / -type f \( -iname "*.txt" -o -iname "*.ini" -o -iname "*.cfg" -o -iname "*.config" -o -iname "*.xml" -o -iname "*.yml" -o -iname "*.yaml" -o -iname "*.cnf" -o -iname "*.conf" -o -iname "*.sh" -o -iname "*.py" -o -iname "*.php" -o -iname "*.git" -o -iname "*.json" \) 2>/dev/null | grep -v "doc\|lib"); do echo -e "\nFile: $i"; grep -Ei "password|passphrase|key|username|user account|creds|users|passkeys|configuration|dbcredential|dbpassword|pwd|login|credentials" "$i" 2>/dev/null | grep -Ev "^\s*#"; done
```

### Searching for databases

```bash
for l in $(echo ".sql .db .*db .db*");do echo -e "\nDB File extension: " $l; find / -name *$l 2>/dev/null | grep -v "doc\|lib\|headers\|share\|man";done
```

### Searching for scripts

```bash
for l in $(echo ".py .pyc .pl .go .jar .c .sh");do echo -e "\nFile extension: " $l; find / -name *$l 2>/dev/null | grep -v "doc\|lib\|headers\|share";done
```

### Searching for notes

```bash
find /home/* -type f -name "*.txt" -o ! -name "*.*"
```

### Enumerating log files

```bash
for i in $(ls /var/log/* 2>/dev/null);do GREP=$(grep "accepted\|session opened\|session closed\|failure\|failed\|ssh\|password changed\|new user\|delete user\|sudo\|COMMAND\=\|logs" $i 2>/dev/null); if [[ $GREP ]];then echo -e "\n#### Log file: " $i; grep "accepted\|session opened\|session closed\|failure\|failed\|ssh\|password changed\|new user\|delete user\|sudo\|COMMAND\=\|logs" $i 2>/dev/null;fi;done
```

### Enumerating cronjobs

```bash
cat /etc/crontab

# /etc/crontab: system-wide crontab
# Unlike any other crontab you don't have to run the `crontab'
# command to install the new version when you edit this file
# and files in /etc/cron.d. These files also have username fields,
# that none of the other crontabs do.

SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# Example of job definition:
# .---------------- minute (0 - 59)
# |  .------------- hour (0 - 23)
# |  |  .---------- day of month (1 - 31)
# |  |  |  .------- month (1 - 12) OR jan,feb,mar,apr ...
# |  |  |  |  .---- day of week (0 - 6) (Sunday=0 or 7) OR sun,mon,tue,wed,thu,fri,sat
# |  |  |  |  |
# *  *  *  *  * user-name command to be executed
```

```bash
ls -la /etc/cron.*/

/etc/cron.d/:
total 28
drwxr-xr-x 1 root root  106  3. Jan 20:27 .
drwxr-xr-x 1 root root 5728  1. Feb 00:06 ..
-rw-r--r-- 1 root root  201  1. Mär 2021  e2scrub_all
-rw-r--r-- 1 root root  331  9. Jan 2021  geoipupdate
-rw-r--r-- 1 root root  607 25. Jan 2021  john
-rw-r--r-- 1 root root  589 14. Sep 2020  mdadm
-rw-r--r-- 1 root root  712 11. Mai 2020  php
-rw-r--r-- 1 root root  102 22. Feb 2021  .placeholder
-rw-r--r-- 1 root root  396  2. Feb 2021  sysstat

/etc/cron.daily/:
total 68
drwxr-xr-x 1 root root  252  6. Jan 16:24 .
drwxr-xr-x 1 root root 5728  1. Feb 00:06 ..
<SNIP>
```
